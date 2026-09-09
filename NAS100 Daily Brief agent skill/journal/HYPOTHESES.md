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

## H12 — Does the VOLUME-weighted wall hold better than the OI-weighted one?

**Claim.** GEXBot's volume-weighted GEX identifies levels price respects better
than our open-interest-weighted walls do.

**Why it matters.** It is the question that decides whether GEXBot *replaces*
the ladder or merely enriches it — and the volume lens is the one thing the
CBOE pipeline cannot build honestly, because volume carries no side.

**Evidence so far (0 sessions).** None. The only snapshot available at the time
of writing was Friday 4 Sep's close, frozen, so nothing could be graded.

What that snapshot *suggests*, and it is suggestion only: price closed at
29,542.65; the volume lens put its heaviest concentration at 29,525–29,550,
while our OI view showed 29,525 at approximately zero. One frozen observation,
after the fact, on an expiry day. **It proves nothing** — it is the reason to
run the test, not the result of it.

### The archive splits this hypothesis in two — verified 2026-09-05

The sibling recorder stores the **compact record only**: the per-strike ladder
goes to `gex_latest` (overwritten each poll) and is deliberately never appended
to `gex_snapshots`, because doing so would cost roughly 1 GB/month.

| Sub-question | Retro-answerable from the archive? |
|---|---|
| Does the **volume wall** hold better than the **OI wall**? | **Yes** — `major_pos_vol` / `major_neg_vol` / `major_pos_oi` / `major_neg_oi` are in every record |
| Do the two lenses disagree, and when? | **Yes** — `regimes_agree` / `walls_agree` are precomputed |
| Does the ranked **C1–C3 / P1–P3 ladder** hold? | **No, and never will** — per-strike history is not retained, by permanent design |

The headline claim is the first row, so the archive is sufficient for H12 *as
written*. The trap is that `gex_retro.py --ladder` grades a **ranked ladder
file**; pointing it at the archive would silently promise a comparison the data
cannot support. Any archive reader must use a separate path that marks its
output walls-only, so the limit is enforced rather than remembered.

**Threshold.** 5 sessions. For live scans, persist a GEXBot ladder alongside
ours and grade both with `gex_retro.py --ladder` and `role_reversal()` — same
rule for both, so they cannot drift. For archived days, walls only.

**Count UNCHANGED at 0 of 5.** Nothing has been recorded since the single
manual run against a frozen Friday feed; the cron is Mon–Fri and 5 Sep was a
Saturday. **Four documents per poll are two observations**, not four —
`NQ_NDX` is `NDX` plus a constant 30.82 and `ES_SPX` is `SPX` plus 6.13,
verified exact across every wall field, so the futures rows carry no
independent information.

**Update 2026-09-05 — the archive was read directly, not inferred.** The
sibling recorder's Firestore archive became readable from a Claude session and
was read field by field (`research/gexbot/EVALUATION.md` §11); the split above
is verified against the stored documents rather than against the recorder's
code. It changes no count: the archive held that one frozen Friday poll and
nothing else. A design for the walls-only reader — the one that must not reuse
`--ladder` — is in `research/gexbot/PROPOSAL-ARCHIVE-RETRO.md`, unbuilt until
Monday's data exists to test it against.

**Status: OBSERVING. Do not swap the engine.**

---

## H13 — Is GEXBot's `zero_gamma` a real flip, or a fallback to spot?

**Claim.** `zero_gamma` may not be an independently computed flip.

**Why it matters.** The flip decides which of the two entry models the brief
recommends. It is the single highest-consequence number in the scan, and H7
already established that our own flip is unstable enough to be the largest
contributor to a wrong call.

**Evidence so far (1 frozen snapshot).** On 2026-09-04's close `zero_gamma`
equalled `spot` **exactly** (29,542.65) for both `gex_full` and `gex_zero`. It
differed for `gex_one` (29,470.0), which argues it is computed rather than
stubbed, and Friday was an expiry with heavy pinning — so equality is
plausible. But a computed value landing exactly on spot to two decimals earns
suspicion, not the benefit of the doubt.

For reference, our own flip on the same snapshot was **29,323.2 — 219 points
away**.

**The stub theory is dead — verified 2026-09-05.** On the *same feed at the same
instant*, `zero_gamma` differs from `spot` on three of four symbols:

| | spot | zero_gamma | diff |
|---|---|---|---|
| **NDX** | 29,542.65 | 29,542.65 | **0.00** |
| SPX | 7,717.85 | 7,712.50 | −5.35 |
| RUT | 2,975.32 | 2,970.08 | −5.24 |
| QQQ | 718.95 | 717.34 | −1.61 |

**A field stubbed to spot could not differ on SPX, RUT and QQQ.** So it is
computed. QQQ matters most here: it is the *same underlying* as NDX and still
returns −1.61, which rules out "their Nasdaq calculation degenerates" as the
explanation.

**This does not rehabilitate the number.** It reframes the question from *"is it
a stub?"* (answered: no) to *"why does the one symbol we trade land exactly on
spot?"* — for which coincidence on a heavily pinned expiry Friday remains the
leading explanation, and one snapshot cannot distinguish it from anything else.
A computed flip sitting on spot is just as unusable as a stubbed one.

**Update 2026-09-08 15:39Z — second observation, and the pattern does not hold.
Count 1 -> 2 of 5.** Read live during the RTH scan, off the same feed:

| | spot | zero_gamma | diff |
|---|---|---|---|
| **NDX** (`gex_full`) | 29,582.66 | 29,532.36 | **-50.30** |
| **NDX** (`gex_zero`) | 29,583.02 | 29,491.02 | -92.00 |
| **QQQ** | 720.06 | 717.59 | -2.47 |

On 4 Sep NDX's `zero_gamma` sat **exactly** on spot. On a live RTH feed it does
not -- it is 50pts below, and the two books disagree with each other (-50.30 vs
-92.00), which a spot fallback could not do on either count.

**This is evidence FOR the coincidence reading, not merely absence of evidence
against it.** 4 Sep was a heavily pinned expiry Friday; the equality did not
survive the first non-expiry session. Nothing structural about the Nasdaq
calculation degenerating -- it computes, and today it computed away from spot.

It is still not usable as a flip, and the reason is unchanged: on the same
snapshot ours read 29,405 and theirs 29,525, **119pts apart**, and the board
uses ours. Two of five. Three more RTH samples before this says anything.

*Earlier framing, kept because it was the reasoning at the time:* a working
credential and a cleaner argument both read like progress; neither was a second
observation.

**Threshold.** 5 RTH samples. Record `zero_gamma`, their `spot`, and our flip on
every scan — **and record it for QQQ alongside NDX**, since a same-underlying
control is now known to be informative.

*Provenance: the four-symbol table above was read out of the archived 4 Sep
record field by field (`research/gexbot/EVALUATION.md` §11), on one feed at one
instant — which is what makes the cross-symbol comparison valid. It is still
that same single snapshot.*

**Status: OBSERVING. Do not use as the flip.**

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

# Observations appended 2026-09-08 (trading day 2026-08-28 — NOT GRADED)

Full working: `journal/2026-08-28/REVIEW.md`. **Nothing below is a calibration
proposal, and no hypothesis count advances.**

**Status: the evidence base did not move.** `track.py` still reads **4 trading
days / 10 scans (24–27 Aug)**. 2026-08-28's only journal entry carries
`test_artefact: true` ("Run to verify sync_archive.py self-commits a scan"), so
`review_day.py` correctly returns *no journal entries*. Today's 2026-09-08 scan
is correctly `HELD BACK — day not finished` (D3's fix working as intended; it
was not graded).

**The binding constraint is not calibration, it is observation rate.** 08-28 has
no real scan, and **31 Aug and 1–4 Sep have none at all** — confirmed against
`research/chart-ladders/`, which jumps `2026-08-27-2233` → `2026-09-08-1539`.
Nothing was lost; nothing was run. Eleven calendar days have passed since the
last graded session and H4/H6 (5 days) and H8 (10 days) are exactly where they
were. No amount of analysis substitutes for sessions.

**H1 — no new point.** Per-day series unchanged: `+61.2 → −11.6 → −73.0 → −86.4`,
mean −27.5. Still a monotonic trend, still no multiplier proposed. Still waiting
on an unpinned / short-gamma day.

**H4 — no countable point.** The 08-28 flip 29145.6 sat **231 pts below** the
session low (29376.4) and was never approached. Consistent with 1 hit / 2 miss,
but **excluded**; the register stays at 3 of 5 days.

**H6 — do not let this reach threshold on the current instrument.** See M4 below.
PD mid chopped again on 08-28 (`up 258.1 / dn 46.1`), a fourth consecutive
session — **not counted**.

**H10 — not testable on 08-28.** The scan read `structure 0, price inside the
prior-week range (29115.9–30245.8)`. Still **1 of 3**.

**Checked and found to be nothing (recorded so it is not re-proposed).**
Across all graded scans the `fuel` component scores 0 points in **25 of 25**
instances and `events` in **14 of 14**. That is not dead weight — D1 already
states *"fuel reports and never votes"*, and `bias_engine.py:176,181,239`
hard-codes `add(..., 0, ...)`. **No proposal.** Every other component is live:
gamma 64% nonzero, vol 63%, breadth 60%, macro 58%, structure 53%, rates 47%,
news 26%. The only residue is presentational — non-voting rows sit inside
`bias_components` carrying a `points` field alongside the rows that do vote,
which invites a reader (or a reviewer agent) to infer they contribute.

**Not opened, 1 instance, recorded so the count is honest.** On the 08-28
artefact `breadth +2` came from *"mega-cap avg +3.83%, NVDA +8.74%"* — a
post-earnings pop read as forward direction, on a day that closed −115.6. One
instance is not a hypothesis. It is **not** being opened here; if it recurs
twice more, write it up properly. (Per the H9 lesson: a hypothesis is opened by
writing it in this register, not by mentioning it.)

## Methodology items awaiting a decision (not calibration, so not 3-day gated)

**M3 — `latest_unreviewed()` returns a day it then refuses to grade, and calls
the refusal an error.** `review_day.py:204` filters on `is_trading_day` but not
on `test_artefact`, unlike the matching filters at `review_day.py:75` and
`track.py:82`. It returns `2026-08-28`; `review()` then answers `{"error": ...}`
instead of the `{"status": "skipped"}` shape that exists for non-gradeable days,
so a caller distinguishing *skip* from *failure* sees a failure. Separately,
nothing in the codebase reads `REVIEW.md` — `grep -rn "REVIEW.md" --include=*.py`
returns nothing — so "unreviewed" is a misnomer: it returns the most recent
trading day whether or not it has been reviewed. Same shape as D1/D3: **a filter
written in three places and kept consistent in only two.**

**M4 — H6 is being tallied off a label D5 already established is unreliable.**
D5 recorded that `grade_level` scores the first touch only, has no concept of
role reversal, and that *"broke UP through it counts as a failure"*. Its fix was
deliberately **additive**: `gex_retro.role_reversal()` was added and
`grade_level` left unchanged. But `review_day.py` still emits the `grade_level`
string, and H6's evidence (*"traded both sides — chopped remains the dominant
outcome"*, hit rate 0.56–0.58) is tallied from exactly that string. Two
sub-faults, each verifiable from a single row:

1. **Near-misses count as touches, and then as breaks.** `TOUCH_TOL = 8.0`
   admits bars whose high never reached the level; the reaction string then
   reports the direction of subsequent travel. Instances in the graded archive:
   08-24 08:28 `MAX PAIN 29099.3` (`travel_down −5.1`, "broke UP through it");
   08-24 08:30/32/33 `PWL 29115.9` (`−0.9`); 08-27 13:23 `PDH 29353.8` (`−7.0`);
   and, unmasked but not counted, 08-28 `CALL WALL 29645.0` (`travel_up −4.5`).
   **Two graded days plus one excluded day.** This is already inside an open
   hypothesis: H6's cull case against MAX PAIN (*"touched on 3 of 4 scans and
   never stalled price once"*) rests partly on a 5.1-pt near-miss.
2. **First-touch blindness is still in the published output.** On 08-28 the
   heaviest level on the board — `29645 CALL WALL ●●●●● 1.30bn` — graded
   *"broke DOWN through it"* off a 02:15 UTC near-miss, while price traded
   **above it for 14 bars (14:35–15:40 UTC) to a high 103.3 pts through it**.
   The output says the wall broke downward on a day price broke it upward.

*Decision needed before H6 reaches 5 days:* is H6 tallied from
`role_reversal()` or from `grade_level`, and should `travel_up < 0` /
`travel_down < 0` report a near-miss rather than a touch-and-break? Re-deriving
after the threshold is hit would mean culling levels on a polluted statistic.

**M5 — `test_artefact` is one flag doing two different jobs.** On 27 Aug it
marked **verification re-runs**: one market state journalled five times, where
exclusion is unarguably right because counting them turns one observation into
five. On 28 Aug it marks a **plumbing test that produced a unique, live,
uncontaminated forecast** — a market state sampled exactly once, on a real
trading day, `prediction` written before the outcome was known. Excluding the
first prevents inflation; excluding the second **discards a real observation**,
and here it discarded a **wrong** one (bias +4 MILDLY BULLISH; the session closed
−115.6), i.e. it failed in the flattering direction — the precise shape of the
D1/D3 lesson. **Not proposed and not counted.** But the flag needs two names —
`duplicate_of` vs `provenance: plumbing-test` — and which one 28 Aug carries is
the trader's call, not the reviewer's.

---

# Defects found 2026-09-09 (during the live scan, before delivery)

## D6 — a FRESH timestamp on a STALE price inverted the regime call

**What happened.** The 15:13Z build published `CFD/index offset -131.3`, from
`NDX reference 29498.6` against a CFD at 29367.3. The true offset was about
**-3**. Every options level on the board — call wall, put wall, max pain, the
flip, every secondary concentration — was **~128pts too low**.

**Why it mattered more than a shift.** The flip published at 29281.8 with price
85.5pts above it, so the brief called **long gamma, Strategy 1, "this is your
fade day"**. Corrected, the flip sat at ~29,409 with price at ~29,371 —
**below** it. The regime was inverted, and with it the entry model.

**How it got through.** `_cash_is_stale()` checks the quote's *timestamp*.
CBOE's `_NDX` returned `last_trade_time` 16 minutes old — inside the 30-minute
tolerance — alongside `current_price` 29,510.7 while the index was actually at
29,376. On a later poll the timestamp advanced by a minute and the price did
not move at all: the feed was ticking its clock, not its value. The quote's own
reported session low (29,393) was already above the live index, which is
internally impossible and was the tell.

**The root cause is one already in this register:** a guard written against a
**proxy** (recency of the timestamp) rather than the **definition** (is this
price current?). Same family as D3's `bars < 150` and D4's missing dominance
test. The docstring on `_nq_implied_cash` records the *previous* time this bug
bit — a -200.7 offset from a stale Monday pre-market close — and the fix then
was the very timestamp check that failed here.

**Two independent confirmations, which is what made this safe to act on:** live
`^NDX` read 29,376.2 and GEXBot's own `spot` read 29,372.72. CBOE alone
disagreed.

**Fix.** `_ndx_live_yahoo()` provides an independent live print;
`gex_levels.build()` compares it against CBOE's and, past
`CASH_DIVERGENCE_TOL = 25.0` pts, anchors to the independent print and labels
the basis `live_cash_divergence_corrected`. The divergence is now always
recorded in `basis` even when it passes, so the check is visible rather than
silent. The timestamp path is unchanged and still handles the closed-market
case, where both sources agree on the same close and the value check correctly
does not fire.

**What this does NOT fix.** Both sources could lag together. The check proves
disagreement, never freshness.

## D7 — the strongest ceiling on the chain appeared nowhere in the brief

Found while verifying D6's fix: the corrected 15:16Z board carried **no CALL
WALL row at all**, though the wall existed (29,500 NDX, 1.32bn, 18,832
contracts, and the 45-day call wall too).

Two filters compounded:

1. `keep()` in `brief.py` drops a CORE level beyond `budget * 1.75`. Against a
   64pt budget the cap was 112pts. The call wall at +140 was dropped; the put
   wall at -110 survived **by two points**. The asymmetry was accidental — it
   tracked where price happened to sit, not anything about the walls.
2. The footnote then rendered `far[:6]`. Six liquidity levels sorted ahead of
   the call wall, so it was truncated out of the fallback as well.

Dropped from the board *and* from the footnote, the level ceased to exist in
the output — with no warning, because each filter did what it was written to do.
This breaks the skill's own contract (*"Never invent a level. Everything
markable comes from the level board"*): a level absent from the board cannot be
marked. It defeats the wall-to-wall strategy this chart was built to serve.

**Fix.** `far_line()` partitions the footnote so `CALL WALL`, `PUT WALL`,
`GAMMA FLIP` and `MAX PAIN` are never truncated; the 6-item cap now applies to
what remains. **`keep()` is deliberately unchanged** — altering it would change
which levels get marked and their stretch tags, which is model behaviour and
belongs behind the evidence gate. This fix only guarantees that a wall the
budget filter rejects still gets *said*, in the footnote, where it always
should have been.

**Open question for the register, not acted on:** whether a wall should be
subject to the range-budget filter at all. It is a dealer-hedging boundary, not
a distance-from-price forecast, and the stated strategy is to trade from one
wall to the next. Needs evidence, not a same-day edit.

## Journal hygiene for 2026-09-09

Three entries exist for one scan (1513, 1517, 1520). **1520 is the record.**
1513 is marked `test_artefact` with `artefact_reason: defective_build` (D6),
1517 with `artefact_reason: verification_rerun`. `track.py` reads 5 trading
days / 11 scans and holds today back as unfinished, which is correct.

`artefact_reason` is the discriminator **M5** asks for — the same flag was
doing two jobs. It is written here but **no reader consumes it yet**; the M3/M5
decision should settle how all three sites filter, rather than a fourth
condition being bolted on mid-scan.

---

# Observations added 2026-09-08 review (written 2026-09-09)

Source: `review_day.py 2026-09-08 --json`, `track.py`, plus a live FRED read.
One gradeable scan (15:39Z NY_MIDDAY), 0 test artefacts. Full write-up in
`journal/2026-09-08/REVIEW.md`. **One item proposed (P1, a defect). Everything
else is an observation appended to an existing open item.**

## P1 — FRED observations carry an age and nothing reads it; the brief says "today"

**PROPOSED — defect, not calibration.** The 09-08 call was bias **+4 MILDLY
BULLISH**; price fell 83.3 and the session closed −82.6. Bucket decomposition:
`gamma +2, vol −3, rates 0, macro +6, breadth +1, fuel 0, structure −1,
news −1`. **Strip macro and the score is −2 — the correct sign.** Macro alone
flipped the call.

Inside macro: `real_yields` **+3**, `yield_decomp` +1, `credit` +2, rest 0.
`real_yields` is the **heaviest single term in the whole engine**
(`bias_engine.py:136`, `_W["real_yields"] = 3`) and it read DFII10 as *"down 3bp
**today**"*. DFII10's latest observation available on 2026-09-08 was
**2026-09-03** — a Thursday value printed as "today" on a Tuesday, **3 business
days stale**. `bias_engine.py:132-133` justifies the macro weight with *"FRED
publishes with a 1-2 day lag"*. Nothing enforces it.

The staleness was visible **in the same brief**: `yield_decomp` honestly printed
*"(2026-09-02 to 2026-09-03)"* directly under a "today" that contradicted it.

**Structural aggravator.** `aligned_change()` exists precisely to stop
cross-series lag mismatches — and only `yield_decomp` (weight 1) uses it.
`real_yields` (weight 3) takes DFII10's own `chg_1`, unaligned and unaged. **The
heaviest term is fed by the stalest series, by construction.** Verified live
2026-09-09: `T10YIE` and `BAMLH0A0HYM2` current to 09-08 while `DFII10`/`DGS10`
stop at **09-04** — a 4-day spread across series the engine mixes.

**Systemic — decomp interval vs scan date, all 6 gradeable days:** 08-24 uses
08-19→08-20 (4d) · 08-25 uses 08-20→08-21 (4d) · 08-26 uses 08-21→08-24 (2d) ·
08-27 uses 08-24→08-25 (2d) · **09-08 uses 09-02→09-03 (5d)** · 09-09 uses
09-03→09-04 (5d).

**Why this is not gated:** same family as **D6** — a component justified in a
comment by an assumed freshness that no code enforces. D6/D7 precedent is that
defects are fixed on discovery. **No new data point is needed:** `series()`
already returns the observation `date`; `interpret()` never reads it.

*What to change (user's call, nothing edited):* render the observation date
instead of "today", and damp or zero a FRED item older than N business days.
**N is deliberately unspecified — that is calibration and needs its own
evidence.** Expected effect on 09-08: `real_yields +3` does not fire, bias lands
at +1 or −2 instead of +4, direction call goes from WRONG to neutral-or-correct.

**What was right and got outvoted:** the engine already held −6 of same-day,
tech-specific bearish evidence — `gamma −2` (price **84.8%** up the
29402.2–29602.2 wall band; it turned within 43pts), `vol −3` (VXN 21.68 **+8.2%**,
VXN/VIX 1.4), `structure −1` (below PD mid). All three correct, all outvoted by
last week's rates data.

## NOT proposed — new watch items opened 2026-09-08

**W1 — macro block weight.** `|macro| ≥ 5` on the **last 5 consecutive deduped scans**
(08-26 13:12 onward), and on 5 of 11 scans overall. Macro alone flipped the sign
of the bias on **2 of the 5 gradeable days**: 08-25 13:04
(bullish→neutral, directionally **right**) and 09-08 (bearish→bullish,
**wrong**). **1–1 is not evidence.** Watching: how often macro alone determines
the sign, and its hit rate when it does. **Do not touch `_W`.**

**W2 — `credit` scores a level, not a change.** `fred_probe.py:187` is
`signal = 1 if hyv < 3.0`, weighted 2. HY OAS has been below 3.0 on **every day
on record** (2.65% on 09-08) — a standing +2 to the bull side rather than a
signal. This is the "component is dead weight" test, but there is no session yet
where HY OAS was above 3.0 or widened >15bp/5d, so what it does when it *moves*
is unknown. Watching: the first such session.

**W3 — PD mid / PD close may be noise.** On 09-08 they were published at
**+3.1** and **−1.5** from spot. A level 2–3pts from price cannot be a reaction
point. One scan. Watching: distance-from-spot at publication, and reaction
grade, across 3+ scans before any cull is argued.

**W4 — level hit rate is not independent of the fuel budget.** `brief.py:359`
sizes the board by `budget * 1.75`, so an EXHAUSTED day publishes a narrow board
and scores a high hit rate almost by construction. 09-08: budget 26.2 → board
span **84.2pts**, post-scan traversal **146.6pts**, hit rate **1.00** (0.86 on
strict touches). **H6 should normalise hit rate by board span ÷ traversal**, or
it will read "levels are working" hardest on the days the board says least.

## Evidence appended to existing items

**M4 — third graded day, and its worst instance yet.** 3 of 7 published levels
were admitted by `TOUCH_TOL = 8.0` without price reaching them: **29614.9**
(`travel_up −0.8` — **never touched at all**, post-scan high 29614.1, yet graded
*"broke DOWN through it"*), 29574.9 (1.9 short), 29570.3 (6.5 short).

**For the first time the tolerance changed the VERDICT, not just the
timestamp.** Starting the 12-bar window at 15:40 instead of the true first touch
at 15:55 gives PD mid `travel_up 39.2` and PD close `43.8` → *"traded both sides
— chopped"*. From the true touch they are **16.5** and **21.1**, both under
`REJECT_PTS = 25` → *"broke DOWN through it"*. H6's headline result is *"chopped
is the dominant outcome"*; on this day **2 of its 3 chop verdicts are tolerance
artefacts**, and they mask clean downside breaks on a day that closed −82.6.
**The M4 decision should be made before H6 reaches 5 days.**

**H2 — the sample does not match the claim.** `track.py:208` selects on
`fuel_state in ("LOW_FUEL","EXHAUSTED")` only; H2's own text requires
`LOW_FUEL`/`EXHAUSTED`-**at-extreme**. Position within the range-so-far at scan,
for the 6 rows the tracker lists: **18%, 33%, 29%, 5%, 77%, 52%** (09-08 is the
52%). Only 08-24 13:45 (5%) qualifies. **H2 stands at 1 valid observation of 3,
not 6.** Same shape as M3/M4 — a statistic tallied off a filter that does not
implement the definition it is labelled with. **09-08 must NOT be counted toward
H2.** Recorded; not proposed.

**H1 — 5th point breaks the monotone run.** Per-day errors: +61.2, −11.6, −73.0,
−86.4, **−26.2** (mean −27.2). The four-point slope H1 refused to fit a
multiplier to is gone; the series now reads as noise around −27.2 rather than a
trend, which **strengthens** H1's existing "do not fit a multiplier" conclusion.
Caveat: the 09-08 point is **low-information** — a NY_MIDDAY scan at 92.8% ADR
with both extremes already in can only score near-zero extension. Fuel was in
fact the model's best call of the day: budget 26.2, extension **exactly 0.0**.

**H4 — 5 of 5 days recorded, still weak.** Flip 29405.3, close 29496.0 →
**90.7pts**. Series: 1.1 / 236.6 / 255.2 / 599.8 / 90.7 — one hit, four misses.
Do not use the flip as a target.

**H12 — first live trading-day observation (1 of 5).** GEXBot volume lens
29,452–29,592; OI lens 28,992–29,267. Post-scan range **29,467.5–29,614.1**. The
volume band bracketed the actual range to within **16–22pts**; the **OI band sat
entirely outside the day**, ~200pts below the session low. Our own CBOE call
wall (29,602.2) agreed with the volume lens to 10pts and marked the post-scan
high. One session, graded post-hoc, with the OI book mid-roll — **it proves
nothing**. Count 1 of 5.

**D7's open question — second instance, one day EARLIER than D7 itself.** On
09-08 `keep()`'s `budget * 1.75` cap was **45.8pts** against a 26.2pt EXHAUSTED
budget, so the board was a ±46pt window while the day's range was **339.3**.
**PUT WALL 29402.2, MAX PAIN 29427.2 and GAMMA FLIP 29405.3 were all dropped.**
The session low was **29394.8 — 7.4pts below the put wall, 10.5pts below the
flip** — and the 177pt bounce that carried price up to the scan started there.
The brief's own text called 29402.2 *"dealers are SHORT gamma here… price
accelerates THROUGH rather than stall. **Not a floor**"*. It was the floor. Not
forward-gradeable (the low was pre-scan), and D7's footnote fix landed 09-09, so
this is evidence for the **open question** — should a wall be subject to a
range-budget filter at all — not for the fix.

## One more thing worth recording: the prose contradicted the score, and the prose won

§3 of the 09-08 brief said *"The day's range is set… Fading the extremes back
into the range is the higher-probability side here, **even when the gamma regime
favours continuation**."* That was exactly right — extension 0.0, and the
post-scan high at 29614.1 was faded 147pts. The headline said **MILDLY
BULLISH**. Two outputs of the same document disagreed, neither acknowledged the
other, and a reader following the headline lost while a reader following the
fuel paragraph won. Not a hypothesis and not proposed — but if it recurs twice
more it should be written up as one.

## P1 — the heaviest macro term is fed by the stalest series, by construction

Raised by the 2026-09-08 review; the structural half verified independently
2026-09-09.

**The day.** 08-09 scored `+4 MILDLY BULLISH`; the session closed **-82.6**.
Component split: `gamma +2, vol -3, rates 0, macro +6, breadth +1, fuel 0,
structure -1, news -1`. **Strip macro and the score is -2 — the correct sign.**
Macro alone flipped it, and -6 of correct same-day evidence (price 84.8% up the
wall band, VXN +8.2%, below PD mid) was outvoted by it.

**Where the +6 came from.** `real_yields` contributed +3 — the heaviest single
term in the engine — off DFII10 reading "down 3bp **today**". DFII10's latest
observation available that day was **2026-09-03**, three business days old.

**Verified live on 2026-09-09**, independently of the review: DFII10's latest
observation is `2026-09-04`, three business days stale, and the rendered line
said "up 1bp **today**". The `date` field is present in the payload and gated
nothing.

**The structural fault.** `fred_probe.aligned_change()` exists precisely to stop
this — its own docstring says *"FRED series publish on different lags"*. It is
used at `fred_probe.py:164` by `yield_decomp`, **weight 1**. `real_yields`,
**weight 3**, takes DFII10's raw `chg_1` at `fred_probe.py:145`. And
`bias_engine.py:130-131` justifies the macro weights with *"FRED publishes with
a 1-2 day lag"* — a constraint asserted in a comment with nothing enforcing it.

**Same family as D6**, one day apart: a rule stated in prose rather than code.
D6 was a guard against a proxy; this is a guard that was never written at all.

**Done now (correctness, not calibration):** the line no longer says "today"
about an older observation. It prints the observation date, warns when FRED has
not published in more than one business day, and carries `obs_date` and
`obs_age_business_days` in the payload. This makes the staleness visible on
every scan.

**NOT done, and deliberately: a stale reading still VOTES at full weight.**
Whether it should — decay the weight, gate the signal past N business days, or
route `real_yields` through `aligned_change()` like `yield_decomp` — is
calibration and belongs behind the evidence gate. One day is one day, however
cleanly the arithmetic reads. **The user's call.**

## Additional evidence on M4, from the 2026-09-08 review

**First case where the touch tolerance changed a VERDICT, not just a label.**
29,614.9 was never touched — the post-scan high was 29,614.1 — yet it graded
*"broke DOWN through it"* off `travel_up -0.8`. Separately, starting the window
at 15:40 instead of the true 15:55 touch turned PD mid / PD close from
`travel_up 16.5 / 21.1` ("broke DOWN") into `39.2 / 43.8` ("chopped").

**H6's headline result is "chop is dominant". Two of this day's three chop
verdicts are artefacts of the tolerance**, and they masked clean downside breaks
on a -82.6 day. **The M4 decision needs making before H6 reaches 5 days**, or
the hypothesis gets settled by its instrument rather than by the market.

## H2's sample does not implement H2's definition

`track.py:208` filters on **fuel state alone**; H2 is defined as *at-extreme*
fading. Position-in-range for its six listed rows: 18%, 33%, 29%, **5%**, 77%,
52% — only one qualifies. **H2 is at 1 of 3, not 6**, and 2026-09-08 should not
count toward it. Recorded, not fixed: changing the filter changes the sample.

## The 7/7 level hit rate is close to tautological

`keep()` sizes the board by `budget * 1.75`, so 08-09's 26.2pt budget produced a
±46pt board inside a 147pt traversal — levels that near price are almost
guaranteed to be touched. Strict-touch scoring gives **6/7 (0.86)**, not 1.00.

Meanwhile the same filter dropped the put wall, max pain and the flip — and the
session low (29,394.8) landed **7.4pts below the put wall and 10.5 below the
flip**, which is where the 177pt bounce began. **This is a second instance of
D7's open question, observed the day before D7 was found.** Two instances, not
three. Still observing.

---

# Retrospective 2026-09-09: the gamma engine against 12 days of price

Ran on request. Method: `fetch_ohlcv_paged` 16 days of M5 (3,263 bars, 08-25 to
09-09), every post-fix ladder graded against the next trading day, and each
published flip/strategy cross-tabbed against what the day actually did.

**Ladders EXCLUDED as invalid, per H11's withdrawal:** `2026-08-26-2212` and
`2026-08-27-1323`, both `pre_fix: True` (45-day book, before the book-mismatch
and wall-dominance fixes). The first draft of this retrospective used both and
had to be thrown away — the same error H11 already records. Valid pairs:
`08-27-1358 -> 08-27` (clipped to post-publication bars), `08-27-2233 -> 08-28`,
`09-08-1539 -> 09-09`. 18 rungs.

## H11 — the ranked walls WORK, and the grader was hiding it

**9 of 18 rungs were touched. Of the 8 with a settled read, 7 HELD.**

| rung | day | worst excursion | held for | re-tests | settled verdict |
|---|---|---|---|---|---|
| C3 29,602 | 09-09 | **+0.8** | 870 min | 2 | HELD as resistance |
| C2 29,414 | 08-27 | +1.6 | 540 min | 1 | HELD as support |
| C1 29,464 | 08-27 | **-4.7** | 430 min | 2 | HELD as support |
| C3 29,514 | 08-27 | -11.2 | 240 min | 2 | HELD as support |
| C1 29,495 | 08-28 | +12.6 | 280 min | 1 | HELD as resistance |
| C3 29,645 | 08-28 | +14.9 | 315 min | 1 | HELD as resistance |
| P1 29,352 | 09-09 | -18.2 | 325 min | 1 | HELD as support |
| P2 29,402 | 09-09 | -30.4 | 260 min | 8 | **LOST** |

**The same 8 rungs under the shipped first-touch grader: FOUR "chopped", TWO
"broke DOWN", ONE "broke UP", ZERO recorded as holding.**

**0 of 8 versus 7 of 8, on identical data.** This is no longer an argument about
M4 — it is a measurement. Two cases carry it on their own:

- **C3 29,602 on 09-09.** First touch at 02:40 says *"broke DOWN, 79pts"*. The
  settled read: worst excursion **0.8 points**, held **870 minutes**, re-tested
  twice and rejected both times. That is close to a perfect ceiling and the tool
  called it broken.
- **C1 29,464 on 08-27.** Worst excursion **-4.7pts** over 430 minutes. This is
  the level the trader described as *"swept through and reversed back above it
  soon after and never broke through again and worked as support"* — his reading
  reproduced to the point. The tool said CHOP.

**H6's headline finding ("chop is dominant") is an artefact of its instrument.**
Under the settled read, chop is not dominant; holding is, 7 to 1.

### The put ladder is the half that does not work

Split by side, the picture is completely different:

| | rungs | touched | held |
|---|---|---|---|
| Calls (C1-C3) | 9 | 6 | **6 of 6** |
| Puts (P1-P3) | 9 | **2** | 1 of 2 |

Six of nine put rungs were **never reached** — 08-27's P1 sat 331pts below spot
and P2 631pts below; 08-28's P1 was 479pts below. **The put side is ranked by
gamma force with no proximity filter and lands outside any tradeable distance.**
That is precisely H11's original claim, now with valid evidence behind it, and it
is a *side-specific* failure rather than the whole-ladder failure the withdrawn
observation asserted.

The one put failure is also the one rung with **8 re-tests** — repeated tapping
looks like distribution rather than defence, and may be a usable tell. One
instance; noted, not proposed.

**Count: 3 valid ladder-days.** The 5-day threshold is not met. Nothing changes.

## H7 — the overnight flip is worse than unreliable; it inverts the strategy

Strategy recommendation against what each day actually paid (day shape = where
price closed in its range; >=75% or <=25% means the move RAN and Strategy 2 was
right; 35-65% means it FAILED BACK and Strategy 1 was right):

| day | shape | close@ | scans -> strategy |
|---|---|---|---|
| 08-25 | FAILED BACK (S1) | 50% | 13:04 **S1 ✓** · 21:56 S2 ✗ |
| 08-26 | RAN (S2) | 99% | 13:12 **S2 ✓** · 13:14 **S2 ✓** · 21:43 S1 ✗ · 22:11 S1 ✗ |
| 08-27 | mixed | 65% | 13:23 S1 ~ |
| 09-08 | RAN (S2) | 23% | 15:39 S1 ✗ |
| 09-09 | FAILED BACK (S1) | 40% | 15:20 **S1 ✓** |

**Overall 4 right / 4 wrong — the same coin flip as the direction call. But it
separates cleanly by session:**

- **In-session scans (PRE_NY, NY_MIDDAY): 4 right, 1 wrong, 1 mixed.**
- **OVERNIGHT scans: 0 right, 3 wrong.**

Every overnight scan called the wrong strategy, and did so by naming the wrong
regime. The mechanism is measurable in the published numbers:

| day | flip range across the day's scans | price moved | regime label |
|---|---|---|---|
| 08-24 | **389.1pts** over 8 scans | 258.7 | ABOVE *and* BELOW — **contradicted itself** |
| 08-25 | 294.7pts over 2 scans | 201.6 | ABOVE *and* BELOW — **contradicted itself** |
| 08-26 | 299.6pts over 4 scans | 153.2 | ABOVE *and* BELOW — **contradicted itself** |

On 08-24 the flip moved **389 points while price moved 259** — the flip is more
volatile than the thing it is measuring. Two scans **two minutes apart** (08:28
and 08:30, price 9pts apart) published flips 192pts apart and *opposite* regime
labels, which means opposite strategies.

**This is 3 of 3 on the overnight sub-claim and 3 of 3 on self-contradiction —
the threshold is met and the evidence points one way.** It is now the
best-supported finding in this register. Reading it, not acting on it, per the
rule: a proposal belongs in its own entry with a stated mechanism, and the
obvious candidate (suppress the regime label and the strategy recommendation on
OVERNIGHT scans, keep the levels) needs writing up as one rather than being
slipped in through a retrospective.

**What this does NOT say.** The direction call from overnight scans was 2 right /
1 wrong — it is specifically the *flip*, and therefore the strategy selection,
that overnight gets wrong. Do not generalise it into "overnight scans are
useless".
