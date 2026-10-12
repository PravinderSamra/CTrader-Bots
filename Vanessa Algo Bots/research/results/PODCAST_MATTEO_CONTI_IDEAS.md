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

## Drift VWAP Pullback (second episode), screened 12 Oct 2026
Rules as stated: VWAP from 9:30 NY on 15-min bars; trend at each 15-min close = price above VWAP, VWAP rising over
15 min, price up >= 0.1% over 1 hour (short = mirror); from 10:30, enter at the next 5-min open after the first
counter-colour 5-min candle; SL 80 pts, TP 40 (long) / 50 (short); max 4 trades a day, stop after 2 losses, no entries
after 15:30, flat 15:55. NAS100 m5, July 2023 - July 2026, tick volume, same-bar SL/TP counted as SL.

| | Trades | Win | Total | Per trade | Max DD |
|---|---|---|---|---|---|
| No costs | 2,227 | 63% | +4,837 pts | +2.17 pts | 1,467 pts |
| FTMO spread 0.65 | 2,227 | 63% | +3,390 pts | +1.52 pts (about 0.02R) | 1,555 pts (about 19R) |

By year after spread: 2023 (half) +64, 2024 +824, 2025 +978, 2026 (half) +1,523 pts. Longs +3,091, shorts +299.
Per trading day +0.057R (sd 1.23R) vs NAS bot +0.321R (sd 2.99R). On days both traded: correlation +0.39,
both lost on 36%.
Verdict: the win rate reproduces (63% vs his 64%) and it made money every year, but the edge per trade is tiny, so one
extra point of slippage per trade would remove two-thirds of it. It also trades NAS100 in the same session as the NAS bot.
A candidate for a proper cTrader tick-data test only if live-like slippage can be checked; not a "golden ticket" on FTMO
(10% target and a static 10% floor, not a cheap futures evaluation with a small target).
