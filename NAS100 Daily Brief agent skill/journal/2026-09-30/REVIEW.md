# REVIEW — 2026-09-30 (graded 2026-10-01)

Source: `review_day.py 2026-09-30 --json`, `track.py`. 1 gradeable PRE_NY scan
(12:47:21Z), `is_trading_day: true`, 0 test artefacts, 276 M5 bars
(09-29 22:00Z → 09-30 20:55Z).

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 30412.5 / 30655.2 / 30262.0 / 30469.1 |
| Range | **393.2 = 0.84x** ADR14 468.4 |
| Net | **+56.6**, close 52.7% up the range |
| High / low times | H 15:50Z (post-scan) · L 11:20Z (**pre-scan**) |
| Pre-scan H/L | 30527.0 / 30262.0 |
| Post-scan H/L | 30655.2 / 30387.3 (+193.9 / −74.0 from the scan) |
| Call | **MILDLY BEARISH −3**, expected direction −1 → **WRONG** |
| Post-scan move | +24.0 on traversal 267.9 — wrong by **9.0%** of the distance travelled |
| Fuel | budget 203.4 vs extension 128.2 → err **−75.2** (0.63x), grader *"about right"*; traversal 1.32x budget |
| Level hit rate | **0.47 published** (8/17) · **0.24 distinct touch events** (4/17) |
| Shape | `SPIKE_THEN_REVERT` — high at 15:50Z then −186.1 into the close: **right** |

Record, carried by hand because `track.py` has no quarantine and still prints
2026-09-24 CORRECT (*D23 CORRECTED*):

| | raw `track.py` | **09-24 excluded** |
|---|---|---|
| all sessions | 15 right / 9 wrong / 7 no-call | **14 / 9 / 7** |
| PRE_NY, by day | 10 / 5 / 3 over 18 days | **9 / 5 / 3 over 17 days** |

09-25's row (bias +1, no-call) is taken from `track.py`'s per-scan table and
agrees with the 09-28 review's register entry; it was **not** re-derived and no
review file was back-dated for 09-24 or 09-25. 09-24's fuel error (+13.6) stays
in the H1 series on the D1 precedent.

## 2. What the levels actually did

| level | brief said | actually |
|---|---|---|
| 30637.7 Options shelf 0.54bn | *"expect price to stall, take partials"* | **capped the day.** High 30655.2 = **+17.5** through, 6 bars above (14:05–16:15), then resistance to the close. Claim good |
| 30537.7 CALL WALL ●●●○○ + shelf ⭐ | *"rallies stall. Take profit into it"* | **sliced.** 73 bars above it (13:30→19:50Z), **+117.5** through, closed 68.6 below. A 6h20 hold above is not a stall |
| 30486.8 Asia High (today) | *"the next session usually runs the stops above it"* | already **40.2** below the pre-scan high; post-scan ran **+168.4**. Not a sweep-and-fail |
| 30471.8 PDH + NY High ⭐ | *"Sweep it, wait for a lower high, CISD = short"* | above it for 103 bars, first at 00:00Z — **swept pre-scan**. Post-scan it ran **+183.4**. The CISD short was the losing side |
| 30465.4 London High (prev) | *"runs the stops above it"* | graded support, worst −22.8, 45min. Already exceeded pre-scan |
| 30457.3 London High (today) | *"runs the stops above it"* | graded support, worst −19.9, 50min. Already exceeded pre-scan |
| 30404.6 PD close | *"price often comes back to fill a gap from here"* | held as support 490min, worst −17.3. Claim good |
| 30391.7 GAMMA FLIP | *"ABOVE it: they're damping, dips supported"* | **held, worst −4.4, 490min.** The cleanest call on the board |
| 30487.7 (section 3, *not on the board*) | *"Expect a stall at 30487.7 (26pts away) — take partials into it"* | **sliced by +167.5.** The only named upside brake, and it is on neither the level board nor the secondary-concentrations table |

**Four levels — 30486.8, 30471.8, 30465.4, 30457.3 — were all resolved by
`bar_index 178`, the 12:50Z scan bar itself.** They are one event, not four. The
published 0.47 is 1.96x the distinct-event rate of 0.24, the worst ratio in the
8-session P-B(b) series. 30471.8 / 30465.4 are **6.4pts apart**, inside the
structural gap between `merge_tol` (`max(3.0, 468.4*0.008)` = **3.747**) and
`TOUCH_TOL` (**8.0**) — guaranteed to publish as two lines and grade as two
touches off one bar.

**Six of the nine levels the grader calls "never reached" were reached — before
the scan.** Pre-scan range 30262.0–30527.0 already contained **12 of the 17**
published levels. Two matter:

- **PUT WALL 30337.7** — *"expect a bounce and a good long-sweep here"*, published
  124pts below spot. Price was **below it for 39 bars, 02:30Z→12:25Z, 75.7pts
  through**, and reclaimed it **22 minutes before the brief was written**. Graded
  *"never reached"*.
- **London Low (today) 30262.0** — *"the next session usually runs the stops below
  it"*, published at −199. **It is the session low, to the point.** Graded
  *"never reached"*.

Nothing reacted to: MAX PAIN 30212.7 (174.6 short of the post-scan low), NY Low
30253.0, PDL 30119.5 — all three correctly tagged *(stretch)*.

## 3. What was wrong, and why

The score was **−3, exactly on the `MILDLY BEARISH` threshold** (`bias_engine.py`
line 271: `total <= -3`). It was carried entirely by **macro −6**, and the two
largest rows of that block say in their own text that they are stale:

| row | pts | its own words |
|---|---|---|
| macro DFII10 | **−3** | *"FRED has not published since 2026-09-28 (2 business days ago) — this is last week's reading, not today's"* |
| macro DGS10 | **−1** | *"moved 7bp **up** (2026-09-25 to 2026-09-28)"* |
| rates US10y | **+1** | *"5.207 (−0.91%) — yields **down**, BULLISH tech"* |

**Dropping DFII10 alone takes the score to 0 — `NEUTRAL / TWO-WAY`, no direction
call, and the WRONG disappears.** Dropping the stale DGS10 as well gives +1, also
neutral. One stale row was the whole margin, and this is the **first** session in
the record where that is true of a wrong call (H18's 6th–8th instances all sat on
correct ones).

**DGS10 and the live `rates` row are the same instrument, scored twice, today
with opposite signs.** On 09-29 the pair pointed the same way and "yields fell"
was worth +2; today they cancel. The duplication is now observed in both
configurations and is code-certain either way.

Two further notes on the same −3:

- **`news −2` was independently sufficient to flip the call**: with news at 0 the
  score is −1, also neutral. It came from **2 auto-scored headlines out of 53
  relevant (3.8%)**, both bearish — while *"Fed's preferred gauge showed core
  inflation at 3.0% in August, **much lighter than expected**"* sat in the
  51-headline unscored pile. H19's mechanism, unchanged.
- **DFII10's `why` string says "last week's reading" about 2026-09-28, which is
  the Monday of the same week.** The phrase is unconditional in the source.

What was right, and worth separating from the above: **gamma +2** (*"above flip
— dips supported, upside grinds"*) was the only directionally correct component,
and the flip held to within 4.4pts over 490 minutes. But the **same block's
strategy text was wrong on the day's dominant leg**: *"dealers fade extensions,
so sweeps genuinely fail — this is your fade day"*, on a session that ran +193.9
from the scan through four session-extreme levels and 117.5pts through the call
wall. The logged coherence fix is scoped to the short-gamma branch; this is the
long-gamma / MODERATE-fuel cell, n=1.

**D22(a) did not fire today** — breadth read the 09-29 cash session (NDX +0.21%
vs ES +0.40%), the correct latest, and both rows scored 0. The D22(a) coupling
below is carried from 09-28/09-29, not from this session.

## 4. Change proposals

`track.py`: 22 days, threshold met. Four items have the evidence; everything else
is logged in `HYPOTHESES.md` and proposes nothing.

**(1) Ship H18 / P1 — age-gate the FRED block — and drop the duplicate DGS10
row.** Evidence: 9 instances; 09-28 (stale rows cancelled and bought a correct
label), 09-29 (opposite pulls, label survived on a net +2 FRED block), **09-30
(sole margin of a wrong call)**. Change: zero or halve any FRED row whose
observation is more than one business day old, and suppress DGS10 whenever a live
US10y read exists. Expected effect: 09-30 becomes `NEUTRAL` / no-call, PRE_NY
record 9/5/3 → **9/4/4**; 09-28 and 09-29 keep their labels. Per 09-28 and 09-29,
**must ship together with D22(a)** — H18 alone would have degraded 09-28.

**(2) Reaffirm the `tested_today` / whole-session grading proposal (09-29).**
4th session, and today supplies the quantified census: 12 of 17 levels already
inside the pre-scan range, 6 of 9 "never reached" levels reached pre-scan, the
PUT WALL reclaimed 22 minutes before the scan and published as a forward bounce,
and the session low published as a forward stop-run. No score change.

**(3) Reaffirm P-B(b) (`merge_tol >= TOUCH_TOL`, publish distinct-touch-events).**
8 sessions; today is the worst ratio recorded (1.96x) and the 6.4pt pair is a
code-certain instance of the structural gap.

**(4) M6 needs a decision, not a 16th instance.** Instances 14 and 15 today, both
of the "benign number hides the real breach" type and both code-certain:
`settled_read` sets `last_far` to the last bar on the far side and measures
`worst_excursion` only after it, so every excursion before the final settle is
invisible by construction. Call wall: *"lost by 39.2pts"* against an actual
**117.5pt** breach held for 6h20. Shelf 30637.7: *"held as resistance, worst
+5.6pts"* against an actual **+17.5**. Both rows also contradict their own
`first_touch_reaction` field.

**Also reaffirmed:** the schema-level `quarantine` field (09-29). Today is the
third review to carry 09-24's exclusion by hand.

**Logged, nothing proposed:** H1 (n=22, MAE 84.9 vs mean budget 108.1 = 79%;
fourth consecutive large error — reinforces closing the multiplier branch) ·
P-E (10th instance, sliced 117.5 → **4 capped / 6 sliced**, the 12–103 middle
still empty) · P-E(b) (shelf 8th instance at +17.5, back inside 22, and today
**contradicts** 09-29's session-extreme lid reading — all four upside extremes
sliced by 168–198) · H19 (counted 2 / uncounted 51, 100% bearish, score −2) ·
H4 (flip held, worst −4.4) · max pain (4th distance-confounded miss, 174.6 short)
· D7 (forward-only, no breach of ±355.95; high-budget bucket 3 of 10) · D23
(offset +37.7 ordinary, but this is an `nq_implied` roll-path day so the proposed
cross-check is **circular here and reports nothing** — and the board's +37.7 vs
section 7's −20.3 is a 2nd instance of two offsets for one grid, 58.0pts apart,
harmless today because section 7 was empty) · P-F (inside-range control, err
−75.2, 18 days) · D21 (did not fire) · structure tolerance band (+165.6, no
instance) · P-C (no `events` row again) · **H23 opened, OBSERVING** (the fuel
section's named brake: 30487.7 sliced by 167.5, and it is on no table in the
document).

**Journal hygiene.** No fabricated or backfilled entries; `prediction` block
untouched. 09-24 excluded by hand from the options fields, the direction tally and
the hit-rate series; its fuel error kept. 09-25 cited, not re-derived. The 09-23
review's pre-registered D21 test is treated as void.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
