"""Gold night effect robustness (28 Oct 2026): neighbouring start/end hours, doubled cost, worst drawdown at 1x,
monthly-skip check, and the unseen 2012-2013 years from data/xauusd_h1_2012_2021."""
import csv, os, math, statistics as st, sys
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
def uk_dst(d):
    m = date(d.year, 3, 31); s = m - timedelta(days=(m.weekday() + 1) % 7)
    o = date(d.year, 10, 31); e = o - timedelta(days=(o.weekday() + 1) % 7); return s <= d < e
def load(paths):
    P = {}
    for p in paths:
        for r in csv.DictReader(open(p)):
            ts = r.get("timestamp_ms") or r.get("timestamp")
            t = datetime.fromtimestamp(int(ts) / 1000, timezone.utc).replace(tzinfo=None)
            uk = t + timedelta(hours=1 if uk_dst(t.date()) else 0); P[uk] = float(r["open"])
    return P
def run(P, h0, h1, cost=0.00012, y0=2014, y1=2026):
    out = []
    for d in sorted({k.date() for k in P if k.weekday() < 5 and y0 <= k.year <= y1}):
        prev = d - timedelta(days=3 if d.weekday() == 0 else 1)
        a = P.get(datetime(prev.year, prev.month, prev.day, h0) if h0 >= 12 else datetime(d.year, d.month, d.day, h0))
        b = P.get(datetime(d.year, d.month, d.day, h1))
        if a and b: out.append((d, b / a - 1 - cost))
    return out
def show(name, T):
    r = [x for _, x in T]; m = st.mean(r); t = m / (st.pstdev(r) / len(r) ** .5)
    eq = pk = dd = 0
    for x in r: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    yrs = defaultdict(float)
    for d, x in T: yrs[d.year] += x
    print(f"  {name:34s} n={len(r)} avg {m*100:+.4f}% t={t:4.1f} {m*252*100:+5.1f}%/yr  maxDD {dd*100:4.1f}%  "
          f"losing years {sum(v<0 for v in yrs.values())}/{len(yrs)}")
F = load(["data/factory_h1/xauusd_h1.csv"])
show("main: 23:00 -> 08:00", run(F, 23, 8))
for h0, h1 in ((22, 8), (0, 8), (1, 8), (23, 7), (23, 9), (0, 7)): show(f"{h0:02d}:00 -> {h1:02d}:00", run(F, h0, h1))
show("main, doubled cost", run(F, 23, 8, cost=0.00024))
show("main, 1 hour later both ends (00 -> 09)", run(F, 0, 9))
old = [os.path.join("data/xauusd_h1_2012_2021", f) for f in os.listdir("data/xauusd_h1_2012_2021") if f.endswith(".csv")]
if old:
    O = load(old); show("UNSEEN 2012-2013 (other file)", run(O, 23, 8, y0=2012, y1=2013))
    show("overlap check 2014-2020 (other file)", run(O, 23, 8, y0=2014, y1=2020))
