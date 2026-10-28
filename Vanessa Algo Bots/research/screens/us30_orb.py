"""US30 opening-range breakout (US30_ORB_TEST_PLAN.md). Range 08:00-09:30 NY; from 10:00 to 13:00 NY the first M5 close
beyond the range with volume >= 1.2x the previous 20 bars -> enter at the next bar's open; stop A = 2.0 x ATR(14) of M5
(target 2.0R) or B = 75 pts x price/34,000 (target 3.0R); same-bar stop+target = stop; flat 16:00 NY; one trade a day.
Usage: us30_orb.py A|B out.json file.csv [...]  (cost 0.01% a round trip)"""
import csv, sys, json, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
import os
V, OUT, files = sys.argv[1], sys.argv[2], sys.argv[3:]
VOL = os.environ.get("ORB_VOL", "1") == "1"; AT_CLOSE = os.environ.get("ORB_CLOSE", "0") == "1"
def us_dst(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7); return s <= d < e
seen = {}
for f in files:
    for r in csv.reader(open(f)):
        if not r or not r[0].isdigit(): continue
        t = datetime.fromtimestamp(int(r[0]) / 1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=4 if us_dst(t.date()) else 5)
        v = float(r[6]) if len(r) > 6 and r[6] else 1.0
        seen[ny] = (float(r[2]), float(r[3]), float(r[4]), float(r[5]), v if v > 0 else 1.0)
T = sorted(seen); B = [(t,) + seen[t] for t in T]
byday = defaultdict(list)
for i, b in enumerate(B): byday[b[0].date()].append(i)
res = {}
for d in sorted(byday):
    if d.weekday() >= 5: continue
    I = byday[d]; mins = lambda i: B[i][0].hour * 60 + B[i][0].minute
    rng = [B[i] for i in I if 480 <= mins(i) < 570]
    if len(rng) < 15: continue
    hi = max(b[2] for b in rng); lo = min(b[3] for b in rng); entry = None
    for i in I:
        m = mins(i)
        if m < 600 or m >= 780: continue
        c, v = B[i][4], B[i][5]; prev = [B[j][5] for j in range(max(0, i - 20), i)]
        if VOL and (not prev or v < 1.2 * sum(prev) / len(prev)): continue
        side = 1 if c > hi else -1 if c < lo else 0
        if side and i + 1 < len(B) and B[i + 1][0].date() == d:
            atr = st.mean(B[j][2] - B[j][3] for j in range(i - 13, i + 1)); entry = (i + 1, side, atr, c); break
    if not entry: continue
    j, side, atr, sc = entry; ep = sc if AT_CLOSE else B[j][1]
    sd = 2.0 * atr if V == "A" else 75 * ep / 34000; rr = 2.0 if V == "A" else 3.0
    stop, tp = ep - side * sd, ep + side * rr * sd; x = None
    for q in [k for k in I if k >= j]:
        t, o, h, l, c, v = B[q]
        if t.hour >= 16: x = o; break
        hit_s = (l <= stop) if side > 0 else (h >= stop); hit_t = (h >= tp) if side > 0 else (l <= tp)
        if hit_s: x = stop; break
        if hit_t: x = tp; break
    if x is None: x = B[I[-1]][4]
    res[str(d)] = (x - ep) * side / sd - 0.0001 * ep / sd
json.dump(res, open(OUT, "w"))
R = list(res.values()); g = sum(r for r in R if r > 0); l = -sum(r for r in R if r < 0)
eq = pk = dd = 0; yr = defaultdict(float)
for d in sorted(res): eq += res[d]; pk = max(pk, eq); dd = max(dd, pk - eq); yr[d[:4]] += res[d]
print(f"{V}: trades {len(R)} total {sum(R):+.1f}R PF {g/l:.2f} win {sum(r>0 for r in R)/len(R):.0%} maxDD {dd:.1f}R")
print("   by year: " + "  ".join(f"{y} {v:+.1f}" for y, v in sorted(yr.items())))
