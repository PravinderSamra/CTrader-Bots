# REVIEW — 2026-10-15 (Thursday)

_Graded 2026-10-16 from `review_day.py 2026-10-15 --json` and `track.py`. One
PRE_NY scan, `is_trading_day: true`, **0 test artefacts** for the day (6 across
the record, excluded by `track.py`). **There is no `2026-10-13` journal
directory — Tuesday's scheduled scan never ran. Nothing was created, back-dated
or inferred; the series skips 10-12 → 10-14.** 09-24 remains quarantined by hand
(13th consecutive review; there is still no schema `quarantine` field). 2026-10-16
is excluded from every statistic below — `track.py` holds it at 180 bars._

> **Three figures in the brief as summarised to this reviewer are wrong and are
> corrected here before anything is built on them.** (a) The published score is
> **−7**, not −6 — `prediction.bias_score: -7`, and the brief's own header reads
> *"The call: BEARISH (score -7)"*; the component list sums to −7
> (−5+4−4+3−3−1−1). (b) 10-15 is **not** the most extreme fuel reading in the
> series: 97.5% of ADR used ranks **6th** (09-17 136.0%, 09-11 127.2%, 09-24
> 105.0%, 10-01 100.2%, 09-11 97.7%), the 11.5pt budget ranks **6th smallest**
> (four scans printed 0.0), and `fuel_ratio` 2.17 ranks **5th-equal** (3.02 /
> 2.54 / 2.33 / 2.23 / 2.17). It is a severe EXHAUSTED reading, not the most
> severe. (c) HY OAS scoring **−2 on 10-16 is not a first** — the row scored
> **+2 on 19 consecutive scans** (08-24 → 09-28) and **−2 on six** (09-29 →
> 10-06) before six zeros (10-07 → 10-15). See §4.

## 1. Scoreboard

| | |
|---|---|
| Session (276 M5 bars, 22:00Z → 20:55Z) | O **29945.8** / H **29996.8** / L **29423.7** / C **29885.3** |
| Range / net | **573.1** (**1.25x** ADR14 457.0) · net **−60.5** |
| Scan | PRE_NY 12:47:20Z at **29638.7** · bias **−7 BEARISH** · `expected_direction −1` · `COHERENT_SHORT` high confidence · regime **BELOW** flip 30626.0 by 987.3 |
| Direction | **0 right / 1 wrong / 0 no-call.** Post-scan move **+283.7 → WRONG** (P-H basis). Day net **−60.5 → CORRECT**. **The two bases disagree: this is a P-H deciding instance, census n=3 → n=4** (09-11, 09-16, 10-07, 10-15) |
| Pre-scan | H **29958.2** / L **29512.7** · range **445.5** · price sat **126.0 above** the pre-scan low, **28.3% up** the pre-scan range — above the 15–17% band of the four H3 instances, and the score is not max-conviction, so **no H3-shaped instance** |
| Post-scan path | L **29423.7** at 13:55Z (**−215.0** from the scan, a new low by **89.0**) → H **29996.8** at 19:45Z (**+573.1** off the low, new high by **38.6**) → C 29885.3 · traversal **573.1** |
| Levels | **6 published, 2 touched, hit rate 0.33** |
| Fuel | budget **11.5** · extension **127.6** · err **+116.1** (**11.1x**, UNDER-estimated) · traversal **573.1 = 49.83x** budget — **the largest finite traversal/budget ratio in the record** (prior 09-21 35.3x) |
| Vol boundaries | VXN-implied range **423.8** vs realised **573.1** → under by **149.3** (realised **1.35x**). Straddle EM band **29210 .. 30067**: close **29885.3 INSIDE**, high inside by 70.2, low inside by 213.7 |
| Blocks | gamma **−5** · macro **+4** · structure **−4** · rates **+3** · breadth **−3** · vol **−1** · news **−1** · fuel **0** · events **0** |
| Board offset | **+77.6** — the largest non-quarantined reading in the record (next: 09-28 45.9, 10-12 43.1, 10-14 41.8). Section-7 conversion on the same page **−346.8**: the two disagree in sign |

## 2. What the levels actually did

**Touched (2 of 6).**

| level | dist | brief said | what happened | verdict |
|---|---|---|---|---|
| **29627.6 STRUCTURAL PUT WALL ●●●●● 1.87bn / 164k** | **−11** | *"the biggest concentration on the chain — the floor for the WEEK/MONTH… where a multi-day sell-off is defended, not an intraday trigger"* | first touch 12:50Z, chopped both sides, price traded **203.9 below it** (low 29423.7), then recovered and closed **257.7 above**. `review_day` grades it *"broke DOWN through it — lost by 60.4pts"* | **UNGRADEABLE on placement — see below.** On behaviour: the breach was real and the recovery was real |
| **29977.6 MAX PAIN** | +339 | *"price drifts toward it as the week goes on. Weak on a Monday, **strong by Thursday/Friday**"* | reached 19:25Z **on a Thursday**, exceeded by only **19.2**, held as resistance 70 min, closed **92.3 below** | **the first success in three within-reach tests** (09-16 Wed and 10-14 Wed both failed). It capped the day to within 19.2pts |

**The structural put wall cannot be graded by this day, and this review does not
grade it.** It was published **11.1pts** from spot on a board carrying a
**+77.6** offset — the level's own uncertainty is **7x its published distance**.
The only directly observable basis for the same session (§3) came in at **−50.3**,
i.e. the wall's true CFD price could be ~**128pts** from where it printed. A
±128pt box around 29627.6 spans 29500–29756, and price traversed that whole box
repeatedly in both directions. Nothing the day did distinguishes "the wall held"
from "the wall was never where the brief said it was". This is the **second**
instance of a board level printing inside its own offset (10-12's put wall was
the first); `|px − flip| < |offset|` stays **n=1** (10-12) — today the flip was
987 away, 12.7x the offset, so the **regime call was formally determined and
correct**.

**Untouched (4).** STRUCTURAL CALL WALL 31377.6 (+1739) and GAMMA FLIP 30626.0
(+987) were never in play. **CALL WALL 30077.6 (+439) was missed by 80.8** — the
brief called it *"heaviest ceiling this week… rallies stall"* on **●●○○○ 0.38bn
/ 3k contracts**, a near-vestigial wall, and the day topped out below it at a
level the board did not name as a ceiling (MAX PAIN did the capping instead).
**PUT WALL 29377.6 (−261) was missed by 46.1** on the session low — the only
level of the six that was approached and not reached.

**The named downside brake failed, and this is the instance that hurts the
proposed fix.** §3 of the brief said *"DOWNSIDE path: has friction. Expect a
stall at **29577.6** (61pts away) — take partials into it rather than assuming a
clean breakdown."* Price touched it at 12:55Z and was **153.9 points below it
within 60 minutes**. H23's running census becomes **9 sliced / 1 capped, n=10
over 8 sessions** (never-reached 2). The register's standing proposal is to rank
`path_read()`'s brake by **gamma force** instead of distance (`brief.py:486`
takes the first positive-sign shelf off a distance-sorted list with no size
test). **Today that fix changes nothing**: 29577.6 was simultaneously the
nearest positive-sign shelf *and* carried **3.94bn**, the largest force figure
in the series, off only 5,096 contracts. In fact it was the **only** positive-sign
shelf within 1.2x ADR below price, so distance-ranking and force-ranking had no
choice to make. **The brake with the most force ever published was sliced by
2.5x its own distance.** That is a counter-instance to the mechanism, not a
confirmation of it, and it should temper the proposal.

**The corridor terminus was right for the fourth time, and this is the first
upside instance.** *"UPSIDE path: clear. Every options shelf from here to
**29977.6** (339pts, 0.74x ADR) is negative gamma — nothing structural to slow a
breakout."* Realised post-scan high **29996.8 — exceeded by 19.2 (0.042x ADR)**,
on the same page as a budget that was out by **116.1 (11.1x)**.

| day | budget | realised ext. | budget err | corridor terminus | realised extreme | terminus err |
|---|---|---|---|---|---|---|
| 10-08 | 115.6 | 326.2 | 2.82x | 30559.6 (398pts, 0.86x ADR) | low 30568.7 | −9.1 |
| 10-12 | 169.5 | 175.9 | 1.04x | 30643.1 (200pts, 0.46x ADR) | low 30634.7 | +8.4 |
| 10-14 | 97.6 | 476.4 | 4.88x | 29941.8 (464pts, 1.08x ADR) | low 29877.9 | +63.9 |
| **10-15** | **11.5** | **127.6** | **11.1x** | **29977.6 (339pts, 0.74x ADR)** | **high 29996.8** | **+19.2** |

Four sessions, terminus error |9.1| / |8.4| / |63.9| / |19.2| — all inside
0.15x ADR; budget error 2.8x / 1.0x / 4.9x / 11.1x on the same four pages. Not a
disguised ADR multiple (0.86 / 0.46 / 1.08 / 0.74).

**The secondary gamma table had its worst session on record — 2 of 6.** It is
still graded by no tool (P5). Measured as: first post-scan touch (±8pt), then the
next 60 minutes.

| shelf | force | what it claimed | next 60 min | verdict |
|---|---|---|---|---|
| 29577.6 | 3.94bn | *"dealers are LONG gamma… damp moves: expect a stall and dip-buying, it acts as **support**"* | **−153.9** / +81.1, approached from above | **WRONG** |
| 29477.6 | 0.59bn | *"amplify… accelerate THROUGH rather than stall. **Not a floor**"* | approached from above, fell only **−53.9** further (the session low) then **+193.4** | **WRONG — it was the floor** |
| 29827.6 | 0.72bn | *"accelerate THROUGH… not a floor"* | from below: **+33.5** then **−80.4** — it stalled the rally | **WRONG** |
| 29877.6 | 1.11bn | *"accelerate THROUGH… not a floor"* | from below: **+21.8** then **−134.3** — it capped | **WRONG** |
| 29677.6 | 0.88bn | *"accelerate THROUGH"* | from below: **+157.1** before any −25 retrace | right |
| 29727.6 | 0.60bn | *"accelerate THROUGH"* | from below: **+133.5** | right |

Caveat stated before the number is used: on a day with one 573pt directional
leg, *every* shelf in the path is sliced almost by construction, so the two
"right" verdicts are nearly free. The informative rows are the three where price
**turned** — 29477.6, 29827.6, 29877.6 — and all three behaved the opposite way
to the printed note. The put-dominant *"not a floor"* claim is asserted in every
brief and today it was wrong at the one strike that mattered.

## 3. What was wrong, and why

**The call was right for 68 minutes and 215 points, then wrong by 573.** Price
made a new low at 13:55Z (89.0 below the pre-scan low) and reversed. No single
component caused this; the honest reading is that the engine was broadly bearish
on a day that was not, and **no minimal counterfactual rescues it**. The label
threshold is −3 for a call (`bias_engine.py:268-271`), so the WRONG call survives
removing breadth (−7 → −4, still BEARISH), and survives removing breadth **and**
news (−3, still a call). **Five of the fourteen bearish points have to go before
the call becomes a no-call.** Nothing in the register's open defect list is worth
five points.

What can be traced:

- **`breadth −3` described Wednesday.** *"mega-cap avg −1.89% (1/4 up): NVDA
  −3.16%, AVGO −3.10%"* and *"NDX −2.02% vs ES −0.37%"* are **10-14 closes**,
  printed 43 minutes before Thursday's cash open, on a day the index then
  rallied 573.1 off its low. This is **D22** with damage for the first time:
  3 of the 7 net points, and the single largest bearish block after gamma,
  came from a one-session-stale, mean-reverting window. (It is not decisive on
  its own — see the counterfactual above.)
- **`gamma −5` was half right and half wrong, and the half that was wrong is the
  tradeable half.** *"Expect range expansion and trends that persist"* — realised
  1.25x ADR, correct. *"Sweeps tend to keep running rather than fail… Fading is
  the wrong trade today"* — the downside sweep of the pre-scan low ran **89.0
  points and then failed completely**, and the upside sweep of the pre-scan high
  ran **38.6** before closing 111.5 back inside. **Both sweeps failed. Fading
  both extremes was the day.**
- **`structure −4`** fired its usual pair. The `−3` *"below the entire prior-week
  range"* branch fired for the 6th time; PWL 30568.7 was never approached within
  571.3, so **H10's proposed reclaim condition would not have changed today's
  call** (same as 10-14). On the post-scan basis the branch is now **1-for-6**.
- **`macro +4` and `rates +3` were the only rows pointing up, and the day went
  up.** The +4 came entirely from two **stale FRED** rows (DFII10 and DGS10, both
  resolving to observation date 2026-10-13, two business days old, in a document
  headed *"today"*). **H18/P1 instance 19; duplication 24 of 24.** The
  consequence cuts against the age-gate proposal: suppressing the stale pair
  would have taken the score from **−7 to −11**, crossing the saturation point
  into *"STRONGLY BEARISH"* and making a wrong call bigger and louder. That is
  the **second** time the gate would have hurt (10-07 was the first), against two
  times it would have helped. The accuracy case stays **retracted**.
- **`news −1`: right-signed on the day net, wrong-signed on the basis we grade
  on, and the size is the established defect.** Raw −2.55 → `round(−2.55/2) = −1`
  (`news_scorer.py:380`). The six "headlines" are **three events**: the 10-14 CPI
  print (×2 — *"CPI comes in hot"*, *"US inflation heats up in September"*),
  reinforced by a third derivative of it (*"Warsh… as Hot Inflation Spurs Rate
  Hike Bets"*); TSMC record profit (×2, the same earnings report); CoreWeave
  (×1). **Two of the four bears are a re-report of an event that printed at
  12:30Z the previous day** — a D20 (freshness) shape, and the same event the
  10-14 brief already scored. **Yes, cancelling TSMC against CPI lost
  information**: the TSMC beat was the only *new*, index-weighted, forward-looking
  item in the set, and the index spent the afternoon rallying while the CPI was
  24 hours old and already traded. The scorer has no way to express "four
  headlines, one event, already in the price", because its magnitude is a
  function of **match count** (H19). **H19 instance appended. This is not D18:
  every sign was right** — including *"TSMC's CEO sees no sign of a slowdown"*,
  which contains a bearish keyword inside a negation and was still classified
  bullish. **D18 stays at 13 headline instances / 7 trading days.**
- **The fuel block and the gamma block gave opposite instructions, and for the
  first time the register's own column and the register's own claim disagree
  about who won.** The brief printed *"Fading the extremes back into the range
  is the higher-probability side here, **even when the gamma regime favours
  continuation**"* — an explicit instruction to override the regime — four
  sections below *"**Fading is the wrong trade today**"*. On the census column as
  written (**extension vs budget**), 10-15 reads **127.6 vs 11.5 = 11.1x** and
  scores to **gamma**, making the census **5–1**. On what the two sentences
  actually tell a trader to do, **the fuel block won outright**: fading the break
  of the pre-scan low returned **+573.1** and fading the break of the pre-scan
  high returned **+111.5**, while continuation lost on both. **The column is
  measuring range arithmetic and the claim is about trade selection; they have
  now come apart, and the census as printed cannot be read as evidence for either
  side until the column is re-specified.** Recorded as a measurement defect in
  the register, not as a model change.
- **M6, session 25.** Both touched rows were decided by `bars[-1]["close"]`, and
  the put-wall verdict is understated by a factor of **3.4**: `review_day` reports
  *"broke DOWN through it — lost by **60.4**pts"* when price traded **203.9**
  below the level. The excursion window opens at `settled_from 14:30` and the low
  was at **13:55** — the settle logic starts measuring after the move it is
  supposed to measure. **Said explicitly as directed: M6's magnitude scales with
  how far the day travelled; 10-15 travelled 573.1 = 1.25x ADR**, so this is a
  mid-scale instance, and the 3.4x understatement at mid-scale is worse than the
  0.108 mean-ratio signature recorded at 1.88x ADR on 10-14.

**The board offset: the time trend survives arithmetically and explains
nothing.** The previously-quoted figures reproduce exactly (r = **+0.607**,
slope **+1.679**/session, R² **0.369**) — on the sample the 10-14 review used,
which was **n=27 first-scan-per-day, ex-09-24, and which already included
10-15's +77.6**. The trend was therefore fitted on the breach it was being used
to explain. Adding 10-16:

| sample | n | r | R² | slope | resid SD |
|---|---|---|---|---|---|
| thru 10-14 | 26 | +0.541 | 0.293 | +1.310 | 15.9 |
| thru 10-15 (register's) | 27 | **+0.607** | 0.369 | +1.679 | 17.8 |
| **thru 10-16** | **28** | **+0.572** | **0.328** | **+1.499** | **18.0** |
| thru 10-16, 10-15 removed | 27 | +0.517 | 0.267 | +1.181 | 15.8 |

**Plainly: the trend survives as a descriptive statistic and fails as an
explanation.** Out of sample, the line fitted through 10-14 predicted **31.1**
for 10-15 (actual **77.6**, residual **+46.5**) and **32.4** for 10-16 (actual
**14.9**, residual **−17.5**). Its residual SD (18.0) is larger than the median
offset of the whole series. As a correction rule it does not beat a constant: over
the last 10 sessions MAE(trend) **18.8** vs MAE(constant 11.9) **18.0**. A single
point (10-15) supplies ~27% of the slope. **The 77.6 is not explained by a drift,
it is not explained by the sell-off hypothesis (falsified 10-15), and it is not
explained by staleness or a contract roll. We do not know what causes it.** That
is the finding; no third story is being substituted.

**The pre-registered realised-close-basis log, observation 2 of 10.** NDX cash
closed **29935.6** on 10-15 (recovered from the 10-16 brief's own
`implied 29863.1 − roll −72.5`); the CFD closed **29885.3**; realised
CFD-minus-cash basis **−50.3** against a scan-time board offset of **+77.6** —
**opposite sign, gap 128.0**, more than double 10-14's 60.8.

| day | scan offset | realised close basis | gap | NQ roll |
|---|---|---|---|---|
| 10-14 | +41.8 | −19.0 | 60.8 | −205.2 |
| **10-15** | **+77.6** | **−50.3** | **128.0** | **−389.8** |

Both observations have the same shape and the gap roughly doubled with the roll.
**n=2 — nothing is proposed, and nothing may be.** One refinement to the
pre-registration, recorded now so it is not invented later to fit: the quantity
to regress on |roll| is the **gap** (scan offset minus realised close basis),
**not the offset** — the 10-15 review falsified roll-magnitude against the
*offset*, which is a different variable, and that falsification does not carry
over. Re-test at n=10 clean observations.

## 4. Change proposals — only material ones

**Nothing new is proposed. No ID was allocated** (`grep -n "^## "` run first;
next free remains **H27 · D27 · P-I**). Everything below is either an existing
item gaining a data point, or an item that has reached a threshold and resolves
to "no model change".

**Reaching a threshold, resolving to no change:**

1. **H8 — ANSWERED at its pre-registered 10 observations, POSITIVE, and nothing
   needs to change.** Straddle band 29210..30067, close 29885.3 **inside**;
   record **8 inside / 2 outside (n=10)**. The claim was *"price closes inside
   roughly two days in three"*; 80% of 10 cannot be distinguished from 67%, so
   the band is **at worst correctly advertised and possibly conservative**. On
   the same day the **VXN-implied range under-read the realised range by 149.3
   (1.35x)** — the 7th such under-read in the recent series. The straddle band
   is the better-behaved of the two forward range measures in the brief, and it
   is already printed. **Keep both; change neither.** H8 moves OBSERVING →
   ANSWERED-POSITIVE.

2. **P-H — the convention now decides the headline, not just a verdict.** 10-15
   is the 4th deciding instance (n=3 → **n=4**: 09-11, 09-16, 10-07, 10-15). Over
   the **16 graded calls** (one PRE_NY scan per day, ex-09-24, inside
   `track.py`'s 45-day window — a different denominator from `track.py`'s own
   scan-level 14 / 7 / 9 line) the two conventions give
   **10 right / 6 wrong (post-scan)** against **12 right / 4 wrong (day net)** —
   62.5% vs 75%. **P-H was already PROPOSED on 10-08; this review adds the
   evidence that the choice is now worth 12.5 points of headline accuracy and
   should be made rather than carried.** No new proposal.

3. **H26 — updated, and 10-15 cuts both ways.** |score| 7 falls in the **6–9**
   bucket, which was 5-of-5; graded on the P-H post-scan basis the day is WRONG,
   so the bucket becomes **5 of 6**. The ≥10 bucket is **unchanged at 3 of 6**.
   Magnitude strengthens and direction weakens, exactly as H26 claims:

   | magnitude | n | correct | wrong | no-call | mean abs(post-scan)/ADR | mean range/ADR |
   |---|---|---|---|---|---|---|
   | 0–2 | 7 | — | — | 7 | 0.18 | 1.10 |
   | 3–5 | 4 | 2 | 2 | 0 | 0.24 | 0.94 |
   | **6–9** | **6** | **5** | **1** | 0 | **0.39** (was 0.35) | **1.06** (was 1.02) |
   | ≥10 | 6 | 3 | 3 | 0 | 0.78 | 1.39 |

   - Spearman(|score|, |post-scan move|/ADR) **+0.594 → +0.612** (n=22 → 23)
   - Spearman(|score|, *signed* move in the called direction/ADR) **+0.221 → +0.165**
   - Spearman(|score|, session range/ADR) +0.190 → +0.196

   A −7 produced **0.62x ADR** of post-scan movement — well above its bucket
   mean — **in the wrong direction**. The H26 proposal (print the measured base
   rate and scale the range language with |score|; change no score) is unchanged
   and is now supported by 23 sessions.

**Existing items, data point appended, nothing proposed:**

- **P4 / H1 — n=27 days, and it changes nothing.** 10-15 error **+116.1**
  (budget 11.5, extension 127.6). `track.py` per-day mean **+31.2 → +34.3**
  (n=27, includes 09-24); **ex-09-24, n=26, +35.1** (was +31.9). **The statistic
  is NOT re-derived**: MAE **116.1** vs leave-one-out constant **98.3** (n=19);
  ex the 09-21 outlier **90.9** vs **75.5** (n=18); sign agreement 9 of 19. The
  claim remains **"no usable skill"**, not "inversely predictive". **The
  multiplier branch stays closed.** Traversal **49.83x** budget is the largest
  finite ratio in the record and is a property of the 11.5pt denominator, not new
  information.
- **H23 — 12th instance.** Brake **sliced**: census **9 sliced / 1 capped, n=10
  over 8 sessions**, never-reached 2. Corridor terminus branch **extended to
  n=4** (+19.2) and is the **first upside instance**; the branch's sub-claim
  takes **two counter-instances** today — the named brake 29577.6 **is** printed
  in the secondary table and the terminus 29977.6 **is** MAX PAIN on the main
  board, so "the named level appears nowhere else" (n=3) now has 2 against.
  Already PROPOSED; not re-proposed.
- **H2 — 4th counter-instance on the budget, 1st clean instance FOR the fade.**
  EXHAUSTED below the flip; the range grew 11.1x the budget (budget wrong), and
  fading both extremes won (fade right). The two halves of H2 point opposite ways
  on the same day. Record stays unproven in both directions.
- **H22 — n=9.** Week net GEX −7.466 → *"expansion likely"* → 1.25x ADR: right.
- **H10 — `−3` branch, 6th firing, 1-for-6 on the post-scan basis.** No reclaim
  occurred (PWL never approached within 571.3), so the proposed reclaim term
  would not have changed the call.
- **H17 — no instance.** Post-scan move 283.7 = **49.5%** of the session range,
  far outside the 5% deadband. Stays 1 of 3.
- **H4 / H7 / H20 / D21 / P-E / P-B(b) — no instance.** Flip never approached
  within 571.3 (H4). No overnight scan (H7). **H20 stays CLOSED-NEGATIVE and is
  not revived.** `gamma +0`, price 37% up the band — neither D21 branch fired.
  CALL WALL missed by 80.8 and never in play (P-E). `merge_tol` = 3.66 vs
  `TOUCH_TOL` = 8.0, but the closest published pair is 50pts apart, so the
  guaranteed double-count window did not fire; inflation **1.00x**, 14th session.
- **P3 / H6 — the 2nd structural touch in the record, and it is ungradeable.**
  See §2. The put-side census cannot take this day.
- **D22 — first damage instance** (breadth −3 from Wednesday's closes, 3 of 7
  net points). Already recorded; no new number.
- **D23 — 12th residual, and the largest in the series.** Board **+77.6** vs
  section-7 **−346.8**; gap **+424.4**; CFD move (11:55Z bar open **29652.5** →
  scan **29638.7**) = **−13.8**; **residual +438.2**. Series:
  `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
  −68.0 / +165.0 / **+438.2**`. The two conversions disagree in **sign**, as on
  10-12. Damage none — research-only, no volume had traded.
- **D25 — 25th consecutive pre-NY scan.** *"The dominant strike is **stable** at
  0 across 6 samples"* printed three lines under *"⚠️ No volume has traded yet
  today"*. Instance appended, not re-opened. Damage none.
- **D24 — no instance.** TSM's pre-market earnings **were** listed in section 5;
  no release fell between the day's open and the scan. `event_gate` null, correctly.
- **D17 — SUCCESS, logged as such.** The 2026-10-16 scan hit a CBOE **429** and
  the retry recovered it on **attempt 1 of 3**. Recorded as a success, not a
  failure.
- **D26 — reporting gap, not data loss; the 10-12 correction stands.**
  `track.py` reports **27 trading days / 30 scans (deduped)**; on disk there are
  **34** day directories, **64** scan JSONs, **29** days with a PRE_NY scan,
  **28** with a `REVIEW.md`, **25** with both. The August days are intact and
  invisible only to the 45-day bar window. **`track.py` no longer prints a
  literal `actionable: YES/NO` line** — the review threshold was applied by hand.
- **Session-context field — 14th session, and the mildest instance recorded.**
  Only **1 of 6** published board rows (29627.6) lay inside the pre-scan range
  29512.7–29958.2. The *"Beyond today's range (context only, don't mark)"*
  footnote carried **London Low 30513.4** and **Asia Low 30504.5** at **+875 /
  +866 above price**, but it prints **no prose**, so **P-G does not fire** — the
  defect there is prose chosen by level kind, and there is no prose. P-G stays at
  instance #21.

**Dead-weight audit, refreshed to n=31 PRE_NY `is_trading_day` scans (09-24
excluded by hand), and one standing claim is corrected:**

| row | scored / present |
|---|---|
| `macro` Yield curve 10y–2y | **0 / 31 — still has never scored** |
| `fuel` ratio row | 0 / 31 |
| `fuel` conviction row | 0 / 18 |
| `events` | 0 / 15 (absent on the rest) |
| `vol` VVIX | 2 / 31 |
| `rates` DXY | 4 / 31 |
| `macro` NFCI | 5 / 31 |
| `macro` WALCL/RRP | 6 / 31 |
| `macro` HY OAS | **25 / 31** |

- **The HY OAS claim in the standing note is wrong and is corrected.** The row is
  **not** dead weight and 10-16's −2 is **not** its first score: **+2 on 19
  consecutive scans (08-24 → 09-28)**, **−2 on six (09-29 → 10-06)**, **0 on six
  (10-07 → 10-15)**, **−2 again on 10-16** at 3.25% / +16bp. What is real is the
  **rendering** defect: HY OAS has printed **no observation date for the 11th
  consecutive session**, so its freshness cannot be checked from the document.
  **That is an H18/P1 rendering item, not a dead-weight item**, and it does not
  unblock H18/P1's retracted accuracy case — a row that scores often and is
  undated is a *bigger* freshness exposure, not evidence of accuracy either way.
- **NFCI's run ended.** It fired −1 on five consecutive scans (10-07 → 10-14) and
  scored **0 on both 10-15 and 10-16**. The 10-15 review's "5th consecutive
  graded session" is the end of the run, not a trend.
- The standing narrowed proposal (drop the yield-curve row and WALCL/RRP) is
  **unchanged and still not actioned**.

**Housekeeping on H3, as directed:**

- **The CLOSED-NEGATIVE recommendation is recorded** — in the 2026-10-15
  appended block (line 10090), *"recommend CLOSED-NEGATIVE, superseded by H26"*.
  **H3's own entry (line 184) still reads `Status: OBSERVING. Do not implement.`**
  and cannot be edited, because everything below the ID-allocation block is
  append-only. A reader who greps `## H3` sees OBSERVING. **The closure is
  therefore recorded but not discoverable at the heading**, and a pointer has
  been added to the ID-allocation block, which is the only in-place-editable
  region.
- **The bad citation is confirmed and its scope is narrower than stated.**
  `2026-08-25/1304-preny.json` scores **0 / NEUTRAL**, so *"08-25 13:04"* is
  wrong wherever it is cited as a **max-conviction bearish call** — that is
  **line 8226**, whose *"bearish branch is now 0 for 4"* is really **0 for 3**,
  and the H3 census that inherits it. **The 10-07 entry's claim that a "4th data
  point for a conviction cap exists" is void: there were only three.** The same
  citation at **line 2818** (a fuel error of +219.8 on a 12.0 budget) and **line
  4301** (an H2 EXHAUSTED-fade instance) is **legitimate** — that scan really was
  EXHAUSTED at 97.1% used — and at **line 1234** (W1, macro flipped
  bullish→neutral) it is legitimate and in fact depends on the score being 0.
  Flagged, not edited.

**Still observing, with nothing to propose:** the board-offset mechanism (no
explanation survives; pre-registered log at 2 of 10); the fuel-vs-gamma census
(cannot be read until its column is re-specified); D20's freshness shape (today's
double-counted 24-hour-old CPI is the clearest instance yet, but the entry is
still below its own "twice more" bar as a *weekday-named* defect); max pain's
day-of-week qualifier (first Thursday test, first success, **n=1**).

## Journal hygiene

One scan file for 10-15 (`1247-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day. **09-24 quarantined by
hand — 13th consecutive review to carry it**; there is still no schema
`quarantine` field and the 09-29 proposal for one is reaffirmed, because
`track.py` keeps 09-24 inside every statistic it prints (its direction line,
**14 right / 7 wrong / 9 no-call**, becomes **13 / 7 / 9** once 09-24 is
removed). **2026-10-13 has no journal directory — the scheduled scan never ran;
nothing was created, back-dated or inferred, and the gap is recorded so the skip
from 10-12 to 10-14 is not later mistaken for data.** 09-09 and 09-25 still have
no `REVIEW.md` and none was created. 2026-10-16 is on disk, unfinished (180
bars), and excluded from every statistic above. **No `prediction` block was
touched. No scoring, wall or grading code was edited.** No fabricated or
backfilled entries found. **No new ID allocated by this review. Next free:
H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
