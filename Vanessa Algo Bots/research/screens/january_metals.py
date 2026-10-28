"""January effect on silver and copper (pre-registered 28 Oct 2026, after gold's pass, before running these).
Same rule and pass test as gold (screens/gold_seasonal.py): long from the first January session open to the last
January session close; costs 0.03% (wider spreads) + 5%/yr swap. FTMO daily data (factory_d1), 2014/15-2026.
Pass: avg after costs > 0, >= 0.5% better than the other months (raw), >= 60% of years up, both halves positive."""
import sys, statistics as st
sys.path.insert(0, "factory"); import factory_d1 as F
from collections import defaultdict
for m in ("xagusd", "copper"):
    d, o, h, l, c = F.load(m); mon = defaultdict(list)
    for i, x in enumerate(d): mon[(x.year, x.month)].append(i)
    ret = {}
    for (y, mm), I in mon.items():
        if len(I) < 15: continue
        raw = c[I[-1]] / o[I[0]] - 1; ret[(y, mm)] = (raw, raw - 0.0003 - 0.05 / 365 * (d[I[-1]] - d[I[0]]).days)
    jan = [(y, net) for (y, mm), (raw, net) in ret.items() if mm == 1]
    rawj = [raw for (y, mm), (raw, net) in ret.items() if mm == 1]; oth = [raw for (y, mm), (raw, net) in ret.items() if mm != 1]
    nets = [x for _, x in jan]; mid = sorted(y for y, _ in jan)[len(jan) // 2]
    h1 = [x for y, x in jan if y < mid]; h2 = [x for y, x in jan if y >= mid]
    ok = st.mean(nets) > 0 and st.mean(rawj) - st.mean(oth) >= 0.005 and sum(x > 0 for x in nets) / len(nets) >= 0.6 and st.mean(h1) > 0 and st.mean(h2) > 0
    t = st.mean(nets) / (st.pstdev(nets) / len(nets) ** .5)
    print(f"{m}: {len(nets)} Januaries, avg after costs {st.mean(nets)*100:+.2f}% (raw {st.mean(rawj)*100:+.2f}% vs other months {st.mean(oth)*100:+.2f}%) "
          f"t={t:.1f} up {sum(x>0 for x in nets)}/{len(nets)}  halves {st.mean(h1)*100:+.2f}% / {st.mean(h2)*100:+.2f}%" + ("  PASS" if ok else "  fail"))
    print("   " + " ".join(f"{y}:{x*100:+.1f}%" for y, x in sorted(jan)))
