# REVIEW — 2026-09-08 (Tue)

Reviewed 2026-09-09. Source: `review_day.py 2026-09-08 --json`, `track.py`.
1 gradeable scan (15:39:24Z, NY_MIDDAY). 0 test artefacts. Journal clean.

---

## 1. Scoreboard

**Session (NAS100 CFD, 21:00Z roll, 276 M5 bars)**

| | |
|---|---|
| Open / High / Low / Close | 29578.6 / 29734.1 / 29394.8 / **29496.0** |
| Range / Net | 339.3 / **−82.6** |
| High made | 04:45Z (Asia) |
| Low made | 14:10Z (NY open) |

Both extremes were set **before** the only scan.

**The scan (15:39Z, price 29571.8)**

| | predicted | actual |
|---|---|---|
| Direction | +1 (bias **+4**, MILDLY BULLISH) | **−1** (−83.3 post-scan) → **WRONG** |
| Fuel | EXHAUSTED, budget **26.2**, ADR used 92.8% | extension **0.0** → **about right** (err −26.2) |
| Traversal | — | 146.6 (5.6× budget) |
| Levels | 7 published | 7 touched (hit rate **1.00**); **6/7 (0.86)** on strict touch |

**Direction calls: 0 right / 1 wrong / 0 no-call.**

**Cumulative after this day** — 5 trading days, 11 scans: direction **4 right /
4 wrong / 3 no-call**; mean level touch rate 0.61; H1 per-day budget error mean
**−27.2** (+61.2, −11.6, −73.0, −86.4, **−26.2**).

---

## 2. What the levels actually did

Board span 29530.7–29614.9 = **84.2pts**, inside a 146.6pt post-scan traversal.

| Level | brief said | actually did | verdict |
|---|---|---|---|
| 29614.9 London High (today) | "next session usually runs the stops above it" | **never reached** — post-scan high 29614.1, 0.8 short. Graded "broke DOWN through it" off `travel_up −0.8` | call failed; **grade is an artefact** |
| 29611.6 NY High (prev-day) | "runs the stops above it" | tagged (+2.5), reversed 79.7 | level worked — as a **ceiling**, not as the stop-run the text described |
| 29602.2 **CALL WALL** ●●●●● 1.40bn | "desks must SELL as price rises into it, rallies stall, take profit into it" | pushed 11.9 through, failed, fell 70.3 | **exactly as described — the day's best level** |
| 29574.9 PD mid | "a target to aim AT, not a trigger" | published **+3.1** from spot; true first touch 15:55 | **no information** — a level 3pts from price cannot be a reaction point |
| 29570.3 PD close | "price often comes back to fill a gap from here" | published **−1.5** from spot | same |
| 29552.2 Options shelf 0.46bn | "expect price to stall, take partials" | crossed repeatedly 16:10 onward, `travel_up 58.6 / down 28.2` | **no stall** — descriptive line, not a reaction point |
| 29530.7 NY Low (prev-day) | "runs the stops below it" | 6.7 below, then 80.1 up; held as the floor 16:55–17:50 | level worked — as **support**, the opposite of the published text |

**Findings.**

1. **The three levels that produced clean, tradeable behaviour (29611.6,
   29602.2, 29530.7) all acted as barriers — and two of the three carried text
   that assumed penetration** ("usually runs the stops above/below it"). The
   level was right and the sentence attached to it was wrong.
2. **PD mid and PD close are noise on this scan.** Published at +3.1 and −1.5
   from spot, they cannot discriminate. They are the current best candidates for
   "stop publishing", but two rows on one day is not a case — see §4.
3. **Hit rate 1.00 here means nothing.** `brief.py:359` sizes the board by
   `budget * 1.75`; against a 26.2pt EXHAUSTED budget that is a **±45.8pt
   window**. A ±46pt board inside a 147pt traversal touches everything by
   construction. Level hit rate is **not independent** of the fuel budget.
4. **The levels that mattered most were not on the board.** The same
   `budget * 1.75` cap dropped **PUT WALL 29402.2**, **MAX PAIN 29427.2** and
   **GAMMA FLIP 29405.3** (all ~145–170pts out). The session low was
   **29394.8 — 7.4pts below the put wall, 10.5pts below the flip** — and the
   177pt bounce that carried price up to the scan started there. Not
   forward-gradeable (the low was pre-scan), but it is a direct instance of
   **D7's open question**, one day *before* D7 was found.
5. The brief's own text called 29402.2 *"dealers are SHORT gamma here… price
   accelerates THROUGH rather than stall. **Not a floor**"*. It was the floor.

---

## 3. What was wrong, and why

### The direction call: macro, on data 3 business days old

Bias **+4** decomposed by bucket (`inputs.bias_components`):

```
gamma +2   vol −3   rates 0   macro +6   breadth +1   fuel 0   structure −1   news −1
```

**Strip macro and the score is −2 — the correct sign.** Macro alone flipped the
call, and macro was +6 of a possible +9.

Inside macro: `real_yields` **+3**, `yield_decomp` +1, `credit` **+2**, the rest 0.

- **`real_yields` is the heaviest single term in the whole engine**
  (`bias_engine.py:136`, `_W["real_yields"] = 3`) and it read DFII10 as *"down
  3bp **today**"*. Verified against the FRED API: DFII10's latest observation
  available on 2026-09-08 was **2026-09-03** — a Thursday value printed as
  "today" on a Tuesday, **3 business days stale**. The engine's own comment
  (`bias_engine.py:132-133`) justifies the macro weight with *"FRED publishes
  with a 1-2 day lag"*. Nothing enforces that.
- The staleness was **visible in the same brief**: the `yield_decomp` line
  honestly printed *"(2026-09-02 to 2026-09-03)"*, immediately below a
  "today" that contradicted it.
- **Structural aggravator.** `aligned_change()` exists precisely to stop
  cross-series lag mismatches — and only `yield_decomp` (weight 1) uses it.
  `real_yields` (weight 3) takes DFII10's own `chg_1` with no alignment and no
  age check. **The heaviest term is fed by the stalest series, by construction.**
  Verified live 2026-09-09: `T10YIE` and `BAMLH0A0HYM2` are current to 09-08
  while `DFII10`/`DGS10` stop at **09-04** — a 4-day spread across series the
  engine mixes.
- `credit` **+2** is a *level* test, not a change: `signal = 1 if hyv < 3.0`
  (`fred_probe.py:187`). HY OAS was 2.65%. It has been below 3.0 on every day on
  record — a standing +2 to the bull side, not a signal.

**Systemic, not a one-off.** Decomp interval vs scan date, all 6 gradeable days:

| scan day | FRED interval used | lag |
|---|---|---|
| 08-24 | 08-19 → 08-20 | 4d |
| 08-25 | 08-20 → 08-21 | 4d |
| 08-26 | 08-21 → 08-24 | 2d |
| 08-27 | 08-24 → 08-25 | 2d |
| **09-08** | **09-02 → 09-03** | **5d** |
| 09-09 | 09-03 → 09-04 | 5d |

### The evidence that was right and got outvoted

The engine already held **−6** of same-day, tech-specific bearish evidence:

- `gamma −2` *"price sits in the top 20% of the wall band (29402.2–29602.2)"* —
  price was **84.8%** up that band and turned within 43pts. Correct and
  immediately actionable.
- `vol −3` — VXN 21.68 **+8.2%**, VXN/VIX 1.4 (tech-specific stress). Correct.
- `structure −1` — below PD mid. Correct.

Three current, instrument-specific reads were outvoted by rates data from the
previous week.

### The prose contradicted the score, and the prose was right

§3 of the brief said: *"The day's range is set… Fading the extremes back into
the range is the higher-probability side here, **even when the gamma regime
favours continuation**."* That was exactly correct — extension 0.0, and the
post-scan high at 29614.1 was faded 147pts. The headline said MILDLY BULLISH.
**Two outputs of the same document disagreed and neither acknowledged the
other.** A reader following the headline lost; a reader following the fuel
paragraph won.

### What was *not* wrong

**Fuel was the model's best call of the day.** EXHAUSTED, 26.2pt budget at
92.8% ADR — the range extended **exactly 0.0**. Do not touch the budget on this
day's evidence.

---

## 4. Change proposals

`track.py` prints `actionable: YES` (5 days ≥ 3), but that is a day count, not
evidence. Read per item.

### Proposed — 1 item (a defect, not calibration)

**P1 — FRED observations carry an age and nothing reads it; the brief calls
them "today".**

- *Evidence:* 6 of 6 gradeable sessions, lag **2–5 calendar days**, table above;
  confirmed live against the FRED API on 2026-09-09. `fred_probe.series()`
  already returns the observation `date` — `interpret()` never reads it, and
  `bias_engine.py:134-142` scores `item["signal"]` with no age term.
- *What to change (user decides, I have not edited anything):* (a) render the
  observation date instead of the word "today"; (b) damp or zero a FRED item
  older than N business days. **I am not proposing N** — that is calibration and
  needs its own evidence.
- *Expected effect on 09-08:* `real_yields +3` would not have fired on a
  3-business-day-old print. Bias would have been **+1 or −2** instead of +4, and
  the direction call would have been neutral-to-correct.
- *Why it clears the gate:* this is the **D6 family** — a component justified in
  a comment by an assumed freshness that no code enforces — and D6/D7 precedent
  is that defects are fixed on discovery, not gated. **No new data point is
  needed**: the date is already in the payload.

### Not proposed — still observing

**Macro block weight.** `|macro| ≥ 5` on the **last 5 consecutive deduped
scans** (08-26 13:12 onward), 5 of 11 overall. Macro alone flipped the sign of
the bias on **2 of the 5 gradeable days**: 08-25 13:04 (bullish →
neutral, directionally **right**) and 09-08 (bearish → bullish, **wrong**).
**1–1 is not evidence.** *Watching:* how often macro alone determines the sign,
and its hit rate when it does. Do not touch `_W`.

**`credit` scores a level, not a change.** HY OAS < 3.0 on every day on record →
a constant +2. This is the "component is dead weight" test, but there is no
session yet where HY OAS was above 3.0 or widened >15bp/5d, so I cannot show
what it does when it moves. *Watching:* the first such session.

**PD mid / PD close as noise.** Two uninformative rows on one scan (published
+3.1 and −1.5 from spot). One day. *Watching:* their distance-from-spot at
publication and their reaction grade, across 3+ scans.

### Data points appended to open items (no proposal attached)

- **M4 gains a third graded day — and its worst instance.** 3 of 7 levels were
  admitted by `TOUCH_TOL = 8.0` without price reaching them: 29614.9
  (`travel_up −0.8`, **never touched**, graded "broke DOWN through it"), 29574.9
  (1.9 short), 29570.3 (6.5 short). **For the first time the tolerance changed
  the verdict, not just the timestamp:** starting the 12-bar window at 15:40
  instead of the true first touch at 15:55 gives PD mid `travel_up 39.2` and PD
  close `43.8` → *"traded both sides — chopped"*; from the true touch they are
  **16.5** and **21.1**, both under `REJECT_PTS = 25` → *"broke DOWN through
  it"*. H6's headline result is *"chopped is the dominant outcome"* — on this
  day **2 of its 3 chop verdicts are tolerance artefacts**, and they mask clean
  downside breaks on a day that closed −82.6. **The M4 decision should be made
  before H6 reaches 5 days.**
- **H2's sample does not match H2's claim.** `track.py:208` selects on
  `fuel_state in ("LOW_FUEL","EXHAUSTED")` only; H2's text requires
  *"LOW_FUEL/EXHAUSTED-**at-extreme**"*. Position within the range-so-far at
  scan, for the 6 rows the tracker lists: 18%, 33%, 29%, **5%**, 77%, **52%**
  (09-08). Only 08-24 13:45 qualifies. **H2 has 1 valid observation of 3, not
  6.** Same shape as M3/M4 — a statistic tallied off a filter that does not
  implement its own definition. **09-08 should not be counted toward H2.**
- **H1's 5th point breaks the monotone run** (+61.2, −11.6, −73.0, −86.4,
  **−26.2**). The four-point slope H1 refused to fit a multiplier to is gone;
  the series now looks noisy around −27.2 rather than trending — which
  *strengthens* H1's existing "do not fit a multiplier" conclusion. Note this
  point is **low-information**: a NY_MIDDAY scan at 92.8% ADR with both extremes
  already set can only score near-zero extension.
- **H4 — 5 of 5 days now recorded, still weak.** Flip 29405.3, close 29496.0 →
  **90.7pts**. Series: 1.1 / 236.6 / 255.2 / 599.8 / 90.7 — one hit, four
  misses. Do not use the flip as a target.
- **H12 — first live trading-day observation (1 of 5).** GEXBot volume lens
  29,452–29,592; OI lens 28,992–29,267. Post-scan range **29,467.5–29,614.1**.
  The volume band bracketed it to within 16–22pts; **the OI band sat entirely
  outside the day**, ~200pts below the session low. Our own CBOE call wall
  (29,602.2) agreed with the volume lens to 10pts and marked the post-scan high.
  One session, post-hoc, and the OI book was mid-roll. **Proves nothing.**
- **D7's open question — second instance.** `budget * 1.75` = 45.8pts against a
  339.3pt day dropped put wall, max pain and flip; the wall/flip cluster marked
  the session floor to within 7–11pts. D7's fix (footnote partition) landed
  09-09, so this is evidence for the **open question** — should a wall be
  subject to a range-budget filter at all — not for the fix.
- **New measurement note (for the register): level hit rate is not independent
  of the fuel budget.** `keep()` sizes the board by `budget * 1.75`, so an
  EXHAUSTED day publishes a narrow board and scores a high hit rate almost by
  construction. 09-08: board span 84.2, traversal 146.6, hit rate 1.00 (0.86
  strict). H6 should normalise by board span ÷ traversal, or it will read
  "levels are working" hardest on the days the board says least.

### Standing items unchanged

M3, M4, M5 remain **awaiting the user's decision**. Nothing here supersedes
them; M4 gained evidence, listed above. No scoring file was edited.
