# NAS100 — review, Thursday 27 August 2026

**Session:** O 29,450.7 · H 29,642.1 · L 29,338.2 · **C 29,566.7**
**Range 303.9pts** (ADR14 390.3 — a 78% day) · **net +116.0**

*Graded after the 21:00 UTC roll. Four verification re-runs excluded — see §6.*

---

## 1. The call was right

**13:23 PRE_NY — BULLISH (+7) → price moved +91.6. CORRECT.**

The first correct pre-NY directional call on record. Price never traded below
the scan price in any meaningful way and closed **+85 above it**.

**Level hit rate 0.7** — the joint best of the four days.

| Level | Outcome |
|---|---|
| 29,588.6 Asia High | **stalled at it** |
| 29,353.8 PDH + PD close | broke UP through it |
| 29,595.9 London High | broke DOWN through it |
| 29,487.9 CALL WALL | traded both sides — chopped |
| 29,451.1 Equal lows ×2 | chopped |
| 29,413.0 London Low | chopped |

The Asia High at 29,588.6 was the good one — it stalled price, and the day's
high finished 53pts above it after a late push.

## 2. Where my commentary was wrong

I wrote this morning: *"price is pinned right under the strongest ceiling on the
board… buying here is buying the last few points before the heaviest selling on
the chain."*

**Price closed 79 points above that call wall, and traded 154 above it.**

| Hour (UTC) | High | Close |
|---|---|---|
| 13:00 | 29,536.1 | 29,417.6 |
| 14:00 | 29,555.8 | 29,536.5 |
| 16:00 | 29,593.9 | 29,586.9 |
| **19:00** | **29,639.3** | 29,636.6 |
| 20:00 | **29,642.1** | 29,566.7 |

The call wall (29,487.9, 2.22bn, also the 45-day call wall) chopped rather than
capped. Price crossed it early in the 14:00 hour and never returned below it.

**What I got wrong was the emphasis, not the fact.** The wall was real and the
brief's own scoring flagged the risk (`gamma −2`, top of the wall band). But I
led with the ceiling and buried the +7 bullish score, and the score was right.
In a long-gamma regime a call wall is a *brake*, not a *lid* — dealers sell into
it, which slows a rally; it does not stop one. I described it as though it
would stop one.

That distinction now matters twice: it is the same word — "wall" — doing two
different jobs, which is what produced the put-wall bug you caught today.

## 3. Fuel — third consecutive over-read, and the trend is now clear

| Day | Budget | Extension | Error |
|---|---|---|---|
| 24 Aug | 88.7 | 168.5 | **+61.2** |
| 25 Aug | 12.0 | 0.4 | −11.6 |
| 26 Aug | 186.2 | 113.2 | −73.0 |
| **27 Aug** | **132.6** | **46.2** | **−86.4** |

Per-day mean **−27.5**. Three consecutive over-reads, each larger than the last,
after one large under-read.

**This is still not a calibration.** Four points running monotonically in one
direction describe a *trend*, not a level — a multiplier fitted here would fit
the slope and be wrong on both ends. What it does now justify is asking whether
something regime-linked is driving it: all three over-read days were long-gamma
or pinning sessions, and the single under-read day was not.

**H1 reaches its threshold and I am still proposing nothing.** The honest
statement is that the budget has been systematically generous on pinned days,
and we do not yet have an unpinned day to test against.

## 4. First chart-ladder test — CORRECTED

**The version of this section published earlier was wrong and is withdrawn.**
It reported *"1 of 7 reached, 6 never reached"* and concluded the ranked walls
do not produce in-range levels. It graded the wrong ladder — the 26 Aug 22:12Z
file, which was never delivered in a scan, carries `book: None` (the 45-day book
from before today's fixes), and was anchored to a post-NVDA spike price.

Caught by the trader, who noticed a level in it (29,599) that had never appeared
in any ladder he was given.

**The ladder actually delivered with today's scan**, graded from publication
forward:

| Rank | Level | First-touch grade | After it settled |
|---|---|---|---|
| C3 | 29,514 | CHOP | held 120min, worst **−11.2** → support |
| C1 | 29,464 | CHOP | held **310min**, worst **−4.7** → support |
| C2 | 29,414 | BROKE | held 420min, worst **+1.6** → support |

**All three C-ranks were in range, all three were touched, and all three held.**
They span 100 points, not 600.

### And the grader was wrong too

The trader read C1 as: chopped through at the open on news, then acted as
resistance, then — once price got above it — support; swept once, reclaimed,
never broken again.

Measured: C1 had **exactly one bar close below it** in the entire
post-publication session, then held for **310 minutes** with a worst excursion
of **4.7 points**.

`grade_level` called it CHOP, because it scores the *first touch* and stops. On
a news-driven open the first touch is the worst possible sample. It also has no
concept of role reversal, and treats "broke UP through it" as a failure even
when the level is below price and never revisited — which for a call wall in a
rally is the successful outcome.

Logged as **D5**. `role_reversal()` now reports settled side, duration, retests
and worst excursion alongside the first-touch grade. It is additive, so the
written review and the chart still use the same rule and cannot drift.

**The honest summary: the trader read the level better than the tool did.** The
measurement was wrong, not just the conclusion.

## 5. Live-wall research — first graded result, and it is promising

Estimating 26 Aug's open interest from that day's volume, graded against what
the OCC published this morning:

| | |
|---|---|
| Estimated ΔOI | **+7,217** |
| Actual ΔOI | **+9,927** |
| Error | −2,710 — **−24.2% of the day's positioning move** |
| Mean absolute error | 2.8 contracts |
| Within hard bounds | **98.9%** |
| Implied k (overall) | 0.568 |

**−24.2% on day one, with unfitted priors, is inside the 25% target and
approaching the published 15% benchmark.** Better than I expected this early.

Calibration refitted from the observation — my priors were systematically too
low, which matches the implied k of 0.568:

```
1-5d/atm   0.35 -> 0.50      6-20d/atm  0.40 -> 0.25
1-5d/far   0.45 -> 0.60      6-20d/far  0.50 -> 0.65
21d+/near  0.50 -> 0.65      6-20d/near 0.45 -> 0.60
```

**⚠️ One number needs investigating: within hard bounds is 98.9%, not 100%.**

The method document states plainly that this figure *must* be 100% — the bounds
`[max(−V, −OI), +V]` are arithmetic, not modelled, and cannot be violated by a
correct dataset. 1.1% of contracts fell outside them, which means an input is
not what it claims to be. Candidates: the volume field being exchange-specific
rather than consolidated, a snapshot taken before volume finished accruing, or
contracts re-listed between the two fetches.

**Not diagnosed yet, and I am not going to guess at it.** It goes to the top of
tomorrow's list, because every accuracy number above rests on those bounds being
sound.

## 6. Process note — I inflated the evidence

Five journal entries were written today for **one** real scan. Four came from
re-running the brief while fixing the put-wall bug you found. The 15-minute
dedupe collapses only the closest pair, so three would have entered the record
as independent observations of a market state sampled once.

Fixed both ways: `brief.py --no-journal` for verification runs, and the four
already written are marked `test_artefact` and excluded by both `track.py` and
`review_day.py`. Marked rather than deleted — a journal quietly tidied is
indistinguishable from the fabricated entry that produced W2.

**Before the fix this review read "5 right / 0 wrong."** It is 1 right / 0
wrong. Same day, same market, five times the confidence.

## 7. Scoreboard

| | Status | Days | Today |
|---|---|---|---|
| **H1** budget = range extension | **THRESHOLD MET** | 4 / 3 | ⚠️ 3rd consecutive over-read, monotonic. **Nothing proposed** |
| **H2** fade beats continuation at low fuel | OBSERVING | 2 / 3 | No qualifying scan (MODERATE) |
| **H3** bias over-commits at extremes | OBSERVING | 1 / 3 | No new evidence |
| **H4** flip as magnet | OBSERVING | 4 / 5 | Close 29,566.7 vs flip 28,966.9 — **599.8pts. Miss** |
| **H5** budget under-reads early | THRESHOLD MET, no evidence | 4 / 3 | Still **one** late-session scan. Cannot fit |
| **H6** level board reaction quality | OBSERVING | 4 / 5 | ✅ **0.70 — joint best** |
| **H7** flip instability | OBSERVING | 3 / 3 | No large drift today |
| **H8** expected move | OBSERVING | **2 / 10** | ✅ Band 29,221–29,741, **close 29,566.7 INSIDE** |
| **H9** earnings pin | OBSERVING | 1 / 3 | No qualifying event |
| **H10** prior-week rule, no reclaim | OBSERVING | 1 / 3 | Rule did not fire |

**H4 is now looking weak** — one hit and three clear misses. The 1.1pt finish on
24 Aug increasingly looks like the coincidence it was flagged as.

**H8 is 2 for 2.** Too early to mean anything, but the band has now contained
one close and missed another by 4.9pts.

## 8. Tomorrow

1. **Diagnose the 98.9%.** It invalidates nothing yet, but it is the foundation
   the live-wall numbers sit on.
2. **Second chart-ladder test** — today's ladder against tomorrow. If the ranked
   walls are again mostly out of range, a proximity filter is the answer.
3. **H1 needs an unpinned day.** All three over-reads were long-gamma sessions.
4. Friday: **weekly expiry.** Max pain gets strong, and the fuel model has not
   been tested on one.
