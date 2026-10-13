"""Dylan O'Neal VIX confirmation checks. Data: CBOE daily VIX OHLC and SPX closes (1990-2026); NAS100 RTH daily OHLC
2021-Jul 2026 (cTrader) as the index for the intraday-level test (he trades ES/NQ; VIX OHLC is daily here).
A) '1% rule': index up >= 1% AND VIX up >= 1% -> expect next-day weakness (mirror for down days).
B) Breakdown below yesterday's low: VIX confirming (VIX high >= its prior-day high) vs not; how often does the index close
   back above the prior-day low (failed breakdown) and where it closes relative to that low (in % of price). Mirror for
   breakouts above the prior-day high with VIX low <= its prior-day low."""
import csv, statistics as st
from datetime import datetime
from collections import defaultdict
from vlib import nas_daily
vix = {}
for r in csv.DictReader(open("vixdata/vix.csv")):
    vix[datetime.strptime(r["DATE"], "%m/%d/%Y").date()] = tuple(float(r[k]) for k in ("OPEN", "HIGH", "LOW", "CLOSE"))
spx = {}
for r in csv.DictReader(open("vixdata/spx.csv")):
    spx[datetime.strptime(r["DATE"], "%m/%d/%Y").date()] = float(r["SPX"])
days = sorted(d for d in spx if d in vix and d.year >= 1990)
print("A) 1% rule, SPX closes 1990-2026")
for lab, cond in (("SPX>=+1% & VIX>=+1%", lambda s, v: s >= 0.01 and v >= 0.01),
                  ("SPX>=+1% & VIX down", lambda s, v: s >= 0.01 and v < 0),
                  ("SPX<=-1% & VIX<=-1%", lambda s, v: s <= -0.01 and v <= -0.01),
                  ("SPX<=-1% & VIX up", lambda s, v: s <= -0.01 and v > 0),
                  ("all days", lambda s, v: True)):
    nxt = []
    for i in range(1, len(days) - 1):
        d0, d1, d2 = days[i-1], days[i], days[i+1]
        s = spx[d1] / spx[d0] - 1; v = vix[d1][3] / vix[d0][3] - 1
        if cond(s, v): nxt.append((spx[d2] / spx[d1] - 1) * 100)
    if nxt:
        print(f"  {lab:24s} n={len(nxt):5d} next-day avg {st.mean(nxt):+.3f}%  up {sum(x>0 for x in nxt)/len(nxt):4.0%}  median {st.median(nxt):+.3f}%")
print("\nB) NAS100 RTH daily 2021-Jul 2026 vs VIX daily")
nd = nas_daily(); rows = [(b[0].date(),) + b[1:] for b in nd if b[0].date() in vix]
res = defaultdict(list)
for i in range(1, len(rows)):
    d, o, h, l, c = rows[i]; pd = rows[i-1]
    vh, vl = vix[d][1], vix[d][2]; vph, vpl = vix[pd[0]][1], vix[pd[0]][2]
    if l < pd[3]:
        k = "breakdown, VIX confirms (high>=PDH)" if vh >= vph else "breakdown, VIX not confirming"
        res[k].append((c > pd[3], (c - pd[3]) / pd[3] * 100))
    if h > pd[2]:
        k = "breakout, VIX confirms (low<=PDL)" if vl <= vpl else "breakout, VIX not confirming"
        res[k].append((c < pd[2], (pd[2] - c) / pd[2] * 100))
for k in sorted(res):
    v = res[k]
    print(f"  {k:38s} n={len(v):4d}  failed (closed back inside) {sum(x[0] for x in v)/len(v):4.0%}  "
          f"avg close vs level {st.mean(x[1] for x in v):+.2f}% (positive = against the break)")
