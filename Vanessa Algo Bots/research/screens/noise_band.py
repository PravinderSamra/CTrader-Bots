"""Noise Area intraday momentum (Zarattini, Aziz & Barbon 2024, "Beat the Market", SPY 2007-Feb 2024).
Rules as published: sigma(t) = 14-day average of |price at time-of-day t / today's 9:30 open - 1|.
Upper = max(open, prev close) * (1 + sigma), Lower = min(open, prev close) * (1 - sigma).
Check every 30 minutes 10:00..15:30 New York: long above Upper, short below Lower. Trailing stop at the checks:
long exits below max(Upper, VWAP), short above min(Lower, VWAP). Flat at 16:00. One-unit (1x notional) positions.
Honest fill: next 5-minute bar's open. Cost per round trip given on the command line (FTMO spread ~0.01%).
Pre-registered 27 Oct 2026: pass if net > 0 in every year AND in the post-paper period (Mar 2024 on), Sharpe >= 0.8.
Usage: noise_band.py file.csv [file2.csv ...] cost"""
import csv, sys, math, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
import os
files, COST = sys.argv[1:-1], float(sys.argv[-1])
LB = int(os.environ.get("NB_LB", 14)); STEP = int(os.environ.get("NB_STEP", 30)); OUT = os.environ.get("NB_OUT")

def nyoff(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7)
    return 4 if s <= d < e else 5

bars = {}
for f in files:
    for r in csv.reader(open(f)):
        if not r or not r[0].isdigit(): continue
        t = datetime.fromtimestamp(int(r[0]) / 1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=nyoff(t.date()))
        v = float(r[6]) if len(r) > 6 and r[6] else 1.0
        bars[ny] = (float(r[2]), float(r[3]), float(r[4]), float(r[5]), v)
days = defaultdict(list)
for k in sorted(bars):
    m = k.hour * 60 + k.minute
    if k.weekday() < 5 and 570 <= m < 960: days[k.date()].append((m, *bars[k]))
D = sorted(d for d in days if len(days[d]) >= 70 and days[d][0][0] == 570)
moves = {}       # day -> {minute_end: |close/open - 1|}
for d in D:
    o = days[d][0][1]; moves[d] = {m + 5: abs(c / o - 1) for m, _, _, _, c, _ in days[d]}
checks = list(range(570 + STEP, 960, STEP))   # every STEP minutes from 10:00 (30) .. 15:30
res = []; prev_close = None
for n, d in enumerate(D):
    B = days[d]; o = B[0][1]
    if n < LB or prev_close is None: prev_close = B[-1][4]; continue
    hist = D[n-LB:n]; up0, lo0 = max(o, prev_close), min(o, prev_close)
    pos = 0; e = 0; pnl = 0.0; ntr = 0; pv = vv = 0.0; idx = {m: i for i, (m, *_) in enumerate(B)}
    for i, (m, op, hi, lo, c, v) in enumerate(B):
        tp = (hi + lo + c) / 3; pv += tp * v; vv += v
        end = m + 5
        if end not in checks or i + 1 >= len(B): continue
        sig = st.mean(moves[h].get(end, 0) for h in hist)
        U, L, vw = up0 * (1 + sig), lo0 * (1 - sig), pv / vv
        fill = B[i + 1][1]
        if pos > 0 and c < max(U, vw): pnl += (fill - e) / e - COST; pos = 0; ntr += 1
        elif pos < 0 and c > min(L, vw): pnl += (e - fill) / e - COST; pos = 0; ntr += 1
        if pos == 0:
            if c > U: pos, e = 1, fill
            elif c < L: pos, e = -1, fill
    if pos:
        x = B[-1][4]; pnl += pos * (x - e) / e - COST; ntr += 1
    res.append((d, pnl, ntr)); prev_close = B[-1][4]

if OUT:
    import json; json.dump({str(d): p for d, p, _ in res}, open(OUT, "w"))
r = [p for _, p, _ in res]; eq = pk = dd = 0
for p in r: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
sh = st.mean(r) / st.pstdev(r) * math.sqrt(252)
print(f"days {len(res)} ({res[0][0]}..{res[-1][0]})  trades {sum(t for *_, t in res)}  "
      f"net {sum(r)*100:+.1f}% at 1x  Sharpe {sh:.2f}  maxDD {dd*100:.1f}%  traded days {sum(t>0 for *_,t in res)}")
yr = defaultdict(float)
for d, p, _ in res: yr[d.year] += p
print("  by year: " + "  ".join(f"{y} {v*100:+.1f}%" for y, v in sorted(yr.items())))
post = [p for d, p, _ in res if d >= date(2024, 3, 1)]
if post: print(f"  after the paper (Mar 2024 on): {sum(post)*100:+.1f}% over {len(post)} days, Sharpe {st.mean(post)/st.pstdev(post)*math.sqrt(252):.2f}")
