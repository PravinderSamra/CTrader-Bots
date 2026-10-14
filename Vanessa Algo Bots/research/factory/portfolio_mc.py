"""Factory candidates as they would trade live (5-day hold + 3 x ATR(20) catastrophe stop), then added to the
account Monte Carlo with the NAS bot ($550) and Daily Systems. Daily P/L booked on the exit day."""
import sys, statistics as st
from collections import defaultdict
import numpy as np
import factory_d1 as F
sys.path.insert(0, F.R0 + "/scripts")
import monte_carlo as MC

CANDS = {"A: BB2.5 any trend": ("BB", 2.5, "none"), "B: BB2.0 uptrend only": ("BB", 2.0, "trend")}


def live_trades(ek, ep, f, hold=5, cat=10.0):
    out = []
    for m in F._M["IDX"]:
        sig = F.entry_signal(m, ek, ep, 1) & F.filt(m, f, 1)
        o, h, l, c, A = m.o, m.h, m.l, m.c, m.atr; n = len(c); nxt = 0
        for s in np.flatnonzero(sig):
            if s < nxt or s + 1 >= n or not A[s] > 0: continue
            e = o[s + 1]; stop = e - cat * A[s]; x = None; j = s + 1
            last = min(n - 1, s + hold)
            while j <= last:
                if l[j] <= stop: x = min(stop, o[j]) if j > s + 1 else stop; break
                if j == last: x = c[j]; break
                j += 1
            nights = (m.dates[j] - m.dates[s + 1]).days
            r = (x - e - m.cost * e - m.swap * e * nights) / (2 * A[s])     # 1R = 2 x ATR
            out.append((m.dates[j], r, m.name)); nxt = j + 1
    return sorted(out)


if __name__ == "__main__":
    F._init("IDX")
    daily = {}
    for name, (ek, ep, f) in CANDS.items():
        T = live_trades(ek, ep, f)
        rs = [r for _, r, _ in T]; eq = pk = dd = 0
        for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
        d = defaultdict(float)
        for x, r, _ in T: d[x.isoformat()] += r
        daily[name] = d
        recent = [r for x, r, _ in T if x.year >= 2021]
        print(f"{name}: {len(T)} trades, avg {st.mean(rs):+.3f}R, 2021-26 avg {st.mean(recent):+.3f}R ({len(recent)} trades, "
              f"{len(recent)/5.8:.0f}/yr), max DD {dd:.1f}R, worst trade {min(rs):+.2f}R, worst day {min(d.values()):+.2f}R")
    keys = sorted(k for k in set(MC.ds) | set(MC.nas) | set(daily["A: BB2.5 any trend"]) if "2021-01-01" <= k <= "2026-10-31")
    print(f"\nMonte Carlo, {len(keys)} days 2021-26, start $97,421, pass $110k, fail $90k or a -$5k day")
    base = [MC.ds.get(k, 0) + MC.nas.get(k, 0) * 550 for k in keys]
    p, fl, md = MC.sim(base); print(f"  NAS $550 + Daily Systems (now)                pass {p:5.1%} fail {fl:5.1%} median {md} days")
    for name, d in daily.items():
        for usd in (100, 200, 300):
            days = [b + d.get(k, 0) * usd for b, k in zip(base, keys)]
            p, fl, md = MC.sim(days)
            print(f"  + {name:22s} ${usd}/R (disaster stop 10xATR)  pass {p:5.1%} fail {fl:5.1%} median {md} days")
    both = [b + (daily["A: BB2.5 any trend"].get(k, 0) + daily["B: BB2.0 uptrend only"].get(k, 0)) * 200 for b, k in zip(base, keys)]
    p, fl, md = MC.sim(both); print(f"  + A and B together $200/R                      pass {p:5.1%} fail {fl:5.1%} median {md} days")
    for name, d in daily.items():
        for other, src in (("Daily Systems", MC.ds), ("NAS bot", MC.nas)):
            a = [d.get(k, 0) for k in keys]; b = [src.get(k, 0) for k in keys]
            print(f"  corr {name} vs {other}: {st.correlation(a, b):+.2f}")
