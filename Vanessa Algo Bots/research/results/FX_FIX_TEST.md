# FX fix reversal (strategy C) — verdict (2026-09-29): **FAIL, parked**

Plan (committed before the data was downloaded): `../FX_FIX_TEST_PLAN.md`. Full tables: `FX_FIX_TEST_RAW.md`.

## Calibration 2012–2018 (inside the paper's sample): the effect is there
EURUSD gross: pre-fix leg +2.37 bp/day, post-fix leg +1.33 bp/day (GBPUSD +1.15 / +0.80).
Both legs positive on both pairs, as the paper reports, so our data and timing are sound.
After a 1-pip cost it was already thin (EURUSD both legs +2.03 bp/day, t 1.82).

## Test 2019–2026 (after the paper's sample): the effect is gone
| EURUSD, 1-pip cost | Net per day | t | Positive years |
|---|---|---|---|
| Pre-fix (08–16, long USD) | −0.68 bp | −0.87 | 4 of 8 |
| Post-fix (16–21, short USD) | −1.09 bp | −2.41 | 1 of 8 |

Gross (before costs) both legs together: +0.02 bp/day, i.e. nothing. GBPUSD agrees (both legs −1.59 bp/day net).
Worst year 2025 (EURUSD −8.4 bp/day both legs). Fails every pre-registered criterion.

## Reading
A published, top-journal effect that was real through 2018 has disappeared since. That is the same
pattern as strategies A and B, and it is well documented in general: returns of published anomalies
shrink sharply after publication (McLean & Pontiff, Journal of Finance 2016).

## Decision
Strategy C parked. No parameter changes will be tried on these data (that would be fitting to the test set).
