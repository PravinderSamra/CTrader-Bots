"""Gold daily trend-following (pre-registered 28 Oct 2026, before any run; classic untuned rules).
T1 12-month momentum: long while the close is above the close 252 trading days earlier, else flat (decided at the
   close, acted at the next open).
T2 50/200 moving-average cross: long while the 50-day average is above the 200-day, else flat.
T3 Turtle: long on a close above the 55-day high, exit on a close below the 20-day low; short the mirror image.
Costs: 0.012% per position change, swap 5%/yr on every night held (long or short, conservative).
Benchmark: buy and hold with the same swap. Data: XAUUSD daily closes 2011-06..2026-10 (from H1).
Pass: Sharpe >= 0.5 overall, positive in both 2011-18 and 2019-26, AND (Sharpe above buy-and-hold OR max drawdown at
least 30% smaller than buy-and-hold's)."""
import csv, math, statistics as st
from datetime import datetime, timezone
from collections import OrderedDict
P = {}
for p in ("data/xauusd_h1_2012_2021/xauusd_h1.csv", "data/factory_h1/xauusd_h1.csv"):
    for r in csv.DictReader(open(p)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        P[t] = (float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]))
D = OrderedDict()
for t in sorted(P):
    d = t.date() if t.hour < 21 else (t.replace(hour=0) + __import__("datetime").timedelta(days=1)).date()   # 21:00 UTC rollover
    o, h, l, c = P[t]
    if d not in D: D[d] = [o, h, l, c]
    else: x = D[d]; x[1] = max(x[1], h); x[2] = min(x[2], l); x[3] = c
days = [d for d in D if d.weekday() < 5]; O = [D[d][0] for d in days]; H = [D[d][1] for d in days]
L = [D[d][2] for d in days]; C = [D[d][3] for d in days]; n = len(C)
def sma(i, k): return sum(C[i-k+1:i+1]) / k
def position(rule):
    pos = [0] * n
    for i in range(252, n):
        if rule == "T1": pos[i] = 1 if C[i] > C[i-252] else 0
        elif rule == "T2": pos[i] = 1 if sma(i, 50) > sma(i, 200) else 0
        else:
            p = pos[i-1]
            if p <= 0 and C[i] > max(H[i-55:i]): p = 1
            elif p >= 0 and C[i] < min(L[i-55:i]): p = -1
            elif p == 1 and C[i] < min(L[i-20:i]): p = 0
            elif p == -1 and C[i] > max(H[i-20:i]): p = 0
            pos[i] = p
        if rule == "BH": pos[i] = 1
    return pos
def daily(pos):
    r = []
    for i in range(253, n):
        p = pos[i-1]                               # decided at yesterday's close, held from today's open
        x = p * (C[i] / C[i-1] - 1) if p else 0.0
        if pos[i-1] != pos[i-2]: x -= 0.00012 * abs(pos[i-1] - pos[i-2])
        if p: x -= 0.05 / 365 * (days[i] - days[i-1]).days
        r.append((days[i], x))
    return r
def stats(r):
    v = [x for _, x in r]; sh = st.mean(v) / st.pstdev(v) * math.sqrt(252) if st.pstdev(v) else 0
    eq = 1; pk = 1; dd = 0
    for x in v: eq *= 1 + x; pk = max(pk, eq); dd = max(dd, 1 - eq / pk)
    yrs = len(v) / 252; cagr = eq ** (1 / yrs) - 1
    return sh, cagr, dd
res = {}
for rule in ("BH", "T1", "T2", "T3"):
    r = daily(position(rule)); sh, cagr, dd = stats(r)
    a = [x for d, x in r if d.year <= 2018]; b = [x for d, x in r if d.year >= 2019]
    res[rule] = (sh, cagr, dd)
    yrs = {}
    for d, x in r: yrs[d.year] = yrs.get(d.year, 1) * (1 + x)
    line = f"{rule}: Sharpe {sh:.2f}  {cagr*100:+.1f}%/yr  max DD {dd*100:.0f}%  2011-18 {sum(a)*100:+.0f}%  2019-26 {sum(b)*100:+.0f}%"
    if rule != "BH":
        bsh, _, bdd = res["BH"]
        ok = sh >= 0.5 and sum(a) > 0 and sum(b) > 0 and (sh > bsh or dd <= 0.7 * bdd)
        line += "  PASS" if ok else "  fail"
    print(line); print("    " + " ".join(f"{y}:{(v-1)*100:+.0f}%" for y, v in sorted(yrs.items())))
