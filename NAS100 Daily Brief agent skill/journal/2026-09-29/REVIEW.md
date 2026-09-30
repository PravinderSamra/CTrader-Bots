# REVIEW — 2026-09-29 (graded 2026-09-30)

1 gradeable scan (12:48Z PRE_NY), `is_trading_day: true`, 0 test artefacts, 276
bars. **2026-09-24 is excluded from every options statistic, the direction tally
and the hit-rate series below**, per `HYPOTHESES.md` → *D23 CORRECTED*; its fuel
error (+13.6) is kept, on the D1 precedent, so it is inside the H1 series and
nowhere else. `track.py` has no quarantine and still prints 09-24 as CORRECT, so
the direction counts below are carried by hand off its per-scan table. **09-25's
figures are taken from the 09-28 review's register entry**, where that session
was graded and folded in; no review file was back-dated for 09-24 or 09-25. No
`prediction` block was edited. No fabricated or backfilled entries found.

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 30315.9 / 30471.8 / **30119.5** / 30404.6 |
| range · net | 352.3 (**0.76x** ADR14 464.5) · **+88.7** |
| close position in range | 80.9% |
| direction call | **CORRECT** (BULLISH +6, expected +1; realised +1) |
| post-scan move | **+12.9** · traversal 218.8 — right by 5.9% of the distance travelled |
| fuel | budget **118.6** vs extension **6.4** → **−112.2, 0.05x (18.5x OVER)** · traversal 1.84x budget |
| level hit rate | **0.67** (10 of 15) — but 10 touches fall in **7 distinct 5-min bars**, 3 of them in one; 2 of the 10 were never actually reached (see §2). Strict rate **0.53** |
| VXN-implied range 423.7 | realised 352.3 → VXN **over** by 1.20x |
| straddle close band 30199–30588 | close 30404.6 **inside** ✓ |
| record to date, PRE_NY days (09-24 excluded) | direction **9 right / 4 wrong / 3 no-call** over 16 days |
| record to date, all sessions (09-24 excluded) | **14 right / 8 wrong / 7 no-call** |
| H1 per-day fuel error | mean **+23.3** (n=21); **−4.0** without the 09-21 tail; **MAE 85.4** against a mean budget of 103.6 |

## 2. What the levels actually did

| level | brief said | what happened | verdict |
|---|---|---|---|
| 30518.2 CALL WALL ●●●●● | "rallies stall, take profit into it" | never reached, **46.4 short** of the high | untested — no P-E instance, but see §4 on the census rule |
| 30501.9 NY High (prev-day) | "next session runs the stops above it" | never reached, 30.1 short | untested |
| 30479.1 London High (prev-day) | "runs the stops **above** it" | **never actually reached** — `travel_up −7.3`; counted as touched by the 8pt grading tolerance only. Stops above were not run | **false touch** — inflates the hit rate |
| 30465.4 London High (today) | "runs the stops above it" | ran **6.4** above, failed, then held as resistance **490min**, worst +6.4 | **right as a lid, wrong as a stop-run.** Best level on the board |
| 30418.2 Options shelf 0.51bn | "expect price to stall, take partials rather than push through" | price ran **53.6** above it | **sliced — P-E(b) counter-instance** |
| 30382.5 PD mid | "a target to aim AT, not a trigger" | touched 12:50Z, then price closed **below** it from 13:30Z to **20:15Z** — 6.75h of the session. Graded "held as support 40min" off the last 8 bars | target reached; the structure row built on it did not survive the day (§3) |
| 30368.2 Options shelf 0.53bn | "expect price to stall" | held as support **60min**, worst **−5.7**, 4 retests | **right.** Shelves 1-for-2 today |
| 30359.2 Asia High (today) | "runs the stops **above** it" | published **34pts below price** — the stops above it were already taken before the scan. Held as support 75min, worst −17.1 | **prose wrong-sided — P-G instance #11** |
| 30324.8 Asia Low (prev-day) | "runs the stops below it" | dipped **28.0** below, then **closed 79.8 above** it. Graded *"broke DOWN through it — lost by 28.0pts"* | **verdict inverted — M6 session #13** |
| 30310.0 PD close | "price often comes back to fill a gap from here" | came back to it at 13:40Z, held as support **170min**, worst **−13.2** | **right, and the most literal call on the board** |
| 30280.6 London Low (prev-day) + Equal lows ×2 ⭐ | "runs the stops **below** it" | price went **0.4** below, held **180min**, worst −11.7 | right as support, wrong as a stop-run |
| 30275.8 London Low (today) | "runs the stops below it" | **never actually reached** — `travel_down −4.4`; tolerance-only touch, same bar as the line above, **4.8pts away from it** | **false touch + unmerged duplicate — P-B(b)** |
| 30204.8 GAMMA FLIP _(stretch)_ | "lose it and stop fading" | never reached, 66.6 short | untested; the fade regime was never invalidated |
| 30168.2 MAX PAIN _(stretch)_ | "weak on a Monday, strong by Thursday/Friday" | never reached, 103.2 short | **distance-confounded again** — 3rd such miss; see §4 |
| 30119.5 Asia Low (today) + PUT WALL ●●●●● ⭐ | "expect a bounce and a good long-sweep here" | graded **"never reached"** — and it **is the session low to the point**, made pre-scan, from which price had already bounced **274pts** | **the brief and the grader are both blind to it** (§3) |

**Three levels were resolved by one 5-minute bar.** 30479.1, 30465.4 and 30359.2
all show `bar_index 186` = the **13:30Z NY cash-open bar**, which therefore
spanned at least 103.9pts and contained the day's high. The whole 200pt post-scan
swing started in it. A document whose regime block said *"expect a tight, pinned
range"* met a ≥104pt opening bar.

**The fade thesis itself was vindicated.** Both extremes failed — the upside
sweep by 6.4pts, the downside by 0.4 — and price closed 80.9% up the range,
12.9pts from the scan. `COHERENT_LONG` / Strategy 1 described this day correctly,
and the fuel prose (*"expect price to keep MOVING but mostly inside the
extremes"*) was exactly right: traversal 218.8 with only **6.4pts** of new range.
This is the first LOW_FUEL session in the record where the fuel block and the
gamma block agreed rather than contradicting each other, and both were right.

## 3. What was wrong, and why

**+4 of the +6 came from FRED rows that are at best two business days old, and
one of them double-counts a live row.** From `inputs.bias_components`:

| row | pts | defect |
|---|---|---|
| macro DFII10 2.83% | **+3** | **H18**, 8th instance. Its own `why` prints *"FRED has not published since 2026-09-25 (2 business days ago) — this is last week's reading"* and it still scores full weight. This is the single largest row in the model |
| macro DGS10 −1bp | **+1** | same staleness (dated **09-24 → 09-25**), for a **1bp** move — and it is the *same variable* as `rates +1 "US10y 5.217 (−0.44%)"`, which is live. **The 10-year yield is scored twice, once stale** |
| breadth NDX −1.08% vs ES +0.14% | **−1** | **D22(a)**, and code-certain from the register's own persisted closes: 30276.81 / 30608.13 − 1 = **−1.0825%** = the **09-25 → 09-28 cash session**, i.e. Monday, printed present-tense on Tuesday pre-market as *"tech lagging, rotation out of tech"*. The like-for-like overnight leg is CFD 30393.5 vs PD close 30310.0 = **+0.28%** against ES +0.14% — tech **leading**. The row has the sign backwards by 1.36pp |

Corrected: drop DFII10 and fix breadth → **+5**; also drop the duplicate DGS10 →
**+4**. Both land in `MILDLY BULLISH` rather than `BULLISH` — **one notch weaker,
direction unchanged, verdict unchanged.** So nothing was lost today; what is
established is that the published label was one notch stronger than the clean
inputs support, and that on 09-28 the same two defects cancelled in the opposite
direction. **H18 and D22(a) are now confirmed as coupled in both signs** — 09-28
the stale row bought conviction, 09-29 the stale rows and the stale breadth row
pull opposite ways. Neither can ship alone.

**The structure row asserted a persistent state from an 11pt position.**
`structure +1 "price above PD mid 30382.5"` was true by **11.0pts** at the scan
and false for 6.75 of the next 8 hours — price closed below PD mid from 13:30Z to
20:15Z. The row has no tolerance band, so ±11pts of a magnet scores the same as
±400. Smallest margin in the whole record (next is 27.9 on 09-16). **n=2, not
proposed** — see §4.

**The PUT WALL's forward scenario had already been resolved, and the grader
cannot see that either.** The board published `30119.5 Asia Low (today) + PUT
WALL` at −274 with *"expect a bounce and a good long-sweep here"*. That level
**was** the session low, made in the Asia window before the scan, and it had
already produced the 274pt bounce the brief was telling the reader to wait for.
`prediction.levels` carries `dist`, `reach`, `stretch`, `confluence` and **no
field for prior interaction**. `review_day.grade_level` then slices
`bars[i_from:]` from the scan bar, so it reported that level as **"never
reached"** — a verdict a reader would take as "untested" about the day's actual
low. **Both halves of the pipeline are blind to the same fact.** This is the
third session of the brief-side defect (09-17 call wall, 09-28 put wall, 09-29
put wall) and the first recorded instance of the grader-side one.

**The document published two conversion offsets 150.1pts apart for the same NDX
option grid.** The level board converted at **+18.2** (`nq_implied`: cash close
30276.81 + NQ move +98.5 = 30375.3, reconciles exactly — the D23 roll-forward
working as intended, second clean day after 09-28). Section 7 converted at
**+168.3** (`brief.py` line ~95: CFD bar close at the feed time minus GEXBot's
own spot). One of those two index references is wrong by ~150pts. Section 7 is
explicitly excluded from the call, so there is **no damage today** — but it is
the D23 mechanism living in a second code path, again wearing a reassuring label
(*"matched to feed time"*).

**`events` did not merely score zero — the row was absent.** The component is
`add("events", 0, ...)` over `heavyweight_earnings_next_5d` only; the macro
calendar never reaches the score at all, and the gate needs `impact == "High"`
within 1.5h. Today: two **Medium** prints 72 minutes after the scan, a **High**
Core PCE 23.7h out, `event_gate: None`, and no events row in the 23 components.
The register's *"0 points on 16 of 16 rows"* census was never measuring a
hypothesis — it was measuring a literal constant.

## 4. Change proposals

### PROPOSED — stop quoting the raw level hit rate; it is inflated by same-bar multi-touches, and `merge_tol` is half of `TOUCH_TOL`

**Evidence, 4 sessions** (plus the already-logged 09-18 clustering instance):

| day | published | touched | distinct touch bars | rate as published | rate on distinct events |
|---|---|---|---|---|---|
| 09-21 | 7 | 3 | 2 | 0.43 | 0.29 |
| 09-22 | 16 | 9 | 5 | 0.56 | 0.31 |
| 09-23 | 21 | 12 | 7 | 0.57 | 0.33 |
| **09-29** | 15 | 10 | **7** | **0.67** | **0.47** |
| controls | | | | | |
| 09-18 | 9 | 7 | 7 | 0.78 | 0.78 |
| 09-25 | 14 | 7 | 6 | 0.50 | 0.42 |
| 09-28 | 7 | 4 | 4 | 0.57 | 0.57 |

The published rate runs **1.4x–1.8x** the independent-event count whenever the
board is clustered, and exactly equal when it is not. **Mechanism, code-certain:**
`brief.py` merges lines at `merge_tol = max(3.0, adr14 * 0.008)` = **3.72** today,
while `review_day.py` grades a touch at `TOUCH_TOL = 8.0`. Any two levels between
3.72 and 8.0 apart are therefore guaranteed to publish as two lines and grade as
two touches off one bar. **That fired today**: 30280.6 and 30275.8, **4.8pts
apart**, same bar 209, and the second was never actually reached.

Proposal: (a) set `merge_tol >= TOUCH_TOL`; (b) report distinct-touch-events
alongside the raw rate and never quote the raw rate alone. Expected effect: no
change to any call; the hit-rate series stops being a function of how many lines
the board happened to print. **This is P-B(b), with the cause now quantified.**

### PROPOSED — one session-context field, covering the brief and the grader

Threshold met exactly as the register pre-specified (*"if a third arrives, this
and the H1 session-context sub-observation should be one proposal"*): **09-17**
call wall tested pre-scan, published as "+26 away"; **09-28** put wall already
broken pre-scan and bounced 193pts, published as an unresolved conditional;
**09-29** put wall already tested pre-scan and bounced 274pts, published as
"expect a bounce here" — and additionally reported by the grader as *"never
reached"* while being the session low.

Proposal: add `tested_today` (time, direction of approach, reaction) to each
`prediction.levels` entry from the session windows the scan already has; and let
`review_day` grade published levels against the **whole** session, reporting
pre-scan interaction separately rather than dropping it. Expected effect: no
score change; three of three instances would have printed "already tested at
HH:MM, bounced N" instead of a forward scenario, and 09-29's review would not
have said "never reached" about the low.

### Appended to HYPOTHESES.md, nothing proposed

- **M6 — session #13, a new polarity.** `settled_read` gave Asia Low (prev-day)
  `settled_side: above`, `held: false`, `acted_as: lost`, rendered *"broke DOWN
  through it"*, for a level price **closed 79.8pts above**. Previous instances hid
  a violation inside the verdict; this one invents one. Still the same root cause
  and the same written fix. **M6 needs a decision, not a 14th session.**
- **P-B — the cleanest tolerance instance in the record.** 30324.8 graded **lost**
  and 30310.0 graded **held**, 14.8pts apart, from the **same** settled window
  (both `settled_from 18:05`), because the dip was 28.0 below one and 13.2 below
  the other and `SETTLE_TOL = 25.0` sits between them. The verdict is a coin-flip
  on level spacing, not on behaviour.
- **P-E(b) — first counter-instance.** The nearest upside shelf (30418.2) was
  sliced by 53.6 while the lower one (30368.2) held inside 5.7. The true lid was
  a **session extreme** — the day's high landed in the 13.7pt band between London
  High (prev-day) and London High (today). With 09-28 (London High today capped
  480min) that is **2 sessions** where a prior London high was the real ceiling
  and the call wall was irrelevant. **Third instance and this becomes a proposal
  to lead the upside line with session extremes, not shelves.**
- **P-E census rule.** The call wall stalled 46.4 below the high without a touch,
  which lands inside the "empty middle" band (12–103) the census says is empty —
  but the census requires a touch, so near-misses can never populate it. The
  empty middle may be partly an artefact of that rule, not only of `SETTLE_TOL`.
- **Structure row has no tolerance band.** `|price − PD mid|` under 30pts: 09-16
  (+27.9, row +1, price then lost PD mid by 50.8–94.6) and 09-29 (+11.0, row +1,
  price below PD mid for 6.75h). **n=2 of 3.** Watching for a third day inside
  30pts; the test is whether price holds the scored side through the NY session.
- **D7.** Budget 118.6 → ±1.75x cap 207.6. Forward-only: no breach either side
  (+78.3 up, −122.1 down). Under the session-extreme convention the 09-28 table
  used, breach below **+66.4** (the pre-scan Asia low). **The convention itself is
  the defect** — 09-28's breach was post-scan, today's would be pre-scan, and the
  table conflates them. Under forward-only the high-budget bucket goes to **3 of
  9**; under the 09-28 convention, 4 of 9. The split still holds either way.
- **H1 — n=21.** Series extended by **−112.2**. Mean **+23.3**; **−4.0** without
  09-21, which flips the sign of the 09-28 figure (+1.7). **MAE 85.4 against a
  mean budget of 103.6 — the typical error is 82% of the typical budget.** No
  multiplier can repair an estimator with that ratio. The last three sessions are
  −124.4, +113.9, −112.2: unbiased and uninformative. **Recommend closing H1's
  multiplier branch as settled-negative** and keeping only the qualitative
  LOW_FUEL/HIGH_FUEL state, which was right today.
- **H2.** First LOW_FUEL session where the fuel block and the gamma block agreed
  (long gamma + favour fades) instead of conflicting. Both right. Supports the
  logged coherence fix: the 3 conflict instances are all **short**-gamma days.
- **P-C / `events`.** Row absent entirely today (23 components, no events row),
  so the census is 16 of 17 rows present and the row is zero **by construction**.
  Mechanism already logged; recording that the census measures a constant.
- **D23.** Second clean conversion day (offset +18.2, roll reconciles to the
  point). **Caveat on the proposed cross-check:** on days the brief derives its
  reference *by* rolling the cash close with the NQ delta, comparing that
  reference to futures-minus-premium is nearly self-referential — it retains power
  only through premium drift. It must compare against an independently measured
  NQ-minus-premium **level**, or it is vacuous on exactly the roll-path days.
- **Max pain's day-of-week qualifier.** Third distance-confounded miss (103.2
  short, Tuesday). The register's own recommendation to tighten the threshold to
  *"3 days on which max pain is within reach"* is reinforced; still ungradeable
  until M6 is decided.
- **P-G — instance #11.** Asia High (today) at −34.3 carrying *"the next session
  usually runs the stops above it"*.

## Journal hygiene

No fabricated or backfilled entries; no `prediction` block touched. 09-24
quarantined as directed and excluded from the options, direction and hit-rate
statistics above. 09-25 not re-graded here — its figures are cited from the 09-28
review. `track.py` still counts 09-24 as CORRECT and has no quarantine
mechanism, which means **every future review must carry this exclusion by hand
or the tally will silently drift.** That is now the second hand-carried
correction in the register (the other being 09-25's late grading) and it is worth
a `quarantine` field in the journal schema that `track.py` reads.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
