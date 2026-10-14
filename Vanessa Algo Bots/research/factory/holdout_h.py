"""HOLDOUT 2024-2026 for the v2 shortlist, run once. Also: trades per year, edge over a random-entry baseline
(same exit, enter every bar of the same session/filter), drawdown, worst day, correlation with NAS bot + Daily Systems."""
import json, re, statistics as st
from collections import defaultdict
import numpy as np
import factory_h as F

SL = json.load(open("results_v2/shortlist.json"))
nas = json.load(open(F.R0 + "/data/nas_bot_daily_R_2021_2026.json"))
if isinstance(nas, dict) and len(nas) == 2 and all(isinstance(v, list) for v in nas.values()): nas = dict(zip(*nas.values()))
ds = {}
for f in ("3e7ac88f-DS_tick_data_20-23_log.txt", "6d9a4ab0-DS_tick_data_24-26_log.txt"):
    for line in open(f"/root/.claude/uploads/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/{f}"):
        m = re.search(r"Info \| P\|(\d{4}-\d\d-\d\d)\|(-?\d+)", line)
        if m: ds[m.group(1)] = float(m.group(2))


def parse(raw):
    ek, ep, f, xk, xp, side = raw
    ep = float(ep) if "." in ep else int(ep)
    xp = eval(xp) if xk == "STOPTGT" else (xp if xk == "MR" else int(xp))
    return (ek, ep, f, xk, xp, int(side))


def corr(d1, d2):
    keys = sorted(k for k in set(d1) | set(d2) if k >= "2021-01-01")
    try: return st.correlation([d1.get(k, 0) for k in keys], [d2.get(k, 0) for k in keys])
    except Exception: return 0.0


cache = {}
for row in SL:
    g, tf = row["group"], row["tf"]
    if (g, tf) not in cache:
        F._init(g, tf); cache[(g, tf)] = F._M[g]
    spec = parse(row["raw"]); T = []; base = []
    for m in cache[(g, tf)]:
        flt = F.filt(m, spec[2], spec[5])
        T += F.simulate(m, F.entry_signal(m, spec[0], spec[1], spec[5]) & flt, spec[3], spec[4], spec[5])
        base += F.simulate(m, flt & (np.arange(len(m.c)) % 7 == 0), spec[3], spec[4], spec[5])
    H = [t for t in T if t[2] == "H"]; s = F.stats(H); lo = F.boot_lo([t[1] for t in H])
    allr = sorted(T); eq = pk = dd = 0
    for t in allr: eq += t[1]; pk = max(pk, eq); dd = max(dd, pk - eq)
    day = defaultdict(float)
    for t in allr: day[t[0].isoformat()] += t[1]
    yrs = (allr[-1][0] - allr[0][0]).days / 365.25
    b_avg = F.stats([t for t in base if t[2] in "BC"])["avg"]; s_avg = F.stats([t for t in T if t[2] in "BC"])["avg"]
    row["holdout"] = dict(n=s["n"], avg=s["avg"], pf=s["pf"], lo=lo)
    print(f"{g:3s} {row['spec']:40s} {len(T)/yrs:5.0f}/yr | edge vs random {s_avg - b_avg:+.3f}R | maxDD {dd:5.1f}R worst day {min(day.values()):+.2f}R | "
          f"corr NAS {corr(day, nas):+.2f} DS {corr(day, ds):+.2f} | HOLDOUT n={s['n']} avg={s['avg']:+.3f}R pf={s['pf']:.2f} 95%low={lo:+.3f} "
          f"{'PASS' if s['avg'] > 0 else 'FAIL'}")
json.dump(SL, open("results_v2/shortlist_holdout.json", "w"), indent=1, default=str)
