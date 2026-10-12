# REVIEW — 2026-10-09 (Friday, expiry)

Graded 2026-10-12 from `review_day.py 2026-10-09 --json`, `track.py`, the scan's
own `1249-preny.json`/`.md`, and the M5 bar series. Direction is graded on the
**post-scan basis** per P-H. 09-24 is **quarantined and excluded by hand** from
every statistic below (10th consecutive review).

## 1. Scoreboard

| | |
|---|---|
| Session O/H/L/C | **30799.9 / 31045.0 / 30732.4 / 30906.9** |
| Range | **312.6** = **0.65x** ADR14 484.0 · net **+107.0** · 275 bars |
| Scans | 1 (12:49:18Z PRE_NY, `is_trading_day: true`, 0 test artefacts) |
| Published call | **NEUTRAL / TWO-WAY, score −2** → `expected_direction 0` |
| Direction | **no call** (0 right / 0 wrong / 1 no-call). Post-scan **−35.3**; day net **+107.0** — **the two bases disagree in sign** |
| Post-scan session | O 30942.2 / H **31001.7** (13:15Z) / L **30772.2** (14:10Z) / C 30906.9 |
| Post-scan traversal | **229.5** = **1.34x** budget |
| **Range extension** | **0.0** — the day's entire 312.6 range was set **before** the scan |
| Fuel | budget **171.4**, extension **0.0**, error **−171.4** = **exactly −budget**, the arithmetic floor. 2nd-largest over-read in the per-day record (10-06 −180.1) |
| Levels | **16 published / 7 touched = 0.44**. Above the scan 4/9, below 3/7 |
| Regime | ABOVE flip by 298.7, `COHERENT_LONG` high confidence, week net GEX **+8.896bn** → **correct** (see §2) |
| VXN-implied range | 428.3 vs realised 312.6 — **over by 115.7** (realised 0.73x) |
| Straddle band | ±219 → 30717..31155. Close **inside**, and **both intraday extremes inside — the first time in the record** |
| `track.py` | 24 days / 27 scans; direction all-time **13 / 6 / 8**, levels 0.51. No literal `actionable` line (field at `track.py:185`, renders as prose: *"24 of 3 days … threshold met, read the evidence before proposing"*) |

## 2. What the levels actually did

**CALL WALL 31000.7 (+64) — it capped, and this is the single most informative
row of the day.** Separating the two things the register keeps conflating:

- **Close-side control: total.** One post-scan bar (13:15Z) printed a high above
  it, by **1.0pt**. **Zero** post-scan bars sat entirely above it. Price then
  fell **229.5** to 30772.2 and closed **93.8 below**. On the forward-only
  convention this is the **tightest cap in the P-E census** (previous cap mode
  3.6–11.9).
- **Intraday penetration: it had already happened, before publication.** The
  wall had **53 pre-scan touch-bars and 15 pre-scan bars entirely above it**, and
  the pre-scan high 31045.0 cleared it by **44.3**. The board's unconditional
  *"rallies stall"* was asserted about a level the session had already broken —
  and this time the level **reasserted** itself. That is the **opposite** outcome
  to 10-05, the other pre-breached wall in the census, which was sliced by 279.2.
  **Pre-scan breach does not predict the mode** (n=2, one each way).
- Caveat that must be stated: the test and rejection happened at **13:05–13:15Z,
  before the 13:30Z cash open**. The cap was earned in pre-market.

**The giant wall was the only thing that stopped the rally, and the fuel section
named something else.** `path_read()` flagged *"UPSIDE path: has friction. Expect
a stall at 30950.7 (14pts away)"* — the **0.78bn** shelf. Price **sliced it by
51.0** and stalled 50pts further on, at the **2.62bn + 2.17bn** stack. The
downside brake, *"a stall at 30900.7 (36pts away)"*, was **sliced by 128.5**;
the level that actually held the downside was **PD close 30791.5**, a magnet at
−145, which held as support with 19.3 of adverse excursion and finished **115.4
below the close**. So: *"both paths have friction"* was the right **character**
read on a long-gamma day — both paths did stall — and **both named prices were
wrong, by 3.6x and 3.5x their stated distance.** Mechanism in §3.

**Other touched rows:**

| level | published as | what it did |
|---|---|---|
| 30995.5 Asia High | *"runs the stops above it"* | capped at **+6.2**, close 88.6 below. Shares the 13:05Z bar with the call wall |
| 30957.7 London Low (today) | *"runs the stops below it"* | exceeded by **44.0**, then lost by 178.5 — the stops below **were** run |
| 30950.7 Options shelf 0.78bn | *"expect price to stall"* | **sliced by 51.0** |
| 30904.3 PD mid | *"a target to aim AT… price drifts here on quiet days"* | **the best row on the board**: close **30906.9 = +2.6**. A 312pt day pinned to 2.6pts of PD mid |
| 30894.9 London Low (prev-day) | *"runs the stops below it"* | chopped both sides, 23 of 31 post-scan touch-bars |
| 30791.5 PD close | *"price often comes back to fill a gap from here"* | **held as support**, worst −19.3, close +115.4 |

**Untouched, and why it matters.** Of the 9 untouched rows, **4 had already been
traded pre-scan and were never revisited** — 31045.0 (1 pre-scan bar), 31038.2
(4), 31024.6 (17) and 30732.4 (1) — and **5 were never in play at all**: 31145.1
and 31064.0 sat above the session high, and the PUT WALL 30700.7, GAMMA FLIP
30637.6 and MAX PAIN 30200.7 below the session low (the low stopped **71.5 above
the put wall** and **134.6 above the flip**). **No level on the board was
noise** — but a quarter of the board was history, not forecast.

**MAX PAIN 30200.7 at −736 = 1.52x ADR** is the 6th distance-confounded
publication. It was a **Friday**, the day the row's own qualifier calls strongest,
and it was 736pts away. The qualifier stays ungradeable.

## 3. What was wrong, and why

**The regime call was right, and it was the best thing in the document.** All of
it, graded against `inputs.bias_components`:

| claim | verdict |
|---|---|
| `gamma +2` *"above flip 30637.6 by 298.7 — long gamma, dips supported"* | **right**; price never came within 134.6 of the flip |
| `gamma +2` *"week net GEX 8.896 → pinning likely"* | **right**; 0.65x ADR and **zero** post-scan range extension |
| `COHERENT_LONG` *"tight, pinned range… breakouts mostly fail"* | **right**; both extremes rejected, close 2.6 from PD mid |
| STRATEGY 1 *"sweeps genuinely fail… this is your fade day"* | **right, and the trade existed**: the 13:05–13:15Z sweep of 30950.7 / 30957.7 / 30995.5 / 31000.7 failed and paid **229.5**, and fading 30772.2 paid **134.7** back |

**The ~15bn GEX swing was tracked correctly, but it is not the anomaly it looks
like.** `+14.841bn` week-on-week is the largest **positive** swing in the record
(2nd in absolute terms behind 09-28's −16.909). The **flip's** 487.5pt overnight
drop is only the **6th largest of 28** consecutive-scan moves — the median
absolute overnight flip move in this series is ~265pts, and the `expiry_shape`
label has **changed sign roughly 15 times in 28 transitions**. Calling this a
regime flip is accurate; calling it unusual is not. The 10-12 scan has already
reversed it (−9.970bn, back to `COHERENT_SHORT`): **the "high confidence"
`COHERENT_LONG` read lasted exactly one session.**

**Why the engine still printed a no-call: gamma +4 was outvoted, for the second
consecutive session.**

| block | pts | verdict on the day |
|---|---|---|
| `gamma` | **+4** | **right on regime, range and strategy** |
| `breadth` | **−3** | no content. Mega-caps −1.88% and *"NDX −1.39% vs ES +0.32%"* are **the previous session's** closes; the day then ran ±0.1% net. Wrong on day-net (+107.0), nominally right on post-scan (−35.3) at a magnitude indistinguishable from zero |
| `macro` | **−2** | DGS10 −1 off a **1bp** move in a **2-business-day-stale** window; NFCI −1 (3rd consecutive firing) |
| `news` | **−1** | a **September**-dated Fed-hike headline, scored on **9 October** — D20 |
| `vol` | **0** | +1 contango *"calmer, more rangebound"* **right**; −1 VXN/VIX 1.45 *"tech-specific stress"* **wrong** (tech closed up). They cancelled |
| `structure` | **0** | +1 above PD mid **right**; −1 *"2 pools above / 3 below → draw lower"* **wrong on net**, right on path |

On 10-08 this same shape — gamma right, outvoted into a no-call — cost a 671pt
trend day. On 10-09 it cost **nothing**: the day was genuinely two-way and flat,
so the no-call was the right label *by cancellation of two blocks, one of which
was right*. **n=2. That is a pattern, not a proposal.**

**"Two-way" described the day, and this time the no-call was cheap.** Post-scan
the day went **+65.4 above** the scan and **−164.1 below** it and closed −35.3;
the ±219 band held every tick. Unlike 10-08 there was no trend to miss. **Cost of
the no-call: ~0.** Stated plainly because the equivalent sentence on 10-08 was
the opposite.

**D20 — the stale headline, quantified.** Label bands are NEUTRAL −2..+2 and
`expected_direction` fires at |score| ≥ 3. Counterfactuals computed exactly:

| variant | score | label | dir |
|---|---|---|---|
| as published | **−2** | NEUTRAL / TWO-WAY | no call |
| drop the September `news −1` (D20) | −1 | NEUTRAL / TWO-WAY | **no change** |
| drop the stale `macro DGS10 −1` (age gate) | −1 | NEUTRAL / TWO-WAY | **no change** |
| drop both | 0 | NEUTRAL / TWO-WAY | **no change** |
| `gamma` block alone | **+4** | MILDLY BULLISH | **+1 — and the basis decides it**: WRONG post-scan (−35.3), CORRECT on day net (+107.0) |

**The staleness carried a real point and cost nothing** — the exact reverse of
10-08, where the age gate alone converted a no-call into a correct call. No single
defective row could move today's label; it would take deleting the whole breadth
block. Recorded as an instance, **not** as grounds to revive anything.

**The root cause of the two failed brakes is code-certain.** `brief.py:486`
`path_read()` selects `brake = next((p_ for p_ in span if p_["sign"] == "+"),
None)` — the **nearest** positive-gamma shelf, sorted by distance, with **no size
test at all**. The level board prints the top **six** concentrations by gamma
force. On 10-09 those two rules disagreed in both directions: the named upside
brake (0.78bn) was the 4th-heaviest thing in its own corridor, and the named
downside brake, **30900.7, is not on the level board or in the secondary gamma
table — it appears exactly once in the whole document, in the fuel section.** A
tradeable instruction at a price the brief never marks.

## 4. Change proposals

**One proposal. Everything else is an appended observation.**

### PROPOSED — rank `path_read()`'s named brake by gamma force, not by distance (H23, now at n=9 across 6 sessions)

- **What to change:** in `brief.py:486` `path_read()`, choose `first_brake` as the
  **heaviest** positive shelf in the corridor, or name both (*"nearest 30950.7
  (0.78bn), heaviest 31000.7 (2.62bn)"*). Additionally, never name a brake the
  level board does not print — today's downside brake exists only in that one
  sentence.
- **Evidence:** H23's record goes to **8 sliced / 1 capped, n=9** (09-30, 10-01
  ×2, 10-02 ×2, 10-05, 10-06, **10-09 ×2**). 10-09 is the first instance with a
  **control**: the named brake was sliced by 51.0 while the heavier structure
  50pts beyond it capped the move to **1.0pt**. The mechanism is code-certain, not
  inferred.
- **Expected effect:** **zero change to any score.** `path_read()` is prose-only —
  `bias_engine.py` never imports it; it is rendered at `brief.py:558` and
  `brief.py:1024`, so a fix must cover both. It would also remove the
  internal contradiction between the fuel section's brake and the board's own
  force ranking.

### Not proposed — threshold not met, or met and already answered

- **P4 / H1 — the live fuel proposal, one new data point only.** Budget 171.4,
  extension **0.0**, error **−171.4 = exactly −budget**. A zero-extension day, so
  the error is at its arithmetic floor and this is the maximum over-read the
  day's budget allowed. The established finding stands unchanged and is **not
  re-derived**: the budget has **no usable skill** (MAE 116.1 vs a leave-one-out
  constant 98.3, n=19; 90.9 vs 75.5 ex-09-21, n=18; sign agreement 9 of 19). The
  correlation sign is **outlier-driven** (−0.080 all days, **+0.224** without
  09-21) — the claim is *"no usable skill"*, **not** *"inversely predictive"*.
  **H1's multiplier branch stays closed.** Caveat that is new today: D26 removed
  **three more days** from the sample, so the n=19 the statistic was computed over
  is already not reproducible.
- **P-E — instance 13, and it is a cap.** Census → **5 capped / 1 middle / 7
  sliced**, cap mode now **1.0**–11.9. P-E stays a **continuum**; no two-mode
  framing, no discriminator search (closed 10-06).
- **P-E(b) — counter-instance.** The standalone 0.78bn shelf was sliced by 51.0,
  outside the 22pt band; the only shelf that bounded the move (2.17bn) is
  **co-located with the call wall** and so carries no information independent of
  it. The shelves did **not** outperform the call wall's top line today.
- **M6 — session 22, and the mildest instance in a week.** 2 of 5 reported
  excursions understate (30957.7 **2.67x**, 30950.7 **2.17x**) and **both invert
  from "held as resistance" to "lost"** against `SETTLE_TOL = 25`. Three rows are
  exact (1.00x). **It does not move the record** — 10-08's 14.99x stands. Separate
  wording inversion: the call wall and 30995.5 both print
  *"broke **DOWN** through it"* for a rejection **from below** on a level price
  never settled above. **Re-proposed unchanged, 22nd session.**
- **D26 — third consecutive day of eaten evidence, and the worst yet.**
  `track.py` now holds back **2026-08-28 (97 bars)** as *"day not finished"*;
  08-26 and 08-27 have left the table entirely. Day count **26 → 24** while 10-09
  was added, i.e. **three graded days deleted by the calendar in one day**.
  All-time direction moved **15 / 8 / 7 → 13 / 6 / 8** (12 / 6 / 8 ex-09-24):
  **three rights and two wrongs deleted.** H1's per-day n moved 25 → 23 ex-09-24.
  **D26(b): `outcome` is still `None` on 61 of 61 scan files.** Appended, not
  re-opened.
- **H18 / P1 — instance 16. Accuracy case stays retracted.** Today **DFII10
  scored 0** (*"up 1bp… no change in that reading"*) while **DGS10 scored −1** off
  the same 10-06→10-07 1bp window — so neither the duplication census (21 of 21,
  conditioned on DFII10 ≠ 0) nor the stale-vs-live agreement census (7 of 17,
  both ≠ 0) takes a row. **New sub-observation:** the two rows reading the same
  1bp move disagree in sensitivity — one scores 0, the other −1. **`HY OAS` still
  renders no observation date: 7th consecutive session**, and that is still the
  blocker. Live `rates US10y` read flat; the stale pair net −1; the age gate
  changed **nothing** today.
- **H7 — the overnight flip moved 487.5pts and the new reading was right.** The
  measurement that matters is the one above: 487.5 is the **6th largest of 28**,
  the median is ~265, and the shape label flips sign about every other scan.
  Positive observation; H7's instability claim is **unaffected** — the flip was
  not more stable today, it was differently located and happened to be correct.
- **H22 — the row was right today, and the persistence measurement is new.** Week
  net GEX **+8.896** → *"pinning likely"* → **0.65x ADR**, the smallest range/ADR
  in the recent table and the **first positive-GEX row** in it. Against that: the
  sign changed **~15 times in 28 transitions** and reversed again on 10-12 by
  9.970bn. The direction test's n cannot be extended — **D26 shrank its sample
  today**. The 10-08 counterfactual (zeroing the row converts wrongs *and* rights
  into no-calls) stands. **Nothing proposed.**
- **D23 — 9th residual, and the largest in the series.** Board offset **+0.7**
  (NDX ref 30935.6, cash last traded 2026-10-08T16:14:59 rolled forward by the NQ
  move +209.8, vs CFD 30936.3; basis `nq_implied`, greeks
  `repriced_bs_at_current_spot`). Section 7 offset **+267.5** at feed time
  11:59Z. Gap **266.8**; CFD move (11:55Z open 31014.9 → scan 30936.3) =
  **−78.6**; **residual +345.4**. Series: `+190.5 / −201.3 / +203.8 / −7.3 /
  +2.9 / +246.6 / +203.6 / +209.5 / +345.4` — intervening move explains **2 of
  9**. Extended as a new data point, **not** re-measured. Damage **none**
  (research-only; no volume had traded).
- **D25 — 22nd consecutive pre-NY scan.** *"The dominant strike is stable at 0
  across 6 samples"* printed three lines below *"No volume has traded yet
  today"*. Appended, not re-opened. Damage none.
- **H20 — not an instance.** `events_24h` empty; *"No High/Medium US events"*.
  Stays **CLOSED-NEGATIVE**.
- **P-H — no 4th deciding instance, but the bases disagreed in SIGN for the first
  time since it opened.** Post-scan **−35.3** vs day net **+107.0**. On a no-call
  the basis cannot decide a verdict, so the census stays **n=3**; it would have
  decided the grade at |score| ≥ 3, and the `gamma`-block counterfactual above is
  the worked example. Basis stated: **post-scan**.
- **H4 — no instance.** GAMMA FLIP 30637.6 at −299 never reached (missed by
  134.6). The row's *"we are above it, fades work"* branch was correct all day,
  but that is the regime read, not a level read.
- **H8 — observation 7 of 10.** Band 30717..31155, close **inside** → **6 inside
  / 1 outside**. First instance where **both intraday extremes were also inside**,
  which the standing caveat says should be rare. VXN-implied 428.3 vs realised
  312.6: **over by 115.7**, reversing 10-08's 261.8 under-read.
- **H2 / H3 / H10 / H17 / D21 / D22 / D24 — no instance.** `structure 0` on the
  prior-week row (H10 did not fire); fuel was MODERATE not LOW_FUEL (H2);
  no max-conviction call (H3); no-call regardless of deadband (H17); the band row
  scored **0** (*"mid-band, 79% up the range"*) so neither D21 branch fired; the
  breadth legs were mixed and printed with the correct shape (no D22(a)); no
  forward events at all (D24 unfalsifiable).
- **P-G — instance #17.** Two "Low" rows published **above** the scan with
  *"the next session usually runs the stops below it"*: `London Low (today)
  30957.7` at **+21**, inside the ±25pt *"sitting on it"* band the proposal
  already specifies, and `Asia Low (prev-day) 31024.6` at **+88**. Unlike #14–#16
  **the day validated the direction** of both claims (30957.7 lost by 178.5;
  31024.6 never revisited). Already PROPOSED.
- **Session-context field — 11th session. 11 of 16 rows had been interacted with
  pre-scan.** CALL WALL 31000.7 (**53** touch-bars, 15 bars entirely above), Asia
  High 30995.5 (51), PD mid 30904.3 (18), PD close 30791.5 (18), Asia Low
  (prev-day) 31024.6 (17), London Low (prev-day) 30894.9 (16), 30950.7 (12),
  30957.7 (11), Equal highs 31038.2 (4), London High 31045.0 (1), Asia Low
  30732.4 (1). **Costliest instance, and it is the ⭐ row:** *"Equal highs ×2 +
  PWH — 2 touches at this price, **never traded through** — a real stop cluster.
  Prime S1 sweep trigger"* at 31038.2. The pre-scan high was **31045.0** — it had
  been traded through by **6.8pts** four hours before the board printed, and the
  sweep never came back. Identical in shape to 10-08's 30895.1. Already PROPOSED
  09-29.
- **P-B(b) — 15th session, and TWO guaranteed double-count windows, one fired.**
  `merge_tol = max(3.0, 484.0 × 0.008) = 3.87` vs `TOUCH_TOL = 8.0`. Board pairs
  inside the guaranteed window: **31000.7 / 30995.5 (5.2)** and **30957.7 /
  30950.7 (7.0)**. The first **fired** — both first-touched in the same 13:05Z
  M5 bar. 7 touches → **5 distinct M5 bars**, inflation **1.40x**. Proposal
  unchanged.
- **Dead-weight audit — 27 PRE_NY scans ex-09-24 on my own denominator, which
  does NOT reconcile with the register's "28 scans".** `macro` yield curve
  **0 / 27 — still never scored**; `vol` VVIX **2 / 27**; `rates` DXY **3 / 27**;
  both `fuel` rows **0 / 27**; `events` **absent on 19 of 27 and has never
  scored** (P-C). `macro` NFCI fired **−1 again — 3rd consecutive session**, which
  further vindicates the 10-07 decision not to drop it. The standing proposal
  stays **narrowed to the yield-curve row and WALCL/RRP**. The denominator
  mismatch is itself the reproducibility complaint already on file: `track.py`
  counts 09-24 inside every statistic **and** D26 changes the sample daily, so no
  quoted figure in this register is reproducible from the journal.
- **H19 / D18 — coverage 1.7%.** 138 headlines → 58 relevant → **1 auto-scored**
  (0 bull / 1 bear) → `news −1`. Neither keyword defect could fire on one
  headline. The one scored headline was month-stale (D20, above).

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**; no
`REVIEW.md` created for any day lacking a prediction. **09-09 and 09-25 still
have no `REVIEW.md`, and none was created or back-dated.** One scan file for
10-09 (`1249-preny.json` + `.md`), `is_trading_day: true`, `review_day` reports
**0 test artefacts** for the day (`track.py` excludes 6 across the record).
**09-24 quarantined by hand — 10th consecutive review; there is still no schema
`quarantine` field.** 2026-10-12's scan exists (`1248-preny.json`,
`is_trading_day: true`) and is **correctly** held back (180 bars);
**2026-08-28 is held back INCORRECTLY — see D26.** **No new IDs allocated by this
review; next free remains H26 · D27 · P-I.**
