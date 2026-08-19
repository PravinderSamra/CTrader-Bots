# Backtest & Data Summary — Factor-Residual Statistical Arbitrage

## Verification

All figures below were read directly from the full text of Avellaneda, M., & Lee, J.-H.,
"Statistical Arbitrage in the U.S. Equities Market," **working paper dated June 15, 2009** (first
draft July 11, 2008), retrieved in-session from
`math.nyu.edu/~avellane/AvellanedaLeeStatArb20090616.pdf`. Published as *Quantitative Finance*
10(7), 761–782 (2010); the published version was not consulted.
**Evidence grade: `verified-primary`** for the working paper.

---

## 1. Data sample and backtest setup

| Field | Value |
|---|---|
| Market | US equities |
| Backtest period | **1997 – 2007** |
| Universe | US stocks with **market capitalisation above $1 billion** |
| Universe size (example) | 1,417 stocks on 1 May 2007 |
| Sector partition | **15 sectors**, each mapped to a sector ETF |
| Correlation matrix window | **252 trading days (1 year)** prior to trade date |
| OU estimation window | **60 business days** (`T₁ = 60/252`) |
| Mean-reversion filter | **κ > 8.4** (reversion time < half the estimation window) |
| **Transaction cost assumed** | **5 bp per trade → 10 bp round trip** |
| Rebalance | Daily; estimation always looks back from the trade date (no look-ahead) |

The paper states estimation is "always done looking back 60 days from the trade date, thus
simulating decisions which" use only information available at that time.

## 2. Headline performance (net of transaction costs)

| Signal | Period | **Sharpe ratio** |
|---|---|---|
| **PCA** | 1997–2007 | **1.44** |
| **PCA** | 2003–2007 | **0.90** |
| **Sector ETF** | 1997–2007 | **1.10** |
| **ETF + volume information** | 2003–2007 | **1.51** |

Read these together and the story is clear:

1. **PCA beats sector ETFs** over the full period — 1.44 vs 1.10. Statistically derived factors
   capture the return structure better than a fixed sector taxonomy.
2. **Both degrade sharply after 2002–2003.** PCA falls from 1.44 to 0.90; the paper reports ETF
   signals "experiencing a similar degradation after 2002." This decay is *inside the sample*, not
   an after-the-fact observation.
3. **Volume time reverses the decay for ETF signals.** Adding trading-volume information lifts the
   2003–2007 ETF Sharpe to **1.51** — better than anything else in the study, in the *harder* later
   period. The most valuable finding in the paper for anyone building this today.

## 3. Trading rule parameters as tested

| Parameter | Value | Note |
|---|---|---|
| `s_bo` (buy to open) | **1.25** | Open long when s-score < −1.25 |
| `s_so` (sell to open) | **1.25** | Open short when s-score > +1.25 |
| `s_bc` (close short) | **0.75** | Asymmetric — closes shorts sooner |
| `s_sc` (close long) | **0.50** | Close long when s-score > −0.50 |
| Cutoff fitting period | **2000–2004** (ETF factors); asymmetry chosen on 2000–2002 | Disclosed by the authors |
| Position on open | $1 of stock vs `β_i` dollars of sector ETF(s) | Market-neutral by construction |

Because the s-score is dimensionless, these thresholds are intended to be valid across all stocks —
the paper states the cutoffs are "expected to be valid across the different stocks." That is a
genuine advantage over per-pair threshold calibration.

## 4. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Maximum drawdown | **NOT REPORTED IN SOURCE** as a headline figure — the August 2007 episode is analysed qualitatively |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Win rate | **NOT REPORTED IN SOURCE** |
| Profit factor | **NOT REPORTED IN SOURCE** |
| Turnover | Not tabulated; implied high (daily rebalance across a large universe) |
| Borrow cost on the short leg | **Not modelled** — the 10 bp round trip covers slippage/commission only |
| Market impact at scale | Not modelled |
| Capacity estimate | **NOT REPORTED IN SOURCE** |

The missing borrow cost matters more here than the missing drawdown. A daily-rebalanced
market-neutral book with short exposure across ~1,400 names accrues meaningful financing and stock
loan costs that a flat 10 bp round trip does not capture.

## 4.1 Implementation verification (run in-session)

The reference pipeline in `source_or_pseudo_code.txt` was executed end-to-end on synthetic data with
a known ground truth: 60 stocks driven by 2 common factors plus stock-specific Ornstein–Uhlenbeck
residuals with a true `κ = 12.0`.

| Check | Result |
|---|---|
| PCA eigenportfolio extraction | 3 factors; first component explains **95.7%** of variance (the "market" eigenvector, as the paper describes) |
| Stocks passing the `κ > 8.4` filter | **59 / 60** |
| Median fitted half-life | 5.2 days |
| s-score range | −2.09 to +1.81 |
| Signals generated at 1.25 thresholds | 7 long, 6 short, 46 flat |
| Threshold logic asserted against s-scores | **Verified** |

Two findings from this exercise are recorded as replication warnings rather than smoothed over:

**1. The OU time step is a trap.** `κ` must be estimated with `dt = 1/252` (one trading day), not
the 60-day window length. Getting this wrong scales `κ` down by the number of observations — the
first run of this test returned `κ ≈ 0.2` against a true 12.0 and **zero stocks passed the filter**.
A replicator hitting "no trades ever fire" should check this first. The code and pseudo-code now
state it explicitly.

**2. `κ` is biased upward on a 60-day window.** With a true `κ` of 12.0, the estimator returned a
median of **33.8** — a large upward bias, from two compounding sources: AR(1) slope coefficients are
biased toward zero in short samples, which biases `−ln(b)` upward, and regressing out the factors
removes some genuine persistence before the OU fit sees the residual.

> The practical consequence is that **the `κ > 8.4` filter binds more loosely than it appears**. It
> admits residuals whose *true* mean-reversion is slower than the intended 30-day cutoff. Since this
> filter is the method's key improvement over the parent distance approach, anyone implementing it
> should either bias-correct the AR(1) slope or check fitted half-lives against realised holding
> times and tighten the threshold until they agree. This is a caveat on the *method as commonly
> implemented*, not a claimed error in the paper — the paper's own estimation appendix was not
> examined at this level of detail.

## 5. The August 2007 quant crisis

The paper devotes explicit attention to "the liquidity crisis of the summer of 2007" and reports
results **consistent with Khandani & Lo (2007)**, validating their **"unwinding" theory** of the
quant fund drawdown.

The mechanism is essential context for anyone running this strategy:

- Many market-neutral equity books held **highly correlated residual positions** — a natural
  consequence of everyone regressing similar universes on similar factors and trading the leftovers.
- One or more large participants deleveraged, likely for reasons unrelated to the equity book
  (subprime losses elsewhere forcing liquidation of what could be sold).
- The forced selling moved residual spreads against **everyone holding the same positions**,
  triggering further deleveraging.
- Losses were severe and then substantially reversed within days — the signature of a liquidity
  event rather than an information event.

> **Market-neutral is not crowding-neutral.** A book with zero market beta can still be almost
> perfectly correlated with every competitor's book. This is the dominant tail risk of the strategy
> class and it is invisible in any backtest that does not model competitor positioning.

## 6. Where the strategy thrives vs. fails

**Thrives when:**
- Residuals mean-revert quickly. The **κ > 8.4** filter is the operative constraint: only fast-
  reverting names are traded, and this is what separates the method from the parent distance
  approach.
- The factor model genuinely captures systematic risk, leaving a clean idiosyncratic residual.
- Dislocations are liquidity-driven and transient — the classic case for a liquidity provider.
- The stock universe is broad, so many weakly correlated small bets diversify into a low-volatility
  aggregate. The paper's framing: "make many bets with positive expected returns, taking advantage
  of diversification across stocks."
- Volume information is incorporated. The 1.51 Sharpe for ETF+volume in the difficult 2003–2007
  window is the strongest single result in the study.

**Fails when:**
- **Crowded books deleverage simultaneously** — August 2007. The defining risk.
- The factor structure shifts abruptly, so residuals estimated on a 252-day correlation matrix are
  mismeasured and yesterday's "mispricing" is today's genuine factor exposure.
- A residual divergence is fundamental rather than transient. As with all convergence strategies,
  the model cannot distinguish a dislocation from news.
- Costs rise or borrow tightens. Daily rebalancing across a large universe is cost-sensitive by
  construction; the 10 bp assumption is generous for anything but large caps.
- Estimation windows are misspecified for the prevailing regime — 60 days is a bet that parameters
  are locally constant.

## 7. Decay and current status

**`decay_status: substantially-decayed`.**

- **The decay is documented within the paper's own sample.** PCA Sharpe 1.44 (1997–2007) → 0.90
  (2003–2007); ETF signals degrade similarly after 2002. The authors state performance was "much
  stronger prior to 2003" in the abstract itself.
- **The obvious causes are structural and permanent.** Decimalisation, electronic execution, the
  proliferation of statistical arbitrage capital, and the commoditisation of exactly this technique
  (PCA on returns, OU on residuals, s-score thresholds — all now textbook) compressed the residual
  dislocations the strategy feeds on.
- **The 2007 crowding event is evidence the trade was already crowded** at the end of the sample.
  That crowding has not diminished.
- **But the framework has not decayed — only this parameterisation of it.** Factor-residual
  decomposition remains the correct skeleton for equity market-neutral trading. What has moved on is
  the factor set (richer than PCA-on-correlations), the residual model (richer than a single OU
  process), the signal timing (volume time, and beyond it order-flow-informed timing), and the
  horizon.
- **The volume-time result points to where the remaining edge lives.** ETF+volume improved *in the
  harder period* — the one signal enhancement in the paper that fought the decay rather than
  succumbing to it.

**How to use this entry.** As the modern, correctly-specified replacement for the parent
distance-method entry — and as the concrete implementation of the half-life filter that entry
identifies as the distance method's key missing ingredient. Treat the specific cutoffs (1.25 /
0.75 / 0.50) and windows (60 / 252) as the paper's fitted values on 1997–2007 data, not as
constants. Benchmark any modern equity market-neutral system against this construction before
adding complexity, and model crowding explicitly — the backtest will never show it.
