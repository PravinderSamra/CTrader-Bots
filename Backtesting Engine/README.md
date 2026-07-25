# Backtesting & Optimisation Engine

**Status:** Phase 1 complete — research done, build specification written, ready for implementation.

## What this is

A backtesting and parameter-optimisation engine for the cTrader cBots in this repo
(ORB Bot, ThreeDownDaysBot, IchimokuRsiSwingBot, and future bots built on the shared
Base Parameters framework). It is designed to be **operated by an AI agent**: the agent
takes a bot's `.cs` source, a parameter search-space definition, and market data from
the repo, then runs a staged optimisation pipeline that finds parameter sets which are
**robust** — not merely the best historical fit.

The explicit goal ordering is: **survive live conditions first, maximise performance
second.** Target metrics: good Sharpe ratio, controlled drawdown, high profit factor —
validated out-of-sample, not in-sample.

## Key architectural decision (read this first)

We do **not** re-implement the strategies in Python. The engine drives the **official
cTrader CLI backtester** (`ghcr.io/spotware/ctrader-console` Docker image), which runs
the *actual compiled cBot* (`.algo`) with *actual cTrader execution logic* against
`m1-csv` data — the same M1 OHLCV CSVs already stored in this repo. A Python
"intelligence layer" sits on top and handles search, walk-forward, Monte Carlo,
overfitting statistics, and reporting.

Rationale, alternatives considered, and fallback plans are in
[01-Research-Findings.md](01-Research-Findings.md) §2.

## Documents

| File | Purpose | Audience |
|---|---|---|
| [01-Research-Findings.md](01-Research-Findings.md) | Phase 1 research: engine architecture options, anti-overfitting methodology (walk-forward, Monte Carlo, DSR/PBO, plateau analysis), metric definitions, data considerations | You (the trader) + any model |
| [02-Build-Specification.md](02-Build-Specification.md) | Explicit, module-by-module build instructions with file layout, schemas, formulas, CLI contracts, acceptance tests | Opus (implementer) |

## Pipeline at a glance

```
bot .cs ──compile──> .algo ─┐
search_space.yaml ──────────┤
repo M1 CSV ──convert───────┼──> Stage 0  Parity & smoke test (engine trusted?)
                            ├──> Stage 1  Coarse search (Optuna, in-sample only)
                            ├──> Stage 2  Walk-forward analysis (rolling IS/OOS)
                            ├──> Stage 3  Robustness: plateau, Monte Carlo, regime slices
                            ├──> Stage 4  Overfit statistics: DSR, PBO gates
                            ├──> Stage 5  One-shot untouched holdout test
                            └──> Report + recommended .cbotset (or explicit REJECT)
```

A parameter set must pass **every gate** to be recommended. "No robust parameter set
exists for this bot on this market" is a first-class, honest output of the engine.

## What is needed from the trader (blocking items for the build)

1. **Demo cTrader account credentials** for the CLI (`--ctid`, password file,
   `--account`). The CLI needs a login even for backtesting (symbol metadata).
   Provide as environment secrets — never committed to the repo.
2. **Broker execution profile** per symbol you trade: typical spread (pips),
   commission, observed live slippage. Used for realistic + stressed simulation.
3. **Risk constraints**: account size the results should be scaled to, maximum
   acceptable drawdown (% and £), and minimum trades/year you consider tradeable.
4. **Market data per target market** in the same format as
   `XAUUSD historical Pricing data/data/` (the fetch script there is reusable).
   XAUUSD 2021–2026 M1 is already present. UK100 (for ORB) still needs an export.
5. Confirmation of **which bot × market pairs to optimise first**.

## Repo data currently available

- `XAUUSD historical Pricing data/data/XAUUSD_M_1_{2021..2026}.csv` — 1-minute OHLCV,
  UTC, ~5.5 years, `datetime,open,high,low,close,volume` (volume = tick count).
