# Wiring the GEXBot archive into the review flow

**Status: PROPOSAL. Nothing here is built.** Written 2026-09-05 after the first
real Firestore read (`EVALUATION.md` §11).

Goal: let `gex_retro.py` grade GEXBot's volume-weighted and open-interest-weighted
levels on days no scan was run, so H12 accumulates on the calendar rather than
on the days the desk happened to be staffed.

---

## 1. What H12 can be tested against today

**Nothing. The count is still 0 sessions.**

This is the finding, and it is worth being blunt about because the Firestore
read *feels* like progress and is not, for H12's purposes:

- The archive holds **one poll**, of a **frozen weekend feed**, captured by a
  manual run on a Saturday.
- Its four documents are **two** underlyings — `NQ_NDX` and `ES_SPX` are fixed
  basis offsets of `NDX` and `SPX`, verified exact to the cent.
- That instant is **the same frozen Friday close** already written into
  H12 and H13 as "1 frozen snapshot".

So the read did not add a sample. It confirmed the pipe works and re-served a
data point the register already had. **H12 stays at 0/5, H13 at 1/5.**

What genuinely changed is the *rate* at which they can now be settled. Once
scheduled runs start (Monday 2026-09-07 13:00Z), the archive accrues without
anyone running a scan — which is precisely the constraint the tick-stream
evaluation identified as binding.

### What the archive will be able to test — and what it will not

The distinction is structural and permanent, not a matter of implementation:

| H12 sub-question | Answerable retro? | Why |
|---|---|---|
| Does the **volume wall** hold better than the **OI wall**? | **Yes** | `major_pos_vol` / `major_neg_vol` / `major_pos_oi` / `major_neg_oi` are in every compact record |
| Does `zero_gamma` behave as a flip? (H13) | **Yes** | `zero_gamma` + `spot` in every record |
| Do the two lenses **disagree**, and when? | **Yes** | `regimes_agree` / `walls_agree` precomputed |
| Does the ranked **C1–C3 / P1–P3 ladder** hold? | **No — ever** | the 142-strike ladder is written only to `gex_latest`, which is overwritten each poll. Per-strike history is never retained |

The first row is H12's headline claim, so **the archive is sufficient for the
hypothesis as written**. The last row is not a gap to close later; it is a
deliberate size trade in the recorder (~1 GB/month otherwise). A retro
*ladder* grade would need a second, much larger collection, and that should not
be built to answer a question the compact record already answers.

**Naming consequence.** `gex_retro.py --ladder` grades a *ranked ladder file*.
What the archive supports is a **wall grade**. Calling the new path `--ladder`
would promise the C1–C3 comparison it cannot deliver. Propose `--from-archive`,
emitting documents whose `ranked_positive` / `ranked_negative` carry a **single
entry each** (the wall), explicitly flagged.

---

## 2. The design

Three pieces. Only the first is new code of any size.

### 2.1 `gexbot_archive.py` — a read-only Firestore reader

New file, `.claude/skills/nas100-daily-brief/scripts/gexbot_archive.py`.
Mirrors `gexbot.py`'s shape (`available()`, `last_error()`) so the brief's
existing source-health reporting picks it up unchanged.

```python
def available() -> bool
    # FIREBASE_SERVICE_ACCOUNT_JSON present AND google-cloud-firestore imports

def snapshots(day, ticker="NDX", scope="zero") -> list[dict]
    # every gex_snapshots doc for one UTC day, sorted by source_ts.
    # Doc ids are {TICKER}_{scope}_{source_ts}, so this is a key range scan:
    #   start_at(f"{ticker.upper()}_{scope}_{day_start_ts}")
    #   end_at  (f"{ticker.upper()}_{scope}_{day_end_ts}")
    # -- no index needed, and it reads only the day asked for.

def distinct_source_ts(day, ticker="NDX") -> list[int]
    # the cadence measurement, as its own callable
```

**The key-range scan is verified, not assumed.** Run against the live archive
on 2026-09-05: `order_by("__name__")` with `start_at` / `end_at` on synthetic
doc ids returned the Friday document for `2026-09-04` and an empty result for
`2026-09-05`, with no composite index and no full-collection read. It relies on
`source_ts` being fixed-width so lexicographic order matches numeric order —
unix seconds stay 10 digits until 2286, so that holds.

Read-only by construction: no `set`, `update` or `delete` anywhere in the
module. The Admin SDK *can* write — §9 is explicit that this is the cost of
option B — so the constraint has to live in the code, and be visible.

### 2.2 `to_ladder_doc()` — reuse the existing schema

The critical reuse: `gexbot.persist_ladder()` **already** emits the chart-ladder
schema, so `gex_retro.py --ladder` grades GEXBot output with the same
`review_day.grade_level` + `role_reversal` rule that grades ours. That property
is the whole reason two graders never appear, and it must not be forked.

So the archive path does not invent a format — it fills the *same* dict:

```python
def to_ladder_doc(snap, weight, offset):
    return {
        "schema": 1, "source": "gexbot_archive", "weight": weight,
        "book": "gexbot_" + weight,
        "generated_utc": iso(snap["source_ts"]),   # feed time, NOT read time
        "spot": snap["spot"] + offset,
        "flip": snap["zero_gamma"] + offset,
        "flip_equals_spot": snap["zero_gamma"] == snap["spot"],
        "call_resistance": snap[f"major_pos_{weight}"] + offset,
        "put_support":     snap[f"major_neg_{weight}"] + offset,
        "ranked_positive": [{"rank": "C1", "price": ..., "net_$bn": None, "oi": 0}],
        "ranked_negative": [{"rank": "P1", "price": ..., "net_$bn": None, "oi": 0}],
        "ladder": [],                # never available retro -- say so, don't fake it
        "walls_only": True,          # gex_retro must refuse to rank-compare these
        "regimes_agree": snap["regimes_agree"],
        "walls_agree":   snap["walls_agree"],
    }
```

`net_$bn: None` rather than a fabricated magnitude. `sum_gex_vol` is a
whole-book total, not a per-strike force, and quietly substituting it would
produce exactly the class of confident-and-wrong number the register keeps
recording.

**`generated_utc` must be the feed's `source_ts`, not `fetched_at`.**
`build_from_ladder()` clips bars to those after `generated_utc` to prevent
look-ahead. Using the read time would grade the level against the hour before
it existed — the same look-ahead bug that section already documents surviving
by luck once.

### 2.3 The offset problem — and why it is solvable without new storage

The archive stores **NDX index** levels. `gex_retro.py` grades against
**NAS100 CFD** bars. The live path gets the basis handed to it (`persist_ladder`
takes `offset` and `cfd_price` from the running scan). A retro day has no scan,
so no offset was recorded.

It does not need to have been. Each snapshot carries **both** `spot` and
`source_ts`, so the basis is recoverable per timestamp:

```
offset = cfd_close_of_M5_bar_covering(source_ts) - snap["spot"]
```

`review_day.fetch_day_bars(day)` already returns exactly those M_5 CFD bars.
So the offset is derived from data both sides already have, per snapshot rather
than per day — which is better than storing it, since the index/CFD basis
drifts intraday (it moved 30.82 on the archived Friday close).

Guard it: if no bar covers `source_ts` within one bar-width, **skip that
snapshot** rather than carrying a stale basis forward. A wrong offset shifts
every level uniformly and would look like a plausible result.

### 2.4 The call site

`gex_retro.py` grows one flag, alongside the existing `--ladder`:

```
python3 gex_retro.py --from-archive 2026-09-08 --weight vol
python3 gex_retro.py --from-archive 2026-09-08 --weight oi
```

Both run for every archived day; `review_day.py` calls them as a pair so the
two lenses are always graded on identical bars with an identical rule. Grading
one lens without the other is how a comparison silently becomes an endorsement.

Which snapshot of the day to grade: propose the **first snapshot at or after
13:30Z** (the cash open), so every day is graded from the same point in the
session and the sample is not skewed by whichever poll happened to land. Record
the chosen `source_ts` in the output.

---

## 3. Guardrails

Restating the standing constraints, because this is the seam where they would
erode:

1. **Additive only.** Nothing here feeds the call, the level board or the fuel
   model. The output goes to the H12/H13 evidence trail and nowhere else.
2. **5 sessions minimum** before H12 or H13 moves off OBSERVING. The archive
   raises resolution to 5-minute; it does **not** shorten the threshold. Twelve
   correlated polls of one day are one session, not twelve.
3. **One grader.** The archive path reuses `grade_level` + `role_reversal`
   unmodified. If a wall grade needs different treatment, change it for both
   lenses and ours, or not at all.
4. **Read-only.** No write call in `gexbot_archive.py`, ever.
5. **Do not fabricate the ladder.** `walls_only: True` travels with every
   archive-derived document, and `gex_retro` refuses a rank comparison on one.

## 4. Sequencing

Nothing should be built against the current archive — one frozen row cannot
exercise a day-range scan, a cadence measurement, or an offset reconstruction,
and code written against it would be tested only by its own assumptions.

1. **Mon 2026-09-07, after 21:00Z** — first RTH session lands. *Then*:
   measure distinct `source_ts` per ticker (settles the cadence question and
   `recorder.md`'s open limitation), confirm the `ladder` key now appears in
   `gex_latest`, and confirm the `priors` ordering by the two-poll check
   `recorder.md` §"The strike ladder" specifies.
2. **After that** — build `gexbot_archive.py` against a day of real rows.
3. **Then** — `--from-archive`, graded both ways, on that same day.
4. **Then** — five sessions. Not before.

The credential should be regenerated before any of this becomes routine — see
`EVALUATION.md` §11 and the note in the session that produced it.
