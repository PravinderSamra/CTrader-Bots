# REVIEW — 2026-10-30 (Friday)

_Written 2026-11-02 after the 11-02 brief was delivered. Nothing here blocked,
delayed or altered that brief. One scan graded: `1318-preny.json` + `.md`,
`PRE_NY` 13:18:33Z, `is_trading_day: true`, 275 bars, **0 test artefacts**.
No `prediction` block was touched; no scoring, wall or grading code was edited._

**⚠️ Two comparability facts govern every number below. Read them first.**

1. **The 10-30 trigger fired 32 minutes late** (13:16Z against a 12:45Z
   schedule); the scan ran at **13:18:33Z with NY cash 11 minutes away** instead
   of the usual ~42. **10-30 is EXCLUDED from every pre-scan-keyed statistic**,
   exactly as 10-27 was, under the exclusion the 10-30 scan's own carry-forward
   pre-registered. The excluded set, per the 10-28 precedent, is **P-B(b)'s
   denominator, the session-context field census, and pre-scan sweep/
   contamination counts**. Direction, level grading, fuel error, M6, P5, P-E/
   P-E(b), P-G, H2, H22, H26, H18/P1, P-H, H23, D7, D23/D25/D26/D27/D28 and the
   dead-weight audit are graded normally, **which is the precedent, not my
   judgement** — and §3 below records why the fuel limb of that precedent is
   open to challenge. **This is the SECOND late trigger, so it is a recurring
   category; it is given a named counter below (D29) rather than re-derived a
   third time.**
2. **From 2026-11-02 the daily scan is no longer a PRE_NY scan.** US clocks went
   back on 11-01; the Routine still fires at 12:45 UTC, which is now 07:48 ET
   and lands in **LONDON**. See §4 / **D29**. It does not change 10-30's grade;
   it changes what 10-30 is the last of.

**`track.py` DID NOT COMPLETE — 5th failed run, 2nd by me.** `timeout 200
python3 -u track.py`, exit **124**, **zero bytes on both stdout and stderr**.
Every census figure here is therefore derived **FROM SOURCE** (the journal JSONs
plus a single 45-day `M_5` fetch: 8539 bars, 2026-09-18 → 2026-11-02) and is
reported **alongside** the register's carried value, never replacing it. The
3-session rule was applied **by hand, per entry**. `track.py` does emit an
`actionable` key (`n_days >= MIN_SESSIONS`, `track.py:187`) but it is a global
day-count gate, not a per-hypothesis verdict — and it emitted nothing today.

---

## 1. Scoreboard

**Call:** `STRONGLY BEARISH −13` at **28634.2** · direction **−1** · shape
`COHERENT_SHORT` (0DTE −4.786 / week −7.744 / 45-day −11.323 $bn per 1%) · fuel
`LOW_FUEL` · budget **171.7** · ADR14 **592.0** · `adr_used_pct` **71.0** ·
`fuel_ratio` **1.42** · offset **18.7** (clean) · `event_gate: None`.

| | value |
|---|---|
| Session O / H / L / C | **29014.9 / 29028.2 / 28084.6 / 28379.8** |
| Range | **943.6** (**1.594× ADR14**) |
| Net move | **−635.1** |
| Post-scan move | **−261.1** (`review_day`, `fwd[0].open` anchor) · **−254.4** (`price_at_scan` anchor) |
| Direction, post-scan basis | **CORRECT** |
| Direction, day-net basis | **CORRECT** |
| Levels published / touched | **9 / 3** → hit rate **0.333** |
| Range extension vs budget | 523.3 vs 171.7 = **3.05×** → `fuel_call: "UNDER-estimated"` |
| Price traversal vs budget | 626.9 = **3.65×** |
| \|post-scan\| / ADR | **0.441** |
| Fuel error (extension − budget) | **+351.6** |

**The windows, because the last two sessions were decided inside one of them:**

| window (UTC) | O | H | L | C | range | net |
|---|---|---|---|---|---|---|
| day start → 19:55 (to the cash close) | 29014.9 | 29028.2 | 28084.6 | 28381.4 | 943.6 | −633.5 |
| **20:00 → 20:50 (post-close)** | 28381.7 | 28436.1 | 28374.4 | 28379.8 | **61.7** | **−1.9** |

**The post-close hour supplied 6.5% of the range and 0.3% of the net move.**
After 10-28 (53.0%) and 10-29 (43.4%) this is a **clean counter-instance**: the
post-close distortion stays at **n=2** and is not a pattern. 10-30 was decided in
cash hours — a monotone grind 13:30→18:50Z, then a +296 last-hour bounce.
**AAPL reports after the 11-02 close, so 11-02 may still be a third instance.**

---

## 2. What the levels actually did

**Touched — 3 rows.**

| level | dist | published expectation | what happened |
|---|---|---|---|
| **28675.2 Asia Low (today)** | **+41** | *"the next session usually runs the stops below it"* | **The stops below it had already gone** — the pre-scan low was 28607.9, 67.3 lower, set in London. Price poked **+36.3** back above it at 13:55Z, then fell and **closed 295.4 below**. Grader prints *"broke **UP** through it — lost by 34.5pts"*. |
| **28607.9 London Low (today)** | −26 | *"runs the stops below it"* | Ran. Settled below from 15:05, **held as resistance 345 min, worst +17.4**, closed **228.1 below**. **Behaved exactly as published** — the day's best-behaved liquidity row. |
| **28468.7 PUT WALL ●●●●● 0.65bn** | −166 | *"if it breaks, expect it to **speed UP, not bounce**. Don't buy the break."* | Contact 14:20Z, then **2h20m of chop around it** — price traded back to **28685.6, 216.9 ABOVE the wall** — before losing it for good at 16:45Z. It then ran **384.1 = 0.649× ADR** to 28084.6 at 18:50Z, and **bounced 351.5** in 65 minutes to 28436.1, closing **88.9 below** and never reclaiming it. 70k contracts this week / 128k on the 45-day. |

**The put-wall rider (H14), graded clause by clause — and it SPLITS, where on
10-29 it was wrong on both.** *"Speed up, not bounce"* is **wrong on first
contact** (2h20m of chop, +216.9 of adverse travel) and **right on the sustained
break** (384.1 = 0.649× ADR, the largest run-through in the 6-instance series).
*"Don't buy the break"* is **right at the wall** (a buy at 28468.7 was 384.1
underwater) and **wrong at the extreme** (+351.5 off the low in 65 minutes).
**The rider has no concept of WHICH break it is talking about.** That is the
first time the series has separated the two breaks, and it is the mechanism the
entry has been missing — n=1 as a stated mechanism, so nothing is proposed.

**Untouched — 6 rows, every one of them above price**, on a day the brief called
`STRONGLY BEARISH` with 171.7 points of budget left:

| level | dist | ×ADR |
|---|---|---|
| CALL WALL ●○○○○ 0.01bn | +1934 | 3.27× |
| GAMMA FLIP | +1436 | 2.43× |
| STRUCTURAL CALL WALL ●●●●● 0.82bn | +1084 | 1.83× |
| Asia High (prev-day) + MAX PAIN ⭐ | +985 | 1.66× |
| London High (today) | +226 | 0.38× |
| PWL | +186 | 0.31× |

- **The hit rate 0.333 is close to meaningless.** Four of the nine rows sit
  1.66×–3.27× ADR away and were unreachable **on the brief's own forecast**. The
  gradeable board was five rows; three of those were touched.
- **The CALL WALL is a non-level and the brief said so by accident.** ●○○○○
  **0.01bn at +1934** is the weakest wall ever published on this board, and its
  note still reads *"Heaviest ceiling this week (36k contracts) — desks must SELL
  as price rises into it, so rallies stall."* Thirty-six thousand contracts
  producing 0.01bn of force is the exact case the board's own header text warns
  about (*"Not contract count: a far-away wall can hold 24x the contracts and
  still push price less"*), and the note contradicts the header. **There was no
  ceiling on the board at all, and nothing in §4 said so.** n=1; recorded.
- **PWL +186 — the proximity-gap shape again.** `structure −3` named PWL 28820.4
  as flipped resistance and the board repeated it. Price never came within
  **108.9** of it. The penalty was right about direction and the level it names
  was never tested. Same shape as 10-07 / 10-22 / 10-23.
- **MAX PAIN merged with Asia High (prev-day) at +985 = 1.66× ADR.**
  Hopelessly distance-confounded, therefore **UNTESTABLE**. The clean census
  stays **1–2 at n=3** and the day-of-week clause (*"strong by Thursday/
  Friday"*) **does NOT take a Friday miss** — grading a level 1.66× ADR away as
  a miss would manufacture the data point that triggers its deletion.
- **P5 — the secondary gamma table is 3 of 3.** Rows at **−16, −116 and −366**
  all claimed *"dealers are SHORT gamma here, so they amplify: price tends to
  accelerate THROUGH rather than stall. Not a floor"* and **all three were
  sliced** (price reached 28084.6, 184.1 below the deepest of them). The +284
  row was never reached. **The day's best level was the PUT WALL on the MAIN
  board** (255 min as resistance), so the *"best level is in the secondary
  table"* streak stays **broken**.
- **D7, second limb — INSTANCE 2, and it is the same row as instance 1.** The
  footnote printed **6 rows at its cap of 6**, selected by descending **price**
  (`brief.py:373` sorts, `far_line(cap=6)` truncates): +701 to +1302 away.
  **PDL 28964.4, at +330, named by the brief's own `structure −1` row, appears
  neither on the board nor in the footnote** — and nor does PD mid 29303.6
  (+669), also named by that row. On 10-23 the dropped row was **also the PDL**
  (29550.0 at +189). Two instances, both PDL, **n=2 → nothing proposed.**
- **P-G instance #36.** *"Asia Low (today) — the next session usually runs the
  stops below it"* printed for a level **above** price whose sell-stops London
  had already taken. The note is chosen by level **kind**, not by which side
  price is on. This is the cleanest instance in the series: not merely
  side-inappropriate but **describing an event that had already happened.**
- **M6 — session 36. 2 of 3 touched rows carry inverted wording.** Asia Low:
  *"broke **UP** through it"* for a row price closed **295.4 below**. PUT WALL:
  `first_touch_reaction` *"broke **UP** through it"* for the day's defining
  breakdown. Asia Low's *"lost"* verdict is produced by the **`settled_read`
  origin defect already recorded at ~5535 / ~6061 / ~7054** — its settle window
  opens at **13:55**, the exact bar that set the post-scan high 36.3 above the
  level, so the 34.5 "worst excursion" that exceeds `SETTLE_TOL = 25.0` **is the
  window's own first bar**. Not reopened. **The driver of the M6 series remains
  UNKNOWN** — travel-scaling is dead at four consecutive failures, window
  placement at 7 of 7.
- `TOUCH_TOL = 8.0` — **checked, 10-30 is NOT an instance.** Nearest untouched
  row (PWL) missed by **108.9**, 13.6× the tolerance. Stays at **n=2**.
- **P-B(b) — denominator NOT advanced** (late-trigger exclusion), stays at
  **23 sessions**. Recorded observed-and-excluded so a later reviewer does not
  "find" it again: the board held **zero** guaranteed double-count windows, the
  closest pair being **28859.8 / 28820.4, 39.4 apart**, 4.9× `TOUCH_TOL`.
- **Session-context field census — NOT advanced**, stays at **22 sessions**.
- **P3/H6 — no structural touch** (the structural call wall was +1084 away), so
  no new instance and the standing *"stop publishing it"* narrowing **stays
  blocked** at 1 clean touch / 1 confounded.
- **P-E / P-E(b) — no instance.** Both concern capping on the **upside**; price
  never traded more than 77.3 above the scan.
- **H23 — no named brake on either side**, so the **clear-path read** is graded
  instead, n=2 → **n=3, and it SPLITS again**. Downside: *"every shelf from here
  to 28018.7 (616pts, 1.04× ADR) is negative gamma — nothing structural to slow
  a breakdown"* → **RIGHT**, price ran **549.6** of the stated 616 and stopped
  **66.1 short** of the terminus with nothing braking it. Upside: *"clear to
  29318.7"* → **UNTESTED**. Census: 2 right / 0 wrong / 1 untested on the
  downside limb; the upside limb has never been testable on a below-flip day.

---

## 3. What was wrong, and why

**The direction call was right on both bases, so every finding here is about how
−13 was built, not about its sign.** Six of the seven blocks pointed bearish and
the day fell 635. That is the easy part. The register's job is the rest.

### (a) `news −3` is a match-count artefact — H19, and the caller's premise is wrong

Four auto-scored headlines, **two events**:

| event | headlines | rule | mag | freshness | weight |
|---|---|---|---|---|---|
| Amazon / Intel earnings | *"Nasdaq futures fall more than 2% as Amazon and Intel tumble after earnings"* · *"Stock Market Today: Nasdaq Futures Dive As Amazon, Intel Plunge On Earnings"* · *"Nasdaq-100 futures fall 2% as Amazon and Intel tumble after earnings - CNB"* | `earnings_miss` | 170 | 1.0 | −1.70 ×3 |
| Google / BBC ad sales | *"Google value plunges by $500bn as its own AI search hits ad sales - BBC"* | `earnings_miss` | 170 | 1.0 | −1.70 |
| | | | | **sum** | **−6.80** ✓ |

- **Published:** `round(−6.80 / 2) = −3`. **Not at the cap** (unlike 10-29).
- **One vote per event:** −1.70 + −1.70 = −3.40 → `round(−3.40 / 2) = −2`.
  **Over-count: 1 point.**
- **Sign: RIGHT.** Both events bearish, the day fell 635.1.
- **Verdict effect: ZERO.** News −2 → score **−12** → still `STRONGLY BEARISH`
  (`bias_engine.py:270`, ≤ −10), still direction −1, still CORRECT, still H26's
  **≥10** bucket.

**THRESHOLD NOT MET. NOTHING PROPOSED — and the count in the task I was given is
one session too high.** The pre-registration (recorded 10-29) requires **3 graded
sessions** in which (i) ≥2 auto-scored headlines collapse to one event **and**
(ii) the one-vote-per-event score differs from the published block by ≥1 point.
**10-28 fails clause (i)** — 2 headlines, 2 distinct events, explicitly recorded
as *"no match-count inflation today"* — so it is not in the sample. The
qualifying graded sessions are **10-29** (differs by 2) and **10-30** (differs by
1): **n=2, not n=3.** One more is needed. I am not widening the clause after
seeing the data.

### (b) The news block scored an event that was already in the price — and scored it three times

This is the finding with the most teeth and it is **not** H19.

The Amazon/Intel earnings printed **after the 10-29 cash close**. By the 13:18Z
scan the market had already moved: an **829-point overnight drop**, **420.3 of
range = 71.0% of ADR14 spent before the scan**, and price **below the entire
prior-week range**. All four headlines carry **freshness 1.0** on a rule with a
printed **180-minute half-life**, for an event roughly **17 hours old**.
**`news_scorer.py` ages the HEADLINE, not the EVENT.**

The same event is then counted again elsewhere in the score: `structure −3`
(*"price is BELOW the entire prior-week range"*) and `breadth −1` (*"NDX −1.38%
vs ES −1.12%"*) are both **consequences of that earnings print**, not independent
evidence about what happens next. So of the −13, **−7 is one Thursday-night
earnings report read three times.**

This is **adjacent to H27 but not covered by it.** H27's measured pairs are
`vol ↔ breadth` (+0.533) and `structure ↔ gamma` (+0.555), with every other pair
at |r| ≤ 0.22 — `news ↔ structure` is not a general correlation, it is a
**same-event** double count on this particular day. **n=1 as a measured claim.
Observed, not proposed, and no number taken** — the mechanism (`news` scores a
stale event at full weight) is a `news_scorer.py` freshness question, and I am
not opening a defect for it on one session when the alternative reading (the
market was still repricing at 09:18 ET, and it was — another 635 points of it)
cannot be ruled out from one day.

### (c) The engine held three readings of the 10-year and resolved them 4–3 for the stale pair

| row | instrument | as of | points |
|---|---|---|---|
| `rates +3` | US10y 4.935%, **−1.08% today** | live | **+3** |
| `macro −3` | DFII10 real 10y, +3bp | **2026-10-28** (2 business days stale) | −3 |
| `macro −1` | DGS10 nominal 10y, +6bp | **2026-10-27 → 10-28** | −1 |

Net **−1 on the 10-year**, from one instrument, and **the only fresh reading of
it was the one that lost.** This is **H18 / P1 instance 29, duplication 34 of
34** — and it is the **first session in the series where the stale FRED pair and
the live rate row point in OPPOSITE directions**, so the duplication is not just
double-weighting a correct signal, it is **outvoting the current price of the
thing it is measuring**. The brief printed the staleness warning in full
(*"⚠️ FRED has not published since 2026-10-28"*) and nothing read it. **P1's
RENDERING proposal is unchanged and no weight change is proposed** — note that
the fresh row was **wrong** today (yields fell, tech fell 635), so "trust the
fresh one" is not supported either.

### (d) `gamma +2` bottom-of-band — 7th firing, on the widest band in the record, and WRONG

| day | price | put wall | band | % up band | *"bottom 20%"* window | ×ADR | outcome |
|---|---|---|---|---|---|---|---|
| 08-24 | 29132.8 | 29110.2 | 200pt | 11% | 40pt | 0.04× | WRONG |
| 09-14 | 28830.7 | 28787.8 | 500pt | 9% | 100pt | — | RIGHT |
| 10-07 | 31031.7 | 31025.8 | 200pt | 3% | 40pt | — | RIGHT |
| 10-12 | 30843.5 | 30843.1 | 500pt | 0.08% | 100pt | — | WRONG |
| 10-22 | 29361.0 | 29115.7 | 1300pt | 18.9% | 260pt | 0.50× | WRONG |
| 10-23 | 28875.7 | 28789.0 | 600pt | 14.5% | 120pt | 0.22× | RIGHT |
| **10-30** | **28634.2** | **28468.7** | **2100pt** | **7.9%** | **420pt** | **0.71×** | **WRONG** |

**Census 3–3 → 3 right / 4 wrong.** The row said *"poor risk/reward for
shorts"* with price **165.5 above the put wall**; shorts then made another
**549.6**, and price finished **384.1 BELOW the band's own floor**.

**D21's width defect at a new extreme.** The band was **2100.0 points = 3.55×
ADR14**, so *"the bottom 20%"* is a **420-point = 0.71× ADR trigger window** —
price can sit two-thirds of an average day above the put wall and still score
*"poor risk/reward for shorts"*. Width instances now number **three** (09-18
0.04×, 10-22 0.50×, 10-30 0.71×), which is three sessions. **It is still NOT
proposed, for D21's own standing reason**: the only evidence that a normalised
version performs better is the absolute-distance re-cut, which was found **after**
looking at outcomes, and re-using it now would be fitting to the same data twice.
**What a clean test needs, pre-registered here:** write the normalised threshold
(e.g. *"within 0.15× ADR of the put wall"*) down **before** the next firing, then
collect three firings under it. Nothing else will settle this.

**Prose contradiction 7 of 7.** *"Poor risk/reward for shorts"* sits three rows
above *"if it breaks, expect it to speed **UP**, not bounce. Don't buy the
break"*, §1's *"Strategy-1 fades have a materially lower hit rate here"* and §2's
*"Fading is the wrong trade today"*. **Zero sign changes in seven firings**:
−13 would have been −15, same label, same side, same verdict.

### (e) H2 — cell instance 9, graded under the rules fixed in writing, and the fade LOSES cleanly

10-30 is in the cell: `PRE_NY` · `is_trading_day` · **`LOW_FUEL`** · price
**1436.3 below the gamma flip** · the fade instruction printed (§3: *"The range
is close to done… favour fades over chasing breaks"*) against §2's *"Fading is
the wrong trade today"* and §3's own *"Do not fade it"* on both path reads.

Graded by the 10-20 rule, **unaltered**:

| step | value |
|---|---|
| pre-scan extremes | H 29028.2 / **L 28607.9** |
| first post-scan sweep | **down**, 13:30Z bar, low 28540.5 |
| engage bar (first close back inside) | 13:35Z, close 28656.4 |
| target (nearest published level inside) | **28675.2 Asia Low** |
| target on the engage bar? | **no** — high 28658.2, misses 28667.2 by 9.0 |
| swept low re-lost at | **13:40Z**, low 28581.2 |
| **result** | **FADE LOSES** (re-lost before target; no tie) |

The target was eventually touched at 13:55Z — **after** the sweep level had been
re-lost, which the rule scores a loss. Not a marginal one: a long from the engage
close went **571.8 points underwater** before the day was done.

**Census 6–2 → 7–2 to the gamma block; 9–0 if ties go against the fade.
H2's claim stays FALSIFIED and its existing proposal is unchanged.** The
two-opposite-instructions contradiction fires again **inside the LOW_FUEL
branch** — consistent with the 10-23/10-26/10-27 localisation, and a further
data point against which the 10-28 `ROOM_TO_EXPAND` breakout must be read.

### (f) H26 at −13 — a ≥10 instance, and the two censuses say different things

|post|/ADR **0.441**, range/ADR **1.594**, direction **CORRECT**.

| basis | ≥10 bucket before 10-30 | after 10-30 |
|---|---|---|
| register's carried figure | **3/7 = 42.9%** | **4/8 = 50.0%** |
| from source, 45-day bar window | **3/6 = 50.0%** | **3/6 = 50.0%** |

**Both are reported; neither is averaged; the conflict is now worse, not
better.** The from-source figure is **numerically unchanged** because **09-15
(score −12, direction RIGHT) aged out of the bar window on the same session that
10-30 (score −13, direction RIGHT) entered it**. One right day left, one right
day arrived, and the ratio stood still. That is **D26**, in its purest form: the
figure is stable for a reason that has nothing to do with evidence.

From source at **n=28** (down from n=31 on 10-30), magnitude monotonicity
**survives an 11th session**:

| bucket | n | mean \|post\|/ADR | direction (post-scan) |
|---|---|---|---|
| 0–2 | 6 | 0.207 | — (all no-call) |
| 3–5 | 7 | 0.384 | 4/7 = 57.1% |
| 6–9 | 9 | 0.524 | 5/9 = 55.6% |
| **≥10** | **6** | **0.650** | **3/6 = 50.0%** |

The magnitude ladder is clean. **The direction ladder is still inverted at the
top** — the most confident bucket is the worst direction bucket, and the
*"inverted at the top"* claim stays **SUSPENDED** as recorded, because the ≥10
cell holds six observations and its composition changes every week. No Spearman
is quoted; its derivation is still unwritten (the 10-20 correction).

### (g) H27 — observation 6, and it is the WEAKEST instance in the series

| | 10-23 | 10-26 | 10-27 | 10-28 | 10-29 | **10-30** |
|---|---|---|---|---|---|---|
| vol ↔ breadth | −7 | −3 | +1 | +4 | +1 | **−2** |
| structure ↔ gamma | −6 | −3 | 0 | +4 | −7 | **−6** |
| independent remainder | −3 | 0 | −4 | −2 | +1 | **−5** |
| score | −16 | −6 | −3 | +6 | −5 | **−13** |

The two correlated pairs carry **−8 of a −13** and the independent remainder is
**−5, same-signed and 38% of the score** — materially more independent content
than observations 1 (−3 of −16, inside the deadband), 2 (0 of −6) or 4/5
(opposite-signed). **This is a counter-instance to H27's founding configuration**
and it is recorded as one. The weight limb stays **ANSWERED-NEGATIVE** and
nothing is re-proposed. Note the caveat from (b): the remainder's own −8 of
macro+news is itself duplicated, just along axes H27 does not measure.

### (h) H10 — the −3 branch fired and was RIGHT

`structure −3`: *"price is BELOW the entire prior-week range (28820.4–29936.0) —
PWL 28820.4 is now resistance, not support."* Price was **186.2 below the PWL =
0.31× ADR**. **No reclaim occurred** — price never came within 108.9 of the PWL —
and the day fell 635.1. **Branch 2-for-8 → 3-for-9.** The proposed reclaim term
would have changed nothing again: there was no reclaim to detect. **Fourth
proximity-gap instance** (10-07, 10-22, 10-23, 10-30) — the rule scored 186
points below the boundary identically to 2000 points below. **Still the DISTANCE
term, not the reclaim term, that the evidence argues for, and still not proposed
without an accuracy test.**

### (i) D28 — the condition recurred, and the register's own carry-forward is WRONG about it

`inputs.events_24h` is **`null`** and §5 printed **"No High/Medium US events in
the next 24h."** — the missing-calendar state rendering as a positive factual
claim. **The 10-29 review's carry-forward block recorded this scan as
"`events_24h` populated"**. It is not. **That line is corrected here**, and with
it the 10-29 conclusion that *"the 10-28 calendar outage was transient"* — the
outage recurred on the very next scan.

**Harm is NOT demonstrated on 10-30** and is not claimed: no 45-minute window
dominated the session (largest hour 19:00Z at 287.2 of 943.6, and it was the
bounce, not a release). **D28's harm count stays 2 of N; the condition count
advances; D28 is not re-opened or re-numbered and proposes nothing new.**
**D24 is a clean control** — both earnings rows (AAPL 11-02, AMD 11-03) are
forward-dated, so the forward-only filter hid nothing.

### (j) P-F — 5th same-signed treatment instance, and the prohibited sentence printed verbatim

Price **28634.2 = 330.2 below PDL 28964.4**, far past the >150pt trigger.

| treatment day | price vs PD range | error |
|---|---|---|
| 09-14 | −187.6 below PDL | +79.4 |
| 09-17 | +174.5 above PDH | +40.0 |
| 09-21 | +259.0 above PDH | +569.2 |
| 10-22 | −189.0 below PDL | +382.7 |
| **10-30** | **−330.2 below PDL** | **+351.6** |

**5 of 5 positive, mean +284.6, median +351.6**, on both sides of the range. The
inside control is **not** re-derived this session and no control figure is
quoted. And this is the instance P-F was written for: §3 printed *"The range is
close to done. Expect price to keep MOVING but mostly **inside** the extremes
rather than making new ones — favour fades over chasing breaks"* — and the range
then extended **523.3** further, every extreme broke, and every sweep ran.
**P-F is already PROPOSED and ADVANCED as written; nothing new is proposed, and
never a multiplier** (fitted to +40 / +79 / +352 / +383 / +569 it fits the tail,
not the level — the H1 lesson).

### (k) The fuel budget, and why the exclusion precedent deserves a challenge

Budget **171.7**, extension **523.3**, **error +351.6** — the **5th largest in
the record** (behind 09-21 +569.2, 10-16 +479.3, 10-22 +382.7, 10-14 +378.8).
From source at **n=28**: mean error **+65.4**, median **+16.1**; the zero/
non-zero split that H1 established **holds** — budget = 0 mean **+235.4** (n=3)
against budget > 0 mean **+45.0** (n=25).

**This is the NINTH value reported under one series name** (the register carries
53.9 → 52.1 at n=30, then −76.1 and +112.4 at n=31; from source it is now
+65.4 at n=28). **It stays flagged, not averaged.** D26 again.

**And here is the challenge, filed rather than acted on.** The 10-28 precedent
grades fuel error normally on a late-trigger day, and I followed it. But the
budget is computed **from** `today_range` at scan time: a 32-minute-longer
pre-scan window mechanically **inflates** range-at-scan (420.3 = 71.0% of ADR)
and **deflates** the budget, which biases the error **positive** — the exact
direction 10-30 shows. Both late-trigger days now sit in the n=28 sample
(10-27 +29.4, 10-30 +351.6). **I am not re-deriving the series with them removed,
because choosing that treatment after seeing +351.6 is precisely the
contamination this register keeps catching.** The honest statement is that the
fuel limb of the exclusion precedent is **unresolved**, and from 11-02 the
problem gets worse, not better — see D29.

### (l) Housekeeping observations, no proposal attached

- **H22 — n=16 → n=17, label RIGHT.** Week net GEX **−7.744** → *"expansion
  likely"*; realised **1.594× ADR**. The **VXN-implied 454.2**, which §3 told the
  reader to prefer as the smaller budget, was **beaten by 489.4** — the **6th**
  counter-instance to the VXN-implied budget.
- **D27 — 7th consecutive gexbot 401** on `/v2/NDX/classic/gex_full`; the
  volume-weighted ladder is again absent and **H12/H13 cannot be tested**. The
  11-02 scan on disk carries an **8th**. Nothing proposed: no credential change,
  no retry policy.
- **D25 — interrupted at 29.** The brief renders §1–§6 only; there is no §7, so
  the unguarded `drift` sentence did not render for a **fourth** consecutive
  session. Its counter resumes when §7 does.
- **D23 / the realised-close-basis log — observation 13, NO residual.** §7 did
  not render and **none is inferred**. Offset **18.7**, price basis
  `nq_implied`, greeks `repriced_bs_at_current_spot`; NDX cash 1024 minutes
  stale, rolled forward by the NQ move (−787.0) to 28615.5. Recorded clean.
- **D26 — the gap has WIDENED.** From source: **29 journal trading days have a
  full bar set** (incl. 09-24, quarantined → **28 gradeable**) against **43
  finished trading-day directories on disk** — **14 invisible past the 45-day
  window**, up from the 10 reported on 10-29. **09-18 is present at 96 of 276
  bars**, the "not finished" boundary symptom, and **10-13 has 276 bars and no
  journal directory** (documented, not recreated). The concrete harms this
  session are the H26 ≥10 standstill in (f) and the ninth P4/H1 value in (k).
- **The dead-weight audit — 14 of 28 rows scored 0.** `events` **0 of 2** and
  has still never scored in its history (`bias_engine.py:259–263`), with AAPL
  earnings after the 11-02 close priced at **+0** three days before it moved the
  tape. `rates` scored on 1 of 2. **P-C** takes the `events` instance.
- **H9 — no instance** (no same-day index-defining earnings; Amazon/Intel were
  the prior evening, AAPL is 11-02).
- **H17 — no instance.** |post-scan| 261.1 = 0.441× ADR is not a deadband case.
  Stays **2 of 3**.
- **H8 — post-closure only, and the thing I was asked to check is CLEAN.** The
  expected-move block correctly printed **"the next 3 sessions"**, ±**557pts**
  (28077 .. 29191) off the **2026-11-02** straddle (655pts, ATM IV 15.8%),
  because there was no 10-30 expiry. **Re-checked against every open entry: H8
  is the only census that consumes this figure, it is CLOSED
  (ANSWERED-POSITIVE, 8 of 10), and nothing treats it as a daily band.** The
  close 28379.8 is inside it; **that fact is recorded and NOT counted.**
- **The gamma-outvoted cell — no instance.** Largest block was `macro −5` and
  gamma (−3 net) agreed with it; there was no outvote. Stays **n=5**.
- **No instance:** H3 (CLOSED-NEGATIVE, superseded by H26 — not re-opened) · H4
  (flip 1436 away, never reached) · H5 · H7 (no overnight scan) · H11 ·
  H12/H13 (volume ladder lost to the 401) · H20 (CLOSED-NEGATIVE; no events
  anyway) · D5 · D9 · D18 (see below) · D22 · `PIN_THEN_EXPAND` (CLOSED,
  FALSIFIED 3 of 3; **P-I** remains the live proposal and nothing here reopens
  it).
- **D18 — a NEAR-MISS, deliberately NOT entered, and it exposes an
  inconsistency in the entry's own counting.** *"Google value plunges by $500bn
  as its own AI search hits ad sales"* matched `earnings_miss`
  (`news_scorer.py:98`, `google … plunges`) and printed *"Mega-cap miss/warning
  -> index-weighted drag"* for a story that is **not an earnings event**. By the
  **10-29 standard** this is a near-miss, not an instance, because the printed
  **mechanism is TRUE** — Alphabet's weight did drag the index. By the **10-21
  standard** a *"category error rather than a negation one"* **was** entered as
  an instance. **Those two precedents cannot both be right, and the difference
  decides whether D18 reads 10 days or 11.** Recorded as a defect **in the
  entry's measurement definition**, not a new claim, and **not entered**: D18
  stays at **10 trading days / 17 headlines** until someone writes the criterion
  down. No number taken.

---

## 4. Change proposals

**NOTHING IS PROPOSED BY THIS REVIEW.** The 3-session rule was applied **by
hand, per entry**, because `track.py` produced zero bytes for the fifth time.
Every item above is either an existing entry taking a data point, an existing
entry reaching a threshold and resolving to *no model change*, or a correction to
something the register already says. The table, so the reasoning is auditable:

| item | state after 10-30 | why nothing is proposed |
|---|---|---|
| **H2** (fade at LOW_FUEL below flip) | instance 9; **7–2 / 9–0** to gamma | Threshold met long ago; claim **FALSIFIED**; the live proposal is unchanged. Nothing new to propose. |
| **H19** (news match-count) | **n=2** graded qualifying sessions | Pre-registration requires **3**. 10-28 fails clause (i). Not widening the clause after seeing the data. |
| **`gamma +2` band width (D21)** | 3 width instances; branch **3–4** | The only pro-normalisation evidence is a **post-hoc** re-cut. A clean threshold is pre-registered in §3(d) instead. |
| **H26 ≥10 bucket** | **4/8** carried vs **3/6** from source | Two censuses disagree and the from-source cell is 6 observations that rotate weekly. Nothing is tunable on that. |
| **H27** (block collinearity) | observation 6, a **counter-instance** | Weight limb already **ANSWERED-NEGATIVE**. |
| **D7** second limb (price-sorted footnote) | **n=2**, both PDL | One short of threshold. |
| **H14** put-wall rider | instance 6; first **split** by break-type | The "which break?" mechanism is **n=1**. |
| **news scores stale events at full weight** | **n=1** | One session; the competing reading (still repricing) cannot be excluded. |
| **CALL WALL note contradicts the board's own header** | **n=1** | One session. |
| **D18** category-vs-negation counting | **n=1** as a definition defect | It is a measurement question inside an existing entry. |
| **P-F**, **P-H**, **H10**, **H18/P1**, **P-G**, **P5**, **P3/H6**, **H22**, **H23**, **M6**, **D23**, **D25**, **D26**, **D27**, **D28**, **P-C** | data point each | All already PROPOSED-and-unactioned, CLOSED, or below threshold. |

**P-H — no 6th deciding instance.** Post-scan **−261.1** and day-net **−635.1**
agree; 10-30 is CORRECT on both bases. Carried: **14/26 vs 15/26**, deciding set
**n=5**. From source at n=22 calls: **12/22 vs 13/22**, deciding set **n=3**
(10-07, 10-15, 10-19) — **D26 has eaten two of the five deciding days**.
The **grading-window limb** stays at **n=3 split 2–1** and takes **no 4th
instance**: 10-30's verdict is identical whether the window ends at 19:55Z
(−633.5) or 20:50Z (−635.1), and the post-close hour held **6.5%** of the range
against the corrected range evidence of **2 of 31 from source**. Nothing
proposed.

### One ID allocated: **D29**

`grep -n "^## "` was run first and confirms **H28 · D29 · P-J** were all unused.
The claim was then grepped by wording — *daylight* (0 hits), *DST* (0),
*clocks* (0), *EST* (0), *session category* (0) — and by family: **M7** is
`track.py`/`review_day.py` disagreeing about which days are *gradeable*, **D26**
is the 45-day bar window eating days from the *back*, and **D1** is a fuel
measurement corrupted across the 21:00Z rollover. None of them is this. The only
prior trace anywhere in the file is a single August observation that *"early
LONDON scans still run ~1.9× light"* on the fuel axis — which is **evidence for**
the entry, not coverage of it.

**D29 — the daily scan's session category and pre-scan window length are not
constants, and every census keyed to PRE_NY silently stops accruing.**

US clocks went back on **2026-11-01**. The Routine still fires at **12:45 UTC**.
`session_context.py:33–36` keys its windows to **ET hours** (`LONDON` 3.0–8.5,
`PRE_NY` 8.5–9.5), so a fixed-UTC trigger crosses the boundary when the offset
changes:

| | under EDT | under EST |
|---|---|---|
| 12:45–12:48 UTC in ET | 08:45–08:48 | **07:45–07:48** |
| `session_window` | `PRE_NY` | **`LONDON`** |
| minutes before NY cash open | ~42 | **~101** (the 11-02 brief's own figure) |

Verified on disk: **`2026-11-02/1248-london.json`, `session_window: "LONDON"`,
`scan_et: "2026-11-02 07:48 ET (Mon)"`** — against `*-preny.json` / `PRE_NY` on
every one of the 30-plus trading-day scans before it. **10-30 is therefore the
last PRE_NY scan of the series**, and the next DST change is **2027-03-14**, so
roughly **93 trading days** of LONDON scans are coming unless the Routine time
changes.

**Consequences, recorded so no later reviewer pools them:**

1. **Every census keyed to PRE_NY stops accruing from 11-02.** That includes the
   *"33 PRE_NY `is_trading_day` scans"* H27 was derived on, **P-B(b)'s
   denominator** (23), the **session-context field census** (22), and the
   **pre-scan sweep counts**. Widening any of them to include LONDON scans is a
   **change of population, not an extra observation**, and the August
   *"LONDON scans run ~1.9× light"* note is direct evidence the two are not
   interchangeable on at least the fuel axis.
2. **No CODE is blind to today's scan — checked, and this is the good news.**
   `grep -rn "PRE_NY" --include=*.py` over the whole skill returns exactly two
   non-test hits: **`track.py:175`**, whose early-session list is
   `("ASIA", "LONDON", "PRE_NY")` and therefore **still captures** an 07:48 ET
   scan, and `session_context.py:36`, the window table itself. `review_day.py`
   reports `session_window` and never filters on it. **The exposure is entirely
   in this register's hand-maintained prose censuses.**
3. **The pre-scan window now has THREE distinct lengths in the record and they
   are not interchangeable:** the historical norm (~42 min before the open),
   the two late triggers (**10-27 ~26 min longer**, **10-30 ~32 min longer** —
   shorter pre-scan-to-open, longer pre-scan window), and **11-02 onward (~63
   min longer still, in the same direction)**. Any statistic computed on
   `today_range`, `adr_used_pct`, `fuel_ratio`, `remaining_budget`, board offset
   or pre-scan contamination is a function of this length. **D29 absorbs the
   named late-trigger counter the 10-29 block asked for** rather than taking a
   second number for the same measurement axis: **late triggers 10-27, 10-30
   (n=2); DST shift from 11-02 (n=1 and standing).**
4. **The fuel time-of-day baseline rebased CORRECTLY and that limb is sound.**
   11-02 printed *"ADR14 627.7, 37.9% used vs ~42% normal by 07:48 ET ->
   fuel_ratio 0.9"*. The expectation curve followed the clock. It is the
   **comparability of the resulting series** that breaks, not the arithmetic.

**D29 PROPOSES NOTHING.** No schedule change — **changing a Routine is the
user's to authorise and it is being reported to them separately**. No code
change. No census is widened, narrowed or re-derived here. The entry exists so
that the next reviewer who sees a LONDON scan does not append it to a PRE_NY
count, and so the third pre-scan-window length is on the record before anyone
averages across it.

### Is a new data point needed?

**No, and the one that would have helped most is not obtainable.** What decided
10-30 was an earnings reaction that printed **before** the scan — the 829-point
overnight drop was already in the price, already in `today_range`, already in
`structure −3`. Nothing was missing from the page; the same event was on it
three times (§3(b)). The one genuinely absent input is an **event-age** field for
`news_scorer.py` to age the *event* rather than the *headline* — and that is a
change to code the register already owns, **free, local, and not a new feed**.
It is **not proposed at n=1.** **No external source is proposed.**

---

## Journal hygiene

One scan file for 10-30 (`1318-preny.json` + `.md`), `is_trading_day: true`,
**275 bars**, `review_day` reports **0 test artefacts**. **09-24 quarantined by
hand — 25th consecutive review to carry it**; there is still no schema
`quarantine` field and the 09-29 proposal for one is reaffirmed. **2026-10-13 has
no journal directory — documented, not recreated** (it has 276 bars in the
window and is excluded for want of a scan, not by choice). **2026-08-23, 09-09
and 09-25 still have no `REVIEW.md`; none was created and nothing was
back-dated.** **2026-11-02 is on disk, `is_trading_day: true`, 168 bars,
correctly held back and NOT graded.** No fabricated or backfilled entries found.
**No `prediction` block was touched. No scoring, wall or grading code was
edited.** Journal census from source: **45 directories, 44 with at least one
`is_trading_day: true` scan, 39 with a `REVIEW.md`.**

**One ID allocated by this review: D29. Next free: H28 · D30 · P-J**, confirmed
by `grep -n "^## "` before writing, and the ID allocation block at the head of
`HYPOTHESES.md` has been updated in place.

**`track.py` DID NOT COMPLETE — 5th failed run across three callers.** `timeout
200 python3 -u track.py` → exit **124**, **0 bytes stdout, 0 bytes stderr**,
unbuffered, so the emptiness is real and not a pipe artefact. This is a standing
operational fact about `track.py` and belongs with **M7** when someone has the
bandwidth to diagnose it; it is recorded, not opened. Every figure in this review
labelled *from source* was derived from the journal JSONs plus one 45-day `M_5`
fetch and is reported **alongside** the register's carried value.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
