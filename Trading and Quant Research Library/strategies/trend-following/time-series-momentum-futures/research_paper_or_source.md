# Time Series Momentum (TSMOM) — Moskowitz, Ooi & Pedersen

**Category:** Trend Following & Time-Series Momentum
**Anchor paper:** Moskowitz, T. J., Ooi, Y. H., & Pedersen, L. H. (2012). "Time series momentum."
*Journal of Financial Economics*, 104(2), 228–250.

---

## 1. Abstract / summary of the core edge

An instrument's own past 12-month excess return predicts its next-month return. Not relative to
other instruments — relative to zero. Go long what has gone up over the past year, short what has
gone down, size every position to the same risk, and hold for a month.

In the authors' words:

> "We document significant 'time series momentum' in equity index, currency, commodity, and bond
> futures for each of the 58 liquid instruments we consider. We find persistence in returns for one
> to 12 months that partially reverses over longer horizons, consistent with sentiment theories of
> initial under-reaction and delayed over-reaction. A diversified portfolio of time series momentum
> strategies across all asset classes delivers substantial abnormal returns with little exposure to
> standard asset pricing factors and performs best during extreme markets."

Two facts make this the anchor entry for the whole trend-following family:

1. **Universality.** All 58 futures contracts show positive time-series momentum returns, and 52 of
   them are statistically significant at the 5% level. An effect that appears in every instrument
   across four unrelated asset classes is very hard to dismiss as data mining.
2. **The payoff is convex, not linear.** TSMOM earns its largest profits during the most extreme
   market moves — up *and* down. Regressing quarterly TSMOM returns on the market and the market
   *squared* gives an insignificant beta on the market but a significantly positive coefficient of
   **1.99 (t = 3.88)** on the squared term. The strategy behaves like a long straddle on the market.
   This is why trend following is held as a crisis diversifier rather than as a return enhancer.

This is what separates TSMOM from the more famous cross-sectional momentum of Jegadeesh & Titman
(1993). Cross-sectional momentum buys relative winners and sells relative losers, is roughly
dollar-neutral, and **crashes** in sharp reversals. Time-series momentum takes an outright
directional position per instrument, can be net long or net short the whole world at once, and is
long convexity. The two are related — TSMOM has a beta of 0.66 on cross-sectional momentum with an
R² of 44% — but they are not the same: TSMOM retains a significant **76 bp/month alpha (t = 5.90)**
after controlling for cross-sectional momentum.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Moskowitz, Ooi & Pedersen (2012), JFE — full text PDF (verified in-session) | paper | https://w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf |
| AQR summary page | article | https://www.aqr.com/Insights/Research/Journal-Article/Time-Series-Momentum |
| **AQR public dataset — the paper's own TSMOM return series** | dataset | https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Original-Paper-Data |
| SSRN version | paper | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2089463 |
| Huang, Li, Wang & Zhou — "Time-series momentum: Is it there?" (the main challenge) | paper | https://ink.library.smu.edu.sg/context/lkcsb_research/article/7520/viewcontent/Time_series_momentum_JFE_sv.pdf |
| Lim, Zohren & Roberts — "Enhancing Time Series Momentum Strategies Using Deep Neural Networks" | paper | https://arxiv.org/pdf/1904.04912 |

The AQR dataset link matters: the authors published the actual monthly return series from the
paper. Any replication can be checked against ground truth rather than argued about.

## 3. Mathematical and logical foundation

### 3.1 Ex-ante volatility estimate

Every position is sized by risk, so the volatility estimator is part of the strategy, not a
detail. MOP use an exponentially weighted estimate of annualised variance:

```
σ²_t = 261 · Σ_{i=0}^{∞} (1 − δ) · δ^i · ( r_{t−1−i} − r̄_t )²
```

where:
- `261` annualises from daily data (trading days per year),
- weights `(1 − δ)·δ^i` sum to one,
- `r̄_t` is the exponentially weighted average return computed the same way,
- `δ` is chosen so the **centre of mass** of the weights is **60 days**:
  `Σ (1 − δ)·δ^i·i = δ/(1 − δ) = 60`, giving `δ ≈ 0.9836`.

Two design choices worth copying:

- **The model is identical for all assets at all times.** No per-asset tuning, so no room to
  overfit the risk model.
- **`σ_{t−1}` is applied to time-`t` returns**, explicitly to guarantee no look-ahead bias.

The authors note results are robust to more sophisticated volatility models; simplicity was chosen
deliberately.

### 3.2 The signal and position size

For instrument `s`, the TSMOM return is:

```
r^{TSMOM,s}_{t,t+1} = sign( r^s_{t−12,t} ) · ( 40% / σ^s_t ) · r^s_{t,t+1}
```

Three components:

1. **`sign(r^s_{t−12,t})`** — the entire signal. Not the magnitude of the past return, not a moving
   average crossover, not a ranking. Just the sign of the past 12-month excess return. Long if
   positive, short if negative.
2. **`40% / σ^s_t`** — the position size, inversely proportional to ex-ante volatility, targeting
   40% annualised volatility per position. MOP state the 40% choice is "inconsequential" — it is a
   scaling constant chosen because it is similar to the risk of an average individual stock, and
   it makes the resulting factor comparable to other published factors.
3. **`r^s_{t,t+1}`** — next month's realised excess return. Holding period is one month.

### 3.3 The diversified portfolio

Equal-weight across all `S_t` instruments available at time `t`:

```
r^{TSMOM}_{t,t+1} = (1 / S_t) · Σ_{s=1}^{S_t} sign( r^s_{t−12,t} ) · ( 40% / σ^s_t ) · r^s_{t,t+1}
```

Because each position is scaled to 40% annualised volatility and the instruments are imperfectly
correlated, the diversified portfolio lands at **12% annualised volatility** over 1985–2009 —
roughly the risk level of the Fama–French factors, which is what makes the comparison meaningful.

### 3.4 Why the edge should exist

MOP's stated mechanism is **initial under-reaction followed by delayed over-reaction**: prices
adjust too slowly to new information (creating 1–12 month persistence), then overshoot (creating
the partial reversal beyond 12 months). The reversal is critical evidence — a pure risk-premium
explanation does not predict that returns should reverse at longer horizons, but a
sentiment/over-reaction story does.

The paper adds a direct test of *who is on each side*. Examining the trading activity of speculators
versus hedgers in CFTC position data, they find **speculators profit from time series momentum at
the expense of hedgers**. This is the strongest part of the paper's economic story: trend followers
are being paid to take the other side of hedgers' risk transfer, which is a sustainable structural
reason for the premium to persist rather than an anomaly awaiting arbitrage.

### 3.5 Why the payoff is convex

TSMOM tends to be positioned *with* an existing trend. When a market keeps moving in the same
direction — a crash or a melt-up — the position is already aligned and gains compound. When markets
reverse sharply, the strategy is on the wrong side but is stopped out by the monthly rebalance.
The result is the straddle-like profile Fung & Hsieh (2001) describe for trend-following hedge
funds.

The paper's own worked example is the 2008 crisis: TSMOM **lost** in Q3 2008 as trends broke, which
positioned the strategy short across many contracts, and then made large profits in October,
November and December 2008 as those markets fell further. It then suffered sharp losses in March,
April and May 2009 — because the end of a crisis is itself a sharp trend reversal.

## 4. Known criticisms and limitations

1. **The direct challenge: "Time-series momentum: Is it there?"** Huang, Li, Wang & Zhou argue that
   once the test is specified properly, the evidence for time-series momentum as a *predictive*
   effect is much weaker than MOP report, and that a large part of TSMOM's performance is
   attributable to the volatility-scaling and to the average returns of the underlying assets
   rather than to trend predictability itself. This is the single most important counterweight to
   this entry and is queued as its own Wave 6 adversarial-review entry.
2. **Volatility scaling does a lot of the work.** `40%/σ_t` is a risk-parity overlay. Part of the
   reported performance comes from that overlay rather than from the sign signal — an important
   ambiguity when attributing the edge.
3. **Reported results are gross.** Figure 2's Sharpe ratios are explicitly labelled *gross*. Futures
   are cheap to trade and monthly rebalancing is low-turnover, so the haircut is small, but net
   figures are not what the paper publishes.
4. **The 12-month/1-month combination is chosen after examining the horizon grid.** MOP show
   results across 1–48 month lookbacks and defend 12/1 from that evidence, but it remains a
   selection from a surveyed grid.
5. **Crisis-alpha depends on trends persisting long enough to be caught.** A sharp V-shaped shock
   with no persistence (a single-day crash and immediate recovery) is the worst case: the strategy
   gets whipsawed in both directions.
6. **Crowding.** Managed futures grew enormously after this literature became widely known. The
   post-publication performance of the trend-following industry (broadly weak 2011–2019, strong
   2022) is consistent with a real but capacity-constrained and regime-dependent premium.
