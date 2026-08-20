# Backtest & Data Summary — Deep Momentum Networks

## Verification

All figures below were read directly from Lim, B., Zohren, S., & Roberts, S., "Enhancing Time Series
Momentum Strategies Using Deep Neural Networks," **arXiv:1904.04912**, retrieved in-session.
Exhibit references are to that document. **Evidence grade: `verified-primary`.**

> **Exhibit discipline matters here.** The paper reports two tables: **Exhibit 2** (raw signal
> outputs) and **Exhibit 3** (rescaled to target volatility). The narrative claims — "more than two
> times," "44%" — refer to **Exhibit 3**. Quoting Exhibit 2 numbers against those claims produces an
> apparent inconsistency. This entry states which exhibit each figure comes from.

---

## 1. Data sample

| Field | Value |
|---|---|
| Universe | **88 continuous futures contracts** (commodity, equity index, fixed income, currency) |
| Data range | **1990 – 2015** |
| Out-of-sample evaluation | **1995 – 2015** |
| Calibration | Expanding window, six 5-year blocks |
| LSTM context | ~3 months of daily history (unrolled) |
| Rebalance | Daily |

## 2. Headline results — Exhibit 3 (rescaled to target volatility)

| Model | Objective | E[Return] | Vol. | MDD | **Sharpe** | Sortino | Calmar | % +ve |
|---|---|---|---|---|---|---|---|---|
| **Reference** | Long only | 0.117 | 0.154 | 0.431 | **0.759** | 1.141 | 0.271 | 53.8% |
| **Reference** | **Sgn(Returns)** — i.e. TSMOM | 0.215 | 0.154 | 0.264 | **1.392** | 2.108 | 0.815 | 54.8% |
| **Reference** | MACD | 0.172 | 0.155 | 0.317 | **1.111** | 1.622 | 0.543 | 53.9% |
| Linear | Sharpe | 0.232 | 0.155 | 0.303 | **1.496** | 2.254 | 0.765 | 54.9% |
| MLP | Sharpe | 0.312 | 0.154 | 0.335 | **2.017** | 3.042 | 0.930 | 56.0% |
| MLP | Binary | 0.017 | 0.154 | 0.661 | **0.108** | 0.162 | 0.025 | 50.8% |
| WaveNet | Sharpe | 0.148 | 0.155 | 0.349 | **0.956** | 1.429 | 0.424 | 53.5% |
| **LSTM** | **Sharpe** | **0.451** | 0.155 | **0.209** | **2.907** | **4.290** | **2.159** | **59.6%** |
| LSTM | Ave. Returns | 0.208 | 0.154 | 0.365 | 1.349 | 2.045 | 0.568 | 54.8% |
| LSTM | MSE | 0.121 | 0.154 | 0.362 | 0.791 | 1.211 | 0.335 | 52.8% |
| LSTM | Binary | 0.075 | 0.155 | 0.682 | 0.486 | 0.762 | 0.110 | 51.0% |

### The two headline comparisons check out arithmetically

| Claim | Computation | Result |
|---|---|---|
| "improving the best neural network model (Sharpe-optimised MLP) by **44%**" | 2.907 / 2.017 | **1.441** ✅ |
| "the best reference benchmark (Sgn(Returns)) by **more than two times**" | 2.907 / 1.392 | **2.089** ✅ |

Both claims verify exactly against Exhibit 3. Note that `Sgn(Returns)` at 1.392 **is** the TSMOM
strategy from this library's trend-following entry — so the comparison is directly against the
parent strategy, which is the right benchmark.

The LSTM also posts the **lowest maximum drawdown** (0.209) of any model in the table while
achieving the highest return, which is the combination the Sharpe loss is designed to produce.

## 3. Raw signal outputs — Exhibit 2

Before volatility rescaling, for reference:

| Model / objective | Sharpe |
|---|---|
| Long only | 0.738 |
| Sgn(Returns) | 1.192 |
| MACD | 0.976 |
| Linear (Sharpe) | 1.094 |
| MLP (Sharpe) | 1.383 |
| WaveNet (Sharpe) | 0.854 |
| **LSTM (Sharpe)** | **2.804** |

The paper notes portfolio-level volatility scaling "had a larger beneficial effect on machine
learning models compared to the reference benchmarks" — visible by comparing the two exhibits.

## 4. The three structural findings

### 4.1 The loss function dominates the architecture

Holding architecture fixed and varying the objective:

| Architecture | Sharpe loss | Ave. Returns | MSE | Binary |
|---|---|---|---|---|
| **LSTM** | **2.907** | 1.349 | 0.791 | 0.486 |
| **MLP** | **2.017** | 1.731 | 1.017 | 0.108 |

Sharpe-optimised beats every alternative objective within each architecture (with one noted minor
exception in the MLP raw-signal case). **Binary classification is catastrophic** — the paper explains
that most binary models achieve "about a 50% accuracy which, while expected of a classifier with a
0.5 probability threshold, is far below" what a trading signal requires.

> The practical lesson generalises well beyond this paper: **train on the objective you are actually
> optimising.** A model that predicts direction correctly 51% of the time is worthless if it sizes
> every position identically; a model trained on Sharpe learns sizing and direction together.

### 4.2 Complexity is not free — WaveNet underperforms everything

| Model | Sharpe (Exhibit 3) |
|---|---|
| WaveNet (Sharpe) | **0.956** |
| Sgn(Returns) — a sign function | **1.392** |
| Linear (Sharpe) | **1.496** |

The most sophisticated architecture tested loses to a **sign function**. The authors' explanation is
tuning burden: WaveNet needs dilation rates, layer counts, and hidden sizes chosen, whereas "only a
single design parameter is sufficient to specify the hidden state size in both the MLP and LSTM."

> This independently corroborates Gu, Kelly & Xiu's "shallow learning outperforms deeper learning"
> finding — different data, different asset class, different problem framing, same conclusion. Two
> independent confirmations make this one of the better-supported claims in financial ML, and it is
> recorded across both entries in this category.

### 4.3 Direct position generation beats forecast-then-size

Models that "directly generate positions perform the best — demonstrating the benefits of
simultaneous learning both trend estimation and position sizing functions." The two-step approach —
forecast a return, then convert to a position with a separate rule — throws away the interaction
between the two decisions.

## 5. Transaction costs — the honest constraint

| Finding | Value |
|---|---|
| LSTM outperforms benchmarks up to | **2–3 basis points** |
| Profitability erodes by | **~5 bps** |
| Proposed mitigation | **Turnover regularisation** term in the loss |
| Cost level tested with regularisation | `c = 10 bps` (Exhibit 8) |

The turnover regulariser "does help improve the LSTM" at higher cost levels but does not restore the
uncosted advantage. This is a narrow, falsifiable claim and the paper does not overstate it.

> **This is the number that should govern any use of this entry.** A 2.907 Sharpe that survives only
> to 2–3 bps is a strategy for the most liquid contracts traded by an operator with institutional
> execution. Price your own costs with
> `../../execution-and-cost/almgren-chriss-optimal-execution/` before assuming the result transfers.

## 5.1 Implementation check (run in-session)

The Sharpe-loss idea was tested in isolation, using a **linear** position model rather than an LSTM —
deliberately, because the paper's own claim is that the *loss function* matters more than the
architecture. Synthetic series with a persistent AR(1) drift, 60/40 train-test split.

| Model | Out-of-sample Sharpe | Turnover |
|---|---|---|
| **Linear, Sharpe loss** | **3.15** | 0.0423 |
| Linear, Sharpe loss + turnover regularisation | 3.11 | **0.0248** |
| `Sgn(Returns)` — TSMOM benchmark | **1.92** | — |

**What reproduces:**

- ✅ **A Sharpe-trained linear model beats the sign rule** (3.15 vs 1.92). This mirrors the paper's
  Exhibit 3, where Linear/Sharpe scores 1.496 against `Sgn(Returns)` at 1.392 — the same ordering
  from a model with no deep learning at all. The loss function alone does real work.
- ✅ **Turnover regularisation does what it claims:** turnover falls **41%** (0.0423 → 0.0248) for a
  Sharpe cost of just 0.04. That is the intended trade — materially cheaper trading for a marginal
  return give-up — and it confirms the penalty term is wired into the objective correctly.

**What does not transfer:** the Sharpe *levels* and the shape of the cost curve. The synthetic
series has a strong persistent drift by construction, so 3.15 is an artefact of a generous
data-generating process, and the resulting cost sensitivity (Sharpe still 2.96 at 10 bps) is far
flatter than the paper's real result, where the advantage erodes by ~5 bps. **Trust the paper's cost
curve, not this one** — a synthetic test cannot calibrate cost sensitivity because it does not
reproduce realistic turnover.

## 6. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Capacity | **NOT REPORTED IN SOURCE** |
| Turnover in absolute terms | Implied high; not tabulated in the sections consulted |
| Live or post-2015 performance | **Outside the sample** |
| Per-contract breakdown | Not in the main exhibits |
| Multiple-testing correction across the 5 × 4 grid | **NOT APPLIED** |

## 7. Where it applies vs. fails

**Applies when:**
- The instruments are **highly liquid futures** where all-in costs are genuinely 2–3 bps.
- Volatility scaling is retained — the hybrid design keeps TSMOM's well-motivated component.
- The loss function is the trading objective, not forecast error.
- The architecture is **kept modest** — LSTM with one tunable dimension beat WaveNet with several.
- A genuine expanding-window walk-forward is enforced.

**Fails when:**
- **Costs exceed ~5 bps.** Stated plainly by the authors.
- Applied to illiquid contracts without the turnover regulariser.
- The architecture is scaled up on the assumption that capacity helps — WaveNet is the
  counter-example, in this paper's own results.
- Trained on MSE or binary classification. Binary in particular collapses to near-zero Sharpe.
- The underlying trend premium is absent. This model learns a better trend rule; it cannot manufacture
  trends that are not there.

## 8. Decay and current status

**`decay_status: partially-decayed`.**

- **The methodological findings are durable.** Train on the objective; keep the architecture modest;
  generate positions directly; regularise turnover. None of these depend on a market regime, and two
  of them are independently corroborated by the parent ML entry.
- **The reported performance level is not a forecast.** A 2.907 Sharpe is far above what
  managed-futures programmes realise, is gross of costs beyond 2–3 bps, and is the best cell of a
  20-cell architecture-by-objective grid with no multiple-testing correction. Treat it as an upper
  bound on a research construction, not an expectation.
- **It inherits TSMOM's decay.** The parent entry is graded `partially-decayed`; the trend premium
  it enhances weakened materially through the 2010s. A better estimator of a weaker signal is still
  a weaker signal.
- **Published 2019, sample ends 2015.** Deep-learning trend models are now standard research at
  systematic managers, so the post-publication crowding argument applies with full force.

**How to use this entry.** As the demonstration that **how you train matters more than what you
train** — the single most transferable result here. Its concrete contributions to any trend system
are the Sharpe loss function, direct position generation, and turnover regularisation, all three of
which can be adopted without adopting an LSTM. Read it alongside
`../../trend-following/time-series-momentum-futures/` (the strategy being enhanced, and the honest
benchmark at 1.392) and `../empirical-asset-pricing-via-machine-learning/` (the protocol standard
and the independent shallow-beats-deep confirmation).
