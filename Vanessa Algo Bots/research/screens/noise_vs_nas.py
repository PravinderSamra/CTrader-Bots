"""Noise band (US100) vs the live NAS bot, same dates (2021-01-04 .. 2026-07-02), equal risk.
NAS bot: daily R from data/nas_bot_daily_R_2021_2026.json x $500. Noise band: daily % x notional, notional chosen so its
daily volatility equals the NAS bot's. Also a 50/50 half-size mix."""
import json, math, statistics as st
from datetime import date, timedelta
R = json.load(open("data/nas_bot_daily_R_2021_2026.json"))
NB = json.load(open("/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad/nb_us100.json"))
d, end = date(2021, 1, 4), date(2026, 7, 2); days = []
while d <= end:
    if d.weekday() < 5: days.append(str(d))
    d += timedelta(days=1)
nas = [float(R.get(k, 0)) * 500 for k in days]
nbp = [float(NB.get(k, 0)) for k in days]
N = st.pstdev(nas) / st.pstdev(nbp); noise = [x * N for x in nbp]
mix = [(a + b) / 2 for a, b in zip(nas, noise)]
def stats(name, s):
    eq = pk = dd = 0; worst5 = min(sum(s[i:i+5]) for i in range(len(s)-5))
    for x in s: eq += x; pk = max(pk, eq); dd = max(dd, pk - eq)
    yrs = {}
    for k, x in zip(days, s): yrs[k[:4]] = yrs.get(k[:4], 0) + x
    mo = {}
    for k, x in zip(days, s): mo[k[:7]] = mo.get(k[:7], 0) + x
    sh = st.mean(s) / st.pstdev(s) * math.sqrt(252)
    print(f"{name:28s} total ${sum(s):9,.0f}  ${sum(s)/5.5:7,.0f}/yr  Sharpe {sh:4.2f}  max DD ${dd:7,.0f}  "
          f"worst day ${min(s):7,.0f}  worst week ${worst5:7,.0f}  months up {sum(v>0 for v in mo.values())/len(mo):.0%}")
    print("   " + "  ".join(f"{y} ${v:8,.0f}" for y, v in sorted(yrs.items())))
print(f"noise band notional for equal risk: ${N:,.0f} (live NAS risk $500/R)\n")
stats("NAS bot (live rules, $500/R)", nas); stats("Noise band US100 (equal risk)", noise); stats("50/50 mix (each half size)", mix)
a, b = nas, noise; ma, mb = st.mean(a), st.mean(b)
print(f"\ncorrelation {sum((x-ma)*(y-mb) for x,y in zip(a,b))/len(a)/(st.pstdev(a)*st.pstdev(b)):+.2f}")
