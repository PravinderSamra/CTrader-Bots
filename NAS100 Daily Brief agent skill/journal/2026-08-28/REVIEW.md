# REVIEW — trading day 2026-08-28

Graded 2026-08-28 22:15 UTC, after the 21:00 roll. One gradeable scan
(13:14 PRE_NY). `2233-overnight` carries `scan_utc 2026-08-27T22:33Z`, is the
21:00 roll working correctly, and is marked `test_artefact` — it enters nothing.

---

## 1. Scoreboard

Trading day = 2026-08-27 22:00 UTC → 2026-08-28 20:50 UTC (275 M_5 bars, complete).

| | |
|---|---|
| Open / High / Low / Close | 29570.4 / 29748.3 / 29376.4 / 29454.8 |
| Range | 371.9 |
| Net | **−115.6** |
| Direction calls | **0 right / 1 wrong** |
| Level hit rate | **0.73** (16/22) |
| Fuel | budget 254.9 vs range extension 244.2 → **ratio 0.96**, err **−10.7** |

The 13:14 scan called **BULLISH +6** at 29,597.5. Price moved **−143.7** from
the scan. **The direction call was wrong.** The record is now
**4 right / 4 wrong / 3 no-call** across 5 days — a coin flip, and it should be
read as one.

## 2. What was right, stated separately from the arrow

The direction arrow was the *only* thing that failed. Every part of the brief
the trader actually acts on — which model, where, and when to stand aside — was
correct, and the day paid on the short side precisely as the regime section
described.

**The regime call was right.** The brief said: above the flip, long gamma,
*"sweeps of a high or low tend to genuinely fail — this is your fade day,"*
Strategy 1. That is exactly what happened, in the direction opposite the bias.

**The event gate was right and it was protective.** The brief posted a stand-
aside for Warsh + the Prelim Benchmark Payrolls Revision at 14:00 UTC. That hour
ran **29,444.1 → 29,735.8, a 292-point whipsaw in both directions**. Non-
negotiable #1 exists for exactly this bar, and it held the trader out of it.

**The gate's follow-on instruction produced the day's trade.** The rule reads:
no entries until 30 minutes after the print, then use the post-print 30-minute
range H/L as the day's sweep levels. Graded:

| | |
|---|---|
| Post-print window 14:00–14:30Z | H **29,641.7** / L **29,444.1** |
| First sweep of that high | 14:35Z at 29,649.9 |
| Low after that sweep | **29,376.4** — **−265.3 pts** from the swept level |

Sweep, fail, reverse 265 points. That is the Strategy 1 sequence the regime
section called for, off a level the gate itself defined.

**The call wall marked the high of the day.** Published at 29,735.4 as
*"heaviest ceiling this week… take profit into it."* Day high **29,748.3** —
12.9 points through it, and **not one bar closed above it in 1,375 minutes of
session**. Price then fell 211.5 points off it. The strongest level on the board
did the single most valuable thing a level can do.

## 3. ⚠️ DEFECT — D5's fix was wired into one path only (found and fixed today)

The retro reported **"0 held · held rate of reached 0.0%"** on a day the call
wall capped completely. That figure is wrong in substance, and the cause is a
wiring defect, not a market read.

`role_reversal()` — added on 27 Aug as the fix for D5, after the trader read C1
better than the tool did — is called **only from `build_from_ladder()`**, the
`--ladder` chart path. The standard board retro, `build()`, never called it, so
**every level in every board retro returned `role: None`** and the whole day was
graded on first touch alone, the rule D5's own docstring calls *"the worst
possible sample."*

`HYPOTHESES.md` D5 records that role_reversal *"now reports, for every touched
level…"*. **For the board retro that was never true.** The register's claim and
the code disagreed, and the register was wrong.

Measured properly, on the same bars and the same board:

| measure | first touch (reported) | settled behaviour (role_reversal) |
|---|---|---|
| of 16 reached | **0 held (0%)** | **13 held (81%)** — 11 resistance, 2 support |
| 29,735.4 call wall | BROKE | **RESISTANCE**, settled below 1375min, worst excursion **+12.9** |
| 29,405.4 max pain | CHOP | **SUPPORT**, settled above from 19:00, worst −12.9 |

**Fixed** in `gex_retro.build()`, mirroring the ladder path exactly. The fix is
**additive by design**, as D5 requires: `grade_level` and the `outcome` field
are untouched, the headline counts and the chart are byte-for-byte unchanged,
and the settled read sits *beside* the first-touch grade rather than replacing
it. `test_consistency.py --offline`: **16 passed, 0 failed.**

This is a defect, not a hypothesis, so the 3-day rule does not gate it.

## 4. Hypotheses — evidence only

**H1 (fuel, 5 days).** Today err **−10.7** on a 0.96 ratio, the second-smallest
of the five. Per-day: +61.2 / −11.6 / −73.0 / −86.4 / −10.7. The sign still
flips and there is still no consistent bias to correct. The blocker restated on
27 Aug — the budget is a pure linear ADR remainder with no regime term — is
untouched by today. **Nothing proposed.**

**H6 (level board, threshold 5 days — MET TODAY).** Today's split by the board's
own `stretch` flag: **non-stretch 16/19 = 0.84, stretch 0/3 = 0.00.** Same sign
for the **5th consecutive day**, no exceptions.

Cumulative: non-stretch **0.81**, stretch **0.45**. H6 has now reached its
threshold, which is permission to read the evidence, not to act.

- **Recommended:** report the two rates separately in the review. No scoring
  change, nothing published to the trader changes.
- **Still not proposed:** dropping stretch levels. The cumulative 0.45 is a real
  reaction rate; today's 0/3 is 3 levels, and all three sat 259–812 points away
  on a day whose range budget was 255.

**H9 (earnings).** No same-day index-defining earnings. No observation.

## 5. The honest read

A brief can be wrong on direction and still be worth having, and today is the
cleanest example on record: the arrow failed, the regime, the model selection,
the stand-aside and the top level of the board all worked, and the sequence they
jointly described was a 265-point short. The scoreboard cannot see that, which
is the argument for §3 being fixed rather than the argument for a scoring
change — the measurement was wrong, again, in the same direction as D5.

**No change to the bias engine is proposed.** One wrong call inside a 4/4 record
is not evidence of a defect in the scoring; it is the sample being small.
