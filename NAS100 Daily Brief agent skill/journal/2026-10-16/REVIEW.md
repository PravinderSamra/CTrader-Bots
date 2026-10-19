# REVIEW — 2026-10-16 (Friday)

_Reviewed 2026-10-19. One PRE_NY scan (`1248-preny.json`), `is_trading_day: true`,
0 test artefacts. 09-24 quarantined by hand (14th consecutive review; still no
schema `quarantine` field). 2026-10-13 has no directory — Tuesday's scan never
ran; nothing created, back-dated or inferred. No `prediction` block touched. No
scoring, wall or grading code edited._

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | **29903.0 / 30028.6 / 29073.7 / 29191.5** |
| Range · net | **954.9** (2.01x ADR14 475.6) · **−711.5** · close 12.3% up the range |
| Scan | 12:48:42Z @ 29878.0 (bar basis 29879.6) · **BEARISH −6** · `COHERENT_SHORT` high · `MODERATE` |
| Post-scan | high **29889.7** (+10.1) · low 29073.7 (−806.0) · move **−688.1** |
| Direction — post-scan (P-H) | **CORRECT** |
| Direction — day net | **CORRECT** |
| Levels | **10 / 17 touched = 0.59**; distinct touch bars **6 / 17 = 0.35** (inflation 1.67x) |
| Fuel | budget 210.8 → extension **690.1 (3.27x)**, traversal **816.0 (3.87x)**, signed error **+479.3** |

**The session high was set at 05:05Z, 7h43m BEFORE the scan.** Pre-scan range
29763.8–30028.6 = 264.8, which is exactly the `today_range` the fuel block used.
Post-scan price rose **10.1 points** and then fell 806.0. Every grading statement
below that says "never reached" means *the day went the other way*, not *the
level held*.

**P-H, both conventions, 17 graded calls** (one PRE_NY scan per day, ex-09-24,
inside `track.py`'s 45-day window). Reproduced from `review_day`'s own arithmetic;
the n=23 sample reproduces the register's published figures exactly before 10-16
is added.

| basis | right | wrong | rate |
|---|---|---|---|
| post-scan (P-H) | 10 → **11** | 6 | 62.5% → **64.7%** |
| day net | 12 → **13** | 4 | 75.0% → **76.5%** |

**10-16 is NOT a 5th deciding instance.** Both bases are correct; the deciding
set stays **09-11, 09-16, 10-07, 10-15 (n=4)**. The convention is now worth
11.8 points of headline accuracy, not 12.5.

`track.py`: **28 trading days / 31 scans (deduped)**, direction **15 / 7 / 9**
(**14 / 7 / 9** ex-09-24), mean level hit rate 0.5. It no longer prints a literal
`actionable: YES/NO`; the threshold rule was applied by hand.

---

## 2. What the levels actually did

**The upper half of the board was dead on arrival.** Nine rows sat above price
(29938.0 → 30134.8). **None was reachable** — post-scan price never got within
48 points of the nearest one. Worse, **eight of those nine had already been
traded through earlier the same morning**:

| row | dist at scan | pre-scan status | post-scan |
|---|---|---|---|
| 30134.8 GAMMA FLIP | +257 | not reached (missed by 106.2) | never reached, by 245.1 |
| 30030.8 Equal highs ×2 + Asia High | +153 | **missed by 2.2** | never reached |
| **30014.9 CALL WALL ●●●●● + MAX PAIN + shelf ⭐** | **+137** | **exceeded by 13.7 at 05:05Z** | never reached |
| 30008.9 / 30004.2 / 29996.8 / 29938.0 | +131…+60 | all traded through | never reached |

The call wall's note — *"desks must SELL as price rises into it, so rallies
stall. Take profit into it… the strongest ceiling on the board"* — describes
something that **had already happened before the brief was written**. Price
tagged 30028.6, failed, and was 150 points below it by the time the scan ran.
The board had no way to say so. This is the **strongest session-context instance
in the series** (15th session): **10 of 17 rows** lay inside the pre-scan range
29763.8–30028.6.

**Everything that was touched was touched on the way down, and nothing stopped
it.** Ten rows, all from above, all settling below, in 68 minutes (13:10Z →
15:05Z) plus one late pair:

- **29664.9 PUT WALL ●●●●● 1.52bn** — first touch 13:40Z. Next 60 min: only
  **72.5** below, then a bounce to 29749.1. Then it resumed: eventual
  run-through **591.2**, close **473.4 below**. The note — *"BUT today the desks
  are pushing moves along — if it breaks, expect it to speed UP, not bounce.
  Don't buy the break"* — **was right, and it is the best single line in the
  document.** H14's regime-aware wall note earns its keep for the third recorded
  time; run-through census **n=4 → 5**.
- **This also breaks a two-session pattern:** the register recorded "the put-wall
  break marked the day's low for the SECOND consecutive session" (10-07, 10-08).
  Today the break marked the **start** of the move, not the end — 591 points of
  it. The pattern is now 2 of 3 and should not be relied on.
- **29885.3 PD close** (+7) — the gap-fill magnet. Price touched it, made its
  post-scan high 4.4 above, and never saw it again. Correct, and the only level
  on the board that did what its note said *in the direction price actually went*.
- **29763.8 Asia Low (today)**, **29710.2 PD mid**, **29699.5 London High
  (prev-day)**, **29831.7 Asia High (prev-day)**, **29567.0 / 29549.7 prev-day
  Asia/London lows** — all sliced. Seven of ten were graded
  *"traded both sides — chopped around it"*, which on a day with one 806pt
  one-way leg is a tolerance artefact, not a description.

**Levels that are noise and should stop being published as written:**

- **MAX PAIN.** It printed at the same price as the call wall (30014.9) and was
  never within reach post-scan. That is its **6th consecutive distance-confounded
  non-test**, against one success (10-15). It adds a ⭐ to a line it does not
  independently earn.
- **The secondary gamma table (P5).** Of six shelves, **five were never reached
  post-scan**. The one that was — 29614.9, *"dealers are SHORT gamma here, so
  they amplify: price tends to accelerate THROUGH rather than stall. Not a
  floor"* — stopped the decline on first touch and price went **+134.2 in the
  next 60 minutes** before resuming. **1 of 1 graded, and it was wrong.** Still
  graded by no tool.
- **`macro` yield curve (0/32)** and the **`fuel` ratio row (0/32)** have still
  never scored a point.

---

## 3. What was wrong, and why

The direction was right. Five things were wrong, and they are traceable.

**(a) The budget. `fuel +0`, `fuel_ratio 1.24 (normal)`, budget 210.8 → realised
extension 690.1.** The one session in seven labelled *normal pace* produced the
largest range in the 24-day graded sample (2.01x ADR). The register has already
rejected *"hot early pace predicts expansion"*; **10-16 is its mirror — cool
early pace did not predict a quiet day either.** The pre-scan pace carried no
information about the session, in either direction. Error **+479.3**, the
second-largest signed budget error on record (09-21 +569.2 is first), and
`track.py`'s per-day mean moves **+34.3 → +50.2 (n=28)**.

**(b) The fuel block's target advice contradicted the gamma block's, and gamma
won by 480 points.** Section 3, `MODERATE`: *"Continuation is fine to the nearest
pool; **don't plan on a third leg**"* and *"break-even at 1R or 50% of remaining
budget"*. Section 2, `COHERENT_SHORT`: *"Today's ADR can be exceeded — **don't
cap the target too early**."* There were at least three legs and the day ran 2x
ADR. **This is not the fade-vs-continue conflict** — `MODERATE` prose recommends
no fade, so on that axis today is **not an instance**, exactly as flagged. It is
a *third* pairing (fuel vs shape, on target size), after fuel-vs-gamma on
fade-vs-continue and the 10-05 bias-vs-strategy cell. See §4 for a specification.

**(c) The corridor terminus was overshot by 441.2 points — 0.93x ADR.** The
brief: *"DOWNSIDE path: clear. Every options shelf from here to **29514.9**
(363pts, 0.76x ADR) is negative gamma — nothing structural to slow a breakdown.
If it goes, it has room. Do not fade it."* The read was **qualitatively perfect**
and quantitatively useless: price went to 29073.7.

| day | corridor terminus | realised extreme | terminus err | / ADR |
|---|---|---|---|---|
| 10-08 | 30559.6 (398) | low 30568.7 | −9.1 | 0.02x |
| 10-12 | 30643.1 (200) | low 30634.7 | +8.4 | 0.02x |
| 10-14 | 29941.8 (464) | low 29877.9 | +63.9 | 0.15x |
| 10-15 | 29977.6 (339) | high 29996.8 | +19.2 | 0.04x |
| **10-16** | **29514.9 (363)** | **low 29073.7** | **+441.2** | **0.93x** |

**And there is a mechanism, read off the code, not inferred.**
`brief.py:520` sets `corridor_end = span[-1]` where `span` is *every shelf within
1.2x ADR on that side*. **The terminus is the far end of the shelf list, not a
barrier.** Its previous 4-for-4 accuracy was a property of the shelf grid
happening to run out near where price stopped; when price kept going, the
quantity had nothing to say. The 10-15 proposal to publish the terminus as a
range forecast should **not** be actioned as written.

**(d) The named brake was on the wrong side of the market.** *"UPSIDE path: has
friction. Expect a stall at 30014.9 (137pts away)"* on a day that went down 806.
H23 instance **13**; census stays **9 sliced / 1 capped**, **never-reached 2 → 3**.

**(e) Two stale FRED rows voted against the correct call.** `macro +3` DFII10 and
`macro +1` DGS10 both resolve to observation date **2026-10-14**, in a document
headed *"today"*; the age warning printed on DFII10 and not on DGS10 — **H18/P1
instance 20, duplication 25 of 25**. `macro −2` **HY OAS** was the only macro row
pointing the way the day went, and **it rendered no observation date for the 12th
consecutive session**.

*The component trace, in full:* gamma **−5** (flip −3, week GEX −2) was the
engine's correct and dominant signal; `structure −3` (below the entire prior-week
range) was correct and is H10's `−3` branch, **7th firing, now 2-for-7**, with
PWL 30568.7 **690.7 away and never approached** — the proposed reclaim term would
again have changed nothing. Against them, `macro +4` from the stale pair and
`vol +1` (VIX9D/VIX 0.873 → *"calm, mean-reversion favoured, mild upward drift"*)
on a day that realised 2x ADR. **Suppressing the stale pair takes −6 → −10, i.e.
a correct call made bigger** — the age gate's **3rd** helping instance against 2
hurting (10-07, 10-15). A 3–2 split is not evidence; **the accuracy case stays
retracted.**

---

## 4. Change proposals — only material ones

**No new ID is allocated by this review. Next free remains H27 · D27 · P-I.**
Every item below is an existing entry taking a data point, or a correction to a
live proposal. Nothing here proposes a score change.

### Material: the 10-15 corridor-terminus proposal should not be actioned as written

**Evidence:** 5 sessions (10-08, 10-12, 10-14, 10-15, 10-16), table in §3(c),
plus the code reading of `brief.py:520`. **Expected effect:** prevents shipping a
range forecast whose accuracy was an artefact of where the shelf list ends.
**Replacement is not proposed** — the right move is to keep measuring the
terminus for five more sessions and to publish it, if ever, as *"the last
positioning we can see"*, never as *"how far it can go"*. This is a change to a
proposal, not to the model.

### Below threshold — appended, nothing proposed

- **H23 force-ranking fix — the unfalsifiability risk is now real, n=2.** On
  10-15 the brake was the only positive-sign shelf in range, so distance-first
  and force-first *could not* differ. On 10-16 they **agreed on a genuine
  choice**: four positive-sign shelves above price (30014.9 / 30064.9 / 30114.9 /
  30164.9) and the nearest, **30014.9, was also the heaviest (1.64bn > 1.02 >
  0.72 > 0.38)**. The proposed fix would have published the same level twice
  running. *(If the fix is instead read as ranking all in-range shelves by force
  ignoring sign, it would have named 29914.9 at +37 — also never reached. Either
  way the output is unchanged.)* **Pre-registered now: if a third consecutive
  session produces agreement, the fix is unfalsifiable in practice and H23's
  ranking branch should be closed rather than carried.**
- **H26 — the magnitude claim WEAKENS on 10-16, which the headline must not
  hide.** n=23 → **24 days**. The 6–9 bucket goes **5/6 → 6/7**. But a **−6**
  delivered **1.447x ADR** of post-scan movement — **the largest in the entire
  sample**, ahead of 10-14's −18 at 1.126x. So: bucket means stay monotonic
  (0.181 / 0.236 / **0.545** / 0.783) while the rank correlation **falls**.
  Spearman(|score|, |post-scan|/ADR) **+0.612 → +0.577**; signed-direction
  **+0.165 → +0.157**; range/ADR +0.196 → **+0.198**. The 10-15 entry's
  *"magnitude strengthens"* does not survive one more session. H26's proposal
  (print the base rate, scale the range language, change no score) stands at 24
  sessions but on a thinner correlation than the register currently states.
- **The two-opposite-instructions census — a clean specification, offered, not
  scored.** The suspension is correct and is **not lifted**. The reason the
  column and the claim came apart is that **three different conflicts have been
  counted as one**: (i) fuel vs gamma on *fade vs continue* (the registered cell,
  `LOW_FUEL`/`EXHAUSTED` below the flip); (ii) bias vs strategy block (10-05,
  n=1); (iii) **fuel vs shape on target size** (10-16, and arguably 10-05's
  *"don't plan on a third leg"*). **Proposed specification, to be re-derived from
  scratch before any score is quoted:** one column per axis, each graded by a
  rule fixed in advance — axis (i) by whether fading the first post-scan sweep of
  a pre-scan extreme was profitable at the next published level; axis (iii) by
  whether realised post-scan traversal exceeded the budget-implied cap. **No
  score is quoted for any axis, including today's.** On axis (iii) 10-16 is an
  instance and gamma was right; on axis (i) it is **not** an instance.
- **P4 / H1 — n=28 days, one new data point, statistic NOT re-derived.** 10-16
  error **+479.3** (budget 210.8, extension 690.1). `track.py` per-day mean
  **+34.3 → +50.2**; per-scan +51.2 (n=31). The standing measured claim — MAE
  116.1 vs leave-one-out constant 98.3 (n=19); ex-outlier 90.9 vs 75.5 — is
  **not** re-derived and is **not** weakened by a day that makes the budget look
  worse. Claim remains **"no usable skill"**, not "inversely predictive". The
  multiplier branch stays closed.
- **M6 — session 26, and the artefact at its largest absolute scale.** Said
  explicitly: **M6's magnitude scales with how far the day travelled**, and
  10-16 travelled 954.9 = 2.01x ADR. All **10 of 10** touched rows understate;
  mean understatement **4.5x**, worst **8.2x**.

  | level | review_day `travel_down` | actual excursion below | ratio |
  |---|---|---|---|
  | 29664.9 PUT WALL | 72.5 | **591.2** | **8.2x** |
  | 29699.5 London High (pd) | 107.1 | 625.8 | 5.8x |
  | 29710.2 PD mid | 117.8 | 636.5 | 5.4x |
  | 29848.9 Equal lows ×3 | 189.2 | 775.2 | 4.1x |
  | 29856.4 / 29763.8 / 29885.3 / 29831.7 / 29567.0 / 29549.7 | 196.7 / 171.4 / 225.6 / 239.3 / 152.2 / 134.9 | 782.7 / 690.1 / 811.6 / 758.0 / 493.3 / 476.0 | 4.0 / 4.0 / 3.6 / 3.2 / 3.2 / 3.5x |

  And the wording inversion fires **3 of 3** again: 29885.3, 29763.8 and
  **29664.9** are all reported as *"held as resistance"* — three levels price
  collapsed through by 591 to 812 points.
- **Session-context field — 15th session, and the strongest instance by
  consequence.** 10 of 17 rows already traded pre-scan, including the **CALL
  WALL / MAX PAIN ⭐ at 30014.9, exceeded 7h43m before the brief printed it as a
  live ceiling.** Already PROPOSED; this is evidence, not a new proposal.
- **P-B(b) — 15th session.** `merge_tol = max(3.0, 475.6 × 0.008) = 3.805` vs
  `TOUCH_TOL = 8.0`. **Four published pairs sit in the structurally guaranteed
  3.805–8.0 window** — (30014.9, 30008.9) 6.0 · (30008.9, 30004.2) 4.7 ·
  (30004.2, 29996.8) 7.4 · (29856.4, 29848.9) 7.5 — the most in the series. **One
  fired**: 29856.4 and 29848.9 both graded touched at bar 178. Published rate
  **0.59**, distinct-event rate **0.35**, **inflation 1.67x**. No tolerance-only
  touches (all ten have positive travel both ways). Proposal unchanged.
- **P-G — instances #22 and #23.** Two prev-day session-extreme rows sit *below*
  price and still print the above-side note: **29831.7 Asia High (prev-day)** at
  −46 and **29699.5 London High (prev-day)** at −178, both *"the next session
  usually runs the stops above it"* — stops that were behind the market. The
  today-session rows (29856.4, 29763.8, 30004.2, 30030.8) were all correctly
  sided, which is the point: the defect is kind-driven, not side-driven.
- **D23 — 13th residual.** Board **+14.9** vs section-7 **−24.5** matched to feed
  time 11:59Z. Gap **+39.4**; CFD move (11:55Z bar open 29872.2 → scan 29878.0) =
  **+5.8**; **residual +33.6** — the third-smallest in the series
  (`+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
  −68.0 / +165.0 / +438.2 / **+33.6**`). The two conversions **disagree in sign**
  for the third consecutive session (10-12, 10-15, 10-16). Damage none —
  research-only, no volume had traded.
- **D25 — 26th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, three lines under *"⚠️ No volume has traded yet today"*.
  Damage none.
- **D26 — reporting gap, not data loss, and it widened.** `track.py` sees **28
  trading days / 31 scans**; on disk: **35** day directories, **65** scan JSONs,
  **30** days with a PRE_NY scan, **29** with a `REVIEW.md` (30 after this file),
  **26** with both. The four August PRE_NY days are intact and invisible only to
  the 45-day bar window — they are also the reason `track.py`'s per-day mean and
  this review's own n=24 H26 sample have different denominators.
- **H18 / P1 — instance 20, duplication 25 of 25.** See §3(e). HY OAS renders no
  observation date for the **12th** consecutive session, and on 10-16 it was the
  only macro row on the right side of the day. **Correction carried forward: HY
  OAS is not dead weight and never was — 25 of 32 PRE_NY trading-day scans
  ex-09-24.**
- **Dead-weight audit, refreshed to n=32** PRE_NY `is_trading_day` scans
  (09-24 excluded by hand): yield curve **0/32**, `fuel` ratio row **0/32**,
  `events` **0/13 present**, VVIX 3/32, DXY 4/32, NFCI 5/32, WALCL/RRP 6/32,
  HY OAS **25/32**. The narrowed standing proposal (drop the yield-curve row and
  WALCL/RRP) is unchanged and still not actioned.
- **H22 — n=10.** Week net GEX −5.172 → *"expansion likely"* → **2.01x ADR**. The
  row was right. Nothing proposed.
- **H19 — mandated per-scan record.** 130 headlines / 10 feeds → 53 relevant →
  **0 auto-scored**. Coverage **0.0%**, equal-lowest in the record.
  **A D18-shaped mis-tag with no damage:** *"S&P 500 Correction Risk Grows as
  Index Rally Lacks Broad Participation"* is tagged **`[risk_on]`**. It scored
  nothing, so **D18 stays at 13 headline instances / 7 trading days** and this is
  recorded as a tagger observation only.
- **H8 — ANSWERED-POSITIVE at its pre-registered 10 observations; NOT reopened.**
  Recorded as post-closure data only: straddle 279 → band **29641..30115**, close
  **29191.5 OUTSIDE by 449.5**. For context on the same page, the **VXN-implied
  range 430.8 under-read the realised 954.9 by 524.1 (realised 2.22x)** — both
  forward range measures failed on the same day, the straddle band by less.
- **D17 — already logged, not double-counted.** The CBOE 429 on the 10-16 scan
  and its attempt-1 recovery were **already recorded as a D17 success in the
  register's 2026-10-16 block** (written while grading 10-15). No second entry is
  made for the same event.
- **No instance:** **H4** (flip never approached within 245.1) · **H7** (no
  overnight scan) · **H2** (`MODERATE`, outside the cell) · **H20**
  (CLOSED-NEGATIVE, and no High/Medium events) · **D21** (`gamma +0`, price 61%
  up the band — neither branch) · **D24** (section 5 forward-only, no release
  between open and scan identified) · **P-F** (price inside the prior-day range)
  · **H17** (post-scan move = 72.1% of session range, far outside the deadband).

### Is a new data point needed?

**No.** Every miss today is already named by an open entry. The one field that
would have changed the document — *"price has already traded this level today"* —
is the **session-context field**, proposed on 09-30 and still not actioned. It is
free (the board already holds the pre-scan range) and reliable (it is arithmetic
on data the brief already prints). Nothing new should be added before it is.

### Carried forward from today's 10-19 scan — NOT graded here

- **Board offset: 14.9 (10-16) then −3.9 (10-19).** The time-trend explanation
  was already substantively dead; these are two more points against it. Fitted
  through 10-14 the trend predicted 32.4 for 10-16 (actual 14.9) and ~34 for
  10-19 (actual −3.9) — **three consecutive out-of-sample misses, the last two
  both low.** Mechanism recorded as **unexplained**; nothing proposed.
- **Realised-close-basis log, observation 3 of 10.** From the 10-19 brief's own
  arithmetic, NDX cash close 10-16 = implied 29563.5 − roll (+376.0) = **29187.5**;
  CFD close **29191.5**; **realised basis +4.0**; scan offset +14.9; **gap +10.9**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
  | 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
  | **10-16** | **+14.9** | **29187.5** | **29191.5** | **+4.0** | **+10.9** | **+376.0** |

  **This breaks the "same shape" reading at n=3**, and it already cuts against
  the pre-registered scoping fix: **the largest |roll| in the log (376.0)
  produced the smallest gap (10.9)**. Re-test still at n=10. **Nothing proposed.**
- **⚠️ A defect in the register's own offset analysis, found today.** The
  scratchpad extractor behind the 10-14/10-15/10-16 offset entries parses the
  roll with `NQ futures move \((-?[\d.]+)\)`, which **cannot match a positive
  roll** — the brief prints `(+376.0)`. **15 of 29 days have up-rolls and every
  one of them was silently recorded as `None`.** The published claim
  *"r(offset, |roll|) = +0.039 within down-roll days"* is correctly scoped, but
  the down-roll sample was never a choice. **Any future |roll| regression must be
  rebuilt with a sign-tolerant parse.** No model code is affected.
- **`expiry_shape: PIN_THEN_EXPAND` is NEW — confirmed against the whole
  journal.** Census of all 65 scan JSONs: `COHERENT_LONG` 27 · `COHERENT_SHORT`
  18 · `FRONT_FLAT_BACK_SHORT` 11 · `FRONT_FLAT_BACK_LONG` 6 ·
  `SPIKE_THEN_REVERT` 2 · **`PIN_THEN_EXPAND` 1 (2026-10-19, first ever)**.

  **Pre-registered test, written before the outcome is known** (same pattern as
  the 10-05 `SPIKE_THEN_REVERT` pre-registration, which took no ID, so this takes
  no ID either). The shape makes a **timing** claim, not a direction claim:
  *"Chop early, resolve late… breakouts will fail while the pin holds. From
  roughly 13:00 ET the pin weakens."*

  1. **Split the session at 17:00 UTC (13:00 ET).** Measure range and absolute
     net move in 13:30–17:00 UTC (pre) and 17:00–20:55 UTC (post).
  2. **Confirmed if** post-13:00 ET range **>** pre-13:00 ET range **and** the
     session extreme in the direction of the day's close is made **after**
     17:00 UTC.
  3. **Falsified if** the pre-13:00 ET window holds the larger range, **or** if
     the day's high and low are both set before 17:00 UTC.
  4. **Secondary, for the "breakouts will fail" half:** count post-scan sweeps of
     the pre-scan high/low before 17:00 UTC and whether price closed back inside
     within 30 minutes. ≥1 sweep that reverses = supports; a sweep that runs =
     against.
  5. **Threshold: 3 `PIN_THEN_EXPAND` days.** On present frequency that is many
     months away. **Nothing may be concluded from 10-19 alone**, and the first
     observation is to be recorded without a verdict attached.

---

### Journal hygiene

One scan file for 10-16 (`1248-preny.json` + `.md`), `is_trading_day: true`,
**0 test artefacts** for the day (6 across the record, excluded by `track.py`).
**09-24 quarantined by hand — 14th consecutive review to carry it**; the 09-29
proposal for a schema `quarantine` field is reaffirmed, because `track.py` still
keeps it inside every statistic it prints (direction **15 / 7 / 9** becomes
**14 / 7 / 9** once 09-24 is removed). **2026-10-13 has no journal directory** —
the scheduled scan never ran; nothing was created, back-dated or inferred.
**2026-10-19 is on disk, unfinished (180 bars), correctly held back by `track.py`
and excluded from every statistic above.** 09-09 and 09-25 still have no
`REVIEW.md` and none was created. No fabricated or backfilled entries found. No
`prediction` block was touched. No scoring, wall or grading code was edited.
**No new ID allocated. Next free: H27 · D27 · P-I.**
