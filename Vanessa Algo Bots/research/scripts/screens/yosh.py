"""Trader Yosh (Chart Fanatics) value-area models, coded without order flow (tick volume only) on NAS100 m5.
Prior RTH day's volume profile (5-pt bins, each bar's tick volume spread over its range): POC and 70% value area.
 A) 80% rule (Market Profile classic, his model 1 'look above/below and fail'): open outside yesterday's value area,
    price re-enters and two consecutive 30-min bars close inside -> trade to the far edge. Stop beyond the extreme made
    outside the value area (+2 pts). Entries until 13:00 NY.
 B) Failed-breakout fade of yesterday's VAH/VAL: price trades at least 5 pts beyond the edge, then an m5 close back
    inside -> enter, stop beyond the extreme +2, TP1 at POC (half, stop to entry), rest at the far edge.
    Entries 9:35-12:00, one per side per day.
Exit by 15:55. Cost per trade = spread."""
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
        days[t.date()].append((m, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]),
                               max(float(r["volume"]), 1)))
dl = [d for d in sorted(days) if len(days[d]) >= 75 and days[d][0][0] == 570]


def profile(bars, step=5.0):
    vol = defaultdict(float)
    for _, o, h, l, c, v in bars:
        lo, hi = int(l // step), int(h // step)
        n = hi - lo + 1
        for b in range(lo, hi + 1):
            vol[b] += v / n
    poc = max(vol, key=vol.get)
    tot, inc, lo, hi = sum(vol.values()), vol[poc], poc, poc
    while inc < 0.7 * tot:
        up, dn = vol.get(hi + 1, 0), vol.get(lo - 1, 0)
        if up >= dn: hi += 1; inc += up
        else: lo -= 1; inc += dn
    return (poc + 0.5) * step, lo * step, (hi + 1) * step


def manage(bars, i0, side, e, stop, tp1, tp2, half_on):
    risk = abs(e - stop); half = False
    for m, o, h, l, c, v in bars[i0:]:
        adv = l if side == 1 else h; fav = h if side == 1 else l
        if (adv <= stop) if side == 1 else (adv >= stop):
            r = side * (stop - e)
            return ((tp1 - e) * side + r) / 2 / risk if half else r / risk, risk
        if half_on and not half and ((fav >= tp1) if side == 1 else (fav <= tp1)):
            half, stop = True, e
        if (fav >= tp2) if side == 1 else (fav <= tp2):
            r = side * (tp2 - e)
            return (((tp1 - e) * side + r) / 2 if half else r) / risk, risk
        if m >= 955:
            r = side * (c - e)
            return (((tp1 - e) * side + r) / 2 if half else r) / risk, risk
    return 0.0, risk


def run(cost):
    A, B = [], []
    for k in range(1, len(dl)):
        d, b = dl[k], days[dl[k]]
        poc, val, vah = profile(days[dl[k - 1]])
        o0 = b[0][1]
        # A) 80% rule
        if o0 > vah or o0 < val:
            side = -1 if o0 > vah else 1
            ext = o0; inside = 0
            for i, (m, o, h, l, c, v) in enumerate(b):
                ext = max(ext, h) if side == -1 else min(ext, l)
                if m % 30 == 25:
                    inside = inside + 1 if val < c < vah else 0
                    if inside >= 2 and m < 780:
                        stop = ext + 2 if side == -1 else ext - 2
                        tgt = val if side == -1 else vah
                        if abs(c - stop) >= 3 and side * (tgt - c) > 0:
                            r, risk = manage(b, i + 1, side, c, stop, tgt, tgt, False)
                            A.append((d, r - cost / risk))
                        break
        # B) failed-breakout fade
        for side, edge in ((-1, vah), (1, val)):
            ext, armed = None, False
            for i, (m, o, h, l, c, v) in enumerate(b):
                if m >= 720: break
                if side == -1 and h >= edge + 5: armed = True; ext = h if ext is None else max(ext, h)
                if side == 1 and l <= edge - 5: armed = True; ext = l if ext is None else min(ext, l)
                if armed and m >= 575 and ((c < edge) if side == -1 else (c > edge)):
                    stop = ext + 2 if side == -1 else ext - 2
                    far = val if side == -1 else vah
                    if abs(c - stop) >= 3 and side * (poc - c) > 0:
                        r, risk = manage(b, i + 1, side, c, stop, poc, far, True)
                        B.append((d, r - cost / risk))
                    break
    return sorted(A), sorted(B)


bot = dict(zip(*json.load(open(sys.argv[1])).values()))


def report(name, t):
    if not t: print(name, "none"); return
    rs = [x[1] for x in t]
    yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[1]
    eq = pk = dd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    dv = defaultdict(float)
    for x in t: dv[x[0].strftime("%Y%m%d")] += x[1]
    com = [k for k in dv if k in bot]
    corr = st.correlation([bot[k] for k in com], [dv[k] for k in com]) if len(com) > 5 else float("nan")
    print(f"{name:28s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.3f}R "
          f"tot={sum(rs):+6.1f}R dd={dd:5.1f}R corr={corr:+.2f} | "
          + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))


for cost in (0.0, 1.2):
    A, B = run(cost)
    report(f"80% rule cost {cost}", A)
    report(f"VA fade cost {cost}", B)
