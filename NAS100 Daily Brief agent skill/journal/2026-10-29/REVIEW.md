# REVIEW — 2026-10-29 (Thursday)

_Written 2026-10-30 after the 10-30 brief was delivered. Nothing here blocked,
delayed or altered that brief. One scan graded: `1248-preny.json` + `.md`,
`PRE_NY` 12:48:55Z, `is_trading_day: true`, 276 bars, **0 test artefacts**.
No `prediction` block was touched; no scoring, wall or grading code was edited._

---

## 1. Scoreboard

**Call:** `MILDLY BEARISH −5` at **29463.2** · direction **−1** · shape
`COHERENT_SHORT` · fuel `MODERATE` · budget **257.8** · ADR14 **565.9**.

| | value |
|---|---|
| Session O / H / L / C | **29623.8 / 29642.7 / 28964.4 / 29069.5** |
| Range | **678.3** (1.199× ADR14) |
| Net move | **−554.3** |
| Post-scan move (last bar, `price_at_scan` anchor) | **−393.7** (`review_day`: −395.1 on the `fwd[0].open` anchor) |
| Direction, post-scan basis | **CORRECT** |
| Direction, day-net basis | **CORRECT** |
| Levels published / touched | **17 / 5** → hit rate **0.294** |
| …deduplicated for the 6.9-pt pair | **4 / 16 distinct prices = 0.250** |
| Range extension vs budget | 370.2 vs 257.8 = **1.44×** → `fuel_call: "about right"` |
| Price traversal vs budget | 593.9 = **2.30×** |
| \|post-scan\| / ADR | **0.696** |

**The two windows, because every number above depends on which one you use:**

| window (UTC) | O | H | L | C | range | post-scan move | extension vs budget |
|---|---|---|---|---|---|---|---|
| day start → 19:55 (to the cash close) | 29623.8 | 29642.7 | 29259.0 | **29423.5** | 383.7 | **−39.7** | 75.6 = **0.29×** |
| **20:00 → 20:55 (post-close)** | 29417.4 | 29442.4 | **28964.4** | **29069.5** | 478.0 | — | — |

The **20:00Z bar alone** was `O 29417.4 / H 29442.4 / L 29091.0 / C 29091.0` —
a **−351.4-point five-minute bar** on the AMZN after-hours tape. The post-close
hour supplied **43.4% of the day's range** and **89.9% of the graded post-scan
move**.

---

## 2. What the levels actually did

**Touched — 5 rows, 4 distinct prices.**

| level | dist | published expectation | what happened |
|---|---|---|---|
| **29521.7 PDL** | +58 | *"Sweep it, wait for a higher low on the 1m, then CISD = **long**"* | Touched 12:55Z, poked **+27.6** through, then fell **262.7**. The long instruction lost; the continuation short that §1 and §2 both called for won. |
| **29403.8 London Low (today)** | −59 | *"the next session usually runs the stops below it"* | Ran. Closed **334.3 below**. Grader prints *"broke **UP** through it — lost by 38.6"*. |
| **29396.9 Equal lows ×2** | −66 | *"a real stop cluster. Prime S1 sweep trigger"* | Same bar, same outcome. Closed **327.4 below**. Same inverted wording. |
| **29334.6 Asia Low (today)** | −129 | *"runs the stops below it"* | Ran. Closed **265.1 below**. Same inverted wording. |
| **29089.3 PUT WALL ●●●●● 0.68bn** | −374 | *"if it breaks, expect it to **speed UP, not bounce**. Don't buy the break."* | Broke by **124.9** (0.221× ADR) at 20:00Z, then **bounced 165.1** and was pinned within 65 pts of the wall for the last 50 minutes, closing **19.8 below**. The explicit instruction was wrong on both clauses. |

- The three liquidity rows at 29403.8 / 29396.9 / 29334.6 were **first touched at
  the same bar** (13:30Z, index 186) and their `settled_read` windows all open at
  **19:55** — i.e. every verdict in the day is produced inside the post-close
  hour. **M6, session 35.** The driver of the M6 series remains **UNKNOWN**.
- The *"broke **UP** through it"* wording is internally consistent with
  `review_day.py:159` (it names the adverse excursion, not the net move), but on
  three rows price broke **DOWN** through and closed 265–334 points below.
  **Second consecutive session** with the wording-inversion shape (session 34's
  seventh shape).
- **29403.8 and 29396.9 are 6.9 points apart — inside `TOUCH_TOL = 8.0`.** They
  are one touch counted twice. A second guaranteed window sits at
  **29590.9 / 29586.1 = 4.8 apart** (untouched). The published hit rate 0.294 is
  inflated to 0.250 once the realised double-count is removed.
- **PUT WALL is formally UNGRADED** — *"touched, no settled read (too few bars on
  one side)"*, because the touch landed at 20:00Z with eleven bars left. For the
  **second consecutive session** the best-executed wall on the board is the one
  the official grader cannot score.

**Untouched — 12 rows, all of them above price.** `GAMMA FLIP 29941.3` (+478),
three prev-day session highs (+349…+391), `STRUCTURAL CALL WALL ●●●●● 1.11bn +
London Low prev-day ⭐` (+276), `MAX PAIN 29669.3` (+206), `Asia Low prev-day`
(+188), `CALL WALL ●●○○○ 0.28bn` (+176), `Asia High today + NY Low prev-day +
Equal highs ×2 ⭐` (+156), `PD close` (+128), `London High today` (+123),
`Equal highs ×2` (+114).

- **The hit rate is structurally capped by the board's own asymmetry, not by the
  levels.** 12 of 17 rows sat above a correctly-called bearish day; five of them
  were marked _(stretch)_ beyond a 258-point budget. A correct direction call
  guarantees a low hit rate on this board. The hit rate is therefore **not** a
  measure of level quality on days like this and should not be read as one.
- **MAX PAIN 29669.3 is a clean, non-distance-confounded test and it FAILS by
  599.8** — on a **Thursday**, the day its own rider calls strongest
  (*"weak on a Monday, strong by Thursday/Friday"*). Clean census **1 hit / 2
  misses at n=3** (10-27 fail 234; 10-28 hit 6.2; 10-29 fail 599.8).
- **STRUCTURAL CALL WALL: never reached, so no touch and no confounding
  question.** P3/H6 stays **loose 2 touches / 2 worked, strict 1 clean / 1
  worked**. Under either count the call side is below 3, so the standing
  *"stop publishing the structural CALL wall"* narrowing **must not be actioned**.
- **The day's real post-break ceiling was a level the brief told the reader not
  to mark.** The footnote read *"Beyond today's range (context only, don't mark):
  … **29136 Equal lows ×2** …"*. After the 20:05 low, the remaining eleven bars
  topped at **29129.5 — 6.5 below it**, inside `TOUCH_TOL`. It capped the entire
  post-break tape and is invisible to every statistic because it is not a board
  row. D7's truncation limbs are both **clean controls** here (footnote 5 rows
  against a cap of 6, nothing dropped) — this is the *budget-demotion* rule, not
  truncation, and it is a different shape. **n=1.**
- **The "clear path" read was right.** §3: *"DOWNSIDE path: clear… to 28889.3
  (574pts, 1.01× ADR) — nothing structural to slow a breakdown."* Price ran
  **498.8** of those 574 and stopped **75.1** short of the named terminus. The
  six secondary-table strikes all said *"dealers are SHORT gamma here… accelerate
  THROUGH rather than stall. Not a floor"* and **none of them stalled anything**
  — correct, but undiscriminating: every row said the same thing on a one-way day.
- **No level qualifies as noise-to-be-dropped on this session's evidence.** The
  untouched rows were untouched because the direction call was right, which is
  the opposite of the noise case.
- **P5:** the best-placed level on the page was **PUT WALL on the MAIN board**
  (close 19.8 away); the nearest secondary row was 169.8 away. **Second
  consecutive session** with the best level on the main board.

---

## 3. What was wrong, and why

**The direction was right. The score was numerically right by the exact
cancellation of two equal and opposite defects. That is luck, not calibration.**

Published: `gamma −5 · macro +4 · news −4 · structure −2 · rates +1 · breadth +1
· vol 0 · fuel 0 · events 0` = **−5**.

### (a) `news −4` — H19 match-count inflation, quantified for the first time

Five auto-scored headlines, raw **−9.42**, **two events**. The per-headline
weights reconstruct exactly from `news_scorer.py`'s own rule table
(`weighted = direction × mag/100 × freshness`):

| event | rule | mag | freshness | weight |
|---|---|---|---|---|
| Q3 GDP / Sept PCE | `cpi_hot` | 250 | 1.0 | **−2.50** |
| Q3 GDP / Sept PCE | `cpi_hot` | 250 | 1.0 | **−2.50** |
| Alphabet / Samsung | `earnings_miss` | 170 | 1.0 | **−1.70** |
| Alphabet / Samsung | `earnings_miss` | 170 | 1.0 | **−1.70** |
| Alphabet / Samsung | `earnings_miss` | 170 | **0.6** | **−1.02** |
| | | | **sum** | **−9.42** ✓ |

- **Sign: RIGHT.** Both events were bearish and the day fell 554.3.
- **Magnitude at one vote per event:** −2.50 + −1.70 = **−4.20** →
  `round(−4.20 / 2)` = **−2**.
- **Published −4, and it was AT THE CAP**: `round(−9.42 / 2) = −5`, clipped to
  −4 by `max(-4, min(4, …))`. The cap absorbed one point of the inflation and
  the block still over-counted by **2**. **This is the largest measured H19
  harm in the record.**
- **Consequence: none, today.** News −2 → score **−3** → still `MILDLY BEARISH`
  (the label band is ≤ −3), still direction −1, still **CORRECT**, still H26's
  **3–5** bucket. The defect is real and it changed nothing.

### (b) The `cpi_hot` tag on the GDP headline — **NOT entered as a D18 instance**

*"Third-quarter U.S. GDP increases a **better-than-expected 3.4%** as September
inflation accelerates"* → `[cpi_hot]` → *"Hot inflation -> yields up, multiple
compression"*. The 10-29 review flagged this as a D18-family shape — *one
headline, two opposite signals, first match wins* — and deliberately deferred
entry. **Entering it would be wrong, and the deferral was the right call.**

D18's claim is that **the printed reason is FALSE**. Here it is **true**:
September inflation did accelerate, and that is what the rule says. And the two
clauses are **not opposite signals for the NDX** — a better-than-expected GDP
*plus* accelerating inflation both push the hawkish read in the same direction,
which is exactly the printed mechanism (*yields up → multiple compression*). The
growth beat reinforces the tag; it does not contradict it. What remains is a
**latent** ordering hazard — the rule reached a right answer by matching one
clause and would have been indifferent had the clauses pointed opposite ways —
and a latent hazard is not an instance. **D18 stays at 10 trading days / 17
headlines. Recorded as a NEAR-MISS and a named control.**

### (c) `+5` of the brief's `+6` positive points are three readings of the same instrument

| row | block | pts | as of |
|---|---|---|---|
| *"US10y 5.026 (−0.38%) — yields down, BULLISH tech"* | `rates` | **+1** | live |
| *"Real yield, 10y (DFII10) … 2.64%, down 2bp"* ⚠️ | `macro` | **+3** | **2026-10-27** |
| *"10y nominal yield (DGS10) moved 1bp down"* | `macro` | **+1** | **2026-10-26 → 10-27** |

This is **H18 / P1's duplication as a TRIPLE for the first time** — the register
has only ever recorded the DFII10/DGS10 *pair* — and **two of the three legs are
two business days stale** while the third is live. Collapse to one vote at the
largest leg (+3) and **2 points come off**.

### (d) The two defects cancel to the point

```
published :  gamma −5 + macro +4 + rates +1 + breadth +1 + structure −2 + news −4  =  −5
corrected :  gamma −5 + 10y-collapsed +3 + breadth +1 + structure −2 + news −2     =  −5
```

Identical. **A +2 over-count on the 10-year yield and a −2 over-count on
duplicated headlines produced the right number between them.**

### (e) The same page read the same world both ways, and neither block defers

`macro +4` says *yields are falling, tailwind for tech*, off FRED data that
stops at **2026-10-27** and is ⚠️-flagged in the brief's own text. `news −4`
says *hot inflation → yields up, multiple compression*, off a **same-morning**
GDP/PCE print. They cancelled to roughly zero inside a −5 call. Had `macro` been
current, the score would have been **−9** (`BEARISH`) — and the realised
**0.696** \|post\|/ADR sits above the 6–9 bucket mean (0.510) and above the ≥10
mean (0.634), so the deeper score would have been the better magnitude forecast.

### (f) `breadth +1` was yesterday's tape — D22

*"NDX +0.55% vs ES −0.44% — tech leading, genuine risk appetite"* is the
**10-27 → 10-28 cash** move, printed 42 minutes before a session that fell
554.3. Removing it → **−6** (`BEARISH`), closer to the realised move. The
companion row, *"mega-cap avg +0.15% (1/4 up): NVDA −1.18%, MSFT −0.06%,
AAPL −0.94%, AVGO +2.77%"*, scored **0** on a mean that is positive **only**
because of AVGO while three of four were down. That is the **second** recorded
instance of the outlier-driven mega-cap mean (after the 08-28 artefact); it did
**no damage** today because it scored 0. The register's own note says open it at
a third recurrence. **Not opened.**

### (g) `events 0 on 3 of 3` — including the thing that decided the day

`AMZN earnings 2026-10-29 time-after-hours (cons $2.01) — sector-relevant`
scored **+0**, and the AMZN tape produced **89.9% of the graded post-scan move
in one five-minute bar**. This is the **second consecutive session** with that
exact shape (10-28: MSFT/GOOG/GOOGL at +0, 100% of the graded move). **n=2.**
Dead-weight census for the day: **17 of 28 rows scored zero** (`events` 3/3,
`macro` 4/6, the three `news` bullets, `fuel`, the band `gamma` row, the
prior-week `structure` row, `vol` 2/4, `rates` 1/2, `breadth` 1/2).

### (h) What was RIGHT, and it should be said

`gamma −5` was the best block on the page and both of its rows were correct:
*"below flip by 478 — dealers amplify, downside accelerates, rallies unstable"*
(price fell 393.7 post-scan with no sustained rally) and *"week net GEX −5.001 →
expansion likely"* (range **1.199× ADR**). `structure −2` was also right
(*below PD mid*; *3 pools above / 4 below → draw lower* — the draw was lower).
**H22 n=16, label RIGHT.**

### (i) The grading-window caveat, stated once because it infects everything above

On the cash-close basis the same day reads: post-scan **−39.7**, extension
**75.6 = 0.29× budget** (a **3.4× over-read**, against the official 1.44×
under-read), \|post\|/ADR **0.070** instead of 0.696, H8's straddle band
**INSIDE** instead of outside, H9's containment claim **supported** instead of
contradicted, H17's deadband **5.9%** instead of 58.0%. **One five-minute bar
flips five register statistics.** See §4.2 — this did **not** reach the
pre-registered threshold and nothing is proposed on it.

---

## 4. Change proposals — **NONE**

**No material change is proposed by this review. No ID was allocated.** Every
item below is either an existing entry taking a data point, or a claim that has
not reached three same-signed sessions. `track.py` prints **no literal
`actionable: YES/NO`**, so the 3-session rule was applied **by hand, per entry**,
and is stated per item.

**1 — H19 event-deduplication. Threshold NOT met. Nothing proposed.**
Large match-count instances: **10-29** (5 headlines / 2 events, harm 2 points,
graded above) and **10-30** (4 headlines / 2 events, raw −6.80 → −3, **not
graded**). That is **n=2, one of them ungraded**, against a rule of three. The
obvious fix — one vote per event — is **not** proposed.
*Pre-registered so the next reviewer does not re-derive it:* this becomes
actionable at **3 graded sessions** where (i) ≥2 auto-scored headlines collapse
to one event and (ii) the recomputed one-vote-per-event score differs from the
published `news` block by ≥1 point, **with the direction-verdict effect reported
per session**. On 10-29 that effect was **zero**.

**2 — P-H, the grading-window limb opened on 10-28. 10-29 is NOT a 4th
instance. Nothing proposed.**
Computed both ways with `price_at_scan` as the anchor: to the **last bar before
20:00Z** (19:55 close 29423.5) → **−39.7, CORRECT**; to the **last bar**
(20:55 close 29069.5) → **−393.7, CORRECT**. **The bases agree**, so AMZN-
after-the-close did *not* reproduce the 10-28 split. The direction limb stays at
**3 instances, split 2–1** (09-29 late hour *saved* a wrong call; 09-30 and
10-28 late hour *broke* a right call), confirmed from source today — below the
pre-registered **4 instances / 3 same-signed**. **Which way does 10-29 point?**
*Against* the limb as a direction question (the convention would have cost
nothing) and *for* it as a magnitude question (89.9% of the graded move came
after the cash close).
**Correction to the limb's RANGE evidence, filed against the 10-28 entry.** That
entry reported post-20:00Z bars supplying >20% of the day's range on **3 of 31**
days: 10-28 **53.0%**, 10-19 **46.0%**, 09-17 **22.1%**. Re-derived from source
today under the method that **reproduces 10-28's 53.0% exactly**, 09-17 and
10-19 both return **0.0%** — their post-close windows sit wholly inside their own
cash ranges — and they also return 0.0% under two alternative definitions
(contribution to the post-scan range; post-window range ÷ day range). **From
source the range limb is 2 of 31: 10-28 53.0% and 10-29 43.4%.** Both counts are
reported; **neither is averaged and neither is retracted**. Either way the limb
is **below three**.

**3 — P-H proper: no 6th deciding instance.** Post-scan **CORRECT**, day-net
**CORRECT**; the bases agree. The register's hand-carried series goes to
**14/26 vs 15/26**, deciding set stays **n=5**. **From source today the same
census reads 13/24 vs 15/24 with a deciding set of n=4** (09-16, 10-07, 10-15,
10-19) — a different sample under the same name, because 09-14 has aged out of
the 45-day bar window and 10-29 has entered it. **Both reported, neither
averaged.** (D26.)

**4 — H26: 10-29 is a 3–5 instance, and the bucket's two headline figures are
in open conflict, as instructed.** The register's carried 6–9 figure and the
from-source figure are **reported both ways and averaged neither**:
register-carried **6/10 = 60.0%**, from-source **5/9 = 55.6%**.
From source at **n=31 days**:

| bucket | days | calls | right | direction | mean \|post\|/ADR | mean range/ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | 0 | — | — | 0.167 | 1.103 |
| **3–5** | **9** | **9** | **5** | **55.6%** | **0.370** | 1.130 |
| 6–9 | 9 | 9 | 5 | 55.6% | 0.510 | 1.074 |
| ≥10 | 6 | 6 | 3 | **50.0%** | 0.634 | 1.243 |

- **Magnitude monotonicity survives an 11th consecutive session** (0.167 / 0.370
  / 0.510 / 0.634).
- **The range/ADR column is not monotonic; the range/ADR claim stays RETIRED**
  and is printed only so it is not re-derived. No Spearman quoted.
- **⚠️ The ≥10 bucket no longer falls below a coin flip from source.** The
  standing figure is **3/7 = 42.9%**; from source today it is **3/6 = 50.0%**,
  because one WRONG ≥10 day aged out of the window. **Both reported, neither
  averaged.** The *"direction is inverted at the top"* claim is **suspended, not
  retracted**, until it survives a sample that is not shrinking underneath it.
- **10-29's own point:** \|score\| 5 → 3–5, direction **CORRECT**,
  \|post\|/ADR **0.696**, range/ADR **1.199**. **0.696 is the largest value the
  3–5 bucket has ever carried** — larger than the 6–9 *and* ≥10 bucket means —
  and it **alone** lifts the bucket mean from 0.329 to 0.370. On the cash-close
  basis the same day contributes **0.070**, the *smallest* value in the bucket.
  **H26's central surviving claim is being fed by the unresolved P-H window.**

**5 — H14, put-wall rider: 5th run-through instance, and the rider was wrong.
No new ID; H14 already carries a live PROPOSED item.** Run-through before any
reclaim **124.9 = 0.221× ADR**; series now `0.23 / 0.31 / 0.48 / 0.38 / **0.22**`
— the band's lower edge fails by 0.009, i.e. it is at the edge rather than
broken. Not reclaimed on the close (−19.8), so resistance-after-break goes to
**3 for / 2 against**; reclaimed within the session **2 of 5**. The rider's own
words — *"expect it to speed UP, not bounce. Don't buy the break"* — were
**wrong on both clauses**: the break produced a **165.1-point bounce** and a
50-minute pin. H14's existing proposal text should read *"run-through
0.22–0.48× ADR (n=5), reclaimed within the session 2 of 5"*. **Evidence
appended; nothing new proposed.**

**6 — Max pain: clean census reaches n=3 and does NOT point one way. Nothing
proposed.** 10-27 fail (234), 10-28 hit (6.2), **10-29 fail (599.8)** —
**1 hit / 2 misses**. Three instances that disagree is not three pointing the
same way. *Pre-registered:* the **day-of-week clause** (*"weak on a Monday,
strong by Thursday/Friday"*) is the specific thing to kill — it has now been
contradicted on a Thursday by the largest miss in the record and on a Wednesday
by the only hit. Propose deleting the clause after **two more Thursday/Friday
misses**, not before.

**7 — Items taking a data point, nothing proposed on any of them.**
- **H27 — observation 5.** `vol 0 ↔ breadth +1` (+1); `structure −2 ↔ gamma −5`
  (−7); independent remainder `macro +4 · rates +1 · news −4` = **+1, opposite in
  sign to the call**. Same shape as observations 1, 2 and 4. The pre-registered
  collapse, run as written: the vol/breadth pair is not strictly same-signed
  (vol 0) so nothing drops; structure/gamma is, so structure −2 drops → **−3,
  direction −1, still CORRECT, same label**. **The weight limb stays
  ANSWERED-NEGATIVE.**
- **H2 — a NON-instance, and the cleanest confirmation of the 10-28 mechanism.**
  `MODERATE` fuel (ratio 1.21) and **below** the flip: H2's cell is
  `LOW_FUEL`/`EXHAUSTED` ∩ below the flip, so this is a non-instance on the fuel
  axis. **Census stays 6–2 / 8–0.** Critically, **the two-opposite-instructions
  contradiction did NOT fire**: §2 says *"Sweeps tend to keep running rather than
  fail. Fading is the wrong trade today — Strategy 2"* and §3 says *"Continuation
  is fine to the nearest pool; don't plan on a third leg"* — **they agree**. The
  10-28 review's mechanism (*the fuel prose is inverted by state, the gamma prose
  is not conditioned on fuel at all, so they contradict at both ends of the fuel
  scale and agree in the middle*) predicted exactly this. **n=1 control in the
  MODERATE cell, and it matches.** The 10-30 scan (`LOW_FUEL`, below the flip,
  fade instruction printed) **is** a cell instance and must be graded as one.
- **H9 — observation 2, and the verdict flips with the window.** AMZN, a same-day
  index-defining earnings event, with `COHERENT_SHORT` saying *"expect range
  expansion… today's ADR can be exceeded"*. Last-bar basis: range **1.199× ADR**
  → **expansion, H9 CONTRADICTED**. Cash-close basis: **0.678× ADR** →
  **contained, H9 SUPPORTED**. n=2 against a threshold of 3. **Nothing proposed.**
- **H1 / P4 — n=31, error +112.4, and the EIGHTH value under one series name.**
  Budget 257.8 vs extension 370.2 → **+112.4** (ext − budget, the register's
  sign). From source the per-day mean is **+48.2 at n=31**, against the
  register's **46.4 at n=31** yesterday and 51.4 / 52.1 / 53.9 and two earlier
  values. **Different membership under one name. FLAGGED, not averaged.** The
  *"about right"* grade is again **bought by the post-close hour**: to 19:55Z the
  extension was **75.6 against a 257.8 budget, a 3.4× over-read**. Same shape as
  10-28's 12× over-read. **n=2 — below three, nothing proposed.** P4 is already
  ANSWERED-NEGATIVE, so there is no model change available in any case.
- **D26 — the sample moved again and it is now eating three separate figures.**
  `2026-09-14` has **aged out of the 45-day window entirely** (it was the
  *"day not finished / 97 bars"* entry yesterday; an independent fetch today
  returns **no 09-14 bars at all**). **Visible from source: 31 finished trading
  days. On disk: 44 journal directories, 43 of them finished** (08-23 … 10-29;
  10-30 live) — the 10-28 review's on-disk figure was 42/41, so the two series
  differ by one as well as by the day added. **Eleven finished days (08-23 …
  09-12) now sit past the 45-day bar window**, and 09-24 is excluded by hand on
  top of that, leaving **31** in every statistic. The ageing-out
  is what moved H26's ≥10 bucket (3/7 → 3/6), P-H's deciding set (n=5 → n=4) and
  P4's mean (46.4 → 48.2) in a single session. **Reported as separate numbers;
  nothing averaged.**
- **D27 — 401 on `/v2/NDX/classic/gex_full` for a 7th consecutive day**
  (`2026-10-29/1248-preny.md:146`-family render and again on the 10-30 scan).
  Volume-weighted ladder lost again, so **H12/H13 are untestable** and **D25
  stays interrupted at 29**. **Nothing proposed** — no credential change, no
  retry policy.
- **D23 / realised-basis log — observation 12, and it is a record outlier with a
  known cause.** §7 is **absent from the 10-29 brief** (sections 1–6 only,
  confirmed) and has not rendered since 10-21, so **no residual is inferable**.
  Basis arithmetic from the scan's own figures: NDX reference **29423.9** =
  cash close 10-28 + NQ roll **−389.2** → cash close 10-28 = **29813.1**; CFD
  close 10-28 (= 10-29's `PD close`) **29590.9**; **gap +222.2** against 10-28's
  ordinary **+9.4**. The gap is **entirely the 10-28 post-cash-close collapse** —
  the CFD fell 246.6 after NDX cash printed its last trade. A third register
  measurement distorted by the same hour.
- **H8 — post-closure, and OUTSIDE by 21.5.** Band **29091 .. 29836** (ATM
  straddle 438, IV 25.6%); close **29069.5**. **Inside on the cash-close basis
  (29423.5).** Expected move ±373 vs realised post-scan 393.7 — beaten by 20.7.
- **H22 — n=16, label RIGHT** (−5.001 → *"expansion likely"* → 1.199× ADR). The
  **VXN-implied 441.4**, which §3 told the reader to prefer as the smaller
  budget, was **beaten by 236.9** — the **5th** counter-instance to the
  VXN-implied budget.
- **H4 — no instance.** Flip 29941.3 never reached (478 away).
- **H10 — clean CONTROL.** Price inside the prior-week range (28820.4–29936.0),
  `structure +0`, no branch fired; PWL 28820.4 was never approached (low 143.9
  above it). Stays **2-for-8**. *(The 10-30 scan fires the −3 branch — price
  below the entire prior-week range — so it is a firing to grade next time.)*
- **H17 — no instance.** Post-scan move **58.0%** of the session range, far
  outside the 5% deadband. Stays **2 of 3**. (Cash basis: 5.9%, marginal.)
- **H23 — a NON-instance on the brake branch, and a corridor data point.** §3
  named **no** brake on either side (both paths printed *"clear"*). Slice census
  stays **15/3/3**. The downside corridor terminus **28889.3** was approached to
  within **75.1** and not reached; the corridor read was directionally correct.
- **D21 / `gamma +2` bottom-of-band — NOT a firing, a control.** 10-29's row is
  `gamma +0 — price mid-band (29089.3–29639.3), 68% up the range`; band width
  **550.0 = 0.97× ADR**. Branch stays **6 firings, census 3–3**.
- **P-E / P-E(b) — instances 19 and 20.** All six secondary strikes printed the
  same *"amplify, accelerate THROUGH, not a floor"* text; four were traded
  through and none stalled anything. Correct, and **undiscriminating** — the
  shelves again did not separate outcomes. The call wall (0.28bn) was never
  reached.
- **P-G — instance #36.** `29650.8 Asia Low (prev-day)`, **+188 ABOVE price**,
  printed *"the next session usually runs the stops **below** it"*. Same mirror
  as #14/#15/#24/#25/#33/#35.
- **P-G family, a distinct shape worth naming — n=1, not opened.** The
  `29521.7 PDL` row printed *"Sweep it, wait for a higher low on the 1m, then
  **CISD = long**"* on a page whose §1 said *"**STRATEGY 2** — continuation"* and
  whose §2 said *"**Fading is the wrong trade today**"*. The level text is chosen
  by level **kind** and is unconditional on the regime, exactly P-G's mechanism,
  but it is a **strategy instruction** rather than a stop-side description.
  Recorded; **not opened** (one instance is not a hypothesis).
- **P-B(b) — 23rd session, and it REVERSES 10-28's clean negative.** **Two**
  guaranteed double-count windows (`29590.9 / 29586.1 = 4.8`;
  `29403.8 / 29396.9 = 6.9`, both inside `TOUCH_TOL = 8.0`) and **one of them was
  realised** — both rows touched at the same bar and graded identically.
  Published hit rate **0.294 → 0.250** deduplicated. **The first live
  double-count the item has caught in several sessions.**
- **`TOUCH_TOL = 8.0` — a candidate instance, recorded with its number.** The
  nearest untouched row to a post-scan extreme was `29577.7 Equal highs ×2`,
  missed by **19.4** against a post-scan high of 29558.3 — **2.4×** the
  tolerance. On the 10-23 (31.4) and 10-26 (12.8) precedent values this is the
  same shape, which would make **n=3**; the entry's criterion is not written as a
  numeric threshold, so the figure is filed and **nothing is proposed**.
- **Session-context field — 23rd session.** **9 of 17** published rows (29639.3
  down to 29334.6) sat inside the pre-scan range **29334.6–29642.7**, i.e. price
  had already traded them today, and no field says so.
- **D7 — both truncation limbs CLEAN, 4th consecutive control.** Budget 257.8;
  footnote held **5 rows against a cap of 6**, so nothing was dropped by price or
  by distance, and every wall shipped. *(The budget-demotion observation about
  29136 is in §2 and is a different shape.)*
- **P-F — treatment candidate on one limb, control on the other; not scored.**
  Price at the scan was **OUTSIDE the prior-day range**, 58.5 **below PDL**
  (PDH 30023.6 / PDL 29521.7) — a treatment candidate — and **INSIDE the
  prior-week range** (28820.4–29936.0) — a control. Exactly 10-28's ambiguity
  with the signs reversed. The PD-vs-PW definition decides which arm this lands
  in, and choosing it after seeing the outcome would contaminate the control.
  **Logged ambiguous; no control figure quoted.** Error for the record: **+112.4**.
- **The gamma-outvoted cell — NO instance.** `gamma −5` was the largest block and
  the published call followed it. **Stays n=5.**
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26 — not re-opened) ·
  **H5** · **H6** (no structural touch) · **H7** (no overnight scan) · **H11** ·
  **H12/H13** (volume ladder lost to the 401) · **H20** (CLOSED-NEGATIVE) ·
  **D5** · **D24** (`event_gate: null` correct; `events_24h` **populated**, which
  is the control D28 needed and which 10-28's outage lacked) · **D28** (no
  missing-calendar render; harm count unchanged at 2 of 6) ·
  **`PIN_THEN_EXPAND`** (CLOSED, FALSIFIED 3 of 3; **P-I** is the live proposal
  and nothing here re-opens it).

**8 — Is a new data point needed? No.**
Everything that decided 10-29 was already on the page or already in the
pipeline. The **AMZN after-hours print** that produced 89.9% of the graded move
was **printed in §5 and scored `events +0`** — that is a scoring question inside
the dead-weight audit and **P-C**, not a missing feed. The **GDP/PCE release**
reached the brief through the existing news pipeline and was scored. The
**FRED staleness** is H18/P1 and needs no new source — it needs the age the
brief already prints to be read. **No external source is proposed.** The one
thing genuinely absent is a **same-day after-hours earnings-reaction tape**, and
it is **not** proposed: it is not free and reliable at the 12:48Z scan time,
because the event it would measure has not happened yet.

---

## Carried forward from the 2026-10-30 scan — recorded, NOT graded

- **⚠️ LATE TRIGGER, SECOND OCCURRENCE. Pre-registered exclusion.** The trigger
  fired at **13:16Z against 12:45Z** — **32 minutes late** — so the scan ran at
  **13:17Z/13:18Z with NY cash 11–12 minutes away**, against a normal ~12:48Z.
  **10-30 must be EXCLUDED from every pre-scan-keyed statistic when it is
  graded** (fuel ratio, `adr_used_pct`, range-at-scan, board offset, and the
  session-context count), exactly as 10-27 was. **This is the second occurrence,
  so the late-trigger exclusion is now a recurring category rather than a
  one-off** and should be given a named counter rather than re-derived each time.
- **`STRONGLY BEARISH −13` at 28634.2** after an **829pt overnight drop**; flip
  **30070.5** (1436.3 below it), week net GEX **−7.744**, `COHERENT_SHORT`,
  `LOW_FUEL` ratio **1.42**, budget 171.7, ADR14 592.0, 71.0% used. Offset
  **18.7**, clean.
- **H19 repeats immediately — back-to-back large instances.** 4 auto-scored
  headlines, raw **−6.80 → −3**, and again **two events**: three are the same
  Amazon/Intel earnings story, one is the Google/BBC ad-sales story.
- **The expected-move block printed *"the next 3 sessions"*, ±557pts, off the
  **2026-11-02** straddle** (655pts, ATM IV 15.8%) because there is no 10-30
  expiry. **That is correct behaviour and must not be graded as a daily band.**
  Checked: **H8 is the only census that consumes this figure, it is CLOSED
  (ANSWERED-POSITIVE, 8 of 10), and no open entry treats it as a daily number** —
  so nothing is currently mis-counting it. The risk is a future reviewer doing
  so; flagged here for that reason.
- **The CALL WALL printed at `●○○○○ 0.01bn, 1934pts away` (30568.7)** — there is
  effectively **no ceiling on the board at all**. Record the force and the
  distance when it is graded.
- **The `gamma +2` bottom-of-band branch FIRED — 7th firing — on a 2100.0-point
  band** (28468.7–30568.7 = **3.55× ADR14**) with price **7.9%** up it. The band
  width is the thing to note: a +2 "poor risk/reward for shorts" vote derived
  from a band 3.5 ADRs wide. Census stands at 3–3 before this firing.
- **H2 — 10-30 IS a cell instance**: `LOW_FUEL` **and** below the flip, with the
  fade instruction printed. Grade it as one.
- **H10 — the −3 branch FIRED** (*price is BELOW the entire prior-week range;
  PWL 28820.4 is now resistance*). 10-29 was a control; 10-30 is a firing.
- **`events_24h` populated; `gexbot` 401 again (7th); no §7 again.**

## Journal hygiene

One scan file for 10-29 (`1248-preny.json` + `.md`), `is_trading_day: true`,
**276 bars**, `review_day` reports **0 test artefacts**. **09-24 quarantined by
hand — 24th consecutive review to carry it**; there is still no schema
`quarantine` field and the 09-29 proposal for one is reaffirmed.
**2026-10-13 has no journal directory — documented, not recreated.**
**2026-08-23, 09-09 and 09-25 still have no `REVIEW.md`; none was created and
nothing was back-dated.** **2026-10-30 is on disk, `is_trading_day: true`,
correctly held back and NOT graded.** No fabricated or backfilled entries found.
**No `prediction` block was touched. No scoring, wall or grading code was
edited. No ID was allocated. Next free: H28 · D29 · P-J**, confirmed by
`grep -n "^## "` before writing.

**`track.py` did not complete.** Three runs (one piped, two redirected, the last
unbuffered) produced **zero bytes** over more than 25 minutes; two were killed by
the harness at exit 143/144. Every census figure in this review was therefore
derived **from source** — the journal JSONs plus a single 45-day `M_5` fetch —
using the method that **reproduces the 10-28 review's figures exactly** (10-28
post-close share 53.0%; the P-H deciding set 09-29 / 09-30 / 10-28; the H26 6–9
bucket 5 of 9). That reproduction is the only warrant offered for the
from-source numbers, and every one of them is reported **alongside** the
register's carried value rather than replacing it. `track.py` prints **no
literal `actionable: YES/NO`** in any case — the 3-session rule was applied **by
hand, per entry**.
