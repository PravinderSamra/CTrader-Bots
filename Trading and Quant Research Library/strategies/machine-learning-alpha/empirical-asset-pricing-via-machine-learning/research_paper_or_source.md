# Empirical Asset Pricing via Machine Learning

**Category:** Machine-Learning Alpha — *the first entry in this category*
**Anchor paper:** Gu, S., Kelly, B., & Xiu, D. (2020). "Empirical Asset Pricing via Machine
Learning." *The Review of Financial Studies*, 33(5), 2223–2273.

---

## 1. Why this is the category anchor

The machine-learning-in-finance literature is mostly noise: papers reporting spectacular Sharpe
ratios on short samples with no walk-forward discipline, no baseline comparison, and no accounting
for the multiple-testing problem. The library's ingestion standard exists partly to keep that
material out.

This paper is the counter-example, and it earns the anchor position for a specific reason: **it is
a comparative study with a protocol, not a demonstration of one model.** It runs the whole toolkit —
OLS, elastic net, PCR, PLS, generalized linear models, random forests, boosted trees, and neural
networks from one to five layers — on the same data, with the same out-of-sample discipline, against
the same benchmarks. That design is what makes its conclusions credible and what any subsequent ML
entry in this library will be measured against.

The headline economic results:

| Strategy | Out-of-sample annualised Sharpe |
|---|---|
| S&P 500 **market timing** with neural network forecasts | **0.77** |
| Buy-and-hold benchmark | **0.51** |
| **Stock-level value-weighted long-short decile spread**, neural network forecasts | **1.35** |
| Leading regression-based strategy from the literature | roughly half of 1.35 |

And the three findings that matter more than the Sharpe ratios:

1. **Interactions are the whole story.** Trees and neural networks improve prediction; the
   generalized linear model — which adds nonlinearity through splines of each predictor *individually
   but with no interactions* — "fails to robustly outperform the linear specification." The gain does
   not come from nonlinearity per se. It comes from **predictor interactions**.
2. **Shallow learning beats deep learning.** Neural network performance "peaks at three hidden layers
   then declines as more layers are added," and tree methods select trees with fewer than six leaves
   on average. The authors attribute this to "the relatively small amount of data and tiny
   signal-to-noise ratio for our return prediction problem." This is the single most useful practical
   finding in the paper and directly contradicts the instinct imported from computer vision.
3. **All methods agree on which signals matter** — "variations on momentum, liquidity, and
   volatility." Machine learning did not discover new anomalies. It found better ways to combine the
   ones already documented, several of which have their own entries in this library.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Gu, Kelly & Xiu (2020) — full text (verified in-session) | paper | https://dachxiu.chicagobooth.edu/download/ML.pdf |
| Published RFS version | paper | https://academic.oup.com/rfs/article-abstract/33/5/2223/5758276 |
| Lim, Zohren & Roberts — Deep Momentum Networks (the sibling entry) | paper | https://arxiv.org/pdf/1904.04912 |
| Harvey, Liu & Zhu — "…and the Cross-Section of Expected Returns" (the multiple-testing critique) | paper | https://faculty.fuqua.duke.edu/~charvey/Research/Published_Papers/P118_and_the_cross.pdf |

## 3. Method and foundation

### 3.1 The problem statement

Measuring the risk premium is framed as a prediction problem:

```
r_{i,t+1} = E_t[ r_{i,t+1} ] + ε_{i,t+1}
E_t[ r_{i,t+1} ] = g*( z_{i,t} )
```

where `z_{i,t}` is a large predictor vector and `g*(·)` is an unknown, possibly nonlinear function
with interactions. Every method in the study is a different way of approximating `g*`.

This framing matters: it makes the ML question **"what functional form does the conditional
expectation take?"** rather than "can a black box beat the market?" The former is answerable and
falsifiable.

### 3.2 The predictor set

| Component | Count |
|---|---|
| Stock characteristics | **94** |
| Interactions of each characteristic with aggregate time-series variables | 94 × **8** |
| Industry sector dummies | **74** |
| **Total baseline signals** | **900+** |

Some methods expand this further with nonlinear transformations and interactions of the baseline
signals. This is a genuinely high-dimensional problem, and the paper's point is that
high-dimensionality is manageable *provided overparameterisation is controlled* — "the
high-dimensional predictor set in a simple linear specification is at least competitive with the
status quo low-dimensional model, as long as overparameterization can be controlled."

### 3.3 Out-of-sample discipline

The protocol is the part worth copying. Data are divided into training, validation, and testing
subsamples, with the **validation** sample used for hyperparameter tuning and the **testing** sample
never touched during model selection. Models are re-estimated as the window rolls forward.

This is what separates the paper from most ML-in-finance work: **the reported out-of-sample R² is
genuinely out-of-sample**, including the hyperparameter choices. A model tuned on the test set is
not out-of-sample no matter how the results are labelled.

### 3.4 Why shallow beats deep here

The explanation the authors give is the correct one and generalises to almost all financial ML:

> "This is likely an artifact of the relatively small amount of data and tiny signal-to-noise ratio
> for our return prediction problem, in comparison to the kinds of nonfinancial settings in which
> deep learning thrives thanks to astronomical data sets and strong signals (such as computer
> vision)."

Monthly returns for 30,000 stocks over 60 years is roughly 3–4 million observations with an R² of
well under 1%. Image recognition has billions of observations and near-deterministic labels. The
architectures that work in one setting have no reason to work in the other, and empirically they do
not.

## 4. Known criticisms and limitations

1. **The economic magnitudes rest on small R² values.** Stock-level monthly out-of-sample R² of
   0.33%–0.40% is the paper's *best* result. That is a genuine improvement over the alternatives, and
   it is still a very weak signal. The Sharpe ratios come from applying that weak signal across
   thousands of stocks, which requires the diversification to actually work.
2. **Costs are not the focus.** A value-weighted long-short decile strategy rebalanced monthly across
   the CRSP universe has real turnover, and the short leg carries borrow costs. The 1.35 Sharpe is
   before those. Price it with `../../execution-and-cost/almgren-chriss-optimal-execution/`.
3. **Small and illiquid stocks contribute disproportionately.** The paper itself notes that
   "individual stock returns behave erratically for some of the smallest and least liquid stocks in
   our sample" — which is why portfolio-level predictions are stronger than stock-level ones. Any
   implementation must check how much of the result survives a liquidity screen.
4. **Multiple testing across the whole enterprise.** The paper is careful within itself, but it sits
   in a literature that has tested thousands of predictors. Harvey, Liu & Zhu's critique applies to
   the 94 characteristics being fed in, not to the ML methods applied on top of them.
5. **Sample ends in 2016.** Post-publication performance of these methods, now widely known and
   implemented, is the open question. The paper cannot answer it.
6. **"All methods agree on the same dominant signals" cuts both ways.** It is reassuring for
   robustness and deflationary for novelty: momentum, liquidity and volatility already had large
   literatures. What ML adds is a better combination function, not new information.
