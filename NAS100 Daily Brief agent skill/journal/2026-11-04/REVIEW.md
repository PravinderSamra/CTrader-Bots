# 2026-11-04 (Wednesday) — review

_Written after the 2026-11-05 brief was delivered. Nothing here blocked, delayed
or altered it. One scan graded: `1247-london.json` / `.md`, `LONDON`
12:47:54Z, `is_trading_day: true`, **276 bars**, `review_day` reports **0 test
artefacts**. **No `prediction` block was touched. No scoring, wall or grading
code was edited.**_

**`track.py` DID NOT COMPLETE — 8th consecutive failure.** `timeout 240 python3
-u track.py` → exit **124**, **0 bytes stdout, 0 bytes stderr**, identical to the
previous seven. There is no `actionable: YES/NO` line to read, so **the 3-session
rule was applied by hand, per entry.** Census figures below are derived **FROM
SOURCE** (46 finished journal day directories scanned, **30 gradeable**, one
45-day `M_5` fetch of **9092 bars, 2026-09-21 → 2026-11-05**) and reported
**alongside** the register's carried value, never replacing it. The derivation
reproduces the register's published values exactly where they overlap — 11-03
**−258.2**, 11-02 **+161.2**, 10-30 **+351.6**, 10-29 **+112.4**, 10-28
**−76.1**, 10-16 **+479.3**, the P-F treatment split **+283.5 / median +351.6**
on the same three days, and `review_day`'s own 11-04 figures to the decimal
(range 1345.9, extension 305.9, traversal 704.9). That is the only warrant
offered for it.

**D29's G1–G4 applied as written, not re-decided.** 11-04 is the **third** graded
`LONDON`/EST scan. Per **G1** the `PRE_NY`-keyed censuses do **not** accrue
(P-B(b) stays **23**; the session-context-field census stays **22**) and the
parallel **`LONDON/EST (from 2026-11-02)`** census goes to **n=3**. Per **G2** the
fuel series **accepts** 11-04 and the error is tagged `LONDON/EST`; the
window-length concern is again **measured, not assumed** — the pre-scan window
held **178 bars = 890 minutes = 14h50m**, the EDT norm (14h45m) to within five
minutes, identical to 11-03. Per **G3** everything else grades normally. Per
**G4** the post-close census stays **n=2** and takes no instance.

**What the `LONDON` census reaching n=3 does and does not license.** It is the
first time a `LONDON`-keyed limb has a **threshold-eligible sample**, and that is
all it is. It licenses *considering* a proposal keyed to the EST era. It does
**not** license (i) merging with the `PRE_NY` denominators — G1 forbids it and
the populations differ by 59 minutes of pre-open tape; (ii) reading three
**condition** instances as three **harm** instances, which is the D28 / merge-note
counting rule and is the binding constraint here (the session-context field has
**3 of 3** condition instances in the `LONDON` census and **1** demonstrable harm
case, today's); or (iii) anything about the fuel series, which under G2 is
**pooled with a tag**, not split. **Nothing is proposed off it.**

---

## 1. Scoreboard

| | |
|---|---|
| call | **STRONGLY BEARISH −12** at 28239.5 (`LONDON`, NY cash +102 min) |
| session O/H/L/C (`review_day`, 21:00Z bucket) | **28176.8 / 28838.9 / 27493.0 / 28436.1** |
| same, on the D30-clean 22:00Z basis (276 bars) | **28290.5 / 28838.9 / 27493.0 / 28515.0** |
| range · net | **1345.9** (**2.126× ADR14 633.1**) · **+259.3** (clean basis **+224.5**) |
| direction, post-scan (P-H basis) | **+230.0 → WRONG** |
| direction, day-net | **+259.3 → WRONG** · clean-basis net **+224.5 → WRONG** |
| | all three bases **agree**; **no P-H deciding instance** |
| levels | **4 published / 3 touched = 0.75** (30-day mean **0.51**) |
| levels inside the realised post-scan range | **3 of 3 touched = 1.00** |
| fuel | budget **0.0**, extension **305.9** → error **+305.9**; traversal **704.9**; `review_day` verdict *"UNDER-estimated"* |
| VXN-implied budget | **543.1**, the figure §3 told the reader to prefer — realised range **1345.9**, under by **802.8** |
| ATM straddle band | ±486 → 27753 .. 28726; close **28436.1 INSIDE** (290 of room); day high **28838.9 outside by 112.9** |
| \|post\|/ADR · post/range | **0.363** · **17.1%** |
| offset | **−68.8** (`nq_implied`, `repriced_bs_at_current_spot`) — **6th D6 breach, 1st negative** |

**Direction, from source, n=30 gradeable (09-24 quarantined, 09-21 aged out):**
**12/24 = 50.0%** post-scan vs **13/24 = 54.2%** day-net, 6 no-calls, deciding set
**n=3 (10-07, 10-15, 10-19)**, unchanged. Carried: **15/30 vs 16/30**.

**No subset of blocks fixes this call, and that is worth stating.** Negatives
total **−14** (gamma −5, vol −4, macro −3, rates −1, news −1) against **+2**
(breadth +1, structure +1). **Deleting every bearish block gives +2 — a no-call,
not a correct call.** The −12 was not reachable by component surgery; nothing
below should be read as "and this row is the lever".

---

## 2. What the levels actually did

**The board was four options rows and two of them had already been traversed
before the scan.** That is the day's finding, and it is not a hit-rate finding.

- **`PUT WALL 27631.2 ●●●●○` at −608.** Published note: *"Heaviest floor this
  week (54k contracts), BUT today the desks are pushing moves along — **if it
  breaks, expect it to speed UP, not bounce. Don't buy the break.**"* The day's
  low was **27493.0 — 138.2 points BELOW the put wall — printed at 03:05Z, 9h42m
  before the scan**, and price had recovered **746.5 points** from it by scan
  time. The level had already broken and already bounced, hard, and the brief
  described the break as a future event with a forecast attached. `review_day`
  grades it *"never reached"* because it grades post-scan only; it was reached
  and sliced and reclaimed while the brief was being written.
- **`CALL WALL 28431.2 ●●●●● 0.64bn` at +192**, described in §3 as *"First real
  brake … far enough that little stands in the way of a breakout before it"* and
  on the board as *"Heaviest ceiling this week … rallies stall. Take profit into
  it … the strongest ceiling on the board."* The **pre-scan high was 28533.0 —
  101.8 ABOVE it**, made in the 10:00Z hour, 2h17m before the scan, after which
  price fell back to 28134.4. Post-scan price **sliced it by 407.7 points
  (0.644× ADR14)** on the way to 28838.9 and closed **4.9 above it**. The first
  clause of §3's sentence was right (nothing stood in the way); the brake did not
  brake. **P-E instance 21 — SLICED**, and the overshoot (407.7) is far outside
  P-E's 12–103 "middle" band.

**Only one row held anything, and it was MAX PAIN on the wrong day of the week.**
`MAX PAIN 28581.2` printed *"price drifts toward it as the week goes on. **Weak
on a Monday, strong by Thursday/Friday**"* — Wednesday. It was exceeded by
**257.7** at 15:15Z and then **held as resistance for 160 minutes** from 18:15Z
(worst excursion **+21.7**), closing **145.1** below. It is the only row on the
board with `held: true`, and the clause that would have discounted it names the
two days it was not. **n=1 for the mid-week case; nothing proposed.**

**`GAMMA FLIP 28679.5` was reclaimed and lost, and the brief's own conditional
was the right read.** §2: *"Reclaim and hold above and they start damping moves
again, and fading becomes valid."* Price closed above the flip from **14:40Z to
15:40Z**, made the day high **159.4 above it**, then closed back below at 15:45Z
and held below for **330 minutes**, finishing **243.4** beneath. `review_day`
settles it `lost`, worst excursion **30.5**. **H4 — close-to-flip distance
243.4. Recorded; the census convention used by every prior review counts only
days the flip was approached, so this is the first distance recorded since
August and the entry stays OBSERVING at 1 hit / 4 misses, misses widening. Do
not use the flip as a target.**

**The 0.75 hit rate is a four-row board, not a good board.** Three touches came
off **two** M5 bars — 14:30Z (`CALL WALL`, and that one is a `TOUCH_TOL`
artefact: the bar's high 28423.4 is **7.8** short of 28431.2, inside the 8.0
tolerance, and the tape's own first trade through the wall was 14:35Z) and
14:40Z, whose 158.8-point range first-touched **both** 28581.2 and 28679.5.
**Inflation 1.50×, equal to 11-03's record** — this is **H6**'s density artefact
arriving through bar size rather than board crowding, which is a new route to the
same artefact. The rows themselves are **98.3 to 1048.3** points apart, so
**P-B(b) has ZERO guaranteed double-count windows** on this board — the first
`LONDON`/EST session with none (min gap **98.3 = 12.3× `TOUCH_TOL`**).
**Observed and EXCLUDED under G1; the `LONDON/EST` census goes to n=3;
`PRE_NY` stays 23.**

**Secondary table (P-E(b), instance #22) — 3 of 5 unreachable, 2 of 2 graded
rows wrong.** `28181.2` (−58, put-dominant, *"accelerate THROUGH rather than
stall. **Not a floor**"*) was the **post-scan floor**: price bottomed 47.2 below
it at 13:00Z and never returned. `28631.2` (+392, call-dominant, *"they damp
moves: expect a stall — rallies lose momentum into it"*) was **sliced by
207.7** — though the afternoon then closed three consecutive hours at
28631.5 / 28632.9 / and traded 28646–28662, i.e. it behaved as a magnet after
failing as a brake. `27831.2`, `28031.2`, `28081.2` were never reached (post-scan
low 28134.0). **P5 — 2 of 5 gradeable, 0 right / 2 wrong, still graded by no
tool.** The *"best level is in the secondary table"* sub-claim takes a **FIFTH
consecutive counter-session**; it is dead, and that is not a model change.

**The level that decided the launch was not in the document.** `PDH 28316.4` —
named by the brief's own `structure +1` row — appears **neither on the board nor
in the footnote**. Price chopped **28310–28341 for 55 minutes (13:35Z–14:30Z)**,
a 9.2-point overshoot and a pullback to 28230.3, and then the 14:35Z/14:40Z bars
ran 28286.8 → 28677.1. The PDH was the base of the 704.9-point rally. See §3.4.

---

## 3. What was wrong, and why

### 3.1 The fuel block was the most extreme reading ever recorded and it was wrong by the largest margin a zero budget has produced

| | |
|---|---|
| pre-scan range at 12:47Z | **1040.0** (H 28533.0 10:30Z / L 27493.0 03:05Z) |
| ADR14 | **633.1** → **164.3% used**, `fuel_ratio` **3.91**, `EXHAUSTED` |
| published budget | **0.0** |
| realised extension | **+305.9** (new high 28838.9 at 15:15Z) |
| realised range | **1345.9 = 2.126× ADR14** |

**The pre-scan 1040 points were a completed overnight V, and the engine read a
finished move as a finished day.** 28382.0 (23:00Z) → **27493.0 (03:05Z)** →
**28533.0 (10:30Z)**: the low was **9h42m old** at the scan and the high **2h17m**
old. The brief then printed, verbatim: *"**The day's range is set** … Continuation
into new highs/lows is the **low-probability** trade; the range width is where
the remaining opportunity is."* Realised: the day made a **new high 305.9 above
the pre-scan high**, and the entire post-scan edge was in that new high — the
"range width" available after the scan (post-scan low 28134.0 to the pre-scan
high 28533.0) was **399 points**, less than the 704.9 traversal and barely more
than the extension it said would not happen.

**§3 carried four incompatible range statements on one page.** Budget **0.0**;
VXN-implied **543.1** with an instruction to *"use the smaller budget"*; ATM
straddle **572** close-to-close (ATM IV **48.2%**); ADR14 **633.1**. Realised
**1345.9**. The one quoted as authoritative was the worst of the four, and the
instruction to prefer the smallest took the **9th counter-instance** in that
series (under by **802.8**, against 11-02's +275.7 and 11-03's −143.0).

**H1 / P4 — error +305.9, n=30, and the TWELFTH value under one series name.**
From source **mean +49.0, median +16.1** (was +57.8 / +16.1 at n=30 — the mean
fell because **09-21's +569.2 aged out** on the same day +305.9 entered; see
D26). **ANSWERED-NEGATIVE; flagged, not averaged.** Tagged `LONDON/EST` per G2.
The zero/non-zero split does not merely hold, it widens — see §4.

**H22 — n=19 → 20, label RIGHT, and the magnitude is anti-correlated three
sessions running.** Week net GEX **−1.305bn** → *"expansion likely"* → realised
**2.126× ADR**, the **largest range/ADR in the live 45-day window** (09-21's
2.462 was larger and has aged out). But 11-03's **−3.083bn**, a figure **2.4×
larger**, produced **0.610×**, and 11-02's **−0.579bn** produced 1.257×. The
label is right; the number carries no ordering information at all. **Still not
discriminating.**

**P-F — 11-04 is a CONTROL day and it is the third-largest control error in the
record.** Price at scan **28239.5** sat **inside** the prior-day range
(PDH 28316.4 / PDL 27906.8), so P-F's *">150pts outside"* trigger does **not**
fire. From source: treatment **n=3, mean +283.5, median +351.6**; control
**n=27, mean +23.0, median +0.1**. 11-04's **+305.9 exceeds the treatment mean**
while sitting in the control group. **That is a counter-instance to P-F's
trigger, not to P-F's claim** — and the trigger that does capture it is
`remaining_budget == 0`. See §4.

### 3.2 H2 — INSTANCE 10, graded under the unaltered 10-20 rule, and the fade loses cleanly

Cell confirmed: `is_trading_day` · **`EXHAUSTED`** · price **440.0 below the
flip** · fade instruction printed (§3 *"Fading the extremes back into the range
is the higher-probability side here, **even when the gamma regime favours
continuation**"*).

| step | value |
|---|---|
| pre-scan extremes | **H 28533.0** / L 27493.0 |
| first post-scan sweep | **up**, 14:40Z (high 28677.1) |
| engage bar (first close back inside) | **15:45Z**, close 28507.2 |
| swept extreme re-exceeded | **on the engage bar itself** (15:45Z high 28566.9), again 15:55Z (28547.5) |
| target (nearest published level inside) | **28431.2 CALL WALL** |
| target first touched | **16:00Z** (low 28426.4) |
| **result** | **FADE LOSES** — reclaimed before target, **no tie** |

**Census 7–2 → 8–2 to the gamma block; 10–0 if ties go against the fade. Claim
stays FALSIFIED; existing proposal unchanged.** Stated against myself: a looser
rule that ignored the reclaim and marked to the close would have called this a
**win** (+71 from the engage close). The rule as written was fixed before the
outcome and is not being re-cut now; the looser reading is recorded so the
margin is visible.

**The two-opposite-instructions 2×2 needs a fourth column, and its own
prediction holds.** The 10-30 specification tabulates `ROOM_TO_EXPAND` /
`MODERATE` / `LOW_FUEL` against gamma sign and has **no `EXHAUSTED` column**.
11-04 is **`EXHAUSTED` ∩ below the flip**, and it is the sharpest **CONTRADICT**
cell in the record: §1 *"Strategy-1 fades have a materially lower hit rate
here"*, §2 *"**Fading is the wrong trade today** — Strategy 2 … is the right
one"*, §4's put-wall row *"Don't buy the break"* — against §3, which names §2's
argument and **overrules it in the same sentence**. Three statements against
fading, one for it, and the one for it is the most explicit. **Per the
10-19 / 11-02 precedent this is a correction to a live specification inside the
suspended census: the 2×2 becomes a 2×4, the `EXHAUSTED` ∩ below-flip cell is
CONTRADICT, no ID is taken and nothing is proposed.**

### 3.3 The gamma block's amplitude limb was right, its direction limb was wrong, and the branch still has no distance scaling

`gamma −5` = **−3** (*"below flip 28679.5 by **440.0pts** — SHORT gamma, dealers
amplify: downside accelerates, rallies unstable"*) **−2** (*"week net GEX
−1.305 → expansion likely"*) **+0** (band).

- **The amplification arrived and pointed UP.** Traversal **704.9**, range
  **2.126× ADR** — the largest in the window. The *"dealers amplify"* content was
  not merely right, it was the single best statement on the page. What it does
  not contain is a **sign**: §2's *"sweeps tend to keep running rather than
  fail"* was satisfied by the **up**-sweep of the pre-scan high (305.9 beyond it),
  which is the trade the direction call forbade.
- **440.0pts = 0.695× ADR earns the identical −3 that 10-27's 22.6pts
  (0.040× ADR) earned.** This is the largest distance yet to buy the same
  full-strength direction term, and it confirms for a further session that **the
  branch has no distance scaling at all**. **Routes to the unarbitrated
  two-gamma-rows conflict, which already owns the distance-as-direction finding
  (10-26, 10-27). No number taken.** There is **no** two-row sign conflict today
  — `0_2dte −1.314`, `this_week −1.305`, `45d −4.29`, all negative,
  `COHERENT_SHORT`, confidence high — so the shape engine and the score agreed,
  and both were wrong about direction while right about amplitude.
- **`gamma +2` DID NOT FIRE — recorded as a NON-INSTANCE, not a miss.** Price was
  *"mid-band (27631.2–28431.2), 76% up the range"* → **+0**. Under the published
  *"bottom 20%"* rule it misses by 56 percentage points; under the **10-30
  pre-registered normalised rule** price was **608.3 above the put wall =
  0.961× ADR** against a 0.15× threshold, so **neither rule fires**. Census stays
  **4 right / 4 wrong**; the pre-registration stays at **1 of 3 firings
  collected** (11-03). **D21** — the band was **800.0 wide = 1.264× ADR**, so each
  20% window is 160 points; no firing, nothing to grade.

### 3.4 D7's second limb, INSTANCE 3 — the nearest level in the document was the one that got truncated, and this time it was the PDH

With `remaining_budget = 0.0`, `keep()` (`brief.py:416–433`) gives a cap of
**0.0**, so **every** non-exempt level is rejected regardless of distance; the
board collapsed to **4 rows, 100% options-derived**. `rows.sort(key=lambda r:
-r["level"])` (`brief.py:373`) then leaves `far` in **descending price** order and
`far_line(cap=6)` (`brief.py:146–159`) protects only
`CALL WALL / PUT WALL / GAMMA FLIP / MAX PAIN` — **none of which is in `far`
today** — so the footnote keeps the **six highest-priced** demoted rows:

> _Beyond today's range (context only, don't mark): 30024 PWH · 28984 Equal highs
> ×2 · 28541 Equal highs ×2 · 28533 London High (today) · 28469 Equal highs ×2 ·
> 28382 Asia High (today)_

**At the cap of 6, all six above price, +143 to +1785 away. Dropped from the
board AND from the footnote: `PDH 28316.4` at +77, `PD mid 28111.6` at −128,
`PDL 27906.8` at −333 — all three named by the brief's own `structure +1` row —
plus every session low and every equal-lows cluster.** The document retained
**PWH at +1785** and discarded the PDH at **+77**.

**Harm, demonstrable from the tape:** `PDH 28316.4` capped the 13:35Z–14:30Z
consolidation to a **9.2-point** overshoot (13:40Z high 28325.6), price pulled
back to 28230.3, and the next two bars ran **28286.8 → 28677.1**. It was the base
of the day's move and the one price-ordered row the cut removed.

**Second limb: condition n=3** (10-22 PDL at +189, 10-30 PDL at +330, **11-04
PDH at +77 — the closest dropped row in the series and the first PDH**).
**Harm n=2** (10-22's pre-scan-low sweep, 11-04's launch base). The mechanism is
**deterministic from the sort**, so the condition count is an identity rather
than evidence, and harm is **below three**. **The `abs(dist)` truncation ranking
is ALREADY part of D7's proposal (added 10-22); nothing new is proposed and no
number is taken.** First limb (the vanishing wall) is a **clean control**: all
four walls reached the board.

### 3.5 D30 — the fuel figures are nested for a THIRD time, and the prior-day limb breaks for the FIRST time

**Asked directly: is the migrated hour nested again, or is this the day it
isn't? Both, on different limbs, and the distinction matters.**

11-03's post-close hour (**21:00–21:55Z, O 28176.8 / H 28316.4 / L 28139.8 /
C 28282.4**, range 176.6, **+105.6**) sits inside 11-04's bucketed day.

**Limb 1 — today's range. NESTED, 3 of 3.** 28139.8–28316.4 lies strictly inside
both the pre-scan range **27493.0–28533.0** and the full day **27493.0–28838.9**.
Measured with and without the hour:

| | with the migrated hour | without it |
|---|---|---|
| pre-scan range at 12:47Z | **1040.0** | **1040.0** (identical) |
| `adr_used_pct` | 164.3% | 164.3% |
| `remaining_budget` | 0.0 | 0.0 |
| session range | 1345.9 | 1345.9 |
| extension, fuel error | 305.9, **+305.9** | 305.9, **+305.9** |

**Identical to 0.1 of a point on every fuel figure. D30's consequence #1 stays
FALSIFIED as a magnitude claim, 3 of 3, and the fuel grade stands unqualified.**

**Limb 2 — the PRIOR day. NOT NESTED, and this is the first instance.** Viewed
as part of 11-03 on the 22:00Z basis the hour makes a **new high**:

| 11-03 session | O | H | L | C |
|---|---|---|---|---|
| 21:00Z basis (grader) | 28002.7 | **28310.3** | 27906.8 | 28167.6 |
| 22:00Z basis (brief's `D_1`) | 28049.2 | **28316.4** | 27906.8 | 28282.4 |

**The brief's `PDH` is 28316.4; the grader's 11-03 high is 28310.3. +6.1 points.**
D30's own 11-03 note reasoned *"a close is an endpoint, not an extremum, which is
why it and only it disagreed."* **That sentence is now superseded: an extremum
disagrees too.** Two consequences follow, both measured:

1. **ADR14 contamination is non-zero for the first time.** `d1[-15:-1]` holds
   **two** EST bars (11-02, 11-03); 11-02's range is identical on both bases
   (788.9), 11-03's is **409.6 vs 403.5**. Clean ADR14 **632.7** against the
   published **633.1** — **+0.4**. 11-03's review recorded **0.0**; today it is
   **+0.4**. Immaterial, and no longer zero.
2. `actual_session.open` **28176.8** vs a clean **28290.5** (**113.7**) and
   `net_move` **+259.3** vs **+224.5** (**34.8**) — the largest open shift the
   defect has produced. **It changed no verdict**: all three bases are positive
   against an expected −1.

**The mechanism is confirmed, the reconciliation proposal is unaffected, and the
magnitude claim stays conditional on the hour breaking a range — which it has now
done once, on the prior-day limb, by 6.1 points. Friday 2026-11-06 is still the
day to watch** (`trading_day(21:00Z Fri) → Saturday`, and the hour vanishes).
**The grading-window limb of P-H stays permanently MOOT under D30 and was not
revisited.**

### 3.6 The offset was −68.8 and the ±69 cost nothing on the scoreboard and something on the level record — graded, not asserted

**Arithmetic confirmed independently and reproduced:** NDX cash **28180.26** at
2026-11-03T16:14:59 (**933 min** stale), NQ roll **+128.0** → implied **28308.3**;
CFD **28239.5**; **28239.5 − 28308.3 = −68.8**. No contract roll involved.
**Sixth D6 breach, first materially negative one: 09-28 +45.9 · 10-12 +43.1 ·
10-14 +41.8 · 10-15 +77.6 · 10-20 +74.5 · 11-04 −68.8.**

**Board composition is driven by the BUDGET, not the offset — confirmed, and the
conjunction is n=1.** 11-04 is **100% options-derived (4 of 4)** with six session
levels in the footnote, but a zero budget forces that in **10 of 10** cases,
breach or not; the breach-day mean is **36.7% vs 31.6%** once 10-15's 11.5-point
budget is set aside. **The conjunction of a breach and a zero budget has
occurred once in 46 days. Treated as the n=1 instance, and the harm is MEASURED
rather than asserted:**

| offset basis | board prices | touched | per-row settled verdicts |
|---|---|---|---|
| **published, −68.8** | 28679.5 / 28581.2 / 28431.2 / 27631.2 | **3/4** | flip `lost` · max pain **`held resistance`** · call wall no settled · put wall unreached |
| **0.0** | 28748.3 / 28650.0 / 28500.0 / 27700.0 | **3/4** | flip `lost` · max pain **`lost`** · call wall no settled · put wall unreached |
| **+68.8 (sign flipped)** | 28817.1 / 28718.8 / 28568.8 / 27768.8 | **3/4** | flip **`held resistance`** · max pain `lost` · call wall **`held resistance`** · put wall unreached |
| **−137.6 (doubled)** | 28610.7 / 28512.4 / 28362.4 / 27562.4 | **3/4** | flip `lost` · max pain `held resistance` · call wall **`lost`** · put wall unreached |

**The direction verdict, the hit rate (0.75) and the reachability of every row
are INVARIANT across the whole ±137 sweep**, because the post-scan traversal
(**704.9**) is **10.2×** the offset. **The per-row settled verdict is NOT
invariant: 1 of 4 rows flips at zero offset and 2 of 4 at the opposite sign.**

So the honest finding is narrow and it is not the one that was suspected: on this
day the ±69 cost **nothing** on the scoreboard and cost **the robustness of the
level-quality record** — the "max pain held as resistance" credit in §2 would not
survive a 69-point revision of the offset. **The offset matters when the day's
traversal is of the same order as the offset, and today it was an order of
magnitude larger. n=1, NOTHING PROPOSED, and the
offset-vs-options-proximity hypothesis stays NULL.**

### 3.7 The news block mis-tagged 3 of its 4 scored headlines, and the one headline that described the day sat in the uncounted pile

`news −1` from raw **−2.75**, 4 auto-scored of **40 relevant / 125 fetched
(coverage 10.0% of relevant, 3.2% of raw)**, 36 for judgement.

| headline | tag / printed reaction | verdict |
|---|---|---|
| *"**Euro zone** inflation hits 4% …"* | `hawkish` → *"bearish long-duration tech"*, ~180pts/90min | **D9 instance 5** — the matched subject is **ECB** policy, scored against the Nasdaq. Same shape as 10-21's UK CPI (D9 #2). It **scored.** |
| *"Musk Faces Setback as SpaceX and Tesla Stocks Tumble on **Midterm Election Results**"* | `earnings_miss` → *"Mega-cap **miss/warning** → index-weighted drag"*, ~170pts/180min | **D18 family** — no earnings in the headline; same shape as 10-30's price target tagged as an earnings miss. **11th trading day / 18th headline.** |
| *"El Niño Poses 'Meaningful Risk' for Inflation to Rise in **2027**, SF Fed Report"* | `cpi_hot` → *"Hot inflation → yields up"*, ~250pts/75min | **D18 family, 19th headline** — a 2027 forecast in a report, scored as a live inflation print, on the same scan whose judgement queue correctly flagged a different row *"hypothetical/speculative, not an event."* |
| *"AMD earnings beat the Street"* | `earnings_beat` → bullish | **the only correctly-tagged row, and the only one whose sign matched the day.** |

**Meanwhile, uncounted:** *"**Dow futures surge 800 points after decisive win by
Democrats in U.S. midterms: Live updates"*** `[risk_on]`, plus
*"Nvidia Took Back the World's Biggest Company Title From Apple on Election
Day"*. The single most market-relevant headline on the page was in the
judgement queue while three mis-tagged rows voted the score bearish on a day
that rose 259.3.

**Verdict effect: ZERO.** `news −1` → 0 gives **−11**, still ≤ −10, still
`STRONGLY BEARISH`, still −1, still WRONG, still H26's ≥10 bucket.
**H19 — clause (i) FAILS: the four scored headlines are four distinct events, so
there is no match-count inflation and n stays 2.** D9 and D18 both already own
their instances; **nothing is proposed and no number is taken.**

### 3.8 H18 / P1 — instance 32, duplication 37 of 37, and the live and stale readings of one instrument disagreed in sign

`rates −1` = **−3** (*"US10y **4.952 (+1.19%)** — yields up … BEARISH tech"*) **+2**
(DXY −0.55%). `macro −3` = **−3** DFII10 (2.62%, +2bp, **dated 2026-11-02, with
its own ⚠️**) **+1** DGS10 (*"moved 3bp **down** (2026-10-30 to 2026-11-02)"*)
**0** HY OAS **0** NFCI **−1** WALCL/RRP **0** curve.

**The configuration, stated plainly: the live 10-year yield says yields ROSE
1.19% and the stale 10-year yield says they FELL 3bp, and both votes were
counted.** The duplication is **37 of 37**; the `macro` pair is
**opposite-signed internally** for the first time in the series.

**De-duplication would have HURT again — second consecutive session.**
Arithmetic only: collapse the DFII10/DGS10 pair keeping the larger member →
**−13**; drop both FRED yield rows → **−10**; drop the stale `DGS10 +1` and keep
the live `rates −3` → **−13**. Every variant moves **further** from a realised
**+230**. On **11-03** the same-signed version was also a counter-example
(−12 → −16). **The RENDERING proposal stands unchanged; no weight change, and
the standing counter-example is now a pair of consecutive ones.**

### 3.9 H27 — observation 9, and the collapse rule is INERT on this configuration

| | 10-26 | 10-27 | 10-28 | 10-29 | 10-30 | 11-02 | 11-03 | **11-04** |
|---|---|---|---|---|---|---|---|---|
| vol ↔ breadth | −3 | +1 | +4 | +1 | −2 | −7 | −9 | **−3** |
| structure ↔ gamma | −3 | 0 | +4 | −7 | −6 | −3 | −6 | **−4** |
| independent remainder | 0 | −4 | −2 | +1 | −5 | +7 | +3 | **−5** |
| score | −6 | −3 | +6 | −5 | −13 | −3 | −12 | **−12** |

Two things, and they point different ways:

1. **The two-session "opposite-signed remainder" streak BREAKS.** The pairs
   carried **−7 of −12 (58%)** and the *"independent"* remainder was **−5, SAME
   signed, and ALSO WRONG.** Every block of the score was bearish-net except
   breadth and structure, and all of it lost.
2. **The pre-registered collapse rule changes NOTHING on this day.** It drops the
   smaller member only when a pair shares a **strict** sign; `vol −4 / breadth
   +1` and `structure +1 / gamma −5` are both **internally opposite-signed**, so
   neither collapses. **Published and collapsed bases are identical at −12, both
   WRONG.** A null observation for the census, and the first one.

**Weight limb stays ANSWERED-NEGATIVE; nothing re-proposed.**

### 3.10 Everything else, graded

- **H26 — a ≥10 instance, and the MAGNITUDE MONOTONICITY BREAKS. It is D26's
  doing, not 11-04's, and that distinction is the finding.** `|post|/ADR`
  **0.363**, range/ADR **2.126** (largest in the live window), direction
  **WRONG**. ≥10 bucket: **carried 4/9 = 50.0%→44.4% → 4/10 = 40.0%**; **from
  source 3/7 = 42.9% → 2/7 = 28.6%**. **Both reported; neither averaged.** The
  from-source fall is **not** 11-04 alone — **09-21 (a ≥10 CORRECT day, and the
  largest `|post|/ADR` and range/ADR in the sample at ≈1.378 and 2.462) aged out
  of the bar window on the same run.** With 09-21 retained the figure would read
  **3/8 = 37.5%**. From source at **n=30**:

  | bucket | n | mean \|post\|/ADR | mean range/ADR | direction (post-scan) |
  |---|---|---|---|---|
  | 0–2 | 6 | 0.207 | 1.042 | — (all no-call) |
  | 3–5 | 8 | 0.452 | 1.144 | 5/8 = 62.5% |
  | 6–9 | 9 | 0.524 | 1.074 | 5/9 = 55.6% |
  | **≥10** | **7** | **0.429** | **1.239** | **2/7 = 28.6%** |

  **The 13-session monotonic magnitude ordering (0.207 / 0.452 / 0.524 / 0.574)
  is BROKEN: ≥10 now sits BELOW 6–9 at 0.429.** Reconstructed with 09-21 in, the
  ≥10 mean is **0.548** and the ordering **holds** — so the break is produced by
  **D26 ageing out the sample's largest observation**, not by new evidence. The
  **range/ADR** form still orders correctly and ≥10 is still the widest bucket.
  **Direction stays monotonically inverted and steepens again (62.5% / 55.6% /
  28.6%).** *"Inverted at the top"* **stays SUSPENDED** for exactly this reason:
  D26 recomposes the ≥10 cell weekly. **No Spearman quoted**; its derivation is
  still unwritten. **Reported both ways, averaged neither.**
- **D26 — the gap WIDENED from 15 to 16, and it has now cost a live statistic.**
  From source, **30** journal trading days hold a full bar set against **46**
  finished trading-day directories with a live scan — **16 invisible**. **09-22 is
  now the oldest usable day; 09-21 fell out of the window on this run**, taking
  H26's largest ≥10 observation and P4's largest error with it. The entry's own
  warning (*"H26's ≥10 cell and P-F's treatment set remain hostage to this"*) is
  **realised, measurably, today**. **Nothing proposed** — the fix is persistence
  of graded outcomes, which `review_day.py:40–55` already says in its own comment.
- **P-H — no 6th deciding instance.** Post-scan **+230.0**, day-net **+259.3**,
  clean-basis **+224.5**, all WRONG; the bases agree. Carried **15/30 vs 16/30**;
  from source **12/24 = 50.0% vs 13/24 = 54.2%**, deciding set **n=3**,
  unchanged. **Grading-window limb MOOT under D30.**
- **M6 — session 39, ONE instance, expected-by-identity.** `GAMMA FLIP` settled
  `lost` and printed *"**broke UP through it** — lost by 30.5pts"* while
  `settled_side` is **below** and the close finished **243.4 beneath** it: the
  level **rejected** price, which is the opposite of what the sentence says. This
  is `review_day.py:159–161`'s identity (the `lost` branch names the direction of
  the **adverse excursion**, the sentence reads as the direction of the **break**),
  **not a finding**. The only **open** defect in the family is `_first_touch`'s
  12-bar window. **Two candidate fixes are with the user; nothing proposed.**
- **D5 — no defect instance; the two instruments diverged on 3 of 3 touched
  rows.** All three first-touch reads say *"traded both sides — chopped around
  it"* (the 14:30Z/14:40Z bars are 142.5 and 158.8 points tall, so a 12-bar
  window around them straddles everything); the settled reads say `lost`,
  `held resistance` and `no settled read`. **Every divergence is the known window
  difference and none is an inversion.** The settled read is the better one on all
  three.
- **H23 — instance 23; census 15 → 16 sliced / 3 capped / 4 never-reached
  (n=23).** §3's named upside brake **28431.2 (+192)** was **sliced by 407.7 =
  0.644× ADR14**; the sentence's reachability clause was right and its braking
  claim was wrong. Downside *"clear"* with **no brake named** — **untested**,
  price went only 72.1 below the scan bar's open. **Force-ranking branch: a THIRD
  disagreement and it again favours neither — the nearest call-dominant (damping)
  strike 28631.2 (+392) was ALSO sliced, by 207.7. Distance-first and force-first
  both lose. Branch stays CLOSED; nothing re-opened.** **Trap RE-FLAGGED for the
  5th time so no one opens a defect**: §3 reads `largest_abs_gex`
  (`brief.py:515`), the secondary table reads `walls_ranked` (`brief.py:647`) —
  different lists, and the damp/amplify label is keyed on `dominant` while the
  brake is keyed on `sign`. **Not a skipped brake.**
- **P-C / `events` / dead-weight audit — the `events` ROW WAS ABSENT ENTIRELY.**
  `events_24h` is `null` and `inputs.bias_components` carries **no `events`
  component at all** (8 components, 26 rows). `events` has **still never scored
  in its history** and today did not render. Same shape as 10-01. High-event
  limb **n=2** (10-28, 11-03), Medium-cluster limb **n=2** (09-29, 10-23) — both
  below three. **P-C is already PROPOSED and gains nothing new.** **12 of 26 rows
  scored 0** (the band `gamma` row, the VXN level row, HY OAS, NFCI, the curve,
  both `fuel` rows, both remaining `structure` rows, three `news` bullets).
  `fuel` scored 0 again. **Nothing proposed.**
- **D28 — the condition RECURRED; condition instance 3 since opening, harm NOT
  demonstrable.** `events_24h` is **`null`** and §5 printed *"No High/Medium US
  events in the next 24h"* as a positive factual claim. Condition instances since
  the entry opened: **10-28, 10-30, 11-04 (n=3)**; across the record this is the
  **8th** `null` scan. **Harm requires a real in-window event demonstrable from
  inside the pipeline, and nothing in §6 or the judgement queue names one** — the
  midterm coverage is political, not calendared. **Harm stays 2 of 8.** The
  condition reaching three changes nothing: D28 is **already PROPOSED** as a
  rendering fix and its proposal is unchanged. **D24 is a clean control** — no
  events renderer ran at all.
- **D22 — a CLEAN CONTROL, and the first in three sessions.** `breadth −1` printed
  *"NDX +0.68% vs ES +0.93%"*. Both legs are positive on a day the whole US tape
  rose, so **neither leg is implausible and no claim is made.** The **n=2 candidate
  count is unchanged.** Recorded because the 11-03 instance turned on exactly this
  implausibility test.
- **The outlier-driven mega-cap mean — NOT an instance today, and the question
  was checked against the register before being treated as new.** `breadth +2`
  read *"mega-cap avg **+1.55%** (**3/4 up**): NVDA +2.29, MSFT +2.73, AAPL −1.90,
  AVGO +3.07"* — the mean's sign matches 3 of 4 members, so there is no averaging
  defect, and **the row was RIGHT.** The averaging-over-dispersion claim is
  **already owned by an unnumbered watch item** (HYPOTHESES.md line **1714**,
  08-28 *"mega-cap avg +3.83%, NVDA +8.74%"*, and line **15617**, 10-30
  *"avg +0.15%, 1/4 up"*), **n=2**, whose own rule says write it up at a third
  recurrence. See the carry-forward block: **the 11-05 scan is that third
  condition instance**, and it is **not graded here**.
- **P-G — NO instance, and a clean control for the right reason.** The board
  carries **no session-extreme row at all** (D7's zero-budget collapse removed
  every one of them), and the six footnote rows are **all above price and all
  highs**, so no *"the next session usually runs the stops below it"* string could
  be mis-sided. **Census unchanged at #40.** The **merge-note limb takes NO
  instance**: there is **no merged row on the board** (all four rows
  `confluence: 1`) and no `PD close` row anywhere in the document, so
  `brief.py:382–385`'s `rank` could not discard anything. **Condition stays n=3,
  harm stays n=2 — a genuine non-instance, as anticipated.**
- **Session-context field — observed and EXCLUDED under G1; `LONDON/EST` census
  to n=3, and this is its first demonstrable HARM case.** **2 of 4** published
  rows sat inside the pre-scan range 27493.0–28533.0 and no field says so — and
  the two are not merely "already traded today", they were **traversed and
  reversed from**: the put wall by **138.2 beneath** (9h42m before the scan), the
  call wall by **101.8 above** (2h17m before). The put-wall row's forecast
  (*"if it breaks, expect it to speed UP, not bounce"*) describes an event that
  had already happened and resolved the other way. `PRE_NY` stays **22**.
  **Condition 3 of 3 in the LONDON census, harm n=1. Below three on harm.
  NOTHING PROPOSED.**
- **P3 / H6 — NO structural instance.** The board carried **no structural wall
  row**; the strict clean count stays **1 clean / 1 confounded** and the standing
  *"stop publishing it"* narrowing stays **blocked**.
- **H14 — no post-scan instance, and a pre-scan counter-observation.** The put
  wall was never touched **after** the scan (missed by **502.8** from the
  post-scan low), so the break rider was not tested and **the count is
  unchanged**. Recorded against the rider anyway, outside the census: it **was**
  broken pre-scan, by 138.2, and price **bounced 746.5** — the exact behaviour
  *"expect it to speed UP, not bounce"* forbids. **Not entered as an instance;
  pre-scan contamination is why P-E keeps a forward-only convention.**
- **H8 — post-closure, and this is a HIT.** Band **±486** off the 2026-11-04 ATM
  straddle (572pts, **ATM IV 48.2%**) → 27753..28726; close **28436.1 INSIDE**
  with 290 points of room, while the day **high** closed outside it by 112.9 —
  which the band's own text anticipates (*"a CLOSE-to-close band … routinely
  trades outside it intraday"*). H8 stays **CLOSED ANSWERED-POSITIVE (8 of 10)**
  and is **NOT re-opened**; post-closure record **2 hits / 1 miss**.
- **H17 — not a deadband case.** Post-scan move is **17.1%** of session range,
  far above the ~5% watch line. **Stays 2 of 3.**
- **H15 / HY OAS — scored 0** (3.43%, +13bp/5d, *"middling"*). Not dead weight —
  the 10-16 correction stands (the row has scored on most scans, and it scores
  **−2** on the 11-05 scan). **No instance.**
- **`PIN_THEN_EXPAND` / P-I — NO instance.** `expiry_shape` was `COHERENT_SHORT`.
  **P-I keeps its single harm case (11-02's *"from roughly 13:00 ET"*, early by
  ~2h30m) and nothing here reopens it.** Noted against the shape engine's credit:
  `COHERENT_SHORT`'s own forecast — *"Expect range expansion and trends that
  persist. Today's ADR can be exceeded — don't cap the target too early"* — was
  **the most accurate sentence in the document** (range 2.126× ADR), and it sat
  four lines above a fuel block that said the range was finished. **Logged under
  the two-opposite-instructions surface, §3.2; no ID.**
- **D23 — observation 16, NO residual, NONE inferred.** §7 did not render. Offset
  **−68.8**, basis `nq_implied`, greeks `repriced_bs_at_current_spot`; NDX cash
  **933 min** stale, rolled forward by the NQ move (+128.0) to 28308.3.
  **Recorded clean**, and a **D6 breach — the series goes to six** (§3.6).
- **D25 — interrupted at 29.** §1–§6 only; no §7, so the unguarded `drift`
  sentence did not render for a **7th** consecutive session. **Counter frozen.**
- **D27 — 11th CONSECUTIVE `gexbot` 401** on `/v2/NDX/classic/gex_full` (the
  11-04 render printed *"[volume-weighted view unavailable: HTTP 401 …]"* and it
  recurred again on the 11-05 scan). Volume-weighted ladder absent, **H12/H13
  untestable**, **D25 SUPPRESSED**. **Nothing proposed** — no credential change,
  no retry policy.
- **`TOUCH_TOL = 8.0` — a tolerance-granted touch, and it cost nothing.** The
  14:30Z first touch of 28431.2 came off a bar whose high was **7.8** short of the
  level; the tape's own first trade through it was 14:35Z, five minutes later.
  **The verdict is unaffected** (the level was genuinely traversed by 407.7), so
  **this is not an instance of the tolerance claim. Stays n=2.**
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26 — not re-opened) ·
  **H5** · **H7** (no overnight scan) · **H9** (AMD is `sector-relevant`, not
  index-defining under the engine's own definition — **NVDA only**) · **H10**
  (price inside the prior-week range 28084.6–30023.6, `structure +0`; the rule
  did not fire, so the reclaim condition is untested — **7th firing count
  unchanged**) · **H11** · **H12/H13** (401) · **H16** · **H19** (clause (i)
  fails) · **H20** (CLOSED-NEGATIVE) · **H21** (CLOSED-NEGATIVE) · **D8** ·
  **D14** · **D15** · **the gamma-outvoted cell** (`gamma` netted −5 and
  **agreed** with the losing call; stays **n=5**) · **the max-pain
  Thursday/Friday clause** (Wednesday — see §2, logged at n=1) ·
  **the *"whole move was over by 10:30 ET"* watch item** (a **SUPPORTING
  instance**, and a clean one: the post-scan low printed **13:00Z = 08:00 ET** and
  the day high **15:15Z = 10:15 ET**, so the entire **704.9**-point post-scan
  traversal completed inside the window; the remaining **5h40m** ranged
  28344.7–28782.2 and gave back **402.8** of the move. A watch item with no ID;
  nothing proposed).

---

## 4. Change proposals — only material ones

**ONE proposal, and it lands on an existing entry. No number is allocated and
nothing new is opened.** `track.py` could not be read, so the 3-session rule was
applied by hand, per entry.

### PROPOSED — widen **P-F**'s trigger to include `remaining_budget == 0`

**P-F already exists and is already PROPOSED** (*"the budget has no term for
price already being outside the prior day's range"*; prose and strategy selection
only, **never a multiplier**). It was grepped for first, together with **P4**
(*"stop quoting a point-precise budget above zero"* — whose scope is explicitly
budgets **above** zero, so the zero case falls outside it), **H1** (multiplier
branch SETTLED-NEGATIVE), **H5** and **H20** (CLOSED-NEGATIVE). The claim below
is **P-F's own sentence with a different trigger**, so it takes no ID.

**What to change.** P-F's trigger is *"`price_at_scan` sits >~150pts outside the
prior day's high/low"*. Add the disjunct **`remaining_budget == 0.0`**. In that
state the `EXHAUSTED` block must not print *"the day's range is set"*,
*"continuation into new highs/lows is the low-probability trade"*, or a
fade-first strategy; it prints the budget as **unreliable in this state**.
**Explicitly NOT proposed: a multiplier, a factor, or any score term** — that is
the H1 lesson and P-F's own prohibition.

**The evidence, from source, n=30.**

| trigger | n | mean error | median | sign |
|---|---|---|---|---|
| `remaining_budget == 0` | **4** | **+253.0** | +237.9 | **4 of 4 POSITIVE** |
| `remaining_budget > 0` | 26 | **+17.7** | −8.8 | 12 of 26 positive |
| P-F's existing *">150 outside PD"* trigger | 3 | +283.5 | +351.6 | 3 of 3 positive |
| union of the two triggers | **6** | **+246.6** | — | **6 of 6 POSITIVE** |
| all other days | 24 | **−0.4** | — | — |

The four zero-budget days are **10-01 (+153.7), 10-19 (+169.8), 10-22 (+382.7),
11-04 (+305.9)**; all four are `EXHAUSTED`, and **all four printed both
prohibited sentences verbatim** (checked in the `.md` files, not inferred).
**09-17 (+40.0)** is a fifth, from the register's own P-F table, and has aged out
of the bar window — reported, not counted. The two triggers are **nearly
disjoint** (only 10-22 is in both), which is the point: P-F's trigger **misses
10-01, 10-19 and 11-04 entirely**, and **11-04 is a P-F control day whose error
exceeds the treatment mean**.

**Why this clears the gate where nothing else does.** Four sessions, same
direction, same cell, same prose, and the cell is defined by a **published field
in the journal** rather than by a cut found after the outcome. The **ratio is
14.3×**, and the harm is a sentence, not a number: on 11-04 the brief told the
reader that new highs were the low-probability trade and the entire post-scan
edge was a **305.9-point new high**.

**Expected effect.** No score changes, no level changes, no gate changes. One
branch of prose stops making a claim it has been wrong about **4 times out of
4**, and the fade-first strategy stops being selected in the one state where the
H2 census reads **8–2 against the fade**. Measured on the four days, the removed
sentences are wrong on four of four; the sentences that replace them assert
nothing.

### Everything else that came close, and exactly why each fell short

| item | evidence | why not proposed |
|---|---|---|
| **D7 second limb** — rank `far_line`'s truncation by `abs(dist)` | condition **n=3** (10-22, 10-30, 11-04) · **harm n=2** (10-22, 11-04) | The condition is **deterministic from `brief.py:373`'s sort**, so it is an identity, not evidence; harm is **2 sessions**. Counted the way D28 counts condition vs harm. **The fix is ALREADY in D7's proposal (added 10-22); nothing new.** |
| **D28** rendering fix for `null` calendars | condition **n=3 since opening** (10-28, 10-30, 11-04) | **Already PROPOSED.** The condition count reaching three changes nothing; **harm is 2 of 8** and 11-04 supplies no demonstrable in-window event. |
| **H2's live proposal** — subordinate the fade instruction to the regime note | census **8–2 / 10–0** against the fade, threshold long met | **Already PROPOSED** and **already scoped** to `LOW_FUEL`/`EXHAUSTED` ∩ below the flip. 11-04 strengthens it and widens its 2×2 to a 2×4. **Nothing new, and the scope is NOT widened beyond that cell.** |
| **H18/P1 de-duplication as an accuracy fix** | duplication **37 of 37** | 11-04 is the **second consecutive counter-example**: every collapse variant moves −12 → −13 or −10, further from +230. **The RENDERING proposal stands; no weight change.** |
| **a distance scale on `gamma −3`** | 0.040× ADR and 0.695× ADR both bought −3 (10-27, 11-04) | n=2 on the normalised form, and the **unarbitrated two-gamma-rows conflict** already owns the finding. The amplitude/direction separation is the real claim and it has **no accuracy test written down**. |
| **`news_scorer` event-age field** | ageing **n=2** (10-30, 11-02); already-in-the-price **n=2** (10-30, 11-03) | Both limbs at two sessions; 11-04 adds neither (its scored events were same-day). **Still the only genuinely absent input, still free and local, still NOT proposed.** |
| **D9 / D18 tagging** | D9 **instance 5**, D18 **11th day / 18th–19th headline** | Both entries exist and neither is proposed on harm. **Verdict effect on 11-04 is ZERO** (−12 → −11, same label, same side, same grade). More regex is the wrong answer — that is D9's own stated scope. |
| **H26 *"inverted at the top"*** | ≥10 now 28.6% from source, direction inverted and steepening | **STAYS SUSPENDED.** The monotonicity break this session is **D26 ageing out the sample's largest observation**, not evidence. Tuning on a cell that recomposes weekly is the failure this register exists to prevent. |
| **the mega-cap averaging defect** | n=2 graded (08-28, 10-30) + 1 **ungraded** condition (11-05) | The third condition instance is on a **scan that has not been graded**. The 08-28 rule requires a third **recurrence**; it is flagged for the 11-05 review, not claimed here. |
| **the `§3`-vs-`§4` brake contradiction** | re-flagged, 5th time | *"Different lists, not a skipped brake."* **Re-flagged, not opened.** |

### Is any published level never reacted to?

**Not answerable from a four-row board, and the question was not forced.** All
three reachable rows were touched (**3 of 3 inside the realised post-scan range**)
and the fourth was missed by **502.8**. The **STRUCTURAL PUT WALL** — the standing
candidate — **was not published at all** today, so it takes no instance and stays
blocked at **1 clean / 1 confounded**. **No level is proposed for deletion.** The
opposite problem is the live one: **the nearest level in the document (`PDH` at
+77) was deleted by the renderer** (§3.4).

### Is a bias component always near zero?

**12 of 26 rows scored 0**, and the `events` component **did not render at all**
for the second time in the record — but `events` **never scoring** is **P-C's
measured constant** and P-C already carries the proposal. `fuel` scored 0 again
and is **informational by design**. **Nothing proposed.** The dead-weight audit's
narrowed proposal (the yield-curve row and WALCL/RRP) is unchanged and still not
actioned.

### Is the fuel budget systematically over or under?

**Yes, and the answer is now conditional rather than global — which is the one
material change above.** Globally the estimator is close to unbiased at n=30
(**mean +49.0, median +16.1**) and the dispersion is the whole problem
(**−258.2 to +479.3** in the live window). **Split on the published budget it is
not unbiased at all: `budget == 0` is +253.0 on 4 of 4 positive; `budget > 0` is
+17.7 with a median of −8.8 — a 14.3× difference.** **No multiplier** — that is
P4 for the non-zero case (already PROPOSED) and **P-F widened** for the zero case
(§4). 11-04 is the strongest single argument in the record for both: a **0.0**
budget and *"the day's range is set"* against a realised **2.126× ADR**, the
widest day in the live window.

### Is a new data point needed?

**No, and 11-04 argues it harder than 11-03 did.** Everything that decided the
day was either on the page or had been deleted from it by the page's own
renderer: the shape block forecast *"range expansion … today's ADR can be
exceeded"* four lines above a fuel block that said the range was over; the
`PDH` that based the rally was truncated out of the footnote by a price-ordered
cut; the put wall was described as an unbroken floor nine hours after it broke;
and §6 put *"Dow futures surge 800 points"* in the judgement pile while scoring
a 2027 El Niño forecast as a live inflation print. **No external source is
proposed.** The one genuinely absent input remains an **event-age** field for
`news_scorer.py` — free, local, owned code, **n=2, NOT proposed**.

---

## Carried forward from the 2026-11-05 scan — recorded, NOT graded

- **Fourth consecutive `LONDON` scan**, 12:47Z. **G1–G4 apply when it is
  graded**; the parallel `LONDON/EST` censuses go to **n=4** then, not now.
  **MILDLY BEARISH −4.**
- **Offset −9.2, CLEAN.** The **D6 breach series stays at six**; D23 takes
  observation 17 when graded.
- **`macro −7` — the largest macro contribution in the series** (DFII10 −3,
  DGS10 −1, HY OAS −2, WALCL −1) against `rates +3` and `breadth +3`.
- **H18/P1 is OPPOSITE-SIGNED AGAIN, and mirrored.** `rates +3` reads a **live**
  US10y that **fell 1.17%**; `macro −3 / −1` reads DFII10/DGS10 **stale to 11-03
  and rising**. On **11-04** the live row said yields UP and the stale row said
  DOWN; on **11-05** it is the exact reverse. **Two consecutive sessions in which
  the live and stale readings of one instrument disagree in sign, in opposite
  directions.** Duplication will be **38 of 38**.
- **HY OAS is widening 22bp over five days — the largest widening recorded** —
  and it **scored −2**, which is further evidence against the retired
  "HY OAS is dead weight" claim.
- **The volatility panic has unwound hard: VXN −17.9% to 25.08**, backwardation
  **gone (0.898 contango)**, VVIX **90.41**. Against 11-04's VXN 30.53 /
  VIX9D/VIX 1.203 / VVIX 107.4, the four `vol` rows that cast **−4** of the −12
  have reversed in one session.
- **Fuel `LOW_FUEL`, ratio 1.73, budget 187.2 — and `ADR14` has climbed 633.1 →
  688.3 in ONE session**, i.e. the day the engine declared exhausted at 164.3%
  raised the 14-day average by **55.2 points**. **It is another H2 cell
  instance** and will be graded under the unaltered 10-20 rule.
- **`breadth +2` reports a mega-cap average of +1.70% that conceals a 9.85pp
  split — MSFT +6.68% and AAPL +5.31% against NVDA −3.17% and AVGO −2.00%.**
  **Checked against the register before being called new: it is NOT new.** The
  averaging-over-dispersion defect is an **unnumbered watch item** at
  HYPOTHESES.md lines **1714** (08-28) and **15617** (10-30), **n=2**, whose own
  rule is *"if it recurs twice more, write it up properly"* / *"write it up at a
  third recurrence."* **11-05 is that third condition instance** — and it is the
  **worst** of the three, because 2 of 4 members are down and the mean is
  positive. **Nothing is opened today: the instance sits on an UNGRADED scan.**
  **This is the item the 11-06 review should expect to reach its own
  pre-registered threshold.**
- **The STRUCTURAL PUT WALL at −108 carries 246k contracts / 1.79bn — the largest
  force figure in the series — with PWL 6pts beneath it.** At **−108** it is by
  far the closest structural wall ever published (11-03's was −298.6, and the
  10-21 note recorded that it had never been within 200pts). **P3/H6's census is
  stuck at 1 clean / 1 confounded because the level is never reachable; this is
  the session that can move it.** Flagged for the next review.
- **`PIN_THEN_EXPAND` did not fire on 11-04** (`COHERENT_SHORT`), so **P-I keeps
  its single harm case** and gains nothing.
- **D27 — the 401 recurred on the 11-05 scan, an 11th consecutive day.**
- **D25 frozen at 29. D23 observation 16 recorded above with no residual
  inferred. D26 gap 16.**

---

## Journal hygiene

One scan file for 11-04 (`1247-london.json` + `.md`), `is_trading_day: true`,
**276 bars** (equal to 11-03; the 21:00Z and 22:00Z buckets both hold 276 on this
day, which is D30's symmetry and not data loss), `review_day` reports **0 test
artefacts**. **09-24 quarantined by hand — 28th consecutive review to carry it**;
there is still no schema `quarantine` field and the 09-29 proposal for one is
reaffirmed. **2026-10-13 has no journal directory — documented, not recreated.**
**2026-08-23, 09-09, 09-24 and 09-25 still have no `REVIEW.md`; none was created
and nothing was back-dated.** **2026-11-05 is on disk, `is_trading_day: true`,
and is NOT graded here.** No `prediction` block was read for anything but grading
and none was modified. No scoring, wall or grading code was edited; the offset
counterfactual in §3.6 calls `review_day.grade_level` on shifted level prices and
writes nothing.
