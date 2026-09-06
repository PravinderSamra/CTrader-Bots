# Sources already extracted — read before re-deriving anything

Rule 1 in `../CLAUDE.md` exists because the API contract was extracted in one
session and then not re-read in the next, so documented behaviour got inferred
from probing instead. This index is the fix. **Check here first.**

## Vendor documentation

| Source | Where | Contains |
|---|---|---|
| API contract + route table | extracted from the site's JS bundle | Every endpoint, its parameters (or lack of them), required headers, 87 field descriptions |
| FAQ | same bundle | **Historical Data** section (1-second granularity, ~23,400 samples/session, 365-day availability "for purchase or lookup"), licensing (personal, non-commercial, no redistribution), OI update schedule (08:00 ET, fixed all day), Classic described as *naive GEX* |
| Metrics page | same bundle | Why OI is the reliable "how many"; volume as an *"intermediary solution"* giving a *"rough idea"*; explicit admission that buy/sell cannot be told from Time & Sales |

The bundle is not committed (it is the vendor's, and large). Re-fetch the
site's main JS bundle and grep it; `docs/api-reference.md` holds the distilled
result.

## Video transcripts — `../youtube-research/`

| Source | Value |
|---|---|
| `transcripts/gexbot-channel/` (12 English, ~87k words) | **Primary source.** The founders on their own model. Includes the two-part NQ futures interview, which is our exact use case |
| `gexfuture-master-classic-*` | Siento's operational rules — the specification's origin |
| `chart-fanatics-*` | Siento's long-form explanation of *why* |
| `analysis/gexbot-channel-corpus.md` | Write-up, including one retracted section — read the retraction, not just the claim |
| `transcripts/gexbot-channel/MANIFEST.md` + `FETCH_LOG.txt` | Which videos have captions, which genuinely do not, and one corrected false positive |

## Our own data

| Source | Where |
|---|---|
| Live snapshots, 5-minute | Firestore `gex_snapshots` / `gex_latest` |
| Completed sessions, derived | Firestore `gex_sessions` |
| Free independent check | Cboe delayed NDX chain — no key, no account; reproduces GexBot's per-strike numbers at r² ≈ 0.95 (`scripts/sign_convention_test.py`) |

## Settled — do not re-derive

- **Sign convention**: naive; calls positive, puts negative. Confirmed three
  ways (measured at r ≈ 0.97, stated in the FAQ, stated by the founder).
- **Units**: notional gamma per 1% move, in $m — 98% of textbook.
- **Scopes**: `zero` = 0DTE, `one` = next expiry, `full` = 3 months.
- **OI is frozen intraday**; volume is the only Classic reading that moves.
- **NDX is a suitable instrument** — the co-founder trades NQ deliberately.
