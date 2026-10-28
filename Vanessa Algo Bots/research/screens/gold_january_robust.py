"""Gold January robustness: t-stat, neighbouring windows, worst point inside the month, and the dollar size."""
import csv, statistics as st
from datetime import datetime, timezone, date, timedelta
P = {}
for p in ("data/xauusd_h1_2012_2021/xauusd_h1.csv", "data/factory_h1/xauusd_h1.csv"):
    for r in csv.DictReader(open(p)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        P[t] = (float(r["open"]), float(r["low"]), float(r["close"]))
ks = sorted(P)
def window(a, b):
    out = []
    for y in range(2012, 2027):
        A, B = a(y), b(y); seg = [k for k in ks if A <= k < B]
        if len(seg) < 50: continue
        o = P[seg[0]][0]; c = P[seg[-1]][2]; low = min(P[k][1] for k in seg)
        out.append((y, c / o - 1 - 0.00012 - 0.05 / 365 * (B - A).days, low / o - 1))
    return out
def show(name, T):
    r = [x for _, x, _ in T]; m = st.mean(r); t = m / (st.pstdev(r) / len(r) ** .5)
    print(f"  {name:34s} n={len(r)} avg {m*100:+.2f}% t={t:3.1f} up {sum(x>0 for x in r)}/{len(r)}  worst year {min(r)*100:+.1f}%  "
          f"deepest dip inside {min(d for *_, d in T)*100:+.1f}%")
show("January (1 Jan -> 1 Feb)", window(lambda y: datetime(y, 1, 1), lambda y: datetime(y, 2, 1)))
show("15 Dec -> 31 Jan", window(lambda y: datetime(y - 1, 12, 15), lambda y: datetime(y, 2, 1)))
show("1st half of January", window(lambda y: datetime(y, 1, 1), lambda y: datetime(y, 1, 16)))
show("2nd half of January", window(lambda y: datetime(y, 1, 16), lambda y: datetime(y, 2, 1)))
show("January + February", window(lambda y: datetime(y, 1, 1), lambda y: datetime(y, 3, 1)))
show("December (control)", window(lambda y: datetime(y - 1, 12, 1), lambda y: datetime(y, 1, 1)))
