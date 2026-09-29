# FX fix reversal (strategy C) — pre-registered plan (written 2026-09-29, before downloading data)

Source: Krohn, Mueller & Whelan (2024, Journal of Finance): dollar strengthens into the 16:00 London (WM/R)
fix and weakens after it. Paper sample 1999–2018.

## Data
EURUSD (primary) and GBPUSD (secondary) H1 bars from the cTrader feed (Pepperstone demo), 2012-01 .. 2026-09.
Stored in `research/data/`. Times converted to Europe/London (DST-aware). Weekdays only; a day is skipped
if any of the needed bars is missing.

## Rules (UK time; price at HH:00 = open of the H1 bar starting at HH:00)
- **Pre-fix leg:** sell the pair (long USD) at 08:00, buy back at 16:00.
- **Post-fix leg:** buy the pair (short USD) at 16:00, sell at 21:00 (our window ends at 21:00; the paper held to 22:00 UK).
- **Both legs:** the sum of the two on the same day.
- Return per trade in basis points; cost per round trip: base **1.0 pip**, stress **2.0 pips**
  (FTMO estimate 0.7–1.2 pips, see `results/FX_FIX_COSTS.md`).

## Periods
- **Calibration, 2012–2018** (inside the paper's sample): checks that our data and timing reproduce the effect.
  Expected: gross mean > 0 for both legs. If not, our setup differs from the paper and the test result is not interpretable.
- **Test, 2019-01-01 .. 2026-09-28** (after the paper's sample): the real question.

## Pass criteria (EURUSD, test period, base cost) — decided now
- Post-fix leg: net mean > 0 **and** t > 2 **and** positive in at least 5 of the 8 calendar years 2019–2026.
- Pre-fix leg: same criteria, judged separately.
- GBPUSD is reported as a replication; it does not rescue a EURUSD fail.
- No parameter search: times are fixed above and will not be changed after seeing results.
