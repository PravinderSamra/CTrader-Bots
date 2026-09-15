# REVIEW — 2026-09-14 (Mon)

Reviewed 2026-09-15. Source: `review_day.py 2026-09-14 --json`, `track.py`,
plus `review_day.py` re-runs on 08-27 … 09-11 for the cross-session counts.
2 gradeable scans (13:04:58Z PRE_NY, 17:23:20Z NY_MIDDAY). 0 test artefacts.
Both `is_trading_day: true`.

**Journal integrity:** clean. `1723-nymidday.json` carries a 2026-09-15 mtime,
which looks like a backfill — it is not. `git log --follow` puts it in commit
`18d2b53`, authored **2026-09-14 17:23:21Z**, one second after its own
`scan_utc`. The mtime is a later checkout touching the file. Nothing on this day
is fabricated or backfilled.

---

## 1. Scoreboard

**Session (NAS100 CFD, 21:00Z roll, 276 M5 bars)**

| | |
|---|---|
| Open / High / Low / Close | 29053.7 / 29291.4 / 28804.7 / **29183.0** |
| Range / Net | **486.7** / **+129.3** |
| Range vs ADR14 (354.5) | **137.3%** |

**The scans**

| | 13:04Z PRE_NY | 17:23Z NY_MIDDAY |
|---|---|---|
| Bias | **−11 STRONGLY BEARISH** | **−12 STRONGLY BEARISH** |
| Shape | COHERENT_SHORT | COHERENT_SHORT |
| Price at scan | 28830.7 | 29246.7 |
| Post-scan move | **+352.1** | −68.1 |
| Direction | **WRONG** | CORRECT |
| Fuel state / budget | LOW_FUEL / 61.9 | EXHAUSTED / 0.0 |
| Actual extension | **194.1** → UNDER by **+132.2 (3.14×)** | 26.6 → err +26.6 |
| Traversal | 472.9 (7.64× budget) | 155.1 |
| Levels published / touched | 5 / 2 = 0.40 | 5 / 2 = 0.40 |

**Direction: 1 right / 1 wrong. Mean level hit rate 0.40.**

**Cumulative** (`track.py`, verbatim) — 7 trading days, 10 deduped scans:
direction **5 right / 3 wrong / 2 no-call**; levels touched **0.48**;
H1 per-day budget error mean **−0.9** (−86.4, −10.7, −26.2, −64.0, +57.3,
+44.3, **+79.4**). H5 early 49.8 vs late −15.9.

The −11 was published at 28830.7, **26.0 points above the session low**, which
was already in from London. It is the worst-timed call in the journal: the
engine reached near-maximum bearish conviction at the day's floor and the index
then ran 352 points in the other direction.

---

## 2. What the levels actually did

**13:04 board — 2 of 5 touched, and both touched ones were excellent.**

| Level | brief said | actually did | verdict |
|---|---|---|---|
| 29591.3 **GAMMA FLIP** _(stretch, +761)_ | "the line where desks switch from pushing to damping" | **never reached** — closed 408.3pts below it | untestable. Published 761pts away on a day the same brief budgeted **61.9pts** of range |
| 29287.8 **CALL WALL** ●●●●● 1.89bn _(stretch, +457)_ | "desks must SELL as price rises into it, so **rallies stall. Take profit into it**" | touched 17:45, held as resistance **475min**, worst excursion **+3.6pts**. Session high 29291.4 | **worked exactly as written.** 3.6pts of overshoot on a 486.7pt day — the tightest ceiling in the journal after 09-11's +9.6 |
| 29262.8 MAX PAIN _(stretch, +432)_ | "price drifts toward it as the week goes on. **Weak on a Monday**, strong Thu/Fri" | touched 16:45, held as resistance **140min**, worst **+7.4pts** | **worked, and the hedge was wrong.** It was a Monday and max pain was the first thing to stop the rally. The day-of-week qualifier has now been wrong in both directions: it failed on the Friday (09-11) and worked on the Monday |
| 28804.7 London Low (today) | "the next session usually runs the stops below it" | **never traded below it after the scan** — it *was* the session low | **wrong call, right level.** The stop run did not happen. The level was the reversal pivot, not a liquidity target |
| 28787.8 **PUT WALL** ●●●○○ 1.08bn _(−43)_ | "if it breaks, expect it to **speed UP, not bounce. Don't buy the break**" | **never reached** — price came within 16.9pts and turned | untested. The floor held without being tagged; the "don't buy the break" warning was the losing side of the day |

**17:23 board — 2 of 5 touched.**

| Level | brief said | actually did | verdict |
|---|---|---|---|
| 29351.2 **GAMMA FLIP** _(+104)_ | "reclaim and hold above and fading becomes valid" | **never reached** — closed 168.2pts below | no test |
| 29317.4 **CALL WALL** ●●●●● 2.43bn _(+71)_ | "rallies stall. Take profit into it" | **never reached** — the high was in at 29291.4, 26pts below | no test. The wall the 13:04 board published (29287.8) was the one that held; the 17:23 re-read moved it **+29.6pts away** and past the high |
| 29292.4 MAX PAIN _(+46)_ | "drifts toward it… weak on a Monday" | touched 17:50, held as resistance **215min**, worst **−1.0pts** | **worked.** 1.0pt violation — the cleanest hold on the board |
| 29167.4 **PUT WALL** ●●●○○ 1.39bn _(−79)_ | "if it breaks, **expect it to speed UP, not bounce. Don't buy the break**" | touched 19:55, held as **support 40min**, 6 further touches, worst **−16.1pts**, settled above, closed 15.6pts above it | **the brief said the opposite of what happened.** It bounced. "Don't buy the break" was the wrong instruction at the level that ended up carrying the close |
| 28767.4 STRUCTURAL PUT WALL _(−479)_ | "mark it and leave it… **not an intraday trigger**" | never reached | correctly labelled, and correctly untradeable — see §4 |

**The finding of the day is that the level board was right and the direction
call was wrong.** The 13:04 brief told the trader to sell into a 761pt-away flip
and warned him off buying a put-wall break. The two levels it did put in range
above — call wall and max pain — capped the rally within 3.6 and 7.4 points. A
trader who ignored the bias line and traded only the published ceilings had a
good day; a trader who followed the −11 did not.

---

## 3. What was wrong, and why

### The −11 at 13:04, component by component

Score decomposes as: gamma −3, vol +3, rates −2, macro −2, breadth +1, fuel 0,
**structure −5**, **news −3** = **−11**. Two blocks carry 8 of the 11.

**(a) `structure −3` — prior week range, no reclaim condition (H10).**
Fired on PWL 29018.3: *"price is BELOW the entire prior-week range… PWL 29018.3
is now resistance, not support."* Price reclaimed it during the session and
**closed 164.7 points above it**. The proof is in this journal, not in my
arithmetic: the 17:23 scan of the same engine prints
`structure 0 — "price inside the prior-week range (29018.3-29734.1)"`. The
premise expired **within 4h19m** and the −3 was live for all of it, because the
rule scores a state with no decay and no inversion.

**(b) `gamma −3` — flip distance is ignored.**
*"below flip 29591.3 by 760.6pts — SHORT gamma, dealers amplify."* The full −3
is awarded at 760pts below the flip exactly as it would be at 5pts below. The
partially-offsetting `gamma +2` ("bottom 20% of the wall band — poor risk/reward
for shorts") is the only thing in the engine that noticed price was at an
extreme, and it is worth two thirds of the penalty it is offsetting. Net gamma
on the day: −3.

**(c) `macro −3` — a frozen FRED series that still moves the score.**
*"Real yield 10y (DFII10) is 2.55%, up 9bp as of 2026-09-10… ⚠️ FRED has not
published since 2026-09-10 (2 business days ago) — this is last week's
reading."* The engine **prints the staleness warning and then scores the full
−3 anyway**. This is the largest single macro weight in the model, and it has
been driven by a frozen 2026-09-10 print for four trading days running.

**(d) `news −3` from 5 headlines out of 52.** The auto-scorer counted 5
(1 bull / 4 bear) and left **47 uncounted**. A −3 block — 27% of the total score
— set by a 9.6% sample.

### What would actually have saved the call — and what would not

Honest accounting: removing the PWL −3 alone gives −8, still STRONGLY BEARISH.
Removing the stale macro −3 as well gives −5, still BEARISH. **No single fix
rescues this day.** What would have changed it is the thing none of these
components model: price was at the day's low with 82.5% of ADR already spent,
and the engine's own fuel block says in words *"fuel is short — this dampens
CONVICTION… it does not change direction"* and then contributes **0**. That is
H2/H3 territory and it is now the third day it has bitten.

### The fuel call

Budget 61.9 → extension 194.1 (**3.14×**), traversal 472.9 (**7.64×**). The
13:04 brief simultaneously said "61.9pts of range left" and published three
levels 432, 457 and 761 points away. Two of those three were reached. The
internal contradiction was visible on the page before the day started.

---

## 4. Change proposals

`track.py` reports the 3-day threshold met for H1/H2/H3/H5/H7 and the 5-day
threshold met for H4/H6, with the standing warning that *day count alone is not
evidence*. Four items below clear that bar on evidence, not just on count.
Everything else is logged as observation only.

### P1 — Zero or decay the macro weight when the FRED series is stale (NEW, propose)

**Change.** When a FRED-derived component's underlying series has not published
for ≥1 business day, scale its points toward 0 rather than scoring it at full
weight. The engine already detects and prints the condition.

**Evidence (4 trading days: 09-10, 09-11, 09-14, 09-15).** DFII10 has been
frozen at the 2026-09-10 print since 09-10. Scores in that window: `0, 0, −3,
−3, −3, −3, −3`. **The score changed from 0 to −3 while the data did not
change at all** — because the 5-day comparison window keeps rolling forward
while the endpoint stays fixed. A frozen series is manufacturing a moving
signal, and it is the biggest single macro weight in the model.

**Expected effect.** On 09-14 13:04 it removes 3 bearish points from a call that
was wrong by 352 points. It does not make the day right on its own (§3), and it
would have *cost* nothing on 09-11, where the same −3 rode along with a call
that was correct for other reasons.

### P2 — Add a reclaim term to the prior-week-range rule (H10, propose)

**Change.** `structure −3` should decay or invert when price trades back inside
the prior-week range intraday. Not a smaller constant — a reclaim condition.

**Evidence (4 firings, 4 trading days: 08-24, 08-26 ×2 scans, 08-26 overnight,
09-14). Every one produced a wrong direction call.** 08-24 13:45 (−12, closed
+147 above the scan), 08-25 21:56Z for the 08-26 session (−15, closed +140),
08-26 13:12 (wrong by 249.8pts, price reclaimed within the hour and never traded
half a point below the level), 09-14 13:04 (wrong by 352.1pts, reclaimed within
4h19m, closed 164.7 above the PWL). **The rule is 0-for-4.**

**Caveat, stated plainly:** four firings is a small sample and three of them sit
in one cluster of consecutive August sessions, which may be one market
condition rather than four independent tests. I am proposing it because it is
0-for-4 with a *mechanism* — no reclaim term — that is visible in the code path,
not because the count reached 4.

**Expected effect.** −11 → −8 on 09-14 13:04 once the reclaim lands, and the
component stops being the single largest bearish weight on days where its own
premise has already failed.

### P3 — Exclude `kind: structural` levels from the level hit-rate statistic (propose)

**Change.** Do not count structural walls in `levels_touched` / `level_hit_rate`.
Keep publishing them — do not drop them.

**Evidence (5 publications, 3 trading days: 09-09, 09-10 ×2, 09-14). Zero
touches, and that is correct behaviour**: the brief itself labels them *"the
floor for the WEEK/MONTH… mark it and leave it, not an intraday trigger."*
Scoring a deliberately multi-day level on whether it was hit intraday is a
measurement error, not a model error. Corpus hit rate **0.544 all levels →
0.581 excluding structural**; 09-14 17:23 goes 0.40 → 0.50.

**Expected effect.** Removes a known bias from H6's denominator before H6 is
read at its 5-day threshold. No change to what the trader sees.

### P4 — Stop quoting a point-precise budget when it is above zero (propose)

**Change.** Print the number when `remaining_budget == 0`; print a band or a
qualitative state when it is > 0.

**Evidence (7 trading days, 10 scans).** Split the H1 errors by whether the
budget was zero:

| budget | scans | errors | MAE |
|---|---|---|---|
| **= 0.0** | 3 (09-10, 09-11, 09-14) | 0.0, 0.0, +26.6 | **8.9** |
| **> 0.0** | 7 | −86.4, −10.7, −26.2, −64.0, +114.6, +88.7, **+132.2** | **74.7** |

Mean budget when > 0 is 147pts and the mean absolute error is **51% of it**,
with the sign flipping (four over-reads then three under-reads). Per-day mean
error is −0.9 — the number is unbiased and useless at the same time. **There is
no multiplier to fit here and I am not proposing one.** The zero case, by
contrast, is now 4-for-4 across four days counting 24 Aug's +5.3: once ADR-used
passes ~125%, the extremes really are in.

**Expected effect.** Kills the 09-14 failure mode where the page says "61.9pts
of range left" beside three levels 432–761pts away, two of which traded.

### Tested and NOT proposed

- **Fuel-ratio correction to the budget.** I checked whether "burning hot"
  (`fuel_ratio` > 1) predicts the under-read. It does not: ratio 2.75 → err
  −10.7, ratio 1.06 → −64.0, ratio 2.17 → +88.7, ratio 1.65 → +132.2. No
  relationship. Fitting one would be tuning on noise. Recorded as a negative
  result so nobody re-runs it.
- **Dropping the `fuel` component as dead weight.** It is 0 in all 17 entries
  across 10 scans, but that is the documented "reports, never votes" design, not
  a bug. No change.
- **Gamma-flip distance scaling** (§3b). Mechanically suspect, but I have one
  clean instance of an extreme distance. Logged to H7, not proposed.

### Still observing — the watch list

- **H4 (flip as magnet):** now **9 days**, threshold met, and it fails. Close-to-
  flip distances: 1.1, 236.6, 255.2, 599.8, 309.2, 26.2, −263.5, 57.7/335.6,
  −408.3/−168.2. Three near, six far. HYPOTHESES' standing verdict — *do not use
  the flip as a target* — holds. No further change to propose; the flip is
  already not published as a target.
- **H2/H3 (over-commitment at the extreme):** 09-14 13:04 is the third instance
  — max-conviction continuation printed at a session extreme with fuel short,
  and price reversed. 08-24 13:45 and 08-25 13:04 were the first two. This is
  the strongest untouched hypothesis in the register and I expect it to become a
  proposal next session. Not this one: all three instances are *bearish* calls at
  *lows*, so I cannot yet tell over-commitment from a directional artefact.
- **News auto-scorer sampling bias (NEW, watching).** Across 11 days the
  auto-scorer has produced **20 bearish, 4 bullish, 7 flat** readings, counting a
  median of 2 headlines and leaving a median of ~47 uncounted. On 09-14 it was
  5 of 52. Either the news really has been bearish for eleven straight days, or
  the keyword patterns that make a headline auto-scorable skew to alarm. The
  distinction matters because `news` is the most negative block in the engine
  (sum −19 over 10 graded scans, vs structure −5). **What to record:** counted
  vs uncounted count, and the sign, every scan. **What would settle it:** score
  the uncounted headlines by hand on three days and compare the sign to the
  auto-scored subset. Free, no new data source. Not proposing a weight change
  until that test is run.
- **H1 time-of-day term (H5):** early 49.8 vs late −15.9 still points the right
  way, but 09-14's largest-ever under-read (+132.2) came from a 09:04 ET scan
  that was already at 82.5% ADR — early by clock, late by range life. If a
  correction is ever fitted, the axis should be range-life, not clock time.
