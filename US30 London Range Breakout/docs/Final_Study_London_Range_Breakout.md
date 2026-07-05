# London Range Breakout — Comprehensive Research Study
## US30 vs NAS100 · 3 years of 5-minute data · cTrader

**Analyst:** Quant research (Claude) · **Date:** 2026-07-05
**Data:** cTrader (Pepperstone UK GBP spread-bet demo). M5 OHLCV + tick volume,
**2023-07-02 → 2026-07-03**, 212,296 US30 bars / 212,383 NAS100 bars, **938 trading days**.
All timestamps UTC, windowed in exchange-local time with DST (Europe/London, America/New_York).

> **Bottom line.** The strategy *as originally specified* (50pt stop / 100pt target,
> break from 09:30 ET) is **not viable** over 3 years (US30 PF 1.04, NAS100 PF 1.17).
> Two rule changes you introduced — **wait until 10:00 ET** and **require high volume** —
> plus the refinement this study adds — **wider stops with higher R targets** — turn it
> into a **robust, every-year-profitable** edge on both instruments. **NAS100 is the
> better vehicle** on a risk-adjusted basis (PF ~1.33–1.36, ~−12R drawdown, profitable
> all 4 years, cleaner volume signal). US30 has a higher return ceiling but deeper
> drawdowns and one flat year (2024).

---

## 1. Method

- **Range:** high/low of M5 bars in a range window ending at **09:30 ET** (NY open).
- **No-trade zone:** 09:30–10:00 ET skipped (your rule; strongly validated below).
- **Entry:** from **10:00 ET**, the **first** M5 candle to *close* beyond the range that
  also passes the **volume filter** (tick volume ≥ 1.2× trailing-20 by default). One
  trade per day per direction (first qualifying breakout).
- **Exit:** stop / target per config; bar-by-bar M5 simulation to resolution; if a bar
  spans both SL and TP we assume **SL first (pessimistic)**; force-close at 16:00 ET.
- **P&L in R-multiples** (1R = the stop distance). Sizing to £ is a fixed-risk overlay
  (see §9); R keeps instruments and stop sizes comparable.

Reproducible: `scripts/` (engine `backtest.py`, sweeps `run_sweeps.py`, volume
`volume_study.py`, robustness `robustness.py`, charts `make_charts.py`). Raw data in
`data/US30/`, `data/NAS100/`. All result tables in `analysis/`.

---

## 2. The original spec fails; the rule updates fix it

Same 46-day sample, US30 (`analysis/US30_45day_rule_update_comparison.md`):

| Variant | Trades | Win% | Total R | PF |
|---|---|---|---|---|
| OLD (range 03–08 London, break from 09:30, no vol) | 28 | 25% | **−7.0** | 0.67 |
| NEW structure (range→09:30 ET, exec from 10:00 ET) | 31 | 42% | **+8.0** | 1.44 |
| NEW + high volume ≥1.2× trailing-20 | 18 | 50% | **+9.0** | 2.00 |

Over the **full 3 years**, the literal 50/100 base case is only marginally positive —
confirming the 46-day PF-2.0 was a lucky window, and that the **50pt stop is the core
weakness** (it is ~1× a single post-open M5 candle range, so it is stopped by noise):

| Instrument | Trades | Win% | Expectancy | Total R | PF | MaxDD |
|---|---|---|---|---|---|---|
| US30 base 50/2R | 493 | 32.9% | +0.024R | +11.7 | 1.04 | −26R |
| NAS100 base 50/2R | 422 | 31.0% | +0.098R | +41.3 | 1.17 | −14.5R |

**Waiting to 10:00 ET is the single most important rule.** The 09:30–10:00 window is the
noisiest of the day; breakouts taken there are mostly false. Skipping it flips the sign.

---

## 3. Session structure (range window × execution window)

Full grid in `analysis/{INST}_stage1_session.csv`. Best-performing structures:

- **US30** prefers a **tight range built just before the open (08:00–09:30 ET, the last
  90 min)** and execution 10:00–13:00 ET. A tight, recent range gives cleaner, closer
  breakout levels than a wide overnight range.
- **NAS100** prefers a **wide range (02:00–09:30 ET)** and a **short execution window
  (10:00–11:00 ET)** — most of NAS100's edge is in the first hour after the wait.

Time-of-day tick volume (`analysis/{INST}_volume_tod_profile.csv`) peaks **exactly at
10:00 ET** (US30 ~1,475 vs London ~550; NAS100 ~1,732) — so the strategy executes at the
day's liquidity peak, which is *why* the 10:00 wait works.

---

## 4. Risk structure — the biggest source of edge

Stop size × R-target sweep, on each instrument's best session window
(`analysis/{INST}_stage2_risk.csv`; heatmaps in `charts/{INST}_risk_heatmap.png`).
The base 50pt/2R is dominated across the board. Widening the stop and **raising the target
to 2.5–3.5R** is where the strategy comes alive.

**US30** (range 08:00–09:30 ET, exec 10:00–13:00 ET):

| Stop | RR | Trades | Win% | Total R | PF | MaxDD |
|---|---|---|---|---|---|---|
| fixed 75 | 3.0 | 613 | 20% | **+117** | 1.31 | −20R |
| fixed 60 | 3.5 | 613 | 20% | +124 | 1.30 | −31R |
| ATR×2.0 | 2.0 | 613 | 32% | +81 | 1.23 | **−16R** |
| ATR×2.0 | 1.5 | 613 | 42% | +78 | 1.24 | **−10.5R** |

**NAS100** (range 02:00–09:30 ET, exec 10:00–11:00 ET):

| Stop | RR | Trades | Win% | Total R | PF | MaxDD |
|---|---|---|---|---|---|---|
| fixed 40 | 3.5 | 398 | 21% | **+93** | 1.36 | −12R |
| fixed 40 | 3.0 | 398 | 25% | +85 | 1.34 | −12R |
| fixed 60 | 2.0 | 398 | 30% | +69 | 1.33 | −13R |

Note the **instrument asymmetry**: US30 wants a *wider* stop (60–75pt), NAS100 a *tighter*
one (40pt) — consistent with NAS100's cleaner post-open trend and US30's chop. Both want
**R targets well above the original 2R**: winners run further than 2× the stop often enough
that 3R–3.5R maximise expectancy despite lower hit rates.

**RR trade-off:** higher R = higher total return + PF, but lower win rate (down to ~20%),
which means **long losing streaks** and psychologically harder trading. The 30–42% win-rate
configs (US30 ATR×2.0/2.0R, NAS100 fixed60/2.0R) are the most *tradeable* compromise.

---

## 5. Volume investigation (cTrader tick volume)

Full tables in `analysis/{INST}_outcome_by_*.csv`, `_threshold_*.csv`;
charts `charts/{INST}_volume_winrate.png`.

- **The volume edge is real on NAS100, weak on US30.**
  - **NAS100:** breakout candle **≥ ~1.3× trailing-20** lifts expectancy to +0.16 to +0.23R;
    *below* 1.2× is **negative**. Pre-open-relative (> pre-open avg) and z-score confirm it
    monotonically. Requiring above-average volume is a genuine filter here.
  - **US30:** the relationship is **non-monotonic** — moderate volume is best and the
    **highest-volume quintile is slightly negative** (chasing the biggest candles hurts,
    likely exhaustion/spikes). A light filter (≥1.2×) helps; a heavy one does not.
- **Practical filter:** keep **≥1.2× trailing-20** as the base rule for both; for NAS100,
  **≥1.3–1.4×** is modestly better. Do **not** demand extreme volume (≥2×) — it starves the
  sample and, on US30, selects worse trades.
- **Caveat:** this is **tick volume** (update count), not traded contracts. It tracks
  activity well and is exactly what a live cTrader bot would see, but it is not exchange
  volume. Conclusions are internally consistent for execution on this feed.

---

## 6. Robustness (walk-forward by year)

`analysis/candidate_summary.csv`. Every recommended config is **profitable in all 4
calendar years** (2023 H2 – 2026 H1); the base 50/2R is not (US30 lost in 2024).

| Config | 2023 | 2024 | 2025 | 2026* | Yrs + |
|---|---|---|---|---|---|
| US30 base 50/2R | +1.6 | **−9.7** | +11.8 | +8.0 | 3/4 |
| US30 fixed75/3.0R | +14.8 | +10.6 | +58.5 | +32.8 | **4/4** |
| US30 ATR×2.0/2.0R | +21.5 | +1.2 | +47.4 | +11.4 | **4/4** |
| NAS100 fixed40/3.5R | +8.9 | +26.7 | +39.2 | +18.2 | **4/4** |
| NAS100 fixed60/2.0R | +17.8 | +20.7 | +19.0 | +11.4 | **4/4** |

*2026 is a half-year with few trades (18–83) and inflated ratios — do not over-weight.

**2024 was hard for US30** (base lost, fixed75 only +10.6R / PF 1.07) but fine for NAS100
(all configs +20R+). NAS100's edge is the more *consistent* across regimes.

---

## 7. US30 vs NAS100 — verdict

| Dimension | US30 | NAS100 | Winner |
|---|---|---|---|
| Best PF (robust) | 1.31 | 1.33–1.36 | NAS100 |
| Max drawdown (best cfgs) | −16 to −20R | **−12R** | NAS100 |
| Return ceiling | **+117R** | +93R | US30 |
| Consistency (yrs profitable) | 4/4 (2024 thin) | **4/4 (all strong)** | NAS100 |
| Volume filter quality | weak, non-monotonic | **clean, monotonic** | NAS100 |
| Trades to achieve it | 613 | **398** | NAS100 |
| Win rate at chosen cfg | 20–32% | 21–30% | ~tie |

**Recommendation: carry NAS100 forward as the primary instrument.** It delivers similar
absolute R to US30 in *fewer trades*, with *lower drawdown*, *more consistent* yearly
performance, and a *genuine* volume filter. US30 is a viable secondary — its higher return
ceiling (fixed75/3.0R) is real but comes with deeper drawdowns and a weaker volume signal.
Running **both** (they are correlated but not identical; entries differ day-to-day) would
diversify, but if choosing one, **NAS100**.

---

## 8. Recommended configurations

**NAS100 — primary**
- Range: **02:00 → 09:30 ET** high/low · skip 09:30–10:00 · execute **10:00–11:00 ET**
- Entry: first M5 close beyond range with **volume ≥ 1.3× trailing-20**
- Two profiles:
  - **Balanced (tradeable):** stop **60pt**, target **2.0R** → 30% win, PF 1.33, −12.9R DD, +69R
  - **Aggressive (max return):** stop **40pt**, target **3.5R** → 21% win, PF 1.36, −12R DD, +93R

**US30 — secondary**
- Range: **08:00 → 09:30 ET** (last 90 min) · skip 09:30–10:00 · execute **10:00–13:00 ET**
- Entry: first M5 close beyond range with **volume ≥ 1.2× trailing-20** (do not over-filter)
- Two profiles:
  - **Balanced:** **ATR×2.0** stop, target **2.0R** → 32% win, PF 1.23, −16R DD, +81R
  - **Aggressive:** stop **75pt**, target **3.0R** → 20% win, PF 1.31, −20R DD, +117R

---

## 9. Caveats & limitations (read before building a bot)

1. **Spread/commission not modelled.** On this spread-bet feed the entry spread is ~1–2pt
   (US30) / ~1–1.5pt (NAS100). On a 40–75pt stop that is ~0.02–0.04R drag per trade — over
   400–600 trades, roughly **−12 to −16R**. Edges survive it (PF stays > 1.2) but totals
   shrink; model it explicitly before sizing.
2. **Tick volume ≠ contract volume** (see §5).
3. **Pessimistic same-bar assumption** (SL before TP when a bar spans both) slightly
   *understates* results — real fills may be a touch better.
4. **No stop slippage** modelled; index stops can gap on news.
5. **Selection bias:** ~100 configs were swept. The yearly walk-forward (§6) mitigates but
   does not eliminate this — genuine out-of-sample is *forward* testing on demo.
6. **Low win rates (20–32%)** demand discipline: 8–12 trade losing streaks are normal at
   3R+. The balanced (30–32% win) profiles are easier to execute.
7. **First-qualifying-breakout-per-day only** — taking every breakout was not tested here
   as the base rule (it inflates whipsaw losses; see Phase 1 decision).

---

## 10. Next steps

1. **Model spread/commission** in the engine and re-confirm expectancy (quick).
2. **Forward-test on demo** the two NAS100 profiles (and US30 balanced) via the cTrader
   MCP for 4–8 weeks — true out-of-sample before any capital.
3. Optional edge extensions to test: (a) trailing stop / partial at 1R + runner, (b) skip
   high-impact news days, (c) range-width filter (avoid the widest/narrowest range days),
   (d) require the breakout candle to close in the top/bottom third of its range.
4. **Decision gate:** if demo forward-test holds PF > 1.2 with the modelled costs, build the
   bot on **NAS100 balanced (60pt / 2.0R)** first.

*All figures reproducible from `scripts/` against the stored data in `data/`.*
