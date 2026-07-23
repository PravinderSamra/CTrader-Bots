# ORB "Stocks in Play" — Full Strategy Analysis

**Source paper:** Zarattini, C., Barbon, A., Aziz, A. — *A Profitable Day Trading Strategy For The U.S. Equity Market* (Concretum Research / University of St. Gallen / Peak Capital Trading, first version 16 Feb 2024). Copy stored at `research/paper/Zarattini-Barbon-Aziz-2024-ORB-Stocks-In-Play.pdf`.

**Analyst:** Fable 5 (Phase 1). This document is the canonical strategy reference for the ORB Scanner agent skill. Every rule the skill implements must trace back to a numbered rule here.

---

## 1. Strategy in one paragraph

Each trading day, scan all liquid US equities at 9:35 am ET (after the first 5-minute candle closes). Keep only stocks whose first-5-minute volume is **abnormally high relative to their own recent history** (Relative Volume ≥ 100%) — these are "Stocks in Play", almost always driven by a fundamental catalyst. Rank by Relative Volume and trade only the top of that ranking. Direction is dictated by the first candle: bullish candle → long-only via a buy-stop at the opening-range high; bearish candle → short-only via a sell-stop at the opening-range low; doji → no trade. Stop loss at 10% of the 14-day ATR from the fill price. No profit target — exit at 4:00 pm ET if the stop is never hit. Size every position so a stop-out loses 1% of capital, capped at 4× leverage.

The economic rationale: the opening range reveals an institutional supply/demand imbalance; **abnormal opening volume confirms the imbalance is real (not yet priced in)**, and a real imbalance tends to persist as an intraday trend. The strategy is a low-win-rate, high-payoff trend capture: frequent small stop-outs (−1R) paid for by occasional large trend days (+5R…+15R).

---

## 2. Headline evidence (2016–2023, 7,000+ US stocks, survivorship-bias-free, net of $0.0035/share commissions)

| Strategy | Total return | IRR | Vol | Sharpe | Daily hit ratio | MDD | Worst day | Alpha | Beta |
|---|---|---|---|---|---|---|---|---|---|
| ORB Base (all qualifying stocks) | 29% | 3.2% | 6.6% | 0.48 | 41.4% | 13% | −0.8% | 3.3% | 0.01 |
| **ORB + RelVol top-20 ("Stocks in Play")** | **1,637%** | **41.6%** | 14.8% | **2.81** | 48.4% | 12% | −1.61% | **35.8%** | 0.00 |
| S&P 500 buy & hold | 198% | 14.2% | 18.3% | 0.78 | 54.9% | 34% | −10.9% | 0.00% | 1.00 |

Key readings:

- **The edge is stock selection, not the breakout mechanics.** The identical ORB rules applied to *all* qualifying stocks earn ~3% a year; applied only to the top-20 RVOL stocks they earn ~42% a year. Relative Volume is the alpha engine. The scanner is therefore the single most valuable component to get right.
- **Beta ≈ 0** — returns are uncorrelated to the market (long-short, intraday-only). This is a diversifying return stream, not leveraged market exposure.
- **Monotonic RVOL → expectancy relationship** (paper Fig. 4, net of commissions):
  - RVOL < 1× → **−0.02R** average per trade (negative edge — must be excluded)
  - RVOL ≥ 1× → **+0.08R** per trade
  - RVOL ≥ 30× → **+0.38R** per trade
  - Expectancy rises monotonically between these points. **Higher RVOL rank = better pick.** This justifies both the ≥100% filter and ranking by RVOL for the top-3 selection.
- **Per-trade win ratios are LOW even for the best stocks** (17–24% for the top-25 5m-ORB names). The daily portfolio hit ratio is ~48% but individual trades stop out most of the time. The profit comes from the unbounded winners (e.g., worked BLDR example: +13.62R on one trade). Any attempt to "improve" the win rate with profit targets breaks the strategy (Wu et al. 2020, cited in paper: profit targets are detrimental; stop losses are beneficial).

---

## 3. Formal rule set

Let day *t*, stock *j*. All times US/Eastern (ET). Regular session 09:30–16:00.

### R1 — Universe filters (computed pre-open from daily data)
1. **Price:** today's opening price > **$5** (excludes penny stocks).
2. **Liquidity:** 14-day average daily volume ≥ **1,000,000 shares**.
3. **Volatility:** 14-day ATR > **$0.50** (Wilder's ATR, 14 periods, daily bars — see §4.1).

### R2 — Opening range (5-minute variant, the best performer)
- OR window = first 5 minutes: 09:30:00–09:34:59 ET.
- `ORH` = high of window, `ORL` = low of window, `ORV` = volume of window.
- Direction `d`:
  - first candle close > open → `d = +1` (long only)
  - first candle close < open → `d = −1` (short only)
  - close = open (doji) → **no trade** for this stock today.

### R3 — Relative Volume (the Stock-in-Play detector)

```
RelVol(t,j) = ORV(t,j) / [ (1/14) × Σ_{i=1..14} ORV(t−i, j) ]
```

i.e. today's opening-range volume divided by the mean opening-range volume of the **same window** over the previous 14 **trading days**.

4. **Filter:** RelVol ≥ **1.0** (100%).
5. **Ranking:** sort qualifying stocks by RelVol descending; the paper trades the **top 20**; our skill reports the **top 3** (plus a watch table).

### R4 — Entry
- Long (`d=+1`): **buy stop** at `ORH`. Short (`d=−1`): **sell stop** at `ORL`.
- The stop order rests from 09:35 to 16:00; it may trigger any time in that window (the BLDR example triggered ~10:00).
- One trade per stock per day. No re-entry after a stop-out. No trade in the opposite direction ever, even if price breaks the other side of the range.

### R5 — Exit
- **Stop loss:** `0.10 × ATR14` from the executed entry price
  (long: `SL = entry − 0.1×ATR`; short: `SL = entry + 0.1×ATR`).
- **No profit target.** If not stopped, close at 16:00 ET (market-on-close).
- Definition of risk unit: **R = 0.1 × ATR14 per share**. Trade PnL is reported in R multiples: `PnL_R = d × (P_exit − P_entry) / (0.1 × ATR14)`.

### R6 — Position sizing
- Size so a stop-out loses **1% of account equity**: `shares = (0.01 × Equity) / (0.1 × ATR14)`.
- **Leverage cap 4×**: `shares ≤ (4 × Equity) / entry_price` (FINRA day-trading margin). The cap binds on low-ATR-relative-to-price stocks, making realised risk < 1% on those.

### R7 — Portfolio
- All top-N qualifying stocks traded simultaneously, long and short mixed as directed by their opening candles. No market-direction overlay, no sector constraints, no correlation adjustment in the paper.

---

## 4. Mathematical details

### 4.1 Wilder's ATR(14) on daily bars
True Range of day *i*: `TR_i = max(H_i − L_i, |H_i − C_{i−1}|, |L_i − C_{i−1}|)`.
The paper says "average true range over the previous 14 days"; the classic Wilder smoothing is `ATR_i = (13×ATR_{i−1} + TR_i)/14`. A simple 14-day mean of TR is an acceptable approximation and is what "14-day average" literally states — the difference is immaterial to filter/stop behaviour, but **the implementation must document which it uses and be consistent** (skill spec mandates simple mean of the last 14 TRs, matching the paper's plain-language definition, computed on data *up to and including yesterday*).

Worked example from the paper: BLDR, ATR = $5 → stop distance 0.1 × $5 = $0.50. Short entry $174.44, EoD exit $167.63 → move $6.81 → **+13.62R**.

### 4.2 Why 5 minutes beats 15/30/60
Same rules, RVOL measured over the respective n-minute window:

| Timeframe | Total return | IRR | Sharpe |
|---|---|---|---|
| 5m | 1,637% | 41.6% | 2.81 |
| 15m | 272% | 17.4% | 1.43 |
| 30m | 21% | 2.3% | 0.21 |
| 60m | 39% | 4.1% | 0.40 |
| COMBO (equal-weight all four) | 234% | 15.8% | 1.99 |

Authors' hypothesis: the shorter the opening range, the larger the fraction of a trend day's move captured after the breakout. **The skill implements the 5-minute variant only**; 15m is the only defensible alternative (Sharpe 1.43) and may be a later option flag.

### 4.3 Expectancy anatomy
With stop = 0.1×ATR and typical trend-day ranges of 1–3 ATR, the payoff distribution is: P(stop-out) ≈ 0.75–0.83, loss ≈ −1R (plus slippage); winners unbounded, tail up to >10R. At the observed +0.08R mean (RVOL≥1) and ~20 trades/day across the book, edge compounds fast, but **single-name expectancy is noisy — the discipline of taking every qualifying signal and never widening stops is what the backtest actually assumes.**

### 4.4 What the paper does NOT use (do not "improve" it silently)
- No profit targets (evidence they hurt).
- No VWAP/moving-average/momentum confirmation.
- No news-sentiment gating — RVOL alone proxies the catalyst. (Catalyst identification is useful *context* for the human, and our skill reports it, but it is **not** a filter.)
- No gap-size filter, no market-regime filter, no time-of-day cutoff for entries.
- Unadjusted intraday prices (splits/dividends unadjusted) — irrelevant intraday, matters only when stitching multi-day intraday history across a split date (see §6.5).

---

## 5. The "Stock in Play" concept (qualitative layer)

Typical catalysts behind RVOL spikes (paper §3, from Bellafiore/Aziz practice): earnings reports, earnings warnings/pre-announcements/surprises, FDA decisions, M&A, partnerships/major product news, major contract wins/losses, restructurings/layoffs/management changes, splits/buybacks/debt offerings, breaks of key technical levels.

A catalyst is *necessary but not sufficient* — if it's already priced in, institutions don't transact and RVOL stays low. **RVOL is the measurement; the catalyst is the explanation.** The skill's report should attach a one-line catalyst note per pick (via news search) so the human can veto obvious traps (e.g., halted stocks, merger-arb pinned prices — a stock pinned at a cash-deal price can show huge RVOL but zero trend potential; this is the main known failure mode of pure-RVOL ranking).

---

## 6. Execution nuances the implementation must respect

1. **Clock discipline.** The scan cannot run before 09:35:00 ET — the OR candle must be complete. Report generation target: 09:35–09:45 ET (picks lose value as price runs away from the range).
2. **DST.** 09:30 ET = 13:30 UTC in US summer, 14:30 UTC in winter. Compute from the America/New_York timezone, never hardcode a UTC offset.
3. **Trading-day calendar.** The 14 prior OR volumes must come from the previous 14 *trading* days (skip weekends/holidays). Half-days (e.g. day after Thanksgiving, Christmas Eve) still have a 9:30–9:35 window and count normally; a recent IPO with <14 days of history cannot compute RelVol → excluded.
4. **Stop-through gaps.** A stop order that is jumped (price gaps over ORH on a halt resumption etc.) fills at market with slippage; R accounting uses the *executed* price. The advisory report quotes entry = ORH/ORL but flags "already through level by X%" if price has run.
5. **Split-adjustment trap.** If a stock split within the last 14 days, raw OR-volume history spanning the split distorts RelVol (share count changes). Detection heuristic: >40% overnight close-to-open move with matching volume regime change → flag the pick as "RelVol unreliable — recent split/corporate action".
6. **Commissions/costs.** Paper nets $0.0035/share. On a CFD/spread-bet venue the cost is the spread — materially different microstructure. Advisory mode is unaffected; any future auto-execution must re-validate expectancy under spread costs (see ADAPTATIONS).
7. **Doji is exact.** Close == open to the tick → skip. Near-dojis still trade — no discretionary "too small" filter exists in the paper.
8. **Direction lock.** The rule "bullish candle → long-only" holds even if the ORL breaks first and stops would have been avoided. Never flip.

---

## 7. Adaptations required for the cTrader data source

The paper uses CRSP + IQFeed share-volume data. Our data source is the cTrader Open API via MCP (HTTP). Differences that must be handled:

| Paper assumes | cTrader reality | Adaptation |
|---|---|---|
| Share volume (shares/day) | `tickVolume` on trendbars (tick count, not shares) | **RelVol is a ratio of same-symbol volumes → tick volume is a valid proxy** (units cancel). The 1M-shares/day absolute filter cannot be applied literally → replace with a liquidity ranking/threshold on the account's own universe (audit will calibrate; e.g. require 14-day avg daily tickVolume above a percentile floor). Flag clearly in reports that liquidity filter is proxy-based. |
| $ ATR > $0.50 absolute | CFD prices mirror underlying $ prices | Keep $0.50 absolute (prices match the US listing) — verify in audit. |
| 7,000-stock universe | Whatever share instruments the broker enables (audit needed; the confirmed symbol map in `ctrader-mcp-integration-guide.md` shows only indices/FX/commodities — equities availability on this account is **unverified**) | Phase 2 audit enumerates `get_symbols`, isolates enabled share-class instruments, measures 5-minute data quality. If the account has no/few US shares, options: (a) different Pepperstone account type with share CFDs, (b) hybrid — shortlist via TradingView screener MCP, verify/price via cTrader for whatever overlaps, (c) advisory-only picks on full US universe using a supplementary data source. Decision point for the user at end of audit. |
| Continuous 9:30–16:00 bars | cTrader equity CFDs follow exchange hours; bars in UTC | Identify the 09:30 ET bar by timezone conversion; confirm no pre-market bars pollute the OR window (audit task — if pre-market bars exist, the OR bar is the one starting exactly at 09:30 ET, not the first bar of the day). |
| Prices in dollars | Trendbar prices in pipettes (divide by 10^pipDigits, auto-detect per symbol) | Use the proven `detect_pip_digits`/divisor approach from the integration guide; for equities expect divisor 10^2 or 10^5 — audit confirms. |
| Fast bulk data | One HTTP call per symbol per window; 720h max range per trendbar request | Two-pass design: **pre-open pass** (daily bars → filters + ATR + cache of 14-day OR volumes from M_5 history) on a bounded watchlist; **09:35 pass** fetches only today's M_5 bar per watchlist symbol. Keep the 09:35 pass ≤ ~60 symbols so the report lands by ~09:40. |

Connection method: **persistent HTTP with session keep-alive exactly as documented in `/ctrader-mcp-integration-guide.md`** (Lessons 1, 6, 7). Do not use the `mcp__ctrader__*` tool layer from scripts; use the Python `_call_tool()` pattern. This is the "most stable connection" the user referenced.

---

## 8. What the skill is (and is not)

**Is:** a scanner + advisor. At/after 09:35 ET it produces the ranked Stock-in-Play table, the top-3 picks with full trade plans (direction, entry stop level, SL, sizing at 1%/4× cap, EoD exit), catalyst notes, and data-quality flags.

**Is not (yet):** an execution bot. No orders are placed in this phase. The trade-plan output is deliberately structured (JSON + human report) so a future execution phase can consume it unchanged.
