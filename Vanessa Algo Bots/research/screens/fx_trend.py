"""FX trend-following (pre-registered 28 Oct 2026, before any run; classic untuned rules from the CTA literature).
11 FTMO pairs, daily 2010-2026 (data/fx_d1_2010_2026). Each pair long or short:
 F1 12-month momentum: sign of the 252-day return.
 F2 blended momentum: sign of the average of the 1-, 3- and 12-month returns (each as a sign).
 F3 Turtle: long on a close above the 55-day high / short below the 55-day low; exit on the opposite 20-day level.
 F4 50/200 moving-average cross, long or short.
Equal risk per pair: weight = (10% / pair's 60-day annualised volatility) / 11, refreshed monthly (portfolio ~10% vol).
Signals at the close, held from the next day. Costs: 1 bp per unit of position change (spread + FTMO commission) and
today's FTMO swap per pair, long or short (Cost Scanner; AUDJPY/EURGBP assumed -2%/yr both ways).
Pass: portfolio Sharpe >= 0.5 after costs, positive in 2010-17 and 2018-26, >= 60% of years up, >= 6 of 11 pairs positive."""
import csv, math, statistics as st
from datetime import datetime, timezone
from collections import defaultdict
PAIRS = ["eurusd", "gbpusd", "usdjpy", "audusd", "usdcad", "usdchf", "nzdusd", "eurjpy", "gbpjpy", "audjpy", "eurgbp"]
SWAP = {"eurusd": (-3.27, 0.15), "gbpusd": (-1.73, -1.03), "usdjpy": (0.98, -4.74), "audusd": (-1.67, -3.11),
        "usdcad": (0.31, -3.54), "usdchf": (1.45, -7.08), "nzdusd": (-3.37, 0.03), "eurjpy": (0.26, -2.29),
        "gbpjpy": (0.54, -4.08), "audjpy": (-2.0, -2.0), "eurgbp": (-2.0, -2.0)}
data = {}
for p in PAIRS:
    rows = list(csv.DictReader(open(f"data/fx_d1_2010_2026/{p}_d1.csv")))
    data[p] = {datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc).date(): (float(r["high"]), float(r["low"]), float(r["close"])) for r in rows}
days = sorted(set.intersection(*[set(v) for v in data.values()]))
days = [d for d in days if d.weekday() < 5]
def series(p, k): return [data[p][d][k] for d in days]
def signals(rule, H, L, C):
    n = len(C); s = [0] * n; pos = 0
    for i in range(260, n):
        if rule == "F1": s[i] = 1 if C[i] > C[i-252] else -1
        elif rule == "F2": s[i] = 1 if sum((1 if C[i] > C[i-k] else -1) for k in (21, 63, 252)) > 0 else -1
        elif rule == "F4":
            s[i] = 1 if sum(C[i-49:i+1]) / 50 > sum(C[i-199:i+1]) / 200 else -1
        else:
            if pos <= 0 and C[i] > max(H[i-55:i]): pos = 1
            elif pos >= 0 and C[i] < min(L[i-55:i]): pos = -1
            elif pos == 1 and C[i] < min(L[i-20:i]): pos = 0
            elif pos == -1 and C[i] > max(H[i-20:i]): pos = 0
            s[i] = pos
    return s
for rule in ("F1", "F2", "F3", "F4"):
    port = defaultdict(float); bypair = {}
    for p in PAIRS:
        H, L, C = series(p, 0), series(p, 1), series(p, 2); s = signals(rule, H, L, C)
        r = [0] + [C[i] / C[i-1] - 1 for i in range(1, len(C))]
        w = 0; prev = 0; tot = 0
        for i in range(261, len(C)):
            if i == 261 or days[i].month != days[i-1].month:
                vol = st.pstdev(r[i-60:i]) * math.sqrt(252); w = (0.10 / vol) / len(PAIRS) if vol else 0
            pos = w * s[i-1]
            x = pos * r[i] - abs(pos - prev) * 0.0001
            sw = SWAP[p][0] if pos > 0 else SWAP[p][1]
            x += abs(pos) * sw / 100 * (days[i] - days[i-1]).days / 365
            port[days[i]] += x; tot += x; prev = pos
        bypair[p] = tot
    ks = sorted(port); v = [port[k] for k in ks]
    sh = st.mean(v) / st.pstdev(v) * math.sqrt(252); eq = pk = dd = 0
    for x in v: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    yrs = defaultdict(float)
    for k in ks: yrs[k.year] += port[k]
    a = sum(port[k] for k in ks if k.year <= 2017); b = sum(port[k] for k in ks if k.year >= 2018)
    up = sum(x > 0 for x in yrs.values()) / len(yrs); pp = sum(x > 0 for x in bypair.values())
    ok = sh >= 0.5 and a > 0 and b > 0 and up >= 0.6 and pp >= 6
    print(f"{rule}: Sharpe {sh:.2f}  {sum(v)/len(v)*252*100:+.1f}%/yr  max DD {dd*100:.1f}%  2011-17 {a*100:+.0f}%  2018-26 {b*100:+.0f}%  "
          f"years up {sum(x>0 for x in yrs.values())}/{len(yrs)}  pairs up {pp}/11" + ("  PASS" if ok else "  fail"))
    print("    years: " + " ".join(f"{y}:{x*100:+.0f}" for y, x in sorted(yrs.items())))
    print("    pairs: " + " ".join(f"{p}:{x*100:+.0f}" for p, x in bypair.items()))
