# Noise band (US100) test plan

## Band width (27 Oct 2026; prompted by a quant_labde post: "widening the band mattered most", no multiplier given)
Band = K x the published 14-day average move. FTMO 5-minute US100, Jun 2020 - Jul 2026, 0.01% cost (screens/noise_band.py, NB_K):
| K | Net at 1x | Sharpe | Max DD | Trades | After Mar 2024 |
|---|---|---|---|---|---|
| 0.75 | +56.2% | 0.91 | 17.5% | 1,895 | +5.3% |
| 1.0 (published) | +62.0% | 1.18 | 8.1% | 1,480 | +19.4% |
| 1.25 | +58.9% | 1.22 | 6.0% | 1,142 | +19.7% |
| 1.5 | +38.4% | 0.97 | 9.2% | 905 | +10.2% |
| 2.0 | +9.2% | 0.31 | 9.3% | 540 | +9.0% |
| 2.5 | +11.3% | 0.50 | 3.4% | 280 | +7.1% |
A little wider (1.25) is slightly smoother; much wider is clearly worse. Not a "significant" improvement on this data.

## Pre-registered unseen test (written before the 2012-2020 Dukascopy data finished downloading)
Dukascopy USATECHIDXUSD minute data 2012-01 .. 2020-06, rebuilt into 5-minute bars, same rules, 0.01% cost.
Run exactly two versions: K = 1.0 and K = 1.25. Each passes if Sharpe >= 0.8 and at least 6 of the 8 full years
(2012-2019) are positive. K = 1.25 is preferred only if it passes AND its Sharpe is not lower than K = 1.0's.

## RESULT of the unseen test (28 Oct 2026; Dukascopy USATECHIDXUSD, 2,194 of 2,217 days, 2012-02 .. 2020-06)
| | K = 1.0 (published) | K = 1.25 (wider) |
|---|---|---|
| Net at 1x | +32.6% | +38.3% |
| Sharpe | 0.55 | 0.74 |
| Max drawdown | 17.5% | 12.4% |
| Positive years 2012-2019 | 6 of 8 | 7 of 8 |
| By year | 2012 +8.1, 2013 -2.6, 2014 +5.8, 2015 +1.9, 2016 -0.7, 2017 +2.0, 2018 +26.1, 2019 +0.5, 2020H1 -8.6 | 2012 +8.1, 2013 +0.8, 2014 +4.8, 2015 +4.4, 2016 -1.8, 2017 +1.2, 2018 +23.6, 2019 +0.8, 2020H1 -3.6 |
BOTH FAIL the pre-registered Sharpe >= 0.8. Most of the profit is 2018; without it ~1-2% a year. The wider band is better
on both periods (supports the quant_labde claim in direction, not size). Verdict: the edge is strong only in 2020-2026;
not robust enough to trade on its own. Demoted from 'parked for a future account' to 'watch list' (re-test with live data).
