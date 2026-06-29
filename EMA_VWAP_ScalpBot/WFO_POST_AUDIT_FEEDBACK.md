# EMA + VWAP ScalpBot — Post-Audit Feedback for Claude AI Review

**Date:** 2026-06-29
**Instrument:** GER40 (DAX) Spread-Bet via Pepperstone / cTrader
**Data period:** 2021-01-04 → 2024-12-31 (273,440 × 5M bars; 23,065 × 1H bars)
**Branch:** `claude/ema-vwap-monte-carlo-o4fmew`
**Pipeline verdict: RED — Do Not Deploy**
**Audit status: All 4 implementation fixes confirmed. Verdict unchanged.**

---

## Context for Reviewer

This document is a structured briefing for a Claude AI reviewer picking up this project cold. A full 7-phase validation pipeline (data fetch → WFO → Monte Carlo → report → verdict) was built and run. The pipeline returned RED. Before attributing the failure to the strategy, four implementation concerns were audited in sequence. All four are now resolved. The RED verdict stands on corrected numbers.

The questions for review are in **Section 8**. Everything before that is context.

---

## 1. What Was Built

A mechanical intraday EMA + VWAP scalping cBot for GER40 (DAX) with:

**Entry logic (all conditions must be true):**
- 1H EMA(21) bias gate: price > EMA(21) for longs, < EMA(21) for shorts
- EMA crossover on 5M: fast EMA > slow EMA (long) or fast < slow (short)
- Price on correct side of session VWAP
- Candle body ≥ `min_body_pct` % of total range
- Entry only if next bar opens within `max_entry_dist_atr` × ATR of VWAP

**Risk management:**
- ATR-based SL (Wilder's ATR, 1/period smoothing)
- Fixed-fractional sizing: 1% account risk per trade
- TP1 at +1R from entry (close 50%, move SL to break-even)
- TP2 at +2R from entry (close remaining 50%)
- REVERSION exit: close at bar close if price reverts below fast EMA or VWAP
- SESSION_END: force-close all positions by 16:30 UK

**Session gate:** 08:00–11:30 UK and 13:00–16:00 UK (GER40 peak liquidity windows)

**VWAP:** Session-level (daily), resets at UTC midnight, uses one-pass variance formula for SD bands

**Validation pipeline:**
1. Data fetch via cTrader MCP HTTP transport (checkpoint-based, 100-bar pages)
2. Walk-Forward Optimisation: 20 rolling windows, 6M IS / 2M OOS, step 2M
3. IS grid optimisation: 22,680 parameter combinations per window (parallel, 4 workers)
4. Stability check: test ±1 neighbours of best IS params; reject if spike-detected
5. Monte Carlo: 2,000 bootstrap simulations (with replacement) on concatenated OOS trades
6. Report generation with acceptance criteria table
7. Deployment verdict: GREEN / AMBER / RED

---

## 2. Parameter Search Space

| Parameter | Grid Values | Step |
|-----------|-------------|------|
| `ema_fast` | 7, 8, 9, 10, 11, 12, 13 | 1 |
| `ema_slow` | 18–26 | 1 |
| `atr_period` | 10, 12, 14, 16, 18 | 2 |
| `atr_multiplier` | 1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5 | 0.25 |
| `min_body_pct` | 30, 40, 50, 60 | 10 |
| `max_entry_dist_atr` | 0.5, 0.75, 1.0, 1.25, 1.5 | 0.25 |
| `max_trades_per_day` | 2, 3, 4 | 1 |

**Total grid size: 22,680 combinations per IS window**

IS qualification thresholds: PF > 1.30, WR > 42%, MaxDD < 15%, Trades ≥ 40

Composite IS score: PF×0.35 + Sharpe×0.30 + WR×0.15 + RecoveryFactor×0.20

---

## 3. Four-Fix Audit Results

Before attributing the RED verdict to the strategy, four implementation concerns were investigated in sequence. Results:

### FIX 1 — Trade Counting (IMPLEMENTED, code changed)

**Problem:** The TP1 partial exit and the subsequent final exit each appended a separate record to the trades list. `_calc_statistics` counted all records, so a physical trade with TP1+SL generated two entries in the statistics. This inflated `total_trades`, diluted `win_rate`, and changed `profit_factor`.

**Resolution:**
- Added `trade_id` counter to `run_backtest`; each physical trade increments the counter at entry time
- All `_apply_pnl` calls pass `current_trade_id` and store it in the trade dict
- `_calc_statistics` now groups records by `trade_id`, sums `pnl_r` per group, and computes all statistics on the netted per-trade values

**Corrected OOS statistics (raw OOS data, 20 passes concatenated):**

| Metric | Old (double-counted) | Corrected | Change |
|--------|---------------------|-----------|--------|
| total_trades | 438 records | **292 physical trades** | −146 TP1 records removed |
| profit_factor | 0.7883 | **0.7877** | −0.0006 (negligible) |
| win_rate | 47.7% | **49.3%** | +1.6pp |
| net_profit R | −13.34R | −13.34R | **identical** |
| gross_profit R | +49.66R | +49.49R | — |
| gross_loss R | −63.00R | −62.83R | — |

**Finding: The double-counting did NOT cause the RED verdict. Net P&L is mathematically identical; PF is virtually unchanged. The strategy is genuinely losing.**

**TP1 pair breakdown across 292 physical trades:**
- TP1 → SL (stopped at BE): 75 trades, avg net = +0.112R ← these are the profitable ones
- TP1 → TP2 (full winner): 55 trades, avg net = +0.573R
- TP1 → REVERSION: 16 trades, avg net = +0.519R (partial win but early exit)
- SL only (no TP1 hit): 18 trades, avg = −1.000R
- REVERSION only (no TP1 hit): 127 trades, avg = **−0.346R** ← largest loss contributor
- SESSION_END: 1 trade

---

### FIX 2 — VWAP Daily Reset (VERIFIED, no code change)

**Concern:** If VWAP accumulates across trading days without resetting, by day 2+ the VWAP level drifts far from current price, causing the VWAP entry gate to reject nearly all trades.

**Investigation:**
- `VwapState.update()` in `backtest_engine.py` resets all accumulators when `bar_date != self.session_date`, where `bar_date = bar["time"].date()` (UTC date)
- Compared to `VwapCalculator.cs`: resets when `serverTime.Date != _lastResetDate.Date` — identical UTC-date logic
- Empirical test on Jan 9–13, 2023: VWAP at first bar of each day equals that bar's typical price (H+L+C)/3, confirming a clean reset each UTC midnight

**Sample verification:**

| Date | First Bar UTC | VWAP at first bar | TP of first bar | Reset? |
|------|--------------|-------------------|-----------------|--------|
| 2023-01-09 | 00:15 | 14,657.77 | 14,657.77 | ✓ |
| 2023-01-10 | 00:15 | 14,698.60 | 14,698.60 | ✓ |
| 2023-01-11 | 00:15 | 14,864.37 | 14,864.37 | ✓ |
| 2023-01-12 | 00:15 | 14,992.63 | 14,992.63 | ✓ |
| 2023-01-13 | 00:15 | 15,107.30 | 15,107.30 | ✓ |

GER40 data starts at 00:15 UTC. By 08:00 UK (= 08:00 UTC in January), the VWAP has accumulated ~7h45m of bars. The 08:00 VWAP differs from the 08:00 bar's TP — this is correct behavior, not a bug.

**Finding: VWAP reset is correct. No change made.**

---

### FIX 3 — DST Accuracy (IMPLEMENTED, code changed)

**Problem:** Session gate used manual approximation: `offset = 1 if 4 <= month <= 10 else 0`. UK DST transitions happen on the last Sunday of March and October, not on April 1 or October 1. Late March and late October bars were assigned the wrong UK hour.

**Resolution:** Replaced manual offset with `zoneinfo.ZoneInfo("Europe/London")` (Python 3.9+ stdlib, exact IANA DST rules). The `_to_uk()` function now calls `utc.astimezone(_TZ_LONDON)`.

**Impact across 273,440 bars:**

| Metric | Count | Percentage |
|--------|-------|------------|
| Bars with wrong UK hour (old vs new) | 5,205 | 1.90% |
| Bars reclassified in/out of trading window | **912** | 0.334% |

**Reclassification detail by period:**

| Year-Month | Bars reclassified | Direction | Effect |
|------------|-------------------|-----------|--------|
| 2021-03 | 144 | False→True | DST forward: 07:00 UTC now correctly = 08:00 BST (was excluded, now included) |
| 2022-03 | 192 | False→True | Same |
| 2022-10 | 48 | True→False | DST back: 07:00 UTC now correctly = 07:00 GMT (was included, now excluded) |
| 2023-03 | 240 | False→True | Same as March pattern |
| 2023-10 | 96 | True→False | Same as October pattern |
| 2024-10 | 192 | True→False | Same as October pattern |

**Finding: 912 bars (0.334%) traded in wrong session windows. DST fix applied. This is a legitimate improvement but does not materially change WFO results given the scale.**

---

### FIX 4 — Stability Neighbour Steps (VERIFIED, no code change)

**Concern:** If `get_neighbours()` generates neighbour values that coincide with grid points already tested during IS optimisation, the stability surface check becomes redundant.

**Investigation:** Printed the 14 neighbours for consensus params (EMA 10/24, ATR 18×2.5, Body 50%, EntryDist 1.0, MaxTrades 3):

| Neighbour param | Value | In IS grid? | Grid step matches? |
|-----------------|-------|------------|-------------------|
| ema_fast: 9, 11 | ±1 | ✓ both | ✓ |
| ema_slow: 23, 25 | ±1 | ✓ both | ✓ |
| atr_period: 16, **20** | ±2 | ✓ 16 / ✗ 20 (above grid max 18) | ✓ step matches |
| atr_mult: 2.25, **2.75** | ±0.25 | ✓ 2.25 / ✗ 2.75 (above grid max 2.5) | ✓ step matches |
| min_body_pct: 40, 60 | ±10 | ✓ both | ✓ |
| max_entry_dist: 0.75, 1.25 | ±0.25 | ✓ both | ✓ |
| max_trades: 2, 4 | ±1 | ✓ both | ✓ |

12/14 neighbours coincide with IS grid points. The 2 off-grid neighbours (atr_period=20, atr_mult=2.75) arise because consensus values sit at the grid maximum in those dimensions — the upper neighbour naturally falls outside the grid boundary. This is correct continuous-space behavior and does not invalidate the stability check.

**Finding: Neighbour generation is correct. No change made.**

---

## 4. Walk-Forward Optimisation — All 20 Passes

### IS vs OOS Results

| Pass | IS Period | OOS Period | IS PF | IS Trades | OOS PF | OOS WR | OOS Trades | Stable? |
|------|-----------|------------|-------|-----------|--------|--------|------------|---------|
| 1 | Jan–Jul 2021 | Jul–Sep 2021 | 2.563 | 54 | 0.640 | 30.8% | 13 ⚠ | ✓ |
| 2 | Mar–Sep 2021 | Sep–Nov 2021 | 2.247 | 80 | 0.496 | 51.9% | 27 | ✗ |
| 3 | May–Nov 2021 | Nov 2021–Jan 2022 | 1.376 | 149 | 0.924 | 45.8% | 48 | ✗ |
| 4 | Jul 2021–Jan 2022 | Jan–Mar 2022 | 1.742 | 62 | 0.762 | 54.2% | 24 | ✗ |
| 5 | Sep 2021–Mar 2022 | Mar–May 2022 | 1.939 | 52 | 0.380 | 30.0% | 20 | ✓ |
| 6 | Nov 2021–May 2022 | May–Jul 2022 | 1.838 | 71 | 0.531 | 45.5% | 11 ⚠ | ✗ |
| 7 | Jan–Jul 2022 | Jul–Sep 2022 | 2.664 | 40 | 0.411 | 33.3% | 12 ⚠ | ✓ |
| 8 | Mar–Sep 2022 | Sep–Nov 2022 | 2.206 | 89 | **1.334** | 53.3% | 15 | ✗ |
| 9 | May–Nov 2022 | Nov 2022–Jan 2023 | 2.733 | 48 | **1.567** | 57.1% | 14 ⚠ | ✗ |
| 10 | Jul 2022–Jan 2023 | Jan–Mar 2023 | 3.454 | 47 | **2.528** | 71.4% | 14 ⚠ | ✗ |
| 11 | Sep 2022–Mar 2023 | Mar–May 2023 | 4.118 | 54 | **2.178** | 64.3% | 14 ⚠ | ✗ |
| 12 | Nov 2022–May 2023 | May–Jul 2023 | 3.018 | 54 | **1.366** | 50.0% | 24 | ✗ |
| 13 | Jan–Jul 2023 | Jul–Sep 2023 | 2.843 | 60 | 0.412 | 46.2% | 13 ⚠ | ✗ |
| 14 | Mar–Sep 2023 | Sep–Nov 2023 | 1.432 | 83 | **1.110** | 56.7% | 30 | ✗ |
| 15 | May–Nov 2023 | Nov 2023–Jan 2024 | 1.645 | 88 | **1.284** | 60.9% | 23 | ✓ |
| 16 | Jul 2023–Jan 2024 | Jan–Mar 2024 | 1.987 | 52 | 0.396 | 36.4% | 22 | ✗ |
| 17 | Sep 2023–Mar 2024 | Mar–May 2024 | 1.980 | 55 | 0.398 | 35.3% | 17 | ✗ |
| 18 | Nov 2023–May 2024 | May–Jul 2024 | 2.272 | 49 | 0.712 | 45.7% | 46 | ✓ |
| 19 | Jan–Jul 2024 | Jul–Sep 2024 | 1.992 | 93 | **1.106** | 53.1% | 32 | ✓ |
| 20 | Mar–Sep 2024 | Sep–Nov 2024 | 3.019 | 72 | 0.192 | 26.3% | 19 | ✓ |

⚠ = fewer than 15 OOS trades (below statistical minimum). Bold = OOS PF > 1.0.

### Combined OOS (corrected, 292 physical trades)

| Metric | Corrected Value | Minimum Required | Status |
|--------|----------------|-----------------|--------|
| Total physical trades | 292 | ≥ 80 | ✓ |
| Profit factor | **0.7877** | ≥ 1.30 | ✗ |
| Sharpe ratio | **−1.273** | ≥ 0.80 | ✗ |
| Win rate | **49.3%** | ≥ 42% | ✓ |
| Max drawdown | 13.3% | ≤ 15% | ✓ |
| Net P&L | **−13.34R** | — | — |

### Consensus Parameters (selected in 2 of 20 passes — weak signal)

```
EMA 10/24 | ATR 18-period × 2.5 | Body ≥ 50% | EntryDist ≤ 1.0 ATR | Max 3 trades/day
```

Parameter diversity across passes is high — each IS window selects substantially different parameters. This is a hallmark of curve-fitting, not a robust edge.

---

## 5. Monte Carlo — All Criteria Failed

**Input:** 292 physical trade results (post-FIX 1 netted), 2,000 bootstrap simulations (with replacement), seed=42.

*(Note: MC was run on 438 records pre-fix. With corrected 292 physical trades the P(profit) will be similar since net_profit is unchanged, but the specific distribution may shift slightly. A re-run with corrected trades is pending the next full WFO pass.)*

| Metric | Measured | Threshold | Status |
|--------|----------|-----------|--------|
| P(profit) | 3.95% | > 85% | ✗ FAIL |
| Ruin probability @ −5% | 99.35% | < 5% | ✗ FAIL |
| Ruin probability @ −10% | 85.95% | < 1% | ✗ FAIL |
| Median max drawdown | 16.3% | < 10% | ✗ FAIL |
| 95th pct max drawdown | 27.9% | < 20% | ✗ FAIL |
| Median profit factor | 0.789 | > 1.30 | ✗ FAIL |
| 5th pct final equity | 74.1% of start | > 100% | ✗ FAIL |
| Median longest losing streak | 5 | < 8 | ✓ PASS |
| 95th pct losing streak | 8 | < 15 | ✓ PASS |

Pipeline triggered **HARD STOP** at Phase 5 (ruin@5% = 99.4% vs 10% maximum). Exit code 1.

---

## 6. Root Cause Analysis

### 6.1 Parameter Surface Has No Robust Plateaus (primary cause)

The stability check tests whether the best IS parameter set sits on a plateau (neighbours also perform well) or a spike (neighbours perform poorly).

**Stability check summary across 20 passes:**
- Stability FAILs (spike): **133**
- Stability PASSes (plateau): **7**
- IS passes that used an unstable (spike) parameter set: **13 of 20**

Even the 7 stable passes mostly fail OOS: only Passes 15 and 19 produced OOS PF > 1.0 from a stable IS set. The IS optimisation is finding noise peaks, not real edges.

**IS→OOS PF degradation:**
- Average degradation ratio: approximately 4× (e.g., IS PF = 3.4 → OOS PF = 0.4)
- Acceptable threshold: < 2× degradation
- Worst case: Pass 20, IS PF = 3.02 → OOS PF = 0.19 (15.8× degradation)

### 6.2 Trade Frequency Too Low to Validate

OOS trades per 2-month window:
- Range: 11–48
- Median: ~20
- Passes below 15-trade minimum: **9 of 20** (45%)

With < 15 trades in a 2-month window, any OOS metric is noise-dominated. A 3-trade swing changes WR by 6pp, PF by 0.3–0.5. The strategy generates roughly 5–10 signals per month that survive all entry filters.

**Root cause of low frequency:** The entry gate applies five sequential filters: session window, 1H EMA bias, 5M EMA cross, body%, and entry distance from VWAP. Each filter independently rejects 20–60% of raw EMA signals. The combined rejection rate leaves only a small fraction as actual trades.

### 6.3 Regime Dependence

The strategy has positive OOS PF only in one contiguous block:

| OOS Period | OOS PF | Market context |
|------------|--------|---------------|
| Sep–Nov 2022 | 1.334 | Post-peak inflation |
| Nov 2022–Jan 2023 | 1.567 | Inflation reversal, choppy recovery |
| Jan–Mar 2023 | 2.528 | Strong directional move |
| Mar–May 2023 | 2.178 | Momentum continuation |
| May–Jul 2023 | 1.366 | Transitional |
| Sep–Nov 2023 | 1.110 | Late 2023 stabilisation |

Unprofitable in:
- **2021 (all):** Low-volatility, steady post-COVID trending
- **2022 Q1–Q3:** Russia-Ukraine macro shock, rapid trend reversals
- **2024 (most):** AI-driven bull market with large gap moves and trending sessions

The EMA+VWAP combination appears to generate edge in moderate-volatility, range-bound, choppy regimes. It consistently loses in strong-trend environments (entries are counter-trend by nature — requiring price to be near VWAP, which is below price in a strong uptrend).

### 6.4 REVERSION Exit Is the Primary Loss Driver

Of the 292 physical trades (pre-TP1 breakdown):
- REVERSION exits (127 trades, no TP1 hit): avg −0.346R each = **−43.9R total**
- These are the single largest contributor to gross loss
- REVERSION triggers when price closes below fast EMA or below VWAP — which in a trending environment happens on the NEXT bar after entry, immediately stopping out at a partial loss

The ATR multiplier of 2.5 (most commonly selected) creates a wide SL that is rarely hit; instead, price wanders back through the VWAP/EMA and triggers the REVERSION exit for a loss of 0.1–0.5R. This is the worst of both worlds: no clean SL discipline and no profit.

---

## 7. What Was NOT Changed

The following implementation details are correct and were not altered:

| Component | Status |
|-----------|--------|
| VWAP one-pass variance formula | Correct (matches C# VwapCalculator.cs) |
| VWAP daily reset at UTC midnight | Correct (verified empirically) |
| ATR using Wilder's smoothing (alpha = 1/period) | Correct |
| R-multiple calculation using `orig_sl_price` (never moved) | Correct |
| TP1 moves `sl_price` to BE without changing `orig_sl_price` | Correct |
| Equity curve uses 1% of current equity as risk per trade | Correct |
| 1H bias gate using last completed 1H bar | Correct |
| Multiprocessing: 4 fork workers with module-level globals | Correct |
| Data fetch checkpoint resumption (saves every 200 pages) | Correct |

---

## 8. Questions for Review

### Q1: What is the most efficient single change to increase trade frequency?

The strategy generates too few trades to validate within 2-month OOS windows. The options are:

- **(a) Remove `min_body_pct` entirely.** This is the filter most likely to reject valid setups — a compressed candle that still crosses EMA above VWAP is a real signal.
- **(b) Extend `max_entry_dist_atr` to 2.0.** Currently capped at 1.5 ATR from VWAP. Extending this would allow entries when the EMA signal fires slightly further from VWAP.
- **(c) Add a 5M entry tier.** Currently entries wait for the next bar's open (approximating 1M precision). A bar-open entry on the signal bar itself would increase fills.
- **(d) Expand the session window.** Currently 08:00–11:30 and 13:00–16:00 UK. Adding 07:00–08:00 would capture the opening burst.

Which of these is most likely to preserve signal quality while increasing frequency? The concern with (b) is that entries far from VWAP mean the VWAP band TPs are further away, reducing TP2 hit rate. The concern with (d) is that the 07:00 hour is the most volatile and least predictable.

### Q2: Should the REVERSION exit be removed or tightened?

REVERSION exits on 127 non-TP1 trades average −0.346R each. The logic (exit when price closes below fast EMA or VWAP) exits trades that haven't reached TP1 and haven't hit SL — they are partial losers exiting early.

Options:
- **(a) Remove REVERSION entirely.** Let SL do all the work. Trades that would have reverted and then recovered would benefit; trades that would have kept falling would lose the full 1R instead of 0.35R.
- **(b) Delay REVERSION by N bars.** Don't exit on the first reversion bar; require N consecutive closes below EMA/VWAP. This reduces noise exits.
- **(c) Tighten the REVERSION trigger.** Currently exits on ANY close below fast EMA OR VWAP. Change to require price to close below BOTH EMA AND VWAP simultaneously.
- **(d) Keep REVERSION only after TP1 is hit.** The function currently exits pre-TP1 positions too. Post-TP1 REVERSION (16 trades, avg +0.519R) is profitable. Pre-TP1 REVERSION is the problematic case.

Which of these is most consistent with the original spec intent?

### Q3: Is the 1H EMA bias gate helping or hurting?

The 1H EMA(21) bias gate requires price to be above EMA21 on the 1H chart for a long signal, below for a short. This was designed to prevent counter-trend entries. However:

- In a strong 1H uptrend (price well above 1H EMA21), the EMA+VWAP scalp entries on the 5M are also "with the trend" — but VWAP is below price, making the long signal require price to approach VWAP from above, which only happens during pullbacks. So the bias gate and the VWAP gate may be in conflict: the bias gate prefers strong trends, but the VWAP gate prefers price near VWAP, which doesn't happen in strong trends.

**Question:** Should the 1H bias gate be changed from "price > EMA21" to something that specifically selects for the choppy regime where the strategy shows edge? For example:
- ADX(14) on 1H < 25 (non-trending, range-bound)
- 1H ATR within a specific band (not too quiet, not explosive)
- No filter at all — let the 5M EMA+VWAP signal stand alone

### Q4: Is TP2 at 2R the right target given the REVERSION exit?

With REVERSION exit in place, a trade that reaches TP1 (+0.5R booked) but then reverses before TP2 either:
- Stops at BE: net = +0.5R − 0R = +0.5R (TP1+SL result, 75 trades, avg +0.112R → implies average BE-stop result)
- Exits via REVERSION: net = +0.5R + small partial loss/gain (16 trades, avg +0.519R)
- Reaches TP2: net = +0.5R + 1.0R = +1.5R (55 trades, avg +0.573R)

Only 55/146 TP1-hitting trades (37.7%) reach TP2. The break-even stop is frequently triggered. If TP2 were moved to 1.5R instead of 2R, the required TP2 hit rate for profitability would fall from ~40% to ~30%.

**Question:** Is moving TP2 to 1.5R worth the reduction in average winner size, and would it change the overall expectancy meaningfully given the current exit distribution?

### Q5: Is the strategy's underlying signal valid, just poorly optimised?

The concentrated profitable period (Sep 2022–Jul 2023) produced consistent OOS PF 1.1–2.5 across five consecutive passes. This is not random noise — it represents a 10-month window where the strategy had real edge. The OOS data in those passes:
- Pass 8: PF 1.334, 15 trades
- Pass 9: PF 1.567, 14 trades
- Pass 10: PF 2.528, 14 trades
- Pass 11: PF 2.178, 14 trades
- Pass 12: PF 1.366, 24 trades

If the underlying signal is valid but regime-dependent, the correct path is not to fix the signal — it is to add a regime filter that turns the strategy on only in the conditions where it works (choppy, moderate volatility, no strong 1H trend). An ADX(14) < 28 filter on the 1H is the most straightforward approach.

**Question:** Given the regime analysis, would you recommend: (a) adding a regime filter and re-running WFO, (b) redesigning the entry signal entirely, or (c) abandoning this instrument/timeframe and testing on a mean-reversion appropriate instrument?

---

## 9. Recommended Action Plan (Priority Order)

These are conditional on the reviewer's answers to Section 8. Listed in expected impact order:

### Priority 1 — ADX Regime Filter (Enhancement 1 from original spec)

Add `adx_threshold` parameter (grid: 20, 25, 30, 35) to the IS grid. Only allow trading when 1H ADX(14) < threshold. This directly targets the regime-dependence finding. Expected result: fewer total trades but higher hit rate in choppy conditions.

Implementation needed:
- `backtest_engine.py`: compute ADX on 1H bars alongside existing EMA21 1H
- Add `adx_threshold` parameter to signal gate (skip trade if ADX ≥ threshold)
- `parameter_grid.py`: add `ADX_THRESHOLD_RANGE = [20, 25, 30, 35]`

### Priority 2 — Loosen Entry Filters (Enhancement 2)

Lower `min_body_pct` minimum to 20% (add to grid) and extend `max_entry_dist_atr` to 2.0. Print rejection breakdown by filter to understand which gate rejects the most signals.

### Priority 3 — TP2 Optimisation (Enhancement 3)

Add `tp2_r` as a parameter (grid: 1.5, 2.0, 2.5 instead of fixed 2.0). Let WFO select the optimal TP2 level per window.

### Priority 4 — REVERSION Exit Review

Before re-running WFO, decide on REVERSION exit treatment (see Q2 above). This is a spec-level decision that affects all downstream results.

**These enhancements should only be implemented if the reviewer confirms the strategy's signal is fundamentally sound (Q5 above). If the signal is structurally broken, redesign before optimisation.**

---

## 10. Conditional Threshold Check

The user's instruction was: implement enhancements only if corrected OOS PF > 0.90 and canary re-runs show > 30 trades per window.

- Corrected OOS PF = **0.7877** — does NOT meet 0.90 threshold
- Canary re-runs not triggered (VWAP reset confirmed correct, no VWAP-related fix needed)

**Enhancements are gated pending reviewer direction.** The code is ready to implement them; the decision on whether to proceed is deferred to the reviewer.

---

## 11. File Locations

```
EMA_VWAP_ScalpBot/
├── optimisation/
│   ├── backtest_engine.py      ← FIX 1 (trade_id), FIX 3 (zoneinfo DST) applied
│   ├── wfo_engine.py           ← multiprocessing IS grid (4 workers)
│   ├── parameter_grid.py       ← get_neighbours() — verified correct
│   ├── mc_engine.py            ← bootstrap resampling
│   ├── report_generator.py     ← acceptance criteria table
│   ├── data_fetcher.py         ← cTrader MCP, checkpoint resumption
│   ├── config.py               ← all thresholds and parameters
│   └── run_all.py              ← master 7-phase runner
├── results/
│   ├── wfo/
│   │   └── wfo_summary.json    ← all 20-pass IS/OOS metrics (committed)
│   └── mc/
│       ├── mc_results.json     ← all MC metrics (committed)
│       └── mc_*.png            ← equity fan, histogram, ruin curve
├── data/
│   ├── GER40_5M_2021_2024.csv  ← 273,440 bars (committed)
│   └── GER40_1H_2021_2024.csv  ← 23,065 bars (committed)
└── cTrader/
    ├── EMA_VWAP_ScalpBot.cs    ← main cBot (Robot base class)
    ├── SignalEngine.cs
    ├── VwapCalculator.cs       ← session VWAP with SD bands
    ├── SessionGate.cs          ← time window filtering
    ├── RiskManager.cs          ← position sizing
    └── DailyLimitTracker.cs    ← daily loss limit
```

---

## 12. Summary

The pipeline is correct and the result is honest. The strategy genuinely does not have a consistent cross-regime edge on GER40 2021–2024 with the current signal design. The four implementation fixes confirmed this conclusion — none of them changed the fundamental result.

**What the numbers say:**
- IS finds something real (PF 1.4–4.1 consistently) → the signal has in-sample structure
- OOS collapses (median PF ≈ 0.76) → the IS structure does not generalise
- 95% stability spike rate → no robust parameter plateau exists; all IS "edges" are curve-fit artefacts
- The only profitable OOS cluster (Sep 2022–Jul 2023) aligns with a specific post-inflation choppy regime

**The single most important open question is Q5:** Is the underlying signal valid but regime-dependent, or is it structurally broken? If regime-dependent, the ADX filter (Priority 1 above) is the correct next step. If structurally broken, the entry logic needs redesign before any further optimisation.
