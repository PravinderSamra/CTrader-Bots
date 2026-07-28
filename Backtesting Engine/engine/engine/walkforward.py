"""Stage 2 walk-forward analysis (build-spec §9, methodology 01-Research §5.1).

Every headline metric in the final report comes from the *concatenated
out-of-sample* curve produced here — never from in-sample. That is the whole
point: in-sample performance after a parameter search is biased upward by
construction, whatever the strategy's real edge.

Two questions are answered separately, because they are different questions:

  * **Re-optimised WFA** — re-run the search on each fold's in-sample window and
    apply the winner to the unseen out-of-sample window. This measures the
    *process*: "if I re-optimise every six months, how does that do?"
  * **Fixed-θ evaluation** — take each stage-1 candidate and apply it unchanged
    across every fold's OOS. This measures the *parameter set*: "does this one
    configuration keep working?"

The recommendation comes from the fixed-θ table, because that is what you will
actually run live. The re-optimised table tells you whether a re-optimisation
cadence is worth adopting, which is an operational decision rather than a
parameter choice.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any

import pandas as pd

from engine.config import SearchSpace, StudyConfig
from engine.metrics import Metrics, compute
from engine.optimise import REJECTED, Stage1Search, TrialRecord, objective_value
from engine.runner import RunSpec, Runner

log = logging.getLogger(__name__)


def add_months(d: date, months: int) -> date:
    """Calendar-month arithmetic, clamping to the end of a short month."""
    total = d.month - 1 + months
    year = d.year + total // 12
    month = total % 12 + 1
    day = d.day
    while day > 1:
        try:
            return date(year, month, day)
        except ValueError:
            day -= 1
    return date(year, month, 1)


@dataclass(frozen=True)
class Fold:
    index: int
    is_start: date
    is_end: date       # exclusive
    oos_start: date    # == is_end
    oos_end: date      # exclusive

    def as_dict(self) -> dict:
        return {
            "fold": self.index,
            "is_start": self.is_start.isoformat(),
            "is_end": self.is_end.isoformat(),
            "oos_start": self.oos_start.isoformat(),
            "oos_end": self.oos_end.isoformat(),
        }


def generate_folds(
    data_start: date, holdout_start: date, is_months: int, oos_months: int,
    step_months: int, mode: str = "rolling", align: str = "end",
) -> list[Fold]:
    """Build the fold table. No fold may touch data at or after holdout_start.

    ``align`` decides which end of the series absorbs the remainder, because the
    window geometry rarely divides the data exactly:

      * ``"end"`` (default) — the last OOS window finishes exactly at
        ``holdout_start``, so the months immediately before the holdout are
        used and the *oldest* data is dropped instead.
      * ``"start"`` — folds march forward from ``data_start``, leaving a gap
        before the holdout.

    "end" is the better default for a day-trading strategy: the months next to
    the holdout are the most recent regime and the most relevant evidence, and
    throwing them away to preserve 2021 is the wrong trade. On the UK100 study
    "start" alignment silently discards five months of the most recent data.
    """
    folds: list[Fold] = []

    if align == "end":
        i = 0
        while True:
            oos_end = add_months(holdout_start, -i * step_months)
            oos_start = add_months(oos_end, -oos_months)
            is_end = oos_start
            is_start = data_start if mode == "anchored" \
                else add_months(is_end, -is_months)
            if is_start < data_start or is_start >= is_end:
                break
            folds.append(Fold(0, is_start, is_end, oos_start, oos_end))
            i += 1
        folds.reverse()
        folds = [Fold(n, f.is_start, f.is_end, f.oos_start, f.oos_end)
                 for n, f in enumerate(folds)]
    else:
        i = 0
        while True:
            is_start = data_start if mode == "anchored" \
                else add_months(data_start, i * step_months)
            is_end = add_months(data_start, is_months + i * step_months)
            oos_end = add_months(is_end, oos_months)
            if oos_end > holdout_start or is_start >= is_end:
                break
            folds.append(Fold(i, is_start, is_end, is_end, oos_end))
            i += 1

    if not folds:
        raise ValueError(
            f"no walk-forward folds fit between {data_start} and {holdout_start} with "
            f"IS={is_months}m OOS={oos_months}m. Shorten the windows or extend the data."
        )
    return folds


@dataclass
class FoldResult:
    fold: Fold
    selected_params: dict[str, Any]
    is_metrics: Metrics | None
    oos_metrics: Metrics | None
    oos_trades: pd.DataFrame = field(default_factory=pd.DataFrame)
    oos_equity: pd.Series = field(default_factory=lambda: pd.Series(dtype="float64"))
    failed: bool = False


def concatenate_oos(results: list[FoldResult], nominal_balance: float) -> tuple[pd.Series, pd.Series]:
    """Stitch each fold's OOS into one continuous equity curve and P&L series.

    Folds are chained by *increment*, not by absolute level: each fold's
    backtest restarts at the nominal balance, so the raw curves all begin at
    the same value and simply concatenating them would erase every fold's
    return.
    """
    pnl_parts: list[pd.Series] = []
    equity_points: list[pd.Series] = []
    running = nominal_balance

    for r in sorted(results, key=lambda x: x.fold.index):
        if r.failed or r.oos_equity.empty:
            continue
        deltas = r.oos_equity - r.oos_equity.iloc[0]
        equity_points.append(deltas + running)
        running += float(deltas.iloc[-1])
        if not r.oos_trades.empty:
            pnl_parts.append(r.oos_trades["net_pnl"])

    equity = pd.concat(equity_points).sort_index() if equity_points \
        else pd.Series(dtype="float64")
    pnl = pd.concat(pnl_parts, ignore_index=True) if pnl_parts \
        else pd.Series(dtype="float64")
    return pnl, equity


def walk_forward_efficiency(results: list[FoldResult]) -> float:
    """OOS performance as a fraction of IS performance for the selected params.

    Below ~0.5 the search is mostly fitting noise: the parameters that looked
    good in-sample stop working the moment they meet unseen data.
    """
    is_vals, oos_vals = [], []
    for r in results:
        if r.failed or r.is_metrics is None or r.oos_metrics is None:
            continue
        is_vals.append(r.is_metrics.sharpe)
        oos_vals.append(r.oos_metrics.sharpe)
    if not is_vals:
        return 0.0
    is_mean = sum(is_vals) / len(is_vals)
    oos_mean = sum(oos_vals) / len(oos_vals)
    if is_mean <= 0:
        return 0.0
    return oos_mean / is_mean


def fold_concentration(results: list[FoldResult]) -> float:
    """Largest share of total OOS profit contributed by any single fold.

    A strategy whose entire out-of-sample profit comes from one lucky six-month
    window has not been validated, however good the aggregate looks.
    """
    profits = [
        float(r.oos_metrics.net_profit) for r in results
        if not r.failed and r.oos_metrics is not None
    ]
    total = sum(p for p in profits if p > 0)
    if total <= 0:
        return 1.0
    return max((p / total for p in profits if p > 0), default=1.0)


def parameter_dispersion(results: list[FoldResult], space: SearchSpace) -> dict[str, float]:
    """How much each selected parameter moved across folds, normalised to 0-1.

    High dispersion with good OOS numbers is a warning rather than a failure:
    it can be legitimate regime adaptation, or it can mean the objective
    surface is flat and the search is picking essentially at random. Either
    way it means a single fixed θ is unlikely to hold.
    """
    out: dict[str, float] = {}
    for name, p in space.search.items():
        values = [r.selected_params.get(name) for r in results if not r.failed]
        values = [v for v in values if v is not None]
        if len(values) < 2:
            continue
        if p.type in ("float", "int") and p.low is not None:
            span = max(float(p.high) - float(p.low), 1e-9)
            mean = sum(float(v) for v in values) / len(values)
            var = sum((float(v) - mean) ** 2 for v in values) / (len(values) - 1)
            out[name] = math.sqrt(var) / span
        else:
            # Categorical/bool: fraction of folds disagreeing with the mode.
            mode = max(set(values), key=values.count)
            out[name] = 1.0 - values.count(mode) / len(values)
    return out


class WalkForward:
    def __init__(
        self, study_cfg: StudyConfig, space: SearchSpace, runner: Runner, csv: Path,
    ):
        self.cfg = study_cfg
        self.space = space
        self.runner = runner
        self.csv = csv

    def folds(self) -> list[Fold]:
        w = self.cfg.windows
        return generate_folds(
            w.data_start, w.holdout_start, w.wfa.is_months, w.wfa.oos_months,
            w.wfa.step_months, w.wfa.mode, w.wfa.align,
        )

    def _evaluate(self, params: dict[str, Any], start: date, end: date, tag: str):
        spec = RunSpec(
            parameters={**self.space.fixed, **self.space.bot_parameters(params)},
            csv=self.csv, start=start, end=end,
            spread_pips=self.cfg.execution.spread("realistic"), trial_id=tag,
        )
        outcome = self.runner.run_one(spec)
        if outcome.result.failed:
            return None, outcome
        m = compute(
            outcome.result.trade_pnl, outcome.result.equity_curve,
            self.cfg.account.nominal_balance, self.cfg.account.risk_per_trade,
        )
        return m, outcome

    def run_reoptimised(
        self, storage_dir: Path, seed_candidates: list[TrialRecord], trials_per_fold: int,
    ) -> list[FoldResult]:
        """Re-run the search on each fold's IS, then apply the winner to its OOS."""
        results: list[FoldResult] = []
        for fold in self.folds():
            search = Stage1Search(
                study_cfg=self.cfg, space=self.space, runner=self.runner, csv=self.csv,
                start=fold.is_start, end=fold.is_end, seed=1000 + fold.index,
            )
            study = search.run(
                storage_dir / f"wfa_fold{fold.index}.db",
                n_random=max(1, trials_per_fold // 4),
                n_tpe=trials_per_fold - max(1, trials_per_fold // 4),
            )
            completed = [t for t in study.trials
                         if t.value is not None and math.isfinite(t.value)
                         and t.value > REJECTED]
            if not completed:
                results.append(FoldResult(fold, {}, None, None, failed=True))
                continue

            best = max(completed, key=lambda t: t.value)
            is_metrics = _metrics_from_attrs(best.user_attrs.get("metrics"))
            oos_metrics, outcome = self._evaluate(
                dict(best.params), fold.oos_start, fold.oos_end, f"wfa-oos-{fold.index}",
            )
            results.append(FoldResult(
                fold=fold, selected_params=dict(best.params), is_metrics=is_metrics,
                oos_metrics=oos_metrics,
                oos_trades=outcome.result.trades_frame() if oos_metrics else pd.DataFrame(),
                oos_equity=outcome.result.equity_curve if oos_metrics else pd.Series(dtype="float64"),
                failed=oos_metrics is None,
            ))
        return results

    def run_fixed(self, params: dict[str, Any], label: str) -> list[FoldResult]:
        """Apply one parameter set unchanged to every fold's OOS window."""
        results = []
        for fold in self.folds():
            m, outcome = self._evaluate(
                params, fold.oos_start, fold.oos_end, f"fixed-{label}-{fold.index}")
            results.append(FoldResult(
                fold=fold, selected_params=dict(params), is_metrics=None, oos_metrics=m,
                oos_trades=outcome.result.trades_frame() if m else pd.DataFrame(),
                oos_equity=outcome.result.equity_curve if m else pd.Series(dtype="float64"),
                failed=m is None,
            ))
        return results


def _metrics_from_attrs(attrs: dict | None) -> Metrics | None:
    if not attrs:
        return None
    kwargs = dict(attrs)
    for key in ("max_dd_peak", "max_dd_trough"):
        kwargs[key] = pd.Timestamp(kwargs[key]) if kwargs.get(key) else None
    try:
        return Metrics(**kwargs)
    except TypeError:
        return None


def summarise(
    reoptimised: list[FoldResult],
    fixed: dict[str, list[FoldResult]],
    space: SearchSpace,
    nominal_balance: float,
) -> dict:
    """Build the report payload for Stage 2."""
    pnl, equity = concatenate_oos(reoptimised, nominal_balance)
    reopt_metrics = compute(pnl, equity, nominal_balance, 1.0) if len(pnl) else None

    fixed_rows = []
    for label, results in fixed.items():
        f_pnl, f_equity = concatenate_oos(results, nominal_balance)
        if not len(f_pnl):
            fixed_rows.append({"candidate": label, "failed": True})
            continue
        m = compute(f_pnl, f_equity, nominal_balance, 1.0)
        fixed_rows.append({
            "candidate": label,
            "params": results[0].selected_params,
            "oos_sharpe": m.sharpe,
            "oos_profit_factor": m.profit_factor,
            "oos_max_dd_pct": m.max_dd_pct,
            "oos_trades": m.trades,
            "worst_fold_profit": min(
                (r.oos_metrics.net_profit for r in results if r.oos_metrics), default=0.0),
            "fold_concentration": fold_concentration(results),
        })
    fixed_rows.sort(key=lambda r: r.get("oos_sharpe", -math.inf), reverse=True)

    return {
        "folds": [f.as_dict() for f in (r.fold for r in reoptimised)],
        "reoptimised": {
            "walk_forward_efficiency": walk_forward_efficiency(reoptimised),
            "fold_concentration": fold_concentration(reoptimised),
            "parameter_dispersion": parameter_dispersion(reoptimised, space),
            "concatenated_oos": reopt_metrics.as_dict() if reopt_metrics else None,
            "per_fold": [
                {**r.fold.as_dict(),
                 "params": r.selected_params,
                 "is_sharpe": r.is_metrics.sharpe if r.is_metrics else None,
                 "oos_sharpe": r.oos_metrics.sharpe if r.oos_metrics else None,
                 "oos_profit": r.oos_metrics.net_profit if r.oos_metrics else None,
                 "failed": r.failed}
                for r in reoptimised
            ],
        },
        "fixed_theta": fixed_rows,
        "recommended": fixed_rows[0] if fixed_rows and not fixed_rows[0].get("failed") else None,
    }


def write_summary(payload: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n")
