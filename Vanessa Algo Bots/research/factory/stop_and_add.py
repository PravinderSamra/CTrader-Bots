"""Candidate A (BB2.5, any trend, 5-day hold): disaster-stop width and an add-to-winner rule. 2010-2026, 9 FTMO
indices (US2000 removed). Add rule (pre-set): after the close of day k (k = 1, 2), if the trade is up >= 0.5R
(1 x ATR), add the same size again at the next open; both parts exit together. Keep a change only if total R rises
AND profit / max drawdown does not fall."""
import statistics as st
from collections import defaultdict
import numpy as np
import factory_d1 as F

F.GROUPS["IDX"] = [m for m in F.GROUPS["IDX"] if m != "us2000"]

def run(cat, add_day=None, add_thr=0.5, hold=5):
    T = []
    for m in F._M["IDX"]:
        sig = F.entry_signal(m, "BB", 2.5, 1)
        o, h, l, c, A = m.o, m.h, m.l, m.c, m.atr; n = len(c); nxt = 0
        for s in np.flatnonzero(sig):
            if s < nxt or s + 1 >= n or not A[s] > 0: continue
            R = 2 * A[s]; e = o[s + 1]; stop = e - cat * A[s]; legs = [e]; x = None; j = s + 1; last = min(n - 1, s + hold)
            while j <= last:
                if l[j] <= stop: x = min(stop, o[j]) if j > s + 1 else stop; break
                if j == last: x = c[j]; break
                if add_day and j == s + add_day and c[j] - e >= add_thr * R and j + 1 <= last: legs.append(o[j + 1])
                j += 1
            nights = (m.dates[j] - m.dates[s + 1]).days
            r = sum((x - le - m.cost * le - m.swap * le * nights) / R for le in legs)
            T.append((m.dates[j], r, m.name)); nxt = j + 1
    T.sort(); rs = [t[1] for t in T]; eq = pk = dd = 0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    day = defaultdict(float)
    for t in T: day[t[0]] += t[1]
    stops = sum(1 for r in rs if r <= -(cat / 2) + 0.05)
    return len(T), sum(rs), st.mean(rs), dd, min(rs), min(day.values()), stops

F._init("IDX")
print("disaster stop width (no add):")
for cat in (10, 8, 7, 6, 5):
    n, tot, avg, dd, worst, wd, stops = run(cat)
    print(f"  {cat:2d} x ATR: n={n} total={tot:+6.1f}R avg={avg:+.3f}R maxDD={dd:5.1f}R profit/DD={tot/dd:4.2f} worst trade={worst:+.2f}R worst day={wd:+.2f}R stop hits={stops}")
print("add to winner (stop 10 x ATR):")
for k in (1, 2):
    n, tot, avg, dd, worst, wd, _ = run(10, add_day=k)
    print(f"  add after day {k} if up 0.5R: total={tot:+6.1f}R maxDD={dd:5.1f}R profit/DD={tot/dd:4.2f} worst trade={worst:+.2f}R worst day={wd:+.2f}R")
