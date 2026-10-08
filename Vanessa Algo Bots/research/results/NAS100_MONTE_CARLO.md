# NAS100 bot: Monte Carlo test

Live settings (size 5, trigger 0.7, TP 4.5R, trailing from 2.5R, step 0.1, +33% ladder, 4-loss rule). Source: the real cTrader ladder log 2021-01-01 .. 2026-09-28: 634 trading days (227 winning, 36%), about 9.2 trading days a month. Each day is converted to R using the risk the bot actually used that day. 10,000 simulations per test. Starting balance $98,073.77. The log includes a small commission (30 per million), so it is slightly conservative against FTMO's $0 index commission.

Average day +0.35R; best day +8.57R; worst day -2.68R.

## A. Was the backtest's order of days lucky?

The same days reshuffled into random orders, at a fixed risk.

| | Actual backtest | Typical | Bad (1 in 20) | Very bad (1 in 100) |
|---|---|---|---|---|
| Worst drawdown | 28.1R | 33.3R | 52.1R | 63.5R |
| Longest run of losing days | 11 | 13 | 18 | 22 |

## B. The next 12 months from $98,074 (about 110 trading days, ladder on, no target)

| Scenario | Method | Typical profit | Bad year (1 in 10) | Very bad (1 in 20) | Chance of a losing year | Typical worst drawdown | Bad drawdown (1 in 20) | Longest losing run (1 in 20) | Chance of hitting $90k |
|---|---|---|---|---|---|---|---|---|---|
| Backtest as is | 10-day blocks | $+15,435 | $-5,922 | $-8,197 | 25.1% | 11.6% | 20.7% | 13 days | 8.08% |
| Backtest as is | single days | $+18,078 | $-8,084 | $-8,245 | 24.6% | 12.1% | 22.5% | 14 days | 10.27% |
| Winning days 10% smaller | 10-day blocks | $+4,140 | $-8,157 | $-8,286 | 38.9% | 11.3% | 20.3% | 13 days | 13.80% |
| Winning days 10% smaller | single days | $+5,262 | $-8,192 | $-8,316 | 37.0% | 11.7% | 21.9% | 14 days | 15.98% |
| Winning days 20% smaller | 10-day blocks | $-1,976 | $-8,270 | $-8,392 | 57.5% | 10.7% | 19.7% | 13 days | 23.70% |
| Winning days 20% smaller | single days | $-1,591 | $-8,278 | $-8,412 | 55.2% | 11.2% | 21.0% | 14 days | 25.40% |

Worst single day in all the 12-month simulations: -$3,618. Days at or beyond FTMO's $5,000 daily loss limit: 0. (Closing balances only; a trade's open loss is capped by its stop.)

## C. The FTMO journey from $98,074: phase 1 to $110k, then phase 2 $100k to $105k

| Scenario | Method | Pass phase 1 | Reach funded | Fast (1 in 4) | Typical time | Slow (1 in 4) |
|---|---|---|---|---|---|---|
| Backtest as is | 10-day blocks | 87.8% | **82.7%** | 4.8 mo | **8.6 mo** | 14.7 mo |
| Backtest as is | single days | 86.1% | **79.8%** | 4.5 mo | **7.8 mo** | 13.1 mo |
| Winning days 10% smaller | 10-day blocks | 75.8% | **66.1%** | 6.0 mo | **10.9 mo** | 18.6 mo |
| Winning days 10% smaller | single days | 75.9% | **65.8%** | 5.3 mo | **9.5 mo** | 16.3 mo |
| Winning days 20% smaller | 10-day blocks | 53.4% | **39.5%** | 6.4 mo | **11.7 mo** | 20.3 mo |
| Winning days 20% smaller | single days | 57.0% | **43.4%** | 6.0 mo | **10.9 mo** | 18.4 mo |

## What it means
- **The backtest's order of days was slightly kind.** Its worst drawdown (28.1R) and longest losing run (11 days) are both
  better than typical for a random order of the same days (33R and 13 days). Expect deeper dips than the backtest showed: a losing run of
  about 18 days and a drawdown of about 50R are 1-in-20 events.
- **The edge comes from a few big days.** Only 36% of days win, and cutting every winning day by 10% removes about a third
  of the average profit (+0.35R to +0.24R a day); a 20% cut removes about 70% (to +0.10R). Live fills and slippage on
  winning days matter more than anything else, so compare live trades with the backtest every month.
- **The ladder roughly halves the floor risk.** Over 12 months from $98,074 with 10-day blocks: ladder 8.1% chance of
  hitting $90k (typical profit +$15,435); a fixed $550 risk 17.1% (typical profit +$18,241).
- **The daily loss limit is not the danger; the $90k floor is.** No simulated day reached -$5,000 (worst -$3,618).
  The account starts only about 14R above the floor at today's risk, which is where almost all the failure risk sits.
- About 1 in 4 twelve-month stretches from this balance end below the starting balance, even though every calendar
  year of the backtest was profitable (2021 +$18k is the weakest).
