"""Gold 'night effect' (pre-registered 28 Oct 2026, before any run). FTMO XAUUSD H1, 2014-2026, UK local time.
Sessions: ASIA 23:00 (previous evening) -> 08:00; LONDON 08:00 -> 13:00; NEW YORK 13:00 -> 20:00 (all UK time; flat
before FTMO's ~21:00 UK swap). Trades: N1 long ASIA every weekday; N2 short LONDON+NY (08:00 -> 20:00);
N3 both together. Cost 0.012% per round trip (no swap: nothing held at 21:00 UK).
Pass: >= +0.02% a trade after costs AND positive in each of 2014-20, 2021-23, 2024-26, AND t >= 2 overall.
Also shown (not a trade): average raw return per session, to see where gold's gains happen."""
import csv, math, statistics as st
from datetime import datetime, timezone, timedelta, date
from collections import defaultdict
def uk_dst(d):
    m = date(d.year, 3, 31); s = m - timedelta(days=(m.weekday() + 1) % 7)
    o = date(d.year, 10, 31); e = o - timedelta(days=(o.weekday() + 1) % 7); return s <= d < e
P = {}
for r in csv.DictReader(open("data/factory_h1/xauusd_h1.csv")):
    t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
    uk = t + timedelta(hours=1 if uk_dst(t.date()) else 0)
    P[uk] = (float(r["open"]), float(r["close"]))
COST = 0.00012
per = lambda d: "2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"
def px(d, h): return P.get(datetime(d.year, d.month, d.day, h), (None,))[0]   # open of the hour = price at hh:00
days = sorted({k.date() for k in P if k.weekday() < 5 and k.year >= 2014})
raw = defaultdict(list); T = defaultdict(list)
for d in days:
    prev = d - timedelta(days=3 if d.weekday() == 0 else 1)
    a23 = px(prev, 23); p8, p13, p20 = px(d, 8), px(d, 13), px(d, 20)
    if None in (a23, p8, p13, p20): continue
    asia, ldn, ny = p8 / a23 - 1, p13 / p8 - 1, p20 / p13 - 1
    raw["ASIA 23-08"].append(asia); raw["LONDON 08-13"].append(ldn); raw["NEW YORK 13-20"].append(ny)
    T["N1 long Asia"].append((d, asia - COST)); T["N2 short London+NY"].append((d, -(p20 / p8 - 1) - COST))
    T["N3 both"].append((d, asia - COST - (p20 / p8 - 1) - COST))
print("Average raw move per session (2014-2026):")
for k, v in raw.items():
    print(f"  {k:16s} {st.mean(v)*100:+.4f}% per day  (sum {sum(v)*100:+.0f}% over {len(v)} days)")
for k, v in T.items():
    r = [x for _, x in v]; m = st.mean(r); t = m / (st.pstdev(r) / len(r) ** .5)
    by = defaultdict(list)
    for d, x in v: by[per(d)].append(x)
    ok = m >= 0.0002 and all(st.mean(by[p]) > 0 for p in ("2014-20", "2021-23", "2024-26")) and t >= 2
    yrs = defaultdict(float)
    for d, x in v: yrs[d.year] += x
    print(f"{k:22s} n={len(r)} avg {m*100:+.4f}% t={t:4.1f} win {sum(x>0 for x in r)/len(r):.0%} | "
          + "  ".join(f"{p} {st.mean(by[p])*100:+.4f}%" for p in sorted(by)) + ("  PASS" if ok else ""))
    print("    by year: " + " ".join(f"{y}:{v*100:+.1f}%" for y, v in sorted(yrs.items())))
