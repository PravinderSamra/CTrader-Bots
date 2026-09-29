# London-open range breakout — verdicts

## XAUUSD: **FAIL** (2026-09-29)
- Training 2021-07 .. 2024-06: all four settings lost money (mean −0.05R to −0.14R per trade, 485 trades each).
- Chosen setting (stop 0.4 x median day range, 2R): test 2024-07 .. 2026-07 +0.005R per trade (212 trades, t 0.06);
  fails all four criteria.
- Data problem found: the feed's gold tick volume is capped, so the volume filter stops passing from about May 2026
  (no trades after 2026-05-06). Diagnostic on training only, volume filter off: still −0.03R to −0.13R on all settings.
  The cap is not what sinks gold; the London-open breakout simply has no edge on it after costs.
- Full tables: `LONDON_BREAKOUT_XAUUSD_RAW.md`; trades: `london_breakout_xauusd_trades.csv`.
