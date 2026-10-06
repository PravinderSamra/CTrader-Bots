# REVIEW — 2026-10-02 (graded 2026-10-05)

1 gradeable PRE_NY scan (12:47:44Z), `is_trading_day: true`, 0 test artefacts,
275 M5 bars (10-01 22:00Z → 10-02 20:50Z). Scan bar 178 of 275.

## 1. Scoreboard

- Session **O 30520.6 / H 31037.1 (14:25Z) / L 30520.6 (opening bar, 22:00Z) /
  C 30809.0**. Range **516.5 = 1.09x** ADR14 474.8. Net **+288.4**, close
  position 55.8%.
- Bias **+1 NEUTRAL / TWO-WAY → no direction call.** Post-scan move **−75.2**
  (direction −1) on traversal 292.9. **Day net and post-scan direction
  disagree** — second consecutive session (10-01: +64.3 day / −74.7 post-scan).
- Pre-scan H **30901.7 (12:35Z)** / L 30520.6; post-scan H **31037.1 (14:25Z)** /
  L **30744.2 (15:25Z)**. The 135.4 of extension was **entirely upside**.
- Fuel: budget **93.7** vs extension **135.4** → **+41.7, 1.45x over**
  (`review_day`: "about right"). Traversal/budget 3.13x.
- Hit rate **0.55 published (6/11)**; **3 distinct touch bars** (178, 186, 206)
  → distinct rate **0.27**, inflation **2.00x — the worst in the P-B(b)
  series**. Excluding the 4 rows beyond 2x budget the reachable board was
  **6/7 = 0.86**.
- Direction record, **09-24 excluded** per *D23 CORRECTED*: PRE_NY
  **9 right / 5 wrong / 5 no-call over 19 days**; all sessions **14 / 9 / 9**.
  (`track.py` raw, no quarantine: **15 / 9 / 9**.)
- H1: n=24 days, per-day mean **+25.4**; **+1.74** excluding the 09-21 outlier.
  MAE **86.0** against mean budget **103.1** = **83%**.

## 2. What the levels actually did

**Touched (6 of 11).**

| level | brief said | what happened | verdict |
|---|---|---|---|
| 30903.4 PDH + Asia High (prev-day) | *"biggest pile of stops above us. Sweep it, wait for a lower high, then CISD = short"* | swept 12:50Z, then **held above for 110min and 133.7pts** before reversing at 14:25Z | **the sweep did not fail.** The short instruction had no invalidation distance and 133.7pts of adverse travel ahead of it |
| 30896.7 Options shelf 0.56bn | *"expect price to stall. Take partials rather than push through"* | **sliced by 140.4** | wrong, and it had **already been exceeded by 5.0pts at 12:35Z**, 12 min before the brief was written |
| 30846.7 Options shelf 1.42bn | *"expect price to stall"* (also the named **downside brake**) | price traded **190.4 above** it, then **102.5 below** it; graded *"held as resistance, worst +17.3"* | the level did eventually cap the close, but the grade is an inversion (§3) |
| 30820.3 PWH | *"flipped to SUPPORT. Sweep it and buy"* | touched 13:30Z on the way up, then **fell 76.1 straight through it** to 30744.2 with no stall, and **closed 11.3 BELOW it**; `review_day` returns no settled read | **failed as support, and the close puts price back inside the prior-week range the `structure +3` row said had been left behind** |
| 30797.1 London High (prev-day) + shelf 1.27bn | *"the next session usually runs the stops **above** it"* | price was already 68 **above** it; it acted as **support**, 100min | prose on the wrong side (P-G); the level worked, in the opposite role |
| 30790.0 London High (today) | *"runs the stops above it"* | acted as **support**, 105min | same P-G defect |

**Untouched (5 of 11).** CALL WALL 31046.7 — **the session high stopped 9.6pts
short at 14:25Z and the day then lost 228.1 into the close.** The prose
(*"rallies stall. Take profit into it… the strongest ceiling on the board"*) was
the most accurate line in the document and `review_day` grades it
**"never reached"**, identically to the structural put wall 1269pts away.
GAMMA FLIP −522, MAX PAIN −589, PUT WALL −819, STRUCTURAL PUT WALL −1269: four
rows at 1.1x–2.7x ADR on a day with a **94pt** budget. None was reachable; none
reacted.

## 3. What was wrong, and why

**No call was made on a +288.4 day, and one stale FRED row is the whole margin.**
Components: macro **−6** · structure +5 · rates +3 · breadth −3 · gamma +2 = +1,
inside the ±3 neutral band. Of the macro −6, **DFII10 is −3 on a 2026-09-30
observation** (its own `why` says *"FRED has not published since 2026-09-30
(2 business days ago)"*) and **DGS10 is −1 on a 09-29→09-30 move** that is also
**opposite in sign to the live `rates` row** (+3, *"US10y 5.159 (−1.49%) —
yields down"*). Zeroing DFII10 alone gives **+4 → `MILDLY BULLISH`**.
On **day net** that call is right. On the **post-scan** convention `track.py`
and this register use, it is **WRONG (−75.2)** — the **second consecutive
session** on which the proposed age gate manufactures a wrong call. See H18/P1
below; the accuracy case stays retracted.

**`review_day`'s settled read understated every excursion today, and inverted
three verdicts (M6, 17th session, worst instance in the record).**
`settled_read` measures `worst_excursion` only over bars after the **final**
side change. Price spent the first 2h35 of the post-scan window above all five
settled levels and then fell through them, so the window that mattered is
excluded by construction:

| level | reported worst | true post-scan excursion through it | ratio |
|---|---|---|---|
| 30846.7 | *"held as resistance"*, **+17.3** | **+190.4** | **11.0x — verdict inverted** |
| 30790.0 | *"held as support"*, −7.0 | −45.8 | 6.5x — inverted |
| 30797.1 | *"held as support"*, −9.4 | −52.9 | 5.6x — inverted |
| 30903.4 | lost by 33.1 | +133.7 | 4.0x |
| 30896.7 | lost by 39.8 | +140.4 | 3.5x |

All three "held" verdicts breach `SETTLE_TOL = 25`; 30846.7 breaches it by 7.6x.
Prior worst understatement in the series was 2.0x (10-01).

**The hit rate is wrong in both directions at once.** `merge_tol =
max(3.0, 474.8*0.008) = 3.80` against `TOUCH_TOL = 8.0`, so two pairs were
*structurally guaranteed* to publish as two lines and grade as two touches off
one bar: **30903.4/30896.7 (6.7pt gap, both at bar 178)** and
**30797.1/30790.0 (7.1pt gap, both at bar 206)** — the first board in the series
carrying two such pairs. Simultaneously four unreachable rows pad the
denominator. 0.55 is the sum of a 2.00x inflation and a 4-row dilution.

**A High-impact release 17 minutes before the scan is nowhere in the document.**
NFP, AHE and the unemployment rate printed at **12:30:00Z**; the scan ran at
**12:47:44Z**. Section 5 reads *"No High/Medium US events in the next 24h"* and
`event_gate: None` — true forward-looking, and the most misleading possible
rendering on NFP morning. The impulse is unmistakable in the bars: the **12:30Z
M5 bar opened 30748.0 and ran to 30874.0, +126.0pts in five minutes**, and the
pre-scan high **30901.7 followed at 12:35Z**. The 80.3%-of-ADR /
`fuel_ratio 1.78` *"burning hot"* reading that the whole fuel section is built
on **is that spike**, and the document cannot say so. The news scorer caught
none of it either: **0 of 47 relevant headlines auto-scored (0.0% coverage, a
new low)**, with the judgement pile still holding *"…Jobs Due"* — a
pre-release headline.

**`STRATEGY 1 — this is your fade day` was wrong for 110 minutes.** It is
defensible on the close (the day gave back 228.1 from the high and the call wall
capped it), but the document's one executable instruction — short the PDH sweep
— faced 133.7pts of adverse travel first, and nothing in the brief bounds it.

## 4. Change proposals

**D24 (NEW) — render events that have already fired, not only future ones.**
Evidence, 4 sessions where High-impact 12:30Z data landed **before** the PRE_NY
scan and section 5 listed only future events: **08-26** (Core PCE, Prelim GDP;
bias −4 WRONG), **09-11** (CPI ×4; −7 CORRECT), **09-30** (Core PCE, Final GDP;
−3 WRONG), **10-02** (NFP, AHE, U-rate; +1 no-call). The data is already in the
pipeline — all three 10-02 items sat in **10-01's own `events_24h`** at
`+23.7h`. Change: a *"released in the last 6h"* block, and never print
*"No High/Medium US events in the next 24h"* on a day one has just fired.
Expected effect: no score change (`events` scores 0 regardless, per P-C); the
fuel section's `burning hot` becomes attributable instead of mysterious. The
1 right / 2 wrong / 1 no-call split against an overall 9/5/5 is **suggestive
only — n=3 called. Do not weight the score on it.**

**M6 — re-proposed for decision, not more evidence (17 sessions).** Compute
`worst_excursion` over the whole post-scan window, or report both figures.
Expected effect: no call changes; today's board reads 3 lost / 3 inverted-held
instead of 3 lost / 3 held, and the grader stops scoring a level sliced by
190.4pts as *"held as resistance"*.

**P-B(b) — reaffirmed, unchanged** ((a) `merge_tol >= TOUCH_TOL`, (b) always
report distinct-touch-events beside the raw rate). Today is the worst instance:
**2.00x**, two guaranteed double-counts in one board.

**P3 / H6 — exclude `kind: structural` from the hit-rate denominator and move
the row to the context footnote.** 9 publications (08-24, 08-25, 09-10, 09-15,
09-21, 09-22, 09-23, 09-24*, 10-02), distances **−350 to −1900pts = 0.97x to
4.47x ADR14**, **0 within 200pts, 0 within `budget*1.75`, 0 touches**. Its own
note says *"mark it and leave it"* — so it should not sit in the table headed
*"Level board — mark these"*. Expected effect: +0.05 on today's rate, no call
change, ever. (*09-24 options fields quarantined; 8 usable publications.)

**H23 — threshold met (3 sessions, 5 named brakes): 4 sliced / 1 capped.**
Slices **102.5, 140.4** (today), **167.5** (09-30), **300.5** (10-01) =
**0.22x–0.65x ADR**; the single cap was +1.3 (10-01). The fuel section asserts
*"has friction. Expect a stall at X — take partials into it rather than
assuming a clean breakdown/breakout"* as fact. Change: drop the assertion or
print the measured base rate beside it. **Expected effect: removes a specific
instruction with a 1-in-5 hit rate.** Today also kills the
*"brake against the dominant leg caps"* reading floated on 10-01 (n=2, 1 for /
1 against): today's counter-leg brake was sliced 102.5.
**Corollary, and it is the useful part:** H23 is the pre-registered control for
**P-E(b)**. Shelves selected *after* the fact cap 8 of 9 inside 22pts; shelves
**named in advance** are sliced 4 times in 5. P-E(b)'s census is
selection-driven and must not be used to ship a "the nearest shelf caps" claim.
The known distance-selection caveat stands and is non-monotonic.

**Session-context field — 6th session, reaffirmed unchanged** (`tested_today`
per `prediction.levels`; grade against the whole session). Today's is the
degenerate version: the shelf 30896.7 was published as *"expect a stall… rather
than push through"* and named as the **upside brake**, while price had printed
**30901.7 — 5.0pts above it — twelve minutes earlier**, on the NFP bar; PDH
30903.4 was published *"+38 … sweep it"* having been within **1.7pts** at the
same bar. Both under the banner *"everything below is fresh"*.

**D23 "two offsets for one grid" — today CONTRADICTS the 10-01 proposal's
premise, and it should be re-measured before shipping.** 4th consecutive
instance by magnitude: board offset **−3.3**, section 7 **+168.7**,
**172.0pts apart** (09-29: 150.1 · 09-30: 58.0 · 10-01: 158.0). But section 7
is *"matched to feed time 11:59Z"* and the CFD moved from **30677.5 at 11:59Z
to 30865.5 at the 12:47Z scan — +188.0pts**, which accounts for **~92% of the
172.0 gap**. So today the two offsets differ **by design and correctly**, not
because of a broken conversion, and the 10-01 entry's framing — *"a 158pt
latent error that becomes live the first time H12/H13 promote section 7"* — does
not hold on this instance. **Recommendation: before shipping "derive both grids
from one conversion", measure the 11:59Z→scan CFD move on 09-29, 09-30 and
10-01 and subtract it.** If those gaps are also ~the intervening move, the
defect is cosmetic (two numbers shown, no stated reconciliation) and the fix is
to print the time-delta, not to re-derive the grid. All four instances remain
damage-free: section 7 is research-only and had **no volume** (*"No volume has
traded yet today"*).

**Observed, nothing proposed** (detail appended to `HYPOTHESES.md`): **H10** —
the `structure +3` row fired at **+45.2 above PWH, the smallest distance on
record**, and failed (price closed **11.3 below PWH**, back inside the
prior-week range the row said had been left behind); branch now 2-for-4, and
because the failure is at the *nearest* distance it **cuts against H10's own
proposed distance decay**, so no decay is proposed; H18/P1 #11
(age gate would make a 2nd consecutive wrong call on the post-scan convention →
correctness-only case stands; HY OAS renders no observation date for the 2nd
consecutive session, so the gate is still blocked; DFII10's *"last week's
reading"* text wrong for the 3rd consecutive session, this time on a −3 row);
P-G #12 (two rows); P-E no instance (call wall missed by 9.6 — inside its own
3.6–11.9 cap mode, so the empty 12–103 band is undisturbed; the near-miss
*trade* generalisation is already rejected under H24 C1); max pain 5th distance
miss at −589 = 1.24x ADR; **D7 counter-instance** — budget 93.7 → cap 164.0
worked and all 6 demoted levels went untouched, which supports the **narrow**
fix (floor the cap) and argues against the broad session-extreme exemption;
H4 and H20 no instance; H22 n=3 and non-monotonic (GEX 0.036 → 0.84x ADR,
5.58 → 1.33x, 9.526 → 1.09x, same *"pinning likely"* label); H19 coverage 0.0%,
a new low; P-F inside-range control → 20 days; structure tolerance band no
instance (+271.0); post-scan vs day-net direction disagreement n=2.

## Hygiene

No fabricated or backfilled entries; no `prediction` block touched. **09-24
remains quarantined** (options fields and direction call out of P-E, P-E(b), H6,
M6, the hit-rate series and the direction tally; fuel error +13.6 kept on the D1
precedent) and the exclusion is carried **by hand** off `track.py`'s per-scan
table for the **fifth consecutive review** — the 09-29 proposal for a
`quarantine` field read by `track.py` and `review_day.py` is reaffirmed.
No REVIEW.md back-dated for 09-24 or 09-25; 09-25's figures stay cited from the
09-28 entry. The 09-23 pre-registered D21 test stays void. The **D23
cross-check is NOT validated** — it is circular on `nq_implied` roll-path days,
and 10-02 is another one (offset −3.3, basis `nq_implied`). 2026-10-05's scan is
correctly held back by `track.py` (179 bars).

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
