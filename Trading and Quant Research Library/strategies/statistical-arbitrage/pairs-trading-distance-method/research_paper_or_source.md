# Pairs Trading — Distance Method (Gatev, Goetzmann & Rouwenhorst)

**Category:** Statistical Arbitrage & Relative Value
**Anchor paper:** Gatev, E., Goetzmann, W. N., & Rouwenhorst, K. G. (2006). "Pairs Trading:
Performance of a Relative-Value Arbitrage Rule." *The Review of Financial Studies*, 19(3), 797–827.
DOI: 10.1093/rfs/hhj020

---

## 1. Abstract / summary of the core edge

Two stocks that have historically moved together are close economic substitutes. When their prices
diverge, at least one of them is mispriced relative to the other. The strategy shorts the relative
winner, buys the relative loser, and waits for convergence — taking no view on the market
direction, only on the *relative* value of the pair.

GGR test this with daily CRSP data over 1962–2002. Pairs are selected purely mechanically: the
minimum sum of squared deviations between normalised price series over a 12-month formation
window. Trading then runs for a 6-month window, opening a position whenever the pair diverges by
two historical standard deviations and closing on the next crossing.

The headline result, in the authors' own words:

> "A simple trading rule yields average annualized excess returns of up to 11% for self-financing
> portfolios of pairs. The profits typically exceed conservative transaction-cost estimates."

The important part is not the return level but what survives the controls. The profits are not
explained by the Fama–French three factors, by momentum, or by short-term reversal. After
controlling for all five, the top-20 portfolio still shows a monthly intercept of **0.764%
(t = 7.08)**. The edge is not repackaged reversal — it is compensation for enforcing the Law of One
Price between substitutes.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| GGR (2006), RFS — full text PDF (verified in-session) | paper | http://stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingGGR.pdf |
| Publisher version | paper | https://academic.oup.com/rfs/article-abstract/19/3/797/1646694 |
| SSRN working paper version | paper | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=141615 |
| NBER working paper w7032 | paper | https://www.nber.org/papers/w7032 |
| Do & Faff (2010), "Does Simple Pairs Trading Still Work?" — the decay evidence | paper | https://www.tandfonline.com/doi/abs/10.2469/faj.v66.n4.1 |
| Engle & Granger (1987) — cointegration foundation for the modern variant | paper | https://www.jstor.org/stable/1913236 |

## 3. Mathematical and logical foundation

### 3.1 Pair selection — the distance criterion

For each stock `i`, build a cumulative total-return index `P_i(t)` over the 12-month formation
period, normalised to start at 1. For every candidate pair `(i, j)`, compute the sum of squared
deviations:

```
SSD(i, j) = Σ_{t in formation} ( P_i(t) − P_j(t) )²
```

Rank all pairs by `SSD` ascending. The "top n" portfolio takes the n pairs with the smallest
distance. This is deliberately atheoretical — no sector constraint, no factor model, no
cointegration test. Its virtue is that it cannot be overfit: there are no free parameters in the
selection step.

Note what the criterion actually selects for: **low volatility of the spread**, not high
correlation. This is why the selected pairs concentrate so heavily in utilities — 71% of the
stocks in the top-20 pairs are utility stocks (Table 2, Panel B).

### 3.2 The trading rule

Let `S(t) = P_i(t) − P_j(t)` be the normalised price spread, and `σ_S` its standard deviation
estimated **over the formation period only** (no look-ahead).

```
Open   short i, long j   when  S(t) > +2·σ_S
Open   long i,  short j  when  S(t) < −2·σ_S
Close  both legs         when  S(t) crosses zero
Force-close              at the end of the 6-month trading period
```

Each leg is one dollar, so the position is self-financing at initiation. A pair may open and close
multiple times within one trading window — GGR measure an average of **2.02 round trips per pair**
for the top-5 portfolio.

### 3.3 The two return conventions (this is where most replications go wrong)

GGR report returns two ways, and the gap between them is large:

- **Fully invested (return on employed capital):** divide payoffs by the number of pairs that
  actually opened. This is the return on capital when deployed.
- **Committed capital:** divide by the full number of pairs in the portfolio, whether or not they
  traded. Idle pairs earn zero and drag the average down.

The committed-capital figure is the conservative and honest one for a fund that must reserve
capital for all n pairs. It is roughly **half** the fully-invested figure (0.81% vs 1.44% monthly
for the top 20). Any replication quoting the higher number without saying which convention it used
is not comparable to anything.

### 3.4 Why the edge should exist

GGR's own interpretation is that the profits are compensation to arbitrageurs for enforcing the Law
of One Price — a payment for supplying liquidity to whoever is pushing the two substitutes apart.
Supporting this reading:

- Profits load on a **latent common factor** that is not the market, size, value, momentum, or
  reversal. The authors note this factor "has been relatively dormant recently."
- The strategy's exposure to the market is statistically indistinguishable from zero for the top-5
  and top-20 portfolios (market beta −0.067, t = −1.03 and −0.032, t = −0.64).
- The returns are **positively skewed** (skewness 1.39 for the top-20 with no waiting), which is
  unusual — most convergence strategies are negatively skewed. GGR note this means their Sharpe
  ratios are, if anything, biased *downward*.

### 3.5 The modern cointegration variant

The distance method is a crude proxy for a stationary spread. The formal version tests whether a
linear combination of the two log price series is stationary — i.e. whether the pair is
*cointegrated* in the Engle–Granger sense:

```
log P_i(t) = α + β · log P_j(t) + ε(t)
```

Run an ADF test on the residual `ε(t)`; if the unit-root null is rejected, the pair is
cointegrated and `β` is the hedge ratio. The spread is then commonly modelled as an
Ornstein–Uhlenbeck process:

```
dε(t) = θ ( μ − ε(t) ) dt + σ dW(t)
```

which gives a mean-reversion half-life of `ln(2)/θ` — the single most useful number for deciding
whether a pair is tradable at all. A pair with a 200-day half-life will not converge inside a
6-month window often enough to pay for its costs.

This variant is a separate library entry (queued, Wave 2). It is mentioned here because the
distance method is its ancestor and the two are frequently confused.

## 4. Known criticisms and limitations

1. **Decay — but not in GGR's own holdout.** Do & Faff (2010) extend the methodology to later
   data and confirm a continuing downward trend in profitability, though the strategy still performs
   strongly in periods of prolonged turbulence. Note carefully that GGR's *own* out-of-sample test
   (1999–2002, model frozen from the 1999 draft) returned 10.4% p.a. with a t-statistic of 4.82 —
   the decay evidence comes from later authors and later data, not from GGR. See
   `backtest_and_data_summary.md` §7 for the full treatment.
2. **Bid–ask bounce inflates the raw result.** GGR's own one-day-waiting test cuts the top-20
   fully-invested return from 1.44% to 0.895% per month. The one-day-waiting figure is the one to
   quote; the no-waiting figure is contaminated by buying at bid and selling at ask.
3. **Utility concentration.** With 71% utility stocks in the top-20, a large part of the result is
   a bet on interest-rate-sensitive, low-volatility names, and its factor exposure is not as clean
   as "market neutral" suggests.
4. **The trigger is probably too tight.** GGR note in a footnote that "the optimal trigger point in
   terms of profitability may actually be much higher than two standard deviations, although we have
   not experimented to find out." Because the selection step picks the *smallest* historical spread
   volatility, `σ_S` is likely underestimated, so positions open too early to cover costs.
5. **Divergence is not always mispricing.** The strategy has no mechanism to distinguish a
   temporary dislocation from a permanent change in fundamentals. A merger, a fraud, or a
   regulatory shock produces a divergence that never converges, and the mechanical rule holds the
   losing position to the end of the window.
