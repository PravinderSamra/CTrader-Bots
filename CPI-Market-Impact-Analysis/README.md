# CPI Market Impact Analysis

Two-year study (Jun 2024 – May 2026 reference months, 23 releases) of how US
CPI headline MoM/YoY surprises move **US500** and **NAS100** in the 30
minutes after the 8:30am US Eastern release (13:30 UK local time, except two
DST-mismatch dates flagged below where it's 12:30 UK).

See `METHODOLOGY.md` for the full classification rules.

## Files

- `data/cpi_calendar.csv` — verified CPI release calendar: reference month,
  release date, MoM/YoY actual vs forecast vs previous, confidence notes.
  Sourced from original BLS press releases (not revised FRED data) with
  forecast figures cross-checked from investing.com/tradingeconomics/CNBC.
- `data/raw_candles/{month}_{instrument}.json` — raw 1-minute OHLCV cTrader
  data for US500 (symbolId 115) and NAS100 (symbolId 116) around each
  release, straight from `get_trendbars` (prices are raw/100000).
- `data/price_reaction.csv` — the processed dataset: pre/post-release prices
  (P0/P1/P5/P15/P30), net and initial point moves, expected label, actual
  label, points moved, hit/miss — one row per instrument per event (46 rows).
- `data/build_price_reaction.py` — deterministic script that regenerates
  `price_reaction.csv` from the calendar + raw candles (re-run any time the
  calendar or methodology changes; no LLM judgment involved in the numbers).

## Headline findings (see full report for detail)

- **Combined hit rate (actual reaction matched the textbook expected
  reaction): 34.8%** (16/46) — barely above the ~33% you'd expect from
  chance across three possible outcomes (Bullish/Bearish/Whipsaw). The
  simple "hot CPI = bearish, cool CPI = bullish" heuristic does **not**
  reliably predict the 30-minute post-release move on either index in this
  sample.
- **NAS100 hit rate (43.5%) noticeably beats US500 (26.1%)** — Nasdaq's
  reaction aligns with the textbook direction almost twice as often.
- **Actual reactions skew heavily bullish** (26 of 46 events, 56.5%)
  regardless of the CPI surprise direction — consistent with this 2-year
  window being a broad uptrend for both indices, which appears to dominate
  the 30-minute post-release drift more than the CPI surprise itself.
- **Whipsaw (no sustained direction / sharp reversal) hit 8 of 46 events**
  (17%), with average 5-minute spike ranges of ~23 pts (US500) / ~123 pts
  (NAS100) — i.e. even "flat" CPI reactions still produce a real tradeable
  spike in the first few minutes before fading.
- **Average points moved when a clean Bullish/Bearish reaction did occur**:
  US500 ≈ 15-17 pts, NAS100 ≈ 57-89 pts (NAS100 moves ~4-5x the raw points
  of US500 on a clean reaction, roughly tracking its ~4x higher index level).
- **DST edge case confirmed**: release lands at 12:30 UK local (not 13:30)
  on 2025-03-12 and 2026-03-11 — the ~2-week windows each spring where UK
  DST hasn't started yet but US DST already has.
- **2025-10 CPI was never released** (government shutdown) — genuine gap,
  not a data error; excluded from the 23-event sample.

## Regenerating / extending

To add a new month once it's released: append a row to `cpi_calendar.csv`,
add its `release_utc` to `RELEASE_UTC` in `build_price_reaction.py`, fetch
its two raw candle JSON files via cTrader `get_trendbars` (symbolId 115/116,
M_1, ~20min before to ~35min after release) into `data/raw_candles/`, then
re-run `python3 data/build_price_reaction.py`.
