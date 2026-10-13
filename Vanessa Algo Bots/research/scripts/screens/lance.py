"""Lance Breitstein 'right side of the V' capitulation reversal, coded mechanically. Screening only.
Long (short = mirror on inverted prices; tested both ways, also long-only): at bar i the move is a capitulation if
  - at least `nd` consecutive lower highs (holding prior-bar highs),
  - close below the lower Bollinger band (20, 2) and at least `dist` x ATR(14) below the 20-SMA,
  - bar range >= `rx` x ATR(14) (acceleration) and volume >= `vx` x 20-bar average (where volume exists).
Entry: first later bar that trades above the prior bar's high (buy stop), within 3 bars. Stop: lowest low of the move.
Exit: trail prior-bar lows; or target the 20-SMA (whichever first). Daily: swap; m5: NY 9:45-15:30 entries, flat 15:55."""
import statistics as st, sys, json
from collections import defaultdict
from vlib import nas_m5, nas_daily, gold_daily, report

def run(bars, side, nd, dist, rx, vx, cost, intraday, swap_per_bar=0.0, vols=None):
    if side == -1: bars = [(t, -o, -l, -h, -c) for t, o, h, l, c in bars]
    n = len(bars); out = []; i = 21
    tr = [0.0] + [max(bars[k][2], bars[k-1][4]) - min(bars[k][3], bars[k-1][4]) for k in range(1, n)]
    while i < n - 1:
        t, o, h, l, c = bars[i]
        if intraday:
            m = t.hour*60+t.minute
            if not (585 <= m < 930) or bars[i-20][0].date() != t.date(): i += 1; continue
        cl = [b[4] for b in bars[i-19:i+1]]; ma = st.mean(cl); sd = st.pstdev(cl); atr = st.mean(tr[i-13:i+1])
        ok = c < ma - 2*sd and ma - c >= dist*atr and (h - l) >= rx*atr
        ok = ok and all(bars[k][2] < bars[k-1][2] for k in range(i-nd+1, i+1))
        if ok and vols and vx > 0:
            ok = vols[i] >= vx * st.mean(vols[i-20:i])
        if not ok: i += 1; continue
        low = min(b[3] for b in bars[i-nd:i+1]); filled = None
        for j in range(i+1, min(n, i+4)):
            if bars[j][2] > bars[j-1][2] and (not intraday or bars[j][0].date() == t.date()):
                filled = j; break
            low = min(low, bars[j][3])
        if filled is None: i += 1; continue
        e = max(bars[filled][1], bars[filled-1][2]); stop = low; risk = e - stop
        if risk <= 0: i = filled + 1; continue
        ex = None; k = filled
        while k < n:
            tk, ok_, hk, lk, ck = bars[k]
            cl = [b[4] for b in bars[k-19:k+1]]; ma = st.mean(cl)
            trail = stop if k == filled else max(stop, bars[k-1][3])
            if lk <= trail: ex = min(trail, ok_) if k > filled else trail; break
            if hk >= ma: ex = max(ma, ok_); break
            if intraday and (tk.hour*60+tk.minute >= 955 or (k+1 < n and bars[k+1][0].date() != tk.date())): ex = ck; break
            if not intraday and k - filled >= 20: ex = ck; break
            k += 1
        if ex is None: break
        held = k - filled
        pnl = ex - e - cost - (abs(e)*swap_per_bar*held if not intraday else 0)
        out.append((bars[filled][0].date(), pnl/risk)); i = k + 1
    return out

bot = dict(zip(*json.load(open(sys.argv[1])).values()))
import csv
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
m5 = nas_m5(); vols = []
for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")): vols.append(float(r["volume"]))
for nd, dist, rx, vx in ((4, 2.5, 1.5, 2.0), (5, 3.0, 2.0, 2.0), (3, 2.0, 1.2, 0)):
    for cost in (0.0, 1.2):
        L = run(m5, 1, nd, dist, rx, vx, cost, True, vols=vols); S = run(m5, -1, nd, dist, rx, vx, cost, True, vols=vols)
        report(f"NAS m5 nd{nd} d{dist} rx{rx} v{vx} c{cost} long", L, bot); report(f"   same short", S, bot)
for name, d, cost, sw in (("NAS daily", nas_daily(), 1.2, 0.082/252), ("Gold daily", gold_daily(), 0.3, 0.06/252)):
    for nd, dist, rx in ((3, 2.0, 1.2), (3, 2.5, 1.5), (2, 2.0, 1.0)):
        report(f"{name} nd{nd} d{dist} rx{rx} long", run(d, 1, nd, dist, rx, 0, cost, False, sw))
        report(f"{name} nd{nd} d{dist} rx{rx} short", run(d, -1, nd, dist, rx, 0, cost, False, 0.0))
