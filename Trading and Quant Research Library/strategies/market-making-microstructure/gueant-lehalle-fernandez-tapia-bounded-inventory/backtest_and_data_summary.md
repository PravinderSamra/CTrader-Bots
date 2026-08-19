# Backtest & Data Summary — Bounded-Inventory Market Making

## Verification

Figures and formulas below were read directly from Guéant, O., Lehalle, C.-A., &
Fernandez-Tapia, J., "Dealing with the Inventory Risk: A solution to the market making problem,"
**arXiv:1105.3115v5, draft dated July 2012**, retrieved in-session from `arxiv.org/pdf/1105.3115`.
Published as *Mathematics and Financial Economics* 7(4), 477–507; the published version was not
consulted. **Evidence grade: `verified-primary`** for the arXiv draft.

> **This is a theoretical paper, not an empirical study.** There is no historical backtest, no
> market data, and consequently no Sharpe ratio, drawdown, or win rate. What it delivers is an
> *exact* solution to a stochastic control problem plus closed-form approximations, illustrated with
> numerical figures. The correct way to evaluate it is to check the mathematics and the limiting
> behaviour — which this entry does — not to look for performance statistics that do not exist.

---

## 1. What the paper actually provides

| Deliverable | Status |
|---|---|
| Exact solution under inventory constraints `q ∈ {−Q,…,Q}` | **Yes** — via a linear ODE system |
| Removal of the need for PDE numerics | **Yes** — "numerical approximation of partial differential equations is now unnecessary" |
| Asymptotic (`T → ∞`) optimal quotes | **Yes** — Theorem 2, via the eigenvector for the smallest eigenvalue of `M` |
| Closed-form approximation to those asymptotics | **Yes** — Proposition 3, Gaussian `f⁰` |
| Numerical illustration of quote behaviour vs. `q`, `k`, `γ`, `σ` | **Yes** — Figures 4–8 |
| Historical backtest on market data | **NO** |
| Sharpe ratio / drawdown / win rate / P&L distribution | **NOT REPORTED IN SOURCE** |
| Calibration of `A` and `k` from real fill data | **NOT PERFORMED IN SOURCE** |

## 2. The parameter reduction

The whole problem collapses to two effective parameters:

| Parameter | Definition | Meaning |
|---|---|---|
| `α` | `(k/2)·γ·σ²` | Cost of carrying inventory risk |
| `η` | `A·(1 + γ/k)^{−(1+k/γ)}` | Value of capturing order flow |

The ratio `√(α/η)` is the single number governing how aggressively quotes skew with inventory. This
is the most useful practical takeaway in the paper: **tune `√(α/η)`, not four parameters
independently.**

## 3. The formulas to implement

```
Half-spread base term    (1/γ)·ln(1 + γ/k)                        [per side]
Inventory skew unit      √( (σ²γ)/(2kA) · (1 + γ/k)^{1+k/γ} )     [= (1/k)·√(α/η)]

δ^b*_∞(q) ≈ base + ((2q+1)/2) · skew_unit
δ^a*_∞(q) ≈ base − ((2q−1)/2) · skew_unit
ψ*_∞(q)   ≈ 2·base + skew_unit
```

### Structural properties (verified numerically in §5)

| Property | Behaviour |
|---|---|
| Spread vs. inventory | **Independent of `q`** in the closed-form approximation; very slightly decreasing in `|q|` in the exact solution (see §5) |
| Quote centre vs. inventory | Shifts linearly; long inventory pushes both quotes down |
| Time dependence | **None** — these are stationary, unlike A–S's `(T−t)` terms |
| Base term vs. A–S | Identical: `(1/γ)ln(1+γ/k)` per side |

## 4. Comparison with the parent model

| | Avellaneda–Stoikov (2008) | Guéant–Lehalle–Fernandez-Tapia |
|---|---|---|
| Inventory | Unbounded | **Bounded `q ∈ {−Q,…,Q}`** |
| Solution method | Asymptotic expansion in `q` | **Exact, via linear ODE system** |
| Numerics required | PDE / expansion | **Matrix exponential** |
| Spread inventory term | `γσ²(T−t)` — **decays to zero at `T`** | `√(α/η)/k` — **stationary** |
| Reservation-price shift | `−q·γσ²(T−t)` — decays to zero | Linear in `q`, stationary |
| Behaviour at session end | Spread collapses, skew vanishes | Well-behaved |
| Adverse selection | None | **None** |

## 5. Structural verification (run in-session)

The closed-form approximations of Proposition 3 were implemented and evaluated to confirm the
properties the paper asserts. Parameters: `σ = 0.3, γ = 0.05, k = 1.5, A = 0.9`.

| Derived quantity | Value |
|---|---|
| Base half-spread `(1/γ)·ln(1+γ/k)` | 0.6558 |
| Skew unit `√(σ²γ/(2kA)·(1+γ/k)^{1+k/γ})` | 0.0679 |
| Independent cross-check `√(α/η)/k` with `α = 0.003375`, `η = 0.325678` | **0.0679** ✓ |

| Inventory `q` | Bid distance `δ^b` | Ask distance `δ^a` | Spread `ψ` |
|---|---|---|---|
| −3 | 0.4861 | 0.8933 | 1.3795 |
| −2 | 0.5540 | 0.8255 | 1.3795 |
| −1 | 0.6219 | 0.7576 | 1.3795 |
| **0** | **0.6897** | **0.6897** | **1.3795** |
| +1 | 0.7576 | 0.6219 | 1.3795 |
| +2 | 0.8255 | 0.5540 | 1.3795 |
| +3 | 0.8933 | 0.4861 | 1.3795 |

Confirmed properties:

- **The spread is constant at 1.3795 for every inventory level** — across `q ∈ [−5, 5]` the
  computation returns exactly one distinct spread value. Inventory moves the quote *centre*, never
  the *width*, precisely as the formula predicts and matching the parent model's structural result.
- **Long inventory pushes the market maker to sell.** At `q = +3` the bid sits 0.8933 from the mid
  (far away, unlikely to buy more) while the ask sits 0.4861 (close, likely to sell). At `q = −3`
  the reverse. This is the inventory-management mechanism working with no explicit flattening logic.
- **Perfect antisymmetry**, asserted programmatically: `δ^b(q) = δ^a(−q)` for all `q` tested.
- **Skew is linear in `q`**, stepping by 0.0679 per unit of inventory — equal to the independently
  computed `√(α/η)/k`, which confirms the algebra connecting Proposition 3 to the `α`/`η`
  parameterisation.
- **No time dependence.** Evaluating at any `t` returns identical quotes, unlike the parent model
  whose skew and inventory-risk spread both decay to zero as `t → T`.

### The cleanest cross-model check

Avellaneda–Stoikov's order-arrival spread term is `(2/γ)·ln(1+γ/k)`. At these parameters that
evaluates to **1.3116**, and GLFT's `2 × base` evaluates to **1.3116** — identical. The two models
agree exactly on the liquidity component of the spread, and differ only in the inventory term
(A–S: `γσ²(T−t)`, decaying; GLFT: `√(α/η)/k = 0.0679`, stationary). That is a satisfying confirmation
that GLFT is a strict generalisation rather than a different model.

### Exact solution vs. closed form (Theorem 2 vs. Proposition 3)

The exact asymptotic quotes were also computed from the eigenvector of the smallest eigenvalue of
`M` (`Q = 10`) and compared against the closed-form approximation:

| `q` | Exact `δ^b` | Approx `δ^b` | Difference | Exact spread | Approx spread |
|---|---|---|---|---|---|
| −3 | 0.4833 | 0.4861 | −0.0029 | 1.3799 | 1.3795 |
| −1 | 0.6212 | 0.6219 | −0.0007 | 1.3807 | 1.3795 |
| 0 | 0.6904 | 0.6897 | +0.0007 | **1.3808** | 1.3795 |
| +1 | 0.7595 | 0.7576 | +0.0019 | 1.3807 | 1.3795 |
| +3 | 0.8967 | 0.8933 | +0.0033 | 1.3799 | 1.3795 |

**The approximation is good** — the largest quote discrepancy is 0.0033, roughly 0.5% of the quote
distance, and the error grows with `|q|` as expected from a Gaussian approximation to a discrete
eigenproblem.

> **But note what the comparison exposes.** The exact spread is **not** constant in `q`: it peaks at
> 1.3808 when flat and falls to 1.3799 at `q = ±3`. The perfectly flat spread is an artefact of the
> **closed-form approximation**, not a property of the exact solution. The true optimal policy
> tightens the spread very slightly as inventory grows — economically sensible, since a market maker
> holding risk has more reason to trade out of it. The effect is small (under 0.1% here) and the
> approximation is entirely usable, but "the spread does not depend on inventory" should be stated
> as a property of the *approximation*, which is how this entry now words it.

This validates the implementation against the paper's stated structure. It does **not** validate the
model against markets — no such test is possible without fill data.

## 6. Where the model thrives vs. fails

**Thrives when:**
- The market maker operates **continuously**, with no genuine terminal liquidation time. This is the
  model's key advantage over the parent and the reason to prefer it in production.
- Inventory limits are a **binding operational reality** — capital, margin, or risk limits — rather
  than a theoretical nicety.
- `σ`, `A`, `k` are stable enough to be estimated and are re-estimated often.
- Order flow is genuinely two-sided and largely uninformed.
- Ticks are small relative to volatility, so continuous quoting is a fair approximation.

**Fails when:**
- **Informed flow dominates.** No adverse-selection term exists. This remains the primary way live
  implementations lose money, and it is not a small correction.
- The price jumps. Brownian dynamics have no gap risk.
- Queue position determines fills — tight-tick, deep-book markets. See Guilbaud & Pham.
- `A` and `k` shift regime faster than they can be re-estimated. Both are volatile in practice, and
  a stale `k` mis-sizes the base spread directly.
- `Q` is set without reference to actual funding. The model optimises *given* `Q`; choosing `Q`
  badly is outside its scope.

## 7. Decay and current status

**`decay_status: intact`.**

As with the parent entry, this is a **model**, not an empirical anomaly, so it cannot decay the way a
measured premium does. The mathematics remains correct under its assumptions, and the linear-ODE
reduction is a permanent contribution — it is the standard reference for solving the constrained
market-making problem and the basis of much of the subsequent literature.

What has changed is the competitive context. In institutional equity and futures markets, market
making is decided by latency, queue position, and short-horizon adverse-selection prediction — none
of which this framework models. Its value today is as the **correct inventory-management skeleton**,
particularly in markets where the assumptions fit best (crypto perpetuals, less latency-sensitive
venues), with the adverse-selection layer supplied separately.

**How to use this entry.** Prefer these formulas over vanilla Avellaneda–Stoikov for any
continuously operating quoter: the stationary asymptotics remove the terminal-time pathology, and
the inventory bound is built into the optimisation rather than bolted on afterwards. Then treat the
result as a *baseline* to which an adverse-selection signal must be added — see
`../order-flow-imbalance-price-impact/`, which supplies exactly that measurement, and
`../guilbaud-pham-limit-and-market-orders/`, which adds execution priority and market orders.
