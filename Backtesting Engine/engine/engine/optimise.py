"""Stage 1 coarse search (build-spec §8), and the resumability contract.

## Surviving an interrupted machine

This is designed to run for days on a laptop that sleeps, loses network, or gets
closed. Three mechanisms, in order of importance:

1. **The result cache** (`runner.ResultCache`) is content-addressed and written
   atomically. A completed backtest is never repeated, whatever killed the
   process. This is what makes a restart cheap rather than catastrophic.
2. **Optuna's SQLite storage** holds every completed trial. Restarting resumes
   the same study by name, keeps the sampler's history, and only runs the
   trials still owed. WAL journalling means an abrupt power loss loses at most
   the in-flight transaction, never the database.
3. **In-flight trials are the only loss.** A trial killed mid-backtest is
   re-run from scratch on resume — at most `workers` trials of wasted work.

macOS sleep is the *benign* case: the process suspends and continues on wake.
The one thing that needs handling is Docker's socket going away underneath a
suspended worker, which surfaces as an infrastructure error and is retried with
backoff by the runner.

Nothing here is ever destructive: re-running `engine optimise` on a finished
study is a no-op that reprints the result.
"""

from __future__ import annotations

import json
import logging
import math
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Callable

import optuna
from optuna.samplers import RandomSampler, TPESampler
from optuna.trial import TrialState

from engine.config import GatesConfig, SearchSpace, StudyConfig
from engine.metrics import Metrics, compute, suspicion_flags
from engine.runner import RunSpec, Runner

log = logging.getLogger(__name__)

# Optuna's own logging is noisy across thousands of trials.
optuna.logging.set_verbosity(optuna.logging.WARNING)

REJECTED = -math.inf


@dataclass
class TrialRecord:
    """What a trial produced — the raw material for DSR and PBO later."""
    number: int
    params: dict[str, Any]
    score: float
    metrics: dict[str, Any]
    rejected_reason: str = ""
    flags: list[str] | None = None


def storage_url(path: Path) -> str:
    """SQLite storage with WAL, so an abrupt kill cannot corrupt the study."""
    path.parent.mkdir(parents=True, exist_ok=True)
    return f"sqlite:///{path}?timeout=60"


def _enable_wal(path: Path) -> None:
    import sqlite3
    con = sqlite3.connect(path)
    try:
        con.execute("PRAGMA journal_mode=WAL")
        con.execute("PRAGMA synchronous=NORMAL")
    finally:
        con.close()


def suggest(trial: optuna.Trial, space: SearchSpace) -> dict[str, Any]:
    """Build one parameter set, honouring conditional parameters.

    A conditional parameter is only suggested when its parent toggle is on, so
    Optuna never wastes trials exploring a dimension that has no effect — and,
    more importantly, the trial log does not pretend to more dimensions than
    were actually in play.
    """
    values: dict[str, Any] = {}
    for name, p in space.search.items():
        if p.condition:
            parent = values.get(p.condition, space.fixed.get(p.condition))
            if not parent:
                continue
        if p.type == "float":
            values[name] = trial.suggest_float(name, p.low, p.high, step=p.step)
        elif p.type == "int":
            values[name] = trial.suggest_int(name, int(p.low), int(p.high),
                                             step=int(p.step) if p.step else 1)
        elif p.type == "bool":
            values[name] = trial.suggest_categorical(name, [True, False])
        else:
            values[name] = trial.suggest_categorical(name, p.choices)
    return values


def check_constraints(m: Metrics, gates: GatesConfig, span_years: float) -> str:
    """Hard constraints from 01-Research §4.3. Returns "" when the trial passes.

    A violating trial is rejected outright rather than scored badly: a strategy
    that trades twice and wins both is not a better version of one that trades
    two hundred times.
    """
    if m.trades == 0:
        return "no trades"
    if m.trades_per_year < gates.min_trades_per_year:
        return (f"trades/year {m.trades_per_year:.1f} < {gates.min_trades_per_year}")
    if m.max_dd_pct > gates.max_dd_pct:
        return f"max drawdown {m.max_dd_pct:.1f}% > {gates.max_dd_pct}%"
    if m.profit_factor < gates.min_pf:
        return f"profit factor {m.profit_factor:.2f} < {gates.min_pf}"
    return ""


def objective_value(m: Metrics) -> float:
    """Primary objective: annualised Sharpe of the daily-return series.

    Never raw net profit. Note the caveat recorded in 03-Verification-Findings
    §4.1 — Sharpe is only meaningful when the trade count supports it, which is
    what the min_trades_per_year constraint is for.
    """
    return m.sharpe


class Stage1Search:
    """Runs the random + TPE budget, logging every trial."""

    def __init__(
        self,
        study_cfg: StudyConfig,
        space: SearchSpace,
        runner: Runner,
        csv: Path,
        start: date,
        end: date,
        seed: int = 42,
    ):
        self.cfg = study_cfg
        self.space = space
        self.runner = runner
        self.csv = csv
        self.start = start
        self.end = end
        self.seed = seed
        self.span_years = max((end - start).days / 365.25, 1e-9)

    def _evaluate(self, trial: optuna.Trial) -> float:
        params = suggest(trial, self.space)
        merged = {**self.space.fixed, **params}

        spec = RunSpec(
            parameters=merged, csv=self.csv, start=self.start, end=self.end,
            spread_pips=self.cfg.execution.spread("realistic"),
            trial_id=str(trial.number),
        )
        outcome = self.runner.run_one(spec)

        if outcome.result.failed:
            trial.set_user_attr("failed", True)
            trial.set_user_attr("failure", outcome.result.failure_excerpt[:500])
            # A crashed bot is not a bad parameter set — it is no information.
            raise optuna.TrialPruned(f"backtest failed: {outcome.result.failure_excerpt[:200]}")

        m = compute(
            outcome.result.trade_pnl, outcome.result.equity_curve,
            self.cfg.account.nominal_balance, self.cfg.account.risk_per_trade,
        )
        trial.set_user_attr("metrics", m.as_dict())
        trial.set_user_attr("cache_key", outcome.key)
        trial.set_user_attr("equity_source", outcome.result.equity_source)

        flags = suspicion_flags(m)
        if flags:
            trial.set_user_attr("suspicion_flags", flags)

        reason = check_constraints(m, self.cfg.gates, self.span_years)
        if reason:
            trial.set_user_attr("rejected_reason", reason)
            return REJECTED

        return objective_value(m)

    def run(
        self,
        storage_path: Path,
        n_random: int,
        n_tpe: int,
        progress: Callable[[int, int], None] | None = None,
    ) -> optuna.Study:
        """Run (or resume) the stage-1 budget.

        Safe to call repeatedly: completed trials are read from storage and only
        the outstanding balance is run.
        """
        url = storage_url(storage_path)
        total = n_random + n_tpe

        study = optuna.create_study(
            study_name=f"{self.cfg.study}_stage1",
            storage=url,
            direction="maximize",
            load_if_exists=True,
            sampler=RandomSampler(seed=self.seed),
        )
        _enable_wal(storage_path)

        done = self._finished(study)
        if done >= total:
            log.info("stage 1 already complete (%d trials)", done)
            return study

        # Random first for unbiased coverage — it is also the reference
        # distribution PBO needs later.
        remaining_random = max(0, n_random - done)
        if remaining_random:
            study.sampler = RandomSampler(seed=self.seed)
            self._optimise(study, remaining_random, total, progress)

        done = self._finished(study)
        remaining_tpe = max(0, total - done)
        if remaining_tpe:
            study.sampler = TPESampler(seed=self.seed, n_startup_trials=0)
            self._optimise(study, remaining_tpe, total, progress)

        return study

    def _optimise(self, study, n, total, progress) -> None:
        def callback(st, _tr):
            if progress:
                progress(self._finished(st), total)
        study.optimize(
            self._evaluate, n_trials=n, callbacks=[callback],
            catch=(),          # a real exception must stop the study, not be swallowed
            gc_after_trial=True,
        )

    @staticmethod
    def _finished(study: optuna.Study) -> int:
        return sum(1 for t in study.trials
                   if t.state in (TrialState.COMPLETE, TrialState.PRUNED))


def trial_records(study: optuna.Study) -> list[TrialRecord]:
    """Every trial ever run — DSR and PBO deflate by this, so nothing is dropped."""
    out = []
    for t in study.trials:
        if t.state not in (TrialState.COMPLETE, TrialState.PRUNED):
            continue
        out.append(TrialRecord(
            number=t.number,
            params=dict(t.params),
            score=float(t.value) if t.value is not None else REJECTED,
            metrics=t.user_attrs.get("metrics", {}),
            rejected_reason=t.user_attrs.get("rejected_reason", ""),
            flags=t.user_attrs.get("suspicion_flags"),
        ))
    return out


def plateau_prescreen(records: list[TrialRecord], space: SearchSpace, k: int = 20) -> list[TrialRecord]:
    """Rank candidates by their neighbourhood, not their peak (build-spec §8).

    Scoring each candidate by the mean objective of its nearest logged
    neighbours demotes isolated spikes before they ever reach walk-forward.
    A lucky single point is the classic overfitting artefact; a point whose
    neighbours also work is a plateau.
    """
    viable = [r for r in records if math.isfinite(r.score) and not r.rejected_reason]
    if not viable:
        return []

    names = list(space.search)
    ranges: dict[str, float] = {}
    for n in names:
        p = space.search[n]
        if p.type in ("float", "int") and p.low is not None:
            ranges[n] = max(float(p.high) - float(p.low), 1e-9)

    def distance(a: TrialRecord, b: TrialRecord) -> float:
        total = 0.0
        for n in names:
            va, vb = a.params.get(n), b.params.get(n)
            if va is None or vb is None:
                total += 1.0 if va != vb else 0.0
            elif n in ranges:
                total += abs(float(va) - float(vb)) / ranges[n]
            else:
                total += 0.0 if va == vb else 1.0
        return total

    # Neighbours count only in proportion to how near they actually are: a point
    # 60% of the way across the space is not evidence about this point's
    # neighbourhood. `scale` is in normalised units, so 0.1 means "within about
    # 10% of each parameter's range".
    scale = 0.1
    n_expected = max(2, 2 * len(names))

    scored = []
    for r in viable:
        others = sorted((x for x in viable if x is not r), key=lambda x: distance(r, x))
        near = others[:n_expected]
        weights = [math.exp(-distance(r, x) / scale) for x in near]
        support = sum(weights)

        # Missing evidence is treated as evidence against, not as neutral. A
        # candidate with no near neighbours has not demonstrated a plateau, and
        # an isolated peak is the classic overfitting artefact — so the absent
        # neighbours drag the score down rather than leaving the raw peak intact.
        deficit = max(0.0, n_expected - support)
        numerator = r.score + sum(w * x.score for w, x in zip(weights, near))
        scored.append((numerator / (1.0 + support + deficit), r))

    scored.sort(key=lambda s: s[0], reverse=True)
    return [r for _, r in scored[:k]]


def write_stage1_output(
    records: list[TrialRecord], top: list[TrialRecord], path: Path
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "total_trials": len(records),
        "viable_trials": sum(1 for r in records if math.isfinite(r.score) and not r.rejected_reason),
        "rejected": sum(1 for r in records if r.rejected_reason),
        "rejection_reasons": _count_reasons(records),
        "flagged": [
            {"trial": r.number, "flags": r.flags} for r in records if r.flags
        ],
        "top_k": [
            {"trial": r.number, "score": r.score, "params": r.params, "metrics": r.metrics}
            for r in top
        ],
    }
    path.write_text(json.dumps(payload, indent=2, default=str) + "\n")


def _count_reasons(records: list[TrialRecord]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for r in records:
        if not r.rejected_reason:
            continue
        key = r.rejected_reason.split()[0:2]
        counts[" ".join(key)] = counts.get(" ".join(key), 0) + 1
    return dict(sorted(counts.items(), key=lambda kv: -kv[1]))
