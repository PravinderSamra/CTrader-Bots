# Chart Fanatics: Matteo Conti's four research-paper ideas (checked 12 Oct 2026)

Quick first looks on NAS100 m5 (cTrader, July 2023 to July 2026), FTMO costs (spread 0.65 points, no commission,
no swap if flat before 20:59 UK). These are screening checks, not full pre-registered tests.

| Idea (paper) | Check | Result | Verdict |
|---|---|---|---|
| 1. Market intraday momentum (2018): overnight gap + first 30 min predicts the last 30 min | Signal = prev 16:00 close to 10:00; trade 15:30-15:55 in that direction | Correlation -0.01. Long+short -506 pts over 739 days; long-only +0.9 pts/trade vs +1.1 for always long | No edge left on NAS100 |
| 1b. His version: 30-min opening range breakout | Tested earlier on NAS100 (15 and 30 min ranges) | Both failed | Already closed; our London Range (02:00-09:30) is the version that works |
| 2. VWAP trend (industry paper, QQQ 1-min) | Long above session VWAP, short below, flip on cross, flat 15:55; tick volume as volume | Long+short -2,750 pts (7.8 trades/day); long-only -735 pts. Profitable only in 2025 | Not viable on the CFD at m5; costs of ~5 pts/day exceed the gross edge |
| 3. Post-earnings drift (small/mid caps, 60-day holds) | Not tested | FTMO has no small caps; 60 days of swap at ~8%/yr is ~1.3% a trade; no edge on mega caps per his own source | Not suitable for FTMO |
| 4. Overnight drift | See OVERNIGHT_DRIFT_TEST.md | Real, but swap and gap risk | Closed |

Useful takeaways: his pipeline (rules first, in-sample/out-of-sample, Monte Carlo, automate, monitor) is what this
project already does; risk a fixed amount per trade (the NAS bot already does); build a portfolio of uncorrelated bots.
