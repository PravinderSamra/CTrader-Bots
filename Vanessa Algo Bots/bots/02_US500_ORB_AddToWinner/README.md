# US500 ORB — v3.0 Add To Winner

Your live US500 ORB bot (`ORB Projects/ORB Bot/ORB_Bot.cs`, ORB Breakout v2.0) with the same optional
**Add To Winner** feature as the NAS100 version. **With "Enable Add To Winner" = No it trades exactly like the live bot.**

Separate bot (`OrbBreakoutBotV3Atw`, label prefix `ORBA`), so it can sit next to the live bot (`ORB`) without either
touching the other's trades. Compiled against the official cTrader.Automate package: 0 errors, 0 warnings.
Only five original lines changed (class name, label prefix, start-up registration and a position loop); the rest is added.

The parameters and behaviour are identical to the NAS100 version; see
`../01_NAS100_London_Range_AddToWinner/README.md` for the full table and worked example.

## What is different on US500
The US500 bot tightens its stop in two stages (in the tested configuration): risk down to **37% at +0.74R**, then
**break-even at +1.2R**, then trailing in 1R steps. The add sizes itself from whatever risk has been removed at the
moment it triggers, so the trigger level changes the add size a lot:

| Add Trigger R | Stop at that point | Risk removed | Add risk at Add Size 1.0 |
|---|---|---|---|
| 0.74 | −0.37R | 0.63R | 0.63R |
| 1.0 | −0.37R | 0.63R | 0.63R |
| 1.2 | break-even | 1.0R | 1.0R |

So on US500 it is worth testing **Add Trigger R = 1.0 and 1.2** as well as the Add Size values.

## Suggested backtest plan (cTrader, US500, 2022–2026)
1. Load your live US500 `.cbotset` into this bot.
2. **Enable Add To Winner = No** first: the result must match your original backtest.
3. Then Add Size **1.0, 1.5, 2.0**, each with Add Trigger R **1.0** and **1.2** (six runs).
4. Send me the logs; every add prints an `ADD TO WINNER:` line.

## Before you run (added after the first match check)
- **Use the same data setting for every run** (tick data *or* 1-minute bars, not a mix).
- **Set "Quiet Log (hide repeated warnings)" = Yes** (Diagnostics group) so a multi-year log is not cut off by
  repeated warnings. Trading is unaffected. For the match check, compare the backtest summary numbers.
