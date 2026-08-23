#!/usr/bin/env python3
"""
levels_fuel.py — Phase-1 prototype: NAS100 liquidity levels + range/fuel budget.

Built on the broker's own NAS100 CFD prices via cTrader (same HTTP client the
Liquidity Trap phone skill uses), so every level printed is a price you can
type straight onto the chart — no futures/cash basis to mentally adjust.

Produces exactly the level set the two NAS100 strategies key off:
  PDH/PDL, PWH/PWL, Asia H/L, London H/L, NY-open range,
  unmitigated swing highs/lows from recent days, prior-day mid/equilibrium,
  plus the ADR-based fuel gauge (mirrors Liquidity Trap reference 03).

    python3 levels_fuel.py            # human-readable
    python3 levels_fuel.py --json
"""
import json, os, sys
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo

_HERE = os.path.dirname(os.path.abspath(__file__))
_CANDIDATES = [
    os.path.join(_HERE, "..", "..", ".claude", "skills",
                 "liquidity-inducement-phone", "scripts"),
    os.path.expanduser("~/CTrader-Bots/.claude/skills/"
                       "liquidity-inducement-phone/scripts"),
]
for _c in _CANDIDATES:
    if os.path.isfile(os.path.join(_c, "ctrader_http.py")):
        sys.path.insert(0, os.path.abspath(_c)); break
import ctrader_http as ct                                    # noqa: E402

SYMBOL = "NAS100"

# Session windows MUST be derived from exchange local time, not hardcoded UTC.
# The original version hardcoded NY at 13:30-20:00 UTC and London at
# 07:00-12:30 UTC. Both are wrong for half the year:
#
#   09:30 ET (NY cash open) = 13:30 UTC in EDT, 14:30 UTC in EST
#   08:00 London (LSE open) = 07:00 UTC in BST, 08:00 UTC in GMT
#
# Tokyo does not observe DST, so the Asia window is genuinely fixed in UTC.
# Getting this wrong shifts the session highs/lows — which are primary
# strategy-1 sweep levels — by a full hour for ~8 months of the year.
_ET = ZoneInfo("America/New_York")
_LON = ZoneInfo("Europe/London")

# (tz or None for fixed-UTC, start_local_hour, end_local_hour)
_SESSION_SPEC = {
    "asia":   (None, 23.0, 7.0),      # Tokyo open -> pre-London, no DST
    "london": (_LON, 8.0, 13.5),      # LSE open -> before NY cash
    "ny":     (_ET, 9.5, 16.0),       # NYSE cash session
}


def session_windows(on_date):
    """Resolve the session windows to UTC hours for a given trading date,
    honouring whatever DST rule is in force that day."""
    out = {}
    for name, (tz, h0, h1) in _SESSION_SPEC.items():
        if tz is None:
            out[name] = (h0, h1)
            continue
        out[name] = (_local_hour_to_utc(tz, on_date, h0),
                     _local_hour_to_utc(tz, on_date, h1))
    return out


def _local_hour_to_utc(tz, on_date, hour):
    h, m = int(hour), int(round((hour - int(hour)) * 60))
    local = datetime(on_date.year, on_date.month, on_date.day, h, m, tzinfo=tz)
    u = local.astimezone(timezone.utc)
    return u.hour + u.minute / 60.0


def _h(dt):
    return dt.hour + dt.minute / 60.0


def daily_bars(days=40):
    return ct.fetch_ohlcv(SYMBOL, "D_1", hours_back=days * 24)


def intraday(days=6, period="M_5"):
    return ct.fetch_ohlcv_paged(SYMBOL, period, days=days)


def trading_day(dt):
    """cTrader daily bars roll at 21:00 UTC — bucket intraday bars the same way
    so 'previous day' means the same thing on both feeds."""
    d = dt.date()
    return d + timedelta(days=1) if dt.hour >= 21 else d


def session_levels(bars, day):
    """Asia/London/NY high-low for one trading day, DST-resolved."""
    out = {}
    for name, (h0, h1) in session_windows(day).items():
        if h0 > h1:   # wraps midnight (Asia)
            w = [b for b in bars if trading_day(b["time"]) == day
                 and (_h(b["time"]) >= h0 or _h(b["time"]) < h1)]
        else:
            w = [b for b in bars if trading_day(b["time"]) == day
                 and h0 <= _h(b["time"]) < h1]
        if w:
            out[name] = {"high": round(max(b["high"] for b in w), 1),
                         "low": round(min(b["low"] for b in w), 1),
                         "bars": len(w),
                         "complete": len(w) > 5}
    return out


def swing_points(bars, left=3, right=3):
    """Fractal swing highs/lows."""
    hi, lo = [], []
    for i in range(left, len(bars) - right):
        w = bars[i - left:i + right + 1]
        b = bars[i]
        if b["high"] == max(x["high"] for x in w):
            hi.append({"price": round(b["high"], 1), "time": b["time"]})
        if b["low"] == min(x["low"] for x in w):
            lo.append({"price": round(b["low"], 1), "time": b["time"]})
    return hi, lo


def unmitigated(swings, bars, side):
    """A swing is 'unmitigated' (liquidity still resting) if price has not
    traded through it since it formed. These are the sweep targets."""
    out = []
    for s in swings:
        later = [b for b in bars if b["time"] > s["time"]]
        if not later:
            continue
        breached = (max(b["high"] for b in later) > s["price"] if side == "high"
                    else min(b["low"] for b in later) < s["price"])
        if not breached:
            out.append(s)
    return out


def cluster(levels, tol):
    """Merge levels within `tol` points — equal highs/lows = stronger pool."""
    if not levels:
        return []
    xs = sorted(levels, key=lambda s: s["price"])
    groups, cur = [], [xs[0]]
    for s in xs[1:]:
        if abs(s["price"] - cur[-1]["price"]) <= tol:
            cur.append(s)
        else:
            groups.append(cur); cur = [s]
    groups.append(cur)
    return [{"price": round(sum(g_["price"] for g_ in g) / len(g), 1),
             "touches": len(g),
             "confirmed": len(g) >= 2,
             "last_formed": max(g_["time"] for g_ in g).isoformat()}
            for g in groups]


def run(days_intraday=6, days_daily=40):
    d1 = daily_bars(days_daily)
    m5 = intraday(days_intraday, "M_5")
    if not d1 or not m5:
        return {"error": "no data", "detail": ct.last_error()}

    bid, ask = ct.get_live_price(SYMBOL)
    price = round((bid + ask) / 2, 1)

    today = trading_day(datetime.now(timezone.utc))
    # completed daily bars, newest last
    prev = d1[-2] if trading_day(d1[-1]["time"] + timedelta(hours=3)) == today else d1[-1]
    cur = d1[-1]

    # ---- ADR + fuel (Liquidity Trap ref-03 model) --------------------------
    rng = [b["high"] - b["low"] for b in d1[-15:-1]]
    adr14 = sum(rng) / len(rng) if rng else 0
    today_bars = [b for b in m5 if trading_day(b["time"]) == today]
    if today_bars:
        t_hi = max(b["high"] for b in today_bars); t_lo = min(b["low"] for b in today_bars)
    else:
        t_hi, t_lo = cur["high"], cur["low"]
    today_range = t_hi - t_lo
    used = (today_range / adr14 * 100) if adr14 else 0
    remaining = max(0.0, adr14 - today_range)
    state = ("ROOM_TO_EXPAND" if used <= 40 else "MODERATE" if used <= 70
             else "LOW_FUEL" if used <= 90 else "EXHAUSTED")

    # volume state on the execution TF
    vols = [b["volume"] for b in m5[-120:]]
    recent = sum(vols[-12:]) / 12 if len(vols) >= 12 else 0
    base = sum(vols[:-12]) / max(1, len(vols) - 12) if len(vols) > 12 else recent
    rel = round(recent / base, 2) if base else None
    vstate = (None if rel is None else "expanding" if rel >= 1.25
              else "drying_up" if rel <= 0.7 else "normal")

    # ---- session + day-frame levels ---------------------------------------
    yday = sorted({trading_day(b["time"]) for b in m5 if trading_day(b["time"]) < today})
    prev_day = yday[-1] if yday else None
    # Prior *calendar* week (ISO Mon-Sun), not "4-11 days ago" — the rolling-
    # window version drifts by weekday and produced a PWH/PWL pair that spanned
    # parts of two different weeks.
    cur_iso = today.isocalendar()[:2]
    prior_week = []
    for b in d1:
        bd = trading_day(b["time"] + timedelta(hours=3))
        iso = bd.isocalendar()[:2]
        if iso < cur_iso and (cur_iso[1] - iso[1] in (1,) or
                              (cur_iso[1] == 1 and iso[1] >= 52)):
            prior_week.append(b)

    lv = {
        "PDH": round(prev["high"], 1), "PDL": round(prev["low"], 1),
        "PD_mid": round((prev["high"] + prev["low"]) / 2, 1),
        "PD_close": round(prev["close"], 1),
        "PWH": round(max(b["high"] for b in prior_week), 1) if prior_week else None,
        "PWL": round(min(b["low"] for b in prior_week), 1) if prior_week else None,
        "today_high": round(t_hi, 1), "today_low": round(t_lo, 1),
    }
    lv["sessions_today"] = session_levels(m5, today)
    if prev_day:
        lv["sessions_prev_day"] = session_levels(m5, prev_day)

    # ---- unmitigated pools -------------------------------------------------
    # Calibrated 2026-08-22 on 6d of NAS100 M_5 (1,379 bars): tol=5 found only
    # 1 confirmed pool, tol=15-20 found 6 above / 1-2 below. NAS100 needs a
    # wider equal-high band than FX because ADR is ~475 pts.
    tol = max(12.0, adr14 * 0.03)
    hi_s, lo_s = swing_points(m5, 4, 4)
    un_hi = cluster(unmitigated(hi_s, m5, "high"), tol)
    un_lo = cluster(unmitigated(lo_s, m5, "low"), tol)
    pools_above = sorted([p for p in un_hi if p["price"] > price],
                         key=lambda p: p["price"])[:6]
    pools_below = sorted([p for p in un_lo if p["price"] < price],
                         key=lambda p: p["price"], reverse=True)[:6]
    for p in pools_above + pools_below:
        p["dist"] = round(abs(p["price"] - price), 1)
        p["reach"] = "intraday" if p["dist"] <= remaining else "swing"

    return {
        "symbol": SYMBOL, "generated_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "price": price, "bid": bid, "ask": ask, "trading_day": str(today),
        "fuel": {"adr14": round(adr14, 1), "today_range": round(today_range, 1),
                 "adr_used_pct": round(used, 1), "remaining_budget": round(remaining, 1),
                 "expansion_state": state,
                 "volume_relative": rel, "volume_state": vstate},
        "levels": lv,
        "unmitigated_pools_above": pools_above,
        "unmitigated_pools_below": pools_below,
        "bars_used": {"D_1": len(d1), "M_5": len(m5)},
    }


if __name__ == "__main__":
    out = run()
    if "--json" in sys.argv or "error" in out:
        print(json.dumps(out, indent=2, default=str)); sys.exit(0)
    f, l = out["fuel"], out["levels"]
    print(f"{out['symbol']} {out['price']}  (day {out['trading_day']}, "
          f"{out['generated_utc']})")
    print(f"FUEL  ADR14 {f['adr14']}  today {f['today_range']} "
          f"({f['adr_used_pct']}% used)  budget left {f['remaining_budget']}  "
          f"-> {f['expansion_state']}  vol {f['volume_state']} ({f['volume_relative']})")
    print(f"PDH {l['PDH']}  PDL {l['PDL']}  PDmid {l['PD_mid']}  PDclose {l['PD_close']}")
    print(f"PWH {l['PWH']}  PWL {l['PWL']}")
    for tag in ("sessions_prev_day", "sessions_today"):
        if tag in l:
            print(f"{tag}: " + "  ".join(
                f"{k.upper()} {v['high']}/{v['low']}" for k, v in l[tag].items()))
    print("\nUnmitigated pools ABOVE:")
    for p in out["unmitigated_pools_above"]:
        print(f"   {p['price']:>10}  touches {p['touches']}  {p['dist']:>7} away  {p['reach']}")
    print("Unmitigated pools BELOW:")
    for p in out["unmitigated_pools_below"]:
        print(f"   {p['price']:>10}  touches {p['touches']}  {p['dist']:>7} away  {p['reach']}")
