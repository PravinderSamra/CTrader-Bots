# REVIEW — 2026-09-23 (Wed) — max conviction, wrong way, and nothing on the register would have caught it

Graded 2026-09-24 from `review_day.py --json` (resolved to 2026-09-23) and
`track.py`. **1 gradeable scan** (12:47:46Z PRE_NY). **0 test artefacts.**
`is_trading_day: true`; no `is_trading_day: false` scan exists on this date, so
nothing was excluded on that ground. The 2026-09-24 scan is **excluded** from
every statistic — `track.py` holds it back at 179 bars.

**Journal integrity: clean.** `1247-preny.json` is in commit `41c143cb`, authored
`2026-09-23T12:47:50Z` — four seconds after its own `scan_utc: 12:47:46Z`. Not
backfilled, not fabricated. `outcome` is still `null`; every actual figure below
comes from `review_day.py`, not from the journal's own claims. No `prediction`
block was touched.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 30729.9 / 30820.3 / **30369.5** / **30497.6** |
| Range / net | **450.8** / **−232.3** (net = 52% of range) |
| ADR14 | 424.9 → range **1.06x ADR** · VXN-implied 390 → **1.16x** |
| Bars | 276 |

**Direction** — **0 right / 1 wrong / 0 no-call.**
Bias **+13 STRONGLY BULLISH**, `expected_direction +1`, post-scan move
**−184.5** → **WRONG**. Running record: **12 right / 8 wrong / 6 no-call**
(17 trading days, 26 deduped scans).

**Fuel** — budget **242.4**, extension **268.3**, error **+25.9**,
`about right` (1.11x). Traversal 367.9 = **1.52x** budget. H1 per-day mean
**+35.8 (n=16) → +35.2 (n=17)**; still entirely tail-driven by 09-21.

**Levels** — 21 published, 12 touched, hit rate **0.57** (17-day mean 0.54).
Clustered at 25pts the 21 levels occupy **11 distinct zones, 5 touched → 0.45**.
Dropping the 4 levels that sat **650–1900pts** away against a 242pt budget:
**7 zones, 5 touched → 0.71**.

**Expected-move band** 30521 .. 30845 (close-to-close): close 30497.6, **outside
by 23.4 low**. Stated as 2-in-3; one miss is not a finding, recorded for the
standing series.

**News coverage (standing record):** counted **1** (0 bull / 1 bear, 100%
bearish), uncounted **48** — coverage **2.0%** — score **0**.

---

## 2. What the levels actually did

| level | brief said | what happened | verdict |
|---|---|---|---|
| **30732.9** shelf 0.63bn | *"expect price to stall… take partials"*, and named as the UPSIDE friction stall | Held as resistance **490min**, worst **+4.5**, 2 re-touches | **Best call on the page.** The upside-friction sentence named the exact price the post-scan high failed at |
| **30632.9** shelf 0.69bn | *"expect price to stall… take partials"* | Held as resistance 435min, worst **+12.9** | Right |
| **30532.9** shelf 0.39bn | *"expect price to stall… take partials"* | Held as resistance 335min, worst **+10.3** | Right |
| **30394.0** PDL + London Low ⭐ _(stretch)_ | *"Sweep it, wait for a higher low on the 1m, then **CISD = long**"* | Swept by **13.7**, held as support 235min, 4 re-touches, **+159.4** travel up | **The only complete trade on the board, and the board told the reader to skip it.** 289pts away against a 242pt budget → marked _(stretch)_, "partials-only" |
| **30728.1** PD close | *"price often comes back to fill a gap from here"* | Returned to it (worst +9.3), then held as resistance 450min | Factually right, direction-neutral by construction |
| **30642.2 / 30637.8 / 30632.9 / 30611.5 / 30591.0 / 30572.3** | *"prime S1 sweep trigger"* ×2 · *"stops get run"* ×2 · *"a target to aim AT"* | **All six first touched 13:35–13:50** in one 70pt slide; all "chopped around it"; all settled below | **Six published levels, one observation.** Two held tight (+8.0 / +12.9), two mid (+23.0 / +23.9), two lost (+34.3 / +39.9). The "S1 sweep trigger" framing = long the equal lows, into a 313pt decline |
| **30709.7** Asia Low (today) | *"the next session usually **runs the stops below it**"* | Price was **already 26.7 below it at scan**. Chopped, settled below | **Note was spent before publication** — see §4 P-G |
| **30572.3** London High (prev-day) | *"the next session usually **runs the stops above it**"* | Level sat **110.7pts BELOW price at scan**. Acted as resistance on the way down | **Same defect, larger.** A stop-run instruction pointing at an event three sessions old |
| **30491.0** NY Low + Asia Low (prev-day) ⭐ | *"the next session usually runs the stops below it"* | Sliced, 121.5pts down after, no settled read | **The ⭐ earned nothing.** Two reasons to respect it produced no reaction |

**Untouched post-scan:** CALL WALL 30832.9 (+150), Asia High (+137), PDH cluster
(+100/+105), equal highs (+79) — the whole upper board, on a bullish call.
PUT WALL (−650), GAMMA FLIP (−759), MAX PAIN (−950), STRUCTURAL PUT WALL
(−1900). The call wall was **never tested**, so P-E gains no instance today and
stays 4 capped / 5 sliced.

**Options shelves are now 7-for-7 across 4 sessions** (09-18, 09-21, 09-22,
09-23) with worst excursions **−5.0, −21.3, −9.1, −2.3, +4.5, +12.9, +10.3** —
every one inside 22pts. Over the same window the call wall, which the board
prints first and marks ●●●●●, ran through by 103 / 154 / 185 / 573 / 205. §4.

**Regime prose was wrong.** `COHERENT_LONG`, net GEX 5.481, *"Expect a tight,
pinned range… keep targets modest; breakouts mostly fail"* → range 1.06x ADR,
1.16x VXN-implied, and a 232pt directional close. Another instance for the
standing negative result on "pinned range" (HYPOTHESES.md §*Negative result —
"pinned range" does NOT predict chop*) and for H22.

---

## 3. What was wrong, and why

`+13` decomposes as **macro +6 · structure +5 · breadth +3 · gamma +2 · vol 0 ·
rates −3**. To reach a bearish call it needed **−14**. Tracing it:

**3a. The whole bullish case was yesterday's tape, or older.**
Of the +19 bullish points: `macro +6` is entirely FRED, and its two largest rows
(`DFII10 +3`, `DGS10 +1`) carry their own staleness warning in their own `why`
string — *"FRED has not published since 2026-09-21 (2 business days ago)"*.
`breadth +3` is the prior cash session's mega-cap closes plus the NDX/ES row
(§3b). `structure +3` is a prior-week comparison three sessions stale (§3c).
Zeroing the two self-declared-stale FRED rows gives **+9** — still strongly
bullish. **This is the 8th H18/P1 instance and the first where the stale row
added conviction to a WRONG call** (sequence `09-10 0, 09-10 0, 09-11 −3, 09-11
−3, 09-14 −3, 09-14 −3, 09-15 −3, 09-16 0, 09-17 −3, 09-18 −3, 09-21 +3,
09-22 −3, 09-23 +3`).

**3b. `breadth +1` compared two different days. This one is mechanical.**
The row printed *"NDX +3.67% vs ES −0.10% — tech leading, genuine risk appetite"*.
Reconciled against the journal's own close series, **the actual prior-session NDX
move was +0.76%** (30728.1 / 30495.6). +3.67% matches the **09-18 → 09-22**
two-session move (+3.57%, within the usual CFD/cash offset noise). I checked all
10 PRE_NY-equivalent scans where both closes are recoverable: 8 reconcile to the
prior session within ±0.15pp; **09-23 is off by +2.91pp and 09-24 by +0.71pp with
a sign flip** (reported −0.04%, actual −0.75%).

Separately, and certain from the code rather than inferred: the two legs cannot
cover the same window. `bias_engine.py:186-192` reads
`macro["index"]["ndx_daily"]` and `breadth_proxy["es_sp500"]`, both from
`macro_probe.yahoo_series` (`macro_probe.py:207, 224`) — `^NDX` with the default
`range=10d`, `ES=F` with `range=5d`. `^NDX` does not print pre-market, so its
`chg_pct` is **yesterday's cash session**; `ES=F` trades overnight, so its
`chg_pct` is **this morning's globex move**. On 09-23 the row therefore compared
yesterday's Nasdaq gain against this morning's flat S&P and concluded "genuine
risk appetite" 42 minutes before the index began a 232pt slide. Opened as **D22**.

**Honest limit: fixing D22 would not have changed the call.** Recomputing both
legs on the overnight window (NQ −0.15% vs ES −0.10%) gives *"in line"*, score
**0** instead of +1 → **+12, still STRONGLY BULLISH**. D22 is an integrity
finding, not an accuracy one — but its blast radius is wide: the same
`yahoo_series` `prev = closes[-2]` derivation feeds `rates −3` (US10y, DXY) and
`breadth +2` (the four mega-caps), i.e. **6 of 24 rows and ±8 points today**.
Those were not shown to be wrong and I am not claiming they were; they need the
same audit.

**3c. `structure +3` has no distance term and no reset.**
*"price is ABOVE the entire prior-week range (28757.3-29704.2)"* has now paid
**+3 on four consecutive sessions off the identical range**, while price walked
from **+259 above PWH (09-21) → +788 (09-22) → +979 (09-23) → +490 (09-24)**.
A reclaim that happened three sessions and 979 points ago is scored exactly like
one that happened this morning. Graded record of the `+3` branch: **09-21 ✓,
09-22 ✓, 09-23 ✗ — and the failure is the furthest firing.** With the register's
`−3` branch at 0-for-4, the prior-week row is **2-for-7** as a directional
predictor while carrying the largest single weight in the structure block.
Appended to H10.

**3d. `gamma −2` was the only row pointing at the outcome — and D21 says that
means nothing, for a reason I can now name.**
The row fires on *percent of the wall band*, with **no normalisation for band
width**. Across its 15 firings the band spans **100 → 800pts**, so "top 20%"
is a trigger window of **20pts to 160pts** — 4.7% to 37% of ADR14. The same −2
is awarded for "price is 17pts under the call wall" (09-18) and "price is 150pts
under it" (09-23). **The 9 graded firings D21 has been tallying are a mixture of
two physically different conditions**, which is why the tally reads as noise.
Re-cut by absolute distance to the call wall it inverts cleanly — see §4.

**3e. Candidate tested and rejected, so it does not become the story.**
The tempting post-hoc narrative is "price was already 45pts below the prior
close and the structure block scored it +1 for being above PD mid". I tested
`sign(price_at_scan − prior close)` against realised direction on the 9
recoverable PRE_NY scans: **5 right, 4 wrong** (✓ 09-15, 09-17, 09-18, 09-21,
09-23 · ✗ 09-11, 09-14, 09-16, 09-22). A coin flip. **Not proposed, and the
09-23 story it would have told is retired.**

**3f. The uncomfortable summary.** Every proposal on the register, plus both new
ones below, applied together, moves `+13` to roughly `+9`. **Nothing available
would have turned this call.** The engine had no bearish information beyond
`rates −3` and one mis-specified `gamma −2`. Saying so is the finding; inventing
a fix that reaches −14 would be fitting one day.

---

## 4. Change proposals

`track.py`: **17 trading days ≥ 3 — threshold met** for the 3-day hypotheses
(H1/H2/H3/H5/H7), with its own caution that "day count alone is not evidence".
H4/H6 need 5, H8 needs 10. **One new proposal, one new defect held below
threshold, one new sub-proposal folded into an existing item.** No scoring change
is proposed and I have edited no scoring file.

### P-G (NEW, PROPOSED) — session-extreme prose is selected by level kind, not by which side price is on

**Change — prose only, no score, no board membership.** Choose the note for
`Asia/London/NY High|Low` from the **sign of (level − price_at_scan)**, with a
±25pt "price is sitting on it" band. A session high **below** current price has
already had its stops run; it is support-or-nothing, not a stop-run target.

**Evidence — 9 instances across 5 of 11 PRE_NY scans**, from the journals'
`prediction.levels` and `price_at_scan`:

| day | level | side | offset | published note |
|---|---|---|---|---|
| 09-15 | London High (prev-day) | below price | **−145.0** | *"stops run above it"* |
| **09-23** | London High (prev-day) | below price | **−110.7** | *"stops run above it"* |
| 09-18 | London High (prev-day) + PD close | below price | **−70.4** | *"stops run above it"* |
| **09-23** | Equal lows ×2 + Asia High (prev-day) | below price | −40.8 | *"stops run above it"* |
| 09-15 | Asia High (prev-day) + Equal lows ×2 | below price | −29.6 | *"stops run above it"* |
| **09-23** | Asia Low (today) | above price | +26.7 | *"stops run below it"* |
| 09-11 | Asia Low (prev-day) | above price | +2.9 | *"stops run below it"* |
| 09-16 | Asia High (today) | below price | −2.3 | *"stops run above it"* |
| 09-18 | PDH + NY High (prev-day) | below price | −1.5 | *"stops run above it"* |

Four are inside 3pts and any tolerance catches them. **Three are 70–145pts** —
the board handing the reader a directional instruction for an event that had
already happened, on the level it also marked ⭐.

**Expected effect.** No score moves, no level is added or dropped, hit rate is
unchanged. On ~45% of scans the board stops issuing a spent instruction. This is
adjacent to but distinct from the standing item *"the board has no field for
'price already tested this today'"* — that one is about today's intraday tests;
this is about the side price occupies at scan time, which the generator already
knows exactly.

### P-E(b) (NEW, folded into P-E — not a competing proposal) — the shelves are what should replace the wall's top line

P-E already proposes stripping the unconditional *"rallies stall. Take profit
into it"* from the call wall. It has never said what the reader should mark
instead. **The options shelves have, and the asymmetry is now large.**

| family | sessions | instances | worst penetration |
|---|---|---|---|
| Options shelf | 09-18, 09-21, 09-22, 09-23 | **7** | −5.0, −21.3, −9.1, −2.3, +4.5, +12.9, +10.3 → **all inside 22pts** |
| CALL WALL ●●●●● | 08-27, 08-28, 09-08, 09-11, 09-14, 09-18, 09-22 | 9 (P-E) | capped 3.6–11.9 **or** sliced 103 / 154 / 185 / 205 / 573 |

**Change — board ordering and emphasis only.** Give the shelf line the strength
marker and the "take partials" instruction, and demote the call wall's line to
P-E's bimodal wording. **Expected effect:** the level a reader marks first
changes from one with a 103–573pt failure mode to a family with a 22pt worst case
over 7 instances.

**Caveats stated up front.** (i) M6 applies — "held as resistance/support" is
partly a property of where the session closed; the *worst-excursion* figures are
not, and those are what the table uses. (ii) 09-18's shelf sat 9.6pts from the
call wall and that review called it redundant — treat that instance as clustered,
leaving **6 independent shelf holds over 4 sessions**, still clear of the bar.
(iii) This is prose and ordering. **No change to `gex_levels.py` scoring is
proposed.**

### D22 (NEW, OPENED — BELOW THRESHOLD, NOTHING PROPOSED) — `yahoo_series` does not guarantee a prior-session `prev_close`, and the NDX/ES legs cover different windows

Two parts, deliberately separated by how well each is evidenced.

**(a) Window mismatch — certain from the code, present on every PRE_NY scan.**
`^NDX` `chg_pct` is yesterday's cash session; `ES=F` `chg_pct` is this morning's
overnight. Mechanism is not in doubt (§3b). **Still not proposed this cycle:**
P-G is already a prose change shipping into the same board, and the register's
own "one change at a time" rule from 09-21 applies. It is also worth nothing on
accuracy — recomputed both-overnight, 09-23 goes +13 → +12, same label.

**(b) Two-session skip on the NDX leg — n=2, OBSERVING, no proposal.**
09-23 (+3.67% vs actual +0.76%) and 09-24 (−0.04% vs actual −0.75%). The
suspected mechanism is `macro_probe.py:55`:

```python
closes = [c for c in q["close"] if c is not None]
...
prev = closes[-2] if len(closes) > 1 else last
```

Stripping nulls collapses date gaps, so `closes[-2]` is not guaranteed to be the
**prior session** — the same class of bug as the `chartPreviousClose` error the
code's own comment at lines 59-63 records fixing. **Two sessions is below the
three-session bar and I am proposing nothing.** The check that settles it in one
call, and which I have not run because it needs a live fetch: print the dated
closes `yahoo_series("^NDX")` returns and compare the last four against the
journal's own PD-close series. A missing date confirms it; no missing date
refutes it and (b) closes negative.

### Appended to existing items, nothing proposed

- **H10** — `+3` branch now **2-for-3**, and the new content is the missing
  distance term: four consecutive firings off one range at +259 / +788 / +979 /
  +490 above PWH. A decay or a re-arm condition is the obvious candidate and
  **is not proposed** — the failure sits at the largest distance on n=3, and
  fitting a decay to that is fitting one point. Falsification: the next `+3`
  firing at >700pts above PWH.
- **D21** — 9th graded firing; today the row was the **only** bearish row on a
  wrong bullish call. The new content is the width defect (§3d) and the cut it
  implies. Re-cut by **absolute distance to the call wall**, the 8 graded
  firings invert: **within 50pts** (08-27 +7, 09-18 +17, 09-17 +26, 09-08 +30,
  09-22 +31, 09-21 +46) → **5 up / 1 down**, i.e. "poor risk/reward for longs"
  wrong 5 of 6; **beyond 50pts** (08-28 +71, 09-23 +150) → **2 down / 0 up**,
  right 2 of 2. **Not proposed.** n=8, and I found the cut after looking at the
  outcomes — the exact procedure the standing rule forbids acting on. It is
  logged as a **pre-registered test**: 09-24 fired TOP at **+30 (within 50)**, so
  the cut predicts an **UP** day on 09-24. That is the first out-of-sample point
  and it grades itself tomorrow, against a prediction written here and not into
  any `prediction` block.
- **H18 / P1** — 8th DFII10 instance; **first time the stale row added
  conviction to a WRONG call** (+3 of a +13). P1 already covers it.
- **P-B(b)** — 21 levels → 11 zones; 6 published levels collapsed into one 70pt
  band first touched inside 15 minutes. Published 0.57 / zone 0.45.
- **P3 / H6** — structural put wall published on a **12th trading day**, 0
  touches, today at **−1900 = 4.47x ADR14**. Last four sessions: −1454, −1469,
  −1900, −1720. It cannot be touched by construction.
- **H1** — +25.9 today; per-day mean +35.8 → **+35.2 (n=17)**. Sign is positive
  in 8 of 17 days. **No multiplier**, for the 09-21 reason unchanged.
- **H22 / "pinned range does not predict chop"** — another instance: strongest
  long-gamma shape on record produced 1.06x ADR and a 232pt directional close.
- **`events`** — scored 0 again; the dead-weight audit stands.
- **News sampling bias** — 09-23: counted 1, uncounted 48, coverage **2.0%**,
  the lowest in the record, sign 100% bearish, score 0.

### What would make the open items actionable

1. **D22(b):** one `yahoo_series("^NDX")` fetch with dated closes. Free,
   reliable, settles it immediately. No new data source needed.
2. **D21's distance cut:** 09-24 (pre-registered above), then two more firings
   in each bucket.
3. **H10:** a `+3` firing at >700pts above PWH, to see whether 09-23 was the
   distance or the day.
4. **P-E:** one more call-wall test — it was untouched today, so nine instances
   still stand.

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
