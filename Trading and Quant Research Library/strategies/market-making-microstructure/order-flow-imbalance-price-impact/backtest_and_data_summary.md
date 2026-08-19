# Backtest & Data Summary — Order Flow Imbalance & Price Impact

## Verification

All figures below were read directly from Cont, R., Kukanov, A., & Stoikov, S., "The price impact of
order book events," **arXiv:1011.6402, draft dated March 2011**, retrieved in-session from
`arxiv.org/pdf/1011.6402`. Published as *Journal of Financial Econometrics* 12(1), 47–88 (2014); the
published version was not consulted. **Evidence grade: `verified-primary`** for the arXiv draft.

---

## 1. Data sample

| Field | Value |
|---|---|
| Data source | **NYSE TAQ** — consolidated trades and consolidated quotes |
| Data level | **Level-1** (best bid/ask only), not full order book depth |
| Sample period | **April 2010** — one calendar month |
| Universe | **50 US stocks** |
| Sampling grid | Uniform, **Δt = 10 seconds** |
| Estimation windows | Separate regression per **half-hour** subsample |
| Robustness | Repeated on a subsample of stocks at other timescales |

The choice of a 10-second grid is justified in the paper by the observation that autocorrelations
"typically vanish after 10 seconds" in this data.

## 2. Headline results

### 2.1 OFI explains price changes; trade imbalance largely does not

Three regressions, estimated per half-hour subsample:

```
(8a)   ΔP_k = α̂_i    + β̂_i · OFI_k                + ε̂_k
(8b)   ΔP_k = α̂_T,i  + β̂_T,i · TI_k               + ε̂_T,k
(8c)   ΔP_k = α̂_D,i  + θ̂_O,i · OFI_k + θ̂_T,i · TI_k + ε̂_D,k
```

| Specification | Average R² |
|---|---|
| **Order flow imbalance (OFI)** | **65%** |
| **Trade imbalance (TI)** | **32%** |

When both variables are included together (8c):

| Finding | Value |
|---|---|
| Average t-statistic of `TI` | **falls by a factor of four** |
| Fraction of subsamples where `θ̂_T` is significant | **31%** |
| Dependence on `OFI` | "remains convincingly strong" |

> This is the paper's central empirical claim, and it is a strong one. A single-parameter linear
> model on an observable variable explains **two-thirds of short-horizon price variation**, and
> subsumes the trade-based measures that most of the prior literature relied on. The reason is
> mechanical: OFI counts cancellations and limit-order additions, which trade imbalance cannot see,
> and those events dominate modern order flow.

### 2.2 Per-stock example (Table 2, AMD)

| Quantity | Value |
|---|---|
| `α̂` | −0.0032 (t = −0.17) |
| `β̂` (price impact coefficient) | 0.0008 (t = 9.96) |
| `γ̂_Q` | 1.4E-07 (t = 0.68) |
| **R²** | **64%** |
| Fraction of subsamples rejecting `{β ≠ 0}` | 98% |
| Fraction rejecting `{α ≠ 0}` | 0% |

The intercept is indistinguishable from zero (0% of subsamples reject), the OFI slope is
overwhelmingly significant (98%), and R² sits at the sample average. This is what a well-specified
linear relation looks like.

### 2.3 Impact is inversely proportional to depth

The price impact coefficient `β` exhibits intraday seasonality matching known patterns in spreads,
depth and volatility. The paper links this directly to **market depth**:

```
β  ∝  1 / D
```

The significance is methodological: intraday variation in price impact and volatility is explained
using **only observable quantities** — order flow imbalance and market depth — "as opposed to
unobservable parameters previously invoked in the literature, such as information asymmetry or
informativeness of trades."

### 2.4 The square-root law is demoted to an artefact

The linear OFI model plus a scaling argument reproduces the empirically observed square-root
relation between price changes and trade volume. The authors' verdict: the relation "is not robust
and is a statistical artifact due to the aggregation of data," and price-vs-volume is "noisy and
less robust than the one based on order flow imbalance."

## 3. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio of any trading strategy | **NOT REPORTED IN SOURCE** — this is a price-impact study, not a strategy |
| Drawdown / win rate / profit factor | **NOT REPORTED IN SOURCE** |
| **Predictive (lead-lag) R²** | **NOT REPORTED** — see the caveat below |
| Transaction costs | Not applicable |
| Results below 10-second scale | Not presented in the consulted draft |

> ⚠️ **The most important caveat in this entry.** The 65% R² is **contemporaneous**: OFI over
> interval `k` is regressed against the price change over **the same interval** `k`. This is a
> decomposition of what moved the price, not a forecast of what it will do next. Anyone reading 65%
> as "OFI predicts two-thirds of future returns" has misread the paper. Converting OFI into a
> tradable signal requires establishing that OFI *leads* price at some horizon, which this study does
> not claim and does not test.
>
> That does not make it useless for trading — quite the opposite. For a **market maker**, the
> contemporaneous relation is exactly what matters: it says that when you are filled against
> prevailing order flow, the price is moving away from you *at that moment*. That is adverse
> selection, measured.

## 3.1 Implementation status (run in-session)

The reference pipeline in `source_or_pseudo_code.txt` was executed on synthetic Level-1 quote
streams. **It confirms the code, not the paper's empirical claims** — and the distinction matters:

| Confirmed | Not reproduced |
|---|---|
| Pipeline runs end to end (contributions → 10s aggregation → per-half-hour regressions) | The **65% R²** — synthetic runs gave 0.54 and 0.19, which are properties of the simulator, not evidence about markets |
| `β` positive and significant in **100%** of windows (median t = 4.9 and 12.3) | The **32%** trade-imbalance figure — synthetic trades were price-independent by construction |
| `α` near zero, matching the paper's AMD result (0% of subsamples reject `α ≠ 0`) | The `β ∝ 1/D` depth scaling — needs genuine cross-window depth variation |
| OFI dominates trade imbalance jointly (t(OFI) = 21.5, t(TI) insignificant) | — |

Only real TAQ data can test the headline claims. This entry does not claim otherwise.

### An implementation finding worth carrying forward

In the first synthetic run the quote price moved on nearly every update, which makes the
**price-change branch** of the contribution rule fire constantly — so `e_n` takes the **full queue
size** (~500) rather than the size *delta* (~40). OFI inflated by roughly two orders of magnitude and
the fitted `β` shrank by the same factor (1.9e-06 against a generator coefficient of 1e-03).

> **`β` is not a transferable constant.** Its scale depends on how often the quote price moves in
> your data, which varies by instrument, tick size, venue, and sampling frequency. Always
> re-estimate `β` on the exact configuration you intend to trade. Porting a `β` across instruments
> or timescales will mis-size every quote adjustment built on it.

## 4. Where the model applies vs. fails

**Applies when:**
- Horizons are short — seconds to minutes. The relation is documented at a 10-second scale.
- The instrument is liquid with a well-populated best-quote queue.
- Level-1 data is available. Notably the paper shows full depth is **not** required, which is a
  practical gift: OFI is computable from cheap data.
- You need an adverse-selection input to a market-making model. This is the natural companion to
  `../avellaneda-stoikov-optimal-quoting/` and
  `../gueant-lehalle-fernandez-tapia-bounded-inventory/`, neither of which has any concept of
  informed flow.
- Depth is being tracked, so the `β ∝ 1/D` scaling can be applied rather than assuming a fixed
  impact coefficient.

**Fails or requires care when:**
- **Used as a return forecast.** See the contemporaneity caveat above.
- Activity concentrates away from the best quotes. OFI as defined is a best-quote measure; large
  hidden or deep-book activity is invisible.
- Tick size is large relative to volatility, so the mid-price is pinned and quantised — the linear
  relation has little variation to explain.
- Extreme events. April 2010 is a normal-conditions month; the sample ends before the 6 May 2010
  Flash Crash.
- Sub-second horizons, where queue position and latency dominate and the 10-second regularity may
  not carry over.
- Markets other than US equities — no evidence is presented for futures, FX, or crypto.

## 5. Decay and current status

**`decay_status: intact`** — with the qualification that "intact" here means the *relation* holds,
not that an *edge* remains.

- **The mechanism is structural.** Prices move when the queue at the best quote is depleted or
  replenished. That is not an anomaly to be arbitraged away; it is a description of how a limit order
  book works. The linear OFI–price relation should hold as long as markets are organised as
  continuous double auctions.
- **The measurement has become standard.** OFI is now a staple input in execution algorithms,
  short-horizon alpha models, and market-making quote adjustment. Its widespread adoption is
  evidence that it works, and simultaneously means that trading naively on it is competing against
  everyone else computing the same number from the same feed.
- **The competitive frontier has moved to speed and depth.** Whatever standalone predictive content
  OFI has at a 10-second horizon is heavily contested; the surviving applications are (a) as a
  *defensive* skew in a quoting model, and (b) as one feature among many in a richer
  microstructure model using full depth, queue position, and multi-level imbalance.
- **The square-root-law critique remains underappreciated.** Execution cost models across the
  industry still rest on square-root impact. This paper's argument that it is an aggregation artefact
  of an underlying linear mechanism is a live methodological issue, not settled history.

**How to use this entry.** As the adverse-selection layer the market-making entries explicitly lack.
Compute OFI at the best quotes, scale by depth, and skew quotes against prevailing flow — that is a
defensive use of a contemporaneous relation and does not require any predictive claim. Treat any
attempt to use OFI as a standalone directional signal as requiring its own lead-lag evidence, which
this paper does not supply.
