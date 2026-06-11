"""
/Trend-Continuation-Agent — Sub-Agent 2: Gate Layer

Spec §3 / §7. Applies four binary gates to each instrument's 4H data. All
four must pass for the instrument to proceed to scoring. Direction (LONG /
SHORT) is set by G2 (EMA stack) and confirmed by G3 (price side) — if they
disagree the instrument fails (no ambiguous direction).
"""

from __future__ import annotations

from config import ADX_PERIOD, EMA_FAST, EMA_MID, EMA_SLOW, GATE_ADX_MIN, RSI_PERIOD, SWING_LOOKBACK, SWING_N
from agents.data_retrieval import InstrumentData
from utils.indicators import adx, ema, find_swings, rsi


def evaluate_gates(data: InstrumentData) -> dict:
    """
    Returns the Gate Agent Output Schema (spec §3), plus a few extra fields
    (`fail_gate`, EMA values, RSI series) consumed by Sub-Agent 3 / 4.
    """
    bars = data.bars_4h
    closes = [b.close for b in bars]

    base = {
        "symbol": data.symbol,
        "passed": False,
        "direction": None,
        "gates": {
            "G1_adx": False,
            "G2_ema_stack": False,
            "G3_price_side": False,
            "G4_no_divergence": False,
        },
        "adx_value": None,
        "adx_previous": None,
        "adx_rising": False,
        "fail_gate": None,
    }

    # ── G1: Trend Exists (ADX rising and above threshold) ───────────────────
    adx_vals, _plus_di, _minus_di = adx(bars, ADX_PERIOD)
    adx_current = adx_vals[-1]
    adx_previous = adx_vals[-2]
    if adx_current is None or adx_previous is None:
        base["fail_gate"] = "G1_adx"
        return base

    g1_pass = (adx_current > GATE_ADX_MIN) and (adx_current > adx_previous)
    base["adx_value"] = adx_current
    base["adx_previous"] = adx_previous
    base["adx_rising"] = adx_current > adx_previous
    base["gates"]["G1_adx"] = g1_pass

    # ── G2: EMA Stack (also determines direction) ───────────────────────────
    ema21_series = ema(closes, EMA_FAST)
    ema50_series = ema(closes, EMA_MID)
    ema200_series = ema(closes, EMA_SLOW)
    ema21, ema50, ema200 = ema21_series[-1], ema50_series[-1], ema200_series[-1]

    if ema21 is None or ema50 is None or ema200 is None:
        base["fail_gate"] = "G2_ema_stack"
        return base

    bull_stack = ema21 > ema50 > ema200
    bear_stack = ema21 < ema50 < ema200
    g2_pass = bull_stack or bear_stack
    direction = "LONG" if bull_stack else ("SHORT" if bear_stack else None)

    base["gates"]["G2_ema_stack"] = g2_pass
    base["ema21_4h"] = ema21
    base["ema50_4h"] = ema50
    base["ema200_4h"] = ema200

    if direction is None:
        base["fail_gate"] = "G2_ema_stack"
        return base
    base["direction"] = direction

    # ── G3: Price Side ────────────────────────────────────────────────────────
    close_latest = closes[-1]
    if direction == "LONG":
        g3_pass = close_latest > ema21
    else:
        g3_pass = close_latest < ema21
    base["gates"]["G3_price_side"] = g3_pass

    if not g2_pass:
        base["fail_gate"] = "G2_ema_stack"
        return base
    if not g3_pass:
        base["fail_gate"] = "G3_price_side"
        return base
    if not g1_pass:
        base["fail_gate"] = "G1_adx"
        return base

    # ── G4: No Divergence ────────────────────────────────────────────────────
    rsi_vals = rsi(closes, RSI_PERIOD)
    swing_highs = find_swings(bars, "high", SWING_N, SWING_LOOKBACK)[-2:]
    swing_lows = find_swings(bars, "low", SWING_N, SWING_LOOKBACK)[-2:]

    g4_pass = True
    if direction == "LONG" and len(swing_highs) >= 2:
        sh1, sh2 = swing_highs[-2], swing_highs[-1]
        rsi_h1, rsi_h2 = rsi_vals[sh1["idx"]], rsi_vals[sh2["idx"]]
        if rsi_h1 is not None and rsi_h2 is not None:
            price_hh = sh2["price"] > sh1["price"]
            rsi_lh = rsi_h2 < rsi_h1
            g4_pass = not (price_hh and rsi_lh)
    elif direction == "SHORT" and len(swing_lows) >= 2:
        sl1, sl2 = swing_lows[-2], swing_lows[-1]
        rsi_l1, rsi_l2 = rsi_vals[sl1["idx"]], rsi_vals[sl2["idx"]]
        if rsi_l1 is not None and rsi_l2 is not None:
            price_ll = sl2["price"] < sl1["price"]
            rsi_hl = rsi_l2 > rsi_l1
            g4_pass = not (price_ll and rsi_hl)

    base["gates"]["G4_no_divergence"] = g4_pass
    base["passed"] = g1_pass and g2_pass and g3_pass and g4_pass
    if not g4_pass:
        base["fail_gate"] = "G4_no_divergence"

    return base
