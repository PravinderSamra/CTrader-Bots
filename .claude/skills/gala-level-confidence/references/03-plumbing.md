# 03 — Plumbing: everything a fresh session needs to know

Read this before the first run in a new session. Every item here is a failure
mode that was actually hit and fixed, not a hypothetical.

## Preflight

```bash
python3 "Gala Heatmap/src/preflight.py"
```

Checks the token, Python version, repo layout, cTrader reachability, and the
three external feeds in about 20 seconds. Run it if anything looks wrong; skip it
if the user is in a hurry and just run the tool.

## Paths and working directory

Scripts resolve their imports and output paths from `__file__`, so they work from
anywhere. **Sessions start at the repo root**, so prefer:

```bash
python3 "Gala Heatmap/src/level_confidence.py" --level 4049
```

The folder name contains a space — always quote it. `cd "Gala Heatmap"` then
`python3 src/...` works too; both write reports to `Gala Heatmap/reports/` and
journal entries to `trade-journal/` regardless of where you ran from.

## Timeouts — the most likely fresh-session failure

**A full run takes 2–4 minutes**, dominated by M1 paging (the cTrader server caps
every trendbar response at 100 bars, so 14 days of M1 is ~150 sequential
requests). The default Bash tool timeout is 2 minutes and **will kill it
mid-run**.

Always pass an explicit timeout of at least 900000 ms. If you are running
several levels, or `journal_review.py` over a month, allow more.

## Credentials

Only one is needed: `CTRADER_MCP_SLUG` (or `CTRADER_MCP_TOKEN`) — the `eyJwb…`
slug. If missing you get:

```
FAILED: Neither CTRADER_MCP_SLUG nor CTRADER_MCP_TOKEN is set.
```

Say so and stop. Do not invent one, and do not fall back to the `mcp__ctrader__*`
tools — those are a different transport and the scripts do not use them.

Nothing else needs a key. Yahoo, CBOE and CFTC are all unauthenticated. The DOM
recorder is the exception and needs its own cTrader Open API app, but it is not
part of the scoring path.

## Instrument scope — this one silently produced garbage

The futures / options / gamma / COT layers are **gold-only**. They are gated on
the symbol (`GOLD_SYMBOLS` in `level_confidence.py`).

Before that gate existed, running UK100 computed a "GC basis" of **−6768** (gold
futures minus a FTSE price), shifted gold's volume profile by it to manufacture
nodes at UK100 prices, and attached gold's net GEX to a UK100 level. Every number
looked plausible and all of them were fictitious.

For a non-gold symbol the report now says so explicitly and the score rests on
price history alone — which usually means a much lower total. **That is correct
behaviour, not a broken run.** Explain it rather than trying to "fix" it.

Also note: the stop-floor evidence (−0.33R unfloored, +0.62R at 7 pts) was
measured on XAUUSD only. The report says so, and flags that the floor on any
other instrument is scaled from price rather than verified.

## Market-closed / stale data

If the newest M1 bar is more than 30 minutes old the report opens with a
**MARKET LOOKS CLOSED** banner and states the age. Everything below it — spot,
day bias, session — describes the last session that traded.

This matters most at weekends, when a Saturday run happily reports "bearish day"
from Friday's close. Surface the banner; never present a stale run as a live
read.

## What each script needs, and what it costs

| Script | External calls | Typical runtime |
|---|---|---|
| `level_confidence.py` | cTrader (H1+M1), Yahoo ×3, CBOE, CFTC | 2–4 min |
| `gold_context.py` | cTrader (H1), Yahoo ×3, CBOE, CFTC | 60–90 s |
| `level_stats.py` | cTrader (H1+M1) | 2–4 min |
| `journal_review.py` | cTrader (M1) | 30–90 s |
| `dom_recorder.py` | cTrader Open API (separate creds) | 60 s probe |

External feeds retry three times with backoff — a transient reset once removed
the whole options layer from a run before that was added. If a layer is still
unavailable after retries the report says so and the score is capped; it does not
silently score zero.

## Reading stderr

Progress goes to stderr, the report to stdout. Useful lines:

- `[3/5] spot … → bearish day · late session  ⚠ last bar 47.9h old` — staleness
- `[4/5] futures/options/COT layers SKIPPED` — non-gold instrument
- `note: dropped N futures bars outside the measured basis window` — expected in
  small numbers (weekends). Hundreds means the basis window is too narrow.
- `roll=yes` — a contract roll is inside the window; the per-bar basis conversion
  already handles it.

## Common errors and what they mean

| Message | Cause | Action |
|---|---|---|
| `Neither CTRADER_MCP_SLUG nor…` | no token | stop, tell the user |
| `HTTP 401 — token unauthorised or expired` | stale slug | stop; it is a credential issue, not retryable |
| `only N M1 bars — cannot build reliable statistics` | window too short, or a long market closure | raise `--days` |
| `only N H1 bars returned — widen --days` | same | raise `--days` |
| `symbol 'X' not found` | wrong name | the error lists available symbols; all end `_SB` |
| `only N overlapping hours — cannot measure basis` | gold layer, thin overlap | usually a weekend; retry when markets open |
| `no levels survived filtering` | only when auto-detecting | pass `--level` explicitly |

## Output locations

- Reports: `Gala Heatmap/reports/` (markdown, overwritten per symbol)
- Journal: `trade-journal/YYYY-MM.jsonl` (append-only, never rewritten)
- `--json` on `level_confidence.py` emits the journal records to stdout instead
  of the markdown report, for piping.

## Dependencies

Python 3.10+ (3.11 in this environment). **Everything in the scoring path is
standard library** — no numpy, scipy, pandas or yfinance. CBOE supplies option
greeks directly, which is why no Black-Scholes is needed.

Only `dom_recorder.py` needs installs (`ctrader-open-api`, `twisted`), and it is
optional.
