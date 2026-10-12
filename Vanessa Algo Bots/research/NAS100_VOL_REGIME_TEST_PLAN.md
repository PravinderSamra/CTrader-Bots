# Pre-registered test: does the NAS bot do worse after very calm or very volatile days? (written 12 Oct 2026, before running)

Found while checking Gianluca Bruni's ideas (Chart Fanatics): on the live bot's ladder log, July 2023 - July 2026, days
after the previous NY session (09:30-16:00) range was in the top quarter averaged -0.49R (81 days), the bottom quarter
-0.11R (80 days), the middle half +0.78R / +0.97R. Four buckets were looked at once, so this may be luck.

Fixed thresholds (quartiles of the NY-session range as % of price, Jul 2023 - Jul 2026, cTrader NAS100 m5):
calm = previous range < 0.877%; volatile = previous range > 1.651%.

Test period, not used to find the effect: 4 Jan 2021 - 5 Jul 2023 (bot ladder log days; previous-day range from
data/nas100_m30/nas100_m30_2021_2023.csv, 09:30-16:00 NY M30 bars).
Pass (filter worth adopting) if, in the test period: days after a "volatile" day average < 0R AND below the middle days
by at least 0.4R. Same rule judged separately for "calm". Anything else: no filter, the 2023-26 pattern was chance.
Note 2022 was a high-volatility year, so the "volatile" bucket will hold more days than in 2023-26; that is expected.

## Result (run once, 12 Oct 2026), 2021-01-04 .. 2023-07-05
| Previous NY-session range | Days | Win | Expectancy |
|---|---|---|---|
| Calm (< 0.877%) | 49 | 33% | **-0.20R** |
| Middle | 109 | 40% | +0.29R |
| Volatile (> 1.651%) | 135 | 38% | **+0.63R** |

- **Volatile: FAIL.** In 2021-23 these were the best days (+0.63R). The 2023-26 result was chance. No filter.
- **Calm: PASS (narrowly).** Below 0R and 0.49R below the middle days. Across both periods: 129 days after a calm
  session, all negative (-0.11R and -0.20R). Small sample (standard error ~0.3-0.4R per bucket).
- Next step: an optional "skip the day after a calm NY session" switch in a NEW bot version (live bot untouched),
  default off; full 2021-2026 cTrader tick-data run with it on vs off before any change to live settings.
