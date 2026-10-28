# REVIEW — 2026-10-27 (Tuesday)

_Written 2026-10-28. Grades the single PRE_NY scan `1314-preny` (13:14:12Z,
`is_trading_day: true`, 276 bars). The 10-28 brief was delivered before this ran
and nothing here touched it._

## ⚠️ COMPARABILITY EXCLUSION — applied, and stated so it cannot be missed

The 10-27 trigger fired **27 minutes late**: the scan ran at **13:13–13:14Z with
NY cash 16 minutes away** instead of the usual ~42. Its **pre-scan window is
~26 minutes longer than every other scan in the record**. The 2026-10-27 review
filed this warning in advance, in both files.

**2026-10-27 is EXCLUDED from every pre-scan-keyed statistic in this review and
must stay excluded in future ones:**

- **P-B(b)** — the denominator is **not** advanced. It stays at the 10-26 value
  (21st session). The board did contain one guaranteed double-count window
  (29429.0 / 29422.4, **6.6** apart, inside `TOUCH_TOL = 8.0`, and both touched
  on the **same 13:30 bar**) — **observed and deliberately not entered.**
- **Session-context field census** — not advanced. Stays at 21 sessions.
- **Pre-scan sweep counts / pre-scan contamination flags** — not advanced.
- **Pre-scan range figures** (28:00-equivalents, `range_at_scan = 335.0`,
  `adr_used_pct = 59.6`) are quoted below only as inputs to that day's own fuel
  arithmetic, never as a cross-day observation.

**Not affected and graded normally:** direction, fuel error, level grading, the
bias-component trace, M6, P5, P-E/P-E(b), P-G, H22, H26, H18/P1, P-H, D23,
D25/D26/D27, H2, H10, H23, dead-weight.

---

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | **29318.7 / 29725.3 / 29133.4 / 29642.0** |
| session range · net | **591.9** (1.052x ADR14) · **+323.3** |
| call | **MILDLY BEARISH −3**, `expected_direction −1`, price 29399.8 |
| post-scan move (P-H basis) | **+245.3** → **WRONG** |
| day net | **+323.3** → **WRONG** (bases agree) |
| levels published / touched | **14 / 7** → hit rate **0.50** |
| fuel | budget **227.5** vs extension **256.9** → error **+29.4**, ratio **1.13**, `fuel_call: about right` |
| traversal | **384.5** = **1.69x** budget |
| shape | `PIN_THEN_EXPAND`, 4th firing, **outside the sealed n=3 sample** |
| offset | **−2.4** (cleanest of the month) |
| test artefacts | **0** for the day (6 across the record, excluded by `track.py`) |

`track.py`: **31 days / 32 scans visible**, direction **14 / 11 / 7**;
**13 / 11 / 7** once 09-24 is hand-quarantined.

---

## 2. What the levels actually did

**Touched — 7 of 14, all of them above 29397.**

**29697.6 · STRUCTURAL CALL WALL ●●●●● 1.07bn (+298).** Prose: *"the ceiling for
the WEEK/MONTH, not today. Mark it and leave it: it is where a multi-day rally
runs out of room, **not an intraday trigger**."* **It was the intraday trigger.**
Session high **29725.3**, exceeded by **27.7**, then held as **resistance for 70
minutes** with a worst excursion of **+1.6** and the close settled **55.6
below** it. This is the **first gradeable touch of the structural CALL wall in
the record** (12 publications / 0 touches / never within 200pts as of 10-08;
still 0 as of 10-23) — and it worked, while its own text told the reader to
ignore it. See §4.

**29597.6 · CALL WALL ●●●●● 0.68bn + Options shelf 0.26bn ⭐ (+198).** Prose has
two clauses. Clause 1, *"desks must SELL as price rises into it, so rallies
stall. Take profit into it"* — **wrong**: **sliced by 127.7** on the approach.
Clause 2, *"a held close above flips that selling to buying and it becomes a
launchpad"* — **right**: price settled above it from 15:30 and held for **325
minutes**, worst **−12.5**, acting as **support** into a close 44.4 above. First
instance in the P-E series where the **conditional second clause** is the one
that paid.

**29468.4 · London High (today) (+69).** *"The next session usually runs the
stops above it."* Run at **13:30**, then **support for 390 min**, worst −16.7.
Right, correctly sided.

**29429.0 · Asia High (today) (+29).** Same prose, run on the same 13:30 bar.
Grader prints *"broke DOWN through it — lost by 39.7"*; the close is **+213.0
above**. M6 inversion.

**29422.4 · GAMMA FLIP (+23).** Prose: *"We're BELOW it: they're pushing, so
don't fade. **Reclaim and hold above and fading becomes valid again.**"* Price
reclaimed it at **14:20** and never closed below again — **395 minutes above**,
close **+219.6**. The conditional clause was the correct read of the day; the
score's unconditional `gamma −3` was not (§3). Grader prints *"lost by 33.1"* —
M6 inversion #2.

**29411.0 · PDH + NY High (prev-day) + MAX PAIN ⭐ (+11).** As a support shelf:
**right** — held 395 min, worst −21.7. **As MAX PAIN: wrong, and this is the
first clean test the row has ever had.** The prior ten max-pain observations
were distance-confounded; here it was published **11 points from spot** (the
max-pain input is 29407.6, merged into the PDH row at a 3.4 offset) and price
closed **234.4 above it**. *"Price drifts toward it as the week goes on"*
produced a 234-point drift **away** on a Tuesday. The brief's own *"weak on a
Monday, strong by Thursday/Friday"* hedge does not cover Tuesday.

**29397.6 · Options shelf 0.69bn (−2).** *"Expect price to stall. Good place to
take partials."* Held as **support for 395 min**, worst −8.3. Right — but the
row printed at **−2.2** on a **−2.4** conversion offset, i.e. **inside its own
conversion error**. 4th instance of the 10-12 / 10-16 / 10-22 series; unlike
those, the absolute damage here is ~2 points.

**Never reached — 7 of 14, every one of them below price.** PD close 29301.9
(−98) · STRUCTURAL PUT WALL 29197.6 (−202) · Asia Low 29157.9 · Asia High
prev-day 29148.9 · London Low + PD mid + equal lows 29138.8 · equal lows + NY
Low 29012.8 · PUT WALL 28997.6 (−402). **Post-scan low 29340.8 (14:15Z)**, so
the nearest dead row was **38.9** below it and the furthest **343** below. Half
the board — the half the −3 call was pointing at — was never in play.

**`TOUCH_TOL = 8.0` — checked, and 10-27 is NOT an instance.** The mandate
flagged it as a strong candidate (shelf at −2, three rows inside ±30). It is
not: every row inside ±30 was **touched**, and the nearest untouched row missed
by **38.9**, five times the tolerance. The pattern needs an 8–13 point miss on a
decisive level. **n stays at 2** (10-23's put wall at 31.4; 10-26's PD close at
12.8).

**The ceiling the day actually used was not on the main board.** 29646–29698 was
represented by one main row labelled *"not an intraday trigger"*, one **footnote**
row (*29646 Equal highs ×2*, under *"Beyond today's range, context only, don't
mark"*) and one **secondary-table** row (29647.6). Price traded above 29646 on
**44 of 93** post-scan bars. The footnote relegation used the **228pt budget**
as its test and the realised extension was **256.9**.

**P5 — the secondary gamma table, still graded by no tool, went 2 of 3, and it
again held the best level in the document.**

| strike | published read | outcome |
|---|---|---|
| **29347.6** (−52) | *"dealers LONG gamma — expect a stall and dip-buying, it acts as **support**"* | **RIGHT.** Post-scan low **29340.8**, **6.8** below it, reversal **+384.5** |
| 29497.6 (+98) | *"expect a stall — rallies lose momentum into it"* | **RIGHT on the approach.** Opening spike stalled **29531.0** @13:40 and reversed 190pts |
| 29647.6 (+248) | *"expect a stall"* | **WRONG.** Touched 15:40, exceeded by **77.7** to the session high |

**29347.6 located the day's low to 6.8 points and is not on the main board.**
That is the **second consecutive session** (10-20 was the first) where the best
single level in the brief sat in the ungraded secondary table.

---

## 3. What was wrong, and why

**The score.** `macro −4 · breadth +3 · vol −2`; `gamma 0`, `structure 0`,
`rates 0`, `fuel 0`, `news 0`, `events 0`. Total **−3**, one point past the
deadband.

### (a) The entire bearish content was two readings of one instrument, both two business days stale

`macro −4` is **`DFII10 −3` + `DGS10 −1`** and nothing else. The −3 row's own
text says it: *"up 2bp **as of 2026-10-23**… ⚠️ FRED has not published since
2026-10-23 (2 business days ago) — **this is last week's reading, not today's**."*
The −1 row reads the **same instrument pair** over the **same 10-22 → 10-23
window**, with no ⚠️. Every other macro row scored 0.

So on a Tuesday when NDX futures were **+1.09%** and the mega-caps **+1.29%**,
the only negative evidence on the page was **Friday's bond tape, counted twice**.

**Counterfactuals, arithmetic only:**

| treatment | score | call | graded |
|---|---|---|---|
| published | **−3** | MILDLY BEARISH | **WRONG** |
| H18/P1 collapse rule (drop the smaller member of the duplicated pair, `DGS10 −1`) | **−2** | inside ±3 | **no-call** |
| drop both 10-23-dated rows | **+1** | inside ±3 | **no-call** |

**Neither counterfactual buys a correct call — both buy a no-call.** And on
**10-26** the identical stale pair pointed the **right** way and was outvoted.
This is **H18 / P1 instance 26, duplication 31 of 31**; the **rendering**
proposal stays the live item and **no weight change is proposed**, because the
pair's sign is not stable across the two sessions.

### (b) `gamma` netted exactly zero on the day gamma was the most informative block

`−3` *"below flip 29422.4 by **22.6pts** — SHORT gamma, dealers amplify:
**downside accelerates**"* `+1` straddling `+2` pinning `+0` band = **0**.

The −3 branch awarded a **full-strength direction term** for a distance of
**22.6 points = 0.040x ADR14**. It is the same branch that awarded the same −3
on **10-26** for a distance of **351.2 points = 0.64x ADR**. **The branch has no
distance scaling whatsoever**, and it treats an *amplitude* statement (short
gamma amplifies whatever is happening) as a *direction* statement. 10-26's
review made this finding at long distance; **10-27 is the second consecutive
session and the short-distance mirror of it.** The engine then handed back `+1`
for "straddling, reduce conviction" — a rider that is doing the job the missing
distance term should do, but only once, in integer points, and only inside
0.15%.

Price **reclaimed the flip at 14:20Z and held it for 395 minutes.** The brief's
own regime prose stated the condition — *"reclaim and hold above and fading
becomes valid again"* — and **nothing in the engine reads it forward.** This is
the unarbitrated short-gamma-distance/direction conflict already on the
register; **n=2, no number taken, nothing proposed.**

### (c) The only live, same-day directional input on the page was right and lost

`breadth +3` — *"mega-cap avg +1.29% (3/4 up): NVDA +2.39%, MSFT +1.54%,
AAPL −1.10%, AVGO +2.33%"* and *"NDX +1.09% vs ES +0.29% — tech leading,
genuine risk appetite"*. Both rows correct, both measured **that morning**.
They were outvoted by a Friday bond print. **This is the same shape as 10-26**,
where `structure +2` was the only block that called the day and was outvoted
5-to-2. **n=2 for "the one correct block was outvoted by a stale or
amplitude-misread one"; logged, nothing proposed.**

### (d) `vol −2` split the same way

`VXN 26.4 (−6.7%) +2` is live, same-day, and **right**. Against it:
`VIX9D/VIX 1.01 BACKWARDATED −2`, `VXN/VIX 1.49 −1`, `VVIX 101.43 −1` — three
readings of one vol surface, summing **−4**. The backwardation row's
**amplitude** limb (*"expect range expansion"*) was **right** (range 1.052x ADR,
extension 1.13x budget); only its bolted-on *"downside skew"* direction clause
was wrong. Nothing watches that row's direction clause — **2nd recorded
instance**, unchanged from 10-14.

### (e) H27 — the mandated check, and 10-27 INVERTS the first two observations

| pair / block | 10-23 | 10-26 | **10-27** |
|---|---|---|---|
| vol ↔ breadth | −7 | −3 | **+1** (−2 vs **+3**, opposite signs) |
| structure ↔ gamma | −6 | −3 | **0** (0 and 0) |
| independent remainder | −3 | **0** | **−4** |
| score | −16 | −6 | **−3** |

On observations 1 and 2 the two collinear pairs carried **−13 of −16** and
**−6 of −6**. **On 10-27 they carry +1 and the independent remainder carries the
entire score and more.** The two correlated members pull **opposite ways**, which
is the configuration the entry had not yet seen.

**This is a clean control for H27's ANSWERED-NEGATIVE weight limb.** The
pre-registered collapse rule drops a member only when both subtotals share a
**strict** sign; on 10-27 neither pair qualifies, so collapsing changes **nothing**
and leaves the score at **−3, still WRONG**. The limb stays ANSWERED-NEGATIVE
and **nothing is re-proposed.**

**The rendering limb stays at n=2 and is NOT advanced by 10-27.** The §1 line
*"Driven by: macro −4 · breadth +3 · vol −2"* is, for once, an honest list of
three genuinely different blocks. What it conceals — that `macro −4` is one
instrument read twice and dated two business days earlier — is **H18 / P1's**
complaint, not H27's. Filing it under H27 would inflate that entry with a case
it does not own.

### (f) `PIN_THEN_EXPAND`, 4th firing — post-verdict observation ONLY

The test is **CLOSED, FALSIFIED 3 of 3** and **P-I** is the live proposal.
**10-27 is outside the sealed sample, the test is not re-opened, and this
changes the verdict neither way.** For the record, run on the same windows:

| window | range | abs net | high | low |
|---|---|---|---|---|
| **pre** 13:30–17:00Z | **378.0** | **245.7** | 29718.8 @16:00 | 29340.8 @14:15 |
| **post** 17:00–21:00Z | **115.6** | 15.5 | 29725.3 @19:45 | 29609.7 @18:00 |

**Consistent with the three in character:** the morning window held **3.3x** the
range and **16x** the directional move. **One difference:** the closing-side
extreme (high @19:45Z) fell in the **late** window, where on all three sample
days it did not — but the late window added only **6.5 points** of new high over
four hours above the 16:00Z level. The *"breakouts will fail while the pin
holds"* limb takes the same shape as observations 1 and 2: the 13:30 break above
the pre-scan high ran to 29531.0, failed back **190 points** to 29340.8
(supports by the letter), and then the 14:20 reclaim **ran 384.5**.

### (g) M6 — session 33, 2 of 7 inverted, both off ONE bar

| level | settled_side | printed verdict | close vs level |
|---|---|---|---|
| 29429.0 | above | *broke DOWN through it — lost by 39.7* | **+213.0** |
| 29422.4 | above | *broke DOWN through it — lost by 33.1* | **+219.6** |

Both verdicts come from the **same low, 29389.3 on the 14:25 bar**. For both
levels `last_far = 14:20`, so the settle window **opens with the 14:25 bar** —
the bar that **opened 29395.6 and closed 29454.0**, i.e. the reclaim bar itself,
and its opening wick fails the level against a fixed `SETTLE_TOL = 25.0`
(**0.044x** of a 562.5 ADR). **2 of 2 here match session 32's measured
mechanism** (worst excursion on the bar immediately after `last_far`). This is
the `settled_read` origin defect already recorded at ~5535 / ~6061 / ~7054 and
is **not reopened**. **The driver of the M6 series is recorded as UNKNOWN** —
travel-scaling failed four sessions and window placement failed too; neither is
restated as an explanation.

### (h) The news engine scored nothing from 135 headlines

`0 auto-scored, 0 bull / 0 bear, NEUTRAL`, with **56 of 135 relevant** left for
judgement. Coverage **0.0% of raw / 0.0% of relevant** — the first zero-score
day in this stretch. Given the engine's last three graded false positives
(D9 instances 2 and 3; D18 instances 15/16), **a zero is the correct outcome on
a day whose feed was genuinely directionless** — the judgement list is
chip-rally and Fed-preview noise, with one `[risk_off]` correctly deflected as
hypothetical. **Logged against D9/D18 as the counter-example the entries lacked:
the gate that produced three false tags also produced a clean zero. n=1 as a
control; nothing proposed.**

---

## 4. Change proposals

`track.py` **no longer prints a literal `actionable: YES/NO`** — it prints
*"threshold met, read the evidence before proposing"*. **The 3-session rule was
therefore applied by hand, per entry**, and is stated for each item below.

### ID allocation — `grep -n "^## "` run first

Confirmed **H28 · D28 · P-J** all unused as headings before anything was
written. Highest allocated was **H27 · D27 · P5 and P-I**. **This review
allocates ONE number: D28.** Next free after it: **H28 · D29 · P-J.**

---

### PROPOSED — **D28 (NEW)**: a missing calendar renders as a positive factual claim

**What to change.** `journal.py:102` is
`"events_24h": (mc.get("calendar") or {}).get("upcoming_next_24h")`. When the
calendar block is **absent** from the macro context the field is **`null`**;
when the fetch succeeded and nothing is in window it is **`[]`**. **Section 5
renders both as the same sentence** — *"No High/Medium US events in the next
24h."* **Propose: print *"⚠️ economic calendar unavailable — event coverage is
unknown for this scan"* when the field is `null`, and reserve the existing
sentence for `[]`.** Rendering only.

**Evidence — 6 sessions, from the pipeline's own records.**

| day | `events_24h` | section 5 printed | a real event was in the window? |
|---|---|---|---|
| 08-24 | `null` | *"No High/Medium…"* | **YES** — Treasury Sec Bessent Speaks 18:00Z (Medium), carried in another scan's own `events_24h` |
| 08-27 | `null` | *"No High/Medium…"* | not demonstrable from the pipeline |
| 10-09 | `null` | *"No High/Medium…"* | not demonstrable from the pipeline |
| 10-21 | `null` | *"No High/Medium…"* | not demonstrable from the pipeline |
| 10-22 | `null` | *"No High/Medium…"* | not demonstrable from the pipeline |
| **10-28** | `null` | *"No High/Medium…"* | **YES — the FOMC rate decision**, 5 hours ahead of the 12:52Z scan |

**6 of 61 trading-day scans, 3 of them in the last 6 sessions.** The defect — a
positive assertion made without data — fires on all **6**. The *harm* (a real
event in the window) is demonstrable on **2**, and **nothing is proposed on the
harm count.**

The 10-28 case is airtight from inside the document: the judgement list carries
*"Fed meeting live updates: No hike expected, but all eyes on Warsh for what's
next"* and a `[fomc_event]`-tagged *"Dow Falls Ahead Of Rate Decision, Warsh
Comments"*, while section 5 says there is nothing. The feed **does** cover FOMC
— on **09-16** the pipeline carried *FOMC Statement*, *Federal Funds Rate*,
*FOMC Economic Projections* and *FOMC Press Conference*, all tagged High. It
simply returned nothing on 10-28.

**Expected effect: no score change.** The `events` component is
`add("events", 0, …)` over `heavyweight_earnings_next_5d` only (P-C), and the
gate stays `None`. The brief stops claiming knowledge it does not have.

**Explicitly NOT proposed:** any score term, any gate change, any second
calendar source. One missing-feed day is not grounds for a new dependency.

**This is NOT D24, and D24 does NOT clear anything on 10-28.** D24 is the
**forward-only filter** hiding an event that **already fired** before the scan
(NFP 10-02, CPI 10-14 — both with a populated `events_24h`). 10-28's FOMC was
**five hours ahead** of the scan and absent because **the calendar block was
absent entirely**. **D24's own proposed fix — a "released in the last 6h"
block — would not have caught it.** D24 stands where it has stood since
2026-10-05: **threshold met at 4 sessions, PROPOSED, unactioned**, with the
10-14 CPI worked example. It gains **no instance** from 10-28.

---

### CORRECTION to a live recommendation — P3 / H6: do not act on *"stop publishing the structural CALL wall"*

Not a new claim and **no number taken** (the 10-19 precedent: a correction to a
live proposal belongs to the entry that owns it).

The standing narrowing — *"'stop publishing it' applies to the structural CALL
wall only"* (10-08, reinforced 10-23) — rests on a census of **12+ publications,
0 touches, never within 200 points**. **On 10-27 it took its first gradeable
touch and it worked**: published at **+298 (0.53x ADR)**, the session high
exceeded it by 27.7, it then held as **resistance for 70 minutes with a +1.6
worst excursion**, and the close settled **55.6 below** it. **It defined the
day's high.** Its own prose — *"not an intraday trigger"* — argued against using
the best ceiling in the document, the same self-defeating text the structural
**put** wall carried on 10-23.

**n=1 on the call side. Nothing is proposed either way, and the recommendation
must not be actioned on a census that now has a counter-instance in it.** The
census is re-stated as: **structural CALL wall — 1 touch, 1 worked; structural
PUT wall — 2 touches, 2 worked.** Three touches, three successes, across both
sides. Revisit at 3 call-side instances.

---

### Nothing else is proposed. Observations appended to existing entries

- **P-H — no 6th deciding instance.** Post-scan **+245.3 WRONG**, day net
  **+323.3 WRONG**; the bases **agree**. **13/24 = 54.2%** vs **14/24 = 58.3%**;
  deciding set stays **n=5**; the convention's cost **4.3 → 4.2**.
- **H26 — a 3–5 bucket instance and a MISS.** |score| **3**, |post|/ADR
  **0.436**, range/ADR **1.052**. The 3–5 bucket goes **4/7 → 4/8 = 50.0%**.
  ≥10 untouched at **3/7 = 42.9%**; 6–9 untouched at **6/9 = 66.7%**; **direction
  is still INVERTED at the top.** Derived bucket means on |post|/ADR:
  **0.181 / 0.351 / 0.507 / 0.704** — **monotonicity survives, 9th consecutive
  session** — but these are **extrapolated from the n=29 source re-derivation
  plus two days and must be re-derived from source next session, not quoted
  from here.** **The range/ADR monotonicity claim stays RETIRED and is not
  restated.** No Spearman quoted.
- **H18 / P1 — instance 26, duplication 31 of 31**, and the **first day where the
  stale pair was the ENTIRE score**. `DFII10 −3` (obs 10-23, ⚠️ printed) +
  `DGS10 −1` (same 10-22→10-23 window, **no ⚠️**) = the whole of `macro −4` = the
  whole of a −3 call. Collapsing it buys a **no-call**, not a correct call, and
  **10-26's instance pointed the opposite way**. **The rendering proposal stays
  live; no weight change is proposed.**
- **H27 — observation 3, and it INVERTS observations 1 and 2.** See §3(e).
  Weight limb **ANSWERED-NEGATIVE, re-confirmed by a clean control** (the
  collapse rule drops nothing when the pair signs disagree). **Rendering limb
  stays n=2 — 10-27 does not advance it.**
- **H1 / P4 — n=31 days, error +29.4**, per-day mean **52.1 → 51.4**.
  Traversal/budget **1.69x**. **This is the sixth value published under one
  series name (see D26) — flagged, not averaged.**
- **H2 — clean NON-instance.** `MODERATE`, `fuel_ratio` **1.19**; the scan does
  not appear in `track.py`'s low-fuel list. Census stays **6–2 / 8–0**. Also a
  **control** on the two-opposite-instructions cell: §2 (*"Fading is the wrong
  trade today"*) and §3 (*"take partials into it"*) **do not contradict**,
  localising that defect to the LOW_FUEL/EXHAUSTED branch a **3rd** time.
- **H10 — clean CONTROL.** Price **inside** the prior-week range
  (28820.4–29936.0); the −3 branch did not fire. Stays **2-for-8**, proximity
  gap unaddressed at 3 instances.
- **H22 — n=13 → 14, label WRONG.** Week net GEX **+1.459** → *"pinning
  likely"*; realised range **1.052x ADR**. Also: the **VXN-implied 488.9**, which
  the brief told the reader to prefer as *"the smaller budget"*, was beaten by
  **103 points**.
- **H23 — instances 18 and 19, both brakes reachable and this time they do NOT
  split.** Downside named brake **29397.6** (2pts away): **sliced by 56.8** to
  the 14:15 low. Upside **29597.6** (198 away): **sliced by 127.7**. On the
  settled read both **held**. Slice-basis census **11/3/3 → 13/3/3**.
- **H8 — post-closure, and OUTSIDE.** Published straddle band
  **29179 .. 29620**; close **29642.0**, out by **22.0**.
- **H4 — an instance, and negative.** The flip was touched, lost, reclaimed, and
  the close finished **219.6** away from it. Not a settlement magnet today.
- **P-E / P-E(b) — instance 16, and a FIRST.** The call wall with an options
  shelf stacked at the same price was **sliced** on the approach and **held as
  support** afterwards; the shelf again did not separate the two outcomes
  (P-E(b) #17). **First instance where the prose's conditional *"a held close
  above makes it a launchpad"* clause is the one that paid** — recorded because
  P-E's complaint has always been that the prose *asserts a lid*, and today the
  lid clause failed while the conditional succeeded.
- **P5 — 2 of 3 gradeable, and the table again held the best level on the
  page.** See §2. Still graded by no tool. **Second consecutive session** (with
  10-20) where the single best level was in the secondary table.
- **P-G — instance #33.** `29148.9 Asia High (prev-day)` printed *"the next
  session usually runs the stops **above** it"* while sitting **251 points
  below** price. Mirror of #14/#15/#24/#25.
- **Max pain — the FIRST clean, non-distance-confounded test in the record, and
  it FAILS.** Published **+11** from spot; close **+234.4** away. The prior ten
  observations were all distance-confounded non-tests. **n=1 clean; nothing
  proposed** — one clean instance against ten voids is not a census.
- **D23 / realised basis — observation 10, and NO residual for a FOURTH
  consecutive session.** §7 did not render on 10-22, 10-23, 10-26 **or 10-27**
  (sections 1–6 only, confirmed by grep). **No residual is inferred.** **D25
  stays interrupted at 29.**
- **D26 — the held-back set did NOT rotate, second consecutive session.**
  `track.py` sees **31 days / 32 scans**, up from 30 / 31; 10-27 entered and
  nothing left. On disk there are **40 finished trading days** (08-24 … 10-27)
  of which **9 (08-24 … 09-11) remain invisible** past the 45-day bar window.
  **Visible 31 vs on-disk 40 reported as two numbers; the conflict stays
  flagged and nothing is averaged.** H1/P4 now has **six** values under one
  series name.
- **D27 — 5th consecutive 401** on `/v2/NDX/classic/gex_full`
  (*"volume-weighted view unavailable"* at `1314-preny.md:158`, and **again on
  the 10-28 scan**, `1252-preny.md:158`). Both ladder files lost again; D25's
  false sentence still suppressed rather than fixed. **Nothing proposed.**
- **`gamma +2` bottom-of-band — NOT a firing, and not counted as one.** 10-27's
  band row is `gamma +0 — price mid-band (28997.6-29597.6), **67%** up the
  range`: a **near-miss control**, exactly as on 10-26. **The branch stays at
  6 firings, census 3–3, prose contradiction 6 of 6, zero sign changes.**
- **Board offset — 4th instance of a level printing inside its own offset.**
  Offset **−2.4**; the 0.69bn shelf published at **−2.2**. Unlike 10-12 / 10-16 /
  10-22 the offset itself is tiny, so the damage is ~2 points. **The
  offset-vs-options-proximity hypothesis stays NULL and is not revived.**
- **Dead-weight audit.** `events` **0 on 4 of 4**; `rates` **0 on 2 of 2**;
  `news` 0; NFCI, WALCL/RRP, the yield curve **and HY OAS** all 0. **13 of 27
  rows scored zero.** The narrowed standing proposal is unchanged and still not
  actioned.
- **Watch item, *"the whole move was over by 10:30 ET"* — COUNTER-INSTANCE.** The
  post-scan low was **10:15 ET** and the +378 leg ran **10:15 → 12:00 ET**. The
  item does not extend; it stays an ID-less watch note.
- **No instance:** **H7** (no overnight scan) · **H11** · **H12 / H13** (volume
  ladder lost to the 401) · **H14** (put wall 402 below, never approached) ·
  **H17** (post-scan 41.5% of session range, far outside the 5% deadband; stays
  **2 of 3**) · **H20** (CLOSED-NEGATIVE, not revived) · **H3** (CLOSED-NEGATIVE,
  superseded by H26 — **not re-opened**) · **D24** (see above; `event_gate: null`
  correct, four earnings all forward) · **P-F** (price 11.2 **below** PDH, inside
  the prior-day range — an inside-control with error +29.4; **the control is not
  re-derived and no control figure is quoted**) · **D22** · **D21** · **the
  gamma-outvoted cell** (gamma netted **0**, so there was no gamma vote to
  outvote; stays **n=5**) · **D7** (footnote held 4 rows against a cap of 6,
  nothing truncated).

### No new data point is warranted

Every failure on 10-27 is a **staleness**, **sign** or **distance** problem in
rows that were already on the page. The bearish case was Friday's real yield
counted twice; the bullish case that was right — NDX +1.09% vs ES +0.29%,
mega-caps +1.29% — was printed two rows below it and lost 4-to-3; the gamma
flip's reclaim condition was printed in prose and read by nothing; the day's
low was located to 6.8 points by a strike in the ungraded secondary table.
**No free, reliable external feed fixes any of those — the numbers the engine
needed on 10-27 were all inside the scan.** The one genuine data **gap** found
this cycle is the **missing calendar on 10-28**, and the fix for that is to stop
asserting its absence (D28), not to buy a second feed.

---

## Carried forward from the 2026-10-28 scan — recorded, NOT graded

- **🔴 FOMC rate decision day, and section 5 says there are no events.**
  `events_24h: null`, `event_gate: null`, section 5 prints *"No High/Medium US
  events in the next 24h"*, while the judgement list carries two FOMC headlines
  including a `[fomc_event]`-tagged one. **Opened as D28 above. It is NOT a D24
  instance** — different mechanism, and D24's proposed fix would not have caught
  it.
- **D18 negation failure, same shape as the 10-12 instance.** *"Federal Reserve
  likely to **skip** rate hike as elevated inflation drives voters to the polls"*
  → **[hawkish] → "Hawkish repricing -> bearish long-duration tech"**,
  ~180pts / 90min. **Skipping a hike is dovish.** Graded on the D9 convention,
  reason and score separately: **reason FALSE**; **score** — it carries −1 of a
  −2 `news` block inside a **+6 BULLISH** call, so removing it gives **+7**, or
  **+8** if the surviving `[tariff_general]` tag is also judged non-scoring.
  **The call does not change side**; the error **shrank a bullish call**, which
  is the conviction-reducing direction. To be entered as **D18's 10th trading
  day / 17th headline instance** when 10-28 is graded. Nothing proposed — D18
  already carries live proposals.
- **Regime FLIPPED.** 10-28 is **ABOVE** the flip (29679.2, price 29746.5,
  **+67.3**), **long gamma**, shape **`COHERENT_LONG`**, **STRATEGY 1** — the
  first fade day in some time — at **+6** (a **6–9** bucket instance), offset
  **−2.9**, week net GEX **+2.12**.
- **Fuel `ROOM_TO_EXPAND`**, `fuel_ratio` **0.79**, budget **373.4**, ADR14
  **578.0**, 35.4% used — **the first ROOM_TO_EXPAND state in this stretch.**
- **`gexbot` HTTP 401 for the 5th consecutive scan** (appended to D27 above).
- **No §7** on 10-28 either; no residual inferable, **D25 stays interrupted at 29**.

## Journal hygiene

One scan file for 10-27 (`1314-preny.json` + `.md`), `is_trading_day: true`,
276 bars, `review_day` reports **0 test artefacts** for the day (6 across the
record, excluded by `track.py`). **09-24 quarantined by hand — 22nd consecutive
review to carry it**; there is still no schema `quarantine` field and the 09-29
proposal for one is reaffirmed (`track.py` prints direction **14 / 11 / 7** and
still scores 09-24 CORRECT, so the hand-carried figure is **13 / 11 / 7** over
31 days). **2026-10-13 has no journal directory — documented, not recreated.**
**09-09 and 09-25 still have no `REVIEW.md` and none was created or
back-dated.** **2026-10-28 is on disk, `is_trading_day: true`, 184 bars,
correctly held back and NOT graded.** **No `prediction` block was touched. No
scoring, wall or grading code was edited.** No fabricated or backfilled entries
found. **One new ID allocated by this review: D28. Next free: H28 · D29 ·
P-J.** `track.py` prints **no literal `actionable: YES/NO`** — it prints
*"threshold met, read the evidence before proposing"* — so the 3-session rule
was applied by hand, per entry.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
