# REVIEW — 2026-10-06 (Tue)

Graded from `review_day.py 2026-10-06 --json` and `track.py`. One scan on
record: **12:48:24Z PRE_NY** (`1248-preny.json`), `is_trading_day: true`,
0 test artefacts. 09-24 excluded by hand from every statistic (quarantined,
~305pt conversion error — "D23 CORRECTED") except where its direction call is
part of a figure `track.py` prints, which is flagged where it occurs.

---

## 1. Scoreboard

**Session** — O **31117.9** / H **31385.1** / L **31078.9** / C **31270.8**.
Range **306.2** (0.63x ADR14 486.2), net **+152.9**, 276 M5 bars.

| | |
|---|---|
| direction calls | **1 right / 0 wrong / 0 no-call** (+3 MILDLY BULLISH, post-scan move **+37.5**, dir +1) |
| post-scan move as share of session range | **12.2%** — above H17's 5% deadband, no instance |
| post-scan dir vs day-net dir | **AGREE** (+37.5 / +152.9). **Not** the third divergence instance the 10-02 flag pre-registered; that stays at n=2 |
| levels published / touched | **19 / 3** — hit rate **0.16** |
| distinct touch bars | **3** (bar 178, 186, 194) → P-B(b) inflation **1.00x** |
| hit rate split by side | rows **above** the scan **3 of 4**; rows **below** the scan **0 of 15** |
| fuel | budget **256.2**, extension **76.1**, error **−180.1** · extension/budget **0.30x** · traversal 156.4 = **0.61x** budget |
| fuel verdict | OVER-estimated. **−180.1 is the largest single-day over-read in the 26-day record** (previous worst −124.4, 09-25) |
| straddle band (H8) | EM ±182 → 31060 .. 31426; close 31270.8 **INSIDE**. Record **3 inside / 1 outside, 4 of 10** |
| VXN-implied range | 427.1 vs realised 306.2 — **over by 120.9** (realised 0.72x) |
| wall band position | price 89.2% up the 30707.6–31307.6 band (600pts wide) → `gamma −2` fired |
| cumulative (`track.py`) | **26 trading days, 35 scans**, 6 test artefacts excluded, 10-07 held back (181 bars) · direction **17 right / 9 wrong / 9 no-call** (includes quarantined 09-24's CORRECT; **16/9/9** without it) · all-time mean level hit rate **0.52** vs today's 0.16 |
| H1 aggregate | `track.py` per-DAY mean **+14.0** (n=26), per-scan **+19.8** (n=33); **−8.2** excluding the 09-21 outlier (n=25). MAE **88.9** against a mean per-day budget of **110.8** — the typical error is **80% of the typical budget**. (MAE and mean budget are aggregated from `track.py`'s own `per_day` list; it does not print them.) |
| H5 | early (26) mean err **+30.6** vs late (5) **−11.7** — unchanged in sign |

---

## 2. What the levels actually did

Three rows were touched, all of them above the scan price. Everything else sat
below price on a day whose entire post-scan extension was upside.

**31309.0 — London High (today) + CALL WALL ●●●●● 1.12bn + Options shelf 1.11bn (+66).**
The brief: *"Heaviest ceiling this week (13k contracts) — desks must SELL as
price rises into it, so rallies stall. Take profit into it… the strongest ceiling
on the board."* What happened: first post-scan touch 13:30Z, and price crossed it
**inside that single M5 bar** (O 31284.0 → H 31334.9) before closing the bar back
at 31257.5 — so the *first* break did fail, which is the brief's claim. It then
re-broke and ran to **31385.1 at 15:15Z, +76.1 through the row (+77.5 through the
unmerged wall at 31307.6)**, faded, settled below from 18:10 and closed
**31270.8 — 38.2 BELOW the wall**. Verdict: **it did not stall the rally, and it
did win the close.** Both halves of the brief's text came true, four hours apart,
and the document gives the unconditional lid first and the escape clause (*"a
held close above flips that selling to buying"*) last. On the close the lid was
the better read; on the intraday high it was 76pts wrong.

Two further things about this row. It is **the pre-scan high to the point** —
pre-scan H = 31309.0 — with **5 pre-scan touches and 0 pre-scan bars strictly
above it**. So it was published as an untested ceiling about a level the session
had already rejected five times, information the board has no field for; and,
unusually for this register, it is a **clean, non-pre-scan-broken** call-wall
test. And the force rating ●●●●● is 1.12bn on **13k contracts**, while the
research-only secondary table on the same page carries **31507.6 at 0.65bn /
13,958 contracts** — more contracts than the headline wall. Noted, not counted:
the high stopped 122.5 below it, so this is not a D7 contract-vs-force instance.

**31357.6 — Options shelf 0.97bn (+115).** *"Heavy dealer hedging parked here —
expect price to stall. Good place to take partials rather than push through."*
Price exceeded it by **+27.5** (the session high), then held below it for 330min.
**This was the best call on the board**: it located the day's ceiling to 27pts
and the instruction (partials, don't push) was the right one.

**31257.6 — Options shelf 0.58bn (+15), and §3's named UPSIDE brake.** §3:
*"UPSIDE path: has friction. Expect a stall at 31257.6 (15pts away) — take
partials into it rather than assuming a clean breakout."* Price ran **+127.5
beyond it** (0.26x ADR14). It then worked well as **support** — worst excursion
−28.9 from first touch, close +13.2 above. **Right level, wrong role**: the board
and §3 both asserted resistance for a level that spent the session as a floor.

**Rows that nothing reacted to, and why most of them are not evidence.**
16 of 19 untouched, **15 of them below the scan price**. That is board placement
measured against a one-way session, not level quality, so **0.16 must not be read
as a quality number** (standing caution, 09-21). The ones worth naming anyway:

- **30786.4 GAMMA FLIP (−457) · 30707.6 PUT WALL ●○○○○ (−535) · 30607.6 MAX PAIN
  (−635) · 30257.6 STRUCTURAL PUT WALL (−985).** All four sat **292–822pts below
  the day's low**. The structural wall is now **0 touches on 10 publications
  across 9 trading days and has never been within 200pts of price** (today 985 =
  2.03x ADR14). Max pain is a **7th distance miss in 10 evidence days** at 1.31x
  ADR14. `review_day` grades a level 985pts away and a level missed by 9.6pts
  with the identical string *"never reached"*.
- **31115.8 "Equal lows ×4 — 4 touches at this price, never traded through — a
  real stop cluster. Prime S1 sweep trigger."** In **this same graded session**
  price traded below it in **44 bars (22:35Z → 07:05Z, 20 of them entirely
  below)**, bottoming **36.9pts through it** at the Asia low. *"Never traded
  through"* is **false in its own session**, and the S1 sweep it offered as a
  forward trigger had already happened and already failed.
- **31137.3 PDH + NY High (prev-day) (−106)** — *"the biggest pile of stops
  **above us**. Sweep it, wait for a lower high on the 1m, then CISD = short"* —
  printed while price stood **105.7 ABOVE it**. 67 pre-scan touches.
- **31207.6 shelf 1.08bn**, §3's named DOWNSIDE brake (*"Expect a stall at
  31207.6 (35pts away) — take partials into it rather than assuming a clean
  breakdown"*): **never tested post-scan** (post-scan low ≈31247), and the
  session had already traded below it in **153 of 178 pre-scan bars**.
- **31407.6 shelf 0.55bn** — missed by 22.5. Genuinely untested; the nearest
  shelf above the high.

---

## 3. What was wrong, and why

**(a) The call was right, and the rows that nearly broke it were the stale ones.**
`inputs.bias_components`: macro **−6** · breadth **+3** · structure **+3** ·
gamma **+2** · rates **+1** · vol **0** · news **0** → **+3**. The macro −6 is
three FRED rows: DFII10 **−3** keyed to an observation dated **2026-10-02** (two
business days stale, and the brief says so), DGS10 **−1** on a 10-01→10-02 move,
HY OAS **−2** with **no observation date rendered at all — 4th consecutive
session**. The DFII10 row read *"yields rising = tech gets hit hardest"* on a day
when the **live** `rates` row in the same document read *"US10y 5.277 (−0.64%) —
yields down, BULLISH tech, +1"*. **Two rows, same instrument, opposite signs, and
the stale one carries three times the weight.** Damage: none to the sign —
zeroing DFII10 gives **+6**, zeroing all three stale macro rows gives **+9**,
both still bullish, both still CORRECT. The cost was **6 points of conviction on
a correct call**, which is the second instance of that shape in the series.
H18/P1's **accuracy** case stays retracted and the age gate stays blocked,
because HY OAS still renders no date to gate on. The DFII10 textual sub-defect
(*"this is last week's reading"*) did **not** fire: today is Tuesday and 10-02 is
Friday, so the unconditional string happened to be true again — luck, not a fix.

**(b) `gamma −2` "top 20% of the wall band" fired, and the day went up.** Price
31243.0 sat **89.2% up a 600pt band** (30707.6–31307.6), **64.6 below the call
wall**. Price left the band upward (high +77.5 above the band top) and closed
back inside it. On the register's current convention — absolute distance to the
call wall, not band percentage — 64.6 puts today in the **beyond-50pts** bucket,
which stood at **3 down / 0 up**; it is now **3 down / 1 up**. The within-50
bucket is unchanged at 5 up / 1 down. So today is the **first counter-instance in
the only bucket where the re-cut looked clean** — and the re-cut was already
flagged as having been found after looking at outcomes. Also the **width defect,
10th firing**: "top 20%" of a 600pt band is a **120pt trigger window = 0.25x
ADR14**, against 20pts on 09-18. The row keeps awarding the same −2 for
physically different conditions.

**(c) The fuel miss is dispersion, not bias.** −180.1 is the largest single-day
over-read on record, and the per-day aggregate still sits at **+14.0** (n=26),
**−8.2** without the 09-21 outlier. MAE **88.9** against a mean per-day budget of
**110.8**: **the typical error is 80% of the typical budget**, for the sixth entry in
a row. A multiplier corrects a bias that is not there; what is wrong is the
spread, and nothing in the record identifies a term that explains it.
The prose gloss (*"The range has room but not unlimited room. Continuation is
fine to the nearest pool; don't plan on a third leg"*) was **fine today** — the
range used 30% of its budget — which is the mirror of 10-05, where the same
sentence was badly wrong. That is the point: **the sentence is unanchored, not
consistently wrong**, so it cannot be fixed by flipping it.

**(d) §3's named brake failed upward for the 7th time.** H23 is now **6 sliced /
1 capped**. Today's slice, +127.5 = 0.26x ADR14, on a brake named at **+15**.
Both of today's named brakes were levels the same session had already traversed.

**(e) The strategy block was 50/50 on the only level it applied to.**
`STRATEGY 1 — sweep → failed re-break → CISD reversal`, *"dealers fade
extensions, so sweeps genuinely fail. This is your fade day"*, `COHERENT_LONG`,
*"expect a tight, pinned range… breakouts mostly fail"*. The **range** claim
held (0.63x ADR14). The **trade** claim was right on the 13:30Z sweep of 31309.0
(failed, −77 back) and wrong on the second attempt 40 minutes later (ran to the
high; the day closed +152.9 net up). One level, two sweeps, one of each, and the
document offers no way to tell them apart.

---

## 4. Change proposals

`track.py`: **26 trading days, 35 scans** — `actionable: YES` in the JSON, which
the human output deliberately renders as *"26 of 3 days for the 3-day hypotheses
— threshold met, read the evidence before proposing"*. It is a day-count gate,
not a licence; H4/H6 need 5 days and H8 needs 10. Read as the register requires:
**one new proposal, and one pre-registered question answered.**

### P-E — the empty middle is no longer empty. No new proposal; the existing prose fix stands.

Instance **12**: CALL WALL 31309.0 overshot by **+76.1** (+77.5 against the
unmerged 31307.6). Cap mode has been 3.6–11.9 and slice mode
103 / 117.5 / 154 / 185 / 205 / 279.2 / 573 across eleven observations, with
**nothing between 12 and 103**. **76.1 lands in the middle of that band.**

The 09-22 entry pre-registered exactly this: *"Watching for one instance between
12 and 103 — an empty middle in nine observations is either real bimodality or an
artefact of `SETTLE_TOL`, and a middle observation separates those."* It has
arrived, and on the cleanest available footing: per the 10-05 contamination
caveat, this wall had **0 pre-scan bars strictly above it** (it *is* the pre-scan
high), so it is **not** an already-broken level. Today is also the **first
instance where a material overshoot ended with the close BELOW the wall** —
every slice that quotes a close closed above it.

**Consequence: stop reading P-E as bimodal.** It is a continuum, and the two-mode
framing should not be extended or used to look for a mode discriminator. The
change that was already proposed is the right one and the only one: **the prose**
— lead with the conditional, drop the unconditional *"rallies stall. Take profit
into it… the strongest ceiling on the board"*, and if a number is printed beside
it, print the measured run-through distribution rather than an assertion.
Expected effect: a reader who acted on today's board would have been short into
a level that then gave up 76pts and only worked on the close.

### D25 (NEW, PROPOSED) — D14's fix never covered the `drift` sentence, and it has printed the same false claim on 20 consecutive pre-NY scans

Section 7 of today's brief says:

> **The dominant strike is stable** at 0 across 6 samples — positioning is settled there.

That string is **byte-identical in 20 scan files**: 09-11 ×2, 09-14 1304, and
every pre-NY scan from 09-15 to 10-07 — **19 scans across 17 completed,
non-quarantined trading days**. It is the same sentence `gexbot.py`'s own
`strike()` docstring quotes as a **D14 symptom**. The 09-16 fix guarded the strike
*fields* in `gexbot.levels()`; `brief.py` (the `gb["drift"]` block) reads
`dr["distinct_strikes"][0]` with **no guard**, so the absent dominant strike still
renders as `0` and is then asserted to be settled positioning.

Proof it is absence and not data: the only mid-RTH scan in the record with volume
present — **09-14 17:23Z** — printed *"**The dominant strike is MOVING** … 29,050,
29,100, 29,250, 29,300, 29,350 (a 300pt spread)"*. Pre-open it is 0 every single
time. This is the 12:45Z scheduled scan hitting the no-volume window every
weekday, exactly as the D14 entry predicted it would.

**Damage: none** — section 7 is research-only, says so, and the same section
already prints *"No volume has traded yet today"* two lines above. That is what
makes it a clean defect rather than a calibration question: the page contradicts
itself in writing.

**Change.** Suppress the drift sentence when `volume_fields_absent`, or route
`distinct_strikes` through the existing `strike()` guard and render "—".
**Expected effect:** removes a false assertion from every scheduled brief, and
closes the last place a volume-absent `0` survives as a claim — which matters
because H12/H13 were explicitly instructed not to count volume-absent scans.

### Explicitly NOT proposed

- **No fuel multiplier.** H1 n=26, per-day mean +14.0 / −8.2 ex-outlier. Sixth
  consecutive entry; the multiplier branch should be closed.
- **No H22 change, and today is the near-replicate the register asked for.**
  Week net GEX **9.084** → range/ADR14 **0.63x**, against 10-02's **9.526** →
  **1.09x**: a 4.6% difference in the input, a 0.46x difference in the outcome,
  the same unconditional *"pinning likely"* label. Across n=5 the input spans
  0.036 → 9.526 with no ordering at either end. **But the row carries +2 of
  DIRECTION score, and five range observations say nothing about direction** —
  proposing against it on range evidence would be the mis-targeting D21's own
  ledger exposed. **Logged, not proposed.** The test that would settle it needs
  no new data: grade the `pinning likely` row against realised **direction**
  across the 26 days already on record.
- **No D21 change.** The for/against tally is not restated here: the register
  switched to the distance re-cut on 09-23, that cut was found after looking at
  outcomes, and today is its first counter-instance.
- **No new data point.** Nothing today would have been changed by a feed we do
  not have. The two gaps that mattered — pre-scan interaction per level, and an
  observation date on HY OAS — are both already-proposed uses of data the
  pipeline already holds.
- **No back-dating.** 09-09 and 09-25 still have no `REVIEW.md`; not created, not
  amended. No `prediction` block touched.

### What I am watching

1. **P-E**, now as a continuum: whether further overshoots fill 12–103 or 76.1
   stays a singleton. One more middle observation and the bimodality claim is
   dead rather than weakened.
2. **H23** at 6 sliced / 1 capped — already proposed; whether the capped case
   ever recurs.
3. **The session-context field** (PROPOSED 09-29), 8th session, and today's
   sub-shape is the strongest yet: a row asserting *"never traded through"* about
   a level today's own session traded 36.9pts through.
4. **H18/P1's blocker**: a 5th consecutive session with no observation date on
   HY OAS keeps the age gate unmeasurable.
5. **M6**, 19 sessions: today **3 of 3** touched rows understate the breach and
   **3 of 3 "held" verdicts invert** when measured first-touch → close.
   Already re-proposed on 10-05; no new argument from me.

---

_Full per-item evidence appended to `journal/HYPOTHESES.md` under
"Observations appended 2026-10-07 (grading the 2026-10-06 session)"._
