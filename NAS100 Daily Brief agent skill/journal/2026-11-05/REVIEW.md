# REVIEW — 2026-11-05 (Thu) — direction right, magnitude wrong by 7.7×, and §3 contradicted itself

_Graded 2026-11-06 from `review_day.py --json` (1 scan, `LONDON` 12:47Z) and
`track.py --json` (31 trading days, 31 scans, `actionable: YES`). **D29's G1–G4
applied unchanged, not re-decided**, per `journal/2026-11-02/REVIEW.md §0`._

## 0. Grading rules applied

- **(G1)** `PRE_NY`-keyed pre-scan censuses do **not** accrue. The parallel
  `LONDON/EST (from 2026-11-02)` censuses go to **n=4**, exactly as the 11-05
  review pre-registered.
- **(G2)** The fuel-error series **accepts** this scan; the error is tagged
  `LONDON/EST`. Pre-scan market time is the Tue–Fri EST **14h45m**.
- **(G3)** Everything else grades normally.
- **(G4)** The post-close-hour census stays **CLOSED at n=2** (structural, per
  D30 — the graded day ends at the cash close).

---

## 1. Scoreboard

| | |
|---|---|
| call | **MILDLY BEARISH −4** at 28199.0 (`LONDON`, NY cash +102 min), `COHERENT_SHORT`, `LOW_FUEL`, Strategy 2 |
| session O / H / L / C | **28443.0 / 28542.5 / 26593.0 / 26639.2** (276 bars) |
| range · net | **1949.5** (**2.832× ADR14 688.3**) · **−1803.8** |
| direction, post-scan (P-H basis) | **−1554.1 → CORRECT** |
| direction, day-net | **−1803.8 → CORRECT** · bases **agree**, **no P-H deciding instance** |
| levels | **15 published / 7 touched = 0.47** (31-day mean **0.51**) |
| …by side of the scan | **7 of 7 below price touched = 1.00** · **0 of 8 above price = 0.00** |
| fuel | budget **187.2** vs extension **1448.4** → **7.74×**, error **+1261.2**, `UNDER-estimated` |
| traversal vs budget | **1656.4 = 8.85×** |
| VXN-implied range | **445.5** — the figure §3 told the reader to prefer — realised **1949.5**, under by **1504.0** |
| ATM straddle band (rest of day) | ±**349** → 27850 .. 28548; close **26639.2 OUTSIDE by 1210.8** (3.47× the half-width) |
| \|post\|/ADR · range/ADR | **2.258** · **2.832** |
| offset | **−9.2** (`nq_implied`, `repriced_bs_at_current_spot`) — **clean**, D6 breach series stays at **six** |
| hygiene | 1 scan, `is_trading_day: true`, **0 test artefacts** |

**Three figures are the largest in the 31-day record, and not by a little:**

| | 2026-11-05 | previous max | ratio |
|---|---|---|---|
| fuel error (H1/P4) | **+1261.2** | +479.3 (10-16) | **2.63×** |
| range / ADR14 | **2.832** | 2.126 (11-04) | 1.33× |
| \|post-scan\| / ADR14 | **2.258** | 0.925 (11-02, in-window) | 2.44× |

**Direction, from source, n=30 gradeable (09-24 hand-quarantined):**
**12/24 = 50.0%** post-scan, 6 no-calls. **Identical to yesterday's figure, and
that is D16/D26, not stability:** 09-22 (CORRECT) aged out of the 45-day bar
window on the same run that 11-05 (CORRECT) entered it. A genuinely new
observation bought **zero** movement in the headline statistic by exact
substitution at the window edge. **`track.py` reports 31 days / 31 scans; the
journal holds 47 finished trading-day directories — D26's gap is now 16.**

**H1/P4 — the THIRTEENTH value under one series name, and the largest.** The
31-day per-day mean error went **+50.2 → +89.3** (ex-09-24: **+91.8**) on one
session: **the mean rose 78% on one observation, which contributes 45.6% of the whole
31-day error sum.** H1 is already **ANSWERED-NEGATIVE** (the budget loses to a constant
over 21 days); today adds that the estimator is not merely noisy but
**fat-tailed on the positive side**, which is the side that costs a trader money.
**No multiplier is proposed** — the H1 lesson and P-F's own prohibition stand.

---

## 2. What the levels actually did

**Every published level below the scan was touched. Not one of the eight above
it was.** On a day the document itself called `COHERENT_SHORT`, below-flip,
*"fading is the wrong trade today"*, the board spent **8 of 15 rows (53%)** on
the side its own §2 forbade trading. The closest unreached row, `NY Low
(prev-day)` at **+82**, is 5.3% of the distance price travelled the other way.

### The rows that worked

| level | what the brief said | what happened | verdict |
|---|---|---|---|
| **27890.8** PUT WALL ●●●●● 0.94bn | *"BUT today the desks are pushing moves along — if it breaks, expect it to speed UP, not bounce. **Don't buy the break.**"* | lost; price ran a further **930.0 = 1.351× ADR** below it | **RIGHT, and the most consequential instance in the record.** H14's regime-aware rider earned its keep |
| **28166.0** PD mid | *"a target to aim AT, not a trigger"* | touched 12:50Z, broke up through, then held as **resistance 420 min**, worst **+16.6** | right in substance — it was the last thing price touched before the break |
| **28084.6** PWL | *"big pool, best Mon-Tue"* | lost, then held as **resistance 395 min**, worst **+20.2** | the pool was taken and never reclaimed |

### The rows that did not

| level | what the brief said | what happened | verdict |
|---|---|---|---|
| **28090.8** STRUCTURAL PUT WALL ●●●●● **1.79bn / 246k contracts** | *"the biggest concentration on the chain — **the floor for the WEEK/MONTH** … where a multi-day sell-off is defended"* | broke **DOWN** through on first touch (14:20Z), inverted to **resistance** within 5 min, price **926.3 = 1.346× ADR** below it by the close | **WRONG, and the hedge does not save it.** *"Not an intraday trigger"* excuses the timing; it does not excuse a claim about the **week** that failed inside one session |
| **28145.4** Equal lows ×2 + London Low ⭐ | *"a real stop cluster. **Prime S1 sweep trigger**"* | lost by 37.2 on first contact, price **809.7** below by the close | the ⭐ confluence row was the single worst S1 trigger available |
| **28041.4** Asia Low (today) | *"the next session usually runs the stops below it"* | lost, **1080.6** below by the close | the stops ran and kept running — correct event, useless as a level |

**The largest force figure ever published produced zero support.** 1.79bn /
246k contracts, `●●●●●`, at **−108** — by far the closest a structural wall has
come in the series (11-03's was −298.6; the 10-21 note recorded it had never
been within 200pts). **P3/H6 finally has a reachable instance and it is a clean
counter: census 2 clean / 1 confounded.** Below 3, so **nothing is proposed** —
but the entry's premise has flipped. It was *"the level is never reachable"*;
the open question is now *"does the force figure mean anything when it is"*.

**H14 — instance 8, and it BREAKS the pre-registered run-through band.** The
register's own text is *"run-through **0.22–0.48× ADR (n=5)**"*, extended to
0.499 by instance 7. Today: **1.351× ADR**, **2.7× the top of the band**. One
session does not falsify a band, but it does establish that the band was
measured on quiet days only, and the band was about to be shipped as a
**target**. See §4. First contact was **wrong again** (`first_touch`: *"traded
both sides — chopped around it"*, then 930 points) → **n=3** for that mechanism
inside H14.

### M6 — four inverted rows on one board, and they are the four that matter

`review_day.py:159–161` names the direction of the **adverse excursion** while
the sentence reads as the direction of the **break**. Today it printed *"broke
**UP** through it"* on **28145.4, 28123.3, 28041.4 and 27890.8** — every one of
them lost downward on a session that fell 1803.8 into its close. The put wall's
row reads *"broke UP through it — lost by **209.4**pts"* on a level price ended
**930.0 below**. **Reported as expected-by-identity** (session 40, driver found
and owned by M6); flagged here only because a human reading this grade cold
would take the board's four most important rows backwards.

**M6's open limb — `_first_touch`'s 12-bar window — fires on four rows.** It
returned *"traded both sides — chopped around it"* for 28145.4, 28123.3,
28041.4 and 27890.8, which price subsequently lost by **809.7 / 864.4 / 1080.6
/ 930.0**. A 60-minute verdict on a 1949-point day is a verdict about noise.

### Everything else, one line each

- **P-G — instance #41.** `28280.9 NY Low (prev-day)` published at **+82 ABOVE**
  the scan with *"the next session usually runs the stops **below** it"*. Those
  stops were already run. Prose-only, already **PROPOSED**, no new ID.
- **H23 — instance 24.** **No brake named on either side** (both paths *"clear
  … nothing structural to slow a breakdown … Do not fade it"*). The downside
  limb is the strongest supporting instance in the series: price went **1606**
  below the scan through a shelf stack §3 called *"clear"* for 558pts. Census of
  **named** brakes unchanged at 16 sliced / 3 capped / 4 never-reached.
- **H8 — post-closure instance 4, and the worst miss in the entry's life.** Band
  ±349 from the 11-05 ATM straddle (411pts, **ATM IV 30.4%**, down from 48.2%
  the session before); close **1210.8 outside**. Post-closure **2 hits / 2
  misses**. Entry stays **CLOSED ANSWERED-POSITIVE (8 of 10)** and is **NOT
  re-opened** — but its 8-of-10 was earned on sessions under 1.3× ADR.
- **H22 — n=21, and the FIRST session where the magnitude ordering works.** Week
  net GEX **−5.219bn** (the largest in the series) → *"expansion likely"* →
  **2.832× ADR** (the largest realised). Against 11-03's −3.083bn → 0.610× and
  11-04's −1.305bn → 2.126×, the series is still **not monotone**; what today
  adds is that the **extreme** point is correctly ordered. A threshold effect
  (|week GEX| > ~4bn) is **n=1** and is **not** proposed.
- **H2 — instance 11; the fade loses cleanly and by the largest margin in the
  series** (1448.4 of extension, 1656.4 of traversal, against a budget of
  187.2). The 11-05 review recorded the census as **8–2 / 10–0**; today advances
  both the way they already pointed. Census stays **suspended**.
- **H26 — the magnitude ordering BREAKS at the bottom of the scale.** `|score|
  4` → bucket **3–5** → **|post|/ADR 2.258**, the largest value in the record,
  produced by the **weakest non-neutral** call in the record's bearish set. On
  consecutive sessions: **−12 → +259 (WRONG)**, **−4 → −1804 (CORRECT)**.
- **No instance:** H4, H7, H9, H10 (price inside the prior-week range,
  `structure +0` — the reclaim condition is untested, **7th-firing count
  unchanged**), H11, H12/H13 (**D27 — no new instance**; the 11-05
  scan's 401 on `/v2/NDX/classic/gex_full` was already counted as the **11th
  consecutive** by the 11-05 review. Both untestable, **D25 SUPPRESSED**), H15/HY OAS
  (scored **−2**, the largest widening on record — not dead weight), H16, H17
  (post-scan move is 79.7% of session range, nowhere near a deadband), H19
  (below), H20/H21 (CLOSED-NEGATIVE), D8, D14, D15, P-I (`PIN_THEN_EXPAND` did
  not fire), **P-E** and **P-E(b)** (no call wall, shelf or secondary row was
  reached — every row above the scan went untouched), **P5** (§7 did not
  render, so the secondary table had no graded row). **D23 — observation 17,
  NO residual** (offset −9.2). **§7 did not
  render: 8th consecutive non-render, D25 frozen at 29.**

---

## 3. What was wrong, and why

The direction was right. **Nothing else about the magnitude was**, and three
separate components caused it.

### 3.1 Every row that pushed the score UP was a lagging read of the previous session

`bias_components` splits cleanly into forward-looking and backward-looking rows:

| | rows | points |
|---|---|---|
| **forward-looking** (options chain, credit, Fed) | gamma −3 −2 0 · macro −3 −1 −2 0 −1 0 | **−12** |
| **backward-looking** (prior-session % changes) | vol +2 +1 −1 0 · rates +3 0 · breadth +2 +1 | **+8** |
| structure / fuel / news | +1 0 −1 · 0 0 · 0 | **0** |
| **published** | | **−4** |

Every one of the five positive rows is a **percent change of a finished
session**: VXN −17.9%, US10y −1.17%, mega-cap avg +1.70%, NDX +0.91% vs ES
+0.03%, VIX9D/VIX 0.898. The forward-looking half of the engine said **−12** and
was right; the rear-view half said **+8** and cancelled two thirds of it. The
label printed was `MILDLY BEARISH` on a **2.832× ADR** collapse.

This is **D22(a)'s window mismatch** at scale — certain from the code, present
on every scan — and it is the mechanism, not a new claim. **No weight change is
proposed**, because D22(a) already owns it and because one session cannot
distinguish "rear-view rows are miscalibrated" from "11-05 was a regime break".

### 3.2 The vol complex priced calm into the largest range on record — and got PAID +3 for it

VXN 25.08 (−17.9%), VIX9D/VIX 0.898 contango, VVIX 90.41 *"no tail-hedge bid"*,
ATM IV 30.4% (down from 48.2%), VXN-implied range 445.5. §2's prose: *"a calmer,
more rangebound day."* Realised: **1949.5**, 4.38× the VXN figure, with the ATM
band missed by 1210.8.

The structural point is that **the vol rows score the LEVEL and the CHANGE of
vol, never the fact that a collapse in vol is itself the setup for a gap**. A
−17.9% one-day VXN collapse bought **+2** here. **n=1 for the harm. Nothing is
proposed** — this is written down so that the second and third instances can be
counted against it, and I am explicitly **not** opening an ID for a one-session
story that is indistinguishable from "the market was simply wrong too".

### 3.3 `breadth +2` was manufactured by the two names that were not driving the index

*"mega-cap avg **+1.70%** (2/4 up): NVDA **−3.17%**, MSFT +6.68%, AAPL +5.31%,
AVGO **−2.00%**"* — a **9.85pp** spread, positive only because of MSFT and AAPL.
Meanwhile §6's own unscored list reads *"Semiconductor stocks are sliding"*,
*"Nasdaq lags on chip weakness"*, *"Nvidia chips stockpile in Hong Kong awaits
China import approval"*. The chip complex was down and the brief scored the
breadth of the index **bullish**.

**Removing breadth's +3 gives −7 (`BEARISH`), closer to a realised |post|/ADR of
2.258 — so the row cost conviction on a CORRECT call.** This is the unnumbered
**averaging-over-dispersion** watch item (lines 1714 / 15617), previously n=2 of
condition with **zero** damage, and 11-05 was its third **condition** instance
while ungraded. It is now graded: **condition n=3, harm n=1.** The 08-28 note's
own rule said *"write it up at a third recurrence"* — this is the write-up.
**Counted the way D28 counts condition vs harm, 3 condition + 1 harm is not
three harm instances, so NOTHING IS PROPOSED and no weight is changed.**

### 3.4 News scored 0 on the largest down day in the record

139 headlines, 10/10 feeds, 49 relevant, **0 auto-scored** → `news +0`.
**H19 coverage 0.0%**, the lowest possible, for the second time in the series
(10-05, NFP day, was the other). The judgement list contained a Bank of England
hike to 4%, two separate chip-weakness items and an explicit *"Nasdaq lags"*.
H19's established finding — magnitude tracks **match count**, not importance —
is unchanged; at zero matches the row cannot be wrong, only absent. **Nothing
new, nothing proposed.**

### 3.5 H18 / P1 — opposite-signed for the second consecutive session, and mirrored

`rates +3` read a **live** US10y that **fell 1.17%**. `macro −3 / −1` read
DFII10/DGS10 **stale to 2026-11-03 and rising**, with the brief's own warning
*"this is last week's reading, not today's"* printed inside the −3. On 11-04 the
live row said UP and the stale row said DOWN; on 11-05 it is the exact reverse.
**Duplication 38 of 38, code-certain.** De-duplication counter-example check:
collapsing the stale rows moves the score **up** toward 0 and **away** from a
realised −1803.8, so — **third consecutive session** — the **RENDERING**
proposal stands and **no weight change is made**.

---

## 4. Change proposals

Two. Both land on existing entries except where noted; one is a **correction to
yesterday's proposal**, which today falsifies as sufficient.

### 4.1 CORRECTION — the 11-05 review's `remaining_budget == 0.0` trigger would NOT have caught today, and the right trigger is the gamma regime

**Yesterday's proposal** (grading 11-04) was to add `remaining_budget == 0.0` as
a disjunct to P-F's trigger, so the `EXHAUSTED` block stops printing a
fade-first strategy. Its evidence was good: `budget == 0` is 4 of 4 positive at
mean +253.0 against +17.7 for `budget > 0`.

**Today's budget was 187.2, not zero, the state was `LOW_FUEL`, not
`EXHAUSTED`, and the error was +1261.2 — 5.0× the mean of the four cases the
proposal was built on.** The budget-magnitude trigger does not fire on the
largest instance of the harm it exists to prevent. **It is necessary and it is
not sufficient.**

**What to change.** Gate the fade instruction on the **gamma regime**, not on
the budget: when price is **below the gamma flip** and **weekly net GEX is
negative**, §3's closing sentence must not read *"favour fades over chasing
breaks"*, and §3's *"the range is close to done"* must be subordinated to §2's
expansion read or the brief must name which block is live. This is the standing
**fuel-block-vs-gamma-block coherence fix**, re-affirmed unchanged in wording
and now carrying the evidence it lacked.

**Evidence — 7 sessions, one census, 6–1 to gamma on the column:**

| day | fuel state | budget | side of flip | extension vs budget | who was right |
|---|---|---|---|---|---|
| 09-14 | LOW_FUEL | 61.9 | BELOW | 194.1 (3.1×) | **gamma** |
| 09-15 | LOW_FUEL | 97.3 | BELOW | 16.0 (0.16×) | fuel |
| 09-28 | LOW_FUEL | 65.5 | BELOW | 179.4 (2.7×) | **gamma** |
| 10-08 | LOW_FUEL | 115.6 | BELOW | 326.2 (2.82×) | **gamma** |
| 10-14 | LOW_FUEL | 97.6 | BELOW | 476.4 (4.88×) | **gamma** |
| 10-15 | EXHAUSTED | 11.5 | BELOW | 127.6 (11.1×) | **gamma** |
| **11-05** | **LOW_FUEL** | **187.2** | **BELOW** | **1448.4 (7.74×)** | **gamma** |

**And today the contradiction is INSIDE §3, which is new.** All six prior
instances were §2 against §3. Today §3 printed, four lines apart:

> *"**DOWNSIDE path: clear.** … nothing structural to slow a breakdown. If it
> goes, it has room. **Do not fade it.**"*
> *"**UPSIDE path: clear.** … **Do not fade it.**"*
> *"The range is close to done. … **favour fades over chasing breaks.**"*

The 10-15 instance was logged as a measurement defect because the column and the
trade instruction disagreed. **Today they agree**: the column says gamma by
7.74× and the tape says a fade at any of the seven touched levels lost between
809.7 and 1080.6 points. **There is no reading of 11-05 on which the fade
instruction was correct.**

**Expected effect.** Prose and gating only — **no score change, no board change,
no multiplier on the budget**. It removes one of two mutually exclusive trade
instructions from a single section of the document. On the seven sessions above
it changes the instruction on six and leaves 09-15 (where the fade was right by
16.0 points of extension) reading worse by a margin too small to matter.

**Grepped first** to **P-F** (owns *">150pts outside the prior day's range"*;
scope is budget-derived), **P4** (explicitly budgets above zero), **H1**
(multiplier branch SETTLED-NEGATIVE), **H2** (owns *whether* the fade wins, not
*whether the document may say two things*), **H5** and **H20**
(CLOSED-NEGATIVE), **H22**. **No new ID** — this is the standing unnumbered
coherence item, and the correction lands on the 11-05 review's own proposal.

### 4.2 D31 (NEW, ALLOCATED) — §3 compares a close-to-close sigma to a high-low range and calls the result "a quieter day"

**Mechanism, certain from the code** (`brief.py:996`, read not edited):

```python
implied = round(px * (vxn / 100) / (252 ** 0.5), 1) if vxn else None
```

That is a **1-sigma close-to-close** daily move. It is then compared directly to
`f['adr14']`, a **14-day average high-low range**, and the comparison gates a
trade instruction:

```python
f"({'below' if implied and implied < f['adr14'] else 'above'} ADR — "
f"{'options market prices a quieter day, use the smaller budget' if ... }"
```

**The brief already knows this is an error.** Eight lines below, about the
straddle band, it prints: *"this is a **CLOSE-to-close** band, not a high-low
range. ADR measures high-low and is always the larger number; comparing the two
directly is the same error as reading the range budget as price travel."*
H8's entry has carried the identical warning since 2026-08-25 (line 1032).
**§3 states the rule and then breaks it, in the same section, for the other
number.**

**Evidence that the gated instruction harms.** Today is the **10th**
counter-instance to *"use the smaller budget"* (445.5 against a realised 1949.5
— under by **1504.0**), after 802.8 on 11-04 and the series at lines 13377 /
14540 / 15075 / 15565 / 16160 / 17523. **Three consecutive sessions, same
direction, increasing magnitude.**

**What I checked before proposing, and what it cost the claim.** I expected the
`implied < adr14` branch to be near-unconditional. **It is not: of the 81 briefs on disk
carrying the line, 58 took the "below" branch and 21 took "above"** (2 printed
neither, VXN absent). The comparison does vary, so
the defect is **not** "the sentence always prints" — it is "the sentence is
derived from a unit mismatch, and 10 of the sessions where it printed went the
other way". Reported because it weakens my own case.

**What to change — prose only.** Either (a) print the same close-to-close
caveat the straddle band gets and **drop the `use the smaller budget`
instruction**, or (b) scale `implied` to a high-low comparable before comparing
it to ADR14. **(a) is the conservative one and the one proposed**; (b) requires
a conversion factor nobody here has measured and would be tuning.

**Expected effect.** No score change, no board change, no budget change. One
fewer range instruction in §3, and it is the instruction that has been wrong on
10 sessions. Combined with 4.1, §3 would carry **one** range instruction instead
of three mutually inconsistent ones.

**ID check, per the register's own rule.** `grep -n "^## D31"`, `"^## H28"`,
`"^## P-J"` all return **0**. No `^## ` heading matches `VXN|vol-implied|implied
range`. The *"use the VXN-implied range as the budget"* idea is separately
recorded as already-killed and is **not** what this proposes. **D31 allocated.**

### 4.3 BLOCKED — do not ship H14's run-through band as a target

H14's live proposal text is *"run-through **0.22–0.48× ADR (n=5)**, reclaimed
within the session **2 of 5**"*, extended to 0.499 by instance 7. **Today's
run-through was 1.351× ADR — 2.7× the top of the quoted band**, on the one
session in the record with |week net GEX| above 4bn. The band was measured
entirely on sessions under 1.6× ADR and does not survive contact with an
expansion day. **Blocking a proposal, not making one; no ID, no change to H14's
status.** If it ships, it ships as *"0.22–1.35× ADR (n=7)"*, which is not a
usable target and should be published as a range rather than a number.

### Still observing — the watch list, with nothing proposed

- **The vol-collapse-as-setup claim (§3.2) — n=1.** Watching: does a one-day
  VXN fall >15% precede a range above 1.5× ADR? Needs 3 instances; there is 1.
- **P3/H6 — 2 clean / 1 confounded.** Watching: the next reachable structural
  wall. The premise has changed from *"never reachable"* to *"reachable and
  inert"*; one more clean instance settles it.
- **H22's threshold effect — n=1** at |week GEX| > 4bn.
- **Averaging-over-dispersion — condition n=3, harm n=1.** Watching for a
  second and third harm case before any rendering change is proposed.
- **H26's magnitude ordering — one hard break at the low end.** Watching
  whether weak-|score| calls keep producing the largest realised moves.
- **M6's `_first_touch` 12-bar window — 4 more inverted-by-horizon rows.** The
  only limb of M6 still open.

### No new data point is warranted

Everything that decided 11-05 was on the page. §2 called the regime exactly
right (*"sweeps tend to keep running rather than fail. Fading is the wrong trade
today"* — the most accurate sentence in the document), §3's path reads called
both paths *"clear"* and were right, and the week's net GEX of −5.219bn was
printed in bold. The engine's forward-looking rows summed to **−12**. **The
failure was not missing information; it was the document arguing with itself and
the rear-view rows outvoting the chain.** **No external source is proposed.**
The one genuinely absent input remains an **event-age** field for
`news_scorer.py` — free, local, owned code, **n=2 on each limb, NOT proposed**
(11-05 adds to neither; it scored nothing at all).

---

## Journal hygiene

One scan file for 11-05 (`1247-london.json` + `.md`), `is_trading_day: true`,
**276 bars**, `review_day` reports **0 test artefacts**. **09-24 quarantined by
hand — 29th consecutive review to carry it**; there is still no schema
`quarantine` field and the 09-29 proposal for one is reaffirmed. **2026-10-13
has no journal directory — documented, not recreated.** **2026-08-23, 09-09,
09-24 and 09-25 still have no `REVIEW.md`; none was created and nothing was
back-dated.** **09-22 aged out of the bar window on this run** — recorded under
D16/D26, not silently absorbed. **D26's gap is 16** (31 full bar sets against 47
finished trading-day directories). **No `prediction` block was modified. No
scoring, wall or grading code was edited.**
