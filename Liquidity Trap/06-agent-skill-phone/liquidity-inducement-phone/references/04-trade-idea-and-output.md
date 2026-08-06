# 04 — Building the Trade Idea & the Output Format

Synthesise the analyzer facts + strategy into the **single highest-probability
intraday setup**, trend-first, and present it phone-friendly.

## Selecting the setup

1. **Direction = the day's bias** (reference 02). Primary idea trades with it.
2. **Target = the in-reach draw in that direction** (`draw_up` for longs,
   `draw_down` for shorts), reach `intraday` (reference 03). If it's `swing`,
   apply the draw-beyond-fuel rule. **If it's `too_close: true`, there is no
   target** — the pool is inside the noise. **If it's `confirmed: false`, it is
   not a pool at all** — a single touch is one bar's extreme. **If it's
   `swept: true`, the liquidity is already gone** — price has been through it
   since it formed, so it is a liquidity block now, not a draw. In each case
   skip to the next pool out that is in reach, not `too_close`, unswept and
   confirmed;
   if there isn't one, the answer is **no-trade / wait for the range to
   resolve**, not a few-point scalp.
3. **Trigger = a sweep of the near opposite pool** (for a long: a pool in
   `pools_below` swept + bullish reclaim; for a short: `pools_above` swept +
   bearish reclaim). Look at `recent_sweep`:
   - Sweep present, **`still_valid: true`**, in the right place → the trap is
     set: **armed** (enter on the retest of `lb_zone`) or just-triggered.
   - **`still_valid: false`** → the trap **failed**: price has traded back
     through the swept level. This is a **no-trade**, not a setup. Say the
     reclaim failed and what that implies; never dress it up as armed.
   - No sweep yet → **watching**: name the **zone** you need swept.
4. **Stop = `recent_sweep.stop_beyond`** — just past the swept extreme (the LB)
   with a spread buffer. For a long it's below the swept low; short, above the
   swept high.
5. **Sanity gate before RR: trigger and target must be far apart.** The gap
   between the sweep zone and the target zone must be ≥ `range.min_target_dist`
   *and* clear the stop distance by the RR floor. Quoting a trigger and a target
   only a few points apart is a broken read — go back to step 2.
6. **RR check**: distance to the in-reach target ÷ stop distance. **Floor ≈
   1:3.** Below it, say the RR is too thin (or note a tighter execution-TF entry
   would be needed). Partial at the nearest internal pool only where it pays
   ≈1:5+.
7. **Run the six gates** (SKILL.md). Any fail → downgrade to watching/no-trade
   with the reason.

## Sizing (optional, informational only)

If asked, size per the repo guide's spread-bet formula:
`volume = round(risk_gbp / stop_points) × 100` (each 100 = £1/pt). State it as a
suggestion — **this skill does not place orders.**

## Primary vs secondary

- **Primary** = the with-trend idea above.
- **Secondary (optional)** = a counter-trend idea, offered ONLY if a clean
  counter-setup exists (opposite pool swept + reclaimed into an LB, ideally with
  a time excuse like the 10:00 NY roll). Label it clearly *counter-bias /
  short-term*, target the near pool only, smaller size/expectation, out fast.
  If no clean counter-setup: say "no secondary today."

## Output format (what the user sees)

Keep it tight and skimmable — this is a phone:

```
<INSTRUMENT> — <bias label> day (score <n>)
Time: <session.label>, <ny_local> NY (<minutes_from_ny_open> min from open)
Bias: <one line: direction + why, from reasons + two-lines logic>
Fuel: <adr_used_pct>% of ADR used (<today_range> of <adr14>) · <remaining_budget> pts left
      volume <state> (<exec_relative>x) · <expansion_state>
      Reach today: <what that budget realistically permits — name the pools it
      does and does not cover>

PRIMARY (<with-trend>):  <LONG/SHORT>
  Trigger : sweep of <low>–<high>  (pool: <name>, <touches> touches)
  Entry   : <entry_zone low>–<high>  (retest/rejection)
  Stop    : <stop_beyond>  — beyond the LB <lb_zone low>–<high>
  Target  : <target zone low>–<high>  (<dist> pts = <n>% of remaining budget)
  RR      : ~1:<x>   [+ partial at <internal zone low>–<high> if ~1:5]
  Bigger draw (context, not today): <swing pool zone or "none">
  Invalidation: <price/condition>
  State   : ARMED / WATCHING / NO-TRADE — <reason if not armed>

SECONDARY (counter-trend, optional): <one line or "none today">

Waiting for: <the single event that arms/kills this>
```

### Two rules that are not optional

**1. Every area is quoted as a band, `low`–`high`.** Pools, liquidity blocks,
entry zones, sweep triggers and targets are all areas — quote the `zone` /
`lb_zone` / `entry_zone` arrays, never the midpoint `price`. The user marks
these on a chart, so a single number is not actionable. **The only bare number
is the stop** (`stop_beyond`), because a stop genuinely is one line. If you
catch yourself writing "target 4071.66", replace it with "4070.25–4072.82".

**2. Every output carries the fuel line, with numbers.** State
`adr_used_pct`, `today_range` vs `adr14`, `remaining_budget`, `volume.state`
with `exec_relative`, and `expansion_state` — then **scope the target against
that budget explicitly**: say what fraction of the remaining range the target
consumes, and name any pool that is technically `intraday` but would eat most
or all of it. A target at 100% of remaining budget is a stretch, not a plan;
say so rather than quoting it flat. This applies to no-trade outputs too — the
fuel state is often *why* there is no trade.

Then one plain-English sentence of desk read, and the standard footer:
*Nothing is 100%; analysis, not financial advice; no orders are placed.*

## Worked shape (illustrative)

> **UK100 — BULLISH day (score +45)**
> Bias: higher highs/lows and above PDH; session low just swept and reclaimed —
> the intact PDH above is the draw.
> Fuel: 38% ADR used, volume expanding → ROOM_TO_EXPAND; PDH ~30 pts away,
> within the ~60-pt budget → valid intraday target.
> PRIMARY (with-trend): LONG. Trigger: session-low pool 10,503–10,506 swept +
> reclaimed (done). Entry: retest of the LB zone 10,505–10,509. Stop: 10,498
> (below the swept low + buffer). Target: PDH pool 10,543–10,547 (RR ~1:3.3).
> Invalidation: 5m close back below 10,498. State: ARMED.
> Secondary: none today (no clean counter-setup).
> Waiting for: it's live — manage to PDH; partial only if an internal pool pays
> ≈1:5.
> *Nothing is 100%; analysis, not advice; no orders placed.*

Do not template-match the numbers — recompute every run from the analyzer.

## Targets: always a ladder, never a single number

Quote `targets_up` / `targets_down` as three tiers, each as a band:

```
TARGET LADDER (long)
  T1  4245.58-4248.16   prior_close   6 touches   prime   bank / stop to BE
  T2  4270.52-4275.31   equal_highs   9 touches   heavy   trail to
  T3  4280.92-4284.75   equal_highs   5 touches   heavy   runner
```

Why: 83% of planned entries filled, but only 27% of fills reached their one
target. The entries work; the all-or-nothing exit did not. Management detail
lives in reference 05.

- `quality` is the tier grade, not the touch count: **prime** = 2-4 touches
  (hit 50%), **heavy** = 5+ (hit 20% - a wall as often as a magnet), **thin**
  = unconfirmed (never once reached). Put T1 on a `prime` tier where possible,
  never on a `thin` one.
- If a side returns no usable tier, say so. Do **not** substitute
  `draw_up`/`draw_down` - those fall back to swept and unconfirmed pools when
  nothing clean is in reach.
- Give `pct_of_remaining_budget` per tier as scope, **not** as a veto. Targets
  beyond the remaining ADR budget were hit slightly more often than
  comfortable ones, so it decides how much comes off at T1, not whether the
  trade is taken.

## Counter-trend ideas are judged on their gates

State counter-bias as a fact, then judge the setup on its own gates and RR.
It is never on its own a reason to decline: counter-trend secondaries have
returned +1.59R against with-trend primaries at -0.60R, and two of the three
declined ideas that later hit target were turned down for nothing else.
