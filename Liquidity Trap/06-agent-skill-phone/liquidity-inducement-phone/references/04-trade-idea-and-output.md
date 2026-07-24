# 04 — Building the Trade Idea & the Output Format

Synthesise the analyzer facts + strategy into the **single highest-probability
intraday setup**, trend-first, and present it phone-friendly.

## Selecting the setup

1. **Direction = the day's bias** (reference 02). Primary idea trades with it.
2. **Target = the in-reach draw in that direction** (`draw_up` for longs,
   `draw_down` for shorts), reach `intraday` (reference 03). If it's `swing`,
   apply the draw-beyond-fuel rule.
3. **Trigger = a sweep of the near opposite pool** (for a long: a pool in
   `pools_below` swept + bullish reclaim; for a short: `pools_above` swept +
   bearish reclaim). Look at `recent_sweep`:
   - Sweep present, in the right place → the trap is set: **armed** (enter at the
     stab/rejection) or just-triggered.
   - No sweep yet → **watching**: name the exact level you need swept.
4. **Stop = just beyond the swept extreme** (the LB) + a small spread buffer.
   For a long: below the swept low; short: above the swept high.
5. **RR check**: distance to the in-reach target ÷ stop distance. **Floor ≈
   1:3.** Below it, say the RR is too thin (or note a tighter execution-TF entry
   would be needed). Partial at the nearest internal pool only where it pays
   ≈1:5+.
6. **Run the six gates** (SKILL.md). Any fail → downgrade to watching/no-trade
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
Bias: <one line: direction + why, from reasons + two-lines logic>
Fuel: <adr_used%, expansion_state, volume state; is the draw in reach>

PRIMARY (<with-trend>):  <LONG/SHORT>
  Trigger : <the sweep you need / that just happened>
  Entry   : <zone or "on rejection after the stab of X">
  Stop    : <price> (just beyond the LB)
  Target  : <in-reach pool price> (RR ~1:<x>)   [+ partial at <internal> if ≈1:5]
  Bigger draw (context, not today): <swing pool or "none">
  Invalidation: <price/condition>
  State   : ARMED / WATCHING / NO-TRADE — <reason if not armed>

SECONDARY (counter-trend, optional): <one line or "none today">

Waiting for: <the single event that arms/kills this>
```

Then one plain-English sentence of desk read, and the standard footer:
*Nothing is 100%; analysis, not financial advice; no orders are placed.*

## Worked shape (illustrative)

> **UK100 — BULLISH day (score +45)**
> Bias: higher highs/lows and above PDH; session low just swept and reclaimed —
> the intact PDH above is the draw.
> Fuel: 38% ADR used, volume expanding → ROOM_TO_EXPAND; PDH ~30 pts away,
> within the ~60-pt budget → valid intraday target.
> PRIMARY (with-trend): LONG. Trigger: session low 10,505 swept + reclaimed
> (done). Entry: on the reclaim, ~10,508–10,512. Stop: 10,498 (below the swept
> low + buffer). Target: PDH 10,545 (RR ~1:3.3). Invalidation: 5m close back
> below 10,498. State: ARMED.
> Secondary: none today (no clean counter-setup).
> Waiting for: it's live — manage to PDH; partial only if an internal pool pays
> ≈1:5.
> *Nothing is 100%; analysis, not advice; no orders placed.*

Do not template-match the numbers — recompute every run from the analyzer.
