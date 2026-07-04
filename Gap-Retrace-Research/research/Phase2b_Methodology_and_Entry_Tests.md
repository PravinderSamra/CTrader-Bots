# Phase 2b — Backtest Methodology, M5 Entry, and Break-vs-Retest

**Date:** 2026-07-04 · Answers three follow-up questions on how the testing was done and whether a
finer entry timeframe or a break-and-retest entry changes the result.

---

## 1) Was it sequential, Monte Carlo, or walk-forward?

**Sequential, single chronological pass — event-driven, order-of-touch.** For every qualifying gap
session the engine walks the intraday bars in time order and resolves each trade by which level
(stop or target) price touches first. When one bar's range spans **both** stop and target, the tie
is broken **adverse-first (counted a loss)** — deliberately conservative. No look-ahead: trigger,
stop and target are fixed from information available at/before the entry bar.

What the earlier labels really were:

- **"Walk-forward by quarter" was NOT a true walk-forward.** A real walk-forward *re-optimises*
  parameters on a training window and tests on the next unseen window, rolling forward. What was
  actually done: **one fixed parameter set run across the whole 2 years, then results reported
  sliced by calendar quarter.** That is an **out-of-sample *stability* check** ("does the same fixed
  rule survive different regimes?" → yes in 6/8 quarters), *not* walk-forward optimisation. Honest
  label: **segmented / anchored out-of-sample reporting.**
- **No Monte Carlo.** No trade-sequence bootstrap, no randomised slippage/entry resampling, no
  parameter perturbation, no synthetic paths. So there are **no confidence intervals** — the "+0.25R"
  is a point estimate, and the lumpy equity curve says the true error bars are wide.
- **Parameter selection carried mild in-sample optimism:** the grid was full-sample and the defaults
  (gap ≥0.25%, warmup 2) were chosen seeing all 2 years. The two *filters* (skip weekend gaps; size
  floor) were justified a priori by Phase-1 mechanics, so they aren't pure curve-fit, but the exact
  thresholds are not out-of-sample.

**Bottom line:** robust in construction (no look-ahead, conservative fills, out-of-sample
time-slicing) but **not** validated by walk-forward optimisation or Monte Carlo. Those are the
honest next step to put error bars on the edge.

---

## 2) Does entering on M5 instead of M15 change R / win-rate?

Downloaded **12 months of GER40 M5** (60,836 bars) and re-ran the exact same setups (same sessions,
same gap filter, same prior-close target) changing **only the execution timeframe**, with
**time-based** warmup (30 min) and max-wait (240 min) so M15 and M5 are compared fairly.
Script: `compare_entries.py`. Figure: `../analysis/fig4_entry_experiment.png`.

**Breakout entry — expectancy (R/trade), 12-month common window:**

| gap filter | setups | breakout·M15 | breakout·M5 |
|---|---|---|---|
| ≥0.25% | 30 | **+0.44** (win 69%) | +0.31 (win 69%) |
| ≥0.15% | 64 | **+0.26** (win 64%) | +0.21 (win 63%) |
| ≥0.10% | 96 | **+0.12** (win 61%) | +0.11 (win 61%) |

**Finding: M5 does *not* improve the breakout entry — it is consistently, marginally *worse*.**
Win-rate is essentially identical; the average *winner* is smaller on M5. Mechanism: the 5-minute
series sees **higher intrabar wicks**, so the session extreme (where the stop sits) is placed a
little **wider → larger risk → each win is worth fewer R.** And the "catch it earlier" benefit
doesn't materialise, because the fade-rejection trigger forms on the same ~30-minute scale either
way — the entry *time* (median 30 min) is unchanged, so the finer timeframe only costs R.

So the intuition ("5m hits R sooner before the trend changes") **does not hold for this trigger**:
the signal fires at the same moment; going finer just widens the stop. M5 would only help if the
*trigger itself* were redefined to fire earlier (e.g. a 5-minute structure shift), which is a
different rule, not just a finer view of the same one.

---

## 3) Is it break-and-retest, or pure breakout?

**The current rule is pure breakout** — it enters when a bar *closes back through the session-open
level* in the fade direction. There is **no retest**. So question #3's suspicion is correct: nothing
was waiting for price to return to a zone and reject it.

I built and tested a **break-and-retest** variant: after the break (close back through the open),
wait for price to **retest the open level** and enter there on a limit (sell the pullback into the
zone), stop beyond the session extreme, same target. Same setups, both timeframes:

**Risk profile @ gap ≥0.15% (12-month common window):**

| variant | trig% of setups | win% | avg winner | avg loser | expectancy |
|---|---|---|---|---|---|
| breakout · M15 | 78% | 64% | +1.00R | −1.05R | **+0.26R** |
| breakout · M5 | 80% | 63% | +0.96R | −1.06R | +0.21R |
| break-retest · M15 | 48% | 32% | **+2.86R** | −1.09R | +0.19R |
| break-retest · M5 | 55% | 37% | **+3.07R** | −1.10R | +0.45R |

**Findings:**
- **Break-retest is a fundamentally different profile, not a strict upgrade.** It **wins far less
  often (27–37%)** but its **winners are much bigger (+2.5 to +4R)** because the limit entry at the
  level gives a tight stop / large reward-to-risk. It also **skips ~50% of setups** — the sessions
  that fill the gap and run *without* pulling back are missed entirely (those are often the best
  breakout trades).
- **Expectancy is comparable-to-noisy, not clearly higher.** At large gaps (≥0.25%) retest looks
  strong; at small gaps (≥0.10%) M15-retest goes **negative** (−0.13R). It is far more
  sample-sensitive than breakout — a few big winners drive it, so trust it least.
- **M5 helps the *retest* (unlike the breakout):** finer granularity fills the pullback at a better
  level and resolves the path more precisely (+0.45R vs +0.19R at ≥0.15%). This is the one place the
  5-minute chart earns its keep — but on tiny samples (n≈31–35), so treat as suggestive only.

**Practical read:** breakout is the **higher-win-rate, more-reliable, more-frequent** entry and is
the right default. Break-retest is a **lower-win-rate / high-R:R / fewer-trades** style that suits
**larger gaps** and a trader comfortable being right ~1/3 of the time for big winners; if you run it,
run it on **M5 and only on gaps ≥0.25%.** Neither is a free lunch, and all numbers here are a single
12-month window — directional, not definitive.

---

## Caveats (apply to #2 and #3)
- **12 months / 30–96 setups.** Structural conclusions (M5 doesn't help breakout; retest = low-win /
  high-R / fewer trades) are consistent across three gap thresholds and believable; the *exact*
  expectancies, especially retest, are noise-dominated.
- Retest stop still uses the session extreme (consistent with breakout); a tighter swing-based stop
  could improve retest R further — untested.
- Same flat 2pt cost; real spread widens at the open where these trigger.
- No walk-forward / Monte Carlo (see #1) — so no error bars.

### Reproduce
```
cd Gap-Retrace-Research/scripts
python3 fetch_m5.py          # 12m GER40 M5 -> ../data/GER40_M5_12m.csv
python3 compare_entries.py   # M15 vs M5 x breakout vs retest -> ../analysis/entry_experiment.txt
python3 make_chart_entry.py  # fig4_entry_experiment.png
```
