# REVIEW — 2026-11-12 (graded 2026-11-13)

One scan: `1246-london.json`, 12:46:47Z, `LONDON`, `is_trading_day: true`,
`test_artefacts: 0`, `outcome: null`. No `is_trading_day: false` scan in the
window examined, so nothing was excluded on that ground.

## 1. Scoreboard

| | |
|---|---|
| Session O/H/L/C | **28375.1 / 28548.3 / 27911.7 / 28283.9** (276 M5 bars) |
| Range / net | **636.6** (0.737× ADR14 864.1) / **−91.2** |
| Path | pre-scan range 375.0; scan print **28099.5**; post-scan **low 27911.7 first (−187.8)**, then **high 28548.3 (+448.8 from the scan)**; both session extremes were post-scan (traversal 636.6 = full range) |
| Direction | **0 right / 1 wrong / 0 no-call.** Score **−11** `STRONGLY BEARISH`. Post-scan **+195.0 → WRONG** (official). Day-net **−91.2 → CORRECT** |
| P-H | **deciding instance 7** — verdict flips with the basis. Same sign pattern as 10-07 (post-scan up against a down day) |
| H17 | **not** a noise case on either basis (post-scan 30.6% of range, day-net 14.3%) |
| Levels | **14 of 18 touched = 0.78** |
| Fuel | budget **489.1** vs extension **261.6** = **0.53×**, `review_day` *"about right"*; H1 error **−227.5** (over-forecast); traversal **1.30×** budget |
| VXN-implied | **473.3** vs realised **636.6** — under by **163.3** (third consecutive *under*: 11-10, 11-11, 11-12) |
| Straddle band | ±327 → 27773..28426; close **28283.9 INSIDE** (H8 post-closure HIT) |

## 2. What the levels actually did

| level | the brief said | what happened |
|---|---|---|
| **28543.7** GAMMA FLIP (+444) | *"Reclaim and hold above and fading becomes valid again"* | **The best row on the board.** Session high **28548.3 = 4.6 above**, never held, resistance for **490 min**. As a *ceiling* it was exact. As a *magnet/settlement* level (H4's claim) it was not: close **259.8 below** |
| **28483.7** CALL WALL ●●○○○ (+384) | *"rallies stall. Take profit into it. A held close above flips that selling to buying"* | Exceeded by **64.6**, no held close above, so the conditional correctly never triggered. The unconditional *"rallies stall"* stalled **60 points too low** — the flip did the work |
| **28283.7** MAX PAIN (+184, 0.21× ADR, inside budget) | *"drifts toward it as the week goes on … strong by Thursday/Friday"* | **Close 28283.9 = 0.2 points above it, on a Thursday.** A genuine, non-distance-confounded test (184 away, well inside the 489 budget). **Clean close-pin census 1–2 → 2–2 at n=4** (11-04's Wednesday *held as resistance* stays separately logged at n=1), and the **first Thursday/Friday HIT** against the pre-registered deletion trigger (*two more Thursday/Friday misses*). Confound, stated: PD close 28319.9 and London High 28300.5 sit within 36 points |
| **28319.9** PD close | *"price often comes back to fill a gap from here"* | Filled (touched 15:50Z, crossed both ways). Honest row |
| **28300.5** / **28265.5** / **28214.8** prior/Asia/London highs | *"next session usually runs the stops above it"* | All three run on the way to the flip. Honest rows |
| **28061.3** Equal lows ×2 (−38) | *"a real stop cluster. **Prime S1 sweep trigger**"* | **Right, and it contradicted §1–§3.** Swept by **149.6** to the session low, then the day's whole move (+636.6) came off it |
| **27983.7** PUT WALL ●●●●● 0.38bn (−116) | *"if it breaks, expect it to speed UP, not bounce. **Don't buy the break.** … the strongest floor on the board"* | **FALSIFIED.** Broken by **72.0 (0.083× ADR)** at ~13:05Z, then reversed into a **636.6-point** rally. The break was the failed sweep, and buying it was the trade of the day |
| 28117.1 / 28095.4 / 28079.9 / 28030.4 near lows | *"the next session usually runs the stops below it"* | All run within 20 minutes of the scan. Honest rows, but they were 4–69 points away — close to tautological |
| Untouched: 29033.7 structural, 28838.9 PWH, 28591.4 PDH, 27743.5 PDL | — | PDH missed by **43.1**; PDL by **168.2**. No void: the high and low both landed on or next to published rows |

**M6 — session 44.** 28174.2 *"held as support 325 min, worst −9.1"* and
28117.1 *"held as support 350 min, worst −18.1"* are both asserted over settle
windows opening at 15:30Z / 15:05Z, **after** those levels had been broken by
**262.5** and **205.4**. The put wall's *"lost by 41.5"* understates a true
excursion of **72.0**. Expected-by-identity; no new claim.

**No level is a candidate to stop publishing on today's evidence.** The board
framed the day well: flip = ceiling to 4.6 points, max pain = close to 0.2,
equal lows = the reversal point. The *prose* attached to the put wall was the
failure, not the level.

## 3. What was wrong, and why

**Score −11 = gamma −5 · macro −4 · news −4 · structure −2 · rates −1 against
breadth +3 · vol +2.** Post-scan was +195.0, so on the official basis every
block except breadth and vol was wrong-signed.

1. **`gamma −3` — amplitude spent as direction, 4th instance of the shape, and
   the routing in the register cannot own it.** *"below flip 28543.7 by
   444.2pts — dealers amplify: downside accelerates, rallies unstable."* The
   amplification arrived in **both** directions (−187.8, then +636.6) and the
   rally stopped **4.6 points above the flip** — a grind-back that closed 101%
   of the gap at the high. Register instances: 10-26, 11-04, 11-09, now 11-12.
   **The register routes the shape to the "unarbitrated two-gamma-rows
   conflict", but 11-12 was `COHERENT_SHORT` (today −2.26 / week −2.345 /
   45-day −5.729, every tenor short) and so was 11-04.** Two of the four
   instances had no conflict to arbitrate. The full flip-row census is in §4.
2. **`gamma −2` *"week net GEX −2.345 → expansion likely"* — label WRONG
   (H22).** Range 0.737× ADR. The shape's *"Today's ADR can be exceeded — don't
   cap the target too early"* was falsified with it.
3. **`macro −4` — stale and duplicated.** DFII10 as of **11-09**, the
   Veterans-Day repeat already logged, plus the DGS10 row that locks to it
   (H18/P1). Wrong-signed post-scan.
4. **`news −4` — coverage 5 of 75 = 6.7% (H19), one D9 tag.** *"Jensen Huang
   affair in DC: Resignation calls and moves to **tighten** Nvidia China
   exports"* → `hawkish` → *"Hawkish repricing"* — the **same `tighten` token as
   D9 instance 3** (*"tighten race"*), on export policy, not the Fed. The one
   bullish tag (*"Nasdaq 100 Advances 3%"*) was the prior session's move.
5. **The four blocks of the document agreed, and the day falsified the
   instruction they shared.** §1 Strategy 2, §2 *"Sweeps tend to keep running
   rather than fail. Fading is the wrong trade today"*, §3 *"DOWNSIDE path:
   clear … Do not fade it"*, §4 put wall *"Don't buy the break."* Price broke
   the strongest floor by 72.0 and reversed 636.6. **The only rows that called
   it were §4's liquidity rows** (*"Prime S1 sweep trigger"*). That is the
   **second consecutive session** where a liquidity row and the gamma regime
   sentence gave opposite instructions and the liquidity row won — 11-11 above
   the flip, 11-12 below it, so it is not one regime's problem. **n=2, nothing
   proposed.**

**The 11-11 partition does NOT repeat.** On 11-11 the only right-signed block
was current data (gamma) and all wrong-signed weight was older data. On 11-12,
post-scan basis, it is the reverse: **current-data gamma −5 was wrong; the
prior-session block (vol +2, rates −1, breadth +3 = +4) was the only
right-signed one, and it was outvoted.** On the day-net basis it flips back.
One day each way is noise. **Rear-view block census, n=5:** post-scan basis
adds a new cell (*right and outvoted*); day-net basis makes it *cancel-a-correct*
(3 cancel-a-correct / 2 amplify-a-wrong). **"Late, not biased" survives on
either basis; no weight change.**

**D22(a) on the graded scan.** Part 1 (both legs prior-session): DXY true
**+0.665%** → `rates −2`, breadth gap 1.008pp → `+1` stands → **−13**. Part 2
(NDX leg on the overnight window): NDX reference **28115.8** vs the 11-11 cash
close 28374.25 = **−0.911%** against ES **−0.40%** → gap **−0.51** → breadth
**−1** → **−13**. **Both corrections move the score the same way, by the same
amount, and neither changes the grade.** Post-scan basis: both move AWAY from
the realised day. Day-net basis: both move TOWARD it.

## 4. Change proposals — only material ones

**NO NEW PROPOSAL. NO NEW ID ALLOCATED.** `grep -c` for `^## H28`, `^## D32`,
`^## P-J`, `^## M8` all return **0**, re-confirmed 2026-11-13.

### One CORRECTION to a live recommendation: part 2's evidence is graded on the basis P-H recommends AGAINST

The 11-12 review recommended shipping **D22(a) part 2 before part 1**, on a
five-row table scored *"live 4 right / 1 neutral / 0 wrong"*. **That table is
graded on DAY-NET** (11-06's live +1 is called *right* against +331.9 although
the post-scan move was −28.0). **P-H's recommended basis is POST-SCAN, shipped
together with H17's deadband.** Re-graded both ways, with 11-12 added:

| scan | printed | prior-session (part 1) | live (part 2) | post-scan | day-net |
|---|---|---|---|---|---|
| 11-05 | +1 | −1 | −1 | −1554.1 | −1803.8 |
| 11-06 | −1 | −1 | +1 | −28.0 (H17 noise) | +331.9 |
| 11-09 | +1 | +1 | 0 | +652.7 | +1045.5 |
| 11-10 | +1 | +1 | −1 | −69.1 | −167.8 |
| 11-11 | −1 | −1 | +1 | +101.9 | +652.9 |
| **11-12** | **+1** | **+1** | **−1** | **+195.0** | **−91.2** |

| basis | printed | part 1 | part 2 |
|---|---|---|---|
| **day-net** (the table's own) | 1 R / 5 W | 2 R / 4 W | **5 R / 0 W / 1 neutral** |
| **post-scan + deadband** (P-H + H17) | 2 R / 3 W / 1 no-call | 3 R / 2 W / 1 no-call | **3 R / 1 W / 1 neutral / 1 no-call** |

**11-12 is part 2's FIRST falsifier-shape instance on the post-scan basis**
(live wrong-signed, printed right) — **1 of the 3** its falsifier needs. On the
day-net basis it is a fifth right. **The recommendation survives on both bases
— part 2 is never worse than part 1 — but on the register's own recommended
basis its margin over part 1 is ONE wrong call (3–1 vs 3–2), against 5–0 vs
2–4 on day-net.** The sequencing call is
therefore **coupled to P-H** the way H3 was: state the basis before quoting the
margin. **Not withdrawn, not widened.**

### The runner's 11-13 claims — verified independently (own Yahoo fetch 2026-11-13; gates `bias_engine.py:150` ±0.4 and `:190` ±0.2)

**Claim 1 — CONFIRMED 5 of 5.** True prior-session = 11-11 close → 11-12 close.

| symbol | printed | true | verdict |
|---|---|---|---|
| `^NDX` | −0.30% | 28374.25 → 28289.19 = **−0.2998%** | match (cash) |
| `^TNX` | +2.10% | 4.998 → 5.103 = **+2.1008%** | match (cash) |
| `^VXN` | +6.8% | 26.74 → 28.55 = **+6.769%** | match — **4th clean D22(b) control** |
| `ES=F` | +0.26% | 7640.50 → 7615.25 = **−0.3305%** | **sign flip, 0.591pp** |
| `DX-Y.NYB` | +0.06% | 102.91 → 103.17 = **+0.2526%** | **wrong, 0.193pp** |

Printed DXY last **103.234** vs the 11-12 close 103.17 = **+0.062%** → the
printed figure is the live intraday move, confirmed a second time. Mega-cap leg
unaffected for an **8th** scan (NVDA −4.340 / MSFT +0.359 / AAPL −0.211 /
AVGO +5.544, all match). **Blast radius stays 2 of 12. Part 1 tally: n=8 scans,
16 of 16 leg-pairs mis-windowed, point-changing rows 8 → 9.**

**Claim 2 — CONFIRMED, with a correction to what it shows.** DXY: printed
+0.06 and true +0.253 both inside ±0.4 → `rates +0` either way. Breadth: true
gap **+0.0307pp** → `0`, so **−16 → −15**, label unchanged. **But part 2 does
NOT remove this row.** On the journal's own inputs (NDX reference 28303.4 vs
cash close 28289.19 = **+0.050%**, ES **+0.26%**) the overnight gap is
**−0.210** → **−1, kept**, clearing the gate by ~0.01pp; on independent 5m
bars it reads −0.185 at 12:40Z and −0.213 at 12:45Z — **on the gate.** On the
overnight window *"tech lagging"* is (barely) true; it is false only on the
prior-session window.

**Claim 3 — the run is CONFIRMED, the mechanism comparison is CORRECTED.** The
outside-±0.4 run ends at **4** (scans 11-09..11-12); 11-13's true +0.253 is
inside. **But today does not discriminate between the two mechanisms.** The
runner's original reading (*"bites when the dollar trends"*) also predicts no
point change on a non-trend day, so both are consistent with 11-13. And the
*"straddle the gate"* description is an **identity** for any thresholded row —
a point changes if and only if the two values land on opposite sides of the
gate — so no day can *confirm* it. What carries information is the conditional
rates. **Recounted from source over every trading-day scan 10-01 → 11-13
(n=31): 11 point-changing. True outside ±0.4: 7 of 7 point-changing (false
negatives, because the 12:46Z live move is small). True inside: 4 of 24 (17%,
false positives — 10-07, 10-14, 11-04, 11-06).** The carried "6 of 12" was
10-28 → 11-12 only; on that window it is now **6 of 13**.

**Claim 4 — CORRECTED: today supports PART 1, not part 2.** It is the first
scan in the part-2 table (11-05 →) where part 1 removes a false narrative that part 2 would
keep. It cannot be graded until 11-13 closes. **This does not move the
sequencing call**; the basis-dependence above does.

**The other five flags:**
- **Huang / NVDA magnitude — routes to H19, not a new item, and the tape does
  not support "under-sized".** 11-13's five scored rows include **two
  polarity-inverted tags**: *"Nvidia **Climbs** After Tumbling On CEO Huang's
  Exit"* → `earnings_miss` (**D18** — bullish headline, bearish keyword) and
  *"**Slow** federal inflation rise brings small **relief**"* → *"Hot inflation"*
  (**D18**). The Huang event enters as many times as headlines happen to match —
  that is H19's *magnitude tracks match count* limb exactly. On the size
  question the evidence points the other way: NVDA fell **4.34%** on 11-12 while
  NDX fell only **0.30%** (AVGO +5.54% offset it), and NQ was ~flat overnight.
  **n=1, nothing opened.**
- **The flip-straddle rider — the threshold is right, but this is D16's
  harmless half, not a guard that works.** 21.8pts = 0.077% < 0.15%, so the
  text is true (no D8). The rider is still `+1 if px > gf else +1`
  (`bias_engine.py:87`, unfixed). Below the flip it softens −3 to −2 by
  construction; above the flip it inflates +2 to +3. Trading-day firings:
  **4 above (09-09 ×2, 09-11, 09-16) / 4 below (10-12, 10-21, 10-27, 11-13)**.
  Record as D16's 4th below-flip firing, sign correct by accident.
- **`PIN_THEN_EXPAND` — the 4th post-verdict firing, not the 5th.** Test sample
  10-19 / 10-21 / 10-26 (falsified 3 of 3); since then 10-27, 11-02, 11-09,
  11-13. The three graded post-verdict firings all resolved early. **6 of 6
  graded firings against the timing prose**; 11-13 pending. P-I unchanged.
- **Week net GEX +4.004 → −2.345 → +0.164:** noted, not reopened. +0.164 prints
  *"pinning likely"* at **0 points** (the same wording-vs-gate gap as 09-30's
  0.036, H22).
- **US10y 5.103% is NOT the first print through 5% — CORRECTED.** The series
  printed ≥5% on **22 earlier trading-day scans** (09-15; 09-24 → 10-22
  continuously, peak **5.337 on 10-07**; 10-29 at 5.026). It is the first print
  above 5% since 10-29. It is also the 11-12 *cash close* (D22(a) cash leg), not
  a live read; overnight `ZN=F` at 12:45Z was −0.267% in price (yields up),
  **same sign** — `ZN=F` paired reading 2: 1 opposite / 1 same, still DECLINED.
  **DFII10 CONFIRMED:** as-of 11-09 → **11-10**, 2.66 → **2.78% (+12bp)**,
  matching TNX's +11.9bp on 11-10. The Veterans-Day repeat has resolved.

### Everything else, one line each

- **The flip-side row's direction skill — census COMPLETED, and it answers the
  question 3b (2026-09-09) left open. NOT proposed: the answer depends on P-H.**
  Every graded trading-day scan 09-30 → 11-12 (n=31; 09-29 truncated by D26,
  09-28 aged out), `+2 above flip` / `−3 below flip` against the realised move:

  | basis | −3 below flip (n=23) | +2 above flip (n=8) | total |
  |---|---|---|---|
  | **post-scan + 5% deadband** (official + H17) | 10 R / 11 W / 2 noise | 4 R / 4 W | **14 R / 15 W** |
  | **day-net** | 13 R / 10 W | 7 R / 1 W | **20 R / 11 W** |

  **On the grader's own basis the largest single term in the score has no
  directional skill at n=31.** On day-net it is 65% (one-sided p ≈ 0.08, in a
  window where the scan price fell from ~30,460 (09-30) to ~28,100 (11-12),
  which flatters a row that was bearish on 23 of 31 days). The amplitude-as-direction shape (10-26, 11-04, 11-09, 11-12) is the
  mechanism; 2 of those 4 were `COHERENT_SHORT` with no two-gamma conflict, so
  the register's routing to the "unarbitrated two-gamma-rows conflict" owns only
  half of it. **Nothing proposed, for the reason H3 was blocked: the verdict
  flips with the grading basis, and P-H is undecided. Once P-H is decided, this
  table decides the flip weight.**
- **H26** — ≥10 bucket, `|post|/ADR` = 195.0/864.1 = **0.226**, WRONG
  (post-scan).
- **H23** — no named brake (both paths *"clear"*); no instance. Both-clear graded:
  upside ran (448.8), downside *"Do not fade it"* falsified at 0.22× ADR.
- **H22** — −2.345 → *"expansion likely"* → 0.737× ADR, label WRONG.
- **D31** — under by 163.3, third consecutive; serial left unnumbered pending
  the reconciliation the 11-12 review flagged.
- **H8 (CLOSED)** — post-closure was logged at 3 hits / 3 misses through 11-09;
  **11-10 (27726.5 in 27470..28098) and 11-11 (28380.4 in 27829..28742) were
  never logged and both HIT**; 11-12 HIT. **6 hits / 3 misses**. Not reopened.
- **H19** — 11-12 coverage 6.7%, `news −4`, wrong post-scan / right day-net.
- **D9** — `tighten` token, 11-12, export-policy headline scored hawkish.
- **D22(b)** — stays SETTLED NEGATIVE (VXN 4th clean control).
- **H10** — did not fire (inside the prior-week range).

### New data point

None. `ZN=F` stays declined (one change at a time while D22(a) is live).

## Journal hygiene

`2026-11-12/1246-london.json` + `.md`, `is_trading_day: true`, 276 bars,
`outcome: null` — not back-written, correct. Commit **ec14b5d 2026-11-12
12:46:50Z** for a 12:46:47Z scan; **453f96c 2026-11-13 12:46:42Z** for the
12:46:41Z 11-13 scan. Same-second commits, no backfill. **No fabricated or
backfilled entry found; no `prediction` block was modified by this review.**

## track.py

**COMPLETED, exit 0. 31 trading days / 31 scans (deduped), 6 `test_artefact`
entries excluded.** The literal `actionable: YES/NO` string is **still not
emitted by this build**; the header reads *"31 of 3 days for the 3-day
hypotheses — threshold met, read the evidence before proposing"*, and the
3-session rule was applied by hand to every item above. Flagged, not
substituted silently.

- **Direction 12 / 13 / 6 → 11 right / 14 wrong / 6 no-call = 11 of 25 = 44.0%**
  (was 48.0%). **Not one data point:** 11-12 enters WRONG **and 09-29 (CORRECT,
  +6) left the bar window on the same run.** If P-H + H17 ship, restate it.
- **H1 per-day mean +103.0 → +99.3 at n=31** (11-12's −227.5 in, 09-29's
  −112.2 out). Dispersion, no trend; nothing proposed.
- **Levels touched 0.49** running; 11-12's 0.78 is above it.
- **D26 — second consecutive mislabel.** `track.py` reports **2026-09-29 at 97
  bars under "HELD BACK — day not finished"** — a session six weeks old,
  truncated by the fetch window, exactly as 09-28 was yesterday. Gap: **31 full
  bar sets against 53 finished day directories** (54 minus the unfinished
  11-13) — **21 → 22**. `2026-11-13` is correctly held back (182 bars).
- **H2** — 11-12 is `MODERATE` and below the flip; not in `track.py`'s H2 list,
  so a non-instance.
