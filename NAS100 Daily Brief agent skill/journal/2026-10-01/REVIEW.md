# REVIEW — trading day 2026-10-01 (graded 2026-10-02)

1 gradeable PRE_NY scan (12:47:53Z), `is_trading_day: true`, 0 test artefacts,
276 M5 bars (09-30 22:00Z → 10-01 20:55Z). No fabricated or backfilled entries;
no `prediction` block touched.

**2026-09-24 remains quarantined** per *D23 CORRECTED*: its options fields and
its direction call stay out of the direction tally, the hit-rate series, P-E,
P-E(b), H6 and M6. Its fuel error (+13.6) is kept on the D1 precedent and is
inside `track.py`'s H1 series, so H1's printed figures need no hand correction.
`track.py` has no quarantine and still prints 09-24 CORRECT, so the direction
counts below are carried by hand off its per-scan table, as the 09-28, 09-29 and
09-30 reviews did. **09-25's row is cited from the 09-28 review's register
entry**, not re-derived; no review file was back-dated for 09-24 or 09-25. The
09-23 pre-registered D21 test stays void.

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 30462.5 / **30903.4** / **30285.5** / 30526.8 |
| range | **617.9 = 1.33x** ADR14 463.3 · net **+64.3** · close 39.1% up the range |
| scan | 12:47:53Z, bar 178 of 276, price 30603.5 |
| pre-scan H / L | **30903.4 (06:10Z)** / 30439.2 (09-30 22:00Z) — range 464.2 |
| post-scan H / L | 30637.3 (17:45Z) / **30285.5 (15:10Z)** — extension 153.7, **all downside** |
| bias | **+2 NEUTRAL / TWO-WAY → no direction call** |
| post-scan move | **−74.7 (direction −1)** on traversal 351.8 |
| fuel | budget **0.0** vs extension **153.7** → err **+153.7, UNDER** |
| levels | 3 published, 2 touched, 2 distinct events → **0.67 / 0.67** |

**Direction record, 09-24 excluded.** PRE_NY **9 right / 5 wrong / 4 no-call over
18 days**. All sessions **14 / 9 / 8**. (`track.py` raw: 15 / 9 / 8.)

**H1, n=23 days.** Mean **+24.7**; **−0.08 without 09-21**. MAE **87.9** against a
mean budget of **103.5** — the typical error is **85% of the typical budget**, up
from 82% (09-29) and 79% (09-30). Fifth consecutive large error: −124.4, +113.9,
−112.2, −75.2, **+153.7**.

**Hit-rate series (published / distinct):** 09-18 .78/.78 · 09-21 .43/.29 ·
09-22 .56/.31 · 09-23 .57/.33 · 09-25 .50/.42 · 09-28 .57/.57 · 09-29 .67/.47 ·
09-30 .47/.24 · **10-01 .67/.67**.

## 2. What the levels actually did

Only **3** levels were published — the smallest board in the record — because the
range budget was 0.0. See §3.

**PUT WALL 30336.0** _(stretch, −268)_ — *"expect a bounce and a good long-sweep
here."* **This was the call of the day and the grader marks it a failure.** First
touch 14:05Z; price swept **50.5pts through** to the session low 30285.5 at
15:10Z, reclaimed, settled above from 15:50Z and closed **+190.8 above** after a
**+241.3** reversal. A sweep-then-reclaim-then-rally is precisely what the note
asked for. `review_day` renders it *"broke DOWN through it — lost by 25.3pts"*,
`acted_as: "lost"`, `held: false` — while its own `first_touch_reaction` on the
same row says *"broke UP through it"*. Two separate defects, both already logged
(M6).

**GAMMA FLIP + MAX PAIN 30307.8** _(stretch, −296)_ — *"we're ABOVE it: they're
damping, so fades work. Lose this and hold below and that reverses."* Held as
**support**, worst excursion **−22.3**, 490min, closed **+219.0** above. Price
lost it by 22.3 and did not hold below, exactly as written. The `gamma +2` row
was the single most useful line in the document, second consecutive session
(09-30: worst −4.4).

**CALL WALL 30736.0** _(stretch, +132)_ — *"Heaviest ceiling this week… rallies
stall. Take profit into it… the strongest ceiling on the board."* Graded **"never
reached."** It is not: **29 bars printed highs above it and 27 bars CLOSED above
it, 04:50Z → 07:10Z, reaching 30903.4 = 167.4pts through**, a 2h20 hold entirely
inside the graded session and six hours before the brief was written. The brief
published the session's already-broken ceiling as an intact one, under a banner
reading *"everything below is fresh."* Forward-only it was never threatened —
post-scan high 30637.3 sat 98.7 below it.

**Off-board, and this is where the information was.** The footnote *"Beyond
today's range (context only, don't mark)"* listed **30903 Asia High (today) —
which is the session high to 0.4pt** — and two levels price traded clean through
after the scan: **30512 London Low (today)**, 91.5 from the scan, first touched
13:30Z and penetrated by **226.5**; and **30487 Asia High (prev-day)**, 116.5
away, penetrated by **201.5**. Both were told not to mark.

**Section 3's named brakes.** *"DOWNSIDE path: has friction. Expect a stall at
30586.0 (18pts away)"* — touched on the scan bar itself and **sliced by 300.5pts
(0.65x ADR)**. *"UPSIDE path… Expect a stall at 30636.0 (32pts away)"* — reached
once, 17:45Z, high 30637.3: **capped at +1.3pts**, which is the post-scan high.
Unlike 09-30, both named strikes **do** appear on the secondary-concentrations
table, so yesterday's *"the trader cannot mark it"* complaint is day-dependent,
not structural (H23, n=2 sessions — not actionable).

## 3. What was wrong, and why

**The only thing that stopped a wrong call was the threshold, and yesterday's
proposed fix would have removed it.** Score **+2**; `bias_engine.py` labels
`MILDLY BULLISH if total >= 3`. The 09-30 review PROPOSED, as shipping, (a) an
age-gate zeroing FRED rows more than one business day old and (b) suppressing
`DGS10` whenever a live `US10y` read exists. Today `DGS10` is **−1** and is both
stale (observation 2026-09-29, two business days back) and duplicated (live
`US10y` row: *"5.283 (−0.19%) — yields flat"*, 0 points). **Either half of
yesterday's proposal zeroes it → +3 → MILDLY BULLISH → a long call into a
−74.7 post-scan move. The fix manufactures a WRONG call on the very next
session.** One day after the register finally found H18's damage instance, the
sign reverses.

Two further points on the same block, both code-certain:

- **DFII10's text is wrong for the second consecutive day.** It renders *"this is
  last week's reading, not today's"* unconditionally. The observation date is
  **2026-09-29 — Tuesday of the current week** (Mon 09-28 / Tue 09-29 / Wed 09-30
  / Thu 10-01). The row scored 0, so no damage; the string is still false.
- **The age-gate may not be applicable to the largest surviving macro row.**
  `HY OAS` (**−2**, the biggest single contributor to macro −3) renders **no
  observation date at all** — only *"+40bp over 5 days"*. Whether it can be
  age-gated is unverified and must be checked before anything ships.

**DGS10's duplication now appears in a third sign configuration** — 09-29 stale
and live agreeing (+2 between them), 09-30 opposite signs cancelling, 10-01 stale
**−1** against live **0**, so the stale row is the whole net. Code-certain in all
three.

**The fuel block's specific claim was wrong; its advice was right.** Budget 0.0,
`EXHAUSTED`, text: *"the day's range is set… expect real movement still, just
**within** the extremes rather than beyond them. Continuation into new highs/lows
is the low-probability trade."* Price made a **new session low**, 153.7 beyond the
pre-scan low. The *"Stop management"* paragraph — fade the extremes back into the
range — then caught the +241.3 reversal off that low.

**D7, and this is the clean instance the register was missing.** `keep()` filters
session-extreme and PD/PW levels by `abs(dist) <= budget * 1.75`. With
`budget = 0.0` the cap is **0.0**, so the predicate passes only at `dist == 0`
and **every non-exempt level is rejected regardless of distance**. That is what
collapsed the board to 3 gamma rows and demoted 30512 and 30487 — 91.5 and 116.5
points away — to *"don't mark"* on a day that travelled 318.0 points down from
the scan. Forward-only breach of the ±0.0 cap: **+33.8 above, +318.0 below**.
09-17 is the only other zero-budget PRE_NY day and it breached +470.1.

**P-B(b)'s inflation vanished, and the mechanism is now proven.** 3 published / 2
touched / **2 distinct → 1.00x**, the first session in nine with no inflation at
all, immediately after 09-30's worst-ever 1.96x. The difference is entirely that
D7's zero budget stripped the dense structural cluster and left three levels
400 and 28 points apart. The inflation is caused by **publishing clustered
structural levels**, not by `TOUCH_TOL`. The corollary is a warning about this
scoreboard: **0.67 is above the 0.53 series mean and was bought by publishing
almost nothing**, while the board missed the session high by 167pts. Hit rate
alone is not a quality measure.

**Everything else that did not fire.** 18 of 24 scored rows were 0; the +2 came
from 6 rows. No `events` row again (component is `add("events", 0, …)` over
heavyweight earnings only, and there were none) despite two Medium items 1.2h out
and three High items at +23.7h — and the day's low landed at 15:10Z, 1h10 after
the 14:00Z ISM/Waller pair, so no `event_gate` and no H20 instance either. D21:
`gamma +0` *"price mid-band, 67% up the range"* — did not fire. H6/P3: **no
`structural` level published**, because D7 removed them all — so H6 cannot
accumulate evidence on low-budget days. D18: the single scored headline matched
`cpi_cool` and contains no `risk_on` token; first-match-wins did not fire. P-F:
price inside the prior-day range at the scan (51.7 below PDH, 341.5 above PDL) —
inside-range control, error +153.7, control now **19 days**.

**Max pain was hit, and the hit is unusable.** 30306.0 sat **1.8pts** from the
gamma flip, so the 490-minute hold cannot be attributed to max pain rather than
the flip. It was a Thursday, consistent with the brief's own *"weak on a Monday,
strong by Thursday/Friday"*, but as evidence it is **confounded** and should not
be counted as max pain's first clean in-reach success.

**H22 is not discriminating.** Week net GEX **5.58 $bn/1%** → *"pinning likely"*;
09-30 printed the same words at **0.036**. A 155x difference in the input, the
same output label, and the larger reading produced the **wider** realised range
(1.33x vs 0.84x ADR). Graded forward-only the pin claim is defensible — price
reverted 241 of 318 and the overhead shelf capped at +1.3; graded on the session
it is not. n=2, logged, no claim.

**D23.** Offset **+36.0** (reference 30567.5 = cash close rolled forward by the
NQ move +159.0, against CFD 30603.5) — ordinary basis, 4th consecutive clean
offset. **This is again an `nq_implied` roll-path day, so the proposed
cross-check is circular and reports nothing. It is NOT validated** and still
needs re-specifying against an independently measured NQ-minus-premium level
before it can replace D6.

## 4. Change proposals

Three proposals and one retraction. Everything else is observation.

**(1) RETRACT the accuracy case for the 09-30 H18 proposal.** The DGS10/FRED
staleness fix removed a WRONG on 09-30 and **creates** one on 10-01 (+2 → +3 →
long into −74.7). Across its only two damage instances the net accuracy effect is
**zero**. The duplication and the stale rows are real and code-certain, so fix
them **on correctness grounds**, with the accuracy claim withdrawn and the
coupling to D22(a) unchanged. Before shipping, resolve whether `HY OAS` carries
an observation date at all — if it does not, the age-gate silently exempts the
largest macro row. Expected effect: honest; 10-01 stays a no-call.

**(2) D7's second half — floor the budget filter.** Already proposed; today
supplies the degenerate case and the mechanism. Either exempt session-extreme and
PD/PW levels from the budget filter as the gamma levels already are, or floor the
cap at a fraction of ADR so `budget = 0.0` cannot reject the whole board.
Evidence: 17 sessions in the register's table, plus 10-01 (cap 0.0, two levels
inside 117pts demoted and then penetrated by 226.5 and 201.5) and 09-17 (cap 0.0,
breach +470.1). Expected effect on 10-01: 30512 and 30487 marked, published count
3 → 5+, both touched, and the trader is not told to ignore the two levels price
actually traded through.

**(3) D23 — one conversion per grid.** Third consecutive session on which the
level board and section 7 publish different CFD offsets: **+36.0 vs +194.0,
158.0 apart** (09-29: 150.1; 09-30: 58.0). All three are damage-free only because
section 7 is research-only and had no volume, and all three sit behind the
reassuring label *"matched to feed time"*. Derive both grids from one conversion,
or make section 7 reuse the board's offset and print the feed-time delta
separately. Expected effect: no change to any call today; removes a 158pt latent
error that becomes live the first time H12/H13 promote section 7.

**(4) Dead weight — the audit's counts are now decisive.** Measured across the
first scan of every `is_trading_day: true` entry (24 scans, 23 completed days):
`NFCI` **0 / 24**, `yield curve 10y–2y` **0 / 24**. `WALCL / RRP` is **5 / 24**
and has not scored since **2026-08-28** — 0 of the last 19. Three rows of prose
in every brief carrying no information. Drop or replace them. Expected effect:
no score changes at all, a shorter macro block, and the dead-weight audit's stale
*"0 / 16"* figure refreshed.

**Observing only, nothing proposed.** H23 (named path brake) is at **n=2
sessions** against its own 3-session threshold — today gave a 300.5pt slice
downside and a **+1.3pt** cap upside, and both strikes were on a table. P-E has
**no forward-only instance** (the call wall was untouched post-scan); the pre-scan
slice of +167.4 would be the 11th instance and lands inside the existing 103–573
slice mode, so the empty 12–103 band survives either way — census unchanged at
4 capped / 6 sliced. P-E(b): the shelf family takes a 9th instance at **+1.3**
(8 of 9 inside 22pts) and today again contradicts the 09-29 session-extreme
reading, but **which** shelf caps is still unpredicted — 09-30's nearest shelf
(+26) failed while the far one (+150) capped, 10-01's nearest (+32) capped. The
09-29 flip stays **withdrawn** and the census's undeclared selection on distance
is now demonstrably non-monotonic. M6 reaches **16 sessions** with another
understatement (put wall breach reported **25.3**, actual **50.5** — 2.0x) and
another English inversion; it needs a decision, not more evidence, and it is not
re-proposed. H1's **multiplier branch should be closed SETTLED-NEGATIVE**: with
n=23 the mean error excluding 09-21 is **−0.08** while MAE is 85% of the mean
budget — an unbiased estimator carrying no per-day information, which a
multiplier cannot help. H19: coverage **1 of 56 relevant = 1.8%**, the lowest
recorded (09-30: 3.8%), the one scored headline was bullish at +0.66 and was then
rounded to **0** by the label threshold, and the uncounted pile held *"Broadcom to
lend Anthropic up to $42 billion to lease its chips"*. Session-context field:
**5th session**, and the strongest instance yet — the headline level on the board
was graded *"never reached"* on a day it had been closed through 27 times.

**Fourth consecutive review carrying the 09-24 exclusion by hand.** The 09-29
entry's proposed `quarantine` field in the journal schema, read by `track.py` and
`review_day.py`, is **reaffirmed** — today adds only another chance for the
correction to be dropped silently.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
