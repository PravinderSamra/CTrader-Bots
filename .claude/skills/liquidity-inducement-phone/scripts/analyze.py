#!/usr/bin/env python3
"""
analyze.py — deterministic intraday liquidity + bias + expansion analyzer for
the Marco Trades "Liquidity Inducement" model, driven by cTrader OHLCV over HTTP.

This is the MECHANICAL layer (like the ORB intel's computeOrbIntel): it turns
raw bars into a structured, reproducible JSON "read" — bias/trend, liquidity
pools, room-for-expansion, volume state. The AGENT (Opus) reads this JSON plus
the strategy references and produces the actual trade idea. Numbers here are
facts; the trade decision is the agent's.

READ ONLY. No orders are placed.

Usage:
    export CTRADER_MCP_TOKEN=...        # your account bearer token
    python3 analyze.py UK100            # index, default exec TF M_5
    python3 analyze.py XAUUSD --exec M_5
    python3 analyze.py US30 --exec M_15 --json      # raw JSON only
    python3 analyze.py --dry-run        # synthetic self-test, no token needed
"""

import sys
import json
import argparse
import statistics
from datetime import datetime, timezone

try:
    import ctrader_http as ct
except Exception:  # allow running from another dir
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    import ctrader_http as ct


# ── small structure helpers ──────────────────────────────────────────────────
def _pivots(bars, k=2):
    """Return (swing_highs, swing_lows) as lists of (index, price). A swing high
    at i = high[i] strictly >= the k bars either side; mirror for lows."""
    highs, lows = [], []
    n = len(bars)
    for i in range(k, n - k):
        hi = bars[i]["high"]
        lo = bars[i]["low"]
        if all(hi >= bars[j]["high"] for j in range(i - k, i + k + 1) if j != i):
            highs.append((i, hi))
        if all(lo <= bars[j]["low"] for j in range(i - k, i + k + 1) if j != i):
            lows.append((i, lo))
    return highs, lows


def _cluster(levels, tol):
    """Cluster nearby price levels into pools. levels: list of floats.
    Returns list of {price, touches} sorted by touches desc."""
    if not levels:
        return []
    pts = sorted(levels)
    clusters = [[pts[0]]]
    for p in pts[1:]:
        if abs(p - clusters[-1][-1]) <= tol:
            clusters[-1].append(p)
        else:
            clusters.append([p])
    out = [{"price": round(statistics.mean(c), 5), "touches": len(c)}
           for c in clusters]
    out.sort(key=lambda x: (-x["touches"], x["price"]))
    return out


def _adr(daily_completed, n=14):
    ranges = [b["high"] - b["low"] for b in daily_completed[-n:]]
    return round(statistics.mean(ranges), 5) if ranges else 0.0


def _sma(closes, n):
    if len(closes) < n:
        n = len(closes)
    return sum(closes[-n:]) / n if n else 0.0


# ── the analysis ─────────────────────────────────────────────────────────────
def analyze(instrument, exec_period="M_5",
            d1=None, h1=None, ex=None, live=None):
    """Pure computation over already-fetched bars (so it is dry-run testable)."""
    warnings = []
    if not d1 or len(d1) < 5:
        return {"error": "insufficient daily data", "instrument": instrument}

    today = d1[-1]                       # forming daily bar
    completed = d1[:-1]                  # closed daily bars
    prior = completed[-1]                # yesterday
    closes_d = [b["close"] for b in completed]

    price = None
    if live:
        price = round((live[0] + live[1]) / 2, 5)
    if price is None:
        price = ex[-1]["close"] if ex else today["close"]

    adr14 = _adr(completed, 14)
    today_range = today["high"] - today["low"]
    adr_used_pct = round(100 * today_range / adr14, 1) if adr14 else None
    remaining_budget = round(max(adr14 - today_range, adr14 * 0.05), 5) if adr14 else None

    # previous ISO week high/low from completed dailies
    def iso_wk(b):
        return b["time"].isocalendar()[:2]
    this_wk = iso_wk(today)
    prev_wk_bars = [b for b in completed if iso_wk(b) == (this_wk[0], this_wk[1] - 1)]
    pwh = round(max(b["high"] for b in prev_wk_bars), 5) if prev_wk_bars else None
    pwl = round(min(b["low"] for b in prev_wk_bars), 5) if prev_wk_bars else None

    # ---- daily bias / trend ----
    score = 0
    reasons = []
    # 1) daily structure over last ~6 closed bars: HH/HL vs LH/LL
    hi6 = [b["high"] for b in completed[-6:]]
    lo6 = [b["low"] for b in completed[-6:]]
    if len(hi6) >= 4:
        up = hi6[-1] > max(hi6[:-1]) and lo6[-1] > min(lo6[:2])
        dn = lo6[-1] < min(lo6[:-1]) and hi6[-1] < max(hi6[:2])
        if up and not dn:
            score += 35; reasons.append("daily making higher highs/lows")
        elif dn and not up:
            score -= 35; reasons.append("daily making lower highs/lows")
    # 2) price vs 20-day SMA (trend proxy)
    sma20 = _sma(closes_d, 20)
    if sma20:
        if price > sma20:
            score += 15; reasons.append("price above 20-day average")
        else:
            score -= 15; reasons.append("price below 20-day average")
    # 3) position vs PDH/PDL/prior close
    if price > prior["high"]:
        score += 15; reasons.append("trading above prior-day high (breakout)")
    elif price < prior["low"]:
        score -= 15; reasons.append("trading below prior-day low (breakdown)")
    elif price > prior["close"]:
        score += 7; reasons.append("above prior close")
    else:
        score -= 7; reasons.append("below prior close")
    # 4) today's candle direction so far
    if today["close"] >= today["open"]:
        score += 10; reasons.append("today green from the open")
    else:
        score -= 10; reasons.append("today red from the open")
    score = max(-100, min(100, score))
    if score >= 25:
        bias_label = "BULLISH"
    elif score <= -25:
        bias_label = "BEARISH"
    else:
        bias_label = "NEUTRAL"

    # ---- liquidity levels ----
    tol_price = max(price * 0.0006, (adr14 or price) * 0.03)  # equal-level tolerance
    ex = ex or []
    h1 = h1 or []
    ex_hi, ex_lo = _pivots(ex, k=2)
    h1_hi, h1_lo = _pivots(h1, k=3)
    equal_highs = _cluster([p for _, p in ex_hi] + [p for _, p in h1_hi], tol_price)
    equal_lows = _cluster([p for _, p in ex_lo] + [p for _, p in h1_lo], tol_price)

    # today's developing session hi/lo (from exec bars in the current daily bar)
    day_start = today["time"]
    ex_today = [b for b in ex if b["time"] >= day_start] or ex[-30:] if ex else []
    sess_hi = round(max(b["high"] for b in ex_today), 5) if ex_today else today["high"]
    sess_lo = round(min(b["low"] for b in ex_today), 5) if ex_today else today["low"]

    named = {
        "PDH": round(prior["high"], 5), "PDL": round(prior["low"], 5),
        "prior_close": round(prior["close"], 5),
        "PWH": pwh, "PWL": pwl,
        "day_open": round(today["open"], 5),
        "session_high": sess_hi, "session_low": sess_lo,
    }

    def reach(dist):
        if remaining_budget is None:
            return "unknown"
        return "intraday" if dist <= remaining_budget * 1.10 else "swing"

    def pool_list(clusters, named_side, side):
        """Build target pools on one side of price, with reach + touches."""
        out = []
        seen = []
        # seed with named reference levels for this side
        for nm, val in named_side:
            if val is None:
                continue
            if side == "buy" and val <= price:
                continue
            if side == "sell" and val >= price:
                continue
            out.append({"name": nm, "price": round(val, 5),
                        "dist": round(abs(val - price), 5),
                        "reach": reach(abs(val - price)), "touches": 1,
                        "kind": "reference"})
            seen.append(val)
        for c in clusters:
            val = c["price"]
            if side == "buy" and val <= price:
                continue
            if side == "sell" and val >= price:
                continue
            if any(abs(val - s) <= tol_price for s in seen):
                # merge touches into the existing named level
                for o in out:
                    if abs(o["price"] - val) <= tol_price:
                        o["touches"] = max(o["touches"], c["touches"])
                continue
            out.append({"name": f"equal_{'highs' if side=='buy' else 'lows'}",
                        "price": val, "dist": round(abs(val - price), 5),
                        "reach": reach(abs(val - price)),
                        "touches": c["touches"], "kind": "equal_level"})
        out.sort(key=lambda x: x["dist"])
        return out

    buy_named = [("PDH", named["PDH"]), ("PWH", named["PWH"]),
                 ("session_high", named["session_high"]),
                 ("prior_close", named["prior_close"])]
    sell_named = [("PDL", named["PDL"]), ("PWL", named["PWL"]),
                  ("session_low", named["session_low"]),
                  ("prior_close", named["prior_close"])]
    pools_above = pool_list(equal_highs, buy_named, "buy")
    pools_below = pool_list(equal_lows, sell_named, "sell")

    # nearest in-reach pool each side = the actionable draws
    def nearest_reachable(pools):
        for p in pools:
            if p["reach"] in ("intraday", "unknown"):
                return p
        return pools[0] if pools else None
    draw_up = nearest_reachable(pools_above)
    draw_down = nearest_reachable(pools_below)

    # ---- recent sweep / reclaim (last ~40 exec bars) ----
    sweep = None
    if len(ex) >= 6:
        recent = ex[-40:]
        rmax = max(b["high"] for b in recent[:-1])
        rmin = min(b["low"] for b in recent[:-1])
        last = ex[-1]
        # look for a bar that poked beyond a prior extreme then closed back
        for b in reversed(recent[-6:]):
            if b["high"] > rmax and b["close"] < rmax:
                sweep = {"side": "buy_side", "level": round(rmax, 5),
                         "note": "recent high swept and price closed back below (bearish reclaim)"}
                break
            if b["low"] < rmin and b["close"] > rmin:
                sweep = {"side": "sell_side", "level": round(rmin, 5),
                         "note": "recent low swept and price closed back above (bullish reclaim)"}
                break

    # ---- volume / expansion ----
    vol_state = "unknown"
    rel_vol = None
    if len(ex) >= 25:
        recent_v = [b["volume"] for b in ex[-3:]]
        base_v = [b["volume"] for b in ex[-25:-3]]
        avg_recent = statistics.mean(recent_v) if recent_v else 0
        avg_base = statistics.mean(base_v) if base_v else 0
        if avg_base > 0:
            rel_vol = round(avg_recent / avg_base, 2)
            if rel_vol >= 1.25:
                vol_state = "expanding"
            elif rel_vol <= 0.7:
                vol_state = "drying_up"
            else:
                vol_state = "normal"

    if adr_used_pct is None:
        expansion_state = "unknown"
    elif adr_used_pct >= 90:
        expansion_state = "EXHAUSTED"
    elif adr_used_pct >= 70:
        expansion_state = "LOW_FUEL"
    elif adr_used_pct <= 40 and vol_state in ("expanding", "normal", "unknown"):
        expansion_state = "ROOM_TO_EXPAND"
    else:
        expansion_state = "MODERATE"

    # ---- no-man's-land flag ----
    nml = False
    if draw_up and draw_down:
        span = draw_up["price"] - draw_down["price"]
        if span > 0:
            pos = (price - draw_down["price"]) / span
            nml = (0.30 < pos < 0.70) and sweep is None and \
                  (adr_used_pct is None or adr_used_pct < 70)

    return {
        "instrument": instrument,
        "as_of": datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "exec_period": exec_period,
        "price": price,
        "daily_bias": {
            "label": bias_label, "score": score,
            "trend_day_potential": bool(abs(score) >= 40 and
                                        (adr_used_pct or 0) < 55),
            "reasons": reasons,
        },
        "range": {
            "adr14": adr14, "today_range": round(today_range, 5),
            "adr_used_pct": adr_used_pct, "remaining_budget": remaining_budget,
            "expansion_state": expansion_state,
        },
        "volume": {"exec_relative": rel_vol, "state": vol_state},
        "named_levels": named,
        "pools_above": pools_above,
        "pools_below": pools_below,
        "draw_up": draw_up,
        "draw_down": draw_down,
        "recent_sweep": sweep,
        "no_mans_land": nml,
        "warnings": warnings,
    }


# ── data fetch + CLI ─────────────────────────────────────────────────────────
def run_live(instrument, exec_period):
    d1 = ct.fetch_ohlcv(instrument, "D_1", hours_back=720)
    if not d1:
        return {"error": "data fetch failed", "instrument": instrument,
                "detail": ct.last_error()}
    h1 = ct.fetch_ohlcv(instrument, "H_1", hours_back=120)
    ex = ct.fetch_ohlcv(instrument, exec_period, hours_back=48)
    live = ct.get_live_price(instrument)
    return analyze(instrument, exec_period, d1=d1, h1=h1, ex=ex, live=live)


def _synthetic():
    """Deterministic fake bars for --dry-run (no token needed)."""
    import math
    from datetime import timedelta
    base = datetime(2026, 7, 1, tzinfo=timezone.utc)
    d1 = []
    px = 10000.0
    for i in range(30):
        o = px
        px += 20 * math.sin(i / 3) + 8
        hi = max(o, px) + 25
        lo = min(o, px) - 25
        d1.append({"time": base + timedelta(days=i), "open": o, "high": hi,
                   "low": lo, "close": px, "volume": 1000 + i})
    ex = []
    p = px - 40
    for j in range(300):
        o = p
        p += 3 * math.sin(j / 8)
        ex.append({"time": d1[-1]["time"] + timedelta(minutes=5 * j),
                   "open": o, "high": max(o, p) + 4, "low": min(o, p) - 4,
                   "close": p, "volume": 200 + (j % 40)})
    return d1, d1[-120:], ex, (p - 1, p + 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instrument", nargs="?", default="UK100")
    ap.add_argument("--exec", dest="exec_period", default="M_5")
    ap.add_argument("--json", action="store_true", help="print raw JSON only")
    ap.add_argument("--dry-run", action="store_true",
                    help="run on synthetic data (no token/network)")
    args = ap.parse_args()

    if args.dry_run:
        d1, h1, ex, live = _synthetic()
        result = analyze(args.instrument, args.exec_period,
                         d1=d1, h1=h1, ex=ex, live=live)
    else:
        result = run_live(args.instrument, args.exec_period)

    print(json.dumps(result, indent=2, default=str))
    if result.get("error"):
        sys.exit(2)


if __name__ == "__main__":
    main()
