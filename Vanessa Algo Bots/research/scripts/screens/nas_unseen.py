"""Pre-registered 14 Oct 2026: the two NAS watch-list models on UNSEEN NAS100 m5 data, Jul 2020 - Jun 2023
(downloaded to US30 London Range Breakout/data/NAS100_2020_2023). Code unchanged from the original screens.
PASS: Omar/NBB with weekly+daily bias: mean of the 4 versions >= +0.10R and >= 3 of 4 positive.
      Kane TradeZella version (kane_tz): >= +0.10R."""
import statistics as st
from datetime import datetime, timezone
import rajan_jade as rj
import omar as om

F = "NAS100_2020_2023/nas100_m5_2020_2023.csv"
LO, HI = datetime(2020, 7, 1, tzinfo=timezone.utc), datetime(2023, 7, 1, tzinfo=timezone.utc)
cut = lambda tr: sorted(t for t in tr if LO <= t[0] < HI)

bars = rj.load(F)
print(f"NAS100 m5 {bars[0][0]:%Y-%m-%d} .. {bars[-1][0]:%Y-%m-%d}, {len(bars)} bars; trades counted {LO:%Y-%m} .. {HI:%Y-%m}")
b15 = om.m15(bars); ib = om.inv(b15); avgs = []
for f in (0.62, 0.705):
    for sl in (0.9, 1.0):
        tr = cut(om.run(b15, 1.5, "both", f, sl) + om.run(ib, 1.5, "both", f, sl))
        avgs.append(st.mean(r for _, r in tr) if tr else 0)
        rj.summ(f"Omar/NBB both-bias f={f} stop={sl}", tr)
print(f"  -> Omar mean of 4 = {st.mean(avgs):+.3f}R, positive {sum(a > 0 for a in avgs)}/4")
for f in (0.62, 0.705):
    rj.summ(f"Omar/NBB no bias f={f} stop=1.0 (ref)", cut(om.run(b15, 1.5, "none", f, 1.0) + om.run(ib, 1.5, "none", f, 1.0)))
rj.summ("Kane TZ (pre-registered)", cut(rj.kane_tz(bars, 1.5)))
rj.summ("Kane old version (ref)", cut(rj.kane(bars, 1.5, False)))
