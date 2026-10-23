# REVIEW — 2026-10-22 (Thursday)

Graded from `review_day.py 2026-10-22 --json`, `track.py`, the day's own
`1248-preny.json` / `.md`, and the M5 bar series. Direction graded on the
**post-scan** basis per **P-H**. **09-24 excluded by hand** (18th consecutive
review to carry it — there is still no schema `quarantine` field).
No `prediction` block was touched; no scoring, wall or grading code was edited.

---

## 1. Scoreboard

| | |
|---|---|
| Session | O **29804.2** / H **29817.9** / L **28860.5** / C **28921.0**, 276 bars |
| Range | **957.4** = **1.844x** ADR14 519.3 · net **−883.2** |
| Scan | 12:48:45Z PRE_NY, one scan, 0 test artefacts, `is_trading_day: true` |
| Call | **MILDLY BULLISH +3** at 29361.0, `COHERENT_SHORT`, `EXHAUSTED`, budget **0.0** |
| Direction | post-scan **−441.6 WRONG** · day net **−883.2 WRONG** — **both bases agree** |
| Levels | **6 published / 2 touched = 0.33** |
| Fuel | budget **0.0** vs extension **382.7** → error **+382.7**, the **3rd-largest** under-estimate in the record (behind 09-21 +569.2 and 10-16 +479.3) |
| Traversal | **554.3** = 1.07x ADR |
| Vol reads | VXN-implied range **451.7** vs realised **957.4** — **under by 505.7**. Straddle band **28940 .. 29782**, close **28921.0 OUTSIDE by 19.0** |
| `track.py` | 31 trading days / 34 scans · direction **17/8/9** → **16/8/9** ex-09-24 · levels touched 0.5 · H1 per-day **+58.6** |

**P-H:** post-scan **13/21 (61.9%)** vs day-net **14/21 (66.7%)**. Both bases
wrong, so **10-22 is NOT a 6th deciding instance**; deciding set stays **n=5** and
the convention's cost falls **5.0 → 4.8** points purely on the larger denominator.

---

## 2. What the levels actually did

**Touched (2 of 6), and both were on the put side.**

- **PUT WALL 29115.7 (−245, ●●●●● 0.54bn).** First touch 14:30Z, chopped both
  sides, settled **below** from 16:25Z, graded *lost*. True excursion from first
  touch is **−255.2**; the close finished **194.7 below** it. The row's
  regime-aware note — *"today the desks are pushing moves along — if it breaks,
  expect it to speed UP, not bounce. **Don't buy the break**"* — was **right**,
  and it is the second consecutive session H14's 09-10 fix has paid.
- **STRUCTURAL PUT WALL 28915.7 (−445, ●●●●● 1.01bn / 174k contracts).** Touched
  18:00Z, undercut by **55.2**, close **5.3 above it**. It located the session low
  to 55.2 points and the close to 5.3. **Its own prose told you not to use it** —
  *"the floor for the WEEK/MONTH. Mark it and leave it: where a multi-day
  sell-off is defended, **not an intraday trigger**."* It was precisely an
  intraday floor. This is the **2nd structural-put-wall touch in the record and
  the first that is safely gradeable** (offset 15.7 against a 445pt distance),
  and it supports **P3 / H6**'s existing narrowing: the *"stop publishing it"*
  recommendation belongs to the structural **call** wall only.

**Never reached (4 of 6) — and three of them were out of range by construction.**

- **CALL WALL 30415.7 (+1055, ●○○○○ 0.02bn)** — missed by **1000.9** (post-scan
  high 29414.8). It is **2.03x ADR** away and carries the weakest gamma force
  ever published in a headline wall row, yet its prose reads *"Heaviest ceiling
  this week (15k contracts) — desks must SELL as price rises into it, so rallies
  stall. Take profit into it."* The same table calls a **0.02bn / 15k** row the
  heaviest ceiling and a **0.54bn / 3k** row the heaviest floor: **contract count
  for the superlative, dollar gamma for the stars**. D7-shaped, 3rd instance.
  **P-E: no instance.**
- **GAMMA FLIP 30282.0 (+921)** — missed by 867.2. Its escape clause (*"reclaim
  and hold above and fading becomes valid"*) sat **1.77x ADR** away against a
  **0.0** budget: unreachable by construction, the same complaint logged on 10-20
  at 1.20x ADR, now at its worst. **H4: no instance.**
- **MAX PAIN 29815.7 (+455)** — missed by 400.9 post-scan: **8th
  distance-confounded non-test**, and the row's *"strong by Thursday/Friday"*
  qualifier went untested **on a Thursday**. It also sat **2.2 points below the
  pre-scan high** and 11.5 above the day's opening print — published as a stretch
  objective the session had already traded through 14 hours earlier.
- **STRUCTURAL CALL WALL 29715.7 (+355)** — missed by 300.9. Still **0 gradeable
  touches** across its whole publication history.

**The path read was the best thing on the page.** *"DOWNSIDE path: clear. Every
options shelf from here to 28915.7 (445pts, 0.86x ADR) is negative gamma —
nothing structural to slow a breakdown. If it goes, it has room. **Do not fade
it.**"* Price ran **−500.5** through every one of them. The upside clear-path
call was untested (price never exceeded +53.8 post-scan). **H23: no brake
instance** — both paths were flagged clear, so no named brake existed; census
stays **11 sliced / 3 capped / 3 never-reached, n=17**.

**The secondary table (P5) beat the board again, and one of its rows is void.**
Four of the six *"Other gamma concentrations"* strikes were reachable; all four
were penetrated and the close finished **245–445 below each**, so the
*"**Not a floor**"* half of their prose is **right on every gradeable row**. The
*"accelerate THROUGH rather than stall"* half is weaker: time from first touch to
a close 50pts beyond was 5 / 20 / 20 minutes on three rows but **85 minutes and
15 touches** on 29315.7. **29365.7 is VOID and must not be graded**: published at
**+5** on a **+15.7** board offset (realised basis **−37.7**), so the level's
location uncertainty is 3–11x its published distance from price — the **4th
instance, and the third consecutive session**, of a board row printing inside its
own offset. Census gains **3/3 on "not a floor", 2/3 on "accelerates"**.

**No published level was noise** in the untouched-and-useless sense; the four
misses are all distance, and three of the four were unreachable by construction
rather than by bad luck.

---

## 3. What was wrong, and why

**The score was bullish; every piece of prose on the page was bearish; the prose
was right.** §2 said *"Sweeps tend to keep running rather than fail. Fading is
the wrong trade today."* §3's path read said *"Do not fade it."* §3's stop
management, **four lines later**, said *"Fading the extremes back into the range
is the higher-probability side here, even when the gamma regime favours
continuation."* The headline said **MILDLY BULLISH**. Four instructions, three of
them correct, and the one the reader sees first was wrong.

**Component trace (`inputs.bias_components`):**

| block | pts | verdict |
|---|---|---|
| `gamma` location −3 | *"below flip by 921 — downside accelerates, rallies unstable"* | **RIGHT on both limbs** — downside accelerated, every rally failed |
| `gamma` week GEX −2 | *"−6.602 $bn/1% → expansion likely"* | **RIGHT** — 1.844x ADR (**H22** range label right at **n=14**) |
| `gamma` band +2 | *"bottom 20% of the wall band — poor risk/reward for shorts"* | **WRONG** |
| `rates` +3 | US10y 5.036 (−2.14%) *"yields down, BULLISH tech"* | **WRONG-SIGNED**, and the single largest positive row |
| `breadth` +3 | mega-caps 4/4 up (NVDA +2.54%), NDX +1.13% vs ES −0.92% | **WRONG-SIGNED on both legs** — both measured on a pre-market tape the cash session reversed (**D22**) |
| `macro` +2 | DFII10 **+3** and DGS10 **+1**, both resolving to **2026-10-20**, two business days stale; HY OAS **−2** | the stale pair **outvoted the only right macro row 4-to-2** |
| `structure` −1 | below PD mid | RIGHT |
| `news` −1 | see below | right in sign, wrong in mechanism |

**gamma was outvoted −3 against +6 and gamma had the day.** This is the **5th
instance** of the outvote cell and the **2nd** that produced a directional call:

| day | `gamma` | rest | g − rest | published | realised post-scan |
|---|---|---|---|---|---|
| 10-08 | −5 | +4 | −9 | NEUTRAL | 1.50x ADR |
| 10-09 | +4 | −6 | +10 | NEUTRAL | 0.07x ADR |
| 10-12 | −2 | +4 | −6 | NEUTRAL | 0.41x ADR |
| 10-20 | −5 | +9 | −14 | MILDLY BULLISH +4 | 0.56x, **outvote right** |
| **10-22** | **−3** | **+6** | **−9** | **MILDLY BULLISH +3** | **0.850x, outvote WRONG** |

The pre-registered quantity still **does not order the outcome** — the two
instances at **|9|** produced **1.50x** and **0.850x**, and the largest margin
(14) produced the second-smallest move.

**Three different single-row suppressions each convert the day to a no-call, and
none produces a correct call.** Age-gate the stale FRED pair: **+3 → −1**,
no-call. Drop the `gamma +2` band rider: **+3 → +1**, no-call. Drop `breadth`:
**+3 → 0**, no-call. Headline dedup: no duplicates today, **no change**. The
failure is not a row, it is that the only block measuring where price actually
was got outvoted by three blocks measuring something other than today — two of
them (FRED, pre-market breadth) measuring a different *time*.

**H2 — instance 8, and the falsification extends.** `EXHAUSTED`, below the flip
by 921: an in-cell day under the 10-16 specification. First post-scan sweep of a
pre-scan extreme was the **pre-scan low 29243.2 at 14:20Z**; price **never closed
back inside** for the remaining 98 bars (max subsequent close 29229.4), so the
fade **LOSES** with no target ambiguity. Census **6–2 to the gamma block; 8–0 if
ties go against the fade**. H2's claim stays **FALSIFIED**, and the live proposal
(suppress or subordinate the fuel block's fade instruction below the flip) gains
its 8th supporting instance. **New detail worth carrying:** on 10-22 the two
opposite instructions were **inside the same section, four lines apart**.

**H10 — neither branch fired, and the proximity gap recurs.** `structure 0`,
*"price inside the prior-week range (29073.7–31079.0)"*, with price **287.3
above the PWL**. The day broke the PWL by 213.2 and **closed 152.7 below it**.
The rule scores that identically to a mid-range day — **2nd proximity-gap
instance** (after 10-07). The reclaim term would again have changed nothing.

**News — D18 instances 15 and 16, with the polarity reversed, and that matters.**
Two judgement-list headlines were tagged **`risk_on`** by first-match-wins:
*"Stock Market Today: Dow Falls As Oil Prices Jump; **Meta, Tesla Slide On
Earnings**"* and *"Gold hits over two-month low as oil rally fuels inflation
worries"*. Both are bearish text carrying a bullish tag. **Damage was zero only
because `risk_on` is absent from `HIGH_CONFIDENCE`** — the very asymmetry that
did the damage on 09-18. **Fixing the asymmetry alone, without fixing
first-match-wins, would have made 10-22 worse**: it would have cast a bullish
vote off *"Meta, Tesla Slide On Earnings"* on an −883 day. Meanwhile the one
counted bullish row (*"Meta Stock Climbs After Q3 Results Beat"*, +150pts/180min)
was **wrong-signed**, and the headline that described what actually happened sat
uncounted in the judgement list. **H19 coverage 2 / 128 = 1.6%.**

**Fuel.** `EXHAUSTED` with 110.7% of ADR consumed before the cash open named the
**most expansive session in the recent record** (1.844x ADR). The block printed
*"The day's range is set"* and *"Continuation into new highs/lows is the
low-probability trade"*; the range grew another **382.7** and every continuation
worked. The VXN-implied range of 451.7 came with *"below ADR — options market
prices a quieter day, **use the smaller budget**"* against a realised **957.4**
— **2.12x** the recommended number, and a **third counter-instance** to the
already-killed *"use the VXN-implied range as the budget"* idea.

**M6 — session 30, and travel-scaling fails a THIRD consecutive time.** Both
graded levels understate: PUT WALL reported **49.1** against a true first-touch
excursion of **255.2** (**5.20x**), STRUCTURAL PUT WALL reported **14.8** against
**55.2** (**3.73x**). **One verdict is inverted in English**: the put wall prints
*"**broke UP** through it — lost by 49.1pts"* on a day it closed **194.7 below**
it, because the word is derived from `settled_side` and not from the side the
breach was on. Post-scan travel was **1.07x ADR**, *higher* than session 29's
0.64x, yet the worst ratio **fell from 13.75x to 5.20x** — session 27's
*"magnitude scales with travel"* claim now has **three** consecutive
counter-instances and is not restated. The driver is again **window placement**:
the put wall was first touched 14:30Z and the 12-bar window closed at 15:25Z,
2–5 hours before the 255pt breach.

---

## 4. Change proposals

### Advanced: **P-F** — the budget has no term for price already being outside the prior day's range

**Evidence (4 same-signed treatment sessions, ex-09-24).** Price at scan
**29361.0 was 189.0 below PDL 29550.0**, comfortably past P-F's own >150pt
trigger. Budget 0.0, extension 382.7, **per-day error +382.7**.

| treatment day | price vs PD range | error |
|---|---|---|
| 09-14 | −187.6 below PDL | +79.4 |
| 09-17 | +174.5 above PDH | +40.0 |
| 09-21 | +259.0 above PDH | +569.2 |
| **10-22** | **−189.0 below PDL** | **+382.7** |
| (09-24, quarantined) | −175.5 below PDL | +13.6 |

**4 of 4 positive, mean +267.8, median +231.1**, on both sides of the range.
**The register's own standing caveat is now dead:** the 09-28 rebuild said
*"P-F's discriminating power is carried by one tail point — drop 09-21 and
outside mean is +44.3 against inside +6.3."* Drop 09-21 today and the outside
mean is **+167.4**. Two tail points on opposite sides of the range is a level,
not a tail.

**What to change** (unchanged from the original, prose and strategy selection
only, **no score change and no multiplier**): when `price_at_scan` sits >150pts
outside the prior day's high/low, the `EXHAUSTED`/`LOW_FUEL` block must print the
budget as unreliable in that state and must **not** emit *"the day's range is
set"*, *"continuation into new highs/lows is the low-probability trade"*, or a
fade-first stop-management line.

**Expected effect.** On 10-22 it removes all three of those sentences, which were
each falsified by 382.7pts of new range, and it removes the fade instruction that
H2's census has now lost on **8 of 8** in-cell sessions. It does **not** change
the direction call, and it must never be shipped as a multiplier — fitted to
+40 / +79 / +383 / +569 it would fit the tail, not the level. That is the H1
lesson and it still applies.

### Advanced: **D7's second half** — the zero-budget board, with a new sub-mechanism

**5th zero-budget PRE_NY day** (09-17, 09-24, 10-01, 10-19, **10-22**).
`keep()` (`brief.py:431`) filters session-extreme and PD/PW levels by
`abs(dist) <= budget * 1.75`; at budget **0.0** the cap is **0.0** and every
non-exempt level is rejected regardless of distance. The board collapsed to
**6 rows, all options-derived** — no PDH, no PDL, no session extreme, nothing the
Strategy-1 sweep triggers are built on.

**The new half, code-certain and not previously recorded.** `rows.sort(key=lambda
r: -r["level"])` (`brief.py:373`) leaves `far` in **descending price** order, and
`far_line()` (`brief.py:146–159`) protects only `CALL WALL / PUT WALL / GAMMA
FLIP / MAX PAIN` before taking `rest[:6]`. With no wall in `far`, the footnote
keeps the **six highest-priced** demoted rows — and on a day price sits at the
bottom of the level set, that is a **distance-blind** cut. 10-22's footnote reads
31079 / 29936 / 29840 / 29832 / 29743 / 29682, i.e. levels **+321 to +1718** away,
while **PDL 29550.0 at +189 — named by the brief's own `structure −1` row —
appears nowhere on the board and nowhere in the footnote.** That is D7's original
complaint word for word (*"dropped from the board and from the footnote, the
level ceased to exist in the output"*), surviving for non-wall levels after the
09-10 fix.

**What to change** (unchanged mechanism, now with the second limb named): exempt
session-extreme and PD/PW levels from the budget filter as the gamma levels
already are, **or** floor the cap at a fraction of ADR so a zero budget cannot
reject the whole board; **and** rank `far_line`'s truncation by `abs(dist)`
rather than by the inherited price sort.

**Expected effect.** On 10-22 it restores PDL 29550.0 and the session lows to the
document. The pre-scan low **29243.2** — 117.8 below the scan price, swept at
14:20Z, and the sweep that defined the whole afternoon — was invisible in a
document whose own strategy block is *"sweeps run rather than fail."*

### Threshold reached, and deliberately NOT proposed

**The `gamma +2` bottom-of-band rider, 5th firing — it is at its widest and worst
and I am still not proposing the fix.** 10-22: price **18.9% up a 1300pt band**
(29115.7–30415.7), **245.3 above the put wall**, below the flip by 921. Outcome
**WRONG** (post-scan −441.6, day net −883.2). Census **2 right / 3 wrong**, and
the score-versus-prose contradiction is now **5 of 5**: *"poor risk/reward for
shorts"* printed four rows above *"if it breaks, expect it to speed UP, not
bounce. Don't buy the break"* — and on 10-22 the wall broke and price sped up by
**255.2**. The **D21 width defect reaches its extreme here**: a 1300pt band is
the widest on record (prior max 800), so *"bottom 20%"* is a **260pt trigger
window = 0.50x ADR14**, against **20pts = 0.04x ADR** on 09-18 — the **same ±2
for a 12.5x spread in trigger distance**, and the prior four firings fired at
0.4–42.9pts from the put wall against today's 245.3.

**Why nothing is proposed.** The only evidence that a normalised version performs
better is the absolute-distance re-cut, which the register itself records as
**found after looking at the outcomes** — the procedure the standing rule forbids
acting on. And the ledger already shows the row has **never flipped a direction
call's sign**, so demoting or rescaling it cannot be argued as an accuracy fix.
Logged as the strongest instance of the width complaint; **no proposal**.

### New ID allocated: **D27** — gexbot auth failure as a data-source failure mode

**Warranted at n=2, and opened.** The 10-21 review withheld a number *"deliberately
at n=1"*; the 401 recurred on the 10-23 scan, so it is an auth/endpoint condition
rather than a transient and the stated reason for withholding no longer holds.
**D17** (CBOE 429) is the precedent for a data-source failure taking a number;
**H12/H13** are claims about gexbot's *data*, not its failure modes. **D27
records the mode and its two measured side effects and proposes nothing** — no
credential change, no code change.

### New data point

**None is warranted.** Every failure today traces to the **vintage or the
measurement window of rows already on the page** — a two-business-day-stale FRED
pair, a pre-market breadth read the cash session reversed, a band rider that
fires 245pts from its own wall, and a level set pruned to nothing by a zero
budget. No free, reliable feed fixes any of those, and buying a feed to paper
over a weighting problem is how the model gets worse.

---

## Journal hygiene

One scan file for 10-22 (`1248-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** (6 across the record, excluded by
`track.py`). **09-24 quarantined by hand — 18th consecutive review**; no schema
`quarantine` field, 09-29 proposal reaffirmed. **2026-10-13 has no journal
directory — documented, not recreated.** 09-09 and 09-25 still have no
`REVIEW.md` and none was created or back-dated. **2026-10-23 is on disk,
`is_trading_day: true`, 180 bars, correctly held back.** No fabricated or
backfilled entries found. **One new ID allocated: D27. Next free: H27 · D28 ·
P-I.**

**D26 — the symptom changed again, and this is the sharpest instance yet.**
`track.py` prints **31 trading days / 34 scans**, direction **17/8/9**, levels
0.5 — *the identical headline figures the 10-22 run printed, over a different
31 days.* **2026-09-08 has now joined `HELD BACK` at 98 bars**: a day completed
six weeks ago, filed as *"day not finished"* because only part of its bar series
survives inside the 45-day fetch window. So 09-08 left the sample as 10-22
entered it, the count did not move, and the H1 per-day mean went **+45.4 → +58.6**
on a change that is **one day in and one day out**, not one day added. On disk:
**39** day directories, **69** scan JSONs, **34** days with a PRE_NY scan,
**33** with a `REVIEW.md` (**34** after this review), **30** with both (**31**
after). The **silently invisible set did not grow** — it is still the six August
directories (08-23 … 08-28), for which `review_day` returns no `scans` key and
`track.py:84` `continue`s. 39 − 6 = 33 = 31 graded + 09-08 held + 10-23 held,
which reconciles exactly. `track.py` still prints **no literal
`actionable: YES/NO`**; the threshold rule was applied by hand.
