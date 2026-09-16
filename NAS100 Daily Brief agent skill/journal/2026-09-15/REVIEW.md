# REVIEW — 2026-09-15 (Tue)

Reviewed 2026-09-16. Source: `review_day.py --json` (resolved to 2026-09-15),
`track.py`, and the immutable `prediction` block of `2026-09-15/1246-preny.json`.
**1 gradeable scan** (12:46:58Z PRE_NY). 0 test artefacts. `is_trading_day: true`.

**Journal integrity: clean.** `1246-preny.json` is in commit `2f3a37e`, authored
`2026-09-15T12:47:02Z` — four seconds after its own `scan_utc`. Not backfilled,
not fabricated. No `is_trading_day: false` scan exists on this date, so nothing
was excluded on that ground.

---

## 1. Scoreboard

**Session (NAS100 CFD, 21:00Z roll, 276 M5 bars)**

| | |
|---|---|
| Open / High / Low / Close | 29174.2 / 29189.4 / 28909.8 / **28983.4** |
| Range / Net | **279.6** / **−190.8** |
| Range vs ADR14 (360.9) | **77.5%** |

**Direction — 1 right / 0 wrong / 0 no-call**

| | |
|---|---|
| Bias / label | **−12 / STRONGLY BEARISH** |
| Expected direction | −1 → actual **−1** → **CORRECT** |
| Price at scan | 29119.3 → close 28983.4 (**−135.9**) |
| Max favourable from scan | to the low 28909.8 = **−209.5** |

**Fuel — OVER-estimated**

| | |
|---|---|
| Remaining budget | 97.3 |
| Range extension | **16.0** (0.16×, error **−81.3**) |
| Price traversal | 269.3 (2.77×) |

**Levels — 14 published, 9 touched, hit rate 0.64** (0.69 = 9/13 excluding the
one `kind: structural` level, per the standing P3 proposal).

---

## 2. What the levels actually did

**The `acted_as` column is uninformative today and I am not going to quote it as
a result.** Eight of the nine touched levels graded "held as resistance", the
ninth "held as support" — and the ninth (Asia Low prev-day, 28963.1) is simply
the only level below the close. The close, 28983.4, sits between it and 29005.8,
and the verdicts partition exactly there. This is **M6** (the settled verdict is
a function of `bars[-1].close`) in its cleanest form yet: a −190.8 day cannot
produce anything but a wall of "resistance". **Ninth session of M6 evidence.**

The non-degenerate read is `first_touch_reaction`:

| | count | levels |
|---|---|---|
| broke DOWN through it | 3 | PD close 29183.0, Equal highs 29167.2, London High prev-day 28974.3 |
| traded both sides — chopped | 6 | London High 29134.8, Asia High prev-day 29089.7, PD mid 29048.1, PUT WALL 29019.4, Asia Low 29005.8, Asia Low prev-day 28963.1 |
| clean rejection | **0** | — |

**Not one level produced a clean rejection on a 279.6-point trend day.** Six of
nine chopped. The nine touched levels span 219.9pts (29183.0 → 28963.1) inside a
269.3pt traversal — the board is denser than the path, so touching most of it is
close to arithmetic. The 0.64 hit rate is substantially a density artefact, not a
result. (Same finding as HYPOTHESES line ~1330.)

**The put wall label was right, and that is worth recording.** 29019.4 was
published with the regime-aware note *"Heaviest floor this week… BUT today the
desks are pushing moves along — if it breaks, expect it to speed UP, not bounce.
Don't buy the break."* Price chopped around it, broke, and ran 109.6pts to the
low without a bounce. It did **not** act as a floor. This is the **H14 fix
working as designed for the second recorded time**, and it is the one label on
the board that made a falsifiable claim and survived it.

**Never reached (5/14).** CALL WALL 29319.4, MAX PAIN 29259.4, GAMMA FLIP
29240.2, Asia High (today) 29189.4, STRUCTURAL PUT WALL 28769.4.

- The three upside gamma levels were 120–200pts above spot and all carried
  `stretch: true`. The call wall sat 130.0pts above a session high that was
  already in, against a 97.3pt budget. Correctly flagged; D7 deliberately exempts
  walls from the budget filter. **No finding — the labelling did its job.**
- **Asia High (today) 29189.4 was the session high to 0.0pts** and still counts
  as a miss, because the high printed before the scan. That is the right call by
  the grader and still means a descriptively perfect level scored as a failure.
- **STRUCTURAL PUT WALL: 6th publication across 4 trading days, 0 touches.** Its
  own note says *"the floor for the WEEK/MONTH… mark it and leave it, not an
  intraday trigger."* It is behaving correctly and being graded incorrectly.
  Reinforces standing proposal **P3**; this is not a level to stop publishing.

**Published, claimed, and never graded: the secondary gamma table.** Four more
strikes were published with explicit behavioural claims (29219.4, 29119.4,
29069.4, 28919.4) and **none of them appear in `prediction.levels`**, so none has
ever entered a statistic. One made a checkable call and lost: **28919.4** —
*"dealers are SHORT gamma here, so they amplify: price tends to accelerate
THROUGH rather than stall. Not a floor."* The session low was **28909.8**, 9.6pts
through it, and price closed **73.6pts back above**. It acted as a floor. n=1,
ungraded — an observation, not a proposal. The measurement gap itself is §4 P5.

---

## 3. What was wrong, and why

The direction call was right, so the failures are elsewhere — and the direction
grade hides them.

**(a) The fuel over-read by −81.3, the second-largest on record** (worst: −86.4,
08-27). Budget 97.3 → extension 16.0. Nothing new in mechanism; it lands in the
`budget > 0` bucket, which is now **n=8, MAE 75.5** against a mean budget of
~147pts — **51% of the number being printed**, unchanged from the 09-14 reading.
The `budget = 0` bucket stays **n=3, MAE 8.9**. Per-DAY error across 7 days is
**−0.2pts** with a ±80pt spread: there is no bias for a multiplier to remove.

**(b) The prose attached to that budget was wrong in a way "CORRECT" conceals.**
The brief said *"nothing structural to slow a breakdown… If it goes, it has
room. Do not fade it."* It had **16.0pts** of room. The −209.5 that was actually
available came from price sitting **193.5pts above a low (28925.8) that had
already printed before the scan** — retracement inside the range, not extension
of it. H1's claim block already says the budget means *"the extremes are probably
in — expect movement between them"*; **that reading is not reaching the prose.**
The component responsible is the fuel block itself: it reports
`remaining_budget` and `adr_used_pct` and **does not report distance to the
existing session extremes**, so the narrative has no field to say "the move is
back to the low, not beyond it". Meanwhile `LOW_FUEL` printed *"this dampens
CONVICTION"* on a day offering a 209-point short. **Observation, logged under H1.**

**(c) `macro −3` was set by a series that had not published — and today is the
clincher for H18.** The component fired at full weight on `DFII10`, and the
engine's own `why` string says *"FRED has not published since 2026-09-11 (2
business days ago) — this is last week's reading, not today's."* It detects
staleness and scores anyway. That −3 was **25% of the −12**. It pointed the right
way, which is luck, not validation.

The new evidence is the next scan. On **2026-09-16 12:46Z** FRED published
through 09-14 and the same series scored **0** — with the 5-day move essentially
unchanged (**18bp → 17bp**). The −3 existed only inside the stale window and
died the moment real data arrived. Score sequence over the freeze:
`09-10 0, 09-10 0, 09-11 −3, 09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3, 09-16 0`.
**The series moved 1bp; the score moved 3 points twice.** Standing proposal
**P1** should be prioritised on this.

**(d) `news −3` was set by 4 headlines out of 57 — a 7.0% sample** (0 bull / 4
bear). H19's open question. Today sharpens the *mechanism*: on 09-16 the same
scorer read **1 of 50, 0 bull / 1 bear → NEUTRAL (0)**. Both days were **100%
bearish among counted headlines**; the scores were **−3 and 0**. The difference
is the **match count**, not the sentiment. So the magnitude of the most negative
block in the engine tracks how many headlines happened to trip a keyword. A
minimum-count floor may well be deliberate and sensible — but it means "−3" and
"0" here are not two readings of the news, they are two sample sizes.
**Recorded under H19. Still OBSERVING; the hand-score test has not been run.**

**(e) H10 did not fire.** `structure 0 — "price inside the prior-week range"`.
The prior-week-range rule stays **0-for-4**; today adds nothing to it.

**(f) H3 got its first observation from the top of the range — and it still does
not separate the two explanations.** Bias −12 was printed at 29119.3, which is
**73% up the range already established at scan** (28925.8–29189.4), 70.1pts below
the session high. All three contaminating H3 instances were max-conviction
bearish calls printed at *lows*, all wrong. This one was printed near the *high*
and was right.

That is the missing cell, and it is tempting. It is also **not** the separator
H3 needs. A plain bearish skew predicts today exactly as well as H3 does — the
engine printed −12 and the day fell; nothing distinguishes "correctly read the
top of the range" from "is always bearish and got a down day". The separator is
still **a max-conviction BULLISH call**, and after 8 graded days there has not
been one. **Record, do not propose.**

---

## 4. Change proposals

`track.py` reports the day-count gate **met** (7 trading days, 10 scans, vs
`MIN_SESSIONS = 3`) and prints its own warning that *"day count alone is not
evidence."* I am treating that as the standard. Four proposals (P1–P4) from the
09-14 review are already with the user; I am not re-proposing them, only
reporting what today does to their evidence.

### Standing proposals — effect of today

| | status after 09-15 |
|---|---|
| **P1** scale a macro component toward 0 when its FRED series is stale | **Strengthened decisively.** §3(c): the same series scored −3 then 0 on a 1bp move, with the −3 living entirely inside the freeze. **Prioritise.** |
| **P2** add a reclaim condition to the prior-week-range rule | Unchanged. Rule did not fire. Still 0-for-4. |
| **P3** exclude `kind: structural` from the hit-rate denominator | **Strengthened.** 6th publication / 4 days / 0 touches, behaving exactly as its own note instructs. |
| **P4** print a band, not a point, when `budget > 0` | **Strengthened.** `>0` bucket n=8, MAE 75.5 ≈ 51% of the printed number; `=0` bucket n=3, MAE 8.9. Per-day mean error −0.2 — dispersion, not bias. |

### P5 (NEW) — grade the secondary gamma table

**What.** Add the secondary "other gamma concentrations in range" strikes to
`prediction.levels` (or to a parallel graded list) so `review_day.py` scores them.

**Evidence.** The table is published in **every brief**, and across the whole
journal it accounts for **107 strike-publications over 22 trading-day scans on 10
separate trading days — of which 0 appear in `prediction.levels` and 0 have ever
been graded.** Each row carries a directional claim in its own words ("brake a
move" / "accelerate THROUGH rather than stall. Not a floor"). Those claims have
been published for three weeks and tested never.

**Why this clears the bar despite being new.** It is not a tuning and it touches
no scoring logic — it converts an unmeasured output into a measured one. The
3-session rule exists to stop fitting to noise; this proposal adds observations
rather than consuming them.

**Expected effect.** Provides the first data on whether the put-dominant
"accelerates through, not a floor" note is true. Today is a point against it
(28919.4 caught the low to within 9.6pts and price closed 73.6 above), but n=1
and ungraded is exactly why this is needed.

**Sequencing caveat.** This enlarges the hit-rate denominator, so it must land
**with or after P3** and before H6 is read at its 5-day threshold, or H6 will be
read off a denominator that changed underneath it.

### Not proposed

- **M6 remains the blocker on all level statistics.** Today is its 9th session
  and its cleanest instance. Nothing about H6, H14's empirical half, or any
  `acted_as` count can advance until the settled verdict stops being a function
  of the close. M6's fix direction is already written up; it needs a decision,
  not more evidence.
- **H19** — no weight change. The hand-score test has not been run. Today's
  contribution is mechanism (§3d), not a distributional claim.
- **H3 / H2** — no conviction cap. Sample is still one-sided (§3f).
- **No new data point is needed.** Every gap found today is in what the engine
  already holds and does not read: FRED's own `realtime_end` (P1), the fuel
  block's distance to existing extremes (§3b), the news scorer's uncounted
  headlines (H19), and strikes the brief already computes (P5). Nothing here
  argues for a new feed.

### What I am watching

1. A **max-conviction bullish call** — the only thing that separates H3 from a
   bearish skew. Absent in 8 graded days.
2. Whether `DFII10` re-freezes and the score walks again (H18, forward test of P1).
3. The **news match count** per scan alongside the sign, now that §3d shows the
   magnitude tracks the count (H19).
4. Whether any level ever produces a **clean rejection** rather than "chopped" or
   "broke through" — 0 in 9 touches today.

---

_Evidence appended to `journal/HYPOTHESES.md`. No `prediction` block was edited._
