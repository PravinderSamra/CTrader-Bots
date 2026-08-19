# Market Making with Limit *and* Market Orders (Guilbaud & Pham)

**Category:** Market Making & Order-Flow Microstructure (Wave 2 depth entry)
**Anchor paper:** Guilbaud, F., & Pham, H. (2013). "Optimal high-frequency trading with limit and
market orders." *Quantitative Finance*, 13(1), 79–94. arXiv:1106.5040 (draft consulted: 24 June
2011).
**Parent entry:** `../avellaneda-stoikov-optimal-quoting/`

---

## 1. Abstract / summary of the core edge

Avellaneda–Stoikov and Guéant–Lehalle–Fernandez-Tapia both model a market maker who posts limit
orders and waits. Neither lets the agent do the thing every real desk does when inventory gets
uncomfortable: **cross the spread and get out**.

This paper adds that option, and two more pieces of realism that matter in practice:

1. **Market orders as an impulse control.** The agent may pay the spread for immediate execution.
   This turns the problem into a **mixed regular/impulse control problem** — continuously adjusting
   limit quotes (regular control) while occasionally jumping via a market order (impulse control).
2. **A discrete tick and execution priority.** The bid-ask spread is modelled as a **Markov chain on
   finite values that are multiples of the tick size**, subordinated by a Poisson "tick-time clock."
   The agent can post at the best quote, or **improve it by one tick to gain queue priority** —
   "which is a crucial issue in high frequency trading," as the authors put it.
3. **Execution risk that depends on where you quote.** Limit orders execute only when they meet
   counterpart market orders, modelled as **Cox processes whose intensities depend on the spread and
   on the agent's limit prices**.

The result the entry exists for is the benchmarked comparison. Against three alternatives, the
optimal strategy's information ratio (terminal wealth mean / standard deviation, 10⁵ simulations):

| Strategy | IR |
|---|---|
| **Optimal (limit + market orders)** | **2.117** |
| Optimal **without** market orders | 1.999 |
| Constant symmetric quoting | 0.472 |
| Random quoting | 0.376 |

Two readings, and the second is the more useful one:

- **The layered optimisation is worth a great deal versus naïve quoting.** 2.117 against 0.472 for
  symmetric constant quotes is a 4.5× improvement in risk-adjusted terms.
- **But market orders add surprisingly little.** 2.117 versus 1.999 — the gain from the entire
  impulse-control machinery is **0.124 standard deviations** of terminal wealth, against **0.194**
  for the optimal-vs-constant comparison. Most of the value is in quoting intelligently; the ability
  to cross the spread is a refinement, not the main event.

Where market orders *do* earn their place is inventory control, and the numbers are unambiguous —
see §3.3.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Guilbaud & Pham — arXiv:1106.5040 (verified in-session, June 2011 draft) | paper | https://arxiv.org/pdf/1106.5040 |
| arXiv abstract page | paper | https://arxiv.org/abs/1106.5040 |
| Published: *Quantitative Finance* 13(1), 79–94 | paper | https://www.tandfonline.com/doi/abs/10.1080/14697688.2012.708779 |
| Avellaneda & Stoikov (2008) — the parent model | paper | https://www.math.nyu.edu/~avellane/HighFrequencyTrading.pdf |
| Guéant, Lehalle & Fernandez-Tapia — bounded inventory | paper | https://arxiv.org/pdf/1105.3115 |

## 3. Mathematical foundation

### 3.1 The spread as a Markov chain in tick time

The distinguishing modelling choice. Rather than a continuous price with a continuous quoting
decision, the **bid-ask spread `S_t` is a Markov chain on a finite set of tick multiples**,
subordinated by a Poisson process — the "tick time clock" — whose intensity `λ(t)` is itself
estimated from data and varies through the day.

This matters because it makes the model's state space match what a trader actually observes. The
spread is 1 tick, or 2 ticks, or 3; it is not 1.37 ticks. Quoting decisions are therefore discrete
choices: post at the best bid `B^b`, or at `B^{b+}` (one tick better, gaining queue priority), and
similarly on the ask.

### 3.2 Execution intensities depend on the quote

Limit order fills arrive as **Cox processes** with intensities depending on both the prevailing
spread and the agent's chosen limit price. The trade-off the paper identifies explicitly:

> "There is then a tradeoff between a larger performance for a quote at the current best bid (resp.
> ask) price, and a smaller performance for a quote at a higher bid price, but…"

— i.e. improving your quote by a tick buys execution probability and queue priority at the cost of a
worse fill price. This is the queue-position problem that Avellaneda–Stoikov's smooth
`λ(δ) = A·exp(−kδ)` intensity function cannot represent, because it has no notion of discrete price
levels or priority.

### 3.3 The control problem and its tractable reductions

The full problem is a **mixed regime-switching regular/impulse control problem**, characterised via
dynamic programming as a **quasi-variational system**. In that generality it is not practical.

The paper's contribution is showing two special cases collapse to something solvable:

- a **mean-variance criterion with a martingale reference price**, or
- an **exponential utility criterion with a Lévy price process**,

in either of which "the dynamic programming system can be reduced to a system of simple equations
involving only the **inventory and spread variables**." Two state variables — inventory and spread —
is a small enough system to solve numerically and run in production.

### 3.4 Calibration is part of the paper

Unlike the parent entries, which take `A`, `k` and `σ` as given, this paper derives **calibration
procedures** for the spread transition matrix, the tick-time-clock intensity, and the Cox execution
intensities — and applies them to real data (SOGN.PA, tick-by-tick Level 1, 18 April 2011, from
Quanthouse). This is a meaningful practical advantage: the model comes with instructions for
estimating its own parameters.

### 3.5 What market orders are actually for

The backtest makes the role of the market-order option clear, and it is not profit:

| Metric | Optimal | Without market orders | Constant | Random |
|---|---|---|---|---|
| Mean terminal wealth | 26.759 | 25.190 | 24.314 | 21.543 |
| Market-order executions | **6.336** | 0 | 0 | 0 |
| **Mean max inventory** | **241.0** | 176.2 | **607.9** | **772.4** |
| sd of max inventory | 53.5 | 23.7 | 272.6 | 337.4 |

Note the counter-intuitive result: the optimal strategy carries a **larger** maximum inventory
(241.0) than the no-market-order variant (176.2). Having an escape hatch lets the agent *tolerate*
more inventory, because it knows it can exit. What both optimal variants achieve is inventory an
order of magnitude better controlled than constant (607.9) or random (772.4) quoting, with a
fraction of the dispersion.

## 4. Known criticisms and limitations

1. **The backtest is on simulated data.** The authors are explicit that "absolute values of `m(X_T)`
   are not representative of what would be the real-world performance," and that the simulated
   backtest "must be completed by a backtest on real data." Calibration uses real data; the
   performance comparison does not. This is a materially weaker evidential claim than a live or
   historical test.
2. **A single stock, a single day.** Calibration is on SOGN.PA on 18 April 2011. Parameter stability
   across instruments, days, and regimes is untested.
3. **Still no adverse selection in the usual sense.** Execution intensities depend on the spread and
   the agent's quotes, but a fill does not update the agent's belief about future price direction.
   Informed flow remains unmodelled — see `../order-flow-imbalance-price-impact/`.
4. **Tractability requires a special case.** The general quasi-variational system is not solved; the
   practical results rest on the mean-variance-with-martingale-price or exponential-utility-with-Lévy
   assumptions. Whether the reference price is a martingale over the relevant horizon is exactly what
   a market maker is exposed to being wrong about.
5. **The market-order gain is modest.** 0.124 standard deviations of terminal wealth over the
   no-market-order variant. Against the considerable additional complexity of an impulse-control
   layer, that is a real cost-benefit question, not an obvious win.
6. **Queue priority is modelled coarsely.** The agent chooses best-quote or one-tick-better; there is
   no explicit model of position *within* the queue at a level, which is the dominant consideration
   in the most competitive books.
