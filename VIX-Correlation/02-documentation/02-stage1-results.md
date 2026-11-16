# Stage 1 results — does the VIX leg add anything?

Run 2026-11-16. Daily bars, 274 aligned sessions (16 Nov 2024 → 10 Dec 2025).
ES = `US500` (id 115), VIX = `VIX` (id 152), both from the cTrader MCP account.
NQ reconstructed from `US30 London Range Breakout/data/NAS100/nas100_m5.csv`
(Pepperstone demo feed) bucketed into the *same* session boundaries, 274/274.

Rules pre-registered in `01-dylan-oneal-rules.md` BEFORE this was run.

---

## The methodological finding that mattered most

The first pass used **the day's close as the entry** and every arm lost money
(arm A: −0.27 avgR at 1R). That was my error, not the strategy's. The source
enters at the reclaim of the previous day low, which sits a **median 0.35%
below the close** — so a close-entry test both pays 0.35% more and inflates
the stop distance, since risk is measured from entry down to the day's low.

Re-run with entry at `previous day low × 1.0014` (the ~8-handle cushion from
the source's worked example), every arm turns positive. Median stop drops
from 0.90% of price to 0.47%.

**Entry convention decided the sign of the result.** Worth remembering before
trusting any backtest of a level-reclaim strategy.

---

## Event frequency

ES trades below the previous day's low and closes back above it:
**68 events in 274 sessions = 24.8% of days, ~63 per year.** Common.

---

## Results (entry at the reclaim, stop below the day's low, max 10 days, no time stop)

### Target 2R
| Arm | n | win% | avgR | totalR |
|---|---|---|---|---|
| A — reclaim alone (the null) | 68 | 52.9% | +0.60 | +40.5 |
| B — + VIX weak | 13 | **69.2%** | **+1.22** | +15.8 |
| B' — + VIX confirmed | 55 | 49.1% | +0.45 | +24.7 |
| C — + VIX weak + NQ held | **1** | 100% | +2.00 | +2.0 |
| D — + NQ held, no VIX condition | 7 | 42.9% | +0.29 | +2.0 |

### Target 3R
| Arm | n | win% | avgR | totalR |
|---|---|---|---|---|
| A — reclaim alone (the null) | 68 | 39.7% | +0.51 | +34.9 |
| B — + VIX weak | 13 | **69.2%** | **+1.83** | +23.8 |
| B' — + VIX confirmed | 55 | 32.7% | +0.20 | +11.1 |
| C — + VIX weak + NQ held | **1** | 100% | +3.00 | +3.0 |
| D — + NQ held, no VIX condition | 7 | 42.9% | +0.71 | +5.0 |

---

## Findings

**1. The null already works.** A plain previous-day-low reclaim returns +0.60
avgR at 2R over 68 trades. Any claim for the VIX leg has to beat THIS, not
beat zero.

**2. The VIX leg beats the null, but the sample is small.** 13 events,
9 winners, identical 69.2% at 1R, 2R and 3R — meaning when it works it runs
past 3R, and when it fails it stops out. Binary.

| Target | VIX weak | VIX confirmed | Fisher one-sided p |
|---|---|---|---|
| 1R | 9/13 (69.2%) | 30/55 (54.5%) | 0.260 |
| 2R | 9/13 (69.2%) | 27/55 (49.1%) | 0.159 |
| 3R | 9/13 (69.2%) | 18/55 (32.7%) | **0.018** |

Only the 3R result clears p<0.05, and **three targets were tested**, so a
Bonferroni threshold is 0.017 and p=0.018 just misses it. **Suggestive, not
established.** H24's correction is the precedent for not over-reading this.

**3. It is not an artefact of the April 2025 crash.** Excluding 25 Mar–15 May
2025: VIX-weak n=10, 60% win, +1.48 avgR at 3R vs confirmed 30%, +0.12.
The 13 events spread across Nov 2024 to Dec 2025, not clustered.

**4. The NQ leg is worse than decorative — it is destructive.**
- NQ holds its low while ES breaks on only **7 of 68 events (10%)**.
- All three legs aligned **once in 274 sessions — ~0.9 per year**. n=1.
- NQ holding, on its own, scores **42.9% / +0.29 avgR — WORSE than the null**.

The source's own May 2025 example had the NQ leg failing and they took the
trade anyway, calling VIX "the main factor". The data agrees. **Drop NQ.**

**5. The 1% rule never fired.** ES up ≥1% and VIX up ≥1% on the same day:
**0 occurrences in 274 sessions.** The source said it was rare; in this window
it did not happen at all. Untestable here.

**6. Stop sizes are workable.** Median risk entry→stop 0.47% of price, p75
0.68%. Against H25 (median favourable run 48–79 pts regardless of stop size)
these are tight enough that 2–3R is plausible, unlike the wide-stop cases.

---

## The caveat that blocks building anything

**Daily bars cannot see sequence.** The test assumes the day's low came
BEFORE the reclaim. Where the low actually came *after* price reclaimed the
previous day low, the real trade would have been stopped out — and this test
scores it as a winner.

**This biases every number above optimistic, and by an unknown amount.**
It cannot be resolved without intraday data. Nothing should be built until it is.

Secondary caveats: 13 months only; 13 events in the headline arm; ES/VIX come
from a different broker feed than the live account (`US500` vs `US500.cash`),
acceptable because each instrument is measured against its own previous day.

---

## Stage 2 (not yet run)

1. **Resolve the sequencing problem on intraday bars.** The single thing that
   could destroy this result. Do it first.
2. Threshold-test "VIX weakness" — currently a binary did-it-reach-PDH.
3. Test the entry cushion rather than inheriting 0.14% from one example.
4. Measure weekend-gap exposure: how many of these were open over a weekend,
   and what the gap did (Vanessa, 2026-11-16 — a sizing question, not a yes/no).
5. Extend the window beyond 13 months.
