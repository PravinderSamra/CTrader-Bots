# UK100 Historical Pricing Data

1-minute OHLCV for **UK100** (FTSE 100 index CFD), pulled from cTrader and stored as
per-year CSVs for the ORB backtesting studies.

| | |
|---|---|
| Symbol | `UK100` (cTrader `symbolId` **113**, "UK 100 Index") |
| Timeframe | M1 |
| Span | **2021-07-29 → 2026-07-28** (~5 years) |
| Rows | **1,635,908** |
| Columns | `datetime,open,high,low,close,volume` |
| Timestamps | ISO-8601 UTC, **bar open** time |
| Volume | broker **tick count**, not traded contracts |
| Audit | PASS (no duplicates, no OHLC violations, no non-positive prices) |

## Bars per year

| Year | Bars |
|---|---|
| 2021 | 151,867 (from 29 July) |
| 2022 | 356,178 |
| 2023 | 339,102 |
| 2024 | 317,602 |
| 2025 | 299,539 |
| 2026 | 171,558 (to 28 July) |

The year-on-year decline from 2022 is expected rather than a defect: a bar exists only
for minutes that traded, and 2022 was an unusually active year (Ukraine, the gilt
crisis). It is worth keeping in mind when comparing per-year results.

## Gaps

The audit reports 664 non-weekend gaps over an hour. Inspection shows these are UK
market closures, not missing data — Christmas and Boxing Day, the four-day Easter
weekend, New Year. A FTSE calendar simply has more holidays than a metals calendar.
The largest is 108 hours across Christmas 2025.

## How this was fetched

Using the same script as the gold data, which paces itself and checkpoints so an
interrupted run resumes rather than restarting:

```bash
cd "XAUUSD historical Pricing data"
export CTRADER_MCP_SLUG=...        # a 401 means the token has expired
nohup python3 fetch_xauusd_history.py \
    --symbol-id 113 --symbol-name UK100 --years 5 --period M_1 \
    --out-dir "../UK100 historical Pricing data" > fetch.log 2>&1 &
```

Roughly 16,400 requests at ~3.2/s — about 85 minutes. **Do not fetch candles by
issuing tool calls**; that is ~16,000 model round-trips for a job a script does for
free.

The `_raw_bars_*.jsonl` and `_checkpoint_*.json` work-files are gitignored: they exist
so an interrupted fetch can resume, and the per-year CSVs are the deliverable.

## Consumed by

`Backtesting Engine/studies/orb_uk100/` and `orb_uk100_exits/`, via
`engine data-prepare`, which converts these to the cTrader `m1-csv` format, audits
them, and splits the holdout onto disk before any optimisation runs.
