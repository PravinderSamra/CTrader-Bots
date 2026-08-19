# Optimal Mean-Reversion Bands (OU Double Stopping with Costs & Stop-Loss)

**Category:** Statistical Arbitrage & Relative Value (Wave 2 depth entry)
**Anchor paper:** Leung, T., & Li, X. (2015). "Optimal Mean Reversion Trading with Transaction Costs
and Stop-Loss Exit." *International Journal of Theoretical and Applied Finance*, 18(3).
arXiv:1411.5062v3 (14 May 2015).
**Parent entries:** `../pairs-trading-distance-method/`, `../factor-residual-statistical-arbitrage/`

---

## 1. Abstract / summary of the core edge

Both existing convergence entries in this library set their trading thresholds by assertion. Gatev,
Goetzmann & Rouwenhorst open at two historical standard deviations — and note in a footnote that
"the optimal trigger point in terms of profitability may actually be much higher." Avellaneda & Lee
open at an s-score of 1.25, fitted on 2000–2004 data. Neither derives its bands; both admit as much.

This paper derives them. Given a spread following an Ornstein–Uhlenbeck process, transaction costs,
and a discount rate, it solves the **optimal double stopping problem** — when to enter, and then when
to exit — and produces the entry and exit levels as the solution to a rigorous optimisation rather
than as a fitted parameter.

The results are not what the standard practice would predict, and that is the point of the entry.

**Finding 1 — the entry region is a *bounded interval*, and the wait region is disconnected.**
With a stop-loss in place, it is optimal to enter only when the spread lies inside a bounded band
that sits **strictly above** the stop-loss level. You wait if the spread is too high — expected, that
is the usual "not cheap enough" logic — but you **also wait if it is too close to the stop-loss**.

The authors' reasoning is exactly right and rarely implemented:

> "it is optimal to wait if the current price is too high or too close to the lower stop-loss level.
> This is intuitive since entering the market close to stop-loss implies a high chance of exiting at
> a loss afterwards. As a result, the delay region (complement of the entry region) is disconnected."

This inverts standard practice. A distance-method or s-score system opens **more** eagerly the
further the spread diverges. This paper says that beyond a point you should open **less** eagerly,
because a spread that has moved far enough is more likely to hit your stop than to revert in time.

**Finding 2 — the stop-loss and the take-profit are coupled.** "A higher stop-loss level always
implies a lower optimal take-profit level." You cannot set a stop and a target independently; moving
one changes where the other should be. The paper shows the optimal liquidation level decreases with
the stop-loss level until the two coincide — at which point the trade is not worth taking.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Leung & Li — arXiv:1411.5062v3 (verified in-session) | paper | https://arxiv.org/pdf/1411.5062 |
| arXiv abstract page | paper | https://arxiv.org/abs/1411.5062 |
| Published: *IJTAF* 18(3), 2015 | paper | https://www.worldscientific.com/doi/abs/10.1142/S021902491550020X |
| Leung & Li — *Optimal Mean Reversion Trading* (World Scientific, 2016), the book-length treatment | book | https://www.worldscientific.com/worldscibooks/10.1142/9839 |
| Elliott, van der Hoek & Malcolm (2005) — earlier OU pairs-trading formulation | paper | https://www.tandfonline.com/doi/abs/10.1080/14697680500149370 |

## 3. Mathematical foundation

### 3.1 The spread process

The traded portfolio value `X_t` follows an Ornstein–Uhlenbeck process:

```
dX_t = μ(θ − X_t) dt + σ dB_t
```

with mean-reversion speed `μ`, long-run mean `θ`, and volatility `σ`. Note the model allows a
**non-zero long-run mean** and does not assume the spread reverts to zero — a real improvement over
implementations that centre on zero by construction.

### 3.2 The optimal double stopping problem

Two nested optimal stopping problems. **First, the exit problem** — given an existing position,
when to liquidate:

```
V(x) = sup_τ  E_x[ e^{−rτ} ( X_τ − c ) ]
```

where `c` is the transaction cost of closing and `r > 0` is the investor's subjective discount rate.
`V(x)` is the expected liquidation value of holding the spread at level `x`.

**Then the entry problem** — the investor can choose when to open, or not to open at all:

```
J(x) = sup_ν  E_x[ e^{−r̂ν} ( V(X_ν) − X_ν − ĉ ) ]
```

The entry reward is `V(X_ν) − X_ν − ĉ`: the value of the position you would acquire, minus what you
pay for it, minus the entry cost. This nesting — the entry problem's reward function contains the
exit problem's value function — is what makes it a *double* stopping problem and what most practical
implementations skip entirely.

### 3.3 The solution structure

The exit rule takes the form of a threshold: liquidate the first time the spread reaches `b*`,

```
τ* = inf{ t ≥ 0 : X_t ≥ b* }
```

with `b*` characterised as the solution to an equation involving `F` and `G`, the classical
increasing and decreasing solutions of the OU differential equation. The optimal levels are found by
maximising the relevant expectation over the candidate interval `[a*, b*]`.

The discount rate `r` matters more than it looks. It is what makes waiting costly: without
discounting, a mean-reverting spread's optimal policy degenerates because there is no penalty for
waiting arbitrarily long for a better entry.

### 3.4 With a stop-loss constraint

Adding a stop-loss level `L` changes the geometry qualitatively rather than quantitatively:

| Without stop-loss | With stop-loss |
|---|---|
| Entry region is a half-line (enter when cheap enough) | **Entry region is a bounded interval strictly above `L`** |
| Wait region is connected | **Wait region is disconnected** |
| Take-profit set independently | **Take-profit decreases as `L` rises** |

The disconnected wait region is the structural insight. It says the standard mental model — "the
further the spread diverges, the better the trade" — is wrong in the presence of a stop-loss, because
a far-diverged spread is closer to the stop and has a materially higher probability of being
stopped out before reverting.

### 3.5 Relationship to the parent entries

This is the theoretically correct version of the question the parent entries answer by assertion:

| Entry | Trigger | Basis |
|---|---|---|
| GGR distance method | 2 historical σ | Chosen arbitrarily; authors note the optimum "may be much higher" |
| Avellaneda–Lee | s-score 1.25 / 0.75 / 0.50 | Fitted on 2000–2004 simulations |
| **Leung & Li** | `[a*, b*]` from optimal double stopping | **Derived**, given `μ`, `θ`, `σ`, `c`, `r`, `L` |

The paper explicitly contrasts its result with "the conventional practice… where the entry/exit
levels are set as ±1 standard deviation from the long-run mean."

## 4. Known criticisms and limitations

1. **The OU assumption is the whole model.** If the spread is not OU — if `μ`, `θ` or `σ` drift, if
   the spread is regime-switching, or if the cointegrating relationship breaks — the derived bands
   are optimal for a process that is not the one being traded. This is a *stronger* dependence on
   the model than the ad-hoc thresholds have, and it cuts both ways: more rigour, less robustness.
2. **Parameters must be estimated, and `μ` is estimated poorly.** Mean-reversion speed is
   notoriously hard to pin down on short samples (see the κ bias documented in the factor-residual
   entry: a median estimate of 33.8 against a true 12.0 on a 60-day window). The bands inherit that
   estimation error.
3. **The discount rate `r` is subjective and the results depend on it.** It is a preference
   parameter, not a market observable. Different `r` gives different bands, and there is no
   principled way to choose it beyond the operator's own opportunity cost.
4. **Single spread, no portfolio.** The framework optimises one spread in isolation. Real stat-arb
   books hold hundreds of simultaneous positions with shared capital and correlated residuals; the
   paper says nothing about allocation across them.
5. **No leverage, funding, or borrow modelling.** Transaction cost is a single constant `c` per
   trade. The short leg's borrow cost, financing, and margin are absent.
6. **The empirical section is illustrative, not a backtest.** Two ETF pairs over ten months
   demonstrate that the OU fit is reasonable. That is a model-adequacy check, not a demonstration
   that trading these bands is profitable — and the paper does not claim otherwise.
