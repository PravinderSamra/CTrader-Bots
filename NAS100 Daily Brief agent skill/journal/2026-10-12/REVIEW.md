# REVIEW — 2026-10-12 (Monday)

_Graded 2026-10-14 from `review_day.py 2026-10-12 --json` and `track.py`. One
PRE_NY scan, `is_trading_day: true`, 0 test artefacts. **There is no
`2026-10-13` journal directory — Tuesday's scheduled scan never ran. Nothing was
created, back-dated or inferred for it; the series legitimately skips a day.**_

## 1. Scoreboard

| | |
|---|---|
| Session (21:00Z roll, 276 M5 bars) | O **30919.3** / H **31079.0** / L **30634.7** / C **30669.5** |
| Range / net | **444.3** (1.015x ADR14 437.9) · net **−249.8** |
| Scan | PRE_NY 12:48:38Z at **30843.5** · bias **+2 NEUTRAL / TWO-WAY** · `expected_direction 0` |
| Direction | **0 right / 0 wrong / 1 no-call.** Post-scan move **−181.3** (P-H basis, applied), day net **−249.8** — both bases agree in sign, so **no P-H deciding instance**; census stays n=3 |
| Post-scan path | H **30877.4** (13:05Z) → L **30634.7** (18:50Z) · traversal **242.7** |
| Levels | **17 published, 6 touched, hit rate 0.35** |
| Fuel | budget **169.5** · extension **175.9** · err **+6.4** (ratio 1.04, *"about right"*) · traversal **242.7 = 1.43x** budget |
| Vol boundaries | VXN-implied range **399.3** vs realised **444.3** → under by **45.0** (1.11x). Straddle EM band **30666 .. 31021**, close **30669.5 — INSIDE by 3.5**, both extremes outside |
| Blocks | vol **+3** · macro **+3** · gamma **−2** · structure **−2** · breadth **+1** · news **−1** · rates/fuel/events **0** |

## 2. What the levels actually did

**Touched (6).**

| level | dist | brief said | what happened | verdict |
|---|---|---|---|---|
| **30876.7 GAMMA FLIP** | +33 | *"we're BELOW it: they're pushing, don't fade. Reclaim and hold above and fading becomes valid"* | touched 13:00Z, exceeded by **0.7pts** across the whole post-scan session (490min), then **−149.9** | **right, and the cleanest row on the board** |
| **30843.1 PUT WALL ●●●●● 1.19bn** | at price | *"heaviest floor this week"* **+** *"if it breaks, expect it to speed UP, not bounce. Don't buy the break"* | chopped both sides, settled below from 13:20, ran **208.4 (0.48x ADR)** to the low, closed **173.6 below, never reclaimed** | headline **wrong**, regime rider **right** |
| **30820.8 London Low (today)** | −23 | *"the next session usually runs the stops below it"* | broke down, 172.3 of travel below | right |
| **30798.9 Equal lows ×3** | −45 | *"a real stop cluster. **Prime S1 sweep trigger**"* | swept, chopped (worst +23.6), then **−150.4** | sweep right, **the S1 fade it recommends was the wrong trade** — the same brief's strategy line says so |
| **30772.2 NY Low (prev-day)** | −71 | *"runs the stops below it"* | the only **"lost"** verdict: 50.3 of retrace above it, day closed **102.7 below** | see M6 in §3 |
| **30732.4 PDL + Asia Low ⭐** | −111 | *"sweep it, wait for a higher low, then CISD = **long**"* | swept at 13:30Z and kept going **97.7 further**; 4 re-tests, all capped (worst +20.1) | **the long instruction would have been run over** |

**Untouched (11).** Three were never in play: CALL WALL 31343.1 (+500, **466
above the session high**), PWL 30568.7 (missed by 66.0), MAX PAIN 30043.1 (−800
= **1.83x ADR14**, and on a Monday — the row's own text calls itself *"weak on a
Monday"*: **7th consecutive distance-confounded publication, and the only row
today that is honestly noise**). The other eight — Asia High 31079.0, PDH
31045.0, London High 31004.3, Asia High prev 30995.5, NY High prev 30958.7, Asia
Low today 30948.3, PD close 30906.9, PD mid 30888.7 — are **not forecasts**:
price had already traded them before the scan and never came back. The 0.35 hit
rate measures placement, not quality (standing 09-18 caution).

**Secondary gamma table (published, graded by no tool — P5).** All three put-side
shelves carried *"dealers are SHORT gamma here, so they **amplify** … Not a
floor"*. **30743.1 sliced** (worst +9.4 after), **30693.1 sliced** (worst +7.9),
**30643.1 did NOT** — the session low **30634.7** is **8.4pts** below it, price
settled above for 110min with 2 re-tests (worst −3.9) and closed **26.4 above**.
**2 of 3 right, and the one that was wrong is the exact price the fuel section
named as the end of the "clear" corridor.**

**Fuel paths.** *"DOWNSIDE: clear … every shelf to 30643.1 is negative gamma —
nothing structural to slow a breakdown. If it goes, it has room. Do not fade
it."* — **right**, and the corridor terminus landed within **8.4pts** of the
session low. *"UPSIDE: stall at 30943.1"* — **never reached** (post-scan high
30877.4, missed by **65.7**), and **30943.1 occurs exactly once in the whole
document** (line 108): not on the level board, not in the secondary table. Same
defect as 10-09's 30900.7.

## 3. What was wrong, and why

**The call. "Two-way" described the morning and mis-described the day.**
Post-scan the session was one-way: high at 13:05Z, **+33.9** above the scan,
then **242.7 straight down** over five hours, closing 34.8 off the low. The
268.4 of two-way range the brief measured all happened **before** the scan. Cost
of the no-call: **181.3pts = 0.41x ADR** in the direction the gamma block named
— the opposite of 10-09, where the identical label cost ~0.

**Trace by component** (`inputs.bias_components`):

| block | pts | verdict |
|---|---|---|
| `vol` | **+3** | **wrong on both clauses.** *"VXN 20.55 (−6.5%) — fear falling, bullish"* +2 and *"VIX9D/VIX 0.727 contango — calm, mean-reversion favoured, mild upward drift"* +1, on a day that fell 249.8 with a 1.015x-ADR range. Largest wrong block |
| `macro` | **+3** | **DFII10 +3 and DGS10 +1 are the same FRED observation date, 2026-10-08** — two business days stale, under a document headed *"today"*. H18/P1 instance 17; duplication **22 of 22** |
| `gamma` | **−2** | **had the day right and was halved by its own two positive riders.** Raw rows: −3 below flip, −2 week net GEX. Riders: **+1** straddle (D16/P-A) and **+2** bottom-of-band (D21 mirror). Gamma without the riders is **−5** |
| `structure` | **−2** | **right** — below PD mid, *"3 pools above / 4 below → draw lower"*, and the day drew lower |
| `breadth` | **+1** | *"NDX +0.51% vs ES +0.02% — tech leading, genuine risk appetite"* is the **previous** session's closes (D22, and the window is still not recorded). Wrong |
| `news` | **−1** | **accidentally right-signed off a misread headline** — see D18 below |

**Minimal counterfactual.** No single row flips the call. Removing the stale
DFII10 **+3** alone gives **−1**, still NEUTRAL (`MILDLY BEARISH` needs ≤ −3).
Removing **DFII10 +3 and bottom-of-band +2** gives **−4 → MILDLY BEARISH**, the
correct side. That pair is the whole margin between a no-call and a correct
directional call.

**The regime determination was formally undetermined, and it was right anyway.**
Price 30843.5, flip 30876.7 — **33.2pts below** — on a board whose CFD/index
offset was **43.1**. The regime test is a sign test on `price − flip`, and
**33.2 < 43.1**: at a zero basis the same scan reads **9.9 ABOVE** the flip and
the engine selects **STRATEGY 1 (fade)** instead of STRATEGY 2. The two
strategies are opposite instructions and STRATEGY 2 was worth ~180pts. The
conversion arithmetic was independently verified at scan time (Friday cash close
30883.15, NQ roll-forward, no contract roll), so **43.1 is a real CFD-vs-cash
basis, not a conversion fault** — which is what makes this a measurement problem
rather than a bug. **Census: this configuration has occurred once in 30 PRE_NY
scans carrying both a flip and an offset** (`|px−flip| < |offset|`); the next
closest are 09-30 (69.6 vs 37.7) and 10-07 (82.6 vs 25.8). The outcome was right
— the flip was touched and rejected by 0.7pts and price fell 149.9 — but being
right on a sign test whose input uncertainty exceeds its margin is **luck, not
method**, and is recorded as such.

**The put wall "at price" is untestable on this day.** 30843.1 against a price
of 30843.5. At a zero basis the same strike converts to ≈30800, which is within
**1.1pts** of Equal lows ×3 at **30798.9** — and **both prices produced the same
behaviour**: chop with a ~24pt adverse excursion, then a break (worst +24.1 and
+23.6 respectively). The session cannot discriminate between the two placements,
so the wall gets no credit for precision the day did not test.

**M6 — session 23, and the day gives the artefact its full scale.** All six
touched rows sit **above** the close, so all six verdicts are decided by
`bars[-1]["close"]` before any level behaviour is consulted; five read *"held as
resistance"*. Worst excursion against distance-below-close: 0.7/207.2 · 24.1/173.6
· 1.7/151.3 · 23.6/129.4 · 50.3/102.7 · 20.1/62.9 — mean ratio **0.19**. The day
travelled 444.3 (1.015x ADR), so this is **not** the muted version a quiet day
produces; the understatement is at full scale. The single *"lost"* verdict,
**30772.2 — "broke UP through it — lost by 50.3pts"** — is awarded to a level the
day broke **downward** by 137.5 and closed **102.7 below**: the grader is
measuring the retrace, because `held` is derived from the close side. **Only the
GAMMA FLIP (+0.7 over 490min, two rejected re-tests) is a verdict the close did
not manufacture.**

## 4. Change proposals

### Proposed (one) — give the put-wall break rider a measured horizon

**What.** `brief.py`'s put-wall note currently asserts *"if it breaks, expect it
to speed UP, not bounce. Don't buy the break."* with **no horizon and no base
rate**. Print the measured record instead of (or beside) the assertion.

**Evidence — 3 sessions, same wall family, same rider, all below the flip:**

| session | PUT WALL | run-through before any reclaim | x ADR14 | reclaimed same session? |
|---|---|---|---|---|
| 10-07 | 31025.8 (−6) | 107.8 | 0.23 | yes — closed **+146.8 above** |
| 10-08 | 30709.6 (−248) | 140.9 | 0.31 | yes — closed **+81.9 above** |
| **10-12** | **30843.1 (at price)** | **208.4** | **0.48** | **no — closed 173.6 below, never reclaimed** |

**Expected effect: zero on any score.** The note is prose; `bias_engine.py` does
not read it. Two things change for the reader: the acceleration claim acquires a
target (**0.23–0.48x ADR, n=3**), and the implied one-way outcome is corrected —
**2 of 3 breaks reclaimed within the session**, so the rider must stop reading as
a trend promise. This also closes out the "missing field" named without an ID on
10-07 and again on 10-08.

**No new ID.** This is **H14's open empirical half** — *"whether a put wall acts
as resistance-after-break in short gamma"*, which H14's own fix note said needed
two more sessions. They have arrived, and **the claim fails at n=3: 1 for
(10-12) / 2 against (10-07, 10-08)** — and the one "for" is close-side derived
(M6), so it is the weakest of the three.

### Not proposed — threshold reached, evidence null or mechanism-only

- **"The gamma block was right and outvoted into a no-call" — now n=3** (10-08,
  10-09, 10-12), all three NEUTRAL / TWO-WAY. The quantity pre-registered on
  10-09 (`gamma` minus the sum of all other blocks, against realised
  `|post-scan move| / ADR`) reads **−9 → 671pt trend day**, **+10 → 0.07x**,
  **−6 → 0.41x**. Three points, and the magnitude does not order the outcome.
  The fix would be a **weight change**, which is exactly the kind of tuning three
  judgement-coded points cannot support. **Nothing proposed.** Keep logging the
  pair.
- **The `gamma +2` bottom-of-band branch — 4 firings in the whole record, and
  4 of 4 fired BELOW the flip in short gamma** (08-24, 09-14, 10-07, 10-12).
  Mechanism: the branch can only fire near the **put wall**, and in a negative-GEX
  book that is precisely where the same brief's wall note says the floor will not
  hold — **the score and the prose of the same component give opposite
  instructions, 4 times out of 4**. But the outcomes on the post-scan convention
  are **2 right (09-14, 10-07) / 2 wrong (08-24, 10-12)** — **null**. Count
  threshold met, evidence points nowhere. **Nothing proposed.** (This is also the
  2nd instance of *"the gamma component voted against its own location row"*,
  opened 10-07 at n=1 — and today it is the mirror: the location row was wrong
  and the two it outvoted were right. 1-1.)
- **Board-offset drift — n=2, below threshold.** 10-12 **43.1** and 10-14
  **41.8**, two consecutive breaches of the D6 ~40pt line, against 0.7 · 9.6 ·
  25.8 · 7.6 · 8.1 · −3.3 · 36.0 · 37.7 on the eight prior sessions. **Nothing
  proposed on it.** Pre-registered: if a third consecutive >40 offset prints,
  measure it against the same session's cash close before proposing anything.
- **Regime-undetermined — n=1 of 30.** Pre-registered test, written before the
  next occurrence: when `|px − flip| < |offset|` next prints, record whether the
  regime read was right **before** looking at anything else. One instance is not
  a case for a guard.

### Observations appended, no proposal attached

- **P4 / H1 — n=25 days.** 10-12's error **+6.4** is the **smallest absolute
  budget error in the entire record**. It changes nothing: `track.py` per-day mean
  **+17.3** (n=25, includes 09-24); **ex-09-24, n=24, +17.5**. The statistic is
  **not re-derived** — P4's answer stands (MAE 116.1 vs leave-one-out constant
  98.3, n=19; ex-09-21 90.9 vs 75.5, n=18; sign agreement 9 of 19; correlation
  sign outlier-driven, so the claim is **"no usable skill"**, not "inversely
  predictive"). **H1's multiplier branch stays closed.** One bullseye on a
  question already answered negative is noise, logged as noise.
- **D26 — reporting bug, not data loss, and the earlier claim is withdrawn.**
  `track.py` today shows **25 trading days / 28 scans**, window opening 09-08. On
  disk: **32 day directories, 62 scan JSONs, 27 days with a PRE_NY scan, 26
  `REVIEW.md`, 23 days holding both.** The five hidden August trading days —
  **08-24 (8 scan JSONs), 08-25 (2), 08-26 (4), 08-27 (5), 08-28 (1) = 20 files**
  — plus their 5 REVIEWs are **all intact**. The 45-day bar window hides them; it
  does not eat them. *"The P4 sample no longer exists"* is **wrong and retracted.**
- **D23 — 10th residual, and the two conversions disagreed in SIGN.** Board
  offset **+43.1** (NDX ref 30800.4 vs CFD 30843.5, basis `nq_implied`, greeks
  `repriced_bs_at_current_spot`); section-7 offset **−40.7**, matched to feed time
  11:59Z. Gap **−83.8**; CFD move (11:55Z bar open **30859.3** → scan 30843.5) =
  **−15.8**; **residual −68.0**. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 /
  +246.6 / +203.6 / +209.5 / +345.4 / −68.0`. Third-smallest |residual| — and it
  arrives the day after the largest (+345.4 on 10-09, which came on the
  **smallest** board offset of the week, 0.7). Extended as a new data point; **not
  re-measured**. Damage none (section 7 is research-only, no volume had traded).
- **D25 — 23rd consecutive pre-NY scan.** *"The dominant strike is stable at 0
  across 6 samples — positioning is settled there"*, printed three lines under
  *"No volume has traded yet today"*, with the strike rendered as literal **0**.
  Damage none.
- **D18 — 7th trading day, 13th headline instance, and the clearest negation
  failure in the record.** The **sole** auto-scored headline was *"Fed officials
  want to **hold off** a rate hike this month…"*, tagged **[hawkish] 🔴 bear,
  "Hawkish repricing → bearish long-duration tech", −1.80**. *Holding off a rate
  hike is dovish.* The scorer matched `rate hike` and did not read `hold off`.
  That one row **is** the entire `news −1`, and it was **accidentally right-signed**
  on a down day — the worst possible outcome for a defect, because the result
  argues for keeping it.
- **H19 — coverage 1.85%**: 139 headlines → 54 relevant → **1** auto-scored, 53
  left for judgement.
- **H18 / P1 — instance 17; duplication 22 of 22.** DFII10 (+3) and DGS10 (+1)
  both resolve to observation date **2026-10-08**. The brief **did** print the age
  warning on DFII10 and did **not** print one on DGS10. **HY OAS rendered no
  observation date for the 8th consecutive session** (*"3.15% (−9bp over 5
  days)"*). The accuracy case stays retracted.
- **H8 — observation 8 of 10.** Straddle 209pts (ATM IV 8.9%) → EM ±178 → band
  **30666 .. 31021**. Close **30669.5 — INSIDE by 3.5pts**; high 31079.0 and low
  30634.7 both **outside**. Record **7 inside / 1 outside**.
- **H22 — n=7.** Week net GEX **−1.074** — the **smallest magnitude in the
  series** — carrying *"expansion likely"*; realised range **1.015x ADR**,
  extension 1.04x budget. Mildly expansionary, i.e. the weakest reading produced
  a near-average day. **Still no ordering.**
- **H4 — 3rd consecutive clean flip read, and the best one.** Touched, exceeded
  by **0.7pts** over 490 minutes, 3 re-tests, then −149.9. STRATEGY 2 was right.
- **H23 — 10th instance, and it is "never reached".** Named upside brake
  **30943.1** at +100; post-scan high 30877.4, missed by **65.7**. No slice/cap
  data point, so the census **stays 8 sliced / 1 capped, n=9 over 6 sessions**.
  What it does add is the **2nd instance of the sub-claim**: the named brake
  appears **nowhere else in the document** — not on the board, not in the
  secondary gamma table — exactly as 10-09's 30900.7. The standing H23 proposal
  (rank `path_read()`'s brake by gamma force, or print both, and never name a
  brake the board does not print; `brief.py:486`, rendered at `:558` and `:1024`)
  is **unchanged and still live**.
- **P-G — instance #18.** Two *"Low"* rows published **above** the scan carrying
  *"the next session usually runs the stops **below it**"*: **Asia Low (today)
  30948.3** at **+105** and **London Low (prev-day)**, merged into the 30958.7
  row, at **+115**. Both were already behind price; neither was revisited.
- **Session-context field — 12th session. 11 of 17 published rows had been
  traded before the scan**, under the banner *"New trading day … everything below
  is fresh"*. Touch-bars pre-scan: London High 31004.3 (**35**), Asia High prev
  30995.5 (**32**), NY High prev 30958.7 (**32**), PDH 31045.0 (**25**), GAMMA
  FLIP 30876.7 (**24**), PUT WALL 30843.1 (**21**), Asia Low today 30948.3
  (**20**), PD mid 30888.7 (**17**), London Low today 30820.8 (**7**), PD close
  30906.9 (**4**), Asia High today 31079.0 (**3**). Notably the PUT WALL and the
  GAMMA FLIP — the two rows the whole regime call rests on — had each been traded
  for ~2 hours before the board printed them as forward-looking.
- **P-B(b) — 16th session; no instance.** `merge_tol = max(3.0, 437.9 × 0.008) =
  **3.50**` vs `TOUCH_TOL = **8.0**`. **No published pair fell in the guaranteed
  double-count window**; the closest was 31004.3 / 30995.5 at **8.8**, missing it
  by 0.8. Inflation **1.00x**. The proposal is unchanged — today is simply a clean
  board.
- **Dead-weight audit, refreshed — n=28 PRE_NY `is_trading_day` scans, 09-24
  excluded by hand.** `macro` yield curve 10y–2y **0 / 28 — still has never
  scored**; both `fuel` rows **0 / 28**; `vol` VVIX **2 / 28**; `rates` DXY
  **3 / 28**; `events` absent or zero throughout (P-C). The standing proposal
  stays narrowed to the **yield-curve row and WALCL/RRP**. `macro` NFCI fired
  **−1 for the 4th consecutive graded session** — the 10-07 decision to return it
  to observation rather than drop it continues to look right.
- **Max pain — 7th distance-confounded miss**, −800.4 = **1.83x ADR14**, the
  largest in the series, and on a **Monday**, the day the row's own text calls
  weak. The day-of-week claim stays ungradeable.
- **No instance:** **H2** (fuel MODERATE, not LOW_FUEL/EXHAUSTED — the cell was
  never entered). **H3** (no max-conviction call; score +2). **H7** (no overnight
  scan). **H10** (`structure 0`, price inside the prior-week range
  30568.7–31385.1 — but the 4th consecutive proximity gap: the session low came
  within **66.0** of PWL and the rule scores that identically to a mid-range day).
  **H17** (no-call; post-scan move 181.3 = 40.8% of range, far outside the 5%
  deadband). **H20** — `events_24h` empty, *"No High/Medium US events in the next
  24h"*; **stays CLOSED-NEGATIVE, not revived**. **D24** — unfalsifiable, no
  forward events at all. **D21** — the top-of-band −2 branch did not fire (the
  bottom-of-band +2 did; see §4). **P-E / P-E(b)** — CALL WALL 31343.1 published
  **466 above the session high** and never in play; the upside shelf 31143.1 the
  same. **P-E is a continuum, not bimodal**, and no two-mode framing is attempted.
  **P3 / H6** — no structural rows on the board; census unchanged.
- **Pre-scan contamination, stated explicitly (P-E discipline):** of the six
  levels that reacted, **three were published after price had already traded them
  today** — GAMMA FLIP (**24** touch-bars pre-scan), PUT WALL (**21**), London Low
  today (**7**) — so the reaction credited to them is not a clean forward test.
  The other three are **clean, 0 pre-scan touch-bars, published before the move
  credited to them**: Equal lows ×3 (30798.9), NY Low prev (30772.2) and PDL
  (30732.4). The three secondary shelves (30743.1 / 30693.1 / 30643.1) are also
  clean on this test.

## Journal hygiene

One scan file for 10-12 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 11th consecutive review to
carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` continues to print 09-24 inside every
statistic it reports. **2026-10-13 has no journal directory — the scheduled scan
never ran. No entry was created, nothing was back-dated, and no observation was
inferred for it; the gap is recorded here so the skip from 10-12 to 10-14 is not
later mistaken for data.** **09-09 and 09-25 still have no `REVIEW.md` and none
was created.** No `prediction` block was read-modified-written, and no scoring,
wall or grading code was edited. No fabricated or backfilled entries found.
**No new IDs allocated by this review; next free remains H26 · D27 · P-I.**
