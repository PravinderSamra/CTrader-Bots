# EURUSD flow-timing tests (pre-registered 28 Oct 2026, before any code was run on these windows)
Why these two: EURUSD is FTMO's cheapest market (spread ~0.1% of the daily range), but the obvious intraday ideas are
already closed (London-open breakout, 4pm fix reversal, noise band, FX trend, Omar/Mayne/TG/Ali Crooks/Trading Cafe
setups). What has NOT been tried is trading predictable *flows* on known dates rather than chart patterns.

Data: cTrader FTMO EURUSD H1 (data/eurusd_h1.csv, 2012-26); US500 and EU50 daily closes (data/factory_d1, EU50 from
2014-07). FOMC dates: ssrn/fomc_drift.py (scheduled meetings 2014-2026). Whole period counts as unseen: no tuning,
one rule per idea, decided now. Costs: 1.0 bp a round trip (spread + $5/lot commission), stress 2.0 bp; one night of
long-EURUSD swap (-3.27%/yr = 0.9 bp) where a position is held over 17:00 New York.

## M1 Month-end equity rebalancing (Melvin & Prins 2015, J. Int. Money & Finance)
Foreign holders of US shares hedge their dollars; when US shares beat European shares over the month, they sell
dollars into the month-end London 4pm fix. Rule: on the last US trading day of each month, compare month-to-date
returns (to the previous day's close) of US500 and EU50. US500 ahead -> buy EURUSD; behind -> sell. In at 08:00 UK,
out at 16:00 UK. About 12 trades a year, Aug 2014 - Sep 2026.

## F1 / F2 Dollar around FOMC (Mueller, Tahbaz-Salehi & Vedolin 2017, J. Finance: foreign currencies tend to gain
against the dollar on FOMC days)
F1 pre-announcement: buy EURUSD 14:00 NY on meeting day 1 -> 14:00 NY on announcement day (same window as the live
FOMC bot). F2 full day: buy EURUSD 16:00 NY on day 1 -> 16:00 NY on announcement day. 8 trades a year, 2014-2026.

## Pass (each of M1, F1, F2; three trials in total)
Average >= +2 bp a trade after the 1 bp cost (and swap), t >= 2.0, positive after costs in both 2014-2019 and
2020-2026, at least 60% of calendar years positive, still positive at the 2 bp stress cost. F1/F2 must also show
daily correlation below 0.5 with the live FOMC bot's index trade (US100 long, same window) to add anything.

## Result (28 Oct 2026, screens/eurusd_flows.py, results/EURUSD_FLOWS.txt): all three FAIL
- M1 month-end: 145 trades, -0.2 bp after costs (gross +0.8), t -0.07, 6/13 years up; +2.0 bp 2014-19, -2.0 bp 2020-26.
- F1 pre-FOMC: 101 trades, +3.8 bp (gross +5.7), t 1.03, 7/13 years up. Right sign in both halves but far too noisy
  to tell from luck; correlation +0.19 with the US100 FOMC trade.
- F2 FOMC day: +2.3 bp, t 0.62, 8/13 years up; correlation +0.30.
No changes will be tried on these data. EURUSD closed as a bot market for now.
