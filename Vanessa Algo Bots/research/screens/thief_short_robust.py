"""Thief SHORT robustness: neighbours (band width, ATR filter), doubled costs, per index, t-stat, bootstrap."""
import sys, random, statistics as st
sys.path.insert(0, "factory"); import factory_d1 as F
IDX = ["us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50"]
SW = 0.05 / 365
data = {m: [list(x) if i else x for i, x in enumerate(F.load(m))] for m in IDX}
def run(k=2.0, atrf=True, cost=0.00025, lb=20):
    T = []
    for m in IDX:
        d, o, h, l, c = data[m]; n = len(c)
        for i in range(30, n - 25):
            w = c[i-lb:i]; mid = sum(w)/lb; sd = (sum((x-mid)**2 for x in w)/lb) ** .5
            w2 = c[i-lb+1:i+1]; mid2 = sum(w2)/lb; sd2 = (sum((x-mid2)**2 for x in w2)/lb) ** .5
            if not (c[i-1] > mid + k*sd and c[i] < mid2 + k*sd2): continue
            if atrf:
                tr = lambda q: max(h[q], c[q-1]) - min(l[q], c[q-1]); atr = sum(tr(q) for q in range(i-14, i)) / 14
                if not (h[i-1]-l[i-1] > atr and h[i]-l[i] > atr): continue
            j = i + 1
            while j < min(n - 2, i + 20):
                if c[j] < sum(c[j-19:j+1]) / 20: break
                j += 1
            e, x = o[i+1], o[j+1]
            T.append((d[i], m, -(x-e)/e - cost - SW*(j-i)*1.4))
    return T
def line(name, T):
    r = [t[2] for t in T]; m = st.mean(r); se = st.pstdev(r)/len(r)**.5
    print(f"  {name:34s} n={len(r):4d} avg {m*100:+.3f}%  t={m/se:4.1f}  win {sum(x>0 for x in r)/len(r):.0%}")
base = run()
line("Thief short (as published)", base)
for k in (1.8, 2.2, 2.5): line(f"band {k} sd", run(k=k))
line("no ATR filter", run(atrf=False))
line("doubled costs", run(cost=0.0005))
by = {}
for d, m, r in base: by.setdefault(m, []).append(r)
print("  per index: " + ", ".join(f"{m} {st.mean(v)*100:+.2f}% ({len(v)})" for m, v in by.items()))
random.seed(3); r = [t[2] for t in base]
bs = sorted(st.mean(random.choices(r, k=len(r))) for _ in range(5000))
print(f"  bootstrap 95% range of the average: {bs[125]*100:+.3f}% .. {bs[4874]*100:+.3f}%")
yrs = {}
for d, m, x in base: yrs.setdefault(d.year, []).append(x)
print("  by year: " + ", ".join(f"{y} {sum(v)*100:+.1f}%({len(v)})" for y, v in sorted(yrs.items())))
