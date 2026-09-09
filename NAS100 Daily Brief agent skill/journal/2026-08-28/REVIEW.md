# REVIEW — 2026-08-28 (Fri)

**Verdict: NOT GRADED. There was no admissible forecast for this session.**

The day's only journal entry, `2233-overnight.json`, carries
`test_artefact: true` with the note *"Run to verify sync_archive.py self-commits
a scan. Not an independent observation."* `review_day.py 2026-08-28 --json`
returns `{"error": "no journal entries for 2026-08-28"}` and `track.py` shows the
evidence base still at **4 trading days / 10 scans (24–27 Aug)** — 08-28
contributes nothing to any statistic. That exclusion is correct and is not
disturbed here.

Everything in sections 2 and 3 below is a **diagnostic unmask**, run only so the
exclusion is not silently flattering. **None of it enters any tally, any
hypothesis count, or any threshold.**

---

## 1. Scoreboard

| | |
|---|---|
| Admissible scans | **0** (1 journal entry, 1 excluded as `test_artefact`) |
| Direction calls | 0 right / 0 wrong / 0 no-call |
| Level hit rate | n/a |
| Fuel accuracy | n/a |
| Evidence base after today | **4 trading days / 10 scans — unchanged** |

Actual session, context only, graded against nothing:

`O 29570.4  H 29748.3  L 29376.4  C 29454.8   range 371.9   net −115.6   275 bars`

High 15:00 UTC, low 17:05 UTC. A full, normal, liquid session — and the archive
holds no forecast covering it.

---

## 2. What the levels actually did  *(diagnostic only — not counted)*

Unmasked, the excluded scan published 13 levels, 9 touched (0.69). Two findings,
and both are about the **measuring instrument**, not about the levels.

**The call wall reading is wrong in both directions at once.**
`29645.0 CALL WALL ●●●●● 1.30bn + shelf 1.09bn + PDH` — the single heaviest
level on the board, the one the brief exists to say "rallies stall here" about.

- Graded reaction: **"broke DOWN through it"**, first touch 02:15 UTC,
  `travel_up −4.5`.
- `travel_up −4.5` means price **never actually reached it** on that touch — it
  came within 4.5 pts and the 8-pt `TOUCH_TOL` counted it anyway. So the level is
  scored as *touched* (it feeds the 0.69 hit rate) and as *broken* (downward), on
  a bar that neither touched nor broke it.
- Meanwhile the session went **straight through it later**: 14 bars traded above
  29645 between 14:35 and 15:40 UTC, to a high of **29748.3 — 103.3 pts above the
  wall**. First-touch grading is blind to all of it.

So on the day's most important level the output says "broke down through it"
when what actually happened was: near-miss overnight, then a 70-minute clean
break 103 pts *up*. Whatever the truth about that wall is, the review tool did
not report it.

**`29445.0 Options shelf 1.24bn`** is the mirror case: `up 303.3 / dn 0.9` —
price touched it and never traded 0.9 pts below, then ran 303 pts up. That is a
floor holding perfectly, and the label reads **"broke UP through it"**.

**`29490.2 PD mid`** graded *chopped* (`up 258.1 / dn 46.1`) — a fourth
consecutive session of PD mid chopping. Its cull case under H6 continues to
build, but this row does not count toward the 5-day threshold.

Never reached: `29360.8 NY Low`, `29338.2 PDL+Asia Low`, `29145.6 GAMMA FLIP`,
`29115.9 PWL` — the flip 231 pts below the low, consistent with H4's running
1 hit / 2 miss.

---

## 3. What was wrong, and why

**The real failure of 2026-08-28 is not a bad call. It is that no call was
archived for a live session, and then the archive gap widened.** 08-28 has one
test entry; 31 Aug, 1–4 Sep have **nothing at all** — confirmed against
`research/chart-ladders/`, which jumps 2026-08-27-2233 → 2026-09-08-1539. No
scan was lost; none was run. Five to six unobserved trading days is why H4 and
H6 (5 days) and H8 (10 days) are no closer than they were on 27 August, eleven
calendar days ago. That, not any parameter, is the binding constraint on this
project right now.

**Diagnostic trace of the excluded scan** (`bias +4 MILDLY BULLISH`,
`expected_direction +1`; price fell 118.4 from the scan, close −115.6 on the
day). Not a graded miss — but the component structure is worth reading:

- `gamma +2` *"above flip 29145.6 by 428.7pts — long-gamma, dips supported"* and
  `gamma +2` *"week net GEX 7.98 → pinning likely"* supplied the entire net score.
- `gamma −2` *"price sits in the top 20% of the wall band (28845–29645) — poor
  risk/reward for longs"* was the **only component describing what actually
  happened**, and it was outvoted 4:2 by the two positive gamma terms **within
  its own component**. Price was 70.7 pts under the call wall, ran 103 pts
  through it, then gave back 371.9.
- `breadth +2` came from *"mega-cap avg +3.83%, NVDA +8.74%"* — yesterday's
  post-earnings pop read as tomorrow's direction. One instance; logged, not a
  claim.
- `macro −3` (real yield) and `macro −1` (nominal) were right in sign.

The interesting shape is that gamma both drove the call and contained its own
refutation. **One observation. Not a proposal.**

---

## 4. Change proposals

**No calibration change is proposed. Zero admissible sessions were graded
today, so nothing about the model may move on this review.**

Two items are raised as **defects/methodology**, which the register's own
precedent (D1: *"not a calibration question and so not subject to the 3-day
rule"*) exempts from the 3-session gate. Both are about measurement, not scoring.
Neither touches `bias_engine.py` or `brief.py`.

**M3 — `latest_unreviewed()` picks a day it then refuses to grade, and calls the
refusal an error.** `review_day.py:204` filters on `is_trading_day` but *not* on
`test_artefact`, unlike the matching filters at `review_day.py:75` and
`track.py:82`. It therefore returns `2026-08-28`, and `review()` answers
`{"error": ...}` rather than the `{"status": "skipped"}` shape built for
non-gradeable days — a caller distinguishing skip from failure sees a failure.
Separately, nothing in the codebase reads `REVIEW.md` (`grep -rn "REVIEW.md"
--include=*.py` returns nothing), so "unreviewed" is a misnomer: the function
returns the most recent trading day, reviewed or not, forever. *Expected effect:
`python3 review_day.py` stops erroring on a clean skip and stops re-offering
already-reviewed days.* Decision is the trader's.

**M4 — the H6 statistic is being tallied off a label D5 already established is
unreliable.** D5 (27 Aug) recorded that `grade_level` scores the first touch
only, has no concept of role reversal, and that *"broke UP through it counts as a
failure"*. The fix was deliberately **additive** — `gex_retro.role_reversal()`
was added and `grade_level` left unchanged. But `review_day.py` still emits the
`grade_level` string, and H6's running evidence (*"traded both sides — chopped
remains the dominant outcome"*, hit rate 0.56–0.58) is tallied from it. Two
distinct sub-faults, both verifiable from single rows:

1. **Near-misses count as touches and as breaks.** `TOUCH_TOL = 8.0` admits bars
   whose high never reached the level, then the reaction string reports the
   direction of subsequent travel. Instances in the graded archive: 08-24 08:28
   `MAX PAIN 29099.3` (`dn −5.1`, "broke UP through it"), 08-24 08:30/32/33
   `PWL 29115.9` (`dn −0.9`), 08-27 13:23 `PDH 29353.8` (`dn −7.0`), plus 08-28
   `CALL WALL 29645.0` (`up −4.5`) unmasked above. **Two graded days plus one
   excluded day.** This matters directly: H6's cull case against MAX PAIN
   (*"touched on 3 of 4 scans and never stalled price once"*) is built partly on
   a 5.1-pt near-miss.
2. **First-touch blindness is still in the published output**, demonstrated
   above on the 08-28 call wall (near-miss overnight recorded; 103-pt break 12
   hours later invisible).

*Proposal:* before H6 reaches its 5-day threshold, decide whether it is tallied
from `role_reversal()` or from `grade_level`, and report `travel_up < 0` /
`travel_down < 0` as a near-miss rather than a touch-and-break. *Expected
effect:* H6's hit rate and its "chop is dominant" conclusion get re-derived from
an instrument that D5 already said was wrong. Doing this **after** the threshold
is hit would mean tuning the level board on a polluted statistic.

### Checked and found to be nothing — recorded so it is not re-proposed

- **`fuel` is not dead weight, it is non-voting by design.** 25 instances across
  the graded archive, **every one scores 0** (nonzero rate 0%). That looks like a
  cull candidate until you read D1: *"fuel reports and never votes."*
  `bias_engine.py:176,181` hard-codes `add("fuel", 0, ...)`. Same for `events`
  (14/14 zero, `bias_engine.py:239`). **No proposal.** The only observation worth
  keeping is presentational: both appear inside `bias_components` with a `points`
  field beside the components that do vote, which invites exactly the wrong
  inference — the 08-28 fuel row reads *"fuel_ratio 2.75 (burning hot)"* and
  contributes nothing.
- **Every other component is live**: gamma 64% nonzero, vol 63%, breadth 60%,
  macro 58%, structure 53%, rates 47%, news 26%. Nothing is near-zero enough to
  question.

### What I am watching, with no proposal attached

- **H1** — 4 days, per-day error `+61.2 → −11.6 → −73.0 → −86.4`, monotonic.
  Still a trend, not a level. Needs an unpinned/short-gamma day before any
  multiplier is fitted. No new point today.
- **H4** (flip as magnet) 1 hit / 2 miss, needs 5 days. 08-28's flip sat 231 pts
  below the session low; **not counted**.
- **H6** — see M4. Do not let it reach 5 days on the current instrument.
- **H10** (prior-week rule has no reclaim condition) — still 1 observation. Not
  testable on 08-28: the scan read `structure 0, price inside the prior-week
  range`.
- **New, unopened, 1 instance only:** does `breadth` read a large single-name
  earnings move (NVDA +8.74%) as forward direction? Needs 3 instances before it
  is even written up as a hypothesis. Logged here, not opened — a hypothesis is
  opened by writing it in the register, not by mentioning it.

### One question for the trader, which I must not decide

`test_artefact` is currently doing two different jobs. On 27 Aug it marked
**verification re-runs** — one market state journalled five times, where
exclusion is unarguably right because counting them inflates one observation into
five. On 28 Aug it marks a **plumbing test that happened to produce a unique,
uncontaminated, live forecast** at a market state sampled exactly once, on a real
trading day, whose `prediction` block was written before the outcome was known.
Excluding the first prevents inflation. Excluding the second **discards a real
observation** — and here it discarded a losing one, which is the flattering
direction, the same shape as D1/D3's lesson about guards that fail quietly.

I am not proposing that it be counted, and I have not counted it. But the flag
needs two names, and which of them 08-28 gets is the trader's call.
