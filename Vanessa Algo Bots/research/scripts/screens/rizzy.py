"""Marcy Silver 'little Rizzy' measured move, coded mechanically. Screening only.
Down version (up = mirror on inverted prices): swing high H1, swing low L1, then a lower swing high H2 (< H1).
Trend line through H1 and H2; D = line value at L1's bar minus L1. Projection = L1 - D.
Entry: short at the bar that confirms H2 (k bars after it), at that bar's close. Stop: H2 + buffer.
Target: projection. Only if reward/risk >= minrr. Optional filter: H1 at or above the 20-bar Bollinger middle line
(she prefers patterns that start near the top of the bands). Exit: target, stop, or time limit.
Intraday NAS100 m5: 03:00-15:55 NY, skip 9:30-9:45, flat 15:55. Daily: NAS100 and gold, max hold 20 days, swap."""
import csv
import glob
import json
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")


def nas_m5():
    out = []
    for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
        out.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return out


def daily(rows):
    d = {}
    for t, o, h, l, c in rows:
        k = t.date()
        if k in d:
            x = d[k]; x[2] = max(x[2], h); x[3] = min(x[3], l); x[4] = c
        else:
            d[k] = [t, o, h, l, c]
    return [tuple(d[k]) for k in sorted(d)]


def nas_daily():
    rows = []
    for r in csv.DictReader(open("/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv")):
        rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY),
                     float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    last = rows[-1][0]
    rows += [x for x in nas_m5() if x[0] > last]
    return daily([x for x in rows if (x[0].hour, x[0].minute) >= (9, 30) and x[0].hour < 16])


def gold_daily():
    rows = []
    for f in sorted(glob.glob("/home/user/CTrader-Bots/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
        for line in open(f):
            if line[0] != "2": continue
            p = line.split(",")
            if p[0][15] not in "05": continue
            t = datetime.strptime(p[0][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc).astimezone(NY)
            rows.append((t, float(p[1]), float(p[2]), float(p[3]), float(p[4])))
    return daily(rows)


def run(bars, side, k, buf, minrr, bb, cost, intraday, maxhold, swap_per_bar, maxseq=99):
    if side == -1:
        bars = [(t, -o, -l, -h, -c) for t, o, h, l, c in bars]  # inverted: 'down' logic finds up patterns
    n = len(bars); closes = [b[4] for b in bars]
    sh, sl = [], []
    trades = []; pos = None
    for i in range(n):
        t, o, h, l, c = bars[i]
        if pos:
            e, stop, tgt, risk, i0 = pos
            ex = None
            if h >= stop: ex = stop
            elif l <= tgt: ex = tgt
            elif intraday and (t.hour * 60 + t.minute >= 955 or (i + 1 < n and bars[i + 1][0].date() != t.date())): ex = c
            elif not intraday and i - i0 >= maxhold: ex = c
            if ex is not None:
                held = i - i0
                pnl = (e - ex) - cost - (abs(e) * swap_per_bar * held if not intraday else 0)
                trades.append((t.date(), pnl / risk)); pos = None
            continue
        j = i - k
        if j < k: continue
        if bars[j][2] == max(x[2] for x in bars[j - k:j + k + 1]): sh.append(j)
        if bars[j][3] == min(x[3] for x in bars[j - k:j + k + 1]): sl.append(j)
        if not sh or sh[-1] != j or len(sh) < 2: continue
        h2, h1 = sh[-1], sh[-2]
        lows = [x for x in sl if h1 < x < h2]
        if not lows: continue
        l1 = min(lows, key=lambda x: bars[x][3])
        H1, H2, L1 = bars[h1][2], bars[h2][2], bars[l1][3]
        if not H2 < H1: continue
        # TradeZella playbook: only the 1st/2nd structure of a fresh trend (count of consecutive lower highs ending at H2)
        seq = 1
        while len(sh) > seq + 1 and bars[sh[-seq - 1]][2] < bars[sh[-seq - 2]][2]: seq += 1
        if seq > maxseq: continue
        if intraday:
            m = t.hour * 60 + t.minute
            if not (180 <= m < 900) or 570 <= m < 585: continue
            if bars[h1][0].date() != t.date(): continue
        if bb:
            w = closes[max(0, h1 - 19):h1 + 1]
            if len(w) < 20 or H1 < st.mean(w): continue
        line_at_l1 = H1 + (H2 - H1) * (l1 - h1) / (h2 - h1)
        D = line_at_l1 - L1
        if D <= 0: continue
        tgt = L1 - D; e = c; stop = H2 + buf; risk = stop - e
        if risk <= 0 or e - tgt < minrr * risk: continue
        pos = (e, stop, tgt, risk, i)
    return trades


def report(name, t, bot=None):
    if not t: print(name, "none"); return
    rs = [x[1] for x in t]
    yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[1]
    eq = pk = dd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    corr = ""
    if bot:
        dv = defaultdict(float)
        for x in t: dv[x[0].strftime("%Y%m%d")] += x[1]
        com = [k for k in dv if k in bot]
        if len(com) > 5: corr = f"corr={st.correlation([bot[k] for k in com], [dv[k] for k in com]):+.2f}"
    print(f"{name:36s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.3f}R "
          f"tot={sum(rs):+6.1f}R dd={dd:5.1f}R {corr} | " + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ != "__main__": raise SystemExit
bot = dict(zip(*json.load(open(sys.argv[1])).values()))
m5 = nas_m5()
for bb in (False, True):
    for minrr in (1.0, 2.0):
        for cost in (0.0, 1.2):
            t = sorted(run(m5, 1, 3, 2.0, minrr, bb, cost, True, 0, 0) + run(m5, -1, 3, 2.0, minrr, bb, cost, True, 0, 0))
            report(f"NAS m5 bb={bb} rr>={minrr} cost {cost}", t, bot)
for name, d, cost, sw in (("NAS daily", nas_daily(), 1.2, 0.082 / 252), ("Gold daily", gold_daily(), 0.3, 0.06 / 252)):
    for bb in (False, True):
        for minrr in (1.0, 2.0):
            t = sorted(run(d, 1, 2, 0.0, minrr, bb, cost, False, 20, sw) + run(d, -1, 2, 0.0, minrr, bb, cost, False, 20, sw))
            report(f"{name} bb={bb} rr>={minrr}", t)
