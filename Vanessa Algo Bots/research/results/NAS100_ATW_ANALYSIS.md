# Add To Winner — NAS100 analysis

Runs: CONTROL_rebuilt, NB_0.7_x1, NC_0.7_x2. First run is the control. Figures at the backtest risk ($300).

## Totals

| Run | Positions | Net profit | vs control | Profit from adds | Max balance DD | Worst day |
|---|---|---|---|---|---|---|
| CONTROL_rebuilt | 634 | $32,077.77 | +0.0% | $0.00 | 4.33% | $-415.43 (-0.42%) |
| NB_0.7_x1 | 1005 | $37,337.11 | +16.4% | $5,259.34 | 5.14% | $-415.43 (-0.42%) |
| NC_0.7_x2 | 1005 | $42,609.40 | +32.8% | $10,531.63 | 5.96% | $-495.92 (-0.50%) |

Check: control net $32,077.77; main trades only from the last run $32,077.77.

## Profit by year

| Year | CONTROL_rebuilt | NB_0.7_x1 | NC_0.7_x2 |
|---|---|---|---|
| 2021 | $4,318 | $5,312 | $6,309 |
| 2022 | $9,272 | $10,451 | $11,634 |
| 2023 | $3,996 | $4,564 | $5,133 |
| 2024 | $4,504 | $4,875 | $5,246 |
| 2025 | $4,706 | $5,464 | $6,224 |
| 2026 | $5,282 | $6,671 | $8,063 |
| **Years better than control** | – | 6 / 6 | 6 / 6 |
| **Worst year vs control** | – | $372 | $742 |

## Days (main trade + add counted as one result)

| Run | Trading days | Winning days | Win rate | Losses per win | Longest losing run | Runs of 4+ | Runs of 6+ | Costliest losing run |
|---|---|---|---|---|---|---|---|---|
| CONTROL_rebuilt | 634 | 230 | 36% | 1.76 | 11 | 33 | 16 | $4,334 |
| NB_0.7_x1 | 634 | 228 | 36% | 1.78 | 11 | 34 | 17 | $5,145 |
| NC_0.7_x2 | 634 | 227 | 36% | 1.79 | 11 | 34 | 17 | $5,960 |

## Month of year (control): is any month reliably worse?

| Month | Days | Net | Avg per day | t vs overall average |
|---|---|---|---|---|
| 01 | 57 | $49 | $1 | -0.78 |
| 02 | 48 | $5,022 | $105 | +0.78 |
| 03 | 58 | $2,027 | $35 | -0.25 |
| 04 | 45 | $8,754 | $195 | +2.00 |
| 05 | 56 | $3,413 | $61 | +0.16 |
| 06 | 57 | $-514 | $-9 | -0.93 |
| 07 | 59 | $5,082 | $86 | +0.57 |
| 08 | 60 | $1,174 | $20 | -0.50 |
| 09 | 45 | $125 | $3 | -0.67 |
| 10 | 46 | $-165 | $-4 | -0.76 |
| 11 | 55 | $341 | $6 | -0.68 |
| 12 | 48 | $6,770 | $141 | +1.30 |

|t| above ~2 would suggest a real seasonal effect; with 12 months tested, one reaching ~2 by chance is expected.

## Chance of hitting FTMO's $90,000 floor from today's balance ($96,952.19)

Resampled from each run's real daily results in blocks of 10 consecutive trading days, so losing streaks stay intact (5,000 simulated futures). ~21 trading days a month.

| Run | Risk | 3 months | 6 months | 12 months |
|---|---|---|---|---|
| CONTROL_rebuilt | $300 | 0.0% | 0.1% | 0.8% |
| CONTROL_rebuilt | $500 | 0.6% | 3.0% | 6.4% |
| NB_0.7_x1 | $300 | 0.0% | 0.4% | 1.4% |
| NB_0.7_x1 | $500 | 1.6% | 5.0% | 9.2% |
| NC_0.7_x2 | $300 | 0.1% | 0.8% | 2.6% |
| NC_0.7_x2 | $500 | 3.0% | 7.8% | 12.7% |

## Chance of a drawdown of 6% / 8% / 10% within 12 months (from a fresh $100,000)

| Run | Risk | 6% | 8% | 10% |
|---|---|---|---|---|
| CONTROL_rebuilt | $300 | 5.1% | 0.9% | 0.2% |
| CONTROL_rebuilt | $500 | 38.2% | 14.6% | 5.1% |
| NB_0.7_x1 | $300 | 10.2% | 2.3% | 0.5% |
| NB_0.7_x1 | $500 | 51.7% | 23.5% | 10.2% |
| NC_0.7_x2 | $300 | 16.6% | 4.4% | 1.2% |
| NC_0.7_x2 | $500 | 64.4% | 34.1% | 16.6% |
