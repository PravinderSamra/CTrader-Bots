# REVIEW — 2026-10-08

Graded from `review_day.py 2026-10-08 --json` and `track.py` (26 trading days /
31 scans; **09-24 excluded by hand from every statistic** — ninth consecutive
review to carry it, there is still no schema `quarantine` field). One scan on the
day: **12:48:12Z PRE_NY**, `is_trading_day: true`, 0 test artefacts.

Direction is graded on the **post-scan** basis, as P-H recommends. On this day
the two bases agree (post-scan −166.5, day net −393.3, both `−1`), so nothing
here turns on the convention — see §4.

`track.py` does not print the literal string `actionable: YES/NO` any more; the
`actionable` field still exists (`track.py:185`) and renders as
*"26 of 3 days for the 3-day hypotheses (H1/H2/H3/H5/H7) — threshold met, read
the evidence before proposing"*. Read as **threshold met**.

## 1. Scoreboard

| | |
|---|---|
| Session (21:00Z roll) | O **31184.8** / H **31240.0** / L **30568.7** / C **30791.5** · 276 bars |
| Range / net | **671.3** (**1.46x** ADR14 460.7) · net **−393.3** · traversal 576.4 |
| Range rank | **2nd largest absolute** range in the 21-day PRE_NY record (behind 09-21's 958.4); **3rd largest relative** (09-21 2.46x, 09-17 1.47x, 10-08 1.46x) |
| Scan | 12:48:12Z PRE_NY, price **30957.9**, **NEUTRAL / TWO-WAY −1**, dir **0**, `COHERENT_SHORT` high conf, `LOW_FUEL` |
| Direction | **no call** (score −1, inside the ±2 deadband). Post-scan **−166.5**, day net **−393.3** — same sign, so **no P-H divergence**; the 4th instance did not arrive. |
| Levels | **12 published / 10 touched = 0.83** — the highest hit rate since 09-22. 10 touches land on **7 distinct M5 bars** → inflation **1.43x**; rows above scan **5/7 (0.71)**, rows below **5/5 (1.00)** |
| Fuel | budget **115.6** · extension **326.2** · error **+210.6** (**2.82x** of budget) · traversal 576.4 = **4.99x** budget |
| Fuel ledger (H1) | raw per-day **+16.4** (n=26) / per-scan **+17.8** (n=30). Ex-09-24: per-day **+16.5** (n=25), **−6.5** ex-09-21 (n=24), **MAE 101.3** against a mean per-day budget of **124.8** — the typical error is **81% of the typical budget** (was 78% yesterday). |
| Fuel streak | the three-day over-read **ended**: −66.5 (10-05), −180.1 (10-06), −97.8 (10-07), **+210.6 (10-08)**. It is now the **second-largest under-read in the record**, behind only 09-21's +569.2. |
| Vol boundaries | VXN-implied daily range **409.5** vs realised **671.3** → **under by 261.8** (realised **1.64x** the VXN read), the worst of the four-day comparison. Straddle EM band **30739 .. 31177**, close **30791.5 — INSIDE** (H8: **5 inside / 1 outside**, obs **6 of 10**) |
| All-time | track raw **16 right / 8 wrong / 7 no-call**; ex-09-24 **15 / 8 / 7**, mean level hit rate **0.54**. **Not comparable to yesterday's 15 / 9 / 7 — a day aged out of the bar window overnight, see §3(e).** |

## 2. What the levels actually did

The board was the best part of the document. 10 of 12 rows were touched, the two
that were not are the two that are never within reach, and the sequence the
levels described — rally into the flip, fail, accelerate down through everything
— is what happened.

**GAMMA FLIP 31125.1 (+167, _(stretch)_).** *"We're BELOW it: they're pushing, so
don't fade. Reclaim and hold above and fading becomes valid again."* Price rallied
**+187.2** off the scan, tagged the flip at **14:25Z** and exceeded it by only
**20.0**, never settled above, and then fell **576.4pts** to 30568.7 at 17:25Z.
Closed **−333.6 below** it. The reclaim condition was tested and failed, and the
failure was the trade of the day. **H4's third consecutive clean read** (09-30,
10-07 as magnet/settlement, 10-08 as rejected resistance); the row needs 5 days
and now has them in substance, but as a positive, not a proposal.

**CALL WALL 31209.6 (+252, _(stretch)_) — never touched post-scan.** Post-scan
high 31145.1, missed by 64.5. **No P-E instance, stated explicitly as directed:**
there is no intraday penetration and no close-side read, so the 10-06 closure of
P-E as a continuum stands untouched and no mode-discriminator search is reopened.
With both walls 248–252pts away on a 116pt budget, a no-instance outcome was the
expected and correct result. Worth recording separately: this row carried
*"desks must SELL as price rises into it, so rallies stall. Take profit into
it"* while the **same graded session had already traded 37 touches of it and
spent 19 bars entirely above it** overnight (open 31184.8, overnight high
31240.0). The ceiling prose was written about a level the session had already
lived on top of.

**London High 31064.0 (+106), PWH 31037.1 (+79), Asia Low 31024.6 (+67),
London Low prev-day 30979.1 (+21).** All four were taken out to the upside in the
13:20–14:25Z rally and then all four became resistance for the rest of the day.
That is the `structure +1` row's *"3 above / 2 below — draw higher"* being right
on path and wrong on destination: the upside pools were swept first, the day
closed 393 lower. Verdicts on these rows are badly understated — see M6 in §3.

**PDL + NY Low 30918.0 (−40) ⭐ and Equal lows ×3 30895.1 (−63) ⭐ — the two
costliest rows on the board.** *"Sweep it, wait for a higher low on the 1m, then
CISD = long"* and *"3 touches at this price, never traded through — a real stop
cluster. Prime S1 sweep trigger."* Both are **long** triggers, in a document
whose top line says *"Strategy-1 fades have a materially lower hit rate here —
only take them at the far walls"*. Both were sliced on the way to 30568.7, 349.3
and 326.4pts of further downside respectively. And the sweep each one offers as a
**forward** trigger had **already completed pre-scan**: the pre-scan low was
**30894.9**, i.e. **23.1 through the PDL** and **0.2 through the "never traded
through" equal lows. The factual claim on the ⭐ row was false in its own
session.** Session-context field, 10th instance, and the same sub-shape as
09-30's 31115.8.

**MAX PAIN 30839.6 (−118 = 0.26x ADR14).** Reached 16:45Z, and the close
**30791.5 finished 48.1 below it (0.10x ADR)** having started 118.3 above.
This is the **third within-reach test** under the tightened ≤0.5-ADR threshold
and the **first hit** (09-16 against, 10-07 against, 10-08 for), on a **Thursday**
— the day the row's own qualifier says it should be strong. One data point in
favour of a qualifier that is 2-for-3 against; the day-of-week claim stays
ungradeable while M6 contaminates the reaction verdict.

**PUT WALL 30709.6 (−248, ●●●●○ 0.65bn, _(stretch)_) — the second consecutive
session in which the put wall break marked the day's low.** The regime rider:
*"BUT today the desks are pushing moves along — if it breaks, expect it to speed
UP, not bounce. Don't buy the break."*

| time | what happened |
|---|---|
| 12:48Z | scan, 30957.9, −1 NEUTRAL, LOW_FUEL, 115.6 budget |
| 14:25Z | post-scan high **31145.1** — gamma flip tagged, exceeded by 20.0, rejected |
| 16:45Z | one M5 bar **30968.5 → 30844.7, −123.8**; max pain taken |
| 17:00Z | first touch of the PUT WALL (30704.3) |
| **17:25Z** | session low **30568.7 — 140.9 below the wall, 0.31x ADR14, 25 minutes after first touch** |
| 19:40Z | back above the wall, holds to the close |
| 20:55Z | close **30791.5 = +81.9 above the put wall, +131.9 above the structural put wall** |

**Exactly the 10-07 shape, exactly the same error.** The acceleration claim was
mechanically right and economically irrelevant: it bought 140.9pts in 25 minutes
and that was the whole of the downside. Price then reclaimed both put levels and
closed above both. *For the second day running the level the document told the
user not to buy was the day's floor, and for the second day running the trade
that worked was the S1 fade the same document discouraged.* **n=2 on this shape,
nothing proposed** — but it is the same wall, the same rider and the same
outcome, and the third instance should settle it. What would make it measurable
is still the field the board does not have: for each wall, the distance it has
run through on prior breaks in the same gamma regime (10-07: 107.8 = 0.23x ADR;
10-08: 140.9 = 0.31x ADR — two numbers, already remarkably close).

**STRUCTURAL PUT WALL 30659.6 (−298 = 0.65x ADR14) — the FIRST structural row
ever touched.** Sliced by 90.9, reclaimed, closed +131.9 above. The P3/H6 census
read *"0 touches on 11 publications across 10 trading days, and it has never been
within 200pts of price"* yesterday. It now reads **1 touch on 13 publications**,
and the census needs splitting by side: the **structural CALL wall** is
**0 for 12 and was +502 (1.09x ADR) away today**, while the **structural PUT
wall** was within reach, was reached, and behaved (the slice stopped 90.9 in and
the level ended the day as support). See §4.

**Nothing on the board was noise today.** No row was published that price
ignored at a distance it could have reached.

## 3. What was wrong, and why

`−1 = gamma −5 · macro +3 · vol +1 · rates −1 · breadth +1` (structure 0,
fuel 0, news 0).

**(a) The engine's single best signal was outvoted 7-to-5 by four rows that the
day falsified, two of which are one stale FRED print counted twice.** The gamma
block was right about direction *and* about range:

| row | pts | its own words | verdict |
|---|---|---|---|
| gamma | **−3** | below flip 31125.1 by 167.2 — *"downside accelerates, rallies unstable"* | **right, and precisely** — the rally died 20.0 above the flip; the downside ran −123.8 in one M5 bar and 576.4 in three hours |
| gamma | **−2** | week net GEX −5.945 → *"expansion likely"* | **right** — 1.46x ADR14 |
| macro | **+3** | DFII10 real yield, *"down 4bp **as of 2026-10-06**… ⚠️ FRED has not published since 2026-10-06 (2 business days ago)"* | **wrong, and stale** |
| macro | **+1** | DGS10, *"moved 4bp down (2026-10-05 to 2026-10-06)"* — same instrument, same window | **wrong, and a duplicate** |
| vol | **+1** | VIX9D/VIX 0.75 contango, *"calm, mean-reversion favoured, mild upward drift"* and *"a calmer, more rangebound day"* | **wrong on both clauses** — 1.46x ADR, net −393.3 |
| breadth | **+1** | *"NDX −0.21% vs ES −0.41% — tech leading, genuine risk appetite"* | **wrong** — both legs negative, printed as appetite (D22(a) shape); NDX then fell 1.27% |
| structure | **+1** | *"in-reach unmitigated pools: 3 above / 2 below — draw higher"* | **right for 97 minutes** — the upside pools were swept to 31145.1 first, then the day closed 393 lower. The only positive row the day validated at all. |

Counterfactuals, computed exactly:

| variant | score | label | dir | grade |
|---|---|---|---|---|
| **as published** | **−1** | NEUTRAL / TWO-WAY | 0 | **no call** |
| de-duplicate only (drop DGS10 +1) | −2 | NEUTRAL / TWO-WAY | 0 | no call — **no change** |
| age-gate only (zero the 10-06 DFII10 +3) | −4 | MILDLY BEARISH | −1 | **CORRECT** |
| both | −5 | MILDLY BEARISH | −1 | **CORRECT** |
| gamma block alone | −5 | MILDLY BEARISH | −1 | **CORRECT** |

**This is the exact reverse of 10-07, and it matters.** Yesterday de-duplication
changed the label and the age gate changed nothing; today **de-duplication
changes nothing and the age gate alone converts a no-call into a correct
MILDLY BEARISH on a 671pt day.** Per the standing retraction, **H18/P1's accuracy
case stays retracted and is NOT re-proposed** — `HY OAS` still renders no
observation date (**6th consecutive session**), so the age gate cannot be
evaluated cleanly. The cost of that blocker is now explicit: in the last two
sessions the age gate has decided the published call twice, in opposite
directions, and the register is not allowed to say anything about it.

**The duplication finding itself is unchanged and is now 21 of 21.** DFII10 +3
and DGS10 +1, same instrument, same 10-05→10-06 window, same sign: whenever
DFII10 scores non-zero, DGS10 scores the same sign — **21 of 21 across 23 graded
days**. A guaranteed ±4 off one FRED observation.

**And today the stale pair contradicted the live row, which was right.** `macro`
DFII10/DGS10 read *yields falling, tailwind for tech* (**+4**, observation
10-06); the live `rates` row read *"US10y 5.316 (+0.74%) — yields up, multiple
compression, BEARISH tech"* (**−1**). Yields were up and tech fell 393. The
live-vs-stale sign agreement census moves to **7 of 17** days both are non-zero —
still a coin flip, still with the stale side carrying four times the weight.
**H18/P1 instance 15**, appended to the existing entry as directed.

**(b) The internal contradiction the task asked about: the regime block was
right, the fuel block was wrong, and the margin is the largest on record.**

| block | instruction | outcome |
|---|---|---|
| Regime (§2) | *"Sweeps tend to keep running rather than fail. **Fading is the wrong trade today** — Strategy 2 (go with the move)"* + `COHERENT_SHORT`: *"Today's ADR can be exceeded — don't cap the target too early"* | **RIGHT** — 1.46x ADR, 576.4pt one-way leg |
| Fuel (§3) | *"The range is close to done… expect price to keep MOVING but mostly **inside** the extremes rather than making new ones — **favour fades over chasing breaks**"* | **WRONG** — 326.2 of new range, 2.82x the budget |

The logged coherence item (`LOW_FUEL` + below the flip) reaches **4 instances**
and the census is now **3-1 to the gamma block**: 09-14 3.1x gamma, 09-15 0.16x
fuel, 09-28 2.7x gamma, **10-08 2.82x gamma**. The fix already proposed — in
short gamma the fuel block must not recommend fades and must present the budget
as likely to be exceeded, or the brief must name which block is live — is
re-affirmed unchanged, and today is its largest-margin instance. Note the
document contained the right answer in a third place as well: the **DOWNSIDE
path** sentence advertised *"clear… to 30559.6 (398pts, 0.86x ADR)… If it goes,
it has room"* — **the session low was 30568.7, 9.1pts short of that number**,
while the fuel block three lines above it said 115.6. A **3.4x internal
disagreement inside one section**, and the larger number was right to 9 points.
Second consecutive instance of that disagreement (10-07: 2.6x); n=2, logged, not
proposed, and now with a sign: on both days the clear-path distance beat the
budget as a forecast of reach.

**(c) The fuel call, graded directly.** `LOW_FUEL` was published on
`adr_used_pct 74.9` and `fuel_ratio 1.66` with 115.6pts of raw budget left; the
range then grew **326.2** and the day printed the **2nd-largest absolute range in
the record**. So: **the over-read streak did not extend to four — it reversed,
and hard.** The model was not "finally right on a LOW_FUEL day"; it was wrong by
the second-largest margin on file, in the opposite direction to the previous
three days. That answers the question the task posed about where the defect sits:
**it is not a sign error that a multiplier could fix in either direction, and
it is not the state label alone.** Measured properly (§4a), the budget has **no
skill at all** against the quantity it forecasts.

One tempting reading, killed before it reaches §4: *"the three widest days in the
record (09-21 2.46x, 09-17 1.47x, 10-08 1.46x) were all published LOW_FUEL with
budgets of 18.7 / 0.0 / 115.6"*. That is **definitionally driven** — realised
range includes the already-spent portion, and the spent portion is what sets the
budget, so range/ADR and budget are mechanically anti-correlated. The clean
quantity is **extension**, and `r(adr_used_pct, extension) = 0.008` over 21 days
(−0.242 ex-09-21). **The 09-21 rejection of "hot early pace predicts expansion"
stands and is stronger at n=21 than it was at n=10.**

**(d) M6, session 21, and the worst ratio in the record for the second day
running — again on the put wall.** `SETTLE_TOL = 25.0`; reported
`worst_excursion` is measured from the settled point, true excursion measured
first touch → close:

| level | reported verdict | reported | true f.t.→close | ratio | verdict if measured properly |
|---|---|---|---|---|---|
| 31125.1 GAMMA FLIP | *"held as resistance 390min, worst +9.3"* | +9.3 | **+20.0** | 2.15x | held ✓ |
| 31064.0 London High | *"held as resistance 375min, worst +12.2"* | +12.2 | **+81.1** | **6.65x** | **lost** |
| 31037.1 PWH | *"broke UP — lost by 39.1"* | +39.1 | **+108.0** | 2.76x | lost ✓ (understated) |
| 31024.6 Asia Low | *"held as resistance 275min, worst +8.8"* | +8.8 | **+120.5** | **13.69x** | **lost** |
| 30979.1 London Low | *"broke UP — lost by 37.6"* | +37.6 | **+166.0** | 4.41x | lost ✓ (understated) |
| 30918.0 PDL ⭐ | *"broke UP — lost by 53.8"* | +53.8 | **+53.8** | 1.00x | lost ✓ |
| 30895.1 Equal lows ⭐ | *"broke UP — lost by 76.7"* | +76.7 | **+76.7** | 1.00x | lost ✓ |
| 30839.6 MAX PAIN | *"held as resistance 250min, worst +24.5"* | +24.5 | **+132.2** | **5.40x** | **lost** |
| **30709.6 PUT WALL** | *"held as **support** 75min, worst −9.4"* | **−9.4** | **−140.9** | **14.99x** | **lost** |
| 30659.6 STRUCTURAL PUT WALL | *"broke DOWN — lost by 30.0"* | −30.0 | **−90.9** | 3.03x | lost ✓ (understated) |

**8 of 10 understate; 4 of 5 "held" verdicts invert to "lost".** The **14.99x**
on the PUT WALL beats yesterday's 14.77x and is the worst in the series — and it
is the second consecutive session in which the single most load-bearing row of
the day is the one the grader misreports. Read cold, `review_day` says the
0.65bn put wall *held as support for 75 minutes* on a day price sliced it by
**140.9pts = 0.31x ADR14**. Also note the wording on five rows: *"broke **UP**
through it"* on a day that closed −393.3 — the word is derived from the settled
side, not from the side the breach was on, which is the 10-06 inversion again.
**Re-proposed unchanged, 21st session.**

**(e) D26 has swallowed another day, and the all-time scoreboard moved overnight
with no new information.** `track.py` printed:

> HELD BACK - day not finished (grades after 21:00 UTC on its own date):
>   2026-08-25  98 bars so far
>   2026-10-09  180 bars so far

10-09 is held back **correctly** (today's session, in progress). **2026-08-25
finished 44 days ago**; it is served partial by the `days=min(days_back, 45)` cap
and filed under a label that reads as *pending*. 08-24 vanished from the table
entirely. Measured damage, today: **two graded scans left the sample, one of them
a WRONG**, so the all-time direction record went **15 / 9 / 7 → 15 / 8 / 7
(ex-09-24)** while a scan was *added*. **A wrong call was deleted from the
record by the calendar.** This is the second consecutive day D26 has eaten
evidence, and D26(b) gets a free reinforcement: **the schema already has an
`outcome` block, `journal.py:106` writes it as `None`, and it is `None` on all
60 scan files in the journal.** The place to persist graded outcomes exists and
nothing has ever written to it.

## 4. Change proposals — only material ones

### (a) P4, decided by measurement: the range budget has NEGATIVE skill, and the prose it drives should go

**Not a new ID.** I grepped for one and this claim already lives in **P4**
(*"stop quoting a point-precise budget above zero"*, standing since 09-14) and is
the question **H1** was opened to answer. Nothing new was allocated; the
allocation block is unchanged (next free remains **H26 · D27 · P-I**).

**The evidence, 21 PRE_NY trading days (09-24 excluded; 08-24/08-25 aged out):**

| forecast of range extension | MAE |
|---|---|
| **the published budget** | **117.7** |
| a fixed constant = the sample median extension (128.2) | **92.5** |
| an honest leave-one-out median constant | **98.0** |
| a fixed constant of 120.0 | 92.9 |

- `r(budget, extension) = −0.106` (**+0.175** ex-09-21). **The budget carries no
  information about the quantity it forecasts, and loses to a constant by ~20pts
  of MAE.**
- `r(adr_used_pct, error) = +0.443` looks like a signal and is **definitional** —
  error = extension − budget and budget is a linear function of the pace, so
  `r(budget, error) = −0.562` falls straight out of the arithmetic. This is the
  one-sided-estimator caveat already recorded under H1 on 09-17, quantified.
- Conditional means are contaminated by the same one-sidedness and are reported
  only so nobody rediscovers them as a finding: LOW_FUEL/EXHAUSTED scans
  **+54.7** mean error (n=17, mean budget 50.6) vs non-low-fuel **−34.1**
  (n=12, mean budget 219.7). The negative error is **floored at −budget**, so a
  small budget can only be wrong upward. Do not fit a state-conditional
  multiplier to this.

**What to change (user decides, no code touched):**
1. Stop deriving prose from `remaining_budget` as if it were a forecast. The
   specific string is `_FUEL_MEANING["LOW_FUEL"]` — *"The range is close to
   done… favour fades over chasing breaks"* — which was the wrong instruction
   today, is the losing side of the 3-1 coherence census, and is driven by a
   number with no measured skill.
2. If a number must be printed, print the sample's own central value with its
   error (median extension ≈ **128**, MAE ≈ **98**) and label the budget as what
   it actually is — an accounting identity, `ADR14 − range used` — not a
   prediction.
3. Add the constant baseline to `track.py` so this skill test re-runs every day
   rather than being rediscovered.

**Expected effect:** no change to any direction score (both `fuel` rows score 0
on every scan in the record). It removes the least accurate number in the
document and the prose it generates. **Blast radius to check before shipping:**
the `_(stretch)_` tag, the board's range filter (D7 exempts walls, D15/P-D cover
the zero case) and `path_read()`'s reach all read the same variable.
**The multiplier branch stays closed** — this is a baseline comparison at n=21,
not a parameter fitted to a tail. H1's own question is now answered: *no, the
budget does not forecast range extension accurately, and it is beaten by a
constant.*

### (b) P3 / H6: narrow the "stop publishing structural walls" recommendation to the CALL side

**New evidence, and it is a counter-instance to a standing recommendation.**
The STRUCTURAL PUT WALL 30659.6 was **the first structural row ever touched** —
reached at 17:20Z from 298pts (0.65x ADR14), sliced 90.9, reclaimed, closed
+131.9 above. Census now:

| row | publications | touched | ever within 200pts |
|---|---|---|---|
| STRUCTURAL CALL WALL | **12** | **0** | **never** (today +502 = 1.09x ADR) |
| STRUCTURAL PUT WALL | 2 | **1** | yes, today |

**Proposed narrowing:** keep P3's exclusion of `kind: structural` from the hit
rate (it is a denominator argument and unaffected), but the stronger
*"stop publishing it"* recommendation should apply to the **structural call wall
only** — 12 publications, 0 touches, never once in range. The put side has one
day of evidence that it is a real level and must not be dropped on the strength
of a census that was measuring the other side. Dropping a row on the one session
it fires is the mistake the 10-07 NFCI note already warned about.

### Not proposed — observations appended, nothing to change

- **H22 — the pre-registered direction test, finally run, is null.** The register
  asked for `week net GEX → realised direction` across the days already on
  record. Grading sign(week net GEX) against realised post-scan direction on all
  gradeable PRE_NY days (09-24 excluded; 09-17 and 09-25 unusable, no post-scan
  sign): **11 right / 8 wrong = 58%, n=19** (p≈0.32 against a coin). Range side,
  n=7: Spearman(GEX, range/ADR) = **−0.179** — the sign is the one the row
  claims, the magnitude is noise. 10-08 is the most negative GEX in the table
  (−5.945) and produced the widest day (1.46x), which is one point *for* the row,
  and 10-07 (−4.447 → 0.79x) is one against.
  **Counterfactual run before proposing anything:** zeroing the row's ±2 across
  all 21 gradeable scans gives **9 right / 4 wrong / 8 no-call** against the
  published **11 / 7 / 3** — it converts 3 wrongs *and* 2 rights into no-calls,
  i.e. it mostly shrinks conviction near the deadband rather than fixing
  accuracy, and on **this** day the row was right. **Nothing proposed.** The
  test is done and the answer is "no information, and removing it is not
  obviously an improvement".
- **The gamma-vs-vol conflict, 3rd co-occurrence and the first in the mirrored
  configuration.** Today it was `gamma −2 "expansion likely"` against
  `vol +1 "calm, mean-reversion favoured… a calmer, more rangebound day"` —
  the reverse of 09-16/09-17's pinning-vs-backwardation pairing. **Gamma was
  right** (1.46x ADR). Record: 09-16 vol, 09-17 gamma, 10-08 gamma. **The
  pre-registered test as written — "positive net GEX **and** backwardated
  VIX9D/VIX" — cannot absorb this day**, because the configuration is inverted.
  That is worth fixing in the test definition before more data is discarded:
  record the pair and the realised range every scan regardless of which way
  round the signs fall. H21 closed the VIX9D/VIX→*fuel* claim; nothing is
  watching its *direction* points, and today they were wrong.
- **H2 — second counter-instance, and the fade lost badly.** `LOW_FUEL`, price
  **18.3% up the pre-scan range** and 63.0 above the pre-scan low — the fade
  (long the low, expecting no extension) was run over by **326.2pts** of new
  range. Record: **3 for the fade (08-24, 08-25, 09-14) / 2 against (09-21,
  10-08)**, and both "against" instances are an order of magnitude larger than
  any "for". Caveat preserved: the engine issued **no directional call**, so this
  is evidence about the *fuel* claim, not against the bias engine. H2's empirical
  claim remains unproven in both directions.
- **H18 / P1 — instance 15.** Duplication **21 of 21**; live-vs-stale agreement
  **7 of 17**; `HY OAS` renders no observation date for the **6th** consecutive
  session. Accuracy case stays **retracted**, as directed. The DFII10 textual
  sub-defect **did fire** today in the correct direction by luck: observation
  2026-10-06, scan 2026-10-08, and *"this is last week's reading"* is **true**
  for once — the string is still unconditional.
- **M6 — session 21, re-proposed unchanged** (§3d). Compute `worst_excursion`
  over the whole post-touch window or report both; derive DOWN/UP from the side
  the breach was on; do not seed the settled read from `"open"`.
- **D26 — appended, already PROPOSED** (§3e), plus the new free argument: the
  `outcome` block exists in the schema and is `None` on 60 of 60 scan files.
- **P-H — no 4th instance.** Post-scan −166.5 and day net −393.3 agree in sign;
  the basis could not matter on a no-call anyway. Stays **n=3**, PROPOSED,
  recommended basis post-scan, applied here and stated at the top.
- **P-B(b) — 14th session.** `merge_tol = max(3.0, 460.7 × 0.008) = **3.69**`
  against `TOUCH_TOL = **8.0**`. **No published pair falls in the guaranteed
  3.69–8.0 window** (smallest gap on the board is 12.5, 31037.1/31024.6), so no
  double-count fired. Touch inflation **1.43x** (10 touches → 7 distinct M5 bars:
  1, 6, 17, 19, 47, 50, 54). Proposal unchanged: `merge_tol >= TOUCH_TOL`, and
  always report distinct touch events beside the raw rate. **Placement note:**
  rows below the scan went **5/5**, rows above **5/7** — a genuinely two-way day,
  so today's 0.83 is the least distorted hit rate in the recent series and should
  not be read as the board improving.
- **Session-context field — 10th session.** 8 of 12 published rows had been
  interacted with pre-scan under the banner *"New trading day… everything below
  is fresh"*: CALL WALL 31209.6 (**37** touches, 19 bars entirely above), Asia Low
  31024.6 (30), PWH 31037.1 (27), London Low 30979.1 (18), PDL 30918.0 (13),
  GAMMA FLIP 31125.1 (11), London High 31064.0 (7), Equal lows 30895.1 (3, and
  the pre-scan low **30894.9 is 0.2 through it**). Already PROPOSED 09-29.
- **P-G — instance #16.** `Asia Low (today) 31024.6`, **+66.7 above** the scan,
  published as *"the next session usually runs the stops **below it**"* — the
  stops below it had already been run, by 130pts, in this same session. A second
  row, `London Low (prev-day) 30979.1` at **+21.2**, carries the same string and
  falls **inside** the ±25pt "sitting on it" band the proposal already specifies,
  so the proposed fix would have caught one of the two cleanly and softened the
  other. Already PROPOSED.
- **H14 — the regime-aware wall note worked again.** Both put rows carried
  *"today the desks are pushing moves along — if it breaks, expect it to speed
  UP, not bounce"*, and the break did accelerate (−140.9 in 25 min). The 09-10
  fix is doing its job; the residual problem is that the note has no horizon
  (§2, put wall), not that it is regime-blind.
- **D23 — 8th residual.** Board offset **+9.6** (NDX reference 30948.3, cash last
  traded 2026-10-07T16:14:59 rolled forward by the NQ move −211.8, against CFD
  30957.9; basis `nq_implied`, greeks `repriced_bs_at_current_spot`). Section 7's
  own offset **−187.8**, matched to feed time 2026-10-08 11:59Z. Gap **197.4**;
  CFD move 11:55Z bar open 30970.0 → scan 30957.9 = **−12.1**; **residual
  +209.5**. Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 /
  +209.5` — **five of eight sit in 190–250**, and the intervening move explains
  2 of 8. The measured negative result stands. Damage **none** (section 7 is
  research-only and had no volume).
- **D25 — fired again**, as it does on every pre-NY scan: *"**The dominant strike
  is stable** at 0 across 6 samples — positioning is settled there"*, three lines
  below *"No volume has traded yet today"*. **21st consecutive pre-NY scan.**
  Instance appended, not re-opened. Damage none.
- **D24 — unfalsifiable today.** `inputs.events_24h` is **empty** and the brief
  printed *"No High/Medium US events in the next 24h"*, so the forward-only
  renderer had nothing to hide or reveal. Note for the record: this was **not**
  an H20 instance either way — H20 is CLOSED-NEGATIVE and 10-08 carried no
  High/Medium event at all.
- **D21 — no instance.** The band row scored **0** (*"price mid-band
  (30709.6–31209.6), 50% up the range"*); neither the top-of-band −2 nor the
  bottom-of-band +2 branch fired. The `−2` census is unchanged.
- **H19 / D18 / D20 — coverage 1.9%.** 137 headlines → 53 relevant → **1
  auto-scored** (0 bull / 1 bear) → `news` **0**. The one scored headline
  (*"Federal Reserve officials expect another rate hike will be needed this
  year"*, hawkish, ~180pts/90min) was **directionally right on a −393pt day and
  contributed nothing**, because the magnitude tracks match count. The judgement
  list carried *"Fed's Waller signals further rate hikes as inflation stalls"* —
  the same theme, the day's dominant theme, uncounted. Second consecutive
  session where the news block's only correct read was discarded while a
  multi-day-old FRED print was counted twice.
- **H17 — no instance.** Post-scan move **−166.5 = 24.8%** of the session range,
  far above the 5% deadband, and the scan was a no-call regardless. Stays 1 of 3.
- **H23 — no instance.** Both paths were flagged *clear*, so no named brake
  existed to test; record unchanged at **6 sliced / 1 capped, n=7**. The
  clear-path *distance* observation is in §3(b) and is n=2, not an H23 instance.
- **H8 — observation 6 of 10.** Straddle 258pts (ATM IV 14.4%) → EM ±219 → band
  30739 .. 31177; close 30791.5 **INSIDE** (and 31145.1 / 30568.7 both outside
  intraday, exactly as the caveat says). **5 inside / 1 outside.** VXN-implied
  range 409.5 vs realised 671.3 — VXN **under by 261.8**, the worst of the four
  days compared so far (0.91x, 1.00x-ish, now 0.61x of realised).
- **H10 — did not fire.** `structure 0`, *"price inside the prior-week range
  (30101.2–31037.1)"*; neither ±3 branch fired, so the 3-for-5 record is
  unchanged and the pre-registered falsification test was not met. Worth one
  line: price was **79.2 below PWH** at the scan, **cleared PWH by 108.0**
  intraday, and closed **245.6 below** it — the rule scored a day that traded
  both sides of the prior-week high identically to a mid-range day, which is the
  proximity gap logged on 10-07.
- **Dead-weight audit — refreshed to 28 scans.** `macro` NFCI **2 / 28** (−1
  again, second consecutive firing — the 10-07 decision to return it to
  observation rather than drop it is vindicated); `macro` yield curve 10y–2y
  **0 / 28**; `macro` WALCL/RRP **5 / 28, 0 of the last 23**. The standing
  proposal to drop rows stays narrowed to the **yield-curve row and WALCL/RRP**.
  Also unscored today: `vol` VXN, `vol` VXN/VIX, `vol` VVIX, `rates` DXY, both
  `fuel` rows, `structure` prior-week, `macro` HY OAS, `news` (×2), `breadth`
  mega-cap, `events` (**absent again — P-C's row has never scored in the
  record**).
- **P-E / P-E(b) — no instance, stated explicitly.** CALL WALL 31209.6 published
  at +252 and **never touched post-scan** (missed by 64.5): no intraday
  penetration, no close-side read. The board named **no shelf brake** on either
  side. The 10-06 closure stands: P-E is a **continuum**, the two-mode framing is
  not resumed, no discriminator search reopened. With both walls 248–252pts out
  on a 116pt budget this was the expected outcome.

## Journal hygiene

No fabricated or backfilled entries; **no `prediction` block touched**, and no
`REVIEW.md` created for any day that lacks a prediction. One scan file for 10-08
(`1248-preny.json` + `.md`), `is_trading_day: true`, `review_day` reports **0
test artefacts** for the day (`track.py` excludes 6 across the record).
**09-24 quarantined by hand — ninth consecutive review to carry it**; the 09-29
proposal for a schema `quarantine` field is reaffirmed, and the cost is now
compounded by D26: `track.py` prints 09-24 inside every statistic *and* the
sample it prints them over changes with the calendar, so no quoted figure is
reproducible. **09-09 and 09-25 still have no `REVIEW.md`, and none was created
or back-dated.** 2026-10-09's scan exists (`1249-preny.json`,
`is_trading_day: true`) and is **correctly** held back (180 bars);
**2026-08-25 is held back INCORRECTLY — see D26.** No new IDs were allocated by
this review; next free remains **H26 · D27 · P-I**.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
