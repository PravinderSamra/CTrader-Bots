# NAS100 — Dynamic Stop (break-even + trailing) test plan

Written 1 Oct 2026, before running. Trigger: the 1 Oct 2026 trade reached about +$1,600 and then reversed to a −$691 loss.

## Base (unchanged)
Live NAS100 Add To Winner settings: trigger 0.7, Add Size 5, Max Total Risk 2.5, TP 4R, risk reduction to 70% at 0.7R,
close 15:50 NY, Risk $300, tick data, 1 Jan 2021 – 28 Sep 2026. Base result: **$58,446.89, max equity DD 6.83%**.

## How the Dynamic Stop works (code checked)
At Break Even Trigger R the stop moves to entry + Break Even Extra Pips. After that, every further Dynamic Step R of profit
moves the stop up by the same amount, so it follows price at about the trigger distance. The add follows the same stop.
Break Even Extra Pips = 22 makes the whole position (main + size-5 add entered at +0.7R) break even, not just the main trade.

## Runs
| Run | Break Even Trigger R | Extra Pips | Dynamic Step R |
|---|---|---|---|
| DS1 | 1.0 | 22 | 0.25 |
| DS2 | 1.5 | 22 | 0.5 |
| DS3 | 2.0 | 22 | 0.5 |

## Decision rule
Switch only if a run beats $58,447 in net profit, or is within about 5% of it with a clearly smaller drawdown
(about 1 percentage point or more). Otherwise keep the current setup: today's trade was an unlucky day, not a pattern.

## Results (2 Oct 2026)
| Run | BE trigger | Extra pts | Step | TP | Net 2021–26 | Max equity DD | Winners |
|---|---|---|---|---|---|---|---|
| Base (no trailing) | – | – | – | 4R | $58,446.89 | 6.83% | 420 |
| DS1 | 1.0 | 22 | 0.25 | 4R | $15,096.80 | 6.72% | 508 |
| DS2 | 1.5 | 22 | 0.5 | 4R | $39,401.38 | 7.22% | 477 |
| DS2b | 1.5 | 2 | 0.5 | 4R | $42,601.90 | 7.53% | 432 |
| DS3 | 2.0 | 22 | 0.5 | 4R | $49,642.93 | 7.46% | 452 |
| DS3b | 2.0 | 2 | 0.5 | 4R | $52,074.96 | 7.35% | 421 |
| DS4 | 2.5 | 2 | 0.5 | 4R | $62,877.35 | 6.88% | 423 |
| **DS4b** | **2.5** | **2** | **0.25** | 4R | **$63,941.03** | 6.87% | 427 |
| DS4b + TP5 | 2.5 | 2 | 0.25 | **5R** | $63,637.42 | **6.61%** | 427 |
| DS4b + TP6 | 2.5 | 2 | 0.25 | 6R | $63,556.11 | 6.71% | 427 |
| DS5 | 3.0 | 2 | 0.5 | 4R | $59,668.48 | 6.83% | 422 |

**Findings.** A trailing stop that starts early (1–2R) cuts the big winners and loses money against the base. It peaks at
**2.5R** (DS4 and DS4b both beat the base, and 3R is still above it), so the benefit is a plateau rather than one lucky
setting. The target barely matters once trailing is on (4R, 5R and 6R are within $400).

**Decision: DS4b with TP 5R**: break-even at 2.5R (+2 pts), trail in 0.25R steps, target 5R. About +$5,200 (+9%) over the
base with a slightly lower drawdown (6.61% against 6.83%), and a trade that reaches +2.5R can no longer become a full loss.
Note: 11 variants were tried, so expect a little of the gain to be luck; the plateau (2.5–3R all at or above the base) is the
reassurance.

Addendum: DS4b + TP 4.5R = $64,758.49, max DD 6.73%, 427 winners. Targets from 4R to 6R are all within about $1,200 (a flat
plateau, i.e. noise), so tuning stops here. Either 4.5R or 5R is fine.
Addendum 2: BE 2.5R (+2 pts), **step 0.1R**, TP 4.5R = **$65,832.08**, max DD 6.72%, 430 winners. Finer steps help a little and
consistently (step 0.5 → 0.25 → 0.1), because the stop tracks new highs more closely while staying 2.5R behind.
**Final live choice: BE trigger 2.5R, extra 2 pts, step 0.1R, TP 4.5R.** Tuning closed.
