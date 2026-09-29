# London-open range breakout — verdicts

## XAUUSD: **FAIL** (2026-09-29)
- Training 2021-07 .. 2024-06: all four settings lost money (mean −0.05R to −0.14R per trade, 485 trades each).
- Chosen setting (stop 0.4 x median day range, 2R): test 2024-07 .. 2026-07 +0.005R per trade (212 trades, t 0.06);
  fails all four criteria.
- Data problem found: the feed's gold tick volume is capped, so the volume filter stops passing from about May 2026
  (no trades after 2026-05-06). Diagnostic on training only, volume filter off: still −0.03R to −0.13R on all settings.
  The cap is not what sinks gold; the London-open breakout simply has no edge on it after costs.
- Full tables: `LONDON_BREAKOUT_BOTH_RAW.md`; trades: `london_breakout_xauusd_trades.csv`.

## EURUSD: **FAIL** (2026-09-29)
- Volume check (Amendment 1): no ceiling (one bar per quarter at the maximum); the volume filter was kept as planned.
  Volume levels are lower from 2026 Q2 but not capped.
- Training 2021-07 .. 2024-06: all four settings slightly negative (−0.02R to −0.04R per trade, 622 trades each).
- Chosen setting (stop 0.4 x median day range, 2R): test 2024-07 .. 2026-09 −0.001R per trade (418 trades), −0.04R at
  the stress cost. Half-years +10.0, −2.2, −12.1, +5.7, −1.7R. Fails all four criteria.
- Trades: `london_breakout_eurusd_trades.csv`. Data: `research/data/eurusd_m5/` (cTrader feed, 2021-06 .. 2026-09).

## Reading
The London-open breakout of the Asian range does not pay on gold or EURUSD after costs, in any setting tested.
The NAS100 bot's range breakout works on a US index at the New York open; the same idea at the London open on
gold and EURUSD, like FTSE and DAX before them, does not.
