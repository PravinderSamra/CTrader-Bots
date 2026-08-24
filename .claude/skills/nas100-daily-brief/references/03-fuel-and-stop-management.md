# 03 — Fuel, range budget, and when to move the stop

Answers: *is there enough room left for this move today, and do I need to manage
the stop actively?*

## What the budget actually forecasts — read this first

**It forecasts how much further the day's HIGH-LOW RANGE can grow. It has never
forecast how far price will travel.** Those two things diverge sharply once a
range is established, and confusing them is the single easiest way to misread
this section.

Measured on 2026-08-24: the 13:45 scan published a **0.0pt budget**. The range
then extended **5.3pts** — the forecast was essentially exact. In the same
window price **traversed 284.4pts** inside that range.

So `EXHAUSTED` does not mean "nothing will happen". It means:

> The extremes are probably in. Expect real movement still — just **between**
> them rather than beyond them.

**This inverts which setup to prefer.** If the range will not extend, then by
definition price has to turn at the extremes. At `LOW_FUEL`/`EXHAUSTED` the
higher-probability trade is **fading the extremes back into the range**, even
when the gamma regime favours continuation. On 24 Aug the brief called
continuation at 28,903 with a 0pt budget; price bottomed 30pts later and rallied
178 into the close. The fade was the trade, and the fuel state said so.

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
Whether the budget under-estimates range EXTENSION early in the session. On
2026-08-24 the London scans published 88.7 against 168.5 of actual extension
(~1.9x), while the exhausted-point scan was essentially exact (0.0 vs 5.3).
One session. Do not recalibrate on it.

A previously-recorded data point from 2026-08-20 has been **withdrawn**: it came
from a backdated journal entry created to test the review loop, not from a real
scan, and should never have been cited as evidence.
