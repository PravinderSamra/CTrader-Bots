# 07 — The Bias Engine: turning the data into a bull/bear opinion

You asked for **an opinion**, not a data dump. This is how it is produced —
deterministically, so that a wrong call can always be traced to the input that
caused it. `prototypes/bias_engine.py` implements this and runs today.

---

## Design principles

1. **Every component states its own contribution and its reasoning.** No black
   box. When the brief is wrong you can see exactly which rule misfired and fix
   *that rule*, which is what makes Phase 4 possible.
2. **Direction and conviction are separate.** Fuel, event risk and regime
   instability reduce *conviction*; they do not flip *direction*.
3. **Events are a gate, not a vote.** A High-impact print in 90 minutes doesn't
   make the day bearish — it makes the day untradeable until it clears.
4. **The strategy call matters as much as the direction call.** Being right on
   direction while using the wrong entry model still loses money.

---

## The components and their weights

| Component | Max ± | Rationale |
|---|---|---|
| **Gamma regime** | ±8 | Highest weight. Decides *how* price moves, which decides which of your two strategies works. Sub-rules: side of the flip (±3), sign/size of week net GEX (±2), position within the call/put wall band (±2), flip-straddle instability (+1 damping) |
| **Volatility** | ±6 | VXN daily change (±2), VIX9D/VIX term structure (±2), VXN/VIX tech-stress ratio (−1), VVIX tail-hedge bid (−1) |
| **Rates / FX** | ±6 | 10y daily change (±3 — the biggest single macro lever on NAS100), short-end-led selloff penalty (−1), DXY (±2) |
| **Breadth / leadership** | ±5 | Mega-cap average move (±2), narrow-rally divergence (−2), NDX vs ES relative strength (±1) |
| **Structure** | ±5 | Prior-week displacement (±3), side of PD mid (±1), in-reach pool imbalance (±1) |
| **Fuel** | 0 | **Reports, never votes.** Fuel changes position management and target scope, not direction |
| **Events** | 0 + gate | Reports the calendar; can raise a hard STAND-ASIDE flag |

## Score → label

| Score | Label |
|---|---|
| ≥ +10 | STRONGLY BULLISH |
| +6 … +9 | BULLISH |
| +3 … +5 | MILDLY BULLISH |
| −2 … +2 | NEUTRAL / TWO-WAY |
| −3 … −5 | MILDLY BEARISH |
| −6 … −9 | BEARISH |
| ≤ −10 | STRONGLY BEARISH |

---

## Worked example — live run, 2026-08-22 10:02 UTC

```
BIAS -6  ->  BEARISH

  [gamma    ] -3  below flip 29327.2 by 36.7pts — SHORT gamma, dealers amplify
  [gamma    ] +1  but price is straddling the flip (<0.15%) — regime unstable
  [gamma    ] -2  week net GEX -0.331 $bn/1% -> expansion likely
  [gamma    ] +0  price mid-band (29181.6-29381.6), 54% up the range
  [vol      ] +2  VXN 21.98 (-5.5%) — fear falling, bullish
  [vol      ] +1  VIX9D/VIX 0.831 contango — mean-reversion favoured
  [vol      ] -1  VXN/VIX 1.45 — tech-specific stress above the broad market
  [vol      ] +0  VVIX 86.27 — no tail-hedge bid
  [rates    ] -1  US10y 4.738 (+0.89%) — yields up, BEARISH tech
  [rates    ] +0  DXY 98.839 (-0.06%) — dollar flat
  [breadth  ] +0  mega-cap avg +0.01% (2/4 up)
  [breadth  ] +0  NDX +0.33% vs ES +0.38% — in line
  [fuel     ] +0  ADR14 474.7, 67.1% used vs ~38% normal by 10:00 -> ratio 1.77 (burning hot)
  [structure] -1  price below PD mid 29292.9
  [structure] -3  price BELOW the entire prior-week range (29422.4-30175.7) —
                  weekly draw has flipped bearish; PWL is now resistance
  [structure] +1  in-reach unmitigated pools: 3 above / 1 below
  [events   ] +0  NVDA earnings 2026-08-26 AH (cons $2.01) — index-defining
```

**Read:** a genuinely bearish structural picture (below the whole prior week,
below the gamma flip, yields rising) partially offset by falling implied vol
and a contango term structure. The −6 with two meaningful offsets is exactly
right — bearish, but not a conviction trade.

---

## Rules that emerged from building it (and why they matter)

### Prior-week displacement — the highest-value single rule
Price trading entirely outside the previous calendar week's range is one of the
strongest structural reads available, and it is easy to miss looking at a
1-minute chart. On 2026-08-22 it was worth −3 on its own and flipped the call
from MILDLY BEARISH to BEARISH. It also **reclassifies a level**: PWL at
29,422.4 is no longer support, it is resistance, and it should be traded as a
strategy-1 short-sweep level rather than a long-sweep level.

### Narrow-rally divergence
Index up > 0.3% while the mega-cap average is down > 0.2% means the move is
being carried by the tail. Those rallies fade into the NY close far more often
than they extend.

### Flip-straddle damping
Within 0.15% of the gamma flip the regime is genuinely undecided. The engine
adds back +1 as an explicit conviction reduction rather than pretending to
know. Better to say "unstable" than to be confidently wrong.

---

## Two bugs found and fixed while building this — recorded because they matter

1. **Yahoo `chartPreviousClose` is the close before the *whole range*, not the
   prior session.** On a 10-day range it reported AVGO as −13.87% when the
   actual daily move was +1.21%, which corrupted the entire breadth component.
   Fixed by deriving the prior close from the series itself
   (`macro_probe.py:yahoo_series`). **Any future data source must be validated
   the same way — check one number by hand against a known value before
   trusting a whole feed.**
2. **Narrow-rally rule fired on a non-divergence.** The condition
   `nd > 0.3 > avg` triggered when the mega-cap average was +0.01%. Now
   requires the mega-caps to actually be down.

Both were caught only because every component prints its reasoning. That is the
argument for the transparent design.

---

## Confidence and honest uncertainty

The brief should always carry a confidence label alongside the direction:

| Condition | Confidence |
|---|---|
| Score ≥ \|8\|, components agreeing, no event gate, fuel normal | **HIGH** |
| Score ≥ \|5\| with 1–2 offsetting components | **MEDIUM** |
| Score < \|5\|, or straddling the flip, or fuel exhausted, or event within 2h | **LOW — reduce size or stand aside** |

An honest LOW is worth more than a confident guess. The engine should be
comfortable outputting "NEUTRAL / TWO-WAY — no edge today", and the brief
should say so plainly rather than manufacturing a setup.

---

## Phase 4 hook

Every run should append its score, components, and the levels it published to
`data/history/YYYY-MM-DD.json`. After ~40 sessions that archive supports the
questions Phase 4 needs to answer:

- Which components actually predict the day's direction, and which are noise?
- Does the score threshold need moving?
- Do sweeps of the call wall fail more often than sweeps of PDH?
- Is the fuel model's remaining-budget estimate calibrated, or systematically
  over/under-stating the range?
- Does strategy selection by gamma regime measurably beat picking one strategy?

Those are answerable questions — but only if the data is logged from day one.
**That is the strongest argument for building Phase 2 in the repo with a
scheduled job: the archive builds itself.**
