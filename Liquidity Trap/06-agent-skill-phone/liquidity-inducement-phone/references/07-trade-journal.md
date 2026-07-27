# 07 — The Trade Journal

Every idea this skill produces gets written down, **including the ones that say
no-trade**. The point is not record-keeping for its own sake: it is that after
enough sessions, "does the London window work for me", "is the RR floor right",
"do drying-volume days actually stall" become answerable from *your own logged
ideas and what price did next* — rather than from a replay whose assumptions I
picked. Today's research was wrong three times in a row precisely because it
had no ground truth to check against. The journal is that ground truth.

## Where it lives

```
trade-journal/YYYY-MM.jsonl      # one JSON object per line, append-only
```

At the repo root, one file per month. JSONL so appending never rewrites history
and two sessions cannot corrupt each other's entries.

## Writing an entry

**One entry per idea block per scan** — the primary, the secondary if offered,
and the London alternative each get their own line, so `kind` distinguishes
them. A scan producing "no trade" still logs, with `state: "NO_TRADE"` and the
reason; a day with no entry is indistinguishable from a day never scanned, and
that gap is what makes later analysis worthless.

From a phone session, append via the GitHub tools (`create_or_update_file` on
the month's file, or `push_files`). Read the existing file first and append —
never overwrite. If the month's file does not exist, create it.

### Schema

```json
{
  "id": "2026-07-27T17:36:28Z-XAUUSD-primary",
  "logged_at": "2026-07-27T17:40:02Z",
  "instrument": "XAUUSD",
  "as_of": "2026-07-27T17:36:28Z",
  "price_at_idea": 4074.265,
  "session": "NY_AFTERNOON",
  "kind": "primary",
  "state": "WATCHING",
  "direction": "long",
  "trigger_zone": [4070.25, 4072.82],
  "entry_zone": null,
  "stop": null,
  "target_zone": [4093.93, 4098.44],
  "rr": null,
  "context": {
    "bias_label": "NEUTRAL", "bias_score": 12,
    "adr_used_pct": 59.3, "remaining_budget": 34.83,
    "expansion_state": "MODERATE",
    "volume_state": "drying_up", "volume_rel": 0.68,
    "target_touches": 6,
    "sweep": null,
    "no_mans_land": false
  },
  "management": "BE at 4076.86-4079.88; trail below each pool on a close beyond it; tighten on LOW_FUEL",
  "reason": "no sweep yet - gate 2 fails",
  "review": null
}
```

Field notes:

- **`id`** — `{as_of}-{instrument}-{kind}`. Deterministic, so a re-scan at the
  same timestamp cannot double-log.
- **`kind`** — `primary` | `secondary` | `london_alt`.
- **`state`** — `ARMED` | `WATCHING` | `NO_TRADE`. Only `ARMED` implies you
  would actually be in; the others are still logged, because "what did the
  setups I passed on go on to do" is exactly as informative.
- **`entry_zone` / `stop` / `rr`** — null when not armed. Do not invent them to
  fill the schema.
- **`context`** — copied verbatim from the analyzer output. It is what lets a
  later review ask "did drying volume predict the stall" without re-deriving.
- **`review`** — always `null` at write time. Filled later by the reviewer.

## Reviewing entries

`scripts/journal_review.py` scores unreviewed entries against what price
actually did afterwards:

```
python3 journal_review.py                 # report only
python3 journal_review.py --write         # also write review back into the journal
python3 journal_review.py --month 2026-07
```

For each entry it fetches M5 bars after `as_of` and asks, in order: did price
reach the trigger zone; did it then reach the entry zone; did target or stop
come first; how far in favour did it get (MFE). It fills:

```json
"review": {
  "reviewed_at": "...", "triggered": true, "filled": true,
  "outcome": "target",          // target | stop | expired | no_fill
                                // | never_triggered | watch_only
  "r": 3.6, "mfe_r": 4.1, "max_rr_reached": 4.1,
  "verdict": "target_hit",
  "bars_to_outcome": 22, "bars_available": 340,
  "excursion_pts": null         // unfilled ideas only
}
```

**`max_rr_reached` (= `mfe_r`) is the field that earns its keep**, and
`verdict` is what it buys. Judging an idea only on "did it reach the pool"
throws away the difference between two very different failures:

| `verdict` | meaning | what to fix |
|---|---|---|
| `target_hit` | destination reached | nothing |
| `direction_right_destination_missed` | ran ≥1.0R in favour, then stopped | **the exit** — reference 05 |
| `direction_marginal` | 0.3–1.0R | entry timing / LB quality |
| `direction_wrong` | never cleared 0.3R | **selection** — the gates |
| `not_taken` | never filled | see `excursion_pts` |

A run of `outcome: stop` carrying `direction_right_destination_missed` does
not mean the ideas were wrong — it means the management was. That is the whole
argument for actively managing rather than letting trades run to a fixed pool.

`excursion_pts` does the same job for ideas that never filled: an idea price
then ran 20 points in favour of was a right call with a wrong entry, which is a
different fix from a wrong call.

**Read `bars_available` before trusting a verdict.** An idea logged minutes
before the review has almost no forward data; the reviewer prints a warning
for anything under 2 hours. Those verdicts are provisional — re-run the review
the next day to settle them.

## Running the review without blocking a scan

Reviewing fetches a lot of history and takes far longer than producing an idea.
**Do not make the user wait for it.** When a scan is requested and there are
unreviewed entries, spawn a background subagent to run the review and carry on
with the scan immediately; report its findings when they arrive, or on the next
scan.

The user has asked for this explicitly, so it is expected behaviour here rather
than something to check first. Keep the subagent's brief narrow — run the
review, summarise outcomes and any pattern in `mfe_r` versus `outcome` — and
relay only what changes a decision.
