# London-open range breakout (gold, EURUSD) — pre-registered plan
Written 2026-09-29, before any results were seen. Modelled on the NAS100 London Range Volume Breakout bot
(range before the open, M5 close beyond it, 1.2x tick-volume filter, fixed stop, R target, one trade a day).

## Instruments and data
- XAUUSD: 1-minute bars 2021-07 .. 2026-07 (`XAUUSD historical Pricing data/data`), aggregated to 5-minute for signals;
  stops/targets resolved on 1-minute bars.
- EURUSD: 5-minute bars 2021-06 .. 2026-09 (cTrader feed); stops/targets resolved on 5-minute bars.
- All times Europe/London (DST-aware). Weekdays only.

## Rules (identical for both instruments)
- **Range:** high and low of 00:00–07:00 UK (the Asian session).
- **Signal window:** 5-minute bars closing between 08:05 and 11:00 UK.
- **Signal:** the first bar whose close is above the range high (long) or below the range low (short), with tick volume
  >= 1.2 x the average of the previous 20 five-minute bars. A bar that fails the volume test is skipped, not a stand-down.
- **Entry:** open of the next bar. One trade per day.
- **Stop:** fixed distance from entry = S x the median daily range (00:00–21:00 UK) of the previous 20 days.
- **Target:** R x stop distance. **Exit** at 20:55 UK if neither is hit. If stop and target fall in the same bar, count the stop.
- **Costs per round trip:** gold base $0.35/oz, stress $0.70 (FTMO metals commission $5.81/lot = $0.06/oz, plus spread);
  EURUSD base 1.0 pip, stress 2.0 pips.

## Settings searched (only these four) and how one is chosen
S in {0.25, 0.40}, R in {2.0, 3.5}. On the **training period 2021-07-01 .. 2024-06-30**, pick the setting with the highest
net mean R at base cost among those with >= 150 trades (tie: the smaller stop). That one setting is then run **once** on the
**test period 2024-07-01 .. end of data**. No other settings will be tried on the test period.

## Pass criteria (test period, base cost), per instrument
1. Net mean R > 0 with bootstrap probability of a true edge <= 0 below 5%;
2. positive in each calendar half-year of the test period, allowing at most one negative half-year;
3. still positive after removing the 5 best trades;
4. still positive at the stress cost.

## Amendment 1 (2026-09-29, after the gold run, before any EURUSD result was seen)
The gold 1-minute tick volume from this cTrader feed is capped (maximum per minute fell from ~520 to 240 by 2026),
so on busy mornings every bar sits at the cap and the 1.2x volume test cannot pass. Before running EURUSD:
check its 5-minute tick volume for the same cap (a hard ceiling that many bars sit on, in any quarter).
If capped, the volume filter is dropped for EURUSD over the whole period, training and test alike. Nothing else changes.
