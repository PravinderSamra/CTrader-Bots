"""Weekend gap risk for the Daily Systems bot. (1) History: Friday close -> Monday open gaps (Yahoo daily, cash index
opens; a CFD/futures reopens Sunday evening, so this is an approximation). (2) Bot exposure over weekends from backtest
logs (H| lines): notional held from a Friday into the next week. (3) Scenario: that exposure x historical worst gaps."""
import json, os, sys, statistics as st
from datetime import datetime, timezone
from collections import defaultdict

G = sys.argv[1]
def load(n):
    r = json.load(open(os.path.join(G, n + ".json")))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    out = []
    for t, o, c in zip(r["timestamp"], q["open"], q["close"]):
        if o and c: out.append((datetime.fromtimestamp(t, timezone.utc).date(), o, c))
    return out
names = {"GSPC": "US500", "NDX": "US100", "DJI": "US30", "GDAXI": "GER40", "GC=F": "Gold"}
gaps = {}
for f, nm in names.items():
    d = load(f); g = []
    same = sum(1 for i in range(1, len(d)) if abs(d[i][1] / d[i - 1][2] - 1) < 1e-6) / len(d)
    for i in range(1, len(d)):
        if d[i][0].weekday() == 0 and d[i - 1][0].weekday() == 4 and d[i][0].year >= 1990:
            g.append((d[i][0], 100 * (d[i][1] / d[i - 1][2] - 1)))
    gaps[nm] = dict(g)
    v = [x for _, x in g]; yrs = (g[-1][0] - g[0][0]).days / 365.25
    print(f"{nm:6s} {g[0][0].year}-{g[-1][0].year} weekends {len(v)} (open==prev close {same:.0%} of days) | "
          f"gap down >=2%: {sum(x <= -2 for x in v)}  >=3%: {sum(x <= -3 for x in v)}  >=5%: {sum(x <= -5 for x in v)}  "
          f">=7%: {sum(x <= -7 for x in v)} | worst: " + ", ".join(f"{a} {x:+.1f}%" for a, x in sorted(g, key=lambda z: z[1])[:4]))

def exposure(log):
    pos = []
    for l in open(log):
        if "| H|" in l:
            p = l.split("| H|")[1].split("|")
            sym = p[2].split(".")[0].replace("XAUUSD", "Gold")
            e = datetime.strptime(p[3], "%Y-%m-%d").date(); x = datetime.strptime(p[4], "%Y-%m-%d").date()
            pos.append((sym, e, x, float(p[5]) * float(p[6]) * (1.106 if sym == "GER40" else 1)))
    fr = defaultdict(lambda: defaultdict(float))
    for sym, e, x, n in pos:
        d = e
        while d < x:
            if d.weekday() == 4 and (x - d).days >= 3: fr[d][sym] += n
            d = d.fromordinal(d.toordinal() + 1)
    return fr

for lab, log in (("2020-23 (v1.3 hold)", sys.argv[2]), ("2024-26 (v1.1 final test)", sys.argv[3])):
    fr = exposure(log)
    tot = sorted(sum(v.values()) for v in fr.values())
    nweeks = len({d for d in fr})
    print(f"\n{lab}: weekends with positions held {nweeks}; notional held over the weekend: median ${st.median(tot):,.0f}, "
          f"90th pct ${tot[int(.9*len(tot))]:,.0f}, max ${tot[-1]:,.0f}")
    # replay: actual weekend gap loss on the positions held (using cash-index gaps of that weekend)
    res = []
    for fri, v in fr.items():
        mon = fri.fromordinal(fri.toordinal() + 3)
        loss = sum(n * gaps[s].get(mon, 0) / 100 for s, n in v.items())
        res.append((loss, fri))
    res.sort()
    print("  worst actual Monday-gap results on positions held: " + ", ".join(f"{d} ${l:,.0f}" for l, d in res[:5]))
    mx = tot[-1]
    print(f"  stress: max exposure ${mx:,.0f} hit by a uniform gap of -3% = ${-0.03*mx:,.0f}, -5% = ${-0.05*mx:,.0f}, -7% = ${-0.07*mx:,.0f}, -10% = ${-0.10*mx:,.0f}")
