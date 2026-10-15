# REVIEW — 2026-10-14 (Wednesday)

_Graded 2026-10-15 from `review_day.py 2026-10-14 --json` and `track.py`. One
PRE_NY scan, `is_trading_day: true`, 0 test artefacts. **There is no `2026-10-13`
journal directory — Tuesday's scheduled scan never ran. Nothing was created,
back-dated or inferred for it; the series skips from 10-12 to 10-14.** 09-24
remains quarantined by hand (12th consecutive review). 2026-10-15 is excluded
from every statistic below: its session is not finished (`track.py` holds it
back at 180 bars)._

## 1. Scoreboard

| | |
|---|---|
| Session (21:00Z roll, 276 M5 bars) | O **30594.0** / H **30688.3** / L **29877.9** / C **29931.8** |
| Range / net | **810.4** (**1.88x** ADR14 431.6 — the largest range/ADR in the graded record) · net **−662.2** |
| Scan | PRE_NY 12:47:54Z at **30406.0** · bias **−18 STRONGLY BEARISH** · `expected_direction −1` · `COHERENT_SHORT` high confidence |
| Direction | **1 right / 0 wrong / 0 no-call.** Post-scan move **−485.9** (P-H basis), day net **−662.2** — both bases agree in sign, **no P-H deciding instance**; census stays n=3 |
| Post-scan path | H **30456.8** (+50.8) → L **29877.9** (−528.1) · traversal **578.9** |
| Levels | **10 published, 5 touched, hit rate 0.50** |
| Fuel | budget **97.6** · extension **476.4** · err **+378.8** (ratio **4.88x**, UNDER-estimated) · traversal **578.9 = 5.93x** budget |
| Vol boundaries | VXN-implied range **404.9** vs realised **810.4** → under by **405.5** (realised **2.00x**), **the largest miss in the series** (prior: −261.8). Straddle EM band **30129 .. 30683**; close **29931.8 OUTSIDE by 197.2**, high outside by 5.3, low outside by 251.1 |
| Blocks | gamma **−5** · macro **−5** · structure **−4** · rates **−3** · news **−1** · vol **0** · breadth **0** · fuel **0** · events **0** |
| Conviction, in context | −18 is the most extreme score in 63 scans (previous extreme −15 / +13). The label saturates at ±10 (`bias_engine.py:268`), so it printed the **same two words** as the −10 of 10-07, which was wrong |

## 2. What the levels actually did

**Touched (5).**

| level | dist | brief said | what happened | verdict |
|---|---|---|---|---|
| **30423.1 London Low (prev-day)** | +17 | *"the next session usually runs the stops below it"* | touched 12:50Z, chopped, settled below from 13:45 and held as resistance 430min, worst **+21.2** | right, but see §3 — price was already below it when it printed |
| **30402.6 Asia Low (prev-day)** | −3 | same prose | settled below from 13:45; graded *"broke UP through it — lost by 41.7pts"* | **M6 wording inversion** — the day broke it DOWNWARD and closed **470.8 below** |
| **30386.7 PDL + NY Low (prev) ⭐** | −19 | *"the biggest pile of stops below us. Sweep it, wait for a higher low on the 1m, then **CISD = long**"* | swept and kept going **508.8 further down**; retrace capped at **+57.6** | **the long instruction would have been run over**, and it contradicts the document's own STRATEGY 2 header |
| **30041.8 PUT WALL ●●●●○ 0.90bn** | −364 | *"heaviest floor this week"* **+** *"if it breaks, expect it to speed UP, not bounce. Don't buy the break"* | broke at 16:10Z, ran **163.9 (0.38x ADR)** to the low, **never reclaimed**, closed **110.0 below**; two re-tests capped at **+1.8** | headline **wrong**, regime rider **right**, and the retrace cap is the cleanest behavioural row of the day |
| **30011.8 MAX PAIN** | −394 | *"price drifts toward it as the week goes on. Weak on a Monday, strong by Thursday/Friday"* | reached 16:20Z on a **Wednesday**, **exceeded by 133.9**, closed **80.0 below**; retrace capped at +21.3 | reached, **not a magnet** — 2nd within-reach test in the record and the 2nd failure |

**Untouched (5).** CALL WALL 30841.8 (+436) was **385.0 above the post-scan
high** and 153.5 above the session high — never in play, for the 2nd consecutive
publication. GAMMA FLIP 30612.7 (+207) was never approached within 155.9, which
is a *correct* regime read, not a dead level. The other three — **PWL 30568.7**,
**London Low (today) 30513.4**, **Asia Low (today) 30504.5** — are not forecasts:
all three sit inside the pre-scan range **30354.3–30688.3**, i.e. price had
already traded them this morning, and none was revisited.

**The honest decomposition of 0.50.** Of 10 rows, **7 lie inside the pre-scan
range** and were therefore already traded before the board printed them under
*"New trading day … everything below is fresh"*. Only **3 were clean forward
objects**: CALL WALL (never reached), PUT WALL (broke and ran), MAX PAIN
(exceeded). The hit rate measures placement, not quality — standing 09-18
caution, 13th consecutive session-context instance.

**P-G, instances #19–#21.** Three *"Low"* rows printed **above** the scan price
carrying *"the next session usually runs the stops below it"*: London Low (today)
30513.4 at **+107**, Asia Low (today) 30504.5 at **+98**, London Low (prev-day)
30423.1 at **+17**. The stops below them had been run before the document was
written. Already PROPOSED.

**Secondary gamma table (P5, still graded by no tool) — 4 of 4 where testable.**
All six shelves carried *"dealers are SHORT gamma here, so they amplify … Not a
floor"*. Upside **30441.8 (1.41bn, +36)** was pierced (post-scan high 30456.8) and
did not hold; downside **30341.8 / 30241.8 / 30191.8** were all sliced on the way
to 29877.9. **30541.8** and **30641.8** were never reached. No counter-instance.
**P5 unchanged, n+1.**

**Fuel paths (H23, instance 11).** *"UPSIDE: mostly clear. First real brake is
30841.8 (436pts away)"* — **never reached**, so no slice/cap data point; the
census stays **8 sliced / 1 capped, n=9 over 7 sessions**, with never-reached now
at 2 (10-12, 10-14). This instance is a **counter-example to H23's sub-claim**:
30841.8 is the CALL WALL and is printed on the board. *"DOWNSIDE path: clear …
every shelf to **29941.8** (464pts, 1.08x ADR) is negative gamma — nothing
structural to slow a breakdown. If it goes, it has room. Do not fade it."* —
**right**, and the corridor terminus landed **63.9** from the session low
(29877.9). But **29941.8 occurs exactly once in the document** (line 107 — not on
the board, not in the secondary table): **3rd instance of the sub-claim**, a
tradeable price the brief never marks.

## 3. What was wrong, and why

### The −18 was right, and it was right for the reason the gamma block gave

`gamma −5` (below flip by 206.7 in short gamma, week net GEX −4.214 →
*"expansion likely"*, `COHERENT_SHORT`: *"Today's ADR can be exceeded — don't cap
the target too early"*) is the best thing in the document. Realised **1.88x ADR**
and a **528.1pt** one-way post-scan leg. `structure −4` was right on both rows:
price never traded back to PD mid, and **PWL 30568.7 was never reclaimed** — the
first win for H10's `−3` branch in **five firings** (previously 0-for-4), and the
reclaim the proposed reclaim-term is designed to catch simply never happened.

**But the call was over-determined, not finely calibrated.** No single row, and
no pair, flips it: removing the entire stale `macro −5` block leaves **−13**,
still STRONGLY BEARISH; removing `news −1` as well leaves **−12**. The engine
reached −18 because **nine of twenty-five rows happened to lean the same way**,
which is a count, not a conviction. That matters for how the number should be
read — see §4 / H26.

### The things that were wrong on a correct day

- **`news −1` is the defect of the day, and it is magnitude, not sign.** A hot
  CPI (3.7%) printed **17 minutes before the scan** and was the proximate cause of
  the pre-scan collapse (the M5 bars run 30600.7 at 12:05Z to 30354.3 at 12:40Z,
  −246 before the document existed). The scorer matched it, signed it correctly,
  and `round(−2.50 / 2) = −1` — **1 point out of 18** for the month's largest
  macro release, the same weight any single bearish keyword match earns. Three
  further headlines describing the same print were left unscored
  (*needs_model_judgement* 59). **This is H19's finding — the news score's
  magnitude tracks match count, not importance — not a new D18 instance: today's
  row was correctly signed, so D18's census stays at 13 headline instances / 7
  trading days.**
- **The CPI was invisible to the events renderer (D24).** Section 5 lists six
  releases **23.7h away** and TSM tomorrow; the release that had already moved the
  index 246pts does not appear, and `event_gate` is `None` under a header that
  says *"The 08:30 ET data lands in here — check the gate before anything else"*.
  This is the worked example D24 has been short of.
- **`macro −5` is three rows and two observations.** `DFII10 −3` and `DGS10 −1`
  both resolve to **2026-10-09**, three business days stale, in a document headed
  *"today"*; the age warning printed on DFII10 and not on DGS10. **H18 / P1
  instance 18, duplication 23 of 23.** The accuracy case stays retracted — the
  pair was right-signed today — but the heaviest block in the document carried
  **4 of its 5 points from one stale observation** while the live driver (CPI) got
  1. **HY OAS rendered no observation date for the 9th consecutive session.**
- **`vol 0` on the widest day in the record, and its only positive row was a
  direction claim.** `VIX9D/VIX 0.773 contango → +1, "calm, mean-reversion
  favoured, mild upward drift"` on a day that fell 662 and realised 1.88x ADR.
  **4th co-occurrence of the gamma-vs-vol conflict, mirrored configuration
  (gamma −2 expansion vs vol +1 calm); gamma right; census 3–1 to gamma** and this
  is its largest margin. **2nd instance** of the 10-08 note that *nothing is
  watching the VIX9D/VIX row's direction points* — wrong on both clauses again.
- **`breadth 0`, and the two rows that pointed up were the stalest in the
  document.** *"mega-cap avg +0.55% (4/4 up)"* and *"NDX −0.31% vs ES −0.34% — in
  line"* are the **previous session's** closes, published into a morning that had
  already given back 334pts. Harmless because both scored 0; recorded as the
  D22-family window complaint.
- **The fuel block told the reader to do the opposite of the regime block, for the
  5th time.** `LOW_FUEL`, 97.6pts: *"The range is close to done … favour **fades**
  over chasing breaks"*, four sections below *"**Fading is the wrong trade
  today**"*. Extension **476.4 = 4.88x** budget. **Census 4–1 to gamma over 5
  instances**, and this is the largest margin on record. The mechanism is at its
  clearest here: the 77.4% of ADR the budget counted as *spent* was the CPI
  reaction, and the model's response to a hot CPI print was to dampen conviction
  in continuation.
- **M6, session 24, at full scale.** All **5** touched rows sit above the close
  (29931.8), so every verdict was decided by `bars[-1]["close"]` before any level
  behaviour was consulted; **3 read "held as resistance"**.

  | level | worst excursion | distance below close | ratio |
  |---|---|---|---|
  | 30423.1 London Low prev | +21.2 | 491.3 | 0.043 |
  | 30402.6 Asia Low prev | +41.7 | 470.8 | 0.089 |
  | 30386.7 PDL ⭐ | +57.6 | 454.9 | 0.127 |
  | 30041.8 PUT WALL | +1.8 | 110.0 | 0.016 |
  | 30011.8 MAX PAIN | +21.3 | 80.0 | 0.266 |

  Mean ratio **0.108**. **Said explicitly as directed: M6's magnitude scales with
  how far the day travelled, and this day travelled 810.4 = 1.88x ADR, the
  largest in the record — so this is the artefact at maximum scale.** On a
  far-travelling day every touched row ends hundreds of points above the close, so
  the ratios are *small by construction*; the low mean is the signature of the
  defect, not evidence against it. **Two "lost" verdicts (30402.6, 30386.7) are
  awarded for upward retraces on levels the day broke downward and closed 455–471
  below.**
- **D25, 24th consecutive pre-NY scan.** *"The dominant strike is **stable** at 0
  across 6 samples"*, three lines under *"⚠️ No volume has traded yet today"*.
  Instance appended, not re-opened. Damage none.

## 4. Change proposals

### PROPOSED — H26 (NEW): the score's magnitude is a RANGE forecast, not a direction forecast, and the label throws that away

**Measured over every gradeable PRE_NY day, 09-24 and the unfinished 10-15
excluded, n=22 days:**

| score magnitude | n | correct | wrong | no-call | mean abs(post-scan move) / ADR | mean range / ADR |
|---|---|---|---|---|---|---|
| 0–2 | 7 | — | — | 7 | 0.18 | 1.10 |
| 3–5 | 4 | 2 | 2 | 0 | 0.24 | 0.94 |
| 6–9 | 5 | **5** | 0 | 0 | 0.35 | 1.02 |
| **≥10** | **6** | **3** | **3** | 0 | **0.78** | **1.39** |

- Spearman(|score|, |post-scan move| / ADR) = **+0.594**
- Spearman(|score|, *signed* move in the called direction / ADR) = **+0.221**
- Spearman(|score|, session range / ADR) = +0.190
- Not a gamma proxy: Spearman(|week net GEX|, |move|/ADR) = −0.138, and the
  partial rank correlation of |score| with |move| **controlling for |week GEX|**
  is **+0.610**.

**Every max-conviction call in the record (|score| ≥ 10), both grading bases:**

| day | score | post-scan | day net | abs(move)/ADR | range/ADR |
|---|---|---|---|---|---|
| 09-14 | −11 | WRONG | +129.3 WRONG | 0.99 | 1.37 |
| 09-15 | −12 | CORRECT | −190.8 CORRECT | 0.47 | 0.77 |
| 09-21 | +13 | CORRECT | +847.7 CORRECT | 1.38 | 2.46 |
| 09-23 | +13 | WRONG | −232.3 WRONG | 0.43 | 1.06 |
| 10-07 | −10 | WRONG | −107.5 CORRECT | 0.29 | 0.79 |
| **10-14** | **−18** | **CORRECT** | **−662.2 CORRECT** | **1.13** | **1.88** |

**Hit rate at the extreme end: 3 of 6 post-scan (50%), 4 of 6 on day net (67%),
n=6.** It is **worse than the 6–9 bucket's 5 of 5** and indistinguishable from a
coin flip. **So: is −18 distinguishable from the −10s? On direction, no — one
observation inside a 50% bucket. On magnitude, yes, and sharply:** the two
largest |score| readings in the record (+13 on 09-21, −18 on 10-14) produced the
two largest ranges in the record (2.46x and 1.88x ADR) and the two largest
post-scan moves (1.38x and 1.13x ADR). The engine is a usable volatility
forecaster and a coin flip on direction once it gets excited.

**What to change.** `bias_engine.py:268` saturates the label at ±10, so −18 and
−10 print the identical words *"STRONGLY BEARISH"* — the brief's vocabulary
discards the only component of the score that carries information, and the word
*"STRONGLY"* promises directional reliability the record does not support.
**Print the measured base rate next to the call** (for |score| ≥ 10: *"direction
3 of 6 in the record; days like this have averaged 1.4x ADR of range"*), and
**size the expected-range language off |score|** rather than only off the gamma
block. **Expected effect: zero change to any score, level, budget or strategy
selection** — it is a label-and-prose change in section 1. **Evidence: 22
sessions.** `track.py` no longer prints `actionable: YES/NO`; this clears the
register's 3-session rule by a factor of seven.

**This also settles H3 negatively and should close its cap branch.** 10-14 is the
**5th max-conviction bearish call printed at a session low** (price 30406.0 sat
**51.7 above the pre-scan low 30354.3**, **15.5% up the pre-scan range** —
geometrically the same setup as 08-24, 09-14, 10-07) and the **first that was
right**, on **both** grading bases, so P-H does not block it. The branch is
**1-for-5**. More importantly, a conviction cap could never have fixed any of the
four misses — capping changes the adjective, not the sign — while it *would* have
suppressed the engine's correct and unusually valuable *range* call on the two
biggest days in the record. **Recommend H3's cap be recorded CLOSED-NEGATIVE and
superseded by H26.**

### PROPOSED — H23 family: the fuel section's "clear corridor" terminus is the best reach estimate in the document, and it is the one number not graded

| day | budget | realised extension | budget err | corridor terminus | realised extreme | terminus err |
|---|---|---|---|---|---|---|
| 10-07 | 158.9 | 61.1 | 2.6x internal disagreement with the 406pt path | — | — | *(register's record, not re-measured)* |
| 10-08 | 115.6 | 326.2 | 2.82x | 30559.6 (398pts) | low 30568.7 | **−9.1** |
| 10-12 | 169.5 | 175.9 | 1.04x | 30643.1 (200pts) | low 30634.7 | **+8.4** |
| **10-14** | **97.6** | **476.4** | **4.88x** | **29941.8 (464pts)** | **low 29877.9** | **+63.9** |

**Three sessions where the corridor terminus landed within 0.15x ADR of the
session extreme while the range budget on the same page was out by 2.8x–4.9x**,
plus the 10-07 instance the register already logged. The terminus is not a
disguised ADR multiple (0.86x, 0.46x, 1.08x of ADR on the three measured days),
so it is carrying real information from the gamma shelves. **Change: grade it
(`review_day` should emit `corridor_terminus` and its distance to the realised
extreme), and print it as the day's reach estimate beside the budget rather than
burying it in a prose bullet.** **Expected effect: zero on any score** —
`path_read()` is prose-only and `bias_engine.py` never imports it; it renders at
`brief.py:558` and `:1024`, so any change must cover both. **No new ID — this is
H23's own corridor branch**, and it cuts the opposite way from H23's brake
sub-claim: the named *brake* is noise (8 sliced / 1 capped), the corridor
*terminus* is not.

### NOT PROPOSED — the board offset. The sell-off hypothesis is FALSIFIED; the breach count is 4, not 3

The pre-registered third-breach test has arrived and was run. **The hypothesis
that the futures-implied cash reference is biased low in a sell-off, so the offset
widens as the market falls, does not survive the record.**

- **The register's drift table starts at 09-30 and therefore omits 09-28's
  45.9.** The breach series against the D6 ~40pt line is **09-28 45.9 · 10-12
  43.1 · 10-14 41.8 · 10-15 77.6 — four, not three.**
- **Direction of the overnight move explains a little; magnitude explains
  nothing.** Across 27 PRE_NY days: down-move days mean offset **+22.7**
  (median 23.4), up-move days **+9.3** (median 8.8) — r(offset, roll) = **−0.361**,
  R² 0.13. **Within the 13 down-move days, r(offset, |roll|) = +0.039.** The
  single largest down roll in the record — **09-14, NQ −525.5** — produced an
  offset of **−12.2**, the opposite sign and near the bottom of the series. A
  correction scaled to the overnight move would have pushed that day's conversion
  the wrong way by tens of points.
- **A time trend dominates.** r(offset, sequence) = **+0.607**, slope
  **+1.68pts per session**, R² 0.37 against the roll's 0.13; in a joint fit the
  roll coefficient halves (−0.034 → −0.023) and the trend survives intact. Staleness
  is not the cause either: all three October breaches sit at the ordinary 992–993
  min overnight age except 10-12's weekend 3874.
- **The pre-registered test itself — measure the breach against the same session's
  cash close — is possible on exactly one of the four, and it fails.** NDX cash
  closed **29950.82** on 10-14; the CFD closed **29931.8**; the realised CFD-minus-
  cash basis at the close was **−19.0**, against a scan-time board offset of
  **+41.8** — opposite sign, gap **60.8**.
- **Extended to the whole record** (prior-day cash close recovered from each
  brief's own `implied − roll`, paired with that day's CFD close): the scan-time
  offset and the same day's realised close basis are **uncorrelated, r = −0.076,
  n = 20, mean |gap| 27.4**. *Caveat stated plainly: the CFD session close is ~45
  min after the 16:15 ET cash print, so the realised basis is a noisy estimator and
  this correlation is attenuated. It is not noisy enough to hide a real effect of
  the size being claimed.*

**Conclusion: the offset is not measuring a CFD-vs-cash basis and it is not a
sell-off effect. No stress correction is proposed, because its only candidate
predictor is falsified and tuning the conversion on a 13-point sample with
r = +0.04 is exactly the failure this register exists to prevent.** The
conversion arithmetic was verified independently on all three October breaches
and was correct each time; there is no contract roll (NQ and NDX day-over-day
agree within ~10pts), so this is not the 09-24 failure mode. **Damage on 10-14:
none** — price was 206.7 below the flip, **4.9x** the offset, so the regime sign
test was never in doubt. **Pre-registered next step:** record the realised
close-basis every day going forward (free — the NDX close is already fetched for
the next morning's roll) and re-test the trend at n=10 clean observations. The
10-12 instance of `|px − flip| < |offset|` stays at **n=1**.

### Appended, nothing proposed

- **P4 / H1 — n=26 days.** 10-14 error **+378.8** (budget 97.6, extension 476.4),
  the **second-largest in the record** after 09-21's +569.2. `track.py` per-day
  mean moves **+17.3 → +31.2** (n=26 incl. 09-24); **ex-09-24, n=25, +31.9** (was
  +17.5). **One day moved the ex-09-24 mean by +14.4**, which is the whole P4
  argument restated. **The statistic is NOT re-derived**: MAE 116.1 vs
  leave-one-out constant 98.3 (n=19); ex-outlier 90.9 vs 75.5 (n=18); sign
  agreement 9 of 19; "no usable skill", **not** "inversely predictive".
  **H1's multiplier branch stays closed.** Traversal **578.9 = 5.93x** budget.
  Today's LOW_FUEL / 97.6pt budget on a 1.88x-ADR day is the single worst
  calibration instance in the record and it changes nothing that was not already
  answered.
- **H2 — third counter-instance; the record is now 3 for the fade / 3 against.**
  LOW_FUEL below the flip, continuation was the trade by 4.88x budget, and the
  three "for" instances remain the directionally-contaminated August/September
  sample. Unproven in both directions, as before.
- **H14 — run-through census extends to n=4 and the band holds.** PUT WALL
  30041.8 broke and ran **163.9 = 0.38x ADR** before any reclaim (series: 0.23 /
  0.31 / 0.48 / **0.38**); **not reclaimed**, closed 110.0 below.
  Resistance-after-break is now **2 for / 2 against**, and today's "for" is the
  least contaminated of them (two re-tests capped at **+1.8** over 225 min). The
  10-14-review proposal to print *"run-through 0.23–0.48x ADR, reclaimed within the
  session 2 of 4"* should carry the updated figures.
- **H22 — n=8.** Week net GEX **−4.214**, *"expansion likely"*, realised **1.88x
  ADR** — the row was right, and on the recent five-day table the ordering is now
  positive (Spearman +0.5, n=5). Over the full graded sample it is still
  **−0.145, n=22**. The 10-08 counterfactual stands; **nothing proposed**.
- **H8 — observation 9 of 10, and the worst.** Record **7 inside / 2 outside**;
  VXN-implied range missed by **405.5** (realised 2.00x), the largest miss in the
  series.
- **H10 — the `−3` branch's first win in five firings** (1-for-5). No reclaim
  occurred, so the proposed reclaim term would not have changed today's call.
  `+3` branch unchanged at 2-for-4.
- **D23 — 11th residual.** Board offset **+41.8** (NDX reference 30364.2, cash last
  traded 2026-10-13T16:14:59, rolled by NQ **−205.2**) vs section-7 offset
  **+20.1** matched to feed time 11:59Z. Gap **+21.7**; CFD move (11:55Z bar open
  **30549.3** → scan 30406.0) = **−143.3**; **residual +165.0**. Series:
  `+190.5 / −201.3 / +203.8 / −7.3 / +2.9 / +246.6 / +203.6 / +209.5 / +345.4 /
  −68.0 / +165.0`. The two conversions agree in sign today, unlike 10-12. Damage
  **none** — section 7 is research-only and no volume had traded.
- **D26 — reporting gap restated, not data loss.** `track.py` reports **26 trading
  days / 29 scans (deduped)**; on disk: **33** day directories, **63** scan JSONs,
  **28** days with a PRE_NY scan, **27** with a `REVIEW.md`, **24** with both. The
  August days remain intact on disk and invisible to the 45-day bar window.
- **Dead-weight audit, n=29 PRE_NY `is_trading_day` scans (09-24 excluded by
  hand).** `macro` yield curve 10y–2y **0 / 29 — still never scored**; both `fuel`
  rows **0 / 29**; `vol` VVIX **2 / 29**; `events` absent or zero throughout (P-C).
  `rates` DXY scored today (**4 / 29**). `macro` NFCI fired −1 for the **5th
  consecutive graded session**. Proposal stays narrowed to the yield-curve row and
  WALCL/RRP. Also unscored today: VXN level, HY OAS, WALCL/RRP, both breadth rows,
  the in-reach-pools structure row, the second `news` row, `events`.
- **H17** — no instance; the call was real and correct, post-scan move 485.9 =
  **60%** of the session range, far outside the 5% deadband. Stays 1 of 3.
- **H4 / H7 / H20 / D21 / P-E / P-E(b) / P3-H6 / P-B(b)** — no instance. The flip
  was never reached (H4); no overnight scan (H7); **H20 stays CLOSED-NEGATIVE and
  is not revived** (the one release that mattered was in the past, which is D24,
  not H20); neither band branch of D21 fired (`gamma +0`, price 46% up the band);
  the CALL WALL was never in play, so P-E and P-E(b) get nothing; no structural
  rows on the board; and no published pair fell in the `merge_tol`/`TOUCH_TOL`
  double-count window.

## Journal hygiene

One scan file for 10-14 (`1247-preny.json` + `.md`), `is_trading_day: true`,
`review_day` reports **0 test artefacts** for the day (6 across the record,
excluded by `track.py`). **09-24 quarantined by hand — 12th consecutive review to
carry it**; there is still no schema `quarantine` field and the 09-29 proposal for
one is reaffirmed (`track.py`'s direction line, 14 right / 6 wrong / 9 no-call,
becomes **13 / 6 / 9** once 09-24 is removed). **2026-10-13 has no journal
directory and none was created, back-dated or inferred. 2026-10-15 is on disk but
unfinished and is excluded from every statistic here.** 09-09 and 09-25 still have
no `REVIEW.md` and none was created. No `prediction` block was touched. No
scoring, wall or grading code was edited. No fabricated or backfilled entries
found. **One new ID allocated by this review: H26. Next free: H27 · D27 · P-I.**

Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01M7sro1DKMp5T7EBDusm6pM
