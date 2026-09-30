# NAS100 London Range — v3.2 Auto Risk Ladder

A copy of `01_NAS100_London_Range_AddToWinner` (v3.0) that can set its own risk per trade from the account balance.
With **Enable Auto Risk Ladder = No**, it behaves exactly like v3.0.

## What it does (when enabled)
Once a day, at the new-day reset before the range forms:
1. It reads the account **balance**.
2. It picks the risk from the ladder: the highest line the balance has reached.
3. If this bot has had **4 losing days in a row** (main trade + adds, taken from the account history), it uses **one level lower** until the next winning day.
4. It prints one line in the log, even with Trades-Only Log on:
   `L|date|balance|risk|losing days in a row|cut`

Default ladder ("balance:risk"): `115000:1000,112000:900,109000:800,106000:700,103000:600,100000:500,97000:400,94000:300,0:200`

| Balance | Risk |
|---|---|
| $115k+ | $1,000 |
| $112k | $900 |
| $109k | $800 |
| $106k | $700 |
| $103k | $600 |
| $100k | $500 |
| $97k | $400 |
| $94k | $300 |
| below | $200 |

You can edit the ladder text in the parameters without changing any code.

## Checking it in a backtest
Use the size 5 settings (trigger 0.7, Add Size 5, Max Total Risk 2.5, TP 4R), plus Enable Auto Risk Ladder = Yes and Trades-Only Log = Yes.

Expected result (from the size 5 log, 2021-01-01 .. 2026-09-28, $100k, no payouts):
- net about **+$176,800**
- deepest drawdown about $27,000
- risk mostly at $1,000 after the first year

A backtest never takes payouts, so the balance keeps climbing to the top of the ladder. On FTMO, each payout resets you to $100k and $500.

## Notes
- It only counts this bot's own trades for the losing-days rule (label prefix `ORBVL`). US500 has its own bot.
- If the bot restarts mid-day, it chooses again from the balance at that moment.
- Class `OrbVolumeBreakoutBotV32Ladder`.
