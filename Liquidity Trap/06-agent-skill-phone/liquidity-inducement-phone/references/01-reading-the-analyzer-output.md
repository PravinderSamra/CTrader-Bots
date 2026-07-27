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
| `pools_above` / `pools_below` | ranked target pools each side: `price`, **`zone` [low,high]**, `dist`, `reach`, `touches`, `kind`, **`too_close`**, **`confirmed`** | The liquidity map. **Quote the `zone`, not `price`.** |
| `…[].confirmed` | true when `touches ≥ 2` or it is a day-frame level (PDH/PDL/PWH/PWL/prior_close/**session_high**/**session_low**) | **Only confirmed pools are targets.** A single-touch swing level is one bar's extreme, not liquidity — but the day's own high/low always count, they are the most obvious resting stops there are. |
| `…[].swept` | true when price has traded beyond the pool **since it was last touched** | **A swept level is a liquidity block, not a target.** Its stops are already gone — aiming at it is aiming at spent liquidity. Measured from the last touch, so a level re-formed after the day's extreme still counts as live. |
| `draw_up` / `draw_down` | nearest **confirmed**, **unswept**, non-`too_close`, in-reach pool each side | Candidate targets. The one in the bias direction is usually *the* draw. If it comes back `confirmed: false`, nothing confirmed was in reach — downgrade, don't dress it up. |
| `session` | DST-correct session context: `label`, `ny_local`, `ny_open_utc`, `minutes_from_ny_open` (neg = until open), `in_trade_window` | **Gate 5.** ALWAYS use this — never hand-convert UTC to NY time (the offset shifts with DST: open is 13:30 UTC in summer, 14:30 in winter). |
| `recent_sweep` | swept level + reclaim side + **`lb_zone`** + **`stop_beyond`** + `bars_ago` + **`still_valid`**, or null | **Gate 2** (the trap). Null **or `still_valid: false`** = no live trap → at most *watching*. An invalidated reclaim means the trap FAILED — price traded back through the swept level; never present it as an active setup. |
| `no_mans_land` | true = price stranded mid-range | **Gate 6**. true → stand down. |
| `warnings` / `error` | data issues | If `error` present, relay `detail` and stop. |

## Everything is a zone, never a tick

Pools, liquidity blocks and entries are **areas**. The analyzer gives you the
band; use it:

- A pool's `zone` `[low, high]` is where the liquidity sits — say
  *"4,071–4,074"*, not *"4,071.91"*. `price` is only the midpoint for maths.
- `recent_sweep.lb_zone` is the swept, no-liquidity extreme — the factual band.
  `lb_width` is how wide it actually is; **`thin_lb: true`** means the pocket is
  narrower than the instrument's own noise band (a shallow stab), so it can't
  be "worked" as an area.
- **`recent_sweep.entry_zone`** is the practical band to quote as the entry —
  `lb_zone` widened to the noise tolerance when it's thin. Use this for entry,
  `lb_zone` when describing the structure.
- `recent_sweep.stop_beyond` is the stop level (true extreme + buffer) — one
  price, because a stop *is* a single line. It is anchored to the **real**
  extreme, so a widened `entry_zone` never loosens your risk.
- **`recent_sweep.pool_taken`** names the pool the sweep actually consumed, or
  `null`. The detector fires on a poke beyond the recent swing extreme, which
  is not necessarily a pool — `null` means an incidental high/low was poked and
  **no real liquidity was taken**, so it is not the trap. A `pool_taken` with
  `confirmed: true` and high `touches` is the strong version.
- Targets are quoted as the far edge of the pool zone you're aiming into (exit
  as it's being taken, not after).

## Sanity-check the distances before you write an idea

`too_close: true` (dist < `range.min_target_dist`) means that pool is **not a
target** — reaching it wouldn't cover the stop and spread. If the draw in your
bias direction is `too_close`, or the two draws are barely apart, the honest
answer is **no tradeable structure yet**: name the further pool that *would* pay
and wait for price to leave the compression. Never present two levels a few
points apart as a trigger and a target — that is a round-trip in the noise.

## The cycle: one side gets taken, it becomes the block, you target the other

The two draws are not two trade ideas — they are the two ends of one machine:

1. **Both draws are live targets** while unswept. Price is between them.
2. **One side gets swept.** Price takes that pool's stops and closes back
   through it (`recent_sweep`, `still_valid: true`, ideally with a named
   `pool_taken`).
3. **That pool is now the liquidity block, not a target.** Its liquidity is
   spent; `swept` flips to true and it drops out of draw selection on the next
   run. Your stop hides behind it (`stop_beyond`), your entry is the retest of
   `entry_zone`.
4. **The opposing draw becomes the target.** You trade *away* from the swept
   side, toward the pool that is still intact.

So: sweep low → long toward the upper draw; sweep high → short toward the
lower draw. Gate 4 (bias lockout) is the same rule stated defensively — after
a high is taken you do not buy until the paired low is taken.

Two things this does **not** mean:
- A *break* is not a sweep. Price must close back through the level. A break
  that holds is a breakout/breakdown — no trap, no LB, no trade.
- The swept pool is not always a draw. `recent_sweep` fires on the recent swing
  extreme; check `pool_taken` to see whether real liquidity was consumed.

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
