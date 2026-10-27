"""CPI close->close on US100: robustness (t-stat, bootstrap, neighbouring windows, US30, doubled cost, year by year)."""
import csv, json, random, statistics as st, sys
from datetime import datetime, timezone, timedelta, date
sys.path.insert(0, "ssrn"); from fomc_drift import ny_offset
CPI = sorted(date.fromisoformat(x["date"]) for x in json.load(open("data/macro_dates/cpi.json"))["release_dates"])
SW = 0.05 / 365
def load(m):
    b = {}
    for r in csv.DictReader(open(f"data/factory_h1/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=ny_offset(t.date())); b[ny] = (float(r["open"]), float(r["close"]))
    return b
def k(d, h): return datetime(d.year, d.month, d.day, h)
def run(b, start, end, cost=0.00025):
    out = []
    for d in CPI:
        if d.year < 2014: continue
        prev = d - timedelta(days=3 if d.weekday() == 0 else 1)
        (da, ha, fa), (dz, hz, fz) = start(prev, d), end(prev, d)
        if k(da, ha) not in b or k(dz, hz) not in b: continue
        pa = b[k(da, ha)][fa]; pz = b[k(dz, hz)][fz]
        out.append((d, pz / pa - 1 - cost - SW * (dz - da).days))
    return out
def show(name, T):
    r = [x for _, x in T]; m = st.mean(r); t = m / (st.pstdev(r) / len(r) ** .5)
    random.seed(5); bs = sorted(st.mean(random.choices(r, k=len(r))) for _ in range(4000))
    print(f"  {name:44s} n={len(r)} avg {m*100:+.3f}% t={t:4.1f} 95% [{bs[100]*100:+.3f}, {bs[3899]*100:+.3f}] win {sum(x>0 for x in r)/len(r):.0%}")
CLOSE = lambda p, d: (p, 15, 1)
for m in ("nas100", "us500", "us30"):
    b = load(m); print(m)
    show("close before -> close on CPI day (the pass)", run(b, CLOSE, lambda p, d: (d, 15, 1)))
    if m == "nas100":
        show("  doubled cost", run(b, CLOSE, lambda p, d: (d, 15, 1), cost=0.0005))
        show("close before -> 08:00 (before the number)", run(b, CLOSE, lambda p, d: (d, 8, 0)))
        show("close before -> 10:00 (after the open)", run(b, CLOSE, lambda p, d: (d, 10, 0)))
        show("close before -> 12:00", run(b, CLOSE, lambda p, d: (d, 12, 0)))
        show("14:00 before -> close on CPI day", run(b, lambda p, d: (p, 14, 0), lambda p, d: (d, 15, 1)))
        T = run(b, CLOSE, lambda p, d: (d, 15, 1)); yrs = {}
        for d, x in T: yrs.setdefault(d.year, []).append(x)
        print("   by year: " + "  ".join(f"{y} {sum(v)*100:+.1f}%" for y, v in sorted(yrs.items())))
