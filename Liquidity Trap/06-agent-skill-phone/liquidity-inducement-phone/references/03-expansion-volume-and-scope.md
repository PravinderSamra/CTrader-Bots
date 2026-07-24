# 03 — Room for Expansion, Volume Left & Intraday Scope

This is what keeps ideas **day-sized**: is there enough range and participation
left for the move to reach its target *today*? Mirrors the UK100 ORB-intel
range-budget model (ADR14 + adrUsedPct + remaining budget).

## The fuel gauge — `range.expansion_state`

Computed from `adr_used_pct` (today's range ÷ ADR14) and volume:

| State | Trigger | What it means for the trade |
|---|---|---|
| `ROOM_TO_EXPAND` | ≤ 40% ADR used, volume not drying | Full tank. Trend-day continuation and far in-reach draws are on the table. |
| `MODERATE` | 40–70% used | Normal. Nearest in-reach pool is the target; don't over-reach. |
| `LOW_FUEL` | 70–90% used | Little fuel for fresh breakouts. **Favour fades back into the range over chasing**; tighten targets to the nearest pool. |
| `EXHAUSTED` | ≥ 90% used | Day's range largely spent. New continuation is low-probability; prefer no-trade or a small mean-reversion into the range. |

(This is the ORB "R4 — range budget" rule: *"78% of a typical day's range is
already spent — fresh breakouts have little fuel; favour fades."*)

## Volume left — `volume.state` / `.exec_relative`

`exec_relative` = recent tick volume ÷ the prior baseline on the execution TF:
- **`expanding` (≥1.25)** — participation is behind the current move; a sweep
  here is more likely a real trap with follow-through. Confidence up.
- **`normal` (~1.0)** — neutral.
- **`drying_up` (≤0.7)** — moves are running on fumes; sweeps may not follow
  through, chop risk. Downgrade, especially into lunch/late session.

Combine with the gauge: **best setups = ROOM_TO_EXPAND/MODERATE + expanding
volume in the bias direction.** Worst = EXHAUSTED + drying volume → stand down.

## Intraday scope (targets must be reachable today) — soft scope

For every candidate target, the analyzer already tags `reach`:
- **`intraday`** — distance from price ≤ ~remaining_budget → a valid target
  today.
- **`swing`** — beyond today's budget → **context only, never today's target.**

Rules:
1. The trade's target = the **nearest `intraday` pool** in the bias direction
   (`draw_up`/`draw_down` are pre-selected as the nearest in-reach pool).
2. A `swing` draw is mentioned as the bigger-picture magnet but is **not** the
   target — say "the bigger draw is X but it's beyond today's range."
3. **Draw-beyond-fuel** (ORB R7): if the only pool in the bias direction is
   `swing`, either take a **partial-only** trade to the nearest in-reach
   internal pool and be flat by session end, or — if nothing is in reach —
   **no-trade today** ("right idea, wrong day").
4. Reach is a *probability filter*, not a guarantee — a strong trend day can
   exceed ADR. Note that as upside, never as the planned target.

## Putting the fuel read in the advisory

One line, always: e.g. *"Fuel: 38% of ADR used, volume expanding →
ROOM_TO_EXPAND; PDH at 10,545 is ~30 pts away, within today's ~60-pt budget →
a valid intraday target."* If LOW_FUEL/EXHAUSTED, say so and bias toward fades
or no-trade.
