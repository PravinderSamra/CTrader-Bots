# Backtest & Data Summary — Variance Risk Premium Harvesting

## Verification

Figures below were read directly from the full text of Carr, P., & Wu, L., "Variance Risk Premia,"
**working-paper draft dated May 27, 2004**, retrieved in-session from
`engineering.nyu.edu/sites/default/files/2019-01/CarrReviewofFinStudiesMarch2009-a.pdf`. The final
published version is *Review of Financial Studies* 22(3), 1311–1341 (2009), which is paywalled and
was **not** consulted.

**Evidence grade: `verified-primary`** for the working paper; figures should be re-checked against
the published article before being cited as "Carr & Wu (2009)." Section and table references are to
the working paper.

---

## 1. Data sample

| Field | Value |
|---|---|
| Data source | OptionMetrics (acknowledged in the paper) |
| Sample period | **January 1996 – February 2003** |
| Underlyings | **5 stock indexes + 35 individual stocks** (40 series total) |
| Indices covered | S&P 500 (SPX), S&P 100 (OEX), Dow Jones Industrial Average, Nasdaq-100, QQQ |
| Instruments | Listed equity and index options; synthetic variance swap rates constructed from them |
| Horizon | Monthly (30-day) variance swap rates and matched realised variance |
| Standard errors | Newey–West, 30-day lag (overlapping daily observations) |

## 2. Headline results

### 2.1 The premium exists and is large on indices

| Quantity | Definition | Finding |
|---|---|---|
| `RP` | `100 × (RV − SW)` | Mean **negative** for all stock indexes and most individual stocks |
| `LRP` | `ln(RV / SW)` | Mean **negative**; the continuously compounded excess return to a long-variance position |

**The headline number:** the mean log variance risk premium is **over −50% per month** for the two
S&P indexes (SPX, OEX) and for the Dow Jones. A long variance swap position on the major US indices
lost, on average, more than half its value per month over 1996–2003. The short side collected it.

| Group | Statistical significance |
|---|---|
| S&P 500, S&P 100, Dow Jones | **Strongly significant** for both `RP` and `LRP` — the largest t-statistics in the study |
| Nasdaq-100 and QQQ | `RP` **not** significant; `LRP` significant |
| 35 individual stocks | `LRP` significantly negative for **21 of 35**; `RP` insignificant for **all but 3 of 35** |

### 2.2 The premium is a market-variance phenomenon

Regressing each underlying's log premium on its variance beta
`β^V_j = Cov(RV_j, RV_SPX) / Var(RV_SPX)`:

```
LRP_j = 0.0201 + 0.2675 · β^V_j          R² = 15.9%
```

Carr and Wu's conclusion: the market "does not price all return variance variation in each single
stock, but only prices the variance risk in the stock market portfolio."

**This is the single most actionable finding in the paper.** Selling single-name variance is not a
diversified version of selling index variance — on most individual names the premium is not
reliably there at all.

### 2.3 Standard risk factors do not explain it

- **CAPM:** cannot explain the strongly negative premia. The leverage effect makes long variance
  qualitatively attractive as insurance, but does not quantitatively account for the magnitude.
- **Fama–French factors:** "can only [explain a small part of] the average variance risk premia";
  the paper concludes the FF factors "cannot account for the strongly negative variance risk
  premia."

### 2.4 Information ratios — and the authors' own warning

Going short variance swaps on the S&P and Dow indices produces **raw information ratios over 3.0**
(mean excess log return / standard deviation, annualised by √12). After Newey–West serial-dependence
adjustment, the ratios remain "higher than an average stock portfolio investment."

> ⚠️ **Do not use these numbers to size a position.** The authors themselves attach the caveat:
> *"given the nonlinear payoff structure, caution should be applied when interpreting Sharpe ratios
> on derivative trading strategies"* (citing Goetzmann, Ingersoll, Spiegel & Welch, 2002). A short
> variance position is precisely the payoff shape that inflates a Sharpe ratio while hiding
> ruin risk. An information ratio above 3 on a short-convexity strategy is a warning, not a
> selling point.

## 2.5 Implementation verification (run in-session)

The model-free replication in `source_or_pseudo_code.txt` was tested against a case with a known
answer: under Black–Scholes with constant volatility σ, the variance swap rate must equal σ².

| Test | Result |
|---|---|
| True variance (σ = 20%, τ = 30/365) | 0.040000 |
| Replicated swap rate (strikes 20–300, step 0.25) | **0.040013** |
| Relative error | **0.03%** |

The integral is correct. A second test quantifies the truncation problem flagged in §4 of the
research file — real option chains do not extend to infinity:

| Strike range | Understates true variance by |
|---|---|
| 60–160 (±60%) | 0.03% |
| 80–125 (±25%) | 0.03% |
| 90–112 (±12%) | **1.43%** |

Note the direction of the bias, which matters for anyone measuring the premium: a truncated chain
produces a **too-low** swap rate, which makes `RV − SW` look **less negative** than it truly is. A
narrow strike range therefore *understates* the variance risk premium — it does not inflate it. Any
replication using a thin option chain is measuring a conservative version of the effect.

## 3. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Maximum drawdown | **NOT REPORTED IN SOURCE** |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Win rate | **NOT REPORTED IN SOURCE** — though the strategy's character implies a high one |
| Profit factor | **NOT REPORTED IN SOURCE** |
| Transaction costs / bid-ask on the option strip | Not modelled |
| Margin and funding requirements | Not modelled |

The paper is a **measurement study**, not a strategy backtest. It establishes that the premium
exists, how large it is, where it lives, and that standard factors do not explain it. It does not
claim to be an implementable trading system, and the missing metrics are the ones that decide
whether harvesting it survives contact with a margin clerk.

## 4. Where the strategy thrives vs. fails

**Thrives when:**
- Realised volatility is stable or falling and the implied-realised gap is wide.
- On **broad market indices** — SPX, OEX, DJIA — where the premium is measured to be largest and
  most significant.
- Volatility is elevated but not exploding: the premium tends to be richest after a shock has
  already repriced implieds upward.
- Position sizing is small relative to capital and the operator can survive a multi-sigma variance
  spike without being forced out.

**Fails when:**
- **A volatility spike arrives.** This is not a tail scenario to be hedged around; it is the
  strategy's defining risk. Realised variance is unbounded above.
- **Positions are levered.** The strategy's smooth, high-Sharpe return stream invites leverage, and
  leverage is what converts a drawdown into a termination event. The 5 February 2018 collapse of
  inverse-volatility ETPs — outside this paper's sample — is the canonical demonstration.
- **Applied to single stocks indiscriminately.** Per §2.2, the premium is not reliably present on
  individual names. Idiosyncratic variance risk appears to be largely unpriced.
- **Funding is procyclical.** Margin requirements rise exactly when the position is losing, forcing
  liquidation at the worst prices.
- **Jumps dominate.** The replication argument assumes continuous paths; gap moves break it in the
  unfavourable direction.

## 5. Decay and current status

**`decay_status: partially-decayed`.**

- **The premium is structural and has persisted.** It is compensation for bearing a genuinely
  undesirable risk — volatility spikes coincide with wealth destruction — so it does not get
  arbitraged away the way a pricing inefficiency does. Someone must underwrite the insurance, and
  they must be paid to do it. The mechanism identified in 1996–2003 has no reason to disappear.
- **But the harvest has been substantially competed down.** The premium became one of the most
  widely known and most heavily traded effects in the market after this literature. The growth of
  systematic option-selling funds, volatility-targeting strategies, and retail-accessible ETPs
  compressed the spread, and the crowding created its own reflexive risk: 5 February 2018 saw
  inverse-volatility ETPs lose the large majority of their value in one session, with the
  liquidation of those products itself amplifying the move.
- **The measurement method has not decayed at all.** The model-free replication in §3.1 of the
  research file is the basis of the VIX and remains the correct way to compute the premium. That
  part of the paper is infrastructure, not alpha.

**How to use this entry.** As the rigorous, model-free definition of what the variance risk premium
*is*, where it lives (indices, not single names), and how large it was before the trade became
crowded. Treat the reported information ratios as a case study in why Sharpe ratios mislead on
short-convexity payoffs. Any live harvesting programme needs an explicit tail-risk budget and a
hard answer to "what happens at a 4× variance spike" before position sizing is even discussed.
Dispersion trading (short index variance / long single-stock variance), which the variance-beta
result motivates directly, is queued for Wave 3.
