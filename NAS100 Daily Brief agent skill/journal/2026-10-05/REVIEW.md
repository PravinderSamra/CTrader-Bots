# REVIEW — 2026-10-05 (graded 2026-10-06)

1 gradeable PRE_NY scan (12:47:11Z), `is_trading_day: true`, 0 test artefacts,
276 M5 bars (10-04 22:00Z → 10-05 20:55Z). Scan bar 178 of 276, price 30750.8.

## 1. Scoreboard

- Session **O 30856.4 / H 31137.3 (19:15Z) / L 30726.9 (09:40Z, pre-scan) /
  C 31110.3**. Range **410.4 = 0.86x** ADR14 476.9. Net **+253.9**, close
  position **93.4%** — a grind-up trend day that closed 27.0pts off its high.
  Hourly closes post-open: 30921.6 · 31015.0 · 31002.6 · 31015.2 · 31062.3 ·
  31086.4 · 31102.6 · 31110.3 (monotonic but one).
- Bias **+9 BULLISH → direction +1 CORRECT.** Post-scan move **+369.8**
  (direction +1) on traversal 400.7. Day net **+253.9**, also +1 — **post-scan
  and day-net direction AGREE today** (see §4; this is *not* a third instance of
  the 10-02 disagreement finding).
- Pre-scan H **30987.6 (01:40Z)** / L **30726.9 (09:40Z)**; post-scan H
  **31137.3 (19:15Z)** / L **30736.6 (12:50Z)**. The 149.7 of extension was
  **entirely upside**.
- Fuel: budget **216.2** vs extension **149.7** → **−66.5, 0.69x (under-used)**
  (`review_day`: "about right"). Traversal/budget **1.85x**. Price traveled
  **+386.5 above the scan price** against a 216.2 budget.
- VXN-implied daily range **410.7** vs realised range **410.4 — 0.3pts.** The
  straddle EM band **30533 .. 30968** was breached from 14:20Z and the close
  (31110.3) finished **142.3 outside** it.
- Hit rate **0.56 published (10/18)**; **7 distinct touch bars** (178, 179, 182,
  185, 186, 189, 224) → distinct rate **0.39**, inflation **1.43x**. All 8
  untouched rows were below price (−24 to −343) on a one-way up day.
- Direction record, **09-24 excluded** per *D23 CORRECTED*: PRE_NY
  **10 right / 5 wrong / 5 no-call over 20 days**; all sessions
  **15 / 9 / 9**. (`track.py` raw, no quarantine: **16 / 9 / 9**.)
- H1: n=25 days, per-day mean **+21.7**; **−1.08** excluding the 09-21 outlier
  (n=24). MAE **85.2** against mean budget **107.6** = **79%**.

## 2. What the levels actually did

**Touched (10 of 18).** Verdicts are `settled_read`; the understatement column
is §3's M6 instance.

| level | brief said | what happened | verdict |
|---|---|---|---|
| **31037.1** PDH + PWH + NY High _(stretch)_ | *"the biggest pile of stops above us. Sweep it, wait for a lower high on the 1m, then CISD = short"* | swept 16:40Z, then **held above for 220min** and closed **+73.2 above**; max give-back after the touch **35.3** | **the sweep did not fail. The one named trade in the document lost.** The level then worked as support — a role the prose does not offer |
| **30987.6** Asia High (today) _(stretch)_ | *"the next session usually runs the stops above it"* | ran it at 13:45Z, acted as **support** 280min | right, and reached despite being flagged beyond the budget |
| **30908.1** Options shelf 0.37bn | *"expect price to stall. Good place to take partials rather than push through"* | **sliced +229.2**, closed +202.2 above | wrong — and price had already been **above it in 52 of 178 pre-scan bars** |
| **30865.7** London High (today) | *"runs the stops above it"* | **sliced +271.6** | right in direction, no stall |
| **30858.1 CALL WALL ●●●●● 1.34bn** + shelf | *"Heaviest ceiling this week — desks must SELL as price rises into it, so rallies stall. Take profit into it… the strongest ceiling on the board"* | **crossed inside the single 13:30Z bar (30825.6 → 30925.4)**, ran **+279.2**, closed **+252.2 above** | **the strongest claim on the board, falsified in five minutes.** P-E instance 11. Also already exceeded pre-scan in **73 of 178 bars**, last at 08:25Z |
| **30809.0** PD close + shelf 0.22bn | *"expect price to stall"*, and §3's named **upside brake** at 30808.1 | **sliced +328.3** (0.69x ADR) | wrong; largest H23 slice on record |
| **30790.0** London High (prev-day) | *"runs the stops above it"* | broke up, acted as **support** 455min | right |
| **30778.8** PD mid | *"a target to aim AT, not a trigger"* | reclaimed 12:55Z, **support 455min**, closed **+331.5 above** | right as a magnet; fatal to the `structure −1` row (§3) |
| **30770.2** Asia Low (today) | *"the next session usually runs the stops **below** it"* — on a level **19.4 ABOVE** the scan price | acted as **support** for 475min | **wrong-sided prose, P-G instance #13** |
| **30744.2** NY Low (prev-day) | *"runs the stops below it"* | support, worst −7.6 | right |

**Untouched (8 of 18), all below.** GAMMA FLIP 30631.4 (−119, closest approach
105.2 — no H4 instance) · London Low prev-day · Asia High prev-day 30689.8
(−61.0, *"usually runs the stops above it"* on a level price was already above —
second P-G row) · Equal lows ×2 30727.2 (−24, *"prime S1 sweep trigger"*, never
reached) · Asia Low prev-day · PDL · PUT WALL 30458.1 (−293) · MAX PAIN 30408.1
(−343 = **0.72x ADR, 6th consecutive distance miss**).

**The level that actually marked the day is not on the board.** The session high
**31137.3** and the close **31110.3** sit **+29.2 / +2.2** from **31108.1**,
published only in the research-only *"Other gamma concentrations"* table
(0.45bn, **34,453 contracts — the largest contract count on the page**) with the
note *"dealers are LONG gamma here… expect a stall — rallies lose momentum into
it"*. That note was the best forecast in the document. It is **+357** from the
scan, i.e. **inside** `keep()`'s 378.4 cap, yet the board's top row stopped at
31037.1 — **100.2pts below the high**, and the last 2h15 of the session traded
above every marked level. Second instance of the 09-23 *"the high was set by
contract count, not dollar gamma"* observation.

## 3. What was wrong, and why

**The direction call was right and the strategy block told the trader to trade
against it.** `+9 BULLISH` came from gamma +4 · vol +3 · breadth +3 · macro +2 ·
structure −2 · news −1. The same gamma rows that produced the +4 also selected
**STRATEGY 1** (*"Positive gamma above the flip: dealers fade extensions, so
sweeps genuinely fail… This is your fade day"*), and `expiry_shape`
**SPIKE_THEN_REVERT** (0-2DTE −0.264 inside 45d +3.127) added *"Fade the
extremes… don't hold for continuation"*. The fuel block's MODERATE text added
*"don't plan on a third leg"*. The day produced eight consecutive rising hourly
closes, finished 93.4% up its range, and the only concrete setup the brief named
— CISD short off the PDH sweep — lost by 73.2 at the close with 35.3 of
adverse travel and no stated invalidation. **One document, a correct +9 long
call and three separate instructions to fade.** n=2 on SPIKE_THEN_REVERT
(09-30, 10-05) — below threshold, nothing proposed, but the conflict is now
recorded on the *above*-flip / MODERATE cell as well as the registered
LOW_FUEL/below-flip cell.

**`structure −1` is the pre-registered third instance of the no-tolerance-band
defect, and it fired at 28.0pts.** The row read *"price below PD mid 30778.8"*;
30750.8 − 30778.8 = **−28.0**, inside the 30pt window the 09-30 entry named as
the test. Price reclaimed PD mid **eight minutes after the scan** and held above
it for **455 of 490 post-scan minutes**, closing **+331.5 above**. With 09-16
(+27.9, row +1, PD mid lost) and 09-29 (+11.0, row +1, price below for 6.75h),
**3 of 3 inside-30pt firings were wrong about the side.** Threshold met as
specified.

**`news −1` is three sign-flipped votes — D18, 6th trading day.** Reproduced
from `news_scorer.py` on today's own headlines:

```
'Traders slash bets on October Fed rate hike'                       rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
'Asian shares are higher as easing worries over inflation reduce
 odds for a rate hike'                                              rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
'S&P 500, Nasdaq, Dow End Week Higher As Weak Jobs Report Cools
 Rate Hike Bets'                                                    rule=hawkish dir=-1 conf=HIGH flags=[] weighted=-1.8
```

All three are dovish or outright bullish in their own words. **One of them
contains no market-direction word at all** (*"Traders slash bets on…"*), so
D18's documented *first-match-wins* mechanism cannot explain it: the `hawkish`
regex (`news_scorer.py:71`) matches the noun phrase **"rate hike"** with no
reading of the verb acting on it — *slash bets on*, *cools … bets*, *reduce odds
for* all score −1 at HIGH confidence with no flags. That is a **missing-negation
defect**, a sub-shape D18 has not previously recorded. Damage today is
conviction only: correcting the three leaves the label BULLISH and the call
CORRECT.

**The board was converted from a scan price that hid the 14.75 hours of its
own session that preceded it.** Pre-scan H 30987.6 / L 30726.9 means **8 of the
18 published rows had
already been traded through today**, under the banner *"New trading day …
everything below is fresh"*: the CALL WALL (16 touches, price above it in **73**
of 178 pre-scan bars, last 08:25Z), the 0.37bn shelf (23 touches, 52 bars
above), London High today, PD close/shelf (42 touches), London High prev-day
(45), PD mid (33), Asia Low today (32), Asia High today (the pre-scan high
itself, published at +237 and marked *(stretch)*). **Session-context field, 7th
session, and much the largest instance in the series** — previous ones were one
or two rows. This also contaminates today's P-E instance: the "strongest ceiling
on the board" had already failed once, overnight, before the brief asserted it.

**The grader understated 6 of 10 touched levels and inverted 3 of 6 "held"
verdicts — M6, session 18.** `worst_excursion` is measured only after the final
side change:

| level | `review_day` verdict | reported | true (first touch → close) | ratio |
|---|---|---|---|---|
| 31037.1 | *"held as support 220min, worst −3.8"* | −3.8 | **−35.3** | **9.29x — breaches SETTLE_TOL, INVERTED** |
| 30987.6 | *"held as support 280min, worst −20.0"* | −20.0 | **−104.7** | **5.23x — INVERTED** |
| 30770.2 | *"held as support 475min, worst −14.1"* | −14.1 | **−33.6** | **2.38x — INVERTED** |
| 30778.8 | *"held as support, worst −1.5"* | −1.5 | −22.7 | 15.13x (verdict survives, 25pt tol) |
| 30790.0 | *"held as support, worst −12.7"* | −12.7 | −19.7 | 1.55x (survives) |
| 4 × "lost" rows | — | exact | exact | 1.00x |

**Plus a wording inversion on all four "lost" rows:** 30908.1, 30865.7, 30858.1
and 30809.0 each print *"broke **DOWN** through it — lost by Npts"* with
`settled_side: above`, on a day price closed **+202 to +328 ABOVE** them. Read
cold, `review_day` says the call wall failed downward. It failed upward by
279.2.

**What the stale rows did today, for the record.** The macro block's two stale
FRED rows pushed the score **up** this time (DFII10 **+3** on a 2026-10-01
observation, DGS10 **+1** on a 09-30→10-01 move) against a live `rates` row of
0. Zeroing DFII10 gives **+6 — still BULLISH, still CORRECT: no damage.** The
DFII10 textual sub-defect did **not** fire for the first time in four sessions
(today is Monday, so *"this is last week's reading"* is true of a 10-01
observation). **HY OAS (−2) again renders no observation date — third
consecutive session**, and the age gate still cannot measure it.

## 4. Change proposals

**PROPOSED — one, and it is pre-registered.** Give the PD-mid `structure` row a
deadband: score **0** when `|price_at_scan − PD mid| < 30pts` (or `0.06 ×
ADR14`, which is 28.6 today — either form passes the test). Evidence is the test
the 09-30 entry specified, now complete at **3 of 3**: 09-16 (+27.9), 09-29
(+11.0), 10-05 (−28.0) — every inside-30pt firing was wrong about which side
price would hold, and today's was wrong 8 minutes after the scan and stayed
wrong for 455 minutes. **Expected effect: no label and no direction call changes
anywhere in the record** — 09-16 +4→+3 stays MILDLY BULLISH (still WRONG),
09-29 +6→+5 stays MILDLY BULLISH (still CORRECT), 10-05 +9→+10 stays BULLISH
(still CORRECT). It removes a row that is a coin-flip by construction inside its
own measurement error.

**Strengthened, not re-proposed** (all already PROPOSED; today adds an
instance): **M6** whole-window excursion (session 18, 3 inverted "held" verdicts
plus a 4-row wording inversion) · **session-context `tested_today`** (7th
session, 8 of 18 rows) · **H23** drop or base-rate the named brake (**6th
instance: 5 sliced / 1 capped**; today's slice +328.3 = 0.69x ADR is the
largest, and unlike the earlier ones the named strike *was* on the board, 0.9pts
away) · **P-B(b)** `merge_tol ≥ TOUCH_TOL` (11th session: merge_tol 3.82 vs
TOUCH_TOL 8.0; 30865.7/30858.1 at 7.6pts both graded touched at bar 186;
inflation 1.43x) · **dead-weight audit** (NFCI **0/25**, yield curve **0/25**,
WALCL/RRP **0 of the last 20**) · **P5** persist and grade the secondary gamma
table — today it held the strike that marked both the high and the close.

**The D23 measurement the 10-02 review asked for is done, and the answer is
negative.** Gap between the board offset and section 7's offset, minus the CFD
move from the 11:59Z feed time to the scan (11:55Z M5 bar open as the proxy):

| day | board | §7 | gap | CFD move 11:59Z→scan | residual |
|---|---|---|---|---|---|
| 09-29 | +18.2 | +168.3 | +150.1 | −40.4 | **+190.5** |
| 09-30 | +37.7 | −20.3 | −58.0 | +143.3 | **−201.3** |
| 10-01 | +36.0 | +194.0 | +158.0 | −45.8 | **+203.8** |
| 10-02 | −3.3 | +168.7 | +172.0 | +179.3 | −7.3 |
| **10-05** | **+8.1** | **−13.5** | **−21.6** | **−24.5** | **+2.9** |

The intervening move explains the gap on **2 of 5** days (10-02, which is the
day the 10-02 entry generalised from, and today). On the other three the gap and
the move have **opposite signs** and a residual of **≈ ±200pts** remains. So the
*"mostly the intervening CFD move, therefore cosmetic"* reading does **not**
generalise, and the 10-01 framing of a latent error survives. **Nothing
proposed:** keep section 7 research-only, do not ship *"derive both grids from
one conversion"*, and print the feed-time delta **and** the residual before any
promotion. The ±200 magnitude is noted as a lead toward D12's ~200pt
greeks disagreement — a lead, not a claim. My 11:59Z proxy carries ~10pts of
noise, which does not touch a 200pt signal.

**Observed, nothing proposed.** **D18** 6th trading day / 12th headline
instance, still blocked by H19's unrun baseline — but the missing-negation
sub-shape is new and should be recorded so the eventual fix covers it ·
**P-E** instance 11, census **4 capped / 7 sliced**, slice mode now
103 / 117.5 / 154 / 185 / 205 / **279.2** / 573 with the **12–103 band still
empty**, and today's instance flagged as pre-scan-contaminated · **H19**
coverage **12.7%** (7 of 55 relevant, 136 headlines) — the best in the recent
series after 0.0 / 1.8 / 3.8% · **H8** observation 3 of 10 (close **outside**
the band by 142.3; the register's claim that EM beats the VXN range is untested
and today the VXN range won by 0.3pts — different objects, n=1, no claim) ·
**H22** n=4 (0.463 $bn/1% → *"pinning likely"* → 0.86x ADR on a trend day
closing at 93.4%; still no ordering) · **H1** n=25, 5th consecutive entry
recommending the multiplier branch be closed **SETTLED-NEGATIVE** (mean −1.08
excluding one outlier; MAE 85.2 is 79% of the mean budget — the error is noise,
not bias) · **P-F** inside-range control, 21st day · **D21** did not fire (band
30458.1–30858.1 = 400pts, price 73% up, no −2) and its silence was right ·
**H10** did not fire (price inside the prior-week range) · **H4 / H20 / D24 /
P3** no instance (flip 105.2 away at the closest; one Medium event ahead of the
scan; nothing fired pre-scan; no `structural` row published) · **max pain** 6th
distance miss · **post-scan vs day-net direction AGREED today**, so the 10-02
flag stays at **n=2** — explicitly not the third instance it pre-registered.

**No new external data point is warranted.** The one gap that cost today is
internal and free: the board cannot see its own session before the scan
(session-context) and cannot see the strike that marked the close (P5). Both are
already proposed and both are in the pipeline's own data.

**Journal hygiene.** No fabricated or backfilled entries; no `prediction` block
touched. 09-24 quarantined by hand per *D23 CORRECTED* — **sixth consecutive
review to do so**; the proposed `quarantine` schema field is reaffirmed again.
09-25 still cited from the 09-28 entry. No review file back-dated for 09-24 or
09-25. The 09-23 pre-registered D21 test stays void. `track.py` prints
*"threshold met, read the evidence before proposing"* rather than
`actionable: YES/NO`, so the 3-session rule was applied by hand per item above.
