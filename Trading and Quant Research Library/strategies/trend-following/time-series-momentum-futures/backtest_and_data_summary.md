# Backtest & Data Summary — Time Series Momentum (TSMOM)

## Verification

All figures below were read directly from the full text of Moskowitz, Ooi & Pedersen (2012),
"Time series momentum," *Journal of Financial Economics* 104(2), 228–250, retrieved in-session from
`w4.stern.nyu.edu/facdir/lpederse/papers/TimeSeriesMomentum.pdf`. Table and figure references are
to that document. **Evidence grade: `verified-primary`.**

Where the paper does not report a statistic, this file says so explicitly rather than substituting
an estimate.

---

## 1. Data sample

| Field | Value |
|---|---|
| Instruments | **58 liquid futures and forwards** |
| — Commodities | 24 contracts |
| — Currencies | 12 cross-currency pairs (from 9 underlying currencies) |
| — Equity indices | 9 developed-market index futures |
| — Fixed income | 13 developed government bond futures |
| Full data range | January 1965 – December 2009 |
| **Main analysis period** | **January 1985 – December 2009** |
| Secondary period | 1966–1985 (limited instrument coverage) |
| Frequency | Daily returns for volatility estimation; monthly for signal and rebalance |
| Position data | CFTC Commitments of Traders — speculator vs. hedger positioning |

MOP restrict the headline sample to post-1985 "to ensure that a comprehensive set of instruments
have" data available, and state results are similar including data back to 1965. The instruments
are deliberately the most liquid contracts in the world, chosen to avoid illiquidity and stale-price
contamination; the paper separately confirms robustness in illiquid contracts (feeder cattle, Kansas
wheat, lumber, orange juice, rubber, tin) and emerging markets.

## 2. Strategy specification as tested

| Parameter | Value |
|---|---|
| Lookback | 12 months (sign of the past 12-month excess return) |
| Holding period | 1 month |
| Position size | `40% / σ_{t−1}` — inverse ex-ante volatility, 40% annualised vol target per position |
| Volatility model | Exponentially weighted, centre of mass **60 days** (`δ ≈ 0.9836`), annualisation factor 261 |
| Look-ahead control | `σ_{t−1}` applied to time-`t` returns |
| Portfolio weighting | Equal-weight across all instruments available that month |
| Resulting portfolio volatility | **12% annualised** (1985–2009) |

## 3. Headline performance

### 3.1 Diversified portfolio

| Metric | Value | Source |
|---|---|---|
| **Annualised Sharpe ratio** | **> 1.0**, "roughly 2.5 times the Sharpe ratio for the equity market portfolio" | Introduction, §1 |
| Annualised volatility | 12% | §4.1 |
| Sharpe, 1966–1985 out-of-sample extension | **1.1** (gross, annualised) | §4.1 |

> ⚠️ MOP characterise the main-sample diversified Sharpe as "greater than one" rather than printing
> a single point estimate in the text. This entry records it as published. Any replication quoting
> a precise decimal for 1985–2009 is quoting a *computed* figure, not the paper's — recompute it
> from the AQR public dataset if you need one. Sharpe ratios in the paper are **gross**.

The 1966–1985 result is the strongest robustness evidence in the paper: an entirely separate,
earlier sample, with a statistically significant return and a **1.1 annualised Sharpe**, described
by the authors as "strong out-of-sample evidence of time series momentum."

### 3.2 Per-instrument consistency (Figure 2)

| Result | Value |
|---|---|
| Contracts with positive TSMOM returns | **58 of 58** |
| Statistically significant at 5% | **52 of 58** |
| Positive alpha vs. always-long the same contract | **90%** of cases (26% of those significant; none of the negative ones significant) |
| Correlation (Sharpe ratio, illiquidity rank) | **−0.16** |

Every single contract works. The near-zero correlation with illiquidity rules out the usual "the
effect only lives in untradeable corners" objection.

### 3.3 Risk-adjusted alpha (Table 3)

**Panel A — MSCI World + Fama–French factors**

| Frequency | MSCI World | SMB | HML | UMD | **Intercept (alpha)** | R² |
|---|---|---|---|---|---|---|
| Monthly | 0.09 (1.89) | 0.05 (0.84) | 0.01 (0.21) | 0.28 (6.78) | **1.58% (t = 7.99)** | 14% |
| Quarterly | 0.07 (1.00) | 0.18 (1.44) | 0.01 (0.11) | 0.32 (4.44) | **4.75% (t = 7.73)** | 23% |

**Panel B — Asness, Moskowitz & Pedersen "everywhere" factors**

| Frequency | MSCI World | VAL Everywhere | MOM Everywhere | **Intercept** | R² |
|---|---|---|---|---|---|
| Monthly | 0.11 (2.67) | 0.14 (2.02) | 0.66 (9.74) | **1.09% (t = 5.40)** | 30% |
| Quarterly | 0.12 (1.81) | 0.26 (2.45) | 0.71 (6.47) | **2.93% (t = 4.12)** | 34% |

A monthly alpha of 1.58% (t = 7.99) against the standard factor set, falling to 1.09% (t = 5.40)
against the far more demanding global value/momentum-everywhere benchmark. It survives both.

### 3.4 Versus cross-sectional momentum (Table 5)

| Metric | Value |
|---|---|
| Beta of TSMOM on XSMOM | **0.66 (t = 15.17)** |
| R² | 44% |
| **TSMOM alpha after controlling for XSMOM** | **76 bp/month (t = 5.90)** |

Related, but not the same strategy. Per-asset-class R² ranges from 56% (FX) to 14% (fixed income),
with TSMOM alpha remaining significant throughout.

### 3.5 The convexity result (Table 3, Panel C)

Quarterly TSMOM returns regressed on the market and the market squared:

| Regressor | Coefficient | t-stat |
|---|---|---|
| MSCI World | 0.01 | 0.17 |
| **MSCI World squared** | **1.99** | **3.88** |
| TED spread | 0.001 | 0.06 |
| TED spread top 20% | 0.008 | 0.29 |
| VIX | 0.001 | 0.92 |
| VIX top 20% | 0.003 | 0.10 |

Zero linear market exposure, significant positive exposure to the *square* of market returns. This
is the "time series momentum smile" (Figure 4): the strategy pays most in the largest moves in
either direction. Note also that TED spread and VIX exposures are insignificant — the payoff is not
simply a short-liquidity or short-volatility position in disguise.

## 4. Robustness across lookback and holding periods (Table 2, Panel A)

t-statistics of alphas, all asset classes, controlling for MSCI World, Barclays Bond Index, S&P
GSCI, and HML/SMB/UMD:

| Lookback ↓ / Holding → | 1 | 3 | 6 | 9 | 12 | 24 | 36 | 48 |
|---|---|---|---|---|---|---|---|---|
| **1** | 4.34 | 4.68 | 3.83 | 4.29 | 5.12 | 3.02 | 2.74 | 1.90 |
| **3** | 5.35 | 4.42 | 3.54 | 4.73 | 4.50 | 2.60 | 1.97 | 1.52 |
| **6** | 5.03 | 4.54 | 4.93 | 5.32 | 4.43 | 2.79 | 1.89 | 1.42 |
| **9** | 6.06 | 6.13 | 5.78 | 5.07 | 4.10 | 2.57 | 1.45 | 1.19 |
| **12** | **6.61** | 5.60 | 4.44 | 3.69 | 2.85 | 1.68 | 0.66 | 0.46 |
| **24** | 3.95 | 3.19 | 2.44 | 1.95 | 1.50 | 0.20 | 0.09 | 0.33 |
| **36** | 2.70 | 2.20 | 1.44 | 0.96 | 0.62 | 0.28 | 0.07 | 0.20 |
| **48** | 1.84 | 1.55 | 1.16 | — | — | — | — | — |

Read this grid carefully — it is the most useful table in the paper:

- The 12-month lookback / 1-month holding combination has the **highest t-statistic in the grid
  (6.61)**, which is why it was chosen as "TSMOM."
- The effect is **not a knife-edge**. Every lookback from 1 to 12 months is significant at every
  holding period out to 12 months. A strategy that only works at one parameter setting is a fitting
  artefact; this one works across a broad plateau.
- Significance **decays monotonically** as lookback extends past 12 months and as holding extends
  past 12 months — consistent with the under-reaction-then-reversal mechanism, and inconsistent
  with a pure risk story.

## 5. Where the strategy thrives vs. fails

**Thrives when:**
- Markets sustain directional moves over multi-month horizons — the fundamental requirement.
- Extreme markets, in **either** direction. This is the documented behaviour, not marketing: the
  squared-market coefficient is 1.99 (t = 3.88).
- Crises that develop over months rather than days. MOP's worked example: TSMOM produced large
  profits in **October, November and December 2008** as commodities and equities fell, bonds rose,
  and currencies moved sharply.
- Diversification is wide. The per-position 40% vol target only collapses to a 12% portfolio vol
  because 58 imperfectly correlated instruments are combined.

**Fails when:**
- **Trends break.** MOP document losses in **Q3 2008** as prior trends reversed, and again in
  **March, April and May 2009**, noting explicitly that "the ending of a crisis constitutes a sharp
  trend reversal that generates losses on a trend following strategy such as TSMOM."
- Markets chop within a range: the monthly sign flip whipsaws, paying costs in both directions.
- V-shaped shocks with no persistence — the crash is over before the signal turns.
- Correlations converge to one across the book, destroying the diversification the 12% portfolio
  volatility depends on.

## 6. Costs, capacity, and what the paper does not report

| Item | Status |
|---|---|
| Sharpe ratios | Reported **gross** (Figure 2 caption is explicit) |
| Transaction costs | Not modelled in the headline results |
| Maximum drawdown | **NOT REPORTED IN SOURCE** — Figure 3 plots cumulative log excess returns, but no drawdown statistic is printed |
| Win rate / profit factor | **NOT REPORTED IN SOURCE** — the paper reports regression alphas and Sharpe ratios, not trade statistics |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Turnover | Not reported; implied low — monthly rebalance of a sign signal |

This is a genuine gap between what academic papers report and what a trading desk needs. Anyone
needing drawdown, Sortino, or win-rate figures should compute them from the **AQR public dataset**
of the paper's own return series
(https://www.aqr.com/Insights/Datasets/Time-Series-Momentum-Original-Paper-Data) rather than take
them from a secondary source. Costs on liquid futures are small relative to a monthly rebalance,
but "small" is not "zero" and the published numbers do not include them.

## 7. Decay and current status

**`decay_status: partially-decayed`.**

- **The academic challenge.** Huang, Li, Wang & Zhou ("Time-series momentum: Is it there?", JFE)
  argue the predictive evidence is substantially weaker under a properly specified test, and that
  much of TSMOM's performance traces to volatility scaling and to the underlying assets' average
  returns rather than to trend predictability. This entry does not adjudicate that dispute; it is
  queued as a Wave 6 adversarial-review entry, and the disagreement is itself part of the record.
- **The live-capital evidence is mixed and regime-dependent.** Managed-futures trend following
  broadly underperformed its backtested profile through the 2010s — a period of central-bank-
  suppressed volatility and frequent sharp reversals — and then performed strongly in 2022 when
  sustained trends returned in rates, energy and currencies. That pattern is exactly what the
  documented convexity predicts, which argues the mechanism is intact but the payoff is
  regime-contingent, not that the effect was spurious.
- **The structural argument for persistence.** Unlike a pure pricing anomaly, MOP identify a
  counterparty: **speculators profit from time series momentum at the expense of hedgers**. If the
  premium is payment for absorbing hedgers' risk transfer, it does not get arbitraged to zero as
  long as hedgers keep hedging. This is the strongest reason to expect a residual edge — and the
  reason this entry is graded `partially-decayed` rather than `substantially-decayed`.

**How to use this entry.** Treat TSMOM as the canonical, correctly-constructed baseline for any
trend-following system: sign-of-12-month signal, inverse-volatility sizing, monthly rebalance, wide
diversification. Any proprietary trend model should be required to beat this baseline out of sample
before it earns its complexity. The AQR dataset makes that a concrete, checkable test.
