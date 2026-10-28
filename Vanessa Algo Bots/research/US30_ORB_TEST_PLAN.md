# US30 opening-range breakout: unseen test (pre-registered 28 Oct 2026, before downloading the data)
Source: US30 London Range Breakout study (2023-07..2026-07 FTMO M5), best US30 structure: range 08:00-09:30 NY,
entries 10:00-13:00 NY on the first M5 close beyond the range with volume >= 1.2x the 20-bar average, one trade a day,
flat at 16:00 NY. Its daily results correlated only 0.07 with the NAS100 version.
Unseen data: Dukascopy USA30IDXUSD minute data 2013-01 .. 2023-06 (5-minute bars), costs 0.01% a round trip.
Exactly two versions:
 A: stop = 2.0 x ATR(14) of M5 bars at entry, target 2.0R.
 B: stop = 75 points scaled to price (75 x price / 34,000), target 3.0R.
Each passes if: profit factor >= 1.15, at least 6 of the 10 full years (2013-2022) positive, max drawdown <= 25R, and
daily correlation with the NAS bot replica (screens/nas_bot_replica.py, same years) below 0.4.

## Engine note and calibration (28 Oct 2026, before the unseen data arrived)
Uses the study's own engine (screens/orb_engine.py = copy of scripts/backtest.py + a price-scaled stop), which
reproduces the study exactly (fixed 75/3R +116.7R PF 1.31; ATR2/2R +81.5R PF 1.23, no costs). With 0.01% costs on the
SAME 2023-26 data: A +49.9R PF 1.13 (DD 23.6R), B (scaled stop) +50.2R PF 1.14 (DD 21.7R); 2024 negative in both.
So even in-sample, after costs, both sit just under the 1.15 pass bar. Runner: screens/us30_orb_unseen.py.

## Unseen result (28 Oct 2026): FAIL
Data: FTMO/cTrader US30 M5 2020-06 .. 2023-06 (same feed as the study, period the study never saw). Dukascopy 2013-19
download stopped: the result below already breaks the drawdown bar, so more years cannot turn it into a pass.
- A (ATR x2, 2R): 702 trades, -15.7R, PF 0.97, max DD 61.3R | 2020 +22.7, 2021 -16.6, 2022 -18.8, 2023H1 -3.1
- B (scaled 75 pts, 3R): 702 trades, -18.4R, PF 0.96, max DD 68.7R | 2020 +31.4, 2021 -18.9, 2022 -31.3, 2023H1 +0.4
- Before costs: both +13 to +15R, PF 1.03 - the edge is roughly the size of the spread.
The 1.13/1.14 in-sample was the best of the study's search; on fresh data it falls to break-even before costs. Not built.
Correlation check not needed (fails on PF and DD first).
