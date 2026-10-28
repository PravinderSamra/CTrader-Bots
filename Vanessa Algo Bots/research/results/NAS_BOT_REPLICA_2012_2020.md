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
