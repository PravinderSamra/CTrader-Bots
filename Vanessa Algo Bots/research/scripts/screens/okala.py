"""Okala (Chart Fanatics) '80/20' NAS100 levels: reversion off prices ending in 20 and 80 (each 100 pts), 10-pt stop,
half off at +15, stop to entry, rest at +30 (or 30 min). NY 9:30-12:00 only, m5 bars (his charts are 200s/10min).
 touch : limit fade at the level the first time price reaches it from the other side within the session window
         (approaching from below -> short at level, from above -> long).
 reject: m5 bar trades through the level but closes back on the approach side -> enter at that close, stop 10 pts
         beyond the level, same targets measured from entry.
Same-bar stop and target on m5: 'cons' counts the stop first, 'opt' the target first (truth is in between).
Control: identical rules on levels ending in 00/50 and on 40/60 to see if 20/80 are special."""
import csv
import json
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
days = defaultdict(list)
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
    m = t.hour * 60 + t.minute
    if 570 <= m < 960:
        days[t.date()].append((m, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
dl = [d for d in sorted(days) if len(days[d]) >= 75 and days[d][0][0] == 570]


def levels_between(lo, hi, ends):
    out = []
    for base in range(int(lo // 100) * 100 - 100, int(hi // 100) * 100 + 200, 100):
        for e in ends:
            if lo <= base + e <= hi: out.append(base + e)
    return out


def manage(b, i0, side, e, stop, first_bar_partial, opt, cost):
    risk = abs(e - stop); half = False; t1, t2 = e + side * 15, e + side * 30
    start_m = b[i0][0] if i0 < len(b) else 960
    for j in range(i0, len(b)):
        m, o, h, l, c = b[j]
        hit_s = (l <= stop) if side == 1 else (h >= stop)
        hit_1 = (h >= t1) if side == 1 else (l <= t1)
        hit_2 = (h >= t2) if side == 1 else (l <= t2)
        if not half:
            if hit_s and (not hit_1 or not opt):
                return (side * (stop - e) - cost) / 10
            if hit_1:
                half, stop = True, e
                if hit_2: return (15 + 30) / 2 / 10 - cost / 10
                continue
        else:
            if hit_2 and (not hit_s or opt): return (15 + 30) / 2 / 10 - cost / 10
            if hit_s: return 15 / 2 / 10 - cost / 10
        if m - start_m >= 30 or m >= 955:
            r = side * (c - e)
            return ((15 + r) / 2 if half else r) / 10 - cost / 10
    return 0.0


def run(ends, mode, opt, cost):
    out = []
    for d in dl:
        b = days[d]
        used = set(); n = 0
        for i, (m, o, h, l, c) in enumerate(b):
            if not (575 <= m < 720) or n >= 4: continue
            prev_c = b[i - 1][4]
            for lv in levels_between(l - 1, h + 1, ends):
                if lv in used: continue
                side = -1 if prev_c < lv else 1          # approaching from below -> short
                if mode == "touch":
                    if (side == -1 and h >= lv) or (side == 1 and l <= lv):
                        used.add(lv); n += 1
                        stop = lv - side * 10
                        # limit fill at lv inside bar i; if stop also inside bar i -> count stop (cons) unless opt
                        if ((side == -1 and h >= stop) or (side == 1 and l <= stop)) and not opt:
                            out.append((d, (-10 - cost) / 10)); break
                        out.append((d, manage(b, i + 1, side, lv, stop, True, opt, cost))); break
                else:
                    through = (h > lv and c < lv) if side == -1 else (l < lv and c > lv)
                    if through:
                        used.add(lv); n += 1
                        stop = lv - side * 10
                        if abs(c - stop) < 3: break
                        e = c
                        out.append((d, manage(b, i + 1, side, e, stop, False, opt, cost) * 10 / abs(e - stop))); break
    return out


bot = dict(zip(*json.load(open(sys.argv[1])).values()))


def report(name, t):
    if not t: print(name, "none"); return
    rs = [x[1] for x in t]
    yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[1]
    dv = defaultdict(float)
    for x in t: dv[x[0].strftime("%Y%m%d")] += x[1]
    com = [k for k in dv if k in bot]
    corr = st.correlation([bot[k] for k in com], [dv[k] for k in com]) if len(com) > 5 else float("nan")
    print(f"{name:34s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.3f}R "
          f"tot={sum(rs):+6.1f}R corr={corr:+.2f} | " + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))


for mode in ("touch", "reject"):
    for ends, nm in (((20, 80), "20/80"), ((0, 50), "00/50"), ((40, 60), "40/60")):
        for opt in (False, True):
            report(f"{mode} {nm} {'opt' if opt else 'cons'} 1.2", run(ends, mode, opt, 1.2))
