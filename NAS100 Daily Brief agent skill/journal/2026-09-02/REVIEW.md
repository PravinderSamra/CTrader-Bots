# REVIEW — trading day 2026-09-02

Graded 2026-09-03 after the roll. One gradeable scan (13:25 PRE_NY). **This is
the last day recorded under the pre-change model** — C1/C2 were applied on the
evening of 2 Sep, after this scan, and C3 on 3 Sep. Nothing below reflects them.

---

## 1. Scoreboard

| | |
|---|---|
| Open / High / Low / Close | 29088.8 / 29166.8 / 28882.4 / 29099.6 |
| Range | 284.4 |
| Net | **+10.8** |
| Direction call | **0 right / 1 wrong** |
| Level hit rate | **0.45** (5 / 11) |
| Fuel | budget 156.7 vs extension 42.8 → err **−113.9**, a large over-read |

The scan called **STRONGLY BEARISH −12** — the most emphatic call the model has
ever made — and price moved **+46.0**. The day closed **+10.8**, essentially
flat. **Wrong, and wrong at maximum conviction.**

## 2. The conviction problem, in one day

This day is the cleanest single illustration of the pattern found across the
whole record: **the model's confidence is not informative.** Strong calls
(|score| ≥ 10) are 1-for-4; weak calls (≤ 5) are 1-for-2. Today was the
strongest call on record and it produced a flat day.

Where the −12 came from is the point. Gamma supplied **−5 of it** through the
two collinear terms:

| | score | label |
|---|---|---|
| as shipped | **−12** | STRONGLY BEARISH |
| after C2 (net-GEX → 0) | −10 | STRONGLY BEARISH |
| after C2 + C3 (both gamma terms → 0) | **−7** | **BEARISH** |

Still the wrong side, so this is **not** a day the changes would have rescued —
and it should not be presented as one. What they remove is the *emphasis*: a
flat day would have been called bearish rather than strongly bearish. That is
the whole claim for C3, and today is consistent with it.

## 3. Levels — the weakest board on record

**0.45 (5/11)**, against a running non-stretch rate of ~0.81. Five of the
eleven published levels were flagged `stretch`, and the day's range was 284
against an ADR of 398, so the board was calibrated for a day considerably wider
than the one that arrived.

Note this is a **pre-C1** board: it was built with the old budget-derived filter
on a day whose budget (156.7) was healthy, so C1 would have changed nothing
here. C1 only bites at a zero budget.

## 4. What actually happened

Price spent the day chopping around the level cluster between 29,022 and
29,124 — the put wall, the call wall, the London high and the prior-day close
all sit inside 100 points of each other, and every one of them graded "traded
both sides". The single directional level, the Asia low at 28,971.7, **broke
UP** through. A pinned day inside a tight cluster, called as a strong
directional breakdown.

## 5. Hypotheses

**H1 (fuel).** Err −113.9, the second-largest over-read on record (after
−124.7 on 08-31). Per-day mean worsens to about −37. Still no consistent sign
across the series; the structural blocker (no regime term in the budget) is
unchanged. **Nothing proposed.**

**H6.** Not counted. `stretch` semantics changed with C1 on the evening of
2 Sep, and the register requires the split to be re-based from that date. This
board predates the change, so it belongs to the old series, which is closed.

**Conviction (open, informal).** Now 1-for-4 at |score| ≥ 10. Worth promoting to
a numbered hypothesis once there are enough strong calls to test — there are
four.

## 6. The honest read

Three of the last four days were called bearish and closed flat or higher. The
model's directional lean and the market's drift were pointed in opposite
directions for the whole recorded window. C3 removes the mechanism behind that
lean; it does not make this day's call right, and no change proposed so far
would have.
