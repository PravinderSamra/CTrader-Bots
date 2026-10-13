# Deni Fib bot: what it does, in plain words

Deni Dantev's Fibonacci 0.618 strategy (The Trading Cafe), on gold (XAUUSD) and GBPUSD, 1-hour bars, buys and sells.
Rules were tested and frozen on 13 Oct 2026 before looking at 2024-26 (research/IDEAS_BACKLOG.md, "The Trading Cafe").

## The rules (sell side; the buy side is the mirror image)
1. **Trend top:** a swing high that is the highest point of the last 50 hours.
2. **Break:** price then closes below the last swing low before that top (the trend has turned).
3. **Order:** a sell limit at the 0.618 retracement of the move from the top down to the lowest point since.
   While waiting, if price makes a new low the order moves down with it.
4. **Stop:** just above the top. **Target:** the -0.272 Fibonacci extension (a bit beyond the low). About 2.3x the risk.
5. The order is cancelled after 30 hours, or if price goes back above the top first.
6. A trade still open after 120 hours (5 days) is closed. One trade per market per direction at a time.

## Size
"Risk Per Trade ($)" = what you lose if the stop is hit (default $100). The bot works out the lot size itself.

## Screen results (H1 bars, costs and swap included)
- Gold 2024-26 (unseen data): +0.22R per trade, 114 trades, 40% win, every year positive.
- GBPUSD 2024-26: +0.10R per trade, 133 trades (2024 -12R, 2025-26 +25R).
- Both 2021-26: about 70 trades a year, +55R in total, worst drawdown 28R, worst day -2.2R.
- No link with the NAS bot (correlation 0.00) or Daily Systems (-0.06).
- At $100 risk: roughly +$1,000 a year expected, worst losing spell about -$2,800.

## Tick backtest to run (the confirmation step)
- cBot: Deni_Fib.cs. Attach to **XAUUSD, 1 hour**. Leave Symbols = XAUUSD,GBPUSD.
- Data: **Tick data from server**. Period: **1 Jul 2021 to today**. Balance 100,000. Commission as for the other bots.
- Settings: all defaults (Risk Per Trade 100).
- Send me the log (it ends with H| lines, one per trade) and a screenshot of the results.

Pass if: net profit is positive in both 2021-23 and 2024-26, gold and GBPUSD are each positive overall, and the worst
drawdown is under about 35R ($3,500 at $100). It goes live only if you decide so after that.
