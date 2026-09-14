# REVIEW — 2026-09-11 (Fri)

Reviewed 2026-09-14. Source: `review_day.py 2026-09-11 --json`, `track.py`.
2 gradeable scans (12:47:08Z PRE_NY, 13:24:06Z PRE_NY). 0 test artefacts.
Both `is_trading_day: true`. Journal clean for this day — no fabricated or
backfilled entries. (The 1324 files carry a 2026-09-14 mtime; that is the
archive commit `f2330d7`, not a rewrite — `scan_utc` and content are consistent
with a live 13:24Z build.)

---

## 1. Scoreboard

**Session (NAS100 CFD, 21:00Z roll, 275 M5 bars)**

| | |
|---|---|
| Open / High / Low / Close | 29118.0 / 29475.8 / 29018.3 / **29370.1** |
| Range / Net | **457.5** / **+252.1** |
| Range vs ADR14 (359.7) | **127.2%** |

**The scans**

| | 12:47Z PRE_NY | 13:24Z PRE_NY |
|---|---|---|
| Bias | −7 BEARISH | −6 BEARISH |
| Shape | COHERENT_LONG | COHERENT_LONG |
| Price at scan | 29336.2 | 29404.5 |
| Post-scan move | **−1.1** | −32.9 |
| Direction | CORRECT | CORRECT |
| Fuel state / budget | EXHAUSTED / 8.4 | EXHAUSTED / 0.0 |
| Actual extension | **97.1** → **UNDER by +88.7** (11.6×) | 0.0 → err 0.0 |
| Traversal | 164.3 (19.6× budget) | 164.0 |
| Levels published / touched | 5 / 3 = **0.60** | 4 / 0 = **0.00** |

**Direction calls: 2 right / 0 wrong / 0 no-call. Mean level hit rate 0.30.**

**Read the 2/2 with the range figure beside it.** The index closed **+252.1**
and the scoreboard records two correct BEARISH calls, because both scans landed
near the high. The 12:47 call is graded on a **−1.1pt** move — **0.2% of the
day's range**, and the smallest graded move in the journal by a factor of 30
(next smallest 7.2%, also today; every other graded scan is 19.7–76.7%).
`review_day.py:204` takes the sign of the move with no magnitude deadband.

**Cumulative** (`track.py`, verbatim) — 7 trading days, 11 deduped scans:
direction **6 right / 3 wrong / 2 no-call**; levels touched 0.56; H1 per-day
budget error mean **−22.7** (−73.0, −86.4, −10.7, −26.2, −64.0, +57.3, **+44.3**).
See §4 for why that 7-day denominator is wrong.

---

## 2. What the levels actually did

**The 12:47 board — 3 of 5 touched, and the two that mattered were near-perfect.**

| Level | brief said | actually did | verdict |
|---|---|---|---|
| 29466.2 **CALL WALL** ●●●●● 1.54bn | "desks must SELL as price rises into it, so **rallies stall. Take profit into it**" | touched 13:00, held as resistance **485min**, worst excursion **+9.6pts**. Session high 29475.8 | **worked as written.** The strongest ceiling call in the journal — 9.6pts of overshoot on a 457pt day |
| 29339.1 Asia Low (prev-day) | "the next session usually runs the stops below it" | first touch broke UP; later lost by **27.6pts**, then reclaimed and closed above | **half right.** The stop run happened (−27.6) but the level did not hold as a floor and did not define the day. Published **+2.9** from spot, so it cannot discriminate anyway |
| 29312.4 **GAMMA FLIP** | "We're ABOVE it: they're damping, so fades work. **Lose this and hold below and that reverses**" | touched 14:45, held as **support 485min**, worst excursion **−0.9pts** | **worked as written**, and the conditional never fired. 0.9pts of violation is the tightest hold on record |
| 29291.2 MAX PAIN | "price drifts toward it as the week goes on… strong by Thursday/Friday" | **never reached** (45pts below spot on a Friday) | the one direct test of the Friday claim, and it failed |
| 29018.3 PDL + Asia Low + Equal lows ×2 + **PUT WALL** ●●●●● ⭐ | "**expect a bounce and a good long-sweep here**… strongest floor on the board" | **never reached** — 318pts below spot, and the low was already in from Asia | untestable as published |

**The 13:24 board — 0 of 4 touched, and that is the finding of the day.**
Nearest level was 131pts away; nothing was reached in the remaining ~7.5 hours.
It was not an unlucky board — it was the *same market* re-read 37 minutes later,
and the re-read moved every level away from price (§3).

Cross-day context, unchanged by today: **CALL WALL 8/13 touched over 7 days
(62%); PUT WALL 3/13 over 5 days (23%)**. Today adds a fifth session in which
the put side was published far from price and did nothing — consistent with
H11's "the put ladder is the half that does not work". No proposal; H11 owns it.

---

## 3. What was wrong, and why

### 3.1 The gamma block was re-read 37 minutes later and disagreed with itself

Not a market move. The chain snapshot:

| | 12:47Z (08:47 ET) | 13:24Z (09:24 ET) | change |
|---|---|---|---|
| price | 29336.2 | 29404.5 | +68.3 |
| **gamma flip** | 29312.4 | 29034.5 | **−277.9** |
| call wall | 29466.2 | 29648.0 | +181.8 |
| put wall | 29016.2 | 28998.0 | −18.2 |
| net GEX 0-2DTE | 0.643 | 3.887 | **6.0×** |
| net GEX this week | 1.81 | 8.119 | **4.5×** |
| **net GEX full 45DTE** | **0.599** | **8.131** | **13.6×** |
| 45d call-wall contracts | 59k | 120k | **2.0×** |
| CFD/index offset | +16.2 | −2.0 | −18.2 |

A 45-day book cannot change 13.6× in 37 minutes, and its call wall cannot take on
61k contracts pre-open. **The 12:47 build read an incomplete chain.** Both briefs
printed `Data age: NDX chain …12:40:23` / `…13:23:05` — the freshness check passed
on both. There is a freshness gate and **no completeness gate**. This is D6's
failure mode ("a FRESH timestamp on a STALE price inverted the regime call")
reappearing on contract counts instead of price.

**−277.9pts in 37 minutes is the largest sub-hour flip move in the journal**,
larger than the 192pt/2min anomaly H7 records. Consecutive-scan drift, all days:

```
08-24 08:28→08:30   2min   dPrice  +8.9   dFlip +192.0   ratio 21.6
08-26 21:43→22:11  28min   dPrice +12.7   dFlip +167.4   ratio 13.2
09-11 12:47→13:24  37min   dPrice +68.3   dFlip -277.9   ratio  4.1
(all other pairs under 60min: 0.4 – 23.5pts)
```

**And today it is the first time the cost is measurable.** The 12:47 flip
(29312.4) held as support for 485 minutes with a 0.9pt worst excursion. The
13:24 revision moved it to 29034.5 — 370pts below spot, never touched. The
engine discarded a level that was working perfectly and replaced it with one
that never mattered. H7 has argued the flip is *unstable*; today shows the
revision **destroys information**, which is a stronger claim.

Uncomfortable and stated deliberately: the **thin** chain produced the better
board. 12:47 nailed the high to 9.6pts and the support to 0.9pts; the fuller
13:24 chain missed the high by 172pts. One day does not settle which snapshot is
truer, and §4's proposal is not "the early board is wrong" — it is "a number
that moves 13.6× in 37 minutes is not a measurement the model should vote on
as though it were."

### 3.2 The bias score was not the problem, and neither component moved the day

Both scans: `news −4`, `macro −3 (DFII10)`, `vol −4`, `rates −2/−1`. Direction
was called correctly-by-sign on moves of −1.1 and −32.9, so **no component can
be credited or blamed on this day's direction** — the day was flat from both
scan points and the −7/−6 conveyed conviction the outcome does not support.

Two things did misfire inside the score:

**`macro −3` is the largest single component in both scans and it is 2 business
days stale** — DFII10 as of 2026-09-09, with the brief's own ⚠️ saying so. This
is P1 verbatim, third session running. Not new; recorded as continuing.

**The straddle rider added conviction while its text removed it.** At 12:47
price was 23.8pts above the flip (0.081%), inside the 0.15% threshold, so
`bias_engine.py:86-89` fired:

```python
if abs(dist_pct) < 0.15:
    add("gamma", +1 if px > gf else +1,
        "but price is straddling the flip (<0.15%) — regime unstable, "
        "reduce conviction")
```

`+1 if px > gf else +1` is a **no-op ternary** — both branches are `+1`. Above
the flip it is added to `+2`, so gamma reads **+3**: "reduce conviction" made the
bullish gamma vote 50% *larger*. Below the flip it softens `−3` to `−2`, which is
the intended behaviour. The sign is almost certainly meant to be
`-1 if px > gf else +1`.

Consequence today: gamma totalled **+5** on the scan straddling the flip by 23.8pts
and **+4** on the scan sitting cleanly 370pts above it. Being *less certain*
scored *more*. Every historical firing has the same sign:

```
2026-09-09 15:17  px 29397.5  flip 29392.5  above  +1
2026-09-09 15:20  px 29418.8  flip 29403.1  above  +1
2026-09-11 12:47  px 29336.2  flip 29312.4  above  +1
```

3 firings, 2 distinct trading days, all above the flip, all wrong-signed. It did
not flip a label on any of them (−7 would have been −8 today), so the impact so
far is conviction magnitude, not direction.

### 3.3 The fuel grade on the second scan is a free pass

12:47 was a genuine miss: budget **8.4**, actual extension **97.1**, under by
88.7 (11.6×) — the engine called EXHAUSTED at 97.7% of ADR and the range then
added another 27% of ADR.

13:24 is graded **"about right"** with `fuel_extension_vs_budget: null`. Budget
was 0.0 and extension was 0.0 — but extension was 0.0 only because
`range_at_scan` (457.5) already equalled the full session range. **A zero budget
scored against a session whose high and low were both already set cannot be
wrong.** track.py logs it as `err 0.0`, indistinguishable from a genuine
bullseye. 09-08, 09-09 and 09-10 15:07 have the same shape (budget 0.0 or near,
extension 0.0). This inflates H1's accuracy with observations that carry no
information.

---

## 4. Change proposals

### P-A (PROPOSE) — gate the gamma block on chain *completeness*, not just freshness

**Evidence — 3 distinct trading days.** Every early scan in the journal reports a
45DTE net GEX an order of magnitude below the same day's later scan:

| day | early scan | 45DTE GEX | later scan | 45DTE GEX |
|---|---|---|---|---|
| 2026-08-24 | 08:28–08:33 (×4) | **0.024** (byte-identical ×4) | 09:37 | −5.48 |
| 2026-09-10 | 08:12 | **1.114** (wk −0.058) | 15:07 | −4.645 |
| 2026-09-11 | 12:47 | **0.599** | 13:24 | 8.131 |

Scans taken after ~13:00Z are stable against each other on the same day
(08-27 13:23 / 13:41 / 13:43 → 11.925 / 11.773 / 11.817).

**It explains two open items rather than adding a third.**
- *H7's headline anomaly.* On 08-24 08:28→08:30 the 45DTE GEX is **identical to
  three decimal places** (0.024) while the flip moves **192pts** on 8.9pts of
  spot. Same chain, different spot, wildly different flip — that is what a
  repriced zero-crossing does on a near-empty book: the gamma profile is flat,
  so the root is ill-conditioned. H7 currently calls this "possibly a cold-start
  artefact"; this is the mechanism.
- *D8's trigger.* D8 fired on 2026-09-10 08:12 because `net = -0.058` sent the
  strategy selector into its `net <= 0` catch-all. That −0.058 is the empty-chain
  reading; by 15:07 the same day it was −3.795. **D8's stated condition was an
  artefact of an incomplete chain, not a market state.**

**What to change.** Add a completeness gate beside the existing age check —
total contracts in the 45DTE chain (or `abs(full_45dte)`) against a trailing
median for that symbol. When it fails, withhold the flip-derived votes and label
the walls provisional, reusing the mechanism `flip_unreliable` already
implements for OVERNIGHT (`bias_engine.py:70-77`) rather than inventing a new
weight.

**Expected effect.** Removes the ±5-point gamma swing H7 has priced twice; stops
the strategy selector branching on a near-zero that means "no data yet"; makes
the "Data age" line honest about what it does not check. **Cost, stated plainly:**
today's 12:47 board would have been gated, and that board was the day's best. The
gate should suppress *votes and regime labels*, not the level board itself.

**Decision required — do not implement without the owner.**

### P-B (DEFECT, not calibration) — fix the no-op ternary at `bias_engine.py:87`

`+1 if px > gf else +1`. A code error, not a tuning preference, so it is not
gated on 3 sessions — logged as **D16** in HYPOTHESES.md alongside D8/D14/D15.
Fix is one character of intent: `-1 if px > gf else +1`. Expected effect: the
straddle rider reduces the magnitude of the gamma vote from either side, as its
own text promises. Historical impact is small (3 firings, 2 days, no label
change); the reason to fix it is that the printed rationale and the arithmetic
currently contradict each other.

**Decision required — I have not touched the file.**

### P-C (PROPOSE) — track.py is excluding a gradeable day and H1's headline may flip sign

`track.py` reports "**7 trading day(s), 11 scans**" and "6 entries marked
test_artefact". Only **2** files in the journal carry an artefact flag
(09-09 1513 `defective_build`, 09-09 1517 `verification_rerun`). Two gaps:

- **2026-08-24 — 8 clean scans, `is_trading_day: true`, no artefact flag —
  is absent from every statistic.** Cause: `review_day.py 2026-08-24` returns
  `{"error": "no NAS100 bars for 2026-08-24", "scans_found": 8}`. The M5 history
  aged out of the feed. This is the day that produced H7's 192pt/2min anomaly and
  D12's evidence, and it is now permanently ungradeable. **Bars should be
  snapshotted into the journal at grade time**, otherwise every day silently
  expires. Cheap, local, no new external data source.
- **2026-08-25 is held back by track.py and gradeable by review_day.py.**
  track.py prints "HELD BACK - day not finished … 98 bars so far"; review_day.py
  grades it in full: `O 29260.9 H 29342.6 L 29086.1 C 29212.9`, 430-minute holds,
  direction 1 right / 0 wrong / 1 no-call. Two graders, two answers about the
  same day.

**Why it is material.** 08-25's fuel error is **+219.8** (budget 12.0 vs
extension 231.8) — larger in magnitude than any of the seven days currently in
H1's mean of **−22.7**, and the opposite sign. Adding one day of that size to a
seven-day mean is capable of turning H1's headline from "the model over-budgets"
to "the model under-budgets". **I have deliberately not recomputed H1** — the
point is that track.py must, once the held-back day is admitted. Until then,
**H1's −22.7 should not be quoted as settled**, and the 09-10 review's "8
trading days, 15 deduped scans" does not reconcile with today's "7 / 11" either.

### Observed, NOT proposed — logged to HYPOTHESES.md

- **No magnitude deadband on the direction grade.** Today's 12:47 CORRECT rests
  on 0.2% of the day's range. Clear instances: **one trading day** (both of
  today's scans). One session is noise. Watching whether sub-5%-of-range graded
  calls recur; if they do, the grade should read `no call (inside noise)`.
- **Zero-budget scans score `err 0.0` automatically** when `range_at_scan`
  already equals the session range (today 13:24; also 09-08, 09-09, 09-10 15:07).
  Watching whether excluding them changes H1's mean. Entangled with P-C — do not
  act on either alone.
- **MAX PAIN on a Friday.** The brief claims it is "strong by Thursday/Friday";
  today it was 45pts away and never reached. Journal-wide MAX PAIN is 3/8 touched
  over 4 days. Not enough to stop publishing it (H6 needs 5 days, and touch rate
  is confounded by publication distance). Watching.
- **P1 (stale DFII10 carrying the heaviest macro weight)** — third consecutive
  session. No new proposal; the item is already open.
