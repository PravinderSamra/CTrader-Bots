# Ideas backlog (second-bot search)

Live: NAS100 London Range (v3.2 Auto Ladder). Goal: a second, ideally uncorrelated, bot that survives FTMO costs.
Filter for new ideas: intraday, flat before 20:59 UK (swap), big moves relative to the spread, different market or time of
day from NAS100 at 10:00 NY, mechanical rules. Non-USD symbols carry FTMO's 0.70% P&L conversion fee.

## Maybes (only if nothing better turns up), in order
| Idea | Source | Status | Next step if revived |
|---|---|---|---|
| **1. ICT London sweep + inversion FVG (NAS100, 02:00-05:00 NY = 07:00-10:00 UK)**: after Asia (20:00-00:00 NY) high/low is swept, enter when a 5-min close inverts a fair value gap the other way; stop beyond the sweep extreme (skip if > 25 pts), target 2-3R, flat by 07:00 NY | Candace Lau, Chart Fanatics | **Re-checked with the real spread (12 Oct): thin.** FTMO US100 spread 07:00-10:00 UK is ~1.75 pts (data/spreads). At 1.8 pts: 2R negative (-0.02 to -0.04R), 3R +0.04 to +0.05R, mostly from 2025 (2023 and 2024 about flat); at 2.3 pts 3R is ~+0.01R. Not worth building unless a sharper entry (1-min) is tested. Earlier: rough m5 screen 2023-26 (3 variants tried): +0.07R (2R) to +0.14R (3R) per trade, ~140 trades a year, positive every year at the 25-pt cap; correlation with the NAS bot +0.02 to +0.06 (different hours). Sensitive to spread: 2R breaks even at ~1.7 pts, 3R stays positive at 2 pts | Other indices (same rules, stop cap 0.12% of price, estimated spreads US30 2.0 / GER40 1.2 / UK100 1.0, 0.7% fee on non-USD): US30 -0.05 to -0.09R, GER40 -0.08 to -0.18R (negative even before costs), UK100 -0.07 to +0.01R, so NAS100-only. With the % cap, NAS100 2R turned negative in 2024 and 2026 (fragile); 3R stayed positive every year (+0.12R). Spread checked (~1.75 pts). Next: write rules on 1-min candles first; cBot; Vanessa tunes 2021-23 on tick data, tests 2024-26 once (3R pre-registered) |
| 2. Gold pullback to an untapped open (London/NY/daily), two broken 5-min swings, 1:2 RR | Claudia, Prop Firm Trader | Not tested; her full method is discretionary, this is the codeable core | Write rules first, build cBot, Vanessa backtests on tick data |

## Closed
| Idea | Why | Where |
|---|---|---|
| Drift VWAP Pullback (Matteo Conti) | 63% win but ~+2.2 pts/trade before costs; real NY spread ~1.2 pts leaves ~+1 pt; correlation +0.39 with the NAS bot | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| Overnight drift (NAS100, GER40, US30, UK100, JP225) | Real, but FTMO swap plus gap risk vs the daily limit and floor | results/OVERNIGHT_DRIFT_TEST.md |
| First 30 min predicts last 30 min (with or without gamma) | No edge 2023-26; pre-registered 2021-23 gamma test failed | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| VWAP trend (QQQ paper) | Spread on ~8 trades a day exceeds the edge | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| Post-earnings drift | Small caps not on FTMO; 60 days of swap | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| US500 London Range | Thin edge, losing days coincide with NAS100 | results/COMBINED_NAS100_US500.md |
| Bitcoin London Range | FTMO crypto commission takes ~85% of the edge | ORB_OTHER_MARKETS_TEST_PLAN.md |
| Gold London Range | Worked 2021-23, failed 2024-26 | ORB_OTHER_MARKETS_TEST_PLAN.md |
| Silver | Spread too large | ORB_OTHER_MARKETS_TEST_PLAN.md |
| NAS100 15/30-min opening range | Both failed | NAS100 test notes |
| JJ Simon "fair pricing": revert to the 9:30 open on displacement candles, SL 25 / TP 38, stop after 3 losses | NAS100 m5 screen 2023-26: 34-40% win, -1,028 to -1,941 pts in every version, lost every full year; his edge is prop-firm economics (45 cheap futures evals, ~$400k spent), not the signal | this file |

## Parked improvements to the live NAS bot (Vanessa: leave the live bot as is for now)
| Idea | Evidence | If revived |
|---|---|---|
| Skip the day after a calm NY session (previous range < 0.877% of price) | Pre-registered 2021-23 test passed narrowly: -0.20R (49 days); 2023-26 -0.11R (80 days) | New bot version with a switch (default off), full 2021-26 tick-data run on vs off. See NAS100_VOL_REGIME_TEST_PLAN.md |
