"""Naoufel T (Chart Fanatics, StrategyQuant X algo trader): the three example systems from the episode. Screening only.
 1) S&P RSI(2): long when close > SMA200 and RSI(2) < 20, exit when RSI(2) > 70 (all at the close). SPX closes 1990-2026
    (CBOE, closes only) and NAS100 NY-session daily 2021-26. Variants of the 20/70 levels as a robustness map.
 2) Turnaround Tuesday (his AI example, classic rule): buy Monday's close if Monday closed down, sell Tuesday's close.
 3) Gold 'gold rush': buy Thursday's close if RSI(14) < 40, stop 1 x ATR(14), exit after 3 bars. Control: other weekdays.
Costs per trade as % of price: US500 spread ~0.01%, NAS ~0.006%, gold ~0.015%; long swap per night held: US500/NAS
8.2%/yr, gold 6%/yr (/360 per calendar night, weekends counted)."""
import csv, statistics as st, sys
from collections import defaultdict
from datetime import datetime, date
from vlib import nas_daily, gold_daily


def rsi(c, n):
    out = [None] * len(c); g = l = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]; up, dn = max(d, 0), max(-d, 0)
        if i <= n: g += up / n; l += dn / n
        else: g = (g * (n - 1) + up) / n; l = (l * (n - 1) + dn) / n
        if i >= n: out[i] = 100 if l == 0 else 100 - 100 / (1 + g / l)
    return out


def summary(name, tr):
    if not tr: print(name, "none"); return
    r = [x[1] for x in tr]; yr = defaultdict(float)
    for d, x, _ in tr: yr[d.year] += x
    eq = pk = dd = 0.0
    for x in r: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    days = sum(x[2] for x in tr)
    neg = sum(v < 0 for v in yr.values())
    print(f"{name:44s} n={len(r):4d} win={sum(x > 0 for x in r)/len(r):4.0%} avg={st.mean(r):+.3f}% tot={sum(r):+6.1f}% "
          f"maxDD={dd:4.1f}% nights={days:5d} losing yrs {neg}/{len(yr)}")
    return yr


def rsi2(dates, c, lo, hi, cost, swap):
    r2 = rsi(c, 2); tr = []; i = 200
    while i < len(c) - 1:
        if c[i] > st.mean(c[i - 199:i + 1]) and r2[i] < lo:
            j = i + 1
            while j < len(c) - 1 and r2[j] <= hi: j += 1
            n = (dates[j] - dates[i]).days
            tr.append((dates[i], 100 * (c[j] / c[i] - 1) - cost - swap * n, n)); i = j
        i += 1
    return tr


def tuesday(dates, c, cost, swap):
    tr = []
    for i in range(1, len(c) - 1):
        if dates[i].weekday() == 0 and c[i] < c[i - 1] and dates[i + 1].weekday() == 1:
            tr.append((dates[i], 100 * (c[i + 1] / c[i] - 1) - cost - swap, 1))
    return tr


def goldrush(D, wd, lvl, cost, swap):
    c = [x[4] for x in D]; r14 = rsi(c, 14); tr = []; i = 15
    while i < len(D) - 3:
        atr = st.mean(max(D[k][2], D[k-1][4]) - min(D[k][3], D[k-1][4]) for k in range(i - 13, i + 1))
        if D[i][0].weekday() == wd and r14[i] < lvl:
            e = c[i]; stop = e - atr; x = None
            for k in range(i + 1, i + 4):
                if D[k][1] <= stop: x = D[k][1]; break
                if D[k][3] <= stop: x = stop; break
            k = min(k, i + 3)
            if x is None: x = c[i + 3]
            n = (D[k][0].date() - D[i][0].date()).days
            tr.append((D[i][0].date(), 100 * (x / e - 1) - cost - swap * n, n)); i = k
        i += 1
    return tr


spx = [(datetime.strptime(r["DATE"], "%m/%d/%Y").date(), float(r["SPX"])) for r in csv.DictReader(open(sys.argv[1]))]
spx = [x for x in spx if x[0] >= date(1989, 1, 1)]
sd, sc = [x[0] for x in spx], [x[1] for x in spx]
nd = nas_daily(); nds, ncs = [x[0].date() for x in nd], [x[4] for x in nd]
SW_IDX, SW_G = 8.2 / 360, 6.0 / 360
print("== 1) RSI(2) above SMA200, exit RSI(2) > hi ==")
for lo, hi in ((20, 70), (10, 70), (30, 70), (20, 50), (20, 80)):
    y = summary(f"SPX 1990-2026 rsi2<{lo} exit>{hi}", rsi2(sd, sc, lo, hi, 0.01, SW_IDX))
    if (lo, hi) == (20, 70): print("   by decade:", {d: round(sum(v for k, v in y.items() if k // 10 * 10 == d), 1) for d in (1990, 2000, 2010, 2020)})
    summary(f"SPX 2021-2026 rsi2<{lo} exit>{hi}", [t for t in rsi2(sd, sc, lo, hi, 0.01, SW_IDX) if t[0].year >= 2021])
    summary(f"NAS 2021-2026 rsi2<{lo} exit>{hi}", rsi2(nds, ncs, lo, hi, 0.006, SW_IDX))
print("== 2) Turnaround Tuesday ==")
for a, b in ((1990, 2005), (2006, 2015), (2016, 2026)):
    summary(f"SPX {a}-{b}", [t for t in tuesday(sd, sc, 0.01, SW_IDX) if a <= t[0].year <= b])
summary("NAS 2021-2026", tuesday(nds, ncs, 0.006, SW_IDX))
print("== 3) Gold rush (weekday close, RSI14 < lvl, 1 ATR stop, 3 bars) ==")
gd = gold_daily()
for lvl in (40, 30, 50):
    for wd, nm in enumerate(("Mon", "Tue", "Wed", "Thu", "Fri")):
        summary(f"Gold 2021-26 {nm} rsi14<{lvl}", goldrush(gd, wd, lvl, 0.015, SW_G))
