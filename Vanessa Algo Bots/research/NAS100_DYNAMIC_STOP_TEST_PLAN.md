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
