# Phase 2c — Cross-Instrument Fade Test (was the edge better elsewhere?)

**Date:** 2026-07-04 · Answers: the M5 / break-retest work was GER40-only — were results better on
another instrument, and should we drill the same way into those?

---

## The gap this fills
Until now, **only gap *statistics*** were computed for the non-GER40 instruments (Phase-1 daily
fill-rates; Phase-2 US RTH fill-rates). The **fade *strategy* P&L** — win%, expectancy, R — had
**only ever been run on GER40**, and the M5 + break-retest drill-downs were GER40-only.

Because US indices barely gap intra-week, their tradeable gap is the **RTH cash open (09:30-ET)**,
not an overnight void. So to compare fairly, `rth_fade_backtest.py` runs the **identical entry
engine** (30-min warmup → breakout close-back-through-open → stop beyond session extreme → target =
prior close → 2pt cost) **anchored to each instrument's RTH session** (GER40 = Xetra, US500/US30 =
NYSE cash), 2 years, M15.

## Result — GER40 wins the *strategy* by a wide margin

| Instrument (RTH-anchored) | best config | N | win% | expectancy | +quarters |
|---|---|---|---|---|---|
| **GER40** | breakout ≥0.15% skip-wknd | 157 | 59% | **+0.114R** | 6/9 |
| GER40 | break-retest ≥0.25% all | 117 | 40% | **+0.165R** | 4/8 |
| US500 | breakout ≥0.25% skip-wknd | 98 | 57% | +0.052R | 5/8 |
| US30 | *every* config | — | — | **negative** | mostly 0–2/9 |

- **GER40 is positive in every configuration** (+0.09 to +0.17R). On its **native overnight-void
  anchor** it's stronger still: **+0.247R, 59% win, +12R** (the Phase-2 recommended config).
- **US500 is marginal-to-negative** — only scrapes positive (+0.05–0.07R) on the ≥0.25% skip-weekend
  cells. Not a reliable edge.
- **US30 is negative almost everywhere** (−0.05 to −0.20R; **0/9 positive quarters** on the filtered
  configs) — the **worst**, despite having the **best** daily fill statistics (70.5%) in Phase 1.

## The lesson: fill probability ≠ fade profitability
US30/US500 *look* best on gap statistics (high fill %, strong fade bias) but **lose** the mechanical
fade. Why: US cash-open gaps fill **fast** (Phase-2b: median 0–15 min). By the time the 30-min
warmup + confirmation trigger fires, the fill has **already happened** — so the entry catches only
the *gap-and-go remainder* and gets stopped. GER40's genuine **~4.5-hour overnight void** produces a
gap that price works back into more slowly, leaving **room for the confirmation entry to be filled
before the target is reached.** The edge lives in the *path*, not the endpoint.

## Answers to the question
1. **Yes — M5 and break-retest were GER40-only**, and so was the whole fade-strategy P&L.
2. **No — results are not better on the other instruments; they're worse** for the tradeable
   strategy. The instruments with better *statistics* (US30, US500) fail the *strategy* test.
3. **So we should NOT spend effort drilling M5 / break-retest into US500 or US30** — there's no base
   M15 edge there to refine. Refinement effort belongs where the base edge exists: **GER40**.
   - Bonus: GER40's **RTH (Xetra-open) anchor is also positive and fires ~3× more often** (157 vs 49
     trades) than its overnight anchor — worth trading *both* GER40 gap types, at lower per-trade edge.
4. **The one untested instrument that could rival GER40 is UK100** — the other European index with a
   genuine nightly void. It was *not* included here (no 2y M15 pulled yet). If you want breadth,
   UK100 is the single most logical addition; the US indices are not.

## Caveats
- RTH anchoring uses CFD prices windowed to cash hours (not the cash auction print) — directionally
  right, first-minute dynamics may differ.
- Same 2pt flat cost; US cash-open spread is often wider at 09:30-ET, which would hurt the US
  numbers *further*.
- Still one 2-year sample, no walk-forward/Monte-Carlo error bars (see Phase-2b §1).

### Reproduce
```
cd Gap-Retrace-Research/scripts
python3 rth_fade_backtest.py   # -> ../analysis/cross_instrument_fade.txt
```
