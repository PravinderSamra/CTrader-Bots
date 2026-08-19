# Bounded-Inventory Market Making (Guéant–Lehalle–Fernandez-Tapia)

**Category:** Market Making & Order-Flow Microstructure (Wave 2 depth entry)
**Anchor paper:** Guéant, O., Lehalle, C.-A., & Fernandez-Tapia, J. (2013). "Dealing with the
inventory risk: a solution to the market making problem." *Mathematics and Financial Economics*,
7(4), 477–507. arXiv:1105.3115 (draft consulted: July 2012, v5).
**Parent entry:** `../avellaneda-stoikov-optimal-quoting/`

---

## 1. Abstract / summary of the core edge

Avellaneda–Stoikov gives the right *shape* of the market-making solution but leaves two problems
unsolved: the inventory is unbounded, and the closed form is an asymptotic approximation obtained
by expanding in the inventory variable.

This paper solves both. The authors take the same stochastic control problem — Brownian reference
price, exponentially decaying order arrival intensities, exponential utility over a finite horizon —
and add a **hard inventory constraint** `q ∈ {−Q, …, Q}`. Their central technical result is that
under these assumptions the Hamilton–Jacobi–Bellman equation, which is nonlinear, **transforms into
a system of linear ordinary differential equations**.

That is the whole contribution, and it is a large one. In their words:

> "We show that the Hamilton-Jacobi-Bellman equations associated to the stochastic optimal control
> problem can be transformed into a system of linear ordinary differential equations and we solve
> the market making problem under inventory constraints."

The practical consequences:

1. **No PDE solver needed.** A linear ODE system with constant coefficients is solved by a matrix
   exponential. The authors note explicitly that "numerical approximation of partial differential
   equations is now unnecessary."
2. **Inventory limits are built in, not bolted on.** The quotes are optimal *given* that the market
   maker will never exceed `±Q`. Compare the parent entry, where a position cap has to be imposed
   externally and the quotes are then no longer optimal.
3. **Genuine closed-form asymptotics.** Using a spectral characterisation, they derive closed-form
   approximations to the optimal quotes that hold as `T → ∞`, removing the terminal-time problem
   that makes vanilla Avellaneda–Stoikov misbehave at a session boundary.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Guéant, Lehalle & Fernandez-Tapia — arXiv:1105.3115 (verified in-session, v5 July 2012) | paper | https://arxiv.org/pdf/1105.3115 |
| arXiv abstract page | paper | https://arxiv.org/abs/1105.3115 |
| Published: *Mathematics and Financial Economics* 7(4), 477–507 | paper | https://link.springer.com/article/10.1007/s11579-012-0087-0 |
| Avellaneda & Stoikov (2008) — the parent model | paper | https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf |
| Ho & Stoll (1981) — the original inventory-risk formulation | paper | https://www.sciencedirect.com/science/article/abs/pii/0304405X81900201 |

## 3. Mathematical foundation

### 3.1 Setup — same as Avellaneda–Stoikov, plus a constraint

- Reference price: `dS_t = σ dW_t`
- Order arrival intensity at quote distance `δ`: `λ(δ) = A · exp(−k·δ)`
- Objective: maximise expected exponential (CARA) utility of P&L over `[0, T]`, risk aversion `γ`
- **New: inventory is constrained to `q ∈ {−Q, …, Q}`** — a set of `2Q+1` states

### 3.2 The linearisation

Under exponential utility with these dynamics, the value function factorises so that the HJB system
reduces to a **linear ODE system in `2Q+1` unknowns**, driven by a tridiagonal matrix `M` built from
two parameters:

```
α = (k/2) · γ · σ²          the inventory-risk term
η = A · (1 + γ/k)^{−(1+k/γ)}   the order-arrival term
```

Everything downstream — the optimal quotes, the asymptotic limits, the closed-form approximations —
is expressed through `α` and `η`. This is worth internalising: the entire market-making problem
under these assumptions collapses to **two effective parameters**, one measuring the cost of holding
risk and one measuring the value of capturing flow.

### 3.3 The asymptotic optimal quotes (Theorem 2)

As `T → ∞`, the optimal quotes converge to limits expressible through `f⁰`, the eigenvector
associated with the **smallest eigenvalue** of `M`:

```
δ^b*_∞(q) = (1/γ)·ln(1 + γ/k) + (1/k)·ln( f⁰_q / f⁰_{q+1} )
δ^a*_∞(q) = (1/γ)·ln(1 + γ/k) + (1/k)·ln( f⁰_q / f⁰_{q−1} )
```

and the resulting asymptotic bid-ask spread:

```
ψ*_∞(q) = −(1/k)·ln( f⁰_{q+1}·f⁰_{q−1} / (f⁰_q)² ) + (2/γ)·ln(1 + γ/k)
```

The eigenvector `f⁰` is characterised as the minimiser of a discrete quadratic form trading off
`α·q²` (inventory penalty) against `η·(f_{q+1} − f_q)²` (flow value).

### 3.4 The closed-form approximation (Proposition 3)

Replacing the discrete eigenvalue problem with its continuous `L²(ℝ)` analogue gives a Gaussian
solution, `f̃⁰(x) ∝ exp(−½·√(α/η)·x²)`, and hence `f⁰_q ≈ exp(−½·√(α/η)·q²)`. Substituting yields the
formulas a practitioner actually implements:

```
δ^b*_∞(q) ≈ (1/γ)·ln(1 + γ/k) + ( (2q+1) / 2 )·√( (σ²γ)/(2kA) · (1 + γ/k)^{1+k/γ} )

δ^a*_∞(q) ≈ (1/γ)·ln(1 + γ/k) − ( (2q−1) / 2 )·√( (σ²γ)/(2kA) · (1 + γ/k)^{1+k/γ} )

ψ*_∞(q)   ≈ (2/γ)·ln(1 + γ/k) +           √( (σ²γ)/(2kA) · (1 + γ/k)^{1+k/γ} )
```

Three things to notice:

1. **The first term is exactly Avellaneda–Stoikov's order-arrival term.** `(1/γ)ln(1+γ/k)` per side
   is half of A–S's `(2/γ)ln(1+γ/k)` total. The models agree on the liquidity component.
2. **The inventory adjustment is linear in `q`**, entering the bid with `+(2q+1)/2` and the ask with
   `−(2q−1)/2`. Long inventory pushes *both* quotes down, exactly as in the parent model — but here
   the coefficient is derived rather than approximated, and it does **not** decay to zero as time
   passes.
3. **The asymptotic spread is independent of `q`.** Inventory shifts the centre of the quotes, not
   their width — the same structural separation A–S found, now confirmed in the bounded, exact
   solution.

### 3.5 Why this is the better production baseline

The parent model's inventory term is `γσ²(T−t)`, which vanishes as `t → T`. That is correct for an
agent with a genuine terminal liquidation date, and actively dangerous for a continuously operating
market maker: the skew and the risk premium both evaporate at exactly the wrong moment. The
asymptotic formulas above have **no `(T−t)` dependence at all**. They are the stationary solution,
which is what a continuously operating desk actually wants.

## 4. Known criticisms and limitations

1. **Still no adverse selection.** The same blind spot as the parent model: order arrivals are
   exogenous and uninformative. A fill carries no signal about future price direction. This remains
   the dominant real-world loss channel and neither paper addresses it — see
   `../order-flow-imbalance-price-impact/` for the measurement side and
   `../guilbaud-pham-limit-and-market-orders/` for a model with execution priority.
2. **Brownian reference price.** No jumps, no drift, no microstructure noise. A gap through the
   quotes is treated as an ordinary Poisson arrival.
3. **`A` and `k` are still unestimated.** The paper takes them as given. They are the parameters
   that decide profitability, they must be calibrated from fill data, and they are regime-dependent.
4. **Continuous prices, no queue.** Quotes are continuous real numbers. Real books are discrete and
   fill probability depends on queue position — the issue Guilbaud & Pham take up directly.
5. **The closed forms are approximations of asymptotics.** Two layers of approximation: `T → ∞`, then
   the continuous replacement of the discrete eigenproblem. The paper provides figures comparing the
   approximation to the exact solution, but a production system should verify the gap at its own
   parameters rather than assuming it is negligible.
6. **`Q` is exogenous.** The inventory bound is imposed by the operator, not derived from capital or
   risk limits. Choosing it is a risk-management decision the model does not make for you.
