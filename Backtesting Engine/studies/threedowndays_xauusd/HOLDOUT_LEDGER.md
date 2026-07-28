# Holdout ledger — threedowndays_xauusd_v1

Append-only. The holdout window (2025-07-01 → 2026-07-16) is **single use**. Once it
has been looked at, it is burned: it can no longer tell you anything you did not
already influence. `engine holdout` appends to this file *before* it runs, refuses to
run a second time, and makes the study immutable afterwards.

If the holdout fails, the answer is not a new candidate — it is back to strategy
design, with a new study and genuinely fresh data (or a forward demo run).

| # | Date (UTC) | Candidate | Verdict at Stage 4 | Holdout result | Operator |
|---|---|---|---|---|---|
| _(no holdout runs yet)_ | | | | | |
