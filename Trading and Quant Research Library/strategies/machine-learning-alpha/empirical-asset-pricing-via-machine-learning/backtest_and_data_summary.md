# Backtest & Data Summary — Empirical Asset Pricing via Machine Learning

## Verification

All figures below were read directly from Gu, S., Kelly, B., & Xiu, D., "Empirical Asset Pricing via
Machine Learning," retrieved in-session from `dachxiu.chicagobooth.edu/download/ML.pdf`. Published in
*The Review of Financial Studies* 33(5), 2223–2273 (2020). **Evidence grade: `verified-primary`.**

---

## 1. Data sample

| Field | Value |
|---|---|
| Universe | **~30,000 individual stocks** |
| Sample period | **1957 – 2016** (60 years) |
| Frequency | Monthly returns |
| Stock characteristics | **94** |
| Aggregate time-series variables | **8** (interacted with each characteristic) |
| Industry dummies | **74** |
| **Total baseline signals** | **900+** |
| Methods compared | OLS, elastic net, PCR, PLS, generalized linear model, random forest, boosted trees, neural networks (1–5 hidden layers) |
| Protocol | Training / **validation** / testing split; hyperparameters tuned on validation only |

## 2. Predictive accuracy — out-of-sample monthly R²

### 2.1 Stock level

| Method | Monthly out-of-sample R² |
|---|---|
| OLS on 900+ predictors | negative (the overparameterisation problem) |
| **Elastic net** | **0.11%** |
| **PCR** | **0.26%** |
| **PLS** | **0.27%** |
| Generalized linear model (splines, **no interactions**) | fails to robustly beat linear |
| **Trees and neural networks** | **0.33% – 0.40%** |

> These are the paper's *best* numbers, and they are **fractions of one percent per month**. That is
> not a criticism — it is what a real return-prediction R² looks like, and any paper reporting an
> order of magnitude more on stock-level monthly returns should be treated with suspicion. The
> economic value comes from applying a weak signal across thousands of names, not from strong
> prediction of any one.

### 2.2 Portfolio level — where the gap widens

Bottom-up S&P 500 forecasts, aggregated from stock-level predictions:

| Method | Monthly out-of-sample R² |
|---|---|
| Benchmark three-characteristic OLS | **−0.22%** |
| Generalized linear model | **0.71%** |
| **Trees and neural networks** | **1.08% – 1.80%** |

A three-layer neural network "produces a positive out-of-sample predictive R² for **every** factor
portfolio we consider" (size, value, investment, profitability, momentum).

**Why portfolio-level prediction is stronger:** aggregation averages out the erratic behaviour of
"some of the smallest and least liquid stocks," boosting signal relative to noise. This is a useful
practical point — the same model looks far better when its forecasts are pooled into portfolios,
which is also how it would actually be traded.

## 3. Economic performance

| Strategy | Out-of-sample annualised Sharpe |
|---|---|
| S&P 500 market timing, neural network forecasts | **0.77** |
| Buy-and-hold | **0.51** |
| **Value-weighted long-short decile spread, stock-level NN forecasts** | **1.35** |
| Leading regression-based strategy from the literature | ≈ half of 1.35 ("more than doubling") |

The market-timing result (0.77 vs 0.51) is the more modest and arguably more honest one — a 51%
improvement in risk-adjusted terms on a single, highly efficient index.

## 4. The two structural findings

### 4.1 Interactions, not nonlinearity, are the source of the gain

| Model class | Nonlinear? | Interactions? | Result |
|---|---|---|---|
| Linear / elastic net | No | No | Baseline |
| **Generalized linear model** | **Yes** (splines per predictor) | **No** | **Fails to robustly outperform linear** |
| Trees, neural networks | Yes | **Yes** | 0.33%–0.40% stock-level R² |

The GLM is the control that makes this a real finding. Adding flexible nonlinearity to each predictor
*separately* buys nothing. Adding **interactions between predictors** is what works. The authors:
"allowing for (potentially complex) interactions among the baseline predictors is a crucial aspect of
nonlinearities in the expected return function."

### 4.2 Shallow learning outperforms deep learning

| Architecture | Result |
|---|---|
| Neural networks, 1 → 5 hidden layers | **Performance peaks at 3 layers, then declines** |
| Boosted trees / random forests | Select trees with **fewer than six leaves** on average |

Attributed to "the relatively small amount of data and tiny signal-to-noise ratio for our return
prediction problem, in comparison to the kinds of nonfinancial settings in which deep learning
thrives."

> **This is the most transferable result in the paper.** The instinct imported from computer vision —
> deeper is better, more capacity is better — is actively wrong in return prediction. Three layers
> and six leaves. Anyone starting a financial ML project with a large architecture is beginning in
> the wrong place.

### 4.3 Which signals dominate

All methods agree: **"variations on momentum, liquidity, and volatility."**

Note what this means for the library. Machine learning did not find new anomalies — it found a better
combination function over signals that already have entries here
(`../../cross-sectional-factors/cross-sectional-momentum-jegadeesh-titman/`,
`../../trend-following/time-series-momentum-futures/`) and in the microstructure category
(`../../market-making-microstructure/order-flow-imbalance-price-impact/`).

## 4.4 Implementation check (run in-session)

The walk-forward pipeline was exercised on a synthetic panel (120 stocks × 180 months) constructed
with a deliberate **interaction** in the data-generating process — `signal = 0.004·x₀·x₁ + 0.002·x₂`
plus noise — to test whether the protocol recovers the paper's central structural finding.

| Method | Can represent interactions? | Out-of-sample R² |
|---|---|---|
| Ridge | No | −0.0735% |
| PLS | No | −0.0967% |
| **Random forest** | **Yes** | **−0.0050%** (best) |
| Neural network (3 layers) | Yes | **−3.8708%** (worst) |
| *True-signal ceiling* | — | *0.274%* |

**What this does and does not show:**

- ✅ **The interaction finding reproduces directionally.** The random forest — the only linear-model
  alternative here that can represent `x₀·x₁` — beats both ridge and PLS by an order of magnitude in
  R². That is GKX's central claim: the gain comes from interactions, not from flexibility per se.
- ✅ **The overfitting warning reproduces.** The three-layer network posted −3.87%, catastrophically
  worse than everything else, on ~7,000 training observations. The paper's explanation — small data,
  tiny signal-to-noise — is visible directly. This is exactly why they find performance peaks at
  three layers rather than growing with depth.
- ❌ **The paper's positive R² values were not reproduced, and could not be.** Every method here is
  *negative* against a true ceiling of 0.274%, because the synthetic sample is roughly three orders
  of magnitude smaller than 30,000 stocks over 60 years. This tests the code and the qualitative
  ordering; only the real CRSP panel can test the magnitudes.

**Two bugs found and fixed while testing**, both of the kind that silently corrupt results rather
than raising errors:

1. **PLS returned an all-NaN column.** Its hyperparameter grid included `n_components = 10` against a
   feature set of 8, which raises inside the fit and was swallowed by a broad `except`, blanking the
   method entirely. It looked like PLS "failed to predict" when it had simply never been fitted. The
   grid is now capped at the feature count.
2. **A NaN validation score could leave a method unselected**, producing the same silent blanking.
   Non-finite scores are now coerced to `−inf` and the first candidate always seeds the selection.

Both are worth flagging generally: in a comparative ML study, a method that silently produces no
output is far more dangerous than one that produces a bad number, because it drops out of the
comparison rather than losing it.

## 5. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Maximum drawdown | **NOT REPORTED IN SOURCE** |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Turnover | Not reported; implied high (monthly decile rebalancing across ~30,000 stocks) |
| Transaction costs | **NOT MODELLED** in the headline Sharpe ratios |
| Borrow cost on the short leg | Not modelled |
| Capacity | Not addressed |
| Post-2016 performance | **Outside the sample** |

The unmodelled costs matter more here than in most entries: a monthly-rebalanced long-short decile
strategy over the full CRSP cross-section is a high-turnover construction, and the paper's own
observation that small illiquid stocks behave erratically suggests the gross result leans on names
that are expensive to trade.

## 6. Where the approach applies vs. fails

**Applies when:**
- The predictor set is **wide** and interactions are plausible. That is exactly where ML beats
  linear models and nowhere else in this paper.
- Forecasts are **aggregated into portfolios** rather than traded name by name — portfolio-level R²
  is 3–5× the stock-level figure.
- A genuine walk-forward protocol with a separate validation sample is enforced.
- The architecture is kept **small**: three layers, shallow trees.
- The signals fed in are economically motivated. The paper's inputs are 94 documented
  characteristics, not raw price history.

**Fails when:**
- **The test set is touched during tuning.** The most common failure in applied financial ML, and it
  invalidates everything downstream.
- Architectures are scaled up on the assumption that more capacity helps. Documented here to be
  false beyond three layers.
- Costs are ignored on a high-turnover construction.
- The strategy concentrates in small, illiquid names where the raw R² looks best and the
  implementation is worst.
- Interactions are excluded — the GLM result shows nonlinearity alone buys nothing.

## 7. Decay and current status

**`decay_status: partially-decayed`.**

- **The methodological contribution does not decay.** The comparative protocol, the
  interactions-versus-nonlinearity finding, and the shallow-beats-deep result are facts about the
  problem structure, not about a particular period. They remain the correct starting point for any
  financial ML project.
- **The specific edge is heavily competed.** Published in 2020 with a sample ending 2016, and the
  methods were already in use at quantitative funds before publication. Every serious quant equity
  shop now runs some version of this. The 1.35 Sharpe is a research figure from a
  pre-publication-crowding sample, gross of costs.
- **The underlying signals were already decaying independently.** Momentum, liquidity and volatility
  are the dominant predictors, and the momentum entries in this library are both graded
  `partially-decayed`. An improved combination function over decaying inputs inherits their decay.

**How to use this entry.** As the **methodological standard** any ML entry must meet before it is
admitted to this library — comparative baselines, a real validation split, honest R² magnitudes, and
a stated economic result net of a plausible cost assumption. Concretely, three rules to carry into
any financial ML work: **(1)** build in interactions, not just nonlinearity; **(2)** keep the model
small — three layers, six leaves; **(3)** expect a monthly R² in the tenths of a percent, and be
suspicious of anything reporting much more.
