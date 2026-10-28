"""EURUSD flow-timing tests M1 / F1 / F2, rules frozen in EURUSD_FLOWS_TEST_PLAN.md (28 Oct 2026)."""
import csv, sys, math, statistics as st
from datetime import datetime, timezone, date, timedelta
from collections import defaultdict
sys.path.insert(0, "ssrn"); from fomc_drift import MEET, ny_offset
D = "data/"
def h1(path):
    return {datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None): float(r["open"])
            for r in csv.DictReader(open(path))}
def d1(path):   # session date -> close (bars stamped 21:00/22:00 UTC the evening before the session)
    return {(datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc) + timedelta(hours=4)).date(): float(r["close"])
            for r in csv.DictReader(open(path))}
def uk_offset(d):
    lm = date(d.year, 3, 31); s = lm - timedelta(days=(lm.weekday() + 1) % 7)
    lo = date(d.year, 10, 31); e = lo - timedelta(days=(lo.weekday() + 1) % 7)
    return 1 if s <= d < e else 0
EU = h1(D + "eurusd_h1.csv"); NQ = h1(D + "factory_h1/nas100_h1.csv")
SPX = d1(D + "factory_d1/us500_d1.csv"); SX5 = d1(D + "factory_d1/eustx50_d1.csv")
def px(S, d, hour_local, off):
    return S.get(datetime(d.year, d.month, d.day) + timedelta(hours=hour_local - off))
COST, STRESS, SWAP = 1.0, 2.0, 3.27 / 365 * 1e4 / 100   # bp; swap bp per night
def report(name, tr):
    g = [b for _, b, _ in tr]
    for c, lab in ((COST, "1bp"), (STRESS, "2bp")):
        net = [x - c - s for x, (_, _, s) in zip(g, tr)]
        m, sd = st.mean(net), st.stdev(net); t = m / sd * math.sqrt(len(net))
        yr = defaultdict(float)
        for (d, _, _), x in zip(tr, net): yr[d.year] += x
        h1_ = [x for (d, _, _), x in zip(tr, net) if d.year <= 2019]; h2 = [x for (d, _, _), x in zip(tr, net) if d.year >= 2020]
        up = sum(v > 0 for v in yr.values())
        print(f"{name} {lab}: n {len(net)} avg {m:+.2f} bp t {t:+.2f} | 2014-19 {st.mean(h1_):+.2f} 2020-26 {st.mean(h2):+.2f} | years up {up}/{len(yr)}")
    print("   gross avg %+.2f bp; by year (1bp): " % st.mean(g) + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(
        {y: sum(x - COST - s for (d, x, s) in tr if d.year == y) for y in {d.year for d, _, _ in tr}}.items())))
# M1 month-end
sess = sorted(d for d in SPX if d in SX5 and d.weekday() < 5)
last = {}
for d in sess: last[(d.year, d.month)] = d
tr = []
for (y, m), T in sorted(last.items()):
    prev = [d for d in sess if d < T]
    if not prev: continue
    pm_end = [d for d in prev if (d.year, d.month) < (y, m)]
    if not pm_end or (y, m) == (sess[-1].year, sess[-1].month) and T == sess[-1] and T.day < 25: continue
    a, b = pm_end[-1], prev[-1]
    if b <= a: continue
    sig = 1 if SPX[b] / SPX[a] - 1 > SX5[b] / SX5[a] - 1 else -1
    o = uk_offset(T); p0, p1 = px(EU, T, 8, o), px(EU, T, 16, o)
    if p0 and p1: tr.append((T, sig * (p1 / p0 - 1) * 1e4, 0.0))
report("M1 month-end", tr)
# F1 / F2
for name, hr in (("F1 pre 14:00->14:00", 14), ("F2 day 16:00->16:00", 16)):
    tr = []; nq = []
    for s in MEET:
        d0 = date.fromisoformat(s); d1_ = d0 + timedelta(days=1)
        a, b = px(EU, d0, hr, ny_offset(d0)), px(EU, d1_, hr, ny_offset(d1_))
        qa, qb = px(NQ, d0, hr, ny_offset(d0)), px(NQ, d1_, hr, ny_offset(d1_))
        if a and b:
            tr.append((d0, (b / a - 1) * 1e4, SWAP))
            if qa and qb: nq.append(((b / a - 1), (qb / qa - 1)))
    report(name, tr)
    xs, ys = zip(*nq); print(f"   correlation with US100 long, same window: {st.correlation(xs, ys):+.2f} (n {len(nq)})")
