# REVIEW — 2026-09-21 (Mon) — the largest-range day on record

Graded 2026-09-22 from `review_day.py --json` (resolved to 2026-09-21) and
`track.py`. **1 gradeable scan** (12:47:15Z PRE_NY). **0 test artefacts.**
`is_trading_day: true`; no `is_trading_day: false` scan exists on this date, so
nothing was excluded on that ground.

**Journal integrity: clean.** `1247-preny.json` is in commit `fa66280`, authored
`2026-09-21T12:47:18Z` — three seconds after its own `scan_utc: 12:47:15Z`. Not
backfilled, not fabricated. `outcome` is still `null`; every actual figure below
comes from `review_day.py`, not from the journal's own claims. The 2026-09-22
scan is **excluded** from every statistic — `track.py` holds it back at 179 bars.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 29647.9 / **30581.9** / 29623.5 / **30495.6** |
| Range / net | **958.4** / **+847.7** (net = **88%** of range) |
| ADR14 | 389.2 → range was **2.46x ADR** |
| Bars | 276 |

**Both of those are records.** Previous largest range ratio on record: 1.47x
(09-17). Previous most-directional day: 82% (09-17). The whole prior distribution
of range ratios was 0.77–1.47; this day sits a full ADR outside it.

**Direction** — **1 right / 0 wrong / 0 no-call.**
Scan 12:47Z PRE_NY, bias **+13 STRONGLY BULLISH**, `expected_direction +1`.
Post-scan move **+537.9** → **CORRECT**.
Running record: **11 right / 7 wrong / 6 no-call** (15 trading days, 24 deduped
scans).

**Levels** — 7 published, **3 touched, hit rate 0.43** (15-day mean 0.54).
The 4 untouched were all _(stretch)_ and all **below** price (−529 to −1454) on a
day that went up 848 points. Nothing was missed; the board simply pointed the
wrong way.

**Fuel** — budget **18.7**, actual extension **587.9**, error **+569.2**,
`UNDER-estimated`. Extension/budget **31.4x**; traversal 659.8 = **35.3x** budget.
This is the largest fuel error in the journal **by a factor of 4.2** (prior
maximum +136.4, 09-16/FOMC). H1 per-day mean: **+1.9 (n=14) → +39.7 (n=15)**.

---

## 2. What the levels actually did

Only three levels were tested. One did its job, one was right for a reason the
brief did not claim, and the headline level was wrong by 573 points.

| level | brief said | what happened | verdict |
|---|---|---|---|
| **30008.8** CALL WALL ●●●●● 0.98bn | *"desks must SELL as price rises into it, so **rallies stall. Take profit into it.** … it is ALSO the 45-day call wall — **the strongest ceiling on the board**"* | First touch 13:35; the only stall it produced was a **53.5pt** retest. Session high **+573.1 above it**; close **+486.8 above** | **The headline failure.** "Take profit into it" exited at 30008 on a day that closed 30495. The strongest ceiling on the board bought 53 points of friction against a 573-point run |
| **29994.0** London High (today) | *"the next session usually runs the stops above it"* | Stops were run at 13:35 and price never came back — 588 points of continuation beyond it | **Factually right, and the brief did not believe its own sentence.** It was tagged _(stretch)_, i.e. beyond the day's remaining budget, 31pts from spot |
| **29958.8** Options shelf 1.73bn | *"expect price to stall … take partials rather than push through"* | Held as **support** 450min, 2 re-touches, worst excursion **−21.3** | **The one good level.** A 21-point floor that was retested twice and never given up. (M6 caveat applies — it is below the close, so "support" is partly a property of the close, not the level) |

**Untouched:** MAX PAIN 29433.8 (−529), GAMMA FLIP 29307.6 (−656), PUT WALL
29258.8 (−704), STRUCTURAL PUT WALL 28508.8 (−1454). The last is explicitly a
*"mark it and leave it"* week/month level and its non-touch is correct behaviour,
not a miss (H6's known denominator pollution). The other three are the ordinary
consequence of a 19-point budget sizing a board that then had to describe a
958-point day: **`brief.py` sized the board off the budget, and the budget was
wrong by 31x, so the board had nothing above price except the level it told the
trader to sell into.**

**The grader inverted two of the three verdicts.** `review_day.py` reported the
call wall as *"broke DOWN through it — lost by 53.5pts"* and the London High as
*"broke DOWN through it — lost by 38.7pts"* on a day that closed 487 and 502
points **above** them respectively. Both were broken **upward** and then held as
support on a retest. This is M6 (verdict derived from `bars[-1]["close"]`), now
in a new and worse form: not just a mis-classification but **wording that reads
as the opposite of what happened**. Anyone reading the grade without the prices
would record this day as two failed levels breaking down.

---

## 3. What was wrong, and why

**The direction call was right and is not the story.** `+13` was correct, and it
was correct for the right reason: `structure +3` — *"price is ABOVE the entire
prior-week range — the weekly draw has flipped bullish; PWH 29704.2 is now
support"* — was the single largest correct component, and price never came within
250 points of PWH all day. What failed was everything the brief said about
**how far** and **how to trade it**.

**1. `fuel` produced a fade day on the biggest trend day in the record.**
`inputs.fuel`: ADR14 389.2, today_range 370.5, `adr_used_pct 95.2`,
`remaining_budget 18.7`, `EXHAUSTED`. The two `fuel` rows score **0** points by
design, so this never touched the bias — it drove the **prose and the strategy**:

> *"The day's range is set … Continuation into new highs/lows is the
> low-probability trade"* · *"➤ Sweeps of a high or low tend to genuinely fail —
> **this is your fade day**"* · `STRATEGY 1 — sweep -> failed re-break -> CISD
> reversal`.

The range then extended **587.9** further and 88% of the day's range was net
directional movement. Every sweep succeeded.

**The specific defect: the budget is ADR-anchored with no term for price already
being outside the prior day's range.** At scan, price was **+259.0 above PDH
29704.2** and above the entire prior-week range. The engine read "370 of 389
points already spent" as *the day is nearly over*; the same fact read as
*yesterday's range has already been left behind before the US open* points the
other way. See §4 — this is the one proposal with a clean 3-session base.

**2. `gamma −2` "top 20% of the wall band" was wrong for the second consecutive
session, in the same way.** (D21.) Price sat in the top 20% of 29258.8–30008.8,
and instead of poor risk/reward for longs it **left the band upward and never
returned** — identical wording to the 09-18 counter-instance. Record moves to
**3 for / 2 against**, and both counter-instances share a feature the row does not
test: price was already outside the prior day's range, so the band it was
measuring against was stale. n=2 on that mechanism — recorded, not proposed.

**3. `gamma +2` "week net GEX 9.693 → pinning likely" is not supported by 15 days
of data.** The 2nd-highest net GEX in the record produced the largest range
expansion in the record. Across all 15 complete days:

| net GEX (this week) | realised range / ADR |
|---|---|
| 16.106 (09-17) | **1.47** |
| 9.693 (09-21) | **2.46** |
| 9.223 (08-27) | 0.78 |
| 7.98 (08-28) | 0.97 |
| 7.697 (09-18) | 0.90 |
| 5.225 (08-25) | 0.97 |
| 3.407 / 3.111 / 1.81 / 0.557 / 0.067 | 0.93 / 1.38 / 1.27 / 0.82 / 1.18 |
| −0.058 / −1.461 / −2.103 / −6.295 | 1.33 / 0.77 / 0.82 / 1.37 |

**Pearson r = 0.269 (n=15); 0.052 with 09-21 removed.** Mean range ratio for
GEX ≥ 5 is 1.26 vs 1.10 below — but the **medians run the other way** (0.97 vs
1.18). There is no relationship, in either direction. This is the same shape as
H21 (VIX9D/VIX vs fuel error, r = 0.053, closed negative).

**4. `vol +1` "VIX9D/VIX 0.825 contango — calm, mean-reversion favoured".**
"Calm" on a 2.46x-ADR day. Adds a 13th point to H21's already-closed table and
does not change it: deep contango carries no information about range.

**5. `news −2` off 2 headlines out of 53.** `scored_high_confidence: 2`,
`needs_model_judgement: 51`. On the strongest and most correct call in the
record, the news module removed 2 points on the basis of 3.8% of the headlines it
had in hand — one of which ("Hawkish Federal Reserve **Steadied Stocks** and
Pulled Bond Yields Lower") is a *bullish* headline scored bearish on the keyword
"hawkish". That is D18, fifth trading day, ninth headline instance.

**6. `macro +3` off a 2-business-day-stale DFII10.** The largest single positive
component came from FRED data last published 2026-09-17, flagged by the brief's
own warning text. H18 again — and note it landed on the *right* side this time,
which is precisely why the register should not start treating H18 as harmless.
`macro` contributed **+6 of the +13**, of which +3 was stale and +2 was HY OAS,
the standing level-test that has now fired **16 of 16 days** (W2).

---

## 4. Change proposals

`track.py`: **threshold met (15 days)** — but its own caution applies, "day count
alone is not evidence". One proposal below clears the bar; everything else is an
observation, and the largest miss in the journal's history deliberately produces
**no tuning at all**.

### P-F (NEW, PROPOSED) — suppress the "range is set / fade day" framing when price is already outside the prior day's range

**Change (prose and strategy selection only — no score, no multiplier).** When
`price_at_scan` sits more than ~150pts outside the prior day's high/low, the
`EXHAUSTED` / `LOW_FUEL` block should print the budget as **unreliable in this
state** and must not emit *"the day's range is set"*, *"continuation is the
low-probability trade"*, or a fade-first strategy.

**Evidence — 3 unambiguous instances, all one direction:**

| day | price at scan vs prior day | budget | extension | error |
|---|---|---|---|---|
| 09-14 | **−187.6 below PDL** 29018.3 | 61.9 | 194.1 | **+79.4** |
| 09-17 | **+174.5 above PDH** 29251.3 | 0.0 | 40.0 | **+40.0** |
| 09-21 | **+259.0 above PDH** 29704.2 | 18.7 | 587.9 | **+569.2** |

Plus a marginal fourth, 08-24 (25pts below PDL at the first scan, back inside by
the PRE_NY scan): **+61.2**. Four for four positive, on both sides of the range.

**Control group — the 11 days where price was inside the prior day's range:**
3 of 11 positive, mean **−14.0**, median **−26.2**.

**Expected effect.** On roughly one day in four the brief stops asserting the
extremes are in and stops leading with a fade. It changes no score and breaks
nothing on the other 11 days, because it does not fire there.

**Explicitly NOT proposed: a budget multiplier for this state.** Fitting one to
+40 / +79 / +569 would fit the tail, not the level — the H1 lesson, and the
reason H1 itself is not being acted on (below).

### H22 (NEW, OPENED) — weekly net GEX does not predict realised range

Full table in §3.3. **n = 15 complete days, r = 0.269 → 0.052 without 09-21,
medians inverted.** The `gamma +2 "pinning likely"` row is scoring a *direction*
claim, which is fine; the problem is that its text drives *range* prose. The
candidate change is to strip the range language from it, exactly as H21 did for
term structure. **Held back deliberately this cycle** — P-F is also a prose change
to the same block, and shipping two at once makes neither of them measurable.
Status: **OPEN, one change at a time.**

### Not proposed, with reasons — this is the important half

- **No fuel multiplier (H1).** The per-day mean moved +1.9 → +39.7 on a single
  session. One point moving a 15-day mean by 38 points is the definition of a
  tail, and the register's own 09-18 conclusion ("no bias to correct, only
  variance") stands. Series: `+61.2 −11.6 −73.0 −86.4 −10.7 −26.2 −64.0 +57.3
  +44.3 +79.4 −81.3 +136.4 +40.0 −38.9 +569.2`.
- **No conviction cap at extremes (H3) — and today is the reason.** The register
  has asked since 09-15 for *"one max-conviction BULLISH call printed at a
  session high"* to separate over-commitment-at-extremes from a plain bearish
  skew. **This is it:** `+13` printed at 29963.2, ~92% up the range established
  at scan, 31pts under the session high, at the top of the wall band, on
  `EXHAUSTED` fuel — and it was **CORRECT by +537.9**. H3's three contaminating
  instances were all bearish-at-lows. The separator has arrived and it points at
  a **direction-specific** failure, not a generic extremes problem. A cap would
  have blunted the single best call in the record. **H3 should not be
  implemented; it should be re-scoped to the bearish branch.**
- **No event-day budget multiplier (H20).** H20 stays at **2 of 3** and its
  mechanism is now weaker, not stronger: `events_24h` was **empty**, `event_gate`
  null, *"No High/Medium US events in the next 24h"* — and this was the largest
  fuel error ever recorded. The two largest errors before today both had a
  scheduled print; the largest of all has an empty calendar. An event multiplier
  would not have caught it.
- **Rejected on test — "hot early pace predicts expansion".** The obvious
  inference from today (95.2% of ADR burned before the US open → a 2.46x day) does
  not survive the other nine PRE_NY days: `r(adr_used_pct, fuel error) = 0.238`
  (n=10), and **0.239 with 09-21 removed**. 09-16 burned only 59.3% and still
  under-read by +136.4. No signal. Recorded so it is not rediscovered.
- **P-E (call wall bimodal) — 8th instance, no new proposal.** Now **4 capped /
  4 sliced**, and the gap in the distribution has widened rather than filled:
  capped overshoots 3.6–11.9pts, slices 103 / 154 / 185 / **573**pts. Still
  **nothing between 12 and 103**. A discriminator fitted to 8 points split 4/4 is
  the noise-tuning the standing rule forbids.
- **M6 — 10th session, new failure mode, fix still blocked on a decision.** See
  §2. Reporting an upward break as *"broke DOWN through it — lost"* is a wording
  inversion on top of the known classification defect. M6's written fix (grade
  against direction of approach, reversal measured from the touch) covers it. Not
  re-proposed.
- **`SETTLE_TOL` is absolute and probably should not be (n=2, note only).**
  25.0pts is 5.6% of today's range and 5.0% of 09-18's. Near-identical *relative*
  excursions on the same call wall graded **"lost"** today and **"held"** on
  09-18. Likely subsumed by M6's fix; flagged so it is not lost if M6 ships
  narrowly.
- **Dead-weight audit (new observation, no proposal).** Across 16 trading days,
  four of the 26 published rows have contributed **zero points on every single
  day**: `NFCI` 0/16, `yield curve 10y–2y` 0/16, `VVIX` 1/16, `DXY` 1/16. They are
  not distorting the score — they are padding a table that advertises "26 checks"
  when 22 of them can ever move. Cosmetic, cheap to fix, not urgent.

### What I am watching next

1. The next day price opens the US session outside the prior day's range — the
   4th/5th instance for **P-F**, and whether the sign holds when the breakout is
   *downward* (only 09-14 so far).
2. Whether the 09-18/09-21 pair of `gamma −2` failures repeats a third time under
   the same "price already outside the prior-day range" condition (**D21**, n=2 on
   that mechanism).
3. One more max-conviction **bullish** call, at any location, to see whether the
   H3 re-scoping to the bearish branch holds up at n=2.
