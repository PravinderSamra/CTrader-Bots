"""Thief re-check: honest fills (enter next open, exit next open after the exit close) and a control:
same exit rule from EVERY day's close (random entry), to see if the entry adds anything."""
import sys, statistics as st
sys.path.insert(0, "factory"); import factory_d1 as F
IDX = ["us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50"]
COST, SW = 0.00025, 0.05 / 365
per = lambda d: "2014-20" if d.year <= 2020 else "2021-23" if d.year <= 2023 else "2024-26"
def rep(name, T):
    by = {}
    for d, r in T: by.setdefault(per(d), []).append(r)
    print(f"  {name:40s} n={len(T):5d} avg {st.mean(r for _,r in T)*100:+.3f}% win {sum(r>0 for _,r in T)/len(T):.0%} worst {min(r for _,r in T)*100:+.1f}% | "
          + " | ".join(f"{p} {st.mean(v)*100:+.3f}%" for p, v in sorted(by.items())))
def exit_mean(o, c, i, side, n):
    j = i + 1
    while j < min(n - 2, i + 20):
        m20 = sum(c[j-19:j+1]) / 20
        if (side < 0 and c[j] < m20) or (side > 0 and c[j] > m20): break
        j += 1
    return j
out = {}
for m in IDX:
    d, o, h, l, c = F.load(m); o, h, l, c = list(o), list(h), list(l), list(c); n = len(c)
    for i in range(30, n - 25):
        w = c[i-20:i]; mid = sum(w)/20; sd = (sum((x-mid)**2 for x in w)/20) ** .5
        w2 = c[i-19:i+1]; mid2 = sum(w2)/20; sd2 = (sum((x-mid2)**2 for x in w2)/20) ** .5
        tr = lambda k: max(h[k], c[k-1]) - min(l[k], c[k-1]); atr = sum(tr(k) for k in range(i-14, i)) / 14
        big = h[i-1]-l[i-1] > atr and h[i]-l[i] > atr
        for side in (1, -1):
            j = exit_mean(o, c, i, side, n); e, x = o[i+1], o[j+1]
            r = side*(x-e)/e - COST - SW*(j+1-i-1)*1.4
            out.setdefault(("control", side), []).append((d[i], r))
            sig = (c[i-1] < mid-2*sd and c[i] > mid2-2*sd2) if side > 0 else (c[i-1] > mid+2*sd and c[i] < mid2+2*sd2)
            if big and sig: out.setdefault(("thief", side), []).append((d[i], r))
for side in (1, -1):
    nm = "long" if side > 0 else "short"
    rep(f"Thief {nm}, honest fills, exit at mean", out[("thief", side)])
    rep(f"Control: every day {nm}, same exit", out[("control", side)])
