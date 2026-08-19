# Avellaneda–Stoikov Optimal Market Making

**Category:** Market Making & Order-Flow Microstructure
**Anchor paper:** Avellaneda, M., & Stoikov, S. (2008). "High-frequency trading in a limit order
book." *Quantitative Finance*, 8(3), 217–224.

---

## 1. Abstract / summary of the core edge

A market maker quotes a bid and an ask, earns the spread on round trips, and carries inventory risk
between them. The naïve approach quotes symmetrically around the mid-price. Avellaneda and Stoikov
show that this is the wrong centre. The correct centre is the **reservation price** — the price at
which the market maker is indifferent to holding their current inventory — which sits below the
mid when long and above the mid when short.

The consequence is a quoting scheme that automatically manages inventory. Accumulate a long
position and both quotes shift down, making your bid less attractive and your ask more attractive,
so the market does your unwinding for you. No separate inventory-management layer, no hard stops:
skewing falls out of the utility maximisation.

The result is not higher profit. It is **dramatically lower variance of profit**. In the paper's own
1000-path simulation with γ = 0.1, the inventory strategy earns 65.0 with a standard deviation of
6.6, while the symmetric benchmark quoting the same average spread earns slightly more — 68.4 — with
a standard deviation of **12.7**, nearly double. Final inventory tells the same story: standard
deviation 2.9 versus 8.4.

That is the edge: for a 5% give-up in expected profit, the risk of the P&L is roughly halved. For a
market maker running continuously with limited capital, this is the difference between a viable
business and an eventual blow-up.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Avellaneda & Stoikov (2008) — full text PDF (verified in-session) | paper | https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf |
| Publisher record | paper | https://ideas.repec.org/a/taf/quantf/v8y2008i3p217-224.html |
| NYU Scholars record | paper | https://nyuscholars.nyu.edu/en/publications/high-frequency-trading-in-a-limit-order-book |
| Open-source replication (Python) | repository | https://github.com/ragoragino/avellaneda-stoikov |
| Open-source replication (alternative) | repository | https://github.com/z772/avellaneda-stoikov-1 |
| Guéant, Lehalle & Fernandez-Tapia — closed-form extension with inventory limits | paper | https://arxiv.org/abs/1105.3115 |
| Guilbaud & Pham — optimal market making with **both limit and market orders**, discrete tick | paper | https://arxiv.org/pdf/1106.5040 |
| Cartea, Jaimungal & Penalva — *Algorithmic and High-Frequency Trading* (CUP, 2015) — the standard treatment of adverse selection | book | — |

Note the replication repositories are third-party and are recorded at `verified-secondary` — they
were identified as existing replications of this paper, but their code was not audited in-session.
The reference implementation in `source_or_pseudo_code.txt` is written directly from the paper's
equations, not adapted from them.

## 3. Mathematical foundation

### 3.1 Model setup

**Mid-price** follows arithmetic Brownian motion (no drift — the market maker has no directional
view):

```
dS_t = σ dW_t
```

**Order arrivals.** The market maker posts a bid at distance `δ^b` below the mid and an ask at
distance `δ^a` above it. Market orders arrive as a Poisson process whose intensity decays
exponentially in the quote distance:

```
λ(δ) = A · exp(−k · δ)
```

Quote closer to the mid and you get filled more often; quote further away and you earn more per
fill but trade less. `A` sets the base arrival rate, `k` the sensitivity of fill rate to quote
distance. The exponential form is grounded in the empirical power-law distribution of market order
sizes (the paper cites tail exponents of ≈1.53 in Gopikrishnan et al. (2000) for NASDAQ and ≈1.5 in
Gabaix et al.).

**Objective.** Maximise expected utility of terminal wealth under constant absolute risk aversion
(CARA):

```
max E[ −exp( −γ (X_T + q_T · S_T) ) ]
```

where `X_T` is cash, `q_T` is terminal inventory, and `γ` is the risk-aversion coefficient. CARA is
what makes the problem tractable and gives inventory a *linear* penalty in the value function.

### 3.2 The two results that matter

Solving the Hamilton–Jacobi–Bellman equation and taking an asymptotic expansion in the inventory
variable yields two remarkably simple expressions.

**(i) The reservation price** — the centre of the quotes:

```
r(s, q, t) = s − q · γ · σ² · (T − t)
```

Read it directly: start at the mid-price `s`, then shift by an amount proportional to inventory `q`,
risk aversion `γ`, variance `σ²`, and time remaining `T − t`. Long inventory (`q > 0`) pushes the
reservation price **below** the mid, so both quotes drop and the market maker leans toward selling.
Short inventory pushes it above. As `t → T` the adjustment vanishes — with no time left, there is no
inventory risk to price.

**(ii) The optimal spread** — the total width around that centre:

```
δ^a + δ^b = γ · σ² · (T − t) + (2/γ) · ln( 1 + γ/k )
```

Two additive components with distinct economic meaning:

- `γ σ² (T − t)` — **inventory risk**. Widen when volatile, when risk-averse, or when the horizon
  is long.
- `(2/γ) ln(1 + γ/k)` — **order-arrival / liquidity**. Depends on `k`, the fill-rate sensitivity. In
  a market where fills fall off sharply with distance (high `k`), quote tighter.

Note what is *absent*: the spread does **not** depend on inventory `q`. This follows from the
exponential arrival assumption. Inventory moves the *centre* of the quotes, not their *width* — a
clean separation that makes the model easy to reason about and easy to implement.

The bid and ask then follow directly:

```
δ^b = r − bid_price      bid = r − (δ^a + δ^b)/2
δ^a = ask_price − r      ask = r + (δ^a + δ^b)/2
```

### 3.3 Why this is the right foundation entry for market making

The paper is not the last word — it assumes no drift, no adverse selection, symmetric arrival
intensities, a finite terminal time, and unlimited inventory. Every one of those has been relaxed
in the subsequent literature (Guéant–Lehalle–Fernandez-Tapia add inventory bounds and give exact
closed-form solutions; Guilbaud–Pham add market orders and a discrete tick grid; the
Cartea–Jaimungal–Penalva line adds order-flow signals and adverse selection).

But it is the paper that established the *shape* of the answer — reservation price plus
symmetric-width spread — and every later model is a refinement of that decomposition. It is also
simple enough to implement in an afternoon and test, which is why it remains the working baseline
for practitioners and the reference point in crypto market making, where the assumptions (continuous
two-sided quoting, no locates, small tick relative to volatility) fit unusually well.

## 4. Known criticisms and limitations

1. **No adverse selection.** The single biggest omission. Order arrival is exogenous and
   uninformative: a fill tells the model nothing about where the price is going. In real markets a
   fill on the bid is disproportionately likely just before the price falls — the trader lifting you
   often knows something. Real market makers lose to informed flow, and this model cannot see that
   loss. The order-flow-imbalance literature and the Cartea–Jaimungal–Penalva treatment address it; see
`../../market-making-microstructure/order-flow-imbalance-price-impact/`.
2. **Terminal time `T` is artificial.** The formulas depend on `T − t`, but a continuously operating
   market maker has no terminal time. Practitioners either roll `T` (treating it as a fixed lookahead
   window) or use the infinite-horizon variant the paper sketches. Simply letting `T − t → 0` at the
   end of a session causes the spread to collapse and inventory skew to vanish, which is dangerous
   rather than optimal.
3. **No inventory limits.** Nothing in the model prevents an unbounded position; the skew merely
   makes further accumulation less likely. Any production implementation needs hard inventory caps,
   which Guéant–Lehalle–Fernandez-Tapia incorporate properly.
4. **Constant `σ`, `A`, `k`.** All three are volatile and regime-dependent in practice, and `A` and
   `k` must be estimated from fill data. Parameter estimation is the hard part of deploying this and
   the paper does not address it.
5. **No queue position, no discrete ticks, no latency.** The model quotes a continuous price and
   assumes fills follow the intensity function. Real fills depend on queue priority at a discrete
   price level, which is the dominant practical consideration in tight-tick markets.
6. **Brownian mid-price.** No jumps, no drift, no microstructure noise. A jump through the quotes
   produces an instant adverse fill that the model treats as an ordinary Poisson arrival.
7. **γ is not observable.** The risk-aversion coefficient is a free parameter chosen by the operator,
   and it drives the results heavily — see the γ = 0.01 / 0.1 / 1 comparison in
   `backtest_and_data_summary.md`. It is best treated as a tuning knob calibrated to a target
   inventory distribution rather than as a preference estimated from data.
