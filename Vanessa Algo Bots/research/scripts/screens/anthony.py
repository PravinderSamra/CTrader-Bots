"""Anthony Crudele (Chart Fanatics, 20-yr index futures trader) daily Bollinger (20, 3 SD) regime system. Screening only.
 A) Expansion = trend: bands opening (upper rising AND lower falling) and close at a 20-day closing high -> long only
    (mirror short). Optional squeeze filter: band width 5 days earlier below its 100-day median (came out of a range).
    Exit on a close below EMA(n) (his 8/21/34 MAs are his exit guide; n = 8 or 21).
 B) Mean reversion ('Beacon'): when the upper band peaks (stops rising after >= 5 up days) take the band values at the peak,
    width W = upper - lower. Levels measured down from the upper band: 30%, 50%. A daily close below the 30% line within
    20 days -> short at the close, target the 50% line, exit on a close back above the stop line (30% line, or the peak
    upper band = wide). Mirror for longs after the lower band troughs (his April 2025 example).
Signals and exits on daily closes. NAS100 NY-session daily 2021-26, SPX closes 1990-2026 (CBOE), gold daily 2021-26.
Costs as % of price per trade: SPX 0.01, NAS 0.006, gold 0.015; swap per night long 8.2%/yr (gold 6%), short 2%/yr."""
import csv, statistics as st, sys
from datetime import datetime, date
from vlib import nas_daily, gold_daily


def bb(c, i, n=20, k=3.0):
    w = c[i - n + 1:i + 1]; m = st.mean(w); s = st.pstdev(w); return m + k * s, m - k * s


def ema(c, n):
    a = 2 / (n + 1); out = [c[0]]
    for x in c[1:]: out.append(out[-1] + a * (x - out[-1]))
    return out


def summ(name, tr, yrs):
    if not tr: print(f"{name:46s} none"); return
    r = [x[1] for x in tr]; eq = pk = dd = 0.0
    for x in r: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    nights = sum(x[2] for x in tr)
    print(f"{name:46s} n={len(r):4d} ({len(r)/yrs:4.1f}/yr) win={sum(x > 0 for x in r)/len(r):4.0%} avg={st.mean(r):+.3f}% "
          f"tot={sum(r):+6.1f}% maxDD={dd:5.1f}% in mkt {nights/(yrs*365):4.0%}")


def pnl(side, e, x, n, cost, sl, ss):
    return side * 100 * (x / e - 1) - cost - (sl if side == 1 else ss) * n


def expansion(d, c, emn, squeeze, cost, sl, ss):
    U, L = [None] * len(c), [None] * len(c)
    for i in range(19, len(c)): U[i], L[i] = bb(c, i)
    W = [None if U[i] is None else U[i] - L[i] for i in range(len(c))]
    E = ema(c, emn); tr = []; i = 125
    while i < len(c) - 1:
        opening = U[i] > U[i - 1] and L[i] < L[i - 1]
        sq = (not squeeze) or W[i - 5] < st.median(W[i - 105:i - 5])
        side = 1 if c[i] > max(c[i - 20:i]) else -1 if c[i] < min(c[i - 20:i]) else 0
        if opening and sq and side:
            j = i + 1
            while j < len(c) - 1 and (c[j] - E[j]) * side > 0: j += 1
            tr.append((d[i], pnl(side, c[i], c[j], (d[j] - d[i]).days, cost, sl, ss), (d[j] - d[i]).days)); i = j
        i += 1
    return tr


def meanrev(d, c, wide, cost, sl, ss, sides=(1, -1)):
    U, L = [None] * len(c), [None] * len(c)
    for i in range(19, len(c)): U[i], L[i] = bb(c, i)
    tr = []; i = 30
    while i < len(c) - 1:
        done = False
        for side in sides:   # side -1: after an upper-band peak (short); +1: after a lower-band trough (long)
            B = U if side == -1 else L
            k = i - 1
            if not all((B[k - m] - B[k - m - 1]) * -side > 0 for m in range(5)) or (B[i] - B[k]) * -side > 0: continue
            top, bot = (U[k], L[k]) if side == -1 else (L[k], U[k])
            w = top - bot; l30, l50 = top - 0.3 * w, top - 0.5 * w
            stop_line = top if wide else l30
            for j in range(i, min(i + 20, len(c) - 1)):
                if (c[j] - l30) * -side > 0 or (side == 1 and c[j] > l30) or (side == -1 and c[j] < l30):
                    pass
                if (side == -1 and c[j] < l30) or (side == 1 and c[j] > l30):
                    e = c[j]; m = j + 1
                    while m < len(c) - 1:
                        if (side == -1 and (c[m] <= l50 or c[m] > stop_line)) or (side == 1 and (c[m] >= l50 or c[m] < stop_line)): break
                        m += 1
                    tr.append((d[j], pnl(side, e, c[m], (d[m] - d[j]).days, cost, sl, ss), (d[m] - d[j]).days)); i = m; done = True
                    break
            if done: break
        i += 1
    return tr


spx = [(datetime.strptime(r["DATE"], "%m/%d/%Y").date(), float(r["SPX"])) for r in csv.DictReader(open(sys.argv[1]))]
spx = [x for x in spx if x[0] >= date(1989, 6, 1)]
nd, gd = nas_daily(), gold_daily()
sets = (("SPX 1990-26", [x[0] for x in spx], [x[1] for x in spx], 0.01, 8.2 / 360, 2 / 360, 36.5),
        ("NAS 2021-26", [x[0].date() for x in nd], [x[4] for x in nd], 0.006, 8.2 / 360, 2 / 360, 5.5),
        ("Gold 2021-26", [x[0].date() for x in gd], [x[4] for x in gd], 0.015, 6 / 360, 2 / 360, 5.5))
for name, d, c, cost, sl, ss, yrs in sets:
    print(f"== {name} ==")
    for emn in (8, 21):
        for sq in (False, True):
            t = expansion(d, c, emn, sq, cost, sl, ss)
            summ(f"A expansion exit<EMA{emn} squeeze={int(sq)} both", t, yrs)
            summ(f"   long only", [x for x in t if x[1] is not None and x in t and True][:0] or None, yrs) if False else None
    for side, nm in ((1, "long"), (-1, "short")):
        t = [x for x in expansion(d, c, 21, False, cost, sl, ss)]
    for wide in (False, True):
        summ(f"B meanrev both stop={'peak band' if wide else '30% line'}", meanrev(d, c, wide, cost, sl, ss), yrs)
        summ(f"B meanrev short-only stop={'peak band' if wide else '30% line'}", meanrev(d, c, wide, cost, sl, ss, (-1,)), yrs)
        summ(f"B meanrev long-only stop={'peak band' if wide else '30% line'}", meanrev(d, c, wide, cost, sl, ss, (1,)), yrs)
