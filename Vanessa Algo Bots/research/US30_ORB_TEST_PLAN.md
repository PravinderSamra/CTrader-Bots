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
