# Test protocol — agree this before running, not after

Every parameter choice made while looking at a period spends that period. Once
spent, it can never again be used as evidence: results on it measure the search,
not the strategy. This file records what has already been spent and what the
remaining clean data is reserved for.

## Provenance of each year

| Period | Status | Why |
|---|---|---|
| 2022 | **SPENT as test** — ran at 1.4x, lost £90.28 over 11 trades | out-of-sample result, keep it that way |
| 2023 | **CLEAN** | never seen |
| 2024 | **CLEAN — the one real out-of-sample result so far** | ran, but nothing was fitted to it |
| 2025-01-01 → 2026-08-13 | **SPENT** | `VolumeMultiplier`, `BreakEvenTriggerR`, `FixedStopPoints` were optimised here |

Measured cost of that spend: **+£55.60/trade in-sample against −£23.21/trade out**,
a −£78.81 swing. That is the size of the illusion optimisation produces on a
94-trade sample, and it is why the rules below matter.

## The trap in "test 1.2 and 1.3 across 2022–2026"

Running both multipliers over all years and keeping the better one spends 2022,
2023 and 2024 in a single afternoon. The winner will look good on the data that
selected it, exactly as 1.4 did. We would have converted our only honest years
into a second in-sample period and learned nothing we could trust.

It also compounds: the three parameters already fitted, times the multipliers now
being added, is a search over many combinations judged on ~150 trades. The best
of many results is a biased estimate of the truth — the more configurations
tried, the more the winner's margin is selection rather than edge.

## Rules

1. **Split by period, decide once.**
   - **Train: 2022 + 2023.** Choose the volume multiplier here. Look freely.
   - **Test: 2024.** Run the chosen multiplier once. Do not run the others.
   - **2025–2026: not evidence.** Report them for completeness; they cannot
     confirm anything because they are already spent.

2. **Pre-commit the decision rule.** Before seeing results, state what wins.
   Suggested: *highest expectancy per trade on 2022+2023 combined, subject to at
   least 40 trades* — the sample-size floor stops a 6-trade fluke winning.

3. **One shot at the test set.** If 2024 disappoints and we re-pick using 2024,
   2024 becomes spent and we are back to having no honest estimate.

4. **Expect degradation.** Whatever the train result, the test result will be
   worse. Budget for roughly the −£79/trade already observed. A config that only
   works if degradation is zero is not viable.

5. **Log every run.** Config, period, trade count, net P/L, PF. Including the
   runs that lost — a search whose failures go unrecorded cannot be corrected
   for later.

## What counts as a pass

Not "profitable". Profitable in-sample is free. The bar is:

- positive expectancy on **2024** with the multiplier picked from 2022–23 alone,
- **and** no single month contributing more than ~40% of the total (checks the
  result is an edge rather than one lucky run),
- **and** enough trades that the result is not a coin flip — below ~40 the
  confidence interval swallows the estimate.

If it fails, that is a real finding and worth more than a fitted curve.

## Run log

| Date | Config | Period | Trades | Net P/L | PF | Notes |
|---|---|---|---|---|---|---|
| — | vol 1.4, BE 0.6R, stop 50pt, fixed-UTC clock | 2022 | 11 | −£90.28 | 0.72 | out-of-sample |
| — | vol 1.4, BE 0.6R, stop 50pt, fixed-UTC clock | 2024 | 37 | −£858.90 | 0.57 | out-of-sample |
| — | vol 1.4, BE 0.6R, stop 50pt, fixed-UTC clock | 2025 | 37 | +£2,179.44 | 4.95 | in-sample |
| — | vol 1.4, BE 0.6R, stop 50pt, fixed-UTC clock | 2026 (to Aug) | 20 | +£989.60 | 2.95 | in-sample |
| — | v2: vol 1.2, BE 2R, no RR, shorts on | 2022 (Jun–Dec) | 42 | +£3,315 | 2.24 | partial year |
| — | v2: vol 1.2, BE 2R, no RR, shorts on | 2023 | 113 | −£4,130 | 0.53 | |
| — | v2: vol 1.2, BE 2R, no RR, shorts on | 2024 | 109 | −£1,288 | 0.83 | |
| — | v2: vol 1.2, BE 2R, no RR, shorts on | 2025 | 113 | +£1,413 | 1.19 | |
| — | v2: vol 1.2, BE 2R, no RR, shorts on | 2026 (to Aug) | 55 | +£1,476 | 1.40 | |
| — | **v2 total** | 2022–2026 | **432** | **+£786** | **1.03** | expectancy +£1.82, 95% CI −£16.90…+£21.87 |

## Provenance note added after the v2 run

The 1.2× multiplier and 2R breakeven were chosen after reviewing all five years of
the v1 run, so every year is now weakly in-sample. The v2 total is not an
out-of-sample number. What survives that caveat is the *mechanical* findings —
the clock split, the range-versus-stop relationship, the outlier concentration —
because they describe the shape of the trade book rather than the level of profit.

The next genuinely clean test would need data outside 2022–2026, or forward
testing on demo.

## v3 stop test — 2026 only (uninformative, kept for the record)

Percentage-of-ORB-range stop replacing the fixed 50pt, run on 2026 alone.

| Stop | Longs only | With shorts |
|---|---|---|
| 15% | +604.30 | +59.50 |
| 20% | +331.58 | −510.44 |
| 25% | +333.86 | −409.29 |
| *v2 fixed 50pt (baseline)* | *≈ +2,273* | *+1,476* |

Every variant underperformed the fixed stop, but 2026 could not test the
hypothesis. The idea is that a fixed stop is too large on quiet days; 2026 was
the most active year in the sample (48.9% of days ranged 300pt or more) and its
14 quiet-day trades were already profitable at +1,277. What the runs actually
measured was stop *size* in an active year, where the ranking 15% > 20% > 25%
and fixed-50pt-best follows mechanically: on a 400pt day those are 60/80/100pt
stops against 50pt, and a smaller stop earns more R per point travelled.

A likely flaw in the formulation: 15% of a 110pt range is a ~17pt stop, which on
US30 M1 with 1-2pt spread sits inside the noise. Quiet days may be stopping out
faster rather than becoming tradeable. If the mechanism shows promise on
2023-2024, the next formulation should be a percentage with a floor, e.g.
max(20% of range, 30pt) - which the bot does not currently support.

Next: 15% and 25%, shorts on, 2023 and 2024 - the two years holding -5,748 of
quiet-day losses, where the mechanism is falsifiable.

## v3 stop test — 2023 + 2024 (the real test)

Identical trade selection to v2 (113 and 109 trades), so this is a paired
comparison: same entries, different exits.

| Stop | 2023 | 2024 | Both | Median trade | PF |
|---|---|---|---|---|---|
| fixed 50pt | −4,130 | −1,288 | **−5,417** | −105.3 | 0.67 |
| 15% of ORB | −3,689 | −371 | **−4,061** | −104.4 | 0.75 |
| 25% of ORB | −4,030 | −39 | **−4,069** | −102.2 | 0.71 |

**The mechanism works, and it is not enough.** Split by the day's range, quiet-day
losses fall from −5,748 to −4,333 (15%) to −3,749 (25%), i.e. the scaling stop does
rescue quiet days as predicted — per-trade loss improves from −33.8 to −22.1. But
active days give it back, going from +331 to −320 at 25%, because a wider stop earns
fewer R per point travelled. Net across both years stays around −4,060.

The earlier "too tight" worry was wrong in the main: anchoring to the ORB edge means
risk = overshoot + pct×range, so median quiet-day stops were 38.9pt (15%) and 55.0pt
(25%), not the ~17pt feared. Mean stop across all trades is *larger* than fixed-50 —
65.3pt and 84.3pt — the change makes stops tighter on quiet days and much wider on
active ones, which is exactly what it should do.

What survives: the median trade barely moves (−105 → −102) and removing the best five
trades still leaves −6,342. 2024 nearly reaches break-even (−39) but 2023 stays at
−4,030 under every configuration tried. 2023 is the quietest year in the sample
(mean ORB range 219pt, 14.2% of days above 300pt), and no exit rule tested has made
it tradeable.

## Where four rounds of changes leave 2023 + 2024

| Config | 2023 | 2024 | Both |
|---|---|---|---|
| v1 fixed50, BE 0.6R, long only | −1,532 | −859 | −2,391 |
| v2 fixed50, BE 2R, shorts | −4,130 | −1,288 | −5,417 |
| v3 orb15, BE 2R, shorts | −3,689 | −371 | −4,061 |
| v3 orb25, BE 2R, shorts | −4,030 | −39 | −4,069 |

Every configuration loses in both years. The strategy has not been made to work in a
quiet market by any exit change tested.

## The untested structural difference

The M5 study in `../../US30 London Range Breakout/docs/` found a US30 edge at PF ~1.31
using a **fixed take-profit at 2.5–3.0R**. This bot has never been run that way:
`TakeProfitR = 50` disables the target entirely, so every trade is a pure runner
managed by the trailing stop. Winners do reach those levels — at 15% of ORB, 25 of 63
winners reached 2R and 15 reached 3R — so a target is not obviously unreachable.
That is the one element of the researched edge never tried here, and it is a
structural change rather than another parameter tweak.
