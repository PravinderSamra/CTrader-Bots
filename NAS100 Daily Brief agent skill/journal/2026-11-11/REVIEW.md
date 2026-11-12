# REVIEW — 2026-11-11 (graded 2026-11-12)

One scan: `1246-london.json`, 12:46:45Z, `LONDON`, `is_trading_day: true`,
`test_artefacts: 0`, `outcome: null`. No `is_trading_day: false` scan anywhere in
the window examined, so nothing was excluded on that ground.

## 1. Scoreboard

| | |
|---|---|
| Session O/H/L/C | **27727.5 / 28591.4 / 27715.3 / 28380.4** (276 M5 bars) |
| Range / net | **876.1** (1.005× ADR14 872.0) / **+652.9** |
| Pre-scan / post-scan | pre-scan range **577.0** (high 28292.3 = London High, low 27715.3 = session low); post-scan high **28591.4**, post-scan low **28095.4** (28591.4 − traversal 496.0) |
| Direction | **0 right / 1 wrong / 0 no-call.** Score **−15** `STRONGLY BEARISH`, expected −1. Post-scan **+101.9**, day-net **+652.9** — WRONG on both bases |
| P-H | **not** a deciding instance (post-scan and day-net agree) |
| H17 | **not** a noise case — post-scan 101.9 / range 876.1 = **11.63%**, outside the proposed 5% band |
| Levels | **7 of 16 touched = 0.44** against the running **0.49** (31 scans) |
| Fuel | budget **295.0** vs extension **299.1** = **1.01×**; error **+4.1**; traversal 496.0 = **1.68×**. `review_day` verdict *"about right"* |
| VXN-implied | **509.1** vs realised **876.1** — under by **367.0** |

**+4.1 is the most accurate budget call in the recent window** — the session
before it was the largest over-estimate on record (−270.2). Two adjacent
sessions at −270.2 and +4.1 is the dispersion H1 has been describing, not a
trend, and nothing is proposed off it.

## 2. What the levels actually did

**Touched (7 of 16), every one of them at or above 28117.1.**

| level | the brief said | what happened |
|---|---|---|
| **28303.7** CALL WALL ●●●●● ⭐ (+18) | *"desks must SELL as price rises into it, so rallies stall. Take profit into it. **A held close above flips that selling to buying and it becomes a launchpad.**"* | **The best row on the page, and the conditional is why.** First touch 13:20Z stalled (`travel_up −3.2`) and the wall capped for ~2h15m. Then it went: high **28591.4 = 287.7 above (0.33× ADR)**, close **28380.4 = 76.7 above**. The headline *"rallies stall"* was falsified; the second sentence called the launchpad exactly. **The conditional earned its place and the unconditional clause did not.** |
| **28292.3** London High (+7) | *"the next session usually runs the stops above it"* | **RIGHT, and it beat §2.** Swept and price ran **299.1 beyond**, closing 88.1 above. §2 told the user the opposite — see §3. |
| **28253.7** shelf (−32), §3's named DOWNSIDE brake | *"Expect a stall at 28253.7 — take partials rather than assuming a clean breakdown"* | **SLICED by 158.3 (0.18× ADR)** to the 28095.4 post-scan low. |
| **28303.7** again, as §3's named UPSIDE brake | *"Expect a stall at 28303.7 — take partials rather than assuming a clean breakout"* | **SLICED by 287.7 (0.33× ADR).** |
| **28403.7** shelf (+118) | *"expect price to stall"* | Touched 15:50Z, chopped both sides, no settled read; price finished **187.7 above** it. No stall. |
| **28353.7** shelf (+68) | *"expect price to stall"* | Touched 15:45Z, *"broke DOWN … lost by 44.6"*, then closed **26.7 above**. Mixed, and the grader's verdict is the wrong half of it. |
| **28174.2** Asia High / **28117.1** London Low | *"the next session usually runs the stops"* | Both run and both then held as support (worst −12.4 / −21.7). Honest rows. |

**This is the second session with BOTH §3 brakes reachable, and unlike the first
they did not split — both were sliced.** H23 census **18 / 3 / 5 → 20 sliced / 3
capped / 5 never-reached, n=28.** The entry's claim is not in doubt any more; it
is waiting on a decision, not on evidence.

**Untouched (9 of 16), and 8 of them are below price on a day that only went up.**
28060.6 · 27995.9 · 27979.5 · 27953.7 · 27935.4 · 27735.3 · 27653.7 · 27453.7
were all published into a side that never traded after the scan — **50% of the
board was dead weight**, which is 11-09's failure (*"42% published into a side
that never happened"*) repeated, not 11-10's void. **Mitigating, and it should be
said: five of the eight already carried `_(stretch)_`,** so the board's own
honesty marker was doing its job on most of them.

**The 10th untouched row is the interesting one: 28653.7 STRUCTURAL CALL WALL,
missed by 62.3 points** — and the session high landed in the **250-point gap**
between 28403.7 and it, 187.7 above the nearest published row. **Level-board
watch item, instance 3, and the first on the UPSIDE** (11-09 wrong side, 11-10
downside void, 11-11 upside void). **n=3 CONDITION, harm still not demonstrable
from any single day — see §4.**

**M6 — session 43, and the two clearest instances in the series.** The grader
reports `worst_excursion` **−63.3** for 28253.7 and **−35.4** for 28303.7 when
price traded **158.3** and **208.3** below them respectively. Both understate by
more than 2×, and 28117.1's *"held as support for 490min, settled_from: open"*
is asserted over a session whose low was **401.8 points beneath it**.
Expected-by-identity; nothing new proposed.

## 3. What was wrong, and why

**The whole score was wrong except one row, and that row read live data.**

| block | rows | points | verdict |
|---|---|---|---|
| gamma (live chain + live price) | +2 −2 +2 | **+2** | the **only** right-signed block |
| rear-view (prior-session closes) | vol 0 −2 −1 0 · rates −3 −1 0 · breadth −2 −1 | **−10** | wrong-signed |
| macro (FRED, as-of **2026-11-09**) | −3 −1 0 0 0 0 | **−4** | wrong-signed |
| state / text | structure +1 0 −1 · fuel 0 · news −3 | **−3** | wrong-signed |
| published | | **−15** | WRONG |

**The rear-view block takes instance 4 and the "late, not biased" conclusion
SURVIVES.** Census: 11-05 **+8** cancelling a correct −12 · 11-06 **−8**
amplifying a falsified −19 · 11-10 **+3** cancelling a correct read · 11-11
**−10** amplifying a falsified −15. **2 cancel-a-correct / 2 amplify-a-wrong at
n=4 — still two-sided, still no weight change proposed.**

**CORRECTION to that item's own table, and it is the finding here.** The
register's partition (line 17861, repeated 18107) files `macro` under
***"forward-looking (chain, credit, Fed)"***. On 11-11 that is simply false:
`macro`'s two non-zero rows are **DFII10 as of 2026-11-09** and **DGS10's
11-06→11-09 move** — both **2 business days** old, i.e. **older than the
rear-view block's 11-10 closes**. `macro` is not the forward half of the score,
it is the stalest part of it, and that is structural rather than a property of
this day: every non-zero `macro` row in the 30-scan window is a FRED series
published with a 1–3 business-day lag. Re-partitioned honestly, **11-11's
only current-data block is `gamma`, it was +2, and it was right; 100% of the
wrong-signed weight came from data older than the scan.** The partition should
be restated before anyone quotes the forward/rear-view census again. **n=1 for
the day, n=30 for the structural claim, NOTHING PROPOSED** — this corrects a
label, it does not license a weight change.

**11-11 is the cleanest control the "internal contradiction" family will ever
get, and it exonerates that family.** §1 `STRATEGY 1`, §2 *"this is your fade
day · sweeps of a high or low tend to genuinely fail"*, §3 *"stall"* on **both**
paths, §4's wall note *"rallies stall"* — **every block agreed**, there was no
contradiction anywhere in the document, and the day falsified all of them
together. **H2 is a NON-instance and a clean control** (MODERATE ∩ above-flip;
no cell conflict). Whatever is costing direction accuracy, it is not the
briefs disagreeing with themselves.

**The one place the document did disagree with itself, §4 won.** §2: *"sweeps of
a high or low tend to genuinely fail."* §4 on 28292.3: *"the next session usually
runs the stops above it."* The sweep ran **299.1 points** and closed 88.1 above.
A gamma-regime sentence and a liquidity sentence gave opposite instructions
about the same price seven points away, and the cheap one was right. **n=1,
logged, nothing proposed.**

**D21's cell fired and lost.** `gamma −2` — *"price sits in the top 20% of the
wall band (27653.7–28303.7) — poor risk/reward for longs"* — at **97.2%** up the
band. Price then ran **305.7 further up** and **closed above the band**. This is
the rule's harm case, not a near-miss: 10-19 and 11-09 were near-misses followed
by price running to the top of the band; **11-11 is the gate FIRING and being
wrong in the same direction.** Added to D21.

**H19 — `news −3` on a +652.9 day, coverage 6.3%.** 4 of 63 headlines scored;
the decisive one was *"Nvidia's valuation tumbles to a 15-year low"* and **NVDA
closed 11-11 at +2.866%** (verified from source). The scorer read a
valuation-commentary headline as `earnings_miss`.

**The `gamma +2` that was right was right for the wrong reason, and its
companion row was falsified.** *"week net GEX 4.004 $bn/1% → pinning likely"*
scored **+2** on a day that ranged **1.005× ADR**. There was no pin. The row
pointed the right way by accident and should not be counted as a success.

## 4. Change proposals — only material ones

**NO NEW ID ALLOCATED.** `grep -c '^## H28'`, `'^## D32'`, `'^## P-J'`,
`'^## M8'` all return **0**, re-confirmed 2026-11-12. The runner supplied the
D22(a) material as claims to verify and left allocation here; it stays at
**D22(a)** as a **fifth limb**, for the reason the 11-10 and 11-11 reviews both
gave — a new number for an owned mechanism is the collision pattern the header
exists to prevent.

### D22(a) — fifth limb: all four runner claims reproduce; one is CORRECTED UPWARD and one DOWNWARD

**Verified independently** (own Yahoo fetch 2026-11-12, gates read from
`bias_engine.py:150` and `:190`) against `journal/2026-11-12/1246-london.json`
(score **−11**, `rates` **−1**).

**Claim 1 — per-symbol windows, CONFIRMED 4 of 4.** True prior-session =
11-10 close → 11-11 close.

| symbol | printed | true prior-session | verdict |
|---|---|---|---|
| `^NDX` | +2.28% | 27740.789 → 28374.25 = **+2.2835%** | **match** (cash) |
| `^TNX` | +0.30% | 4.983 → 4.998 = **+0.3010%** | **match** (cash) |
| `ES=F` | −0.40% | 7544.25 → 7640.50 = **+1.2758%** | **sign flip, 1.676pp** |
| `DX-Y.NYB` | +0.02% | 102.23 → 102.91 = **+0.6652%** | **wrong, 0.645pp** |

Runner's 1.68 / 0.65 are the rounded prints; exact is **1.676 / 0.645** — both
reported, not averaged. **The printed figures are confirmed to be the LIVE
intraday move, not merely wrong:** printed DXY last 102.935 against the 11-11
close 102.910 = **+0.0243%**, which rounds to the published +0.02%.
**`^VXN` is a third clean cash control** (printed 26.74, −6.4%; true 28.57 →
26.74 = −6.405%), and **the mega-cap leg is CONFIRMED UNAFFECTED for a seventh
scan** — NVDA **+2.866** / MSFT **−2.256** / AAPL **+2.043** / AVGO **+3.988**
from source against the printed +2.87 / −2.26 / +2.04 / +3.99. **Blast radius
holds at 2 of 12 symbols.**

**Claim 2 — point-changing on the LIVE published score, CONFIRMED.** Printed
+0.02% → `rates +0`; true +0.6652% clears ±0.4 → **−2**. **Today's −11 would be
−13 and `rates` −1 would be −3**; label unchanged. **Second consecutive day
moving the delivered score.**

**Claim 3 — breadth survives, CONFIRMED.** True gap **+2.2835 − (+1.2758) =
1.0077pp**, still clears ±0.2 → **+1 stands**. The printed gap of **2.68pp**
overstated it **2.66×** (runner said 2.7×). **Running tally for part 1: n=6 → n=7
scans, 14 of 14 leg-pairs mis-windowed, point-changing rows 7 → 8.**

**Claim 4 — the DXY tally, CONFIRMED from independent closes.** Point-changing
on **6 of 7**: 11-04 **−2** · 11-05 **0** · 11-06 **+2** · 11-09 **−4 (sign
flip)** · 11-10 **+2** · 11-11 **−2** · 11-12 **−2**. With the 11-11 review's
0-of-5 for 10-29→11-03, that is **6 of 12 across the full window, all six in the
last seven sessions.**

**The runner's volatility conditional — CORRECTED UPWARD on n, and CORRECTED
DOWNWARD on mechanism.** True prior-session DXY moves by scan date: 10-29
−0.127 · 10-30 −0.147 · 11-02 −0.157 · 11-03 −0.128 · 11-04 +0.118 · 11-05
−0.353 · 11-06 +0.039 — **7 of 7 inside ±0.4**; then 11-09 **+0.739** · 11-10
**−0.635** · 11-11 **+0.571** · 11-12 **+0.665** — **4 of 4 outside**. **It is
n=4 consecutive, not n=2**, and in the full two-month series only five other
sessions clear ±0.4 and **none of them are adjacent** — the current run is
unprecedented in the available window.

**But the conditional's mechanism as stated is wrong, and this matters more than
the n.** *"It bites every day the dollar trends"* is not what the record shows:
it bites whenever the **live** and **true** figures straddle the gate **in either
direction**. In the 7 quiet scans it still fired **twice** (11-04, 11-06), as a
**false positive** — live cleared, true did not. In the 4 trending scans it fired
**4 of 4**, as a **false negative** — true cleared, live did not. **4/4 under
trend, 2/7 when quiet. Both failure modes are live.** The trend conditional
raises the hit rate, it does not gate the defect, and urgency should be argued
from 6-of-12-overall rather than from the trend run.

**CORRECTION AGAINST PART 1's OWN CASE, carried forward and STRENGTHENED.** At
n=7 scans, correcting to *"both prior-session"* still changes **zero direction
grades** — and 11-11 is now graded, which gives the second instance where the
correction moves the score **AWAY** from the realised day: **11-09 −3 → −7
against a +1045.5 day**, **11-11 −15 → −17 against a +652.9 day**. **Two of
seven move away, zero move toward.** Part 1 is a **correctness** fix. It must
not be sold as an accuracy fix, and this review is more confident of that than
the last one was.

**Part 2 (breadth NDX leg on the overnight window) — n=4 → n=5, and 11-11 is its
first GRADED NARRATIVE-HARM case.** The 11-11 review logged the inversion at n=1
on an ungraded scan; it is now graded.

| scan | printed | prior-session | live/overnight | day |
|---|---|---|---|---|
| 11-05 | +1 **wrong** | −1 right | **−1 right** | down hard |
| 11-06 | −1 **wrong** | −1 **wrong** | **+1 right** | +331.9 |
| 11-09 | +1 right | +1 right | **0 neutral** | +1045.5 |
| 11-10 | +1 **wrong** | +1 **wrong** | **−1 right, moves the GRADE** | −167.8 |
| **11-11** | **−1 wrong** | **−1 wrong** | **+1 right** | **+652.9** |

**live 4 right / 1 neutral / 0 wrong · printed 1 right / 4 wrong ·
prior-session 2 right / 3 wrong.** On 11-11 the live basis is `nq_implied`
**28282.0** against the 11-10 cash close **27740.79 = +1.951%** versus ES
+0.91% → **+1**. Score **−15 → −13**, label unchanged, **grade still WRONG** —
so this is a narrative fix on 11-11, not a grade fix, and the narrative harm is
real: the delivered brief told the user ***"NDX −0.60% vs ES +0.91% — tech
lagging, rotation out of tech"*** on a morning NQ was **+1.95% overnight**, and
NDX closed the day **+2.28%**. The sign of the sentence was inverted against
both the overnight tape and the realised session. **Zero new data** — the leg is
already computed in `gex_levels._nq_implied_cash`. **Falsifier unchanged:** three
sessions where live is wrong-signed and printed is right. **Proposal NOT
widened.**

**ONE SEQUENCING RECOMMENDATION, which is the only new ask in this review.**
Parts 1 and 2 are both live and the 11-10 review proposed them together. At n=7
/ n=5 the evidence now separates them cleanly: **part 1 is 0-for-2 on moving the
score toward the day and 2-for-2 on moving it away; part 2 is 4-right / 0-wrong
on the sign and has one grade flip and one narrative inversion to its name.**
**Recommend shipping part 2 first.** Evidence: the five-row table above plus the
seven-scan zero-grade-change result. Expected effect: breadth sign correct on
the 4 of 5 sessions where the overnight tape disagrees with the prior cash
close; score impact ±1 to ±2; **no label change on any of the five.** Part 1 is
not withdrawn — it stops the brief asserting a shared present tense it does not
have, and it is the change that actually removes the hair-trigger gate
fragility — but it is cosmetic for accuracy and should not be allowed to block
the row that is not.

### The three items the runner declined to raise — all three judged correctly, with data

1. **The 6.3bn GEX swing is NOT a finding, and the record says so emphatically.**
   Consecutive-session |Δ week net GEX| across 29 transitions since 10-01:
   **9 of 29 exceed 6.3bn**, the largest is **14.84bn** (10-08 → 10-09), and
   11-11 → 11-12's **6.35bn** sits just above the middle of the distribution.
   Unremarkable. **Closed, not logged as an instance.** *(The more unusual number
   in the same pair is the **gamma flip moving +814.0** while price moved −186.2
   — but that is the 3rd largest of 29 and also has precedent, −998 on 11-02 and
   −859 on 11-06. Also closed.)*

2. **Both-paths-clear without a fade instruction is NOT another 11-05.** Correct
   call. §1 on 11-12 reads *"Strategy-1 fades have a materially lower hit rate
   here — only take them at the far walls"*, which **agrees** with *"Do not fade
   it"*; 11-05's contradiction was *"Do not fade it"* four lines above *"favour
   fades over chasing breaks"*. The shape itself is common — **both-clear in 2 of
   the last 11 sessions, both-friction in 3, split in 6** — so §3's path read is
   **non-discriminating 45% of the time**, which is a separate and older
   observation and is **not** opened here.

3. **The repeat-scored FRED datum IS covered, and it is n=1 anyway.** H18
   (*"a stale FRED series still moves the score"*) and P1 (*"observations carry
   an age and nothing reads it"*) own exactly this; the register has already
   recorded *"one stale FRED observation counted twice"* (line 9526). **And the
   repeat is a one-off:** every scan from 10-20 to 11-11 carries a **distinct**
   DFII10 as-of date advancing one business day at a time; 11-12 is the **first**
   repeat in 17 sessions, and the cause is **Veterans Day** — the bond market was
   shut on 11-11 so FRED had nothing to publish. **n=1, benign, nothing opened.**

### Everything else, one line each

- **H23 — instances 26 and 27, both SLICED, census 18/3/5 → 20 sliced / 3 capped
  / 5 never-reached (n=28).** Second session with both named brakes reachable;
  the first split, this one did not.
- **D21 — the gate FIRED and was WRONG** (97.2% up the band, `gamma −2`, price
  then ran 305.7 up and closed above the band). First firing-side harm instance
  after two near-misses.
- **M6 — session 43**, two `worst_excursion` figures understating by 95.0 and
  172.9 points; expected-by-identity.
- **D31 — the VXN-implied range is under again** (509.1 vs 876.1, by 367.0),
  after 11-10 (507.0 vs 587.4, by 80.4). **Serial reconciliation needed:** the
  register carries counter-instance **12** from the 11-09 grading and the 11-10
  review logged none, so the carried serial is behind by at least one.
- **H19 — coverage 6.3%** (4 of 63), `news −3` on a **+652.9** day.
- **H26 — a ≥10-bucket instance** (|score| 15, `|post|/ADR` = 101.9/872 =
  **0.117**), direction WRONG.
- **H1 — error +4.1**, the most accurate budget call in the window, immediately
  after the largest over-estimate (−270.2). Dispersion, not a trend.
- **H10 — did not fire** (price inside the prior-week range).
- **Level board — instance 3**, first upside void: session high 28591.4 landed
  in the 250-point gap between 28403.7 and 28653.7. **n=3 CONDITION / 0
  demonstrable harm — still NOTHING PROPOSED**, because on all three days the
  void or the wrong side was a consequence of where the chain's density
  actually sat, and three conditions are not three harms.
- **Bias-gate fragility — watch item, no new data point.** 11-12's corrected DXY
  cleared ±0.4 by 0.265pp and corrected breadth cleared ±0.2 by 0.808pp; both
  comfortable. The item stays at n=3 condition / 0 harm.
- **P-C / `event_gate`** — `null` on 11-11, correct (no tier-1 print).

### New data point

**NONE warranted. `ZN=F` stays DECLINED, and it takes its first paired
reading.** For the 11-12 scan the printed `^TNX` row is **+0.30% (yields up,
`rates −1`)** while overnight `ZN=F` went **106.0312 → 106.078 = +0.044% in
price, i.e. yields slightly LOWER** — opposite sign. **n=1 paired reading.** It
cannot be reconstructed for 11-11 (no stored intraday `ZN`), and the
one-change-at-a-time rule applies while D22(a) parts 1 and 2 are both live.
**Watching: overnight `ZN` against the printed `^TNX` prior-session move, every
scan — and recording it now rather than asserting it later.**

## Journal hygiene

`2026-11-11/1246-london.json` + `.md`, `is_trading_day: true`, 276 bars,
`outcome: null` — not back-written, which is correct. `git log` shows
**cdaa49f committed at 2026-11-11 12:46:45Z for a 12:46:45Z scan** and
**ec14b5d at 2026-11-12 12:46:50Z for a 12:46:50Z scan** — same-second commits,
no backfill. **No fabricated or backfilled entry found; no `prediction` block
was read-modified by this review.**

## track.py

**COMPLETED, exit 0, ~16 minutes. 31 trading days / 31 scans (deduped), 6
`test_artefact` entries excluded as always.**

**The `actionable: YES/NO` line the role description expects is NOT emitted by
this build of `track.py`.** The equivalent is the header line *"31 of 3 days for
the 3-day hypotheses (H1/H2/H3/H5/H7) — threshold met, read the evidence before
proposing"*. I have treated that as actionable and applied the 3-session rule by
hand to every item above; where an item was at n=1 or n=2 it was logged and
nothing was proposed. **Flagging the missing string rather than silently
substituting for it.**

**Direction has crossed below 50% for the first time: 12 right / 13 wrong / 6
no-call = 12 of 25 graded = 48.0%** (carried: 13/12/6). **The move is NOT one
data point.** 11-11 enters as WRONG, and **2026-09-28 simultaneously dropped out
of the 45-day bar window**, taking a CORRECT with it. If H17's proposed
`no call (inside noise)` re-grade ships, this number must be restated again.

**D26 — the gap WIDENED to 21 and it has now corrupted a held-back reason.**
**31 full bar sets against 52 finished day directories** (53 minus today's
unfinished 11-12). Worse: **`track.py` reports `2026-09-28` under *"HELD BACK —
day not finished (grades after 21:00 UTC on its own date)"* with 98 bars**, for
a session six weeks in the past. The day is not unfinished, it is **truncated by
the 45-day fetch window**, and the two states are being reported with the same
message. **Routed to D26; a day that has aged out should not be labelled
unfinished.** `2026-11-12` is correctly held back (180 bars).

**H1 per-day mean +103.0 at n=31**, against the carried **+106.5**. 11-11's
**+4.1** is the second-smallest absolute error in the whole table (after 10-26's
+0.1). **H2 — 11-11 is NOT in the low-fuel/exhausted list** (`MODERATE`),
confirming the non-instance read in §3. **Levels touched running mean 0.49**
against today's **0.44**.
