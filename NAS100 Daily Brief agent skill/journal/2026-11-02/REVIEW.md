# 2026-11-02 (Monday) — review

_Written after the 2026-11-03 brief was delivered. Nothing here blocked, delayed
or altered it. One scan graded: `1248-london.json` / `.md`, `LONDON`
12:48:42Z, `is_trading_day: true`, **264 bars**, `review_day` reports **0 test
artefacts**. **No `prediction` block was touched. No scoring, wall or grading
code was edited.**_

**`track.py` DID NOT COMPLETE — 6th consecutive failure.** `timeout 240 python3
-u track.py` → exit **124**, **0 bytes stdout, 0 bytes stderr**. Every census
figure below is derived **FROM SOURCE** (29 journal scans + one 45-day `M_5`
fetch, **8719 bars, 2026-09-21 → 2026-11-03**) and reported **alongside** the
register's carried value, never replacing it. The derivation reproduces seven of
the register's published figures exactly (10-30 post-scan −254.4 and error
+351.6; 10-29 error +112.4; 10-28 error −76.1 and post-scan −155.6; 10-16
+479.3; 09-21 +569.2), which is the only warrant offered for it. The 3-session
rule was applied **by hand, per entry**.

---

## ⚠️ 0. THE D29 GRADING RULE, decided and written down for the next ~93 sessions

11-02 is the **first graded `LONDON` scan**. The rule below is stated once and is
to be applied unchanged until the next DST change (2027-03-14), so that the
following reviews are consistent rather than each re-deciding. **No schedule
change is proposed — that is the user's.**

**(G1) Pre-scan-keyed `PRE_NY` censuses do NOT accrue.** P-B(b)'s denominator
stays **23**; the session-context-field census stays **22**; pre-scan sweep
counts and pre-scan contamination flags do not advance. A `LONDON` scan sits
**59 minutes further from the NY open** and is a **different population, not an
extra observation**. Where a `LONDON`-era figure is wanted, a **parallel census
labelled `LONDON/EST (from 2026-11-02)` starts at n=1** — the existing
denominators are never widened. Both 11-02 figures are recorded below as
observed-and-excluded, and open the parallel census at n=1.

**(G2) The fuel-error series (H1/P4) ACCEPTS 11-02, and my own 10-30 concern is
CORRECTED.** The 10-30 challenge said a longer pre-scan window inflates
range-at-scan and biases the error positive. **Measured, that is the wrong
direction for 11-02.** Market time in the pre-scan window:

| | pre-scan market time | bucket start |
|---|---|---|
| EDT norm (e.g. 10-29) | **14h45m** | 22:00Z |
| **11-02 (Monday after the change)** | **13h45m** | **23:00Z** |
| Tue–Fri under EST | **14h45m** (first hour is the *previous* session's post-close tape) | 21:00Z |

11-02's window is **60 minutes of market time SHORT**, which biases
range-at-scan **down**, the budget **up** and the error **negative**. The
observed error is **+161.2 — positive against the bias**, so inclusion cannot
manufacture the positive mean the challenge worried about. Accepting it is the
conservative choice, and the choice was made on a figure (window length) fixed
before the outcome was known. Every `LONDON`-era error is to be **tagged** in
the record so the two eras can be split later without re-derivation.

**(G3) Everything else grades normally** — direction, level grading, M6, P5,
P-E/P-E(b), P-G, H2, H10, H14, H17, H18/P1, H19, H22, H23, H26, H27, P-C, P-F,
P-H, D5/D7/D9/D18/D21/D22/D23/D25/D26/D27/D28 and the dead-weight audit. This is
the 10-28/10-30 exclusion precedent's own list, not fresh judgement.

**(G4) The post-close-hour census is CLOSED for the EST era.** See **D30**: the
graded day now ends **at** the cash close, so it contains **no post-close bars at
all**. 11-02 is **NOT a third instance**, and the reason is **structural, not
evidential**. The census stays **n=2** (10-28 53.0%, 10-29 43.4%) with 10-30's
6.5% as its counter, and takes no further instances while EST holds.

---

## 1. Scoreboard

| | |
|---|---|
| call | **MILDLY BEARISH −3** at 28583.2 (`LONDON`, NY cash +101 min) |
| session O/H/L/C | **28502.4 / 28754.5 / 27965.6 / 28002.5** |
| range · net | **788.9** (1.257× ADR14 627.7) · **−499.9** |
| direction, post-scan (P-H basis) | **−580.7 → CORRECT** |
| direction, day-net | **−499.9 → CORRECT** · bases **agree**, no deciding instance |
| levels | **19 published / 14 touched = 0.737** |
| fuel | budget **390.0**, extension **551.2** → error **+161.2** (**1.41×**); traversal **788.9 = 2.02×** budget; `review_day` verdict *"about right"* |
| VXN-implied budget | **513.2**, the figure §3 told the reader to prefer — realised range beat it by **275.7** |
| straddle band | ±347 → 28236 .. 28930; close **28002.5 is OUTSIDE it** by 233.5 |
| `|post|/ADR` · range/ADR | **0.925** · **1.257** |

**Direction, from source, n=29 gradeable (09-24 quarantined, 11-03 unfinished):**
**13/23 = 56.5%** post-scan vs **14/23 = 60.9%** day-net, 6 no-calls.
Carried: **15/27 vs 16/27**.

---

## 2. What the levels actually did

**The day was decided at one level, and the brief named it correctly.** CALL WALL
**28728.6 ●●●●● 1.17bn** at **+145**, stacked with a 0.62bn shelf, 38k this week
/ 57k on the 45-day: *"desks must SELL as price rises into it, so rallies stall.
Take profit into it."* Price first exceeded it at **15:20Z**, set the day high
**28754.5** at 15:25Z — overshoot **+25.9** — never regained it, held it as
resistance for **330 minutes** (worst excursion +23.4), and closed **726.1
below**. This is the first session in weeks where the headline wall was **inside
the published budget** (+145 against 390), and it is the one that worked.
**P-E instance 20.** On P-E's own overshoot metric 25.9 falls in the **12–103
"middle"** band → **third middle instance** (after 10-06 and the instance-15
day). The two-mode framing was already retired at the second; nothing new.

**The 0.74 hit rate is bought by a single 5-minute bar.** The 13:35Z bar ran
28563.2 → 28699.9 (**136.7 points in five minutes**) and first-touched **six**
published rows — 28607.9, 28653.2, 28664.8, 28675.2, 28694.8, 28703.2. Adding
28711.5 on the 13:40Z bar, **7 of the 14 touches (50%) were taken inside ten
minutes**, from a board carrying **six rows inside a 58.3-point window**. The
density artefact (**H6**) at its sharpest in the record: the hit rate is
measuring board crowding, not level quality.

**Levels that did their job**

- **28556.4 PD mid + London Low (today) ⭐** — held as resistance **280 min**,
  worst +11.0, close 554 below. The cleanest row on the board after the wall.
- **28457.1 Asia Low (today)** — resistance **210 min**, worst +12.3.
- **28379.8 PD close** — resistance **140 min**, worst +10.4.
- **28428.6 / 28328.6** (secondary, put-dominant, *"accelerate THROUGH rather
  than stall. Not a floor"*) — both correct; price finished 462.7 and 362.7
  below them.

**Levels the brief read wrong**

- **28628.6, the named UPSIDE brake** (+45, 0.36bn, *"expect a stall — rallies
  lose momentum into it"*). Price went **straight through it** on the 13:35Z bar
  and traded **125.9 above** it. The level that actually capped the day was the
  **CALL WALL at 28728.6 — 1.17bn, 3.2× the force, 100 points further out**.
  **H23's force-ranking branch was CLOSED on three consecutive distance-first /
  force-first *agreements*. This is the first DISAGREEMENT, and it favours
  force.** n=1 against a closed branch — recorded, nothing re-opened.
- **28528.6, the named DOWNSIDE brake** (−55, 0.23bn shelf, *"expect a stall …
  rather than assuming a clean breakdown"*) — **right at first contact** (low
  28504.4 at 14:35Z, bounce to 28611.5 five minutes later), **wrong on the
  break**: price finished **562.8 below** it. Same first-contact-versus-
  sustained-break split H14 found on 10-30, now in a different block.
- **28278.6 PUT WALL ●●○○○** at −305, *"if it breaks, expect it to speed UP, not
  bounce. Don't buy the break."* **H14 instance 7.** First contact 19:00Z, ~15
  minutes of chop with a **+7.2** reclaim poke (against 10-30's 2h20m and
  +216.9), then a clean **313.0-point = 0.499× ADR** run-through to 27965.6.
  *Don't buy the break*: **RIGHT** at the wall (313 underwater) **and RIGHT at
  the extreme** this time — the bounce topped at +106.4 and never reclaimed
  (10-30's was +351.5). The rider **splits the same way as 10-30**: wrong on
  first contact, right on the sustained break. **n=2 for that mechanism inside
  H14.**
- **MAX PAIN 28988.6** at +405, missed by 234.1 — untestable. The *"weak on a
  Monday"* qualifier is consistent and untested. Census stays **1–2 at n=3**.

**Levels nothing reacted to — and the one that should stop being published.**
Four rows were never reached (GAMMA FLIP +489, PDH +445, MAX PAIN +405, London
High prev-day +277) and the **STRUCTURAL PUT WALL at −705** was missed by
**87.0**. **P3/H6**: no structural touch, so the standing *"stop publishing the
structural wall"* narrowing **stays blocked** at 1 clean / 1 confounded. On the
denominator: **5 of the 19 rows sat beyond the brief's own 390-point budget** and
were unreachable on its own forecast, so the 0.74 is again structurally inflated.

**`TOUCH_TOL = 8.0` — not an instance.** Nearest untouched rows missed by
**105.3** (28859.8) and **87.0** (27878.6), 13.2× and 10.9× the tolerance. Stays
**n=2**.

---

## 3. What was wrong, and why

The direction was right and the **magnitude was badly short**: `|post|/ADR`
**0.925** against a −3. Every bad call on this page traces to the **same place**
— the part of the score that is *not* the duplicated pairs.

### 3a. H27 observation 7 — the independent remainder cut a −10 to a −3, and the remainder was wrong

| | 10-23 | 10-26 | 10-27 | 10-28 | 10-29 | 10-30 | **11-02** |
|---|---|---|---|---|---|---|---|
| vol ↔ breadth | −7 | −3 | +1 | +4 | +1 | −2 | **−7** |
| structure ↔ gamma | −6 | −3 | 0 | +4 | −7 | −6 | **−3** |
| independent remainder | −3 | 0 | −4 | −2 | +1 | −5 | **+7** |
| score | −16 | −6 | −3 | +6 | −5 | −13 | **−3** |

The two duplicated pairs carried **−10** on their own. The "independent"
remainder — `rates +3` · `macro +3/+1/−1/0/0/0` · `news +1` · `fuel 0` ·
`events 0` — contributed **+7**, and **every signed row in it was wrong**. The
most extreme remainder in the series, **opposite-signed and 233% of |score|**.
**Counter-instance to H27's founding configuration; weight limb stays
ANSWERED-NEGATIVE; nothing re-proposed.**

### 3b. `news +1` — graded as two separate things, because they fail separately

**Reproduced from source** (`news_scorer.score_item`, the headline verbatim):

```
rule=cpi_cool  direction=+1  magnitude_pts=220  half_life_min=75
freshness=1.0  flags=[]  confidence=HIGH  weighted=+2.20
note="Cool inflation -> Fed path softens, duration rallies"
```

**The printed reason is FALSE as applied.** The rule at `news_scorer.py:69` is
`\b(cpi|inflation|pce|ppi)\b.{0,40}\b(cool|…|fall[s]?|drop)`. In *"AI Stocks
Finally Help the Fed Fight Inflation, by Falling"* the thing **falling is AI
stocks**, not inflation; there is no inflation print in the story at all. The
brief told the reader *"Cool inflation → Fed path softens"* about a headline that
reports no inflation data.

**This is D9, exactly — and it is D9's first SCORED recurrence.** D9's founding
note (*"US stocks fall as oil prices jump"* → `risk_on`) closed with *"No damage
today: it fell into NEEDS_JUDGEMENT and never scored … Recorded so that if it
recurs it can be counted rather than rediscovered."* `cpi_cool` **is** in
`HIGH_CONFIDENCE` (`news_scorer.py:235`), so this one voted at full weight.
**D9 instance 2, and the first with damage.**

**It is NOT D18, and that was checked rather than assumed.** Every rule in
`RULES` was run against the headline: **`cpi_cool` is the only match.** No
bearish rule competed, so neither D18 limb (first-match-wins; `HIGH_CONFIDENCE`
asymmetry) is engaged. **D18 stays at 10 trading days / 17 headlines.**

**And it is NOT the 10-30 headline-vs-event ageing defect — but that defect
recurred on the same page.** The arithmetic: `+2.20·1.0 − 1.70·0.6 = +1.18`, and
`round(1.18/2) = +1`. The `−1.70` leg is the **StoneX Amazon/Intel** headline,
scored at **freshness 0.6** on **Monday** for an event that printed after the
**Thursday 10-29 close** — the same event the 10-30 review flagged. `news_scorer`
ages the **headline**, not the **event**. **n=2 (10-30, 11-02). Below threshold.
NOT proposed.**

**The score, graded separately.** Strip the mis-subjected headline and the raw
score is **−1.02 → news −1**, a **2-point swing**, not 1. Total would be **−5**:
still `MILDLY BEARISH`, still −1, still CORRECT. **Verdict effect zero; cost is
2 points of conviction on a day that moved 0.925× ADR.**

### 3c. H18 / P1 — instance 30, duplication **35 of 35**, and the first ALL-SAME-SIGNED-AND-ALL-WRONG instance

| row | instrument | as of | pts |
|---|---|---|---|
| `rates +3` | US10y 4.929%, −1.20% today | **live** | **+3** |
| `macro +3` | DFII10 real 10y, −4bp | **2026-10-29** (2 business days stale) | +3 |
| `macro +1` | DGS10 nominal 10y, −7bp | **2026-10-28 → 10-29** | +1 |

**One instrument, read three times, +7 of a −3 score, two of the three readings
from last week.** The brief printed the staleness warning in full and nothing
read it. Unlike 10-30 (the first opposite-signed instance, where the stale pair
outvoted the fresh row 4–3), **11-02 is same-signed — and all three were
wrong**: yields fell and tech fell 500 points. So *"trust the fresh one"* is
again unsupported, and the **rendering** proposal is unchanged. **No weight
change is proposed.**

**What the full correction buys, stated so it is not over-claimed.** Dropping the
two stale 10-year duplicates (−4) and fixing the news row (−2) moves the score
from **−3 to −9** — one label step, `MILDLY BEARISH → BEARISH`. H26's 6–9 bucket
mean `|post|/ADR` is **0.510**; the realised figure was **0.925**. **No available
correction reaches the realised magnitude.** The score was structurally short of
this day, not short by one bad row.

### 3d. `PIN_THEN_EXPAND` — post-verdict firing 1. The shape worked; the **timing prose was wrong again**, and this is the harm case P-I lacked

The shape is **CLOSED, FALSIFIED 3 of 3**; the verdict was sealed before 11-02
and **nothing here re-opens it**. Recorded as **post-verdict observation 1**.

- *"Breakouts will fail while the pin holds"* — **RIGHT.** The 13:35Z break above
  the Asia high failed; price was back at 28504.4 by 14:35Z.
- *"Chop early, resolve late"* — **directionally RIGHT.** The two largest hours
  were the last two (19:00Z **251.9**, 20:00Z **262.7**).
- *"From roughly **13:00 ET** the pin weakens and the move … gets released. Save
  your risk for the afternoon."* — **WRONG, early by ~2h30m, and it cost the
  day's whole edge.** The high printed at **15:25Z = 10:25 ET** and the release
  ran from there. By 18:00Z (13:00 ET) price had already fallen **450.3 from the
  high** and **−279.0 of the graded −580.7 (48.0%)** was gone. A reader obeying
  *"be patient in the morning"* missed the top and half the move.

**This is direct support for P-I (withdraw the timing prose) on the one axis P-I
targets, delivered by a session on which the shape's direction was right.**
P-I unchanged, nothing new proposed.

### 3e. H2 — the cell is a non-instance, and the contradiction's localisation is FALSIFIED and RE-SPECIFIED

**Not a cell instance** (`ROOM_TO_EXPAND`, below the flip). **Census stays
6–2 / 8–0.**

**The §2/§3 contradiction did NOT fire.** §2: *"Sweeps tend to keep running …
Fading is the wrong trade today — Strategy 2."* §3: *"The range can still grow.
New highs/lows are live — breakouts and continuation have somewhere to go."*
**They agree.**

The 10-28 mechanism — *"the fuel prose is inverted by state while the gamma prose
is not conditioned on fuel at all, so the two blocks contradict at BOTH ENDS of
the fuel scale"* — **predicts a contradiction here and there is none. That
specification is FALSIFIED.** The conditioning variable it is missing is the
**gamma sign**:

| | `ROOM_TO_EXPAND` (§3: breakouts live) | `MODERATE` | `LOW_FUEL` (§3: favour fades) |
|---|---|---|---|
| **above flip / long gamma** (§2: fade) | **CONTRADICT** — 10-28 | — | agree |
| **below flip / short gamma** (§2: go with it) | **agree — 11-02** | agree — 10-29 | **CONTRADICT** — 10-23, 10-26, 10-27, 10-30 |

**This 2×2 fits all seven recorded observations and is the first specification
that does.** 11-02 is the cell that was missing. Per the **10-19 precedent** this
is a **correction to a live specification inside the suspended census, not a new
claim — no ID taken, nothing proposed.**

**But the page still carried two opposite instructions, from a THIRD and FOURTH
block.** §2's *"fading is the wrong trade"* against the shape block's
*"breakouts will fail while the pin holds"* and both named brakes' *"take
partials rather than assuming a clean breakdown/breakout"*. **Recorded as a
distinct surface, n=1, and deliberately NOT entered into the §2/§3 census** —
counting it there would corrupt the 2×2 above.

### 3f. The fuel budget, and D30's fingerprint on it

Error **+161.2** — 8th largest of 29. From source: **n=29, mean +68.7, median
+25.9** (was n=28, +65.4 / +16.1). H1's zero/non-zero split **holds**: budget = 0
**mean +235.4** (n=3) against budget > 0 **mean +49.5** (n=26). `ROOM_TO_EXPAND`
with `fuel_ratio` 0.9 was the right *label*; the number under it was **41% light
on extension and 102% light on traversal**. **P4/H1 remains
ANSWERED-NEGATIVE** — this is the **tenth** value reported under one series name.
**Flagged, not averaged.**

**H22 — n=17 → 18, label RIGHT and still NOT DISCRIMINATING.** Week net GEX
**−0.579bn** → *"expansion likely"*; realised **1.257× ADR**. 10-30's
**−7.744bn** produced the **same label** and 1.594×. A figure **13× smaller**
changes nothing the label says. The VXN-implied budget was beaten by **275.7 —
7th counter-instance.**

---

## 4. Change proposals — only material ones

### PROPOSED — **D30 (NEW)**: `trading_day()`'s hard-coded 21:00Z roll no longer matches the broker's day, and the brief and the grader now disagree about the same session's close by **83.1 points**

`levels_fuel.py:90–94`:

```python
def trading_day(dt):
    """cTrader daily bars roll at 21:00 UTC — bucket intraday bars the same way
    so 'previous day' means the same thing on both feeds."""
    d = dt.date()
    return d + timedelta(days=1) if dt.hour >= 21 else d
```

**The docstring's premise is now false.** The CFD session runs 18:00 → 17:00 ET.
Under EDT that ended at 21:00Z and the constant was correct. Under EST it ends at
**22:00Z**, so the 21:00Z bucket boundary now falls **at 16:00 ET — exactly the
NY cash close** — and cuts the session an hour early.

**Verified on disk and from the tape, not inferred:**

| | EDT (10-30) | **EST (11-02)** |
|---|---|---|
| bars in the graded day | 275 (22:00Z → 20:50Z) | **264 (23:00Z → 20:55Z)** |
| graded close | 17:00 ET close | **the cash close** |
| post-close hour inside the graded day | 55 min | **0 min** |
| 21:00–22:00Z of 11-02 | — | bucketed into **`2026-11-03`**, as its **first 12 bars** |

Three consequences, each demonstrated:

1. **The post-close hour has not disappeared; it has MIGRATED into the next day's
   pre-scan window.** The AAPL after-hours tape (21:00–22:00Z Nov 2:
   O 28002.7 / H 28112.6 / L 28002.0 / C 28085.6, range **110.6**, **+83.1**) is
   `trading_day = 2026-11-03`. It therefore inflates 11-03's `today_range` and
   `adr_used_pct` and deflates its `remaining_budget` — **the exact mechanism the
   10-30 review challenged under H1/P4, relocated.** It must be recorded per day
   for the whole EST era.
2. **The brief and the grader now disagree about one session's close.** 11-03's
   board prints **`PD close + PWL` at 28085.6** — the **21:55Z** close, taken
   from the **D_1** bar (`levels_fuel.py:173, 229`), which rolls at 22:00Z.
   `review_day` grades 11-02's close as **28002.5** — the **20:55Z** close, from
   the `trading_day`-bucketed `M_5` series. **83.1 points apart, same session,
   same skill.** `PDH 28754.5` and `PDL 27965.6` agree only by luck: the lost
   hour happened to stay inside the day's range. **`adr_used_pct` now divides a
   21:00Z-bucketed numerator by a 22:00Z-bucketed ADR14 denominator**, and the
   contamination grows as EST days enter the 14-day window.
3. **Friday's post-close hour will vanish entirely.** `trading_day(21:00Z Fri)`
   returns **Saturday**, which has no scan and never enters a statistic. First
   occurrence **2026-11-06**.

**Evidence:** mechanically demonstrated and arithmetically reproduced, not a
calibration claim — the register's practice for D-numbers (D28, D29 both opened
at n=1 on demonstration). **Expected effect:** making the two day-definitions
agree removes a standing 83.1-point disagreement between published and graded
levels and restores a single meaning for "yesterday". **Which roll is correct is
the user's call** — DST-aware 22:00Z/21:00Z tracking 17:00 ET, or an explicit
cash-close basis — and both have consequences for the back-record, so **no edit
was made.** **D30 also CORRECTS D29's point 2** (*"No CODE is blind to today's
scan — checked"*): that check grepped only for `PRE_NY` and did not reach
`trading_day`. **Grepped before opening:** `^## D30` unused; D29 (session
category / pre-scan length), D26 (45-day window), D1 (fuel across the 21:00Z
rollover), M7 and D23 all checked, none covers the roll constant.

### PROPOSED — **M6's driver is FOUND after 37 sessions**, and it is a one-line inversion

`review_day.py:159–161`, the `lost` branch of `grade_level`:

```python
react = (f"broke {'DOWN' if st['settled_side'] == 'above' else 'UP'} "
         f"through it — lost by {abs(st['worst_excursion']):.1f}pts")
```

`settled_read` sets `settled_side` from `bars[-1]["close"] >= price` — the side
price **ended on**. The ternary names the direction of the **adverse excursion
against** that side, while the sentence *"broke X through it — lost by N"* reads
to any trader as **the direction the level broke**. The two are **always
opposite**.

**Audited over every graded day the bar window serves: 82 of 82 lost-level rows
inverted, across 25 sessions that had one, and `inverted == lost` on 30 of 30
days.** Not a statistic — an identity.

On 11-02 it produced **8 inverted rows of 14 touched** on a day that closed 580
points below the scan — every one reading *"broke **UP** through it"*, including
**28084.6 PDL + PWL ⭐**, a floor that broke **down** by 119.0 and closed 82.1
below, reported as *"broke UP through it — lost by 36.5pts"*. **28711.5 NY High
contradicts itself inside one row**: `reaction` *"broke UP through it"* against
`first_touch_reaction` *"broke DOWN through it"*. 10-28 produced **13 of 13**.

**This resolves M6's own open question.** The register has recorded
*"driver UNKNOWN"* for sessions on end and has rejected travel-scaling (4
consecutive failures) and window placement (7 of 7). **Window placement is a
real, SEPARATE defect** — `_first_touch`'s fixed 12-bar window is correct inside
its window and misleading as a day verdict (10-30's PUT WALL). **The series is
two defects, not one, and conflating them is why 37 sessions found neither.**
The `held` branch (`support`/`resistance`) is **correct** and is not implicated.

**Expected effect:** every "lost" level verdict in the record currently names the
wrong direction; fixing the sentence makes 82 historical rows readable and stops
the M6 counter growing. **This is grading code and I did not touch it.** Two
candidate forms — swap the ternary, or re-word to *"settled below/above it after
a N-point excursion the other way"* — **the choice is the user's**, and the
second is better because it stops conflating the excursion with the break. **No
new ID: this belongs to M6.**

### Evidence appended, threshold NOT met, nothing proposed

- **H26 — a 3–5 instance, and the magnitude limb holds a 12th session.**
  `|post|/ADR` **0.925**, range/ADR **1.257**, direction **CORRECT**.
  3–5 bucket: **carried 5/9 = 55.6% → 6/10 = 60.0%**; **from source 4/7 = 57.1%
  → 5/8 = 62.5%**. **Both reported; neither averaged.** From source at **n=29**:

  | bucket | n | mean \|post\|/ADR | mean range/ADR | direction (post-scan) |
  |---|---|---|---|---|
  | 0–2 | 6 | 0.193 | 1.042 | — (all no-call) |
  | **3–5** | **8** | **0.440** | **1.144** | **5/8 = 62.5%** |
  | 6–9 | 9 | 0.510 | 1.074 | 5/9 = 55.6% |
  | ≥10 | 6 | 0.642 | 1.399 | 3/6 = 50.0% |

  **Magnitude monotonic for a 12th session.** Direction is now **monotonically
  inverted** — 62.5% / 55.6% / 50.0%, best to worst as conviction rises. *"Inverted
  at the top"* **stays SUSPENDED**: the ≥10 cell holds six observations whose
  composition changes weekly (D26). **No Spearman quoted** — its derivation is
  still unwritten (10-20 correction). 11-02's own point is the **largest
  `|post|/ADR` the 3–5 bucket has ever carried**, taking 10-29's 0.696 title.
- **P-F — the CONTROL is derived for the first time, and it supports the entry.**
  Derived from the bars, not the boards (`prediction.levels` is the *filtered*
  board, so 20 of 29 days carry no PDL row — the control was never derivable the
  way it had been attempted). Prior-day H/L from the same bars `review_day`
  grades on; the **>150pt trigger is P-F's own**, so no free parameter was added.

  | | n | mean error | median |
  |---|---|---|---|
  | treatment, price >150 outside the PD range | **3** (10-15, 10-22, 10-30) | **+283.5** | +351.6 |
  | **control**, inside or ≤150 outside | **25** | **+22.9** | **+0.1** |
  | strictly inside (dist 0) | 20 | +47.0 | — |

  **A 12.4× difference in mean error, and the control's median is +0.1.** The
  budget is essentially unbiased inside the prior-day range and badly biased
  positive far outside it. **Caveats, both material:** this sample is **not** the
  register's 5-day treatment list (09-14, 09-17, 09-21 have aged out; 10-15 is a
  treatment day the register's list omits) and **the two must not be merged**;
  and **11-02 is itself a CONTROL day** (dist 0) whose +161.2 is the 3rd largest
  error in the control set, so including it makes the control look **worse** —
  the derivation is conservative. **P-F is already PROPOSED and gains its missing
  half. NOTHING NEW is proposed, and NEVER a multiplier** (the H1 lesson): the
  only defensible form is a **flag** that the budget is unreliable when price is
  far outside, not a scaling factor fitted to +116/+383/+352.
- **H19 — clause (i) FAILS, exactly as anticipated. n stays 2.** 2 auto-scored
  headlines from **2 distinct events** (BeInCrypto/Fed-AI; StoneX/Amazon-Intel) —
  **no match-count inflation**, so 11-02 does not qualify. Sample stays **10-29
  and 10-30 only, n=2**, and **the clause was not widened.**
- **P-G — instances #37 and #38, two on one board.** `28675.2 Asia Low
  (prev-day)` at **+92 ABOVE** price and `28607.9 London Low (prev-day)` at
  **+25 ABOVE** price both printed *"the next session usually runs the stops
  **below** it"*. Both **also promise an event that had already happened** — the
  pre-scan low was **28457.1**, so those sell-stops were taken **218.1** and
  **150.8** points earlier. Same shape as #36. **Controls on the same board:**
  `28457.1 Asia Low (today)` at −126 faces correctly and had **not** been swept;
  the merged `28556.4 PD mid + London Low (today)` again shows the **merge
  picking the wrong note**.
- **Session-context field — observed and EXCLUDED under G1; `LONDON/EST` census
  opens at n=1.** **8 of 19** published rows (28694.8 down to 28457.1) sat inside
  the pre-scan range **28457.1–28694.8**, i.e. price had already traded them
  today, and no field says so. `PRE_NY` census stays **22**.
- **P-B(b) — observed and EXCLUDED under G1; `LONDON/EST` census opens at n=1.**
  **Zero** guaranteed double-count windows, but the closest pair is
  **28711.5 / 28703.2 = 8.3 apart = 1.04× `TOUCH_TOL`** — the **tightest
  closest-pair in the series**, a near-miss by 0.3 points. `PRE_NY` denominator
  stays **23**.
- **P5 — the *"best level is in the secondary table"* sub-claim is DEAD at three
  consecutive counter-sessions** (10-29, 10-30, **11-02**). The day's best level
  was the **CALL WALL on the main board**. Secondary table graded: the two
  put-dominant rows (28428.6, 28328.6) **RIGHT**, the call-dominant brake
  (28628.6) **WRONG**, 28928.6 **never reached** (+345, missed by 174.1).
  Threshold reached; **the resolution is "the sub-claim is dead", which is no
  model change**, and P5's actual proposal (persist and grade the table) is
  unaffected. **Nothing proposed.**
- **`gamma +2` bottom-of-band — a CONTROL, and a clean one.** It did **not** fire:
  price was **mid-band, 68% up** a **450.0-point** band (28278.6–28728.6) =
  **0.717× ADR**, a normal width against 10-30's 2100pt / 3.55×. Census stays
  **3 right / 4 wrong**, prose contradiction **7/7**, zero sign changes in seven
  firings. Recorded against **D21's width pre-registration**: at normal width and
  mid-band the row correctly scores 0. It **DID** fire on the 11-03 scan —
  carried forward, not graded.
- **D7 — a CLEAN CONTROL on both limbs, and the dropped-row census stays n=2.**
  The footnote printed **one** row (*"30024 PWH"*) against its cap of 6, so the
  price-ordered truncation **could not fire**. The 45-day call wall **merged into
  the headline CALL WALL row** (*"ALSO the 45-day call wall, 57k contracts"*), so
  no strong ceiling vanished — first limb clean. GAMMA FLIP, PDH, MAX PAIN and
  both put walls all reached the board. Census stays **2, both PDL** (10-23,
  10-30).
- **D28 — the condition did NOT recur; the harm count is unchanged.**
  `events_24h` carried **one** row (ISM Manufacturing PMI, Medium, 15:00Z) and §5
  printed it. Condition instances stay **10-28 and 10-30 (n=2, non-consecutive)**;
  the *"transient"* conclusion stays **withdrawn**. The 11-03 scan carries **two**
  rows (JOLTS, Congressional Elections). **D24 is a clean control** — the
  same-day AAPL after-hours row rendered correctly alongside the forward-dated
  AMD row.
- **P-C / dead-weight audit — `events` 0 of 2, and it has still never scored in
  its history** (`bias_engine.py:259–263`). **AAPL's after-the-close print was
  priced at +0** on the very day it reported. **12 of 26 rows scored 0** (gamma
  mid-band, VIX9D, DXY, HY OAS, NFCI, yield curve, fuel, prior-week structure,
  both news bullets, both events rows).
- **D22 — a CANDIDATE instance, explicitly UNCONFIRMED.** `breadth −1` printed
  **NDX −3.46% vs ES +0.32% — a 3.78pp divergence, the largest in the 25-scan
  record** (next: 10-19 2.99pp, 10-23 2.46pp). **The NDX leg checks out**: it
  reproduces 10-30's prior-session cash-close-to-cash-close move
  (**−3.54%** at 19:55Z) to **0.08pp**, and 11-03's leg reproduces 11-02's
  (**−1.33%**) to 0.06pp. **The ES leg is the implausible one** — the whole US
  tape fell on 10-30. If NDX is prior-session cash and ES is the live futures
  change at scan time, the row compares **two different windows**, which is
  precisely D22's claim. **I cannot source ES independently and do not claim it.
  n=1 candidate. Nothing proposed.** D22's own cheap test — log each leg's window
  timestamps — is already its proposal.
- **D27 — 8th consecutive `gexbot` 401** on `/v2/NDX/classic/gex_full`;
  volume-weighted ladder absent, **H12/H13 untestable** again. The 11-03 scan
  carries a **9th**. **Nothing proposed** — no credential change, no retry policy.
- **D25 — interrupted at 29.** The brief renders §1–§6; there is no §7, so the
  unguarded `drift` sentence did not render for a **5th** consecutive session.
  Counter resumes when §7 does.
- **D23 — observation 14, NO residual, NONE inferred.** §7 did not render.
  Offset **28.6**, basis `nq_implied`, greeks `repriced_bs_at_current_spot`; NDX
  cash **3874 minutes** stale, rolled forward by the NQ move (**+169.8**) to
  28554.6. **Recorded clean.**
- **D26 — the window moved AGAIN, and the direction reversed.** From source,
  **30** journal trading days now hold a full bar set (incl. 09-24 → **29
  gradeable**, up from 28) against **44** finished trading-day directories —
  **14 invisible** past the 45-day window. **09-18 has now aged out ENTIRELY**
  (the register saw it at 96/276 bars one session ago) and **09-21 became the
  oldest usable day**, which is why **P-F's treatment set lost 09-21** to the
  no-prior-day boundary. Concrete harm this session: P-F's treatment n is **3,
  not 5**, for reasons that have nothing to do with evidence.
- **P-H — no 6th deciding instance, and the window limb is now MOOT.** Post-scan
  **−580.7** and day-net **−499.9** agree; **CORRECT on both**. Carried
  **15/27 vs 16/27**, deciding set **n=5** (D26 has eaten two of the five). From
  source **13/23 vs 14/23**, deciding set **n=3 (10-07, 10-15, 10-19)** —
  unchanged. **The grading-window limb takes NO 4th instance and cannot take
  another while EST holds**: per **D30** the window now ends **at** the cash
  close, so *"to the last bar"* and *"to the cash close"* are **the same basis**.
  The limb is **frozen at n=3, split 2–1.** 19:55Z close 28185.8 vs 20:55Z close
  28002.5 — both CORRECT. **Nothing proposed.**
- **H8 — post-closure, and this is a MISS.** The band was a genuine daily one
  (±347 off the **2026-11-02** straddle, 408pts, ATM IV 18.7%) and the close
  **28002.5 fell 233.5 outside it**. H8 is **CLOSED ANSWERED-POSITIVE (8 of 10)
  and is NOT re-opened**; recorded so that post-closure misses can be counted if
  they accumulate rather than rediscovered.
- **No instance:** **H3** (CLOSED-NEGATIVE, superseded by H26 — not re-opened) ·
  **H4** (flip 489 away, never reached) · **H5** · **H7** (no overnight scan) ·
  **H9** (AAPL is `sector-relevant`, not index-defining under the engine's own
  definition — **NVDA only**; the after-hours tape also fell outside the graded
  day, see D30) · **H10** (`structure +0`, price **inside** the prior-week range
  498.6 above the PWL — the ±3 branch did not fire; the close finished **82.1
  below** the PWL, which the rule never saw) · **H11** · **H12/H13** (401) ·
  **H15/HY OAS** (scored 0; folded into the dead-weight audit) · **H16** ·
  **H17** (`|post|/ADR` 0.925 is not a deadband case; stays **2 of 3**) ·
  **H20** (CLOSED-NEGATIVE; events were Medium only) · **H21**
  (CLOSED-NEGATIVE; VIX9D/VIX 0.996 flat) · **D5** · **D8** · **D14** ·
  **D15** · **D21** (did not fire — see the control above) · **the
  gamma-outvoted cell** (gamma −5 was the largest block and it **agreed** with
  the realised direction; stays **n=5**) · **the max-pain Thursday/Friday
  clause** (level 1.45× the budget away; grading it would manufacture the data
  point that triggers its own deletion).

### Is a new data point needed? **No, and this is the clearest "no" in weeks**

Everything that decided 11-02 was **on the page**. Breadth printed
**mega-caps −3.12%, 0 of 4 up, NVDA −4.22%, AVGO −5.48%** and **NDX −3.46%
against ES +0.32%** — the two most informative rows in the document — and they
were **outvoted by +7 of duplicated and mis-read macro/news**. The one genuinely
absent input remains an **event-age field** for `news_scorer.py` so it ages the
**event** rather than the **headline**; that is **free, local, and a change to
code the register already owns**, and it stands at **n=2 (10-30, 11-02) — NOT
proposed.** **No external source is proposed.**

---

## Carried forward from the 2026-11-03 scan — recorded, NOT graded

- **Second consecutive `LONDON` scan**, 12:47:56Z, `scan_et 07:47 ET`.
  **G1–G4 apply to it when it is graded.**
- **`STRONGLY BEARISH −12`** at **28083.0** — a **≥10** instance, a bucket that is
  a coin flip on both censuses (**carried 4/8 = 50.0%, from source 3/6 = 50.0%**).
  Offset **−15.6**, clean. Flip **28876.5** (price 793.5 below), shape
  `COHERENT_SHORT`, fuel **`ROOM_TO_EXPAND`** ratio-implied, budget **418.6**,
  **ADR14 661.7** (up from 627.7 and 565.9 a week ago), **36.7%** used.
- **The NDX is officially in correction, −10% from its highs**, and the judgement
  list is dominated by it. **`vol −6`, tying the largest vol contribution
  recorded**: **VXN 30.89 (+8.4%, highest of the series)**, **VIX9D/VIX 1.052 —
  BACKWARDATED**, VVIX 110.47, ATM IV 35.3%.
- **Price is sitting exactly on the prior-week low**: `PD close + PWL` merged at
  **+2.6 ⭐** and the brief calls the PWL **resistance**. **Per D30, that
  28085.6 is the 21:55Z (16:55 ET) D_1 close and is 83.1 points above the
  11-02 close `review_day` graded (28002.5).** Record which basis every 11-03
  verdict uses.
- **STRUCTURAL PUT WALL at −298.6 carries 264k contracts / 1.39bn — the largest
  concentration in the series**, and **PUT WALL ●●●●● 0.68bn at −98.6**, both
  **inside** the budget. P3/H6 may finally get a structural put-wall touch.
- **One High event: Congressional Elections 15:16Z**, plus **JOLTS 15:00Z**;
  `events_24h` populated with **two** rows (D28).
- **`gamma +2` bottom-of-band FIRED** (census 3 right / 4 wrong) — grade the band
  width. **`gexbot` 401 for a 9th consecutive scan** (D27).
- **The AAPL post-close hour (21:00–22:00Z Nov 2, range 110.6, +83.1) is inside
  11-03's pre-scan window**, so 11-03's `today_range` / `adr_used_pct` / budget
  carry it. **D30, first live instance.**

## Journal hygiene

One scan file for 11-02 (`1248-london.json` + `.md`), `is_trading_day: true`,
**264 bars** (**not 276 — see D30**), `review_day` reports **0 test artefacts**.
**09-24 quarantined by hand — 26th consecutive review to carry it**; there is
still no schema `quarantine` field and the 09-29 proposal for one is reaffirmed.
**2026-10-13 has no journal directory — documented, not recreated** (it holds 276
bars and is excluded for want of a scan, not by choice). **2026-08-23, 09-09,
09-24 and 09-25 still have no `REVIEW.md`; none was created and nothing was
back-dated.** **2026-11-03 is on disk, `is_trading_day: true`, 180 bars,
correctly held back and NOT graded.** No fabricated or backfilled entries found.
Journal census from source: **46 directories, 44 with a finished trading-day
scan, 40 with a `REVIEW.md`.** **One ID allocated by this review: D30. Next
free: H28 · D31 · P-J**, confirmed by `grep -n "^## "` before writing, and the ID
allocation block at the head of `HYPOTHESES.md` has been updated in place.

`track.py` **does** emit an `actionable` key (`track.py:187`,
`n_days >= MIN_SESSIONS`) but it is a **global day-count gate, not a
per-hypothesis verdict**, and it emitted nothing — the run produced zero bytes
for the **6th** time. The 3-session rule was applied **by hand, per entry**.
**Two items reached a threshold and are PROPOSED (D30; M6's driver). Every other
item is an existing entry taking a data point, or a threshold resolving to no
model change.**
