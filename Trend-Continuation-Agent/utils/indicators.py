"""
/Trend-Continuation-Agent — Indicators (from scratch)

Spec §12 "Critical Implementation Rules":
  - EMA: standard exponential smoothing, multiplier = 2/(N+1), seeded with SMA
    of the first N values.
  - RSI / ATR / ADX: Wilder's smoothing (RMA), NOT a plain EMA.
  - ATR: true range = max(high-low, |high-prev_close|, |low-prev_close|).
  - Bar indexing: index -1 = latest COMPLETED bar (handled by callers, which
    pass already-trimmed bar lists).

All series functions return a list the same length as the input, padded with
``None`` where the value cannot yet be computed.
"""

from __future__ import annotations

from typing import Optional

from utils.mcp_client import Bar


# ── Moving averages / smoothing ─────────────────────────────────────────────
def sma(values: list[float], period: int) -> list[Optional[float]]:
    n = len(values)
    out: list[Optional[float]] = [None] * n
    if n < period:
        return out
    for i in range(period - 1, n):
        out[i] = sum(values[i - period + 1 : i + 1]) / period
    return out


def ema(values: list[float], period: int) -> list[Optional[float]]:
    """Standard EMA, multiplier = 2/(N+1), seeded with the SMA of the first N values."""
    n = len(values)
    out: list[Optional[float]] = [None] * n
    if n < period:
        return out
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    multiplier = 2.0 / (period + 1)
    for i in range(period, n):
        out[i] = (values[i] - out[i - 1]) * multiplier + out[i - 1]
    return out


def rma(values: list[float], period: int) -> list[Optional[float]]:
    """Wilder's smoothing (RMA): seeded with the SMA of the first N values,
    then RMA[i] = (RMA[i-1] * (period-1) + value[i]) / period."""
    n = len(values)
    out: list[Optional[float]] = [None] * n
    if n < period:
        return out
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    for i in range(period, n):
        out[i] = (out[i - 1] * (period - 1) + values[i]) / period
    return out


# ── RSI ──────────────────────────────────────────────────────────────────────
def rsi(closes: list[float], period: int = 14) -> list[Optional[float]]:
    """Wilder's RSI: RMA of gains / RMA of losses over `period` bars."""
    n = len(closes)
    out: list[Optional[float]] = [None] * n
    if n <= period:
        return out

    gains: list[float] = []
    losses: list[float] = []
    for i in range(1, n):
        change = closes[i] - closes[i - 1]
        gains.append(max(change, 0.0))
        losses.append(max(-change, 0.0))

    avg_gain = rma(gains, period)
    avg_loss = rma(losses, period)

    # gains[k] / avg_gain[k] correspond to original index k+1
    for i in range(period, n):
        ag = avg_gain[i - 1]
        al = avg_loss[i - 1]
        if ag is None or al is None:
            continue
        if al == 0:
            out[i] = 100.0
        else:
            rs = ag / al
            out[i] = 100.0 - (100.0 / (1.0 + rs))
    return out


# ── ATR ──────────────────────────────────────────────────────────────────────
def true_range(bars: list[Bar]) -> list[float]:
    n = len(bars)
    out: list[float] = [0.0] * n
    for i in range(n):
        if i == 0:
            out[i] = bars[i].high - bars[i].low
        else:
            out[i] = max(
                bars[i].high - bars[i].low,
                abs(bars[i].high - bars[i - 1].close),
                abs(bars[i].low - bars[i - 1].close),
            )
    return out


def atr(bars: list[Bar], period: int = 14) -> list[Optional[float]]:
    return rma(true_range(bars), period)


# ── ADX (Wilder's, +DI/-DI based) ───────────────────────────────────────────
def adx(bars: list[Bar], period: int = 14) -> tuple[list[Optional[float]], list[Optional[float]], list[Optional[float]]]:
    """Returns (adx, plus_di, minus_di) — each a list the same length as `bars`."""
    n = len(bars)
    plus_dm = [0.0] * n
    minus_dm = [0.0] * n
    for i in range(1, n):
        up_move = bars[i].high - bars[i - 1].high
        down_move = bars[i - 1].low - bars[i].low
        plus_dm[i] = up_move if (up_move > down_move and up_move > 0) else 0.0
        minus_dm[i] = down_move if (down_move > up_move and down_move > 0) else 0.0

    tr_vals = true_range(bars)
    atr_vals = rma(tr_vals, period)
    plus_dm_rma = rma(plus_dm, period)
    minus_dm_rma = rma(minus_dm, period)

    plus_di: list[Optional[float]] = [None] * n
    minus_di: list[Optional[float]] = [None] * n
    dx: list[Optional[float]] = [None] * n
    for i in range(n):
        a = atr_vals[i]
        pdm = plus_dm_rma[i]
        mdm = minus_dm_rma[i]
        if a is None or pdm is None or mdm is None or a == 0:
            continue
        plus_di[i] = 100.0 * pdm / a
        minus_di[i] = 100.0 * mdm / a
        denom = plus_di[i] + minus_di[i]
        dx[i] = 100.0 * abs(plus_di[i] - minus_di[i]) / denom if denom != 0 else 0.0

    # ADX = RMA of DX, seeded once `period` consecutive DX values exist
    first_dx = next((i for i, v in enumerate(dx) if v is not None), None)
    adx_vals: list[Optional[float]] = [None] * n
    if first_dx is not None and (n - first_dx) >= period:
        dx_sub = [v for v in dx[first_dx:]]  # type: ignore[misc]
        adx_sub = rma(dx_sub, period)  # type: ignore[arg-type]
        for offset, val in enumerate(adx_sub):
            adx_vals[first_dx + offset] = val

    return adx_vals, plus_di, minus_di


# ── Swing detection (spec §3 / §7 — used for G4 divergence) ────────────────
def find_swings(bars: list[Bar], kind: str, n: int = 3, lookback: int = 50) -> list[dict]:
    """
    Confirmed N-bar swing points within the last `lookback` bars.

    Swing high: bar[i].high > high of the `n` bars before AND after it.
    Swing low:  bar[i].low  < low  of the `n` bars before AND after it.

    Returns a list of {"idx": i, "price": value}, oldest first.
    """
    total = len(bars)
    start = max(n, total - lookback)
    end = total - n  # need n bars after i to confirm

    swings: list[dict] = []
    for i in range(start, end):
        if kind == "high":
            before = max(b.high for b in bars[i - n : i])
            after = max(b.high for b in bars[i + 1 : i + 1 + n])
            if bars[i].high > before and bars[i].high > after:
                swings.append({"idx": i, "price": bars[i].high})
        else:
            before = min(b.low for b in bars[i - n : i])
            after = min(b.low for b in bars[i + 1 : i + 1 + n])
            if bars[i].low < before and bars[i].low < after:
                swings.append({"idx": i, "price": bars[i].low})
    return swings


# ── Fibonacci levels (spec §8 S6) ────────────────────────────────────────────
def fibonacci_levels(swing_high: float, swing_low: float) -> dict[str, float]:
    """Retracement levels measured down from `swing_high`."""
    swing_range = swing_high - swing_low
    return {
        "0.0": swing_high,
        "0.236": swing_high - 0.236 * swing_range,
        "0.382": swing_high - 0.382 * swing_range,
        "0.618": swing_high - 0.618 * swing_range,
        "0.764": swing_high - 0.764 * swing_range,
        "1.0": swing_low,
    }
