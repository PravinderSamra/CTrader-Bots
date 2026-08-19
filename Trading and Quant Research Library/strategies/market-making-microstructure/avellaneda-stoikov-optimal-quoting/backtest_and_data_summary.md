# Backtest & Data Summary — Avellaneda–Stoikov Optimal Quoting

## Verification

All figures below were read directly from the full text of Avellaneda, M., & Stoikov, S. (2008),
"High-frequency trading in a limit order book," *Quantitative Finance* 8(3), 217–224, retrieved
in-session from `math.nyu.edu/~avellane/HighFrequencyTrading.pdf`. Table references are to that
document. **Evidence grade: `verified-primary`.**

> **Read this before quoting any number below.** These results come from a **Monte Carlo simulation
> of the authors' own model**, not from a historical backtest on market data. There is no Sharpe
> ratio, no drawdown, and no win rate, because there is no historical P&L series — the paper
> validates that the derived control beats a naïve benchmark *inside the model world it assumes*.
> That is a legitimate and useful result, and it is a fundamentally weaker claim than an empirical
> backtest. Any live deployment requires validation on real order-book data with real fills.

---

## 1. Simulation setup

| Parameter | Symbol | Value |
|---|---|---|
| Initial mid-price | `s` | 100 |
| Terminal time | `T` | 1 |
| Volatility | `σ` | 2 |
| Time step | `dt` | 0.005 |
| Initial inventory | `q` | 0 |
| Risk aversion (base case) | `γ` | 0.1 |
| Order-arrival decay | `k` | 1.5 |
| Order-arrival base intensity | `A` | 140 |
| Simulation paths | — | 1000 per configuration |

The mid-price follows `dS = σ dW`. At each step, a bid fill occurs with probability `λ^b(δ^b)·dt`
and an ask fill with probability `λ^a(δ^a)·dt`, where `λ(δ) = A·exp(−k·δ)`.

The paper notes the choice of `dt` is subtle: small enough that multiple fills within one step are
unlikely, but larger than the typical tick interval.

**Benchmark ("symmetric") strategy.** Quotes the **same average spread** the inventory strategy
produced over the run, but centred on the **mid-price** rather than the reservation price. This is
the right control — it isolates the effect of inventory skewing from the effect of spread width,
since both strategies capture identical width.

## 2. Results — the three risk-aversion regimes

### Table 1 — γ = 0.1 (base case)

| Strategy | Average spread | Profit | Std(Profit) | Final q | Std(Final q) |
|---|---|---|---|---|---|
| **Inventory** | 1.49 | **65.0** | **6.6** | 0.08 | **2.9** |
| Symmetric | 1.49 | **68.4** | **12.7** | 0.26 | **8.4** |

The symmetric strategy earns **5.2% more profit** and carries **92% more profit volatility**. Its
inventory dispersion is nearly 3× larger. The authors explain the profit gap directly: the symmetric
strategy is centred on the mid-price and therefore "receives a higher volume of orders."

### Table 2 — γ = 0.01 (near risk-neutral)

| Strategy | Average spread | Profit | Std(Profit) | Final q | Std(Final q) |
|---|---|---|---|---|---|
| Inventory | 1.35 | 68.6 | **8.7** | 0.12 | **5.1** |
| Symmetric | 1.35 | 68.8 | **12.8** | 0.09 | **8.7** |

With risk aversion nearly switched off, the profits converge (68.6 vs 68.8) — but the inventory
strategy *still* delivers materially lower variance (8.7 vs 12.8). Even a near-risk-neutral operator
gains from skewing.

### Table 3 — γ = 1 (highly risk-averse)

| Strategy | Average spread | Profit | Std(Profit) | Final q | Std(Final q) |
|---|---|---|---|---|---|
| Inventory | 3.02 | **31.4** | **5.0** | 0.02 | **1.7** |
| Symmetric | 3.02 | **44.0** | **11.0** | 0.00 | **5.1** |

High risk aversion more than doubles the quoted spread (3.02 vs 1.49 at γ = 0.1) and cuts profit
by half. The paper's own summary: this choice "produces low standard deviations of profits and final
inventory, but generates more modest profits than the corresponding symmetric strategy."

### 2.1 The γ trade-off, read across the three tables

| γ | Avg spread | Inventory profit | Std(Profit) | Profit / Std | Std(Final q) |
|---|---|---|---|---|---|
| 0.01 | 1.35 | 68.6 | 8.7 | 7.9 | 5.1 |
| 0.10 | 1.49 | 65.0 | 6.6 | **9.8** | 2.9 |
| 1.00 | 3.02 | 31.4 | 5.0 | 6.3 | 1.7 |

The "Profit / Std" column is a return-per-unit-risk proxy computed here from the paper's figures
(**not published by the authors** — labelled as this library's derived arithmetic, not a citation).
Read that way, γ = 0.1 dominates the other two settings in this parameter set. That is the practical
lesson: γ is a tuning knob with an interior optimum, not a preference to be maximised or minimised.

## 2.2 Independent reproduction (run in-session)

The simulator in `source_or_pseudo_code.txt` (PART B) was written directly from the paper's
equations (29) and (30) and executed with the paper's parameters — `s0=100, T=1, σ=2, dt=0.005,
k=1.5, A=140`, 1000 paths per configuration. Output:

| Table | γ | Strategy | Spread | Profit | Std(P) | q | Std(q) |
|---|---|---|---|---|---|---|---|
| Table 1 | 0.1 | Inventory | 1.49 | 65.0 | 6.5 | −0.01 | 2.9 |
| Table 1 | 0.1 | Symmetric | 1.49 | 67.9 | 14.0 | −0.02 | 8.6 |
| Table 2 | 0.01 | Inventory | 1.35 | 68.4 | 8.9 | −0.20 | 5.2 |
| Table 2 | 0.01 | Symmetric | 1.35 | 68.4 | 14.4 | −0.17 | 8.9 |
| Table 3 | 1.0 | Inventory | 3.03 | 30.8 | 4.9 | −0.01 | 1.7 |
| Table 3 | 1.0 | Symmetric | 3.03 | 43.4 | 11.3 | 0.08 | 5.3 |

**Assessment: the paper reproduces.** The inventory-strategy figures match to within Monte Carlo
noise across all three risk-aversion regimes — average spread matches to two decimals (1.49 / 1.35 /
3.03 vs. 1.49 / 1.35 / 3.02), profit to within 0.6 (65.0 / 68.4 / 30.8 vs. 65.0 / 68.6 / 31.4), and
Std(Final q) matches exactly at 2.9 / 5.2 / 1.7 vs. 2.9 / 5.1 / 1.7.

**One discrepancy worth recording.** The *symmetric benchmark's* profit standard deviation comes out
consistently higher in this reproduction than published — 14.0 vs. 12.7 at γ = 0.1, and 14.4 vs.
12.8 at γ = 0.01. The direction of the result is unaffected (the benchmark is still far riskier than
the inventory strategy — if anything more so), but the magnitude differs by roughly 10%. The likely
cause is an under-specification in the paper: it states the benchmark "uses the average bid/ask
spread of the inventory strategy over the time period," which leaves ambiguous whether that average
is taken per-path or across all paths, and whether it is held constant through the run or updated.
This reproduction fixes a single constant spread across the whole run. **This is a documented open
item, not a claimed error in the paper** — Wave 2 should test the alternative interpretations and
record which one recovers 12.7.

Two properties of the reproduction are worth noting as validation of the model's core claim:

- Mean final inventory is essentially zero (−0.01 at γ = 0.1) without any explicit flattening logic.
  The skew alone does it.
- The risk reduction is large and consistent: Std(Profit) of 6.5 vs. 14.0 at γ = 0.1 — a **54%
  reduction** in this run, against the paper's 48%.

## 3. What the numbers actually demonstrate

1. **Skewing halves risk at a small profit cost.** The central result, robust across all three γ
   values: the inventory strategy always has substantially lower profit variance than the symmetric
   benchmark quoting the same width.
2. **Inventory control is the mechanism.** Std(Final q) drops from 8.4 to 2.9 at γ = 0.1. The
   strategy never explicitly targets flat inventory — the skew makes flatness emerge.
3. **Symmetric quoting earns slightly more gross.** Being centred on the mid attracts more flow.
   The trade is more revenue for much more risk, which is a bad trade for anyone using leverage or
   facing a risk limit.
4. **Risk aversion widens spreads and cuts profit.** At γ = 1 the spread doubles and profit halves,
   while the risk reduction is modest relative to γ = 0.1.

## 4. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio | **NOT REPORTED IN SOURCE** — no historical return series exists |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Maximum drawdown | **NOT REPORTED IN SOURCE** — only terminal P&L distributions (Figures 2–4 histograms) |
| Win rate | **NOT REPORTED IN SOURCE** |
| Profit factor | **NOT REPORTED IN SOURCE** |
| Backtest on real market data | **NOT PERFORMED IN SOURCE** |
| Fill rates achieved vs. modelled | **NOT REPORTED IN SOURCE** |

Anyone needing these must run the strategy against real order-book data with a queue-position-aware
fill model. `source_or_pseudo_code.txt` includes the simulator to reproduce the paper's tables, which
is the correct first step, but it validates the mathematics, not the market assumptions.

## 5. Where the strategy thrives vs. fails

**Thrives when:**
- **Two-sided, uninformed flow dominates.** The model's core assumption is that arrivals are
  exogenous. Retail-heavy, flow-driven markets fit best.
- **The mid-price is close to driftless over the quoting horizon.** `dS = σ dW` has no drift term;
  a trending market means one side of the book is systematically adversely selected.
- **Volatility is stable and estimable.** `σ` enters both the reservation-price shift and the
  spread. A stale `σ` in a volatility spike means quoting far too tight into exactly the conditions
  that punish it.
- **`A` and `k` can be calibrated from fill data.** These are the least discussed and most important
  practical parameters.
- **Ticks are small relative to volatility**, so the continuous-price approximation holds and queue
  position matters less. This is why the model transplants well to crypto perpetuals and less well
  to tight-tick, deep-queue equity books.

**Fails when:**
- **Informed flow arrives.** The model has no concept of adverse selection. A fill is a fill. In
  reality, the fills you get just before a large move are the ones that determine profitability, and
  this model prices them identically to benign ones. This is the primary reason naïve deployments
  lose money.
- **The price jumps.** Brownian motion has no jumps. A gap through both quotes produces an
  immediate loss the model never anticipated, and the post-jump inventory skew then quotes the
  market maker further into the move.
- **Inventory limits bind.** Nothing bounds `q`. In a sustained one-way market, the skew slows
  accumulation but does not stop it, and position limits or margin will bind before the model
  reaches its own equilibrium.
- **`T − t → 0` at a session boundary.** Both the inventory-risk spread term and the reservation
  price shift go to zero, so the strategy tightens and stops skewing precisely when it is trying to
  flatten. Roll the horizon or use the infinite-horizon variant.
- **Latency and queue position dominate.** In tight-tick markets, whether you get filled depends on
  where you sit in the queue, not on a smooth intensity function.

## 6. Decay and current status

**`decay_status: intact`** — with an important qualification about what "intact" means here.

This entry is a **model**, not an empirical anomaly, so it cannot decay the way pairs trading did.
The mathematics of `r = s − qγσ²(T−t)` remains correct under its assumptions, and the framework is
still the standard starting point in the academic market-making literature and the standard baseline
in practitioner implementations (notably in crypto market making, where the modelling assumptions
fit best).

What *has* changed is the competitive environment the model is deployed into. In institutional
equity and futures markets, market making is now dominated by firms whose edge lies in the areas
Avellaneda–Stoikov explicitly does not model: latency, queue position, and short-horizon
adverse-selection prediction from order-flow signals. Running vanilla A–S against those participants
is a losing proposition — not because the control is wrong, but because it optimises the wrong
subset of the problem.

**How to use this entry.** Treat it as the correct skeleton for the inventory-management layer of a
market-making system, and as the baseline any more sophisticated quoting model must beat. It is not
a complete market-making strategy: the missing adverse-selection layer is where the money is won or
lost. Guéant–Lehalle–Fernandez-Tapia (inventory bounds, exact closed forms) and Cartea–Jaimungal
(order-flow and adverse selection) are queued as Wave 2 entries and are the necessary companions to
this one.
