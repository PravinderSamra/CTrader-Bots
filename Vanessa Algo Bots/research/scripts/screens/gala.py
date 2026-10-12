"""Gala Trades (Chart Fanatics) price action, coded as mechanically as possible, on NAS100 m5 (proxy for QQQ).
Hourly RTH candles (9:30-start) built from m5.
 Levels: open of an hourly candle whose colour differs from the previous one (pivot), last 10 days of RTH;
         a level dies when a later hourly body crosses it (open and close on opposite sides).
 Trend : hourly swing points (2 bars each side) up to yesterday's close: higher high + higher low = up (calls only),
         lower high + lower low = down (puts only), otherwise skip the day.
 Entry : 9:35-10:30 NY (skip the first 5-min candle; he trades about one hour). Long: a 5-min candle with low below
         the level (by at least `dip`) and both open and close above it (wick below, body above); enter at its close.
         Short mirror. Stop = wick extreme -/+ 1 pt. Skip if stop distance > cap.
 Exit  : mode "2R" = all at 2R; mode "trim" = half at 2R, stop to entry, rest at 4R or close of the hour.
         Time stop 11:30 NY.
 Limits: max 2 attempts per level per day, max 3 trades per day. Cost: spread per trade."""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
days = defaultdict(list)
for r in csv.DictReader(open(sys.argv[1])):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
    m = t.hour * 60 + t.minute
    if 570 <= m < 960:
        days[t.date()].append((m, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
dl = [d for d in sorted(days) if len(days[d]) >= 75 and days[d][0][0] == 570]

hourly = {}
for d in dl:
    hs = []
    for k in range(7):
        b = [x for x in days[d] if 570 + 60 * k <= x[0] < 630 + 60 * k]
        if b:
            hs.append((b[0][1], max(x[2] for x in b), min(x[3] for x in b), b[-1][4]))
    hourly[d] = hs


def setup(i):
    """levels and trend known before day dl[i] opens"""
    hist = [h for d in dl[max(0, i - 10):i] for h in hourly[d]]
    if len(hist) < 20:
        return [], 0
    levels = []
    for j in range(1, len(hist)):
        po, pc = hist[j - 1][0], hist[j - 1][3]
        o, c = hist[j][0], hist[j][3]
        if (pc > po) != (c > o):
            lv = o
            dead = any(min(x[0], x[3]) < lv < max(x[0], x[3]) for x in hist[j + 1:])
            if not dead:
                levels.append(lv)
    hi = [j for j in range(2, len(hist) - 2) if hist[j][1] == max(x[1] for x in hist[j - 2:j + 3])]
    lo = [j for j in range(2, len(hist) - 2) if hist[j][2] == min(x[2] for x in hist[j - 2:j + 3])]
    trend = 0
    if len(hi) >= 2 and len(lo) >= 2:
        hh = hist[hi[-1]][1] > hist[hi[-2]][1]
        hl = hist[lo[-1]][2] > hist[lo[-2]][2]
        if hh and hl:
            trend = 1
        elif not hh and not hl:
            trend = -1
    return levels, trend


SETUPS = [setup(i) for i in range(len(dl))]


def run(spread, mode="2R", cap=30.0, dip=0.0, end=630, trend_on=True):
    trades = []
    for i, d in enumerate(dl):
        levels, trend = SETUPS[i]
        if not levels or (trend_on and trend == 0):
            continue
        sides = [trend] if trend_on else [1, -1]
        b = days[d]
        n, tries, pos = 0, defaultdict(int), None
        for (m, o, h, l, c) in b:
            if pos:
                side, e, stop, risk, half, lv = pos
                fav = h if side == 1 else l
                adv = l if side == 1 else h
                ex = None
                if (adv <= stop) if side == 1 else (adv >= stop):
                    ex = stop
                elif mode == "2R" and side * (fav - e) >= 2 * risk:
                    ex = e + side * 2 * risk
                elif mode == "trim":
                    if not half and side * (fav - e) >= 2 * risk:
                        half, stop = True, e
                        pos = (side, e, stop, risk, half, lv)
                    if half and side * (fav - e) >= 4 * risk:
                        ex = e + side * 4 * risk
                if ex is None and m >= 690:
                    ex = c
                if ex is not None:
                    if mode == "trim" and half:
                        r_ = (2 * risk + side * (ex - e)) / 2
                    else:
                        r_ = side * (ex - e)
                    trades.append((d, side, (r_ - spread) / risk, r_ - spread))
                    n += 1
                    pos = None
                continue
            if m < 575 or m >= end or n >= 3:
                continue
            for side in sides:
                for lv in levels:
                    if tries[lv] >= 2:
                        continue
                    if side == 1 and l < lv - dip and min(o, c) > lv:
                        e, stop = c, l - 1
                    elif side == -1 and h > lv + dip and max(o, c) < lv:
                        e, stop = c, h + 1
                    else:
                        continue
                    risk = abs(e - stop)
                    if risk > cap or risk < 3:
                        continue
                    tries[lv] += 1
                    pos = (side, e, stop, risk, False, lv)
                    break
                if pos:
                    break
        if pos:
            side, e, stop, risk, half, lv = pos
            c = b[-1][4]
            r_ = side * (c - e)
            trades.append((d, side, (r_ - spread) / risk, r_ - spread))
    return trades


bot = dict(zip(*json.load(open(sys.argv[2])).values()))


def report(name, t):
    if not t:
        print(name, "no trades"); return
    rs = [x[2] for x in t]
    w = sum(r > 0 for r in rs) / len(rs)
    yr = defaultdict(float)
    for x in t:
        yr[x[0].year] += x[2]
    eq = pk = dd = 0.0
    for r in rs:
        eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    dv = defaultdict(float)
    for x in t:
        dv[x[0].strftime("%Y%m%d")] += x[2]
    com = [k for k in dv if k in bot]
    corr = st.correlation([bot[k] for k in com], [dv[k] for k in com]) if len(com) > 5 else float("nan")
    print(f"{name:34s} n={len(rs):4d} win={w:4.0%} avg={st.mean(rs):+.3f}R tot={sum(rs):+6.1f}R dd={dd:5.1f}R "
          f"corr={corr:+.2f} ({len(com)}d) | " + " ".join(f"{y}:{v:+.1f}" for y, v in sorted(yr.items())))


for sp in (0.0, 1.2, 2.0):
    report(f"2R  spread {sp}", run(sp))
for sp in (0.0, 1.2):
    report(f"trim spread {sp}", run(sp, "trim"))
report("2R 1.2 cap 20", run(1.2, cap=20))
report("2R 1.2 cap 50", run(1.2, cap=50))
report("2R 1.2 dip 3", run(1.2, dip=3))
report("2R 1.2 window to 11:30", run(1.2, end=690))
report("2R 1.2 no trend filter", run(1.2, trend_on=False))
