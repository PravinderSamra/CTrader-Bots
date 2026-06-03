"""
Delta and Order Flow Analysis — Tier 1 Data Only

This module only produces meaningful output when given Binance/Bybit
kline data that includes taker buy volume. For all other markets
(forex, indices, commodities), delta analysis is NOT available and
this module returns clear 'No Tier 1 Data' labels.

Real delta = taker_buy_volume - taker_sell_volume per candle.
Cumulative delta = running sum of delta across the session.
"""

from typing import List, Optional
from data.models import Candle, DeltaBar
from config import DELTA_CONFIRMATION_THRESHOLD


TIER1_UNAVAILABLE = {
    "available": False,
    "reason": (
        "Delta analysis requires tick-level taker buy/sell volume data. "
        "This is only available for crypto via Binance/Bybit public APIs. "
        "For forex and futures, use Bookmap, Sierra Chart, or ATAS to assess "
        "real order flow at this level before entering."
    ),
}


def compute_delta_bars(candles: List[Candle]) -> List[DeltaBar]:
    """
    Convert Tier 1 candles (with taker_buy_volume) into DeltaBar objects.
    Returns empty list if data is not Tier 1.
    """
    if not candles or candles[0].data_tier != 1:
        return []

    bars = []
    cumulative = 0.0

    for c in candles:
        if c.taker_buy_volume is None:
            continue
        delta = c.delta or 0.0
        cumulative += delta

        bars.append(DeltaBar(
            symbol=c.symbol,
            timestamp=c.timestamp,
            timeframe=c.timeframe,
            delta=delta,
            cumulative_delta=cumulative,
            taker_buy_pct=c.delta_pct or 0.5,
            data_source="binance",
        ))

    # Detect divergences across the series
    _flag_divergences(bars, candles)
    _flag_absorption(bars, candles)

    return bars


def compute_session_summary(candles: List[Candle]) -> dict:
    """
    Summarise delta for a session (or any window of Tier 1 candles).
    Returns a labelled dict ready for inclusion in reports.
    """
    if not candles or candles[0].data_tier != 1:
        return TIER1_UNAVAILABLE

    bars = compute_delta_bars(candles)
    if not bars:
        return TIER1_UNAVAILABLE

    total_buy  = sum(c.taker_buy_volume  or 0 for c in candles)
    total_sell = sum(c.taker_sell_volume or 0 for c in candles)
    total_vol  = total_buy + total_sell
    taker_buy_pct = total_buy / total_vol if total_vol > 0 else 0.5

    cvd_final = bars[-1].cumulative_delta
    cvd_start = bars[0].cumulative_delta - bars[0].delta

    any_bearish_div = any(b.bearish_divergence for b in bars)
    any_bullish_div = any(b.bullish_divergence for b in bars)
    any_absorption  = any(b.absorption_signal  for b in bars)

    bias = _bias_label(taker_buy_pct)

    return {
        "available": True,
        "data_tier": 1,
        "taker_buy_pct":  round(taker_buy_pct, 4),
        "taker_sell_pct": round(1 - taker_buy_pct, 4),
        "cumulative_delta": round(cvd_final, 4),
        "cvd_direction": "rising" if cvd_final > cvd_start else "falling",
        "bias": bias,
        "bearish_divergence": any_bearish_div,
        "bullish_divergence": any_bullish_div,
        "absorption_detected": any_absorption,
        "confirmation": _confirmation_label(taker_buy_pct, any_bearish_div, any_bullish_div),
    }


def check_delta_at_level(
    candles: List[Candle],
    level: float,
    direction: str,
    tolerance_pct: float = 0.002,
) -> dict:
    """
    Assess delta behaviour specifically when price is near a key level
    (OB, FVG, liquidity pool).

    direction: 'bullish' (we're looking for buyer defence) or
               'bearish' (looking for seller defence)

    Returns Tier 1 confirmation or 'No data' label.
    """
    if not candles or candles[0].data_tier != 1:
        return {
            **TIER1_UNAVAILABLE,
            "level": level,
            "manual_check": (
                f"At level {level}: check footprint for absorption (large volume, "
                f"price not moving through), delta divergence, and DOM for defended "
                f"{'bids' if direction == 'bullish' else 'offers'}."
            ),
        }

    # Filter candles where price was near the level
    near_level = [
        c for c in candles
        if abs(c.low - level) / level <= tolerance_pct
        or abs(c.high - level) / level <= tolerance_pct
        or (c.low <= level <= c.high)
    ]

    if not near_level:
        return {
            "available": True,
            "data_tier": 1,
            "near_level_candles": 0,
            "result": "Price has not yet reached this level in the fetched data.",
        }

    buy_at_level  = sum(c.taker_buy_volume  or 0 for c in near_level)
    sell_at_level = sum(c.taker_sell_volume or 0 for c in near_level)
    total_at_level = buy_at_level + sell_at_level
    buy_pct = buy_at_level / total_at_level if total_at_level > 0 else 0.5

    confirmed = (
        (direction == "bullish" and buy_pct >= DELTA_CONFIRMATION_THRESHOLD) or
        (direction == "bearish" and buy_pct <= (1 - DELTA_CONFIRMATION_THRESHOLD))
    )

    return {
        "available": True,
        "data_tier": 1,
        "level": level,
        "near_level_candles": len(near_level),
        "taker_buy_pct_at_level": round(buy_pct, 4),
        "taker_sell_pct_at_level": round(1 - buy_pct, 4),
        "tier1_confirmed": confirmed,
        "result": (
            f"{'✅ CONFIRMED' if confirmed else '❌ NOT CONFIRMED'} — "
            f"Taker buy: {buy_pct:.1%} | Taker sell: {1-buy_pct:.1%} at this level. "
            + (f"Buyers aggressively defending." if confirmed and direction == "bullish"
               else f"Sellers aggressively defending." if confirmed and direction == "bearish"
               else f"No clear aggression bias at this level.")
        ),
    }


# ─── PRIVATE HELPERS ─────────────────────────────────────────────────────────

def _flag_divergences(bars: List[DeltaBar], candles: List[Candle]):
    """
    Flag bearish and bullish delta divergences.
    Bearish: price makes HH but delta makes LH.
    Bullish: price makes LL but delta makes HL.
    """
    for i in range(2, len(bars)):
        price_hh = candles[i].high > candles[i - 1].high
        delta_lh  = bars[i].cumulative_delta < bars[i - 1].cumulative_delta
        if price_hh and delta_lh:
            bars[i].bearish_divergence = True

        price_ll  = candles[i].low < candles[i - 1].low
        delta_hl  = bars[i].cumulative_delta > bars[i - 1].cumulative_delta
        if price_ll and delta_hl:
            bars[i].bullish_divergence = True


def _flag_absorption(bars: List[DeltaBar], candles: List[Candle]):
    """
    Flag absorption: large delta (aggression) but minimal price movement.
    This is the closest we can get to absorption detection without tick data.
    """
    if not candles:
        return

    avg_body = sum(c.body_size for c in candles) / len(candles)
    avg_vol  = sum(c.volume     for c in candles) / len(candles)

    for i, bar in enumerate(bars):
        c = candles[i]
        high_volume   = c.volume > avg_vol * 1.5
        small_body    = c.body_size < avg_body * 0.5
        if high_volume and small_body:
            bar.absorption_signal = True


def _bias_label(taker_buy_pct: float) -> str:
    if taker_buy_pct >= 0.58:
        return f"BUYERS dominating — {taker_buy_pct:.1%} taker buys"
    elif taker_buy_pct <= 0.42:
        return f"SELLERS dominating — {1 - taker_buy_pct:.1%} taker sells"
    return f"BALANCED — {taker_buy_pct:.1%} taker buy / {1 - taker_buy_pct:.1%} sell"


def _confirmation_label(
    buy_pct: float,
    bearish_div: bool,
    bullish_div: bool,
) -> str:
    parts = [_bias_label(buy_pct)]
    if bearish_div:
        parts.append("⚠️  BEARISH DELTA DIVERGENCE — price making new highs with declining CVD")
    if bullish_div:
        parts.append("⚠️  BULLISH DELTA DIVERGENCE — price making new lows with rising CVD")
    return " | ".join(parts)
