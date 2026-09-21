# REVIEW — 2026-09-18 (Fri, quad-witching week expiry)

Graded 2026-09-21 from `review_day.py --json` (resolved to 2026-09-18) and
`track.py`. **1 gradeable scan** (12:47:28Z PRE_NY). **0 test artefacts.**
`is_trading_day: true`.

**Journal integrity: clean.** `1247-preny.json` is in commit `ba08973`, authored
`2026-09-18T12:47:33Z` — five seconds after its own `scan_utc: 12:47:28Z`. Not
backfilled, not fabricated. No `is_trading_day: false` scan exists on this date,
so nothing was excluded on that ground. `outcome` is still `null`; every actual
figure below comes from `review_day.py`, not from the journal's own claims.

---

## 1. Scoreboard

| | |
|---|---|
| Session O / H / L / C | 29435.6 / **29704.2** / 29359.6 / **29670.5** |
| Range / net | **344.6** / **+234.9** (net = 68% of range) |
| ADR14 | 383.5 → range was **0.90x ADR** |
| Bars | 275 |

**Direction** — **1 right / 0 wrong / 0 no-call.**
Scan 12:47Z PRE_NY, bias **+4 MILDLY BULLISH**, `expected_direction +1`.
Post-scan move **+174.4** → **CORRECT**.
Running record: **10 right / 7 wrong / 6 no-call** (14 trading days, 23 scans).

**Levels** — 9 published, **7 touched, hit rate 0.78** (14-day mean 0.54).
All 7 touched levels graded `held: true` and `acted_as: support`. The 2 untouched
(`GAMMA FLIP + NY Low` 29316.8, `MAX PAIN` 29294.3) were both labelled
_(stretch)_ in the brief — honest, not a miss.

**Fuel** — budget **65.6**, actual range extension **26.7**, error **−38.9**,
`fuel_call: about right`. Ratio extension/budget **0.41**. Traversal 332.7 =
**5.07x** budget, inside the range. H1 per-day series now n=14, mean **+1.9**.

---

## 2. What the levels actually did

Seven for seven held as support. That is the highest held-rate in the journal —
and it is also the least informative possible outcome, because **every published
level was at or below the scan price on a day that went up 174pts.** A level
below price on an up day is not being tested as a level; it is being left behind.
The 0.78 hit rate is real but it grades a board that had one genuine job — the
ceiling — and got that one wrong.

| level | brief said | what happened | verdict |
|---|---|---|---|
| **29566.3** Equal highs ×2 | *"2 touches at this price, **never traded through** — a real stop cluster. **Prime S1 sweep trigger**"* | Traded through at 18:50 and **held as support** for 70min (worst −5.1). Close 29670.5 is **104pts above it** | **The factual claim was invalidated the same day.** The sweep did not fail — it succeeded and kept going. No S1 setup ever appeared |
| **29519.3** CALL WALL ●●●●● 4.72bn + shelf ⭐ | *"Heaviest ceiling this week (13k contracts) — desks must SELL as price rises into it, so **rallies stall. Take profit into it.**… the **strongest ceiling on the board**"* | First touch 13:25, chopped, then **held as support** 130min (worst −17.3). Session high **29704.2 = 185pts above it**; close **151pts above** | **The headline finding.** The strongest ceiling on the board produced a 17pt stall against a 185pt run-through. "Take profit into it" at +17 would have surrendered the day's remaining 174pts |
| **29500.5** PDH + NY High ⭐ | *"the biggest pile of stops above us. Sweep it, wait for a lower high on the 1m, then **CISD = short**"* | Touched 12:50 (−2pts away at scan), chopped both sides, held as support 135min (worst −11.9) | **The explicit short instruction was the wrong side of a +174 move.** The sweep happened; the lower high did not |
| **29478.9** London Low (today) | *"the next session usually runs the stops below it"* | Broke **UP** through it, held as support 155min (worst −3.8) | Stops were never run. Directionally inverted, though harmless |
| **29469.3** Options shelf 2.36bn | *"expect price to stall… take partials rather than push through"* | Broke **UP**, held as support 160min (worst −5.0) | Stalled by 5pts. Technically "friction", practically noise |
| **29431.6** London High (prev) + PD close ⭐ | *"the next session usually runs the stops above it"* | Held as support 245min, 4 re-touches, worst −6.8 | **Best level on the board.** Four tests, 6.8pts of give, for 245 minutes |
| **29419.3** PUT WALL ●●●○○ 2.39bn | *"expect a bounce and a good long-sweep here… strongest floor on the board"* | Broke **UP** through it, held as support 255min (worst −5.9) | **Right for the wrong reason.** It was a floor — but price was already above it and never came back to sweep it. The "long-sweep" entry never triggered |

**The level nobody needed:** `29469.3 Options shelf 2.36bn` sits **9.6pts** from
London Low 29478.9 and **12.3pts** from the PUT WALL/London-High pair below. Five
of the nine levels are inside the 100pt band 29419.3–29519.3. With `TOUCH_TOL` at
8pts these are not independent observations — one 10-point wiggle at 13:00
"touched" three of them within five minutes (13:25 / 12:55 / 13:00). This is the
denominator pollution **P-B(b)** was opened for, now with a clean instance.

---

## 3. What was wrong, and why

The direction call was right, so the failures are in **conviction** and in **the
board**. Two components voted against a correct call for mechanical reasons, and
both are known defects.

### 3a. The call was right and the engine understated it by 4 points

`bias_components` net **+4**. Two of the negative rows are defects already on
file, not judgements:

| pts | component | why it is not a judgement |
|---|---|---|
| **−3** | `macro` — DFII10 real yield | The `why` string **says so itself**: *"⚠️ FRED has not published since 2026-09-16 (2 business days ago) — this is last week's reading, not today's."* A component voted its single largest available weight on data it had just flagged as missing. **H18, sixth instance.** |
| **−1** | `news` — *"3 auto-scored (0 bull / 3 bear) → MILDLY BEARISH"* | **All three headlines say equities went UP.** Reproduced below. **D18, fourth day.** |

Strip those two and the score is **+8 / BULLISH** instead of **+4 / MILDLY
BULLISH** — on a day that closed +234.9, 68% of its range, in the called
direction. **The damage is not a wrong label, it is a suppressed one.** The
engine's genuinely current, instrument-specific evidence (`vol +3`, `breadth +3`
from mega-caps 4/4 up and NDX +1.73% vs ES +0.82%) was diluted by a stale FRED
print and three misread headlines.

**D18 reproduced from source on today's exact headlines:**

```
'Stock Market Today (Sept. 18, 2026): Nasdaq futures rise after Fed rate hike lifts stocks'
   -> rule=hawkish  direction=-1  confidence=HIGH  flags=[]  weighted=-1.8
"What the Fed's interest rate hike reveals about Warsh, Trump and inflation - CBS News"
   -> rule=hawkish  direction=-1  confidence=HIGH  flags=[]  weighted=-1.8
'Exchange-Traded Funds, Equity Futures Higher Pre-Bell Thursday Amid Economic Data, Fed Rate Hike'
   -> rule=hawkish  direction=-1  confidence=HIGH  flags=[]  weighted=-1.8
```

Headline 1 contains the word **"rise"** and headline 3 contains **"Higher"**, in
their own titles, and both were scored bearish at HIGH confidence with zero
flags. Same mechanism as filed: `hawkish` (line 71) wins the first-match race
over `risk_on` (line 109), and `risk_on` is absent from `HIGH_CONFIDENCE` so it
could not have voted even if reached.

**A second, separate defect in the same block:** headline 3 reads *"Pre-Bell
**Thursday**"*. It is Thursday's story, scored on Friday with
**`freshness: 1.0`** — full weight. That is not D18 (wrong sign); it is a
staleness failure in the freshness field itself. n=1, new today.

### 3b. `gamma −2` "top 20% of the wall band" — first instance AGAINST

This row has been the sharpest single component in the journal: correct and
outvoted on **08-28** (price turned after running 103pts through the wall),
correct on **09-08** (price 84.8% up the band, turned within 43pts), and named
*"the sharpest row on the page"* on **09-17**.

Today it was **wrong**. Price sat in the top 20% of 29419.3–29519.3 and, rather
than showing poor risk/reward for longs, **left the band upward and never came
back** — the band's top became the day's floor. Record now **3 for / 1 against**.
One counter-instance does not overturn three; it is logged so the row is not
treated as infallible.

### 3c. The regime prose called the wrong kind of day

The brief led with `COHERENT_LONG`, *"This is your fade day"*, *"Expect a tight,
pinned range… Keep targets modest; **breakouts mostly fail**"*, and Strategy 1
(sweep → failed re-break → reversal).

The range genuinely was contained — **0.90x ADR**, and the fuel read was right.
But net move was **68% of range**: a trend day, not a chop day. Every sweep on
the board succeeded. **Pinning constrains the range; it does not make the day
directionless**, and the prose conflates the two. Checked against the record
before claiming a pattern: range-ratio vs |net|/range across the graded days
(0.78→38%, 0.78→68%, 0.90→68%, 0.97→35%, 1.27→55%, 1.33→69%, 1.37→27%,
1.38→0.2%, 1.47→82%) shows **no relationship at all** — mean ~52% for sub-ADR
days vs ~47% for above-ADR days. So "small range implies chop" is unsupported in
either direction. Recorded as negative evidence so it is not rediscovered.

---

## 4. Change proposals

`track.py`: **14 trading days, 23 deduped scans — threshold met** for the 3-day
hypotheses. One material proposal.

### P-E (NEW) — the call wall's prose asserts a lid; the record says it is bimodal

**What to change.** Prose and board construction only — **no scoring change**.
Replace the unconditional *"rallies stall. Take profit into it"* with the record:
that this level either caps hard or fails outright, and promote the failure
branch out of the final clause where it currently hides.

**Evidence — 7 tested call-wall instances over 14 trading days**, all figures
from prior REVIEW.md files, not recomputed:

| day | outcome | overshoot / run-through |
|---|---|---|
| 08-26 | capped | *"best call of the day"* |
| 09-08 | capped | +11.9 through, failed, fell 70.3 |
| 09-11 | capped | **+9.6** overshoot, held 485min |
| 09-14 | capped | **+3.6** overshoot, held 475min |
| 08-27 | **sliced** | closed **+79** above, traded **+154** above |
| 08-28 | **sliced** | ran **+103** through |
| **09-18** | **sliced** | ran **+185** through, closed **+151** above |
| 09-15, 09-16 | never reached | untested, excluded |

**The distribution has no middle.** When it caps, overshoot is **3.6–11.9pts**.
When it fails, the run-through is **103–185pts**. There is no instance between
12 and 103. A reader told "rallies stall, take profit into it" is being given a
point estimate for a variable that is **4 capped / 3 sliced with a ~15x gap
between the two modes** — the single worst shape of distribution to describe with
one sentence.

**This is not new analysis.** The 08-27 review already wrote *"In a long-gamma
regime a call wall is a brake, not a lid — dealers sell into it, which slows a
rally; it does not stop one. I described it as though it would stop one."* That
was filed as a prose self-criticism and never given a count. It now has one, and
today is its third and largest instance.

**Expected effect.** No change to any score or hit rate. It stops the board
issuing a directional instruction ("take profit into it", and on 09-18 also
"CISD = short" at the PDH) whose base rate is 4/7 — and on the 3 failure days
that instruction was on the wrong side of moves of 103, 154 and 185 points.

**Explicitly NOT proposed: a rule to predict which mode.** The obvious candidate
is breadth — today was `breadth +3`, mega-caps 4/4 up, NDX leading ES, on a slice
day. But 09-08 held with a positive bias too, so the split is not clean, and
fitting a discriminator to 7 points with a 4/3 split is exactly the noise-tuning
the standing rule forbids. **Named as the thing to watch, not proposed.**

### Logged, not proposed

- **D18, fourth trading day** (08-24, 09-11, 09-17, **09-18**), now **8 headline
  instances**. Reproduced from source again today, on headlines containing "rise"
  and "Higher". Threshold long met and the fix is small — but the standing reason
  to defer is unchanged: it alters a **scoring input** and **H19's hand-score test
  is still unrun**, so changing the scorer now destroys H19's baseline. Appended
  to D18. **Still recommend fixing when H19 resolves or when `news_scorer.py` is
  next opened, not before.**
- **H18 / P1, sixth instance.** DFII10 voted **−3** while its own `why` string
  declared the data 2 business days stale. Sequence: `09-10 0, 09-10 0, 09-11 −3,
  09-11 −3, 09-14 −3, 09-14 −3, 09-15 −3, 09-16 0, 09-17 −3, 09-18 −3`. Damage
  today: **label suppressed one notch** (+4 MILDLY BULLISH vs +8 BULLISH) on a
  correct call — the first instance where the stale row cost conviction on a day
  the engine got right. P1 already covers it; **no new proposal**.
- **`gamma −2` wall-band row: first instance against** (3 for / 1 against). §3b.
  n=1 against; watching.
- **H1.** Today −38.9, a fourth consecutive under-read in the `>0` bucket by sign
  pattern but well inside the spread. Per-day mean moves to **+1.9 (n=14)** — the
  aggregate is now essentially **zero**, which is the strongest argument yet
  against any global multiplier. Appended; **P4 not re-proposed.**
- **Level clustering / `TOUCH_TOL`.** 5 of 9 levels inside a 100pt band, 3
  "touched" within 5 minutes by one wiggle. Clean instance for **P-B(b)**; folded
  into that proposal rather than raised separately.
- **News `freshness: 1.0` on a headline whose own title says "Thursday"**, scored
  on Friday. **n=1, new.** Distinct from D18 (that is sign, this is age). Watching
  — if it recurs twice more it is a one-line fix in the freshness computation.
- **`events` scored 0 again** — now **16 of 16 rows**, including expiry Friday of
  a quad-witching week. Mechanism behind **P-C**; not separate.
- **Max pain's day-of-week qualifier** (*"weak on a Monday, strong by
  Thursday/Friday"*): **never reached on a Friday**, which is the day the
  qualifier claims it is strongest. Third instance, and the three contradict each
  other in different directions (strong Wed, missed Thu, missed Fri). Mixed
  evidence is not evidence. n=3 but **incoherent — not proposable.** Watching.

### Considered and rejected

- **Anything from the 0.78 hit rate or the 7/7 held rate.** Every published level
  was at or below the scan price on a +174pt day. The board was not tested; it was
  outrun. Grading it as a 78% success is the mirror image of 09-16's 0.95 hit rate
  on a day when 16 of 18 levels were lost — **hit rate is measuring level
  placement relative to price, not level quality.** No claim either way.
- **Dropping `Options shelf 2.36bn`** as a never-reacted level. It did react
  (−5.0, 160min). The objection is that it is 9.6pts from another level, which is
  P-B(b)'s business, not a delisting.
- **Any claim that "pinned range" predicts chop.** Tested against all 9 graded
  days in §3c and the relationship is absent. Rejected on the evidence, including
  my own initial reading of it.
- **Re-proposing the D18 fix on strength of a 4th day.** The blocker was never
  the evidence count; it is H19's baseline. More evidence does not unblock it.
