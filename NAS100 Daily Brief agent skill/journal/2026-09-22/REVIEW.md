# REVIEW — 2026-09-22 (Tue) — direction right, the ceiling wrong by 265 points

Graded 2026-09-23 from `review_day.py --json` (resolved to 2026-09-22) and
`track.py`. **1 gradeable scan** (12:47:09Z PRE_NY). **0 test artefacts.**
`is_trading_day: true`; no `is_trading_day: false` scan exists on this date, so
nothing was excluded on that ground. The 2026-09-23 scan is **excluded** from
every statistic — `track.py` holds it back at 179 bars.

**Journal integrity: clean.** `1247-preny.json` is in commit `1f9c4b0`, authored
`2026-09-22T12:47:14Z` — five seconds after its own `scan_utc: 12:47:09Z`. Not
backfilled, not fabricated. `outcome` is still `null`; every actual figure below
comes from `review_day.py`, not from the journal's own claims. No `prediction`
block was touched.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 30510.8 / **30788.1** / 30394.0 / **30728.1** |
| Range / net | **394.1** / **+217.3** (net = **55%** of range) |
| ADR14 | 417.1 → range **0.94x ADR** |
| Bars | 276 |

**Direction** — **1 right / 0 wrong / 0 no-call.**
Bias **+6 BULLISH**, `expected_direction +1`, post-scan move **+241.6** →
**CORRECT**. Running record: **12 right / 7 wrong / 6 no-call** (16 trading days,
25 deduped scans).

**Fuel** — budget **171.5**, extension **148.5**, error **−23.0**,
`about right` (0.87x). Traversal 317.0 = **1.85x** budget. H1 per-day mean
**+39.7 (n=15) → +35.8 (n=16)**; still entirely driven by the 09-21 tail.

**Levels** — 16 published, 9 touched, hit rate **0.56** (16-day mean 0.54).
**Corrected for clustering the 16 levels occupy 10 distinct price zones, of which
4 were touched → 0.40** (0.44 excluding the structural wall). Of the 6 untouched
zones, 4 sat **−219 to −1469** below price on a +217pt up day.

**News coverage (standing record for the sampling-bias item):** counted **2**
(0 bull / 2 bear, 100% bearish), uncounted **51** — coverage **3.8%** — score
**−1**.

---

## 2. What the levels actually did

| level | brief said | what happened | verdict |
|---|---|---|---|
| **30523.4** CALL WALL ●●●●● 1.50bn ⭐ | *"desks must SELL as price rises into it, so **rallies stall. Take profit into it.** … the strongest ceiling on the board"* | 32.4pt retest, then **+264.7 above** at the high and a close **+204.7 above** | **The headline failure, 3rd session running.** "Take profit into it" exited at 30523 on a day that closed 30728. The brief's own escape clause (*"a held close above… becomes a launchpad"*) is what actually happened, and it is the sentence a reader is least likely to act on |
| **30581.9** PDH + NY High ⭐ | *"the biggest pile of stops above us. Sweep it, wait for a lower high on the 1m, then **CISD = short**"* | Swept 13:30, 123.3pts of travel up afterwards, closed **+146.2 above** | **Wrong side of the move.** The one explicit short trigger on the board sat under a 146pt close-above |
| **30573.4** shelf 0.43bn + London High ⭐ | *"the next session usually runs the stops above it"* | Stops run, 131.8pts up afterwards, never reclaimed downward | **Factually right** — and the only up-side level whose note matched the outcome |
| **30639.6 / 30629.5 / 30623.4** Asia High · Equal highs ×3 · shelf 0.62bn | *"prime S1 sweep trigger"* / *"expect price to stall, take partials"* | All three first touched **13:35–13:40** (one move through a 16.2pt band); all three then held as **support** 255–270min, worst excursion −5.1 / −10.3 / −9.1 | **Good levels, but one observation, not three.** The stall was real and small; the "sweep trigger" framing was again the wrong direction |
| **30495.6 / 30489.8 / 30473.4** PD close · Asia Low · shelf 0.36bn | *"price often comes back to fill a gap"* / *"expect price to stall"* | One move through a 22.2pt band at 12:50–13:00; all held as support to the close, worst excursions −4.6 / +1.2 / **−2.3** | **The shelves were the best levels on the page.** 30473.4 held 490min on a 2.3pt wick, 5 re-touches |

**Untouched:** shelf 0.83bn (−69), London Low + Equal lows ×2 (−98/−104),
PUT WALL (−219), GAMMA FLIP (−374), MAX PAIN (−529), STRUCTURAL PUT WALL
(−1469). The lower board was never tested — it was outrun, not wrong.

**STRUCTURAL PUT WALL is now 0 touches on 9 publications across 8 trading days**
(08-24, 08-25, 08-26, 09-10, 09-14, 09-15, 09-21, 09-22), today at **3.52x
ADR14** below spot. Correct behaviour for a level whose own note says *"mark it
and leave it"* — and exactly why it should leave the hit-rate denominator (P3).

**The grader inverted three verdicts again (M6, 11th session).** PDH
(*"broke DOWN through it — lost by 90.9pts"*), shelf 0.43bn + London High
(*"lost by 82.4"*) and the CALL WALL (*"lost by 32.4"*) all closed **146, 155 and
205 points BELOW the close** — i.e. all three were broken **upward** and held as
support into the bell. `settled_side` reads `above` on all three while
`held: false`; the English and the field contradict each other in the same object.

---

## 3. What was wrong, and why

**The direction call is not the story — the ceiling is.** +6 BULLISH was right,
and the two components that earned it were `structure +3` (*"price is ABOVE the
entire prior-week range… PWH 29704.2 is now support"*) and `breadth +2/+1`
(mega-caps 4/4, NDX +2.83% vs ES +0.09%). Price never came within 690pts of PWH.

What was wrong is everything the brief said about **where** the move would end:

1. **`gamma −2`, "price sits in the top 20% of the wall band (30273.4–30523.4) —
   poor risk/reward for longs."** Third consecutive counter-instance, and word
   for word the 09-18 and 09-21 outcome: price left the band upward and never
   returned, high **+264.7** and close **+204.7 above the band top**. Record
   **3 for / 3 against**. Critically, the register's planned disposal of this row
   — *"if a third arrives, it merges with P-F"* — **is contradicted by this
   instance**: P-F's condition is price already outside the prior day's range,
   and at 30492.5 price was **inside** it (PDH 30581.9 / PDL 29623.5). The stale
   band mechanism does not explain today. This row needs its own treatment, and
   it does not have a clean one yet (see §4).
2. **`STRATEGY 1 — sweep → failed re-break → CISD reversal`**, justified as
   *"positive gamma above the flip: dealers fade extensions, so sweeps genuinely
   fail."* Four liquidity sweeps above price — Asia High, equal highs ×3, London
   High, PDH — were all taken and all held. By the register's own grading rule
   (net ≥75% or ≤25% of range) today's 55% is **not judgeable**, so no right/wrong
   is claimed; the *premise sentence* was nonetheless false on every level it
   applied to, and this is the 4th consecutive session above the flip where that
   was true. Two of the four (09-18, 09-22) were inside the prior-day range, so
   P-F would not have caught them.
3. **`macro −3` from DFII10**, seventh instance, with its own `why` string
   admitting *"FRED has not published since 2026-09-18 (2 business days ago) —
   this is last week's reading, not today's."* Removing it gives **+9** instead
   of +6 — stronger and more accurate. Second consecutive session where the stale
   row cost conviction on a **correct** call. P1 covers it; blocked on H19.
4. **`news −1` off 2 of 53 headlines.** Both counted headlines were genuinely
   hawkish-Fed, so this is not a D18 sign error — it is the coverage/sample-size
   mechanism at **3.8%**: 4 counted headlines scored −3 on 09-15, 2 counted
   scored −1 today, on the same 100%-bearish subset sign.

**One thing the brief got right and buried.** The secondary gamma table's
**30773.4** (0.52bn but **25,732 contracts — the largest contract count on the
page**) sat **14.7pts under the session high**, while the headline CALL WALL
(1.50bn, 22k contracts) was 264.7pts under it. The day's high was defined by a
strike ranked by contracts, not by dollar gamma, and it appeared only in a table
the brief tells the reader is *"context"*. This is a D7-shaped instance.

---

## 4. Change proposals — only material ones

`track.py` reports **actionable: threshold met** (16 trading days ≥ 3), so the
day-count gate is open. **I am proposing nothing new.** Every finding above lands
on an item already in the register, and the one that has newly reached three
same-direction sessions does not have a change that survives its own evidence.

**Not proposed, and here is why — `gamma −2` top-20%-of-band (D21).** Three
consecutive counter-instances is the threshold, so I tested the obvious fix
(demote the ±2 to prose, keep the sentence) across all **8 firings** on record:

| day | published | without the row | actual dir |
|---|---|---|---|
| 08-27 | +7 | +9 | +1 |
| **08-28** | **+4** | **+6** | **−1** |
| **09-08** | **+4** | **+6** | **−1** |
| 09-09 | −2 | 0 | −1 |
| 09-17 | −2 | 0 | +1 |
| 09-18 | +4 | +6 | +1 |
| 09-21 | +13 | +15 | +1 |
| 09-22 | +6 | +8 | +1 |

**In 8 firings the row never flipped a direction call's sign.** It only moves
conviction: five days more conviction in the correct direction, two days
(08-28, 09-08) more conviction in a **wrong** one, and two days (09-09, 09-17)
lose their sign to zero. **No label sign changes at all**, so demoting it cannot
be justified as an accuracy fix — it is a conviction-scaling change dressed up as
one, and on the two days it currently helps it is the only bearish row on a wrong
bullish call. **Evidence appended; no change.** What would break the 3/3 tie is a
discriminator, and 6 tested instances is not enough to fit one — that is the
H1/P-E lesson.

**Not proposed — rescaling `SETTLE_TOL` to realised range.** The 09-21 sub-note
suggested it. Today kills it: the three inverted verdicts were −32.4, −82.4 and
−90.9 on a 394.1pt range = **8.2%, 21%, 23%**, all above the 5.0–5.6% band where
the same call wall graded "held" and "lost" on consecutive weeks. A relative
tolerance would still have graded all three "lost". **Only M6's written fix —
grade against direction of approach, reversal measured from the touch — fixes
this.** M6 needs a decision, not more evidence; recording that the cheaper
alternative is now falsified is the point.

**Evidence appended to existing items, no proposal attached:**

- **P-E** — 9th call-wall instance, **4 capped / 5 sliced**. Sliced run-throughs
  now 103 / 154 / 185 / 573 / **205 (close-above)**; capped overshoots still
  3.6–11.9. **Nothing between 12 and 103 in nine observations**, and the last
  three sessions are all slices. P-E is already proposed as prose; today it is
  three-for-three against the unconditional lid.
- **P3 / H6** — structural wall 0 for 9 publications across 8 days; today at
  3.52x ADR14.
- **P-B(b)** — cleanest clustering instance yet: 16 levels → 10 zones, 9 "touches"
  → **4 independent events**. Published hit rate 0.56, zone hit rate **0.40**.
  The three levels that "held support for 255–270min" are one level.
- **H18 / P1** — 7th DFII10 instance, 2nd consecutive on a correct call.
- **H10** — the `+3` above-prior-week-range branch fired for the **2nd time** and
  was right again (n=2). The `−3` branch stays 0-for-4 and did not fire. Do not
  let the positive branch's record rehabilitate the negative one.
- **D7** — contract count vs dollar gamma: the high stopped 14.7pts under the
  heaviest-contract OTM strike, which is not on the actionable board. n=1
  measurable (the secondary table is not in the journal JSON, so this cannot be
  counted historically — that is itself worth fixing before the claim can ever be
  tested).
- **News sampling bias** — 09-22: counted 2, uncounted 51, sign 100% bearish,
  score −1, coverage 3.8%.

**What I am watching, and what would make it actionable:**

1. One more session where `gamma −2` fires with price **inside** the prior-day
   range and price leaves the band upward → 4 against, and the "poor risk/reward
   for longs" claim can be tested against breadth as a discriminator rather than
   guessed at.
2. One more call-wall instance **between 12 and 103 points** of run-through. Nine
   observations with an empty middle is either a real bimodality or a
   measurement artefact of `SETTLE_TOL`; a middle observation distinguishes them.
3. Whether the secondary gamma table's top-contract strike keeps marking the
   extreme. It needs to be persisted in the journal JSON first.
