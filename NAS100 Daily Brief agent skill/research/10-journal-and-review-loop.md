# 10 — Journal, review loop, and session awareness

Three additions that turn the brief from a one-shot report into something that
can be graded and improved.

---

## 1. The journal (`.claude/skills/nas100-daily-brief/scripts/journal.py`)

Every scan writes two files to `journal/<trading-day>/`:

| File | Contents |
|---|---|
| `HHMM-<session>.json` | The machine record — the graded artifact |
| `HHMM-<session>.md` | The brief exactly as delivered |

Plus `journal/index.json`, a flat index so the next scan can find the previous
one in one read (that's what powers "new trading day" vs "continuation").

### Why the JSON matters more than the markdown

It records the **prediction before the outcome is known**:

```json
"prediction": {
  "bias_score": -6, "bias_label": "BEARISH", "expected_direction": -1,
  "gamma_flip": 29331.8, "expiry_shape": "FRONT_FLAT_BACK_SHORT",
  "fuel_state": "MODERATE", "remaining_budget": 156.1,
  "levels": [ {"price": 29381.6, "name": "CALL WALL + MAX PAIN", ...}, ... ]
},
"inputs": { "bias_components": [ ...all 24 rows... ], ... },
"outcome": null
```

That is the only moment this data exists uncontaminated. You cannot reconstruct
"what did we say would happen at 29381.6" after the fact.

**Journal writes are best-effort and never raise** — a disk problem must not
break a brief.

**The journal is committed to git deliberately.** Cloud containers are wiped
between sessions; an ignored journal means Phase 4 has nothing to learn from.

**Synthetic entries are forbidden.** A backdated entry was created during
development to test the review loop, and deleted immediately afterwards. Any
fabricated record silently corrupts every statistic computed from the archive.

---

## 2. The review engine (`.claude/skills/nas100-daily-brief/scripts/review_day.py`)

Grades a past day's scans against real cTrader bars. Deliberately a **script,
not a prompt** — the arithmetic is deterministic and must not be re-derived by a
model each run.

Per scan it computes:
- **Direction call** — CORRECT / WRONG / no-call, measured from the scan time
  forward (a 13:00 scan is not graded on what happened at 09:00)
- **Every published level** — touched or not, and the reaction: *stalled at it*,
  *broke UP through*, *broke DOWN through*, *chopped around it*
- **Fuel accuracy** — realised range vs the budget we published

### First real run, 2026-08-20

```
REVIEW 2026-08-20  O 29487.1 H 29600.9 L 29115.9 C 29219.2  range 485.0  net -267.9
  direction: 1 right / 0 wrong    levels touched: 0.75
  13:15 PRE_NY  BEARISH (-6) -> moved -32.1  [CORRECT]
     fuel: budget 156.1 vs realised 266.6 -> UNDER-estimated
       29381.6  CALL WALL + MAX PAIN        broke DOWN through it
       29200.6  Asia Low (prev-day)         broke UP through it
```

It immediately surfaced the concern I had already flagged by eye: **the range
budget is too conservative** (156 published, 266 realised). One day is not
evidence — but this is exactly the measurement that turns a hunch into a
justified change after ~3 sessions.

---

## 3. The background reviewer (`agents/brief-reviewer.md`)

A sub-agent, run **after** the brief is delivered, never before or during.

Orchestration for Phase 2's SKILL.md:

1. Run `brief.py`, output the brief. **Done — the user is unblocked.**
2. *Then* spawn `brief-reviewer` in the background on the last completed day.
3. Its findings arrive as a notification and are written to
   `journal/<day>/REVIEW.md`. They never appear inside the brief.

Its remit, in order: score the day, judge whether levels behaved as described,
trace bad calls to the component that caused them, and propose **only material
changes with evidence from 3+ sessions**. Tuning on one day's noise is how a
model gets worse, so that threshold is a hard rule, not a guideline.

It may not edit scoring logic, and may not touch a `prediction` block —
predictions are immutable once written.

---

## 4. Session awareness (`.claude/skills/nas100-daily-brief/scripts/session_context.py`)

Stops the brief being confusing about *when* it is:

- **Weekend / holiday detection.** On a Sunday the brief now leads with
  *"Sunday — weekend. This is a PREP scan, not a live one: the numbers below are
  last session's close. Next session Monday 24 Aug."* rather than silently
  reporting Friday's range as "today's".
- **Session window**, resolved in Eastern time so it tracks DST: `OVERNIGHT`,
  `ASIA`, `LONDON`, `PRE_NY`, `NY_OPEN`, `NY_MIDDAY`, `NY_PM`, `NY_CLOSE`,
  `POST_CLOSE`, each with what it means for trading.
- **Relationship to the last scan**, which is the part that removes real
  confusion:
  - *"**New trading day.** Last scan was 20.2h ago (Tue 25 Aug 13:00 ET) and
    covered Tuesday 25 Aug; everything below is fresh."*
  - *"Continuation — last scan 3.8h ago at 09:15 ET today. Read the CHANGES,
    not the whole brief."*
  - And the awkward case, handled explicitly: *"Same session day (the futures
    day rolled at 17:00 ET on Tue), but it is now Wednesday and the last scan
    was 15.8h ago."* Technically the same session day; it would read as nonsense
    without the second clause.

US market holidays are a hardcoded list (`US_HOLIDAYS`) rather than computed —
a wrong entry silently turns a closed day into a trading day, so it is explicit
and needs extending each year.
