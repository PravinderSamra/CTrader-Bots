# Backtest & Data Summary — Momentum Crashes & Dynamic Weighting

## Verification

All figures below were read directly from the full text of Daniel, K., & Moskowitz, T. J. (2016),
"Momentum crashes," *Journal of Financial Economics* 122(2), 221–247 (open access, CC BY), retrieved
in-session from `kentdaniel.net/papers/published/jfe_16.pdf`. Table references are to that document.
**Evidence grade: `verified-primary`.**

---

## 1. Data sample

| Field | Value |
|---|---|
| Primary sample | **January 1927 – 2013**, US equities |
| Data source | CRSP; market proxy is the CRSP value-weighted index |
| Strategy | Long top decile / short bottom decile of past 12-month returns (WML) |
| Robustness markets | US, Europe, Japan, UK |
| Robustness asset classes | Five (equity indices, commodities, fixed income, currencies, plus US equities) |
| Subsample checks | Every quarter-century subsample in US equities |
| Volatility data | VIX-imputed variance swap returns |

The 86-year sample is the point. The Jegadeesh–Titman evidence covers 1965–1989, which contains no
momentum crash of the magnitude the strategy is capable of producing.

## 2. Unconditional performance — Table 1

| Portfolio | Annualised excess return |
|---|---|
| Winner decile | **15.3%** |
| Loser decile | **−2.5%** |
| Market | **7.6%** |

| Metric | WML | Market |
|---|---|---|
| **Sharpe ratio** | **0.71** | **0.40** |
| Market beta | **−0.58** | — |
| **Unconditional CAPM alpha** | **22.3% per year (t = 8.5)** | — |

An ex post optimal combination of the market and WML has a Sharpe ratio more than double the
market's. Taken alone, these numbers make momentum look like the best risk-adjusted trade in
equities — which is exactly the impression the rest of the paper corrects.

From the unconditional market model regression (Regression 1, Table 3):
`β₀ = −0.576`, `α = 1.852% per month (t = 7.3)`.

## 3. The crashes

### 3.1 The two worst episodes

| Episode | Loser decile | Winner decile | Momentum impact |
|---|---|---|---|
| **July–August 1932** (two consecutive months — the two worst in the sample) | **+232%** | **+32%** | Catastrophic: short the +232% leg |
| **March–May 2009** (three months) | **+163%** | **+8%** | Catastrophic |

### 3.2 The sustained drawdown periods

| Period | Description |
|---|---|
| **June 1932 – December 1939** | Largest sustained momentum drawdown |
| **March 2009 – March 2013** | Second largest |

Both start dates are market bottoms — June 1932 following the Great Depression decline, March 2009
following the financial crisis. The pattern is not coincidence; it is the mechanism.

> Note the **duration**. These are not single bad months to be ridden out. The 2009 episode runs
> four years and the 1932 episode seven and a half. Momentum crashes are persistent, which is what
> makes them career-ending rather than merely painful.

## 4. The conditional beta result — Table 3 and §3

Henriksson–Merton up/down beta decomposition:

| State | Up-market beta | Down-market beta | t-stat of difference |
|---|---|---|---|
| **Bear market** (ex ante: negative cumulative 24-month market return) | **−1.51** | **−0.70** | **4.5** |
| Non-bear market | no statistically reliable difference | | |

In bear markets, momentum loses more than twice as fast on the way up as it gains on the way down.
This is a **written call on the market**, and the asymmetry is driven predominantly by the **past
losers**, whose distressed equity behaves as deep-OTM optionality on firm value.

### Conditioning variables

| Variable | Definition | Tradable? |
|---|---|---|
| `I_B,t−1` | 1 if cumulative CRSP VW index return over the **past 24 months** is negative | **Yes** — ex ante |
| `Ĩ_U,t` | 1 if market excess return in month `t` is positive | **No** — contemporaneous, for measurement only |

## 5. The volatility hedge that does not work

| Finding | Result |
|---|---|
| Momentum exposure to market variance innovations, bear markets | Strong and **negative** |
| Same exposure, normal (bull) markets | Not present |
| **Hedging it** (buying S&P variance swaps in bear markets) | **Does not restore profitability** |

The paper's conclusion: time-varying exposure to volatility risk does **not** explain the time
variation in the momentum premium. A documented negative result — the obvious hedge fails, and the
solution has to be dynamic position sizing instead.

## 6. The dynamic strategy — headline result

| Claim | Value |
|---|---|
| Improvement over static momentum | **More than doubles the Sharpe ratio** |
| Alpha vs. market, FF factors, static momentum, **and conditional versions of all of these** | Significant and positive |
| Alpha vs. the constant-volatility strategy (Barroso & Santa-Clara) | Positive; also **spans** its returns |
| **Across all markets and asset classes, implementable dynamic strategy** | **Annualised Sharpe ratio 1.19** |
| Relative to static US-equity momentum over the same period | **~4× larger** |
| Works in Japan, where static momentum famously fails | **Yes** |

The weighting rule is `w_t ∝ μ_t / (γ · σ²_t)` — exploiting forecastability in **both** the
conditional mean and the conditional variance. The distinction from pure volatility targeting is
load-bearing: constant-volatility scaling smooths returns, but the *mean* forecast is what produces
the alpha, and the spanning tests demonstrate the dynamic strategy captures everything the
volatility-scaled version does plus more.

## 7. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Maximum drawdown, as a single number | **NOT REPORTED IN SOURCE** as a percentage — the crash episodes are characterised by their decile returns and durations rather than a peak-to-trough statistic |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Win rate / profit factor | **NOT REPORTED IN SOURCE** |
| Transaction costs of the dynamic overlay | Not the paper's focus; dynamic weighting adds turnover on top of base momentum |
| Realised leverage of the dynamic strategy | Not tabulated in the text consulted |

## 8. Where the strategy thrives vs. fails

**Static momentum — thrives when:** trends persist, volatility is moderate, no recent market crash.
See the parent entry.

**Static momentum — fails catastrophically when:**
- The market rebounds after a sustained decline. Both documented crash episodes begin at a market
  bottom.
- Volatility is high and the market has fallen over the trailing 24 months — the *ex ante*
  identifiable panic state.
- The loser decile is populated by distressed, highly levered firms — precisely the condition after
  a crash, and precisely what creates the written-call payoff.

**Dynamic momentum — thrives when:** the conditional mean and variance forecasts are accurate and
the operator can actually reduce or reverse exposure in panic states.

**Dynamic momentum — fails when:**
- The regime transition is abrupt, so the forecasts lag the state change. The estimates are noisiest
  exactly when they matter most.
- Required leverage in calm periods is unfundable.
- The bear indicator misclassifies a regime — a coarse 24-month cumulative-return rule will.

## 9. Decay and current status

**`decay_status: intact`** — for the *diagnosis*. Qualified for the *fix*.

- **The crash risk is structural and will not decay.** It is a mechanical consequence of what the
  short leg becomes after a market decline: distressed firms whose equity is an option on recovery.
  As long as momentum sorts on past returns, post-crash losers will be levered survivors with convex
  upside, and shorting them will be short a call. No amount of competition removes this.
- **Crowding may have made it worse.** Momentum is among the most widely implemented factors in
  existence. A crowded book unwinds faster, and if many managers adopt similar conditional
  de-risking rules, that de-risking becomes a correlated flow into the same rebound.
- **The dynamic fix is now widely known.** Published in 2016 and adopted quickly by practitioners,
  the volatility-scaled and conditionally-weighted momentum variants are standard. The 1.19 Sharpe
  is an in-sample, full-history figure using estimated conditional moments; live implementations
  should expect materially less.
- **The paper's own honesty about data mining is the right frame.** The authors flag "the paucity of
  momentum crashes" themselves. Two major crash events in 86 years is a thin identification base for
  a conditional model, and the cross-market and cross-asset robustness is what carries the argument
  rather than the US time series alone.

**How to use this entry.** Read it as the mandatory companion to
`../cross-sectional-momentum-jegadeesh-titman/`. That entry tells you what momentum earns; this one
tells you what it costs and when. Any momentum implementation that does not have an explicit answer
to "what happens in the twelve months after a market bottom" is incomplete regardless of its
backtested Sharpe ratio.
