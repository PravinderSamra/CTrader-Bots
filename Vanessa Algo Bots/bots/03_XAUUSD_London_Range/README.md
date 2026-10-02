# XAUUSD London Range breakout — v3.4 (stop as % of price)

A copy of the NAS100 v3.0 Add To Winner bot with one extra setting in "Stops & Targets": **Fixed Stop as % of Price**.
With Enable Fixed Point Stop = Yes and this above 0, the stop distance is that % of the entry price, so it grows with
gold's price level. At 0 it behaves exactly like v3.0 (Fixed Stop Points).

Why: gold was about $1,650–2,100 in 2021–23 but much higher since, so a fixed $6 stop gets relatively tighter every year.

## Settings for the gold test
NAS100 base settings (Add To Winner off, TP 4R, no dynamic stop, risk reduction 0.7R / 70%, range 02:00–09:30 NY,
entries 10:00–11:00 NY, close 15:50 NY), plus:

| Setting | Value |
|---|---|
| Enable Fixed Point Stop | Yes |
| **Fixed Stop as % of Price** | **0.32** (= the winning $6 stop at the 2021–23 average gold price of about $1,850) |
| Max / Min ORB Range Pips | 0 / 0 |
| Commission | 7 (FTMO: 0.0014%) |
| Risk Amount | 300 |
| Trade Saturday / Sunday | No / No |
| Data | Tick data |
| Trades-Only Log | Yes |

1. Sanity check: 1 Jan 2021 – 31 Dec 2023 should land near the fixed-stop results (about +$7–8k).
2. Test, run once: 1 Jan 2024 – 28 Sep 2026. Send the log.

Class `OrbVolumeBreakoutBotV34PctStop`, label prefix `ORBG`. Compiles with 0 errors and 0 warnings.
