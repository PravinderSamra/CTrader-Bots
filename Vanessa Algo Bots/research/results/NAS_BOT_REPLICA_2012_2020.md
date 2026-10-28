# NAS bot core replica: regime check 2012-2020 (28 Oct 2026; live bot untouched)
Script: screens/nas_bot_replica.py (range 08:00 London - 09:30 NY, close beyond range +/-10 pts with volume >= 1.2x the
20-bar average, entries from 10:00 NY, 60-pt stop, TP 4.5R, stop to -0.7R at +0.7R, trail from +2.5R in 0.1R steps,
flat 15:50 NY; main trade only, adds to winners not modelled).

Calibration on the live bot's own period: daily results correlate +0.88 with the real cTrader ladder log, same sign on
96% of 576 shared days. FTMO data 2020-06 .. 2026-07 (live 60-pt stop): +90.0R, 1,284 trades, every year positive
(2020 +15.3, 2021 +11.6, 2022 +24.5, 2023 +14.6, 2024 +12.5, 2025 +6.1, 2026 +5.4), max DD 24.3R.

Unseen 2013-2020 (Dukascopy, stop and offset scaled to price: 60/10 pts at 20,000): +60.7R, 1,520 trades, avg +0.04R
(vs +0.07R since 2020), max DD 33.7R. By year: 2013 -1.3, 2014 +13.4, 2015 -11.3, 2016 -0.7, 2017 +18.5, 2018 +28.3,
2019 -5.9, 2020 (to June) +19.6. Losing years: 4 of 7 full years (2013, 2015, 2016, 2019).
Caveats: the scaled stop matters (on 2023-26 the scaled version gave 2023 -7.8R vs +14.6R with the live 60 pts);
Dukascopy volume differs from FTMO tick volume; adds amplify both directions.
Reading: the bot's edge also existed before 2020 but was about half as strong and lumpier (profit concentrated in
2017-18; year-long flat/losing spells). The monthly switch-off rule matters; no change to the live bot (Vanessa's call).

## With adds to winners (ADDS=1: at +0.7R one add with 1.5R of risk, shared stop and target; matches the live log)
Calibration 2021-26: correlation +0.90 with the live ladder log; replica +186.7R vs live +216.8R on 576 shared days (86%).
Replica by year 2021-26: 27.8 / 46.2 / 30.3 / 29.1 / 17.7 / 10.5R (live log 35.2 / 41.7 / 30.2 / 30.9 / 33.7 / 57.3R).
FTMO 2020-06 .. 2026-07: +198.2R, +0.154R a trade, every year positive, max DD 38.9R.
Unseen 2013-2020 (Dukascopy, scaled stop): +130.2R, +0.086R a trade, max DD 45.8R. By year: 2013 -6.9, 2014 +35.9,
2015 -7.1, 2016 -0.4, 2017 +35.1, 2018 +37.0, 2019 +11.3, 2020 (to June) +25.3. Losing years 3 of 7, all small.
Reading: with the adds the bot holds up well before 2020: about 55% of its recent strength, losing years small.
