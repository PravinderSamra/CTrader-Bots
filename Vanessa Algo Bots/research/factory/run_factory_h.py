"""Run Strategy Factory v2 (H1 and H4). Pre-registered pipeline (15 Oct 2026):
 1. BUILD (.. 2020): >= 300 pooled trades, avg >= +0.10R (or win >= 60%, PF >= 1.2, avg > 0),
    >= 60% of markets and >= 60% of years positive.
 2. Robustness on BUILD: >= 2/3 of parameter neighbours positive; still positive with doubled costs.
 3. CONFIRM 2021-23 (unseen): >= 100 trades, avg >= +0.05R.
 4. Correlation of daily P/L with the live NAS bot (2021-23 only) must be below 0.3; then de-duplicate
    (daily P/L correlation > 0.7 -> keep the better).
 5. HOLDOUT 2024-26 opened once for the shortlist (holdout_h.py)."""
import csv, json, os, statistics as st, sys, time
from collections import defaultdict
from multiprocessing import Pool
import factory_h as F

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_v2"); os.makedirs(OUT, exist_ok=True)
SPECS = F.all_specs()
nas = json.load(open(F.R0 + "/data/nas_bot_daily_R_2021_2026.json"))
if isinstance(nas, dict) and len(nas) == 2 and all(isinstance(v, list) for v in nas.values()): nas = dict(zip(*nas.values()))


def neighbours(s):
    ek, ep, f, xk, xp, side = s; eps = dict(F.ENTRIES)[ek]; xps = dict(F.EXITS)[xk]; out = []
    i, j = eps.index(ep), xps.index(xp)
    for d in (-1, 1):
        if 0 <= i + d < len(eps): out.append((ek, eps[i + d], f, xk, xp, side))
        if 0 <= j + d < len(xps): out.append((ek, ep, f, xk, xps[j + d], side))
    return out


def pooled(pm, tag): return [t for v in pm.values() for t in v if t[2] == tag]


def stage1(pm):
    B = pooled(pm, "B"); s = F.stats(B)
    if s["n"] < 300: return None
    if not (s["avg"] >= 0.10 or (s["win"] >= 0.60 and s["pf"] >= 1.2 and s["avg"] > 0)): return None
    mk = [F.stats([t for t in v if t[2] == "B"])["avg"] for v in pm.values() if any(t[2] == "B" for t in v)]
    if sum(a > 0 for a in mk) < 0.6 * len(mk): return None
    yr = defaultdict(float)
    for t in B: yr[t[0].year] += t[1]
    if sum(v > 0 for v in yr.values()) < 0.6 * len(yr): return None
    return s


def daily(pm, tags):
    d = defaultdict(float)
    for v in pm.values():
        for t in v:
            if t[2] in tags: d[t[0].isoformat()] += t[1]
    return d


def corr(d1, d2, lo, hi):
    keys = sorted(k for k in set(d1) | set(d2) if lo <= k <= hi)
    a = [d1.get(k, 0) for k in keys]; b = [d2.get(k, 0) for k in keys]
    try: return st.correlation(a, b)
    except Exception: return 0.0


if __name__ == "__main__":
    jobs = [(g, tf) for tf in (4, 1) for g in (sys.argv[1:] or list(F.GROUPS))]
    short = []
    for g, tf in jobs:
        t0 = time.time()
        with Pool(4, initializer=F._init, initargs=(g, tf)) as pool:
            res = pool.map(F.evaluate, [(g, s, 1.0) for s in SPECS], chunksize=8)
        data = dict(res); nm = len(next(iter(data.values())))
        bavg = {s: F.stats(pooled(pm, "B"))["avg"] for s, pm in data.items()}
        s1 = {s: v for s, pm in data.items() if (v := stage1(pm))}
        s2 = {s: v for s, v in s1.items() if sum(bavg.get(x, -1) > 0 for x in neighbours(s)) >= (2 / 3) * len(neighbours(s))}
        if s2:
            with Pool(4, initializer=F._init, initargs=(g, tf)) as pool:
                dbl = dict(pool.map(F.evaluate, [(g, s, 2.0) for s in s2], chunksize=4))
            s2 = {s: v for s, v in s2.items() if F.stats(pooled(dbl[s], "B"))["avg"] > 0}
        s3 = {}
        for s, v in s2.items():
            cs = F.stats(pooled(data[s], "C"))
            if cs["n"] >= 100 and cs["avg"] >= 0.05: s3[s] = (v, cs)
        s4 = {}
        for s, (v, cs) in s3.items():
            cn = corr(daily(data[s], "C"), nas, "2021-01-01", "2023-12-31")
            if cn < 0.3: s4[s] = (v, cs, cn)
        print(f"[H{tf} {g}] {len(SPECS)} strategies x {nm} markets ({time.time() - t0:.0f}s): stage1 {len(s1)}  stage2 {len(s2)}  "
              f"confirm {len(s3)}  NAS-corr<0.3 {len(s4)}", flush=True)
        with open(f"{OUT}/H{tf}_{g}_all.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["spec", "B_n", "B_avg", "B_pf", "C_n", "C_avg", "stage"])
            for s, pm in data.items():
                b = F.stats(pooled(pm, "B")); c = F.stats(pooled(pm, "C"))
                w.writerow([F.spec_id(s, tf), b["n"], round(b["avg"], 4), round(b["pf"], 3), c["n"], round(c["avg"], 4),
                            4 if s in s4 else 3 if s in s3 else 2 if s in s2 else 1 if s in s1 else 0])
        for s, (v, cs, cn) in s4.items():
            yrs = (max(t[0] for t in pooled(data[s], "C")) - min(t[0] for t in pooled(data[s], "B"))).days / 365.25
            short.append(dict(group=g, tf=tf, spec=F.spec_id(s, tf), raw=[str(x) for x in s], build=v, confirm=cs, nas_corr=cn,
                              per_year=round((v["n"] + cs["n"]) / yrs), daily=daily(data[s], "BC")))
    short.sort(key=lambda x: -x["confirm"]["avg"]); kept = []
    for row in short:
        if all(corr(row["daily"], k["daily"], "0", "9") <= 0.7 for k in kept): kept.append(row)
    for k in kept: k.pop("daily")
    json.dump(kept, open(f"{OUT}/shortlist.json", "w"), indent=1, default=str)
    print(f"\nSHORTLIST after de-duplication: {len(kept)}")
    for k in kept:
        b, c = k["build"], k["confirm"]
        print(f"  {k['group']:3s} {k['spec']:40s} build n={b['n']:5d} avg={b['avg']:+.3f}R pf={b['pf']:.2f} | confirm n={c['n']:4d} "
              f"avg={c['avg']:+.3f}R | ~{k['per_year']}/yr | NAS corr {k['nas_corr']:+.2f}")
