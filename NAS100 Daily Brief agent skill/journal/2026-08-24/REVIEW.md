# Review — 2026-08-24 (first live trading day)

`O 29328.3  H 29403.8  L 28872.9  C 29050.7  range 530.9  net −277.6`

Shape of the day: gap down at the Sunday Globex open, grind lower through Asia
and London, **low 28,872.9 at 13:50 UTC — 20 minutes into the NY session** —
then a 178pt reversal into the close.

## 1. Scoreboard

| Metric | Result |
|---|---|
| Direction | **2 correct · 1 wrong · 5 no-call** |
| Level hit rate | **0.69** |
| Fuel accuracy | **UNDER-estimated on 8 of 8 scans** |

## 2. What the levels did

**The gamma flip was the standout.** Published at 29,049.6 on the 13:45 scan;
the session closed at **29,050.7 — 1.1 points away**. Price sold off below it,
reversed, and settled almost exactly on it. That is the flip behaving precisely
as the model describes: a regime line price gravitates back to.

Most other levels graded "traded both sides — chopped around it". On a 530pt
trend-and-reverse day that is expected, but it means the level board was better
at describing *where* than at producing clean single-touch reactions.

## 3. What was wrong, and why

### The 13:45 NY_OPEN scan — STRONGLY BEARISH (−12) — called the exact low

Price at scan 28,903.5. It went **30.6pts further** to 28,872.9 five minutes
later, then rallied **+253.8** and closed +147 above the scan price.

Traced to its cause: at that moment the range was **113% of ADR**, fuel was
`EXHAUSTED` with a **0.0pt budget**, and price sat at the low of the day. The
bias engine scored it −12, its strongest bearish reading of the session.

**The design decision that caused it is explicit and documented:** fuel
"reports, never votes" — it changes management and target scope, not direction
or conviction. Today is the case where that cost. A continuation call at maximum
conviction, with zero range budget, at the day's extreme, is the model chasing.

The advice given alongside it — take partials, trail on 1m structure, don't
fade, invalidation at the flip — was sound and would have protected the trade.
**The risk management saved it, not the direction call.**

### ~~Fuel is systematically too tight — now actionable~~ **WITHDRAWN — see addendum**

| Session | Budget published | Realised | Ratio |
|---|---|---|---|
| 2026-08-20 | 156.1 | 266.6 | 1.7× |
| 2026-08-24 (London scans) | 88.7 | 334.7 | 3.8× |
| 2026-08-24 (13:45) | 0.0 | 284.4 | ∞ |

Three independent sessions, every one under-estimating. This clears the
reviewer's "3+ sessions" threshold. `EXHAUSTED` currently reads as "no movement
left"; today it was followed by 284pts of further range. It evidently means
"no more range **in the direction that got us here**" — which is a different
statement, and closer to a reversal signal than a stand-down signal.

## 4. Change proposals

**P1 — Recalibrate the range budget. Evidence: 3 sessions. Ready.**
The budget is measured against ADR14 alone. Every observation says the true
remaining range exceeds it, badly, once a day is already extended. Options: a
multiplier on the remaining budget, or a floor so `EXHAUSTED` never publishes
0.0. Needs a decision on which, not more data.

**P2 — Let fuel cap conviction on continuation calls. Evidence: 1 session.
NOT ready — logging it.**
Hypothesis: when `EXHAUSTED` **and** price is within ~10% of the day's extreme,
a with-trend continuation score should be capped (e.g. |score| ≤ 6) rather than
allowed to reach −12. This would not have flipped today's call to bullish; it
would have stopped it being the most confident call of the day at the worst
possible moment. **Do not implement on one observation** — watch for the next
two instances of `EXHAUSTED`-at-extreme.

**P3 — Deduplicate near-identical scans. Housekeeping.**
Four scans landed within five minutes (08:28/08:30/08:32/08:33) during testing.
They are counted as four observations of the same market state and will skew
every statistic, the same way weekend PREP scans would. Either collapse scans
inside a short window or tag them, as `is_trading_day` already does for weekends.

## 5. Honest note on sample size

One trading day. Two correct calls and one wrong call is not a hit rate. The
only finding here with enough evidence to act on is the fuel budget, and that is
because it has now failed in the same direction across three separate sessions.
Everything else is logged and waiting.


---

# ADDENDUM — this review's central finding was wrong

Re-measured after the question "does fuel mean range extension rather than
movement?". It does, and grading it against price traversal was the error.

| 13:45 scan | |
|---|---|
| Budget published | **0.0pts** |
| Range **extension** that followed | **5.3pts** — forecast essentially exact |
| Price **traversal** inside the range | **284.4pts** |

**The fuel model was right.** The review engine compared the budget against
traversal (how far price roamed) instead of extension (how much the range grew),
manufacturing a "3.8x under-estimate" out of an accurate forecast. Engine fixed.

**The 2026-08-20 data point is withdrawn.** It came from a backdated entry
created to test the review loop and deleted immediately after — not a real scan.
Citing it as one of "three independent sessions" was exactly the archive
corruption this reviewer is written to prevent. Real trading-day evidence is
**one session**, and it does not support recalibration.

**What genuinely follows.** `EXHAUSTED` means the extremes are probably in, not
that movement stops. Since the range will not extend, price must turn at the
extremes — so the higher-probability trade at `LOW_FUEL`/`EXHAUSTED` is **fading
back into the range**, even when the gamma regime favours continuation. That is
a definitional consequence of the forecast being right, not a calibration
tuned on one day. The brief's wording now says this; no thresholds or scores
were changed.

Proposal P1 (recalibrate the budget) is **withdrawn**. P2 (cap conviction when
exhausted at the extreme) is superseded by the reframing above — the fuel state
now argues against the continuation call directly. P3 (deduplicate scans)
stands.
