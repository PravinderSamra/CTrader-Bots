# 05 — Managing the Open Trade

The rest of this skill gets you *in*. This governs what happens after, because
a target is a plan, not a promise. Replaying real sessions turned up trades
that ran **+7.98R, +2.80R and +2.02R in favour and still closed at −1R**, held
flat to a target the day was never going to reach. Every one of those was a
management failure, not a bad entry.

**The principle: manage on structure, scoped by fuel.** The opposing pool gives
you *direction*. Fuel and volume decide how much of it is realistic today.
Structure decides where the stop travels on the way.

## 1. A far pool does not veto the trade

If the setup is clean but the opposing pool sits beyond the remaining budget,
**take it and manage it** rather than standing down. Treat the far pool as the
direction of travel, not a literal exit.

Say so explicitly in the idea:

> "Draw is PWH 4101.85–4104.41 (28.9 pts) against 34.8 pts remaining — reachable
> but consumes 83% of the budget. Taking it as direction; managing out at
> structure or on fuel exhaustion, not holding flat for the pool."

This is the one case where a `swing`-reach draw is still tradeable — but only
with the management plan stated alongside it. Never quote a far pool as a flat
target and leave it there.

## 2. Trail behind structural breaks, not fixed R multiples

The stop moves when **structure** moves, not when a profit number is hit.

For a long (mirror for a short):

| Event | Stop goes to |
|---|---|
| Price clears a confirmed pool above and **holds** (closes beyond it) | Just below that pool's `zone[0]` |
| A new higher low prints on the exec TF and confirms (5-bar pivot) | Just below that low |
| Price reaches the first intermediate pool | Break-even at minimum |

Two rules that stop this becoming a fixed trail:

- **A wick through is not a break.** Require a close beyond the level, same as
  the sweep rule. Trailing on wicks is how you get taken out inside noise.
- **Never move the stop against the trade.** It only ever tightens.

The pools tagged **`too_close: true`** are exactly these checkpoints. They are
useless as *targets* (inside the noise floor) but they are the structure the
trade travels through — use them for trailing and partials, not for aiming.
`path_up` / `path_down` list them in order between price and the draw.

## 3. Fuel and volume decide when to stop being patient

Re-scan while the trade is live. The read that armed it goes stale.

| State on re-scan | Action |
|---|---|
| `expansion_state` reaches **LOW_FUEL** (≥70% ADR) | Tighten to the last structural break; stop adding time |
| **EXHAUSTED** (≥90%) | Take what's there — the day has spent its range |
| `volume.state` flips to **drying_up** | Expect the move to stall; trail tighter, don't wait for the pool |
| `remaining_budget` < distance to target | The target is no longer reachable today — manage out at the nearest structure instead |

That last row is the important one: **the target can expire mid-trade.** A pool
20 pts away with 30 pts of budget is a plan; the same pool with 8 pts of budget
left is not. Re-check it, don't assume it.

## 4. Partials

Take partial at the first intermediate pool **only where it pays** — roughly
1:5 or better on the remaining runner (reference 04 §5). Below that, a partial
just converts a good trade into a mediocre one. On a MODERATE or LOW_FUEL day,
prefer the partial; on ROOM_TO_EXPAND with `trend_day_potential: true`, prefer
holding the runner.

## 5. What invalidates, still

Structural management never overrides the original invalidation. If price
closes back through the swept level (`recent_sweep.still_valid` goes false),
the trap failed — that is an exit, regardless of where the trailing stop sits
or how much is showing.

## Reporting it

When an idea is armed, the output must carry the management plan, not just the
levels:

```
  Manage  : BE at <first intermediate zone>; trail below <pool zone> on a
            close beyond it; tighten on LOW_FUEL or drying volume
  Budget  : target is <n> pts = <x>% of the <y> pts remaining
```

If you are asked about a position already open, work this file top-down: where
is structure now, what has fuel done since entry, and does the original target
still fit inside what is left.
