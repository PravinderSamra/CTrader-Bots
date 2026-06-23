# US500 Overnight Phenomenon Backtest

## Strategy
Buy US500 at daily close. Sell at the next trading day's open.
Captures the documented overnight gap-up bias in the S&P 500.

## Data Source
CTrader Remote MCP HTTP API — Pepperstone demo account (D_1 bars, symbol US500).

## Parameters
| Parameter | Value |
|---|---|
| Backtest period | 12 months (daily rolling window) |
| Risk per trade | $100 |
| Notional per trade | $10,000 (sized so 1% adverse move = $100 loss) |
| Overnight financing | 7.8% p.a. (SOFR ~5.3% + 2.5% Pepperstone markup) |
| Spread | 0.5 pts each way (1.0 pt round-trip) |

## Results (last run)
| Metric | Value |
|---|---|
| Total trades | 259 |
| Win rate (net) | 32.0% |
| Gross P&L | +$341.82 |
| Total costs | $935.40 |
| **Net P&L** | **−$593.58** |
| Profit factor (gross) | 1.38 |
| Max drawdown (net) | $823.85 |
| Avg cost per trade | $3.61 |

## Key Finding
The overnight gap-up phenomenon **does exist** in gross terms — the average overnight
move is positive and the profit factor is 1.38. However, CFD overnight financing
costs (~$2.14/night) plus spread (~$1.47/night) total ~$3.61 per trade, which
fully erodes the edge on a $10,000 notional position.

To make the strategy viable, you would need either:
1. A significantly larger notional (edge scales with size, costs are partly fixed)
2. A spread / swap-free account structure
3. Selective entry (e.g., only trade on Mondays, or after confirmed up-day closes)

## Usage
```bash
cd US500-Overnight-Backtest
python backtest.py
```

Results are also saved to `results.txt` for easy review.
