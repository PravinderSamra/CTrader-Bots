# NAS100 Auto Risk Ladder bot (v3.2): backtest check, 2 Oct 2026

Settings: size 5, trigger 0.7, Max Total Risk 2.5, TP 4.5R, Dynamic Stop on (break-even 2.5R, +2 pts, step 0.1R),
risk reduction 70% at 0.7R, Auto Risk Ladder on (default growth ladder, 4-loss rule), 2021-01-01 .. 2026-09-28, tick data.
With the ladder OFF the bot matched the previous bot exactly ($65,832.08).

Ladder ON: **+$200,204.78** (no payouts, so the balance compounds), max equity DD 14.91% (of a much larger peak balance), 1,005 trades, 430 winners.

## Verification of the log (`data/nas100_ladder_logs/DS4b_TP45_ladder.trades.txt`)
- All **2,095** daily ladder decisions match the ladder rules exactly (0 mismatches), including **300** "cut" days (4-loss rule).
- Every main trade's size equals risk ÷ 60 points (ratio 0.999–1.000).
- Days traded at each risk: $400 6, $500 25, $600 51, $700 31, $800 1, $900 89, $1,000 431.
- **Lowest balance: $100,000** (never below the start). **Worst day: −$2,680** (14 Dec 2022), about half of FTMO's $5,000 daily limit.
- Deepest closed-day drawdown $26,953, all from balances far above $100k.

## FTMO 2-Step journey (phase 1 from $96,510 to $110k, then phase 2 $100k to $105k), growth ladder, 5,000 simulations
| Settings | Reach funded | Typical time | Fast (1 in 4) | Slow (1 in 4) |
|---|---|---|---|---|
| Old: TP 4R, no trailing | 84.2% | 15.0 mo | 8.8 | 24.7 |
| **New: TP 4.5R, trail from 2.5R in 0.1R steps** | **89.1%** | **13.8 mo** | 8.3 | 22.5 |
