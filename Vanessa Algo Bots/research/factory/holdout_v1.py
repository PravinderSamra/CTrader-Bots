"""HOLDOUT 2024-2026 for the v1 shortlist - run once (pre-registered: must be positive)."""
import json, statistics as st
from collections import defaultdict
import factory_d1 as F
from checks_v1 import parse  # noqa (parse only)

SL = json.load(open("results_v1/shortlist.json"))
F._init("ALL"); out = []
for row in SL:
    spec = parse(row["raw"]); g = row["group"]; H = []; per = {}
    for m in F._M[g]:
        sig = F.entry_signal(m, spec[0], spec[1], spec[5]) & F.filt(m, spec[2], spec[5])
        t = [x for x in F.simulate(m, sig, spec[3], spec[4], spec[5]) if x[2] == "H"]
        H += t; per[m.name] = sum(x[1] for x in t)
    s = F.stats(H); lo = F.boot_lo([x[1] for x in H])
    yr = defaultdict(float)
    for x in H: yr[x[0].year] += x[1]
    row["holdout"] = dict(n=s["n"], avg=s["avg"], pf=s["pf"], win=s["win"], lo=lo, years={y: round(v, 1) for y, v in sorted(yr.items())},
                          mkts_pos=sum(v > 0 for v in per.values()) / len(per))
    out.append(row)
    print(f"{g:3s} {row['spec']:34s} confirm {row['confirm']['avg']:+.3f}R | HOLDOUT n={s['n']:3d} avg={s['avg']:+.3f}R pf={s['pf']:.2f} "
          f"win={s['win']:.0%} 95%low={lo:+.3f} mkts+={row['holdout']['mkts_pos']:.0%} {row['holdout']['years']}  {'PASS' if s['avg'] > 0 else 'FAIL'}")
json.dump(out, open("results_v1/shortlist_holdout.json", "w"), indent=1, default=str)
