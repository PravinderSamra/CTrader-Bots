"""Do CPI / PPI / jobs-report (NFP) releases have an FOMC-style drift? Pre-registered 28 Oct 2026, before any run.
Releases are at 8:30 New York, before the cash open. Dates from FRED (data/macro_dates).
W1 pre-release drift (FOMC-style): long 14:00 NY the day before -> 08:00 NY on release day (out before the number).
W2 announcement-day premium (Savor & Wilson 2013): long at the 16:00 close the day before -> 16:00 close on release day.
W3 release day only: 10:00 -> 16:00 NY on release day.
Baseline for each window: the same window on every other Mon-Fri day (not a CPI/PPI/NFP/FOMC day).
Costs 0.025% per round trip + 5%/yr swap per night. US100 and US500 H1 (FTMO), 2014-2026.
Pass: >= +0.05% a trade after costs AND beats the baseline by >= 0.05% in each of 2014-20, 2021-23, 2024-26.
18 trials (3 releases x 3 windows x 2 markets)."""
import csv, json, statistics as st, sys
from datetime import datetime, timezone, timedelta, date
sys.path.insert(0, "ssrn"); from fomc_drift import ny_offset, MEET
REL = {k: {date.fromisoformat(x["date"]) for x in json.load(open(f"data/macro_dates/{k}.json"))["release_dates"]}
       for k in ("cpi", "ppi", "nfp")}
FOMC = {date.fromisoformat(s) + timedelta(days=1) for s in MEET}
ALL = set().union(*REL.values()) | FOMC
COST, SW = 0.00025, 0.05 / 365
per = lambda d: "2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"
def load(m):
    b = {}
    for r in csv.DictReader(open(f"data/factory_h1/{m}_h1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).replace(tzinfo=None)
        ny = t - timedelta(hours=ny_offset(t.date())); b[ny] = (float(r["open"]), float(r["close"]))
    return b
def window(b, d, w):
    prev = d - timedelta(days=3 if d.weekday() == 0 else 1)
    if w == "W1": a, z, nights = (prev, 14, "o"), (d, 8, "o"), 1
    elif w == "W2": a, z, nights = (prev, 15, "c"), (d, 15, "c"), 1
    else: a, z, nights = (d, 10, "o"), (d, 15, "c"), 0
    ka = datetime(a[0].year, a[0].month, a[0].day, a[1]); kz = datetime(z[0].year, z[0].month, z[0].day, z[1])
    if ka not in b or kz not in b: return None
    pa = b[ka][0] if a[2] == "o" else b[ka][1]; pz = b[kz][0] if z[2] == "o" else b[kz][1]
    return pz / pa - 1 - COST - SW * nights * (3 if d.weekday() == 0 and nights else 1)
for m in ("nas100", "us500"):
    b = load(m); days = sorted({k.date() for k in b if k.weekday() < 5 and k.year >= 2014})
    print(f"\n=== {m} ===")
    for w, name in (("W1", "pre-release 14:00 -> 08:00"), ("W2", "close -> close through release"), ("W3", "release day 10:00 -> 16:00")):
        base = {}
        for d in days:
            if d in ALL: continue
            r = window(b, d, w)
            if r is not None: base.setdefault(per(d), []).append(r)
        bm = {p: st.mean(v) for p, v in base.items()}
        print(f" {name:32s} baseline " + "  ".join(f"{p} {bm[p]*100:+.3f}%" for p in sorted(bm)))
        for k in ("cpi", "ppi", "nfp"):
            T = {}
            for d in sorted(REL[k]):
                if d.year < 2014 or d > days[-1]: continue
                r = window(b, d, w)
                if r is not None: T.setdefault(per(d), []).append(r)
            ok = all(p in T and st.mean(T[p]) >= 0.0005 and st.mean(T[p]) - bm[p] >= 0.0005 for p in bm)
            allr = [x for v in T.values() for x in v]
            print(f"   {k.upper():4s} n={len(allr):3d} avg {st.mean(allr)*100:+.3f}% win {sum(x>0 for x in allr)/len(allr):.0%} | "
                  + "  ".join(f"{p} {st.mean(T[p])*100:+.3f}%" for p in sorted(T)) + ("  PASS" if ok else ""))
