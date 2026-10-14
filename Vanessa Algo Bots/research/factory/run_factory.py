"""Run Strategy Factory v1 on all groups and apply the pre-registered pipeline (see factory_d1.py docstring).
Writes research/factory/results_v1/*.csv and a summary to stdout."""
import csv, json, os, sys, time
from collections import defaultdict
from multiprocessing import Pool
import factory_d1 as F

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results_v1")
os.makedirs(OUT, exist_ok=True)
SPECS = F.all_specs()


def neighbours(spec):
    ek, ep, f, xk, xp, side = spec
    eps = dict(F.ENTRIES)[ek]; xps = dict(F.EXITS)[xk]; out = []
    i = eps.index(ep); j = xps.index(xp)
    for di in (-1, 1):
        if 0 <= i + di < len(eps): out.append((ek, eps[i + di], f, xk, xp, side))
    for dj in (-1, 1):
        if 0 <= j + dj < len(xps): out.append((ek, ep, f, xk, xps[j + dj], side))
    return out


def run_group(group):
    t0 = time.time()
    with Pool(4, initializer=F._init, initargs=(group,)) as pool:
        res = pool.map(F.evaluate, [(group, s, 1.0) for s in SPECS], chunksize=8)
    data = {spec: pm for _, spec, _, pm in res}
    print(f"[{group}] {len(SPECS)} strategies x {len(next(iter(data.values())))} markets in {time.time() - t0:.0f}s", flush=True)
    return data


def pooled(pm, tag):
    return [t for v in pm.values() for t in v if t[2] == tag]


def stage1(spec, pm):
    B = pooled(pm, "B"); s = F.stats(B)
    if s["n"] < 100: return None
    ok = s["avg"] >= 0.10 or (s["win"] >= 0.60 and s["pf"] >= 1.2 and s["avg"] > 0)
    if not ok: return None
    mk = [F.stats([t for t in v if t[2] == "B"])["avg"] for v in pm.values() if any(t[2] == "B" for t in v)]
    if sum(a > 0 for a in mk) < 0.6 * len(mk): return None
    yr = defaultdict(float)
    for t in B: yr[t[0].year] += t[1]
    if sum(v > 0 for v in yr.values()) < 0.6 * len(yr): return None
    return s, sum(a > 0 for a in mk) / len(mk), sum(v > 0 for v in yr.values()) / len(yr)


if __name__ == "__main__":
    groups = sys.argv[1:] or list(F.GROUPS)
    summary = []
    for g in groups:
        data = run_group(g)
        bavg = {s: F.stats(pooled(pm, "B"))["avg"] for s, pm in data.items()}
        s1 = {s: v for s, pm in data.items() if (v := stage1(s, pm))}
        s2 = {}
        for s, v in s1.items():
            nb = neighbours(s)
            if sum(bavg.get(x, -1) > 0 for x in nb) < (2 / 3) * len(nb): continue
            s2[s] = v
        # doubled costs for stage-2 survivors
        if s2:
            with Pool(4, initializer=F._init, initargs=(g,)) as pool:
                res = pool.map(F.evaluate, [(g, s, 2.0) for s in s2], chunksize=4)
            dbl = {spec: F.stats(pooled(pm, "B"))["avg"] for _, spec, _, pm in res}
            s2 = {s: v for s, v in s2.items() if dbl[s] > 0}
        s3 = {}
        for s, v in s2.items():
            C = pooled(data[s], "C"); cs = F.stats(C)
            if cs["n"] >= 30 and cs["avg"] >= 0.05:
                s3[s] = (v, cs, F.boot_lo([t[1] for t in C]))
        print(f"[{g}] stage1 {len(s1)}  stage2 (neighbours + double cost) {len(s2)}  stage3 (confirm 2021-23) {len(s3)}", flush=True)
        with open(f"{OUT}/{g}_all.csv", "w", newline="") as fh:
            w = csv.writer(fh); w.writerow(["spec", "B_n", "B_avg", "B_pf", "B_win", "C_n", "C_avg", "stage"])
            for s, pm in data.items():
                b = F.stats(pooled(pm, "B")); c = F.stats(pooled(pm, "C"))
                st_ = 3 if s in s3 else 2 if s in s2 else 1 if s in s1 else 0
                w.writerow([F.spec_id(s), b["n"], round(b["avg"], 4), round(b["pf"], 3), round(b["win"], 3), c["n"], round(c["avg"], 4), st_])
        for s, (v, cs, lo) in s3.items():
            summary.append((g, s, v, cs, lo, data[s]))
    # stage 4: de-duplicate by daily P/L correlation (build + confirm)
    def daily(pm):
        d = defaultdict(float)
        for v in pm.values():
            for t in v:
                if t[2] in "BC": d[t[0]] += t[1]
        return d
    summary.sort(key=lambda x: -x[3]["avg"])
    kept = []
    for row in summary:
        d1 = daily(row[5]); dup = False
        for k in kept:
            d2 = daily(k[5]); keys = sorted(set(d1) | set(d2))
            if len(keys) > 30:
                import statistics as st
                a = [d1.get(x, 0) for x in keys]; b = [d2.get(x, 0) for x in keys]
                try:
                    if st.correlation(a, b) > 0.7: dup = True; break
                except Exception: pass
        if not dup: kept.append(row)
    with open(f"{OUT}/shortlist.json", "w") as fh:
        json.dump([dict(group=g, spec=F.spec_id(s), raw=list(map(str, s)), build=v[0], mkts_pos=v[1], years_pos=v[2], confirm=cs, confirm_lo=lo)
                   for g, s, v, cs, lo, _ in kept], fh, indent=1, default=str)
    print(f"\nSHORTLIST after de-duplication: {len(kept)}")
    for g, s, v, cs, lo, _ in kept:
        print(f"  {g:4s} {F.spec_id(s):38s} build n={v[0]['n']:4d} avg={v[0]['avg']:+.3f}R pf={v[0]['pf']:.2f} win={v[0]['win']:.0%} "
              f"mkts+={v[1]:.0%} yrs+={v[2]:.0%} | confirm n={cs['n']:3d} avg={cs['avg']:+.3f}R (95% low {lo:+.3f})")
