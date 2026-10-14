"""Risk design for the factory candidate (live form): catastrophe stop width and a cap on simultaneous positions.
Positions are taken in signal order; with a cap, extra signals that day are skipped (alphabetical market order)."""
import statistics as st
from collections import defaultdict
import numpy as np
import factory_d1 as F

def trades(ek, ep, f, cat, hold=5):
    ev = []
    for m in F._M["IDX"]:
        sig = F.entry_signal(m, ek, ep, 1) & F.filt(m, f, 1)
        o, h, l, c, A = m.o, m.h, m.l, m.c, m.atr; n = len(c); nxt = 0
        for s in np.flatnonzero(sig):
            if s < nxt or s + 1 >= n or not A[s] > 0: continue
            e = o[s + 1]; stop = e - cat * A[s]; x = None; j = s + 1; last = min(n - 1, s + hold)
            while j <= last:
                if l[j] <= stop: x = min(stop, o[j]) if j > s + 1 else stop; break
                if j == last: x = c[j]; break
                j += 1
            nights = (m.dates[j] - m.dates[s + 1]).days
            r = (x - e - m.cost * e - m.swap * e * nights) / (2 * A[s])
            ev.append((m.dates[s + 1], m.dates[j], r, m.name)); nxt = j + 1
    return sorted(ev)

def capped(ev, cap):
    out = []; open_ = []
    for d0, d1, r, nm in ev:
        open_ = [x for x in open_ if x >= d0]
        if cap and len(open_) >= cap: continue
        open_.append(d1); out.append((d0, d1, r, nm))
    return out

F._init("IDX")
for label, (ek, ep, f) in (("A BB2.5 any", ("BB", 2.5, "none")), ("B BB2.0 uptrend", ("BB", 2.0, "trend"))):
    for cat in (3.0, 5.0, 99):
        ev = trades(ek, ep, f, cat)
        for cap in (0, 3, 2):
            T = capped(ev, cap); rs = [x[2] for x in T]
            eq = pk = dd = 0
            for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
            day = defaultdict(float)
            for x in T: day[x[1]] += x[2]
            rec = [x[2] for x in T if x[0].year >= 2021]; old = [x[2] for x in T if x[0].year < 2021]
            print(f"{label:16s} stop {'none' if cat == 99 else f'{cat:.0f}xATR':6s} max pos {cap or 'all':3} | n={len(T):3d} avg={st.mean(rs):+.3f}R "
                  f"(to 2020 {st.mean(old):+.3f}, 2021-26 {st.mean(rec):+.3f}) maxDD={dd:5.1f}R worst day={min(day.values()):+6.2f}R total={sum(rs):+5.0f}R")
