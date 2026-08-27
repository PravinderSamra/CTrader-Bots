# REVIEW — trading day 2026-08-26

Graded 2026-08-27 13:25 UTC, after the 21:00 roll. This supersedes the manual
review taken at 20:42 UTC on 26 Aug, which was 18 minutes short of the close.

---

## 1. Scoreboard

Trading day = 2026-08-25 22:00 UTC → 2026-08-26 20:55 UTC (276 M_5 bars, complete).

| | |
|---|---|
| Open / High / Low / Close | 29231.9 / 29353.8 / 29028.1 / 29353.7 |
| Range | 325.7 |
| Net | +121.8 |
| Direction calls | **2 right / 2 wrong / 0 no-call** |
| Level hit rate (mean of 4 scans) | **0.71** (13/17, 13/17, 11/18, 12/17) |
| Fuel calls | 4 × "about right" |
| Fuel error, sound scans | **−73.0** (13:12: budget 186.2 vs ext 113.2; 22:11: budget 377.0 vs ext 304.0) |
| Fuel quarantined | 21:43 scan (`SESSION_PENDING`) — direction call kept, fuel dropped |

### Where last night's figures were stale

The session high was set in the **final bar (20:55)**. The last 18 minutes moved
every number:

| | 20:42 cutoff (last night) | final (21:00 roll) |
|---|---|---|
| High | 29314.1 | **29353.8** |
| Close | 29271.1 | **29353.7** |
| Range | 286.0 | **325.7** |
| Net | +39.2 | **+121.8** |
| Fuel error (both sound scans) | −112.7 | **−73.0** |

**Correction to the premise.** The ~29,493 print at 22:12 UTC is **not** part of
this day. The trading day ends at 21:00 UTC, so the NVDA post-earnings gap
belongs to trading day **2026-08-27** (which opens 29450.7 at 22:00 and has since
run to 29595.9). Only the 20:42→21:00 window is new here. Direction tally is
unchanged at 2/2; the fuel error is the figure that moved.

---

## 2. What the levels actually did

**Called correctly, and the best call of the day.** `29343.0 CALL WALL ●●●●●
1.03bn` — the brief said *"Heaviest ceiling this week… rallies stall. Take
profit into it."* Session high **29353.8**, 10.8 pts through it, graded
*stalled at it*. The heaviest call strike named the high of the day to within
11 points.

**Called correctly by omission.** `29293.0 STRUCTURAL CALL WALL 1.66bn` — the
brief said *"the ceiling for the WEEK/MONTH, not today… not an intraday
trigger."* Price broke down through it (up 6.8 / down 80.5) and later closed
above it. Correctly de-emphasised.

**Wrong.** `29093.0 PUT WALL ●●●○○ 0.69bn` — the brief said *"Heaviest floor this
week — expect a bounce and a good long-sweep here."* Price went **64.9 pts
through it** to 29028.1 and graded *traded both sides* (up 44.2 / down 60.4). A
long taken at the wall on that instruction is stopped before the bounce arrives.
The bounce did eventually come — the day closed 325 pts off the low — but
"floor" overstates what a 0.69bn put wall did, and the 60.4 pts of adverse
travel is the number that matters to a trader sizing off it.

**No reaction at all.** MAX PAIN was touched on 3 of 4 scans and never once
stalled price (chopped, chopped, broke down through). PD mid 29144.0 chopped on
all 4. Both are candidates for the H6 cull — but H6 needs 5 days and has 3, so
this is logged, not proposed.

**Not gradeable.** The `2211-overnight.md` secondary-walls table ("28993.0 … a
genuine floor while we stay in long gamma") was written at 22:11 on 25 Aug,
**before** the D2 fix landed on 26 Aug. It is a pre-fix artefact and must not be
counted as a forecast. The 27 Aug brief carries the corrected regime-aware
wording — D2 has **not** regressed.

---

## 3. What was wrong, and why

Both PRE_NY scans read **−4 MILDLY BEARISH** at ~13:12; price then ran **+249.8**
into the close. Tracing to `inputs.bias_components`, the bearish weight came
almost entirely from two −3s:

**(a) `structure −3` — "price is BELOW the entire prior-week range (29115.9–30245.8);
PWL 29115.9 is now resistance, not support".**
The market disagreed inside the same hour. `29118.1 London Low (today) + PWL`
graded *traded both sides* with **145.8 up vs 29.4 down**, and `29086.1 NY Low
(prev-day)` graded ***broke UP through it*** with **177.8 up vs 0.5 down** — price
touched it and never traded 0.5 pts lower. The prior-week low was reclaimed and
held. The rule scores a **state** ("below the prior-week range") with **no reclaim
condition**: once price is back above the PWL the −3 should decay or invert, and
it does neither. This is one session of evidence. Logged under H-new, not proposed.

**(b) `gamma −3` — "below flip 29207.2 by 134.2pts — SHORT gamma, dealers amplify".**
Twelve hours earlier the same engine published flip **29098.5** and scored
`gamma +2` ("above flip, long-gamma, dips supported"). The flip drifted
**+108.7 pts**; the component swung **5 points**, which is larger than the entire
net score of −4. The flip is simultaneously the largest single swing factor in
the score and the least stable input in the model. This is H7.

**New H7 data point, and a sharp one.** Between the 21:43Z and 22:11Z scans on
25 Aug — **28 minutes apart** — the flip moved **28931.1 → 29098.5 (+167.4 pts)**
while spot moved only **~12.7 pts** (29213.5 → 29226.2). Flip drift was **13×**
price movement. This is the second large short-interval drift on record after
the 192 pt / 2 min anomaly on 24 Aug; the other five short-interval pairs drift
0.4–23.5 pts.

**Not a fault, but worth naming.** `events +0` carried the text *"NVDA earnings
— INDEX-DEFINING event; day before pins, day after expands."* It identified the
event and the mechanism correctly and then contributed **zero**. The day did pin
(range 325.7 = 82% of ADR 398.7) until the last 18 minutes, and the next day
expanded exactly as described. One session — no weight proposal.

---

## 4. Change proposals

**None.** No hypothesis that has reached its threshold supports a change.

`track.py` prints `actionable: YES` on the day count (3), but that is a
**global** gate. Checked per hypothesis:

| | threshold | have | reached? |
|---|---|---|---|
| H1 | 3 days | 3 | **yes** |
| H2 | 3 instances at LOW_FUEL/EXHAUSTED-at-extreme | 2 | no |
| H3 | 3 instances | 1 | no |
| H4 | 5 days | 3 | no |
| H5 | 3 days | 3 days but **n=1 late scan** | not usefully |
| H6 | 5 days | 3 | no |
| H7 | 3 overnight→pre-NY pairs | 2 | no |
| H8 | 10 sessions | 1 | no |

**H1 — reached, and it says do nothing.** Per-day mean error: **+61.2 → −11.6 →
−73.0**. The sign reverses and the magnitude is still moving. There is no stable
bias to correct; a multiplier fitted to these three days would be fitted to a
trend, not a level. The post-roll number *softens* last night's picture — −112.7
became −73.0, a 35% reduction — but does not restore the reversal to a settle.
**Keep observing.**

**H5 — day count reached, evidence not.** The late-session bucket still contains
exactly **one** scan (24 Aug 13:45, err +5.3). A time-of-day correction cannot be
fitted to one late observation. Reported as insufficient despite the day count.

**H8 — first outcome recorded.** Band 29,064 .. 29,388 (EM ±162 from the 25 Aug
ATM straddle at 191 pts). Close **29353.7 → inside**. Intraday low **29028.1 →
36 pts below the lower bound**; high stayed inside. Close-inside / low-breached.
1 of 10.

**H4 — data point.** Close 29353.7 vs published flips 29207.2 / 29230.7 / 29098.5
→ **123–255 pts away**. Miss. Running 1 hit / 2 miss across 3 days. Do not use
the flip as a target.

### Two methodology items for the user to rule on (not calibration, so not 3-day gated)

**M1 — `track.py`'s H1 mean pools scans, not days, and 24 Aug is counted 4×.**
Three of its rows (08:28, 09:37, 12:40) carry the **identical** budget 88.7
against the **identical** extension 168.5 — one budget reading graded three
times, hours apart, because the range genuinely did not move all London
(verified against bars: live range was 362.4 at all three timestamps, so this is
real market behaviour, **not** a stale-fuel defect). They are still not three
independent observations of forecast accuracy. Pooled by scan the mean is
**+12.4**; weighted one-vote-per-day it is **−7.8**. The 15-minute dedupe window
does not catch this. Which weighting H1 should use is a decision, not a tuning.

**M2 — the unfinished-day exclusion is silent.** `track.py` records
`_excluded: "session not finished"` in `per_day` but never prints it; only the
fuel quarantine gets a visible EXCLUDED block. 2026-08-27 was correctly held
out of today's table and the reader is told nothing. This is the exact shape D3
warned about — a guard that fails quietly and in the flattering direction.

### Verification requested by the task

- **Day-completeness gate:** working. 2026-08-26 grades (276 bars, wall clock
  past 21:00 on its own date); 2026-08-27 is correctly excluded. Evidence table
  shows **3 trading days, 9 scans**. ✅ (see M2 on the silent exclusion)
- **Field-level rollover quarantine:** working, and correctly *discriminating*.
  The 21:43Z scan (`SESSION_PENDING`, 0.0% ADR used, budget = full ADR 408.7) has
  its fuel dropped and its **+13 direction call counted (CORRECT)**. The 22:11Z
  scan, 71 minutes after the same roll, reports `ROOM_TO_EXPAND` with 5.4% used
  — a genuine live read of the new session — and is **not** quarantined. The
  quarantine is targeting the corruption, not the clock. ✅
- **Journal integrity:** no fabricated or backfilled entries. File mtimes on the
  2026-08-26 directory all read 22:05 because of a git checkout; the `scan_utc`
  fields inside are internally consistent and correctly bucketed
  (21:43Z/22:11Z on 25 Aug → trading day 26 Aug). ✅
- **H9:** referenced in the task but **does not exist** in HYPOTHESES.md, which
  runs H1–H8. Either it was never written or it was lost. Flagging, not creating.
