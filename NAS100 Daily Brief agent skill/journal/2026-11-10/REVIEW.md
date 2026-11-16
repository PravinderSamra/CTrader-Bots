# REVIEW — 2026-11-10 (graded 2026-11-11)

One scan: `1246-london.json`, 12:46:40Z, `LONDON`, `is_trading_day: true`,
`test_artefacts: 0`, `outcome: null`. No `is_trading_day: false` scan in the
window, so nothing was excluded on that ground.

## 1. Scoreboard

| | |
|---|---|
| Session O/H/L/C | **27894.3 / 27995.9 / 27408.5 / 27726.5** (276 M5 bars) |
| Range / net | **587.4** (0.685x ADR14 857.6) / **−167.8** |
| High / low timing | high 27995.9 at **00:05Z (Asia, pre-scan)**; low 27408.5 at **17:40Z** |
| Direction | **0 right / 0 wrong / 1 no-call.** Score **−2**, inside `journal.py:68`'s ±3 dead zone. Post-scan move −69.1 = **11.8%** of range (outside H17's proposed 5% band) |
| Levels | **7 of 22 touched = 0.32** against `track.py`'s running **0.49** (31 scans) |
| Fuel | budget **621.8** vs extension **351.6 = 0.57x**; traversal 571.0 = 0.92x. `review_day` verdict *"about right"*. Error **−270.2** |
| CPI 13:30Z | 27813.5 (13:25) to 27575.2 (13:35) = **−238 in 10 minutes** |
| Post-print 30-min range | 27491.8–27813.9. **High swept 14:55Z, low swept 17:35Z** — both sides, high first |

**−270.2 is the largest OVER-estimate in the 31-day window** (previous worst
−258.2 on 11-03) and it **ends four consecutive under-estimates** (+305.9 /
+1261.2 / +174.0 / +544.7). H1's per-day mean is unchanged at **+106.5**.

## 2. What the levels actually did

**The call wall was the best call on the board.** 27982.9, published as *"desks
must SELL as price rises into it, so rallies stall. Take profit into it"*, and
in §Upside path *"expect a stall at 27982.9 … take partials into it rather than
assuming a clean breakout."* The post-CPI rally topped at **27979.5** — **3.4
points short** — held resistance **490 minutes**, and the day closed 256.4
below. *Caveat recorded against it:* Asia printed **27995.9 at 00:05Z, 13.0
above the wall**, pre-scan, and the board was published as if the level were
untraded. The overshoot was small enough not to bite, but it is the same
session-context blind spot already on the watch list.

**The put wall's conditional was right, and it is a counter-instance to reading
put walls as floors.** 27782.9 was published as *"heaviest floor this week (22k
contracts), BUT today the desks are pushing moves along — if it breaks, expect
it to speed UP, not bounce. Don't buy the break."* It broke, settled below from
15:30Z for **325 minutes**, ran **374.4 points** to 27408.5 and closed 56.4
below. 27764.0 (London Low + Equal lows x2 + Asia Low) did the same, lost by
82.1. Strategy 2's *"sweeps run rather than fail"* was the correct frame.

**Two rows are one zone and should not score as two hits.** 27982.9 (call wall)
and 27960.6 (PD close) sit **22.3 points** apart; both were first reached on the
same 15:00Z bar and both "held as resistance for 490min". Counting them
separately inflates `level_hit_rate`. Same for 27935.4 / 27927.4, **8.0 points**
apart — exactly `TOUCH_TOL` — one lost and one held, which is a tolerance
artefact, not two readings.

**The real level finding is a hole, not a bad level.** Between the 27782.9 /
27764.0 cluster and PD mid 27329.1 there is a **434.9-point void with nothing
published in it**. The day's decisive move — **356 points** from 27764.0 to the
27408.5 low, where price then based for two hours — happened entirely inside
that void. The board carried **10 levels in the 843 points above price**, 2 in
the 435 points immediately below, then nothing. On a day whose own strategy call
was *"below the flip … downside accelerates"*, the board had no density on the
side it told the reader to trade. Nearest misses: PD mid by **79.4**, Asia High
(today) by **16.4**, PDH by **38.4**.

**Untouched: 15 of 22 (68%).** The gamma flip (28132.9) and max pain (28122.9)
were 349/339 away and never approached — consistent with the brief's own
below-flip framing, so not a defect, but they only add denominator. The two
prev-day lows (26707.1 / 26699.9, both ≥1076 away, both `stretch: true`) were
never in play. **Nothing is condemned on one 0.685x-ADR day.**

## 3. What was wrong, and why

Score **−2 → no call** on a day that fell 167.8 and closed below the put wall.
From `inputs.bias_components`:

- **Right-signed (−8):** gamma −3 (below flip by 343.1), gamma −2 (week GEX
  −0.698), macro −3 (real yield) and −1 (nominal), news −1.
- **Wrong-signed (+6):** **breadth +3**, structure +2, vol +1 (net), gamma +2
  (bottom of wall band).

**The largest wrong-signed block is `breadth +3`, and both of its rows are
rear-view by construction.** The mega-cap row (*"avg +2.42% (3/4 up)"*) and the
index row (*"NDX +3.40% vs ES −0.01% — tech leading, genuine risk appetite"*)
both describe **11-09's +1045.5 up day**. The brief printed *"genuine risk
appetite"* while a number it computed four sections earlier said the opposite:
its own `nq_implied` NDX reference was **27800.9** against the 11-09 cash close
**27907.63** — **−106.7 points, −0.38% overnight.**

**This is the first instance in the record where the breadth window choice
changes a DIRECTION GRADE, not just a score.** Put the NDX leg on the overnight
basis the brief already computes (−0.38%) against the live ES (−0.01%) and
`bias_engine.py:190`'s `nd < es − 0.2` fires: the row goes **+1 → −1**, the
score goes **−2 → −4**, which crosses `journal.py:68`'s ≤−3 and emits a real
**−1 call**. The day was −167.8 net / −69.1 post-scan: **that call would have
been CORRECT.** The three prior instances (11-05 / 11-06 / 11-09) moved only the
score and the label.

**Reported against the fix:** `rates` scored **0 / 0** (US10y +0.10%, DXY
+0.12%). Correcting the DXY row to its true prior session (**−0.635%**) scores
**+2** *"dollar soft, risk-on"* and takes the day to **0** — **further** from
the realised decline. The correctness fix is not an accuracy fix.

### D22(a) — runner's notes verified independently, 3 of 3 reproduce

Verified from my own Yahoo fetch (12:50–13:10Z on 11-11), against the printed
rows in `2026-11-11/1246-london.json`. **Gates read from source:**
`bias_engine.py:150` (DXY ±0.4) and `:190` (`nd ≷ es ± 0.2`).

**Note 1 — per-symbol enumeration, CONFIRMED 4 of 4.**

| symbol | dated bar for today? | printed | true prior session | verdict |
|---|---|---|---|---|
| `^NDX` | no (last bar 11-10) | −0.60% | **−0.598%** | **MATCHES** |
| `^TNX` | no (last bar 11-10) | +2.45% | **+2.447%** | **MATCHES** |
| `ES=F` | **yes (11-11)** | +0.91% | **−0.396%** | **WRONG — sign flip, 1.30pp** |
| `DX-Y.NYB` | **yes (11-11)** | +0.30% | **+0.571%** | **WRONG — 0.26pp** |

Exactly the two symbols with a dated same-day bar are wrong; exactly the two
cash indices are right. I also re-derived the four mega-caps: **NVDA −5.474 /
MSFT −2.205 / AAPL −0.622 / AVGO +3.913** reproduce the printed row to 2dp —
the mega-cap leg is **not** affected, which keeps the blast radius at two of
twelve symbols. Runner quoted 1.31pp / 0.27pp from rounded prints; exact is
**1.297pp / 0.262pp**. Same finding, no averaging.

**Note 2 — point-changing TODAY, CONFIRMED.** Printed +0.30% scores `rates +0`
*"dollar flat"*; true +0.571% clears the ±0.4 gate and scores **−2** *"dollar
bid, risk-off"*. **Today's published −15 would be −17, and `rates` −4 would be
−6.** Label is unchanged (both ≤ −10 = STRONGLY BEARISH). Across the window the
DXY row is point-changing on **5 of 6 scans** — exactly as claimed:

| scan | printed DXY | pts | true prior-session | pts | Δ |
|---|---|---|---|---|---|
| 11-04 | −0.55% | +2 | +0.118% | 0 | **−2** |
| 11-05 | +0.10% | 0 | −0.353% | 0 | 0 |
| 11-06 | +0.42% | −2 | +0.039% | 0 | **+2** |
| 11-09 | −0.41% | +2 | +0.739% | −2 | **−4 (sign flip)** |
| 11-10 | +0.12% | 0 | −0.635% | +2 | **+2** |
| 11-11 | +0.30% | 0 | +0.571% | −2 | **−2** |

All five of the 11-10 review's figures reproduce to 2dp, as do all five of its
ES legs (+0.294 / +1.629 / −4.371 / +0.257 / +2.327). The five scans before this
window (10-29 → 11-03) are **0 of 5 point-changing** — the impact is
concentrated, not uniform.

**Note 3 — the breadth point survives by 0.0017pp, CONFIRMED.** Exact:
`nd = −0.597814`, corrected `es = −0.396079`, gate `es − 0.2 = −0.596079`.
`−0.597814 < −0.596079` is **true by 0.001736pp**. Printed, the gap looked like
**1.499pp** (1.51 from the rounded prints). So the row that read as robust on
11-06 / 11-09 / 11-10 is, on corrected data, sitting **on** its gate.

**One thing the notes did not say, and it cuts the other way: across all six
scans, correcting to "both prior-session" changes ZERO direction grades.**
11-04 −12 → −12 (the two corrections cancel), 11-05 −4 → −6, 11-06 −19 → −17,
11-09 −3 → **−7 (more confidently WRONG** on a +1045.5 day), 11-10 −2 → 0, 11-11
−15 → −17. Two labels move (11-05 and 11-09, MILDLY BEARISH → BEARISH) and the
label drives the strategy prose the user reads, so it still matters — but the
claim *"this defect cost direction accuracy"* is **not supported**.

**One new limb, logged not proposed.** Today's **delivered** brief says *"NDX
−0.60% vs ES +0.91% — tech lagging, rotation out of tech"* on a morning when
NQ was **+1.95%** overnight by the brief's own `nq_implied` (28282.0 against the
27740.79 cash close) and **+1.91%** on my independent 13:05Z fetch, against ES
**+0.90%**. The printed row has the sign of the overnight tech-vs-broad
divergence **exactly inverted**. 11-11 is not yet graded; this is a
**narrative-inversion instance at n=1**.

## 4. Change proposals

`track.py`: **31 trading days / 31 scans, `actionable: YES`** (*"threshold met,
read the evidence before proposing"*). Reading the evidence:

**NO NEW ID ALLOCATED.** `^## H28`, `^## D32`, `^## P-J`, `^## M8` all return 0
on `grep -c`, re-confirmed 2026-11-11. The runner allocated nothing and said
allocation was mine; **D22(a)** already owns this mechanism and opening a number
would be the collision pattern the register's header exists to prevent.

**NO NEW PROPOSAL.** The only material item is **D22(a)**, already PROPOSED in
two parts by the 11-10 review. This review adds evidence to both and one
correction to its own count:

1. **Part 1 (correctness: `yahoo_series` returns the window it measured, and
   consumers print it) — n=5 → n=6 scans.** Point-changing rows **6 → 7**; DXY
   point-changing **5 of 6**; **12 of 12 leg-pairs mis-windowed by
   construction**. Expected effect: unchanged — prose and provenance only, no
   score change from part 1 alone. **Correction to the prior review's framing:**
   it counted breadth as clean on 11-11-type rows; today's row clears its gate
   by 0.0017pp, so "clean" overstates it, and **zero direction grades move on the
   prior-session basis** across all six scans.
2. **Part 2 (put the `breadth` NDX leg on the overnight window) — n=3 → n=4
   deciding instances, and the first one that moves a GRADE.** Tally: **live 3
   right / 1 neutral / 0 wrong · printed 1 right / 3 wrong · prior-session 2
   right / 2 wrong.** 11-10 adds `live −1` right where printed and
   prior-session were both wrong-signed, and it is the instance that turns a
   no-call into a correct call. **Zero new data:** the overnight NDX leg is
   already computed inside the brief (`gex_levels._nq_implied_cash`). The
   falsifier stands unchanged: three sessions where live is wrong-signed and
   printed is right. **Not widened.**

**Gate fragility — watch item, n=3 condition / 0 harm, NOTHING PROPOSED.**
Three hair-trigger instances in one window: DXY ±0.4 cleared by **0.02pp**
(11-06), missed by **0.01pp** (11-09); breadth ±0.2 cleared by **0.0017pp**
(11-11). A deadband or hysteresis on bias gates is unmeasured tuning and there
is no harm instance; the change that actually removes the fragility is the
windowing fix already proposed. Watching: margin-to-gate on every `rates`/DXY
and `breadth`/ES row, every scan.

**Level board — routed to the existing unnumbered "level board" watch item as
instance 2, different shape.** 11-09 was *"42% published into a side that never
happened"*; 11-10 is the opposite failure — the right side, with a **434.9-point
void** where the session low formed. **n=2 condition, harm not demonstrable from
one day, NOTHING PROPOSED.** Watching: whether the session extreme lands in a
published void, every scan.

**Stop publishing a level? NO.** One 0.685x-ADR day cannot condemn a
swing-reach row.

**Dead-weight component? NO new claim.** `rates` scored 0/0 today, but that is
the D22(a) row, not a dead component.

**Fuel? NO proposal.** −270.2 is the window's largest over-estimate and it
breaks a four-session under-estimate run, while H1's per-day mean is unchanged
at **+106.5**. A single large counter-signed error is precisely the noise the
three-session rule exists to absorb.

**New data point? NONE warranted.** `ZN=F` stays **DECLINED** on the 11-10
review's own reasoning (n=0 paired readings; one-change-at-a-time while part 1
is live). Watching: overnight `ZN` against the printed `^TNX` prior-session
move, every scan.

## Journal hygiene

**Checked and clean, but one thing looked wrong and was chased down.**
`2026-11-04`, `2026-11-05` and `2026-11-06` all carry an **identical mtime of
2026-11-09T12:46:15Z** — the shape of a backfill. `git log` refutes it: each
file was committed **within 2 seconds of its own `scan_utc`** (bd6c276
2026-11-04 12:47:55 for a 12:47:54 scan; 7918542 11-05 12:47:04 for 12:47:02;
9f23e37 11-06 12:47:50 for 12:47:49). The mtime cluster is a fresh-clone
artefact. **No fabricated or backfilled entry found; no `prediction` block was
modified by this review.**

`2026-11-11` is correctly **held back** by `track.py` (180 bars at review time).
Six `test_artefact` entries excluded as always. `track.py` completed exit 0.
