# Backtest & Data Summary — Market Making with Limit and Market Orders

## Verification

All figures below were read directly from Guilbaud, F., & Pham, H., "Optimal high frequency trading
with limit and market orders," **arXiv:1106.5040, dated 24 June 2011**, retrieved in-session from
`arxiv.org/pdf/1106.5040`. Published as *Quantitative Finance* 13(1), 79–94 (2013); the published
version was not consulted. Table references are to the arXiv draft.
**Evidence grade: `verified-primary`** for the arXiv draft.

> **Provenance note.** This library's Avellaneda–Stoikov entry originally cited arXiv:1106.5040 as
> "Cartea & Jaimungal." That was a mis-attribution introduced in Wave 1 and corrected in Wave 2 —
> the paper at that identifier is Guilbaud & Pham. The A–S entry's source table and metadata now name
> the correct authors.

---

## 1. Data and experimental setup

The paper has **two distinct empirical components**, and conflating them overstates the evidence.

### 1.1 Calibration — real market data

| Field | Value |
|---|---|
| Instrument | **SOGN.PA** (Société Générale, Euronext Paris) |
| Date | **18 April 2011** — a single trading day |
| Data | **Tick-by-tick Level 1**, provided by Quanthouse |
| Calibrated objects | Spread transition matrix `(ρ_ij)`; tick-time-clock intensity `λ(t)` (hourly); Cox execution intensities `λ^a_i(q^b)` etc., in s⁻¹ |

### 1.2 Performance comparison — **simulated** data

| Field | Value |
|---|---|
| Method | Monte Carlo, standard Euler scheme with time step `Δt` |
| Paths | **10⁵ simulations** |
| Processes simulated | `(X^α, Y^α, P, S, N^{a,α}, N^{b,α})` per eq. (2.1)–(2.5) |

> ⚠️ **The headline performance table is from simulation, not from market data.** The authors state
> this plainly: "absolute values of `m(X_T)` are not representative of what would be the real-world
> performance of such strategies," and the simulated backtest "must be completed by a backtest on
> real data." The calibration is real; the performance comparison is not. Treat the ratios between
> strategies as the meaningful output and the absolute levels as arbitrary.

## 2. The benchmarked comparison — Table 5

Four strategies, 10⁵ simulations each:

| Strategy | Description |
|---|---|
| `α*` | **Optimal** — limit orders with tick-level price choice, plus market orders |
| `α_w` | **WoMO** — the same optimisation with market orders disallowed (`ē = 0`) |
| `α_c` | **Constant** — symmetric best-bid/best-ask quoting, fixed size both sides |
| `α_r` | **Random** — limit prices chosen randomly between best and one tick better |

### Results

| Metric | `α*` optimal | `α_w` WoMO | `α_c` constant | `α_r` random |
|---|---|---|---|---|
| **Information ratio `m(X_T)/σ(X_T)`** | **2.117** | **1.999** | **0.472** | **0.376** |
| Mean terminal wealth `m(X_T)` | 26.759 | 25.190 | 24.314 | 21.543 |
| σ(N^a_T) | 3.666 | 3.573 | 3.692 | 4.602 |
| Mean market-order executions | **6.336** | 0 | 0 | 0 |
| σ of market-order executions | 2.457 | 0 | 0 | 0 |
| **Mean max inventory** `m(sup|Y_s|)` | **241.0** | **176.2** | **607.9** | **772.4** |
| σ of max inventory | 53.5 | 23.7 | 272.6 | 337.4 |

### Performance gains, measured in standard deviations

The paper's own normalisation, which is the right way to read the table:

| Comparison | Gain |
|---|---|
| `(m(X_{α*}) − m(X_{α_c})) / σ(X_{α*})` — optimal vs constant | **0.194** |
| `(m(X_{α*}) − m(X_{α_w})) / σ(X_{α*})` — optimal vs WoMO | **0.124** |

## 3. Reading the results honestly

**1. Optimising the quoting layer is where most of the value is.** The information ratio goes from
0.472 (constant symmetric quoting) to 1.999 (optimal limit-order placement, no market orders) — a
**4.2× improvement** before market orders are considered at all. Choosing *where in the tick grid*
to post, conditional on the prevailing spread and inventory, is the dominant effect.

**2. Market orders add little to profit.** 2.117 vs 1.999 in information ratio; 0.124 standard
deviations of terminal wealth. Against the substantial extra complexity of an impulse-control layer,
this is a genuine cost-benefit question rather than a clear win. Anyone building this should
implement the limit-order optimisation first and treat market orders as a later refinement.

**3. Market orders are for inventory control, and there the effect is real but subtle.** The optimal
strategy uses only **6.3 market orders** on average — it is not trading its way out constantly. And
counter-intuitively it carries a **higher** mean maximum inventory (241.0) than the no-market-order
variant (176.2).

> That inversion is the most interesting number in the table. Having an escape hatch does not make
> the agent hold *less* inventory — it makes the agent *willing to hold more*, because a position it
> can exit on demand is less dangerous than one it cannot. The market-order option buys risk
> tolerance, not risk reduction.

**4. Both optimal variants dominate naïve quoting on inventory by an order of magnitude.** 241.0 and
176.2 against 607.9 (constant) and 772.4 (random), with dispersion of 53.5 and 23.7 against 272.6
and 337.4. Naïve symmetric quoting does not merely earn less — it accumulates wildly uncontrolled
positions, which is how market makers actually fail.

## 3.1 Policy-solver verification (run in-session)

The reduced (spread, inventory) value iteration in `source_or_pseudo_code.txt` was solved on
synthetic but plausible parameters — spread states {1, 2, 3} ticks, fill intensities favouring
one-tick price improvement, `tick = 0.01`, `|y| ≤ 10`:

| Risk aversion `γ` | Market-order region |
|---|---|
| 0.0002 | **None** at any spread or inventory |
| 0.0005 | `|y| ≥ 5` at a **1-tick** spread; `|y| ≥ 8` at a **2–3-tick** spread |

**The structure that emerges is the economically correct one, and it validates the model's
distinctive design choice:**

1. The market-order region sits at **large inventory** — you cross only when the position has become
   uncomfortable, never routinely.
2. **The region is wider when the spread is narrow** (`|y| ≥ 5` at one tick versus `|y| ≥ 8` at two
   or three). Crossing costs half the spread, so a tight market makes the escape hatch cheap and the
   agent reaches for it sooner. **A model that did not carry the spread as a state variable could not
   produce this at all** — it is the direct payoff from modelling the spread as a discrete Markov
   chain rather than a constant.
3. At low enough risk aversion the region vanishes, which is the correct limit: a risk-neutral agent
   never pays the spread to flatten.

**A calibration trap found while testing.** An earlier run used `γ = 0.02`, which makes the per-step
inventory penalty for a single unit (0.02) four times the cost of crossing a one-tick spread (0.005).
The optimiser then crossed at *every* non-zero inventory — a degenerate policy that quotes, gets
filled, and immediately pays the spread to undo the fill. If a solver wants to market-order out of
every fill, the risk-aversion parameter is mis-scaled relative to the tick, not the code.

**Not reproduced:** the placement choice stayed at "post at best" in every state — improving by a
tick never paid at the synthetic intensities used. Whether price improvement is worthwhile depends
entirely on the ratio of the two fill intensities to the tick cost, which only real calibration can
supply. Nothing here should be read as evidence that price improvement is generally unprofitable;
the paper's own results say the opposite.

## 4. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio on real data | **NOT REPORTED** — the performance comparison is simulated |
| Maximum drawdown | **NOT REPORTED IN SOURCE** |
| Win rate / profit factor | **NOT REPORTED IN SOURCE** |
| Real-data backtest | **NOT PERFORMED** — the authors name this as required future work |
| Multi-day / multi-instrument parameter stability | **NOT TESTED** — one stock, one day |
| Latency and its effect on fills | Not modelled |
| Fees and rebates | Not modelled |

The paper also reports an efficient-frontier analysis (Table 6) exploring inventory penalisation, and
notes a figure of **47** from an extrapolation in that context; the surrounding text states the
simulated backtest "must be completed by a backtest on real data" before such numbers carry weight.
This entry does not reproduce that extrapolation.

## 5. Where the model applies vs. fails

**Applies when:**
- **Tick size is economically meaningful** relative to volatility, so that "post at best" versus
  "improve by one tick" is a real decision with real queue-priority consequences. This is the model's
  distinctive advantage over the continuous-price parent entries.
- Spread dynamics are well described by a finite Markov chain — i.e. the spread genuinely takes a
  small number of discrete values, as in most liquid equities.
- The desk can act on both sides of the book: posting passively *and* crossing when needed.
- Calibration data is available. The paper supplies procedures for all three parameter sets, which
  is more than the parent entries do.

**Fails or needs care when:**
- **Absolute performance is inferred from the simulation.** The authors explicitly disclaim it.
- Parameters are ported across instruments or days. Calibration is one stock, one day.
- The reference price is not a martingale over the horizon — one of the two assumptions that makes
  the problem tractable, and precisely the exposure a market maker gets hurt by.
- Informed flow dominates. Execution intensities depend on the spread and the agent's quotes, but a
  fill conveys no directional information. See `../order-flow-imbalance-price-impact/`.
- Queue position *within* a price level matters more than level choice — the most competitive books.
- Latency is binding. Not modelled at all.

## 6. Decay and current status

**`decay_status: intact`** — as a model, with the same caveat as its siblings.

The mathematics is unaffected by time. What makes this entry durable is that it models two things
the other market-making entries cannot: **discrete ticks with queue priority**, and **the option to
cross the spread**. Both are permanent features of real venues, so the framework remains the right
one for markets where the tick binds.

The competitive environment has moved on in the usual way — latency and adverse-selection prediction
now dominate professional market making, and neither is in this model. The tick-level placement
decision the paper formalises is now table stakes rather than an edge.

**How to use this entry.** As the market-making model to reach for when **tick size binds** and
queue priority is a live decision — the case where Avellaneda–Stoikov's continuous-price
approximation is least appropriate. Take three things from it specifically: (1) the calibration
procedures, which the parent entries lack; (2) the finding that most of the risk-adjusted gain comes
from intelligent limit placement rather than from market orders, which should shape build order; and
(3) the inventory result — a market-order escape hatch increases inventory tolerance rather than
reducing inventory. Pair it with `../gueant-lehalle-fernandez-tapia-bounded-inventory/` for the
stationary inventory skew and `../order-flow-imbalance-price-impact/` for the missing
adverse-selection layer.
