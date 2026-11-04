# 2026-11-03 (Tuesday) — review

_Written after the 2026-11-04 brief was delivered. Nothing here blocked, delayed
or altered it. One scan graded: `1247-london.json` / `.md`, `LONDON`
12:47:56Z, `is_trading_day: true`, **276 bars**, `review_day` reports **0 test
artefacts**. **No `prediction` block was touched. No scoring, wall or grading
code was edited.**_

**`track.py` DID NOT COMPLETE — 7th consecutive failure.** `timeout 240 python3
-u track.py` → exit **124**, **0 bytes stdout, 0 bytes stderr**, identical to the
previous six. There is no `actionable: YES/NO` line to read, so **the 3-session
rule was applied by hand, per entry**. Census figures below are derived **FROM
SOURCE** (45 journal days scanned, 30 gradeable, one 45-day `M_5` fetch of
**8995 bars, 2026-09-20 → 2026-11-04**) and reported **alongside** the register's
carried value, never replacing it. The derivation reproduces the register's
published H1/P4 figures exactly at n=29 (**mean +68.7, median +25.9**) and
reproduces 11-02 **+161.2**, 10-30 **+351.6**, 10-29 **+112.4**, 10-28 **−76.1**,
10-16 **+479.3**, 09-21 **+569.2** — the only warrant offered for it.

**D29's G1–G4 applied as written, not re-decided.** 11-03 is the **second**
graded `LONDON`/EST scan. Per **G1** the `PRE_NY`-keyed censuses do **not**
accrue (P-B(b) stays **23**; the session-context-field census stays **22**) and
the parallel **`LONDON/EST (from 2026-11-02)`** census goes to **n=2**. Per
**G2** the fuel series **accepts** 11-03 — and the window-length concern is
**measured, not assumed**: the pre-scan window held **178 bars = 890 minutes of
market time = 14h50m**, i.e. the EDT norm (14h45m) to within 5 minutes, because
the 21:00–22:00Z hour it gained offsets the 22:00–23:00Z broker break it lost.
**No window-length bias exists on this day in either direction.** Per **G3**
everything else grades normally. Per **G4** the post-close census stays **n=2**
and takes no instance.

---

## 1. Scoreboard

| | |
|---|---|
| call | **STRONGLY BEARISH −12** at 28083.0 (`LONDON`, NY cash +102 min) |
| session O/H/L/C (`review_day`, 21:00Z bucket) | **28002.7 / 28310.3 / 27906.8 / 28167.6** |
| same, on the D30-clean 22:00Z basis (264 bars) | **28049.2 / 28310.3 / 27906.8 / 28167.6** |
| range · net | **403.5** (**0.610× ADR14 661.7**) · **+164.9** (clean basis **+118.4**) |
| direction, post-scan (P-H basis) | **+78.9 → WRONG** |
| direction, day-net | **+164.9 → WRONG** · clean-basis net **+118.4 → WRONG** |
| | all three bases **agree**; **no P-H deciding instance** |
| levels | **18 published / 3 touched = 0.17** — **2nd-lowest of 30 in-window days** (10-06 0.16; 30-day mean **0.51**) |
| levels inside the realised post-scan range | **3 of 3 touched = 1.00** |
| fuel | budget **418.6**, extension **160.4** → error **−258.2** (**0.38×**); traversal **246.4 = 0.59×** budget; `review_day` verdict *"OVER-estimated"* |
| VXN-implied budget | **546.5**, the figure §3 told the reader to prefer — realised range **403.5**, over by **143.0** |
| ATM straddle band | ±357 → 27726..28440; close **28167.6 INSIDE** |
| \|post\|/ADR · post/range | **0.119** · **19.6%** |

---

## 2. What the levels actually did

**Three rows touched, and two of them are one bar.** `28149.9 Asia High (today) +
Equal highs ×2 ⭐` and `28142.2 London High (today)` are **7.7 points apart =
0.96× `TOUCH_TOL`**, and `review_day` records both first touches at **bar_index
185, 13:25Z** with identical settled verdicts. The board's 3 touches are **2
distinct M5 bars → inflation 1.50×**, the highest in the series (prior 1.43× /
1.40×). Both held as support, 45 min, worst **−24.9** and **−17.2** — correct as
support, but they are one level published twice.

**The day was decided at `28085.6 PD close + PWL ⭐`, at +3, and the brief told
the reader to do the wrong thing with it.** Published note: *"Last week's low —
but we're trading BELOW the whole of last week, so it has flipped to
**RESISTANCE. Sweep it and short, don't buy it**."* Graded: **held as support for
465 minutes, worst excursion −15.9, 4 re-tests, close 82.0 above it.** First
touch 12:50Z, three minutes after the scan, *"broke UP through it"*. This is the
single highest-confluence near row on the board and the instruction attached to
it lost from the first bar to the last.

**Everything on the lower half of the board was published against a low that had
already been made.** The session low **27906.8 printed at 07:20Z — 5h27m before
the scan** and was never revisited. The post-scan low was **28063.9, 19.1 points
below the scan price**, while the nearest published downside row sat at
**−98.6** — **5.2× further from price than price ever went**. `PUT WALL 27984.4`,
`Equal lows ×2 27976.1`, `PDL 27965.6`, `Asia Low 27928.5` and `STRUCTURAL PUT
WALL 27784.4`: five rows, none reached, the nearest missed by **79.5**.

**The structural put wall was NOT reached — so P3/H6 takes no instance.** 264k
contracts / 1.39bn at **−298.6**, the largest concentration in the series,
missed by **157.1** from the post-scan low (**79.5** even from the pre-scan day
low). The strict clean count **stays at 1 clean / 1 confounded** and the standing
*"stop publishing it"* narrowing **stays blocked**. Nothing is confounded because
nothing happened.

**0.17 is a board-construction number, not a level-quality number.** Eight rows
printed *(stretch)* beyond the budget, and four more sat at +277 to +466 on a day
whose entire post-scan traversal was **246.4**. Of the three rows that lay inside
the realised post-scan range, **all three were touched**. The board was not
wrong about levels; it was wrong about reach — 15 of 18 rows could not have been
tested.

**Secondary table (P-E(b), instance #21) — undiscriminating again.** Identical
*"dealers are SHORT gamma… accelerate THROUGH rather than stall. Not a floor"*
text on three put-dominant strikes above price; of the two reached, **28234.4**
was sliced (price ran **+75.9** past it) and **28284.4** **stalled it inside
7.5 points and reversed 169.8** — the text that says "not a floor" describing both
outcomes. The one *"damp — rallies lose momentum into it"* row, **28434.4**, was
missed by **24.1**. Headline `CALL WALL 28634.4` never reached, missed by 324.1,
so **P-E takes no instance.**

---

## 3. What was wrong, and why

### 3.1 The election — the gate did not fire, it was right not to, and the event is not why the call was wrong

`event_gate: None`. **Correct per source**: `bias_engine.py:255` gates on
`0 <= hours_away <= 1.5`; the Congressional Elections row was **2.5h** out and
JOLTS **2.2h**. `events_24h` carried **both** rows and §5 **printed both** — so
unlike 10-28 this is the control D28 lacked: **the render worked and the gate was
still silent.** That separates the two defects cleanly. D28's render limb is a
**clean control** on this day; its harm count stays **2 of 6**.

**Measured the way the post-close census was measured** (marginal contribution —
day range minus range with the window excluded, the method that reproduces
10-28's 53.0% exactly):

| window (UTC) | range | net | marginal share of day range (403.5) | share of post-scan net (78.9) |
|---|---|---|---|---|
| 15:00–15:15 (JOLTS) | 97.7 | +42.4 | **0.0%** | — |
| **15:15–16:15 (election hour)** | 154.7 | **+65.3** | **11.5 = 2.9%** | **82.8%** |
| 15:16 → cash close | — | — | 18.4 = **4.6%** | — |
| 14:30–21:00 (NY cash) | 225.5 | +36.5 | — | — |

**2.9% against 10-28's 53.0% and 10-29's 43.4%.** On the range measure the
decisively-resolved midterms were a **non-event**: the hour that contained them
set the day high (28310.3 at 16:00Z) but price had already been within 11.5
points of that high outside the window.

**And the cumulative tape kills the "the gate should have saved us" reading
outright.** From the scan at 28088.7: **+65.3 by 15:00Z — before either print —
+198.1 by 16:00Z, +78.9 at the close.** **83% of the final post-scan error was
already on the board before the first release**, the election hour added another
+65.3, and the 19:00Z hour gave back **−128.3** of it. Standing aside from 14:46
to 15:46Z would have changed nothing about the direction verdict. **The −12 was
already losing to the London/early-NY tape; the event did not make it wrong, it
briefly made it look worse.** The register should not reach for the gate first
here, exactly as the H20 closure note instructed.

**H20 (CLOSED-NEGATIVE) — post-closure data point, and the closure is
strengthened.** Lifetime scheduled-High-event sessions: 09-10 **+114.6**, 09-16
**+136.4**, 10-07 **−97.8**, 10-28 **−76.1**, **11-03 −258.2**. The last three
are negative; the three in the current bar window average **−144.0** against
**+57.8** for all 30. The founding sign is reversed. **H20 is not re-opened and
no multiplier is proposed** — a factor fitted to three negative tails is the
identical error the 09-17 entry pre-warned about. The inference routes to **P4**,
which is already PROPOSED.

### 3.2 `vol −6` tied the record, every row of it was wrong, and deleting it does NOT fix the sign

Four rows, four functions of one latent variable (the 10-19 finding): VXN 30.89
(+8.4%, series high) **−2**, VIX9D/VIX **1.052 BACKWARDATED −2**, VXN/VIX 1.45
**−1**, VVIX 110.47 **−1**. Every one of the four was wrong on direction, and the
block's shared claim — *"expect range expansion"* — produced a realised
**0.610× ADR contraction**, the smallest range/ADR of any ≥10-score day.

**Deleting the whole block gives −6: label BEARISH, direction −1, STILL WRONG.**
That is a direct **counter-instance to 10-19**, where deletion produced the day's
correct sign. The deletion census is now **1 for / 1 against, n=2 — below
threshold, nothing proposed.** Nor does any other available surgery reach the
day: vol **and** the prior-week −3 gives **−3**, still bearish; the full H18/P1
de-duplication moves it to **−16**, i.e. **further from the outcome** (see 3.4).
**No subset of the published components flips this call.** The score was not
wrong because one block was overweight; it was wrong at every weighting.

### 3.3 `structure −3` — the prior-week rule fired at 1.6 points from its own boundary, price reclaimed in 3 minutes, and the rule has no term for either

`structure −3`: *"price is BELOW the entire prior-week range (28084.6–30023.6) —
PWL 28084.6 is now resistance, not support."* Price at the scan was **28083.0 —
1.6 points below the boundary**, which is **0.0024× ADR14**. The rule scores that
identically to 2000 points below.

- **5th proximity-gap instance** (10-07, 10-22, 10-23, 10-30, **11-03**) and by
  an order of magnitude the most extreme: the prior closest was 10-30 at **186.2
  = 0.31× ADR**.
- **First instance where the reclaim term would actually have fired.** Price
  reclaimed the PWL at **12:50Z, three minutes after the scan**, held above it
  for **465 minutes** and closed **83.0 above**. Every prior −3 firing had
  **no reclaim to detect**; this one did, and the penalty neither decayed nor
  inverted.
- Branch **3-for-9 → 3-for-10** on the post-scan basis.
- **The prose was wrong too**, which is new: on 10-23 the −3 was wrong while the
  *"resistance"* prose was right. Here both failed together.

**Still not proposed.** The register has declined the distance term five times
for a stated reason — no accuracy test exists for a normalised version, and the
re-cut that suggests one was found after looking at outcomes. That reason is
unchanged. **Recorded at n=5 with the first live reclaim case.**

### 3.4 H18 / P1 — instance 31, duplication 36 of 36, and the first ALL-SAME-SIGNED-AND-ALL-RIGHT

| row | instrument | as of | pts |
|---|---|---|---|
| `rates +1` | US10y 4.894%, −0.71% today | **live** | **+1** |
| `macro +3` | DFII10 real 10y, −3bp | **2026-10-30** | +3 |
| `macro +1` | DGS10 nominal 10y, −4bp | **2026-10-29 → 10-30** | +1 |

**One instrument, three times, +5 of a −12 score, two readings from last week.**
Against 11-02 (same-signed, all three wrong) this is same-signed and **all three
right** — so across the two sessions the fresh/stale split has **no discriminating
power in either direction**, and *"trust the fresh one"* stays unsupported from
both sides.

**The de-duplication would have made this day worse.** Dropping the two stale
duplicates moves **−12 → −16**, further from a **+164.9** outcome. Recorded
because it is the honest cost of the standing proposal: **the rendering fix is
about honesty, not accuracy, and 11-03 is the counter-example that proves it.**
**Rendering proposal unchanged. NO weight change proposed.**

**P1's staleness warning did render in full** (*"⚠️ FRED has not published since
2026-10-30 (2 business days ago) — this is last week's reading, not today's"*)
and, as on 10-30 and 11-02, **nothing read it**.

### 3.5 `gamma +2` bottom-of-band — 8th firing, RIGHT, and the FIRST firing under the 10-30 pre-registration

| day | price | put wall | band | % up band | *"bottom 20%"* window | ×ADR | outcome |
|---|---|---|---|---|---|---|---|
| 08-24 | 29132.8 | 29110.2 | 200pt | 11% | 40pt | 0.04x | WRONG |
| 09-14 | 28830.7 | 28787.8 | 500pt | 9% | 100pt | — | RIGHT |
| 10-07 | 31031.7 | 31025.8 | 200pt | 3% | 40pt | — | RIGHT |
| 10-12 | 30843.5 | 30843.1 | 500pt | 0.08% | 100pt | — | WRONG |
| 10-22 | 29361.0 | 29115.7 | 1300pt | 18.9% | 260pt | 0.50x | WRONG |
| 10-23 | 28875.7 | 28789.0 | 600pt | 14.5% | 120pt | 0.22x | RIGHT |
| 10-30 | 28634.2 | 28468.7 | 2100pt | 7.9% | 420pt | 0.71x | WRONG |
| **11-03** | **28083.0** | **27984.4** | **650pt** | **15.2%** | **130pt** | **0.20x** | **RIGHT** |

**Census 3 right / 4 wrong → 4 right / 4 wrong.** Band width **650.0 = 0.98×
ADR14**, a normal width; the trigger-window series is now **0.04× · 0.20× ·
0.22× · 0.50× · 0.71×**.

**The 10-30 pre-registration gets its first test and it PASSES.** That entry
wrote, before this firing and before this outcome, *"write the normalised
threshold (e.g. within 0.15× ADR of the put wall) down BEFORE the next firing."*
On 11-03 price was **98.6 above the put wall = 0.149× ADR14 (0.15× = 99.26)** —
**the normalised rule fires too, by 0.66 points**, and it was **RIGHT**. **1 of
the 3 pre-registered firings collected. Nothing proposed until 3.**

**Prose contradiction 8 of 8** (*"poor risk/reward for shorts"* against §1's
*"Strategy-1 fades have a materially lower hit rate here"*, §2's *"Fading is the
wrong trade today"*, and the put-wall row's *"if it breaks, expect it to speed
UP, not bounce. Don't buy the break"*). **Zero sign changes in eight firings** —
−12 would have been −14, same label, same side, same verdict. It was the only
right row in its own block for the second time.

### 3.6 H27 — observation 8, and it falls against the founding claim a second consecutive session

| | 10-26 | 10-27 | 10-28 | 10-29 | 10-30 | 11-02 | **11-03** |
|---|---|---|---|---|---|---|---|
| vol ↔ breadth | −3 | +1 | +4 | +1 | −2 | −7 | **−9** |
| structure ↔ gamma | −3 | 0 | +4 | −7 | −6 | −3 | **−6** |
| independent remainder | 0 | −4 | −2 | +1 | −5 | +7 | **+3** |
| score | −6 | −3 | +6 | −5 | −13 | −3 | **−12** |

The duplicated pairs carried **−15 of a −12 score — 125% of it — and both pairs
were WRONG. The "independent" remainder was +3, opposite-signed, and RIGHT.**
Second consecutive counter-instance to the founding configuration. **Weight limb
stays ANSWERED-NEGATIVE; nothing re-proposed.**

### 3.7 The `news` block scored an event that was already in the price — n=1 → n=2, and this time the competing explanation FAILS

One auto-scored headline: `[earnings_miss]` *"Apple shares slide after weak
margin outlook; Palantir slumps 8% after earnings"*, raw **−1.70**, printed
reaction *"Mega-cap miss/warning → index-weighted drag, ~170pts / 180min"*.

AAPL reported **after the 11-02 cash close**. By the 12:47Z scan the event was
**~15.8 hours old**, the tape's own first answer to it was **+83.1 UP** in the
21:00–22:00Z hour, and the pre-scan session had already made its low (27906.8 at
07:20Z) and recovered **176.2** from it.

**The 10-30 instance was defeated by a competing reading — "the market was still
repricing at scan time, and it was, for another 635 points." That reading is
available here and it fails.** Graded on the brief's own 180-minute horizon,
12:50 → 15:45Z: predicted **~−170**, realised **+141.7 — a 311.7-point
sign-and-magnitude miss.** `news_scorer.py` still ages the **headline**, not the
**event**. **n=2 for the scored-and-already-in-the-price shape. NOT PROPOSED; no
number taken.** The double-count limb is **weaker** than 10-30's: only `breadth
−2` re-counts AAPL (1 of 4 names), and `structure −3` is last week's selloff, not
this print — so this is a double, not a triple.

**D9 — no instance.** The `earnings_miss` match has its subject correct. **D18 —
no instance.** **H19 — clause (i) FAILS as anticipated: 1 auto-scored headline,
n stays 2**, and coverage was **1 of 50 relevant / 139 fetched = 2.0%** while
*"The Nasdaq 100 Is Now Officially in a Correction"* and four other correction
headlines sat uncounted.

### 3.8 D30 — the defect is real at source, and its measured effect on this day's fuel figures is ZERO

This is the day D30 was opened to describe, so it is graded explicitly.

**Confirmed from source and from the tape.** `review_day`'s 11-03 bar set begins
**2026-11-02 21:00:00Z** — the first 12 bars are 11-02's post-cash-close hour
(O 28002.7 / H 28112.6 / L 28002.0 / C 28085.6, range 110.6, **+83.1**), exactly
as D30 states. `levels_fuel.py:90–94` buckets on 21:00Z; `today_bars` at
`levels_fuel.py:178` uses that function, so the hour **is** inside 11-03's
pre-scan window.

**The 83.1-point close discrepancy is confirmed, and I traced which figure each
consumer used.** The brief's board printed `PD close + PWL` at **28085.6**;
`review_day` graded 11-02's close at **28002.5**; **28085.6 is exactly the
21:55Z bar close in my own fetch**, so the figure is the `D_1` bar's close on the
22:00Z roll. **Difference +83.1, reproduced to the decimal.**
- **Brief / board / `prediction.levels`** → the **22:00Z `D_1`** basis.
  `levels_fuel.py:173` picks `prev` from `d1`, so **PDH 28754.5, PDL 27965.6 and
  PD mid 28360.0 are on that basis too** — they are not, as the register's
  phrasing implies, a second series that agreed by luck. They agreed because the
  migrated hour's extremes (28002.0–28112.6) are **nested inside** 11-02's
  27965.6–28754.5. **A close is an endpoint, not an extremum, which is why it
  and only it disagreed.**
- **`review_day` grading, `actual_session`, the P-H bases** → the **21:00Z `M_5`**
  basis.
- **ADR14** → `d1[-15:-1]`, i.e. **22:00Z**, divided into a 21:00Z numerator, as
  D30 states. On 11-03 exactly **1 of the 14** ADR bars (11-02) is an EST bar,
  and that bar's `D_1` range equals its `M_5`-bucketed range (**788.9**) because
  the extra hour was again nested. **ADR14 contamination on this day: 0.0.**

**D30's consequence #1 is FALSIFIED as a magnitude claim on its own first two
live instances, and this is a correction to the entry.** D30 predicts the hour
*"inflates 11-03's `today_range` and `adr_used_pct` and deflates its
`remaining_budget`."* Measured:

| | with the migrated hour | without it |
|---|---|---|
| pre-scan range at 12:47Z | **243.1** (hi 28149.9 / lo 27906.8) | **243.1** (identical) |
| `adr_used_pct` | 36.7% | 36.7% |
| `remaining_budget` | 418.6 | 418.6 |
| session range | 403.5 | 403.5 |
| extension, fuel error | 160.4, **−258.2** | 160.4, **−258.2** |

**Identical to 0.1 of a point on every fuel figure**, because the migrated hour's
extremes lie strictly inside the clean pre-scan range. **The same is true of the
second instance**: 11-04's migrated hour (21:00–21:55Z Nov 3, O 28176.8 / H
28316.4 / L 28139.8 / C 28282.4, range 176.6, +105.6 after AMD) is also nested
inside 27493.0–28533.0, so 11-04's **1040.0** range is identical with or without
it. **2 of 2 nested.**

**So: the contamination BIASES and does not INVALIDATE — and on 11-03 it does not
even bias.** The fuel grade (**−258.2**, over-estimate, 0.38×) **stands
unqualified**. The figures D30 actually moved on this day are the grader's
`actual_session.open` (**28002.7** vs a clean **28049.2**) and `net_move`
(**+164.9** vs **+118.4**), a **46.5-point** shift — and it changed no verdict
either, both being positive against an expected −1. **The mechanism is real, the
proposal to reconcile the two day-definitions is unaffected, and the magnitude
claim should be restated as conditional on the migrated hour breaking the day's
range — which it has not yet done.**

**The grading-window limb of P-H stays permanently MOOT under D30 and was not
revisited.**

### 3.9 The merge discarded the one note that described the day

`28085.6 PD close + PWL ⭐` is a merged row. `brief.py:382–385` resolves the note
by `rank = {"gamma": 5, "structural": 4, "liquidity": 3, "gamma-shelf": 2,
"magnet": 1, "context": 0}`, and `PD close` is pushed as **`magnet`** — the
lowest-ranked real kind — so **a PD close merged with anything always loses its
note.** The price kept is the first-seen one (the PD close's 28085.6, on the
22:00Z basis), the note kept is the PWL's.

- **note DISCARDED** (`brief.py:187`): *"Where yesterday settled. **Price often
  comes back** to fill a gap from here."* → **price came back to it 4 times over
  465 minutes.** Correct.
- **note PUBLISHED**: *"it has flipped to RESISTANCE. **Sweep it and short, don't
  buy it**."* → **lost from the first bar.**

**Merge-note limb: condition n=3** (09-28 `PD mid + London Low`, 11-02
`28556.4 PD mid + London Low`, **11-03**) — all three the same mechanism, a
`magnet` losing to a `liquidity` row, which is deterministic from `rank` rather
than evidential. **Harm n=2** (09-28, 11-03): on 11-02 the kept note was right.
The limb belongs to **P-G**, grepped first, whose own fix note already says
*"P-G's fix covers this only if it runs after the merge."* **Harm is below three
sessions, so NOTHING IS PROPOSED** — the condition/harm split is counted the way
D28 counts it. Also the published price is **1.0 point above** the PWL the
`structure` row scored (28085.6 vs 28084.6); immaterial here, logged because this
was the decisive level.

### 3.10 Everything else, graded

- **H26 — a ≥10 instance, and the SMALLEST \|post\|/ADR the bucket has ever
  carried.** `|post|/ADR` **0.119**, range/ADR **0.610**, direction **WRONG**.
  ≥10 bucket: **carried 4/8 = 50.0% → 4/9 = 44.4%**; **from source 3/6 = 50.0% →
  3/7 = 42.9%**. Both reported; neither averaged. From source at **n=30**:

  | bucket | n | mean \|post\|/ADR | mean range/ADR | direction (post-scan) |
  |---|---|---|---|---|
  | 0–2 | 6 | 0.207 | 1.042 | — (all no-call) |
  | 3–5 | 8 | 0.452 | 1.144 | 5/8 = 62.5% |
  | 6–9 | 9 | 0.524 | 1.074 | 5/9 = 55.6% |
  | **≥10** | **7** | **0.574** | **1.287** | **3/7 = 42.9%** |

  **Magnitude monotonic a 13th session** (0.207 / 0.452 / 0.524 / 0.574) and
  **direction monotonically inverted and steepening** (62.5% / 55.6% / 42.9%).
  11-03's 0.119 is the lowest value in the ≥10 bucket — the exact mirror of
  10-30 being the largest in 3–5. *"Inverted at the top"* **stays SUSPENDED**
  (D26: the ≥10 cell's composition changes weekly). **No Spearman quoted**; its
  derivation is still unwritten.
- **H1 / P4 — error −258.2, n=30, and the ELEVENTH value under one series name.**
  From source **mean +57.8, median +16.1** (was +68.7 / +25.9 at n=29). The
  zero/non-zero split **holds**: budget = 0 **mean +235.4** (n=3) against
  budget > 0 **mean +38.1** (n=27). **−258.2 is the most negative error in the
  record** and it lands on the **largest budget ever published** (418.6).
  **ANSWERED-NEGATIVE; flagged, not averaged.** Tagged `LONDON/EST` per G2.
- **H22 — n=18 → 19, label WRONG.** Week net GEX **−3.083bn** → *"expansion
  likely"* → realised **0.610× ADR**, the **smallest range/ADR of any ≥10 day**.
  11-02's **−0.579bn** produced the **same label** at 1.257×: a figure **5.3×
  larger** says nothing different. **Still not discriminating.** The VXN-implied
  **546.5** over-forecast the range by **143.0 — 8th counter-instance** to §3's
  own *"use the smaller budget"* instruction.
- **H23 — +1 never-reached; census 15 sliced / 3 capped / 3 → 4 never-reached
  (n=22).** §3 named the upside brake **28684.4 (+601)** as *"far enough that
  little stands in the way"*; missed by **374.1**. Downside flagged clear with no
  brake named — **untested**, price went 19.1 below the scan.
  **Force-ranking branch: a SECOND disagreement, and it again favours force —
  but it is not an instance.** Distance-first named 28684.4; the nearest
  call-dominant (damping) strike was **28434.4 (+351)**, and the day high
  **28310.3 stopped 24.1 short of it** and **75.9 past** the nearer
  put-dominant 28234.4. Suggestive only: **neither level was touched**, so the
  day cannot adjudicate. **Branch stays CLOSED; n=2, nothing re-opened.**
  **Trap RE-FLAGGED for the 4th time so no one opens a defect**: §3 reads
  `largest_abs_gex` (`brief.py:515`), the secondary table reads `walls_ranked`
  (`brief.py:647`) — **different lists, and the "damp/amplify" label is keyed on
  `dominant` while the brake is keyed on `sign`. Not a skipped brake.** The
  reader-facing cost is real and unrecorded: **two statements about the nearest
  upside brake, 250 points apart, on one page, with no reconciliation.** n=1 for
  that framing, nothing proposed.
- **M6 — session 38, ZERO instances, and reported as expected-by-identity.** No
  touched row settled `lost`, so the `review_day.py:159–161` inversion could not
  fire. **The driver is FOUND** (the `lost` branch names the direction of the
  adverse excursion while the sentence reads as the direction of the break — an
  identity, 82 of 82 rows / 30 of 30 days, verified in source). Per the standing
  instruction, future instances are **expected-by-identity, not findings**; the
  only **open** defect in the family is `_first_touch`'s 12-bar window. **Two
  candidate fixes are with the user; nothing proposed.**
- **D5 — no defect instance; the two instruments diverged on 3 of 3 touched
  rows** (`28085.6` first-touch *"broke UP through it"* vs settled *"held as
  support 465min"*; the two 13:25Z rows *"traded both sides — chopped"* vs *"held
  as support"*). Every divergence is the known window difference and **none is an
  inversion.** The settled read is right in all three.
- **P5 — the *"best level is in the secondary table"* sub-claim takes a FOURTH
  consecutive counter-session** (10-29, 10-30, 11-02, **11-03**): the day's
  decisive level was `PD close + PWL` on the **main board**. **The sub-claim is
  dead; that is not a model change.** P5's actual proposal (persist and grade the
  secondary table) is unaffected and unproposed-further.
- **P-G — instances #39 and #40, two on one board.** `28548.7 London Low
  (prev-day)` at **+466 ABOVE** price and `28457.1 Asia Low (prev-day)` at
  **+374 ABOVE** both printed *"the next session usually runs the stops **below**
  it"* — promising an event that had already happened by **641.9** and **550.3**
  points (pre-scan low 27906.8). **Controls on the same board, all correctly
  sided:** `27928.5 Asia Low (today)` at −154; the three prev-day highs at
  +582/+612/+672; `28142.2 London High (today)` and `28149.9 Asia High (today)`
  at +59/+67, both of which **were** exceeded as promised.
- **P-B(b) — observed and EXCLUDED under G1; the `LONDON/EST` census goes to
  n=2.** **One** guaranteed double-count window: **28142.2 / 28149.9 = 7.7 =
  0.96× `TOUCH_TOL`** — and unlike 11-02's 1.04× near-miss this one **landed**,
  both rows grading off bar 185. `PRE_NY` denominator stays **23**.
- **Session-context field — observed and EXCLUDED under G1; `LONDON/EST` census
  to n=2.** **7 of 18** rows sat inside the pre-scan range 27906.8–28149.9 and no
  field says so, including all four lower rows down to the put wall. `PRE_NY`
  stays **22**.
- **D7 — a CLEAN CONTROL on BOTH limbs.** The footnote printed **one** row
  (*"30024 PWH"*) against its cap of 6, so price-ordered truncation could not
  fire; **both** structural walls, GAMMA FLIP, MAX PAIN, both headline walls,
  PDH and PDL all reached the board. Dropped-row census stays **2, both PDL**
  (10-23, 10-30).
- **D28 — the condition did NOT recur; a clean control, and the one the entry
  needed.** `events_24h` carried **two** rows and §5 printed both. Condition
  instances stay **10-28 and 10-30 (n=2)**; harm stays **2 of 6**. **D24 is a
  clean control** — the AMD row is forward/same-dated and correctly marked
  `time-after-hours`.
- **P-C / `events` / dead-weight audit — the gate's silence is now measured on a
  High event with a WORKING feed.** `events` scored **+0** on its single row
  (`bias_engine.py:259–263`) and **has still never scored in its history**; the
  macro calendar never reaches the score at all. High-event-outside-the-gate
  limb: **10-28 (5.1h), 11-03 (2.5h) = n=2**; Medium-cluster limb **09-29, 10-23
  = n=2**. **Both below three. P-C is already PROPOSED and gains nothing new.**
  **7 of 24 rows scored 0** — DXY, HY OAS, NFCI, the yield curve, `fuel`, the
  `news` bullet row and the `events` row. That is the **lowest zero-count in the
  recent record** (11-02 was 12 of 26): on this day almost every row had an
  opinion, and the aggregate of those opinions was wrong by 164.9 points.
- **D22 — a SECOND candidate instance, explicitly UNCONFIRMED.** `breadth −1`
  printed **NDX −1.39% vs ES −0.03%**. The NDX leg is 11-02's prior-session cash
  move and checks out (the register verified it to 0.06pp); the ES leg is again
  the implausible one on a day the whole US tape fell. **ES cannot be sourced
  here and the claim is not made. n=2 candidate. Nothing proposed.**
- **D27 — 10th CONSECUTIVE `gexbot` 401** on `/v2/NDX/classic/gex_full` (the
  11-03 render and again on 11-04). Volume-weighted ladder absent, **H12/H13
  untestable**, **D25 SUPPRESSED**. **Nothing proposed** — no credential change,
  no retry policy.
- **D25 — interrupted at 29.** §1–§6 only; no §7, so the unguarded `drift`
  sentence did not render for a **6th** consecutive session.
- **D23 — observation 15, NO residual, NONE inferred.** §7 did not render. Offset
  **−15.6**, basis `nq_implied`, greeks `repriced_bs_at_current_spot`; NDX cash
  **933 min** stale, rolled forward by the NQ move (**+108.8**) to 28098.6.
  **Recorded clean**, and **not a D6 breach** (the series stays at five through
  11-03).
- **D26 — the window moved again; the gap WIDENED from 14 to 15.** From source,
  **30** journal trading days hold a full bar set against **45** finished
  trading-day directories — **15 invisible**. **09-21 is still the oldest
  usable day**; 09-22 is one session from the boundary. H26's ≥10 cell and
  P-F's treatment set both remain hostage to this.
- **P-H — no 6th deciding instance.** Post-scan **+78.9** and day-net **+164.9**
  (and the clean-basis **+118.4**) all **WRONG**; the bases agree. Carried
  **15/28 vs 16/28**, deciding set **n=5**. From source **13/24 = 54.2% vs
  14/24 = 58.3%**, deciding set **n=3 (10-07, 10-15, 10-19)**, unchanged.
  **The grading-window limb stays MOOT under D30 and was not revisited.**
- **H8 — post-closure, and this is a HIT.** Band ±357 off the 2026-11-03
  straddle (420pts, ATM IV 35.3%) → 27726..28440; close **28167.6 INSIDE**, with
  272 points of room. H8 stays **CLOSED ANSWERED-POSITIVE (8 of 10)** and is
  **NOT re-opened**; post-closure record **1 hit / 1 miss**.
- **H17 — not a deadband case.** Post-scan move is **19.6% of session range**,
  far above the ~5% watch line. **Stays 2 of 3.**
- **H2 — a NON-instance and a clean control.** `ROOM_TO_EXPAND`, not
  LOW_FUEL/EXHAUSTED, so neither axis of the re-specified gamma-sign × fuel-state
  2×2 is engaged. **Census unchanged.**
- **H14 — no instance.** The put wall was never touched (missed by 79.5), so the
  break rider was never tested. **Count unchanged.**
- **`PIN_THEN_EXPAND` / P-I — no instance.** `expiry_shape` was
  `COHERENT_SHORT`. **P-I keeps its single harm case (11-02's *"from roughly
  13:00 ET"*, early by ~2h30m) and nothing here reopens it.**
- **`TOUCH_TOL = 8.0` — not an instance of the tolerance claim, but see P-B(b).**
  Nearest untouched row missed by **79.5 = 9.9×** the tolerance. Stays **n=2**.
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26 — not re-opened) ·
  **H4** (flip 794 away, never approached) · **H5** · **H7** (no overnight scan) ·
  **H9** (AMD is `sector-relevant`, not index-defining under the engine's own
  definition — **NVDA only** — and its tape falls outside the graded day, see
  D30) · **H11** · **H12/H13** (401) · **H15/HY OAS** (scored 0) · **H16** ·
  **H19** (clause (i) fails) · **H20** (CLOSED-NEGATIVE; post-closure point
  recorded at 3.1) · **H21** (CLOSED-NEGATIVE) · **D8** · **D9** · **D14** ·
  **D15** · **D18** · **D21** (the width defect did **not** reach an extreme;
  0.20× is the series median) · **the gamma-outvoted cell** (`gamma` netted −3
  and **agreed** with the losing call; stays **n=5**) · **the max-pain
  Thursday/Friday clause** (Tuesday, level 1.44× the budget away) ·
  **P-E / P-E(b)** on the capping limb (call wall missed by 324.1).

---

## 4. Change proposals — only material ones

**NOTHING IS PROPOSED TODAY, and nothing new is opened.** `track.py` could not
be read, the 3-session rule was applied by hand per entry, and **no item clears
it.** The items that came closest, and exactly why each fell short:

| item | evidence | why not proposed |
|---|---|---|
| **P-G merge-note** — print both notes, or run P-G's fix after the merge | condition **n=3** (09-28, 11-02, 11-03) · **harm n=2** (09-28, 11-03) | The condition is **deterministic from `rank`**, so it is an identity rather than evidence; **harm is 2 sessions.** Counted the way D28 counts condition vs harm. Needs one more harm case. |
| **H10 distance term** on `structure ±3` | proximity gap **n=5**, and 11-03 is the first firing with a real intraday reclaim | The register has declined five times for a **stated** reason — no accuracy test for a normalised version exists, and the re-cut suggesting one was found **after** seeing outcomes. That reason is unchanged. |
| **D21 normalised `gamma +2` threshold** (*"within 0.15× ADR of the put wall"*) | **1 of 3** pre-registered firings collected; it fired and was RIGHT | Pre-registration explicitly requires **three** firings under the written rule. Two to go. |
| **widening the event gate** past 1.5h | High-event-outside-gate **n=2** (10-28, 11-03) | And the 11-03 evidence points **against** it: the event supplied **2.9%** of the day's range and **83% of the error was in before the first print.** Widening would have cost the session and saved nothing. |
| **H20 event-day budget factor** (reversed sign) | 3 consecutive in-window event days negative (−97.8, −76.1, −258.2) | **H20 is CLOSED-NEGATIVE and is not re-opened.** A factor fitted to three negative tails is the error the 09-17 entry pre-registered against. Routes to **P4**, already PROPOSED. |
| **deleting the `vol` block** | deletion census **1 for (10-19) / 1 against (11-03)** | n=2 and split. And on 11-03 **no subset of components flips the call**, so the block is not the lever. |
| **H18/P1 de-duplication as an accuracy fix** | duplication **36 of 36** | 11-03 is a **counter-example**: the correction moves −12 → −16, further from the outcome. The **rendering** proposal stands unchanged; **no weight change.** |
| **the §3-vs-§4 brake contradiction** | n=1 as a reader-facing claim | Already flagged three times as *"different lists, not a skipped brake"*; **re-flagged, not opened.** |
| **`news_scorer` event-age field** | ageing **n=2** (10-30, 11-02); already-in-the-price **n=2** (10-30, 11-03) | Both limbs at two sessions. Free, local, owned code — **still the only genuinely absent input, and still not proposed.** |

### Is any published level never reacted to?

**Not answerable from 11-03 and the question was not forced.** Fifteen of 18 rows
were unreachable — the whole lower half was published against a low already made
5h27m before the scan. The three reachable rows were **3 of 3 touched** and all
three held. The **STRUCTURAL PUT WALL** remains the standing candidate and is
**still blocked at 1 clean / 1 confounded**; it was missed by 157.1 and takes no
instance. **No level is proposed for deletion.**

### Is a bias component always near zero?

**12 of 24 rows scored 0**, and `events` has **never** scored in its recorded
history — but that is **P-C's measured constant**, not dead weight discovered
today, and P-C already carries the proposal. `fuel` scored 0 for the 20th-odd
time. **Nothing proposed.**

### Is the fuel budget systematically over or under?

**Over, and by more than ever on the largest budget ever published.** n=30 from
source: **mean +57.8, median +16.1**, but the dispersion is the story — **−258.2
(11-03) to +569.2 (09-21)** — and the budget=0 / budget>0 split holds at
**+235.4 (n=3) vs +38.1 (n=27)**. **No multiplier. That is P4**, already
PROPOSED: *stop quoting a point-precise budget above zero.* 11-03 is the
strongest single argument for it in the record — a **418.6** budget quoted to one
decimal against a realised **160.4**.

### Is a new data point needed?

**No, and the 11-03 page proves it harder than usual.** Everything that decided
the day was on the page: price was **1.6 points** from the prior-week boundary,
the merged ⭐ row carried the correct note **and the renderer threw it away**, and
§6 printed five *"Nasdaq 100 is now officially in a correction"* headlines into
the uncounted pile while the one scored row re-priced a 16-hour-old earnings
print. **No external source is proposed.** The one genuinely absent input remains
an **event-age** field for `news_scorer.py` — free, local, owned code, **n=2, NOT
proposed.**

---

## Carried forward from the 2026-11-04 scan — recorded, NOT graded

- **Third consecutive `LONDON` scan**, 12:47Z, `scan_et 07:47 ET`. **G1–G4 apply
  when it is graded.** `STRONGLY BEARISH −12` at 28239.5.
- **⚠️ OFFSET −68.8 — a SIXTH D6 breach and the FIRST materially NEGATIVE one.**
  Arithmetic verified independently: NDX cash closed **28180.26** on 11-03, the
  NQ roll was **+128.0** → implied **28308.3** against a CFD of **28239.5**;
  **28239.5 − 28308.3 = −68.8**. No contract roll involved. The breach series,
  re-derived from every journal `.md` file (78 scans across 48 day directories) and reproducing the register's five
  exactly: **09-28 +45.9 · 10-12 +43.1 · 10-14 +41.8 · 10-15 +77.6 ·
  10-20 +74.5 · 11-04 −68.8.** (The quarantined 09-24 **−276.3** and the
  transient mid-fix scans of 08-24 / 08-26 / 09-09 are excluded, as before.)
- **The consequence the user flagged, TABULATED — and the driver is the BUDGET,
  not the offset.** 11-04's board is **4 rows, 4 of them options-derived
  (100%)**, with six session levels pushed into the *"context only"* footnote, so
  **every row carries the ±69 and no exact session level is left to anchor
  against.** But across all 45 gradeable days the 2×2 is unambiguous:

  | | budget = 0 | budget > 0 |
  |---|---|---|
  | **D6 breach** | n=**1** — 100.0% options (11-04) | n=**5** — mean **49.4%** (09-28 57.1 · 10-12 23.5 · 10-14 40.0 · 10-15 100.0 · 10-20 26.3) |
  | **clean offset** | n=**9** — **100.0% on every one** (08-24, 08-25, 09-10, 09-11, 09-14, 09-17, 10-01, 10-19, 10-22) | n=**30** — mean **31.6%** |

  **A zero budget forces a 100%-options board in 10 of 10 cases, breach or not.**
  The breach-day mean (57.8%) exceeds the clean mean (47.4%) only because 10-15
  had a budget of **11.5**; drop it and breach-day composition is **36.7% vs
  31.6%** — nothing. **The harm the user describes is the CONJUNCTION of a breach
  and a zero budget, and in 45 days it has occurred exactly ONCE.** 10-20 is the
  stated inverse for the stated reason: a **202.9** budget kept the session rows
  on the board. **n=1. NOTHING PROPOSED, and the offset-vs-options-proximity
  hypothesis stays NULL.**
- **Fuel is the most extreme ever recorded**: range **1040.0** against ADR14
  **633.1**, **164.3%** used, `fuel_ratio` **3.91**, `EXHAUSTED`, budget
  **0.0** — an **H2 cell instance** (EXHAUSTED, below flip, fade instruction
  printed). Vol likewise: **ATM IV 48.2%**, **VIX9D/VIX 1.203** (deepest
  backwardation yet), **VXN/VIX 1.67** (highest yet), VXN 30.53 (−1.2%, so
  `vol +0` on the level row for the first time in a week).
- **D30, second live instance, again NESTED.** 11-03's post-close hour
  (21:00–21:55Z, range 176.6, **+105.6** after AMD) sits inside 11-04's bucketed
  day and its extremes (28139.8–28316.4) lie **inside** 27493.0–28533.0, so
  11-04's 1040.0 range is unaffected. **Friday 2026-11-06 is still the day to
  watch** — `trading_day(21:00Z Fri) → Saturday`, and that hour vanishes.
- **D27 — the 401 recurred, a 10th consecutive day.**

---

## Journal hygiene

One scan file for 11-03 (`1247-london.json` + `.md`), `is_trading_day: true`,
**276 bars** (against 11-02's **264** — the asymmetry is D30, not data loss),
`review_day` reports **0 test artefacts**. **09-24 quarantined by hand — 27th
consecutive review to carry it**; there is still no schema `quarantine` field and
the 09-29 proposal for one is reaffirmed. **2026-10-13 has no journal directory —
documented, not recreated.** **2026-08-23, 09-09, 09-24 and 09-25 still have no
`REVIEW.md`; none was created and nothing was back-dated.** **2026-11-04 is on
disk, `is_trading_day: true`, 180 bars, and is NOT graded here.** No `prediction`
block was read for anything but grading and none was modified. No scoring, wall
or grading code was edited.
