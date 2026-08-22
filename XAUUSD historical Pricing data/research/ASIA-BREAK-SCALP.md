# Deep Dive: Asia-Range Break → Pullback → Continuation Scalp (1m)

Requested follow-up study. Scripts: `scripts/06_asia_pullback.py` (full grid, walk-forward, Monte Carlo) and `scripts/07_ny_break_scalp.py` (the surviving variant). Raw output archived in `output/`. Costs $0.40/oz round trip throughout. **R = P&L ÷ actual stop distance** (what you risk is what R is measured against).

---

## 1. The headline result — read this first

**The generic version of this strategy — mark Asia, trade the first break's pullback whenever it comes — LOSES money. All 12 tested configurations were negative** (avg −0.03R to −0.23R per trade, every combination of stop width, take-profit and range filter). The walk-forward confirmed it (−0.10R/trade out-of-sample) and Monte Carlo put the probability of a losing year at 77%.

**The reason is a selection effect:** requiring a pullback filters you *into* the weak breaks. The 70% close-through stat from the main report includes all the strong breaks that never look back — the retest days are disproportionately the failures. On top of that, **London breaks are the entire loss**: 923 London-break pullback trades averaged −0.09R, while 188 NY-break trades averaged **+0.13R**. London breaks the range early, pulls back, and dies or reverses; when a range *survives all of London* and only breaks in the NY session, the break is real.

So the answer to your session question is: **it has total bearing. London-break pullbacks are the losing trade. Only the NY-session break carries edge.**

## 2. The tradeable version — step-by-step (UK clock)

> UK summer times shown; subtract 1h in winter for the UTC-anchored steps.

1. **23:00 (11pm) → 08:00** — Asia builds its range. At **08:00**, mark **Asia High (AH)** and **Asia Low (AL)**. Range = AH − AL.
2. **08:00 → 13:00 (London morning): DO NOTHING except watch one thing** — does a 1m candle *close* outside AH/AL? If yes → **no trade today** (this is the disqualifier, ~77% of days). If London respects the range all morning, you have a live setup.
3. **13:00 → 17:00 (NY window): wait for the break.** First 1m **close** beyond AH (long setup) or AL (short setup). Wicks through don't count.
4. **Wait for the pullback:** after the break candle, price must trade back **to the broken level** within **2 hours**. No pullback = no trade (about 10% of breaks never come back — let them go).
5. **Entry:** limit order **at the level** (AH for longs / AL for shorts). The tested "confirmation" variant (wait for a 1m close back beyond the level after the touch) performed almost identically (+0.11R vs +0.13R) — use it if you prefer seeing the level hold; the limit gets a better price, the confirmation gets a better fill rate psychologically.
6. **Stop:** the **middle of the Asian range** (level − 0.5 × range for longs). Non-negotiable placement — the 0.25×-range stop version flipped the system negative (−0.005R). Your risk per trade = 0.5 × Asia range.
7. **Exit:** **no take-profit; hold to 21:55 UK, flat.** TPs at 1.5R (+0.10R) and 2R (+0.07R) both underperformed holding (+0.13R). If you must manage, take a partial at 1.5R and let the rest run — but the backtest says the runner is where the money is.
8. **One trade per day, maximum.** No re-entries after a stop-out.
9. **Sizing: risk a fixed % per trade** (see §5); position = risk £ ÷ (0.5 × Asia range in $) ÷ oz-value.

## 3. Sample results (2021-07 → 2026-07, n = 188 trades)

| Metric | Value |
|---|---|
| Frequency | ~0.7 trades/week (208 qualifying days in 5 years; ~10% no-pullback) |
| Win rate | 46.3% |
| Avg winner / loser | +1.31R / −0.90R (losers < 1R because many are time-exits, not stops) |
| **Expectancy** | **+0.125R per trade** |
| Total | +23.5R over 5 years |
| Max drawdown (historical) | −9.5R |
| Per year | 2021: −6.1R · 2022: +4.6R · 2023: +9.6R · 2024: +3.6R · 2025: +7.5R · 2026 H1: +4.2R |

**Positive every year except 2021** (12 trades, small sample, ranging market). 2024–26 subset: 49.6% win, +0.133R avg, maxDD −6.0R.

**Long/short asymmetry you must know about:** longs +0.28R avg (52% win, n=102); **shorts −0.06R avg** (40% win, n=86). In a 5-year bull market that's expected — but it means the honest version of this system so far is close to *long-only*. Options: trade long-only (halves frequency to ~1 per fortnight), or trade shorts at half size until they prove themselves in a bear regime.

## 4. Monte Carlo (5,000 bootstrap years, 37 trades/year, resampled from the 188 real trades)

| Percentile | Annual return | Max drawdown |
|---|---|---|
| p5 (bad luck) | −10R | −13.1R |
| p25 | −2R | −8.7R |
| **Median** | **+4R** | **−6.3R** |
| p75 | +11R | — |
| p95 (good luck) | +20R | — |
| P(losing year) | **32%** | |

Longest losing streak: median 5, p95 = 9 consecutive losers. Using only 2024–26 trades (46/yr): median year +6R, P(losing year) 24%, median maxDD −5.9R.

**R per day / month:**
- Per *trading* day (when a trade fires): +0.125R average — but only ~1 setup every 7 calendar days.
- **Per month: mean +0.40R, median ≈ 0, best +6.4R, worst −4.0R, only 48% of months positive.** This is the crucial expectation-setting number: most months this strategy does roughly nothing; a handful of strong months per year carry the whole edge.

**Translated to account % at sensible risk:**

| Risk/trade | Median year | Median maxDD | Bad-luck (p5) maxDD |
|---|---|---|---|
| 0.5% | +2% | −3.2% | −6.6% |
| 1.0% | +4% | −6.3% | −13.1% |
| 2.0% | +8% | −12.6% | −26.2% |

## 5. Walk-forward result (for transparency)

The walk-forward in script 06 (best config chosen each year using only prior years, across all sessions) was **negative** (−0.10R/trade OOS) — because the config selector was choosing among variants that all included the London-break poison. The NY-only refinement was identified from the session split *within* this sample, which makes it partly in-sample knowledge. Its year-by-year consistency (positive 5 of 6 years, improving in the newest regime) is encouraging, but treat +0.13R as an optimistic estimate and the MC's 32% losing-year probability as real.

## 6. My desk verdict — how I'd actually pursue this

1. **Trade it, small, as a satellite** — 0.5–1% risk, long-bias, exactly as specified in §2. It is a genuine setup with a clean invalidation story (range survived London = positional energy stored; NY break = release).
2. **Don't make it your primary.** At ~3 trades/month and +0.40R/month average, it cannot be a living. Your primary NY-session vehicle should remain the **13:30 ORB (+1.74R/month average, 5× the frequency)**; this Asia-level trade is the *complement* that fires on the days the ORB often overlaps with anyway — when both trigger the same direction, that's your A+ day.
3. **Never take the London-break pullback** — that's the single most valuable sentence in this study. 923 trades, −0.09R average, five years of proof.
4. **Track shorts separately** from day one. If gold enters a genuine bear regime the short side may come alive; the current stats don't yet justify full size.
5. Re-run `07_ny_break_scalp.py` quarterly. Kill criterion: rolling-50-trade expectancy below zero.
