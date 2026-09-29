# Gamma tests — verdict (2026-09-29)

Plan written before the run: `../GAMMA_TEST_PLAN.md`. Full tables: `GAMMA_TESTS_RAW.md`.
Script: `../scripts/gamma_tests.py` (standard library only, about 20 s).

## Test 1 — Does gamma improve the US500 15m ORB? **No (fail).**

| First trade per day | Trades | Mean R |
|---|---|---|
| Low-gamma tercile | 335 | +0.097 |
| Mid | 287 | +0.029 |
| High-gamma tercile | 315 | +0.092 |

Low minus high = +0.005 R, permutation p = 0.47. Low beat high in 3 of 5 years, but the
pooled difference is zero, so the pass rule (p < 0.05 and 3 of 5 years) is not met.
The ORB edge is spread evenly across gamma regimes; a gamma filter would only cut trades.

## Test 2 — Does last-half-hour momentum work on NAS100 / US30 (2023-07 .. 2026-07)? **No; it ran backwards.**

| | Signal | Trades | Net mean per trade | Net t |
|---|---|---|---|---|
| NAS100 | ROD (Baltussen's best) | 735 | −3.04 bp | −3.13 |
| US30 | ROD | 735 | −1.74 bp | −2.53 |

- Negative in every year on both instruments, and still negative with zero costs (NAS100 −2.29 bp, US30 −1.14 bp gross).
- The first-half-hour signal and the both-agree version are negative too.
- Gamma did not rescue it: low minus high tercile was −0.27 bp (NAS100, p = 0.54) and −2.28 bp (US30, p = 0.91).
  US30 on the 32 negative-GEX days was +2.68 bp (t = 0.52): too few days to mean anything.

Data check: prices at 10:00 / 15:30 / 16:00 New York time match known closes (e.g. NAS100 2025-04-09
tariff-pause rally 17,287 → 18,989 → 19,090).

### Reading it
- Baltussen et al. measured 1974–2020 futures. Over 2023–2026 on CFDs the effect is not just gone but
  slightly reversed: the last half hour tended to pull back against the day's move.
- This matches the noise-area strategy fading since 2025, and the SqueezeMetrics series showing dealers
  long gamma almost every day since 2024 (1 negative day in 2024, 9 in 2025, 9 in 2026 to date).
  Long-gamma dealers sell rallies and buy dips into the close, which is a reversal force.
- Three years is short, and a reversal of about 2–3 bp is too small to trade profitably after costs.
  Do not flip this into a "fade the last half hour" bot on this evidence: that would be fitting to what we just saw.

## Decisions
- Strategy B (last-half-hour momentum): **parked**, same as A. Both rely on the same dealer-hedging engine,
  which the recent data says is not running.
- Keep the gamma data and this script. If negative-gamma periods return (as in 2022), re-run both tests.
- Our US500 ORB stays as it is: no gamma filter.
