# REVIEW — 2026-10-21 (Wednesday)

Graded 2026-10-22. One scan on disk (`1248-preny`), `is_trading_day: true`,
`review_day.py` reports **0 test artefacts** for the day. Grading basis is
**post-scan** per **P-H**; the day-net figure is reported alongside it every
time the two could disagree. **09-24 excluded by hand (17th review to carry
it).** **2026-10-13 has no journal directory** — the scheduled scan never ran;
nothing was created, back-dated or inferred. No `prediction` block was touched
and no scoring, wall or grading code was edited.

---

## 1. Scoreboard

**Session (276 M5 bars):** O **29749.4** (22:00Z 10-20) · H **29936.0**
(17:20Z) · L **29550.0** (10:15Z) · C **29839.5** · range **386.0**
(**0.720x** ADR14 535.8) · day net **+90.1** · close **75.0%** up the range.

**Pre-scan window:** H 29832.5 (00:40Z) · L 29550.0 (10:15Z) · range **282.5**.

| | |
|---|---|
| Call | `BEARISH` **−7**, expected direction **−1**, price 29664.2 |
| Post-scan move (P-H basis) | **+172.7** → **WRONG** |
| Day-net move | **+90.1** → **WRONG** |
| **P-H deciding instance?** | **NO.** Both bases agree. Deciding set stays **n=5** (09-11, 09-16, 10-07, 10-15, 10-19) |
| Post-scan running | **13 / 20 = 65.0%** (was 13/19 = 68.4%) |
| Day-net running | **14 / 20 = 70.0%** (was 14/19 = 73.7%) |
| **Convention cost** | **5.0** points of headline accuracy (was 5.3) |
| Levels published / touched | **23 / 13** → hit rate **0.57** |
| Distinct touch bars | **9** (178, 180, 185, 186, 187, 188, 209, 210, 211) → distinct-event rate **9/23 = 0.391**, **inflation 1.44x** |
| Fuel | budget **253.3**, extension **103.5** → err **−149.8**, **OVER-estimated** (0.41x) |
| Post-scan traversal | **340.8** = **1.35x** the budget, **0.64x** ADR |
| Straddle band (H8, closed) | ±242 → 29422..29906; close **29839.5 INSIDE** |
| VXN-implied range | **471.3** vs realised **386.0** — VXN **over by 85.3** |
| `track.py` | 31 trading days / 34 scans (deduped) · per-day mean err **+51.9 → +45.4** (n=31, incl. 09-24) · per-scan **+46.7** (n=34) · direction **17/8/9** → **16/8/9** ex-09-24 · levels touched 0.52 |

**The shape of the day, because every judgement below depends on it.** Scan
12:48Z at 29664.2 → **down only 69.0** to 29595.2 at 13:40Z (10 minutes after
the cash open) → **up 340.8** to 29936.0 at **17:20Z** → then 215 minutes of
give-back to close 29839.5, 96.5 off the high. Price **reclaimed the gamma flip
29703.2 at 14:35Z and held above it for 380 minutes**. The down leg lasted 52
minutes and never reached the pre-scan low; the up leg lasted 3h40m.

**Not an instance of the *"whole move was over by 10:30 ET"* watch item.** That
item is at n=2 (10-19 finished 11:35 ET, 10-20 finished 10:30 ET). Today the
session high landed at **13:20 ET** and the rally ran 09:40→13:20 ET. **It is a
counter-instance; the watch item does not extend and takes no number.**

---

## 2. What the levels actually did

**10 of 23 published rows were never reached**, and nine of them are the entire
board below **−99** (29565.4 · 29550.0 · 29537.6 · 29515.4 · 29466.7 ·
29415.4 · 29395.0 · 29301.3 · 29065.4). Price went **69.0** below the scan. The
tenth was the CALL WALL at **+401**, 129.4 above the session high.

### The one that cannot be graded, and the grader graded it anyway

**STRUCTURAL CALL WALL 29665.4, published at +1.2, on a board offset of −34.6.**
The level's conversion uncertainty is **29x its published distance from price**.
The directly observable basis for the same session is **+17.0** (see §4), so the
wall's true CFD location could be ~**51.6** from where it printed — a box
spanning roughly 29665–29717, which price traversed in both directions all
morning. `review_day` reports *"stalled at it — held as support for 380min"*.
**That grade is void and must not be quoted.** This is the **third** instance of
a board level printing inside its own offset (10-12 put wall, 10-16 structural
put wall) and the **second consecutive one**. **P3 / H6's structural census
cannot take this day either** — it is the 3rd structural touch in the record and
the 2nd ungradeable one in a row.

Separately, `|px − flip| < |offset|` **stays n=1 (10-12)**: 38.6 against 34.6,
**outside by 4.0 points**, the closest approach since. The regime call was
formally determined.

### Levels whose prose the day contradicted

| level | published claim | what happened | verdict |
|---|---|---|---|
| **29721.6 PDH + NY High ⭐ (+57)** | *"the biggest pile of stops above us. Sweep it, wait for a lower high on the 1m, then CISD = **short**"* | swept, then ran **+214.4**; closed **117.9 above** | **the most actionable wrong instruction on the page** — it names an entry, and the entry was the low of the afternoon rally |
| **29730.1 Equal highs ×4 (+66)** | *"4 touches, never traded through — a real stop cluster. Prime S1 sweep trigger"* | traded through by **+205.9**, no reversal | **WRONG** |
| **29822.3 Equal highs ×4 (+158)** | same | traded through by **+113.7**, no reversal | **WRONG** |
| **29715.4 Options shelf (+51)** | *"expect price to stall… take partials rather than push through"* | **sliced by +220.6** | **WRONG** (and it is the published upside brake — see §4, H23) |
| **29815.4 Options shelf (+151)** | same | **sliced by +120.6** | **WRONG** |
| **29703.2 PD close + GAMMA FLIP ⭐ (+39)** | *"We're BELOW it: they're pushing, so don't fade"* | reclaimed 14:35Z, held 380 min, ran **+232.8** | headline half **WRONG**, conditional half **RIGHT** (below) |
| **29622.3 Asia High (prev-day) (−42)** | *"the next session usually runs the stops **above** it"* — printed while sitting **below** price | lost by 27.1, then **+313.7**; closed **217.2 above** | **P-G mirror, instance #26** — right level, wrong-sided prose |
| **29615.4 MAX PAIN (−49)** | *"price drifts toward it as the week goes on"* | **located the post-scan low to 20.2 points**, then price left it by **320.6** and closed **224.1 above** | **best-located level on the board, and its prose describes the wrong mechanism** — it was a floor, not a magnet |

### Levels the day confirmed

- **29703.2 flip, the conditional half.** *"Reclaim and hold above and they start
  damping moves again, and fading becomes valid again."* Reclaimed 14:35Z, held
  380 minutes, +232.8 of run. **This was the single best sentence on the page,
  and it is the escape clause under the call the page actually made.**
- **29832.5 Asia High (today) (+168).** *"the next session usually runs the stops
  above it"* — ran **+103.5** above. Correct and correctly sided.
- **29865.4 Options shelf (+201).** *"expect price to stall"* — held as
  resistance for 55 min, worst excursion **+6.8**, closed **25.9 below**.
  Correct; the only shelf on the board that did what shelves are advertised to do.
- **Downside path friction** (§3 of the brief): *"expect a stall at 29615.4"* —
  correct within **20.2**.

### Secondary gamma table (P5) and P-E(b)

Two rows published. **29765.4 (+101, 0.40bn)** — *"dealers are LONG gamma here,
so they damp moves: expect a stall"* — touched 14:50Z and **sliced by +170.6**:
**WRONG**. **29965.4 (+301, 0.53bn)** never reached and therefore ungraded — but
it sat **29.4 above the session high**, while the nearest *board* row above
price, 29865.4, was **70.6 below** it. **P-E(b) instance #16: the secondary
table beat the headline board on the side that mattered by 41.2 points, on the
upside this time, and it is still graded by no tool.** Census of gradeable P5
sessions: 2/3 · 2/6 · 1/6 · 2/3 · 3/5 · **0/1**.

---

## 3. What was wrong, and why

**The call was macro's call.** `macro −6` against `structure +2 · rates +1 ·
news −2 · vol −1 · breadth −1 · gamma 0 net`. Strip macro and the score is
**−1**, a no-call.

**The −6 is three rows, and two of them are one observation.**

| row | pts | vintage |
|---|---|---|
| DFII10 real yield | **−3** | **2026-10-19**, two business days stale, ⚠️ printed |
| DGS10 nominal yield | **−1** | same **10-16 → 10-19** window, **no ⚠️** |
| HY OAS | **−2** | **no observation date rendered — 16th consecutive session** |

**The sharpest instance of H18/P1 yet, and the mechanism of today's error.**
Four lines below the stale pair the same page carries `rates +1` — *"US10y
**5.094 (−0.45%)** — yields **down**, BULLISH tech."* **The live read and the
stale read describe the same instrument and disagree in sign, and the stale one
outvoted the live one 4 to 1.** Price then spent the afternoon doing what the
live row said: rallying on falling yields. This is the documented
*"opposite signs on the same instrument"* cell (09-30, 10-02, 10-05, …), and
today it decided the day.

**But the standing proposal would not have saved it, and that is the finding.**

| counterfactual | score | label | direction | verdict |
|---|---|---|---|---|
| published | **−7** | BEARISH | −1 | **WRONG** |
| suppress DGS10 when a live US10y exists (the standing H18/P1 proposal) | **−6** | BEARISH | −1 | **still WRONG** |
| headline dedup alone (§4) | **−5** | MILDLY BEARISH | −1 | **still WRONG** |
| suppress the whole stale pair (age gate) | **−3** | MILDLY BEARISH | −1 | **still WRONG** |
| dedup **and** age gate together | **−2** | NEUTRAL | 0 | no-call |

Only the **combination** of two separately-unproposed changes converts the day,
and fitting a combination to one session is precisely how the model gets worse.
**Nothing is proposed from this.**

**What was right and got outvoted.** `structure +1` *"in-reach unmitigated
pools: 4 above / 2 below — **draw higher**"* and `structure +1` *"price above PD
mid"*, plus `rates +1`. **Three rows, all correct, outvoted 8 to 3.** This is
not the `gamma outvoted` cell — **gamma netted 0 today and was not a voter at
all**, so it can be neither right nor wrong (no instance).

**News: −2 from one story, read twice, about the wrong country.**
Both auto-scored headlines are *"UK inflation rise to highest in almost a year
as Iran war drives fuel prices higher"*, carried by two outlets. Two defects
stack on one row:

1. **H19 match-count magnitude** — the score tracks how many copies arrived.
2. **D9 — the tagger reads a keyword without its subject.** The subject is
   **UK** CPI; the instrument is the **Nasdaq 100**. `cpi_hot` fired on
   inflation language with no test of whose inflation it was. **This is D9's
   second recorded instance and the first that actually scored**: D9's original
   09-10 instance fell into NEEDS_JUDGEMENT and cost nothing. **n=2, recorded,
   nothing proposed.**

**Vol −1** (*VXN/VIX 1.46, tech-specific stress*) was wrong-signed on a day tech
rallied 340.8 points. **Breadth −1** (*NDX −0.13% vs ES +0.30%, rotation out of
tech*) was wrong-signed too, and both were measured on the pre-market tape that
the cash session then reversed.

**The strategy block.** `STRATEGY 2 — continuation below the flip` with §2's
*"Fading is the wrong trade today."* The winning trade was long from 29595 —
counter to both the score and the regime instruction. **This is NOT a
*"direction right, strategy block wrong"* instance** (that cell requires the
bias score to be right; it was wrong). **That cell stays at n=2 (10-14, 10-20).**
It **is** a third below-flip `MODERATE` day on which the counter-trend trade was
the only winner, which is **deliberately not entered into H2's census** —
H2's pre-registered cell is `LOW_FUEL`/`EXHAUSTED` ∩ below the flip, 10-21 is
`MODERATE`, and `track.py`'s low-fuel list correctly omits it. **H2 stays
FALSIFIED at n=7 and its live proposal stays scoped to `LOW_FUEL`/`EXHAUSTED`.
Axis 3 is deleted, not scored.**

---

## 4. Change proposals — none. Observations appended.

**Nothing reaches threshold this session.** `track.py` no longer prints a
literal `actionable: YES/NO`; the ≥3-session rule was applied by hand to every
item below and every one of them is either an existing entry taking a data
point, an existing entry reaching a *null*, or a single observation. **No new
ID is allocated. Next free remains H27 · D27 · P-I.**

### The pre-registered `PIN_THEN_EXPAND` test — RUN AS WRITTEN, FALSIFIED, observation 2 of 3

Identical rules, identical windows, run before any narrative was attached.

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **329.5** | 194.4 | 29924.7 @16:40 | 29595.2 @13:40 |
| **post** 17:00–20:55Z | **226.1** | 51.4 | 29936.0 @17:20 | 29709.9 @19:00 |

- **Clause 2 fails.** Post range **226.1 < 329.5**. (Its *second* limb passes in
  isolation — the day closed up and the session high was set at 17:20Z, after
  the split — but clause 2 is an AND.)
- **Clause 3 fires on its first limb:** the pre window holds the larger range.
  Its second limb does **not** fire (the low was set at 10:15Z, the high at
  17:20Z). **FALSIFIED.**
- **Secondary ("breakouts will fail").** One sweep of the pre-scan high
  **29832.5** at **15:35Z**, **+33.8**; price did **not** close back inside
  within 30 minutes and went on to **+92.2** above it inside the same pre-17:00
  window. **The breakout ran — against the claim.** The pre-scan low was never
  swept (post-scan low 29595.2, **45.2 above** it).
- **Net:** 194.4 of the day's directional move happened **before** the pin was
  said to weaken; the post window gave **51.4 back**.

**Observation 2 of 3, falsified on the same clause as observation 1. Per
clause 5 no verdict attaches and nothing is proposed until observation 3.**
Recorded difference worth carrying: 10-19 failed with both extremes early;
10-21 failed with the *high* late but the *range* early — the shape's range
claim and its timing claim are coming apart in the same direction twice.

### Headline duplication — the first GRADED day, and it does not change the verdict

10-21 is the first graded day in the record on which duplicate scored headlines
are present (previously only 09-24, quarantined). Graded directly rather than
re-deriving the 10-20 table:

| basis | news pts | score | label | direction | call |
|---|---|---|---|---|---|
| published | **−2** | **−7** | BEARISH | −1 | **WRONG** |
| collapse (b), duplicate headlines → one event | **−1** | **−5** | MILDLY BEARISH | −1 | **WRONG** |

**Label changes, side does not, verdict does not.** Appended to the dedup
table's headline row: duplicate scored headlines now occur on **3 of 36** PRE_NY
scans (09-24 quarantined · 10-21 **graded, no verdict change** · and the 10-21
measurement's own note). **The headline half of the dedup measurement has now
touched one graded day and bought nothing. The weight change stays refuted**
(pair collapse 72.2% vs 68.4% published on one day's difference; dropping the
pair 65.0%, worse). The live item remains the **rendering** proposal under
**H18 / P1**.

### H18 / P1 — instance 23, duplication 28 of 28

Pair present and double-counting for the 28th consecutive scan. **HY OAS
rendered no observation date for the 16th consecutive session.** Age gate on
10-21: **−7 → −3**, a wrong call that stays wrong — **neither helped nor hurt
the verdict**; on the magnitude-respecting basis it is a **help** (conviction on
a wrong call cut from 7 to 3). Running: raw **4 helped / 3 hurt / 1 no-change**;
magnitude-respecting **4 helped / 3 hurt**. **The accuracy case stays
RETRACTED.** HY OAS is not dead weight; today it was **wrong-signed**.

### H23 — instances 16 and 17; both brakes graded, and they split

The brief named both brakes unusually close in. Both were reachable, so this is
a clean test on both sides for the first time in the series.

| brake | dist | first touch | run-through | verdict |
|---|---|---|---|---|
| **29615.4 MAX PAIN** | **−49** | 13:40Z | only **20.2** beyond, then **+320.6** | **CAPPED** |
| **29715.4 Options shelf 0.25bn** | **+51** | 13:00Z | **+220.6** beyond | **SLICED** |

Census **10/2/3 → 11 sliced / 3 capped / 3 never-reached** (n=17). The
force-ranking branch stays **CLOSED as unfalsifiable** (10-20 pre-registration)
and the corridor-terminus proposal stays **WITHDRAWN** (`brief.py:520`).
**Trap re-flagged so nobody opens a defect for it:** the board prints options
shelves at **+51 / +151 / +201** while the secondary table prints **+101 /
+301** — the two lists interleave and do not agree about which strikes exist,
because the table is built from `walls_ranked` (`brief.py:647`) and
`path_read()` reads `largest_abs_gex` (`brief.py:515`). **Different lists. Not a
skipped brake.**

### M6 — session 29, a NEW RECORD ratio, and travel-scaling fails a second time

| level | grader travel | actual excursion | ratio | grader verdict |
|---|---|---|---|---|
| **29742.1 London High** | 14.1 up | **193.9** | **13.75x** | *"broke DOWN through it — **lost** by 32.2"* |
| 29730.1 Equal highs ×4 | 26.1 up | **205.9** | 7.89x | *"**lost** by 30.3"* |
| 29703.2 PD close + flip | 33.9 up | **232.8** | 6.87x | *"**lost** by 50.1"* |
| 29622.3 Asia High (prev-day) | 133.9 up | **313.7** | 2.34x | *"**lost** by 27.1"* |

**13.75x is the largest single-row ratio in the record**, past session 28's
9.57x. All four rows closed **97.4–217.2 points above** the level the grader
says they *lost*. **4 of 13 verdicts inverted**, the highest count yet.

**Session 27's *"magnitude scales with travel"* claim fails for the second
consecutive session, and harder.** Post-scan travel was **0.64x ADR** — *below*
session 28's 0.97x and far below 10-16's 2.01x — yet the worst ratio is larger
than either. **The driver is window placement, not travel:** all four inverted
rows were first touched between **13:25Z and 13:40Z**, inside the 52-minute
morning flush, so the grader's 12-bar window closed **before** the 13:40Z
reversal. Counter-example that proves it is placement: **29715.4** has a 10.17x
up-ratio and its verdict (*"held as support"*) is **correct** — ratio size alone
does not imply inversion. **Travel-scaling is not restated as established.**

### D23 — 16th residual, SIXTH consecutive sign disagreement, and an arithmetic coincidence to flag

Board offset **−34.6** (NDX reference 29698.8 vs CFD 29664.2) vs section-7
offset **+194.1**, matched to feed time 11:59Z. Gap **−228.7**; CFD move (11:55Z
bar open **29698.8** → scan **29664.2**) = **−34.6**; **residual −194.1**.

Series: `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 /
+345.4 / −68.0 / +165.0 / +438.2 / +33.6 / −385.5 / +194.1 / **−194.1**`.

**⚠️ Flagged so no one reads meaning into it:** today's residual is the exact
negative of yesterday's, because the 11:55Z CFD bar opened at **29698.8** — the
same number, to 0.1, as the NDX reference. **That is a coincidence, not a
relationship.** Damage **none**: no volume had traded, section 7 is
research-only.

**Board offset −34.6 is NOT a breach.** The breach series stays at five
(09-28 45.9 · 10-12 43.1 · 10-14 41.8 · 10-15 77.6 · 10-20 74.5).

### The realised-close-basis log — observation 6 of 10, and 10-20's impossibility PARTLY RESOLVES

NDX cash close 10-21 = implied **29345.3** (10-22 scan) − roll (**−477.2**) =
**29822.5**; CFD close **29839.5**.

| day | scan offset | NDX close | CFD close | realised basis | gap | NQ roll |
|---|---|---|---|---|---|---|
| 10-14 | +41.8 | 29950.82 | 29931.8 | −19.0 | 60.8 | −205.2 |
| 10-15 | +77.6 | 29935.6 | 29885.3 | −50.3 | 128.0 | −389.8 |
| 10-16 | +14.9 | 29187.5 | 29191.5 | +4.0 | +10.9 | +376.0 |
| 10-19 | −3.9 | 29529.3 | 29559.4 | +30.1 | +34.0 | −187.0 |
| 10-20 | +74.5 | 29490.3 | 29703.2 | +212.9 | +138.4 | +208.5 |
| **10-21** | **−34.6** | **29822.5** | **29839.5** | **+17.0** | **+51.6** | **−477.2** |

**Observation 5's impossibility recurs, mirrored, and that is informative.**
10-20 implied NDX **−39.1** against CFD **+143.8** (a −183pt one-session
divergence); 10-21 implies NDX **+332.2** against CFD **+136.3** (a **+195.9**
divergence). **The two nearly cancel.** A wrong *roll* would not self-reverse on
the following session; a single bad **cash anchor on 10-20** produces exactly
this ± pair. That points the suspicion at the **16:14:59 cash print on 10-20**
rather than at the roll — **but it is n=2 and no mechanism is asserted.**
Re-test still at **n=10 clean observations. Nothing proposed.** The register's
roll parser remains sign-blind and **no |roll| regression may be quoted** until
it is rebuilt.

### H26 — n=27; the 6–9 bucket takes its SECOND miss

|score| **7**, |post|/ADR **0.322**, range/ADR **0.720**, **WRONG**. The 6–9
bucket goes **6/7 → 6/8**. Bucket mean |post|/ADR **0.545 → 0.517**, range/ADR
**1.193 → 1.134** — **arithmetic from the published rounded means, not a
re-derivation from source**, and flagged as such. Means stay monotonic
(0.181 / 0.254 / 0.517 / 0.783) for a 5th session. **The Spearman statistics are
NOT re-derived this session** and the signed one is **still not quoted** — the
live proposal (carry its derivation or stop printing it) remains unactioned.

### P4 / H1 — n=31 days; one new data point, and the statistic is NOT re-derived

10-21 error **−149.8** (budget **253.3**, extension **103.5**) — the
**3rd-largest over-estimate** in the record and the **2nd-largest budget** ever
published. `track.py` per-day mean **+51.9 → +45.4** (n=31, incl. 09-24);
per-scan **+46.7** (n=34). Claim stays **"no usable skill"**; multiplier branch
**closed**; **pre-scan pace carries no information and that question is CLOSED**
(today `fuel_ratio` **1.17 normal** → **0.64x ADR**, a **fourth** consecutive
uninformative reading).

**Two tempting stories checked and killed on the spot rather than proposed:**

1. *"Big budgets systematically over-read."* The eight scans with budget ≥200
   score **+114.6 · +25.9 · −75.2 · −66.5 · −180.1 · +479.3 · −17.7 · −149.8**.
   Mean **+16.3**, both tails present, no separation. **Dead.**
2. *"Use the VXN-implied range as the budget — the brief said so itself."* It
   would have cut today's error from 149.8 to 85.3. Across every VXN-implied
   reading in the register it is **over** on some days (today +85.3, 10-14
   +120.9) and **catastrophically under** on others (10-16 −405.5, 10-19
   −524.1). **Not a rule. Dead.** Logged only as the H8-family data point.

### Appended without proposal

- **H8 — ANSWERED-POSITIVE, not reopened; post-closure data only.** Straddle
  band **29422 .. 29906**, close **29839.5 INSIDE** (10-20 missed by 2.2). On
  the same page VXN-implied **471.3** **over-read** the realised **386.0** by
  85.3 — the first over-read in three sessions.
- **H22 — no re-run.** Week net GEX **+1.607 → *"pinning likely"***; realised
  range **0.720x ADR**, the **quietest day in five sessions**, so the range
  label is **right** this time — **n=13, and the first right reading in several**.
  The direction half stays **15/11 = 58% at n=26, not re-derived**. The row that
  the register measures **null on direction and non-discriminating on range**
  cast **+2** today, inside a gamma block that netted **0**.
- **Second consecutive day of score/prose contradiction in the gamma block.**
  `gamma +2 "pinning likely"` (a range claim scored as direction) sat beside
  §2's *"short gamma… Fading is the wrong trade today."* The **score said pin,
  the prose said amplify, and the day did neither cleanly**. Carried under H22,
  which owns the row; **no number taken, nothing proposed.**
- **`gamma +2` bottom-of-band branch — did NOT fire on 10-21** (`gamma +0`,
  price **60% up the band**, the same near-miss value as 10-20, two sessions
  running 20 points under the D21 threshold). **It fired on the 10-22 scan — 5th
  firing — which is carried forward below and NOT graded here.**
- **P-G — instances #26 and #27.** *"the next session usually runs the stops
  **above** it"* printed on **29622.3 Asia High (prev-day)** at **−42** and
  **29537.6 London High (prev-day)** at **−127**, both sitting **below** price.
  #26 graded: held as support and closed **217.2 above** — right level,
  wrong-sided prose. #27 never reached. Prose only, already PROPOSED, free,
  still not actioned.
- **P-B(b) — 18th session; THREE guaranteed windows, one FIRED; inflation
  1.44x.** `merge_tol = max(3.0, 535.8 × 0.008) = **4.29**` against
  `TOUCH_TOL = **8.0**`. **(29622.3, 29615.4)** 6.9 apart → both graded touched
  at **bar 188: FIRED** — the **same pair that fired on 10-20**.
  **(29822.3, 29815.4)** 6.9 apart → bars 210/209, did not fire.
  **(29721.6, 29715.4)** 6.2 apart → bars 185/180, did not fire. Published
  **13/23 = 0.565**; distinct touch bars **9** → distinct-event rate **0.391**;
  **inflation 1.44x**, identical to 10-20. Proposal unchanged.
- **Session-context field — 18th session, and the highest count in the series.**
  **14 of 23** board rows lay inside the pre-scan range **29550.0–29832.5**, and
  unlike 10-20 **one of them is a structural wall** — the 29665.4 call wall that
  §2 shows cannot be graded. Free, arithmetic on data already on the page,
  **proposed 09-29, still not actioned.**
- **D25 — 29th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples — positioning is settled there"*, printed two lines under
  *"No volume has traded yet today"*. Damage none. **See the carry-forward: it
  did not print on 10-22, for the wrong reason.**
- **D26 — reporting gap, NOT data loss; the retraction stands.** `track.py`
  reports **31 trading days / 34 scans (deduped)**, window opening **09-08**. On
  disk: **38** day directories, **68** scan JSONs, **33** days with a PRE_NY
  scan, **32** with a `REVIEW.md` (**33** after this review), **29** with both
  (**30** after). The six August directories (08-23 … 08-28) are **aged out of
  the 45-day bar window**. **Symptom change worth recording:** they are no longer
  filed as *"not finished"* — `review_day` returns no `scans` key for them and
  `track.py:84` `continue`s, so they are now **silently invisible**: absent from
  the table, from `HELD BACK`, and from `excluded`. 38 on disk − 6 aged out = 32
  = 31 graded + 1 held back, which reconciles exactly. **Still a reporting
  defect, still not data loss, nothing proposed.**
- **Max pain — first properly reachable test in eight sessions.** Published at
  **−49** and reached. It **located the post-scan low to 20.2 points** and then
  price left it by **320.6**, closing **224.1 above**. **As a floor it was the
  best level on the board; as the "drift magnet" its prose claims, it failed.**
  The day-of-week qualifier (*"weak on a Monday, strong by Thursday/Friday"*) is
  untested on a Wednesday. **n=1 on the floor reading, nothing proposed.**
- **No instance:** **H2** (`MODERATE`; correctly absent from `track.py`'s
  low-fuel list) · **H3** (CLOSED-NEGATIVE, superseded by H26) · **H4** (flip
  reached, broken, and the close finished **136.3** away — consistent with the
  existing negative verdict, not a magnet) · **H7** (no overnight scan) ·
  **H10** (price inside the prior-week range 29073.7–31079.0; neither branch
  fired) · **H17** (post-scan 172.7 = **44.7%** of session range, nowhere near
  the 5% band; **stays 2 of 3**) · **H20** (CLOSED-NEGATIVE; no High/Medium
  events) · **D21** (near-miss only, 60% up the band) · **D24** (`event_gate:
  null` correct; META and TSLA both after the close) · **P-E** (CALL WALL at
  +401, never reached, **129.4 above the session high** — no touch, no
  instance) · **P-F** (price inside the prior-day range 29211.8–29721.6) ·
  **the fuel-vs-gamma census** (`MODERATE`, outside the cell) · **the
  *"direction right, strategy block wrong"* cell** (bias was wrong; **stays
  n=2**) · **the *"gamma outvoted"* cell** (gamma netted 0; not a voter).
- **No new data point is warranted.** The call failed on the **vintage and
  double-counting of rows already on the page** — a two-business-day-stale pair
  outvoting the live reading of the same instrument 4-to-1, and one foreign CPI
  story counted twice. No free, reliable feed fixes either, and proposing one to
  paper over a weighting problem is how the model gets worse.

---

## Carried forward from the 2026-10-22 scan — recorded, NOT graded

- **⚠️ NEW DATA-SOURCE FAILURE MODE: `gexbot` returned HTTP 401 on
  `/v2/NDX/classic/gex_full`.** Section 7 was suppressed in full and the brief
  printed *"[volume-weighted view unavailable: HTTP 401 on
  /v2/NDX/classic/gex_full]"*. **This is correct behaviour and is recorded as a
  success: the brief degraded cleanly rather than fabricating a level.**
  **The register has NO prior entry for a gexbot auth failure.** The open gexbot
  entries **H12** (volume- vs OI-weighted wall) and **H13** (`zero_gamma`) are
  *claims about the data*, not failure modes; the only failure-mode entry in the
  family is **D17**, which is a **CBOE 429** and a different thing — a 429 is
  transient and D17's fix was to retry it. **A 401 is an auth/endpoint failure
  and will recur until something changes**, so it is logged now rather than
  rediscovered. **No fix to credentials or code is proposed.** n=1.
- **Side effect 1 — the archive lost two files, not one.** The 10-22 commit
  (`a7cf136`) carries **4 files against the usual 6**; the missing pair is
  `research/gexbot/ladders/2026-10-22-1248-oi.json` **and** `-vol.json`.
  `gexbot.persist_ladder()` fetches `gex_full` for **both** weightings
  (`gexbot.py:219`), so one 401 costs the **open-interest** ladder too — while
  the printed message names only the *volume-weighted* view. **The degradation
  message under-reports what was lost.** Recorded, not proposed, n=1.
- **Side effect 2 — D25 did not print on 10-22, for the wrong reason.** The
  false *"The dominant strike is **stable** at 0 across 6 samples"* sentence was
  absent because the **entire section was suppressed**, not because the
  unguarded render was fixed. **D25's streak is interrupted by an outage, not
  resolved**; the defect is unchanged and the counter should resume, not reset.
- **`gamma +2` bottom-of-the-wall-band branch fired again on 10-22 — 5th
  firing.** Prior four were all **below the flip near the put wall, 2 right / 2
  wrong, with score and prose contradicting 4 of 4**. **For the next review to
  grade; it is NOT graded here.**
- **10-22 call `MILDLY BULLISH +3`** at price 29361.0, board offset **+15.7**
  (NDX reference 29345.3, roll **−477.2**, the largest |roll| in the log).
  `track.py` correctly **HELD BACK** 10-22 at 180 bars.

---

## Journal hygiene

One scan file for 10-21 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 17th consecutive review
to carry it**; there is still no schema `quarantine` field and the 09-29
proposal for one is reaffirmed, because `track.py` keeps 09-24 inside every
statistic it prints (direction **17/8/9** becomes **16/8/9** once 09-24 is
removed). **2026-10-13 has no journal directory — documented, not recreated.**
09-09 and 09-25 still have no `REVIEW.md` and none was created. **2026-10-22 is
on disk, `is_trading_day: true`, 180 bars, correctly held back by `track.py`,
and is excluded from every outcome statistic above.** **No `prediction` block
was touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**
