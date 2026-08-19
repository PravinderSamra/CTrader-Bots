# Order Flow Imbalance & Price Impact

**Category:** Market Making & Order-Flow Microstructure (Wave 2 depth entry)
**Anchor paper:** Cont, R., Kukanov, A., & Stoikov, S. (2014). "The price impact of order book
events." *Journal of Financial Econometrics*, 12(1), 47–88. arXiv:1011.6402 (draft consulted: March
2011).

---

## 1. Abstract / summary of the core edge

Every market-making model in this library — Avellaneda–Stoikov, Guéant et al., Guilbaud–Pham —
shares one blind spot: order arrivals are exogenous and uninformative. A fill tells the model
nothing about where the price is going next. In reality it tells you a great deal, and that gap is
where market makers lose money.

This paper supplies the missing measurement. It shows that over short horizons, mid-price changes
are driven almost entirely by a **single observable variable**: the **order flow imbalance (OFI)** —
the net change in supply and demand at the best bid and ask.

The empirical result is unusually strong for microstructure work:

> "We show that, over short time intervals, price changes are mainly driven by the order flow
> imbalance… Our study reveals a linear relation between order flow imbalance and price changes,
> with a slope inversely proportional to the market depth. These results are shown to be robust to
> seasonality effects, and stable across time scales and across stocks."

**Average R² of 65%** across 50 US stocks, using a linear model with a single parameter. For
comparison, the widely used **trade imbalance** achieves only **32%**. When both are included, the
trade-imbalance t-statistic falls by a factor of four and is significant in only **31% of
subsamples**, while OFI's remains strong.

Three things make this the right companion to the market-making entries:

1. **It defines the adverse-selection signal.** If OFI predicts the next price move linearly, then a
   market maker who skews quotes against prevailing OFI is defending against exactly the flow that
   would otherwise pick them off.
2. **It treats cancellations as first-class.** The OFI variable "treats a market sell and a cancel
   buy of the same size as equivalent, since they have the same effect on the size of the bid
   queue." Trade-based measures miss cancellations entirely, and cancellations dominate modern order
   flow.
3. **It explains price impact with observables only.** The slope is inversely proportional to market
   depth — both directly measurable — rather than to unobservable quantities like information
   asymmetry or trade informativeness.

And a fourth result that is genuinely deflationary: the famous **"square-root law"** of price impact
versus trade volume is derived as a **consequence** of this linear model plus aggregation, and the
authors argue it "is not robust and is a statistical artifact due to the aggregation of data."

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Cont, Kukanov & Stoikov — arXiv:1011.6402 (verified in-session, March 2011 draft) | paper | https://arxiv.org/pdf/1011.6402 |
| arXiv abstract page | paper | https://arxiv.org/abs/1011.6402 |
| Published: *Journal of Financial Econometrics* 12(1), 47–88 | paper | https://academic.oup.com/jfec/article/12/1/47/815637 |
| Kyle (1985) — the theoretical ancestor of linear price impact (λ) | paper | https://www.jstor.org/stable/1913210 |
| Almgren & Chriss (2000) — optimal execution under linear impact | paper | https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf |

## 3. Mathematical foundation

### 3.1 Order flow imbalance

Track the best bid and ask queues. Define the contribution `e_i` of each order book event and
aggregate over an interval:

```
OFI_k  =  L_b − C_b − M_s  −  L_s + C_s + M_b
```

where, over interval `k`:
- `L_b`, `L_s` — limit orders added at the best bid / ask
- `C_b`, `C_s` — cancellations at the best bid / ask
- `M_b`, `M_s` — market buys / sells

Read plainly, OFI **increases** whenever the bid size increases, the ask size decreases, or either
quote price rises; it **decreases** on the mirror-image events.

The key modelling insight is the equivalence classes this creates. A **market sell** and a **cancel
of a bid** of the same size are treated identically, because they have the same effect on the bid
queue. Any measure built only on trades is blind to half of what moves the queue.

### 3.2 The linear price impact model

```
ΔP_k  =  α̂_i  +  β̂_i · OFI_k  +  ε_k
```

estimated separately for each half-hour subsample `i` (indexed to allow the coefficient to vary
intraday). `β̂` is the **price impact coefficient**.

The paper found **no evidence of non-linear price impact** for either OFI or trade imbalance — the
regressions contain only linear terms by design and by finding.

### 3.3 Impact is inversely proportional to depth

The paper's stylised order book model predicts, and the data confirms:

```
β  ∝  1 / D
```

where `D` is a measure of market depth (bid/ask queue sizes averaged over the interval). This is what
lets intraday seasonality in price impact and volatility be explained with **observables only**:
impact is high in the morning because depth is thin, not because information asymmetry is
mysteriously elevated.

For a market maker, this is directly actionable: **the same OFI moves the price further when the
book is thin.** Quote width should respond to depth, not just to volatility.

### 3.4 The square-root law, demoted

The empirical "square-root law" — price change scaling with the square root of traded volume — is
one of the most cited regularities in market microstructure. This paper derives it from the linear
OFI model plus a scaling argument, and then argues it is **an artefact of aggregation** rather than a
fundamental law:

> "the relation between price changes and trade volume is found to be noisy and less robust than the
> one based on order flow imbalance."

That is a substantive claim with implications for execution modelling: cost models calibrated to
square-root-of-volume may be fitting an aggregation artefact rather than the underlying mechanism.

## 4. Known criticisms and limitations

1. **One month of data.** April 2010, 50 stocks. A single calendar month is a thin sample for
   claiming stability, and the authors' robustness checks are across stocks and time scales rather
   than across long time periods. April 2010 also immediately precedes the 6 May 2010 Flash Crash —
   the sample is a normal-conditions sample by construction.
2. **Level-1 data only.** The study uses TAQ (best bid/ask) rather than full depth. The authors
   defend this explicitly as a feature — showing Level-1 data suffices — but OFI as defined captures
   only events **at the best quotes**. Queue dynamics deeper in the book are invisible.
3. **R² of 65% is contemporaneous, not predictive.** The regression explains price changes *over the
   same interval* as the OFI is measured. That is a decomposition of what moved the price, not a
   forecast of what it will do. Using OFI as a trading signal requires establishing *lead-lag*, which
   this paper does not claim.
4. **10-second intervals.** The headline results use a 10-second grid, chosen partly because
   autocorrelations "typically vanish after 10 seconds." Results at millisecond scales — where
   modern market making actually operates — are a different regime.
5. **Depth is measured crudely.** Averaging best bid/ask queue sizes ignores that "the distribution
   of depth across price levels often has humps, gaps and is itself a separate object of study."
6. **US equities only.** No evidence presented for futures, FX, or crypto, where tick size relative
   to volatility, and therefore queue behaviour, differs substantially.
