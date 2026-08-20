# Optimal Execution of Portfolio Transactions (Almgren–Chriss)

**Category:** Execution & Cost — *the first entry in this category*
**Anchor paper:** Almgren, R., & Chriss, N. (2000). "Optimal Execution of Portfolio Transactions."
*Journal of Risk*, 3(2), 5–39. (Draft consulted: December 2000.)

---

## 1. Why this category exists, and why this is its anchor

Every other entry in this library describes an edge. This one describes the tax on collecting it.

The library's ten strategy entries all share a dependency they mostly cannot model: the cost of
actually trading. Gatev, Goetzmann & Rouwenhorst's pairs profits fall from 437–549 bp per six months
to 113–225 bp once their own conservative cost estimate is applied. Jegadeesh & Titman model no costs
at all. Moskowitz, Ooi & Pedersen report gross Sharpe ratios. Whether any of these strategies is
implementable is decided here, not there.

Almgren and Chriss provide the framework. Their statement of the problem:

> "We consider the execution of portfolio transactions with the aim of minimizing a combination of
> volatility risk and transaction costs arising from permanent and temporary market impact. For a
> simple linear cost model, we explicitly construct the efficient frontier in the space of
> time-dependent liquidation strategies, which have minimum expected cost for a given level of
> uncertainty."

The core insight is that execution is **not a cost-minimisation problem** — it is a risk-return
problem with the same structure as portfolio choice.

- **Trade fast** → you pay large market impact, but you are exposed to price risk only briefly.
- **Trade slowly** → impact is small, but you hold an unwanted position while the price wanders.

Neither extreme is optimal. There is an **efficient frontier** of trading trajectories, exactly
analogous to Markowitz's frontier, and a trader picks a point on it according to risk aversion. This
reframing is the paper's lasting contribution and the reason "implementation shortfall" became the
industry's standard execution benchmark.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Almgren & Chriss (2000) — full text PDF (verified in-session) | paper | https://www.smallake.kr/wp-content/uploads/2016/03/optliq.pdf |
| Journal of Risk record | paper | https://www.risk.net/journal-of-risk/2161150/optimal-execution-portfolio-transactions |
| Almgren (2003) — extension to non-linear (power-law) impact | paper | https://www.cims.nyu.edu/~almgren/papers/optliq_nonlin.pdf |
| Perold (1988) — the implementation shortfall concept | paper | https://www.hbs.edu/faculty/Pages/item.aspx?num=6560 |
| Cont, Kukanov & Stoikov — the linear-impact evidence, and the square-root critique | paper | https://arxiv.org/pdf/1011.6402 |

## 3. Mathematical foundation

### 3.1 The two kinds of impact

The distinction that organises everything:

- **Temporary impact** — you push the price away from equilibrium while you trade, and it recovers
  afterwards. This is the cost of demanding immediacy. It depends on your **rate** of trading.
- **Permanent impact** — your trading conveys information (or consumes liquidity that does not
  return), so the price level shifts and stays shifted. It depends on the **total quantity** traded.

The critical asymmetry: **permanent impact is unavoidable** for a given order size. It contributes a
fixed cost `½γX²` independent of the trajectory, so it cannot be optimised away. All the optimisation
happens against temporary impact and volatility risk.

### 3.2 The linear model

For a liquidation of `X` shares over time `T`, divided into `N` intervals of length `τ = T/N`, with
`x_j` shares remaining at time `t_j`:

```
Permanent impact:   g(v) = γ · v
Temporary impact:   h(v) = ε · sgn(v) + η · v
```

where `v = n_j/τ` is the trading rate, `ε` is a fixed cost (typically **half the bid-ask spread**),
`γ` is the permanent impact coefficient, and `η` the temporary impact coefficient.

The trader minimises a mean-variance objective over trajectories:

```
minimise   E[cost] + λ · V[cost]
```

with `λ` the risk-aversion parameter (units of 1/$).

### 3.3 The solution — a hyperbolic-sine trajectory

The optimal holdings path is:

```
x_j = ( sinh( κ(T − t_j) ) / sinh( κT ) ) · X          j = 0, …, N
```

with the associated trade list:

```
n_j = ( 2·sinh(½κτ) / sinh(κT) ) · cosh( κ(T − t_{j−½}) ) · X
```

The single parameter `κ` governs everything, and for short intervals has the clean approximation:

```
κ ≈ √( λσ² / η )
```

Read that directly: **the urgency of trading is the square root of (risk aversion × variance) divided
by temporary impact.** More volatile, or more risk-averse → trade faster. More costly to trade →
trade slower.

The paper notes `n_j > 0` for all `j` as long as `X > 0` — **"the optimal execution of a sell program
never involves the buying of securities"** (absent drift or serial correlation).

### 3.4 The half-life of a trade

Defining `θ = 1/κ` as the trade's **half-life** — "exactly the amount of time it takes to deplete the
portfolio by a factor of `e`" — gives the paper's most portable practical concept.

Crucially, `θ` **does not depend on the imposed execution horizon `T`.** It is determined only by
price dynamics and impact parameters. As the authors put it: "in the absence of any external time
constraint (`T → ∞`), the trader will still liquidate his position on a time scale `θ`. The half-life
`θ` is the intrinsic time scale of the trade."

The ratio `κT = T/θ` then tells you what actually constrains your execution:

| Regime | Meaning | Behaviour |
|---|---|---|
| `T ≫ θ` | The deadline is loose; risk dominates | Most trading done early; approaches the minimum-variance solution |
| `T ≪ θ` | The deadline binds; impact dominates | Approaches the straight-line, minimum-cost (VWAP-like) strategy |
| `T ≈ θ` | Genuine trade-off | The interesting intermediate case |

This is the diagnostic to run before choosing an execution algorithm: compute `θ`, compare it to your
deadline, and the answer to "should I be patient or aggressive?" falls out.

### 3.5 Liquidity-adjusted VaR

Rather than a quadratic utility, the trader may minimise **Value at Risk**, which leads to what the
authors call **L-VaR** — a VaR measure that "explicitly considers the best tradeoff between
volatility risk and liquidation costs."

The point is conceptual and important: standard VaR asks what a position could lose while you hold
it, implicitly assuming you can exit instantly and costlessly. L-VaR asks what it costs to *actually
get out*, which is the question that matters in a crisis. A position is only as safe as its
liquidation path.

## 4. Known criticisms and limitations

1. **Linear temporary impact is the wrong functional form, and the authors know it.** The paper notes
   in a footnote that its model "does not predict more rapid trading for smaller versus larger baskets
   of the same security… this is a result of choosing linear temporary impact functions and the
   problem goes away when one considers more realistic super-linear functions." The empirical
   literature strongly favours a **square-root** law. Almgren (2003) extends the framework to
   power-law impact.
2. **…but the square-root law is itself contested.** Cont, Kukanov & Stoikov derive square-root impact
   as an *aggregation artefact* of an underlying **linear** relation between price changes and order
   flow imbalance, and argue it "is not robust." See
   `../../market-making-microstructure/order-flow-imbalance-price-impact/`. The functional form of
   impact remains genuinely unsettled, which matters because it determines the optimal trajectory.
3. **Static, not adaptive.** With zero drift, the optimal trajectory is determined at time zero and
   never revised. Real execution algorithms respond to realised prices, fills, and liquidity. The
   paper's Section 4 ("The Value of Information") addresses drift and serial correlation as
   extensions.
4. **Constant parameters.** `σ`, `η`, `γ` are fixed. In reality volatility and liquidity have strong
   intraday patterns — the very seasonality Cont, Kukanov & Stoikov document and tie to market depth.
5. **No limit orders, no venue choice, no queue.** Execution is modelled as a rate of consumption of
   liquidity. There is no passive/aggressive decision, no order routing, no queue position — which is
   most of what a modern execution algorithm actually does.
6. **`λ` is unobservable.** As with every risk-aversion parameter in this library, it is chosen, not
   estimated. The paper's own numerical example picks `λ = 10⁻⁶` and reports the corresponding
   "static holdings" interpretation to make it interpretable.
