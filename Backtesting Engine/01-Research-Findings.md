# Phase 1 — Research & Investigation Findings

**Author:** Fable 5 (research phase) · **Date:** 2026-07-25
**Purpose:** Establish the best approach for a backtesting + optimisation engine for the
cTrader cBots in this repo, with anti-curve-fitting as the central design constraint.
The companion document `02-Build-Specification.md` turns these findings into explicit
build instructions.

---

## 1. The problem we are actually solving

Backtesting a strategy is easy. The hard problem is **selection bias under multiple
testing**: when you try N parameter combinations and pick the best, the winner's
backtest performance is *biased upward by construction*, even if the strategy has zero
real edge. With the ORB bot exposing 60+ parameters, an exhaustive grid could easily
exceed 10⁹ combinations — at that scale you are guaranteed to find spectacular
in-sample equity curves that are pure noise.

Every design decision below follows from four principles:

1. **Fidelity** — the simulation must execute the strategy exactly as live cTrader
   would, or results are meaningless regardless of statistics.
2. **Honest accounting of the search** — every trial ever run must be logged, because
   the overfitting statistics (DSR, PBO) depend on *how many things you tried*, not
   just on the winner.
3. **Out-of-sample discipline** — data that influenced any selection decision is
   burned; final judgement uses data nothing was fitted on.
4. **Prefer stability over peaks** — a parameter set whose neighbours also perform
   well beats a sharp isolated optimum, because live conditions are a "neighbour" of
   the backtest, never the backtest itself.

---

## 2. Execution engine: how to actually run the bots

This is the most consequential decision. Three options were investigated.

### Option A — Re-implement each strategy in Python (vectorbt / backtesting.py / custom)

- ✅ Fastest iteration (vectorised runs in milliseconds → millions of trials).
- ❌ **Implementation drift is near-certain.** The ORB bot is ~3,500 lines with
  subtle behaviours: session timezone handling with DST, ORB lock/self-heal/backfill,
  post-lock confirm replay, catch-up entries, multi-TP partial closes with volume
  normalisation, margin safety, spread filters, restart rehydration. A Python port
  *will* diverge, and we would be optimising a different strategy than the one traded.
- ❌ Every bot change requires re-porting. Every new bot requires a new port.

### Option B — Custom C# harness (mock the cAlgo API, host the real .cs files)

- ✅ Runs the actual bot source; good fidelity in principle.
- ❌ The cAlgo API surface actually used by the three bots is large (verified by
  static scan: `Bars`/multi-timeframe `MarketData.GetBars`, `Symbol` metadata and
  volume normalisation, `Positions`/partial close semantics, `History`, `Timer`,
  `Server.Time`, indicators: SMA/ATR/EMA/Ichimoku/RSI, margin model). Re-creating
  cTrader's exact fill, margin, and volume-rounding semantics is months of work and
  becomes the thing that needs validating.

### Option C — Official cTrader CLI backtester, orchestrated from Python  ← **CHOSEN**

Spotware ships a CLI (`ctrader-cli`, cTrader ≥ 4.8) that runs **headless backtests of
compiled cBots**, and provides an official **Linux Docker image**
(`ghcr.io/spotware/ctrader-console`). Verified capabilities:

- `ctrader-cli backtest <bot.algo> [<params.cbotset>] --start=… --end=… --symbol=…
  --period=… --balance=… --spread=… --data-mode=…`
- **`.cbotset` parameter files** — machine-generatable JSON; this is how the optimiser
  injects each trial's parameters without touching source.
- **`--data-mode=m1-csv`** — backtest on a user-supplied 1-minute CSV
  (`datetime,open,high,low,close,volume`) — i.e. exactly the data already in this
  repo, so results are reproducible and broker-server independent.
- Machine-readable output per run: `Report.json` (summary), `Events.json`
  (trade-by-trade), plus `Log.txt` and `Report.html`.
- Requires a cTID login + account id even for backtests (symbol metadata) → the
  trader must supply demo credentials as secrets.
- Bots must target .NET 6+ (all repo bots use the modern API; compilation via the
  `cTrader.Automate` NuGet package with the standard .NET SDK produces the `.algo`).

Why this wins: **zero strategy re-implementation, zero drift** — the engine that
backtests is the engine that trades. The trade-off is speed (each run is a real
event-driven simulation over ~5 years of M1 data, i.e. seconds-to-minutes rather than
milliseconds). That trade-off is acceptable because the anti-overfitting methodology
*deliberately caps the number of trials* (§4) — we don't want millions of trials, and
Bayesian search makes a few thousand trials sufficient.

Mitigations for throughput, specified in the build doc: parallel CLI workers (one
container per core), result caching keyed on (algo hash, cbotset hash, data hash,
window), and coarse-to-fine staging.

**Fallbacks** (documented in case CLI licensing/credential/throughput problems arise):
B (shim) as fidelity-preserving fallback, A (Python port with mandatory parity tests
against CLI runs) only as a screening pre-filter, never as the source of truth.

Sources: [cTrader CLI docs](https://help.ctrader.com/ctrader-algo/documentation/ctrader-cli/),
[CLI backtesting for agents](https://help.ctrader.com/ctrader-ai-agent-connect/cli/backtesting/),
[custom data sources guide](https://help.ctrader.com/ctrader-algo/guides/backtesting-custom-data-sources/),
[cTrader.Automate NuGet](https://www.nuget.org/packages/cTrader.Automate/),
[GUI backtest reference](https://help.ctrader.com/ctrader-algo/documentation/cbots/backtest-a-cbot/).

---

## 3. Data: what we have, what it limits, what to add

### 3.1 Current data

`XAUUSD historical Pricing data/data/` — M1 OHLCV 2021→mid-2026, UTC, bar-open
timestamps, tick-count volume. Format already matches what `m1-csv` mode needs
(a trivial converter handles the ISO `T…Z` → `yyyy-MM-dd HH:mm:ss` datetime reshape
and header removal).

### 3.2 The M1 limitation (important, be honest about it)

With M1 bars the intra-bar price *path* is unknown. cTrader synthesises ticks from
bars deterministically; when both SL and TP fall inside one bar the fill order is a
guess. Consequences and mitigations:

- Strategies whose edge lives at sub-minute granularity can't be validated on M1.
  **None of the current bots need that** — they operate on M1/M5/M15/H1/D1 bars with
  R-multiple stops that are typically much larger than a single M1 bar's range. Fine.
- Same-bar SL+TP ambiguity is stress-tested in Monte Carlo (§5.3): re-score the trade
  list with all ambiguous trades forced to their **worst-case** outcome; the
  parameter set must survive.
- Tick-volume ≠ real volume. It is a decent *activity proxy* for gold CFDs and is
  what the bots would see live on cTrader anyway, so it is consistent.
- If a future strategy needs true tick data, the CLI also supports server tick modes;
  that path costs broker-server dependence and much slower runs. Out of scope now.

### 3.3 Execution-cost modelling

The single most common way backtests lie is free execution. Every run must charge:

- **Spread** — CLI `--spread` in pips. Two profiles per symbol: *realistic* (median
  live spread, from the trader) and *stressed* (≥1.5–2×, plus news-time widening in
  MC). No zero-spread runs, ever, except in engine-debug mode.
- **Commission** — per broker profile; applied in post-processing if the CLI profile
  can't express the broker's schedule exactly.
- **Slippage** — not modelled by bar backtests; injected in Monte Carlo
  (per-trade adverse fill perturbation drawn from a configurable distribution,
  calibrated to the trader's live fill journal when available).

### 3.4 Data hygiene checks (pre-flight, automated)

Gap scan (missing minutes vs expected session calendar), duplicate timestamps,
OHLC sanity (H≥max(O,C), L≤min(O,C)), spike detection (bar range > k·ATR flagged for
review), weekend/holiday map, DST audit of session-time bots (the ORB bot's session
logic is timezone-aware — backtests must reproduce London/NY DST shifts correctly;
data is UTC so this is the bot's job, but the engine verifies trades cluster at the
intended local times).

---

## 4. Optimisation strategy: search without self-deception

### 4.1 Parameter-space discipline comes before any algorithm

The ORB bot has 60+ parameters. Most must **not** be optimised:

- **Fixed/structural** — safety rails (margin safety, spread caps, min risk pips),
  logging, risk amount (fix at nominal, e.g. £100/trade — sizing is a *policy*
  decision, and fixed-risk makes per-trade R-multiples comparable across trials),
  self-heal/backfill toggles (operational, not strategy).
- **Searchable** — the ≤ 8–10 parameters that define the *edge hypothesis*: range
  window times, breakout confirmation (TF, bars, cross type), entry offset, SL % of
  range, TP R, trend-filter settings, trades/day, day-of-week only as *analysis*
  (see below).
- **Conditional** — only searched when their parent toggle is on (Optuna handles
  conditional spaces natively; grid search would explode).

Each bot gets a hand-written `search_space.yaml` (bot author + trader review it):
this is a *hypothesis document*, not a dump of every `[Parameter]`. Rule of thumb
enforced by the engine: **effective dimensions ≤ 10 per study**; more dimensions →
split into staged studies (entry logic first; exit/management second with entry
frozen to the plateau region).

Day-of-week and similar binary include/exclude filters are a notorious overfitting
vector (they're 2⁷ free bits that can only remove losing days in hindsight). Policy:
never optimised; instead reported as a *diagnostic* (per-day P&L with confidence
intervals), and only acted on with an economic rationale the trader signs off.

### 4.2 Search algorithm

- **Optuna** (TPE sampler) as the primary engine: handles conditional/mixed spaces,
  supports multi-objective, resumable storage (SQLite), parallel workers, and — key —
  a **complete log of every trial** for the DSR/PBO computations.
- Grid search only for ≤3-dimensional final refinement around a plateau (it gives
  the dense neighbourhood map needed for plateau visualisation).
- Random search baseline in Stage 1 (cheap, unbiased coverage; also the reference
  distribution PBO needs).
- Trial budgets are configured, not open-ended — typical: 200 random + 600 TPE per
  study. The budget is recorded because DSR *deflates by it*.

### 4.3 Objective function

Never raw net profit. Default single-objective scalar (explicit formula in the build
spec):

```
score = Sharpe_daily(annualised)            # primary
subject to hard constraints (trial rejected → score = -inf):
  trades_per_year   ≥ min_trades  (default 30/yr for day-trading bots)
  max_drawdown      ≤ dd_cap      (trader-set, e.g. 20% of nominal account)
  profit_factor     ≥ 1.15
```

plus a **suspicion filter**, not a target: PF > 4 or win-rate > 85% with < 100 trades
is flagged for manual review, because on M1 data that pattern is usually a
fill-assumption artefact, not an edge.

Optionally (per study) Optuna multi-objective mode `maximise (Sharpe, −MaxDD, PF)`
with final pick from the Pareto front by *robustness score* (§5.5) — recommended for
final refinement stages.

Metric definitions (exact, so every module agrees):

| Metric | Definition |
|---|---|
| Daily returns | Mark-to-market equity (from Events.json) resampled to trading days, simple returns on nominal account size |
| Sharpe (ann.) | mean(d)/std(d)·√252, rf=0 |
| Sortino (ann.) | mean(d)/downside-std(d)·√252 |
| Profit factor | Σwins/│Σlosses│ on closed trades |
| Max drawdown | peak-to-trough on the equity curve, % of nominal account and in £ |
| Calmar | CAGR/MaxDD |
| Expectancy | mean R-multiple per trade (fixed-risk sizing makes this clean) |
| SQN | √n·mean(R)/std(R) (Van Tharp), reported not optimised |
| Ulcer index / recovery time | reported for drawdown character |

### 4.4 Staged pipeline (coarse → fine → validate)

1. **Stage 0 — parity & smoke**: one manual cTrader GUI backtest vs one CLI run,
   same bot/params/data/window → trade lists must match. Establishes engine trust.
   Repeated whenever cTrader or a bot version changes.
2. **Stage 1 — coarse search** on the in-sample region only (holdout already
   fenced off): random + TPE, full constraint set, log everything.
3. **Stage 2 — walk-forward analysis** (§5.1) on the top-K stable candidates
   (K ≈ 10–20 chosen by plateau pre-screen, not just rank).
4. **Stage 3 — robustness battery** (§5.2–5.4) on WFA survivors.
5. **Stage 4 — overfit statistics** (§5.5): DSR + PBO gates using the full trial log.
6. **Stage 5 — holdout**: single run on the untouched final segment. Pass → ship
   `.cbotset` + report; fail → REJECT (and the holdout is now burned — record that).
7. **Stage 6 (recommended, outside the engine): 4–8 weeks demo forward-run** before
   live capital; the engine's report states the expected metric ranges the demo
   should fall inside (from MC bands), so the demo has objective pass/fail criteria.

---

## 5. Anti-overfitting methodology (the core of the engine)

### 5.1 Walk-forward analysis (WFA)

- **Rolling** (not anchored) windows by default — matches the "recent regime matters"
  reality of day-trading strategies. Anchored mode available as a config flag.
- Default geometry for ~5.5y of data with ~12–18m reserved holdout:
  IS = 18 months, OOS = 6 months, step = 6 months → 5–6 folds over 2021–2025-H1,
  holdout = 2025-H2 → mid-2026. (Exact dates in build spec; configurable.)
- In each fold: re-run the (budgeted) search on IS only, apply the selected
  parameters to OOS unseen. Concatenate OOS segments → the **honest equity curve**;
  all headline metrics come from this curve, never from in-sample.
- **Walk-forward efficiency** WFE = annualised OOS performance / annualised IS
  performance of the selected params. Gate: WFE ≥ 0.5 *and* every individual OOS fold
  profitable-or-flat (no single fold contributing >60% of total OOS profit).
- **Parameter-stability-across-folds check**: if the per-fold selected parameters
  jump chaotically across the space, the "edge" is fitting noise even when OOS P&L
  looks fine. Metric: normalised dispersion of selected params across folds; gate
  is a warning (requires trader review), not auto-fail — some drift is legitimate
  regime adaptation.

### 5.2 Parameter plateau / neighbourhood analysis

For the candidate parameter set θ\*: evaluate the full backtest at every neighbour
(each searchable param stepped ±1 grid step / ±10%, one-at-a-time, plus a small
random cloud of joint perturbations). Gates:

- median(neighbour Sharpe) ≥ 0.7 × Sharpe(θ\*)
- no neighbour catastrophic (e.g. neighbour MaxDD ≤ 1.5× candidate MaxDD)
- final recommendation = **plateau centroid**, not the peak.

This is the single most effective practical defence against curve-fitting for small
parameter counts, and it produces an intuitive artefact for the trader: 1D response
curves and 2D heatmaps per parameter pair.

### 5.3 Monte Carlo battery

All MC variants run on the OOS/WFA trade list (n ≥ a few hundred trades ideally),
5,000+ resamples each:

1. **Block bootstrap of trade sequence** (block length ~20 trades to preserve
   streaky autocorrelation): distribution of terminal P&L, MaxDD, longest losing
   streak, time-under-water. Gates: P5(terminal P&L) > 0; P95(MaxDD) ≤ trader's cap;
   risk-of-ruin (hitting −X% of account) < 1%.
2. **Trade dropout**: randomly delete 10–20% of trades (models missed fills, VPS
   outages, illness). Gate: P5 remains profitable.
3. **Execution stress**: perturb every fill by adverse slippage drawn from the
   broker profile ×2, widen spread cost per trade; re-score. Gate: still PF ≥ 1.1.
4. **Same-bar ambiguity worst-case** (§3.2): all ambiguous SL/TP trades → loss.
5. **Concentration test** (not strictly MC): remove the top 5 winning trades —
   strategy must remain profitable. Day-trading edges that live in 3 lucky trades
   are not edges.
6. *(Optional, phase 2)* **Data-level noise injection**: re-run actual backtests on
   price series perturbed within bar-noise bounds (permuted residuals). Costly
   (real CLI runs) but the strongest test; reserved for the final candidate only,
   ~20–50 runs.

### 5.4 Regime robustness

Slice the OOS trade list by: calendar year, volatility tercile (daily ATR of the
underlying), trend/range classification (e.g. ADX or efficiency-ratio terciles), and
session (Asia/London/NY). Gates: no slice with catastrophic loss (< −1.5× its share
of expected profit); the strategy's *worst regime is known and documented* in the
report so the trader can recognise it live. For gold specifically the 2021–2026 span
conveniently contains: range (2021–22), the 2023–24 breakout trend, and the 2025–26
high-volatility regime — the report labels folds with these eras.

### 5.5 Overfit statistics: DSR and PBO

Using the **complete trial log** (why every trial is recorded):

- **Deflated Sharpe Ratio** (Bailey & López de Prado): probability that the
  candidate's Sharpe exceeds the expected-maximum Sharpe of N independent noise
  trials, correcting for non-normal returns (skew, kurtosis) and track length.
  Gate: DSR ≥ 0.95.
- **Probability of Backtest Overfitting** (PBO, via CSCV — combinatorially
  symmetric cross-validation over the trial-performance matrix, S=16 blocks):
  fraction of combinations where the in-sample-best ranks below median
  out-of-sample. Gate: PBO ≤ 0.25.
- Both are *statistics with assumptions*, treated as gates plus context in the
  report, not as oracles.

References: Bailey & López de Prado, *The Deflated Sharpe Ratio* (J. Portfolio
Mgmt 2014); Bailey, Borwein, López de Prado, Zhu, *The Probability of Backtest
Overfitting* (J. Computational Finance 2016); López de Prado, *Advances in
Financial Machine Learning* (Wiley 2018) — purged CV/CPCV chapters; Pardo,
*The Evaluation and Optimization of Trading Strategies* (2nd ed.) — the WFA
canon; White, *A Reality Check for Data Snooping* (Econometrica 2000).

### 5.6 Honest failure as an output

The engine's report has three verdicts: **RECOMMEND** (all gates passed, ship
`.cbotset`), **CONDITIONAL** (specific gates marginal — listed — trader decides),
**REJECT** (with the failing evidence). An agent operating the engine is explicitly
forbidden (in its runbook) from re-running the holdout with new candidates in the
same study — a failed holdout means back to strategy design, and the study is closed.

---

## 6. How an AI agent operates this (workflow sketch)

Everything is a CLI + config-file contract (no notebooks, no GUI), so any model can
drive it:

```bash
engine data prepare  --config studies/orb_xauusd/study.yaml   # convert+audit CSVs
engine compile       --bot "ORB Projects/ORB Bot/…​.cs"        # → .algo (Docker dotnet build)
engine smoke         --config …                                # Stage 0 parity
engine optimise      --config …                                # Stages 1–2 (resumable)
engine validate      --config …                                # Stages 3–4
engine holdout       --config … --confirm                      # Stage 5 (one-shot, guarded)
engine report        --config …                                # Markdown+HTML dossier
```

`study.yaml` pins everything (bot hash, data hash, windows, budgets, gates, broker
profile) so every study is reproducible and auditable. All trials land in SQLite;
all artefacts (cbotsets, trade lists, reports) land under `studies/<name>/runs/` —
committable to the repo.

---

## 7. Honest limitations & open questions

1. **CLI credential requirement** — backtest needs a cTID login even in m1-csv mode.
   Needs the trader's demo credentials as secrets. If Spotware rate-limits or the
   Docker image misbehaves under heavy parallelism, fall back to fewer workers;
   worst case, Option B (shim) is the contingency.
2. **Throughput ceiling** — a 5-year M1 event-driven run per trial means thousands,
   not millions, of trials. The methodology is built around that budget; if a future
   strategy needs huge searches, add the Python-screen + CLI-confirm hybrid (with
   parity tests) as a pre-filter.
3. **Equity granularity in Report/Events JSON** — mark-to-market daily equity should
   be derivable from Events.json; if it turns out to be closed-trade-only, daily
   returns will be computed from closed-trade P&L (slightly flatters Sharpe during
   long holds; the current bots are intraday-to-few-days so impact is small). To be
   confirmed in Stage 0 of the build.
4. **cbotset schema** — JSON, but the exact field naming for every parameter type
   (enums, TimeFrame strings) must be reverse-engineered in Stage 0 by exporting one
   from cTrader GUI and diffing. Build spec includes this as an explicit task.
5. **Spread realism for XAUUSD** — fixed-pip spread is a simplification; gold spreads
   breathe with volatility. Mitigated by the stressed profile + MC; a
   time-of-day-aware spread model is a phase-2 nicety.
6. **Survivorship of the holdout** — once looked at, it's gone. The engine enforces
   single use per study; genuinely fresh validation thereafter only comes from
   forward demo running (Stage 6) and, over time, newly accumulated data.
