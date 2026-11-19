# Review — trading day 2026-11-18 (graded 2026-11-19)

One scan: `1247-london.json`, `is_trading_day: true`, `outcome: null`, 276 bars,
`review_day` reports **0 test artefacts**. Exactly **one commit** (`1d7a0ee`) —
written once, never edited; no `prediction` block was touched. No
`is_trading_day: false` scan entered any statistic below.

Also in scope, at the runner's request: **independent verification of five
claims about today's (11-19) undelivered-outcome scan.** Those are recorded as
scan-level observations, not graded outcomes.

---

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 26992.3 / 27526.5 / 26842.6 / **27109.5** |
| range · net | **683.9** · **+117.2** (UP day) |
| call | **−3 MILDLY BEARISH**, `expected_direction −1` |
| post-scan move | **−26.6** → **CORRECT** |
| day-net basis | **+117.2** → **WRONG** — bases DISAGREE, **P-H deciding instance** |
| H17 noise test | post-scan is **3.89%** of session range — **inside the 5% band** |
| levels published · touched | 19 · 8 → hit rate **0.42** (fleet 0.48) |
| of the 8 touched, settled verdict | 4 held · 1 lost · **3 ungraded** ("too few bars on one side") |
| side of the board that was used | **8 of 8 touches below the scan price**; all 11 rows above never reached |
| budget · extension · error | 409.5 · 125.6 · **−283.9** (0.31×) — largest over-estimate in the 31-day window |
| traversal vs budget | 401.9 · **0.98×** |
| fuel verdict | *OVER-estimated* |
| realised ÷ ADR14 | 683.9 / 967.8 = **0.707×** |
| realised ÷ VXN-implied | 683.9 / 588.8 = **1.161×** |
| `track.py` after this day | 31 days / 31 scans · **14 R / 13 W / 4 no-call = 51.9%** · H1 per-day mean **89.9** |

`track.py` exit 0 (~22 min). This build still emits **no `actionable: YES/NO`
string**; the header line (*"31 of 3 days … threshold met, read the evidence
before proposing"*) was used and is quoted, not silently substituted. **A day
DID age out this run**: `2026-10-05` left the window and is reported under
*"HELD BACK — day not finished"* at 94 bars — a session six weeks past. That is
**D26's known mislabelling** (same shape as 09-28 on 11-12), and it means
14/13/4 → 14/13/4 is *not* "no change": 11-18's CORRECT entered and a CORRECT
left. D26's gap: 31 full bar sets against 56 finished day directories — **25**.

---

## 2. What the levels actually did

**The board was on the right side, and that is the first thing to say.** All 8
touches were below the scan price on a day whose post-scan leg was down; the 11
rows above were never revisited. This is the exact inverse of the 11-09 finding
(*"42% of the board published into a side that never happened"*) and it is
recorded as a counter-instance, not as vindication of the row set.

**It is also the thinnest board in the record by density.** Eight rows sit
inside the **150.0 points** between 26977.7 and 27127.7, and **six of them were
first-touched in the SAME 5-minute bar** (`bar_index 199`, 14:35Z — the first
bar after the NY cash open), a bar spanning at least 94.2 points. The 0.42 hit
rate is therefore mostly one bar: as a measure of whether the levels were
*useful* it is close to meaningless. This is **H6's** normalisation question in
a sharper form than "board span ÷ traversal" — the right denominator may be
*rows consumed per bar*.

**Then the board stops exactly where the day turned.** Below the put wall the
next published row is PWL **26640.2**, a **337.5-point hole**. The session low
**26842.6** is inside it — **135.1 below** the nearest row above, **202.4 above**
the one below — and that low is where the entire post-scan rally began
(26842.6 → ~27244.5 derived from `traversal` 401.9, close 27109.5). The
level-board void watch item has been carried at *"n≥3 condition / 0 demonstrable
harm"* for three weeks. **This is the harm case**: the single pivot of the
post-scan session was in a published void, while eight rows were spent on 150
points that one opening bar erased.

Level by level, against what the brief said:

- **PUT WALL 26977.7** — brief: *"Heaviest floor this week, BUT today the desks
  are pushing moves along — if it breaks, expect it to speed UP, not bounce.
  Don't buy the break."* Reality: it **broke by 135.1 points** and then
  reversed, and buying that break was the best post-scan trade available
  (+401.9 of traversal, close 266.9 above the low). The rider's conditional was
  not merely unhelpful, it was **inverted**.
- **…and the instrument hid the break.** `review_day` grades that same level
  *"stalled at it — held as support for 240min, worst −23.6pts"*, `held: true`,
  `acted_as: support`, on a level price traded **135.1 points through**. The
  settled read measures only from its settle point, so the excursion is
  understated **5.7×** and the verdict is the opposite of the tape. **M6, and
  the largest instance of it I have seen** — previous ones understated a number;
  this one reverses a verdict that `track.py` and `gex_retro.py` both consume.
- **PD mid 26994.3 / Equal lows ×2 + London Low 27003.2** — both graded *held as
  support, worst −8.2 / −17.1*. Same defect, same bar: price was 151.7 and 160.6
  points below them respectively.
- **Asia Low (today) 27013.6** — the one level graded `lost` (−27.5). Correct,
  and the only row whose verdict matches the tape.
- **Options shelf 0.21bn 27127.7** — §3 named it as the downside's friction:
  *"Expect a stall at 27127.7 (11pts away) — take partials into it rather than
  assuming a clean breakdown."* Price chopped at it for 15 minutes and then
  **sliced it by 284.9 points** (0.294× ADR). **H23 instance: SLICED**, and the
  named brake was 11 points away on a path that then ran 285.
- **§3's upside corridor far end 27677.7** — **433.2 points above the session
  high**, after 11-17's far end landed 369.4 *below* the low. Two consecutive
  sessions in which the far end of the corridor is noise, in opposite
  directions.
- **Equal highs ×2 + Asia High (today) 27528.3** — the day's high was
  **27526.5, 1.8 points below it**. Ungradeable: that high was made *before* the
  12:47Z scan (`range_at_scan` 558.3 already contained it), which is also why
  all eleven upper rows read "never reached". Noted so the near-miss is not
  mistaken for a hit on a later re-read.
- **Three of eight touched rows returned no verdict at all** (27127.7, 27096.4,
  27071.9 — *"too few bars on one side"*). The grader declined on 37.5% of what
  it graded. Honest, and worth tracking as measurement coverage.
- **MAX PAIN 27977.7 / STRUCTURAL CALL WALL 28377.7** — 838.7 and 1238.7 away,
  both tagged `stretch: true` in the JSON and **neither printed the tag**
  (D7/D15, unchanged).

---

## 3. What was wrong, and why

**The direction call was right by 26.6 points and wrong by 117.2, depending on
the basis — and both numbers are noise.** `bias_components` gives
`gamma −3` (below flip by 285.5, short gamma), `vol −4`
(VIX9D/VIX 1.099 backwardated −2, VXN/VIX 1.42 −1, VVIX 121.28 −1), against
`rates +1`, `macro +1`, `structure +2`, `news +1`, `breadth −1`. Total −3 — one
point past `journal.py:68`'s `|score| ≥ 3` gate. So this call existed at all
only because the score cleared its threshold by a single point, and it was then
graded on a **26.6-point** drift inside a 401.9-point post-scan traversal (6.6%
of the distance travelled, 3.89% of session range).

That makes 11-18 simultaneously:

- **H17 instance 4**, and the pattern is now 4-for-4: 09-11 (0.2%), 10-19
  (1.35%), 11-06 (2.66%), 11-18 (3.89%) are **all bearish calls graded CORRECT
  on days that closed UP** (+252.1 / +430.6 / +331.9 / **+117.2**), all four
  with the scan near a pre-scan high. H17's pre-registered threshold was met on
  11-09; this is the fourth consecutive confirmation and the first where the
  margin is within one point of the 5% band.
- **P-H deciding instance 8** (post-scan CORRECT, day-net WRONG) — and like
  10-19 and 11-06, it is *also* an H17 noise case. **3 of 8 deciding instances
  are noise cases**, and the post-scan basis P-H recommends is what manufactures
  the CORRECT in all three. The two still have to ship together.

**Yesterday's open question is now answered, and the answer is better than it
looked.** The 11-18 review logged D22(a)'s first grade-changing part-1 instance
— corrected breadth `−1 → +1`, score `−3 → −1`, call `MILDLY BEARISH → NO CALL`
— and recorded that *"whether the no-call improves or destroys a correct call is
not yet knowable."* It is knowable now: on the official post-scan basis the
repair **destroys a CORRECT**. But that CORRECT is an H17 noise case at 3.89%,
which H17's own proposal converts to `no call (inside noise)` anyway, and on the
day-net basis the repair **destroys a WRONG**. **The two pending proposals agree
on 11-18**, so the apparent cost of shipping D22(a) part 1 on this day is zero.
The standing sentence *"part 1 changes zero direction grades"* stays restated;
the new sentence is that its one grade change costs nothing real.

**The range call was wrong in both directions at once, and the cause is
traceable.** §2 printed `COHERENT_SHORT` → *"Expect range expansion and trends
that persist. Today's ADR can be exceeded — don't cap the target too early."*
Realised: **0.707× ADR**, range extension **125.6 against a 409.5 budget
(0.31×, −283.9 — the largest over-estimate in the 31-day window)**, and the
post-scan move was a 26.6-point drift. Nothing expanded and nothing persisted.
11-18 is one of the 8 days the 11-18 review identified where `COHERENT_SHORT`'s
*"deepens with tenor"* is **false by the module's own numbers** (today −0.089 ·
week −0.02 · 45-day −2.265 — the week leg is *shallower* than the front), and
it is also the 1-of-54 day where *"every expiry is short gamma"* is false
(`week −0.02` → `_sign = 0`). **This is the first graded outcome attached to
that prose instance**: the sentence reasoned off a property the book did not
have, and the day it described did not happen. P-I's second limb and H22 both
gain a graded data point.

**The one thing the budget got right was the number nobody trades on.**
`traversal / budget` = **0.98** — price roamed 401.9 inside the range against a
409.5 budget, essentially exact — while `extension / budget` = 0.31. The budget
is behaving like a traversal forecast and being published as an extension
forecast. That observation is three sessions old at most in this sharp a form; I
am not proposing a reinterpretation on it (see §4).

**The news leg was pointed the wrong way by the right headlines.** `news +1`
(*MILDLY BULLISH*, 3 bull / 1 bear) was carried by two `earnings_beat`
classifications — *"Nasdaq futures rise as Nvidia gains on earnings beat"* and
*"What Wall Street analysts are now saying after Nvidia's beat-and-raise
quarter"*. NVDA then closed **−2.90%** and NDX managed **+0.42%**: the beat was
public, priced, and faded inside the session the leg was scoring into. 59 of 63
headlines went unscored (**H19 coverage 6.3%**). n=1 for this specific shape
(an `earnings_beat` scored bullish into the fade session); logged, nothing
proposed.

---

## 4. Change proposals — only material ones

### ONE CORRECTION, and it is the substantive finding: D32's diagnosis is wrong, and the feed is alive

D32 was opened yesterday on the finding that `macro_probe.py:158`
(`api.nasdaq.com/api/calendar/earnings`) returns **HTTP 403**, and concluded
*"a host-wide block, not a parameter error"*, with no replacement source
proposed. **The host is not blocked.** Probed live 2026-11-19 from this machine,
same URLs, same minute:

| client | result |
|---|---|
| `curl` + browser UA | **200**, 39 rows |
| `curl` + the exact `macro_probe.UA` string | **200** |
| `curl --http1.1` | **200** |
| `macro_probe._json` (the scan's own fetch) | **403** |
| bare `urllib.request` + browser UA, + `Accept`, + `Accept-Encoding`, + `Accept-Language` | **403** on every variant |

So it is the **HTTP client**, not the host and not the User-Agent — every
`urllib` variant tried is refused and every `curl` variant is served. The other
two paths D32 cited as evidence of a host-wide block,
`api/calendar/economicevents` and `api/quote/NVDA/info`, **also return 200**.
I could not finish isolating the exact discriminator (reading the 403's own
response headers was blocked by this environment's permission layer), so the
mechanism is **narrowed, not closed**.

**And the data that was lost is recoverable and checkable.** Querying the live
feed for 11-16 → 11-20 returns `NVDA` on **2026-11-17**, `time-not-supplied`,
`epsForecast $2.47`. D32's claim that `bias_engine.py:262`'s *"INDEX-DEFINING
event; day before pins, day after expands"* **should** have printed on 11-12,
11-13, 11-16 and 11-17 is confirmed **from the source itself**, not inferred.

**PROPOSED (amendment to D32, no new ID):** keep D32's two asks — record the
fetch error, print one degraded-source line — and **add a third**: route this
host's fetch through a client that it serves, since the feed is working and the
11-session outage is a client defect rather than a dead source. **Still NOT
proposed:** a replacement data source, any scoring change, or any use of
`events` as a direction term. **Expected effect:** the `events` row returns for
real heavyweight dates; no score, level or gate changes, because the row scores
0 by construction. **Evidence basis:** the live probe is one point in time, but
the *claim being corrected* — "host-wide block" — is falsified by a single
counter-example, which is what this is.

### Everything else: nothing proposed. Observations, with counts.

- **The level-board void takes its first demonstrable harm case** (session low
  26842.6 inside a 337.5-point published hole, 135.1 from the nearest row, and
  it was the day's pivot) — condition n≥6, **harm n=1**. The watch item has been
  carried at *0 harm* for three weeks; that sentence must now be restated. I am
  **not** proposing a spacing rule on one harm case, and the 8-rows-in-150-points
  clustering on the other side of the same board is the more promising lever.
  **Watching:** whether the next two voids also contain a turning point, and
  whether rows-consumed-per-bar separates useful boards from decorative ones
  (H6).
- **M6 gains its strongest instance** — a `held: true / acted_as: support`
  verdict on a level price traded 135.1 points through, excursion understated
  5.7×, on the board's single most important row. Two further instances on the
  same bar (26994.3 by 151.7, 27003.2 by 160.6). M6 is already open with a
  settle-window fix; **this adds magnitude and a verdict-level failure, not a new
  ask.**
- **H1 is not a systematic under-estimate and must stop being described as one.**
  31 days: mean **+89.9**, **median +23.4**, 19 under / 12 over, and the mean
  drops to **+50.9** without 11-05's +1261.2. The **last six sessions mean
  −76.6** (4 of 6 over-estimating), 11-18 the largest over-estimate in the
  window. **No rescale factor is proposable**: the sign of the bias is not
  stable, and a factor fitted to this series would be fitted to one outlier.
- **The budget-as-traversal observation** (`traversal/budget` 0.98 against
  `extension/budget` 0.31). `review_day`'s own docstring argues *for* grading on
  extension and the argument is sound. I am logging the pair, not proposing a
  reinterpretation: 11-18 is n=1 in this clean a form and the 08-24 precedent in
  the register points the other way.
- **H17 instance 4**, **P-H deciding instance 8** (3 of 8 now also H17 cases) —
  both entries already carry their proposals; these are confirmations.
- **D31 supporting**: realised ÷ VXN-implied **1.161×** (683.9 / 588.8), above
  1.0 again, but the **lowest ratio in the recent run** and well below both the
  1.54 median and the analytic √(8/π) = 1.596. Direction consistent, magnitude
  a counterweight to the conversion constant D31 proposed on 11-17.
- **H23**: named brake 27127.7 at −11, **SLICED by 284.9 (0.294× ADR)**. The
  census is hand-maintained; I quote the increment only and do not restate the
  total.
- **H22 / P-I second limb**: first graded outcome for the 11-18
  `COHERENT_SHORT` prose instance — *"ADR can be exceeded"* against realised
  **0.707× ADR**.
- **H19** coverage **6.3%** (4 of 63), `news +1` into a session where its two
  scored bull headlines' subject closed −2.90%.
- **D25**: §7 did not render again. Derived from the files: **21 consecutive
  trading-day briefs carry no `## 7`**, last render **2026-10-21**. The
  register's hand-maintained counter (*"9th consecutive"* at 11-09) does **not
  reconcile** with that. **Flagged for re-derivation; I am not overwriting it
  and I am not quoting it as verified.**
- **D7/D15**: 2 structural `stretch: true` rows, 0 printed tags. Unchanged.
- **D23/D6**: 11-18 offset **−22.3**, 11-19 offset **−11.8**, both on the
  `nq_implied` basis, both inside ±40. **The D6 breach census stays at seven**;
  the 11-17 finding that the standing replacement check is an algebraic identity
  on this basis is unaffected.
- **H2**: no instance — 11-18's fuel was `MODERATE`, not low/exhausted, so it
  does not enter the census. 11-19 (`LOW_FUEL`) will.
- **No new data point is warranted.** The one candidate this day raises — an
  NVDA-specific "was the event already public" flag — is **not needed**: the
  earnings date is already in the feed D32 covers, free and reliable, and
  recovering that feed answers it without a new source.

### ID allocation

**Highest allocated as of 2026-11-19: H27 · D32 · P5 and P-I · M7.** Next free:
**H28 · D33 · P-J** (and **M8**), confirmed by `grep -c` on 2026-11-19 — all
four return **0** before this entry. **This review allocates NOTHING.** D32's
amendment is written into D32; every other finding routes to an existing entry.

---

## 5. The runner's five claims about the 11-19 scan — verified independently

All five checked against an independent Yahoo fetch (12:50–13:10Z), the
immutable 11-18 journal entry, and source. **Four reproduce; one is refuted; two
carry corrections to the runner's reading.**

**(1) D22(a) — second consecutive breadth sign flip: REPRODUCES, with a
correction.** Printed vs true prior session (11-17 close → 11-18 close):

| | printed | true | verdict |
|---|---|---|---|
| `^NDX` | +0.42% | **+0.424%** | MATCH (cash — correct window) |
| `ES=F` | +1.16% | **−0.251%** | **SIGN FLIP, 1.411pp** |
| `DX-Y.NYB` | −0.11% | **+0.358%** | wrong by **0.468pp**; `rates +0` either way |

Mechanism re-confirmed from source and from the live fetch: `macro_probe.py:58`
takes `meta.regularMarketPrice` as `last` against `closes[-2]` as `prev`, so a
still-trading instrument reports a **live partial-day** move while a closed cash
index reports the **prior session**. Independent arithmetic: `ES=F`
`regularMarketPrice` 7427.0 ÷ `closes[-2]` 7340.5 = **+1.178%**; `DX-Y.NYB`
103.747 ÷ 103.86 = **−0.109%**. Both match the printed values. `^TNX` and
`^FVX` were also checked and are **clean** (−0.725% / −0.327%, cash windows,
`rates +1` sound) — the blast radius today is confined to the two 24-hour
instruments, as the register says.

Corrected, the gap is **NDX +0.424% against ES −0.251% = +0.675pp**, past
`bias_engine.py:192`'s ±0.2 gate on the **leading** side, so the row is **+1
*"tech leading, genuine risk appetite"*** and the printed **−1 *"tech lagging,
rotation out of tech"*** is again exactly inverted. **Two sessions in a row with
the narrative backwards.**

**CORRECTION to the runner, against the runner's own case: this IS
grade-changing.** The runner reported it as not grade-changing because both +5
and +7 clear `|score| ≥ 3`. That is right about `expected_direction` and about
the strategy pick (gamma-side driven, unchanged). But `bias_engine.py:268` bands
the **label** at `≥ 6 → BULLISH`, so corrected, `brief.py:836` prints
**"The call: BULLISH (score +7)"** instead of **"MILDLY BULLISH (score +5)"**.
The headline sentence of the brief changes band. D22(a) part 1's grade-affecting
count goes to **2** (11-18 direction, 11-19 label).

**CORRECTION on the hair-trigger, also against the runner's framing:** the DXY
row is a **±2**, not a ±1 (`bias_engine.py:150`). True **+0.358%** sits
**0.042pp** from the −0.4 gate, so the live-vs-true straddle is worth **2
points** here, not 1. It still changes no grade today (7 → 5, or 5 → 3, both
inside their bands), but **bias-gate fragility** should carry the correct
magnitude.

**(2) The NVDA mega-cap window — REFUTED. It does not accrue, and the condition
stays at n=1.** The runner asked whether the 11-19 mega-cap leg (`NVDA −2.90%`,
drawn from the 11-18 cash session) is a second instance of "the intended window
quotes a pre-event session on a day the event is public", and correctly declined
to claim it without establishing the release timing. **Established, three
independent ways, and the answer is no:**

- **The feed itself** (recovered per §4) lists `NVDA` earnings on
  **2026-11-17**, `epsForecast $2.47`.
- **The immutable 11-18 journal entry** already carried
  *"Nasdaq futures rise as Nvidia gains on earnings beat and solid outlook"* and
  *"What Wall Street analysts are now saying after Nvidia's beat-and-raise
  quarter"* in its news block at **11-18 12:47Z** — so the report was public
  before the 11-18 pre-market, i.e. released after the **11-17** cash close.
- **Independent intraday data**: NVDA traded **159.1–161.0 in the 11-18
  pre-market** (11:30–14:00Z) against a 155.46 close on 11-17 (**+2.4% to
  +3.5%**), opened the cash session ~159.2 and closed **150.96 (−2.90%)**.

So the 11-18 cash session that today's row quotes is the **post-event reaction
session** — the market's actual verdict on the beat, and the most informative
number the row could carry. Today's row is **correctly windowed**. The condition
logged at n=1 on 11-18 (where the row quoted the **pre-event** 11-17 session)
**stays at n=1.** Nothing accrues, nothing proposed. The runner was right to
withhold the claim.

**(3) The regime reading is genuine: REPRODUCES.** From `inputs.gamma`:
0-2dte **+2.337**, week **+2.866**, 45-day **+2.573** $bn/1% — all three outside
the `bias_engine` ±0.2 points deadband *and* outside `gex_levels.DEADBAND_BN =
0.05`. `COHERENT_LONG` is a real classification here, and the contrast with
11-18's **−0.02** (inside all three of the document's thresholds, which is the
prose/score mismatch instance) is sound. The **9-of-70** census of
`|week| ≤ 0.2` becomes **9 of 71** — today is not an instance.

**(4) The put-wall rider switch is a real guard, not a dead ternary:
CONFIRMED.** `brief.py:309–322` is a three-branch conditional on
`long_gamma = above_flip and (net_wk or 0) > 0` and `conflicted = above_flip and
not long_gamma` (`:240–241`), both bound to live inputs. Today it correctly
selected the long-gamma form (*"expect a bounce and a good long-sweep here"*).
The runner's caution about having called a dead ternary a working guard last
week was warranted and is answered: this one is live.

**One thing found while checking it, n=1, NOTHING PROPOSED.** `brief.py` defines
`long_gamma` **three times with two different meanings**: `:240`
(`above_flip AND net_wk > 0`) drives the put-wall rider, while `:689–690` (the
gamma-concentration table) and `:862` (§2 Regime) use `px > flip` alone. On a
day with price above the flip and week net GEX negative, §2 would print the
long-gamma regime read and *"this is your fade day"* while the put-wall row
printed *"the book is CONFLICTED — do not treat this as a reliable floor"*.
**Censused: that condition has occurred on 1 of 71 trading-day scans**
(2026-09-10, `net −0.058` — itself inside the ±0.2 deadband). n=1 → logged only.
`bias_engine`'s D8 comment already names this disagreement class for the
strategy selector; the brief's local redefinitions are not covered by it.

**(5) The internal tension and the stale-`macro` partition: REPRODUCES.**
Component sums for 11-19: `gamma +4 · vol −4 · rates +1 · macro +4 ·
breadth −1 · fuel 0 · structure +1 · news 0 = +5`. Verified: **every non-zero
`macro` row is a FRED series stamped 2026-11-17**, two business days stale, and
the **+3 DFII10 row is the single largest contributor to today's score**.
Re-partitioned per the 11-12 correction, **today's only current-data blocks are
`gamma +4` and `vol −4` — they cancel exactly, and the published +5 is produced
entirely by data at least one session old.**

Censused so it is a count and not an anecdote: across 71 trading-day scans,
`gamma + vol` sums to **exactly zero while the published score is a directional
call on 4 of 71** (09-11, 09-14, 09-22, **11-19**) and points the **opposite way
to the published score on 7 of 71** — **11 of 71 (15%)** where the current-data
blocks do not carry the call. The `macro` leg's ±3 real-yield row fires at full
magnitude on **52 of 71 scans (73%)** off a series that is never same-day.
**Condition n=4 on the exact shape the runner flags; harm NOT established** — it
needs those four days' graded outcomes against a block that scores zero, which
is a no-call, not a direction. **NOTHING PROPOSED.** Watching: the next two
zero-current-data days, and whether H18/P1's existing DFII10/DGS10 rendering fix
should carry a staleness gate as well as a collapse.

---

## 6. Journal hygiene

11-18: one scan, `is_trading_day: true`, `outcome: null`, 276 bars, **0 test
artefacts**, **one commit** (`1d7a0ee`) — no backfill, no fabricated entry, no
`prediction` block modified. 11-19: one scan, one commit (**`f213b72`, verified
on `origin/main` at 2026-11-19 12:47:02Z, 4 files**, carrying both 11-19 journal
files), **excluded from every statistic as unfinished** (`track.py` holds it at
184 bars). 6 historical `test_artefact` entries excluded as always. No
`is_trading_day: false` scan entered any statistic above.

Checked and clean: the four 2026-08-24 scans inside six minutes (08:28 / 08:30 /
08:32 / 08:33) are **not** flagged `test_artefact` but **are** collapsed by
`track.py`'s 15-minute `_dedupe`, so they do not inflate anything. Noted because
the 08-27 equivalents *were* flagged and these were not; the dedupe makes the
inconsistency harmless today.

11-19's scan also carries **no `EARNINGS` row** (D32, still unfixed as of the
scan) — see §4, where the feed is shown to be alive.
