# REVIEW — 2026-10-26 (Monday)

Graded 2026-10-27 from `review_day.py 2026-10-26 --json` (one PRE_NY scan,
12:52:57Z, `is_trading_day: true`, 276 bars, 0 test artefacts) and `track.py`
(30 trading days / 31 scans visible). 09-24 excluded by hand everywhere below.
No `prediction` block touched; no scoring, wall or grading code edited.

---

## 0. THE PRE-REGISTERED `PIN_THEN_EXPAND` TEST — n=3 REACHED, **VERDICT: FALSIFIED (3 of 3)**

Clauses 1–4 run **exactly as written in the 2026-10-19 block**, unrevised, on
10-26's bars. Nothing was re-scoped after seeing the data.

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **399.0** | **251.0** | 29411.0 @15:00 | 29012.0 @13:30 |
| **post** 17:00–20:55Z | **128.3** | 26.7 | 29396.0 @17:20 | 29267.7 @20:00 |

- **Clause 2 (CONFIRM)** fails on both limbs. Post range **128.3 < 399.0**. The
  day closed **up** (+148.3), so the extreme on the closing side is the high
  **29411.0 @ 15:00Z — 2h before the split**.
- **Clause 3 (FALSIFY)** fires on **both** limbs: the pre window holds the larger
  range, **and** both session extremes (high 15:00Z, low 08:10Z) were set before
  17:00Z. **FALSIFIED.**
- **Clause 4 (secondary, "breakouts will fail")**: the pre-scan high **29194.8**
  was swept at **14:15Z** (+26.5) and closes returned inside within 30 min
  (14:20 29186.0 / 14:25 29190.9 / 14:30 29160.7) — **supports it by the letter**
  — and then the same level was exceeded by **+216.2** inside the same pre-17:00
  window. **The breakout ran.** Pre-scan low never swept (146.5 below).

**The three-observation record, same rules each time:**

| obs | day | pre range | post range | verdict | failing clause |
|---|---|---|---|---|---|
| 1 | 10-19 | 329.7 | 139.5 | FALSIFIED | 3, both limbs |
| 2 | 10-21 | 329.5 | 226.1 | FALSIFIED | 3, limb 1 |
| 3 | **10-26** | **399.0** | **128.3** | **FALSIFIED** | **3, both limbs** |

Three for three, on the same clause, with the same signature: the pre-13:00 ET
window held both the larger **range** and the larger **directional move**
(251.0 / 194.4 / 14.3 pre vs 26.7 / 51.4 / 48.7 post), and in two of three the
post window gave points **back**. Clause 5's threshold is met, the test is
closed, and the shape's **timing claim is falsified**. The secondary limb is
0 for 3 on substance.

**User-facing consequence.** The prose at `gex_levels.py:509–512` —
*"**Chop early, resolve late.** Be patient in the morning — breakouts will fail
while the pin holds. From roughly 13:00 ET the pin weakens and the move that has
been building gets released. **Save your risk for the afternoon.**"* — told a
reader on 10-26 to sit out the window that produced **251 points in one
direction** and to commit risk to the window that gave **26.7 back**. It should
be **withdrawn**, not inverted (see §4, **P-I**).

10-27's `PIN_THEN_EXPAND` is a **4th** firing and is **not** part of this test.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 29153.6 / **29411.0** / **28865.5** / 29301.9 |
| Range · net | **545.5** (1.000× ADR14 545.4) · **+148.3** |
| Post-scan H / L / range / move | 29411.0 @15:00Z / 29012.0 @13:30Z / 399.0 / **+168.6** |
| Call | **BEARISH −6**, direction −1 → **WRONG** (post-scan basis and day-net basis agree) |
| Levels | **7 of 17 touched = 0.41** published · **5 of 15 = 0.33** distinct |
| Fuel | budget **216.1** vs extension **216.2** → err **+0.1**, `about right` |
| Traversal vs budget | 399.0 / 216.1 = **1.85×** |
| Record, 09-24 excluded (post-scan basis) | **13 right / 10 wrong / 7 no-call** over 30 days |

The fuel error of **+0.1** is the smallest in the 30-day series by a factor of
60 (next smallest 6.4 on 10-12). It is a coincidence and is reported as one: the
per-day mean error moved 53.9 → **52.1** and still has a 569-point and a
−216-point member.

---

## 2. What the levels actually did

**Touched (7).**

- **29329.5 CALL WALL ●●●○○ 0.48bn + options shelf ⭐ (+192)** — the one level
  the brief staked the upside on (*"desks must SELL as price rises into it, so
  rallies stall. Take profit into it."*). **Split verdict, and the brief's
  reader got the worse half first.** On the approach price went **81.5 through
  it** (0.15× ADR) to the session high — a slice, not a stall. It only became a
  ceiling from 19:40Z, holding 75 min with a worst excursion of +12.6 and
  closing 27.6 below. A wall that is sliced on the 15:00 rally and caps the
  20:00 drift did not do the job the prose sold.
- **29155.4 PDH + NY High ⭐ (+17)** and **29148.9 Asia High (+11)** — the brief
  printed the S1 recipe: *"Sweep it, wait for a lower high on the 1m, then CISD
  = short."* Price broke **down** through it on first touch, reclaimed it, and
  then **held it as SUPPORT for 405 minutes** (worst −19.6 / −13.1). The level
  worked; the published instruction was the wrong side of it. The short that
  recipe asks for was 255.6 points offside at the high.
- **29200.2 Equal highs ×2 (+62)** and **29194.8 London High today (+57)** —
  *"prime S1 sweep trigger"*. The sweep happened at 14:15Z and **ran**: +216.2
  beyond, no reversal. Graded `lost` on a close **101.7 / 107.1 above** them
  (see §3, M6).
- **29109.3 / 29073.9 London & Asia High (prev-day)** — graded *"broke DOWN
  through it — lost by 51.5 / 60.4pts"* on a day that closed **192.6 and 228.0
  points ABOVE** them. The verdict is an artefact, not a reading.

**Never reached (10), and two of them are the standing problem.**

- **STRUCTURAL CALL WALL 29729.5 (+592)** — published again, **0 gradeable
  touches in its entire history** (P3/H6). This is the clearest "stop publishing
  it" candidate on the board and the evidence is now many sessions deep, not one.
- **MAX PAIN 29449.5 (+312)** — missed by 38.5. **10th consecutive
  distance-confounded non-test** of the *"weak on a Monday, strong by
  Thursday/Friday"* qualifier. Here the brief's own qualifier and the day agree,
  so nothing is learned either way.
- **GAMMA FLIP 29489.2 (+351)** — missed by 78.2; no H4 test.
- Every downside level (PD close −139 through PUT WALL −408) went untested. The
  post-scan low **29012.0** stopped **12.8 above PD close 28999.2** — inside
  0.023× ADR — and the day reversed **+399** off it. `TOUCH_TOL = 8.0` files it
  as *"never reached"*. **Second instance of the 10-23 pattern**: the level that
  actually turned the day is the one the grader cannot see. The put wall was
  408 away and was never testable, as expected.

---

## 3. What was wrong, and why

**The score, decomposed against `inputs.bias_components`:**
`gamma −5 · vol −2 · macro +2 · structure +2 · news −2 · breadth −1 = −6`.

**(a) `gamma −5` carried the call, and the same scan held a positive gamma
number it never consumed.** `gamma −3` reads *"below flip 29489.2 by 351.2pts —
SHORT gamma, dealers amplify: downside accelerates, rallies unstable"* and
`gamma −2` reads the **weekly** net GEX of −2.141 as *"expansion likely"*. Short
gamma is a statement about **amplitude**, not sign: the amplification arrived and
pointed **up**, +399 off the post-scan low. Meanwhile `near_expiry_0_2dte` was
**+0.42**, positive, and the shape engine used precisely that number to emit
`PIN_THEN_EXPAND`. **One scan, two gamma signs, and only the negative one was
allowed to vote on direction.** The distance-below-flip branch has no term that
distinguishes "falling away from the flip" from "grinding back toward it", and
on 10-26 price spent the session closing the 351-point gap (post-scan high left
only 78.2).

**(b) `structure +2` was the only block that called the day, and it was
outvoted 5-to-2 by one correlated pair.** *"in-reach unmitigated pools: 1 above
/ 0 below — draw higher"* (+1) is exactly what happened: the pool above was run
at 14:15Z and never given back. **H27 instance 2, and it is stronger than
10-23's.** The two correlated pairs carry the whole score — `vol`(−2) ↔
`breadth`(−1) = **−3**, `gamma`(−5) ↔ `structure`(+2) = **−3** — and the
independent remainder (`rates 0` + `macro +2` + `fuel 0` + `news −2` +
`events 0`) is **exactly 0**. A −6 that the §1 *"Driven by:"* line renders as
six independent contributors is, on the measured correlation structure, two.
Per H27's own entry the collapse rule was pre-registered, run, and **hurts**
(59.1% → 52.6%), so **nothing is proposed**.

**(c) `news −2`: the printed reason is false, the score was not the margin.**
Graded separately as requested. *"Apple stock rally and Nvidia sell-off tighten
race for world's most valuable company"* was tagged **[hawkish] → "Hawkish
repricing -> bearish long-duration tech"**. The match is `news_scorer.py:71`,
`\b(hawkish|rate hike|raise rates|**tighten**|higher for longer|…)\b`, firing on
**"tighten race"** — a transitive verb whose object is a corporate league table.
**This is D9 ("the tagger reads a keyword without its subject"), instance 3, and
the first where the matched token is a verb with a non-monetary object.**
*Score:* the other headline (*"US Fed Rate Hike December Expected"*) is a
legitimate hawkish tag, so `news` would be −1 not −2 on a corrected read; at
`news 0` the score is **−4, still BEARISH**. **The defect did not change the
call and is not the margin.** Coverage: 125 headlines → 42 relevant → **2
auto-scored = 1.6% of raw, 4.8% of relevant**, with 40 left for judgement.

**(d) `macro +2` was right and is built on a flagged stale pair.** `DFII10 +3`
(obs 2026-10-22, 2 business days old, ⚠️ printed) and `DGS10 +1` (same
10-21→10-22 window, no ⚠️) are the same instrument twice — **H18/P1 instance 26,
duplication 31 of 31** — and this time the stale pair pointed the **right** way
and was still outvoted. `HY OAS −2` (3.4%, +17bp/5d, *"bonds are usually right
first"*) was **wrong on the day**; stocks rallied 399 points off the low.
*Correction to the task brief:* HY OAS scored **−2 on 10-26**, not 0 — the
"+2bp, scored 0" reading belongs to the **10-27** scan (where it prints +7bp and
scores 0).

**(e) `breadth −1` on a 0.27% spread.** *"NDX −0.00% vs ES +0.27% — tech
lagging, rotation out of tech"*. A 27bp overnight gap on a flat NDX produced a
scoring point in the direction that lost. No deadband. One data point, logged.

**M6 — session 32, 4 of 7 verdicts inverted, and the driver on this session is
nameable (which is not the same as the general driver being known).** The four
rows 29200.2 / 29194.8 / 29109.3 / 29073.9 are all printed *"broke DOWN through
it — lost"* with `settled_side: "above"` on a close 101.7–228.0 points above
them. Measured from the bars: in **every one of the four**, the worst excursion
falls on the **bar immediately after `last_far`** (settled 13:55 → low 14:00;
14:05 → 14:10; 14:30 → 14:35 ×2). `settled_read` sets `last_far` from a **close**
and then measures `worst` over a window that **begins with the recoil of the very
bar that crossed the level**, against a fixed `SETTLE_TOL = 25.0` — 0.046× ADR on
this session. So the level is failed by the wick of its own reclaim bar. **This
is the `settled_read` origin defect already on record (≈ lines 5535 / 6061 /
7054) and is not reopened.** Both previously-offered general explanations stay
dead: travel-scaling failed four consecutive sessions, window placement failed on
7 of 7 rows at session 31. **For the series as a whole the driver remains
unknown**; the above is this session's mechanism, not a replacement theory.

---

## 4. Change proposals

### PROPOSED — **P-I**: withdraw the `PIN_THEN_EXPAND` timing prose (`gex_levels.py:509–512`)

**Change.** Delete the `do` string for `PIN_THEN_EXPAND` and leave the `what`
block (the gamma configuration) standing. Replace with no timing instruction.
**Do not invert it to "resolve early"** — that would be fitting a rule on the
three observations that killed the first one.

**Evidence.** The pre-registered test, written before any outcome was known,
run unrevised on all three qualifying sessions: **FALSIFIED 3 of 3, on the same
clause**, with the pre-13:00 ET window holding the larger range every time
(329.7/139.5 · 329.5/226.1 · 399.0/128.3) and the larger directional move every
time. The *"breakouts will fail"* limb is **0 of 3** on substance. This is the
threshold the register set for itself, met exactly, with no re-scoping.

**Expected effect.** Removes the only instruction in the brief that is
0-for-3 against its own pre-registered test. On 10-26 it cost a reader the
09:30–12:00 ET window (251 points, one direction) in exchange for an afternoon
that retraced 26.7. No scoring changes; no level changes; the shape label and
its mechanical description survive.

### Everything else — appended, nothing proposed

Threshold not met, or met and resolving to no model change:

- **P-H** — 10-26 is **WRONG on both bases** (post-scan +168.6, day net +148.3),
  so it is **not** a 6th deciding instance. Post-scan **13/23 = 56.5%**, day-net
  **14/23 = 60.9%**; deciding set stays **n=5**, convention cost **4.5 → 4.3**.
- **H26** — a **6–9 bucket** instance and a **miss**: 6/8 = 75.0% → **6/9 =
  66.7%**. |post|/ADR **0.309**, range/ADR **1.000**. The ≥10 bucket is
  untouched at **3/7 = 42.9%**. The register's own warning that published 6–9
  figures have drifted is carried, not papered over.
- **H27** — observation 2; the two correlated pairs carry **−6 of −6** with an
  independent remainder of **exactly 0** (see §3b). Weight limb stays
  ANSWERED-NEGATIVE; **no fix re-proposed**.
- **H2** — `MODERATE` fuel, so a **clean non-instance**; census stays 6–2 / 8–0.
  Also a **control** for the two-opposite-instructions cell: §2 (*"Fading is the
  wrong trade today"*) and §3 (*"Do not fade it"*) agree, which localises that
  contradiction to the LOW_FUEL/EXHAUSTED branch for a second session.
- **H1 / P4** — **n=30**, error **+0.1**, the smallest in the record; per-day
  mean **53.9 → 52.1**. This is now the **fifth** value published under one
  series name. **Still flagged, still not averaged.**
- **H10** — price **inside** the prior-week range, so the −3 branch did **not**
  fire: a **clean control**, as predicted. The branch stays **2-for-8** and the
  proximity gap stays unaddressed at 3 instances.
- **`gamma +2` bottom-of-band — the carry-forward note is WRONG and the count is
  corrected.** 10-26's band row reads `gamma +0 — price mid-band
  (28729.5–29329.5), 68% up the range`. **The +2 branch did not fire on 10-26.**
  It did not fire on 10-27 either (`+0`, 67% up the band). The branch stays at
  **6 firings, census 3–3, prose contradiction 6 of 6, zero sign changes**. The
  "7th firing" recorded in the 2026-10-26 carry-forward block is retracted.
- **`TOUCH_TOL = 8.0`** — **2nd instance** of the 10-23 pattern: post-scan low
  **12.8** above PD close (0.023× ADR) with a **+399** reversal off it, filed
  *"never reached"*. The put wall at −408 was never testable, as anticipated.
- **D7** — **clean control on both limbs, 2nd consecutive.** Footnote held **2
  rows against a cap of 6**; nothing truncated, and with both rows above price
  the price-ordering defect could not bite. Separately, the contract-count vs
  dollar-gamma superlative recurs (PUT WALL ●●●●● 0.77bn / "93k contracts" vs
  CALL WALL ●●●○○ 0.48bn / "5k contracts") — **5th instance, ranks agree, no
  damage**.
- **D23 / realised basis — observation 9.** Section 7 did **not** render on
  10-26 (sections 1–6 only). **No residual is inferred**, for the third
  consecutive session. **D25 stays interrupted at 29.**
- **D26** — `track.py` now sees **30 days / 31 scans**, up from 29/30. **The
  held-back set did NOT rotate this session**: 10-26 entered and nothing left.
  On disk there are **39 finished trading days** (08-24 … 10-26, 10-27 held back
  at 185 bars); **9 of them (08-24 … 09-11) are invisible** past the 45-day bar
  window.
- **D27** — the gexbot **HTTP 401 on `/v2/NDX/classic/gex_full`** recurred on the
  **10-27** scan: **4th consecutive day**. Volume-weighted ladder absent again;
  D25's false sentence remains suppressed rather than fixed. **Nothing
  proposed** — no credential change, no retry policy.
- **H23** — upside named brake **29329.5 CAPPED** (settled read, 75 min, worst
  +12.6) though **sliced by 81.5** on the approach; downside clear-path read
  (*"clear to 28529.5, 608pts"*) **never tested** (post-scan low 29012.0).
  Census +1 cap / +1 never-reached on the last published 11 / 3 / 3.
- **P5** — secondary table, 3 of 6 rows reachable post-scan. **29179.5** *"expect
  a stall"* → price ran straight through it to +231 more: **WRONG**. **29029.5**
  *"amplify, accelerate THROUGH, not a floor"* → the post-scan low formed 17.5
  below it and reversed +399: **WRONG**. **29379.5** *"expect a stall"* → high
  29411.0, exceeded by 31.5 then turned: **marginally right**. **1 of 3.**
- **P-B(b)** — 21st session. Two pairs inside `TOUCH_TOL` published as four rows
  (29200.2/29194.8 at 5.4; 29155.4/29148.9 at 6.5), **both pairs touched on the
  same bar**. Hit rate **0.41 published vs 0.33 distinct — inflation 1.24×**.
- **P-E / P-E(b)** — the call wall is a **split** instance again: sliced +81.5 on
  the main rally, capped on the settled read. The shelf stacked at the same price
  did not separate the two.
- **P-G** — the merged rows **29155.4 "PDH + NY High"** and **28820.4 "PDL + PWL
  + NY Low"** each print one kind's note for a 2- and 3-way confluence;
  instances #31/#32.
- **P3 / H6** — structural call wall published again at +592, **0 gradeable
  touches ever**.
- **P-F** — **not** a treatment instance (price 29138.0 sat **inside** the PD
  range, 17.4 below PDH). Logged as an **inside-control** with error **+0.1**,
  which is opposite in character to the 10-23 inside-control (−215.8). The
  control is **not** re-derived.
- **H22** — week net GEX −2.141 → *"expansion likely"*; realised range
  **1.000× ADR exactly**. That is the definitional boundary, so the label is
  **indeterminate** and **n is not advanced** rather than scored arbitrarily.
- **H8** — close 29301.9 sits **inside** the published straddle band
  28811–29465. Post-closure observation.
- **Session-context field** — 21st session. Pre-scan range **28865.5–29194.8**
  under *"New trading day… everything below is fresh."* **9 of 17** marked rows
  lie inside it; **13 of 25** counting the footnote and secondary table.
- **Dead-weight audit** — `events` scored **0 on all four rows** again; `rates`
  **0 on both**; NFCI, WALCL/RRP and the yield curve **0** again. Unchanged;
  the narrowed standing proposal is not re-stated.
- **No instance:** H4 (flip 78.2 above the post-scan high) · H7 (no overnight
  scan) · H11 · H12/H13 (volume ladder lost to the 401) · H14 (put wall never
  approached) · H17 (post-scan 30.9% of session range, far outside the 5%
  deadband; stays 2 of 3) · H20 (CLOSED-NEGATIVE) · D24 (`event_gate: null`
  correct, four earnings all forward) · the gamma-outvoted cell (gamma −5 and
  the independent remainder 0 — no outvote by the pre-registered definition) ·
  the board-offset work (offset **+29.5**, clean; proximity hypothesis stays
  NULL and is not revived).

### No new data point is warranted

Every failure today is a **sign** or **dependence** problem in rows already on
the page: a short-gamma distance term used as a direction term while a positive
0DTE gamma figure sat unused two lines away; a −6 whose independent content is
0; a 27bp breadth spread scoring; and a hawkish regex matching "tighten race".
**No free, reliable external feed fixes any of those** — the positive 0DTE number
the engine needed on 10-26 was **already in the scan**.

### Comparability warning for the 10-27 grade (carry-forward, not graded here)

The 10-27 trigger fired **27 minutes late** (13:12Z against a 12:45Z schedule)
and the scan ran at **13:13Z with NY cash 16 minutes away instead of ~42**. The
fuel block correctly rebased (*"~50% normal by 09:14 ET"*), but the **pre-scan
window is ~26 minutes longer than every other scan in the record**. **When 10-27
is graded it must be treated as NON-COMPARABLE on any pre-scan-range or
pre-scan-contamination statistic** (P-B(b)'s denominator, the session-context
census, pre-scan sweep counts) and excluded from them explicitly rather than
entering silently. For the record: **MILDLY BEARISH −3**, offset **−2.4**
(cleanest of the month), fuel MODERATE 1.19, week net GEX **+1.459** with 0DTE
+2.26, VIX9D/VIX **1.01 BACKWARDATED**, MAX PAIN merged with PDH and NY High at
**+11** with a 0.69bn shelf at **−2**, zero headlines auto-scored,
`PIN_THEN_EXPAND` 4th firing (outside the closed test).

---

## Journal hygiene

One scan file for 10-26 (`1252-preny.json` + `.md`), `is_trading_day: true`,
276 bars, **0 test artefacts** for the day (6 across the record, excluded by
`track.py`). **09-24 quarantined by hand — 21st consecutive review to carry it**;
there is still no schema `quarantine` field and the 09-29 proposal for one is
reaffirmed (`track.py` still prints 09-24 CORRECT, so 14/10/7 is carried by hand
as **13/10/7**). **2026-10-13 has no journal directory — documented, not
recreated.** **09-09 and 09-25 still have no `REVIEW.md` and none was created or
back-dated.** **2026-10-27 is on disk, `is_trading_day: true`, 185 bars,
correctly held back and NOT graded.** No `prediction` block was touched. No
scoring, wall or grading code was edited. No fabricated or backfilled entries
found. **One new ID allocated by this review: P-I. Next free: H28 · D28 · P-J.**
`track.py` prints **no literal `actionable: YES/NO`** — it prints *"threshold
met, read the evidence before proposing"* — so the 3-session rule was applied by
hand, per entry.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
