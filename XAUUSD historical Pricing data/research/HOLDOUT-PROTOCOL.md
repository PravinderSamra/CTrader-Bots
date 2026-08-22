# Holdout Protocol — declared BEFORE any optimisation

To keep the final validation honest, the data is split now and the split is not
revisited. This file is committed before the first V2 backtest is run.

| Set | Period | Days | Use |
|---|---|---|---|
| **DEV** | 2021-07-18 → 2025-07-16 | ~1,010 | All hypothesis generation, tuning, iteration |
| **HOLDOUT** | 2025-07-17 → 2026-07-16 | ~250 | Touched ONCE, at the end, on the final locked config |

Rules:
1. Every iteration in `20_v2_engine.py` reads DEV only. The engine raises if a
   dev-mode run is handed holdout dates.
2. The holdout is scored once, in `21_v2_holdout.py`, on a config that is frozen
   in writing beforehand. No re-tuning after seeing holdout results.
3. If the holdout fails, the honest outcome is reported as a failure — the config
   is not re-optimised to rescue it.
4. Number of dev-set configurations evaluated is counted and reported for the
   multiple-testing haircut.

Note: the holdout period (2025-07 → 2026-07) is the most volatile regime in the
sample (ATR $75 -> $205). That is deliberately a hard test: a config that only
works in calm markets will fail it.
