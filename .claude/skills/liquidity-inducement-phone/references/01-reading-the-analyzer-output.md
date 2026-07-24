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
| `range.expansion_state` | ROOM_TO_EXPAND / MODERATE / LOW_FUEL / EXHAUSTED | Go/caution/fade signal. |
| `volume.exec_relative` / `.state` | recent vs baseline tick volume; expanding/normal/drying_up | Is there participation behind the move? |
| `named_levels` | PDH, PDL, prior_close, PWH, PWL, day_open, session_high/low | The day-frame reference pools. |
| `pools_above` / `pools_below` | ranked lists of target pools each side, each with `price`, `dist`, `reach` (intraday/swing), `touches`, `kind` | The liquidity map. `touches` ≥ 2 = stronger (equal highs/lows). |
| `draw_up` / `draw_down` | the nearest **in-reach** pool each side | Candidate targets. The one in the bias direction is usually *the* draw. |
| `recent_sweep` | a just-swept level + reclaim side, or null | **Gate 2** (the trap). Null = no trap yet → at most *watching*. |
| `no_mans_land` | true = price stranded mid-range | **Gate 6**. true → stand down. |
| `warnings` / `error` | data issues | If `error` present, relay `detail` and stop. |

## How the pieces map to a trade

- **Direction** comes from `daily_bias` (reference 02).
- **The target** is the `draw_*` in your bias direction — but only if its
  `reach == "intraday"` (reference 03). A `swing`-reach draw is context, not
  today's target.
- **The trigger** is a sweep of the *near* pool on the opposite side of your
  entry (for a long: a sweep of a pool *below*, i.e. in `pools_below`), shown as
  `recent_sweep` with a bullish/bearish reclaim. No sweep yet → *watching*,
  name the level you need taken.
- **The stop** hides just beyond the swept extreme (the liquidity block) — for a
  long, below the swept low; for a short, above the swept high.
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
