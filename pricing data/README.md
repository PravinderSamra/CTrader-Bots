# Pricing Data

Central store for all raw OHLCV price history in this repo. One subfolder per instrument.

## What's here

| Instrument | Timeframe | Bars | Coverage | Files |
|---|---|---|---|---|
| **XAUUSD** (gold) | M1 | 1,762,482 | 2021-07-18 → 2026-07-16 | `XAUUSD/XAUUSD_M_1_<year>.csv` (6 files) |
| **NAS100** (Nasdaq 100) | M5 | 212,383 | 2023-07-02 → 2026-07-03 | `NAS100/nas100_m5.csv` |
| **NAS100** | **M1** | *in progress* | target 5 years back from 2026-08 | `NAS100/NAS100_M_1_<year>.csv` |
| **US30** (Dow 30) | M5 | 212,296 | 2023-07-02 → 2026-07-03 | `US30/us30_m5.csv` |

All data: cTrader, Pepperstone UK GBP spread-bet account. Symbol IDs — XAUUSD 241, NAS100 205, US30 219.

## Column formats

Two formats exist because the sets were gathered by different scripts:

- **`<INSTRUMENT>_<PERIOD>_<YEAR>.csv`** (gold, and new NAS100 M1):
  `datetime,open,high,low,close,volume` — ISO-8601 UTC, e.g. `2026-07-16T20:04:00Z`
- **`<instrument>_m5.csv`** (US30, NAS100 M5):
  `timestamp_ms,datetime_utc,open,high,low,close,volume` — plain UTC, e.g. `2026-07-03 16:55:00`

**In both, the timestamp is the bar's OPEN time.**

## Important caveats

1. **Volume is TICK volume** (count of price updates), not real contract volume. Fine as a proxy for
   activity and time-at-price; do not treat it as traded contracts.
2. **Times are UTC.** The XAUUSD dealing day runs 22:00 → 21:00 UTC with a one-hour maintenance
   break. Beware UK DST when converting: 13:30 UTC is 2:30pm BST but 1:30pm GMT.
3. **These are spread-bet CFD prices**, not exchange prices. Close to the underlying but not identical.

## Gathering more data

`fetch_ohlcv.py` is a generalised, resumable fetcher (any instrument, any timeframe):

```bash
# 5 years of 1-minute NAS100
python3 fetch_ohlcv.py --instrument NAS100 --symbol-id 205 --period M_1 --years 5

# for a long job, run detached so a dropped shell can't kill it
nohup python3 fetch_ohlcv.py --instrument US30 --symbol-id 219 --period M_1 --years 5 \
  > us30_fetch.log 2>&1 &
tail -f us30_fetch.log
```

It writes an append-only raw log plus a checkpoint, so **re-running the same command resumes**
rather than starting over. Re-running later with a larger `--years` continues further back from
where it stopped. Output lands in `<INSTRUMENT>/<INSTRUMENT>_<PERIOD>_<YEAR>.csv`.

Requires `CTRADER_MCP_SLUG` in the environment. Rate is roughly 3.6 requests/sec, 100 bars per
request — about 80 minutes for 5 years of 1-minute index data.

**Availability verified:** NAS100 M1 goes back to at least June 2019 (7+ years), so the history
can be extended beyond the current 5-year target if wanted.

## Note on duplication

These files were copied here from their original project folders (`XAUUSD historical Pricing data/`
and `US30 London Range Breakout/`), which still hold their own copies so existing scripts keep
working. Git stores identical content once, so the duplication costs almost nothing in repo
history — but if either copy is ever updated, remember the other exists.
