# Gamma tests — pre-registered plan (written 2026-09-29, before any results were seen)

Data: `research/data/squeezemetrics_dix_gex.csv`. A trade on day D uses **GEX dated D-1** (no look-ahead).

**Gamma regime.** Percentile rank of GEX(D-1) within the 252 trading days ending at D-1.
Low tercile < 33.3%, high tercile > 66.7%. Also reported: sign of GEX(D-1) (negative vs positive).

## Test 1 — US500 15m ORB (existing bot)
- Trades: `ORB Projects/US500 ORB Bot/analysis/us500_trades.csv` (2022-01 .. 2026-08), **first trade per day** (the recommended config). All trades reported as secondary.
- Hypothesis: breakouts pay more on low-gamma days (dealer hedging extends moves).
- Primary statistic: mean net R, low tercile minus high tercile. One-sided permutation test, 10,000 shuffles.
- Pass: p < 0.05 **and** low > high in at least 3 of the 5 calendar years.

## Test 2 — Last-half-hour momentum (strategy B)
- Data: NAS100 and US30 M5 (`US30 London Range Breakout/data`), 2023-07 .. 2026-07. No US500 intraday data is stored.
- Prices at New York time: previous close = 16:00 of the prior session, P10:00, P15:30, P16:00 (closes of the 5-minute bars ending at those times).
- Signals (Baltussen et al. 2021): ROD = sign(P15:30 / prev close - 1); ONFH = sign(P10:00 / prev close - 1); BOTH = trade only if they agree.
- Trade: enter at 15:30, exit at 16:00, return = signal x (P16:00 / P15:30 - 1), in basis points.
- Costs, round trip: NAS100 1.5 points, US30 2.5 points (assumed retail CFD spread; sensitivity at 0x and 2x).
- Questions: (a) is net expectancy > 0 over the whole period and in each year? (b) does it depend on the gamma regime (low minus high tercile, one-sided permutation test)?
- Pass for (a): net mean > 0 with t > 2 on the ROD signal. This window is short (about 3 years), so a fail means "not shown", not "disproved".
