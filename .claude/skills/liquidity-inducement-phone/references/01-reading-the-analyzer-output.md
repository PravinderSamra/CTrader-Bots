# 01 — Reading the Analyzer Output (+ strategy recap)

`analyze.py` returns one JSON object. Every number is a *fact computed from
cTrader bars*; your job is to turn facts into a decision. Fields:

| Field | What it is | How you use it |
|---|---|---|
| `price` | Live mid (or last close) | Reference point for distances/reach. |
| `daily_bias.label` / `.score` | BULLISH / BEARISH / NEUTRAL and a −100…+100 score | The **trend** = your primary direction (reference 02). |
| `daily_bias.trend_day_potential` | true when strong score + low ADR used | A "let it run / hold for the far pool" hint. |
| `daily_bias.reasons` | the drivers that made the score | Quote 1–2 in your bias line. |
| `range.adr14` | 14-day average daily range | The day's fuel tank size. |
| `range.adr_used_pct` | % of ADR already travelled today | Fuel gauge (reference 03). |
| `range.remaining_budget` | ADR left today | **Reach filter**: targets within this are intraday. |
| `range.min_target_dist` | 10% of ADR — the floor for a *tradeable* target | Anything nearer is noise: the move is smaller than the stop+spread it costs. |
| `range.expansion_state` | ROOM_TO_EXPAND / MODERATE / LOW_FUEL / EXHAUSTED | Go/caution/fade signal. |
| `volume.exec_relative` / `.state` | recent vs baseline tick volume; expanding/normal/drying_up | Is there participation behind the move? |
| `named_levels` | PDH, PDL, prior_close, PWH, PWL, day_open, session_high/low | The day-frame reference pools. |
| `pools_above` / `pools_below` | ranked target pools each side: `price`, **`zone` [low,high]**, `dist`, `reach`, `touches`, `kind`, **`too_close`** | The liquidity map. `touches` ≥ 2 = stronger. **Quote the `zone`, not `price`.** |
| `draw_up` / `draw_down` | nearest **meaningful** in-reach pool each side (skips `too_close`) | Candidate targets. The one in the bias direction is usually *the* draw. |
| `recent_sweep` | swept level + reclaim side + **`lb_zone`** + **`stop_beyond`**, or null | **Gate 2** (the trap). Null = no trap yet → at most *watching*. |
| `no_mans_land` | true = price stranded mid-range | **Gate 6**. true → stand down. |
| `warnings` / `error` | data issues | If `error` present, relay `detail` and stop. |

## Everything is a zone, never a tick

Pools, liquidity blocks and entries are **areas**. The analyzer gives you the
band; use it:

- A pool's `zone` `[low, high]` is where the liquidity sits — say
  *"4,071–4,074"*, not *"4,071.91"*. `price` is only the midpoint for maths.
- `recent_sweep.lb_zone` is the swept, no-liquidity extreme: **the entry area**
  you're waiting for price to retest, and what the stop hides behind.
- `recent_sweep.stop_beyond` is the stop level (extreme + buffer) — one price,
  because a stop *is* a single line.
- Targets are quoted as the far edge of the pool zone you're aiming into (exit
  as it's being taken, not after).

## Sanity-check the distances before you write an idea

`too_close: true` (dist < `range.min_target_dist`) means that pool is **not a
target** — reaching it wouldn't cover the stop and spread. If the draw in your
bias direction is `too_close`, or the two draws are barely apart, the honest
answer is **no tradeable structure yet**: name the further pool that *would* pay
and wait for price to leave the compression. Never present two levels a few
points apart as a trigger and a target — that is a round-trip in the noise.

## How the pieces map to a trade

- **Direction** comes from `daily_bias` (reference 02).
- **The target** is the `draw_*` in your bias direction — but only if its
  `reach == "intraday"` **and** `too_close` is false (reference 03). A
  `swing`-reach draw is context, not today's target.
- **The trigger** is a sweep of the *near* pool on the opposite side of your
  entry (for a long: a sweep of a pool *below*, i.e. in `pools_below`), shown as
  `recent_sweep` with a bullish/bearish reclaim. No sweep yet → *watching*,
  name the zone you need taken.
- **The stop** hides just beyond the swept extreme (the liquidity block) — use
  `recent_sweep.stop_beyond`; for a long it sits below the swept low, for a
  short above the swept high.
- **Strength**: prefer pools with higher `touches`, draws with `trend_day_
  potential`, and `expansion_state` of ROOM_TO_EXPAND/MODERATE.

## Strategy recap (the rules the facts feed)

1. **Only confirmed pools are targets** — respected + moved away, or equal
   highs/lows (`touches ≥ 2`), or day-frame levels (PDH/PDL/PWH/PWL). A level
   already swept is now a **liquidity block** (stop anchor), not a target.
2. **Induce → trap → enter.** Price breaks a minor level to induce retail
   (their stops become the pool), then sweeps that pool (the trap), then you
   enter the reversal. Enter *after* the sweep, at the stab, on rejection.
3. **Liquidity block = the swept, no-liquidity extreme.** Your stop sits just
   beyond it (+ a small spread buffer). No LB → no trade.
4. **Bias lockout.** After a high is taken you don't buy until the paired low is
   swept, and vice versa — no matter what happens between.
5. **Targets are the opposing pool**, never a fixed R multiple — and must be in
   today's reach.
6. **Wait.** No confirmed pool + no sweep = no trade. "If you don't see
   liquidity, you are the liquidity."

Full detail: repo `Liquidity Trap/02-documentation/` files 01 (fundamentals),
03 (the setup), 09 (inducement & daily bias), 10 (pattern library), and the
official playbook.
