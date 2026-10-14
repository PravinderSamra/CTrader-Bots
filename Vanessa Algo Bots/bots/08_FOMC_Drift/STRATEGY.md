# Pre-FOMC Drift bot (plain words)

## Why it should work
US stock indices have tended to rise in the 24 hours before a scheduled Federal Reserve (FOMC) announcement
(Lucca & Moench, Journal of Finance 2015). The usual explanation is a risk premium for holding stocks into a
big, uncertain event. It is the one academic calendar effect that still worked after FTMO costs in our SSRN review.

## The rules
- Markets: US100.cash and US500.cash.
- **Buy at 14:00 New York time on the first day of each scheduled Fed meeting** (the day before the statement).
- **Sell at 13:58 New York time on announcement day**, just before the 14:00 statement (we don't hold through it).
- About 8 meetings a year, so about 16 trades a year (2 indices).
- Safety stop 3% below the entry (the worst event since 2014 was -1.9%).
- The meeting dates are a setting (from federalreserve.gov), already filled in for 2021-2027.

## Size
"Notional Per Position" = $20,000 per index. A typical event moves the position by about $150 either way;
the worst event since 2014 would have been about -$380 per index (-1.9%).

## Test results (research/ssrn/fomc_drift.py, 1-hour bars, after costs and one night of swap)
| | Per trade | 2014-20 | 2021-23 | 2024-26 |
|---|---|---|---|---|
| NAS100 | +0.22% | +0.13% | +0.48% | +0.14% |
| US500 | +0.14% | +0.12% | +0.30% | +0.02% |
Expected roughly +$40-70 a meeting at $20k per index, about $500-600 a year. Correlation with the NAS bot 0.02.
Small, independent, and weakening lately: a small add-on, not an income engine.

## Backtest to run
- Attach **FOMC_Drift.cs** to a **US100.cash, 1 hour** chart. Defaults.
- **M1 bars**, **1 Jan 2021 to today**, balance 100,000, commission 30. Send the log and a screenshot.
- Pass if: profitable overall and in both 2021-23 and 2024-26 for US100.

## Upkeep
Once a year, check the Fed's calendar (federalreserve.gov/monetarypolicy/fomccalendars.htm) and add the next
year's meeting day-1 dates in "Extra Dates". The 2027 dates are already included.

## Switch-off rule (monthly review)
Pause if the last 16 trades (one year) are net negative, or if a single event loses more than 3%.
