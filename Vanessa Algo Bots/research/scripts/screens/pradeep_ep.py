"""Pradeep Bonde (Stockbee) episodic pivots on FTMO's US stock list, daily bars (Yahoo, split-adjusted) 2017-2026. Screening.
EP day: gap up >= g% at the open (vs prior close) on volume >= vx x its 50-day average, after a 'neglected' stretch
(prior close no more than 10% above the close 60 days earlier) -- variants drop each filter. NB the volume filter uses the
whole day's volume, which a bot only knows by the close (optimistic for the day-1 entry; fine for delayed entries).
 1) Day-1 EP: buy the open, stop at the prior close (gap filled = thesis wrong), exit on the first close below EMA(10)
    after day 1, or after 40 days.
 2) Delayed reaction EP: within 20 days after an EP day, buy the first close above the EP day's high; stop below the EP
    day's low; same exit. (His intraday red-to-green trigger can't be tested on daily bars.)
 3) Short side (delayed only, as he trades it): gap down >= g% on big volume; within 20 days, short the first close
    below the gap day's low after at least one up day; stop above the highest high since the gap; exit close > EMA(10).
Costs: 0.1% round trip + long swap 8%/yr (short 2%/yr) per calendar night. Results in % per trade and in R."""
import glob, json, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone

D = sys.argv[1]
data = {}
for f in sorted(glob.glob(os.path.join(D, "*.json"))):
    s = os.path.basename(f)[:-5]
    if s != s.upper(): continue
    r = json.load(open(f))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    rows = [(datetime.fromtimestamp(t, timezone.utc).date(), o, h, l, c, v)
            for t, o, h, l, c, v in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"])
            if None not in (o, h, l, c, v) and v > 0]
    data[s] = rows


def ema(c, n):
    a = 2 / (n + 1); out = [c[0]]
    for x in c[1:]: out.append(out[-1] + a * (x - out[-1]))
    return out


def ride(rows, E, i0, side, e, stop, maxd=40):
    for k in range(i0, min(i0 + maxd, len(rows))):
        d, o, h, l, c, v = rows[k]
        if (l <= stop) if side == 1 else (h >= stop):
            x = min(o, stop) if side == 1 else max(o, stop); return k, x
        if k > i0 and (c < E[k]) if side == 1 else (k > i0 and c > E[k]): return k, c
    k = min(i0 + maxd, len(rows)) - 1; return k, rows[k][4]


def res(side, e, x, stop, n):
    pct = side * 100 * (x / e - 1) - 0.1 - (8 if side == 1 else 2) / 360 * n
    return pct, pct / (100 * abs(e - stop) / e)


def run(g, vx, neglect, mode):
    out = []
    for s, rows in data.items():
        c = [x[4] for x in rows]; E = ema(c, 10); i = 61
        while i < len(rows) - 1:
            d, o, h, l, cl, v = rows[i]; pc = c[i - 1]; av = st.mean(x[5] for x in rows[i - 50:i])
            gap = o / pc - 1; side = 1 if gap >= g else -1 if gap <= -g else 0
            if mode != "short" and side != 1 or mode == "short" and side != -1 or v < vx * av: i += 1; continue
            if neglect and side == 1 and pc > 1.10 * c[i - 60]: i += 1; continue
            if mode == "day1":
                k, x = ride(rows, E, i, 1, o, pc)
                out.append((d, s) + res(1, o, x, pc, (rows[k][0] - d).days)); i = k + 1; continue
            done = False; up = False
            for j in range(i + 1, min(i + 21, len(rows) - 1)):
                if mode == "delayed" and c[j] > h:
                    e, stop = c[j], l
                    k, x = ride(rows, E, j + 1, 1, e, stop)
                    out.append((rows[j][0], s) + res(1, e, x, stop, (rows[k][0] - rows[j][0]).days)); i = k; done = True; break
                if mode == "short":
                    if c[j] > c[j - 1]: up = True
                    if up and c[j] < l:
                        e = c[j]; stop = max(x[2] for x in rows[i:j + 1])
                        k, x = ride(rows, E, j + 1, -1, e, stop)
                        out.append((rows[j][0], s) + res(-1, e, x, stop, (rows[k][0] - rows[j][0]).days)); i = k; done = True; break
            i += 1
    return sorted(out)


def rep(name, t):
    if not t: print(f"{name:44s} none"); return
    p = [x[2] for x in t]; r = [x[3] for x in t]; yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[3]
    print(f"{name:44s} n={len(t):4d} win={sum(x > 0 for x in p)/len(p):4.0%} avg={st.mean(p):+6.2f}% med={st.median(p):+5.2f}% "
          f"avgR={st.mean(r):+.2f} | " + " ".join(f"{y % 100}:{v:+.0f}" for y, v in sorted(yr.items())))


for mode in ("day1", "delayed", "short"):
    for g, vx, ng in ((0.08, 3, True), (0.08, 3, False), (0.05, 2, True), (0.05, 2, False), (0.10, 3, False), (0.08, 0, False)):
        rep(f"{mode} gap>={g:.0%} vol>={vx}x neglect={int(ng)}", run(g, vx, ng, mode))
