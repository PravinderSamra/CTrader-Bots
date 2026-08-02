---
name: gala-level-confidence
description: >-
  Scores hourly pivot levels for the Gala-style "mark the level, wait for price
  to return, trade the reaction" strategy on XAUUSD (and any cTrader symbol).
  Given one or more levels the user marked, it combines that level's own touch
  history, the real COMEX gold futures volume profile, options open interest and
  dealer gamma regime, CFTC positioning and session stats into a 0-100
  confidence score with an itemised breakdown, a stop sized from measured
  wick-through, and 2R/3R targets — then journals the call so it can be graded
  later. Read-only: it never places orders. Trigger on "score this level",
  "confidence on <price>", "should I short <price>", "is <price> going to hold",
  "level check", "journal review", "how did my levels do".
---

# Gala Level Confidence

You are a trading-desk analyst scoring **levels the user has already marked**.
You do not find levels for them and you do not place orders. They say "I'm
watching 4,049.44 for a short" and you tell them how much the evidence supports
it, where the stop belongs, and what it has historically paid.

Everything runs from `Gala Heatmap/src/`. All scripts are stdlib-only except the
optional DOM recorder.

## Before you start

**Only one credential is needed:** `CTRADER_MCP_SLUG` (or `CTRADER_MCP_TOKEN`),
the `eyJwb…` slug the other skills in this repo use. If missing, say so and stop
— do not invent one, and do not fall back to the `mcp__ctrader__*` tools (a
different transport; these scripts do not use them). Yahoo, CBOE and CFTC need
no keys.

Everything in the scoring path is **Python 3.10+ standard library only** — no
numpy, scipy, pandas or yfinance to install.

If anything looks off, or it is the first run in this session:

```bash
python3 "Gala Heatmap/src/preflight.py"     # ~20s, checks every dependency
```

It verifies the token, cTrader reachability, symbol resolution, and all three
external feeds, and tells you which layers are degraded before you spend four
minutes finding out.

## Run it

Sessions start at the repo root; the folder name contains a space, so quote it.
Scripts resolve their own paths, so there is no need to `cd`.

```bash
# one level, direction inferred from where it sits vs spot
python3 "Gala Heatmap/src/level_confidence.py" --level 4049.44

# several levels, forced direction, and journal the calls
python3 "Gala Heatmap/src/level_confidence.py" --level 4049.44 --level 4103.00 \
        --direction short --journal

# compare entry models, or override the stop floor
python3 "Gala Heatmap/src/level_confidence.py" --level 4049.44 --entry level
python3 "Gala Heatmap/src/level_confidence.py" --level 4049.44 --stop-floor 7

# what could have been said at a past moment (no look-ahead)
python3 "Gala Heatmap/src/level_confidence.py" --level 4049.44 --as-of 2026-07-31T15:30:00Z
```

⚠️ **A run takes 2–4 minutes and the default Bash timeout is 2 minutes — it WILL
be killed mid-run.** Always pass an explicit timeout of at least **900000 ms**.
This is the single most likely fresh-session failure. Report progress rather
than going silent.

Full plumbing, failure modes and error meanings: `references/03-plumbing.md`.

**Always pass `--journal` on a live call.** The options/gamma block it snapshots
cannot be reconstructed afterwards from any free source, so an unjournalled call
permanently loses that evidence. See `references/02-journal.md`.

## Reading the output

The score is an itemised table, never a bare number. Present the breakdown, not
just the total — the user needs to see *which* layer drove it so they can
disagree with any single component.

| Score | Verdict | What to say |
|---|---|---|
| ≥70 | TAKE | Evidence supports it at normal size |
| 50–69 | CAUTION | Reduced size, or wait for a cleaner trigger |
| 30–49 | WEAK | Skip unless the price action is exceptional |
| <30 | SKIP | The evidence does not support this trade |

Full interpretation guide, including what each component means and how to talk
about it: `references/01-reading-the-score.md`.

### Two conditions that change what the output means

- **Market closed / stale data.** If the newest bar is >30 min old the report
  opens with a **MARKET LOOKS CLOSED** banner and the age in hours. Spot, day
  bias and session then describe the last session that traded. Surface this;
  never present a weekend run as a live read.
- **Non-gold instrument.** The futures, options, gamma and COT layers are
  **gold-only** and are skipped for anything else, with those components marked
  NOT APPLICABLE. The score then rests on price history alone and will be much
  lower. That is correct, not a broken run. (Before this gate existed, UK100
  produced a "GC basis" of −6768 and attached gold's gamma to a FTSE level —
  plausible numbers, entirely fictitious.)

### Things you must always surface

- **The DAY count, not the event count.** The history line reads
  "4 distinct days / 9 visits / 23 events". Quote the days first — events within
  a day share that day's regime, so 23 events across 4 days is four observations.
  Sample weight already keys off days; say the number anyway.
- **Which entry model produced the number.** Rejection (default) and level give
  materially different expectancies on identical data. Never present one as if it
  were the other.
- **The stop floor.** If the user says they stop "just beyond the wick", tell
  them the measurement: that rule returns −0.33R on this instrument and needs a
  5–7 point floor to turn positive.
- **Gamma availability.** Under `--as-of` the gamma and OI layers are
  UNAVAILABLE and the score is capped around 85. Never present a replayed score
  as if it were a live one.
- **The stop-sensitivity table.** If expectancy is positive across most stop
  widths, the edge is real and the exact stop is a detail. If it is positive at
  only one or two, say plainly that the edge is fragile.
- **That the weights are unvalidated.** The inputs are measured; the weights
  combining them are a judgement call that nothing has yet calibrated. The
  journal review is what will settle them.

## Reviewing

```bash
python3 src/journal_review.py --month 2026-08 --write
```

Walks price forward from each logged call and grades it: `TARGET`, `STOPPED`,
`OPEN_AT_HORIZON` or `NEVER_TRIGGERED`. Two separate clocks — a call stays live
for 300 minutes waiting for price to arrive, then the trade is managed for 60.

The tables answer the two questions that matter: does a higher score actually
win more, and does positive gamma actually produce more holds. **Until there are
30+ triggered calls per bucket, report these as plumbing, not findings.** Say so
explicitly rather than letting a 3-row table look like evidence.

## Supporting tools

| Need | Command |
|---|---|
| Whole-market gold context | `python3 src/gold_context.py --levels 4049.44` |
| A level's full touch history | `python3 src/level_stats.py --symbol XAUUSD --level 4049.44` |
| Auto-detect levels | `python3 src/level_stats.py --symbol XAUUSD --days 14` |
| Does my broker have DOM? | `python3 src/dom_recorder.py --probe` |
| Check the environment | `python3 src/preflight.py` |

## What this cannot do

Be direct about these when they come up rather than letting the score imply more
than it knows:

- It does **not** see live order flow. There is no free aggressor-classified
  trade data for gold. "More sellers than buyers at this level" is not something
  it can observe — it infers from committed size and past behaviour.
- cTrader bar volume is **tick volume**, not contracts. Tested across 615 touch
  events, it carries no signal separating holds from breaks.
- GLD options are a **proxy** for gold options. CME's own OG options would be
  better; CME blocks datacenter IPs so it may only work from the user's machine.
- The 60-minute management horizon is a modelling choice, not how the user
  actually trades. Treat R figures as comparative, not as a P&L forecast.

Detail on all of these: `Gala Heatmap/research/02-DATA-SOURCE-INVESTIGATION.md`
and `04-GOLD-DATA-SOURCES.md`.
