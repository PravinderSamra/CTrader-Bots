# Deep Momentum Networks

**Category:** Machine-Learning Alpha (depth entry)
**Anchor paper:** Lim, B., Zohren, S., & Roberts, S. (2019). "Enhancing Time Series Momentum
Strategies Using Deep Neural Networks." *Journal of Financial Data Science*. arXiv:1904.04912.
**Parent entries:** `../../trend-following/time-series-momentum-futures/`,
`../empirical-asset-pricing-via-machine-learning/`

---

## 1. Abstract / summary of the core edge

The TSMOM entry in this library documents a strategy with two hand-chosen components: a **trend
estimator** (the sign of the past 12-month return) and a **position sizing rule** (`40%/σ`). Both
were selected by the researcher, not learned.

This paper asks what happens if you learn both, jointly, from data — and, critically, trains the
network by **directly optimising the Sharpe ratio** rather than by minimising forecast error.

> "We introduce Deep Momentum Networks — a hybrid approach which injects deep learning based trading
> rules into the volatility scaling framework of time series momentum. The model also simultaneously
> learns both trend estimation and position sizing in a data-driven manner, with networks directly
> trained by optimising the Sharpe ratio of the signal."

Backtested on **88 continuous futures contracts**, the Sharpe-optimised LSTM reaches an out-of-sample
Sharpe of **2.907** against **1.392** for the best reference benchmark — "more than two times" — and
**2.017** for the best competing neural network, a **44%** improvement.

Three findings make this the right ML depth entry rather than another deep-learning-beats-everything
paper:

1. **The loss function matters more than the architecture.** Models trained to maximise Sharpe beat
   otherwise identical models trained on MSE or binary classification, consistently across every
   architecture class. Binary classification is catastrophic — MLP binary scores **0.108** Sharpe
   against 2.017 for the same network trained on Sharpe.
2. **More complexity is not better — again.** WaveNet, the most sophisticated architecture tested,
   **underperforms both the simple linear models and the reference benchmarks** (0.956 Sharpe versus
   1.392 for `Sgn(Returns)`). This independently corroborates Gu, Kelly & Xiu's "shallow learning
   outperforms deeper learning" finding from a completely different data set and problem setup.
3. **The edge survives realistic costs, but not generous ones.** The LSTM continues outperforming
   "when considering transaction costs up to 2-3 basis points" — a specific, falsifiable, and
   refreshingly narrow claim. The authors also propose a **turnover regularisation** term that trains
   the network to account for costs at run time.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Lim, Zohren & Roberts — arXiv:1904.04912 (verified in-session) | paper | https://arxiv.org/pdf/1904.04912 |
| arXiv abstract page | paper | https://arxiv.org/abs/1904.04912 |
| Moskowitz, Ooi & Pedersen (2012) — the strategy being enhanced | paper | https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf |
| Gu, Kelly & Xiu (2020) — the methodological sibling | paper | https://dachxiu.chicagobooth.edu/download/ML.pdf |

## 3. Method and foundation

### 3.1 The hybrid structure

The model keeps TSMOM's volatility-scaling skeleton and replaces the hand-specified parts:

```
r^{DMN}_{t,t+1}  =  z_t · ( σ_target / σ_t ) · r_{t,t+1}
```

where `z_t ∈ [−1, 1]` is the network's **directly generated position**, not a forecast that is then
converted into a position. Compare TSMOM, where `z_t = sign(r_{t−12,t})` is fixed by assumption.

Keeping the `σ_target/σ_t` volatility scaling is a deliberate design choice: it imports the part of
TSMOM that is well-motivated and learns only the part that was arbitrary.

### 3.2 The Sharpe loss function

The paper's most important idea, and the one most portable to other problems:

```
L_sharpe(θ)  =  −  E[R(θ)] / √( E[R(θ)²] − E[R(θ)]² )
```

The network is trained to maximise risk-adjusted return **directly**. This is not the same as
predicting returns well:

- An **MSE** loss spends capacity fitting the largest return moves, which are the least predictable.
- A **binary classification** loss with a 0.5 threshold gets roughly 50% accuracy and produces flat
  equity curves — the paper notes most binary models achieve "about a 50% accuracy which, while
  expected of a classifier with a 0.5 probability threshold, is far below" what is useful.
- A **Sharpe** loss optimises the thing the trader actually cares about, and implicitly learns
  position sizing along the way.

### 3.3 Architectures compared

| Class | Description |
|---|---|
| Reference benchmarks | Long-only, `Sgn(Returns)` (i.e. TSMOM), MACD (Baz et al. 2015) |
| Linear | Direct linear position model |
| MLP | Feed-forward network |
| **LSTM** | Recurrent, with an internal memory state over ~3 months of history |
| WaveNet | Dilated causal convolutions |

Each is trained under four objectives: **Sharpe**, average returns, MSE, and binary classification.
That 5 × 4 grid is what makes the loss-function finding credible — it is a controlled comparison, not
a single model demonstration.

### 3.4 Why the LSTM wins

The authors attribute the gain to "using models which capture non-linear relationships, and have
access to more time history via an internal memory state." The LSTM is unrolled over roughly three
months of daily observations, so it can condition on the *path* of returns rather than a single
summary statistic like the 12-month sign.

Their explanation for WaveNet's failure is candid and worth noting: "the difficulties in tuning
models with multiple design parameters — for instance, better results could possibly [be] achieved by
using alternative dilation rates, number of convolutional layers, and hidden state sizes… In
contrast, only a single design parameter is sufficient to specify the hidden state size in both the
MLP and LSTM models."

That is an honest statement about **tuning burden as a real cost of complexity**, not a claim that
convolutional models cannot work.

### 3.5 Turnover regularisation

To handle costs at training time rather than as an afterthought, a penalty term proportional to
turnover is added to the loss, with `c` reflecting the assumed transaction cost. The network then
learns to trade less when trading is expensive — the cost model becomes part of the objective
instead of a post-hoc haircut.

## 4. Known criticisms and limitations

1. **A 2.907 Sharpe on futures should prompt scepticism, not enthusiasm.** It is roughly double what
   the TSMOM literature reports for the same asset class and vastly above what managed-futures funds
   realise. The paper's own cost analysis shows the advantage disappearing by 5 bps, which is a
   partial answer, but the gross figure remains far above live experience.
2. **The out-of-sample protocol is walk-forward but the sample is one market regime.** 1990–2015,
   split into six 5-year blocks with expanding-window calibration. That covers two major crises but
   is a single era of monetary policy and market structure.
3. **Cost sensitivity is narrow and the paper says so.** Outperformance holds "up to 2-3 basis
   points." Many of the 88 contracts do not trade at 2–3 bps all-in, particularly in size, and the
   authors explicitly propose turnover regularisation "to account for more illiquid assets."
4. **No capacity analysis.** A high-turnover daily-rebalanced signal across 88 futures has a capacity
   limit that is never estimated.
5. **Architecture search is itself a multiple-testing exercise.** Five architectures × four loss
   functions × hyperparameters, evaluated on the same data. The best cell of a 20-cell grid is biased
   upward even under honest walk-forward, and no correction is applied.
6. **It enhances a decaying edge.** TSMOM is graded `partially-decayed` in this library. A better
   function over a weakening signal inherits the weakening — the same caveat as the parent ML entry.
