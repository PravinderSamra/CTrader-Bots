# Build Specification — Backtesting & Optimisation Engine

**Audience:** Opus (implementing model). This document is the contract for the build.
**Prerequisite reading:** `01-Research-Findings.md` (methodology and rationale — this
spec assumes you have read it; formulas and gates defined there are normative).
**Rule:** where this spec says MUST, do exactly that. Where it says SHOULD/MAY, use
judgement and record the decision in `Backtesting Engine/engine/DECISIONS.md`.

---

## 0. Scope of the build

Deliver a Python package + Docker-based toolchain, living at
`Backtesting Engine/engine/`, exposing one CLI (`engine …`) that implements the
staged pipeline: data prep → compile → smoke/parity → optimise (search + walk-forward)
→ validate (plateau, Monte Carlo, regime, DSR/PBO) → holdout → report.

Out of scope for v1: live/demo deployment automation, tick-data modes, data-level
noise-injection MC (design for it, stub it), any GUI.

**First study target:** ThreeDownDaysBot × XAUUSD (simplest bot, data already in
repo). Second: ORB Bot × XAUUSD. UK100 waits for data.

---

## 1. Environment & toolchain

- Host requirements: Linux, Docker, Python ≥3.11. All heavyweight tools run in
  containers so the host stays clean.
- **cTrader CLI**: official image `ghcr.io/spotware/ctrader-console:latest`. Wrap all
  invocations in `engine/ctcli.py`; never call docker inline elsewhere. Mount a
  per-run workdir; pass credentials via env/secret file (path from env var
  `CTRADER_CLI_SECRETS`, git-ignored; MUST fail with a clear message if unset).
- **Bot compilation**: .NET 8 SDK container (`mcr.microsoft.com/dotnet/sdk:8.0`).
  Generate a throwaway classlib csproj referencing NuGet `cTrader.Automate` (latest),
  copy the bot `.cs` in, `dotnet build -c Release` → `.algo` artefact. Cache keyed on
  SHA256 of (bot source + package version). One bot file = one algo. If a bot fails
  to compile against the modern API, stop and report — do not patch bot source
  silently. (Trivial compile fixes MAY be proposed as a separate PR for the trader.)
- **Python deps** (pin in `pyproject.toml`): `optuna`, `pandas`, `numpy`, `scipy`,
  `pyyaml`, `jinja2` (reports), `matplotlib` (plots), `typer` or `argparse` (CLI),
  `sqlite` via stdlib/optuna storage. No heavyweight backtesting libs — the CLI is
  the backtester.
- Everything MUST run non-interactively (agent-operated): no prompts except the
  explicit `--confirm` guard on `engine holdout`.

### 1.1 Credentials & secrets

`CTRADER_CLI_SECRETS` points to a YAML: `ctid`, `password_file`, `account_id`,
`broker`. README section MUST tell the trader exactly how to create it. MUST be
covered by `.gitignore`; add a pre-commit guard that greps staged files for the
ctid value pattern.

---

## 2. Directory layout (create exactly this)

```
Backtesting Engine/
  README.md, 01-…, 02-…            # docs (exist)
  engine/                          # the Python package
    pyproject.toml
    engine/                        # package src
      cli.py                       # `engine` entrypoint (subcommands per stage)
      config.py                    # study.yaml + search_space.yaml schema & loader
      data.py                      # converters + audits (§3)
      compile.py                   # .cs → .algo (§1)
      ctcli.py                     # cTrader CLI wrapper + result parser (§4)
      cbotset.py                   # parameter-file generator (§5)
      runner.py                    # parallel backtest executor + cache (§6)
      metrics.py                   # canonical metrics (§7)
      optimise.py                  # Optuna stages (§8)
      walkforward.py               # WFA engine (§9)
      plateau.py                   # neighbourhood analysis (§10)
      montecarlo.py                # MC battery (§11)
      overfit.py                   # DSR + PBO/CSCV (§12)
      gates.py                     # verdict logic (§13)
      report.py                    # dossier generation (§14)
    tests/                         # pytest suite (§16)
    DECISIONS.md
  studies/
    <study_name>/
      study.yaml                   # the study contract (§2.1)
      search_space.yaml            # per-bot hypothesis file (§5.2)
      runs/…                       # artefacts: trials.db, trade lists, reports
      HOLDOUT_LEDGER.md            # append-only: every holdout touch recorded
  data/
    prepared/<symbol>/<hash>/…     # converted+audited CSVs, audit report alongside
```

### 2.1 `study.yaml` (single source of truth per study; loader MUST validate fully)

```yaml
study: orb_xauusd_v1
bot:
  source: "ORB Projects/ORB Bot/ORB_Bot_V_Code_ORB_lock_fixed.cs"
  class_name: OrbBreakoutBot
market:
  symbol: XAUUSD
  period: m1                  # chart period the bot runs on (per bot README)
  data_glob: "XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv"
account:
  nominal_balance: 10000      # £; all % metrics scale to this
  currency: GBP
  risk_per_trade: 100         # fixed, NOT searchable
execution:
  spread_pips: {realistic: 2.0, stressed: 4.0}   # trader-supplied
  commission_per_lot: 0.0
  slippage_model: {dist: lognormal, median_pips: 0.5, p95_pips: 3.0}
windows:
  data_start: 2021-01-04
  holdout_start: 2025-07-01   # NOTHING after this date is touched before Stage 5
  wfa: {mode: rolling, is_months: 18, oos_months: 6, step_months: 6}
budgets:
  stage1_random: 200
  stage1_tpe: 600
  wfa_trials_per_fold: 150
  mc_resamples: 5000
gates:                        # defaults = 01-Research §5; overridable here
  min_trades_per_year: 30
  max_dd_pct: 20
  min_pf: 1.15
  wfe_min: 0.5
  dsr_min: 0.95
  pbo_max: 0.25
  plateau_retention: 0.7
```

---

## 3. `data.py` — preparation & audit

1. **Convert** repo CSVs → cTrader m1-csv format: `yyyy-MM-dd HH:mm:ss` (UTC),
   no header, columns `datetime,open,high,low,close,volume`, concatenated over the
   study window, split at `holdout_start` into `insample.csv` + `holdout.csv`.
   Output under `data/prepared/<symbol>/<sha256-12>/` with `manifest.json`
   (source files, row counts, date ranges, hash). **Stage 0 MUST verify the exact
   datetime format the CLI accepts** (docs show `DateTime.Parse` semantics); if
   ambiguous, test both `2024-01-15 09:30:00` and ISO-T variants with a 1-week
   backtest and record the answer in DECISIONS.md.
2. **Audit** (blocking unless `--allow-dirty`): duplicate/out-of-order timestamps
   (fail), OHLC violations (fail), gap report vs expected 24×5 session map for the
   symbol (warn with table), spike report `range > 12×` rolling median range (warn,
   list top 20 for eyeball), per-year bar counts. Write `audit.md` next to data.
3. Utility: derive D1/H1/M5 resamples for *analysis only* (regime classification,
   plots) — the backtester itself always gets M1.

## 4. `ctcli.py` — cTrader CLI wrapper

- One function: `run_backtest(algo, cbotset, csv, start, end, spread, balance,
  symbol, period, workdir) -> RawResult` invoking the container; capture stdout,
  exit code; locate the run's Backtesting folder; parse `Report.json` +
  `Events.json` into a **canonical result**:
  `trades[]` (open/close time, direction, entry/exit px, volume, gross/net P&L,
  pips, label/comment), `equity_curve` (timestamped; from events if present, else
  reconstructed by replaying closed trades on the nominal balance — record which),
  `summary` (as reported), `log_path`.
- Timeouts (default 30 min/run), 2 retries on infra-class failures only (docker/
  network), never on backtest errors. All raw outputs kept (gzip) under the run dir.
- **Stage 0 discovery tasks** (write findings to DECISIONS.md): exact backtest
  subcommand flags of the current image (`--report-json` availability), Events.json
  schema (field names for partial closes — Multi-TP bots close in slices; the parser
  MUST aggregate slices into logical trades *and* keep the raw slices), whether
  equity marks exist between trade closes, how `--data-mode=m1-csv` names the file
  argument.

## 5. `cbotset.py` — parameter files

1. **Schema discovery (Stage 0):** trader exports one `.cbotset` per bot from the
   cTrader GUI (ask via README instructions) *or* run `ctrader-cli metadata` on the
   `.algo` — determine JSON structure, exact parameter display-name keys, enum and
   TimeFrame value encodings. Record a golden example per bot in the study dir.
2. Generator: `make_cbotset(base: dict, overrides: dict) -> path`, validating every
   override key against bot metadata (unknown key = hard error; type coercion for
   enum/timeframe/string-time params). Deterministic serialisation → file content
   hash used as cache key component.
3. `base` comes from the bot's defaults + study `fixed:` block; overrides come from
   the optimiser trial.

### 5.2 `search_space.yaml` (per bot; written by hand, reviewed by trader)

```yaml
fixed:                        # never searched; explicit > implicit
  "Risk Amount": 100
  "Enable Margin Safety": true
  # …every param not searched is listed here or inherits bot default (listed too)
search:
  "Take Profit R":        {type: float, low: 1.0, high: 4.0, step: 0.25}
  "Stop Loss ORB Percent":{type: float, low: 25, high: 100, step: 5}
  "Confirmation TimeFrame": {type: cat, choices: [Minute, Minute5, Minute15]}
  "Enable Trend Filter":  {type: bool}
  "Trend EMA Period":     {type: int, low: 5, high: 50, condition: "Enable Trend Filter"}
constraints:
  - "TradingStart >= SessionEnd"          # engine-evaluated sanity predicates
notes: |
  Hypothesis rationale per parameter (why this range) — REQUIRED, one line each.
```

Loader MUST enforce: ≤ 10 effective search dimensions (conditionals counted when
active); every searchable param exists in bot metadata; every bot param is
accounted for (searched, fixed, or explicitly `default:`-listed).

## 6. `runner.py` — execution & cache

- Work queue with N parallel workers (default = cores/2; each worker = one container).
- **Cache**: key = SHA256(algo_hash, cbotset_hash, data_hash, start, end, spread,
  balance). Value = canonical result parquet/json. Hit → skip run. This makes every
  stage resumable and idempotent.
- Structured run log (jsonl): trial id, key, wall time, outcome. Failed backtests
  (bot exception in Log.txt) → trial marked FAILED with excerpt; never silently
  scored 0.

## 7. `metrics.py`

Implement exactly the table in `01-Research §4.3` + gates inputs: daily-return
construction (equity → calendar-day last-mark, forward-filled over flat days,
returns on nominal balance), annualised Sharpe/Sortino, PF, MaxDD (% and £, plus
peak/trough dates), Calmar, expectancy in R (R = per-trade risk = `risk_per_trade`),
SQN, Ulcer, longest-loss-streak, time-under-water, trades/year, per-slice variants
(year, weekday, session bucket, vol tercile — tercile boundaries computed on IS
only and frozen). Pure functions over the canonical trade/equity structures;
100% unit-tested against hand-computed fixtures.

## 8. `optimise.py` — Stage 1

- Optuna study (SQLite at `studies/<name>/runs/trials.db`), sampler seeded from
  study.yaml (reproducible), space built from search_space.yaml (conditionals via
  Optuna's dynamic API).
- Objective per §4.3 of research doc: constraint-violating trials get pruned state
  + recorded reason. All metrics stored as user attrs on the trial (needed later by
  PBO/DSR).
- Suspicion flags (PF>4, WR>85% & n<100) stored as attrs, surfaced in report.
- Output: `stage1_top.json` — top-K (default 20) by objective *after* a cheap
  plateau pre-screen (score each candidate by mean objective of its ≤2·dims nearest
  logged neighbours; demote isolated spikes).

## 9. `walkforward.py` — Stage 2

- Fold generation from `windows.wfa` (validate: last OOS end ≤ holdout_start; emit
  the fold table into the report).
- Per fold: fresh Optuna study (budget `wfa_trials_per_fold`, warm-started by
  seeding stage-1 top-K as enqueued trials), select by same objective on IS, then
  **one** run on OOS with the selected params.
- Aggregate: concatenated-OOS equity + metrics; WFE; per-fold table; parameter
  dispersion across folds (per-param normalised std over folds).
- Also evaluate each stage-1 top-K candidate *fixed* across all folds' OOS
  (no re-selection) — distinguishes "stable single θ" from "needs re-optimisation
  cadence"; both results go in the report, and the recommended θ\* is chosen from
  the fixed-θ table (re-optimisation cadence is an operational recommendation).

## 10. `plateau.py` — Stage 3a

Per candidate θ\*: one-at-a-time ±1 step (or ±10% for unstepped floats) on every
searchable param + 32 joint random perturbations within ±1 step box. Real backtests
(cache makes repeats free). Compute retention ratios, produce 1D response plots and
the pairwise heatmap for the two most sensitive params. Gates per research §5.2;
recommend plateau centroid (re-run centroid to confirm ≈ θ\* performance).

## 11. `montecarlo.py` — Stage 3b

On the concatenated OOS trade list (and later once on holdout): implement research
§5.3 items 1–5 exactly (block bootstrap block=20, dropout 10–20%, slippage/spread
stress from `execution.slippage_model`, same-bar-ambiguity worst-case re-score
(ambiguous = SL and TP within one M1 bar's range — detectable from the trade + bar
data), top-5-winners-removed). Deterministic seeds. Output: percentile tables +
fan charts. Data-level noise MC: stub with clear interface, marked phase-2.

## 12. `overfit.py` — Stage 4

- **DSR** per Bailey/López de Prado 2014: E[max SR of N trials] via EMC/Euler
  approximation using the trial-log's SR variance and effective N (deduplicate
  near-identical trials by cbotset hash); non-normality correction from skew +
  kurtosis of the candidate's daily returns; output probability. Unit-test against
  the worked example in the paper.
- **PBO via CSCV**: matrix M (trials × S=16 temporal blocks of the IS period,
  metric = block Sharpe); all C(16,8) splits (or 5,000 sampled if the full set is
  slow); λ-distribution and PBO. Unit-test on synthetic noise (PBO→~0.5) and
  synthetic genuine-edge (PBO→ small) datasets.

## 13. `gates.py` — verdict

Pure function: (all stage outputs, gates config) → verdict RECOMMEND / CONDITIONAL /
REJECT + per-gate pass/fail table with measured values. CONDITIONAL iff ≤2 gates in
their defined "marginal" band (each gate defines one, e.g. WFE ∈ [0.4, 0.5)).
Any hard fail → REJECT. Machine-readable `verdict.json` + human table.

**Holdout guard:** `engine holdout` refuses to run unless verdict ≥ CONDITIONAL,
`--confirm` given, and `HOLDOUT_LEDGER.md` shows zero prior holdout runs for this
study; it appends to the ledger *before* running. After Stage 5 the study is
immutable (engine refuses further optimise/validate calls for it).

## 14. `report.py`

Jinja2 → single self-contained `report.html` + `report.md` per study: study config
snapshot, data audit summary, stage-by-stage results, all gate tables, plots
(equity curves IS vs OOS vs holdout, drawdown, plateau curves, MC fans, per-regime
bars), the recommended `.cbotset` (also written as a file, named
`<bot>_<study>_RECOMMENDED.cbotset`), demo forward-run expectations (MC P5–P95
bands for 1/3/6-month windows), and an honest LIMITATIONS section auto-populated
(equity granularity mode used, spread model, any --allow-dirty data warnings).

## 15. `cli.py` — agent contract

Subcommands (all take `--config studies/<name>/study.yaml`):
`data-prepare`, `compile`, `smoke`, `optimise`, `wfa`, `validate` (plateau+mc+
overfit+gates), `holdout --confirm`, `report`, `status` (machine-readable JSON of
stage completion — agents poll this). Every command: idempotent, resumable,
exit 0 only on success, rich `--help`. A `Makefile`-style `engine all` runs
0→4 and stops before holdout by design.

## 16. Testing & acceptance

1. **Unit tests**: metrics (hand fixtures), cbotset round-trip vs golden files,
   fold generation edge cases, DSR/PBO against paper examples & synthetic data,
   gates truth table, cache key stability.
2. **Integration (needs credentials)**: 1-month smoke backtest per bot; parity —
   same params/window run twice → identical trade list (determinism); CLI vs
   trader's GUI backtest on one agreed config → trade-list match within
   documented tolerance (target: exact).
3. **End-to-end dry-run**: a toy study (3 search params, 2 WFA folds, tiny budgets)
   completing 0→report in < 1 hour on the ThreeDownDaysBot.
4. **Anti-fooling test (mandatory)**: run the full pipeline on a *known-random*
   strategy (ThreeDownDaysBot on shuffled-return synthetic data, or a coin-flip
   param set): the engine MUST output REJECT. If it recommends anything, the
   methodology implementation is broken. This is the single most important test.

## 17. Build order (milestones; commit + short status note after each)

1. **M1 — plumbing**: package skeleton, config loaders, data prepare+audit on the
   XAUUSD CSVs (runnable today, no credentials needed).
2. **M2 — execution**: compile pipeline, ctcli wrapper, Stage-0 discoveries
   (cbotset schema, Events.json schema, csv datetime format) — *blocked on trader
   credentials*; everything else proceeds with a recorded-fixture fake of ctcli.
3. **M3 — measurement**: metrics + runner + cache + smoke command; parity test.
4. **M4 — search**: optimise + walkforward on ThreeDownDaysBot×XAUUSD (small
   budgets), first real study artefacts.
5. **M5 — robustness**: plateau, montecarlo, overfit, gates, holdout guard;
   anti-fooling test passes.
6. **M6 — polish**: report dossier, agent runbook (`engine --help` + a
   `RUNBOOK.md` for agents), full-budget ORB study kicked off.

Keep every module ≤ ~400 lines; prefer boring, explicit code; docstrings state the
formula source (research-doc section) they implement. When reality contradicts this
spec (e.g. a CLI flag differs), follow reality, record it in DECISIONS.md, and
update the spec in the same commit.
