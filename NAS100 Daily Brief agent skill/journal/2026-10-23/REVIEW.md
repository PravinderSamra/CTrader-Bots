# REVIEW — 2026-10-23 (Friday)

Graded 2026-10-26. One PRE_NY scan (`1248-preny.json`), `is_trading_day: true`,
275 bars, `review_day` reports **0 test artefacts**. Direction graded on the
**post-scan** basis per P-H.

---

## 1. Scoreboard

| | |
|---|---|
| Scan | 2026-10-23 12:48:21Z, price **28875.7** |
| Call | **STRONGLY BEARISH −16**, `expected_direction −1`, `COHERENT_SHORT` |
| Session | O **28939.6** / H **29155.4** (14:50Z) / L **28820.4** (13:35Z) / C **28999.2** |
| Range | **335.0** = **0.608x** ADR14 550.8 · net **+59.6** |
| Post-scan move | **+124.5 UP** → **DIRECTION WRONG** |
| Day net | **+59.6 UP** → also WRONG. **Both bases agree — NOT a 6th P-H deciding instance** |
| \|post\|/ADR | **0.226** · range/ADR **0.608** |
| Levels | **15 published, 7 touched = 46.7%**; distinct first-touch bars **5** → effective **33.3%**, inflation **1.40x** |
| Fuel | budget **294.6** (largest ever published), extension **78.8** → **0.27x**, OVER by **3.74x**; traversal **335.0 = 1.14x** budget; H1 error **−215.8 — the largest over-estimate in the record** |
| `track.py` live | **29 trading days / 30 scans**; direction **14 / 9 / 7** (**13 / 9 / 7** ex-09-24); levels touched **0.52**; H1 per-day **+53.9 (n=29)**, per-scan **+54.8 (n=30)** |
| P-H | post-scan **13/22 = 59.1%** vs day-net **14/22 = 63.6%**; deciding set stays **n=5**, cost **4.8 → 4.5** |

---

## 2. What the levels actually did

**Every options level on the board went untouched.** Gamma flip (+826), structural
call wall (+813), max pain (+613), call wall (+513) and put wall (−87) — 0 for 5.
The three prev-day liquidity rows (+368 to +502) were also never reached. All
seven touches came from the six rows inside ±235, and three of those shared a
single bar.

| level | dist | published claim | what happened | verdict |
|---|---|---|---|---|
| **28789.0 PUT WALL ●●●●● 1.21bn** | −87 | *"heaviest floor this week (125k)… if it breaks expect it to speed UP, not bounce"* | **never reached — low stopped 31.4 above it**, then +335 into the close | **the best level on the page, and ungradeable.** `TOUCH_TOL=8.0` files a wall that located the session low to **0.057x ADR** as *"never reached"* |
| 29389.0 CALL WALL ●○○○○ 0.28bn | +513 | *"heaviest ceiling… rallies stall. Take profit into it"* | 233.6 above the post-scan high | never reached; 8k contracts against the put wall's 125k, published as the other half of a symmetric pair it is not |
| 29689.0 STRUCTURAL CALL WALL | +813 | *"the ceiling for the WEEK/MONTH"* | 533.6 away | untouched again — **still 0 gradeable touches in its entire publication history** |
| 29489.0 MAX PAIN | +613 | *"strong by Thursday/Friday"* | missed by 333.6 | **9th distance-confounded non-test, 2nd consecutive on a day the qualifier claims** |
| 29109.3 London High (today) | +234 | *"the next session usually runs the stops above it"* | held as resistance, close **110.1 below** | RIGHT |
| 29073.9 Asia High + **PWL** ⭐ | +198 | *"PWL 29073.7 is now resistance, not support"* (`structure −3`) | cleared by **81.5**, then held as resistance 245min, close **74.7 below** | **the prose was RIGHT and the −3 it justified was WRONG** |
| 28981.6 Equal highs ×2 | +106 | *"a real stop cluster. Prime S1 sweep trigger"* | 35 touches, close +17.6 above | right in substance; graded *"held as support 45min"* only because of where the close landed |
| 28921.0 PD close | +45 | *"price often comes back to fill a gap from here"* | 8 touches, close **+78.2 above** | RIGHT |
| 28888.5 / 28860.5 / 28853.1 | +13 / −15 / −23 | three separate rows | **all first-touched in the same 12:50Z bar**; dipped 68.1 / 40.1 / 32.7; close **+110.7 / +138.7 / +146.1 above** | one price print, three "touches" (P-B(b)); all three graded **`acted_as: "lost"`** |

**Secondary table (P5)** — four put-dominant strikes, both claims graded separately
per the 10-23 refinement. 28589.0 (−287) and 28689.0 (−187) never reached.

| strike | dist | first touch | touches | min to a close 50 beyond | max penetration | close vs level | *"not a floor"* | *"accelerates through"* |
|---|---|---|---|---|---|---|---|---|
| 29089.0 | +213 | 14:40Z | 21 | 130 | 156.6 | −89.8 | n/a (above price) | **WRONG — 21 touches, it stalled there** |
| 28939.0 | +63 | 13:40Z | 10 | 15 | 216.4 | +60.2 | **RIGHT** | **RIGHT** |

**Clear-path read (H23).** Both paths flagged clear. The downside limb is
untested (low 28820.4, 431 short of the declared 28389.0 terminus). The upside
limb **ran 279.7 of the 363 declared, stalled 84 short of the terminus at
29073.9/29109.3 — two liquidity levels the options model says are nothing — and
reversed.** *"Do not fade it"* on the upside was the losing instruction; the
fade at the stall was the winning trade. Clear-path sub-series **n=2, 1 right
(10-22) / 1 wrong**.

---

## 3. What was wrong, and why

**The −16 was not seven independent signals. It was two correlated pairs.**

`inputs.bias_components`: vol **−4**, breadth **−3**, structure **−3**, gamma
**−3** net, rates −1, macro −1, news −1.

Measured across all 33 PRE_NY `is_trading_day` scans (09-24, 10-26 excluded),
the Pearson correlation between block subtotals is near zero for every pair
except two:

- **vol ↔ breadth r = +0.533**
- **structure ↔ gamma r = +0.555**
- every other pair: |r| ≤ 0.25 (next largest `structure↔rates` +0.206)

On the 13 days where the breadth row's prior-day NDX figure is recoverable,
**vol r = +0.698 and breadth r = +0.713 against that same number.** They are two
readings of one event.

On 10-23 that event was **Thursday's −2.90% NDX session**, and the score read it
three times:
- `vol −4` — VXN 28.72 **+17.6%**, VXN/VIX 1.44, VVIX 107.94. All three rows are
  the *consequence* of Thursday, priced after the fact.
- `breadth −3` — *"mega-cap avg −2.43%… NDX −2.90% vs ES −0.44%"*. That **is**
  Thursday.
- `structure −3` — *"price is BELOW the entire prior-week range"*. Price got
  there on Thursday.

**−13 of −16 came from the two collinear pairs; the independent remainder was
−3** (rates −1, macro −1, news −1) — which is *below the engine's own ±3
deadband*, i.e. a no-call. The carry-forward note written on the 10-23 scan
read this score as *"notably broad-based: seven components leaning the same
way… unlike 10-21 this score is not a duplication artefact."* **That reading is
wrong.** It is a duplication artefact; it is just not the FRED-pair kind the
register was watching for. The FRED pair contributed −1, exactly as noted — and
that was the wrong place to look.

**This is the mechanism behind H26.** A large |score| does not mean many
independent things agree; it means one large thing happened and several rows
measured it. That is a statement about the *past*, which is why magnitude
correlates with realised range and not with direction.

**Then it failed on magnitude too.** 10-23 is the 7th ≥10 instance and it is
**the smallest on both measures**: |post|/ADR **0.226** (bucket mean 0.783) and
range/ADR **0.608** (bucket mean 1.390). The pre-registered prior written before
the outcome — *"expect a big move, direction uncertain"* — was **wrong on both
limbs**.

**Second-order failures, each traced:**

- **`structure −3`, the prior-week-range rule (H10).** Price was **198.0 below**
  PWL 29073.7 — 0.36x ADR — and the rule scores that identically to 2000 points
  below. Price then **reclaimed the PWL intraday by 81.7**. The −3 branch goes
  **2-for-7 → 2-for-8**. The rule's *prose* (*"PWL is now resistance"*) was right
  and its *score* was wrong, which is the cleanest separation of those two in the
  series. **Third proximity-gap instance** (10-07, 10-22, 10-23) and the first on
  the −3 branch.
- **`vol −4` has no mean-reversion term.** The highest VXN in the series, +17.6%
  in a day, scored −4 — and the session that followed had the **smallest
  range/ADR of any ≥10-score day in the record**. The VXN-implied range **522.4
  over-read the realised 335.0 by 187.4**.
- **`gamma +2` bottom-of-band, 6th firing — and it was the only directionally
  right row in the gamma block.** Band 28789.0–29389.0 (600pt), price 14.5% up
  it, 86.7 from the put wall; bottom-20% trigger window **120pt = 0.218x ADR**.
  Census **2R/3W → 3R/3W**. It has still **never flipped a call's sign** (−16
  would be −18 without it), so **nothing is proposed** — D21's standing reason.
- **News: 1 scored headline out of 134 = 0.75% coverage, the lowest in the
  record**, and it was the wrong sign for the day. Two directionally relevant
  bullish headlines sat uncounted in the judgement list (*"10-year Treasury yield
  drops back to 5%…"*, *"Bullish Outlook on the Nasdaq 100"*).

**What was NOT wrong, and is worth saying:** the level *prose* outperformed the
*score* badly. PWL-as-resistance, PD-close-as-magnet, the equal-highs stop
cluster and the put wall's floor all behaved as written. The document's
directional thesis was the part that failed.

---

## 4. Change proposals

**None. Nothing proposed this session.**

The obvious proposal — *"down-weight the correlated blocks so a −16 cannot be
built from two pairs"* — was **pre-registered and run, and it makes the record
worse.** Rule fixed in writing before any outcome was inspected: within each
collinear pair ({vol, breadth}, {structure, gamma}), if both subtotals share a
strict sign, drop the smaller-|points| member; deadband unchanged at |score| ≥ 3;
post-scan grading; H26's n=29 sample.

| basis | C | W | no-call | rate |
|---|---|---|---|---|
| published | 13 | 9 | 7 | **59.1%** |
| collinearity-collapsed | 10 | 9 | 10 | **52.6%** |

Scores changed on **23 of 29** days, the call on **5** — **3 hurts** (09-18,
10-06, 10-19 all correct → no-call) against **2 helps** (10-12 no-call →
correct, 10-15 wrong → no-call). **The collinearity is structurally real and
directionally harmful to act on.** This is the same shape as the 10-21
duplication-collapse result and it is recorded so the fix is not re-proposed.
Opened as **H27** below with nothing attached to it.

**Thresholds not met, recorded and still observing:**

- **H26** — n=29. ≥10 bucket **3C/3W → 3C/4W = 42.9%**, now **below a coin flip
  and below every other scoring bucket** (3–5: 57.1%, 6–9: 75.0%). Direction by
  bucket is **inverted at the top**. Magnitude bucket means **re-derived from
  source** (not arithmetic off rounded figures): **0.181 / 0.339 / 0.532 /
  0.704** — **monotonic, 7th consecutive session, survives**. The derivation
  reproduces the register's n=28 bucket counts and three of four means exactly;
  **the published 6–9 figures have drifted** (|post|/ADR 0.517 vs source 0.532;
  range/ADR 1.134 vs source **1.032**). On the source figures the **range/ADR
  bucket form is NOT monotonic** (1.103 / 1.132 / **1.032** / 1.279) and was not
  at n=28 either. Spearman(|score|, |post|/ADR) **+0.525 → +0.479**;
  (|score|, range/ADR) **+0.085 → −0.007**.
- **M6 — session 31, and the driver is NOT window placement.** The 12-bar
  `REACT_BARS` window captured the true excursion on **7 of 7** touched rows.
  The understatement comes entirely from `settled_read` measuring
  `worst_excursion` from `settled_from` rather than from first touch. **4 of 7
  verdicts inverted by the close**: 28921.0 / 28888.5 / 28860.5 / 28853.1 all
  read `acted_as: "lost"` with `settled_side: "above"`, on a session that closed
  **+78.2 / +110.7 / +138.7 / +146.1 above them**. Worst ratio **6.26x**
  (28981.6: reported −11.7, true −73.2). **Session 30's "travel-scaling" driver
  takes a fourth consecutive counter-instance and is not restated.**
- **D7 — CONTROL, both limbs clean.** Budget 294.6 (non-zero), board **15 rows**.
  `far` held **5 rows against a cap of 6**, so `rest[:cap − len(walls)]` dropped
  nothing and the descending-price sort had no victim. All five footnote rows
  were above price; no below-price level was demoted. (Correction to the task
  brief: the 10-23 footnote has **five** entries, not two, and the board was not
  short.)
- **D26 — the held-back set rotated AGAIN, and the sample shrank.** `track.py`
  now prints **29 days / 30 scans** against the 10-23 run's **31 / 34**. Three
  calendar days passed, the 45-day window slid, and **09-08, 09-09 and 09-10
  dropped out of visibility entirely while 09-11 joined `HELD BACK` at 96 bars**
  — a day completed seven weeks ago, filed *"day not finished"*. On disk:
  **40** day directories, **70** scan JSONs, **35** days with a PRE_NY scan
  (all `is_trading_day: true`), **34** with a `REVIEW.md` (**35** after this one).
  Reconciliation: 40 − 9 silently invisible (08-23 … 08-28, 09-08, 09-09, 09-10)
  − 2 held back (09-11, 10-26) = **29**. Exact.
  **P4/H1 figure conflict, reported not resolved:** the live print is **+53.9
  (n=29 days) / +54.8 (n=30 scans)**. It cannot be reconciled with the register's
  **+45.4 (n=31)**, the 10-23 live print **+58.6 (n=31)**, or the **+51.9 (n=30)**
  figure passed by the runner. **Four numbers, one series name, and the sample
  under them changed three times.** Flagged, not averaged.
- **P4 / H1 — n=29 (the day count went DOWN).** 10-23's point: budget **294.6**,
  extension **78.8**, error **−215.8** — **the largest over-estimate in the
  record, on the largest budget in the record.** The *"big budgets over-read"*
  story was checked a third time and **still fails**: the eight visible
  budget≥200 scans run +25.9 / −75.2 / −66.5 / −180.1 / **+479.3** / −17.7 /
  −149.8 / −215.8, mean −25.0, both tails intact. The register's earlier figure
  (+16.3) is **not comparable** — that eight-scan set has itself rotated.
- **H2 — NO instance, and a useful control.** Fuel **MODERATE**, `fuel_ratio`
  **1.03**, the most normal pace in the record; `track.py`'s low-fuel list does
  not carry 10-23. Census stays **6–2 / 8–0 to the gamma block, FALSIFIED**.
  **Mechanism confirmation:** §3 stop management read *"structural stop;
  break-even at 1R or 50% of remaining budget"* with **no fade instruction**, so
  the two-opposite-instructions contradiction that fired on 10-19, 10-21 and
  10-22 **did not fire here**. That isolates the contradiction to the
  LOW_FUEL/EXHAUSTED branch — which is exactly the cell H2's live proposal
  targets.
- **P-F — NOT a treatment instance.** Price 28875.7 sat **15.2 above PDL
  28860.5**, inside the prior-day range, so the >150pt trigger did not fire.
  Treatment set stays at **4 of 4 positive, mean +267.8**. Logged as one
  **inside-control** observation (error −215.8); **the control is not
  re-derived.**
- **D27 — 3rd consecutive session.** `gexbot` HTTP **401** on
  `/v2/NDX/classic/gex_full` on the 10-22, 10-23 **and 10-26** scans. Both
  ladder files lost each time (`gexbot.py:219`) while the printed message names
  only the volume-weighted view. **D25 interrupted at 29, not reset.** Nothing
  proposed: no credential change, no retry policy.
- **D23 — NO 17th residual.** Section 7 did not render (D27), so there is no
  section-7 offset. Series stays at **16** and **is not extended with an inferred
  figure**. Board offset **−11.0**: not a breach; breach series stays at five.
- **Realised-close-basis log — observation 8 of 10, and it DOES discriminate.**
  NDX cash close 10-23 = implied **29108.5** (10-26 scan) − roll **(+151.0)** =
  **28957.5**; CFD close **28999.2**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-20 | +74.5 | 29490.3 | 29703.2 | +212.9 | 138.4 | **+208.5** |
  | 10-22 | +15.7 | 28958.7 | 28921.0 | −37.7 | 53.4 | −72.0 |
  | **10-23** | **−11.0** | **28957.5** | **28999.2** | **−41.7** | **30.7** | **+151.0** |

  This is **the up-roll condition 10-22 could not supply**, at 72% of 10-20's
  roll size, and the gap is **30.7 — the second-smallest in the log**, against
  10-20's 138.4. **The "up-rolls break the basis" story does not survive it; the
  anomaly localises to 10-20 itself or to the anchor.** n=2 on up-rolls. The
  roll parser is still sign-blind and **no |roll| regression is quoted.**
- **H18 / P1 — instance 25, duplication 30 of 30.** `macro 0` DFII10 (obs
  2026-10-21, ⚠️ printed) and `macro −1` DGS10 (2026-10-20 → 2026-10-21, **no
  ⚠️**): same instrument pair, same window, one warning between them. **HY OAS
  rendered no observation date for the 18th consecutive session.** The pair
  carried **−1 of a −16 call**; age-gating it gives −15, same label, same side,
  same wrong verdict — **a clean null, logged as neither help nor hurt**
  (stays 4 helped / 3 hurt raw, 3/3 magnitude-respecting). **HY OAS scored 0
  (+2bp over 5 days) after six consecutive sessions of widening** — the row went
  quiet rather than dead, and it was the only macro row not to cast a wrong vote.
- **H22 — range label WRONG at n=15**, ending a two-session run of right reads.
  Week net GEX **−6.927** → *"expansion likely"* → realised **0.608x ADR**, a
  contraction, and the **smallest range/ADR of any ≥10-score day**. Direction
  half not re-run (stays 15/11 = 58%, n=26).
- **H8 — post-closure, clean.** Straddle 414 (ATM IV 33.9%) → EM ±352 → band
  **28524 .. 29227**. Close 28999.2 **INSIDE**, and the whole session H/L stayed
  inside. VXN-implied range **over**-read by 187.4 — **4th counter-instance** to
  *"use the VXN-implied range as the budget"*, opposite sign to 10-22's 505.7
  under-read. Not revived.
- **P-B(b) — 20th session, and a guaranteed window FIRED.**
  `merge_tol = max(3.0, 550.8 × 0.008) = **4.41**` against `TOUCH_TOL = **8.0**`
  → guaranteed window **(4.41, 8.0]**. The board's smallest gap is **7.4**
  (28860.5 / 28853.1) — **inside it** — and both rows plus 28888.5 first-touched
  in the **same 12:50Z bar**. Published **7/15 = 0.467**; distinct touch bars
  **5** → **0.333**; **inflation 1.40x**. Proposal unchanged.
- **D18 / H19 — instance 17, 10th trading day.** `[risk_on]` on *"TSX futures
  **slip** as oil rally adds to inflation worries"* — bearish text, bullish tag,
  first-match-wins. **Damage zero only because `risk_on` is absent from
  `HIGH_CONFIDENCE`** (confirmed in `news_scorer.py`), the same asymmetry that
  did the damage on 09-18 and the same reason the half-fix stays priced as
  harmful. **H19 coverage 1 / 134 = 0.75%, the lowest in the record.**
- **P-C — 2nd Medium-cluster instance.** `event_gate` requires
  `impact == "High"` within 1.5h, so **four Medium prints at 13:45–14:00Z**
  produced `event_gate: null`. Correct per code — and the session **low landed at
  13:35Z, ten minutes before the first print, and the high at 14:50Z**. The
  entire 335pt range was carved around data the gate ignores by construction.
  n=2 (09-29, 10-23). Mechanism already logged as P-C; **nothing proposed.**
- **P-G — instances #28, #29, #30.** *"the next session usually runs the stops
  **below** it"* printed on **29333.8** (+458), **29243.2** (+368) and
  **28888.5** (+13), all sitting **above** price. The first two were never
  reached; on 28888.5 the stops below it were in fact run. Prose only, already
  PROPOSED.
- **P-E / P-E(b) — instance #17, and it SPLITS.** CALL WALL **+513**, never
  reached, 233.6 above the post-scan high → no P-E instance. P-E(b): on the
  **downside the headline PUT WALL won** (31.4 from the low, against the nearest
  secondary shelf's 131.4) — **the first downside counter-instance**; on the
  **upside the shelf won** (29089.0 at 66.4 from the high, against the call
  wall's 233.6). First split reading.
- **P3 / H6 — structural CALL wall untouched again**, 533.6 away, still **0
  gradeable touches ever**. The 10-08 narrowing (*"stop publishing it"* applies
  to the structural **call** wall only) is reinforced. No structural put wall was
  published. Separately, **`TOUCH_TOL = 8.0` filed the day's single best level —
  the put wall at 31.4 from the low — as *"never reached"***; the touched/
  never-reached binary loses a wall that located the extreme to 0.057x ADR.
- **Session-context field — 20th session.** Pre-scan range **28853.1–29109.3**.
  **7 of 15** marked rows lie inside it, **9 of 24** counting the footnote and
  secondary table, under the banner *"New trading day… everything below is
  fresh."* Proposed 09-29, still not actioned.
- **Dead-weight audit — refreshed from source, n=33** PRE_NY `is_trading_day`
  scans (09-24 and the unfinished 10-26 excluded):

  | row | scored |
  |---|---|
  | `macro` yield curve (10y–2y) | **0 / 33** |
  | `events` | **0 / 24** (row absent on 9 scans — P-C) |
  | `rates` DXY | 4 / 33 |
  | `macro` WALCL/RRP | 4 / 33 |
  | `macro` NFCI | 5 / 33 |
  | `rates` US10y | 25 / 33 |
  | `macro` HY OAS | 25 / 33 |

  **This does not reconcile with the register's hand-maintained n=34** and the
  discrepancy is flagged rather than papered over; the substance is unchanged, so
  the narrowed standing proposal (drop the yield-curve row and WALCL/RRP) is
  **unchanged and still not actioned**.
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26) · **H4** (flip
  546.0 above the post-scan high) · **H7** (no overnight scan) · **H10**'s own
  reclaim branch (no reclaim existed at scan time) · **H11** · **H12 / H13**
  (volume ladder lost to the 401) · **H14** (the put wall never broke) · **H17**
  (post-scan **37.2%** of the session range, far outside the 5% deadband; stays
  2 of 3) · **H20** · **H23**'s brake census (both paths clear; stays **11
  sliced / 3 capped / 3 never-reached**, force-ranking **CLOSED**,
  corridor-terminus **WITHDRAWN**) · **D9** (the one scored headline carries its
  subject) · **D24** (`event_gate: null` correct; all four events forward) ·
  **the gamma-outvote cell** (gamma and the rest both negative — no outvote;
  stays n=5) · **the "direction call vs strategy block" cell** (both bearish;
  stays n=2).
- **`PIN_THEN_EXPAND` — did NOT fire on 10-23** (`COHERENT_SHORT`). **Stays
  observation 2 of 3; no verdict, not revised.**
- **"Whole move over by 10:30 ET" watch item — near-instance, does not extend.**
  Low **09:35 ET**, high **10:50 ET**: the entire 335pt range was set in the
  first 80 minutes of cash, but the high is 20 minutes past the clause.
  Recorded as written; n unchanged.
- **No new data point is warranted.** Every failure today traces to the
  *dependence structure* or the *vintage* of rows already on the page — two
  correlated pairs, a prior-week rule with no distance term, a vol block with no
  mean-reversion term, and 0.75% news coverage. No free, reliable feed fixes any
  of those.

---

## Carried forward from the 2026-10-26 scan — recorded, NOT graded

- **`PIN_THEN_EXPAND` FIRED AGAIN. That is observation 3 of 3 and it COMPLETES
  the pre-registered test.** Observations 1 (10-19) and 2 (10-21) both
  **FALSIFIED** it on the same clause. **The verdict the 10-19 pre-registration
  calls for at n=3 is DUE at the next review.** Run clauses 1–4 on the
  **unrevised** rules against 10-26's bars first, then deliver the verdict.
  **Do not let this slip.**
- **BEARISH −6** at **29138.0**, offset **+29.5** (clean), roll **+151.0**
  (up-roll), fuel **MODERATE** `fuel_ratio` **1.34**, gamma flip **29489.2**,
  week net GEX **−2.141**.
- **News relevance failure, −1 of a −2 news score.** *"Apple stock rally and
  Nvidia sell-off tighten race for world's most valuable company"* tagged
  **hawkish → bearish long-duration tech**. It is a company-ranking story with
  **no Fed content**. The hawkish theme is independently real — the judgement
  list holds three genuine Fed-hike stories — so the *score* may be defensible
  while the *reason printed for it* is false. Grade both separately.
- **`gexbot` HTTP 401 for the 3rd consecutive scan** (D27); **`gamma +2`
  bottom-of-band fired a 7th time.**

## Journal hygiene

One scan file for 10-23 (`1248-preny.json` + `.md`), `is_trading_day: true`,
275 bars, **0 test artefacts** for the day (6 across the record, excluded by
`track.py`). **09-24 quarantined by hand — 19th consecutive review to carry it**;
there is still no schema `quarantine` field and the 09-29 proposal for one is
reaffirmed. **2026-10-13 has no journal directory — documented, not recreated.**
**09-09 and 09-25 still have no `REVIEW.md` and none was created or back-dated.**
**2026-10-26 is on disk, `is_trading_day: true`, 181 bars, correctly held back
and NOT graded.** **No `prediction` block was touched. No scoring, wall or
grading code was edited.** No fabricated or backfilled entries found.
**One new ID allocated by this review: H27. Next free: H28 · D28 · P-I.**
`track.py` prints **no literal `actionable: YES/NO`**; the threshold rule was
applied by hand.
