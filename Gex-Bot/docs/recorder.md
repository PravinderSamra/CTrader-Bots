# GexBot snapshot recorder

Captures GexBot gamma levels into Firestore every 5 minutes through the US
cash session, so we can answer from our own data the question the two source
videos disagree on: **does price respect the volume-derived walls or the
open-interest-derived walls?**

## What this recorder is for

> **Correction (2026-09-05).** This section previously stated there was no
> history endpoint on our tier and that past sessions were unrecoverable.
> **That was wrong.** It came from probing guessed paths (`/hist`,
> `/history`, `/download`, …), getting 404s, and mistaking "my guesses were
> wrong" for "the capability does not exist". The real endpoint is
> `/hist/eod/{TICKER}`, which returns the last completed session at 1–2
> second resolution — roughly 200× denser than this recorder. The full
> account is in [`../research/volume-vs-open-interest.md`](../research/volume-vs-open-interest.md).

The Classic *live* endpoint serves only a current snapshot, so this recorder
samples it every 5 minutes to drive the dashboard.

It is **no longer the primary research instrument**. That job belongs to
`archive_eod.py` and `.github/workflows/gexbot-eod.yml`, which capture each
completed session at full resolution. This recorder remains useful as the
live feed the dashboard reads, and as a same-day record if an EOD download is
ever missed.

One limit does still hold, for a narrower reason: the EOD report's `date`
parameter is ignored and only ever serves the latest session, and the dated
archive is Quant-tier (403). So a session missed is still a session lost —
one day at a time, rather than all of history.

## Why Firestore rather than committing to the repo

This repository is **public**, and GexBot Classic is a **paid subscription**.
Committing a continuous, machine-readable feed of its computed levels here
would republish a paid data product to anyone who browsed the repo.

Firestore keeps it private behind the same rules model the trade journal
uses, reuses the `FIREBASE_SERVICE_ACCOUNT_JSON` secret already configured,
and has two useful side effects: the recorder writes nothing to the repo, so
it never triggers `deploy-dashboard.yml`, and it adds no commit noise (a
5-minute cadence would otherwise be ~100 commits a day).

`Gex-Bot/data/` is gitignored so a local run can never accidentally land
recorded data in the public repo.

> Note: GexBot's terms were not directly readable (their site is
> client-side rendered), so the redistribution concern above is a strong
> inference rather than a quoted clause. It is the conservative default.

## Setup

**One new repository secret is required:**

| Secret | Value | Status |
|---|---|---|
| `GEX_BOT_API_TOKEN` | the GexBot API token | **must be added** |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | service account JSON | already configured |

**Publish the updated Firestore rules.** `xauusd-dashboard/db/firestore.rules`
now includes `gex_latest` and `gex_snapshots`. Paste the file into Firebase
Console → Firestore Database → Rules → Publish. Until this is done the
dashboard cannot read the levels (the recorder still writes fine — the Admin
SDK bypasses rules).

**Merge to `main`.** GitHub only runs scheduled workflows from the default
branch, so nothing fires while this lives on a feature branch.

Then trigger it once manually (Actions → Record GexBot snapshots → Run
workflow) to confirm the wiring before relying on the schedule.

## What gets written

Two collections:

| Collection | Doc id | Purpose |
|---|---|---|
| `gex_snapshots` | `{TICKER}_{scope}_{source_ts}` | Append-only history for analysis |
| `gex_latest` | `{TICKER}_{scope}` | Current levels, overwritten each poll — what the dashboard reads |

Because the history doc id embeds the source timestamp, a repeated poll of an
unchanged feed rewrites an identical document. Idempotent by construction, and
cheaper than reading first to check.

Each record carries **both readings side by side** and takes no view on which
is correct:

```
spot, zero_gamma
major_pos_vol, major_neg_vol, sum_gex_vol      <- volume reading
major_pos_oi,  major_neg_oi,  sum_gex_oi       <- open-interest reading
max_priors                                      <- 1/5/10/15/30-min max-change panel
regime_vol, regime_oi, regimes_agree, walls_agree, spot_vs_zero_gamma
```

`delta_risk_reversal` is also stored but is documented by the vendor as a
discontinued metric, so it should not be relied on.

The derived `regimes_agree` / `walls_agree` flags exist so disagreement is
queryable directly rather than recomputed later. The recorder also prints a
note whenever the two readings disagree on regime.

Default symbols: `spx`, `nq_ndx`, `es_spx`, `ndx` at `zero` (0DTE) scope.

### The strike ladder

`gex_latest` also carries the full 142-strike ladder, one map per strike:

```
{ strike, gex_vol, gex_oi, priors: [5 earlier samples] }
```

It is written **only** to `gex_latest`, which is overwritten each poll and so
stays a fixed ~40 KB (Firestore's document cap is 1 MiB). Appending it to
`gex_snapshots` instead would add that much per symbol per poll — of the order
of a gigabyte a month — to answer a question the compact record already
answers.

`priors` is what lets a wall be read as *building* or *being taken off*, and is
what GexBot's own ladder plots as dots. Two caveats worth knowing:

- **The ordering is confirmed** (2026-09-05), no longer inferred. GexBot's
  own field reference documents the max-change intervals as 1, 5, 10, 15 and
  30 minutes, with the sub-fields ordered most-recent-first. Index 0 is the
  most recent sample.
- **They track the volume series, not open interest.** Verified against live
  data — a far-OTM strike's priors equalled its `gex_vol` exactly while its
  `gex_oi` differed. The dashboard therefore hides the dots on the
  open-interest reading rather than borrowing another quantity's history.

## Volume against write quota

4 symbols × 12 polls/hour × ~9 hours ≈ 430 snapshot writes/day, plus the same
again for `gex_latest` — roughly **860 writes/day** against Firestore's
20,000/day free tier. Comfortable. Adding scopes multiplies this: all three
scopes on four symbols would be ~2,600/day, still fine.

Actions minutes are free — the repository is public.

## Running it by hand

```bash
export GEX_BOT_API_TOKEN=...

# Print, write nothing
python3 scripts/record_snapshot.py --tickers spx nq_ndx --scopes zero --stdout

# Local JSONL only (gitignored), one file per UTC day
python3 scripts/record_snapshot.py

# What CI runs
python3 scripts/record_snapshot.py --firestore --no-local
```

Tests for the Firestore value encoder — the one part that can fail silently,
since a wrong type tag writes junk rather than erroring:

```bash
python3 scripts/__tests__/test_firestore_encoding.py
```

## Known limitations

- **The Firestore write path has not been executed end to end.** No service
  account credentials were available in the development session, so the
  encoder is unit-tested and both failure paths (missing and malformed
  credentials) are verified, but the first real write will happen on the
  first manual run. Check that run's log.
- **The RTH refresh cadence is still unmeasured**, so 5 minutes is a
  reasonable guess, not a derived figure. Once a session of data exists, the
  distinct `source_ts` values will show how often the feed actually updates,
  and the cron can be relaxed or tightened accordingly.
- **Scheduled runs drift.** GitHub queues scheduled workflows on shared
  infrastructure and they are routinely minutes late, occasionally dropped.
  Harmless here — each record carries the feed's own `source_ts`, so a late
  sample is still correctly timestamped — but it is why this cadence is not
  suitable for a live trading feed. That is what the Cloudflare Worker in step
  2 is for.
