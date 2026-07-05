# US30 / NAS100 — London Range Breakout
## Phase 1 — Requirements, Approach & Research Design

**Analyst:** Quant research (Claude)
**Date started:** 2026-07-05
**Status:** Phase 1 — planning & scoping (awaiting sign-off on 4 decisions, see §7)

---

## 1. The strategy under test (as briefed)

On the US30 (and, as an alternative, NAS100):

1. **Mark the "London range"** — the high and low formed during a defined London window
   (exact window is itself a research question — see §4).
2. **Wait for the US cash open** (09:30 America/New_York).
3. A **5-minute candle must break out** beyond the London range (above = long, below = short)
   **on large volume**.
4. **Enter on the close** of that breakout candle, provided the close is beyond the range.
5. **Stop loss 50 points** from entry; **take profit 100 points** from entry (base case, 1:2 R).
6. Mirror rules for shorts on a break below the range.

## 2. What we are measuring

Per instrument (US30, NAS100) and per rule-variant we compute:
- Trade count, **win rate**, loss rate, breakeven/timeout rate
- Average win / average loss (points and R)
- **Expectancy per trade** (R and points), profit factor
- Total P&L in **R-multiples** (primary) and in **£** using the account's spread-bet sizing
- Max drawdown, longest losing streak, best/worst day
- Distribution by weekday, by month/regime, by direction (long vs short)
- Time-to-resolution (how quickly TP/SL hit)

## 3. Refinement axes to sweep

- **Take-profit / R targets:** 2.0R (base, 100pt), **2.5R, 3.0R, 3.5R**, plus 1R and trailing.
- **Stop-loss placement:** fixed 50pt base, plus 30 / 40 / 60 / 75 pt, and
  **volatility/structure-based** stops (ATR-multiple, beyond range edge) — see §7 Q3.
- **Volume filter:** the core "large volume" question — see §5.
- **London-range window:** several candidate definitions — see §4.
- **Breakout timing window** after the open (first candle only, first 30/60 min, whole session).
- **Entry beyond range by a buffer** (0 / few points) to reduce false breaks.

## 4. "London range" — candidate definitions to test

All boundaries handled in **exchange-local time with DST** (Europe/London, America/New_York),
converted from the UTC timestamps cTrader returns. Candidates:

| ID | Window (London local) | Rationale |
|----|-----------------------|-----------|
| LR-A | 03:00–08:00 (early London) | London open drive before EU cash |
| LR-B | 07:00–09:30 (pre + EU cash open) | classic "London session" high/low |
| LR-C | 08:00–13:00 | full London morning to lunch |
| LR-D | 00:00–08:00 (Asia+London to pre-NY) | wider overnight range |
| LR-E | 02:00–08:30 ET-anchored | range ending just before NY open |

We report which window produces the most robust edge, not assume one.

## 5. Volume investigation (core research question)

cTrader returns **tick volume** (number of price updates per bar), not real exchange
contract volume — this is a CFD/spread-bet feed. We will:
- Build a **baseline** of tick volume by time-of-day (Asia / pre-market / open / lunch).
- For each breakout candle, compute volume **relative to**: (a) trailing N-bar average,
  (b) same-time-of-day average, (c) the day's pre-market average, (d) a rolling z-score.
- Correlate the breakout candle's relative volume with **outcome** (TP vs SL) to find the
  volume threshold that best separates winners from losers.
- Deliverable: recommended volume filter (e.g. "break candle ≥ X× trailing-20 average").

**Caveat documented:** tick volume ≈ activity, not traded contracts. Optional cross-check
against real futures (YM/NQ) volume is a decision in §7 Q2.

## 6. Instrument comparison (US30 vs NAS100)

Same pipeline on both, then a head-to-head:
- Note that a **fixed 50-point stop is not equivalent** across instruments
  (US30 ~44k, NAS100 ~20k; 50pt is ~0.11% vs ~0.25%). For a fair comparison we also
  report **ATR-normalised** and **percentage-normalised** stops.
- Compare expectancy, win rate, profit factor, robustness across windows/regimes.
- Recommendation on which instrument to carry forward (or both).

---

## Technical findings from Phase 1 connectivity probe

- **Account:** Pepperstone UK GBP spread-bet demo (£46,466 equity). US30_SB=id **219**, NAS100_SB=id **205**.
- **Data endpoint:** `get_trendbars`, range-mode `(fromTimestamp,toTimestamp)` only. `count`-mode returns empty on this server.
- **Hard cap 100 bars/call.** Windows >100 bars return only the trailing 100. → downloader **pages backwards in ≤8h (≈96-bar) M5 chunks**.
- **History depth:** M5 data available back to at least **2023** (3+ years).
- **Bar schema:** `{timestamp(ms), open, high, low, close, volume}`; prices in pipettes (÷10⁵ for US30/NAS100); `volume` = tick count.
- **Reliability:** use direct-HTTP `_call_tool` with keep-alive + re-init on 404 (the injected `mcp__ctrader__*` tools expire frequently — confirmed).

## Data storage plan

```
US30 London Range Breakout/
  data/US30/     raw M5 (and D1) OHLCV, paged JSON/parquet, + manifest of coverage
  data/NAS100/   same
  scripts/       downloader, session/DST utils, backtester, volume study, comparison
  analysis/      computed trade logs, metric tables, sweep results (CSV)
  charts/        equity curves, distributions, volume-vs-outcome plots
  docs/          this plan + phase write-ups + final study
```
Raw data is downloaded **once** and committed so re-analysis/pivots need no re-download.

## 7. Open decisions (need your call before Phase 2)

See chat — 4 questions on history depth, volume source, stop-loss scope, and trades-per-day.
Defaults chosen if you don't specify: **3yr history · tick-volume only (caveated) ·
fixed + ATR stops · first qualifying breakout/day (capture all for comparison).**
