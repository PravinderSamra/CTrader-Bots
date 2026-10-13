"""'Traveling Trader' Z (Chart Fanatics): the S&P tends to bounce at -10% / -20% from its high. Screening only.
SPX closes 1990-2026 (CBOE, closes only, no dividends). Signal: first close >= d% below the running all-time closing high
(re-armed once the index is back within 5% of its high). Report forward returns after 20/60/120 trading days and the worst
further fall in those 60 days, against the average of all days (baseline drift)."""
import csv, statistics as st, sys
from datetime import datetime, date

rows = [(datetime.strptime(r["DATE"], "%m/%d/%Y").date(), float(r["SPX"])) for r in csv.DictReader(open(sys.argv[1]))]
rows = [x for x in rows if x[0] >= date(1985, 1, 1)]
d, c = [x[0] for x in rows], [x[1] for x in rows]


def fwd(i, n): return 100 * (c[min(i + n, len(c) - 1)] / c[i] - 1)


base = {n: st.mean(fwd(i, n) for i in range(len(c) - n) if d[i].year >= 1990) for n in (20, 60, 120)}
print("baseline all days 1990-2026:", {n: f"{v:+.2f}%" for n, v in base.items()})
for dd in (10, 15, 20):
    hi = c[0]; armed = True; sig = []
    for i in range(len(c)):
        hi = max(hi, c[i])
        if c[i] >= 0.95 * hi: armed = True
        if armed and c[i] <= (1 - dd / 100) * hi and d[i].year >= 1990:
            sig.append(i); armed = False
    print(f"\n-{dd}% from high: {len(sig)} signals")
    for i in sig:
        mae = 100 * (min(c[i:i + 61]) / c[i] - 1)
        print(f"  {d[i]}  +20d {fwd(i,20):+6.1f}%  +60d {fwd(i,60):+6.1f}%  +120d {fwd(i,120):+6.1f}%  worst within 60d {mae:+6.1f}%")
    for n in (20, 60, 120):
        v = [fwd(i, n) for i in sig if i + n < len(c)]
        print(f"  avg +{n}d {st.mean(v):+.2f}% (median {st.median(v):+.2f}%, up {sum(x > 0 for x in v)}/{len(v)})")
