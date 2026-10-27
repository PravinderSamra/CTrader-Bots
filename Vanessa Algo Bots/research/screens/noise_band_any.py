"""Noise band, exact 5-minute version, any market/session (pre-registered 27 Oct 2026, before the data arrived).
Sessions (local): gold and silver (a) London 08:00-16:00, (b) New York COMEX 08:30-13:30; GER40 09:00-17:30 Frankfurt.
Rules as noise_band.py: 14-day sigma by time of day, bands from max/min(open, prev close), checks every 30 minutes from
open+30, trailing stop at the band or VWAP (tick volume), flat at the session close, next-bar fills.
Costs per round trip: gold 0.01%, silver 0.04% (wider spread), GER40 0.01%.
Pass: net > 0 in each calendar year 2023-2026, Sharpe >= 0.8, positive after Mar 2024; 5 trials in total.
Usage: noise_band_any.py file.csv tz(ny|ldn|cet) HH:MM HH:MM cost"""
import csv, sys, math, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
f, tz, a, b, COST = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4], float(sys.argv[5])
def us_dst(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7); return s <= d < e
def eu_dst(d):
    m = date(d.year, 3, 31); s = m - timedelta(days=(m.weekday() + 1) % 7)
    o = date(d.year, 10, 31); e = o - timedelta(days=(o.weekday() + 1) % 7); return s <= d < e
OFF = {"ny": lambda d: -4 if us_dst(d) else -5, "ldn": lambda d: 1 if eu_dst(d) else 0, "cet": lambda d: 2 if eu_dst(d) else 1}[tz]
m0 = int(a[:2]) * 60 + int(a[3:]); m1 = int(b[:2]) * 60 + int(b[3:])
days = defaultdict(list)
for r in csv.reader(open(f)):
    if not r or not r[0].isdigit(): continue
    t = datetime.fromtimestamp(int(r[0]) / 1000, timezone.utc).replace(tzinfo=None) 
    lt = t + timedelta(hours=OFF(t.date())); mm = lt.hour * 60 + lt.minute
    if lt.weekday() < 5 and m0 <= mm < m1:
        days[lt.date()].append((mm, float(r[2]), float(r[3]), float(r[4]), float(r[5]), max(float(r[6] or 0), 1.0)))
need = (m1 - m0) // 5 * 0.9
D = sorted(d for d in days if len(days[d]) >= need and days[d][0][0] == m0)
moves = {d: {mm + 5: abs(c / days[d][0][1] - 1) for mm, _, _, _, c, _ in days[d]} for d in D}
checks = set(range(m0 + 30, m1, 30)); res = []; pc = None
for n, d in enumerate(D):
    B = days[d]; o = B[0][1]
    if n < 14 or pc is None: pc = B[-1][4]; continue
    hist = D[n-14:n]; up0, lo0 = max(o, pc), min(o, pc); pos = 0; e = 0; pnl = 0; pv = vv = 0; ntr = 0
    for i, (mm, op, hi, lo, c, v) in enumerate(B):
        pv += (hi + lo + c) / 3 * v; vv += v
        if mm + 5 not in checks or i + 1 >= len(B): continue
        sig = st.mean(moves[h].get(mm + 5, 0) for h in hist); U, L, vw = up0 * (1 + sig), lo0 * (1 - sig), pv / vv
        fill = B[i + 1][1]
        if pos > 0 and c < max(U, vw): pnl += (fill - e) / e - COST; pos = 0; ntr += 1
        elif pos < 0 and c > min(L, vw): pnl += (e - fill) / e - COST; pos = 0; ntr += 1
        if pos == 0:
            if c > U: pos, e = 1, fill
            elif c < L: pos, e = -1, fill
    if pos: pnl += pos * (B[-1][4] - e) / e - COST; ntr += 1
    res.append((d, pnl, ntr)); pc = B[-1][4]
r = [p for _, p, _ in res]; sh = st.mean(r) / st.pstdev(r) * math.sqrt(252)
eq = pk = dd = 0
for p in r: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
yr = defaultdict(float)
for d, p, _ in res: yr[d.year] += p
post = [p for d, p, _ in res if d >= date(2024, 3, 1)]
ok = all(v > 0 for v in yr.values()) and sh >= 0.8 and sum(post) > 0
print(f"{f.split('/')[-1]:14s} {tz} {a}-{b}: days {len(res)} trades {sum(t for *_, t in res)} net {sum(r)*100:+.1f}% "
      f"({sum(r)*100/(len(r)/252):+.1f}%/yr) Sharpe {sh:.2f} maxDD {dd*100:.1f}% | "
      + " ".join(f"{y} {v*100:+.1f}%" for y, v in sorted(yr.items())) + f" | post-paper {sum(post)*100:+.1f}%" + ("  PASS" if ok else ""))
