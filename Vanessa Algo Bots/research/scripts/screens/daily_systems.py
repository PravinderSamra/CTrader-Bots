import csv, sys, statistics as st
from collections import defaultdict
from datetime import datetime, timezone, date
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")
# NY-session daily bars (09:30-16:00): M30 2021-23 + m5 2023-26
day = {}
def add(t, o, h, l, c):
    d = t.date()
    if not ((9, 30) <= (t.hour, t.minute) < (16, 0)): return
    x = day.get(d)
    if x is None: day[d] = [o, h, l, c, t]
    else:
        x[1] = max(x[1], h); x[2] = min(x[2], l)
        if t >= x[4]: x[3] = c; x[4] = t
for f, cut in (("Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv", None), ("US30 London Range Breakout/data/NAS100/nas100_m5.csv", None)):
    for r in csv.DictReader(open(f)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
        add(t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
ds = sorted(d for d in day if d >= date(2020, 12, 28))
O = [day[d][0] for d in ds]; H = [day[d][1] for d in ds]; L = [day[d][2] for d in ds]; C = [day[d][3] for d in ds]
print("days", len(ds), ds[0], ds[-1])
SPREAD, SWAP = 1.2, 0.082 / 360
def ma(a, i, n): return sum(a[i-n+1:i+1]) / n
def run(name, entry, exitf, start=210):
    trades = []; i = start
    while i < len(C) - 1:
        if entry(i):
            e = C[i]; j = i + 1
            while j < len(C) - 1 and not exitf(i, j): j += 1
            nights = (ds[j] - ds[i]).days
            r = (C[j] - e - SPREAD) / e - SWAP * nights
            trades.append((ds[i], ds[j], r)); i = j + 1
        else: i += 1
    rs = [r for *_, r in trades]
    eq = pk = dd = 0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    by = defaultdict(float)
    for a, b, r in trades: by[a.year] += r
    print(f"{name:42} {len(rs):3} trades, win {sum(r>0 for r in rs)/len(rs):.0%}, avg {100*st.mean(rs):+.2f}%, total {100*sum(rs):+.1f}%, maxDD {100*dd:.1f}%",
          {y: f"{100*v:+.1f}" for y, v in sorted(by.items())})
    return trades
dev = lambda i: abs(C[i] - ma(C, i, 5))
# 1. mean reversion long (stocks/indices: long side), only in an uptrend
mr = run("Mean reversion long (dev>2.5x avg, >200MA)",
    lambda i: C[i] < ma(C, i, 5) and dev(i) > 2.5 * st.mean(dev(k) for k in range(i-20, i)) and C[i] > ma(C, i, 200),
    lambda i, j: C[j] > ma(C, j, 5) or j - i >= 4)
# 2. trend following: close at 100-day high, exit close below 10MA
tf = run("Trend following (100d high, exit <10MA)",
    lambda i: C[i] > max(C[i-100:i]),
    lambda i, j: C[j] < ma(C, j, 10))
# 3. short-term momentum: range > 2x 5-day avg range, up close; exit after 5 days
sm = run("Short-term momentum (range>2x, up day, 5d)",
    lambda i: (H[i]-L[i]) > 2 * st.mean(H[k]-L[k] for k in range(i-5, i)) and C[i] > O[i],
    lambda i, j: j - i >= 5)
print("Buy & hold same period: %+.1f%%" % (100 * (C[-1] / C[210] - 1)))
# correlation with the NAS bot (daily), using mean-reversion and trend positions' daily returns
sys.path.insert(0, "Vanessa Algo Bots/research/scripts")
import monte_carlo_test as mc
risk, pl = {}, {}
for line in mc.LOG.read_text().splitlines():
    m = mc.L_RE.search(line)
    if m: risk[m.group(1)+m.group(2)+m.group(3)] = float(m.group(4)); continue
    m = mc.T_RE.search(line)
    if m: pl[m.group(1)] = pl.get(m.group(1), 0.0) + float(m.group(2))
bot = {datetime.strptime(k, "%Y%m%d").date(): pl[k] / risk[k] for k in pl}
idx = {d: i for i, d in enumerate(ds)}
for name, tr in (("mean reversion", mr), ("trend following", tf), ("momentum", sm)):
    daily = defaultdict(float)
    for a, b, _ in tr:
        for k in range(idx[a] + 1, idx[b] + 1): daily[ds[k]] += (C[k] - C[k-1]) / C[k-1]
    com = [d for d in bot if d in idx and d >= ds[210]]
    x = [bot[d] for d in com]; y = [daily.get(d, 0.0) for d in com]
    mx, my = st.mean(x), st.mean(y)
    c = sum((a-mx)*(b-my) for a, b in zip(x, y)) / (len(x) * st.pstdev(x) * st.pstdev(y))
    print(f"correlation with NAS bot ({name}): {c:+.2f}")
