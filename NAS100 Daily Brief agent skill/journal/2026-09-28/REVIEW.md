# REVIEW — 2026-09-28 (graded 2026-09-29)

1 gradeable scan (12:47Z PRE_NY), `is_trading_day: true`, 0 test artefacts, 276
bars. **2026-09-24 is excluded from every options/direction statistic below**
per `HYPOTHESES.md` → *D23 CORRECTED*; its fuel figures stand. Its fields were
not edited. **2026-09-25 had never been graded** (no `REVIEW.md`, no register
entry); it is graded here and folded into the counts, otherwise the session
thresholds below would be short by one.

## 1. Scoreboard

| | |
|---|---|
| session O / H / L / C | 30646.0 / 30663.7 / **30101.2** / 30310.0 |
| range · net | 562.5 (**1.25x** ADR14 448.6) · **−336.0** |
| close position in range | 37.1% |
| direction call | **CORRECT** (BEARISH −7, expected −1; realised −1) |
| post-scan move | −161.8 · traversal 400.7 |
| fuel | budget **65.5** vs extension **179.4** → **+113.9, 2.74x UNDER** · traversal 6.12x budget |
| level hit rate | **0.57** (4 of 7 touched); 4 of 4 touched graded "held" |
| VXN-implied range 400.6 | realised 562.5 → VXN under by **1.40x** |
| straddle close band 30214–30733 | close 30310 **inside** ✓ (low outside intraday, as its own caveat said) |
| record to date | direction **13 right / 8 wrong / 7 no-call** (09-24 excluded) · H1 per-day error **+30.1** (n=20), **+1.7** without the 09-21 tail |

## 2. What the levels actually did

| level | brief said | what happened | verdict |
|---|---|---|---|
| 30745.9 CALL WALL | "rallies stall, take profit into it" | never reached, 162pts short | untested — no P-E instance |
| 30680.2 GAMMA FLIP | "reclaim and fading becomes valid" | never reached | untested |
| 30572.0 PD mid + London Low (prev-day) ⭐ | "the next session usually runs the stops **below** it" | never reached; price was **already 98pts below it at scan** and stayed there all day | **prose wrong-sided — P-G instance #10** |
| 30479.1 London High (today) | "next session runs the stops above it" | ran 22.8pts above, failed, then capped the day for 480min | **right, and the best level on the board** |
| 30418.5 NY Low(prev) + PDL + Asia Low(prev) ⭐ | "runs the stops below it" | broke down, held as resistance 225min, worst +15.7 | right |
| 30345.9 PUT WALL ●●●●● | "**if** it breaks, expect it to speed UP, not bounce. Don't buy the break" | it had **already broken pre-scan** (London low 30280.6 at 09:15Z, 65pts through) and **bounced 193pts**. It then broke again in NY and accelerated 244.7pts | **1-for-2 in one session**, and the conditional was written for an event already resolved |
| 30245.9 MAX PAIN | "weak on a Monday" | **violated by 144.7pts** (low 30101.2), then reclaimed and held as support 310min into the close | graded "held", but see §3 |

**The day's own lows were never published.** At scan the generator had
`sessions_today` = Asia H 30641.6 / L **30324.8**, London H 30479.1 / L
**30280.6** — both London and Asia windows were complete. Three of those four
were discarded: `brief.py` `keep()` caps session extremes at `budget * 1.75` =
**114.6pts**, so Asia High (+167.8), Asia Low (−149.0) and London Low (−193.2)
all went to the footnote — and `far_line()` prints `rest[:6]` off a
**price-descending** list, so the footnote printed the six *highest* levels
(PWH +346 survived; Asia High +168, the nearest one, did not) and **no downside
level at all**.

Net effect: on a correctly called BEARISH day in short gamma, the lowest thing
the reader was told to mark was max pain at 30245.9. Price went 144.7pts below
it, through two of its own session lows that appeared nowhere in the document.

No clustering today — all 7 levels ≥60pts apart, so 0.57 is an honest hit rate
(clean control observation for **P-B(b)**). It is still uninformative about
quality: the 3 untouched levels were all upside stretch on a day called down
(standing caution, 09-18/09-16).

## 3. What was wrong, and why

**The direction call was right, and it was right by cancellation of two broken
rows — not by being correct.** From `inputs.bias_components`:

- `breadth +2` "mega-cap avg **+1.53%** (4/4 up)" and `breadth +1` "NDX +0.42%
  vs ES −0.35% — tech leading, **genuine risk appetite**". Both legs are
  **Friday's cash session** (`^NDX` and single names do not print pre-market, so
  `regularMarketPrice` is the prior close), printed in the present tense 42
  minutes before a 336pt fall. This is **D22(a)**, and unlike 09-23 it now has
  accuracy consequences: on a like-for-like overnight window NQ was **−0.58%**
  (30473.8 vs PD close 30650.2) against ES −0.35% — tech **lagging**, so the row
  should have been 0/−1, not +1.
- `macro −3` DFII10, carrying its own warning *"FRED has not published since
  2026-09-24 — this is last week's reading"*. **H18 instance #8, and the first
  one where the stale row HELPED.**

Remove breadth's stale +3 → **−10 STRONGLY BEARISH** (one notch stronger, more
accurate). Remove the stale DFII10 −3 → **−4 MILDLY BEARISH** (one notch weaker).
Remove both → **−7**, exactly what shipped. **The published score was correct
because two defective rows happened to be equal and opposite.** That is a
counter-instance to **P1** as written: down-weighting stale rows would, on this
day, have made the call worse unless D22(a) is fixed in the same change.

**The fuel block was wrong and it contradicted the rest of the brief.**
`LOW_FUEL`, 85.4% of ADR used, budget 65.5 → the brief printed *"The range is
close to done… mostly **inside** the extremes rather than making new ones —
**favour fades over chasing breaks**"* while §1/§2 of the same document said
*"**Fading is the wrong trade today** — Strategy 2 (go with the move)"* and
*"Today's ADR can be exceeded — don't cap the target too early"*. The range
extended 179.4 (2.74x budget), the day made 179.4pts of new lows, and the
close-band block — which said the opposite of the budget block — was right.

Census of that contradiction across all 41 trading-day scans: it fires in
exactly one cell, **`LOW_FUEL`/`EXHAUSTED` **and** below the gamma flip**, on
**3 sessions — 09-14, 09-15, 09-28**. Who was right: 09-14 extension 194.1 vs
budget 61.9 (gamma), 09-15 16.0 vs 97.3 (fuel), 09-28 179.4 vs 65.5 (gamma).
**2-1 to the gamma block — not a winner. The contradiction itself is the
finding.**

**M6, 12th session.** Max pain is reported *"held as support for 310min, worst
**−24.3**pts"* on a session where `travel_down` in the same record is **144.7**.
`settled_read()` sets `side_above` from the **last** bar's close and starts the
window at the last bar closing on the other side (15:45), so `worst_excursion`
is measured only inside the final settled window; a 144.7pt violation earlier
the same session is invisible to the verdict. Same defect class as 09-22's three
inverted verdicts, and only M6's written fix (grade against direction of
approach) addresses it.

**Not wrong:** the short-gamma regime read (COHERENT_SHORT → expansion: 1.25x
ADR, 2.74x budget, sweeps ran), the straddle band, and `gamma −5` which carried
the correct call. `events` scored 0 again (row 16 of 16).

## 4. Change proposals

`track.py`: 20 days, 29 scans — **actionable: YES**. Two proposals, both with
≥3 sessions. Neither touches `bias_engine.py` scoring.

### PROPOSED — finish D7 in the CORE branch, and order the footnote by distance

`brief.py` `keep()` exempts `CALL WALL / PUT WALL / GAMMA FLIP / MAX PAIN` from
the range-budget filter (D7, met at 3 instances 09-10) but **session extremes and
PD/PW levels still keep `abs(dist) <= budget * 1.75`**. Tested directly — does
price stay inside `price_at_scan ± budget*1.75`? — on all 16 complete PRE_NY
days:

| | breached below | breached above | either side |
|---|---|---|---|
| all days | 10/16 | 9/16 | **11/16** |
| budget < 70 (8 days) | | | **8 of 8** |
| budget ≥ 88 (8 days) | | | **3 of 8** |

Breach magnitudes when it fails: +119/+286/+303/+470/+307/+93/+258 below,
+101/+125/+352/+586/+362/+75 above. **The rule is wrong on every low-budget day
and right on most high-budget ones — it fails hardest exactly when the board is
narrowest**, which is D7's mechanism, measured.

Second half: `far_line()` protects the four walls but then truncates
`rest[:6]` off a **price-descending** list. Any level dropped *below* price
vanishes from board and footnote together whenever six far levels sit above it —
which is 09-28 exactly.

- **Change:** (a) size the session-extreme/PD/PW cap off ADR14 (or drop the cap
  and tag `(stretch)`), not off the remaining budget; (b) sort/partition
  `far_line` by `abs(dist)` with a minimum of two levels per side.
- **Expected effect:** on 09-28 the board carries London Low 30280.6 and Asia
  Low 30324.8 — the two references the day traded to. No score change, no
  hit-rate definition change (H6/P-B re-measure after, not before).

### PROPOSED — arbitrate the fade instruction instead of printing both

`_FUEL_MEANING["LOW_FUEL"]` emits *"favour fades over chasing breaks"*
unconditionally; the gamma block emits *"Fading is the wrong trade today"* below
the flip. **3 sessions where the brief instructs both (09-14, 09-15, 09-28)** —
prose only, no score.

- **Change:** when the regime block is short-gamma, the fuel block must say the
  range is likely to extend *against* the budget and must not recommend fades;
  say which block is live, or state the conflict.
- **Expected effect:** on 09-28 removes a direct self-contradiction on a day the
  fuel side was wrong by 2.74x. Distinct from the already-logged
  pinning-vs-expansion conflict (that is two scoring rows about range; this is
  two trade instructions).
- **Caveat:** 2-1 on outcomes. This is a coherence fix, not an accuracy claim.

### Strengthened, already proposed, nothing new asked

- **P-G:** instance #10 (PD mid + London Low (prev-day), **+98.2**, on a ⭐ row).
  6 of 12 PRE_NY days now. Note the merge also *discarded* the PD-mid note —
  `liquidity` outranks `magnet`, so the wrong-sided note is the one that printed.
- **P-F:** rebuilt with 09-22…09-28 added. Outside-PD-range >150pts now **4/4
  positive** (09-14 +79.4, 09-17 +40.0, 09-21 +569.2, 09-24 +13.6); inside
  control now **6 of 16 positive, mean −6.3, median −17.3** (was 3/11, −14.0).
  Sign split holds, **but 09-28's +113.9 and 09-16's +136.4 are both larger than
  three of the four "outside" instances.** P-F's magnitude claim rests on 09-21
  alone. Ship as prose; never as a multiplier. (H1 lesson.)
- **H1:** n=20, per-day mean +30.1, **+1.7 without 09-21**. 09-28 is the second
  largest positive at +113.9. No multiplier.
- **M6:** 12th session, new failure mode (above). Needs a decision, not evidence.

### Observed, NOT proposed

- **Max pain's day-of-week qualifier.** Evidence days now 4: 09-16 Wed best
  level on the board · 09-17 Thu never reached (246pts away) · 09-25 Fri never
  reached (**340pts away**) · 09-28 **Mon, the level that held the close**. The
  register's threshold ("3 days published, touched not required") is **met on a
  technicality and should be tightened**: two of the four are misses at 246 and
  340pts, which is a distance effect, not a day-of-week refutation. And 09-28's
  verdict flips with the convention — under M6's proposed grading, max pain was
  *lost* by 144.7pts on a Monday, which **supports** the qualifier. **2 fair
  tests, 1 ambiguous. Nothing proposed until M6 is decided**, because the
  qualifier cannot be graded while the grading rule is the contaminated variable.
- **"No field for price already tested this today" — n=2.** The PUT WALL's
  *"if it breaks"* was a forward conditional for a break that had resolved at
  09:15Z, 3.5h before the scan. First instance 09-17 (call wall). If it recurs,
  this and the H1 session-context sub-observation are one proposal, not two.
- **D22(b) is SETTLED NEGATIVE as specified, and the specified test is void.**
  Ran it: `yahoo_series("^NDX", range=10d)` today returns **every** session
  09-15…09-28 with no nulls, so "a missing date confirms" cannot fire
  retrospectively. But the mechanism *is* confirmed arithmetically — 09-23's
  reported +3.67% is exactly 09-18→09-22 (30732.40/29644.17) and 09-24's −0.04%
  is exactly 09-21→09-23 (30470.29/30482.35), each requiring **a different**
  interior close to have been null at scan time. **The nulls are transient and
  Yahoo backfills them**, so no post-hoc fetch can settle this: the check must
  run live and the dated series must be persisted. 09-28's own leg is clean
  (+0.42% = 30608.13/30478.86 ✓).
- **No P-E instance** (call wall untouched, 162pts short). Still 4 capped / 5
  sliced, still nothing between 12 and 103.
- **No H6/P3 instance** — no `structural` level was published today.
- **Journal hygiene:** no fabricated or backfilled entries. 09-24 quarantined as
  directed; 09-25 was an ungraded completed session and is now graded — worth a
  guard, since proposals are gated on session counts and a silently skipped day
  biases every threshold downward.
