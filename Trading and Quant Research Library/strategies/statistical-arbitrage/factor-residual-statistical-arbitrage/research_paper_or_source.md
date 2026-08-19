# Factor-Residual Statistical Arbitrage (PCA & Sector-ETF)

**Category:** Statistical Arbitrage & Relative Value (Wave 2 depth entry)
**Anchor paper:** Avellaneda, M., & Lee, J.-H. (2010). "Statistical arbitrage in the US equities
market." *Quantitative Finance*, 10(7), 761–782. Working paper version dated June 15, 2009.
**Parent entry:** `../pairs-trading-distance-method/`

---

## 1. Abstract / summary of the core edge

Pairs trading asks: are these two stocks mispriced relative to each other? Factor-residual stat arb
asks the better-posed question: is this stock mispriced relative to *everything that explains its
returns*?

Rather than matching a stock to a single partner, decompose every stock's return into a systematic
part — captured by common factors — and an idiosyncratic residual. Model the residual as a
mean-reverting Ornstein–Uhlenbeck process. Trade the residual when it strays far from its
equilibrium. The result is market-neutral by construction, uses the entire cross-section rather than
a hand-picked partner, and generalises pairs trading rather than replacing it.

Avellaneda and Lee generate the factors two ways and compare them head-to-head:

1. **PCA:** eigenvectors of the correlation matrix of returns, forming "eigenportfolios."
2. **Sector ETFs:** regress each stock on the ETF for its sector.

Backtested results, **after transaction costs**, from the paper's abstract:

| Signal source | Period | Sharpe ratio |
|---|---|---|
| **PCA** | 1997–2007 | **1.44** |
| PCA | 2003–2007 | **0.90** |
| **Sector ETFs** | 1997–2007 | **1.10** |
| **ETF + volume-time** | 2003–2007 | **1.51** |

Two things stand out. First, performance degrades sharply after 2002–2003 — the paper is explicit
that results are "much stronger prior to 2003." Second, incorporating **trading volume** into the
signal (using "trading time" rather than calendar time) more than recovers the decay for ETF-based
signals, lifting the 2003–2007 Sharpe from ~0.9-level performance to **1.51**.

The paper also contains one of the better contemporaneous analyses of the **August 2007 quant
liquidity crisis**, with results consistent with Khandani & Lo's "unwinding" theory of that
drawdown.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Avellaneda & Lee — working paper, June 15 2009 (verified in-session) | paper | https://www.math.nyu.edu/~avellane/AvellanedaLeeStatArb20090616.pdf |
| Published version, *Quantitative Finance* 10(7) | paper | https://www.tandfonline.com/doi/abs/10.1080/14697680903124632 |
| Khandani & Lo — "What Happened to the Quants in August 2007?" | paper | https://www.tandfonline.com/doi/abs/10.21314/JOIS.2007.010 |
| Engle & Granger (1987) — cointegration foundation | paper | https://www.jstor.org/stable/1913236 |

## 3. Mathematical and logical foundation

### 3.1 The generalisation of pairs trading

The paper starts from the pairs relationship and generalises it. For stocks `P` and `Q`:

```
ln(P_t / P_t0) = α(t − t0) + β · ln(Q_t / Q_t0) + X_t
```

or in differential form:

```
dP_t / P_t = α dt + β · (dQ_t / Q_t) + dX_t
```

`X_t` is the residual — the part of `P`'s return not explained by `Q`. Pairs trading bets that `X_t`
mean-reverts. The generalisation replaces the single stock `Q` with a set of **risk factors**:

```
dP_i(t) / P_i(t) = α_i dt + Σ_j β_ij · F_j(t) + dX_i(t)
```

Now every stock has its own residual against a *common* factor set, and every residual is a
candidate trade. This is strictly more powerful than pairs: it uses all cross-sectional
information, the hedge is against systematic risk rather than one idiosyncratic partner, and there
is no combinatorial pair-selection step to overfit.

### 3.2 Factor construction — PCA and eigenportfolios

Compute the correlation matrix of daily returns over a **1-year (252 trading day)** window
preceding the trade date. Its eigenvectors define **eigenportfolios**: portfolios whose returns are
uncorrelated with each other by construction.

The paper notes the interpretation: the **dominant eigenvector corresponds to the "market
portfolio,"** with subsequent eigenvectors capturing sector and style structure. Retaining a modest
number of components separates genuine common structure from the noise spectrum — the eigenvalue
distribution beyond the leading components is essentially random-matrix noise.

The ETF alternative is simpler and more interpretable: associate each stock with the ETF for its
sector (the paper partitions the market into **15 sectors**) and regress on that. Unlike
eigenportfolios, sector ETFs are correlated with each other — a tradeoff of interpretability
against orthogonality.

### 3.3 The Ornstein–Uhlenbeck residual model

The residual is modelled as a mean-reverting OU process:

```
dX_i(t) = κ_i ( m_i − X_i(t) ) dt + σ_i dW_i(t)
```

with equilibrium standard deviation:

```
σ_eq,i = σ_i / √(2κ_i) = σ_i · √(τ_i / 2)          where  τ_i = 1/κ_i
```

Parameters are estimated on a **60-business-day** window (`T₁ = 60/252`). Crucially, the paper
**filters on mean-reversion speed**: only stocks with reversion times less than half the estimation
period are traded, i.e.

```
κ > 252/30 = 8.4
```

> This filter is the single most important practical improvement over the distance method. A residual
> that reverts slowly relative to the holding window will not converge before the position is closed,
> and no threshold tuning fixes that. The parent entry's §3.5 flags the same half-life issue as the
> distance method's key missing ingredient — this is what it looks like implemented.

### 3.4 The s-score and the trading rule

Normalise the residual into a dimensionless score:

```
s_i = ( X_i(t) − m_i ) / σ_eq,i
```

The s-score measures how far a stock is from its model equilibrium in standard deviations. Because
it is dimensionless, **the same thresholds apply across all stocks** — a considerable practical
advantage over per-pair calibration.

The trading rule:

```
buy to open           if  s_i < −s_bo
sell to open          if  s_i > +s_so
close short position  if  s_i < +s_bc
close long position   if  s_i > −s_sc
```

with cutoffs selected empirically by simulating 2000–2004 (ETF factors):

```
s_bo = s_so = 1.25          # open at 1.25 sigma
s_bc = 0.75                 # close shorts at 0.75
s_sc = 0.50                 # close longs at -0.50
```

The paper notes the slight asymmetry — closing shorts sooner, at 0.75 rather than 0.50, gave
better results in the 2000–2002 training period.

Opening a trade means buying one dollar of the stock and simultaneously selling `β_i` dollars of its
sector ETF (or `β_i1, β_i2, ...` dollars of each factor portfolio in the multi-factor case). The
hedge is what makes the book market-neutral.

### 3.5 Volume time

The paper's most interesting extension: replace calendar time with **trading time** by incorporating
daily volume into the signal. The intuition is that price discovery happens per unit of trading
activity, not per unit of clock time — a day with no volume contains no information. This produced
"significant improvement in performance in the case of ETF-based signals," lifting the 2003–2007 ETF
Sharpe to **1.51**.

## 4. Known criticisms and limitations

1. **Decay is documented in the paper itself.** PCA Sharpe falls from 1.44 (1997–2007) to 0.90
   (2003–2007), with ETF signals showing "a similar degradation after 2002." The authors do not hide
   this — the abstract leads with it. Whatever was available in the late 1990s was substantially
   competed away within the paper's own sample.
2. **Estimation-window sensitivity.** 60 days for the OU fit and 252 days for the correlation matrix
   are choices, and the strategy's behaviour depends on them. The paper does not present a
   sensitivity study across those windows in the sections consulted.
3. **Cutoffs are fitted on 2000–2004 and then used out of sample.** Honest practice, and disclosed —
   but 1.25/0.75/0.50 are still fitted parameters, and their stability outside the fitting window is
   the open question.
4. **The number of PCA factors is a judgement call.** Too few and sector structure leaks into the
   residual; too many and genuine idiosyncratic signal is regressed away. Random-matrix theory gives
   guidance, not an answer.
5. **August 2007 is in the sample and is the strategy's defining risk.** The paper's own analysis
   validates Khandani & Lo's unwinding theory: when many market-neutral books hold correlated
   residual positions and one large participant deleverages, the resulting forced liquidation moves
   everyone's positions against them simultaneously. Market-neutral does not mean crowding-neutral.
6. **Costs are modelled but thinly.** The 10 bp round-trip assumption (see the backtest file) is
   reasonable for large-cap US equities in that era but excludes borrow costs on the short leg,
   market impact at size, and the cost of the ETF hedge leg.
7. **Capacity.** The strategy trades a large universe frequently in modest size per name. Scaling it
   pushes into market impact quickly, and the residuals it trades are by definition small
   deviations.
