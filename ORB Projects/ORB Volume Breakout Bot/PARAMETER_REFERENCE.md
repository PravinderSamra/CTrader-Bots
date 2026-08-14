# Parameter reference

Renaming the bot class to `OrbVolumeBreakoutBotV2` makes it a **new bot** as far as
cTrader is concerned, so it starts with no saved settings. That is expected, and the
old bot still has yours.

**Try this before typing anything.** In the cBot's parameter panel there is a
load/folder control next to the preset dropdown. Browse to the `.cbotset` file and
open it — cTrader will fill every field in one go. `.cbotset` files are plain JSON and
carry no bot name, so a file saved under v1 loads into v2 without complaint.

If that will not cooperate, the tables below are every value, written with the labels
as they now appear on screen.

## What to run now — the original method

London range, entries only in the hour after the New York bell, 50pt stop, fixed 100pt (2R) target, breakeven at 1R. This is the config for the 2023 and 2024 backtests.


**Session 1 - Range Window**

| Setting | Value |
|---|---|
| Range Time Zone | `EuropeLondon` |
| Range Start (this zone) | `08:00:00` |

**Session 2 - Trading Window**

| Setting | Value |
|---|---|
| Trading Time Zone | `AmericaNewYork` |
| Range End / Market Open | `09:30:00` |
| First Entry Time | `09:31:00` |
| Enable Last Entry Cutoff | `Yes` |
| Last Entry Time | `10:31:00` |
| Enable Force Close | `Yes` |
| Force Close Time | `16:00:00` |

**Session 3 - Legacy**

| Setting | Value |
|---|---|
| Ignore Zones - Use Fixed UTC | `No` |

**ORB**

| Setting | Value |
|---|---|
| ORB Bars TimeFrame | `m1` |
| Max ORB Range Pips | `500.0` |
| Min ORB Range Pips | `0.0` |
| Point Unit Mode | `1` |
| Enable ORB Backfill | `Yes` |
| Enable ORB Self-Heal | `Yes` |
| ORB Self-Heal Interval Seconds | `30` |
| Enable Post-Lock Confirm Replay | `No` |
| Post-Lock Replay Confirm Bars | `1` |
| Post-Lock Replay Max Delay Minutes | `30` |

**Catch-Up Entry**

| Setting | Value |
|---|---|
| Enable Catch-Up Entry | `Yes` |
| Catch-Up Requires Confirmation Bars | `No` |
| Catch-Up Max Distance Beyond Threshold Pips | `0.0` |

**Entry Offset**

| Setting | Value |
|---|---|
| Entry Offset Pips | `0.0` |

**Breakout**

| Setting | Value |
|---|---|
| Confirmation TimeFrame | `m1` |
| Confirmation Bars Count | `1` |
| Breakout Cross Type | `0` |
| Breakout Evaluation Moment | `1` |
| Candle Direction Requirement | `1` |
| Allow Long | `Yes` |
| Allow Short | `Yes` |

**Volume Filter**

| Setting | Value |
|---|---|
| Enable Volume Filter | `Yes` |
| Volume Multiplier | `1.4` |
| Volume Lookback Bars | `20` |

**Trend Filter**

| Setting | Value |
|---|---|
| Enable Trend Filter | `Yes` |
| Trend TimeFrame | `m15` |
| Trend EMA Period | `9` |
| Trend Slope Lookback Bars | `3` |
| Trend Min Slope Pips | `0.0` |
| Neutral Min Slope Pips | `0.0` |
| Trend Neutral Policy | `0` |
| Trend Filter Verbose Logs | `No` |

**Trades Per Day**

| Setting | Value |
|---|---|
| Max Trades Per Day | `1` |
| Re-Entry Mode | `0` |
| Block Same-Bar Re-Entry | `Yes` |

**Trading Days**

| Setting | Value |
|---|---|
| Trade Monday | `Yes` |
| Trade Tuesday | `Yes` |
| Trade Wednesday | `Yes` |
| Trade Thursday | `Yes` |
| Trade Friday | `Yes` |
| Trade Saturday | `No` |
| Trade Sunday | `No` |

**Stops & Targets**

| Setting | Value |
|---|---|
| Stop Loss ORB Percent | `0.0` |
| Take Profit R | `2.0` |
| Enable Fixed Point Stop | `Yes` |
| Fixed Stop Points | `50.0` |

**Multi Take Profit**

| Setting | Value |
|---|---|
| Enable Multi TP | `No` |
| TP1 R | `2.0` |
| TP1 Close Percent | `25.0` |
| TP2 R | `3.0` |
| TP2 Close Percent | `50.0` |
| TP3 R | `3.5` |
| TP3 Close Percent | `25.0` |
| TP4 R | `0.0` |
| TP4 Close Percent | `0.0` |

**Dynamic Stop**

| Setting | Value |
|---|---|
| Enable Dynamic Stop | `Yes` |
| Break Even Trigger R | `1.0` |
| Dynamic Step R | `100.0` |
| Break Even Extra Pips | `0.0` |

**Early Risk Reduction**

| Setting | Value |
|---|---|
| Enable Early Risk Reduction | `No` |
| Early Risk Reduction Trigger R | `0.5` |
| Early Risk Reduction Remaining Risk % | `50.0` |

**Risk**

| Setting | Value |
|---|---|
| Risk Amount | `100.0` |
| Risk Currency | `0` |

**Execution Risk**

| Setting | Value |
|---|---|
| Enable Execution Risk Cap | `No` |
| Assumed Stop Slippage Pips | `80.0` |
| Max Loss Per Trade (Account CCY) | `200.0` |

**Safety**

| Setting | Value |
|---|---|
| Min Risk Pips | `2.0` |
| Max Volume In Units | `0.0` |
| Max Spread Pips | `0.0` |
| Max Distance Beyond Threshold Pips | `0.0` |
| Require Entry Beyond Threshold | `Yes` |
| Entry Retrace Tolerance Pips | `0.0` |
| Enable Margin Safety | `Yes` |
| Max Margin Usage % | `50.0` |
| Clamp Volume To Margin | `Yes` |
| Enable Protection Fallback | `Yes` |
| Fallback SL Pips | `20.0` |

**Diagnostics**

| Setting | Value |
|---|---|
| Bot Label Prefix | `ORBV` |
| Enable Debug Logging | `Yes` |
| Verbose Logging | `No` |
| Explain Blocked Entries | `Yes` |
| Explain Near-Miss Breakouts | `No` |
| Draw ORB Lines | `Yes` |
| Draw Threshold Lines | `Yes` |

---

## Your earlier settings, for reference

The configuration you were running before this round of work, with the clock corrected. Kept here so nothing is lost.


**Session 1 - Range Window**

| Setting | Value |
|---|---|
| Range Time Zone | `EuropeLondon` |
| Range Start (this zone) | `08:00:00` |

**Session 2 - Trading Window**

| Setting | Value |
|---|---|
| Trading Time Zone | `AmericaNewYork` |
| Range End / Market Open | `09:30:00` |
| First Entry Time | `09:31:00` |
| Enable Last Entry Cutoff | `Yes` |
| Last Entry Time | `11:31:00` |
| Enable Force Close | `Yes` |
| Force Close Time | `15:50:00` |

**Session 3 - Legacy**

| Setting | Value |
|---|---|
| Ignore Zones - Use Fixed UTC | `No` |

**ORB**

| Setting | Value |
|---|---|
| ORB Bars TimeFrame | `m1` |
| Max ORB Range Pips | `500.0` |
| Min ORB Range Pips | `0.0` |
| Point Unit Mode | `1` |
| Enable ORB Backfill | `Yes` |
| Enable ORB Self-Heal | `Yes` |
| ORB Self-Heal Interval Seconds | `30` |
| Enable Post-Lock Confirm Replay | `No` |
| Post-Lock Replay Confirm Bars | `1` |
| Post-Lock Replay Max Delay Minutes | `30` |

**Catch-Up Entry**

| Setting | Value |
|---|---|
| Enable Catch-Up Entry | `Yes` |
| Catch-Up Requires Confirmation Bars | `No` |
| Catch-Up Max Distance Beyond Threshold Pips | `0.0` |

**Entry Offset**

| Setting | Value |
|---|---|
| Entry Offset Pips | `0.0` |

**Breakout**

| Setting | Value |
|---|---|
| Confirmation TimeFrame | `m1` |
| Confirmation Bars Count | `1` |
| Breakout Cross Type | `0` |
| Breakout Evaluation Moment | `1` |
| Candle Direction Requirement | `1` |
| Allow Long | `Yes` |
| Allow Short | `No` |

**Volume Filter**

| Setting | Value |
|---|---|
| Enable Volume Filter | `Yes` |
| Volume Multiplier | `1.4` |
| Volume Lookback Bars | `20` |

**Trend Filter**

| Setting | Value |
|---|---|
| Enable Trend Filter | `Yes` |
| Trend TimeFrame | `m15` |
| Trend EMA Period | `9` |
| Trend Slope Lookback Bars | `3` |
| Trend Min Slope Pips | `0.0` |
| Neutral Min Slope Pips | `0.0` |
| Trend Neutral Policy | `0` |
| Trend Filter Verbose Logs | `No` |

**Trades Per Day**

| Setting | Value |
|---|---|
| Max Trades Per Day | `1` |
| Re-Entry Mode | `0` |
| Block Same-Bar Re-Entry | `Yes` |

**Trading Days**

| Setting | Value |
|---|---|
| Trade Monday | `Yes` |
| Trade Tuesday | `Yes` |
| Trade Wednesday | `Yes` |
| Trade Thursday | `Yes` |
| Trade Friday | `Yes` |
| Trade Saturday | `No` |
| Trade Sunday | `No` |

**Stops & Targets**

| Setting | Value |
|---|---|
| Stop Loss ORB Percent | `0.0` |
| Take Profit R | `50.0` |
| Enable Fixed Point Stop | `Yes` |
| Fixed Stop Points | `50.0` |

**Multi Take Profit**

| Setting | Value |
|---|---|
| Enable Multi TP | `No` |
| TP1 R | `2.0` |
| TP1 Close Percent | `25.0` |
| TP2 R | `3.0` |
| TP2 Close Percent | `50.0` |
| TP3 R | `3.5` |
| TP3 Close Percent | `25.0` |
| TP4 R | `0.0` |
| TP4 Close Percent | `0.0` |

**Dynamic Stop**

| Setting | Value |
|---|---|
| Enable Dynamic Stop | `Yes` |
| Break Even Trigger R | `0.6` |
| Dynamic Step R | `1.0` |
| Break Even Extra Pips | `4.5` |

**Early Risk Reduction**

| Setting | Value |
|---|---|
| Enable Early Risk Reduction | `Yes` |
| Early Risk Reduction Trigger R | `0.5` |
| Early Risk Reduction Remaining Risk % | `50.0` |

**Risk**

| Setting | Value |
|---|---|
| Risk Amount | `100.0` |
| Risk Currency | `0` |

**Execution Risk**

| Setting | Value |
|---|---|
| Enable Execution Risk Cap | `No` |
| Assumed Stop Slippage Pips | `80.0` |
| Max Loss Per Trade (Account CCY) | `200.0` |

**Safety**

| Setting | Value |
|---|---|
| Min Risk Pips | `2.0` |
| Max Volume In Units | `0.0` |
| Max Spread Pips | `0.0` |
| Max Distance Beyond Threshold Pips | `0.0` |
| Require Entry Beyond Threshold | `Yes` |
| Entry Retrace Tolerance Pips | `0.0` |
| Enable Margin Safety | `Yes` |
| Max Margin Usage % | `50.0` |
| Clamp Volume To Margin | `Yes` |
| Enable Protection Fallback | `Yes` |
| Fallback SL Pips | `20.0` |

**Diagnostics**

| Setting | Value |
|---|---|
| Bot Label Prefix | `ORBV` |
| Enable Debug Logging | `Yes` |
| Verbose Logging | `No` |
| Explain Blocked Entries | `Yes` |
| Explain Near-Miss Breakouts | `No` |
| Draw ORB Lines | `Yes` |
| Draw Threshold Lines | `Yes` |
