# Backtest & Data Summary — Optimal Execution (Almgren–Chriss)

## Verification

All figures below were read directly from Almgren, R., & Chriss, N., "Optimal Execution of Portfolio
Transactions," **December 2000 draft**, retrieved in-session from
`smallake.kr/wp-content/uploads/2016/03/optliq.pdf`. Published in *Journal of Risk* 3(2), 5–39
(2000). Table references are to that draft. **Evidence grade: `verified-primary`.**

> **This is a theoretical paper with a worked numerical example — there is no historical backtest.**
> It derives an optimal trading trajectory and illustrates it on a calibrated test case. There are no
> Sharpe ratios or P&L statistics because the paper is about **minimising a cost**, not generating a
> return. Evaluating it means checking the mathematics and the calibration logic, which this entry
> does.

---

## 1. The worked example (Table 1)

The paper's calibrated test case, and the most useful part of it for practitioners — because it shows
**how to derive the impact parameters from observable market quantities**.

### Market assumptions

| Quantity | Value |
|---|---|
| Initial stock price `S₀` | **$50/share** |
| Initial holdings `X` | **10⁶ shares** ($50M position) |
| Annual volatility | **30%** |
| Annual expected return | 10% |
| Bid-ask spread | **1/8** ($0.125) |
| Median daily volume | **5 million shares** |
| Liquidation time `T` | **5 days** |
| Number of periods `N` | 5 (daily trades, `τ` = 1 day) |

### Derived parameters

| Parameter | Derivation | Value |
|---|---|---|
| Daily volatility | `0.3/√250 = 0.019`, scaled by price | `σ = 0.95` ($/share)/day^½ |
| Daily drift | `0.1/250 = 4×10⁻⁴`, scaled by price | `α = 0.02` ($/share)/day |
| Fixed temporary cost | **half the bid-ask spread** | `ε = 0.0625` $/share |
| Temporary impact | *"for each one percent of daily volume we trade, we incur a price impact equal to the bid-ask spread"* → `(1/8)/(0.01 × 5×10⁶)` | `η = 2.5×10⁻⁶` |
| Permanent impact | *"price effects become significant when we sell 10% of daily volume"*, taken as one spread → `(1/8)/(0.1 × 5×10⁶)` | `γ = 2.5×10⁻⁷` |
| Risk aversion | chosen; interpretable as "static holdings 11,000 shares" | `λ_u = 10⁻⁶` /$ |
| VaR confidence | 95% | `λ_v = 1.645` |

> **The two rules of thumb in that table are worth extracting on their own**, because they are how
> practitioners actually calibrate impact when they lack fill data:
> - **Trading 1% of daily volume costs about one bid-ask spread** (temporary).
> - **Price effects become significant at about 10% of daily volume** (permanent).
>
> Note `γ` comes out exactly **10× smaller** than `η` under these assumptions, i.e. temporary impact
> dominates at any given trading rate — which is why the optimisation is essentially a fight between
> temporary impact and volatility.

### Resulting trade characteristics

| Quantity | Value |
|---|---|
| `κ` | **≈ 0.6 / day** |
| `κT` | **≈ 3** |
| Half-life `θ = 1/κ` | ≈ 1.67 days |
| Holding the position untraded for 5 days | σ√T = **$2.12/share**, i.e. **$2.12M** standard deviation |

The authors note `κT ≈ 3` is "near one in magnitude" and therefore "an interesting intermediate in
between the naïve extremes" — neither pure VWAP nor immediate liquidation.

They also note the untraded-position risk of $2.12M is "precisely twice" the `√V` of the
linear-trajectory point, a useful sanity check for any replication.

## 2. The formulas to implement

```
κ  ≈  √( λσ² / η )                          urgency parameter
θ  =  1/κ                                    trade half-life

x_j = X · sinh( κ(T − t_j) ) / sinh( κT )    holdings trajectory
n_j = X · 2·sinh(½κτ)/sinh(κT) · cosh( κ(T − t_{j−½}) )    trade list
```

Expected cost and variance of the optimal strategy (eq. 20):

```
E(X) = ½γX² + εX + η̃X² · tanh(½κτ)·( τ·sinh(2κT) + 2T·sinh(κτ) ) / ( 2τ²·sinh²(κT) )

V(X) = ½σ²X² · ( τ·sinh(κT)·cosh(κ(T−τ)) − T·sinh(κτ) ) / ( sinh²(κT)·sinh(κτ) )
```

Note `½γX²` in the expected cost: the **permanent-impact term is independent of the trajectory**. It
cannot be optimised away, only avoided by not trading.

## 3. Independent verification (run in-session)

The formulas were implemented and evaluated at the paper's Table 1 parameters.

| Check | Paper | Computed | Status |
|---|---|---|---|
| `κ ≈ √(λσ²/η)` | ≈ 0.6/day | **0.6008** | ✅ |
| `κT` | ≈ 3 | **3.0042** | ✅ |
| Untraded 5-day risk `σ√T` | $2.12/share | **$2.1243** | ✅ |
| Untraded position risk | $2.12M | **$2.1243M** | ✅ |
| Untraded ÷ linear-trajectory `√V` | "precisely twice" | **2.0412** | ✅ |
| Permanent impact `½γX²` | trajectory-independent | **$125,000**, identical at every `κ` tested | ✅ |
| Trade list positivity `n_j > 0` | always, for `X > 0` | **holds** at every `κ` tested | ✅ |
| Calibration from observables → `ε`, `η`, `γ` | 0.0625, 2.5×10⁻⁶, 2.5×10⁻⁷ | **0.0625, 2.5×10⁻⁶, 2.5×10⁻⁷** | ✅ exact |
| Calibration → `σ` | 0.95 | **0.9487** (rounding in the paper) | ✅ |

Feeding only the *observable* inputs — spread 1/8, daily volume 5M shares, 30% annual volatility,
$50 price — into the calibration routine reproduces the paper's Table 1 impact parameters exactly.
That confirms the two rules of thumb are being applied as the authors intended, which matters because
those rules are what a practitioner without fill data actually uses.

Cost decomposition at these parameters (`λ = 10⁻⁶`):

| Component | Amount | Note |
|---|---|---|
| Permanent impact `½γX²` | $125,000 | trajectory-independent |
| Spread cost `εX` | $62,500 | |
| Temporary impact | $718,012 | the term the optimisation actually fights |
| **Total expected cost** | **$905,512** | ≈ 1.81% of the $50M position |
| Standard deviation | $608,198 | |
| **L-VaR (95%)** | **$1,905,998** | expected cost + 1.645σ |

Temporary impact is **5.7× the permanent impact** here, which is why the whole optimisation is
effectively a fight between temporary impact and volatility — permanent impact just sits there as a
fixed toll.

### The "precisely twice" claim is a discrete-time result, not a continuous one

Worth recording because it is easy to get backwards. At the paper's own discretisation (`N = 5`
daily steps) the ratio of untraded risk to linear-trajectory `√V` computes to **2.0412** — the
paper's claim holds. But it is **not** the continuous-time limit:

| `N` | Ratio |
|---|---|
| **5** (the paper's case) | **2.0412** |
| 50 | 1.7584 |
| 500 | 1.7347 |

As `N → ∞` the ratio converges to **√3 ≈ 1.7321**, since for a continuous linear liquidation
`V = σ²X²∫₀ᵀ(1−t/T)²dt = σ²X²T/3`. The factor of 2 is an artefact of five daily steps. A replication
using finer time steps will not reproduce it and should not conclude the paper is wrong.

### The trajectory at the paper's parameters

Shares remaining, `X = 10⁶`, `T = 5` days, `κ = 0.6008`:

| Day | 0 | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| **Optimal** `x_j` | 1,000,000 | **545,212** | 293,239 | 150,348 | 63,385 | 0 |
| Linear (VWAP) | 1,000,000 | 800,000 | 600,000 | 400,000 | 200,000 | 0 |

The optimal path is **substantially front-loaded** relative to VWAP — it sells **45.4%** of the
position on day one against VWAP's 20%, and is more than 85% done by day three. At `κT ≈ 3` the
volatility-risk term is already dominating the impact term, which is a more aggressive schedule than
the phrase "interesting intermediate" might suggest.

### The half-life diagnostic across urgency regimes

| `κ` (/day) | `θ = 1/κ` | `κT` | Regime | % sold on day 1 |
|---|---|---|---|---|
| 0.1 | 10.0 days | 0.5 | `T ≪ θ` — impact-dominated | **21.2%** |
| 0.6 | 1.67 days | 3.0 | intermediate (**the paper's case**) | **45.4%** |
| 2.0 | 0.50 days | 10.0 | `T ≫ θ` — risk-dominated | **86.5%** |
| 5.0 | 0.20 days | 25.0 | strongly risk-dominated | **99.3%** |

The regime classification in §3.4 of the research file reproduces cleanly at both ends: at `κ = 0.1`
the schedule is almost exactly the straight line (21.2% versus 20% for pure VWAP), and at `κ = 5` it
collapses to near-immediate liquidation (99.3% on day one). The half-life is therefore a genuine
diagnostic — knowing `θ` relative to `T` tells you which regime you are in before you choose an
algorithm.

## 4. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio | **NOT APPLICABLE** — this minimises a cost, it does not generate a return |
| Historical backtest | **NOT PERFORMED IN SOURCE** |
| Realised vs. predicted impact on live orders | **NOT TESTED IN SOURCE** |
| Empirical calibration of `γ` and `η` from fill data | **NOT PERFORMED** — the example uses rules of thumb, not estimates |
| Comparison against VWAP/TWAP on real orders | **NOT PERFORMED** |

The absent empirical calibration is the significant gap. The paper supplies a framework and two
plausible rules of thumb; it does not estimate impact parameters from data. Anyone implementing this
must calibrate `η` and `γ` on their own fills, and should expect them to vary by instrument, size,
and regime.

## 5. Where the framework applies vs. fails

**Applies when:**
- The order is **large relative to daily volume** — otherwise impact is negligible and any
  trajectory works.
- There is a genuine deadline or risk budget, so the impact-versus-risk trade-off is real.
- Price dynamics are approximately driftless over the execution horizon. With a strong directional
  view, the trajectory should tilt, and the paper's Section 4 covers this.
- Impact parameters can be calibrated, even roughly. The two rules of thumb are a defensible
  starting point.
- You want a **diagnostic** rather than a full algorithm: computing `θ` and comparing it to your
  deadline is valuable even if you execute by other means.

**Fails or needs care when:**
- **Impact is materially non-linear.** The linear form is the paper's known weakness; use Almgren
  (2003) for power-law impact.
- Liquidity or volatility shifts intraday — constant `σ`, `η`, `γ` are assumed.
- The execution should be **adaptive**. The static trajectory does not respond to fills or price
  moves.
- Passive execution matters. There are no limit orders, no venue routing, no queue position — most of
  a modern algorithm's machinery is outside this model.
- The order is small enough that spread and fees, not impact, dominate. Then `ε` is the whole cost
  and the optimisation is moot.

## 6. Decay and current status

**`decay_status: intact`.**

This is a framework, not an edge, so there is nothing to be arbitraged away. Its influence is
visible in the fact that **implementation shortfall** is now the standard execution benchmark and
that essentially every institutional execution algorithm is a descendant of, or a reaction to, this
formulation.

What has moved on:

- **The impact functional form.** Linear temporary impact is superseded in practice by square-root
  and other power laws — and even that is contested, since Cont, Kukanov & Stoikov argue square-root
  impact is an aggregation artefact of an underlying linear order-flow relation. The *framework*
  survives all of this; only the choice of `h(v)` changes.
- **Static → adaptive.** Modern algorithms re-optimise continuously against realised fills and
  live liquidity signals. The Almgren–Chriss trajectory is now typically the *baseline schedule* an
  adaptive algorithm deviates from, rather than the schedule itself.
- **The passive/aggressive decision** has become the dominant practical question, and it lives
  entirely outside this model. See
  `../../market-making-microstructure/guilbaud-pham-limit-and-market-orders/` for the limit-versus-
  market-order treatment.

**How to use this entry.** As the cost layer the rest of the library depends on. Concretely: before
believing any strategy entry's reported returns, compute the execution cost its turnover implies
using the two rules of thumb in §1, and check whether the edge survives. That test is what separates
the entries here that are implementable from the ones that are historically interesting. The
half-life `θ` is the single most portable idea — compute it, compare it to your deadline, and let it
tell you whether you are impact-constrained or risk-constrained before choosing any algorithm.
