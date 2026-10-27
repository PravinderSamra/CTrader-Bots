"""Noise band on other markets, HOURLY version (pre-registered 27 Oct 2026, before any run).
Same rules as noise_band.py but with H1 bars: session open = open of the first session hour, checks at the end of each
hour, flat at the session close. VWAP replaced by the session's average typical price (no volume in this data).
Sessions (local time): US indices 10:00-16:00 New York (first full hour after the 9:30 open); GER40/FRA40/EU50
09:00-17:00 Central Europe; UK100 08:00-16:00 London; JP225 09:00-15:00 Tokyo; gold and silver 08:00-16:00 London;
WTI 09:00-14:00 New York. Cost 0.01% per round trip. 14-day lookback.
Pass: >= 0 in 2014-20, 2021-23 and 2024-26, Sharpe >= 0.8 overall, positive after Mar 2024. US100 is the calibration."""
import csv, math, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
def us_dst(d):
    mar = date(d.year, 3, 1); s = mar + timedelta(days=(6 - mar.weekday()) % 7 + 7)
    nov = date(d.year, 11, 1); e = nov + timedelta(days=(6 - nov.weekday()) % 7); return s <= d < e
def eu_dst(d):
    m = date(d.year, 3, 31); s = m - timedelta(days=(m.weekday() + 1) % 7)
    o = date(d.year, 10, 31); e = o - timedelta(days=(o.weekday() + 1) % 7); return s <= d < e
TZ = {"ny": lambda d: -4 if us_dst(d) else -5, "cet": lambda d: 2 if eu_dst(d) else 1,
      "ldn": lambda d: 1 if eu_dst(d) else 0, "tky": lambda d: 9}
MK = [("nas100", "ny", 10, 16), ("us500", "ny", 10, 16), ("us30", "ny", 10, 16), ("ger40", "cet", 9, 17),
      ("fra40", "cet", 9, 17), ("eustx50", "cet", 9, 17), ("uk100", "ldn", 8, 16), ("jp225", "tky", 9, 15),
      ("xauusd", "ldn", 8, 16), ("xagusd", "ldn", 8, 16), ("wti", "ny", 9, 14)]
COST, LB = 0.0001, 14
per = lambda d: "2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"
for m, tz, h0, h1 in MK:
    days = defaultdict(dict)
    for r in csv.DictReader(open(f"data/factory_h1/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        lt = t + timedelta(hours=TZ[tz](t.date()))
        if lt.weekday() < 5 and h0 <= lt.hour < h1:
            days[lt.date()][lt.hour] = tuple(float(r[k]) for k in ("open", "high", "low", "close"))
    D = [d for d in sorted(days) if len(days[d]) == h1 - h0]
    mv = {d: {h: abs(days[d][h][3] / days[d][h0][0] - 1) for h in days[d]} for d in D}
    res = []; pc = None
    for n, d in enumerate(D):
        B = days[d]; o = B[h0][0]
        if n < LB or pc is None or (d - D[n-1]).days > 4: pc = B[h1-1][3]; continue
        hist = D[n-LB:n]; up0, lo0 = max(o, pc), min(o, pc); pos = 0; e = 0; pnl = 0; tp = []
        for h in range(h0, h1):
            op, hi, lo, c = B[h]; tp.append((hi + lo + c) / 3)
            if h == h1 - 1: break
            sig = st.mean(mv[x][h] for x in hist); U, L, vw = up0 * (1 + sig), lo0 * (1 - sig), st.mean(tp)
            fill = B[h + 1][0]
            if pos > 0 and c < max(U, vw): pnl += (fill - e) / e - COST; pos = 0
            elif pos < 0 and c > min(L, vw): pnl += (e - fill) / e - COST; pos = 0
            if pos == 0:
                if c > U: pos, e = 1, fill
                elif c < L: pos, e = -1, fill
        if pos: pnl += pos * (B[h1-1][3] - e) / e - COST
        res.append((d, pnl)); pc = B[h1-1][3]
    r = [p for _, p in res]; sh = st.mean(r) / st.pstdev(r) * math.sqrt(252)
    by = defaultdict(float)
    for d, p in res: by[per(d)] += p
    post = [p for d, p in res if d >= date(2024, 3, 1)]
    ok = all(by[k] >= 0 for k in ("2014-20", "2021-23", "2024-26")) and sh >= 0.8 and sum(post) > 0
    yrs = len(r) / 252
    print(f"{m:8s} {res[0][0].year}-{res[-1][0].year} {sum(r)*100/yrs:+6.1f}%/yr at 1x  Sharpe {sh:5.2f}  "
          + "  ".join(f"{k} {by[k]*100:+6.1f}%" for k in ("2014-20", "2021-23", "2024-26"))
          + f"  post-paper {sum(post)*100:+5.1f}%" + ("  PASS" if ok else ""))
