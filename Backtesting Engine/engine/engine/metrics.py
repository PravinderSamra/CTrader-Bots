"""Canonical performance metrics (build-spec §7, formulas from 01-Research §4.3).

Every stage of the pipeline scores through this module, so the definitions live in
exactly one place. All functions are pure over the canonical structures defined in
``engine.results``.

Conventions:
  * Daily returns come from mark-to-market equity resampled to calendar days,
    forward-filled across flat days, expressed as simple returns on the nominal
    account balance.
  * Annualisation uses 252 trading days, risk-free rate 0.
  * R = ``account.risk_per_trade``; fixed-risk sizing is what makes expectancy
    in R comparable across trials.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
import pandas as pd

TRADING_DAYS = 252

# A standard deviation below this (relative to the mean's magnitude) is
# floating-point noise, not dispersion. Without this guard a degenerate
# constant-return curve yields a Sharpe around 1e16 and wins every search —
# the most dangerous kind of bug in an optimiser, because it looks like a result.
_DEGENERATE_SD = 1e-12


def _is_degenerate(sd: float, mean: float) -> bool:
    return (not math.isfinite(sd)) or sd <= _DEGENERATE_SD * max(1.0, abs(mean))


@dataclass(frozen=True)
class Metrics:
    trades: int
    trades_per_year: float
    net_profit: float
    profit_factor: float
    win_rate: float
    sharpe: float
    sortino: float
    max_dd_pct: float
    max_dd_abs: float
    max_dd_peak: pd.Timestamp | None
    max_dd_trough: pd.Timestamp | None
    calmar: float
    cagr: float
    expectancy_r: float
    sqn: float
    ulcer: float
    longest_loss_streak: int
    time_under_water_days: float

    def as_dict(self) -> dict:
        d = {k: getattr(self, k) for k in self.__dataclass_fields__}
        for key in ("max_dd_peak", "max_dd_trough"):
            v = d[key]
            d[key] = v.isoformat() if isinstance(v, pd.Timestamp) else None
        return d


def daily_returns(equity: pd.Series, nominal_balance: float) -> pd.Series:
    """Equity curve → daily simple returns on the nominal account.

    ``equity`` is a timestamp-indexed series of account equity. Days with no marks
    inherit the previous close (flat), matching the "no trading, no return" reality.
    """
    if equity.empty:
        return pd.Series(dtype="float64")
    daily = equity.resample("1D").last().ffill().dropna()
    return daily.diff().dropna() / nominal_balance


def sharpe_ratio(returns: pd.Series) -> float:
    """Annualised Sharpe, rf = 0. Zero variance → 0.0, never inf."""
    if len(returns) < 2:
        return 0.0
    mean = float(returns.mean())
    sd = float(returns.std(ddof=1))
    if _is_degenerate(sd, mean):
        return 0.0
    return float(mean / sd * math.sqrt(TRADING_DAYS))


def sortino_ratio(returns: pd.Series) -> float:
    """Annualised Sortino: downside deviation measured against a 0 target."""
    if len(returns) < 2:
        return 0.0
    downside = returns[returns < 0]
    if downside.empty:
        return 0.0
    mean = float(returns.mean())
    dd = float(np.sqrt((downside**2).mean()))
    if _is_degenerate(dd, mean):
        return 0.0
    return float(mean / dd * math.sqrt(TRADING_DAYS))


def profit_factor(pnl: pd.Series) -> float:
    """Sum of wins / |sum of losses| on closed trades. No losses → inf."""
    wins = float(pnl[pnl > 0].sum())
    losses = float(abs(pnl[pnl < 0].sum()))
    if losses == 0:
        return math.inf if wins > 0 else 0.0
    return wins / losses


def max_drawdown(equity: pd.Series, nominal_balance: float) -> tuple[float, float, pd.Timestamp | None, pd.Timestamp | None]:
    """Peak-to-trough drawdown → (pct of nominal, absolute, peak time, trough time)."""
    if equity.empty:
        return 0.0, 0.0, None, None
    running_peak = equity.cummax()
    dd = equity - running_peak
    trough = dd.idxmin()
    worst = float(dd.loc[trough])
    if worst >= 0:
        return 0.0, 0.0, None, None
    peak = equity.loc[:trough].idxmax()
    return abs(worst) / nominal_balance * 100.0, abs(worst), peak, trough


def ulcer_index(equity: pd.Series) -> float:
    """RMS of percentage drawdown — penalises depth *and* duration."""
    if equity.empty:
        return 0.0
    peak = equity.cummax()
    pct_dd = (equity - peak) / peak.replace(0, np.nan) * 100.0
    return float(np.sqrt((pct_dd.fillna(0.0) ** 2).mean()))


def time_under_water(equity: pd.Series) -> float:
    """Days spent below the previous equity peak."""
    if equity.empty:
        return 0.0
    under = equity < equity.cummax()
    if not under.any():
        return 0.0
    seconds = under.astype(int).mul(
        pd.Series(equity.index, index=equity.index).diff().dt.total_seconds().fillna(0.0)
    ).sum()
    return float(seconds / 86400.0)


def longest_losing_streak(pnl: pd.Series) -> int:
    longest = current = 0
    for v in pnl:
        if v < 0:
            current += 1
            longest = max(longest, current)
        else:
            current = 0
    return longest


def sqn(r_multiples: pd.Series) -> float:
    """Van Tharp System Quality Number — reported, never optimised."""
    n = len(r_multiples)
    if n < 2:
        return 0.0
    mean = float(r_multiples.mean())
    sd = float(r_multiples.std(ddof=1))
    if _is_degenerate(sd, mean):
        return 0.0
    return float(math.sqrt(n) * mean / sd)


def cagr(equity: pd.Series, nominal_balance: float) -> float:
    """Compound annual growth rate over the equity curve's span."""
    if len(equity) < 2:
        return 0.0
    years = (equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 86400)
    if years <= 0:
        return 0.0
    start, end = nominal_balance, float(equity.iloc[-1])
    if start <= 0 or end <= 0:
        return 0.0
    return float((end / start) ** (1 / years) - 1) * 100.0


def compute(
    trade_pnl: pd.Series,
    equity: pd.Series,
    nominal_balance: float,
    risk_per_trade: float,
) -> Metrics:
    """Compute the full metric set from closed-trade P&L and an equity curve."""
    pnl = pd.Series(trade_pnl, dtype="float64").reset_index(drop=True)
    equity = pd.Series(equity, dtype="float64").sort_index()

    span_years = 0.0
    if len(equity) >= 2:
        span_years = (equity.index[-1] - equity.index[0]).total_seconds() / (365.25 * 86400)

    rets = daily_returns(equity, nominal_balance)
    dd_pct, dd_abs, dd_peak, dd_trough = max_drawdown(equity, nominal_balance)
    r_multiples = pnl / risk_per_trade if risk_per_trade else pnl * 0.0
    growth = cagr(equity, nominal_balance)

    return Metrics(
        trades=len(pnl),
        trades_per_year=float(len(pnl) / span_years) if span_years > 0 else 0.0,
        net_profit=float(pnl.sum()),
        profit_factor=profit_factor(pnl),
        win_rate=float((pnl > 0).mean() * 100.0) if len(pnl) else 0.0,
        sharpe=sharpe_ratio(rets),
        sortino=sortino_ratio(rets),
        max_dd_pct=dd_pct,
        max_dd_abs=dd_abs,
        max_dd_peak=dd_peak,
        max_dd_trough=dd_trough,
        calmar=float(growth / dd_pct) if dd_pct > 0 else 0.0,
        cagr=growth,
        expectancy_r=float(r_multiples.mean()) if len(r_multiples) else 0.0,
        sqn=sqn(r_multiples),
        ulcer=ulcer_index(equity),
        longest_loss_streak=longest_losing_streak(pnl),
        time_under_water_days=time_under_water(equity),
    )


def suspicion_flags(m: Metrics) -> list[str]:
    """Patterns that usually mean a fill artefact rather than an edge (§4.3).

    These are a *filter for human attention*, never an optimisation target.
    """
    flags = []
    if m.profit_factor > 4 and m.trades < 100:
        flags.append(f"profit factor {m.profit_factor:.2f} on only {m.trades} trades")
    if m.win_rate > 85 and m.trades < 100:
        flags.append(f"win rate {m.win_rate:.1f}% on only {m.trades} trades")
    if m.trades and m.max_dd_pct == 0:
        flags.append("zero drawdown recorded — check the equity reconstruction")
    return flags
