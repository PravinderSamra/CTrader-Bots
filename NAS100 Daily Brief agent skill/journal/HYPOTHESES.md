# Open hypotheses — evidence register

**Rule: nothing here changes the model until it has ≥3 trading days of evidence
pointing the same way.** One session is noise, and tuning on noise is how a
model gets worse. This file is the memory that makes that discipline survive
between sessions.

Run `python3 track.py` (in the skill's `scripts/`) to regenerate the evidence
table. Append observations below; do not rewrite history.

**Status:** 3 trading days on record (24, 25, 26 Aug). Only **H1** has actually
reached its own threshold, and its evidence is a trend rather than a level, so
nothing is proposed. H9 and H10 opened 27 Aug.

---

## H1 — The budget forecasts range EXTENSION, and does it accurately?

**Claim.** `remaining_budget` predicts how much further the day's high-low range
will grow. It does *not* predict how far price will travel.

**Why it matters.** It changes what the number is *for*. Read as "movement
left", `EXHAUSTED` says stand down. Read correctly it says the extremes are
probably in — expect movement *between* them.

**Evidence so far (1 day).**

| Scan | Budget | Extension | Traversal | Error |
|---|---|---|---|---|
| 24 Aug 13:45 NY_OPEN | 0.0 | **5.3** | 284.4 | **+5.3** |
| 24 Aug 12:40 PRE_NY | 88.7 | 168.5 | 290.9 | +79.8 |
| 24 Aug 09:37 LONDON | 88.7 | 168.5 | 334.7 | +79.8 |
| 24 Aug 08:28 LONDON | 88.7 | 168.5 | 334.7 | +79.8 |
| **25 Aug 13:04 PRE_NY** | 12.0 | **0.4** | 256.5 | **−11.6** |
| 26 Aug 13:12 PRE_NY | 186.2 | 113.2 | 268.2 | −73.0 |
| **27 Aug 13:23 PRE_NY** | **132.6** | **46.2** | 281.3 | **−86.4** |

**Per DAY** (the weighting to read for a claim about the model — see M1):
**+61.2 → −11.6 → −73.0 → −86.4**, mean **−27.5**.

**THRESHOLD MET at 4 days, and still no change proposed.** Three consecutive
over-reads, each larger than the last, after one large under-read. Four points
running monotonically in one direction describe a *trend*, not a level: a
multiplier fitted to them would fit the slope and be wrong at both ends.

What it does justify is a specific question rather than a tuning: **all three
over-read days were long-gamma or pinning sessions; the single under-read day
was not.** Record the gamma regime alongside the error from here, and get an
unpinned day before touching the model.

Mean error **+46.6pts** (range grew more than budgeted).

**Read.** At the exhausted point the forecast was near-exact — twice now. On 25
Aug the budget said 12pts of extension remained; price ran to a marginal new
high **0.4pts** above the London high, reversed, and closed 130pts lower. The
range did not extend. Meanwhile price travelled **256.5pts inside** it. Early
LONDON scans still run ~1.9× light. Traversal exceeded the budget every time —
which is the point: they measure different things.

*Fuel excluded:* the scan of **24 Aug 21:56Z** (trading day 25 Aug), budget 0.0
vs extension 371.0. Its fuel was
measured across the 21:00 UTC rollover and described the *previous* day's
finished range — a corrupt input, not a failed forecast. Counting it would have
dragged the mean from 46.6 to 100.7 and invented a systematic bias out of a bug.
See D1 below. Its *direction* call is still counted — see D3 on why only the
fuel fields are quarantined.

**Naming convention (adopted 26 Aug).** A scan is named by its **scan timestamp
in UTC**, with the trading day in brackets where it differs. This register
previously called one scan "25 Aug 21:56" in one place and "24 Aug 21:56" in
another — one scan, two names, in the file whose entire job is to prevent
double-counting.

**Threshold.** 3+ days. If the exhausted-point accuracy holds and early-session
error persists, the fix is a time-of-day correction, not a blanket multiplier.

**Status: OBSERVING — 2 of 3 days.** The exhausted-point claim is now 2-for-2
and looking strong; one more clean session decides it.

---

## H2 — At LOW_FUEL / EXHAUSTED, does fading the extremes beat continuation?

**Claim.** If the range will not extend, price must turn at the extremes, so the
higher-probability trade is a fade back into the range — even when the gamma
regime favours continuation.

**Why it matters.** This directly contradicts the gamma-regime strategy call in
those conditions, and the brief now says so in words. If it is wrong, the brief
is actively misleading on exhausted days.

**Evidence so far (1 day).** 24 Aug 13:45: `EXHAUSTED`, 0pt budget, price at the
day's low, bias **−12 STRONGLY BEARISH** (continuation). Price fell 30.6pts
further, bottomed, then rallied 253.8 and closed +147 above the scan. **The fade
was the trade.** One observation.

**25 Aug 13:04:** `EXHAUSTED`, 12pt budget, bias **0 / NEUTRAL** (no call). Price
made a 0.4pt new high, then sold off 256pts to 29,086 and closed mid-range at
29,212.9. Fading the extreme was again the trade; the engine issued no
directional call, so this is evidence for the *fuel* claim but not against the
bias engine. Two observations.

**Threshold.** 3+ instances of `LOW_FUEL`/`EXHAUSTED`-at-extreme. Record each
time: did price extend, or reverse?

**Status: OBSERVING.** The wording change was made because it is a *definitional*
consequence of H1, not a calibration — but the empirical claim still needs proving.

---

## H3 — Does the bias engine over-commit at range extremes?

**Claim.** With fuel exhausted and price at the day's extreme, a continuation
score should be capped rather than allowed to reach ±12.

**Evidence so far (1 day).** The −12 above was the strongest reading of the
session, produced at the exact low. Follows from the documented design choice
that fuel "reports, never votes".

**Threshold.** 3+ instances. If H2 confirms, this may be redundant — the fuel
wording may already do the work without touching the score.

**Status: OBSERVING. Do not implement.**

---

## H4 — Is the gamma flip a reliable magnet / settlement level?

**Claim.** Price gravitates back to the flip, making it useful as a target and
as trade invalidation.

**Evidence so far (1 day).** 24 Aug: flip published at 29,049.6 on the 13:45
scan; session closed **29,050.7 — 1.1 points away**, after trading well below it
and reversing.

**25 Aug:** flip published at 28,976.3 on the 13:04 scan; session closed
**29,212.9 — 236.6 points away**, and price never traded down to it (session low
29,086.1, still 110pts above). Clearly *not* a magnet on this day. One hit, one
miss.

**Threshold.** 5+ days (this is a distributional claim, so it needs more).
Record the close-to-flip distance each day.

**26 Aug:** flip 29,098.5, close 29,353.7 — **255.2pts away**. Miss.
**27 Aug:** flip 28,966.9, close 29,566.7 — **599.8pts away**. Clear miss.

**Status: OBSERVING — 4 of 5, and looking weak.** One hit, three misses, the
misses widening. 24 Aug's 1.1pt finish now looks firmly like the coincidence it
was warned to be. **Do not use the flip as a target.**

---

## H5 — Does the budget under-read early in the session and self-correct?

**Claim.** Error is largest early and shrinks as the day progresses.

**Evidence so far (2 days).** Early (4 scans) mean error **+56.9**; late (1 scan)
**+5.3**. The 25 Aug PRE_NY scan came in at **−11.6** — the first *over*-read on
record, and it arrived late in the range's life rather than early, which is
consistent with the claim.

**Threshold.** 3+ days. If it holds, the fix is a time-of-day term on the
budget — not a flat multiplier, which would break the accurate late reads.

**Status: OBSERVING.**

---

## H6 — Is the level board producing clean reactions?

**Claim.** Published levels are reaction points, not just descriptive lines.

**Evidence so far (2 days).** Hit rate **0.58** across 5 graded scans. On 25 Aug
both published levels (29,299.6 structural call wall, 29,249.6 options shelf)
graded "traded both sides — chopped around it". That is now the dominant
outcome, and it has a plausible cause: both days were long-gamma/pinning
regimes, where chop *is* the correct behaviour at a level. Worth splitting the
eventual breakdown by gamma regime as well as by level type.

**Threshold.** 5+ days, then break it down by level *type* — if session
extremes react cleanly and, say, PD-mid never does, the board should drop the
latter.

**Status: OBSERVING.**

---

## H7 — Is the overnight gamma flip stable enough to trade off?

**Claim.** The flip published on an overnight/pre-London scan is unreliable,
because the chain reprices and rolls before the session that would use it.

**Why it matters.** The flip decides the *regime label*, which decides which of
the two strategies the brief recommends. If it moves several hundred points
overnight, an overnight regime call is close to worthless.

**First observation.** The scan of 24 Aug 21:56Z published flip **29,271.0** with price
29,051.2 → "BELOW flip, SHORT gamma, dealers amplify" and **−3** on the bias
score, the single largest bearish component. By 25 Aug 13:04 the flip was
**28,976.3** with price 29,252.8 → "ABOVE flip, LONG gamma". The regime label
**inverted overnight**, and it inverted because the flip moved **295 points**,
not because price moved. The strategy recommendation inverted with it
(Strategy 2 → Strategy 1). The overnight scan's direction call was WRONG (−15
STRONGLY BEARISH, day closed +140).

**Second observation.** 25 Aug 22:11Z flip **29,098.5** → 26 Aug 13:12Z flip
**29,207.2**: drift **+108.7pts**, and the regime label inverted again (long →
short gamma). Weaker evidence than the first, because price also moved 153pts
over the same window, so the inversion is not purely flip drift. **2 of 3.**

**Anomaly that widens the scope.** On 24 Aug the flip moved **192 points between
the 08:28 and 08:30 scans** — 120 seconds apart, on a chain that cannot have
repriced in that time — while price moved 8.9pts. The regime label inverted.
The other four short-interval scan pairs in the journal drift only 0.4–23.5pts,
so this is a single anomalous observation, possibly a cold-start artefact on the
session's first scan (08:28's flip of 29,049.9 nearly matches 13:45's 29,049.6,
while everything between sits 200–390pts higher).

H7 was framed as "the chain reprices and rolls **overnight**". That mechanism
does not explain a 192pt move in two minutes. **Widen H7 from overnight
staleness to flip stability generally**, and record consecutive-scan drift, not
just overnight drift. One data point — no proposal.

**Third observation, and the sharpest yet.** Between 25 Aug 21:43Z and 22:11Z —
**28 minutes** — the flip moved **+167.4pts** while spot moved about **12.7**.
Drift was **13× price movement**. That is the second large short-interval move
after the 192pt/2min anomaly; the other five consecutive-scan pairs on record
drift only 0.4–23.5pts.

Related, and it quantifies the cost: the `gamma` component swung **+2 → −3**
overnight on a 108.7pt flip move. A **5-point swing** — larger than the entire
net score of −4 that produced the wrong 26 Aug call — driven by the least stable
input in the model.

**Threshold.** 3+ days. Record the overnight flip and the next-day pre-NY flip;
measure the drift. Also log flip drift between any two consecutive scans.

**Status: OBSERVING. Do not implement.** If the drift is consistently large the
fix is to *widen the confidence band* on overnight regime calls, or suppress the
gamma component before the cash open — not to change the flip maths, which is
sound.

---

## H8 — Is the ATM-straddle expected move a useful boundary?

**Claim.** The ±EM band from the nearest-expiry ATM straddle marks where price
is likely to *close*, and is a better forecast than the VXN-derived daily range
the brief already prints.

**Why it matters.** It is the only forward-looking, market-priced range measure
in the brief. Everything else (ADR, fuel budget) is derived from realised
history.

**Cannot be backtested.** CBOE serves a live snapshot only — there is no
historical straddle price to test against. So this goes in as observation-only
and must be tracked forward.

**First observation (25 Aug, for the 26 Aug session).** Straddle 191pts → EM
**±162** → band **29,065 .. 29,390**. Close **29,353.7 — inside**, 36pts below
the top. *(Logged initially as 4.9pts outside, off the pre-roll close; the final
close was higher and landed inside.)*

**Second observation (27 Aug).** Straddle 306pts → EM **±260** → band
**29,221 .. 29,741**. Close **29,566.7 — inside**. Intraday high 29,642.1, also
inside.

**2 of 2 closes inside. 2 of 10 observations.** Far too early to mean anything,
but nothing has gone wrong yet.

**The trap to avoid.** EM prices a **close-to-close** move; ADR measures a
**high-low** range, which is always larger. Reading "EM 162 vs ADR 399" as "the
market expects a quiet day" is the same category error as reading the range
budget as price travel. The brief says so in words at the point of use.

**Threshold.** 10+ sessions (a 68% claim needs a distribution, not a handful).
Record: did the close land inside the band? Did price trade outside it intraday?

**Status: OBSERVING.**

---

## H9 — Do same-day index-defining earnings suppress the expansion signal?

**Claim.** When a same-day, index-defining earnings event is on the calendar,
the range comes in contained regardless of what expiry structure says — so a
`COHERENT_SHORT` "expect expansion" read should be discounted, not followed.

**Why it matters.** The two signals are computed independently and neither
defers to the other. On the day it mattered the brief printed the earnings line
and the expansion call side by side and let them contradict each other.

**Evidence so far (1 day).** 26 Aug, NVDA after the close. Expiry structure said
`COHERENT_SHORT`, confidence high: *"expect range expansion and trends that
persist. Today's ADR can be exceeded — don't cap the target too early."* Actual
range **325.7 against ADR14 398.7 — 82%**. No expansion, no persistent trend.

*Corrected 27 Aug:* the first write-up of this cited 286.0 / 72%, taken from a
grading run at 20:42 before the session had finished. The day's high and close
were both set in the final bars. 82% is contained but materially less dramatic
than 72%, and it weakens this observation accordingly.

**Threshold.** 3+ index-defining earnings days. NVDA is the most extreme
possible case, so a single observation from it generalises poorly.

**Status: OBSERVING. Do not implement.**

---

## H10 — The prior-week-range rule has no reclaim condition

**Claim.** `structure −3` ("price is BELOW the entire prior-week range; PWL is
now resistance") scores a *state* and has no term for price reclaiming that
range. So the penalty neither decays nor inverts when the premise stops holding.

**Why it matters.** It is one of the largest single components in the engine,
and on 26 Aug it was one of two inputs behind a call that was wrong by 249.8
points.

**Evidence so far (1 day).** 26 Aug 13:12, the rule fired on PWL 29,115.9.
Within the same hour:

| Level | Travel up | Travel down | Graded |
|---|---|---|---|
| 29,118.1 (London Low + PWL) | 145.8 | 29.4 | chopped |
| 29,086.1 (NY Low prev-day) | **177.8** | **0.5** | broke UP through it |

Price touched 29,086.1 and never traded half a point below it. The "resistance"
was reclaimed almost immediately and the −3 stayed on the books.

**Threshold.** 3+ instances where price is outside the prior-week range at scan
time. Record whether the range was reclaimed within the session, and whether the
call went the way the penalty implied.

**Status: OBSERVING. Do not implement.** The fix, if the evidence supports one,
is a reclaim term — not a smaller constant.

---

## H11 — Do the chart's ranked walls produce in-range levels?

**Claim.** C1–C3 / P1–P3 rank by gamma force with no proximity filter, so they
may sit outside the day's range and be useless as day-trade levels.

### ⚠️ The first observation was INVALID and is withdrawn

It reported *"1 of 7 reached, 6 never reached, ranked walls spanned 600pts"* and
concluded the ranks do not produce tradeable levels. **Every part of that rested
on grading the wrong ladder.** Caught by the trader, who noticed a level in it
(29,599) that had never appeared in any ladder he was given.

Three independent faults, any one of which invalidates it:

1. **Wrong ladder.** `--ladder auto` picked the 26 Aug 22:12Z file. That ladder
   was never delivered in a scan — it was generated while building the
   persistence feature.
2. **Pre-fix code.** It carries `book: None, dte_max: 45` — built on the 45-day
   book, *before* the book mismatch and the wall-dominance fixes. Grading it
   measures the version with the bugs in.
3. **Post-spike anchor.** Built at spot 29,492.8 in the post-NVDA move after the
   roll, so its ranks were spread across 600pts of a book anchored to a price
   the next session never returned to.

### The correct first observation

The ladder actually delivered with the 27 Aug scan (13:58Z, week book,
post-fix), graded from publication forward:

| Rank | Level | First-touch grade | **After it settled** |
|---|---|---|---|
| C3 | 29,514 | CHOP | held 120min, worst **−11.2** → support |
| C1 | 29,464 | CHOP | held **310min**, worst **−4.7** → support |
| C2 | 29,414 | BROKE | held 420min, worst **+1.6** → support |

**All three C-ranks were in range and all three were touched.** They span 100
points, not 600. The corrected result points the opposite way to the withdrawn
one.

**Status: OBSERVING, 1 valid observation of 3.** The concern is still live —
one week-book ladder is not proof the ranks are always in range — but there is
now no evidence for the original claim.

**Lesson.** `--ladder auto` picking "the newest file older than the target" is
not the same as "the ladder the trader was given". Ladders written by
development runs sit in the same directory as real ones. The auto-pick needs to
prefer a ladder that accompanied a delivered scan, and to refuse a pre-fix
`book: None` file outright.

---

## D5 — the level grader scores the first touch and nothing else

*Found by the trader 2026-08-27.* He read C1 29,464 as: swept once, reclaimed,
then support for the rest of the session, never broken again. `grade_level`
called it **CHOP**. He was right and the tool was wrong.

Three faults in the rule:

1. **Only the first touch counts.** `grade_level` looks at `REACT_BARS` after
   the first touch and stops. On a news-driven open the first touch is the
   worst possible sample — it grades the noise and discards everything after.
2. **No concept of role reversal.** A call wall that caps price, is reclaimed,
   and then acts as support is a level working well. First-touch scoring calls
   that "chopped".
3. **"broke UP through it" counts as a failure** even when the level sits below
   price and is simply never revisited. For a call wall in a rally that is the
   normal, successful outcome.

Measured properly on 27 Aug, C1 had **exactly one bar close below it** in the
whole post-publication session, then held for **310 minutes** with a worst
excursion of **4.7 points**.

`gex_retro.role_reversal()` now reports, for every touched level: which side
price settled on, from when, how long it held, how many times it was retested,
and the worst excursion through it. It is **additive** — `grade_level` is
unchanged, so the written review and the chart still agree, and the first-touch
grade sits beside the settled-behaviour read rather than being replaced by it.

Two guards learned building it: a level price never came near returns nothing
(a strike 650pts away was scoring as SUPPORT with a +651.6 "excursion"), and
the ladder retro now clips bars to **after the ladder was published** — it was
grading a mid-session ladder against the morning that preceded it, pure
look-ahead that survived only because the first test used a prior-evening
ladder against a whole next day.

**The general point, and it is the important one: the trader read the level
better than the tool did.** The measurement was wrong, not just the conclusion.

---

## Rejected after testing (recorded so they are not re-proposed)

**R1 — Separate 0DTE-only gamma walls.** *Tested and rejected 2026-08-25.*
Hypothesis: since 0DTE carried 5,582,029 contracts of volume against 650,147 on
the next expiry, its walls should be published separately from the blended
this-week bucket. Measured on the live chain, the two rankings are nearly
identical:

| | 0DTE only | blended dte 0-3 |
|---|---|---|
| 1st | 29,233.5 CALL 2.52bn | 29,233.5 CALL 2.80bn |
| 2nd | 29,183.5 CALL 0.87bn | 29,183.5 CALL 1.08bn |
| 3rd | 29,283.5 CALL 0.86bn | 29,283.5 CALL 0.99bn |

Same strikes, same order. Gamma explodes as expiry approaches, so 0DTE already
*dominates* the blended sum — separating it out would add chart lines without
adding information. **Do not re-propose without new evidence.**

**R3 — Session VWAP in the level board.** *Rejected 2026-08-25 by the trader.*
Tested and it works — computable from bars already fetched, and 25 Aug's NY
VWAP (29,185.4) landed within 2 points of the 0DTE call-gamma pivot (29,183.5),
which is genuine cross-mechanism confluence. Not added: **it is already on the
chart.** The brief's job is to supply what the chart cannot, and duplicating a
line the platform draws natively is clutter, not enrichment.

Keep this in mind when weighing future candidates: "is it material?" is only
half the test — the other half is "is it already in front of him?"

**R2 — Vanna and charm as chart levels.** *Rejected 2026-08-25 on design
grounds.* Both are computable from the chain, and both are real forces (charm
drives the end-of-day pin, vanna drives vol-crush rallies). But neither is a
*price level* — they are flows that vary continuously with spot and vol. There
is nothing to draw. If they earn a place later it is as a one-line regime flag
in the bias engine, never as a marking.

---

## Resolved / withdrawn

**W1 — "Fuel is systematically too tight; recalibrate."** *Withdrawn 2026-08-24.*
Rested on grading the budget against price traversal instead of range extension,
which manufactured a 3.8× under-estimate from an accurate forecast. The review
engine was fixed; the proposal was wrong.

**W2 — The 2026-08-20 data point.** *Withdrawn 2026-08-24.* It came from a
backdated journal entry created to test the review loop and deleted immediately
after. It was then cited as one of "three independent sessions" — exactly the
archive corruption this process exists to prevent. Never cite a synthetic entry.

---

## Defects found and fixed (not hypotheses — these were bugs)

**D1 — Fuel measured across the 21:00 UTC day rollover.** *Found and fixed
2026-08-25.* The feed goes quiet over the daily roll, so a scan in that window
found zero bars for the new trading day. `levels_fuel.run()` silently fell back
to the last completed **daily** bar — i.e. it served yesterday's finished range
as today's. The 24 Aug 21:56 scan therefore printed *"range 530.9, 117.7% used,
EXHAUSTED, 0.0 budget"* **56 minutes into a session that went on to build a
397pt range**, telling the reader the day was over before it had begun.

Not a calibration question and so not subject to the 3-day rule — a range that
does not exist yet is *unknowable*, not *exhausted*. `levels_fuel` now reports a
new `SESSION_PENDING` state with the full ADR as budget, and the brief says in
words that there is no fuel read yet. `track.py` quarantines any pre-fix scan
carrying the signature (>100% ADR used within 90 minutes of the roll) so it
cannot enter the statistics.

It did **not** affect the direction call: fuel reports and never votes, so the
bias score was untouched. The two failures on 24–25 Aug overnight are
independent — this one and H7.

**D2 — Secondary-walls table described put strikes backwards.** *Found and fixed
2026-08-26, on the first live scan that contained any.* Under this repo's stated
dealer convention (long calls, short puts) a put-dominant strike means dealers
are **short** gamma there: they amplify, so price accelerates through rather
than stalling. The table called every put-dominant strike below spot *"a genuine
floor while we stay in long gamma"* — the opposite behaviour, carrying a
long-gamma caveat, on a session trading BELOW the flip in short gamma.

The result was two "genuine floors" printed below spot on the same page as the
brief's own *"DOWNSIDE path: clear … nothing structural to slow a breakdown. Do
not fade it."* Contradictory guidance in one document, on the side the trader
would have been managing a short from.

Moneyness was wrong too: a put struck **above** spot is in-the-money, not out.
The label read *"out-of-the-money put gamma above spot — thin, expect little
reaction"* while attached to the single largest force in the table (1.02bn
across 18,551 contracts).

Behaviour is now derived from the **sign of dealer gamma** at the strike rather
than from which side of spot it sits, and is regime-aware.

*Lesson.* The bug survived a full build, a render check and a docs pass because
every one of those confirmed the table *appeared*. Nothing checked it against
the regime read on the same page. **A new panel needs one test that it does not
contradict the rest of the brief**, not just that it renders.

**D4 — the put wall was not required to be put-dominated.** *Found by the trader
2026-08-27, from the chart contradicting itself.*

`max(below, key=put_gex)` returns the strike carrying the most put gamma below
spot — but never checked whether puts actually **dominate** that strike. On
2026-08-27 it returned **29,291**, which held:

| | |
|---|---|
| Call open interest | **45,880** |
| Put open interest | 10,432 |
| Ratio | **4.4 : 1 calls** |
| Net gamma | **+0.742bn** — the 3rd-largest POSITIVE strike on the board |

The brief called it *"heaviest floor this week — expect a bounce and a good
long-sweep here."* The chart stamped **C3** on the same row. One strike, two
labels that cannot both be true, and a long recommended off what is actually a
call-gamma brake.

**NDX makes this the normal case, not an edge case.** The index carries far less
protective put open interest than SPX, so on many days **no strike below spot is
put-dominated at all** — on 27 Aug only 4 of the strikes below spot had negative
net gamma and the largest was −0.029bn. The honest answer on such a day is *there
is no put wall on this chain*, not to promote whichever call-heavy strike happens
to hold the most puts.

Both walls now require dominance (`call_gex > put_gex` / `put_gex > call_gex`),
fixed in `gex_levels.build()` so the brief and the chart inherit it together. The
chart says in words when no put wall exists.

*This is the third time the same root cause has produced a bug* — D2 (secondary
walls), the C/P rank inversion in `gex_chart`, and now this. **Naming a level
after a side without checking which side actually dominates it.**

**And the guard that catches it now existed only as a lesson.** D2's write-up
said: *"a new panel needs one test that it does not contradict the rest of the
brief."* That was written down and never implemented. `gex_chart.consistency_check()`
now runs on every render and refuses to stay silent when a strike carries a PUT
WALL label and a C rank, a CALL WALL label and a P rank, or a wall whose net
gamma has the wrong sign. **A lesson recorded but not built is not a fix.**

**D3 — `track.py` graded an unfinished trading day.** *Found by the reviewer and
fixed 2026-08-26.* The completeness guard tested `bars < 150`. That does not
work: the trading day starts at 21:00 UTC the **previous evening**, so 150 M_5
bars accumulate by 09:30 UTC — four hours before NY opens. At 13:23 UTC on
26 Aug it admitted a day with 185 bars (complete days have 276), whose "close"
was the last tick and whose range had not finished extending.

That single unfinished day flipped **H1's mean error from +46.6 to −19.9 — a
sign change** — and turned `actionable` to **YES** while HYPOTHESES.md still
correctly said nothing was actionable. Fixed to test the wall clock
(`now_utc >= 21:00 UTC on the day's own date`), with the bar count kept only as
a secondary guard against a gappy feed.

The same pass fixed an **over-exclusion**: the rollover quarantine dropped whole
rows, but the corruption is field-level. D1 establishes that fuel reports and
never votes, so those scans' direction calls are sound. Dropping them made the
scoreboard read 1 right / 1 wrong when the honest tally was **1 right / 2
wrong**, and the `SESSION_PENDING` branch would have done that to every future
overnight scan — exactly the population H7 exists to study. Fuel fields are now
quarantined; direction and level statistics keep the row, marked `*`.

*Lesson.* Both D1 and D3 are the same shape: **a guard written against the
symptom rather than the definition.** "Not enough bars" and "over 100% ADR" are
proxies; "the day has not ended" and "this field was measured across a
rollover" are the actual conditions. Proxy guards fail silently and in the
flattering direction.

---

## Regression test — the invariants today's bugs violated

`scripts/test_consistency.py` (24 checks; `--offline` skips the live half).

Every check corresponds to a bug that actually shipped. The point is not to
prove the code works — it is to make **these particular failures loud**, because
every one of them was silent. A brief and a chart that disagreed still rendered.
A put wall on a call-dominated strike still printed. An unfinished day still
produced a number.

Structural: wall dominance at source and in the chart · chart defaults to the
brief's book · `brief.py --chart` builds both files from one `gather()` ·
`--no-journal` exists · both graders honour `test_artefact` · day-completeness by
clock not bar count · held-back days printed · H1 reported per day · ladder retro
clips to post-publication · auto-pick refuses pre-fix ladders · `role_reversal`
ignores untouched levels · one grader shared by `track` and `gex_retro` · every
ladder records its book or is marked `pre_fix`.

Live, from a single build: chart flip == brief flip · both walls agree within bin
rounding · no strike carries contradictory labels · each wall is dominated by its
own side · every C rank is net positive and every P rank net negative.

**It found a real file on its first run** — the 27 Aug 13:23 ladder, written
before the book fix, still sitting in the directory where the auto-pick looks.
Marked `pre_fix` rather than deleted, and the retro now refuses it explicitly.

**Latent, left in place deliberately:** `max_call_oi` / `max_put_oi` in
`gex_levels` carry no dominance test. They are honestly named — they are the
strike with the most open interest on that side, nothing more — and nothing
consumes them but a debug printer. They are annotated with a warning, because
they are exactly the field someone reaches for when building a "floor" and would
reproduce D4 verbatim.

## Housekeeping carried forward

- **Deduplicate near-identical scans.** Four landed within five minutes during
  testing. `track.py` now collapses scans inside a 15-minute window; the raw
  journal keeps them all.
- **Exclude incomplete sessions.** A scan 56 minutes into a new trading day was
  being graded "extension 0.0, traversal 26.1". `track.py` now requires ~12.5h
  of bars before a day enters the evidence.
- **Weekend PREP scans** never enter statistics (`is_trading_day: false`).
- **Verification re-runs are marked, not deleted.** On 2026-08-27 five journal
  entries were written for one real scan — four came from re-running the brief
  while fixing the put-wall dominance bug. The 15-minute dedupe collapses only
  the closest pair, so three would have entered the evidence as independent
  observations of a market state that was sampled once. Exactly the inflation
  the dedupe exists to prevent, caused this time from the inside.
  `brief.py --no-journal` prevents it going forward; the four already written
  carry `test_artefact: true` and `track.py` excludes them and says how many.
  **Marked rather than deleted, deliberately** — the archive's job is to record
  what happened, and a silent deletion is indistinguishable from the synthetic
  entry that produced W2.
- **Quarantine corrupt inputs, don't grade them.** A scan whose *input* was
  wrong is not a forecast that failed. `track.py` now prints an EXCLUDED block
  so the exclusions stay visible rather than silent.

---

# Observations appended 2026-08-27 (trading day 2026-08-26, graded post-roll)

Full working: `journal/2026-08-26/REVIEW.md`. Nothing below is a proposal.

**Status update:** **3 trading days on record** (24, 25, 26 Aug). `track.py`
prints `actionable: YES` on the *day count*, but per-hypothesis only **H1** and
(nominally) **H5** have reached threshold, and neither supports a change.

**H1 — threshold reached; no change supported.** Per-day mean error is
**+61.2 → −11.6 → −73.0**. The sign reverses and the magnitude is still moving,
so there is no stable bias to correct. Note the 26 Aug figure was **−112.7** when
measured last night at 20:42 UTC and is **−73.0** post-roll: the session high
was set in the final bar (20:55), adding 39.7 pts of extension to every scan on
the day. The reversal is real but 35% smaller than it looked. *Keep observing.*

**H2 — no new instance.** 26 Aug produced no LOW_FUEL/EXHAUSTED-at-extreme scan
(MODERATE / ROOM_TO_EXPAND / SESSION_PENDING). Still **2 of 3**.

**H3 — no new instance.** Still 1.

**H4 — third data point, a miss.** Close 29353.7 vs published flips 29207.2
(13:12), 29230.7 (13:14), 29098.5 (22:11) → **123–255 pts away**. Running
1 hit / 2 miss over 3 days. Needs 5. *Do not use the flip as a target.*

**H5 — day count reached, evidence not.** The late-session bucket still holds
exactly **one** scan (24 Aug 13:45, +5.3). A time-of-day term cannot be fitted to
one late observation. Insufficient despite the day count.

**H6 — third day.** Hit rate 0.71 (mean of 4 scans); running mean 0.56. "Traded
both sides — chopped" remains the dominant outcome. Two cull candidates now
have a track record worth watching: **MAX PAIN** was touched on 3 of 4 scans and
never stalled price once (chopped, chopped, broke down through), and **PD mid
29144.0** chopped on all 4. Needs 5 days. *Logged, not proposed.*

**H7 — strongest data point yet, but the pair count did not advance.** No
overnight scan was taken on the evening of 26 Aug, so there is still no third
overnight→pre-NY pair (**2 of 3**). However, the *widened* H7 (drift between any
two consecutive scans) gained a sharp observation: between **25 Aug 21:43Z and
22:11Z — 28 minutes apart — the flip moved 28931.1 → 29098.5 (+167.4 pts) while
spot moved ~12.7 pts** (29213.5 → 29226.2). Flip drift was **13× price
movement**. That is the second large short-interval drift on record after the
192 pt / 2 min anomaly of 24 Aug; the other five short-interval pairs drift
0.4–23.5 pts. Related: on 26 Aug the `gamma` component swung **+2 → −3** between
the 22:11Z and 13:12Z scans on a **+108.7 pt** flip move — a 5-point swing, larger
than the whole net score of −4, on the least stable input in the model.

**H8 — first outcome recorded (1 of 10).** Band **29,064 .. 29,388** (EM ±162
from the 25 Aug ATM straddle at 191 pts, ATM IV 15.5%). 26 Aug close **29353.7 →
INSIDE the band**. Intraday **low 29028.1 → 36 pts BELOW** the lower bound; high
29353.8 stayed inside. Result: **close inside / low breached**.

**H-new (opened, 1 day) — the prior-week displacement rule has no reclaim
condition.** On 26 Aug `structure −3` fired for *"price is BELOW the entire
prior-week range (29115.9–30245.8); PWL 29115.9 is now resistance, not
support"*, and it was half the bearish weight behind two WRONG −4 PRE_NY calls
(price then ran +249.8). Within the same hour `29118.1 London Low + PWL` graded
*traded both sides* at **145.8 up / 29.4 down**, and `29086.1 NY Low (prev-day)`
graded ***broke UP through it*** at **177.8 up / 0.5 down** — price touched it and
never traded 0.5 pts lower. The prior-week low was reclaimed and held, and the
rule scores a **state** with no term for reclaim, so the −3 neither decays nor
inverts. **Threshold: 3 days.** Record each time price is below the prior-week
range at scan time and whether it reclaims intraday. *One observation — no
proposal.*

**D2 did not regress.** `2211-overnight.md`'s secondary-walls table
("28993.0 … a genuine floor while we stay in long gamma") was written 22:11 on
25 Aug, *before* the D2 fix landed. It is a **pre-fix artefact and must not be
graded as a forecast.** The 27 Aug brief carries the corrected regime-aware
wording.

## Two methodology items awaiting a decision (not calibration, so not 3-day gated)

**M1 — `track.py`'s H1 mean pools scans, not days; 24 Aug is counted 4×.** Its
08:28, 09:37 and 12:40 rows carry the **identical** budget 88.7 against the
**identical** extension 168.5. Verified against bars: the live range really was
362.4 at all three timestamps, so this is genuine market behaviour, **not** a
stale-fuel defect — but it is still one budget reading graded three times. The
15-minute dedupe window does not catch it. Pooled by scan the H1 mean is
**+12.4**; weighted one-vote-per-day it is **−7.8**. Which weighting H1 should use
is a decision for the trader, not a tuning.

**M2 — the unfinished-day exclusion is silent.** `track.py` stores
`_excluded: "session not finished"` in `per_day` but never prints it; only the
fuel quarantine gets a visible EXCLUDED block. 2026-08-27 was correctly held out
and the reader is told nothing. Same shape as **D3**: a guard that fails quietly
and in the flattering direction. The housekeeping rule already says exclusions
must stay visible.

**Register gap: there is no H9.** This file runs H1–H8. A review task referred to
"H9 needs 3 days". Flagged, not created — inventing one would corrupt the count.

### Resolved 2026-08-27

**M1 — RESOLVED.** `track.py` now reports H1 **both ways**: per-scan and
per-day, and labels the per-day figure as the one to read for claims about the
model. It does not pick a weighting silently. Per-day the series is
**+61.2 → −11.6 → −73.0, mean −7.8** — monotonic, which is a clearer picture
than either pooled number gave.

**M2 — RESOLVED.** `track.py` now prints a `HELD BACK — day not finished` block
naming each day and its bar count, alongside the existing fuel-quarantine block.

**Also fixed: the `actionable: YES` banner.** It was a global day-count gate and
read far more permissively than the individual thresholds — shouting YES at 3
days while H4/H6 need 5 and H8 needs 10. It now names which hypotheses the day
count applies to and states that day count alone is not evidence.

**The H9 gap was mine.** The 26 Aug review told the trader "opening as H9" and
then never wrote it down — the claim lived only in a chat message. That is
precisely the failure this register exists to prevent, and it is worse than
forgetting, because H9 was subsequently referenced in a review task as though it
existed. **A hypothesis is opened by writing it here, not by saying so.** It is
created properly below.

---

# Observations appended 2026-08-28 (second-pass re-grade of trading day 2026-08-26/27)

*Source: `review_day.py 2026-08-27 --json`, `track.py`, and `inputs.bias_components`
read directly from the journal. 4 trading days on record (24–27 Aug). 2026-08-28
is in progress and is excluded. `2026-08-28/2233-overnight.json` carries
`scan_utc 2026-08-27T22:33Z` — that is the 21:00 roll working correctly, not a
misfile — and is marked `test_artefact`, so it enters nothing.*

## CORRECTION to H1 — the regime explanation is falsified

The 27 Aug review recorded: *"all three over-read days were long-gamma or
pinning sessions, and the single under-read day was not"*, and set the blocker
*"H1 needs an unpinned day."* **Both statements are wrong.** From
`bias_components`:

| Day | Fuel err | `gamma` regime |
|---|---|---|
| 24 Aug | **+61.2** (under) | −3 SHORT gamma, GEX −4.231 → *expansion likely* |
| 25 Aug | −11.6 (over) | +2 long-gamma, GEX +5.225 → *pinning likely* |
| 26 Aug | **−73.0** (over) | −3 SHORT gamma, GEX −2.103 → *expansion likely* |
| 27 Aug | −86.4 (over) | +2 long-gamma, GEX +9.223 → *pinning likely* |

26 Aug was short-gamma, flagged for **expansion**, and over-read by 73.0. 24 Aug
was in the same regime and under-read by 61.2. Long-gamma gives (−11.6, −86.4);
short-gamma gives (+61.2, −73.0). **Regime does not separate the errors, and the
unpinned day the review said it was waiting for already exists.**

**The mechanism instead is structural.** 390.3 (ADR14) − 257.7 (range at scan)
= 132.6 exactly: the budget is a pure linear ADR remainder with **no regime
term**. On that same scan the engine scored `gamma +2 — pinning likely`. The
model held the information and the budget had no way to read it.

**Still no proposal.** With n=2 per regime cell and both signs inside one cell,
there is nothing to fit. What changes is the *question*: H1 is not waiting on an
unpinned day, it is waiting on a reason to connect two existing numbers.
**Status: OBSERVING, blocker restated.**

## H6 — strong split by the board's own `stretch` flag (4 of 5 days)

Cross-tabulating `prediction.levels[].stretch` against `review_day` touches,
all 15 gradeable scans:

| | touched / published | rate |
|---|---|---|
| non-stretch | 85 / 105 | **0.81** |
| stretch (`reach: swing`) | 15 / 33 | **0.45** |

Non-stretch beats stretch on **24, 25, 26 and 27 Aug without exception**. On
27 Aug the split was total: non-stretch **7/7**, stretch **0/3**.

**H6's threshold is 5 days and this is day 4.** The conclusion *stop publishing
stretch levels* is **not proposed** — 0.45 is a real reaction rate. The only
thing proposed (in the 27 Aug review) is that the two rates be **reported
separately**, which changes no scoring and nothing that is published.
**Status: OBSERVING, 4/5.**

## M3 — direction is not per-day weighted, while fuel now is

M1 fixed the fuel mean by reporting per-day alongside per-scan. **The direction
tally never got the same treatment.** 26 Aug 21:43 and 22:11 are **28 minutes
apart**, both bias **+13**, both graded CORRECT, both counted. The 15-minute
dedupe window cannot see them. Collapsing that pair takes the record from
**4 right / 3 wrong** to **3 right / 3 wrong** — 57% to 50% on a 10-scan sample.

This is the same failure §6 of the 27 Aug review caught: the `test_artefact`
marking fixed *that instance*, not the *mechanism*. A 60-minute window would
collapse this pair and nothing else currently on record (24 Aug 08:28/09:37 are
69 min apart, 12:40/13:45 are 65 min) — but that is one day of evidence and one
window fitted to one pair, which is exactly what the 3-day rule exists to stop.
**One observation. No proposal.**

## M4 — `mean_level_hit_rate` is contaminated by single-level scans

24 Aug 13:45 published **1** level; 25 Aug 21:56 published **1** level. Both
score 0.0 and both enter the day mean unweighted. **25 Aug's day figure of 0.34
is that artefact and nothing else** — its only real scan graded 0.67. Published
counts across the record run from **1 to 22**. Two days. **Logged, not proposed.**

## H9 — first gradeable earnings instance goes AGAINST the component

The `events` component fired 14 times across 4 days, **every one scoring 0**,
every one NVDA: *"INDEX-DEFINING event; day before pins, day after expands."*

Graded: 26 Aug (day before) range extension **113.2**; 27 Aug (day after)
extension **46.2**. **The day after expanded less than half as much as the day
before.** The component made a testable claim, contributed nothing to score or
budget, and its first gradeable instance contradicted it.

One instance. **Threshold 3. No proposal.** Watch whether `events` is dead
weight or merely mute.

## Minor corrections to the 27 Aug review (no hypothesis attached)

- *"Price never traded below the scan price in any meaningful way"* — the
  grader's own output has the call wall 29,487.9 touched at 13:25 with
  `travel_down 127.1`, i.e. **29,360.8, 120.4 below the 29,481.2 scan price**.
  The review's own hourly table shows the 13:00 close at 29,417.6.
- *"0.70 — the joint best of the four days"* — per-day means are 24 Aug 0.69,
  25 Aug 0.34, **26 Aug 0.71**, 27 Aug 0.70. **Second of four.**
- **Grader anchor mismatch:** `actual_after_scan.move` = **91.6**, while close
  minus the brief's own `price_at_scan` = **85.5**. 6.1 points of difference in
  what "the move" is measured from. Did not change a sign on this day. Watching.
- **`fuel` is a zero-point component** — 25 emissions, all 0. By design (its own
  text says it dampens conviction, not direction), but it is emitted inside
  `bias_components` with a `points` field, where a reader looks for score
  drivers. Presentation issue, not dead weight.

---

# Observations appended 2026-08-28 (trading day 2026-08-28, graded post-roll)

*Source: `review_day.py`, `track.py`, `gex_retro.py` and `oi_accuracy.py`, run
after the 21:00 roll. **5 trading days on record (24–28 Aug).** One gradeable
scan today (13:14 PRE_NY); `2026-08-28/2233-overnight` is `test_artefact` and
enters nothing.*

Day: O 29570.4 H 29748.3 L 29376.4 C 29454.8, range 371.9, net **−115.6**.
The 13:14 scan called BULLISH +6 and price moved −143.7 — **WRONG**. Direction
across 5 days is now **4 right / 4 wrong / 3 no-call**.

## DEFECT D6 — D5's fix was wired into the ladder path only

`role_reversal()` was added 27 Aug as the fix for D5 and D5 records that it
*"now reports, for every touched level"*. It was called **only from
`build_from_ladder()`**. `build()` — every board retro — never called it, so
each level returned `role: None` and the day was scored on first touch alone,
the rule D5's own docstring calls the worst possible sample. **The register's
claim and the code disagreed, and the register was wrong.**

Effect on today, same bars, same board:

| of 16 reached | first touch | settled behaviour |
|---|---|---|
| held | **0 (0.0%)** | **13 (81%)** — 11 resistance, 2 support |

The call wall 29,735.4 was reported **BROKE**. It was never closed above in
1,375 minutes, worst excursion **+12.9**, and price fell 211.5 off it — it
marked the high of the day to within 13 points.

**Fixed** in `build()`, mirroring the ladder path. Additive as D5 requires:
`grade_level` and `outcome` untouched, headline counts and chart unchanged, the
settled read printed beside the first-touch grade. `test_consistency.py
--offline` 16/16.

**Carry forward:** `test_consistency.py` asserts *"role_reversal ignores levels
price never reached"* and passed throughout — it tests the function, not that
anything calls it. A unit test on a helper does not prove the helper is wired
in. Both D5 and D6 are the same failure: **the measurement was wrong, not the
market read.**

## H1 — 5 days, still no consistent sign

Per-day error: +61.2 / −11.6 / −73.0 / −86.4 / **−10.7**. Today is the second-
smallest, on a 0.96 budget-to-extension ratio (254.9 vs 244.2). The sign still
flips. The blocker restated on 27 Aug — the budget is a pure linear ADR
remainder with no regime term — is untouched. **Status: OBSERVING. Nothing
proposed.**

## H6 — threshold MET (5 of 5 days), same sign every day

Today by the board's own `stretch` flag: non-stretch **16/19 = 0.84**, stretch
**0/3 = 0.00**. Fifth consecutive day the split runs the same way, no
exceptions. Cumulative non-stretch **0.81**, stretch **0.45**.

Threshold reached is permission to read the evidence, not to act.

- **Recommended:** report the two rates separately in the review. No scoring
  change; nothing published to the trader changes.
- **NOT proposed:** dropping stretch levels. Cumulative 0.45 is a real reaction
  rate, and today's 0/3 is three levels sitting 259–812 pts away on a day
  budgeted for 255. **Status: OBSERVING → reporting split recommended.**

## The direction call was wrong; the actionable brief was not

Logged because the scoreboard cannot represent it. The regime section
(long gamma, *"sweeps genuinely fail — this is your fade day,"* Strategy 1) was
correct. The event gate held the trader out of a **292-point whipsaw** in the
14:00 print hour. Its follow-on rule — post-print 30-min range H/L as the
sweep levels — gave H 29,641.7; that high was swept at 14:35Z and price fell
**265.3 points** off it. Sweep → fail → reverse, exactly as described, in the
direction opposite the arrow.

**No bias-engine change proposed.** One wrong call inside 4/4 is small-sample,
not a defect.

---

# DEFECT D7 — `cpi_cool` scores negated inflation phrasing BACKWARDS (found 2026-09-01)

Found while judging the news on the 2026-09-01 13:22 scan. **One story, four
framings, three different verdicts.** Reproduced directly against
`news_scorer.score_item`:

| headline framing | rule | direction | weighted | confidence |
|---|---|---|---|---|
| "…support rate hike **if inflation doesn't ease**" | `cpi_cool` | **+1 BULL** | **+2.2** | HIGH |
| "…Higher Rates Needed **If Inflation Doesn't Cool**" | `cpi_cool` | **+1 BULL** | **+2.2** | HIGH |
| "…open to rate hike **if inflation does not moderate**" | `hawkish` | −1 bear | −1.8 | HIGH |
| "**If** inflation doesn't moderate, **then** we should raise rates" | `hawkish` | none | 0.0 | NEEDS_JUDGEMENT |

**The bug.** `cpi_cool` matches the tokens *ease* / *cool* and does not see the
negation that inverts them. "Inflation doesn't cool" is hawkish; it is scored as
though inflation cooled. The `hawkish` rule wins only when the phrasing happens
to avoid those two words ("does not moderate"), so the verdict depends on which
synonym a subeditor chose — not on what the story says.

**This is the exact failure the pre-filter exists to prevent.** `MODAL` caught
the fourth framing and correctly withheld it. The first two carry
**confidence HIGH** and are auto-scored, so they never reach the judgement list
where a human would catch them.

**Compounding: the same story was counted four times.** Even correctly signed,
one Fed speaker gets four votes because four outlets carried it. There is no
dedupe on story identity, only on exact headline.

**Effect on today's brief.** News published **MILDLY BULLISH +1.76**, worth
**+1** to the bias, carrying **3 × +2.2 = +6.6** of spurious bullish weight from
mis-signed duplicates of a hawkish story. Corrected, the news bucket is
unambiguously bearish.

**It did NOT change today's call** — the scan was already BEARISH −8 on gamma
−5 and macro −3, and the correction only deepens it. **No level, regime or
strategy output is affected.** Logged, not silently patched: this is a scoring
surface, and the fix (negation handling in `cpi_cool`, plus story-level dedupe)
wants its own test cases in `test_news_scorer.py` rather than an edit made
mid-scan.

**Carry forward:** the auto-scored bucket is the dangerous one. A wrong call in
the judgement list gets read by a human; a wrong call at `confidence HIGH` goes
straight into the bias score. Negation belongs in the pre-filter's refusal set
alongside modals and contrast clauses.

---

# Observations appended 2026-09-01 (trading day 2026-08-31, graded post-roll)

*Source: `review_day.py`, `track.py`, `gex_retro.py`. **6 trading days on record
(24–28, 31 Aug).** One gradeable scan (13:28 PRE_NY); no test artefacts in the
day. Graded a day late — 08-31 had no REVIEW.md when the 09-01 brief ran. The
09-01 scan is held back by `track.py` and enters nothing.*

Day: O 29464.7 H 29489.5 L 29223.8 C 29465.5, range 265.7, net **+0.8**.
The 13:28 scan called BEARISH −7 and price moved **+78.5** — **WRONG**.
Direction across 6 days is now **4 right / 5 wrong / 3 no-call**.

**Both of the day's extremes were already set before the scan was published.**
Range extension after the scan: **0.0**. The close finished 0.8 pts from the
day's open and **3.3 pts from the published gamma flip**.

## NEW — the two gamma terms are collinear by construction

`gamma −3 "below flip"` and `gamma −2 "week net GEX → expansion likely"` are the
same observation. The flip is *defined* as the spot where net GEX crosses zero,
so the sign of net GEX and the side of the flip cannot disagree. Checked against
**all 18 live scans on record (7 trading days): sign agreement is 18/18**, with
no exception — (+2,+2) or (+2,0) above the flip, (−3,−2) below it.

Effect: one fact carries **±5** of a score whose typical magnitude is 4–8. On
08-31 gamma supplied −5 of the −7.

If the −2 is removed, labels change on 3 of 9 graded calls (08-31 −7→−5,
08-27 +7→+5, 08-28 +6→+4) and two calls drop below the ±3 threshold to
no-call: **08-26 13:12 (was WRONG)** and **08-24 12:40 (was CORRECT)**. The
direction scoreboard is a **wash**. **Proposed on grounds of construction, not
measured accuracy** — it removes false conviction, not error. The −3 term is
NOT proposed for change on this evidence.

Second point against it: expansion has no sign. A short-gamma book forecasts a
bigger *range*, not a lower *close*, and it is scored as bearish.

## NEW — the below-flip rule is distance-invariant, and today that broke it

Price was 87.4 pts below the flip at 13:28 and inside the flip's 8-pt tolerance
by 13:30 — **the premise expired ~2 minutes after publication** and the day
closed 3.3 above the flip. `−3` is emitted identically at 87.4, 134.2, 146.1,
219.8, 249.1, 276.5 and **520.1** pts of distance. No proximity term, no reclaim
term.

**This is H10's defect in a heavier component.** H10 records that the
prior-week-range rule scores a state with no reclaim condition; the flip rule
has the same hole and more than twice the weight.

Proximity vs outcome, 9 graded calls: |dist| <150 → **1 right / 3 wrong**;
|dist| ≥200 → **3 right / 2 wrong**. Directionally consistent, far too thin.
**Status: OBSERVING. Nothing proposed on proximity.**

## NEW — the regime call was falsified, not just the arrow

Unlike 28 Aug (arrow wrong, regime right, 265-pt short delivered), 08-31 failed
at the regime layer. `COHERENT_SHORT` published *"expect range expansion and
trends that persist… today's ADR can be exceeded."* Range extension **0.0**,
181.6 pts of traversal inside an unchanged range, both extremes held, close
returned to open. A pinning day — the Strategy 1 day the brief explicitly ruled
out (*"fading is the wrong trade today"*).

Short-gamma days' extension error so far: **+79.8 / −73.0 / −124.7**. Sign
flips; n=3. **Nothing proposed.**

## H1 — 6 days, sign now 5 of 6 negative, still not actionable

Per-day error: +61.2 / −11.6 / −73.0 / −86.4 / −10.7 / **−124.7**. Mean
**−40.9** (was −27.5 at 4 days). 5 of 6 negative is p≈0.22 two-sided — not a
bias. Today's −124.7 is the entire budget, because the extremes were already in.

**Tempting slice, explicitly rejected:** all three `MODERATE` days over-read
(−73.0 / −86.4 / −124.7, mean −94.7) while `LOW_FUEL`, `EXHAUSTED` and
`ROOM_TO_EXPAND` were near-exact (+61.2 / −11.6 / −10.7). That is 3 points out
of 6 across 4 buckets, found after the fact. **Logged to test forward, not to
fit.** The standing blocker is unchanged: the budget is a linear ADR remainder
with no term for *where in the session the extremes were made*.
**Status: OBSERVING. Nothing proposed.**

## H4 — threshold MET (6 days). Verdict unchanged: not a magnet.

Added: **28 Aug** flip 29,265.1 vs close 29,454.8 = **189.7 miss**.
**31 Aug** flip 29,462.2 vs close 29,465.5 = **3.3 HIT**.

Running: **2 hits / 4 misses** — 1.1, 3.3 · 189.7, 236.6, 255.2, 599.8.
The register's verdict **"do not use the flip as a target" stands.**

Curiosity logged, **not** proposed: both hits came from **below-flip** scans
(2/2) and all four misses from **above-flip** scans (0/4). Two observations on
the hit side is not evidence. Record the side of the flip alongside the
close-to-flip distance from here.

## H6 — 6th consecutive day, same sign, no exceptions

Today by the board's `stretch` flag: non-stretch **6/7 = 0.86**, stretch
**0/3 = 0.00**.

Cumulative over 6 days, **pooled by level rather than averaged by scan** (per
M4): non-stretch **107/131 = 0.82**, stretch **15/39 = 0.38**.

- **Recommended (2nd time, unchanged):** report the two rates separately in the
  review. No scoring change; nothing published to the trader changes.
- **NOT proposed:** dropping stretch levels. 0.38 is a real reaction rate, and
  today's 0/3 contains one degenerate grade (D8 below).

## D8 CANDIDATE — a level that is already the day's extreme is graded as a forecast

08-31 published **"Asia Low (today) 29,223.8"**. That price *was* the session
low, made in Asia **before** the 13:28 scan.

| grader | verdict | why it is meaningless |
|---|---|---|
| `review_day` (scan onward) | **never reached** | counted as a miss; hit rate 0.60, stretch bucket 0/3 |
| `gex_retro` (whole day) | **BROKE**, settled above from open, worst **+0.0** | "worst excursion 0.0" is the level being the extreme by definition |

Neither number carries information: the level cannot be wrong and cannot be
right. Today it **deflated** the hit rate and **contaminated the H6 stretch
statistic**, which is the statistic closest to being acted on.

**This is a defect candidate, NOT a defect claim.** One clean instance is not
grounds for a code change, and I have not counted how often a published level
coincides with a pre-scan session extreme on earlier days.
**Next step: count the instances across 24–31 Aug before anything is changed.**

## Level classes — nothing is dead, nothing to stop publishing

Touch rate by class over 6 days (pooled): PDH 6/6, PD close 7/7, PWL 11/11,
NY Low 12/13, Asia High 10/11, London High 15/17, London Low 17/20, Equal highs
8/10, Equal lows 6/8, CALL WALL 6/9, MAX PAIN 5/8, PDL 8/13, PUT WALL 6/11,
**GAMMA FLIP 5/10**, **STRUCTURAL PUT WALL 3/10**. Lowest two are 0.30–0.50 over
4 days each — low, not dead, and confounded by distance. **Nothing proposed.**

## Not dead weight, despite scoring zero every time

`fuel` scored 0 in **29/29** emissions and `events` in **17/17** across 7 days.
Both are `add("fuel", 0, …)` / `add("events", 0, …)` — hardcoded narrative rows
by design, not decayed signals. **Do not remove them as dead weight.** They do
inflate the trader-facing "24 checks" count; cosmetic, not proposed.

## D7 — not a factor on 08-31

The single auto-scored headline (Warsh, hawkish) was correctly signed −1. The
`cpi_cool` negation bug does not touch this scan.

---

# Observations appended 2026-09-02 (trading day 2026-09-01, graded post-roll)

*Source: `review_day.py`, `track.py`, `brief.py` source. **7 trading days on
record (24–28, 31 Aug, 1 Sep).** Two gradeable scans, no test artefacts, both
committed by the archive flow at their own scan times. The 09-02 scan is held
back by `track.py` and enters nothing.*

Day: O 29464.6 H 29521.7 L 28954.2 C 29088.3, range **567.5 (147.7% of ADR14)**,
net **−376.3**. 13:22 BEARISH −8 → **+24.9 WRONG**. 14:42 BEARISH −8 → **−97.9
CORRECT**. Direction across 7 days: **5 right / 6 wrong / 3 no-call**.

## NEW — the level board collapses to structural-only whenever the budget is 0

`brief.py` sets `reach = "intraday" if abs(price - px) <= budget`, and `keep()`
retains a non-structural core level only when `abs(dist) <= budget * 1.75`.
**At `remaining_budget == 0.0` both tests are unsatisfiable.** Every session
extreme, PDH/PDL, PWH/PWL and the gamma flip drops to the footnote; only
`kind == "structural"` survives.

Levels published by fuel state: 08-24 13:45 EXHAUSTED/0.0 → **1**; 08-25 13:04
EXHAUSTED/12.0 → **3**; 09-01 13:22 and 14:42 EXHAUSTED/0.0 → **2** each; every
other live scan (budget 88.7–408.7) → **6–22**. Three days, no exceptions —
though only 08-24 and 09-01 had budget *exactly* 0.0, and the 08-25 21:56
overnight scan (1 level) is excluded because its budget was corrupt per D1.

The collapse lands precisely on the days the brief tells the trader that all the
remaining opportunity is *inside* the range. On 09-01 the whole board was two
structural walls that the brief itself labelled *"not an intraday trigger"*,
while four of the six in-range gamma concentrations were traded.

**PROPOSED** (publishing, not scoring; on grounds of construction, as with the
collinear gamma terms): floor the reach filter at a fraction of ADR14, e.g.
`max(budget, 0.25 * adr14)`. On 09-01 13:22 that would have put 29120.5,
29070.5, 28970.5 and the running low 29036.7 on the board — all four traded.
**Cost:** it lowers the headline hit rate by publishing more levels and it
changes what `stretch` means, so **H6's split must be re-based from the change
date.**

## DEFECT CANDIDATE — the in-range gamma concentration table is never graded

The *"Other gamma concentrations in range"* table is not written to
`prediction.levels`, so no grader sees it. On 09-01 it went **4 of 6 touched**
(29170.5, 29120.5, 29070.5 chopped or traded through; 28970.5 floored the day
16.3 above the low) while the graded board went **1 of 4**. So today's
`mean_level_hit_rate` of 0.25 was computed entirely off levels the brief told
the trader not to trade.

**One day of direct examination — NOT a proposal.** Next step: count, across
24 Aug – 01 Sep, touches of published in-range concentrations against the graded
board on the same scan. Sits with M4 and D8.

## H2 — third instance, all three the same way. Threshold met, no change proposed.

EXHAUSTED with price at a session extreme (≤0.1×ADR):

| scan | spot vs running extreme | bias | outcome |
|---|---|---|---|
| 08-24 13:45 | at the day's low | −12 continuation | fell 30.6 more, rallied 253.8 — **fade** |
| 08-25 13:04 | 0.4pt new high | 0 no-call | −256 into the range — **fade** |
| 09-01 13:22 | **18.8 above the running low (0.05×ADR)** | −8 continuation | extended 82.5, reversed 275.9, closed +32.8 — **fade** |

Continuation calls in this bucket: **0 right / 2 wrong**. Three days, same
direction. **Nothing proposed**: the natural consequence is H3 (cap the score at
extremes), and two wrong calls is not grounds to touch a scoring surface.
09-01 14:42 is **not** in this bucket — 173.6 (0.45×ADR) off the running low.

## The §2/§3 fade contradiction — 2 days, below threshold

09-01 13:22 §2: *"Fading is the wrong trade today — Strategy 2 is the right
one."* §3: *"Fading the extremes back into the range is the higher-probability
side here, even when the gamma regime favours continuation."* §3 was right.
Needs short gamma **and** exhausted fuel **and** price at an extreme: 08-24
13:45 and 09-01 13:22 only — 08-25 13:04 was above the flip. **2 of 3. Nothing
proposed.**

## H7 — fourth large short-interval flip move, and the biggest by distance

Flip **29575.6** at 13:22 → **29346.9** at 14:42: **−228.7 pts in 80 minutes**
while spot rose **+110.5**. Drift **2.1× the price move**. Prior: 192pt/2min
(08-24), 167.4pt/28min (08-25), 108.7pt overnight (08-26). The `gamma −3` term
is also **distance-invariant** — identical at **520.1** pts below the flip today
and at **87.4** on 08-31. **Status: OBSERVING. Nothing proposed.**

## H4 — two more misses, and the below-flip curiosity is dead

29575.6 vs close 29088.3 = **487.3 miss**; 29346.9 vs close = **258.6 miss**.
Both from **below-flip** scans, which retires the 08-31 note that both hits came
from below-flip scans. Per day: **2 hits / 5 misses**. *Do not use the flip as a
target* stands.

## H1 — 7 days, sign flips again

Per-day error: +61.2 / −11.6 / −73.0 / −86.4 / −10.7 / −124.7 / **+60.4**. Mean
**−26.4** (was −40.9 at 6 days). Today under-read on both scans (+82.5, +38.2)
from a 0.0 budget, because the extremes were **not** in — price extended 82.5
below the pre-scan low. That is the direct counter-case to 08-31, where a 0.0
budget was exactly right. The standing blocker is unchanged: the budget is a
linear ADR remainder with no term for where in the session the extremes were
made. **Status: OBSERVING. Nothing proposed.**

## H6 — 7th day. No non-stretch levels existed to measure.

Every published level was `stretch`: **1/4 = 0.25**, non-stretch **n = 0**.
Cumulative pooled by level: non-stretch **107/131 = 0.82**, stretch
**16/43 = 0.37**. Note the interaction with the finding above — on zero-budget
days the stretch bucket is the *only* bucket, so **the stretch statistic is
partly an artefact of the reach filter**, not a property of distant levels.

## The put wall floored the session again — 2nd consecutive day

09-01 29020.5 STRUCTURAL PUT WALL: touched 13:30, travel up **110.0** vs down
**28.1** (3.9:1), price rallied 275.9 off it. Graded *"chopped around it"*, which
understates a bounce. Meanwhile the brief's in-range table says put-dominant
strikes *"amplify… Not a floor."* Same on 08-31 (29263.1 PUT WALL ●●●●● floored
a session the model said had no floors). **2 days. Logged, nothing proposed.**

## D8 — a second instance, from the other direction

09-01 13:22 published **29320.5 STRUCTURAL CALL WALL** with the text *"the
ceiling for the WEEK/MONTH, not today… not an intraday trigger."* It was not
reached (52.2 short) and was **graded a miss**. A level the brief explicitly
says is not for today cannot be graded as a same-day forecast. D8's 08-31
instance was a level that was already the day's extreme; this is the mirror
case. **2 instances. Still a candidate, not a claim.**

## Macro components are autocorrelated — statistics on them have an inflated n

`macro −3` (real yield, DFII10) appears with **identical text and value**
(*"2.42%, up 8bp today and 2bp over 5 days"*) on **08-25, 08-28, 09-01 and
09-02**; `+3` on 08-26 and 08-27. DFII10 is a lagged daily FRED series, so
consecutive days share a value. **Any accuracy claim about the macro bucket has
an effective n far below the day count.** Recorded so no future review reads
four repetitions of one number as four observations.

## D7 — the fix makes this day's call worse, not better

`news +1` on the 13:22 scan came from the `cpi_cool` negation bug: three
mis-signed duplicates of a hawkish Barr story, **+6.6** of spurious bullish
weight. Corrected, the bucket is bearish and the score goes **below −8** — the
bug made a **wrong** call **less** wrong. D7 remains worth fixing as a
correctness matter; it must not be counted as an accuracy improvement.

## Gamma collinearity — now 20/20

The two gamma terms agreed in sign on both 09-01 scans (−3 / −2 below the flip).
**20/20 across all live scans.** Removing the −2 takes today's −8 to −6: still
BEARISH, still wrong. Confirms the earlier read that the removal buys honesty,
not accuracy.

## Not dead weight

`fuel` and `events` scored 0 on both scans again — hardcoded narrative rows by
design. **Do not remove.**

---

# MODEL CHANGES APPLIED 2026-09-02 (both authorised by the trader)

Two changes, both proposed in reviews and both applied today. Recorded here
because everything graded from this date carries different semantics.

## C1 — the level board no longer borrows the range budget's zero

**Was:** `reach = "intraday" if abs(price - px) <= budget`, and `keep()` held
non-structural core levels only when `abs(dist) <= budget * 1.75`.

**Defect:** at `remaining_budget == 0.0` both tests are unsatisfiable, so the
board collapsed to `kind == "structural"` alone. Verified across the journal —
the four zero-budget scans published **1, 1, 2 and 2** levels against **6–22**
for every other live scan. The collapse landed precisely on the days the brief
tells the trader the remaining opportunity is *inside* the range, and then
offered only week/month walls it labels "not an intraday trigger".

**Now:** both tests use `reach_span = max(budget, 0.25 * adr14)`. The budget is
still the range forecast and is unchanged; only the markable-distance filter
gets its own floor. A spent range does not mean price stops moving.

**Published wording changed with it.** The caption said *"Today's remaining
range budget is Npts — anything marked (stretch) is beyond that"*. Since
`stretch` is now flagged against the span, quoting the budget would state a rule
the board is not applying. It now reads **"Today's markable distance is Npts"**,
with an explicit note when the floor is active.

> ⚠️ **H6 MUST BE RE-BASED FROM 2026-09-02.** `stretch` no longer means the same
> thing: on a zero-budget day, levels that would have been absent (or flagged
> stretch) are now on the board unflagged. The 0.81 / 0.45 non-stretch vs
> stretch split was measured under the old definition and **cannot be pooled
> with anything graded after today.** Restart the count; do not merge the series.

Also expect the **headline level hit rate to fall**, because the board now
publishes more levels on exactly the days it used to publish almost none. That
is a cost the reviewer stated in advance, not a regression.

## C2 — the net-GEX gamma term is reported but no longer scored

**Was:** `add("gamma", -2 if net < -0.2 else (+2 if net > 0.2 else 0), ...)`.

**Defect:** the gamma flip *is* the spot where net GEX crosses zero, so "below
flip" and "net GEX negative" are one fact stated twice. Across **every scan on
record the two terms have never once carried opposite signs** (25 of 29 both
non-zero and same-signed; the other 4 had the GEX term at zero). Scoring both
let a single observation supply up to **±5 of a score whose typical magnitude is
4–8** — on 08-31 gamma supplied −5 of the −7. Separately, expansion has **no
direction**: a short-gamma book forecasts a wider *range*, not a lower *close*,
so the sign it contributed was never earned.

**Now:** scored `0`, with the regime read still published (`expansion likely` /
`pinning likely`) and marked *"not scored: same fact as the flip term above"*.
The information is preserved for the trader and for the shape section; only the
double-count is gone.

**Expected effect on the record: a wash.** Removing it changes labels on 3 of 9
graded calls and drops two to no-call — one had been WRONG, one CORRECT. That
is the point: **it removes false conviction, not error.** Anyone later reading
an unchanged hit rate as "the fix did nothing" has misread it.

Verified live on the 2026-09-02 chain (`--no-journal`): gamma printed **−3**
where it would have printed −5, and the call read BEARISH −9.

## What is NOT fixed by either change

The below-flip term is still **distance-invariant with no reclaim condition** —
an identical −3 at 107, 181, 204 and 520 points below the flip, all four
observed this week. C2 removes the double-count; it does not make the remaining
term proximity-aware. That is still open, and it is the same defect family as
H10 in a component with twice the weight.

`test_consistency.py`: **19 passed, 0 failed**, including three new checks — the
board surviving a zero budget behaviourally, no floor being invented when ADR is
also zero, and the net-GEX term scoring zero.

---

# MODEL CHANGES APPLIED 2026-09-03 (authorised by the trader)

## C3 — the gamma flip term is reported but no longer scored

**Was:** `+2` above the flip, `−3` below it, plus a straddle adjustment.

**The case, from the 8-day record (24 Aug – 2 Sep, 11 directional calls):**

| finding | figure |
|---|---|
| direction calls right | **4 / 11 (36%)** |
| when it called BEARISH | **2 / 8 (25%)** |
| when it called BULLISH | 2 / 3 (67%) |
| calls made below the flip | 8 of 11 |
| days price actually rose | 8 of 11 |

**The model called bearish 8 times out of 11 in a window where price rose 8
times out of 11.** That single mismatch accounts for most of the miss rate.

Per-component means per day: **gamma −1.9**, news −0.6, macro −0.2, structure
−0.2, rates −0.1, breadth −0.1, vol +0.5, fuel/events exactly 0. **Gamma was
effectively the entire bias** — everything else cancelled around it — and it
scored −5 on five days of eight, never landing between −4 and +1.

**Why it is wrong in principle, which is the actual justification.** Short gamma
means dealers amplify whatever move is already happening. That forecasts a
**wider range**, not a **lower close**. It is a volatility statement being
scored as a directional one — the identical error removed from the net-GEX term
in C2, in the term carrying more weight. The asymmetry (+2 vs −3) then made time
spent below the flip a structural bearish lean.

**Now:** both branches score `0` and publish as a regime read, marked *"tells
you the day's WIDTH, not its direction"*. The read still drives the shape
section and strategy selection, which is where it has been working.

**Bug retired alongside it.** The straddle adjustment read
`+1 if px > gf else +1` — **+1 on both branches** — so a term labelled "reduce
conviction" *increased* it above the flip (+2 → +3). It scored 0 now regardless,
since its only job was to damp a score that no longer exists.

**Expected effect: fewer calls, not better ones.** With gamma neutral, direction
comes from components that average near zero, so the model will return
NEUTRAL / TWO-WAY far more often. That is the honest output for a signal with no
demonstrated edge. On the recorded days this moves the hit rate 36% → 44% on 9
calls instead of 11 — **not significant** (see below), and not the reason for
the change.

> **Do not read the counterfactual as proof.** Overall 4/11 vs a coin flip is
> **p = 0.55**; bearish 2/8 is **p = 0.29**; bullish 2/3 is **p = 1.00**. None
> of it is statistically significant. C3 is justified by the reasoning error,
> which is visible in the code without any data. The record is only what
> prompted the look.
>
> **Explicitly rejected: inverting the model.** Flipping every call scores 7/11
> on this sample. It is three decisions from the current result, has no
> mechanism, and fitting to it is exactly how a model gets worse.
> **Do not re-propose.**

## D7 — FIXED: negated inflation phrasing no longer scores backwards

Logged 2026-09-01, fixed today. `cpi_cool` matched the tokens *ease* / *cool*
without the negation that inverts them, so *"support rate hike if inflation
doesn't ease"* scored **+1 BULLISH at HIGH confidence** on a hawkish story — and
at HIGH confidence it bypassed the judgement list where a human would catch it.

Fixed the way this file handles every other inverted reading: **do not guess the
flipped sign, demote to the model.** A `NEGATOR` match *inside the matched span*
adds a flag, and any flag routes the item to NEEDS_JUDGEMENT. Tested on the span
only, so "inflation cooled in August" still scores and "inflation doesn't cool"
does not.

**Second defect found while fixing the first.** After the negation guard, the
Bloomberg framing *still* scored +2.2 bullish — on a **curly apostrophe alone**.
Every `RULES` pattern is written with straight apostrophes, and `low` was not
normalised, so `Doesn't` and `Doesn’t` took different paths through the scorer.
Punctuation is now normalised at source, which fixes the whole class rather than
this instance.

**NOT done, deliberately: story-level dedupe.** One Fed speaker still gets four
votes when four outlets carry him. Title-token overlap across the four real
framings is only ~50–60%, so any threshold tight enough to collapse them would
also collapse unrelated stories — and this file's stated principle is that
over-filtering is the dangerous failure. After the sign fix the duplication only
inflates the *judgement list*, which a human reads and where duplication is
visible and harmless. Left open.

## Crash fix — the brief died when the vol feed had no prior close

Found running the C3 verification at 21:15 UTC on 3 Sep, just after the roll.
`vxn_c` was `None` and the volatility line formatted it as `{vxn_c:+.1f}`,
raising `TypeError` and **killing the entire brief** — while the three lines
immediately below already used `(vxn_c or 0)`. Now renders `chg n/a`. Not
coerced to 0, which would report "unchanged" as though it had been measured.

Pre-existing and unrelated to the model changes; it would have broken any scan
run in that window.

## Test coverage added

`test_consistency.py` **22 passed, 0 failed** — new: the flip term carries no
points, the news scorer demotes a negated match, punctuation is normalised.
`test_news_scorer.py` **29 passed, 0 failed** — new: all four D7 framings, the
curly-apostrophe framing specifically, plus controls proving un-negated hot and
cool prints still score.

## Where the evidence stands now

**No scan has yet run under the full model.** C1/C2 landed after the 2 Sep
13:25 scan and C3 today, so every graded day on record is pre-change. The
next scan is day 1 of the new series. H6's stretch split re-bases from
2026-09-02 and the direction record should be read the same way.

**The most valuable next action is not another change — it is days.** Eleven
calls cannot settle anything. Run the scan daily and let the record build.
