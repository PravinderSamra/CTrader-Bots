"""
/Trend-Continuation-Agent — Sub-Agent 4: Trade Card (numeric layer)

Spec §5. Computes the entry zone, SL, TP1/2/3, "AT ENTRY" vs "WATCH" status,
distance-to-entry, and (for WATCH cards) the recommended rescan time.

Note: the *rendering* of trade cards (box-drawing layout, Claude commentary)
is done by the orchestrating skill (see SKILL.md) from the structured dict
returned here — this module only does the maths.
"""

from __future__ import annotations

from config import (
    ATR_PERIOD,
    DAY_ENTRY_ZONE_HALFWIDTH_PCT,
    ENTRY_ZONE_HALFWIDTH_PCT,
    SL_ATR_MULTIPLIER,
    SL_SWING_BUFFER_ATR,
    SWING_LOOKBACK,
    SWING_N,
    TP1_R,
    TP2_R,
    TP3_R,
)
from agents.data_retrieval import InstrumentData
from utils.indicators import atr, find_swings
from utils.time_utils import compute_rescan_time, compute_rescan_time_15m, format_uk_short, now_utc


def build_trade_plan(data: InstrumentData, scored: dict) -> dict:
    """Returns `scored` enriched with entry zone, SL/TP, status and (for
    WATCH setups) a recommended rescan time."""
    direction = scored["direction"]
    bars_4h = data.bars_4h
    current_price = scored["current_price"]
    ema21_1h = scored["ema21_1h"]

    atr_4h = atr(bars_4h, ATR_PERIOD)[-1]

    # ── Entry zone: tight band around the 1H EMA21 (see config.py) ──────────
    half_width = abs(ema21_1h) * ENTRY_ZONE_HALFWIDTH_PCT
    entry_low = ema21_1h - half_width
    entry_high = ema21_1h + half_width
    entry_mid = ema21_1h

    # ── Stop loss (spec §5): wider of ATR-based and structure-based ─────────
    sl_atr_distance = SL_ATR_MULTIPLIER * atr_4h
    if direction == "LONG":
        sl_candidate = entry_mid - sl_atr_distance
        swing_lows = find_swings(bars_4h, "low", SWING_N, SWING_LOOKBACK)
        if swing_lows:
            sl_swing = swing_lows[-1]["price"] - SL_SWING_BUFFER_ATR * atr_4h
            sl = min(sl_candidate, sl_swing)  # lower = wider for LONG
        else:
            sl = sl_candidate
    else:
        sl_candidate = entry_mid + sl_atr_distance
        swing_highs = find_swings(bars_4h, "high", SWING_N, SWING_LOOKBACK)
        if swing_highs:
            sl_swing = swing_highs[-1]["price"] + SL_SWING_BUFFER_ATR * atr_4h
            sl = max(sl_candidate, sl_swing)  # higher = wider for SHORT
        else:
            sl = sl_candidate

    sl_distance = abs(entry_mid - sl)

    # ── Take profits: ATR-multiple-of-SL-distance from entry (spec §5) ──────
    sign = 1 if direction == "LONG" else -1
    tp1 = entry_mid + sign * TP1_R * sl_distance
    tp2 = entry_mid + sign * TP2_R * sl_distance
    tp3 = entry_mid + sign * TP3_R * sl_distance

    # ── Status: AT ENTRY ZONE vs WATCH (spec §5 — driven by S2) ──────────────
    at_entry = scored["scores"]["S2"] > 0
    status = "AT_ENTRY" if at_entry else "WATCH"

    if current_price > entry_high:
        distance_points = current_price - entry_high
        entry_zone_position = "above"
    elif current_price < entry_low:
        distance_points = entry_low - current_price
        entry_zone_position = "below"
    else:
        distance_points = 0.0
        entry_zone_position = "at"
    distance_pct = (distance_points / current_price * 100) if current_price else 0.0

    plan = {
        **scored,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_mid": entry_mid,
        "atr_4h": atr_4h,
        "status": status,
        "distance_points": distance_points,
        "distance_pct": distance_pct,
        "entry_zone_position": entry_zone_position,
        "sl": sl,
        "sl_distance": sl_distance,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "tp1_points": abs(tp1 - entry_mid),
        "tp2_points": abs(tp2 - entry_mid),
        "tp3_points": abs(tp3 - entry_mid),
    }

    if status == "WATCH":
        rescan_time = compute_rescan_time(now_utc())
        plan["rescan_time_utc"] = rescan_time
        plan["rescan_time_uk"] = format_uk_short(rescan_time)

    return plan


def build_trade_plans(top_n: list[tuple[InstrumentData, dict]]) -> list[dict]:
    """Convenience wrapper: build a trade plan for each (data, scored) pair."""
    return [build_trade_plan(data, scored) for data, scored in top_n]


def build_day_trade_plan(data: InstrumentData, scored: dict) -> dict:
    """
    Day Trade Pipeline (v1.1 §3.3/§3.4). Same shape as `build_trade_plan`,
    but: entry = current 15M EMA21 (not 1H EMA21), entry zone half-width =
    DAY_ENTRY_ZONE_HALFWIDTH_PCT (0.1%, vs swing's 0.03%), and SL is sized
    off 1H ATR vs the min/max low/high of the last 20 1H bars (vs swing's
    `find_swings`-confirmed 4H structure). TP1/2/3 use the same R-multiples.
    """
    direction = scored["direction"]
    current_price = scored["current_price"]
    ema21_15m = scored["ema21_15m"]
    atr_1h = scored["atr_1h"]

    # ── Entry zone: band around the 15M EMA21 (see config.py) ────────────────
    half_width = abs(ema21_15m) * DAY_ENTRY_ZONE_HALFWIDTH_PCT
    entry_low = ema21_15m - half_width
    entry_high = ema21_15m + half_width
    entry_mid = ema21_15m

    # ── Stop loss (spec §3.3): wider of ATR-based and last-20-1H-bar structure
    last_20_1h = data.bars_1h[-20:]
    sl_atr_distance = SL_ATR_MULTIPLIER * atr_1h
    if direction == "LONG":
        sl_atr = entry_mid - sl_atr_distance
        sl_swing = min(b.low for b in last_20_1h) - SL_SWING_BUFFER_ATR * atr_1h
        sl = min(sl_atr, sl_swing)  # lower = wider for LONG
    else:
        sl_atr = entry_mid + sl_atr_distance
        sl_swing = max(b.high for b in last_20_1h) + SL_SWING_BUFFER_ATR * atr_1h
        sl = max(sl_atr, sl_swing)  # higher = wider for SHORT

    sl_distance = abs(entry_mid - sl)

    # ── Take profits: same R multiples as swing pipeline ─────────────────────
    sign = 1 if direction == "LONG" else -1
    tp1 = entry_mid + sign * TP1_R * sl_distance
    tp2 = entry_mid + sign * TP2_R * sl_distance
    tp3 = entry_mid + sign * TP3_R * sl_distance

    # ── Status: AT ENTRY vs WATCH (spec §3.4 — driven by S2) ──────────────────
    at_entry = scored["scores"]["S2"] > 0
    status = "AT_ENTRY" if at_entry else "WATCH"

    if current_price > entry_high:
        distance_points = current_price - entry_high
        entry_zone_position = "above"
    elif current_price < entry_low:
        distance_points = entry_low - current_price
        entry_zone_position = "below"
    else:
        distance_points = 0.0
        entry_zone_position = "at"
    distance_pct = (distance_points / current_price * 100) if current_price else 0.0

    plan = {
        **scored,
        "entry_low": entry_low,
        "entry_high": entry_high,
        "entry_mid": entry_mid,
        "status": status,
        "distance_points": distance_points,
        "distance_pct": distance_pct,
        "entry_zone_position": entry_zone_position,
        "sl": sl,
        "sl_distance": sl_distance,
        "tp1": tp1,
        "tp2": tp2,
        "tp3": tp3,
        "tp1_points": abs(tp1 - entry_mid),
        "tp2_points": abs(tp2 - entry_mid),
        "tp3_points": abs(tp3 - entry_mid),
    }

    if status == "WATCH":
        rescan_time = compute_rescan_time_15m(now_utc())
        plan["rescan_time_utc"] = rescan_time
        plan["rescan_time_uk"] = format_uk_short(rescan_time)

    return plan


def build_day_trade_plans(top_n: list[tuple[InstrumentData, dict]]) -> list[dict]:
    """Convenience wrapper: build a day trade plan for each (data, scored) pair."""
    return [build_day_trade_plan(data, scored) for data, scored in top_n]
