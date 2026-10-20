# REVIEW — 2026-10-19 (Monday)

Graded 2026-10-20. One scan on disk (`1248-preny`), `is_trading_day: true`,
`review_day.py` reports **0 test artefacts**. Grading basis is **post-scan**
per **P-H**; the day-net figure is reported alongside it every time the two
disagree.

---

## 1. Scoreboard

**Session (276 M5 bars):** O **29128.8** · H **29799.0** (15:35Z) · L **29112.1**
(22:00Z 10-18) · C **29559.4** · range **686.9** (**1.364x** ADR14 503.6) ·
day net **+430.6**.

| | |
|---|---|
| Call | `MILDLY BEARISH` **−5**, expected direction **−1**, price 29559.6 |
| Post-scan move (P-H basis) | **−9.3** → **CORRECT** |
| Day-net move | **+430.6** → **WRONG** |
| **P-H deciding instance?** | **YES — the 5th** (09-11, 09-16, 10-07, 10-15, **10-19**) |
| Post-scan running | **12 / 18 = 66.7%** (was 11/17) |
| Day-net running | **13 / 18 = 72.2%** (was 13/17) |
| Levels published / touched | 5 / 4 → hit rate **0.80** |
| Distinct touch bars | **3** (195, 204, 209) → distinct-event rate **0.60**, inflation **1.33x** |
| Fuel | budget **0.0**, extension **169.8** → err **+169.8**, **UNDER-estimated** |
| Post-scan traversal | **329.7** (0.65x ADR) |
| `track.py` | 29 trading days / 32 scans (deduped) · per-day mean err **+50.2 → +54.3** (n=29, incl. 09-24) · per-scan **+54.9** (n=32) · direction **16/7/9** → **15/7/9** ex-09-24 |

**Note on the headline "CORRECT".** It is earned by a **9.3pt** move on a
**686.9pt** range — **1.35%**. See §3; this is an **H17** instance.

### The pre-registered `PIN_THEN_EXPAND` test — run exactly as written, **FALSIFIED**

Pre-registered in the 2026-10-19 review before the outcome was known. Threshold
is 3 such days; **this is observation 1 of 3 and no verdict attaches to the shape.**

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **329.7** | 14.3 | 29799.0 @15:35 | 29469.3 @14:00 |
| **post** 17:00–20:55Z | **139.5** | 48.7 | 29657.3 @19:25 | 29517.8 @20:00 |

- Clause 2 (CONFIRM) requires post range **>** pre range: **139.5 < 329.7, fails.**
- Clause 3 (FALSIFY) fires **twice**: the pre window holds the larger range,
  **and** both session extremes were set before 17:00Z (high 29799.0 @15:35Z,
  low 29112.1 @22:00Z on 10-18).
- **Verdict: FALSIFIED on both clauses.** The prose said *"save your risk for the
  afternoon"*; the afternoon had **42%** of the morning's range and the day's
  move was already over by 15:35Z (11:35 ET), **85 minutes before** the pin was
  said to weaken.

**Secondary test ("breakouts will fail while the pin holds").** Pre-scan high
**29629.2**, pre-scan low 29112.1 (range 517.1, matching the journal exactly).
One sweep before 17:00Z — the **high**, at 14:15Z — and price closed back inside
within 30 min (14:30Z close 29593.7). **By the letter of the rule that supports
the claim.** By substance it does not: the same level was exceeded by **169.8**
later in the same pre-17:00 window and the breakout **ran**. The pre-scan low was
never swept. **Recorded without a verdict.**

---

## 2. What the levels actually did

| level | dist | prose said | what happened | verdict |
|---|---|---|---|---|
| **MAX PAIN 29771.1** | +212 | *"drifts toward it as the week goes on. **Weak on a Monday**"* | high **29799.0** printed **27.9 above it**, then 253.3 down; close 211.7 below | **the best level on the board**, and the day-of-week qualifier was wrong |
| **CALL WALL 29646.1** | +86 | *"desks must SELL as price rises into it, so **rallies stall**. Take profit into it"* | touched 14:15Z, ran **+152.9** through it to 29799.0; close 86.7 below | **SLICED** |
| **GAMMA FLIP 29638.9** | +79 | *"we're BELOW it: they're pushing, **don't fade**"* | same bar 14:15Z; price traded **160.1 above**, closed **79.5 below** | barrier **no**, *don't fade* **yes** |
| **STRUCTURAL CALL WALL 29696.1** ●●●●● 1.35bn | +136 | *"the ceiling for the WEEK/MONTH, **not today**… not an intraday trigger"* | touched **2h12m after the scan**, price ran **+102.9** through it | **wrong twice** — it *was* intraday, and it did not cap |
| **PUT WALL 29246.1** ●●●●○ | −314 | *"the strongest floor on the board"* | **never reached** (post-scan low 29469.3, missed by 223.2) | **noise, and worse — see below** |

**Three findings, not one.**

1. **The whole call-side cluster was sliced, in one bar.** The call wall, the
   flip and the structural wall all sit within 57 points of each other and all
   three were taken out between 14:15Z and 15:00Z. The board published three
   independent-sounding reasons to expect a stall at ~29640–29700 and price went
   **153–160 points past all of them**. `review_day.py` records every one of
   them as *"stalled at it — held as resistance"* because the settle window opens
   **after** the move (19:20Z and 19:35Z for the wall and the flip, four to five
   hours after first touch). That is **M6**, session 27.
2. **The put wall should not have been published.** It was never reached — but
   the real problem is that price had already traded **134 points below it**
   overnight (session low 29112.1 at 22:00Z) and the board still printed it at
   −314 as *"the strongest floor on the board"*, with no indication it had
   already been traded through. That is the **session-context field**, proposed
   09-30, **16th session**, and the cheapest unactioned item on the register.
3. **Max pain earned its line and the board hedged it away.** A `(stretch)`
   marker, a 0pt budget and *"weak on a Monday"* were attached to the one level
   that located the session high to within 27.9 points. Second within-reach
   success in the record (10-15 the other), against six distance-confounded
   non-tests.

**Board arithmetic, for the record.** `merge_tol = max(3.0, 503.6 × 0.008) =
4.029` against `TOUCH_TOL = 8.0`. The pair **(29646.1, 29638.9)** is **7.2**
apart — inside the structurally-guaranteed double-count window — and it
**fired**: both graded touched at **bar 195**. **P-B(b)**, 16th session,
inflation **1.33x**.

---

## 3. What was wrong, and why

**The call was bearish; the day closed +430.6 up.** The post-scan `CORRECT` does
not rescue it — a 9.3-point post-scan move is 1.35% of the session range, and the
engine's actual view of the day (down) was wrong by 430 points. Tracing to
`inputs.bias_components`:

**`vol −6` is the entire error, and it is one reading counted four times.**
Four rows, all sourced from the same Friday close:

| row | pts |
|---|---|
| VXN 27.13 (+18.5%) — *"fear rising, bearish"* | **−2** |
| VIX9D/VIX 1.082 BACKWARDATED — *"near-term stress, expect range expansion, downside skew"* | **−2** |
| VXN/VIX 1.46 — *"tech-specific stress"* | **−1** |
| VVIX 109.91 — *"active tail hedging"* | **−1** |

Delete the vol block and the score is **+1** — the day's sign. These are not four
signals; they are four functions of one latent variable (near-term implied vol on
the Nasdaq), each scored independently, so a single vol regime votes four times
and outvotes every other block on the page. **This is the largest vol
contribution in the record and it is also its largest single error.**

**The backwardation row was right about magnitude and wrong about sign, and only
the sign is scored.** It says *"expect range expansion"* — the day ran **1.364x
ADR**. It also says *"downside skew"*, which cost −2. The row's informative half
reaches no number.

**Two range forecasts on the same page, opposite signs, and the engine scored the
wrong one.** The fuel block printed `EXHAUSTED`, **0.0 budget**, 102.7% of ADR
used pre-open, `fuel_ratio` **2.28 (burning hot)** — and was wrong by **+169.8**.
Four lines below, the **VXN-implied range 505.2** printed **above** ADR 503.6
with *"options market prices expansion, ADR understates"* — the first time this
month that line argued for expansion, and it was **right** (realised 686.9).
The forecast that was right is prose and feeds nothing; the forecast that was
wrong sets the budget, the `(stretch)` markers on 4 of 5 board rows, and the
stop-management instruction.

**The gamma block voted against itself and the day split the difference.**
`gamma −3` (below flip, *"dealers amplify… rallies unstable"*) and `gamma +2`
(week net GEX **+1.123**, *"pinning likely"*) on the same page, net −1. Neither
happened: nothing pinned (1.364x ADR) and the rally was not unstable (it ran
169.8 past the pre-scan high and 152.9 past the call wall). The one half that
**was** right is the regime text — *"short gamma, don't fade"* — and the fade of
the day's only sweep duly lost (§4, axis 1).

**`macro +4` was the only block on the right side of the day, and it is two rows
with one observation date.** DFII10 (**+3**) and DGS10 (**+1**) both resolve to
**2026-10-15**; the age warning printed on DFII10 and not on DGS10; HY OAS
rendered **no observation date for the 13th consecutive session**. **H18/P1
instance 21, duplication 26/26.** Suppressing the stale pair takes −5 → **−9**:
a bigger call in the wrong day-net direction. On the post-scan convention that
counts as the gate's **4th help** (vs 2 hurts) — but the 4th help is a
**9.3-point** move, so on any basis that respects magnitude the record is **3
helped / 2 hurt**. **The accuracy case stays retracted.**

**Every input on the page was stale in the same direction, because it was a
Monday.** `breadth −3` (mega-cap avg −1.86%, NDX −2.50% vs ES +0.49%) and all
four vol rows are Friday-close readings presented at a Monday 08:48 ET scan;
the NDX cash reference itself was **3873 minutes** old. The NDX/ES comparison on
a Monday pre-open cannot be a like-for-like window — that is a **D22** instance
in the configuration where it matters most. Nothing here is a fixable "wrong
number"; the point is that **−9 of the −5's inputs describe the session that had
already finished**, and the engine has no term for that.

`structure +1` (above PD mid 29551.2) was right and small. `fuel`, `rates`,
`news` and `events` contributed **0** and `events` has now scored 0 on **33 of
33** scans.

---

## 4. Change proposals — only material ones

### PROPOSAL 1 (H2) — the fade-vs-continue census is re-derived and H2 is FALSIFIED. n=7.

**The suspended census is lifted on axis 1 only.** Rules were fixed in writing
before any outcome was inspected (script retained at
`/tmp/claude-0/-home-user-CTrader-Bots/d223cf12-f6c6-532d-a07d-b1099eb082ee/scratchpad/census.py`):

> **Cell:** PRE_NY · `is_trading_day` · 09-24 excluded · `fuel_state ∈
> {LOW_FUEL, EXHAUSTED}` **and** price below the gamma flip. (`LOW_FUEL` body
> text: *"favour fades over chasing breaks"*; `EXHAUSTED` management text:
> *"Fading the extremes… is the higher-probability side here, even when the gamma
> regime favours continuation"* — `brief.py:463–478`. Both are fade instructions;
> below the flip the board says *"they're pushing, so don't fade"*.)
> **Grade:** first post-scan sweep of a pre-scan extreme → fade engages on the
> first bar closing back inside → **FADE WINS** if the nearest published level
> inside is touched before the swept extreme is reclaimed, **LOSES** if reclaimed
> first or never re-entered. Ties scored **to the fade**.

| day | state | sweep | target | result |
|---|---|---|---|---|
| 09-14 | LOW_FUEL | up 15:30 | 28804.7 | **fade LOSES** (never came back inside) |
| 09-15 | LOW_FUEL | down 14:50 | 28963.1 (+37.3) | fade wins — *on the engage bar, tie* |
| 09-28 | LOW_FUEL | down 14:10 | 30345.9 | **fade LOSES** (reclaimed) |
| 10-08 | LOW_FUEL | down 16:45 | 30895.1 | **fade LOSES** (never came back inside) |
| 10-14 | LOW_FUEL | down 12:55 | 30386.7 (+32.4) | fade wins — *on the engage bar, tie* |
| 10-15 | EXHAUSTED | down 13:30 | 29627.6 | **fade LOSES** (reclaimed) |
| **10-19** | **EXHAUSTED** | **up 14:15** | **29246.1** | **fade LOSES** (reclaimed) |

**5–2 to the gamma block, and 7–0 if ties are scored against the fade** — both
"wins" resolved inside the single 5-minute engage bar at sub-40pt targets.
08-24 and 08-26 are in the cell but outside the 45-day bar window and are
reported as unavailable, not excluded by choice.

**What to change:** when `fuel_state` is `LOW_FUEL`/`EXHAUSTED` **and** price is
below the gamma flip, suppress the fuel block's fade instruction or subordinate
it explicitly to the regime note. **Expected effect:** on 7 of 7 recorded days
the brief stops issuing the instruction the board contradicts, and on 5 of them
stops issuing the losing one. **H2's threshold was 3+ and it is met at 7; H2's
claim as written is FALSIFIED.**

**Axis 3 stays suspended, and the specification itself is the defect.** Graded as
specified (*"realised post-scan traversal exceeded the budget-implied cap"*) the
conflict days read **9 of 9 to shape/gamma** — but the control reads **15 of 16
the same way on non-conflict days**. The metric is a near-constant, for the
reason `review_day.py:230–238` already states in its own comment: the budget
bounds range **extension**, and traversal is a different quantity. **Delete the
axis-3 column; do not re-score it.** A valid axis-3 test needs the fuel block's
own target unit, which is an **R multiple**, not points — so it cannot be graded
at all until the R denominator is recorded. **No axis-3 score is quoted.**

### PROPOSAL 2 (H23) — act on the pre-registration: CLOSE the force-ranking branch.

**Third consecutive agreement between distance-first and force-first, so the fix
is unfalsifiable in practice.**

- **Downside — a genuine choice, and they agree.** Positive shelves below:
  29496.1 (**0.78bn**) · 29446.1 (0.63) · 29196.1 is negative-sign. Nearest is
  also heaviest.
- **Upside — they agree by tie.** Heaviest is a **tie at 0.75bn** (29646.1 /
  29896.1), broken by distance to **29646.1** — exactly what distance-first
  published.

Per the pre-registration (10-16 was the second agreement), **H23's ranking branch
should be CLOSED rather than carried.** The brake census itself gains two
instances: **29496.1 CAPPED** (price went only 26.8 below, then rallied 302.9 —
only the **2nd cap in 15**) and **29646.1 SLICED** (+152.9). Census **9/1/3 →
10 sliced / 2 capped / 3 never-reached**.

**One trap flagged so a later reviewer does not open a defect for it.** The
secondary table lists a positive shelf at **29596.1 (+36, 0.47bn)**, nearer than
the published upside brake. That is **not** a brake `path_read()` skipped: the
table is built from `walls_ranked` (`brief.py:647`) and `path_read()` reads
`largest_abs_gex` (`brief.py:515`). **Different lists.** The corridor-terminus
proposal remains **WITHDRAWN** (10-16) and is not revived.

### PROPOSAL 3 (H26) — stop quoting the signed Spearman until its derivation is written down.

Re-deriving H26 at n=24 reproduces the register **exactly** on two of three
statistics — Spearman(|score|, |post-scan|/ADR) **+0.577**, Spearman(|score|,
range/ADR) **+0.198** — which confirms the sample is the same one. The **signed**
statistic does **not** reproduce under either available convention: **+0.220**
treating the 7 no-call days as 0, **+0.102** excluding them, against the
published **+0.157**. One of the three numbers H26's proposal rests on cannot be
reproduced from the journal. **Quote it with its method or stop quoting it.**

**H26 updated, n=25.** 10-19 is a **3–5 bucket** instance, **CORRECT** on the
P-H basis.

| \|score\| | n | C | W | no-call | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.181 | 1.103 |
| **3–5** | **5** (was 4) | **3** (was 2) | 2 | 0 | **0.193** (was 0.236) | **1.023** (was 0.937) |
| 6–9 | 7 | 6 | 1 | 0 | 0.545 | 1.193 |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

Spearman(|score|, |post|/ADR) **+0.577 → +0.548** · range/ADR **+0.198 → +0.190**.
**Is the magnitude claim still standing? In bucket form yes, in correlation form
it is eroding.** The bucket means on |post|/ADR remain monotonic
(0.181 / 0.193 / 0.545 / 0.783), but the rank correlation has now fallen on **two
consecutive sessions** (+0.612 → +0.577 → +0.548), and 10-19 is the cause this
time: the **second-lowest |post|/ADR in the record (0.018)** at a mid-range
|score| of 5. The direction half is unchanged and still weak.

### Nothing proposed — threshold not met, appended only

- **`PIN_THEN_EXPAND`** — **observation 1 of 3. No verdict, nothing proposed**,
  per the pre-registration's own clause 5. The falsification above is recorded
  as data, not as a finding.
- **H17 — 2 of 3.** Post-scan move **1.35%** of session range, the second
  sub-5% graded call in the record after 09-11's 0.2%. Threshold is 3 **days**.
  Append; propose nothing. *(When it is reached, note that it also re-grades
  10-19's `CORRECT` and the 5th P-H deciding instance with it.)*
- **P-E — instance 14, SLICED, and clean.** Pre-scan high 29629.2 was **16.9
  below** the call wall, so there is **no pre-scan contamination** for once.
  Overshoot **+152.9** sits in the slice mode, not the 12–103 middle. Census →
  **5 capped / 1 middle (10-06) / 8 sliced**. Close-side control held (86.7
  below); the intraday lid did not.
- **P-E(b)** — supporting instance: the shelf **29746.1** stalled the rally at
  **+52.9** while the call wall was sliced by 152.9. The shelf located the high
  **100 points better** than the headline wall.
- **P5 — 3 of 6 shelves gradeable, 2 right / 1 wrong.** 29496.1 *"stall and
  dip-buying… acts as support"* → **RIGHT** (26.8 below, then +302.9). 29746.1
  *"rallies lose momentum into it"* → **RIGHT** (+52.9, then −228.3). 29596.1
  *"stall — rallies lose momentum"* → **WRONG** (+202.9 straight through).
  29896.1 / 29446.1 / 29196.1 **never reached**. Better than 10-16's 2-of-6; the
  structural half-the-table-out-of-reach problem persists. **Still graded by no
  tool.**
- **H22 — n=11.** Week net GEX **+1.123** → *"pinning likely"* → realised
  **1.364x ADR**. The label was **wrong**. Still no ordering.
- **H4** — flip touched, acted as a barrier for one bar, closed **79.5 below**.
  Not a settlement magnet; instance against, claim already failed 09-16.
- **D23 — 14th residual, and a FOURTH consecutive sign disagreement.** Board
  **−3.9** vs section-7 **+364.1**, matched to feed time 11:59Z. Gap **−368.0**;
  CFD move (11:55Z bar open **29542.1** → scan 29559.6) = **+17.5**; **residual
  −385.5** — second-largest absolute in the series after +438.2. Series:
  `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
  −68.0 / +165.0 / +438.2 / +33.6 / −385.5`. Damage none: no volume had traded.
- **D25 — 27th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, printed under *"No volume has traded yet today"*.
- **D26 — reporting gap, not data loss.** `track.py` **29 trading days / 32
  scans (deduped)**; on disk **36** day directories, **66** scan JSONs, **31**
  days with a PRE_NY scan, **30** with a `REVIEW.md` (31 after this one), **27**
  with both.
- **M6 — session 27, and the magnitude scales with travel, as directed.**
  Post-scan travel 329.7 = **0.65x ADR** against 10-16's 2.01x, and the
  understatement is correspondingly milder: mean **2.6x**, worst **3.6x**
  (10-16: mean 4.5x, worst 8.2x).

  | level | grader travel | actual excursion | ratio |
  |---|---|---|---|
  | 29696.1 STRUCT CW | 49.5 down | 178.3 | **3.60x** |
  | 29771.1 MAX PAIN | 103.0 down | 253.3 | 2.46x |
  | 29646.1 CALL WALL | 67.6 up | 152.9 | 2.26x |
  | 29638.9 FLIP | 74.8 up | 160.1 | 2.14x |

  The **settle-window defect repeats**: all four rows read *"held as
  resistance"*, with `worst_excursion` of 11.2–23.3 on levels price exceeded by
  **27.9–160.1**, because the window opens at 15:40/16:10/19:20/19:35Z — after
  the 15:35Z high it is meant to measure.
- **Session-context field — 16th session.** Only **1 of 5** rows lay inside the
  pre-scan range, the mildest count in the series — but it is the **put wall**,
  published as *"the strongest floor on the board"* at −314 after price had
  traded **134 points below it** overnight. Free, arithmetic on data already on
  the page, **proposed 09-30, still not actioned.**
- **P4 / H1 — n=29 days, NOT re-derived.** 10-19 error **+169.8**; `track.py`
  per-day mean **+50.2 → +54.3**, per-scan **+54.9** (n=32). The budget was
  **0.0 — the arithmetic floor — so the error is the entire extension** and the
  estimator was one-sided by construction, the 7th such entry. Claim stays **"no
  usable skill"** (MAE 116.1 vs leave-one-out constant 98.3, n=19), **not**
  "inversely predictive". **Multiplier branch stays closed.**
  **Follow-up to 10-16's sub-observation, and it is a clean counter-test.**
  10-16 had `fuel_ratio` **1.24 *(normal)*** and produced the largest range in
  the sample; 10-19 had **2.28 *(burning hot)*** and produced **1.364x ADR** with
  a **+169.8** under-read. Hot pace did not predict expansion (rejected 10-14)
  and cool pace did not predict quiet (10-16). **Pre-scan pace carries no
  information in either direction. Close the question.**
- **P-G — no instance.** The 10-19 board carries no session-extreme rows; the
  prev-day extremes appear only in the context line, which has no side-prose.
- **D21 — no instance.** `gamma +0`, price **78%** up the band — neither branch
  fired. Worth one line only because the 80% threshold missed by 2 points on the
  day price ran to the top of the band.
- **D7/D15 — the degenerate marker, again.** With a 0.0 budget, **4 of 5** rows
  are marked `(stretch)`, which makes the marker uninformative. D7's exemption
  did work: the structural wall is the one row **not** marked.
- **Dead-weight audit, n=33** PRE_NY `is_trading_day` scans (09-24 excluded by
  hand): `events` **0/33** · yield curve **0/33** · DXY 4/33 · NFCI 5/33 ·
  WALCL/RRP 6/33 · US10y 25/33 · **HY OAS 26/33**. The narrowed standing
  proposal (drop the yield-curve row and WALCL/RRP) is unchanged and still not
  actioned. **HY OAS is not dead weight; that correction holds.**
- **H19** — 51 headlines, **2** auto-scored (1 bull / 1 bear → NEUTRAL), 49
  needing context. Coverage **3.9%**.
- **H8 — ANSWERED-POSITIVE, post-closure data only.** Straddle band
  **29152..29967**; close **29559.4**, comfortably **inside**. On the same page
  the VXN-implied range **under-read** the realised range by 181.7. Consistent
  with H8's verdict; not reopened.
- **No instance:** **H7** (no overnight scan) · **H10** (price inside the
  prior-week range 29073.7–31079.0; neither branch) · **H20**
  (CLOSED-NEGATIVE, not revived; no High/Medium events) · **D24** (`event_gate:
  null` correct; NFLX/META/TSLA all after the session) · **P-F** (price inside
  the prior-day range 29073.7–30028.6) · **H3** (CLOSED-NEGATIVE, superseded by
  H26).

### Is a new data point warranted? No — and the one that tempts is already on the register

The input that would have changed 10-19 is a **live** vol read rather than
Friday's close, because the four stale vol rows cast **−6 of a −5 score**. That
is **1 day of evidence**, so **nothing is proposed**, and it is not a new number
either: *"percent-changes are not guaranteed to be prior-session and the legs
cover different windows"* is **D22**, and the Monday-after-a-Friday-selloff
configuration is D22's sharpest instance. **Watch item, no ID, 3 sessions
needed:** do the vol rows' staleness and the Monday configuration coincide, and
does a free intraday vol proxy exist that is reliable at 08:48 ET? Neither
question is answered today. **Before anything new is added, the
session-context field — free, reliable, proposed 09-30, 16 sessions of
evidence — should be actioned.**

---

## Carried forward from the 2026-10-20 scan — recorded, NOT graded

- **Board offset 74.5 — a FIFTH breach**, landing immediately after two clean
  readings (14.9 on 10-16, −3.9 on 10-19). Arithmetic verified independently and
  correct: NDX cash close 10-19 **29529.35**, roll **−187.0**, implied
  **29342.3**, CFD **29416.8** → **+74.45**. Series: 09-28 45.9 · 10-12 43.1 ·
  10-14 41.8 · 10-15 77.6 · **10-20 74.5**, with clean days interleaved.
  **This is intermittent, not a trend** — the time-trend model has now missed
  **four** sessions out of sample. **Mechanism left unexplained; no third story
  is substituted and nothing is proposed.**
- **The suggested offset-vs-proximity tabulation — run, and it is NULL.**
  Nearest options-derived level at scan time, on the five breach days: **127.9 ·
  0.4 · 206.7 · 11.1 · 257.7** (mean 120.8) against **75.9** on the 26 clean
  days — but the breach sample spans the near-smallest and the largest values in
  the whole record. **No separation at n=5. Nothing proposed.** The 10-20
  structural observation stands on its own and is worth keeping: every level
  within 212pts of price is session-derived (cTrader-native, offset-immune) and
  every options-derived level is ≥258pts away, so the practical damage is far
  smaller than 10-15, where the structural put wall sat 11pts from price.
- **The pre-registered realised-close-basis log — observation 4 of 10.**
  NDX cash close 10-19 = implied 29342.3 − roll (**−187.0**) = **29529.3**;
  CFD close **29559.4**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
  | 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
  | 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
  | **10-19** | **−3.9** | **29529.3** | **29559.4** | **+30.1** | **+34.0** | **−187.0** |

  Second consecutive **positive** realised basis, and the |roll| reading cuts
  the same way as 10-16: the **smallest** |roll| in the log (187.0) produced a
  mid-sized gap while the **largest** (376.0) produced the smallest.
  **Re-test still at n=10 clean observations. Nothing proposed.**
- **The roll-parser defect is CONFIRMED and independently verified.** The
  register's own scratchpad extractor matches `NQ futures move \((-?[\d.]+)\)`,
  which cannot match `(+376.0)`. Across every PRE_NY scan there are **16
  up-rolls and 16 down-rolls**, and **all 16 up-rolls were silently recorded as
  `None`** — exactly half the sample. **Any |roll| regression must be rebuilt
  with a sign-tolerant parse before being quoted again.** The defect is in the
  register's analysis, **not** in scoring, wall or grading code.

---

## Journal hygiene

One scan file for 10-19 (`1248-preny.json` + `.md`), `is_trading_day: true`,
**0 test artefacts** for the day (6 across the record, excluded by `track.py`).
**09-24 quarantined by hand — 15th consecutive review to carry it**; there is
still no schema `quarantine` field and the 09-29 proposal for one is reaffirmed,
because `track.py` keeps 09-24 inside every statistic it prints (direction
**16 / 7 / 9** becomes **15 / 7 / 9** once 09-24 is removed). **`track.py` no
longer prints a literal `actionable: YES/NO`; the 3-day threshold rule was
applied by hand throughout.** **2026-10-13 has no journal directory — the
scheduled scan never ran; nothing was created, back-dated or inferred.**
**2026-10-20 is on disk and unfinished (180 bars), correctly held back by
`track.py`, and excluded from every statistic above** — including the axis-3
control, where its in-progress 44.1pt traversal would have been the only "fuel
wins" row. 09-09 and 09-25 still have no `REVIEW.md` and none was created.
**No `prediction` block was touched. No scoring, wall or grading code was
edited.** No fabricated or backfilled entries found. **No new ID allocated by
this review. Next free: H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
