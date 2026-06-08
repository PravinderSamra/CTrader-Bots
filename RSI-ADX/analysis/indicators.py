#!/usr/bin/env python3
"""
RSI / ADX / Rejection-candle analyser for cTrader trendbar JSON.

Input  (stdin or --file): the raw JSON object returned by mcp__ctrader__get_trendbars,
                          optionally with a top-level "symbol" key (e.g. "EURUSD")
                          used to auto-detect the pipette divisor.
Output (stdout):          a compact JSON summary — display-price OHLC, RSI(14),
                          ADX(14)/+DI/-DI, ADX-peak/decline state, and a rejection-
                          candle read on the most recently CLOSED bar.

Usage:
    python3 indicators.py --symbol EURUSD < trendbars.json
    python3 indicators.py --symbol XAUUSD --file candles.json
"""

import sys
import json
import argparse

# Known display-price ranges, used to auto-detect the pipette divisor (10^N).
# Same table as ctrader-mcp-integration-guide.md so behaviour matches the other agents.
PRICE_RANGES = {
    "EURUSD": (0.80, 1.60), "GBPUSD": (1.00, 1.70), "AUDUSD": (0.50, 1.10),
    "NZDUSD": (0.40, 0.90), "USDCHF": (0.75, 1.20), "USDCAD": (1.10, 1.65),
    "USDJPY": (100, 200),   "GBPJPY": (150, 260),   "EURJPY": (110, 190),
    "AUDJPY": (60, 130),    "EURGBP": (0.70, 0.95), "GBPAUD": (1.60, 2.30),
    "EURCAD": (1.30, 1.90), "GBPCAD": (1.60, 2.20),
    "XAUUSD": (1400, 8000), "XAGUSD": (15, 200),
    "US500":  (3000, 12000), "NAS100": (8000, 35000), "US30": (25000, 60000),
    "GER40":  (12000, 30000), "UK100": (6000, 13000), "FRA40": (5000, 12000),
    "EUSTX50": (3000, 8000), "JPN225": (15000, 100000), "AUS200": (5000, 12000),
    "HK50":   (13000, 35000),
    "WTOIL-PERP": (30, 130), "BRENTOIL-PERP": (30, 140), "NATGAS": (1.0, 20.0),
    "BTCUSD": (10000, 200000), "ETHUSD": (500, 10000), "SOLUSD": (10, 1000),
}


def detect_divisor(symbol, sample_price):
    key = (symbol or "").upper().replace("_SB", "")
    lo, hi = PRICE_RANGES.get(key, (0, 0))
    if lo and hi and sample_price > 0:
        for n in range(0, 10):
            if lo <= sample_price / (10 ** n) <= hi:
                return 10 ** n
    return 10 ** 5  # sane forex-style fallback


def wilder_smooth(values, period):
    """Wilder's smoothing — returns a list aligned to `values` (None for the warm-up window)."""
    out = [None] * len(values)
    if len(values) < period:
        return out
    seed = sum(values[:period]) / period
    out[period - 1] = seed
    prev = seed
    for i in range(period, len(values)):
        prev = (prev * (period - 1) + values[i]) / period
        out[i] = prev
    return out


def compute_rsi(closes, period=14):
    gains, losses = [0.0], [0.0]
    for i in range(1, len(closes)):
        delta = closes[i] - closes[i - 1]
        gains.append(max(delta, 0.0))
        losses.append(max(-delta, 0.0))

    avg_gain = wilder_smooth(gains, period + 1)
    avg_loss = wilder_smooth(losses, period + 1)

    rsi = [None] * len(closes)
    for i in range(len(closes)):
        if avg_gain[i] is None or avg_loss[i] is None:
            continue
        if avg_loss[i] == 0:
            rsi[i] = 100.0
        else:
            rs = avg_gain[i] / avg_loss[i]
            rsi[i] = 100.0 - (100.0 / (1.0 + rs))
    return rsi


def compute_adx(highs, lows, closes, period=14):
    n = len(closes)
    tr = [0.0] * n
    plus_dm = [0.0] * n
    minus_dm = [0.0] * n

    for i in range(1, n):
        up_move = highs[i] - highs[i - 1]
        down_move = lows[i - 1] - lows[i]
        plus_dm[i] = up_move if (up_move > down_move and up_move > 0) else 0.0
        minus_dm[i] = down_move if (down_move > up_move and down_move > 0) else 0.0
        tr[i] = max(
            highs[i] - lows[i],
            abs(highs[i] - closes[i - 1]),
            abs(lows[i] - closes[i - 1]),
        )

    atr = wilder_smooth(tr, period + 1)
    sm_plus = wilder_smooth(plus_dm, period + 1)
    sm_minus = wilder_smooth(minus_dm, period + 1)

    plus_di = [None] * n
    minus_di = [None] * n
    dx = [None] * n
    for i in range(n):
        if atr[i] in (None, 0) or sm_plus[i] is None or sm_minus[i] is None:
            continue
        plus_di[i] = 100.0 * sm_plus[i] / atr[i]
        minus_di[i] = 100.0 * sm_minus[i] / atr[i]
        denom = plus_di[i] + minus_di[i]
        dx[i] = 100.0 * abs(plus_di[i] - minus_di[i]) / denom if denom else 0.0

    # ADX = Wilder smoothed DX, seeded once the DX series itself starts
    first_dx = next((i for i, v in enumerate(dx) if v is not None), None)
    adx = [None] * n
    if first_dx is not None and n - first_dx >= period:
        clean_dx = dx[first_dx:]
        sm_adx = wilder_smooth(clean_dx, period)
        for i, v in enumerate(sm_adx):
            if v is not None:
                adx[first_dx + i] = v

    return plus_di, minus_di, adx


def adx_peak_state(adx, lookback=20, decline_floor=18.0, decline_margin=3.0):
    """Has ADX recently peaked above ~25 and is it now declining but not collapsed?"""
    series = [v for v in adx[-lookback:] if v is not None]
    if len(series) < 5:
        return {"available": False}

    current = series[-1]
    peak = max(series[:-1]) if len(series) > 1 else current
    peak_idx_from_end = len(series) - 1 - series[::-1].index(peak) if peak in series else None
    bars_since_peak = (len(series) - 1) - peak_idx_from_end if peak_idx_from_end is not None else None

    declining = (peak - current) >= decline_margin
    healthy_floor = current >= decline_floor
    had_real_trend = peak >= 25.0

    return {
        "available": True,
        "current": round(current, 1),
        "recent_peak": round(peak, 1),
        "bars_since_peak": bars_since_peak,
        "declining_from_peak": bool(declining and had_real_trend),
        "above_chop_floor": bool(healthy_floor),
        "exhaustion_signal": bool(declining and had_real_trend and healthy_floor),
    }


def rejection_read(o, h, l, c, body_max_pct=0.40, wick_min_pct=0.55):
    """Classify the candle's wick structure. Percentages are of the full H-L range."""
    rng = h - l
    if rng <= 0:
        return {"type": "none", "reason": "zero_range"}

    body = abs(c - o)
    upper_wick = h - max(o, c)
    lower_wick = min(o, c) - l

    body_pct = body / rng
    upper_pct = upper_wick / rng
    lower_pct = lower_wick / rng

    result = {
        "body_pct": round(body_pct, 2),
        "upper_wick_pct": round(upper_pct, 2),
        "lower_wick_pct": round(lower_pct, 2),
        "range": rng,
    }

    if lower_pct >= wick_min_pct and body_pct <= body_max_pct and lower_wick > upper_wick:
        result["type"] = "bullish_rejection"   # long lower wick — buyers defended, favours LONG
    elif upper_pct >= wick_min_pct and body_pct <= body_max_pct and upper_wick > lower_wick:
        result["type"] = "bearish_rejection"   # long upper wick — sellers defended, favours SHORT
    else:
        result["type"] = "none"

    return result


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--symbol", default="", help="Instrument name for pip-divisor auto-detection, e.g. EURUSD")
    ap.add_argument("--file", default="-", help="Path to trendbars JSON, or '-' for stdin (default)")
    ap.add_argument("--key-level-lookback", type=int, default=96,
                    help="How many of the supplied bars to scan for the swing high/low used as the 'key level' check")
    args = ap.parse_args()

    raw = sys.stdin.read() if args.file == "-" else open(args.file).read()
    data = json.loads(raw)
    bars = data.get("trendbars") or data.get("trendBars") or data.get("bars") or []
    if len(bars) < 30:
        print(json.dumps({"error": "not_enough_bars", "have": len(bars)}))
        return

    bars = sorted(bars, key=lambda b: b["timestamp"])
    divisor = detect_divisor(args.symbol or data.get("symbol", ""), bars[-1]["close"])

    o = [b["open"] / divisor for b in bars]
    h = [b["high"] / divisor for b in bars]
    l = [b["low"] / divisor for b in bars]
    c = [b["close"] / divisor for b in bars]
    v = [b.get("volume", 0) for b in bars]
    ts = [b["timestamp"] for b in bars]

    rsi = compute_rsi(c, 14)
    plus_di, minus_di, adx = compute_adx(h, l, c, 14)

    # Use the last fully CLOSED bar (index -2) — the final bar in the series may still be forming.
    idx = len(bars) - 2 if len(bars) >= 2 else len(bars) - 1
    rej = rejection_read(o[idx], h[idx], l[idx], c[idx])

    lookback = min(args.key_level_lookback, idx)
    window_h = h[idx - lookback:idx]
    window_l = l[idx - lookback:idx]
    swing_high = max(window_h) if window_h else None
    swing_low = min(window_l) if window_l else None

    avg_vol = sum(v[idx - 20:idx]) / max(1, len(v[idx - 20:idx])) if idx >= 1 else 0
    vol_ratio = (v[idx] / avg_vol) if avg_vol else None

    out = {
        "symbol": args.symbol or data.get("symbol", ""),
        "period": data.get("period", ""),
        "divisor": divisor,
        "bars_used": len(bars),
        "candle": {
            "timestamp": ts[idx], "open": o[idx], "high": h[idx],
            "low": l[idx], "close": c[idx], "volume": v[idx],
            "volume_vs_20avg": round(vol_ratio, 2) if vol_ratio else None,
        },
        "rsi": {
            "value": round(rsi[idx], 1) if rsi[idx] is not None else None,
            "oversold": bool(rsi[idx] is not None and rsi[idx] <= 30),
            "overbought": bool(rsi[idx] is not None and rsi[idx] >= 70),
        },
        "adx": {
            "value": round(adx[idx], 1) if adx[idx] is not None else None,
            "plus_di": round(plus_di[idx], 1) if plus_di[idx] is not None else None,
            "minus_di": round(minus_di[idx], 1) if minus_di[idx] is not None else None,
            **adx_peak_state(adx[: idx + 1]),
        },
        "rejection": rej,
        "key_levels": {
            "lookback_bars": lookback,
            "swing_high": swing_high,
            "swing_low": swing_low,
            "dist_to_swing_high_pct": round(abs(h[idx] - swing_high) / swing_high * 100, 3) if swing_high else None,
            "dist_to_swing_low_pct": round(abs(l[idx] - swing_low) / swing_low * 100, 3) if swing_low else None,
        },
        "current_price": c[-1],   # last (possibly still-forming) close — closest to live price
    }
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
