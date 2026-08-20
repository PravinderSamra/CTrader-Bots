# US500 15m ORB — analysis of the 2022-2026 backtest logs

Source: cTrader backtest logs, US500.cash, m5, 01/01/2022 - 20/08/2026.
Entry on a candle closing 10 points outside the 15-minute opening range.
BE at 1.2R with dynamic step at 1R; risk reduction to 37% at 0.74R.
Fixed $100 risk per trade on a $100,000 balance.

## Configuration comparison (1,099 trades, identical entries)

| | 20R target | 3R target |
|---|---|---|
| Net profit | $8,019 | $7,862 |
| Expectancy | +0.0731R | +0.0716R |
| Win rate | 49.7% | 49.7% |
| Profit factor | 1.184 | 1.181 |
| **Max drawdown** | 17.0R | **14.4R** |
| **Top 10 trades as % of profit** | 58% | **38%** |
| Strip top 20 trades | +0.3R | **+18.7R** |

3R gives up 2% of profit for a 15% smaller drawdown and far less outlier
dependence. 2024 improves from $736 to $1,204; 2022 gives back $523.
**Recommendation: run 3R.**

## Is the edge real?

- Tuned on 2025-01-01 .. 2026-03-31. Out-of-sample = everything else.
- In-sample expectancy +0.0838R (n=335); out-of-sample +0.0684R (n=764).
- Degradation only -18%. Overfitted systems collapse; this does not.
- Permutation p = 0.0142. Bootstrap 95% CI +0.009R .. +0.140R.
- 68% of months profitable.

Verdict: a real but small edge. The CI's lower bound is near zero, so the
size of the edge is not precisely known.

## Costs

Commission is $2.09/trade, $2,295 total = **22% of gross profit**.
Fixed on an FTMO challenge account.

## FTMO sizing (10% target, 10% static max loss, 5% daily)

Daily limit is not binding: max 2 trades/day, worst day -2.28R.
Only the 10% total loss constrains sizing.

| Risk/trade | Pass Phase 1 | Bust | Median time |
|---|---|---|---|
| $300 | 99.5% | 0.4% | 16 months |
| $500 | 96% | 4% | 9 months |
| $600 | 94% | 6% | 7 months |
| $800 | 89% | 11% | 5 months |

Sensitivity: if the true edge sits at the bottom of the CI (+0.009R),
a $600 stake passes only 54% of the time. The simulation is only as good
as the expectancy estimate.

## Correlation with the NAS100 London Range Breakout

Measured on 349 shared trading days:

- **Daily-R correlation +0.478** (95% CI +0.40 .. +0.56)
- Both lose together on 39% of days (28% if independent)
- Combining improves return-per-drawdown by +8% over the better single bot

Time to pass Phase 1, risk sized for a ~90% pass rate:

| Setup | Risk/trade | Median days | ~months |
|---|---|---|---|
| US500 3R alone | $799 | 112 | 5.3 |
| NAS100 LRB alone | $985 | 76 | 3.6 |
| Both, as they really are (r=+0.48) | $710 | 57 | 2.7 |
| Both, if truly uncorrelated | $864 | 47 | 2.2 |

Running both is clearly worth it despite the correlation.
