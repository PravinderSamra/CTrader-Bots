"""
/Trend-Continuation-Agent — Sub-Agent 3: Scoring & Ranking

Spec §4 / §8. Scores every gate-passed instrument across 6 non-correlated
signals (max 100), assigns a tier, and returns a sorted ranking.

Tier bands (spec §4): A 75-100, B 50-74, C 30-49. Scores below TIER_C_MIN
(30) are not actionable in any tier and are dropped entirely (gates passed
but conviction is too low to even watch).
"""

from __future__ import annotations

from config import (
    ATR_PERIOD,
    EMA_FAST,
    EMA_MID,
    EMA_SLOW,
    RSI_PERIOD,
    TIER_A_MIN,
    TIER_B_MIN,
    TIER_C_MIN,
)
from agents.data_retrieval import InstrumentData
from utils.indicators import atr, ema, fibonacci_levels, rsi


def score_instrument(data: InstrumentData, gate_result: dict) -> dict:
    """Returns `gate_result` enriched with `scores`, `total_score`, `tier`,
    and the 1H indicator values used elsewhere (trade card / commentary)."""
    direction = gate_result["direction"]
    adx_value = gate_result["adx_value"]

    closes_1h = [b.close for b in data.bars_1h]
    ema21_1h = ema(closes_1h, EMA_FAST)[-1]
    ema50_1h = ema(closes_1h, EMA_MID)[-1]
    ema200_1h = ema(closes_1h, EMA_SLOW)[-1]
    rsi_1h = rsi(closes_1h, RSI_PERIOD)[-1]
    atr_1h = atr(data.bars_1h, ATR_PERIOD)[-1]

    current_price = data.spot_bid

    # ── S1: ADX Strength (max 20) ────────────────────────────────────────────
    if adx_value >= 40:
        s1 = 20
    elif adx_value >= 30:
        s1 = 15
    elif adx_value >= 25:
        s1 = 10
    else:
        s1 = 0  # shouldn't reach here — G1 requires ADX > 25

    # ── S2: 1H EMA21 Pullback Proximity (max 20) ─────────────────────────────
    ema21_distance_pct = abs(current_price - ema21_1h) / ema21_1h * 100
    if ema21_distance_pct <= 0.3:
        s2 = 20
    elif ema21_distance_pct <= 0.75:
        s2 = 10
    else:
        s2 = 0

    # ── S3: 1H RSI Momentum Zone (max 15) ────────────────────────────────────
    if rsi_1h is None:
        s3 = 0
    elif direction == "LONG":
        s3 = 15 if 45 <= rsi_1h <= 65 else 0
    else:
        s3 = 15 if 35 <= rsi_1h <= 55 else 0

    # ── S4: ATR Range Guard (max 15) ─────────────────────────────────────────
    current_bar_range = data.bars_1h[-1].high - data.bars_1h[-1].low
    atr_ratio = (current_bar_range / atr_1h) if atr_1h else None
    if atr_ratio is None:
        s4 = 0
    elif atr_ratio < 1.0:
        s4 = 15
    elif atr_ratio < 1.5:
        s4 = 8
    else:
        s4 = 0

    # ── S5: Multi-Timeframe EMA Alignment (max 15) ───────────────────────────
    bull_1h = ema21_1h > ema50_1h > ema200_1h
    bear_1h = ema21_1h < ema50_1h < ema200_1h
    if direction == "LONG":
        s5 = 15 if bull_1h else 0
    else:
        s5 = 15 if bear_1h else 0

    # ── S6: Fibonacci Retracement Zone (max 15) ──────────────────────────────
    last_50_4h = data.bars_4h[-50:]
    swing_high_ref = max(b.high for b in last_50_4h)
    swing_low_ref = min(b.low for b in last_50_4h)
    fib = fibonacci_levels(swing_high_ref, swing_low_ref)
    swing_range = swing_high_ref - swing_low_ref
    fib_retracement_pct = ((swing_high_ref - current_price) / swing_range * 100) if swing_range else None

    # The 38.2-61.8% zone is a fixed price band regardless of direction —
    # checking current_price against it is correct for both LONG and SHORT.
    # fibonacci_levels() returns levels in descending order (0.0 = swing_high
    # down to 1.0 = swing_low), so the "deeper" retracement level is the
    # lower bound of each band.
    if fib["0.618"] <= current_price <= fib["0.382"]:
        s6 = 15
    elif (fib["0.764"] <= current_price <= fib["0.618"]) or (fib["0.382"] <= current_price <= fib["0.236"]):
        s6 = 8
    else:
        s6 = 0

    scores = {"S1": s1, "S2": s2, "S3": s3, "S4": s4, "S5": s5, "S6": s6}
    total_score = sum(scores.values())

    if total_score >= TIER_A_MIN:
        tier = "A"
    elif total_score >= TIER_B_MIN:
        tier = "B"
    elif total_score >= TIER_C_MIN:
        tier = "C"
    else:
        tier = None  # below watch threshold — not actionable

    return {
        **gate_result,
        "scores": scores,
        "total_score": total_score,
        "tier": tier,
        "current_price": current_price,
        "ema21_1h": ema21_1h,
        "ema50_1h": ema50_1h,
        "ema200_1h": ema200_1h,
        "rsi_1h": rsi_1h,
        "atr_1h": atr_1h,
        "fib_levels": fib,
        "fib_swing_high": swing_high_ref,
        "fib_swing_low": swing_low_ref,
        # Pre-computed display values for the §9 trade card / commentary
        # (Sub-Agent 4 / SKILL.md) — keeps all numeric work in Python.
        "ema21_distance_pct": ema21_distance_pct,
        "atr_ratio": atr_ratio,
        "fib_retracement_pct": fib_retracement_pct,
    }


def rank_instruments(scored: list[dict]) -> dict:
    """
    Spec §4 "Ranking Output": Tier A first (highest score first), then Tier
    B. Tier C goes to a separate `watchlist`. Returns the top-10 (A+B) plus
    the watchlist.
    """
    actionable = [s for s in scored if s["tier"] in ("A", "B")]
    watchlist = [s for s in scored if s["tier"] == "C"]

    actionable.sort(key=lambda s: (0 if s["tier"] == "A" else 1, -s["total_score"]))
    watchlist.sort(key=lambda s: -s["total_score"])

    return {
        "ranked": actionable[:10],
        "watchlist": watchlist,
    }
