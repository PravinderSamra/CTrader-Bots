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

---

# Moving to NAS100

US30 is finished. Five configurations were tested against 2024, the year reserved
as the honest test, and all five lost: −859, −1,288, −371, −39, and the original
trader's own rules. 2023 lost under every one of them too. That is not a setting
still to be found; it is the absence of an edge.

## Reserve the years again, before touching anything

The same discipline applies and matters more now, because the temptation after a
disappointing result is to search harder.

| Period | Role |
|---|---|
| 2022 + 2023 | **Train.** Choose settings here. Look freely. |
| 2024 | **Test.** One run of the chosen setting. Nothing else. |
| 2025 + 2026 | Report only — the US30 work has already touched these. |

Nothing about NAS100 has been fitted yet, so its 2024 is genuinely clean. Spend
it once.

## Two starting configs, taken from the existing M5 study

`../../US30 London Range Breakout/docs/Final_Study_London_Range_Breakout.md`
tested this family on both instruments and found NAS100 profitable in all four
years, with shallower drawdowns and a volume filter that behaves monotonically
(US30's was non-monotonic — its highest-volume quintile was slightly negative).

Its NAS100 structure is **not** the US30 one:

- range **02:00 → 09:30 ET** — a wide overnight range, not a London session
- execute **10:00 → 11:00 ET** — short and late; most of the edge is in that hour
- volume **≥ 1.3×** trailing-20
- plain stop and target, no breakeven and no trailing

| Config | Stop | Target | Study result |
|---|---|---|---|
| `NAS100_balanced_60pt_2.0R` | 60pt | 2.0R | 30% win, PF 1.33, −12.9R drawdown |
| `NAS100_aggressive_40pt_3.5R` | 40pt | 3.5R | 21% win, PF 1.36, −12R drawdown |

Both zone selectors are set to New York, because on this instrument the range is
a New York overnight concept rather than a London session. Same code, different
answer to "which clock" — which is the point of having two.

Three US30 lessons are already baked in:

- **No breakeven, no trailing.** Every trailing variant tried on US30 amputated
  the right tail; the studied NAS100 edge is a plain stop-and-target.
- **Max ORB range raised to 2000.** US30's 500pt cap silently stood the bot down
  on 41 summer days. NAS100 trades at a different price scale, so that number
  must not be inherited blind.
- **Margin usage raised to 80%.** The 50% cap quietly shrank every trade in the
  last run to 70% of intended size, and nothing in the results said so.

## Check before reading anything into the first run

1. No `SAFETY: Clamping volume` lines — otherwise every result is scaled down.
2. `SESSION_TIMEZONE` shows the range ending at the bell and entry 30 min later.
3. Losses near −1R, wins near the target. If they overshoot, the backtest is on
   bar data rather than tick data and is measuring the simulator.
4. Sensible trade count. Far fewer than ~100/year means a filter is starving it,
   most likely the volume multiplier or the range cap.

## NAS100 result — five full years, one config

60pt fixed stop, 4R cap, volume 1.2x, no breakeven, no trailing, longs and
shorts, 02:00-09:30 ET range, entries 10:00-11:00 ET.

| Year | Trades | Net | Per trade | PF | Minus top 5 |
|---|---|---|---|---|---|
| 2022 | 105 | +$2,914 | +$27.75 | 1.44 | +$922 |
| 2023 | 106 | +$1,671 | +$15.77 | 1.29 | −$234 |
| 2024 *(tuned)* | 85 | +$2,352 | +$27.67 | 1.52 | +$359 |
| 2025 | 88 | +$1,368 | +$15.55 | 1.25 | −$622 |
| 2026 (to Aug) | 50 | +$553 | +$11.07 | 1.16 | −$1,434 |
| **All** | **434** | **+$8,859** | **+$20.41** | **1.34** | **+$6,859** |

Expectancy +$20.41/trade, 95% CI +$4.65 to +$36.38, P(edge ≤ 0) = 0.5%. Max
drawdown −$1,109, about 11R. Excluding 2024, where the 60pt stop was chosen:
349 trades, +$6,507, PF 1.30, four of four years positive, P(edge ≤ 0) = 2.0%.

Against US30 on the same tests: PF 1.03 vs 1.34, P(no edge) 43.4% vs 0.5%,
removing one trade flipped US30 negative while NAS100 keeps +$8,458, and
removing ten leaves +$4,867 against US30's −$7,876. Shorts lost on US30 and
make +$3,818 at PF 1.31 here.

### The drift worth acting on

Per-trade profit falls each year (+27.75, +15.77, +27.67, +15.55, +11.07) and
the fixed stop is the likely reason. Median daily range roughly doubled, 106pt
to 211pt, but as a share of price it barely moved (0.61%–0.98%, no trend) — the
index simply got bigger. So 60 points was 62% of a typical day's range in 2023
and is 28% now. It was never a universal number: it is 51% of 2024's range, the
year it was fitted to.

The fix is a rule that adapts rather than a schedule of numbers by year, which
would be the same fitting mistake in a new costume. Stop Type = No with Stop %
of ORB Range ≈ 50 reproduces what 60pt meant in 2024 and holds that meaning
without further intervention. Test across all five years and look for the
per-trade decline to flatten, not just for a bigger total.

### Risk reduction at 1R, paired test on 2026

Same 50 trades, only the exit rule differs: +$553 → +$844. Six trades improved,
one was hurt by $14, and the average win was identical — it only tightens a
stop, so it cannot shrink a winner. Promising, unconfirmed on the other four
years.

### Provenance

2024 is spent — the 60pt stop was chosen there. 2022, 2023, 2025 and 2026 were
run afterwards on that unchanged setting, so they are effectively out-of-sample,
and all four are positive. Any further change needs re-running all five years.

## 50%-of-ORB stop tested across all five years — REJECTED

Identical entries, only the stop rule changed. The hypothesis was that a fixed
60pt stop had drifted from 62% of a typical day's range in 2023 to 28% in 2026,
and that holding it at a constant share would flatten the falling per-trade
profit. It did the opposite.

| Year | 60pt fixed | 50% of range |
|---|---|---|
| 2022 | +$2,914 (PF 1.44) | +$2,152 (PF 1.48) |
| 2023 | +$1,671 (PF 1.29) | +$889 (PF 1.16) |
| 2024 | +$2,352 (PF 1.52) | +$153 (PF 1.04) |
| 2025 | +$1,368 (PF 1.25) | +$279 (PF 1.07) |
| 2026 | +$553 (PF 1.16) | +$95 (PF 1.05) |
| **All** | **+$8,859, PF 1.34** | **+$3,567, PF 1.19** |

Worse in four years of five, and worse on every secondary test: P(edge ≤ 0)
rises from 0.49% to 7.06%, and removing the ten best trades leaves +$45 against
+$4,867. The per-trade decline did not flatten, it steepened: +20.49, +8.38,
+1.80, +3.17, +1.90.

The mechanism is visible and is the one flagged before the test. Win rate rose
from 38.5% to 47.2% — the wider stop genuinely does get hit less often. But the
average win collapsed from $208.98 to $111.37, because risk is fixed in dollars,
so a wider stop buys a smaller position and the same price move earns less. The
median stop went from a flat 60pt to 108pt, with extremes out to 850pt. Fewer
losses did not pay for smaller wins.

**Conclusion: keep the 60pt fixed stop.** The drift in what 60pt means relative
to the daily range is real and measurable, but correcting it costs more than it
returns. If anything the data leans the other way — with dollar-fixed risk a
tighter stop earns more R per point travelled, which is an argument for testing
40pt (the value the M5 study recommended for NAS100) rather than a wider one.

The falling per-trade profit across the five years remains unexplained. It is
not the stop drifting.

## Risk reduction at 1R (50%) across all years — REJECTED

Paired against the 60pt baseline on identical trades. Criteria were set before
the run: positive in at least four years of five, average win unchanged, and a
steady few-hundred-dollar gain rather than one year carrying it.

| Year | Baseline | With RR | Change | Helped | Hurt |
|---|---|---|---|---|---|
| 2022 *(Jan–Aug only)* | +$2,268 | +$3,035 | **+$766** | 16 | 0 |
| 2023 | +$1,671 | +$1,372 | **−$299** | 8 | 5 |
| 2024 | +$2,352 | +$1,956 | **−$396** | 6 | 7 |
| 2025 | +$1,368 | +$1,552 | +$184 | 13 | 1 |
| 2026 *(to Aug)* | +$553 | +$845 | +$291 | 6 | 1 |
| **Total** | **+$8,214** | **+$8,760** | **+$546** | | |

Positive in three years of five, not four. The +$546 total rests entirely on
2022, which is a partial run — across the four other periods it is **−$220**.
The +$291 on 2026 that motivated the test was not representative.

The failure mode is the one flagged beforehand and then underweighted. A stop
tightened to half distance can still be hit, and when it is, a trade that would
have recovered books a small loss instead. It happened eight times: four in
2023, three in 2024, one in 2025, costing about $1,689 in foregone profit. The
worst single case turned +$397.85 into −$53.17.

The "average win unchanged" criterion was mis-specified on my part. It did move
slightly, but only because converted winners leave the winning pool and change
its mean — not because the rule shrinks winners. The rule genuinely cannot
shrink a winner that survives; it can only kill one outright. That is the real
cost, and it is larger.

**Conclusion: do not adopt it.** Keep 60pt fixed, no risk reduction, no
breakeven, no trailing — the configuration that produced +$8,859 at PF 1.34
across five full years.
