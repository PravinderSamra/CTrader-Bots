# NAS100 London Range — v3.1 Staged Adds (test version)

A copy of `01_NAS100_London_Range_AddToWinner` (v3.0) with one extra setting, **Staged Add Parts**.
Built to answer one question: does splitting the add into steps reduce losses by more than it costs in profit?
The v3.0 bot is unchanged. If this test doesn't help, delete this bot from cTrader.

## What it does
- **Staged Add Parts = 1** (default): identical to v3.0 (one add).
- **Staged Add Parts = 3**: the same total add is split into 3 equal parts:
  - part 1 at Add Trigger R (0.7R)
  - part 2 at Add Trigger R + Next Add Every R (1.4R)
  - part 3 at Add Trigger R + 2 × Next Add Every R (2.1R)
- Each part = Add Size × (risk removed from the main trade) ÷ parts. At size 5 and trigger 0.7 that's 0.5R per part (3 × 0.5R = the 1.5R single add in v3.0).
- All parts share the main trade's stop and target and close with it. Labels end `_ADD1`, `_ADD2` and `_ADD3`.
- Max Adds Per Trade is ignored when parts > 1. Max Total Risk and No Adds In Last Minutes still apply.

## Test run (one backtest)
Same settings as the v3.0 size 5 run, plus:

| Setting | Value |
|---|---|
| Add Size | 5 |
| Add Trigger R | 0.7 |
| Max Total Risk | 2.2 or more |
| **Staged Add Parts** | **3** |
| **Next Add Every R** | **0.7** |
| Trades-Only Log | Yes |

Compare with v3.0 size 5: $58,446.89 net, 6.83% max equity drawdown.

Class `OrbVolumeBreakoutBotV31Staged`, label prefix `ORBVS`.
