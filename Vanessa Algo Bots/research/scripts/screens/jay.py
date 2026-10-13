"""Jay Ortani (Chart Fanatics) - the mechanical parts of his 'market DNA' trading. Screening only.
 1) Continuation day: day t is a big bar (range >= 1.5 x ATR14) closing in its bottom (top) 15% on above-average
    volume -> next day short (long) from the open to the close. FTMO's 45 US stocks (Yahoo daily 2017-26) and NAS100.
    Cost 0.1% per trade (stocks), 1.2 pts (NAS).
 2) Camarilla breakout on NAS100 m5 2023-26: levels from the prior RTH day (H, L, C, R = H - L):
    R3 = C + 1.1R/4, R4 = C + 1.1R/2, R6 = C x H / L (and mirrors S3, S4, S6). First 5-min close above R4 (below S4)
    between 9:35 and 11:30 NY -> enter at that close, stop R3 (S3), target R6 (S6), else flat 15:55.
    Same-bar stop and target counted as a loss. Cost 1.2 pts."""
import csv, glob, json, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
NY = ZoneInfo("America/New_York")

def rep(name, r, unit):
    if not r: print(name, "none"); return
    yr = defaultdict(float)
    for d, x in r: yr[d.year] += x
    v = [x for _, x in r]
    print(f"{name:46s} n={len(v):4d} win={sum(x > 0 for x in v)/len(v):4.0%} avg={st.mean(v):+.3f}{unit} | "
          + " ".join(f"{y % 100}:{s:+.0f}" for y, s in sorted(yr.items())))

# 1) continuation on stocks
out = {1: [], -1: []}
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.json"))):
    s = os.path.basename(f)[:-5]
    if s != s.upper(): continue
    r = json.load(open(f))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    rows = [(datetime.fromtimestamp(t, timezone.utc).date(), o, h, l, c, v) for t, o, h, l, c, v in
            zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"], q["volume"]) if None not in (o, h, l, c, v) and v > 0]
    for i in range(51, len(rows) - 1):
        d, o, h, l, c, v = rows[i]
        atr = st.mean(max(rows[k][2], rows[k-1][4]) - min(rows[k][3], rows[k-1][4]) for k in range(i - 13, i + 1))
        if h - l < 1.5 * atr or v < st.mean(x[5] for x in rows[i - 50:i]): continue
        pos = (c - l) / (h - l)
        side = -1 if pos <= 0.15 else 1 if pos >= 0.85 else 0
        if not side: continue
        n = rows[i + 1]
        out[side].append((n[0], side * 100 * (n[4] / n[1] - 1) - 0.1))
rep("stocks: short day after a big bar closing at its low", sorted(out[-1]), "%")
rep("stocks: long day after a big bar closing at its high", sorted(out[1]), "%")

# NAS m5 RTH days
days = defaultdict(list)
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
    m = t.hour * 60 + t.minute
    if 570 <= m < 960: days[t.date()].append((m, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
D = [d for d in sorted(days) if len(days[d]) >= 70]
dv = [(d, days[d][0][1], max(x[2] for x in days[d]), min(x[3] for x in days[d]), days[d][-1][4]) for d in D]
cont = {1: [], -1: []}
for i in range(15, len(dv) - 1):
    d, o, h, l, c = dv[i]
    atr = st.mean(dv[k][2] - dv[k][3] for k in range(i - 14, i))
    if h - l < 1.5 * atr: continue
    pos = (c - l) / (h - l); side = -1 if pos <= 0.15 else 1 if pos >= 0.85 else 0
    if side: n = dv[i + 1]; cont[side].append((n[0], (side * (n[4] - n[1]) - 1.2) / atr))
rep("NAS: short day after a big bar closing at its low", cont[-1], " ATR")
rep("NAS: long day after a big bar closing at its high", cont[1], " ATR")

# 2) Camarilla
cam = []
for i in range(1, len(D)):
    _, _, H, L, C = dv[i - 1]; R = H - L; b = days[D[i]]
    lv = {1: (C + 1.1 * R / 2, C + 1.1 * R / 4, C * H / L), -1: (C - 1.1 * R / 2, C - 1.1 * R / 4, C - (C * H / L - C))}
    for j, (m, o, h, l, c) in enumerate(b):
        if not (575 <= m <= 690): continue
        side = 1 if c > lv[1][0] else -1 if c < lv[-1][0] else 0
        if not side: continue
        r4, stop, tgt = lv[side]; e = c; risk = side * (e - stop)
        if risk <= 2 or side * (tgt - e) <= 0: break
        res = None
        for m2, o2, h2, l2, c2 in b[j + 1:]:
            if (l2 <= stop) if side == 1 else (h2 >= stop): res = stop; break
            if (h2 >= tgt) if side == 1 else (l2 <= tgt): res = tgt; break
            if m2 >= 955: res = c2; break
        if res is None: res = b[-1][4]
        cam.append((D[i], (side * (res - e) - 1.2) / risk)); break
rep("NAS Camarilla R4/S4 breakout, stop R3/S3, target R6/S6", cam, "R")
