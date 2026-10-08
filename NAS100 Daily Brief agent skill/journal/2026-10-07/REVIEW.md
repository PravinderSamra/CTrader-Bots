# REVIEW — 2026-10-07

Graded from `review_day.py 2026-10-07 --json` and `track.py` (26 trading days /
32 deduped scans; **09-24 excluded by hand from every statistic**, as directed —
there is still no schema `quarantine` field). One scan on the day:
**12:50:43Z PRE_NY**, `is_trading_day: true`, 0 test artefacts.

## 1. Scoreboard

| | |
|---|---|
| Session (21:00Z roll) | O **31280.1** / H **31293.0** / L **30918.0** / C **31172.6** · 276 bars |
| Range / net | **375.0** (0.79x ADR14 472.8) · net **−107.5** |
| Scan | 12:50:43Z PRE_NY, price **31031.7**, **STRONGLY BEARISH −10**, dir **−1**, `COHERENT_SHORT` high conf |
| Direction | **0 right / 1 wrong** on the post-scan convention (post-scan move **+137.8**) — **right** on the day-net convention (**−107.5**). The convention decides the verdict. See §3. |
| Levels | **15 published / 7 touched = 0.47**; 7 touches land on **5 distinct M5 bars** → inflation **1.40x**; rows above scan **4/11 (0.36)**, rows below **3/4 (0.75)** |
| Fuel | budget **158.9** · extension **61.1** · error **−97.8** (0.38x of budget) · traversal **269.5** = 1.70x budget |
| Fuel ledger (H1) | per-day mean **+7.6** (n=25 ex-09-24); **−15.8** ex-09-21 (n=24); **MAE 93.3** vs mean per-day budget **118.9** — the typical error is **78% of the typical budget**. Third consecutive negative day (−66.5 / −180.1 / −97.8). |
| Vol boundaries | VXN-implied range **413.4** vs realised **375.0** → over by **38.4** (0.91x). Straddle EM band **30793 .. 31270**, close **31172.6 — INSIDE** (H8: 4 inside / 1 outside, obs 5 of 10) |
| All-time | direction **15 right / 9 wrong / 7 no-call** (ex-09-24), mean level hit rate **0.52** |

## 2. What the levels actually did

The headline question — structure or regime — has a time-dependent answer, and
the brief got the first 15 minutes right and the next seven hours wrong.

**PUT WALL 31025.8 (−6, ●●●●● 1.15bn, also the 45-day put wall).** The brief:
*"if it breaks, expect it to speed UP, not bounce. Don't buy the break."*
Sequence: first post-scan touch 12:55Z; the 13:30Z bar (NY cash open) swept to
30988.0 and closed **back above** at 31028.0 — first break failed; the **13:35Z
bar ran 31027.8 → 30922.4, −105.4 in a single M5 bar**; low **30918.0 at
13:45Z**, **107.8 below the wall**. So the acceleration mechanism was real and it
was fast. It was also **the whole move**: price never traded lower, was back at
31025.8 by 14:55Z, and closed **+146.8 above the wall**. *The level the brief
told you not to buy was the day's floor.* Structure won on any horizon longer
than an hour.

`review_day` reports this row as *"stalled at it — held as support for 355min,
worst −7.3pts"*. Measured first touch → close the worst excursion is **−107.8**,
a **14.8x** understatement and the worst ratio in the M6 record (previous worst
7.61x, 10-06). Read cold, the grader says the put wall held comfortably on a day
it was sliced by 0.23x ADR.

**GAMMA FLIP 31114.3 (+83).** *"We're BELOW it: they're pushing, so don't fade.
Reclaim and hold above and fading becomes valid again."* Price reclaimed it at
15:35–15:40Z and held above for the last 240+ minutes, closing **+58.3 above**.
The brief's own invalidation trigger fired five hours into the session and
nothing re-evaluates the −10 or STRATEGY 2 when it does. As a level it was the
cleanest row on the board (H4: reached, became the settlement side, closed above).

**31037.1 PWH (+5)** and **31078.9 PDL (+47)** both held as support into the
close, both after being lost by far more than reported (true −119.1 and −43.8 vs
reported −18.6 and −11.8). PDL carried *"the biggest pile of stops **below**
us… sweep it, then CISD = long"* while sitting **47 above** price, with the
sweep already completed pre-scan (5 pre-scan touches, 23 pre-scan bars entirely
below it). That is the exact mirror of 10-06's PDH row — **P-G instance #15**.

**30979.1 London Low (−53) and 30973.1 Equal lows ×2 (−59)** are **6.0pts
apart**, inside `TOUCH_TOL = 8.0`, and were graded as two levels off the **same
M5 bar (187)** with opposite verdicts (*held as support* / *lost by 25.6*). One
of the two is noise. 31232.0 / 31225.8 (6.2pts) is the second such pair on this
board; it did not fire because neither was reached.

**Never reached, and the judgement on each:**
- **CALL WALL 31225.8 (+194)** — post-scan high 31187.5, missed by 38.3. Not a
  P-E instance (per the standing instruction: the level was never touched
  post-scan, so there is no penetration and no close-side read). Worth recording
  anyway: price spent **94 of the 179 pre-scan bars entirely ABOVE** this
  "heaviest ceiling this week", with 36 pre-scan touches. The ceiling prose was
  written about a level the same session had already lived above all night.
- **MAX PAIN 30825.8 (−206 = 0.44x ADR14)** — missed by **92.2**. This is the
  **first within-reach test since 09-16** under the tightened threshold
  (≤0.5 ADR); *"price drifts toward it as the week goes on"* failed on a
  Wednesday. Within-reach tests now **2 of 3** (09-16 against, 10-07 against,
  09-28 ambiguous); the seven distance-confounded misses stay excluded.
- **STRUCTURAL CALL WALL 31475.8 (+444 = 0.94x ADR14)** — untouched. Census:
  **0 touches on 11 publications across 10 trading days, and it has never once
  been within 200pts of price.** P3/H6's recommendation to stop publishing it is
  unchanged and now has an eleventh consecutive null.

**The profitable trade was the one the document discouraged.** STRATEGY 2 said
*"Strategy-1 fades have a materially lower hit rate here — only take them at the
far walls"*; the trade that worked was an S1 fade at the strongest put wall on
the board. The right answer was in the subordinate clause.

## 3. What was wrong, and why

`−10 = rates −5 · macro −5 · gamma −3 · breadth +3 · vol +1 · structure −1`
(fuel 0, news 0).

**(a) −7 of the −10 is one fact counted three times.** `rates −3` "US10y 5.337
(+1.29%) — yields up" (live); `macro −3` DFII10 +3bp (observation **2026-10-05**,
two business days stale); `macro −1` DGS10 +3bp (**2026-10-02 → 2026-10-05**, the
same window, the same instrument). Censused across all 22 graded pre-NY scans:
**whenever DFII10 scores non-zero, DGS10 scores the same sign — 20 of 20** — so
the macro block contains a hard **±4 from a single FRED observation**, and the
live `rates` row agrees with it only **7 times in the 16 days both are non-zero**
(9 disagreements). These are not three measurements of a trend; they are one
stale series at weight 4 plus a live series that disagrees with it more often
than not.
*Effect on this day:* the 09-30 proposal (suppress DGS10 when a live US10y read
exists) takes the score to **−9 = BEARISH**, i.e. **the first instance in the
record where that fix removes the published STRONGLY label**. Zeroing DFII10 too
gives **−6 = BEARISH**. Direction is unchanged in every variant, so the fix stays
call-neutral — but the conviction the user was asked to act on was manufactured
by duplication.

**(b) Standing note 4, answered: they agreed, so the age gate was not the
problem.** Stale DFII10/DGS10 read *yields up, bearish*; live US10y also read
*yields up, bearish*. **H18/P1 instance 14**, and the first in the series where
stale and live point the same way at full weight. An age gate would have changed
nothing here; de-duplication would have changed the label. **HY OAS again
renders no observation date (5th consecutive session)** — the accuracy case stays
retracted and blocked, as directed.

**(c) The only new yield information was the one input not counted.** The
judgement list carried *"10-year Treasury note yield hits highest level since
2002 as traders brace for key bond sale"* — unscored, one of **26 relevant
headlines with 0 auto-scored, coverage 0.0%** (H19: second 0.0% in the record,
after 10-02). A three-day-old 3bp move was scored twice; today's headline move
was scored zero.

**(d) The one row that read the location correctly was outvoted inside its own
component.** `gamma +2` *"price sits in the bottom 20% of the wall band
(31025.8–31225.8) — poor risk/reward for shorts"* — price was **2.9% up a 200pt
band, 5.9 above the put wall**. Net gamma was **−3** because `gamma −3` (below
flip) and `gamma −2` (week GEX) outvoted it 5-to-2. The location row was right.
Separately, `fuel` scored **0** by design with **66.4% of ADR already burned and
fuel_ratio 1.48**, and `structure` scored **0** for *"inside the prior-week
range"* while price sat **5.4 below the prior-week HIGH**. Three rows that each
knew the call was being made at an exhausted extreme, and none of them could vote.

**(e) The grading convention, not the market, decides this verdict — and that is
now a third instance.** Post-scan **+137.8** vs day-net **−107.5**. Previous
instances 10-01 (−74.7 vs +64.3) and 10-02 (−75.2 vs +288.4) were both scored
`bias +2` / `+1` = *no call*, so the split never touched a graded outcome.
**Today it flips a −10 from WRONG to CORRECT.** Reported here explicitly rather
than folded into the scoreboard, as directed. This also blocks H3: 10-07 is the
**4th max-conviction bearish call printed at a session low** (price 17.0% up the
pre-scan range, 52.6 above the pre-scan low) and the 4th to be wrong **on the
post-scan convention only**.

**(f) It was not the FOMC minutes, and H20 gets a counter-instance.**
`event_gate: None` with a High-impact print 5.2h out looks like the obvious
culprit and is not: the low was set **13:45Z**, the flip was reclaimed
**15:35Z**, and when the minutes landed at **18:00Z** price was already +196 off
the low and ranged **31114.2–31165.6 — 51pts**. H20 asks whether High-impact
event days blow the fuel budget; the two prior instances were **+136.4** and
**+114.6**, today is **−97.8**. **n=3, threshold met, and the sign is not
consistent** — the candidate event-day budget multiplier should be dropped, not
fitted.

**(g) breadth +3 was the only component that called the day** (mega-caps 4/4 up,
avg +1.20%, AVGO +3.67%; NDX +0.48% vs ES −0.39%) and it is the smallest
positive on the board.

## 4. Change proposals

`track.py` reports **actionable: YES** (26 days ≥ 3) — which is a day-count gate
only, as the code itself says. Each item below is gated on its own evidence.

### P-H (NEW, PROPOSED) — fix the direction-grading convention and print both numbers
**Evidence, n=3, threshold met:** 10-01 (−74.7 / +64.3), 10-02 (−75.2 / +288.4),
10-07 (+137.8 / −107.5). The first two were *no call* so the split was free;
10-07 decides the verdict on a −10.
**Change:** state the convention in `review_day`'s output and emit **both**
`post_scan_move` and `day_net_move` with an explicit `direction_call_basis`
field. Recommended basis: **post-scan**, because the brief is published at the
scan and can only be traded forward.
**Expected effect:** no model change whatsoever. It changes what the scoreboard
means, and it unblocks **H3**, **D21** and **H10**, all three of whose verdicts
the register already notes flip with the convention. Until it is decided, H3's
bearish-branch cap (now 4-for-4 under one convention, 0-for-4 under the other)
**must not be proposed**, and it is not proposed here.

### D26 (NEW, OPENED and PROPOSED) — `track.py` files an aged-out day as "not finished"
**Evidence, one clean and fully-traceable instance.** `track.py` prints
*"HELD BACK — day not finished (grades after 21:00 UTC on its own date):
2026-08-24 99 bars so far"* — 45 days after that day finished.
`review_day.fetch_day_bars` caps `days=min(days_back, 45)`, so 08-24 is now
served only partially; `_day_complete` requires `bars >= 240`, returns False, and
the day is filed as unfinished rather than as aged out.
**Measured damage today:** H1's per-scan n fell **33 → 30** while one scan was
*added* — the four 08-24 rows silently left the sample — and the per-day mean
moved **+14.0 → +7.9**. Every figure quoted off the tracker is again a number
that moves with the calendar.
**This is D16's exact failure mode at the new boundary, and D16's own fix note
pre-registered it:** *"beyond that the honest fix is to persist graded outcomes
rather than re-derive them from bars that will not exist forever."*
**Change:** (a) label the bucket *"aged out of the bar window"* when
`day < today − 45d` so it can never be read as pending; (b) persist graded
per-day outcomes to disk. **Expected effect:** the evidence base stops shrinking
and the register's quoted statistics become stable. Defect, not calibration, so
not 3-session gated.

### Re-examine the standing dead-weight proposal before dropping NFCI
**Evidence:** `macro NFCI` scored **−1** today — its **first non-zero in 27
scans** (previously 0/26). The refreshed audit is `macro` NFCI **1/27** ·
`macro` yield curve 10y–2y **0/27** · `macro` WALCL/RRP **5/27, 0 of the last
22**. **Change:** narrow the already-PROPOSED drop to the yield-curve and
WALCL/RRP rows and leave NFCI under observation. **Expected effect:** avoids
deleting a row on the one session it fired. (Also unscored today, consistent with
the audit: `vol` VXN, `vol` VVIX, `fuel`, both non-PD-mid `structure` rows,
`news`. Not dead today: `vol` VIX9D/VIX +1, `rates` DXY −2.)

### Already proposed, re-affirmed with today's evidence — no new ID
- **DGS10 suppression (09-30)** — strengthened by the 20-of-20 sign-lock census
  in §3(a), and today is the first day it changes the published label.
- **M6, session 20 — the worst instance in the record.** 7 touched rows: **6
  understate** the true worst excursion and **5 of 6 "held" verdicts invert to
  "lost"** when measured first-touch → close against `SETTLE_TOL = 25`:
  31114.3 −23.4/**−47.2** (2.02x), 31078.9 −11.8/**−43.8** (3.71x), 31037.1
  −18.6/**−119.1** (6.40x), 31025.8 −7.3/**−107.8** (**14.77x**), 30979.1
  −13.3/**−61.1** (4.59x); the one row already graded *lost* (30973.1) understates
  25.6/**−55.1** (2.15x). Only 31181.0 is exact (+6.5). **New sub-shape:**
  31181.0 is reported `settled_side: below, settled_from: "open"` when price at
  the session open (31280.1) was **99.1 ABOVE** it. Re-proposed unchanged.
- **P-B(b)** — `merge_tol = max(3.0, 472.8 × 0.008) = 3.78` against
  `TOUCH_TOL = 8.0`; **two** published pairs sit in the structurally-guaranteed
  3.78–8.0 window (31232.0/31225.8 at 6.2, 30979.1/30973.1 at 6.0) and **one
  fired**. 13th session: published 15 / touched 7 / **distinct 5**, rate 0.47 vs
  distinct 0.33, inflation **1.40x**. Proposal unchanged.
- **P-G → instance #15**, three wrong-sided rows (31078.9 PDL *"below us"* while
  47 above and issuing a long trigger off a completed sweep; 31232.0 and 31203.2
  both *"runs the stops below it"* while 200 and 172 **above**). The PDL row is
  the exact mirror of #14's PDH row on the previous session.
- **Session-context field → 9th session and the largest instance by far:
  12 of 15 published rows had already been interacted with pre-scan**, under
  *"New trading day… everything below is fresh"*. The CALL WALL alone had 36
  pre-scan touches.
- **D25** — the drift sentence *"The dominant strike is stable at 0 across 6
  samples"* printed again on this scan. Damage none (section 7 is research-only
  and says *"No volume has traded yet today"* three lines above). Already
  PROPOSED on 10-07; **not re-opened**.
- **D23 — 7th residual, and the ±200pt residual survives.** Board offset
  **+25.8** (NDX ref 31005.9 rolled by the NQ move −218.8 vs CFD 31031.7, basis
  `nq_implied`, greeks `repriced_bs_at_current_spot`); section 7 offset
  **−184.7** at feed time 11:59Z; gap **210.5**; CFD move 11:59Z → scan
  (11:55Z bar open 31024.8 → 31031.7) = **+6.9**; **residual +203.6**. Series
  now **+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6** — four of
  seven sit in 190–250. Extended as a new data point only, **not re-measured**;
  the measured NEGATIVE result stands. Damage none.
- **H22 → n=6, and the label finally varied without helping.** Week net GEX
  **−4.447** → *"expansion likely"* — the first non-*"pinning likely"* label in
  the series — produced **0.79x ADR**, squarely inside the range the five
  *"pinning likely"* days produced (0.63x–1.33x). **Still nothing proposed, same
  reason:** the row carries **−2 of DIRECTION** and six *range* observations are
  not evidence about direction. The pre-registered test (grade the row against
  realised direction across the days already on record) is still the next thing
  to measure.

### No instance today
- **H2 / H3 (fuel cell)** — fuel `MODERATE`, not LOW_FUEL/EXHAUSTED. Neither cell.
  H3's extremes branch is discussed in §3(e) and is convention-blocked.
- **P-E / P-E(b)** — the CALL WALL was never touched post-scan (missed by 38.3),
  so there is **no penetration and no close-side read**, and the board named **no
  brake** on either side. Per the standing instruction: this is not an instance,
  the continuum framing is untouched, and no mode-discriminator search is resumed.
- **H23** — both paths were flagged *clear*, so there was **no named brake to
  test**. Record stays 6 sliced / 1 capped at n=7. One new n=1 observation
  alongside it: the clear-path sentence advertised **406pts of unobstructed
  downside (0.86x ADR)** in the same section as a **158.9pt** range budget — a
  2.6x internal disagreement — and the realised downside extension was **61.1**.
  Logged, nothing proposed.
- **H10** — `structure 0` *"price inside the prior-week range"*; neither the ±3
  branch fired. Note without proposing: price was **5.4 below PWH** and closed
  **+135.5 above it**, and the rule scores a mid-range and an edge-of-range
  position identically.
- **D21** — today's firing is the **bottom**-of-band `+2` (poor R:R for shorts,
  2.9% up a 200pt band, 5.9 from the put wall), not the top-of-band `−2` the
  census tracks. Outcome: price left the band downward by 107.8, closed back
  inside, and the row was **right**. Kept out of the `−2` ledger deliberately —
  merging populations to make a tally read better is what the register forbids.
- **H17** — post-scan move **+137.8 = 36.7%** of session range, far above the 5%
  deadband. No instance; still 1 of 3 days, both 09-11.
- **P-C / `events`** — **no `events` row at all** in 22 components, on a day with
  a High-impact FOMC release inside the session. Absent or zero on every session
  in the record.
- **D18 / D20** — **0 headlines auto-scored**, so neither keyword defect could
  fire. H19 coverage **0.0%** of 26 relevant (second time in the record).
- **D7** — the beyond-range footnote again lists above- and below-price levels
  interleaved by price (31385 · 31271 · 31260 · 30729 · 30101). Convention
  defect, unchanged, not re-opened.

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**. One scan
file for 10-07 (`1250-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (`track.py` excludes 6
across the whole record). **09-24 quarantined by hand — eighth consecutive review
to carry it**; the 09-29 proposal for a schema `quarantine` field read by
`track.py` and `review_day.py` is reaffirmed, and note that `track.py` still
*includes* 09-24 in every printed statistic, so every figure it prints has to be
corrected by hand before it is quoted. **09-09 and 09-25 still have no
`REVIEW.md` and none was created or back-dated.** 2026-10-08's scan exists and is
correctly held back (179 bars); **2026-08-24 is held back incorrectly — see D26.**
