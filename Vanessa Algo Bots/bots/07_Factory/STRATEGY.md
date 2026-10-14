# Factory Bot, candidate A: "Index Bollinger Dip" (plain words)

The first strategy found by our Strategy Factory (research/factory). One generic cBot (Factory_Bot.cs) runs it;
future factory strategies use the same bot with different settings.

## Why should it work?
When a stock index has an unusually sharp fall (a daily close far below its normal range), forced and emotional
selling tends to overshoot, and prices usually recover part of it within a week. Big funds can't easily trade
this across 10 small index CFDs at once; we can.

## The rules
- Markets: 10 indices: US500, US100, US30, US2000, GER40, UK100, FRA40, EU50, AUS200, HK50 (FTMO .cash names).
- **Buy** when an index closes **below its 20-day Bollinger band at 2.5 standard deviations**
  (20-day average minus 2.5 x the 20-day standard deviation). The order goes 60 minutes after the next daily open.
- **Sell 5 daily bars later.** No take profit. No normal stop: tests showed a normal stop sells right before the
  bounce and kills the edge.
- **Disaster stop** at 10 x the average daily range (ATR 20) below entry, for a true crash. It has almost never been hit.
- One position per index; several indices can be held at once (sharp falls often hit several together).

## Size
"Risk Per R" = $200, where R = 2 x the average daily range. That means a normal bad trade loses about $200-400,
the worst trade in 16 years lost about $1,000 (5R), and the worst single day was about -$1,100 (5.6R).

## Factory test results (daily bars, costs and swap included)
- Build period (to 2020) +0.13R, confirm 2021-23 +0.32R, unseen 2024-26 +0.30R per trade.
- 2010-2026: 328 trades, 59% win rate, average +0.20R, worst drawdown 11.5R (about $2,300 at $200/R).
- About 24 trades a year. Correlation with Daily Systems +0.05, with the NAS bot about 0.
- Account Monte Carlo (NAS $550 + Daily Systems + this at $200/R): fail odds 16.8% -> 16.2%, passes ~6 days sooner.

## Tick backtest to run (confirmation step)
- cBot: Factory_Bot.cs (build it in cTrader as a new cBot called "Factory Bot").
- Attach to **US500.cash, Daily (D1)** chart. Leave all settings at their defaults.
- **Tick data from server**, **1 Jan 2021 to today**, balance 100,000, commission 30.
- If any symbol prints "Symbol not found" at the start, tell me its FTMO name.
- Send me the log (it ends with H| lines) and a screenshot of the results.

Pass if: profitable in both 2021-23 and 2024-26, at least 6 of the 10 indices positive, and the worst drawdown
under about $3,500. Then it can go live at HALF size ($100 per R) for its first 30 trades (QUANT_PROCESS.md stage 6).

## Switch-off rule (monthly review)
Pause if the last 50 trades average below -0.05R, or the drawdown passes $3,500 (1.5 x the backtest's worst).

## cTrader backtest result (14 Oct 2026, M1 bars, 1 Jan 2021 - 14 Oct 2026, $200/R, commission 30): PASS
- Net +$7,465, profit factor 1.92, 176 trades, 58% win, average +$42 a trade (about +0.21R).
- 2021-23: +$2,505 (104 trades); 2024-26: +$4,960 (72 trades). By year: 2021 +4,750, 2022 -1,444, 2023 -801,
  2024 +1,827, 2025 +1,182, 2026 +1,951.
- 8 of the 9 indices traded were positive (AUS200 -$230). US2000.cash does not exist at FTMO (skipped).
- Max balance drawdown 2.69% (~$2.8k), max equity drawdown 3.97% (~$4.2k, floating loss in the April 2025 sell-off);
  worst trade -$472, worst exit day -$508. Swap -$273, commission -$105.
- Versus the factory screen (2021-26: +0.31R): weaker (+0.21R), mainly 2022-23 (FTMO daily bars differ from the
  research feed). Still clearly positive in both halves.
- Decision: go live at HALF size, Risk Per R = $100, for the first 30 trades (QUANT_PROCESS stage 6).
