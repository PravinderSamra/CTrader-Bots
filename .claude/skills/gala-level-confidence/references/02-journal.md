# 02 — The journal

Every live level call gets written to `trade-journal/YYYY-MM.jsonl`, one JSON
object per line, append-only — the same file and convention the
`liquidity-inducement-phone` skill uses, distinguished by
`"source": "gala-level-confidence"`.

## Why this is not optional

Two reasons, and the second is the important one.

**1. Ground truth for the score.** Every weight in `score_level()` is a judgement
call. Nothing has validated them. Without logged calls there is no way to find
out whether a 70 really beats a 45, and the score stays a plausible-looking
number forever.

**2. The gamma layer cannot be reconstructed.** CBOE publishes the *current*
option chain only. There is no free historical chain at any price point that
matters. So the net GEX, the gamma flip and the OI around your level at 15:30 on
a Friday exist in exactly one place after that moment passes: a journal entry
written at the time.

This is why `--as-of` replays report gamma as UNAVAILABLE. It is not a bug to be
fixed later — it is a permanent property of the data. **Every unjournalled live
call destroys evidence that cannot be recovered.** The gamma hypothesis becomes
testable only by accumulating these snapshots going forward.

## Writing entries

```bash
python3 src/level_confidence.py --level 4049.44 --journal
```

One entry per level per run. Calls that score SKIP still get logged — a level you
declined is as informative as one you took, and a day with no entry must be
distinguishable from a day never scanned.

Append only. Never rewrite the file. If you are journalling from a phone session
via GitHub tools, read the month's file first and append to it.

## Schema

Beyond the identifying fields (`id`, `logged_at`, `as_of`, `instrument`,
`level`, `direction`, `side`, `session`, `day_bias`, `price_at_idea`):

| Field | Contents |
|---|---|
| `verdict` / `score` | TAKE / CAUTION / WEAK / SKIP, and 0–100 |
| `score_items[]` | every component with its points and the measurement behind it |
| `entry` / `stop` / `stop_distance` / `target_2r` / `target_3r` | the plan |
| `history` | n, hold rate, win rate, expectancy, p90 and max pierce |
| `robustness[]` | expectancy and win rate at seven stop widths |
| `gamma` | **net_gex, gamma_flip, regime, expiries, gld_ratio, nearest_oi** |
| `volume_profile` | poc, vah, val, basis, nearest node |
| `cot` | the week's positioning snapshot |
| `provenance` | `live` or `as_of_replay` |
| `outcome` | null until `journal_review.py --write` fills it |

The `gamma` block is the irreplaceable part. Everything else can be rebuilt from
price history at any time.

## Grading

```bash
python3 src/journal_review.py --month 2026-08 --write
```

Walks M1 forward from each entry's `as_of`. Two separate clocks:

- **Trigger window (300 min)** — how long the call stays live waiting for price
  to actually reach the level. Marking a level and waiting is the strategy; a
  level reached at minute 64 is a live setup, not a miss.
- **Trade horizon (60 min)** — how long the position is managed once price
  arrives.

Conflating these was a real bug: a single 60-minute window scored a valid call
as `NEVER_TRIGGERED` because price arrived at minute 64.

Outcomes: `TARGET` (+3R), `STOPPED` (−1R), `OPEN_AT_HORIZON` (partial R),
`NEVER_TRIGGERED` (no trade), `NO_DATA`.

The stop is checked before the target and assumed hit first within a bar — the
same pessimistic convention the score was built on, so predicted and realised
are measured the same way and can legitimately be compared.

## Reading the review

The two tables that matter:

- **By score band** — win rate and mean R should rise monotonically with the
  band. If they don't, the weights are wrong and should be changed or dropped.
- **By gamma regime** — the pinning hypothesis, tested against your own logged
  calls. This is the only place that question can ever be answered.

**Report small samples as small.** Below ~30 triggered calls per bucket these
tables are plumbing, not findings. Say that explicitly; a three-row table with
percentages in it looks like evidence and isn't.
