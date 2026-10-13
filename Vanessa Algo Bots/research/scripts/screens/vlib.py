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


