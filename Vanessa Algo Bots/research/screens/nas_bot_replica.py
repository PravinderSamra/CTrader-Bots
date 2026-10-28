"""Python replica of the live NAS bot's core (ORBVL, v3.x live settings), for a regime check on 2012-2020.
Live code untouched. Rules as read from the live log/settings:
 range = high/low of M5 bars 08:00 London .. 09:30 New York; breakout = M5 close beyond range +/- offset (10 pts) with
 volume >= 1.2 x average of the previous 20 M5 bars; first entry 10:00 NY (a breakout confirmed 09:30-10:00 is taken at
 10:00); one trade a day; stop 60 pts; TP 4.5R; early risk reduction at +0.7R (stop to -0.7R); trailing from +2.5R in
 0.1R steps; flat at 15:50 NY. ADDS=1 (env): at +0.7R one add with 1.5R of risk (Add Size 5 x 0.3R removed), sharing the stop
 and target, filled at the +0.7R level (as in the live log: ADD1 ~1.06x the main size).
 SCALE=fixed -> 60/10 pts as live; SCALE=pct -> 60 and 10 pts scaled by price/20,000 (for 2012-19 prices).
 Usage: nas_bot_replica.py fixed|pct out.json file.csv [...]"""
import csv, sys, json, os, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
SCALE, OUT, files = sys.argv[1], sys.argv[2], sys.argv[3:]; ADDS = os.environ.get("ADDS") == "1"
def us_dst(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7); return s <= d < e
def uk_dst(d):
    m = date(d.year, 3, 31); s = m - timedelta(days=(m.weekday() + 1) % 7)
    o = date(d.year, 10, 31); e = o - timedelta(days=(o.weekday() + 1) % 7); return s <= d < e
seen = {}
for f in files:
    for r in csv.reader(open(f)):
        if not r or not r[0].isdigit(): continue
        t = datetime.fromtimestamp(int(r[0]) / 1000, timezone.utc).replace(tzinfo=None)
        v = float(r[6]) if len(r) > 6 and r[6] else 1.0
        seen[t] = (float(r[2]), float(r[3]), float(r[4]), float(r[5]), v)
T = sorted(seen); bars = [(t,) + seen[t] for t in T]
byday = defaultdict(list)
for i, b in enumerate(bars):
    ny = b[0] - timedelta(hours=4 if us_dst(b[0].date()) else 5)
    byday[ny.date()].append(i)
res = {}
for d in sorted(byday):
    if d.weekday() >= 5: continue
    nyo = 4 if us_dst(d) else 5; ldo = 1 if uk_dst(d) else 0
    r0 = datetime(d.year, d.month, d.day, 8) - timedelta(hours=ldo)            # 08:00 London in UTC
    o930 = datetime(d.year, d.month, d.day, 9, 30) + timedelta(hours=nyo)
    e1000 = o930 + timedelta(minutes=30); end = datetime(d.year, d.month, d.day, 15, 50) + timedelta(hours=nyo)
    I = [i for i in byday[d]]
    rng = [bars[i] for i in I if r0 <= bars[i][0] < o930]
    if len(rng) < 12: continue
    hi = max(b[2] for b in rng); lo = min(b[3] for b in rng)
    px = rng[-1][4]; k = px / 20000 if SCALE == "pct" else 1.0
    off, sd = 10 * k, 60 * k
    entry = None
    for i in I:
        t = bars[i][0]
        if t < o930 or t >= end: continue
        c, v = bars[i][4], bars[i][5]
        prev = [bars[j][5] for j in range(max(0, i - 20), i)]
        vol_ok = prev and (v >= 1.2 * (sum(prev) / len(prev)) or (v == 1.0 and max(prev) == 1.0))   # no volume in file -> filter off
        side = 1 if c > hi + off else -1 if c < lo - off else 0
        if side and vol_ok:
            ct = t + timedelta(minutes=5)                       # bar close time
            et = max(ct, e1000)
            j = next((q for q in I if bars[q][0] >= et), None)
            if j is None or bars[j][0] >= end: break
            entry = (j, side); break
    if not entry: continue
    j, side = entry; ep = bars[j][1]; stop = ep - side * sd; tp = ep + side * 4.5 * sd; best = 0; x = None; add = None
    for q in I:
        if bars[q][0] < bars[j][0]: continue
        t, o, h, l, c, v = bars[q]
        if t >= end: x = o; break
        adv = (l if side > 0 else h); fav = (h if side > 0 else l)
        if (side > 0 and adv <= stop) or (side < 0 and adv >= stop): x = stop; break
        if (side > 0 and fav >= tp) or (side < 0 and fav <= tp): x = tp; break
        best = max(best, (fav - ep) * side / sd)
        if best >= 0.7:
            stop = max(stop, ep - side * 0.7 * sd) if side > 0 else min(stop, ep - side * 0.7 * sd)
            if ADDS and add is None:
                ap = ep + side * 0.7 * sd; add = (ap, 1.5 / ((ap - stop) * side / sd))   # (entry, size vs main)
        if best >= 2.5:
            lock = (int((best - 2.5) / 0.1) * 0.1 + 1.5)            # trail: lock 1R less than the best, in 0.1R steps
            ns = ep + side * lock * sd
            stop = max(stop, ns) if side > 0 else min(stop, ns)
    if x is None: x = bars[I[-1]][4]
    r = (x - ep) * side / sd - 0.0001 * ep / sd
    if add: r += add[1] * ((x - add[0]) * side / sd - 0.0001 * add[0] / sd)
    res[str(d)] = r
json.dump(res, open(OUT, "w"))
R = list(res.values()); yr = defaultdict(float)
for d, r in res.items(): yr[d[:4]] += r
eq = pk = dd = 0
for d in sorted(res): eq += res[d]; pk = max(pk, eq); dd = max(dd, pk - eq)
print(f"{SCALE}: trades {len(R)} total {sum(R):+.1f}R avg {st.mean(R):+.3f}R win {sum(r>0 for r in R)/len(R):.0%} maxDD {dd:.1f}R")
print("   by year: " + "  ".join(f"{y} {v:+.1f}R" for y, v in sorted(yr.items())))
