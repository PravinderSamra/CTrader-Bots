# Phase 2 — Longer History, Costs, US Cash-Open Gaps, a Coded Rule & a cBot

**Date:** 2026-07-04 · **Status:** Phase 2 complete
**Builds on:** `Phase1_Gap_Retrace_Research.md` · **Primary instrument:** GER40 (DAX)

> Phase 1 established the mechanics and the direction of the edge on ~5.4 months. Phase 2 does the
> honest work: **2 years** of intraday data, a **cost model**, a **precisely coded rule**,
> **walk-forward** across 8 quarters, the **US cash-open (RTH) gaps** the CFD hides, and a
> **compilable cBot**. The headline: the edge is **real but modest and regime-dependent**, and it
> **concentrates in weekday overnight gaps of ≥0.25%** — the naive "fade every gap" is breakeven.

---

## 0. TL;DR — what changed from Phase 1

1. **The 5.4-month result was optimistic.** On the full **2 years**, the naive fade of all GER40
   gaps ≥0.15% is only **+0.03R / trade (~breakeven after 2pt costs)**. The favourable +0.23R came
   from one benign regime (2026 H1).
2. **The edge is real once you filter it correctly.** Two *mechanistically-justified* filters —
   **(a) skip weekend/holiday gaps, (b) require gap ≥0.25%** — lift it to **+0.247R/trade, 59% win,
   +12R over 49 trades, positive in 6 of 8 quarters.**
3. **Weekend gaps are a *losing* fade** (−0.12R over 2y). They're bigger, news-driven, fill less
   (Phase 1: 73% vs 88%) and overshoot — mechanical M15 fades get stopped. **Trade weekday
   overnight gaps only.**
4. **US cash-open (RTH) gaps DO exist and fill fast.** Reconstructing the 09:30-ET session recovers
   the classic opening gap the CFD hides: **US500 gaps fill ~62% same-session, median time-to-fill
   ~15 minutes**, with the same "small fills / big runs" size decay (87% → 21%).
5. **Deliverables:** a coded, un-optimised strategy (`gapfade_strategy.py`) that the backtest and
   the **`cbot/GapFadeBot.cs`** both implement identically, plus walk-forward and RTH studies.

⚠️ **Honesty flag:** even the recommended config is **flat-to-small in most quarters** with the bulk
of its 2-year profit from a single strong quarter (see `fig3` panel c). This is a **small,
regime-dependent mean-reversion edge**, not a steady equity curve. Size and expectations accordingly.

---

## 1. Longer history + cost model (item 1)

Downloaded **2 years of M15** for GER40, US500, US30 (`../data/*_M15_2y.csv`; GER40 = 40,726 bars).
All backtests deduct **2 index points per round trip** (spread + slippage proxy; GER40 spread is
~1–2 pts) expressed in R against the trade's own stop distance.

**GER40, 2y, coded fade, gap ≥0.15%, all gaps:** 153 trades, **50.3% win, +0.03R, +4.2R total.**
Breakeven. The size- and day-of-week structure underneath it is where the signal is (below).

---

## 2. The coded rule (item 3) — exact, shared by backtest and bot

Per session (sessions split on GER40's nightly void; see Phase 1 §2):

```
prior_close/high/low = prior session close / max-high / min-low
gap      = session_open - prior_close ;  gap_pct = gap/prior_close*100
qualify  : MIN_GAP_PCT <= |gap_pct| <= MAX_GAP_PCT   (default 0.25% .. 1.0%)
bias     : gap up -> SHORT the fade ; gap down -> LONG the fade
warmup   : ignore first WARMUP bars (default 2 = 30 min) — let the gap show its extreme
TRIGGER  : first M15 bar (within MAX_WAIT) that CLOSES back through the SESSION OPEN
           in the fade direction  (gap up -> close < open -> SHORT)
stop     : beyond the running session extreme +/- STOP_BUF_PCT*gap (default 10%)
target   : prior_close (the fill)
exit     : TP/SL by intra-bar touch (adverse-first if a bar spans both) else mark-to-close
```

**Design note that mattered:** an earlier variant that entered on a *break of the opening range*
(chasing the move down) tested **negative**. Selling into the **rejection back through the open**
(near the highs, tight stop, full distance to the fill) is what carries the edge. The coded rule
uses the latter.

### Parameter sensitivity (2y GER40, expectancy R / #trades) — robustness, not optimisation
```
 MIN_GAP \ WARMUP        1            2            4
    0.10%            -0.04/219    -0.04/218    -0.15/214
    0.15%            -0.01/154    +0.03/153    -0.14/155
    0.25%            +0.12/82     +0.17/83     -0.03/83
```
Two clean reads: **WARMUP≈2 (30 min)** is the sweet spot (waiting 4 bars misses the fill), and
**expectancy rises with the gap-size floor.** No single lucky cell — the gradient is smooth.

---

## 3. Where the edge actually lives (items 1 + 4)

**Filter comparison (2y GER40, WARMUP=2, 2pt cost).** Figure: `../analysis/fig3_strategy_walkforward.png`.

| Config | N | Win% | Expectancy | Total R | +Quarters |
|---|---|---|---|---|---|
| all gaps ≥0.15% | 153 | 50.3% | +0.03R | +4.2R | 5/8 |
| all gaps ≥0.25% | 83 | 53.0% | +0.17R | +14.3R | 4/8 |
| **weekday-only ≥0.25% (RECOMMENDED)** | **49** | **59.2%** | **+0.247R** | **+12.1R** | **6/8** |
| weekend-only ≥0.15% (**avoid**) | 50 | 40.0% | −0.12R | −6.0R | 2/8 |

**Day-of-week (2y, gap ≥0.25%):** Monday (= weekend gap) is the clear loser (37% win, −0.08R). Tue
and Fri are strongest; Wed/Thu middling. The finer day-of-week splits are **small samples (n≈10–19)
and noisy** — don't over-fit them. The robust, mechanistically-sound cut is simply **weekday vs
weekend**, plus the **gap-size floor**. Both filters were justifiable *before* seeing the split
(Phase 1 independently showed weekend gaps fill less and big gaps run), so this is not curve-fitting.

**Why weekend gaps lose the fade:** larger (median 0.44% vs 0.24%), driven by real weekend news, and
they overshoot the fill hard — the mechanical stop beyond the open-session extreme is too tight for
that volatility. If you want to trade weekend gaps at all, treat them as a *separate* playbook with
a much wider stop and smaller size; do not run the weekday rule on them.

---

## 4. US cash-open (RTH) gaps — the ones the CFD hides (item 2)

Phase 1 §2 showed a US-index **CFD** barely gaps intra-week because it trades through the overnight
session. But the **classic 09:30-ET opening gap is real** — it just needs a *regular-trading-hours*
lens. We reconstruct the RTH session (09:30–16:00 America/New_York, DST-correct) from the same
cTrader feed and measure the gap of each RTH open vs the **prior RTH close** (`rth_gap_study.py`).

**US500 (2y, 495 RTH sessions):**
- RTH gaps are **near-daily** (493 of 495 sessions gapped) — vs the CFD's ~4% of weekday rolls.
- **Fill rate: 61.7%** all / **53.3%** for gaps ≥0.1%. **Median time-to-fill ≈ 15 min** — US cash
  gaps fill *fast*, early in the session (much faster than GER40's ~90 min overnight fill).
- Same size decay: **<0.25% fill 87%, 0.25–0.5% 55%, 0.5–1% 33%, >1% 21%.**
- Mild fade bias (~53%).

**US30 (2y, 495 RTH sessions):** materially the same picture — RTH gaps near-daily, **fill 65.0%**
all / **55.1%** for ≥0.1% gaps, **median time-to-fill 0–30 min** (often filled inside the first M15
bar), ~50% fade. US30 fills a touch more often and faster than US500 (consistent with Phase 1, where
US30 had the highest daily fill rate). Both US indices behave as textbook fast-fill opening gaps.

**Practical implication:** if you specifically want the *stock-style* opening-gap-fill, trade it on
the **US cash open** — but note (a) you are trading a *reference level* on a continuous CFD, not a
literal void, and (b) the fill is a **first-15–45-minute** event, so this is a fast, opening-drive
play, not the patient overnight fade GER40 offers. Same size filter applies: **skip gaps >0.5–1%.**

---

## 5. The cBot (item 5) — `cbot/GapFadeBot.cs`

A single-file, compilable cTrader Automate robot that implements the coded rule **exactly**, with
the research defaults baked in:

- Runs on an **M15 chart**; pulls prior-day H/L/C from the Daily series.
- Detects the new session, computes the gap, **skips weekend/holiday gaps** (`SkipWeekendGaps=true`)
  and gaps outside **0.25%–1.0%**.
- **Warmup 2 bars**, then enters market on the **close-back-through-open** trigger.
- **Stop** beyond the session extreme + 10% buffer; **TP** at the prior-day close.
- **Risk sizing:** % of equity (default 0.5%) or fixed cash, with a lot cap; uses
  `Symbol.NormalizeVolumeInUnits`/`PipValue` so it sizes correctly across instrument classes.
- Optional flat-by hour, chart labels (draws the fill target + PDH/PDL), and logging.
- `AccessRights.None`, `TimeZone = UTC`.

**Before live use:** compile in cTrader, run its **built-in backtester/optimiser** on GER40 M15 to
reproduce these numbers on your broker's exact spread/fills, then demo it. The Python backtest is a
faithful model but the platform fill engine is the source of truth. Parameters map 1:1 to the
`gapfade_strategy.py` defaults so results should line up.

---

## 6. Honest limitations & what would strengthen it
- **2 years, one instrument-regime.** ~24 recommended trades/year — the sample is still modest and
  the equity is lumpy (one quarter dominates). Treat expectancy as ~+0.15–0.25R with wide error bars.
- **No explicit news filter.** Weekend-gap exclusion removes the worst of it, but a CPI/ECB/NFP
  calendar filter (skip or widen on high-impact days) is the obvious next gain (partly item 4, not
  yet automated — needs an events feed).
- **Costs are a flat 2pt proxy.** Real spread widens at the session open exactly when we trade —
  validate on the platform backtester with live spread.
- **Adverse-first tie-breaking** makes the backtest conservative; live M5 fills may be slightly
  better (small positive bias not claimed here).
- **RTH study uses CFD prices windowed to cash hours**, not the cash index auction print — directionally
  correct, but the very first-minute fill dynamics on the real cash open may differ.

## 7. Suggested Phase 3
1. Compile & optimise `GapFadeBot` in the cTrader backtester on GER40; reconcile with Python.
2. Add an economic-calendar filter (skip high-impact days / widen stops).
3. Extend to a **US500 RTH** variant of the bot (session-open-anchored, fast fill, tighter time-stop).
4. Portfolio it: GER40 weekday-overnight + US500 RTH are largely independent gap streams.
5. Forward-test on demo for a quarter before any capital.

---

### Reproduce
```
cd Gap-Retrace-Research/scripts
python3 fetch_phase2.py         # 2y M15 for GER40, US500, US30 -> ../data
python3 gapfade_strategy.py     # coded rule, walk-forward, sensitivity -> ../analysis/strategy_GER40.txt
python3 rth_gap_study.py        # US cash-open gap study -> ../analysis/rth_gap_*.txt
python3 make_charts_phase2.py   # fig3_strategy_walkforward.png
```
