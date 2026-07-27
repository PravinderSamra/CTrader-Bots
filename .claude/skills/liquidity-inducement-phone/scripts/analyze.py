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
from zoneinfo import ZoneInfo

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
    """Cluster nearby price levels into pools. levels: list of (time, price).
    Returns {price, low, high, touches, last_time} sorted by touches desc. A
    pool is a ZONE (low..high), not a tick — you work an area, not an exact
    price. last_time is when the pool was most recently touched, which is what
    makes it possible to ask whether price has since traded through it."""
    if not levels:
        return []
    pts = sorted(levels, key=lambda tp: tp[1])
    clusters = [[pts[0]]]
    for tp in pts[1:]:
        if abs(tp[1] - clusters[-1][-1][1]) <= tol:
            clusters[-1].append(tp)
        else:
            clusters.append([tp])
    out = [{"price": round(statistics.mean([p for _, p in c]), 5),
            "low": round(min(p for _, p in c), 5),
            "high": round(max(p for _, p in c), 5),
            "touches": len(c),
            "last_time": max(t for t, _ in c)}
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


# Day-frame reference pools (reference 01 §named_levels). The session extremes
# belong here: the day's high and low are the most obvious resting liquidity
# there is — "buy below lows, sell above highs" refers precisely to them — even
# though each is a single print and so never reaches touches >= 2.
_DAY_FRAME = {"PDH", "PDL", "PWH", "PWL", "prior_close",
              "session_high", "session_low"}


def _session(now):
    """Trading-session context with real DST handling. NY open is 09:30
    America/New_York — 13:30 UTC in summer (EDT), 14:30 in winter (EST).
    Computed here so nobody converts UTC by hand and drifts an hour."""
    ny = now.astimezone(ZoneInfo("America/New_York"))
    ldn = now.astimezone(ZoneInfo("Europe/London"))

    def at(dt, h, m=0):
        return dt.replace(hour=h, minute=m, second=0, microsecond=0)

    ny_open, ny_close = at(ny, 9, 30), at(ny, 16, 0)
    lunch_a, lunch_b = at(ny, 12, 0), at(ny, 13, 0)
    ldn_open = at(ldn, 8, 0)
    mins_from_open = round((ny - ny_open).total_seconds() / 60)

    if ny.weekday() >= 5:
        label = "WEEKEND"
    elif ny_open <= ny <= ny_close:
        if lunch_a <= ny < lunch_b:
            label = "NY_LUNCH"
        else:
            label = "NY_MORNING" if ny < lunch_a else "NY_AFTERNOON"
    elif ny < ny_open and ldn >= ldn_open:
        label = "LONDON_PRE_NY"
    elif ny > ny_close:
        label = "POST_NY"
    else:
        label = "ASIA_EARLY"

    return {
        "label": label,
        "ny_local": ny.strftime("%H:%M"),
        "ny_open_utc": ny_open.astimezone(timezone.utc).strftime("%H:%M"),
        "minutes_from_ny_open": mins_from_open,   # negative = until open
        "in_trade_window": label in ("LONDON_PRE_NY", "NY_MORNING",
                                     "NY_AFTERNOON"),
    }


def _zone(low, high, min_width):
    """Return [low, high] widened to at least min_width, centred on the cluster.
    Pools and liquidity blocks are areas to work in; a single-touch level still
    gets a band so you don't chase an exact tick."""
    mid = (low + high) / 2
    if high - low < min_width:
        low, high = mid - min_width / 2, mid + min_width / 2
    return [round(low, 5), round(high, 5)]


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
    equal_highs = _cluster([(ex[i]["time"], p) for i, p in ex_hi] +
                           [(h1[i]["time"], p) for i, p in h1_hi], tol_price)
    equal_lows = _cluster([(ex[i]["time"], p) for i, p in ex_lo] +
                          [(h1[i]["time"], p) for i, p in h1_lo], tol_price)

    # today's developing session hi/lo (from exec bars in the current daily bar)
    day_start = today["time"]
    ex_today = [b for b in ex if b["time"] >= day_start] or ex[-30:] if ex else []
    sess_hi = round(max(b["high"] for b in ex_today), 5) if ex_today else today["high"]
    sess_lo = round(min(b["low"] for b in ex_today), 5) if ex_today else today["low"]
    sess_hi_t = (max(ex_today, key=lambda b: b["high"])["time"]
                 if ex_today else day_start)
    sess_lo_t = (min(ex_today, key=lambda b: b["low"])["time"]
                 if ex_today else day_start)
    # When each level was established, so "has price been through it since?"
    # is answerable. Prior day/week levels predate today entirely.
    named_time = {"PDH": day_start, "PDL": day_start, "prior_close": day_start,
                  "PWH": day_start, "PWL": day_start, "day_open": day_start,
                  "session_high": sess_hi_t, "session_low": sess_lo_t}

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
                        "zone": _zone(val, val, tol_price),
                        "dist": round(abs(val - price), 5),
                        "reach": reach(abs(val - price)), "touches": 1,
                        "kind": "reference",
                        "last_time": named_time.get(nm, day_start)})
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
                        "price": val,
                        "zone": _zone(c["low"], c["high"], tol_price),
                        "dist": round(abs(val - price), 5),
                        "reach": reach(abs(val - price)),
                        "touches": c["touches"], "kind": "equal_level",
                        "last_time": c["last_time"]})
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

    # A pool sitting right on top of price is not a target: the move to it is
    # smaller than the stop + spread it would cost, so it can never pay. Floor
    # the draw at 10% of ADR and tag everything nearer as noise.
    min_target_dist = round(adr14 * 0.10, 5) if adr14 else 0.0
    # "Only confirmed pools are targets" (reference 01 §Strategy recap): equal
    # highs/lows need touches >= 2, or it must be a day-frame level. A single
    # touch is one bar's extreme, not liquidity — it was being handed back as
    # the draw and having to be overridden by hand.
    def already_swept(pool, side):
        """Has price traded beyond this pool SINCE it was last touched? A level
        already taken is a liquidity block (a stop anchor), not a target —
        reference 01 §Strategy recap rule 1. The stops that rested there are
        gone, so aiming at it is aiming at spent liquidity. Measured from the
        pool's last touch, so a level re-formed after the day's extreme still
        counts as live."""
        after = [b for b in ex if b["time"] > pool["last_time"]]
        if not after:
            return False
        lo, hi = pool["zone"]
        if side == "sell":                      # pool sits below price
            return min(b["low"] for b in after) < lo
        return max(b["high"] for b in after) > hi

    for p, side in ([(x, "buy") for x in pools_above] +
                    [(x, "sell") for x in pools_below]):
        p["too_close"] = p["dist"] < min_target_dist
        p["confirmed"] = bool(p["touches"] >= 2 or p["name"] in _DAY_FRAME)
        p["swept"] = already_swept(p, side)

    # nearest CONFIRMED, UNSWEPT, meaningful, in-reach pool each side
    def nearest_reachable(pools):
        in_reach = [p for p in pools if p["reach"] in ("intraday", "unknown")]
        tradeable = [p for p in in_reach
                     if not p["too_close"] and not p["swept"]]
        for p in tradeable:
            if p["confirmed"]:
                return p
        # nothing confirmed in reach — surface the nearest tradeable one
        # (flagged unconfirmed) so the agent can downgrade rather than invent
        if tradeable:
            return tradeable[0]
        return in_reach[0] if in_reach else (pools[0] if pools else None)
    draw_up = nearest_reachable(pools_above)
    draw_down = nearest_reachable(pools_below)

    # ---- recent sweep / reclaim (last ~40 exec bars) ----
    sweep = None
    if len(ex) >= 12:
        recent = ex[-40:]
        buf = tol_price * 0.5
        # Look for a bar that poked beyond the prior extreme then closed back.
        # The reference extreme MUST come from the bars before the candidate:
        # computing it over a window that already contained the candidate made
        # `low < rmin` unsatisfiable for every bar but the last, so any sweep
        # more than one bar old was invisible.
        # lb_zone = the swept, no-liquidity extreme: the band you enter into and
        # hide the stop behind — an area, never a single tick.
        for k in range(1, min(7, len(recent) - 4)):
            b = recent[-k]
            prior = recent[:-k]
            if len(prior) < 5:
                break
            rmax = max(p["high"] for p in prior)
            rmin = min(p["low"] for p in prior)
            if b["high"] > rmax and b["close"] < rmax:
                sweep = {"side": "buy_side", "level": round(rmax, 5),
                         "lb_zone": [round(rmax, 5), round(b["high"], 5)],
                         "stop_beyond": round(b["high"] + buf, 5),
                         "bars_ago": k - 1,
                         "note": "recent high swept and price closed back below (bearish reclaim)"}
                break
            if b["low"] < rmin and b["close"] > rmin:
                sweep = {"side": "sell_side", "level": round(rmin, 5),
                         "lb_zone": [round(b["low"], 5), round(rmin, 5)],
                         "stop_beyond": round(b["low"] - buf, 5),
                         "bars_ago": k - 1,
                         "note": "recent low swept and price closed back above (bullish reclaim)"}
                break

    # A reclaim is only a live trap while price remains on the reclaimed side
    # of the swept level. Once price trades back through it, the trap FAILED —
    # reporting it unmarked made a dead signal read identically to a live one.
    if sweep:
        # lb_zone is the true no-liquidity pocket and stays factual, but a
        # shallow stab can make it thinner than the instrument's own noise
        # band — unworkable as an area to enter against. entry_zone widens it
        # to tol_price for practical use; the stop still hides behind the real
        # extreme, so widening never loosens risk.
        lo, hi = sweep["lb_zone"]
        sweep["lb_width"] = round(hi - lo, 5)
        sweep["thin_lb"] = bool(sweep["lb_width"] < tol_price)
        sweep["entry_zone"] = _zone(lo, hi, tol_price)
        # WHICH pool did this sweep take? The detector fires on a poke beyond
        # the recent swing extreme, which is not necessarily a pool at all.
        # Naming it separates "a real pool of stops was taken" from "an
        # incidental high/low was poked" — only the former is the trap.
        side_pools = (pools_below if sweep["side"] == "sell_side"
                      else pools_above)
        taken = next((p for p in side_pools
                      if p["zone"][0] <= sweep["level"] <= p["zone"][1]), None)
        sweep["pool_taken"] = ({"name": taken["name"], "zone": taken["zone"],
                                "touches": taken["touches"],
                                "confirmed": taken["confirmed"]}
                               if taken else None)
        if sweep["side"] == "sell_side":
            sweep["still_valid"] = bool(price > sweep["level"])
        else:
            sweep["still_valid"] = bool(price < sweep["level"])
        if not sweep["still_valid"]:
            sweep["note"] += (" [INVALIDATED: price has traded back through "
                              "the swept level — this trap failed, do not act on it]")

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
            live_sweep = sweep is not None and sweep.get("still_valid", True)
            nml = (0.30 < pos < 0.70) and not live_sweep and \
                  (adr_used_pct is None or adr_used_pct < 70)

    now = datetime.now(tz=timezone.utc)
    return {
        "instrument": instrument,
        "as_of": now.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "session": _session(now),
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
            "min_target_dist": min_target_dist,
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
