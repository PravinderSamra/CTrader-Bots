"""Gold seasonality (pre-registered 28 Oct 2026, before any run). Published claim: Baur (2013) 'The autumn effect of
gold' - September and November strongest (data to 2010). Everything from 2011 is unseen by that paper.
Trial S1: long gold for September and November (first trading day open -> last trading day close of the month).
Trial S2: long gold for January (popular claim).
Costs: 0.012% per trade + swap 5%/yr for nights held (FTMO gold long). Data: XAUUSD H1 2011-06..2026-10 (two files).
Pass: average month after costs > 0, at least 0.5% better than the average of all other months (raw), positive in
>= 60% of years, and positive in both halves (2011-18 and 2019-26)."""
import csv, statistics as st
from datetime import datetime, timezone, date
from collections import defaultdict
P = {}
for p in ("data/xauusd_h1_2012_2021/xauusd_h1.csv", "data/factory_h1/xauusd_h1.csv"):
    for r in csv.DictReader(open(p)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        P[t] = (float(r["open"]), float(r["close"]))
ks = sorted(P); mon = defaultdict(list)
for k in ks: mon[(k.year, k.month)].append(k)
ret = {}
for (y, m), v in mon.items():
    if (y, m) in ((2011, 6), (2026, 10)) or len(v) < 300: continue
    o, c = P[v[0]][0], P[v[-1]][1]; nights = (v[-1].date() - v[0].date()).days
    ret[(y, m)] = (c / o - 1, c / o - 1 - 0.00012 - 0.05 / 365 * nights)
allm = defaultdict(list)
for (y, m), (raw, net) in ret.items(): allm[m].append(raw)
print("Average raw month (2011-07..2026-09): " + "  ".join(f"{m}:{st.mean(v)*100:+.2f}%" for m, v in sorted(allm.items())))
for name, months in (("S1 Sep + Nov", (9, 11)), ("S2 January", (1,))):
    tr = [(y, m, net) for (y, m), (raw, net) in ret.items() if m in months]
    other = [raw for (y, m), (raw, net) in ret.items() if m not in months]
    rawin = [raw for (y, m), (raw, net) in ret.items() if m in months]
    nets = [x for *_, x in tr]; yrs = defaultdict(float)
    for y, m, x in tr: yrs[y] += x
    h1 = [x for y, m, x in tr if y <= 2018]; h2 = [x for y, m, x in tr if y >= 2019]
    ok = st.mean(nets) > 0 and st.mean(rawin) - st.mean(other) >= 0.005 and sum(v > 0 for v in yrs.values()) / len(yrs) >= 0.6 \
         and st.mean(h1) > 0 and st.mean(h2) > 0
    print(f"{name}: {len(nets)} months, avg after costs {st.mean(nets)*100:+.2f}%  (raw {st.mean(rawin)*100:+.2f}% vs other months "
          f"{st.mean(other)*100:+.2f}%)  years up {sum(v>0 for v in yrs.values())}/{len(yrs)}  2011-18 {st.mean(h1)*100:+.2f}%  "
          f"2019-26 {st.mean(h2)*100:+.2f}%" + ("  PASS" if ok else "  fail"))
    print("   by year: " + " ".join(f"{y}:{v*100:+.1f}%" for y, v in sorted(yrs.items())))
