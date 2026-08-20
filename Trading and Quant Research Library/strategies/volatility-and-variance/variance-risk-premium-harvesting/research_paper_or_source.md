# Variance Risk Premium Harvesting

**Category:** Volatility & Variance Risk Premium
**Anchor paper:** Carr, P., & Wu, L. (2009). "Variance Risk Premiums." *The Review of Financial
Studies*, 22(3), 1311–1341. DOI: 10.1093/rfs/hhn038

> **Version note.** The publicly available full text used for this entry is the **May 27, 2004
> working-paper draft** ("Variance Risk Premia," filename `VarianceSwap15.tex`), hosted at NYU. The
> final RFS 2009 article is paywalled. Figures below are cited from the working paper and may differ
> in detail from the published version. Recorded honestly as such; see the Verification block in
> `backtest_and_data_summary.md`.

---

## 1. Abstract / summary of the core edge

Options are, on average, expensive. Not "sometimes mispriced" — systematically and persistently
priced above what subsequent realised volatility justifies. Whoever sells that insurance collects a
premium; whoever buys it pays one.

Carr and Wu make this precise and, crucially, **model-free**. Rather than arguing about whether
Black–Scholes implied volatility exceeds realised volatility (a comparison contaminated by the
model used to invert the option price), they show the risk-neutral expected variance — the
**variance swap rate** — can be synthesised directly from a portfolio of options with no model
assumptions beyond the absence of arbitrage. The variance risk premium is then simply:

```
RP  = RV(t,T) − SW(t,T)          the P&L of being LONG variance
LRP = ln( RV(t,T) / SW(t,T) )    the continuously compounded excess return of that position
```

Their finding, in the paper's own words: the mean log variance risk premium is **"over −50 percent
per month for the two S&P 500 indexes and for Dow Jones."** Buying variance loses roughly half its
value per month on the major US indices. Selling it earns that.

Two results give this entry its structure and its warnings:

1. **The premium is a market-level phenomenon, not a stock-level one.** Log variance risk premia are
   significantly negative for all stock indices but for only **21 of 35 individual stocks**, and the
   raw premium `RP` is insignificant for **all but three of the 35**. Carr and Wu conclude the market
   "does not price all return variance variation in each single stock, but only prices the variance
   risk in the stock market portfolio." A regression of each stock's premium on its **variance beta**
   confirms it: `LRP_j = 0.0201 + 0.2675·β^V_j`, R² = 15.9%.
2. **It is not compensation for standard risk.** Neither CAPM nor the Fama–French factors account
   for the strongly negative premia. The negative correlation between index returns and index
   volatility (the leverage effect) makes long variance *qualitatively* attractive as insurance —
   but it does not *quantitatively* explain a premium this large.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Carr & Wu, "Variance Risk Premia" — 2004 working paper (verified in-session) | paper | https://engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf |
| Published RFS version (paywalled) | paper | https://academic.oup.com/rfs/article-abstract/22/3/1311/1581057 |
| SSRN record | paper | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=1359527 |
| CBOE VIX White Paper — the same replication logic, productised | article | https://cdn.cboe.com/api/global/us_indices/governance/VIX_Methodology.pdf |
| Bakshi & Kapadia (2003) — delta-hedged gains, the complementary approach | paper | https://academic.oup.com/rfs/article/16/2/527/1581543 |
| Jacquier & Slaoui — *Variance dispersion and correlation swaps* (theory only; see note) | paper | https://arxiv.org/pdf/1004.0125 |

> **Note on the dispersion reference.** Jacquier & Slaoui (arXiv:1004.0125) derive why the implied
> correlation embedded in a variance-swap dispersion trade differs from a correlation swap strike —
> the spread is explained by the trade's **volga** (second-order volatility sensitivity). It is
> listed here as background because it is the rigorous treatment of the dispersion mechanism the
> variance-beta result in §3.3 motivates. It is **not** a separate library entry: the paper contains
> no data, tables, or test statistics, so it does not meet criterion 4 of `INGESTION_STANDARD.md`
> ("Reported results"). A dispersion entry awaits a source with empirical evidence; the canonical
> candidates (Driessen–Maenhout–Vilkov, Bakshi–Kapadia) are paywalled with no public preprint found.

## 3. Mathematical foundation

### 3.1 Model-free replication of the variance swap rate

The result the whole entry rests on. Under a continuous semimartingale price process, the
risk-neutral expected realised variance can be written as a portfolio of European options across all
strikes:

```
E^Q[ RV(t,T) ]  ≈  (2/B(t,T)) · [ ∫_0^F  P(K)/K² dK  +  ∫_F^∞  C(K)/K² dK ]
```

where `P(K)` and `C(K)` are put and call prices at strike `K`, `F` is the forward, and `B(t,T)` the
discount factor. The `1/K²` weighting is the key: it is exactly the weighting that makes a portfolio
of options have constant dollar gamma, so that a delta-hedged position in it accrues P&L
proportional to realised variance regardless of the path.

This is what makes the measurement robust. No volatility model, no Black–Scholes inversion, no
parametric assumption — only static option prices plus dynamic futures trading. **The VIX index is
this formula.** CBOE's methodology is the same replication applied to 30-day S&P 500 options.

### 3.2 The premium and its sign

The variance swap costs nothing to enter, so its rate `SW(t,T)` is the risk-neutral expectation of
realised variance. If investors were risk-neutral about variance, `E[RV] = SW` and the average of
`RV − SW` would be zero. It is not: it is reliably negative on indices.

The economic reading Carr and Wu give: *"investors regard market volatility increases as extremely
unfavorable shocks to the investment opportunity and demand a heavy premium for bearing such
shocks."* Long variance is insurance against exactly the state — a market crash with a volatility
spike — in which a diversified investor's wealth is falling and marginal utility is highest. It
pays to hold, so it is priced above fair value. Selling it is being paid to underwrite that
insurance.

### 3.3 Why the variance beta result matters for implementation

The premium being a *market-portfolio* phenomenon has a direct trading implication that is easy to
get backwards. Selling single-stock variance is **not** a diversified version of selling index
variance. On most individual names there is no reliable premium to harvest — you are taking the
gamma risk without the compensation. The regression `LRP_j = 0.0201 + 0.2675·β^V_j` says that a
stock's premium scales with how much its variance co-moves with market variance, not with how
volatile it is.

This is also the theoretical basis of **dispersion trading** — selling index variance while buying
single-stock variance — since it isolates the correlation component that carries the premium. That
is a separate entry, queued for Wave 3.

## 4. Known criticisms and limitations

1. **The Sharpe ratio is a misleading statistic here, and the authors say so.** Carr and Wu report
   raw information ratios "over three" for short index variance, then immediately caution: *"given
   the nonlinear payoff structure, caution should be applied when interpreting Sharpe ratios on
   derivative trading strategies,"* citing Goetzmann, Ingersoll, Spiegel & Welch (2002). Short
   variance has a payoff profile deliberately engineered to look good under a mean/variance metric
   while carrying catastrophic left-tail risk. **Treat any Sharpe ratio on this strategy as
   uninformative.**
2. **Sample period ends February 2003 — before the strategy's worst episodes.** The working paper's
   data stops well before 2008 and long before the 5 February 2018 "Volmageddon," in which
   inverse-volatility ETPs lost the large majority of their value in a single session and XIV was
   terminated. The published evidence is therefore a measurement of the premium in a period that
   excludes its most violent realisations.
3. **Selling variance is short a convex payoff.** Realised variance is unbounded above and bounded
   below by zero. A short variance swap position has capped gains and effectively uncapped losses,
   with the losses concentrated in exactly the states where funding disappears.
4. **Replication error and discrete strikes.** The theory needs a continuum of strikes to infinity.
   Real option chains are discrete and truncated, which introduces a documented approximation error
   and makes the synthetic swap rate slightly wrong — usually in the direction of understating tail
   risk.
5. **Jumps break the replication.** The `1/K²` portfolio replicates variance exactly only for
   continuous price paths. Under jumps, there is a gap between the variance swap rate and the
   option portfolio, which matters most precisely during the events that hurt short-variance
   positions.
6. **Implementation is not free.** Variance swaps are OTC and require counterparty credit lines.
   The listed alternatives (VIX futures, options strips, ETPs) each carry their own basis, roll
   cost, and path dependency, and none of them is the instrument the paper measures.
