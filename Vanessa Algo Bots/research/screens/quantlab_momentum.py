"""QuantLab 'Momentum Bot' as shown in their video (rules read from the frames, pre-registered 27 Oct 2026):
NAS100 M5. At 09:35 NY (close of the first 5-minute candle of the session): if that close is above the 20-period EMA of
M5 closes -> buy, below -> sell, at the next bar's open. Initial stop: the other end of the first candle (its low for a
buy, high for a sell). Exit: first M5 close back across the EMA (the trend turns), or the stop, or 16:00 NY.
Results in R (1R = entry to initial stop) and in % of price; costs 0.01% per round trip.
Variants (stated before running): EMA 20 (main), EMA 9 and EMA 50 as neighbours."""
import csv, sys, os, math, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
files = sys.argv[1:]; EMA = int(os.environ.get("QL_EMA", 20)); COST = 0.0001
def nyoff(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7); return 4 if s <= d < e else 5
bars = []
for f in files:
    for r in csv.reader(open(f)):
        if not r or not r[0].isdigit(): continue
        t = datetime.fromtimestamp(int(r[0]) / 1000, timezone.utc).replace(tzinfo=None)
        bars.append((t - timedelta(hours=nyoff(t.date())), float(r[2]), float(r[3]), float(r[4]), float(r[5])))
bars.sort(); seen = set(); B = []
for b in bars:
    if b[0] not in seen: seen.add(b[0]); B.append(b)
a = 2 / (EMA + 1); ema = []; e = B[0][4]
for b in B: e = a * b[4] + (1 - a) * e; ema.append(e)
idx = defaultdict(list)
for i, b in enumerate(B): idx[b[0].date()].append(i)
res = []
for d in sorted(idx):
    if d.weekday() >= 5: continue
    I = idx[d]; first = [i for i in I if B[i][0].hour == 9 and B[i][0].minute == 30]
    if not first: continue
    i0 = first[0]
    if i0 + 1 >= len(B) or B[i0 + 1][0].date() != d: continue
    side = 1 if B[i0][4] > ema[i0] else -1
    en = B[i0 + 1][1]; stop = B[i0][3] if side > 0 else B[i0][2]
    risk = (en - stop) * side
    if risk <= 0: continue
    x = None; j = i0 + 1
    while j < len(B) and B[j][0].date() == d and B[j][0].hour < 16:
        if side > 0 and B[j][3] <= stop: x = stop if j > i0 + 1 else min(stop, B[j][1]); break
        if side < 0 and B[j][2] >= stop: x = stop if j > i0 + 1 else max(stop, B[j][1]); break
        if (side > 0 and B[j][4] < ema[j]) or (side < 0 and B[j][4] > ema[j]):
            x = B[j + 1][1] if j + 1 < len(B) and B[j + 1][0].date() == d else B[j][4]; break
        j += 1
    if x is None: x = B[j - 1][4]
    pct = side * (x - en) / en - COST
    res.append((d, pct, pct * en / risk, side))
R = [r for _, _, r, _ in res]; P = [p for _, p, _, _ in res]
eq = pk = dd = 0
for r in R: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
yr = defaultdict(float)
for d, _, r, _ in res: yr[d.year] += r
print(f"EMA {EMA}: trades {len(R)}  total {sum(R):+.1f}R  avg {st.mean(R):+.3f}R  win {sum(r>0 for r in R)/len(R):.0%}  "
      f"max DD {dd:.1f}R  avg % {st.mean(P)*100:+.3f}%")
print("   by year (R): " + "  ".join(f"{y} {v:+.1f}" for y, v in sorted(yr.items())))
print(f"   longs {sum(r for _,_,r,s in res if s>0):+.1f}R ({sum(s>0 for *_,s in res)})  shorts {sum(r for _,_,r,s in res if s<0):+.1f}R ({sum(s<0 for *_,s in res)})")
