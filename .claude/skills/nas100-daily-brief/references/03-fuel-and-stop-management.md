# 03 — Fuel, range budget, and when to move the stop

Answers: *is there enough room left for this move today, and do I need to manage
the stop actively?*

## The gauge
```
ADR14        = mean(High − Low) over the last 14 completed days
adr_used_pct = today's range ÷ ADR14
budget left  = ADR14 − today's range
```

| State | Used | Stop management |
|---|---|---|
| `ROOM_TO_EXPAND` | ≤40% | Leave the structural stop alone. Trail only on confirmed 1m structure breaks |
| `MODERATE` | 40–70% | Structural stop. Break-even at 1R or half the remaining budget, whichever first |
| `LOW_FUEL` | 70–90% | **Active from entry.** BE at 0.7R, 50% off at the first pool, trail tight. Expect to be trailed out rather than target-filled |
| `EXHAUSTED` | ≥90% | Don't initiate. If in: partials now, stop to BE or better, flat before the close |

## fuel_ratio — the part that matters most
NAS100 does not spend its range evenly: roughly 15% in Asia, 25% in London,
**45% in the NY open**, 15% in the afternoon. So the raw percentage is
meaningless without the time of day.

`fuel_ratio` = used ÷ what's normal by this hour (Eastern).

- **> 1.4 burning hot** — trending, or the event already happened. Expect ADR to
  be exceeded *or* an exhaustion reversal. Either way, trail actively.
- **≈ 1.0** — normal.
- **< 0.6 coiled** — compressed; expect expansion later. Don't fade the break.

## Cross-checks
- **VXN-implied range** is forward-looking where ADR is backward-looking. When
  implied < ADR the options market prices a quieter day — use the smaller number.
- **Gamma scales the budget**: positive gamma ×0.8, negative ×1.3,
  backwardated vol a further ×1.2.

## Forced management triggers
Regardless of state:
1. `adr_used_pct` crosses 90% mid-trade → the rest is borrowed. Take partials.
2. Gamma flip crossed against a mean-reversion trade → edge inverted. Tighten or exit.
3. Volume drying while extended (>70% used) → classic pre-reversal. Tighten.
4. Approaching a **positive** gamma shelf with the trade → it will stall. Partials *into* it.
5. Approaching a **negative** shelf with the trade → it accelerates. Give it room.
6. High-impact print inside 15 minutes → flatten or hard-stop to BE.

## Known open question
The review engine found the published budget under-estimating realised range on
2026-08-20 (156 vs 266). One session is not evidence. If the reviewer confirms
it across 3+ sessions, the budget multiplier needs raising — do not change it
before then.
