"""Do the RTH extremes land ON pre-open OI levels, and is there an edge in it?

Null model: for each day, compute the fraction of the day's own RTH range that
lies within +/-tol of SOME published gamma level. That is the probability a
uniformly-placed extreme would look like a hit. Compare to the observed rate.
"""
import json, glob, sys
from datetime import datetime, timezone, time as dtime
sys.path.insert(0, "/home/user/CTrader-Bots/.claude/skills/nas100-daily-brief/scripts")
import ctrader_http as ct, levels_fuel as LF

OPEN_UTC, CLOSE_UTC = dtime(13, 30), dtime(20, 0)
GK = {"gamma", "gamma-shelf"}
TOLS = (8.0, 15.0, 25.0)

def u(b):
    t = b["time"]
    if not isinstance(t, datetime):
        t = datetime.fromtimestamp(t/1000, timezone.utc)
    return t if t.tzinfo else t.replace(tzinfo=timezone.utc)

bars_all = ct.fetch_ohlcv_paged("NAS100", "M_5", days=45, max_calls=300)
byday = {}
for b in bars_all:
    byday.setdefault(str(LF.trading_day(b["time"])), []).append(b)

per_day = {}
for f in sorted(glob.glob("/home/user/CTrader-Bots/NAS100 Daily Brief agent skill/"
                          "journal/2026-*/[0-9]*.json")):
    d = json.load(open(f))
    if not d.get("is_trading_day") or not d.get("scan_utc"):
        continue
    t = datetime.fromisoformat(d["scan_utc"].replace("Z", "+00:00")).astimezone(timezone.utc)
    if t.time() >= OPEN_UTC:
        continue
    day = d["trading_day"]
    if day not in per_day or t > per_day[day][0]:
        per_day[day] = (t, d)

def covered_fraction(levels, lo, hi, tol):
    """Fraction of [lo,hi] within tol of some level — the null hit probability."""
    if hi <= lo: return 0.0
    segs = sorted((max(lo, p - tol), min(hi, p + tol)) for p in levels
                  if p + tol > lo and p - tol < hi)
    tot = 0.0; cur = None
    for a, b in segs:
        if cur is None: cur = [a, b]
        elif a <= cur[1]: cur[1] = max(cur[1], b)
        else: tot += cur[1] - cur[0]; cur = [a, b]
    if cur: tot += cur[1] - cur[0]
    return tot / (hi - lo)

rows = []
for day in sorted(per_day):
    t_scan, d = per_day[day]
    bars = byday.get(day) or []
    rth = [b for b in bars if str(u(b).date()) == day
           and OPEN_UTC <= u(b).time() < CLOSE_UTC]
    if len(rth) < 20:
        continue
    lv = sorted({x["price"] for x in (d["prediction"].get("levels") or [])
                 if x.get("kind") in GK})
    if not lv:
        continue
    op, cl = rth[0]["open"], rth[-1]["close"]
    hb = max(rth, key=lambda b: b["high"]); lb = min(rth, key=lambda b: b["low"])
    hi, lo = hb["high"], lb["low"]
    d_hi = min((hi - p for p in lv), key=abs)
    d_lo = min((lo - p for p in lv), key=abs)
    rows.append(dict(
        day=day, open=op, hi=hi, lo=lo, close=cl,
        t_hi=u(hb).strftime("%H:%M"), t_lo=u(lb).strftime("%H:%M"),
        min_hi=int((u(hb) - u(rth[0])).total_seconds()//60),
        min_lo=int((u(lb) - u(rth[0])).total_seconds()//60),
        d_hi=d_hi, d_lo=d_lo, rng=hi-lo,
        net=cl-op, from_hi=cl-hi, from_lo=cl-lo,
        null={t: covered_fraction(lv, lo, hi, t) for t in TOLS},
        nlv=len(lv)))

print(f"{'day':<12}{'open':>9}{'high':>9}{'t_hi':>7}{'d_hi':>8}{'low':>9}{'t_lo':>7}{'d_lo':>8}{'close':>9}{'range':>8}")
for r in rows:
    print(f"{r['day']:<12}{r['open']:>9.1f}{r['hi']:>9.1f}{r['t_hi']:>7}{r['d_hi']:>+8.1f}"
          f"{r['lo']:>9.1f}{r['t_lo']:>7}{r['d_lo']:>+8.1f}{r['close']:>9.1f}{r['rng']:>8.1f}")

print(f"\nn = {len(rows)} days with a pre-open scan and full RTH bars\n")
for tol in TOLS:
    h = sum(1 for r in rows if abs(r["d_hi"]) <= tol)
    l = sum(1 for r in rows if abs(r["d_lo"]) <= tol)
    e = sum(1 for r in rows if abs(r["d_hi"]) <= tol or abs(r["d_lo"]) <= tol)
    nh = sum(r["null"][tol] for r in rows)
    print(f"tol +/-{tol:>4.0f}pts | high on a level {h:>2}/{len(rows)} ({100*h/len(rows):.0f}%) "
          f"| low {l:>2}/{len(rows)} ({100*l/len(rows):.0f}%) "
          f"| either {e:>2}/{len(rows)} ({100*e/len(rows):.0f}%) "
          f"| NULL expected {nh:.1f}/{len(rows)} ({100*nh/len(rows):.0f}%)")
json.dump(rows, open("/tmp/claude-0/-home-user-CTrader-Bots/"
                     "d223cf12-f6c6-532d-a07d-b1099eb082ee/scratchpad/study2.json","w"),
          indent=1, default=str)
