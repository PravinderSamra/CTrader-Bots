"""
/Trend-Continuation-Agent — Sub-Agent 2: Gate Layer

Spec §3 / §7. Applies four binary gates to each instrument's data. All four
must pass for the instrument to proceed to scoring. Direction (LONG / SHORT)
is set by G2 (EMA stack) and confirmed by G3 (price side) — if they disagree
the instrument fails (no ambiguous direction).

Day Trade Pipeline (v1.1 §2.1-§2.3): the same 4-gate cascade also runs on 1H
bars (different ADX threshold / divergence lookback) via `day_trade_gates`,
which additionally computes a non-excluding 4H directional-bias check from
the already-fetched 4H bars.
"""

from __future__ import annotations

from config import (
    ADX_1H_MIN,
    ADX_PERIOD,
    EMA_FAST,
    EMA_MID,
    EMA_SLOW,
    GATE_ADX_MIN,
    RSI_PERIOD,
    SWING_LOOKBACK,
    SWING_LOOKBACK_1H,
    SWING_N,
)
from agents.data_retrieval import InstrumentData
from utils.indicators import adx, ema, find_swings, rsi
from utils.mcp_client import Bar


def _run_gate_cascade(bars: list[Bar], adx_min: float, swing_lookback: int) -> dict:
    """
    Shared 4-gate cascade (spec §3) over an arbitrary bar series. Returns
    `passed`, `direction`, `gates`, `adx_value`, `adx_previous`, `adx_rising`,
    `fail_gate`, and `ema21`/`ema50`/`ema200` (the EMA values used for
    G2/G3, on whatever timeframe `bars` represents).
    """
    closes = [b.close for b in bars]

    base = {
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
        "ema21": None,
        "ema50": None,
        "ema200": None,
    }

    # ── G1: Trend Exists (ADX rising and above threshold) ───────────────────
    adx_vals, _plus_di, _minus_di = adx(bars, ADX_PERIOD)
    adx_current = adx_vals[-1]
    adx_previous = adx_vals[-2]
    if adx_current is None or adx_previous is None:
        base["fail_gate"] = "G1_adx"
        return base

    g1_pass = (adx_current > adx_min) and (adx_current > adx_previous)
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
    base["ema21"] = ema21
    base["ema50"] = ema50
    base["ema200"] = ema200

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
    swing_highs = find_swings(bars, "high", SWING_N, swing_lookback)[-2:]
    swing_lows = find_swings(bars, "low", SWING_N, swing_lookback)[-2:]

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


def evaluate_gates(data: InstrumentData) -> dict:
    """
    Swing pipeline (spec §3/§7): 4-gate cascade on 4H bars using
    GATE_ADX_MIN (25) and SWING_LOOKBACK (50). Returns the Gate Agent Output
    Schema (spec §3), plus `ema21_4h`/`ema50_4h`/`ema200_4h` consumed by
    Sub-Agent 3 / 4.
    """
    result = _run_gate_cascade(data.bars_4h, GATE_ADX_MIN, SWING_LOOKBACK)
    return {
        "symbol": data.symbol,
        **{k: v for k, v in result.items() if k not in ("ema21", "ema50", "ema200")},
        "ema21_4h": result["ema21"],
        "ema50_4h": result["ema50"],
        "ema200_4h": result["ema200"],
    }


def day_trade_gates(data: InstrumentData) -> dict:
    """
    Day Trade Pipeline (v1.1 §2.1-§2.3): same 4-gate cascade as
    `evaluate_gates`, but on 1H bars with day-trade thresholds (ADX_1H_MIN=22,
    SWING_LOOKBACK_1H=30, SWING_N unchanged).

    Also computes a NON-EXCLUDING 4H directional-bias check (v1.1 §2.1) from
    the already-fetched 4H bars: whether the 4H EMA21/50/200 stack agrees
    with the 1H-determined direction. This does not gate the instrument — it
    feeds Sub-Agent 3's DAY_BONUS_4H scoring bonus.
    """
    result = _run_gate_cascade(data.bars_1h, ADX_1H_MIN, SWING_LOOKBACK_1H)
    direction = result["direction"]

    closes_4h = [b.close for b in data.bars_4h]
    ema21_4h = ema(closes_4h, EMA_FAST)[-1]
    ema50_4h = ema(closes_4h, EMA_MID)[-1]
    ema200_4h = ema(closes_4h, EMA_SLOW)[-1]

    bias_known = ema21_4h is not None and ema50_4h is not None and ema200_4h is not None
    bias_4h_bull = bias_known and ema21_4h > ema50_4h > ema200_4h
    bias_4h_bear = bias_known and ema21_4h < ema50_4h < ema200_4h
    bias_4h_aligned = (direction == "LONG" and bias_4h_bull) or (direction == "SHORT" and bias_4h_bear)

    return {
        "symbol": data.symbol,
        **{k: v for k, v in result.items() if k not in ("ema21", "ema50", "ema200")},
        "ema21_1h": result["ema21"],
        "ema50_1h": result["ema50"],
        "ema200_1h": result["ema200"],
        "ema21_4h": ema21_4h,
        "ema50_4h": ema50_4h,
        "ema200_4h": ema200_4h,
        "bias_4h_bull": bias_4h_bull,
        "bias_4h_bear": bias_4h_bear,
        "bias_4h_aligned": bias_4h_aligned,
    }
