# EMA + VWAP ScalpBot — WFO & Monte Carlo Validation Review

**Date:** 2026-06-28  
**Instrument:** GER40 (DAX) Spread-Bet via Pepperstone / cTrader  
**Data period:** 2021-01-04 → 2024-12-31 (273,440 × 5M bars; 23,065 × 1H bars)  
**Branch:** `claude/ema-vwap-monte-carlo-o4fmew`  
**Verdict: 🔴 RED — Do Not Deploy**

---

## 1. What Was Built

A full mechanical intraday scalping cBot with:

- **Entry logic:** EMA crossover (fast/slow) confirming direction, price must be on the correct side of the session VWAP ± SD bands, minimum candle body %, entry within max_entry_dist_atr × ATR of the EMA
- **Risk management:** ATR-based dynamic stop loss (Wilder), fixed-fractional risk sizing (1% per trade), TP1 at 1R (close 50% position, move SL to break-even), TP2 at 2R (close remaining 50%)
- **Session gate:** UK session 07:00–14:00 only; daily loss limit: 3R maximum
- **Validation framework:** 7-phase pipeline — data fetch (cTrader MCP), Walk-Forward Optimisation (20 passes, 6M IS / 2M OOS), Monte Carlo bootstrap (2,000 sims), report generation, deployment verdict

---

## 2. Parameter Search Space (Coarse Grid)

| Parameter | Values Tested |
|-----------|--------------|
| `ema_fast` | 7, 9, 10, 11, 12, 13 |
| `ema_slow` | 18–26 (step 1) |
| `atr_period` | 10, 12, 14, 18 |
| `atr_multiplier` | 1.0, 1.5, 2.0, 2.5 |
| `min_body_pct` | 30%, 40%, 50% |
| `max_entry_dist_atr` | 0.5, 0.75, 1.0, 1.25, 1.5 |
| `max_trades_per_day` | 2, 3, 4 |

**Total coarse combinations: 22,680 per IS window**

IS qualification thresholds: PF > 1.30, WR > 42%, MaxDD < 15%, Trades ≥ 40

---

## 3. Phase 3 QC — PASSED

- 20-combination test on 2023-Q1 data
- Trades per combo: 10–120
- PF range: 0.67–∞ (varied sufficiently)
- Data quality: confirmed real cTrader MCP bars, pip_digits=5 auto-detected

---

## 4. Walk-Forward Optimisation — All 20 Passes

### IS vs OOS Results

| Pass | IS Period | OOS Period | IS PF | IS WR | IS Trades | OOS PF | OOS WR | OOS Trades | Stable? |
|------|-----------|------------|-------|-------|-----------|--------|--------|------------|---------|
| 1 | Jan–Jul 2021 | Jul–Sep 2021 | 2.563 | 61.1% | 54 | 0.640 | 30.8% | 13 ⚠ | ✓ |
| 2 | Mar–Sep 2021 | Sep–Nov 2021 | 2.247 | 58.8% | 80 | 0.496 | 51.9% | 27 | ✗ |
| 3 | May–Nov 2021 | Nov 2021–Jan 2022 | 1.376 | 51.7% | 149 | 0.924 | 45.8% | 48 | ✗ |
| 4 | Jul 2021–Jan 2022 | Jan–Mar 2022 | 1.742 | 61.3% | 62 | 0.762 | 54.2% | 24 | ✗ |
| 5 | Sep 2021–Mar 2022 | Mar–May 2022 | 1.939 | 61.5% | 52 | 0.380 | 30.0% | 20 | ✓ |
| 6 | Nov 2021–May 2022 | May–Jul 2022 | 1.838 | 60.6% | 71 | 0.531 | 45.5% | 11 ⚠ | ✗ |
| 7 | Jan–Jul 2022 | Jul–Sep 2022 | 2.664 | 62.5% | 40 | 0.411 | 33.3% | 12 ⚠ | ✓ |
| 8 | Mar–Sep 2022 | Sep–Nov 2022 | 2.206 | 61.8% | 89 | **1.334** | 53.3% | 15 | ✗ |
| 9 | May–Nov 2022 | Nov 2022–Jan 2023 | 2.733 | 56.3% | 48 | **1.567** | 57.1% | 14 ⚠ | ✗ |
| 10 | Jul 2022–Jan 2023 | Jan–Mar 2023 | 3.454 | 63.8% | 47 | **2.528** | 71.4% | 14 ⚠ | ✗ |
| 11 | Sep 2022–Mar 2023 | Mar–May 2023 | 4.118 | 64.8% | 54 | **2.178** | 64.3% | 14 ⚠ | ✗ |
| 12 | Nov 2022–May 2023 | May–Jul 2023 | 3.018 | 64.8% | 54 | **1.366** | 50.0% | 24 | ✗ |
| 13 | Jan–Jul 2023 | Jul–Sep 2023 | 2.843 | 66.7% | 60 | 0.412 | 46.2% | 13 ⚠ | ✗ |
| 14 | Mar–Sep 2023 | Sep–Nov 2023 | 1.432 | 54.2% | 83 | **1.110** | 56.7% | 30 | ✗ |
| 15 | May–Nov 2023 | Nov 2023–Jan 2024 | 1.645 | 59.1% | 88 | **1.284** | 60.9% | 23 | ✓ |
| 16 | Jul 2023–Jan 2024 | Jan–Mar 2024 | 1.987 | 65.4% | 52 | 0.396 | 36.4% | 22 | ✗ |
| 17 | Sep 2023–Mar 2024 | Mar–May 2024 | 1.980 | 60.0% | 55 | 0.398 | 35.3% | 17 | ✗ |
| 18 | Nov 2023–May 2024 | May–Jul 2024 | 2.272 | 63.3% | 49 | 0.712 | 45.7% | 46 | ✓ |
| 19 | Jan–Jul 2024 | Jul–Sep 2024 | 1.992 | 59.1% | 93 | **1.106** | 53.1% | 32 | ✓ |
| 20 | Mar–Sep 2024 | Sep–Nov 2024 | 3.019 | 63.9% | 72 | 0.192 | 26.3% | 19 | ✓ |

⚠ = fewer than 15 OOS trades (below statistical minimum)

### Combined OOS (all 20 passes concatenated)

| Metric | Value | Minimum Required |
|--------|-------|-----------------|
| Total trades | 438 | ≥ 80 ✓ |
| Profit factor | **0.788** | ≥ 1.30 ✗ |
| Sharpe ratio | **−1.273** | ≥ 0.80 ✗ |
| Win rate | 47.7% | ≥ 42% ✓ |
| Max drawdown | 13.3% | ≤ 15% ✓ |
| Recovery factor | **−100** | ≥ 1.50 ✗ |
| Gross profit | +49.66R | — |
| Gross loss | −63.00R | — |
| Net P&L | **−13.34R** | — |

### Consensus Parameters (selected in 2 of 20 passes — weak)

```
EMA 10/24 | ATR 18-period × 2.5 | Body ≥ 50% | EntryDist ≤ 1.0 ATR | Max 3 trades/day
```

---

## 5. Phase 5 Monte Carlo — All Criteria Failed

**Input:** 438 real OOS trades, 2,000 bootstrap simulations (with replacement), seed=42

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

**Pipeline triggered HARD STOP** at Phase 5 (ruin@5% = 99.4% vs 10% maximum).  
Exit code 1. Phases 6 (full report) and 7 (acceptance table) not reached.

---

## 6. Root Cause Analysis

### 6.1 Extreme IS→OOS Overfitting (primary cause)

The IS parameter surface consists almost entirely of narrow performance spikes — not robust plateaus.

**Stability check summary across all 20 passes:**
- Stability FAILs (spike detected): **133**
- Stability PASSes (plateau confirmed): **7**
- Passes forced to use unstable top-ranked params: **13 of 20**

Even in the 7 passes where a stable parameter set was found, OOS performance was poor:
- Stable passes with OOS PF > 1.0: Passes 15, 19 only
- Stable passes with OOS PF < 1.0: Passes 1, 5, 7, 18, 20

The IS→OOS PF degradation ratio averages approximately 4×. Typical acceptable degradation is < 2×.

### 6.2 Insufficient OOS Trade Frequency

**OOS trades per 2-month window:**
- Minimum: 11 (Pass 6)
- Maximum: 48 (Pass 3)
- Median: ~20
- Passes below 15-trade minimum: 9 of 20 (45%)

With fewer than 15 trades per window, OOS metrics are dominated by noise. A strategy generating only 5–10 trade signals per month cannot be validated reliably at this window size.

**Cause:** The triple entry gate (session + EMA cross + VWAP band side + body% filter + entry distance filter) is over-restrictive. Most generated EMA signals are rejected by the downstream filters.

### 6.3 Regime-Dependent Edge

The strategy showed positive OOS profit factor only in specific market regimes:

| OOS Period | PF | Market Context |
|------------|-----|----------------|
| Sep–Nov 2022 | 1.334 | Post-peak inflation, volatile trending |
| Nov 2022–Jan 2023 | 1.567 | Inflation reversal, choppy recovery |
| Jan–Mar 2023 | 2.528 | Strong directional move |
| Mar–May 2023 | 2.178 | Momentum continuation |
| May–Jul 2023 | 1.366 | Transitional |

The strategy fails in:
- **2021 (all of it)**: Low-volatility post-COVID recovery trending markets
- **2022 Q1–Q3**: Russia-Ukraine macro shock, rapid trend reversals
- **2024 (most of it)**: AI-driven bull market with large gap moves

The EMA+VWAP combination appears to be a mean-reversion detector that only works in choppy, range-bound conditions with moderate volatility.

### 6.4 R-Multiple Math Does Not Close

With OOS WR = 47.7% and the TP1/TP2 split:
- TP1 hit (close 50% at +1R) = +0.5R for that half position
- For full-hit trades (TP1 → TP2): +0.5R + 1.0R = +1.5R
- SL without TP1: −1.0R

For a 47.7% TP1-hit rate to be profitable, at least ~60% of TP1-hitting trades must continue to TP2.  
The gross profit (+49.66R) vs gross loss (−63.00R) confirms this threshold is not reached. The system reaches TP2 insufficiently, likely because price frequently reverses after TP1 and is stopped at break-even.

---

## 7. Questions for Review

The following questions are being raised for Claude AI review:

### Q1: Is the backtest engine correctly implementing TP1/TP2 mechanics?

The TP1 logic was fixed mid-project (TP1 was previously recording a trade but NOT calling `_apply_pnl`, so equity was not updated). After the fix:
- TP1 hit → records `exit_type="TP1"`, `pnl_r=+0.5`, calls `_apply_pnl`, moves SL to break-even
- Second exit (TP2/BE/SESSION_END) → uses `orig_sl_price` (never moved) for `fraction=0.5` of position

**Concern:** Are double-counted trades inflating the denominator of WR/PF statistics? Each physical trade now produces TWO records in the trade list (TP1 partial + second exit). If `total_trades` counts both, the WR and PF are diluted relative to the underlying edge.

**Specific ask:** Review `_calc_statistics` in `backtest_engine.py` to confirm win_rate is calculated correctly given that TP1 partials and subsequent exits are separate records in the same list.

### Q2: Is the session gate correctly converting UTC → UK time?

The session gate uses a simplified DST approximation: GMT+1 from April–October, GMT+0 otherwise. This is verified for the bulk of the year but may misclassify bars near the DST changeover (last Sunday of March and October). Misclassification would cause the strategy to trade slightly outside the intended 07:00–14:00 UK window, which could either help or hurt depending on the direction.

**Specific ask:** Verify `_in_trading_window_ger40()` in `backtest_engine.py` matches the actual UK DST schedule for the 2021–2024 period.

### Q3: Is the VWAP resetting correctly at each trading session?

The session VWAP should reset at the start of each trading day (or the start of each 07:00 UK window). If VWAP is accumulating across multiple days without reset, the VWAP level will be far from the current price for all bars except early in the history, which would cause the VWAP gate to reject most entries.

**Specific ask:** Confirm that VWAP state variables (`vwap_num`, `vwap_den`, `var_sum`) are reset whenever `_in_trading_window_ger40(bar_time)` transitions from False to True.

### Q4: Are the parameter grid neighbour definitions reasonable for the stability check?

The stability check tests adjacent parameter values. For a parameter like `ema_fast = 9`, neighbours would include `ema_fast = 8` and `ema_fast = 10`. If the coarse grid step sizes are large (e.g., only testing ema_fast in {7, 9, 10, 11, 12, 13}), the "neighbours" for stability testing might be the same as adjacent grid points, which are already in the coarse grid. This means stability testing isn't checking truly continuous neighbours — it's checking other IS-evaluated points.

**Specific ask:** Review `get_neighbours()` in `parameter_grid.py` to confirm it generates ±1 step neighbour values for each parameter, and that these neighbour values are not the same as adjacent grid points in every case.

---

## 8. Recommended Next Steps

Listed in order of expected impact:

### Step 1 — Audit backtest_engine.py trade counting (Q1 above)

If TP1 partials and second exits are double-counted in `total_trades`, fixing this would change the WR and PF numbers. A corrected calculation might reveal a different picture.

**Specific change:** In `_calc_statistics`, either:
- (a) Count only final exits per physical trade (exclude `exit_type="TP1"` from denominator), OR
- (b) Sum pnl_r across both records per trade to get a net per-trade R (TP1 + second exit combined)

### Step 2 — Loosen entry filters to increase trade frequency

The most immediate lever. If OOS generates 40+ trades per 2-month window instead of 11–20, the WFO statistics become more reliable and more IS parameter sets will qualify.

**Suggested parameter range expansions:**
- `min_body_pct`: add 20% to the grid (currently 30%/40%/50%)
- `max_entry_dist_atr`: extend to 2.0 (currently max 1.5)
- Remove `min_body_pct` filter entirely as a test — it may be the most restrictive gate

### Step 3 — Add a market regime pre-filter

The strategy only worked in 5 consecutive passes (Sep 2022–Jul 2023). This maps to the post-inflation-peak choppy recovery. Consider adding a regime detector:

- **ADX filter**: only trade when ADX(14) on 1H chart is < 25 (non-trending / ranging)
- **Volatility filter**: only trade when ATR(14) on 1H is within a defined band (not too quiet, not explosive)

This would explicitly limit the strategy to its working regime rather than attempting to trade through all conditions.

### Step 4 — Revisit TP/SL ratio

The current 1R SL / 1R TP1 / 2R TP2 structure requires the second exit to frequently reach TP2 to be profitable. If TP2 is rarely hit (because price reverses after TP1 and triggers BE stop), consider:

- **Option A:** Move TP2 closer — 1.5R instead of 2R (requires lower hit rate to be profitable)
- **Option B:** Replace TP2 with a trailing stop of 0.5 ATR to let winners run further

### Step 5 — Test on US500 as a generalisation check

The spec includes US500 as a secondary instrument for generalisation testing. If the strategy parameters found on GER40 also show edge on US500, that would increase confidence in the underlying signal. If US500 results are similarly poor, it confirms the edge is absent. If US500 is profitable where GER40 is not, the instrument choice may be the issue.

---

## 9. File Locations (for code review)

```
EMA_VWAP_ScalpBot/
├── optimisation/
│   ├── backtest_engine.py      ← TP1/TP2 mechanics, _calc_statistics
│   ├── wfo_engine.py           ← stability check, IS grid (now parallel)
│   ├── parameter_grid.py       ← get_neighbours() implementation
│   ├── mc_engine.py            ← bootstrap resampling
│   ├── report_generator.py     ← acceptance criteria table
│   ├── data_fetcher.py         ← cTrader MCP data ingestion
│   ├── config.py               ← all thresholds and parameters
│   └── run_all.py              ← master 7-phase runner
├── results/
│   ├── wfo/
│   │   ├── wfo_summary.json    ← all pass-level IS/OOS metrics
│   │   ├── pass_XX_is_results.csv  ← top 500 IS combos per pass
│   │   └── pass_XX_oos_trades.csv  ← individual OOS trades per pass
│   └── mc/
│       ├── mc_results.json     ← all MC metrics and pass/fail
│       ├── mc_equity_fan.png
│       ├── mc_final_equity_hist.png
│       ├── mc_maxdd_hist.png
│       ├── mc_pf_boxplot.png
│       └── mc_ruin_curve.png
└── cTrader/
    ├── EMA_VWAP_ScalpBot.cs    ← main cBot (Robot base class)
    ├── SignalEngine.cs          ← EMA + VWAP signal logic
    ├── VwapCalculator.cs        ← session VWAP with SD bands
    ├── SessionGate.cs           ← time window filtering
    ├── RiskManager.cs           ← position sizing
    └── DailyLimitTracker.cs     ← daily loss limit
```

---

## 10. Summary for Reviewer

This is an honest, complete validation result — not a simulation failure. The pipeline ran successfully end-to-end against 4 years of real cTrader MCP data. The strategy genuinely does not have a consistent cross-regime edge on GER40 with the current signal design.

**Key numbers to focus on:**
- IS PF is consistently 1.4–4.1 across all periods → IS optimisation is finding something
- OOS PF is 0.38–2.53, median ≈ 0.76 → the IS signal does not generalise
- 95% stability spike rate → no parameter plateau exists; all IS "edges" are curve-fit artefacts
- The only profitable OOS period (Sep 2022–Jul 2023) coincides with a specific post-inflation choppy regime

The single most important question is whether the trade counting double-counts TP1 partials (Q1 above). If it does, the true per-trade edge may look different once corrected. Everything else flows from there.
