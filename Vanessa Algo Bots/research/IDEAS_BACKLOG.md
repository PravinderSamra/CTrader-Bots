# Ideas backlog (second-bot search)

Live: NAS100 London Range (v3.2 Auto Ladder). Goal: a second, ideally uncorrelated, bot that survives FTMO costs.
Filter for new ideas: intraday, flat before 20:59 UK (swap), big moves relative to the spread, different market or time of
day from NAS100 at 10:00 NY, mechanical rules. Non-USD symbols carry FTMO's 0.70% P&L conversion fee.

## Maybes (only if nothing better turns up)
| Idea | Source | Status | Next step if revived |
|---|---|---|---|
| Drift VWAP Pullback (NAS100, 10:30-15:55 NY) | Matteo Conti, Chart Fanatics | Screened: 63% win, +1.5 pts/trade after spread, positive every year; thin edge, correlation +0.39 with the NAS bot | cBot + cTrader tick-data test to measure real slippage |
| Gold pullback to an untapped open (London/NY/daily), two broken 5-min swings, 1:2 RR | Claudia, Prop Firm Trader | Not tested; her full method is discretionary, this is the codeable core | Write rules first, build cBot, Vanessa backtests on tick data |

## Closed
| Idea | Why | Where |
|---|---|---|
| Overnight drift (NAS100, GER40, US30, UK100, JP225) | Real, but FTMO swap plus gap risk vs the daily limit and floor | results/OVERNIGHT_DRIFT_TEST.md |
| First 30 min predicts last 30 min (with or without gamma) | No edge 2023-26; pre-registered 2021-23 gamma test failed | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| VWAP trend (QQQ paper) | Spread on ~8 trades a day exceeds the edge | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| Post-earnings drift | Small caps not on FTMO; 60 days of swap | results/PODCAST_MATTEO_CONTI_IDEAS.md |
| US500 London Range | Thin edge, losing days coincide with NAS100 | results/COMBINED_NAS100_US500.md |
| Bitcoin London Range | FTMO crypto commission takes ~85% of the edge | ORB_OTHER_MARKETS_TEST_PLAN.md |
| Gold London Range | Worked 2021-23, failed 2024-26 | ORB_OTHER_MARKETS_TEST_PLAN.md |
| Silver | Spread too large | ORB_OTHER_MARKETS_TEST_PLAN.md |
| NAS100 15/30-min opening range | Both failed | NAS100 test notes |
