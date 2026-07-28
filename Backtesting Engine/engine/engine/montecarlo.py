"""Stage 3b Monte Carlo battery (build-spec §11, methodology 01-Research §5.3).

A backtest is one draw from a distribution. These tests ask what the *other*
draws look like — because the sequence of trades you happened to get is not the
sequence you will get, and a strategy that only survives its own lucky ordering
is not a strategy.

All variants run on the concatenated out-of-sample trade list, never in-sample.
Every one is deterministically seeded so a report can be reproduced exactly.

The five mandated variants:

  1. **Block bootstrap** of the trade sequence (blocks preserve the streakiness
     that trade-level shuffling would destroy).
  2. **Trade dropout** — 10-20% of trades randomly removed, modelling missed
     fills, a VPS outage, or simply being away from the desk.
  3. **Execution stress** — adverse slippage and widened spread on every fill.
  4. **Same-bar ambiguity worst case** — when stop and target both sit inside
     one M1 bar, the backtester guessed; here every guess goes against you.
  5. **Concentration** — remove the five best trades. An edge that lives in
     three lucky trades is not an edge.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Callable

import numpy as np
import pandas as pd

DEFAULT_RESAMPLES = 5000
DEFAULT_BLOCK = 20


@dataclass(frozen=True)
class McDistribution:
    """Percentiles of an outcome across resamples."""
    name: str
    p05: float
    p25: float
    p50: float
    p75: float
    p95: float
    mean: float
    worst: float

    def as_dict(self) -> dict:
        return {k: getattr(self, k) for k in self.__dataclass_fields__}


def _describe(name: str, values: np.ndarray) -> McDistribution:
    if len(values) == 0:
        return McDistribution(name, 0, 0, 0, 0, 0, 0, 0)
    q = np.percentile(values, [5, 25, 50, 75, 95])
    return McDistribution(
        name=name, p05=float(q[0]), p25=float(q[1]), p50=float(q[2]),
        p75=float(q[3]), p95=float(q[4]), mean=float(values.mean()),
        worst=float(values.min()),
    )


def equity_stats(pnl: np.ndarray, starting_balance: float) -> tuple[float, float, int]:
    """Terminal P&L, max drawdown (absolute) and longest losing streak."""
    if len(pnl) == 0:
        return 0.0, 0.0, 0
    curve = starting_balance + np.cumsum(pnl)
    peak = np.maximum.accumulate(curve)
    dd = float(np.max(peak - curve))

    longest = current = 0
    for v in pnl:
        if v < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return float(curve[-1] - starting_balance), dd, longest


@dataclass
class McResult:
    terminal_pnl: McDistribution
    max_drawdown: McDistribution
    longest_loss_streak: McDistribution
    risk_of_ruin: float
    n_resamples: int
    notes: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "terminal_pnl": self.terminal_pnl.as_dict(),
            "max_drawdown": self.max_drawdown.as_dict(),
            "longest_loss_streak": self.longest_loss_streak.as_dict(),
            "risk_of_ruin": self.risk_of_ruin,
            "n_resamples": self.n_resamples,
            "notes": self.notes,
        }


def _run_resamples(
    sampler: Callable[[np.random.Generator], np.ndarray],
    n_resamples: int,
    starting_balance: float,
    ruin_threshold: float,
    seed: int,
) -> McResult:
    rng = np.random.default_rng(seed)
    terminals, drawdowns, streaks = [], [], []
    ruined = 0

    for _ in range(n_resamples):
        sample = sampler(rng)
        terminal, dd, streak = equity_stats(sample, starting_balance)
        terminals.append(terminal)
        drawdowns.append(dd)
        streaks.append(streak)
        if dd >= ruin_threshold:
            ruined += 1

    return McResult(
        terminal_pnl=_describe("terminal_pnl", np.asarray(terminals)),
        max_drawdown=_describe("max_drawdown", np.asarray(drawdowns)),
        longest_loss_streak=_describe("longest_loss_streak", np.asarray(streaks, dtype=float)),
        risk_of_ruin=ruined / n_resamples if n_resamples else 0.0,
        n_resamples=n_resamples,
    )


def block_bootstrap(
    pnl: pd.Series,
    starting_balance: float,
    ruin_threshold: float,
    block: int = DEFAULT_BLOCK,
    n_resamples: int = DEFAULT_RESAMPLES,
    seed: int = 0,
) -> McResult:
    """Resample contiguous blocks of trades (§5.3 item 1).

    Blocks rather than individual trades because losing runs cluster: shuffling
    trade-by-trade would break that autocorrelation and produce a drawdown
    distribution that is far too flattering.
    """
    values = np.asarray(pnl, dtype="float64")
    n = len(values)
    if n == 0:
        return McResult(_describe("terminal_pnl", np.array([])),
                        _describe("max_drawdown", np.array([])),
                        _describe("longest_loss_streak", np.array([])), 0.0, 0,
                        ["no trades to resample"])
    block = max(1, min(block, n))
    n_blocks = math.ceil(n / block)

    def sampler(rng: np.random.Generator) -> np.ndarray:
        starts = rng.integers(0, n, size=n_blocks)
        parts = [np.take(values, range(s, s + block), mode="wrap") for s in starts]
        return np.concatenate(parts)[:n]

    return _run_resamples(sampler, n_resamples, starting_balance, ruin_threshold, seed)


def trade_dropout(
    pnl: pd.Series,
    starting_balance: float,
    ruin_threshold: float,
    drop_min: float = 0.10,
    drop_max: float = 0.20,
    n_resamples: int = DEFAULT_RESAMPLES,
    seed: int = 1,
) -> McResult:
    """Randomly delete 10-20% of trades (§5.3 item 2).

    Models the trades you will miss: a restart, an outage, a holiday, a moment
    of hesitation. If the edge depends on catching every single signal, it is
    not an edge you can trade.
    """
    values = np.asarray(pnl, dtype="float64")
    n = len(values)
    if n == 0:
        return block_bootstrap(pnl, starting_balance, ruin_threshold, n_resamples=1, seed=seed)

    def sampler(rng: np.random.Generator) -> np.ndarray:
        frac = rng.uniform(drop_min, drop_max)
        keep = max(1, int(round(n * (1 - frac))))
        idx = np.sort(rng.choice(n, size=keep, replace=False))
        return values[idx]

    return _run_resamples(sampler, n_resamples, starting_balance, ruin_threshold, seed)


def execution_stress(
    pnl: pd.Series,
    starting_balance: float,
    ruin_threshold: float,
    slippage_cost_per_trade: float,
    n_resamples: int = DEFAULT_RESAMPLES,
    seed: int = 2,
) -> McResult:
    """Charge extra adverse slippage and spread on every fill (§5.3 item 3).

    Bar-based backtests do not model slippage at all, so this is not pessimism
    — it is the cost the backtest silently omitted.
    """
    values = np.asarray(pnl, dtype="float64")
    if len(values) == 0:
        return block_bootstrap(pnl, starting_balance, ruin_threshold, n_resamples=1, seed=seed)

    def sampler(rng: np.random.Generator) -> np.ndarray:
        # Lognormal: usually small, occasionally horrible — the real shape of
        # slippage, unlike a symmetric draw.
        costs = rng.lognormal(
            mean=math.log(max(slippage_cost_per_trade, 1e-9)), sigma=0.75, size=len(values))
        return values - costs

    return _run_resamples(sampler, n_resamples, starting_balance, ruin_threshold, seed)


def same_bar_worst_case(
    trades: pd.DataFrame,
    starting_balance: float,
    risk_per_trade: float,
) -> dict:
    """Force every ambiguous stop/target trade to lose (§5.3 item 4, §3.2).

    When a stop and a target both fall inside one M1 bar, the backtester cannot
    know which came first and guesses. This scores every guess against you.
    Deterministic, not a resample: it is a single worst-case rescore.
    """
    if trades.empty:
        return {"ambiguous_trades": 0, "note": "no trades"}

    df = trades.copy()
    if "ambiguous" not in df.columns:
        return {
            "ambiguous_trades": None,
            "note": "ambiguity not marked — requires bar data alongside the trade list; "
                    "run with the prepared full.csv to populate it",
        }

    n_ambiguous = int(df["ambiguous"].sum())
    worst = df["net_pnl"].where(~df["ambiguous"], -abs(risk_per_trade))
    terminal, dd, streak = equity_stats(worst.to_numpy(), starting_balance)
    base_terminal, base_dd, _ = equity_stats(df["net_pnl"].to_numpy(), starting_balance)

    return {
        "ambiguous_trades": n_ambiguous,
        "ambiguous_fraction": n_ambiguous / len(df),
        "baseline_pnl": base_terminal,
        "worst_case_pnl": terminal,
        "worst_case_max_dd": dd,
        "still_profitable": terminal > 0,
    }


def mark_same_bar_ambiguity(
    trades: pd.DataFrame, bars: pd.DataFrame, risk_per_trade: float,
) -> pd.DataFrame:
    """Flag trades whose stop and target could both have been hit in one bar.

    Requires the prepared M1 series. A trade is ambiguous when the bar
    containing its close spans a range at least as large as the distance
    between its entry and exit — i.e. the bar was big enough to reach both
    sides, and the ordering within it was the simulator's guess.
    """
    if trades.empty or bars.empty:
        out = trades.copy()
        out["ambiguous"] = False
        return out

    b = bars.set_index("datetime").sort_index()
    ranges = (b["high"] - b["low"])

    out = trades.copy()
    flags = []
    for _, t in out.iterrows():
        ts = pd.Timestamp(t["close_time"]).floor("1min")
        bar_range = float(ranges.get(ts, 0.0))
        move = abs(float(t["exit_price"]) - float(t["entry_price"]))
        flags.append(bool(bar_range > 0 and move > 0 and bar_range >= move))
    out["ambiguous"] = flags
    return out


def concentration_test(pnl: pd.Series, top_n: int = 5) -> dict:
    """Remove the best trades and see what is left (§5.3 item 5).

    A day-trading edge that disappears without its five best trades was never
    an edge — it was a handful of lucky sessions.
    """
    values = np.asarray(pnl, dtype="float64")
    if len(values) <= top_n:
        return {"note": f"only {len(values)} trades; cannot remove {top_n}",
                "still_profitable": False}

    order = np.argsort(values)[::-1]
    kept = np.delete(values, order[:top_n])
    total = float(values.sum())
    remaining = float(kept.sum())

    return {
        "total_pnl": total,
        "pnl_without_top": remaining,
        "top_trades_share": (total - remaining) / total if total > 0 else math.inf,
        "still_profitable": remaining > 0,
        "removed": top_n,
    }


def run_battery(
    pnl: pd.Series,
    trades: pd.DataFrame,
    starting_balance: float,
    risk_per_trade: float,
    max_dd_cap_abs: float,
    slippage_cost_per_trade: float,
    n_resamples: int = DEFAULT_RESAMPLES,
    seed: int = 0,
) -> dict:
    """Run every variant and return the report payload."""
    ruin = max_dd_cap_abs
    return {
        "n_trades": int(len(pnl)),
        "block_bootstrap": block_bootstrap(
            pnl, starting_balance, ruin, n_resamples=n_resamples, seed=seed).as_dict(),
        "trade_dropout": trade_dropout(
            pnl, starting_balance, ruin, n_resamples=n_resamples, seed=seed + 1).as_dict(),
        "execution_stress": execution_stress(
            pnl, starting_balance, ruin, slippage_cost_per_trade,
            n_resamples=n_resamples, seed=seed + 2).as_dict(),
        "same_bar_worst_case": same_bar_worst_case(trades, starting_balance, risk_per_trade),
        "concentration": concentration_test(pnl),
        "data_level_noise": {
            "status": "phase-2 stub",
            "note": "re-running real backtests on perturbed price series is the "
                    "strongest test available but costs real CLI runs; reserved "
                    "for the final candidate only (01-Research §5.3 item 6)",
        },
    }
