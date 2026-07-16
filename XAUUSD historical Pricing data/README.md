# XAUUSD Historical Pricing Data — Retrieval Runbook

**Audience:** an automated agent (any model) with **no prior context** on this repo.
**Goal:** pull ~5 years of XAUUSD 1-minute OHLCV from cTrader and save it here as
per-year CSVs, without getting the connection rate-limited or blocked.

The heavy lifting is done by **one self-contained script** — `fetch_xauusd_history.py`
in this folder. Your job is to run it, watch it, verify the output, and commit.
**Do NOT** try to pull candles by issuing `get_trendbars` tool calls yourself — that
is ~18,000 calls for this job and will burn tokens and time for no benefit. Run the
script; it loops internally.

---

## 0. TL;DR — the happy path (4 commands)

```bash
cd "XAUUSD historical Pricing data"
# make sure the token is set (see §2 if this prints nothing):
echo "${CTRADER_MCP_SLUG:+set}"
# run detached so a dropped shell can't kill a ~2-hour job:
nohup python3 fetch_xauusd_history.py --years 5 --period M_1 > fetch.log 2>&1 &
tail -f fetch.log      # watch progress; Ctrl-C stops watching, NOT the job
```
When `fetch.log` shows `FINALIZE DONE`, jump to **§6 (verify)** then **§7 (commit)**.
If it dies or the box restarts, just re-run the **same command** — it resumes from a
checkpoint (§5).

---

## 1. What we are delivering (matches the requester's data spec)

| Spec field   | Requested                                   | What this produces                                                        |
|--------------|---------------------------------------------|---------------------------------------------------------------------------|
| Granularity  | 1-minute OHLCV (5-min acceptable)           | `--period M_1` (default). `--period M_5` for the lighter 5-min pull.       |
| History      | 3–5+ years                                   | `--years 5` (default). Verified available: M_1 ≥6y back, D_1 ≥8y back.     |
| Columns      | `datetime, open, high, low, close, volume`  | Exactly these, in this order.                                             |
| Timestamp    | ISO-8601 w/ tz **or** explicit UTC          | **ISO-8601 UTC**, e.g. `2026-07-14T19:58:00Z`. It is the bar **OPEN** time.|
| Format       | CSV or Parquet                              | CSV, one file per calendar year. (Parquet conversion note in §8.)          |
| Delivery     | a repo folder                               | `XAUUSD historical Pricing data/data/XAUUSD_M_1_<year>.csv`               |

Feed / "which feed" / weekend handling → **§9 (read before shipping)**.

---

## 2. Prerequisite: the cTrader token

The script reads `CTRADER_MCP_SLUG` (preferred) or `CTRADER_MCP_TOKEN` from the
environment. In this repo's sessions it is normally already set. Check:

```bash
echo "${CTRADER_MCP_SLUG:+set}${CTRADER_MCP_TOKEN:+set}"
```
If that prints nothing, the token is missing — **stop and report it**. Do not invent
one. (An expired token shows up later as `HTTP 401 ... not retryable`; same action:
report it, don't retry.)

---

## 3. Why this needs a looping script (the two API limits)

Both were verified empirically against the live API on 2026-07-16. `get_trendbars`:

1. **Returns at most 100 bars per request**, and always the 100 bars that **end at
   `toTimestamp`**. Making `fromTimestamp` earlier does *nothing* — you still get only
   the last 100.
2. **Requires the window to be ≤ 720 hours (30 days)**. A wider window returns an
   **empty list with no error** (silent). This is why naive "give me 5 years" calls
   come back empty and look broken.

So contiguous history can only be gathered by walking **backwards** 100 bars at a
time, moving `toTimestamp` to just before the previous page's earliest bar. For 5
years of 1-minute gold that is **~18,000 requests**. The script does this with one
keep-alive connection, gentle pacing, checkpointing, and reconnect/backoff.

---

## 4. Running it

**Default (5 years, 1-minute):**
```bash
cd "XAUUSD historical Pricing data"
nohup python3 fetch_xauusd_history.py --years 5 --period M_1 > fetch.log 2>&1 &
tail -f fetch.log
```

Useful flags (defaults are already correct for the job):
- `--years 5` — how far back. `--years 3` if you want a smaller pull.
- `--period M_5` — 5-minute bars: **~1/5 the requests (~3,600, ~20 min)**, an
  acceptable fallback per the spec if the M_1 run is too slow or keeps dropping.
- `--sleep 0.12` — seconds between requests. Raise to `0.25` if you ever see
  repeated transient errors (gentler on the server); lower only cautiously.
- `--window-hours 336` — request window width (14 days). Leave it. It must stay
  ≤720; 14 days always straddles weekends/holidays so the walk never stalls in a gap.

Progress lines look like:
```
[..Z] M_1: 2000 pages, 200000 bars, at 2025-11-20T14:00:00Z (2.4 req/s)
```
`at <date>` is how far back it has reached — it should march steadily toward your
start date. The run ends with `FETCH DONE` then `FINALIZE DONE`.

---

## 5. If it stops early (crash, restart, disconnect)

The script is **resumable**. It appends every page to `_raw_bars_M_1.jsonl` and saves
a cursor to `_checkpoint_M_1.json` every 50 pages. To continue, just run the **same
command again** — it picks up from the checkpoint. Do not delete the `_raw_*` or
`_checkpoint_*` files mid-job; they are the resume state.

To rebuild the CSVs from an already-collected raw log without re-fetching:
```bash
python3 fetch_xauusd_history.py --period M_1 --finalize-only
```

---

## 6. Expected scale & verification

| Run          | Requests | Rough wall time | Raw bars | CSV on disk |
|--------------|----------|-----------------|----------|-------------|
| 5y **M_1**   | ~18,000  | ~1.5–2.5 h      | ~1.8M    | ~80 MB total (≈5 files) |
| 5y **M_5**   | ~3,600   | ~20–30 min      | ~370k    | ~17 MB total |

After `FINALIZE DONE`, verify before committing:
```bash
ls -la data/
head -3 data/XAUUSD_M_1_2026.csv          # header + 2 rows
python3 - <<'PY'
import csv, glob
for f in sorted(glob.glob('data/XAUUSD_M_1_*.csv')):
    rows = list(csv.DictReader(open(f)))
    ts = [r['datetime'] for r in rows]
    ok_sorted = ts == sorted(ts)
    ok_unique = len(set(ts)) == len(ts)
    ok_ohlc = all(float(r['high']) >= float(r['low']) for r in rows)
    print(f, len(rows), 'sorted' if ok_sorted else 'NOT-SORTED',
          'unique' if ok_unique else 'DUPES', 'ohlc-ok' if ok_ohlc else 'OHLC-BAD',
          ts[0], '->', ts[-1])
PY
```
Expect: header is exactly `datetime,open,high,low,close,volume`; each file **sorted**,
**unique**, **ohlc-ok**; earliest file starts ~5 years ago; latest ends near today.
Gaps in the minute sequence are **normal** — they are market closures (weekends, the
daily ~21:00–22:00 UTC break, holidays). The script never invents synthetic rows.

---

## 7. Commit to the repo

Only after §6 passes. From the repo root:
```bash
cd /home/user/CTrader-Bots
# remove the resumable work files — they are NOT part of the deliverable:
rm -f "XAUUSD historical Pricing data/_raw_bars_"*.jsonl \
      "XAUUSD historical Pricing data/_checkpoint_"*.json \
      "XAUUSD historical Pricing data/fetch.log"
git add "XAUUSD historical Pricing data/"
git commit -m "Add XAUUSD 5y 1-minute historical OHLCV (cTrader spread-bet feed)"
git push -u origin <the branch you were told to use>
```
Do not `git add` the whole repo blindly. If a `git push` fails on network, retry a few
times with a short backoff; do not force-push.

---

## 8. Format notes

- Files are **per calendar year** so no single file approaches GitHub's 100 MB hard
  cap. The full 5y M_1 set is ~80 MB across ~5 files — acceptable, but large for git.
  Options if you want it smaller (all optional, ask the requester first):
  - `gzip data/*.csv` → ~4–5× smaller, still `datetime,open,high,low,close,volume`.
  - Parquet: `pip install pandas pyarrow` then
    `python3 -c "import pandas as pd,glob;[pd.read_csv(f).to_parquet(f.replace('.csv','.parquet'),index=False) for f in glob.glob('data/*.csv')]"`.
    The spec accepts CSV **or** Parquet, so plain CSV is already compliant.

---

## 9. Feed & caveats — INCLUDE THESE WHEN YOU HAND OVER THE DATA

The requester explicitly asked "which feed" and how weekends are handled. State this:

- **Feed:** cTrader, **Pepperstone UK spread-bet demo** account (`XAUUSD_SB`,
  symbolId 241). These are spread-bet quotes — extremely close to Pepperstone CFD
  XAUUSD, but **not** COMEX/exchange gold and not tick-for-tick identical to any other
  broker. Good for model *shape* (the spec says Pepperstone-matching is "a bonus, not
  required"); do not represent it as exchange data.
- **Volume is TICK volume**, not contract/exchange volume — it is the number of price
  updates within the bar (typically ~40–250/min). Treat it as an *activity* proxy, not
  traded lots. This is inherent to the cTrader CFD/SB feed; there is no real volume
  available from this source.
- **Timestamps are UTC, bar-OPEN time**, ISO-8601 with a trailing `Z`.
- **Prices** are display prices (pipettes ÷ 10⁵), e.g. `4056.09`. Gold quotes to 0.01.
- **Weekends/holidays:** simply absent — no rows exist while the market is closed, and
  nothing is forward-filled. Expect a ~48h gap every weekend and a short daily break
  around 21:00–22:00 UTC. Downstream resampling (to 5m/15m/1H) should treat gaps as
  gaps, not zero-volume bars.

---

## 10. Troubleshooting

| Symptom                                             | Cause / action |
|-----------------------------------------------------|----------------|
| `FETCH FAILED: neither CTRADER_MCP_SLUG nor ...`    | Token not in env. Report it; do not fabricate. (§2) |
| `HTTP 401 ... not retryable`                        | Token expired. Report it; do not retry. |
| Every request returns 0 bars from the start         | Usually a >720h window — you changed `--window-hours` above 720. Reset to 336. |
| Loop stops with `history floor`                     | Normal — the feed has no older data at that point. |
| Repeated `transient error ... reconnecting`         | Server is throttling. Raise `--sleep` to 0.25–0.5 and re-run (it resumes). |
| `No space left on device`                           | Delete `fetch.log` / old raw logs, or run `--period M_5` (5× smaller). |
| Shell closed and job died                            | You didn't use `nohup ... &`. Re-run the same command (it resumes). |
| Want to start completely over                        | Delete `_raw_bars_*.jsonl` and `_checkpoint_*.json`, then re-run. |
