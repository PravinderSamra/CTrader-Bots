# Momentum Crashes & Dynamic Momentum Weighting

**Category:** Cross-Sectional Equity Factors (Wave 2 depth entry)
**Anchor paper:** Daniel, K., & Moskowitz, T. J. (2016). "Momentum crashes." *Journal of Financial
Economics*, 122(2), 221–247. Open access under CC BY.
**Parent entry:** `../cross-sectional-momentum-jegadeesh-titman/`

---

## 1. Abstract / summary of the core edge

This entry exists because the momentum entry is dangerous on its own.

Jegadeesh & Titman established that momentum earns a large premium. Daniel and Moskowitz establish
what it costs: momentum returns are **negatively skewed and punctuated by rare, enormous, persistent
crashes**, and — this is the contribution — those crashes are **partly forecastable**.

The two worst months for a US momentum strategy in the 1927–2013 sample are consecutive: **July and
August 1932**. Over that period the loser decile returned **232%** while the winner decile gained
only **32%**. The more recent instance: over **March–May 2009**, the loser decile rose **163%** while
winners gained **8%**. A long-winners/short-losers book is on exactly the wrong side of both.

The mechanism is a **conditional beta** effect, and it is elegant. After a market decline, the
past-loser portfolio consists of severely distressed, highly levered firms whose equity behaves like
a call option on the firm's assets — deeply out of the money, enormous upside convexity. When the
market rebounds, that optionality pays off violently. The momentum strategy, short those names,
behaves like a **written call option on the market**: it gains a little when the market falls and
loses a great deal when the market rises.

Measured with a Henriksson–Merton specification, in a bear market a momentum portfolio's up-market
beta is more than double its down-market beta: **−1.51 versus −0.70, t-statistic on the difference
= 4.5**. Outside of bear markets there is no statistically reliable difference.

The payoff: because crashes occur in identifiable states — following market declines, when
volatility is high — the momentum premium and momentum volatility are **both forecastable and
separately so**. Scaling exposure by the conditional Sharpe ratio produces a dynamic strategy that
**more than doubles the static strategy's Sharpe ratio**. Applied across all markets and asset
classes, the implementable dynamic strategy delivers an **annualised Sharpe ratio of 1.19 — four
times that of the static momentum strategy applied to US equities over the same period.**

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Daniel & Moskowitz (2016), JFE — full text, open access (verified in-session) | paper | https://www.kentdaniel.net/papers/published/jfe_16.pdf |
| NBER working paper w20439 | paper | https://www.nber.org/system/files/working_papers/w20439/w20439.pdf |
| SSRN record | paper | https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2371227 |
| Barroso & Santa-Clara (2015) — the constant-volatility alternative | paper | https://www.sciencedirect.com/science/article/abs/pii/S0304405X14002323 |
| Kenneth French data library — UMD and market factors | dataset | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html |

## 3. Mathematical and logical foundation

### 3.1 The unconditional picture (Table 1, 1927–2013)

| Portfolio | Annualised excess return |
|---|---|
| Winner decile | **15.3%** |
| Loser decile | **−2.5%** |
| Market | 7.6% |

| Metric | WML | Market |
|---|---|---|
| Sharpe ratio | **0.71** | 0.40 |
| Market beta | **−0.58** | — |
| **Unconditional CAPM alpha** | **22.3% per year (t = 8.5)** | — |

A 22.3% annual alpha with a t-statistic of 8.5 is, on its face, an extraordinary challenge to
rational asset pricing. The rest of the paper is about why that number is not what it appears to be.

### 3.2 The conditional beta specification

The core regression uses two conditioning variables:

- **`I_B,t−1`** — an **ex ante** bear-market indicator, equal to 1 if the cumulative CRSP
  value-weighted index return over the **past 24 months** is negative. Note *ex ante*: it uses only
  past information, so it is tradable.
- **`Ĩ_U,t`** — a **contemporaneous** up-market indicator, equal to 1 if the market excess return in
  month `t` is positive. Not tradable; used to *measure* the option-like payoff, not to trade it.

Unconditional market model (Regression 1, Table 3):

```
R_WML,t = α₀ + β₀ · R_m,t + ε_t
```

giving `β₀ = −0.576` and `α = 1.852% per month (t = 7.3)`.

The Henriksson–Merton up/down decomposition then reveals what the single beta hides:

| State | Up-market beta | Down-market beta | Difference |
|---|---|---|---|
| **Bear market** | **−1.51** | **−0.70** | t = **4.5** |
| Normal market | — | — | no reliable difference |

Read the bear-market row as a payoff diagram. Market falls → the strategy's beta is −0.70, so it
gains modestly. Market rises → the beta is −1.51, so it loses more than twice as fast. **That is a
written call.**

Further decomposition shows most of the asymmetry comes from **past losers**, consistent with the
option-on-distressed-equity story: after a crash, loser-decile firms are near-insolvent, their
equity is deep-OTM optionality on asset value, and a rebound repices that optionality explosively.

### 3.3 The volatility-risk red herring — an honest negative result

If momentum in bear markets is short a call on the market, it should be short volatility too. It is:
using VIX-imputed variance swap returns, the paper finds momentum has strong negative exposure to
innovations in market variance **in bear markets but not in bull markets**.

The natural next step is to hedge it — buy S&P variance swaps in bear markets. The paper tests this
and reports that it **does not restore the profitability of momentum in bear markets**. Time-varying
volatility exposure therefore does *not* explain the time variation in the momentum premium.

This negative result is worth as much as the positive ones. It closes off the obvious fix and forces
the solution to be position sizing rather than hedging.

### 3.4 The dynamic strategy

Two separately forecastable quantities:

1. **The conditional mean** of the momentum premium — low or negative in "panic" states (following
   market declines, high volatility).
2. **The conditional variance** of momentum returns — strongly predictable, and distinct from the
   predictability in the mean.

The optimal weight on the momentum portfolio is proportional to the conditional Sharpe ratio scaled
by conditional volatility:

```
w_t  ∝  μ_t / (γ · σ²_t)
```

where `μ_t` is the forecast conditional mean and `σ²_t` the forecast conditional variance. This
maximises the unconditional Sharpe ratio of the resulting strategy.

**Critically, this is not the same as volatility targeting.** Barroso & Santa-Clara (2015) propose
scaling momentum by realised volatility alone (`w_t ∝ 1/σ²_t`). Daniel and Moskowitz show their
dynamic strategy produces **positive alpha relative to the constant-volatility strategy and spans
its returns** in spanning tests. Volatility scaling smooths the ride; exploiting the forecastable
*mean* is what adds the return.

## 4. Robustness — the part that makes this credible

The authors explicitly confront the data-mining objection ("the pernicious effects of data mining
from an ever-expanding search across studies (and in practice) for strategies that improve
performance"). Their response is breadth:

- Robust in **every quarter-century subsample** in US equities.
- Momentum crashes occur in **four different equity markets** (US, Europe, Japan, UK) and **five
  distinct asset classes**, and are "consistently driven by the conditional beta and option-like
  feature of losers."
- The same option-like behaviour of losers appears in index futures, commodity, fixed income and
  currency momentum.
- The dynamic strategy is "ubiquitously successful" across all of them — **including Japan**, where
  static momentum has famously failed to produce positive profits.

That last point is the strongest single piece of evidence. A fix that only worked where the original
strategy already worked would be suspect; one that rescues the known counter-example is much harder
to dismiss.

## 5. Known criticisms and limitations

1. **Crashes are rare, so the conditioning is estimated from few events.** The authors acknowledge
   "the paucity of momentum crashes." The 1932 and 2009 episodes carry enormous weight in
   identifying the panic-state parameters, and two events is a thin basis for a conditional model —
   which is precisely why the cross-market robustness checks matter so much.
2. **The dynamic weights require forecasting two moments in real time.** Both `μ_t` and `σ²_t` are
   estimated, and both are noisiest exactly when they matter most — during the transition into a
   panic state. The in-sample optimum is not achievable live.
3. **Leverage.** Optimal weights can call for substantial leverage in calm periods. Whether a
   levered momentum book is fundable at those moments is not modelled.
4. **The ex ante bear indicator is a blunt instrument.** "Cumulative 24-month market return is
   negative" is a coarse state variable that will misclassify some regimes and lag turning points.
   Its virtue is that it is unambiguous and cannot be tuned much; its cost is precision.
5. **Costs are not the focus.** Dynamic weighting adds turnover on top of the base momentum
   strategy's already meaningful trading, and the base strategy's short leg is expensive to borrow.
6. **Crowding.** If a large share of momentum capital adopts the same conditional de-risking rule,
   the de-risking itself becomes a correlated flow — potentially deepening the very rebound the rule
   is designed to avoid.
