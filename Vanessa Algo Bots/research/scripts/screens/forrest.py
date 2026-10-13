"""Forrest Knight (Chart Fanatics) volume-profile edges, coded on NAS100 m5 2023-26 with FTMO tick volume. Screening only.
Session = 18:00-17:00 NY (futures day). Profile per session: tick volume spread over each bar's range, 5-pt bins; POC,
70% value area (VAL/VAH). Key levels: prior-session high/low (PDH/PDL) and overnight high/low (18:00-9:30, ONH/ONL).
 A) Signal candle at an edge: 1-hour bar (on the hour, closes 10:00-16:00) that trades through PDH or ONH and closes back
    below it, with an upper wick >= its body and >= 40% of the range (doji / shooting star) and more volume than the
    previous hour -> short at the close, stop bar high + 2, target the next level down (ONL/PDL/prior POC; nearest that is
    at least 1R away, else the farthest). Mirror long at PDL/ONL. Flat 16:55.
 B) Prior VAL retest in an uptrend (prior session closed above its VAH = accepted higher): buy limit at the prior VAL from
    18:00, stop 0.5 x value-area width below, target the prior session high, flat at 16:55. Variant: prior POC.
Costs: 1.2 pts (NY hours) / 1.8 pts (otherwise)."""
import csv, json, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta
from vlib import NY, report

ses = defaultdict(list)
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).astimezone(NY)
    if t.hour == 17: continue
    k = (t + timedelta(hours=6)).date()          # 18:00 starts the next session
    ses[k].append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"]), max(float(r["volume"]), 1)))
S = [k for k in sorted(ses) if len(ses[k]) > 200]


def profile(bars, step=5.0):
    vol = defaultdict(float)
    for _, o, h, l, c, v in bars:
        lo, hi = int(l // step), int(h // step)
        for b in range(lo, hi + 1): vol[b] += v / (hi - lo + 1)
    poc = max(vol, key=vol.get); tot, inc, lo, hi = sum(vol.values()), vol[poc], poc, poc
    while inc < 0.7 * tot:
        up, dn = vol.get(hi + 1, 0), vol.get(lo - 1, 0)
        if up >= dn: hi += 1; inc += up
        else: lo -= 1; inc += dn
    return (poc + 0.5) * step, lo * step, (hi + 1) * step


def mins(t): return t.hour * 60 + t.minute
def cost(t): return 1.2 if 570 <= mins(t) < 960 else 1.8


def walk(bars, side, e, stop, tgt, i0):
    for t, o, h, l, c, v in bars[i0:]:
        if (l <= stop) if side == 1 else (h >= stop): return side * (stop - e)
        if (h >= tgt) if side == 1 else (l <= tgt): return side * (tgt - e)
        if mins(t) >= 1015: return side * (c - e)
    return side * (bars[-1][4] - e)


A, B, Bp = [], [], []
for n in range(1, len(S)):
    prev, cur = ses[S[n - 1]], ses[S[n]]
    poc, val, vah = profile(prev)
    pdh, pdl, pclose = max(x[2] for x in prev), min(x[3] for x in prev), prev[-1][4]
    on = [x for x in cur if not (570 <= mins(x[0]) < 1440 and x[0].hour >= 9 and mins(x[0]) >= 570)]
    on = [x for x in cur if x[0].hour >= 18 or mins(x[0]) < 570]
    if not on: continue
    onh, onl = max(x[2] for x in on), min(x[3] for x in on)
    # A) hourly signal candles in RTH
    hrs = defaultdict(list); idx = {}
    for i, x in enumerate(cur):
        if 540 <= mins(x[0]) < 960: hrs[x[0].hour].append(x); idx[x[0].hour] = i
    used = set(); ph = None
    for hr in sorted(hrs):
        bs = hrs[hr]
        if len(bs) < 12: ph = bs; continue
        o, h, l, c, v = bs[0][1], max(x[2] for x in bs), min(x[3] for x in bs), bs[-1][4], sum(x[5] for x in bs)
        pv = sum(x[5] for x in ph) if ph else 1e18; ph = bs
        rng = h - l
        if hr < 10 or rng <= 0: continue
        for side, lv in ((-1, pdh), (-1, onh), (1, pdl), (1, onl)):
            if side in used: continue
            wick = (h - max(o, c)) if side == -1 else (min(o, c) - l)
            through = (h > lv and c < lv) if side == -1 else (l < lv and c > lv)
            if through and wick >= abs(c - o) and wick >= 0.4 * rng and v > pv:
                stop = h + 2 if side == -1 else l - 2; risk = abs(c - stop)
                tg = [x for x in ((onl, pdl, poc) if side == -1 else (onh, pdh, poc)) if (x - c) * side > 0]
                if not tg or risk < 5: continue
                far = [x for x in tg if abs(x - c) >= risk]
                tgt = min(far, key=lambda x: abs(x - c)) if far else max(tg, key=lambda x: abs(x - c))
                pts = walk(cur, side, c, stop, tgt, idx[hr] + 1)
                A.append((S[n], (pts - 1.2) / risk)); used.add(side)
    # B) prior VAL / POC retest after the prior session closed above its VAH
    if pclose > vah:
        for lvl, out in ((val, B), (poc, Bp)):
            w = vah - val; stop = lvl - 0.5 * w; risk = lvl - stop
            if pdh - lvl < risk or risk < 5: continue
            for i, x in enumerate(cur):
                if mins(x[0]) >= 900 and x[0].hour < 18: break
                if x[3] <= lvl:
                    if x[3] <= stop: out.append((S[n], (stop - lvl - cost(x[0])) / risk)); break
                    pts = walk(cur, 1, lvl, stop, pdh, i + 1)
                    out.append((S[n], (pts - cost(x[0])) / risk)); break

bot = dict(zip(*json.load(open(sys.argv[1])).values()))
report("A signal candle at PDH/ONH/PDL/ONL", sorted(A), bot)
report("B prior VAL retest (uptrend)", sorted(B), bot)
report("B prior POC retest (uptrend)", sorted(Bp), bot)
