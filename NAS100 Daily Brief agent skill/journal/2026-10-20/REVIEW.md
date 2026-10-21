# REVIEW — 2026-10-20 (Tuesday)

Graded 2026-10-21. One scan on disk (`1248-preny`), `is_trading_day: true`,
`review_day.py` reports **0 test artefacts** for the day. Grading basis is
**post-scan** per **P-H**; the day-net figure is reported alongside it every
time the two could disagree. **09-24 excluded by hand (16th review to carry
it).** **2026-10-13 has no journal directory** — the scheduled scan never ran;
nothing was created, back-dated or inferred.

---

## 1. Scoreboard

**Session (276 M5 bars):** O **29564.3** (22:00Z 10-19) · H **29721.6**
(14:30Z) · L **29211.8** (13:45Z) · C **29703.2** · range **509.8**
(**0.966x** ADR14 527.5) · day net **+138.9** · close **96.4%** up the range.

**Pre-scan window:** H 29622.3 (23:00Z) · L 29297.7 (12:30Z) · range 324.6.

| | |
|---|---|
| Call | `MILDLY BULLISH` **+4**, expected direction **+1**, price 29416.8 |
| Post-scan move (P-H basis) | **+295.0** → **CORRECT** |
| Day-net move | **+138.9** → **CORRECT** |
| **P-H deciding instance?** | **NO.** Both bases agree. The deciding set stays at **n=5** (09-11, 09-16, 10-07, 10-15, 10-19) |
| Post-scan running | **13 / 19 = 68.4%** (was 12/18 = 66.7%) |
| Day-net running | **14 / 19 = 73.7%** (was 13/18 = 72.2%) |
| **Convention cost** | **5.3** points of headline accuracy (was 5.5) |
| Levels published / touched | **19 / 13** → hit rate **0.68** |
| Distinct touch bars | **9** (178, 181, 188, 192, 193, 194, 195, 196, 197) → distinct-event rate **9/19 = 0.474**, **inflation 1.44x** |
| Fuel | budget **202.9**, extension **185.2** → err **−17.7**, budget **OVER-read** — `review_day` calls it *"about right"* (0.91) |
| Post-scan traversal | **509.8** = **2.51x** the budget, **0.97x** ADR |
| `track.py` | 30 trading days / 33 scans (deduped) · per-day mean err **+54.3 → +51.9** (n=30, incl. 09-24) · per-scan **+52.7** (n=33) · direction **17/7/9** → **16/7/9** ex-09-24 · levels touched 0.51 |

**The shape of the day, because every judgement below depends on it.** Scan
12:48Z at 29416.8 → **down 205.0** to 29211.8 at 13:45Z (15 minutes after the
cash open), through **three** published pools and **85.9 below the pre-scan
low** → **up 509.8** to 29721.6 by **14:30Z** → then **390 minutes** inside
29511.7–29721.6, closing 18.4 off the high. **The entire realised move was over
by 10:30 ET.** On 10-19 it was over at 11:35 ET. That is two consecutive
sessions; **watch item, no ID, 3 sessions needed** before anything is said about
it.

**No `PIN_THEN_EXPAND` instance.** `expiry_shape` was `COHERENT_SHORT`
(confidence high). The shape fired again on **10-21**, which is **observation 2
of 3** under the 10-19 pre-registration and is **graded tomorrow, on the rules
as written** — not here, and not revised.

**No axis-3 score is quoted,** today's included. The 10-16 specification is a
near-constant (9 of 9 conflict days, 15 of 16 control days) and the column is to
be **deleted, not re-scored**.

---

## 2. What the levels actually did

### The three pool rows below price were the best thing on the board

| level | dist | published claim | what happened |
|---|---|---|---|
| **29395.0** Asia Low (today) | −22 | *"the next session usually runs the stops below it"* | **run by 55.8**, then reversed; closed **+308.2** above |
| **29384.3** Asia Low (prev-day) | −32 | same | **run by 45.1**, closed **+318.9** above |
| **29301.3** London Low (today) | −116 | same | **run by 89.5** — and **89.5 below it is the session low** |

All three right, and the deepest one located the low to **89.5**. The stop-run
half of the session-extreme prose is the part of this board that earns its keep.

### The put side of the *options* board was useless, and the un-graded table was not

- **PUT WALL 29024.5** (−392, ●●●●● 0.55bn, *"the strongest floor on the
  board"*, *"if it breaks expect it to speed UP… don't buy the break"*):
  **never reached — 187.3 below the session low.** Its break condition never
  arose. 3rd consecutive session in which the published floor sat outside the
  day.
- **The secondary gamma table's 29224.5** (−192, 0.42bn, **22,982 contracts**),
  printed as *"out-of-the-money put gamma — dealers are SHORT gamma here, so
  they **amplify**… Not a floor"*: price traded **12.7 below it** and reversed
  **+497.1**. **It located the session low 174.6 points better than the named
  put wall, while its own prose denied it was a floor.**
- **29274.5** (−142, 0.46bn): through by 62.7, then **+447.1** — same error,
  same direction.

This is **P5** (the secondary table is published and graded by no tool) and
**P-E(b)** (the shelves are what should replace the headline wall's top line)
in one instance, and both are already PROPOSED.

### The call wall was a brake, not a lid — and both its sentences came true, four hours apart

**CALL WALL 29674.5** (+258, ●●●○○ 0.38bn): first post-scan touch **14:25Z**,
overshoot **+47.1** (session high 29721.6 at 14:30Z), then **−162.8** to
29511.7, then reclaimed and closed **+28.7 above**.

- **Clean on the contamination axis:** pre-scan high 29622.3 was **52.2 below**
  the wall, so the overshoot was earned entirely post-scan.
- **Overshoot 47.1 lands in P-E's 12–103 "middle"** — the **second** middle
  instance after 10-06. Census → **5 capped / 2 middle / 8 sliced**. The
  two-mode framing stays retired.
- The board printed *"rallies stall. Take profit into it"* first and *"a held
  close above flips that selling to buying"* second. **The day did the first for
  163 points and then the second.** That ordering is exactly what **P-E**'s live
  prose proposal asks to reverse; today supports it without adding anything new.

### The level nothing respected

**Equal highs ×2 at 29600.1** (+183), published as *"2 touches at this price,
never traded through — a real stop cluster. **Prime S1 sweep trigger**"*. Price
crossed it at 14:15Z inside the 45-minute impulse and **never traded back down
to it**; it produced no stall and no reverse. The four rows between 29600.1 and
29629.2 were all sliced in the same **ten minutes**. The named S1 trade at this
row would have been a loss.

### P-G — instances #24 and #25, both the same mirror as #14/#15

- **29480.8 London Low (prev-day)**, **+64.0 above price**, printed *"the next
  session usually runs the stops **below** it"*.
- **29469.3 NY Low (prev-day)**, **+52.5 above price**, same note.

Both then worked — each held as support for **415 minutes** on the way back up —
with prose describing an event on the wrong side of price. Prose only, already
PROPOSED, free, still not actioned.

### Session-context field — 17th session

**11 of 19** board rows lay inside the pre-scan range 29297.7–29622.3, i.e.
price had already traded them before the board was published. Proposed 09-29,
arithmetic on data already on the page, **still not actioned**.

### P-B(b) — 16th → 17th session; TWO guaranteed windows, one fired

`merge_tol = max(3.0, 527.5 × 0.008) = **4.22**` against `TOUCH_TOL = **8.0**`.
Two adjacent pairs fall in the structurally-guaranteed window: **(29615.7,
29622.3)** 6.6 apart — **both graded touched at bar 196, fired** — and
**(29622.3, 29629.2)** 6.9 apart, touched at bars 196 and 197, **did not fire**.
Published 13/19 = **0.684**; distinct-event rate **0.474**; **inflation 1.44x**,
the second-worst in the series. Proposal unchanged.

### Never reached, and one of them could not have been

| level | dist | note |
|---|---|---|
| GAMMA FLIP 30051.1 | **+634.3** | **1.20x ADR away at the scan.** See §3 — this is the whole problem with the day's regime vote |
| MAX PAIN 29814.5 | +397.7 | **7th distance-confounded non-test**; the day-of-week qualifier was untested |
| STRUCTURAL CALL WALL 29774.5 | +357.7 | not reached; **P3/H6** takes no new touch |
| PDL + Equal lows ×2 29112.1 | −304.9 | ⭐ row, never reached |
| PWL 29073.7 | −343.1 | **H10** — price inside the prior-week range all day, neither branch fired |

**H4:** flip never reached. No instance. **H23:** both paths were flagged
**clear**, so `path_read()` named **no brake** — **no H23 instance**, census
stays **10 sliced / 2 capped / 3 never-reached**, and the force-ranking branch
stays **CLOSED as unfalsifiable**. Flagged again so no one opens a defect: the
secondary table reads `walls_ranked` (`brief.py:647`) while `path_read()` reads
`largest_abs_gex` (`brief.py:515`) — **different lists**.

**The corridor read itself is gradeable, and it split.** *"DOWNSIDE path: clear
to 29024.5 (392pts) — nothing structural to slow a breakdown… Do not fade it"*
— the breakdown **stopped 187.3 short** of the corridor end and reversed 509.8.
*"UPSIDE path: clear to 29624.5 (208pts)"* — price ran **97.1 beyond** the
terminus. Consistent with the **10-16 withdrawal** of the corridor-terminus
proposal (`brief.py:520` sets `corridor_end = span[-1]`, the far end of the
shelf list, not a barrier). 6th session of that series; **nothing revived.**

### M6 — session 28, and the worst single-row understatement in the record

| level | grader travel | actual excursion | ratio | grader verdict |
|---|---|---|---|---|
| **29455.5 PD mid** | 27.8 up | **266.1** | **9.57x** | *"broke DOWN through it — **lost** by 32.5"* |
| **29395.0 Asia Low (today)** | 56.8 up | **326.6** | **5.75x** | *"**lost** by 55.8"* |
| **29384.3 Asia Low (prev-day)** | 67.5 up | **337.3** | **5.00x** | *"**lost** by 45.1"* |

**3 of 13 verdicts inverted and 9.57x is the largest ratio on record** (10-16's
worst was 8.2x). All three rows closed **247.7–318.9 points above** the level the
grader says they *lost*. The remaining ten rows read 1.00x on the up side and
1.00–1.76x on the down side.

**M6's "magnitude scales with travel" claim does NOT survive this session.**
Post-scan travel was **0.97x** ADR against 10-16's **2.01x**, yet the worst
ratio is **larger** (9.57x vs 8.2x). The driver here is not travel: it is that
these three rows were **first touched before the reversal**, so the grader's
window measured the leg that ended rather than the one that mattered. Session 27
stated the scaling claim; **session 28 is a counter-instance with a mechanism.**

---

## 3. What was wrong, and why

### The gamma block was WRONG and outvoted, into a directional call — a new cell, 1 for 1

| day | `gamma` | all other blocks | `gamma` − rest | published | realised post-scan |
|---|---|---|---|---|---|
| 10-08 | −5 | +4 | −9 | NEUTRAL / TWO-WAY | 671pt trend day |
| 10-09 | +4 | −6 | +10 | NEUTRAL / TWO-WAY | −35.3 = 0.07x ADR |
| 10-12 | −2 | +4 | −6 | NEUTRAL / TWO-WAY | −181.3 = 0.41x ADR |
| **10-20** | **−5** | **+9** | **−14** | **MILDLY BULLISH +4** | **+295.0 = 0.56x ADR, CORRECT** |

Three instances of *"gamma right, outvoted into a no-call"*; **this is the
first where the outvote produced a call, and the outvote was right.** The
pre-registered quantity — sign and size of `gamma` minus the sum of all other
blocks against `|post-scan| / ADR` — still **does not order the outcome**:
|g−rest| of 9, 10, 6, **14** against 1.5x, 0.07x, 0.41x, **0.56x**. The largest
margin ever recorded produced a mid-sized move. **n=1 in the directional cell.
Nothing proposed.**

**Where the −5 came from, and which half deserved to lose.**

- **−3, location:** *"below flip 30051.1 by 634.3pts — downside accelerates,
  rallies unstable."* **Half right.** The downside did accelerate — 205.0 points
  through three pools in 57 minutes. The rally that followed was **not
  unstable**: 509.8 points in 45 minutes, closing 18.4 off the high. The row
  scores one sign for two claims and only one of them held.
- **−2, week net GEX −5.81 → *"expansion likely"*.** This row carries **±2 of
  direction score** for a statement about **range**. Its direction content is
  measured **null** and I re-ran the register's own pre-registered test with the
  current sample: **15 right / 11 wrong = 58%, n=26 days** — identical to the
  58% at n=19, so more data has not moved it. Its range label was **also wrong
  today**: *"expansion likely"*, realised **0.966x ADR** (**H22 n=12**). A row
  that is null on direction and non-discriminating on range cast **−2 of the −5
  that lost the vote.** H22's own counterfactual (zeroing the row converts wrongs
  *and* rights into no-calls) is why nothing is proposed; the instance is logged.
- **The flip was 634.3pts — 1.20x ADR — away.** The regime row's own escape
  clause (*"reclaim and hold above and fading becomes valid"*) was unreachable by
  construction on a day with a 202.9pt budget, and the board still marked the
  flip `(stretch)` and printed it as actionable.

### The strategy block was wrong, on the one trade the day actually offered

`STRATEGY 2 — "Below the flip in negative gamma: dealers amplify, **sweeps run
rather than fail**. Strategy-1 fades have a materially lower hit rate here —
only take them at the far walls"* and, in §2, *"**Fading is the wrong trade
today**."*

The day's only sweep — pre-scan low 29297.7 taken out by **85.9** at 13:40–13:45Z,
through three published pools — **failed, and reversed 509.8 points.** The
winning trade was a **Strategy-1 fade**, at **29211.8**, which is **not a far
wall**: the nearest named wall was 187.3 lower.

**This is a second instance of "the direction call and the strategy block
pointed opposite ways, and direction won"** (the 10-14 entry, which asked for
exactly this so it would not have to be re-derived). 10-14's instance was
**above** the flip with `MODERATE` fuel and Strategy 1; today is **below** the
flip with `MODERATE` fuel and Strategy 2. **n=2, in opposite gamma regimes, both
with the bias score right and the strategy block wrong.** Below threshold,
nothing proposed.

**It is also a caution on a live proposal, and this is the reason to write it
down.** **H2 is FALSIFIED at n=7** (5–2 to the gamma block, 7–0 if ties go
against the fade) and the live proposal is to **suppress or subordinate the fuel
block's fade instruction below the flip**. **10-20 is `MODERATE`, so it is NOT a
cell instance** — `track.py`'s own low-fuel list omits it, and it is **not**
entered into that census. But it is a day **below the flip** on which the fade
was the only winning trade, by 509.8 points. **The H2 proposal must stay scoped
to `LOW_FUEL`/`EXHAUSTED`; today is evidence against generalising it to "below
the flip" as such.**

### The margin of the call was one stale FRED observation — and suppressing it would have cost the call

`macro +2` = **DFII10 +3** (real yield 2.74%, −4bp **as of 2026-10-16**) +
**DGS10 +1** (*"moved 1bp down, 2026-10-15 to 2026-10-16"*) **− HY OAS 2**.

- **H18 / P1 — instance 22, duplication 27 of 27.** Both rows resolve to the
  same FRED observation date, **2026-10-16, two business days stale**, and the
  age warning printed on **DFII10** and **not** on DGS10 — the rendering defect,
  **27th consecutive certain instance**. **HY OAS rendered no observation date
  for the 14th consecutive session.**
- **Suppressing the stale pair takes +4 → 0**: `NEUTRAL / TWO-WAY`, a **no-call
  on a day with a +295.0 post-scan move**. On the register's own convention the
  age gate's record becomes **4 helped / 3 hurt**, and on a
  magnitude-respecting basis **3 helped / 3 hurt** — today's hurt is **295
  points**, against a 4th "help" worth **9.3**. **The accuracy case stays
  RETRACTED; the live defect remains the rendering one.**
- **HY OAS −2 was wrong-signed** (3.31%, +20bp/5d, *"bonds are usually right
  first"*; the index went up 295). It has now scored on **27 of 34** scans, so
  the *"dead weight"* correction continues to hold — it is wrong, not idle.

### The remaining blocks

- **rates +3** (US10y 5.077, −1.15%) and **breadth +3** (mega-caps +0.96% 3/4
  up; NDX +1.17% vs ES −0.29%) were the right side of the day. **D22 caveat
  recorded, not waived:** the NDX and ES legs do not cover the same window, so
  the +1 *"tech leading"* row is not a like-for-like comparison even on a
  Tuesday. Instance logged on a day the suspect row was **right**.
- **vol +1** net of four rows (VXN +2, VVIX −1, two zeros) — correct side, small.
- **structure 0** net: *"below PD mid"* −1 (price closed **247.7 above** PD mid)
  and *"4 unmitigated pools above / 0 below"* +1 (**right** — the draw was
  higher). The board meanwhile listed **three** pool rows below price. The pool
  counter and the board do not use the same definition of a pool; noted, no
  number taken.
- **news 0.** One auto-scored headline: *"Apple Stock Escaped the AI Downturn.
  Now It Faces a 27% Plunge, Says Analyst"* → tagged **[earnings_miss]**,
  rendered as *"Mega-cap miss/warning → index-weighted drag"*, 🔴 bear, on a day
  that rose 295 points. **It is an analyst price target, not an earnings miss.**
  **D18 — 8th trading day, 14th headline instance.** Damage **none**: raw −0.51
  → 0 points. **H19 coverage 1/133 = 0.75%**, the lowest non-zero reading in the
  record (133 headlines → 44 relevant → 1 scored).
- **events 0** on 3 of 3 rows. NFLX reported **after** the close as printed;
  `event_gate: null` correct. **No D24 instance.** The row is now **0 / 34**.

### H26 — n=26, and the correlation falls for a THIRD consecutive session

Method stated, per the 10-20 proposal: one PRE_NY scan per day, `is_trading_day`,
09-24 excluded, no-call days **included** with their realised values.
**Re-derivation reproduces the register exactly at n=25** (+0.548 / +0.190 and
all four bucket means), which validates the sample before 10-20 is added.

| \|score\| | n | C | W | no-call | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.181 | 1.103 |
| **3–5** | **6** | **4** | 2 | 0 | **0.254** (was 0.193) | **1.013** (was 1.023) |
| 6–9 | 7 | 6 | 1 | 0 | 0.545 | 1.193 |
| ≥10 | 6 | 3 | 3 | 0 | 0.783 | 1.390 |

Spearman(|score|, |post|/ADR) **+0.548 → +0.535** · range/ADR **+0.190 →
+0.191**. **Bucket form holds** — the |post|/ADR means are monotonic for a 4th
consecutive session (0.181 / 0.254 / 0.545 / 0.783). **Correlation form has now
fallen three sessions running** (+0.612 → +0.577 → +0.548 → +0.535), and 10-20
is the cause: |score| **4** with |post|/ADR **0.559**, a near-top-bucket move in
the second-lowest bucket. 10-20 is a **3–5 bucket instance, CORRECT**.
**The signed Spearman is not quoted** — it reproduces under no available
convention (+0.220 / +0.102 vs a published +0.157) and the live proposal is to
carry its method or stop quoting it.

### P4 / H1 — n=30 days; one new data point, and the statistic is NOT re-derived

10-20 error **−17.7** (budget 202.9, extension 185.2) — the **5th-smallest
|error| in the record**, and a **non-zero-budget** day, so it is not one of the
seven arithmetic-floor entries. `track.py` per-day mean **+54.3 → +51.9** (n=30,
incl. 09-24); per-scan **+52.7** (n=33). **NOT re-derived.** Claim stays **"no
usable skill"**; the **multiplier branch stays closed**; **pre-scan pace carries
no information in either direction and that question is closed** — today's
`fuel_ratio` **1.37 (normal)** preceded a **0.97x ADR** range, which is the
third reading in a row that says nothing.

**Traversal vs budget, stated once:** 509.8 against 202.9 = **2.51x**. The
budget bounds **extension**, not travel; this is the quantity the deleted axis 3
was mis-measuring.

---

## 4. Change proposals — none new, and one measurement answered

### The duplication measurement, run across the record — and it does not support a weight change

Asked after the 10-21 scan printed **−7** with **−4 from a single FRED
observation** (DFII10 −3 + DGS10 −1) and **−2 from one UK CPI headline carried
by two outlets**, leaving **−1 of independent signal**. **Rules fixed before any
outcome was inspected:** one PRE_NY `is_trading_day` scan per day, 09-24
excluded, 10-21 excluded as ungraded (**n=26 graded days / 19 calls**);
collapse (a) = the DFII10/DGS10 pair becomes **one row, the larger |points| one
kept**; collapse (b) = duplicate scored headlines become **one event**, raw score
scaled by `events / headlines`, `bias_points = clamp(round(raw/2), ±4)`.

| basis | C | W | no-call | rate | labels changed | sides changed |
|---|---|---|---|---|---|---|
| **published** | 13 | 6 | 7 | **68.4%** | — | — |
| **collapse pair → 1 row** | 13 | **5** | 8 | **72.2%** | **4 / 26** | **1 / 26** |
| **drop the pair entirely** | 13 | **7** | 6 | **65.0%** | **21 / 26** | **7 / 26** |

- **The double-count is structurally real and large.** The pair contributes
  exactly **±4 on 29 of 34 scans** and ±1 on the other 5; **|pair| ≥ |score| on
  9 of 26 graded days**, and on 10-20 it is **exactly the margin** (|pair|/|score|
  = 1.00).
- **It is also nearly inert on direction.** The minimal dedup changes the
  printed **label** on 4 of 26 days and the **side** on **one** (09-30, where a
  WRONG call becomes a no-call). The 3.8-point "improvement" is **one day**. That
  is not evidence and nothing is proposed on it.
- **The aggressive version is worse**: dropping the pair gives **13/20 = 65.0%**,
  with 3 helps (09-25, 10-08 no-call→correct; 09-30 wrong→no-call) against
  **4 hurts** (09-29, **10-20** correct→no-call; 10-01, 10-02 no-call→wrong).
  This is an independent, whole-sample confirmation that **H18/P1's accuracy case
  stays retracted.**
- **The headline half has never yet touched a graded day.** Duplicate scored
  headlines occur on **2 of 35 PRE_NY scans in the whole record**: **09-24**
  (quarantined) and **10-21** (ungraded). On 10-21 the collapse takes news
  **−2 → −1** and the score **−7 → −5**, `BEARISH → MILDLY BEARISH`. **H19's
  match-count defect is confirmed in its purest form and is, so far, a
  label-only effect.**
- **Limitation, stated rather than hidden:** on **2 of 35** scans the published
  news table holds fewer rows than were scored (09-11 13:24: **10 scored, 6
  shown**; 10-05: **7 scored, 6 shown**) and the journal stores no per-headline
  list, so duplicate detection on those two scans is **incomplete and
  unrecoverable**.

**Conclusion, and where it lands.** The right fix is the **rendering** one —
one row per FRED observation, with the observation date on every row — which is
**already PROPOSED under H18 / P1** and was grepped for before this was written.
**No new number is taken, and no weight change is proposed**, because the
measurement says a weight change makes the record worse. The measurement is the
answer to the question, reported in both directions as asked.

### Nothing else reaches a threshold that resolves to a model change

Items at or over threshold today, all resolving to **no change**: **H2**
(FALSIFIED at n=7; today is **not** a cell instance and is **not** added to the
census); **H22** (direction null at 58%, n=26; range label wrong, n=12);
**H26** (bucket form holds, correlation form erodes); **P4/H1** (answered
negative, multiplier closed, pace question closed); **H23** (ranking branch
closed, no brake today); **P-H** (no 6th deciding instance); **H8**
(ANSWERED-POSITIVE, post-closure only).

**Below threshold, appended only:** the MODERATE-below-flip fade instance (n=1);
*"the whole move was over by 10:30 ET"* (n=2 with 10-19); the gamma-wrong-and-
outvoted directional cell (n=1); M6's travel-scaling counter-instance (n=1).

### Standing proposals this day supports, none of them new

**P-E** (lead with the conditional, drop *"rallies stall. Take profit into it"*)
· **P-E(b)** / **P5** (the shelves, and grade the secondary table — today the
22,982-contract shelf beat the named put wall by **174.6 points**) ·
**P-G** (#24, #25) · **session-context field** (17th session, 11 of 19 rows
pre-traded) · **P-B(b)** (inflation 1.44x) · **H18/P1** rendering ·
the narrowed dead-weight proposal.

**Dead-weight audit, refreshed to n=34 PRE_NY `is_trading_day` scans (09-24
excluded by hand):** `events` **0/34** · `macro` yield curve (10y–2y) **0/34** ·
`rates` DXY 4/34 · `macro` NFCI 5/34 · `macro` WALCL/RRP 6/34 · `rates` US10y
26/34 · `macro` HY OAS **27/34**. The narrowed proposal — drop the yield-curve
row and WALCL/RRP — is **unchanged and still not actioned**.

### No new data point is warranted

The input that would have changed 10-20 is **not** a new series. The call was
**right**; what was wrong was the **weighting of rows that are already on the
page** (a stale pair carrying the margin, a range row voting on direction, a
regime row quoting an unreachable escape clause). Nothing free and reliable
would have fixed those, and proposing a feed to paper over a weighting problem
is how the model gets worse.

---

## Appended without proposal

- **D23 — 15th residual, and a FIFTH consecutive SIGN disagreement.** Board
  **+74.5** vs section-7 **−191.3**, matched to feed time 11:59Z. Gap
  **+265.8**; CFD move (11:55Z bar open **29345.1** → scan **29416.8**) =
  **+71.7**; **residual +194.1**, back inside the ±200 band. Series:
  `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
  −68.0 / +165.0 / +438.2 / +33.6 / −385.5 / **+194.1**`. **Damage none** — no
  volume had traded.
- **The realised-close-basis log — observation 5 of 10.** NDX cash close 10-20 =
  implied 29698.8 (10-21 scan) − roll (**+208.5**) = **29490.3**; CFD close
  **29703.2**.

  | day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
  |---|---|---|---|---|---|---|
  | 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
  | 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
  | 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
  | 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
  | **10-20** | **+74.5** | **29490.3** | **29703.2** | **+212.9** | **+138.4** | **+208.5** |

  **Third consecutive positive realised basis and by far the largest.** It
  implies NDX cash fell **39.1** on 10-20 while the CFD rose **143.8** from the
  prior close — a **183-point** one-session divergence between a cash index and
  a CFD that tracks it, which is not a market fact. **One of the two inputs is
  wrong: either the 16:14:59 cash print or the +208.5 roll.** Second up-roll in
  the log, and the register's own parser cannot read up-rolls at all (16 of 32
  silently `None`), so **no |roll| regression may be quoted until it is rebuilt
  sign-tolerant**. Re-test still at **n=10 clean observations. Nothing
  proposed**, and the proximity story is **not** revived — it was NULL at n=5.
- **Board offset 74.5, the fifth breach.** Arithmetic verified independently and
  correct (NDX cash 10-19 **29529.35**, roll **−187.0**, implied **29342.3**,
  CFD **29416.8** → **+74.45**); **no contract roll**. New, and the only thing
  worth adding: the breach **did not mean-revert intraday** — the realised close
  basis was **+212.9**, nearly triple the scan figure. On the one other breach
  day with a logged close (10-15, offset +77.6) the basis **crossed zero** to
  −50.3. **Two breach days, gaps 128.0 and 138.4, opposite directions. n=2,
  mechanism still unexplained, nothing proposed, no third story substituted.**
  The structural mitigation holds: every level within **212pts** of price was
  session-derived (cTrader-native, offset-immune) and every options-derived
  level was **≥258pts** away.
- **D25 — 28th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"*, printed four lines under *"No volume has traded yet
  today"*. Damage none.
- **D26 — reporting gap, not data loss; the retraction stands, and today it did
  NOT eat the day.** `track.py` reports **30 trading days / 33 scans
  (deduped)** and graded 10-20 on the same day `review_day` did — the first
  session in four with no eaten evidence. On disk: **37** day directories,
  **67** scan JSONs, **32** days with a PRE_NY scan, **31** with a `REVIEW.md`
  (**32** after this review), **28** with both. `track.py` still prints **no
  literal `actionable: YES/NO`**; the threshold rule was applied by hand.
- **H7** — no overnight scan, no instance. **D21** — no instance; near-miss
  worth one line: `gamma +0` at **60%** up the band, 20 points under the
  threshold, on a day price closed **above** the band top. **P-F** — price
  inside the prior-day range 29112.1–29799.0, no instance. **H20** —
  CLOSED-NEGATIVE, not revived; no High/Medium events. **H3** —
  CLOSED-NEGATIVE, superseded by H26. **H17** — post-scan move 295.0 = **57.9%**
  of the session range; not a deadband instance, stays **2 of 3**.
- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Straddle
  band **29132 .. 29701**, close **29703.2** — **outside by 2.2 points**, the
  narrowest miss available. The VXN-implied range **473.6** under-read the
  realised **509.8** by 36.2.
- **Max pain** — 7th distance-confounded non-test (+397.7). **P3 / H6** — the
  structural call wall was 357.7 away and untouched; census unchanged.

## Journal hygiene

One scan file for 10-20 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 16th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29 proposal
for one is reaffirmed, because `track.py` keeps 09-24 inside every statistic it
prints (direction **17/7/9** becomes **16/7/9** once 09-24 is removed).
**2026-10-13 has no journal directory** — documented, not recreated. 09-09 and
09-25 still have no `REVIEW.md` and none was created. **2026-10-21 is on disk,
`is_trading_day: true`, 180 bars, correctly held back by `track.py`, and is
excluded from every statistic above** — its scan is counted only in the
dead-weight audit, which counts rows and not outcomes. **No `prediction` block
was touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**
