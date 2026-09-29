# Research data

## squeezemetrics_dix_gex.csv
- Source: SqueezeMetrics, `https://squeezemetrics.com/monitor/static/DIX.csv` (free download).
- Downloaded 2026-09-29. Covers 2011-05-02 to 2026-09-28, one row per US trading day.
- Columns: `date`, `price` (S&P 500 close), `dix` (dark-pool index), `gex` (dealer gamma exposure, $ per 1% move).
- `gex < 0` = dealers short gamma (hedging extends moves); `gex > 0` = long gamma (hedging dampens moves).
- Published after the close: a strategy trading on day D may only use the value dated D-1.
- Built from open interest, so same-day (0DTE) options opened and closed intraday are not included.
- Methodology differs from GEXbot; do not mix the two sources in one test.
