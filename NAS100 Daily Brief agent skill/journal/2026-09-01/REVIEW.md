# REVIEW — trading day 2026-09-01

Graded 2026-09-02 after the 21:00 UTC roll on 09-01. **Two gradeable scans**
(13:22 PRE_NY, 14:42 NY_OPEN). Both `is_trading_day: true`, no `test_artefact`
entries, both committed by the normal archive flow at their own scan times
(`d32e97d`, `f01d81d`) — the entries are genuine. The 09-02 scan is held back by
`track.py` (day unfinished) and enters nothing here.

Arithmetic from `review_day.py --json` and `track.py`; nothing recomputed.

---

## 1. Scoreboard

Trading day = 2026-08-31 22:00 UTC → 2026-09-01 20:55 UTC (276 M_5 bars).

| | |
|---|---|
| Open / High / Low / Close | 29464.6 / 29521.7 / 28954.2 / **29088.3** |
| Range | 567.5 (**147.7% of ADR14 384.3**) |
| Net | **−376.3** |
| Direction call, 13:22 PRE_NY | BEARISH −8 · price **+24.9** from scan → **WRONG** |
| Direction call, 14:42 NY_OPEN | BEARISH −8 · price **−97.9** from scan → **CORRECT** |
| Level hit rate | 13:22 **0.50** (1/2) · 14:42 **0.00** (0/2) · pooled **1/4 = 0.25** |
| Level hit rate by `stretch` | non-stretch **n = 0** · stretch **1/4 = 0.25** |
| Fuel, 13:22 | budget **0.0** vs extension **82.5** → err **+82.5** |
| Fuel, 14:42 | budget **0.0** vs extension **38.2** → err **+38.2** |
| Fuel, per day (`track.py`) | **+60.4** — under-read |
| Traversal inside the range | **314.1** both scans |

Record after 7 graded days: **5 right / 6 wrong / 3 no-call**, levels touched
**0.54**.

**Every level published on this day was flagged `stretch`.** There were only
four of them across two scans. See §4 — that is the day's main finding and it is
mechanical, not bad luck.

Session path in one line: high 29521.7 in Asia (05:00), a six-hour slide to
28992.4 at 13:40, a 275.9-point rally to 29268.3 by 15:00, a second leg to the
day low 28954.2 at 18:00, close back at 29088.3.

## 2. What the levels actually did

**13:22 PRE_NY**

- **29020.5 — STRUCTURAL PUT WALL ●●●○○ 0.83bn.** Touched 13:30. Price went
  **28.1 through** it to 28992.4 at 13:40, then rallied **275.9** to 29268.3.
  Graded *"traded both sides — chopped around it"*, but travel up 110.0 against
  travel down 28.1 is a **3.9:1 bounce**, not chop. The brief's own description —
  *"where a multi-day sell-off is defended"* — was correct. At 18:00 price broke
  66 below it and still closed back above. **This level worked, and the grader's
  label understates it.**
  The contradiction inside the same brief: §4's in-range gamma table says
  put-dominant strikes *"amplify… price tends to accelerate THROUGH rather than
  stall. Not a floor."* The single biggest put concentration on the chain floored
  the session. **Second day running** — 08-31's 29263.1 PUT WALL ●●●●● did the
  same thing on a day the model said floors do not hold.
- **29320.5 — STRUCTURAL CALL WALL ●●●●● 1.39bn.** Never reached; post-scan high
  29268.3 stopped **52.2** short. Graded a miss — but the brief said of it
  *"the ceiling for the WEEK/MONTH, not today. Mark it and leave it: it is where
  a multi-day rally runs out of room, not an intraday trigger."* **The level did
  exactly what the brief said it would do and the scoreboard charged it as a
  failure.** Same class of defect as D8.

**14:42 NY_OPEN** — 0/2, both structural, both far.

- **29339.4 CALL WALL** — 71.1 short of the post-scan high.
- **28789.4 PUT WALL** — 164.8 short of the day's low, published 376.6 points
  away on a day with a 0.0 budget.

**Published, reactive, and invisible to every statistic.** The 13:22 brief's
*"Other gamma concentrations in range"* table is not written to
`prediction.levels`, so nothing grades it. Against the tape:

| strike | brief said | what happened |
|---|---|---|
| 29170.5 | amplify, accelerate through, not a floor | traded through both ways — consistent |
| 29120.5 | amplify, not a floor | touched and chopped at 14:15, 15:05–15:15, 17:00 |
| 29070.5 | amplify, not a floor | touched repeatedly all afternoon |
| 28970.5 | amplify, not a floor | **day low 28954.2 is 16.3 below it, then +134 into the close — it floored the day** |
| 28920.5 / 28820.5 | — | never reached |

**4 of 6 touched.** The un-graded table outperformed the graded board (1 of 4),
and the graded board consisted entirely of levels the brief told the trader not
to trade today.

## 3. What was wrong, and why

**The 13:22 call: BEARISH −8, fired 18.8 points above the session's running low.**

Components: gamma **−5** · macro **−3** · rates −1 · structure −1 · vol +1 ·
news +1.

- **The timing, not the direction, is the failure.** At 13:22 the running range
  was 29036.7–29521.7, **126.2% of ADR14 already spent, `remaining_budget` 0.0,
  `fuel_ratio` 2.52.** Price was 0.05×ADR off the low. Post-scan the range grew
  **82.5** points and price traversed **314.1** inside it. The fuel model was
  right about the day; the arrow was noise on top of it.
- **The brief argued with itself.** §2: *"Sweeps tend to keep running rather than
  fail. **Fading is the wrong trade today** — Strategy 2 (go with the move) is
  the right one."* §3: *"**Fading the extremes back into the range is the higher-
  probability side here**, even when the gamma regime favours continuation."*
  Top-down and bottom-up readers get opposite instructions. §3 was right.
- **`gamma −3` was the largest term and rested on the least stable input.** Flip
  29575.6 at 13:22, **29346.9 at 14:42** — **−228.7 points of drift in 80
  minutes** while spot rose +110.5. Drift was **2.1× the price move**. That is
  the fourth large short-interval flip move on record (192pt/2min on 08-24,
  167pt/28min on 08-25, now 228.7pt/80min). H7 evidence, appended.
  The rule is also distance-invariant: **−3 is emitted identically at 520.1
  points below the flip today and at 87.4 on 08-31.**
- **`gamma −2` is the same fact again.** Sign agreement is now **20/20** live
  scans. Removing it takes −8 to −6: still BEARISH, still wrong. **Not
  exculpatory** — it removes false conviction, not the error.
- **`macro −3` (real yield, DFII10) is not an independent observation.**
  The identical −3 with identical text (*"2.42%, up 8bp today and 2bp over 5
  days"*) appears on **08-25, 08-28, 09-01 and 09-02**. DFII10 is a lagged daily
  FRED series, so consecutive days share a value. Any statistic on the macro
  bucket has an **effective n far below the day count**. Flagged so no future
  review reads "the macro term was wrong four times" as four data points.
- **D7 cuts the other way, and this is the honest note.** `news +1` came from the
  `cpi_cool` negation bug — three mis-signed duplicates of a hawkish Barr story,
  +6.6 of spurious bullish weight. **Fixing D7 would have made this wrong call
  more bearish, i.e. worse.** D7 is a correctness fix, not an accuracy fix, and
  should not be sold as one.

**The 14:42 call was CORRECT and the scoreboard flatters it.** Published at
29166.0 into a rally that ran to **29268.3 — 102.3 points of adverse excursion**
— before delivering −212 to the 18:00 low and closing −77.7. Right on the close,
wrong in sequence. The binary grade cannot see this.

**H4 — gamma flip as magnet: two more misses.** 29575.6 vs close 29088.3 =
**487.3**; 29346.9 vs close 29088.3 = **258.6**. Both from **below-flip** scans,
which **kills the 08-31 curiosity** that all hits came from below-flip scans.
Per day the record is now **2 hits / 5 misses**. *Do not use the flip as a
target* stands.

## 4. Change proposals

`track.py`: *"7 of 3 days — threshold met, read the evidence before proposing."*
One proposal follows. Everything else is logged and nothing else is proposed.

### PROPOSED — floor the level board's reach filter, so an exhausted day still publishes in-range levels

**What.** In `brief.py`, `reach` is set by
`"intraday" if abs(price - px) <= budget else "swing"`, and `keep()` retains a
non-structural core level only when `abs(dist) <= budget * 1.75`. **When
`remaining_budget` is 0.0 both tests are unsatisfiable**, so every session
extreme, PDH/PDL, PWH/PWL and gamma flip is pushed into the footnote and only
`kind == "structural"` survives. Proposed: floor the filter's reach at a
fraction of ADR14 — e.g. `max(budget, 0.25 * adr14)` — so the board degrades
gracefully instead of collapsing.

**Evidence.** This is a **deterministic code consequence**, established by
reading the filter, not fitted to outcomes — the same footing on which the
collinear-gamma finding was raised. Empirically, level counts by fuel state:

| scan | fuel | budget | levels published |
|---|---|---|---|
| 08-24 13:45 | EXHAUSTED | 0.0 | **1** |
| 08-25 13:04 | EXHAUSTED | 12.0 | **3** |
| 09-01 13:22 | EXHAUSTED | 0.0 | **2** |
| 09-01 14:42 | EXHAUSTED | 0.0 | **2** |
| all other live scans | LOW_FUEL / MODERATE / ROOM_TO_EXPAND | 88.7–408.7 | **6–22** |

Three distinct trading days, no exceptions. *Stated honestly:* only **08-24 and
09-01 had budget exactly 0.0**; 08-25 is the near-zero case. The overnight
08-25 21:56 scan (1 level) is **excluded** — its budget was corrupt per D1.

**Why it matters.** The collapse happens **precisely on the days the brief tells
the trader the whole opportunity is inside the range.** On 09-01 the board held
two levels, both described by the brief itself as *"not an intraday trigger"*,
while four of the six in-range gamma concentrations — relegated to an un-graded
secondary table — were traded.

**Expected effect.** On the 13:22 scan the board would have carried 29120.5,
29070.5, 28970.5 and the running low 29036.7 instead of two week/month walls.
**All four were traded within the session.**

**Cost, stated up front.** It will *lower* the headline hit rate by publishing
more levels, and it changes what `stretch` means. **H6's non-stretch/stretch
split must be re-based from the day of any change** or the 6-day series becomes
uninterpretable. This is a *publishing* change; no scoring surface is touched.

### NOT PROPOSED — logged only

- **The un-graded in-range gamma table.** Storing it in `prediction.levels` (or a
  parallel block) is the obvious measurement fix, but I have examined it
  directly on **one day**. **Next step before any change: count, across 24 Aug –
  01 Sep, how many published in-range concentrations were touched, against the
  graded board on the same scan.** Filed as a defect candidate alongside M4 and
  D8, not a proposal.
- **The §2/§3 fade contradiction at EXHAUSTED-at-extreme.** It needs short gamma
  *and* exhausted fuel *and* price at an extreme; that is **2 days** (08-24
  13:45, 09-01 13:22) — 08-25 13:04 was above the flip and printed no
  contradiction. **Below threshold. Nothing proposed.**
- **H2 reaches 3 instances and all three point the same way** — see HYPOTHESES.
  The consequence a fix would follow from (H3, capping the score) is not
  supported by 0-right/2-wrong.
- **Nothing is dead weight.** `fuel` and `events` scored 0 again on both scans;
  they are hardcoded narrative rows by design. **Do not remove.**
- **No new data point is needed.** Every failure today came from inputs already
  in the model.
