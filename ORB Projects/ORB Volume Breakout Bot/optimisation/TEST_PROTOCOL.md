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
