# NAS100 London Range Volume Breakout — v3.0 Add To Winner

Your live NAS100 bot (`ORB Projects/ORB Volume Breakout Bot/ORB_Volume_Breakout_Bot_v2.cs`) with one new,
optional feature. **With "Enable Add To Winner" = No it trades exactly like the live bot.**

It is a separate bot (`OrbVolumeBreakoutBotV3Atw`, label prefix `ORBVA`), so it can sit next to the live bot
(`ORBV`) in cTrader and neither will touch the other's trades. Compiled against the official cTrader.Automate
package with 0 errors and 0 warnings.

## What it does
When the trade is **Add Trigger R** in profit **and** its stop has already been tightened (by early risk reduction,
break-even or trailing), the bot opens one extra position in the same direction:

- **Add risk = Add Size × (risk that has been taken off the trade)**, measured live from the actual stop, so it
  works with whatever risk-reduction settings the bot is using.
- The add uses the **same stop and target** as the main trade and **follows every later stop move**, so both close together.
- The add never counts as a new trade for "Max Trades Per Day".
- If the main trade closes and an add is somehow still open, the add is closed straight away.
- Force Close closes both.

## New parameters (group "Add To Winner")
| Parameter | Default | Meaning |
|---|---|---|
| Enable Add To Winner | No | Master switch |
| Add Trigger R | 1.0 | Profit (in R of the main trade) needed before adding |
| Add Size (× risk removed) | 1.0 | **1.0** = add back exactly what was taken off (total risk = original). **1.5, 2.0 …** = add more |
| Max Total Risk (× original risk) | 2.0 | Hard ceiling on main + adds together. Never exceeded, whatever Add Size says |
| Max Adds Per Trade | 1 | Up to 3 |
| Next Add Every R | 1.0 | Only if Max Adds > 1: 2nd add at Trigger + 1R, 3rd at Trigger + 2R |
| No Adds In Last Minutes | 30 | No adds this close to Force Close Time (when Force Close is enabled) |

**Worked example** (original risk $300, risk reduction leaves $150 on at +1R):
| Add Size | Add risk | Total risk after the add | If it reverses to the stop | Extra if it reaches target |
|---|---|---|---|---|
| 1.0 | $150 | $300 | lose $300 instead of $150 | about +1R more |
| 1.5 | $225 | $375 | lose $375 | about +1.5R more |
| 2.0 | $300 | $450 | lose $450 | about +2R more |

The add triggers only if the stop has been tightened first; if nothing has been taken off, it logs "skipped" and does nothing.

## Suggested backtest plan (cTrader, US100, same years and settings as your 5-year study)
1. Load your current live `.cbotset` into this bot so everything else matches.
2. Run with **Enable Add To Winner = No** first: the result must match your original backtest. If it does not, stop and tell me.
3. Then run **Add Size = 1.0, 1.5 and 2.0** (Add Trigger R = the same level as your risk reduction trigger) for each year.
4. Send me the logs. Each add prints an `ADD TO WINNER:` line (size, risk, total risk), so I can measure exactly
   what the adds contributed, the worst day, and the drawdown for each setting.

Judge it on more than total profit: the worst day and the worst run of losses matter for FTMO, because a reversal
after an add now costs more than it used to.

## Estimate from your existing logs (before building this)
From the 2022–2026 logs with risk reduction at 1R / 50%: a one-third-size add at +1R (Add Size 1.0) would have added
about **+28R** over 399 trades (+16R in the worst case), positive in every year (+5.4R to +6.2R each).
That was an estimate from where each trade finished; the backtests above are the real test.

## Before you run (added after the first match check)
- **Use the same data setting for every run**, original and v3 alike (tick data *or* 1-minute bars, not a mix).
  The first check compared a tick-data run with a 1-minute-bar run, so the results could not match.
- **Set "Quiet Log (hide repeated warnings)" = Yes** (Diagnostics group). It hides only the repeating
  "VOLUME FILTER … rejected" and "ENTRY BLOCKED" lines, which filled cTrader's log within days. Trading is unaffected.
  The original bot has no such setting, so for the match check compare the backtest **summary** (trades, net profit,
  max drawdown) rather than the log.
- **Your live risk reduction** (seen in the log): stop moved to leave **70% of the risk at +0.75R**, so only 0.3R is
  removed. At Add Size 1.0 the add is therefore small (about 0.18x the original size at a 1.0R trigger).
  Add Size 2.0 or 3.0 may be more informative here; the Max Total Risk cap (default 2.0x) still applies.

- **Quiet Log update (v3.0.2):** it now also caps every other warning at 3 per day (e.g. the catch-up
  "Trend filter blocked" warning, which repeated every second and cut a 2021 log off in August).
  `ADD TO WINNER` lines are never hidden. Re-copy the bot from `main` and rebuild before re-running.
