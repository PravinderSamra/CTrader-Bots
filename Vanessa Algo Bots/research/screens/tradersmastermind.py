"""Traders Mastermind ideas (screened 26 Oct 2026, rules fixed before running):
1 Thief: day1 close beyond BB(20,2), day2 close back inside, both day ranges > ATR(14); trade at day2 close against
  day1 (short above / long below). Exits fixed in advance: (a) 5 days, (b) first close past the 20-day average.
2 Tuesday overnight: long Monday 15:45 NY (H1 close of the 15:00 bar) -> Tuesday 9:30 NY open. Baseline: every weeknight.
3 Power hour: long 15:00 -> 15:57 NY (H1 15:00 bar). Fridays vs all days.
4 Outside bar + filters: high > prior high, low < prior low, close in top/bottom 25% of range AND beyond the prior
  high/low, prior bar the other colour; enter next open, hold 1 or 3 days.
Costs 0.025% per round trip + 5%/yr swap per night. Pass: >= +0.05% a trade after costs in 2014-20, 2021-23 AND 2024-26,
and (for longs) better than the all-days baseline."""
import sys, csv, statistics as st
from datetime import datetime, timezone, timedelta, date
sys.path.insert(0, "factory"); sys.path.insert(0, "ssrn")
import factory_d1 as F
from fomc_drift import ny_offset
IDX = ["us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50"]
COST, SW = 0.00025, 0.05 / 365
per = lambda d: "2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"
def rep(name, T):
    if not T: print(f"  {name}: no trades"); return
    by = {}
    for d, r in T: by.setdefault(per(d), []).append(r)
    ok = all(p in by and st.mean(by[p]) >= 0.0005 for p in ("2014-20", "2021-23", "2024-26"))
    print(f"  {name:44s} n={len(T):4d} avg {st.mean(r for _,r in T)*100:+.3f}% win {sum(r>0 for _,r in T)/len(T):.0%} | "
          + " | ".join(f"{p} {st.mean(v)*100:+.3f}% ({len(v)})" for p, v in sorted(by.items())) + ("  PASS" if ok else ""))

def daily(m):
    d, o, h, l, c = F.load(m); return d, list(o), list(h), list(l), list(c)

print("1 THIEF (daily, 9 indices)")
res = {}
for m in IDX:
    d, o, h, l, c = daily(m); n = len(c)
    for i in range(30, n - 6):
        w = c[i-20:i]; mid = sum(w)/20; sd = (sum((x-mid)**2 for x in w)/20) ** .5
        w2 = c[i-19:i+1]; mid2 = sum(w2)/20; sd2 = (sum((x-mid2)**2 for x in w2)/20) ** .5
        tr = lambda k: max(h[k], c[k-1]) - min(l[k], c[k-1])
        atr = sum(tr(k) for k in range(i-14, i)) / 14
        if not (h[i-1]-l[i-1] > atr and h[i]-l[i] > atr): continue
        for side, cond in ((-1, c[i-1] > mid + 2*sd and c[i] < mid2 + 2*sd2), (1, c[i-1] < mid - 2*sd and c[i] > mid2 - 2*sd2)):
            if not cond: continue
            e = c[i]
            x5 = c[i+5]; r5 = side*(x5-e)/e - COST - SW*7
            j = i + 1
            while j < min(n-1, i+20):
                m20 = sum(c[j-19:j+1])/20
                if (side < 0 and c[j] < m20) or (side > 0 and c[j] > m20): break
                j += 1
            rm = side*(c[j]-e)/e - COST - SW*(j-i)*1.4
            res.setdefault(("short" if side<0 else "long", "5 days"), []).append((d[i], r5))
            res.setdefault(("short" if side<0 else "long", "to 20-day avg"), []).append((d[i], rm))
for k, T in sorted(res.items()): rep(f"Thief {k[0]}, exit {k[1]}", T)
base = []
for m in IDX:
    d, o, h, l, c = daily(m)
    base += [(d[i], (c[i+5]-c[i])/c[i] - COST - SW*7) for i in range(30, len(c)-6)]
rep("baseline: long any close, hold 5 days", base)

print("2/3 TUESDAY OVERNIGHT and POWER HOUR (H1)")
def h1(m):
    b = {}
    for r in csv.DictReader(open(f"data/factory_h1/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"])/1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=ny_offset(t.date()))
        b[ny] = (float(r["open"]), float(r["close"]))
    return b
for m in ("us500", "nas100", "us30"):
    b = h1(m); days = sorted({k.date() for k in b})
    on, onall, ph, phf = [], [], [], []
    for dd in days:
        k15 = datetime(dd.year, dd.month, dd.day, 15)
        if k15 in b:
            ph.append((dd, (b[k15][1]-b[k15][0])/b[k15][0] - COST))
            if dd.weekday() == 4: phf.append(ph[-1])
            nxt = dd + timedelta(days=1)
            k930 = datetime(nxt.year, nxt.month, nxt.day, 9)   # 9:00-10:00 bar opens 9:00; use 10:00 bar open ~ 9:30 proxy below
            k10 = datetime(nxt.year, nxt.month, nxt.day, 10)
            if dd.weekday() <= 3 and k10 in b:
                r = (b[k10][0]-b[k15][1])/b[k15][1] - COST - SW
                onall.append((dd, r))
                if dd.weekday() == 0: on.append((dd, r))
    print(f" {m}"); rep("Monday night -> Tuesday open (long)", on); rep("baseline: every Mon-Thu night", onall)
    rep("Power hour, Fridays (long)", phf); rep("Power hour, all days", ph)

print("4 OUTSIDE BAR + filters (daily, 9 indices)")
ob = {}
for m in IDX:
    d, o, h, l, c = daily(m); n = len(c)
    for i in range(2, n-4):
        if not (h[i] > h[i-1] and l[i] < l[i-1]): continue
        rg = h[i]-l[i]
        bull = c[i] >= h[i]-0.25*rg and c[i] > h[i-1] and c[i-1] < o[i-1]
        bear = c[i] <= l[i]+0.25*rg and c[i] < l[i-1] and c[i-1] > o[i-1]
        for side, ok in ((1, bull), (-1, bear)):
            if not ok: continue
            e = o[i+1]
            for hd in (1, 3):
                ob.setdefault(("long" if side>0 else "short", hd), []).append((d[i], side*(c[i+hd]-e)/e - COST - SW*hd*1.4))
for k, T in sorted(ob.items()): rep(f"Outside bar {k[0]}, hold {k[1]} day(s)", T)
