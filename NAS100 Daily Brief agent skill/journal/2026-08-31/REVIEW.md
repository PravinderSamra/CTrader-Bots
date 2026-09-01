# REVIEW — trading day 2026-08-31

Graded 2026-09-01, after the 21:00 UTC roll on 08-31. **One gradeable scan**
(13:28 PRE_NY). No `test_artefact` entries in this day, `is_trading_day: true`,
committed by the normal archive flow (`d050d3d`) — the entry is genuine.

Graded a day late: 08-31 had no REVIEW.md when the 09-01 brief ran. The 09-01
scan is held back by `track.py` (day unfinished) and enters nothing here.

---

## 1. Scoreboard

Trading day = 2026-08-30 22:00 UTC → 2026-08-31 20:55 UTC (276 M_5 bars).

| | |
|---|---|
| Open / High / Low / Close | 29464.7 / 29489.5 / 29223.8 / **29465.5** |
| Range | 265.7 |
| Net | **+0.8** |
| Direction call | 13:28 BEARISH −7 · price +78.5 from scan → **WRONG** |
| Level hit rate (from scan) | **0.60** (6/10) — non-stretch **6/7 = 0.86**, stretch **0/3 = 0.00** |
| Whole-day retro | 8/10 reached · settled roles: 2 resistance, 5 support, 1 no role |
| Fuel | budget **124.7** vs range extension **0.0** → err **−124.7** |

Record after 6 graded days: **4 right / 5 wrong / 3 no-call**, levels 0.59.

The day opened 29464.7, closed 29465.5 and the published gamma flip was
29462.2. **The session closed 3.3 points from the flip and 0.8 points from its
own open.** Both extremes were already set before the scan was published.

## 2. What the levels actually did

**Worked, and worked well.**

- **29486.5 — Equal highs ×2 + London High.** Day high 29489.5: **3.0 points
  through it, and price settled below it for all 1,380 minutes.** The best
  level on the board. Note what the brief called it: *"Prime S1 sweep trigger."*
  It behaved exactly like that — on a day the regime section told the trader S1
  fades were the wrong trade (§3).
- **29476.3 — Asia High.** Settled below from 08:05, 770 min, worst +9.5 →
  RESISTANCE.
- **29263.1 — PUT WALL ●●●●●.** Never reached after the scan; whole-day it
  settled **above** from 02:45 for 1,090 min, worst excursion −22.5 → SUPPORT.
  The brief said of it: *"if it breaks, expect it to speed UP, not bounce.
  Don't buy the break."* It never broke, and it floored the session. The
  strongest floor on the board behaved like a floor on a day the model said
  floors do not hold.
- **29376.4 PDL + NY Low** (settled above from 19:15, SUPPORT) and
  **29349.4 London Low** (settled above from 18:40, SUPPORT) both chopped then
  held. The PDL instruction — *"sweep it, wait for a higher low, CISD = long"* —
  was the right trade.
- **29454.8 PD close** — settled above from 19:55, worst +0.9. The close came to
  rest between PD close and the flip.

**Did not behave as described.**

- **29462.2 — GAMMA FLIP.** The brief's whole thesis hung on price being below
  it. Price was inside the flip's 8-pt tolerance **in the first NY bar, 2
  minutes after publication**, chopped it for the rest of the session, and
  closed 3.3 above. `gex_retro` gives it **no settled role at all** — the only
  level on the board that never picked a side. The brief's own escape clause
  (*"reclaim and hold above and fading becomes valid again"*) fired within
  minutes and nothing downstream reacted to it.

**Untested rather than wrong.**

- **29516.1 CALL WALL ●●●●○ + MAX PAIN** and **29530.1 Asia Low (prev-day)** —
  both stretch, 141–155 pts away on a 124.7 budget, never reached. The call wall
  sat 27 pts above the day high. No evidence either way.

**Degenerate — should not have been graded.**

- **29223.8 Asia Low (today)** *is* the session low, made in Asia before the
  scan. `review_day` scores it "never reached" (a miss, dragging the hit rate to
  0.60 and the stretch bucket to 0/3); `gex_retro` scores it BROKE with a worst
  excursion of exactly **+0.0**. Both readings are artefacts of the level being
  the extreme by construction. See §4.

## 3. What was wrong, and why

**The score was −7. Gamma supplied −5 of it, and both gamma terms encode the
same single fact.**

    gamma  -3   below flip 29462.2 by 87.4pts
    gamma  -2   week net GEX -3.494 $bn/1% -> expansion likely
    rates  -1 · breadth -1 · news -1 · vol +1 · structure 0 · macro 0
    fuel    0 · events 0

The gamma flip is by construction the spot where net GEX crosses zero. "Price
below the flip" and "net GEX negative" are one observation, not two. Across
**all 18 live scans on record (7 trading days) the two terms have never once
disagreed in sign** — +2/+2 or +2/0 above the flip, −3/−2 below it, every time.
One fact is worth ±5 of a score whose typical magnitude is 4–8.

**That fact had a shelf life of about seven minutes.** Price was 87.4 below the
flip at 13:28 and inside its tolerance by 13:30. The `−3` rule is binary and
distance-invariant: 87.4 pts below scores identically to 276.5 (08-24 09:37)
and to 520.1 (09-01 13:22). There is no proximity term and no reclaim term —
**the same structural hole H10 identifies in the prior-week-range rule**, in a
component with more than twice the weight.

**The regime call, not only the arrow, was falsified.** `COHERENT_SHORT` told
the trader: *"Expect range expansion and trends that persist. Strategy 2.
Today's ADR can be exceeded — don't cap the target too early."* Actual range
extension from the scan: **0.0 points.** Price traversed 181.6 pts inside a
range that did not move, both extremes held (day high 3.0 through a published
level, day low floored by the put wall), and the close returned to the open.
That is textbook pinning — the Strategy 1 day the brief explicitly ruled out.
This is a harder failure than 28 Aug, where the arrow was wrong but the regime
section was right and produced a 265-pt short.

**One component got it right and was outvoted.** `structure +1` — *"in-reach
unmitigated pools: 3 above / 2 below — draw higher"* — pointed at the direction
price actually took, against two collinear gamma terms worth −5.

**Not a factor today:** D7 (`cpi_cool` negation bug) does not touch this scan —
the single auto-scored headline (Warsh, hawkish) was correctly signed −1.

## 4. Change proposals

`track.py`: 6 trading days, threshold met for the 3-day hypotheses. That is
permission to read the evidence, not to tune.

### PROPOSE — collapse the collinear gamma term

**Change.** Stop scoring `week net GEX → expansion/pinning` as a *directional*
component. Either drop its points, or convert it to a magnitude-only input that
scales conviction rather than adding sign.

**Evidence.** 18/18 live scans, 7 trading days, sign agreement with the
below/above-flip term is perfect and structural, not empirical. Expansion also
has no direction: a −3.494 $bn/1% book predicts a bigger *range*, not a lower
close — and on 08-31 it predicted a bigger range on a day that extended 0.0.

**Expected effect.** Label changes on 3 of 9 graded calls: 08-31 −7 → −5
(BEARISH → MILDLY BEARISH), 08-27 +7 → +5, 08-28 +6 → +4. Two calls fall below
the ±3 call threshold and become no-calls: **08-26 13:12 (was WRONG) and 08-24
12:40 (was CORRECT)**. The direction scoreboard is therefore a **wash** — this
is proposed on grounds of construction, not measured hit rate, and it should be
accepted or rejected on that basis. It removes false conviction, not error.

**Do not change the −3 below/above-flip term on this evidence.**

### RECOMMEND — report the stretch split separately (no scoring change)

Today: non-stretch **6/7 = 0.86**, stretch **0/3 = 0.00**. **Sixth consecutive
day with the same sign, no exceptions.** Cumulative across 6 days, pooled by
level rather than averaged by scan (per M4): non-stretch **107/131 = 0.82**,
stretch **15/39 = 0.38**.

Still **NOT proposed:** dropping stretch levels. 0.38 is a real reaction rate,
and today's 0/3 includes one degenerate grade (29223.8, below).

### Observations only — nothing proposed

- **H1 (fuel, 6 days).** Per-day error +61.2 / −11.6 / −73.0 / −86.4 / −10.7 /
  **−124.7**. Mean now **−40.9** (was −27.5 at 4 days), 5 of 6 negative. A 5-of-6
  sign is p≈0.22 two-sided — not a bias, and today's −124.7 is the whole budget
  because both extremes were in before the scan. The blocker stands: the budget
  is a linear ADR remainder with no term for *where in the session the extremes
  were made*. **Tempting and rejected:** all three `MODERATE` days over-read
  (−73.0 / −86.4 / −124.7, mean −94.7) while `LOW_FUEL`/`EXHAUSTED`/
  `ROOM_TO_EXPAND` were near-exact. That is a post-hoc slice of 3 points out of
  6 across 4 buckets. Logged to test forward, not to fit.
- **H4 (flip as magnet) — threshold now met at 6 days.** 08-28 flip 29265.1 vs
  close 29454.8 = 189.7 miss; **08-31 flip 29462.2 vs close 29465.5 = 3.3 hit**.
  Running: **2 hits / 4 misses** (1.1, 3.3 · 189.7, 236.6, 255.2, 599.8). The
  register's verdict — *do not use the flip as a target* — survives. Curiosity
  logged, not proposed: both hits are below-flip scans (2/2), all four misses
  are above-flip (0/4). n=2 on the hit side is not evidence.
- **Flip proximity.** |distance to flip| vs outcome across 9 graded calls:
  <150 pts → 1 right / 3 wrong; ≥200 pts → 3 right / 2 wrong. Directionally
  consistent with today's failure, far too thin to act on. Watching.
- **Possible measurement defect (D8 candidate).** A published level that is
  already the day's high or low at scan time is graded like a forecast. Today
  that made **the session low itself** score as "never reached", cost the hit
  rate one miss and contaminated the stretch bucket. One clean instance is not a
  defect claim — I have not yet counted how often it happens on prior days.
  Recorded in HYPOTHESES.md to be counted before anything is changed.
- **No level class is dead.** Lowest touch rates over 6 days: STRUCTURAL PUT
  WALL 3/10 (4 days), GAMMA FLIP 5/10 (4 days). Nothing warrants being dropped.
- **`fuel` and `events` score 0 in all 29/17 emissions** — but they are
  `add("fuel", 0, …)` and `add("events", 0, …)`, hardcoded narrative rows by
  design. Not dead weight to remove. They do inflate the "24 checks" count shown
  to the trader; cosmetic, not proposed.

**No new data point proposed.** Nothing today failed for want of a source; it
failed for want of a proximity/reclaim term on a source already in hand.
