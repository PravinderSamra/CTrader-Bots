# Backtest & Data Summary — Optimal Mean-Reversion Bands

## Verification

All figures below were read directly from Leung, T., & Li, X., "Optimal Mean Reversion Trading with
Transaction Costs and Stop-Loss Exit," **arXiv:1411.5062v3, dated 14 May 2015**, retrieved
in-session from `arxiv.org/pdf/1411.5062`. Published in *International Journal of Theoretical and
Applied Finance* 18(3), 2015; the published version was not consulted.
**Evidence grade: `verified-primary`** for the arXiv version.

> **This is a theoretical paper with an illustrative empirical section — not a backtest.** It derives
> optimal entry and exit levels and demonstrates that real ETF spreads fit the OU model adequately.
> It does **not** report trading performance, and this entry does not pretend it does.

---

## 1. Empirical illustration — data sample

| Field | Value |
|---|---|
| Instruments | **GLD–GDX** and **GLD–SLV** ETF pairs |
| — GLD | SPDR Gold Trust (gold bullion) |
| — GDX | Market Vectors Gold Miners (NYSE Arca Gold Miners Index) |
| — SLV | iShares Silver Trust (silver) |
| Sample period | **August 2011 – May 2012** |
| Observations | **n = 200**, `Δt = 1/252` (daily) |
| Estimation method | **Maximum likelihood estimation (MLE)** of the OU parameters |

The portfolio construction is `$1` in GLD against `−$B` in the second ETF, with `B` chosen to
maximise the average log-likelihood of the OU fit.

## 2. Estimated parameters

| Pair | MLE-optimal `B*` | Portfolio |
|---|---|---|
| **GLD–GDX** | **0.454** | $1 GLD, −$0.454 GDX |
| **GLD–SLV** | **0.493** | $1 GLD, −$0.493 SLV |

MLE estimates of the OU parameters (Table 1), columns `θ̂`, `μ̂`, `σ̂`, `ℓ̂`:

| Pair | Row | `θ̂` | `μ̂` | `σ̂` | Avg. log-likelihood `ℓ̂` |
|---|---|---|---|---|---|
| GLD–GDX | empirical | 0.5388 | **16.6677** | 0.1599 | 3.2117 |
| GLD–GDX | simulated | 0.5425 | **14.3893** | 0.1727 | 3.1304 |
| GLD–SLV | empirical | 0.5680 | **33.4593** | 0.1384 | **3.3882** |
| GLD–SLV | simulated | 0.5629 | **28.8548** | 0.1370 | 3.3898 |

### The model-adequacy check, and what it actually shows

The paper's validation procedure is worth noting because it is a good one and cheap to copy:
estimate OU parameters from empirical prices, **simulate** new paths from those estimates, then
re-run MLE on the simulated paths. If the empirical process is genuinely OU, the two parameter sets
should agree.

For `θ` and `σ` they agree closely — `θ` differs by 0.7% (GLD–GDX) and 0.9% (GLD–SLV), `σ` by 8% and
1% — which the authors reasonably read as evidence that "the empirical price process fits well to
the OU model."

> **But `μ̂` is the conspicuous exception in both pairs.** GLD–GDX: 16.6677 → 14.3893, a **13.7%**
> gap. GLD–SLV: 33.4593 → 28.8548, a **13.8%** gap. The mean-reversion speed is by a wide margin the
> least stable parameter under the paper's own consistency check, and it is precisely the parameter
> the optimal bands depend on most.
>
> This corroborates — from an entirely different estimator and dataset — the instability documented
> independently in this library's factor-residual entry, where the AR(1)-based `κ` estimator returned
> a median of 33.8 against a true 12.0 on a 60-day window. **The two findings agree that
> mean-reversion speed is hard to pin down; they do not agree on the direction of the error**
> (Leung & Li's refit comes in *lower* than the empirical estimate, the factor-residual test came in
> *higher* than truth), and the setups differ enough — different estimator, sample length, and
> residual construction — that no single bias direction should be inferred. The safe conclusion is
> the conservative one: **treat any point estimate of `μ` as carrying substantial uncertainty, and
> check how far the derived bands move across its plausible range before trading them.**

Note also that `ℓ̂` for GLD–SLV (3.3882) exceeds GLD–GDX (3.2117), which the authors take to indicate
a better OU fit for the silver pair — a sensible and cheap pair-selection criterion in its own right,
and one neither parent entry uses.

## 3. The structural results

These, rather than any performance number, are what the entry is for.

| Result | Statement |
|---|---|
| **Entry region shape (with stop-loss)** | A **bounded interval** lying **strictly above** the stop-loss level `L` |
| **Wait region shape** | **Disconnected** — wait if the spread is too high *or* too close to `L` |
| **Stop-loss / take-profit coupling** | "A higher stop-loss level always implies a lower optimal take-profit level" |
| **Degenerate case** | The optimal liquidation level decreases with `L` until the two coincide |
| **Exit rule** | A threshold: `τ* = inf{t ≥ 0 : X_t ≥ b*}` |

### Why the disconnected wait region matters practically

Every convergence system in common use — including both parent entries — becomes **more** eager to
enter as the spread diverges further. This paper says that is wrong once a stop-loss exists: past a
point, a further-diverged spread is closer to the stop and more likely to be stopped out than to
revert in time. The optimal policy therefore **declines to enter** in that zone.

A practitioner running 2σ or s-score bands with a stop-loss is, in this framework, systematically
taking the worst trades in the distribution — the ones nearest the stop.

## 3.1 Independent reproduction (run in-session)

The paper reports no performance figures, but its **structural** claims are testable. Both were
reproduced numerically using the paper's own GLD–SLV parameters (`θ = 0.5680, μ = 33.4593,
σ = 0.1384`, `r = 0.05`, costs 0.0005 per side; equilibrium sd = 0.0169), solving for the exit level
and entry band **jointly** at each stop-loss:

| Stop-loss | `b*` | `b*` in eq. sd | Entry band | Band width |
|---|---|---|---|---|
| none | 0.5919 | **1.41** | [0.5003, 0.5846] | — |
| 0.5400 | 0.5865 | **1.09** | [0.5410, 0.5714] | 0.0304 |
| 0.5450 | 0.5865 | **1.09** | [0.5460, 0.5652] | 0.0192 |
| 0.5500 | 0.5838 | **0.94** | [0.5509, 0.5641] | 0.0132 |
| 0.5550 | 0.5731 | **0.30** | [0.5558, 0.5621] | 0.0063 |

**Both structural results reproduce:**

1. **The take-profit falls as the stop rises** — `b*` declines monotonically from 1.41 to 0.30
   equilibrium standard deviations. This is the paper's "a higher stop-loss level always implies a
   lower optimal take-profit level," recovered independently.
2. **The entry region is bounded and narrows toward nothing** — its width collapses from 0.0304 to
   0.0063 as the stop is raised, matching the paper's statement that the optimal liquidation level
   decreases with the stop-loss "until they coincide," at which point the trade is not worth taking.

A second, higher-resolution run (2,000 simulation paths, finer grid) confirms the same structure with
somewhat different levels:

| Stop-loss | `b*` in eq. sd | Entry band | Band width | (lo − stop)/sd |
|---|---|---|---|---|
| none | 1.60 | [0.5003, 0.5891] | — | — |
| 0.5400 | 0.90 | [0.5403, 0.5714] | 0.0311 | 0.02 |
| 0.5450 | 0.80 | [0.5453, 0.5681] | 0.0228 | 0.02 |
| 0.5500 | 0.70 | [0.5503, 0.5654] | 0.0151 | 0.02 |
| 0.5550 | 0.70 | [0.5552, 0.5646] | 0.0094 | 0.01 |

> **What reproduced, and what did not.**
>
> **Robust across both runs:** `b*` declines monotonically as the stop rises, and the entry band
> narrows steadily toward zero width. Both of the paper's headline structural claims hold under two
> independent resolutions.
>
> **NOT established by these experiments:** that the entry region's lower edge sits *strictly* above
> the stop. The coarse run measured a gap of 0.05–0.06 equilibrium sd; the finer run measured
> 0.01–0.02. **The gap shrinks as resolution improves**, which is the signature of a grid artefact
> rather than a real separation. This numerical approach therefore cannot confirm the paper's
> "strictly above the stop-loss level" result — it is consistent with it, but equally consistent with
> the boundary sitting at the stop. Confirming it properly requires solving the free-boundary problem
> analytically via the `F` and `G` functions, as the paper does, rather than by simulation on a grid.
>
> Recorded this way deliberately: the two runs disagreed, and the disagreement points the wrong way
> for the claim.

### Two implementation failures worth recording

Both are documented in the code file, because each is a trap a practitioner would plausibly hit:

- **Valuing an unresolved position at zero** collapses the value function and makes the entry region
  vanish at *every* parameter setting. A spread that has hit neither barrier has reverted toward
  `θ` and must be marked there.
- **Computing `b*` without reference to the stop, then using it in the stopped problem** produced
  `b* = 2.82` sd — a target so distant that the probability of reaching it before the stop fell to
  0.16–0.20, and **no entry region existed at any level**. That failure is itself a demonstration of
  the paper's central point: setting stop and target independently is incoherent, and the
  incoherence surfaces as a strategy with no viable entry at all.

### The `μ` estimator, quantified

The estimator was checked for consistency across sample sizes (30 independent samples each):

| `n` | mean `μ̂` | median | sd of `μ̂` | mean `θ̂` | mean `σ̂` |
|---|---|---|---|---|---|
| 200 | **40.873** | 40.442 | **14.561** | 0.5668 | 0.1392 |
| 1,000 | 34.075 | 34.057 | 4.523 | 0.5673 | 0.1378 |
| 5,000 | 33.181 | 33.135 | 1.740 | 0.5682 | 0.1384 |
| 50,000 | 33.407 | 33.411 | 0.706 | 0.5680 | 0.1382 |
| **truth** | **33.459** | — | — | **0.5680** | **0.1384** |

The estimator is consistent — it converges. But at **`n = 200`, the paper's own sample size**, `μ̂`
carries a standard deviation of **14.6 against a true value of 33.5** (a 44% coefficient of
variation) plus a **~22% upward bias in the mean**, while `θ` and `σ` are recovered to under 1%.

> This **settles the direction question** left open in §2 above. Small-sample OU speed estimates are
> biased **upward** and hugely dispersed — matching the independent finding in this library's
> factor-residual entry (median 33.8 against a true 12.0 on a 60-day window). The paper's Table 1
> refit landing *lower* than its empirical estimate is a single draw from this very wide
> distribution, not evidence of a downward bias. The practical implication stands and is now
> quantified: **at 200 observations, a `μ` point estimate is worth little on its own.**

## 4. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio | **NOT REPORTED IN SOURCE** |
| Annualised return | **NOT REPORTED IN SOURCE** |
| Maximum drawdown | **NOT REPORTED IN SOURCE** |
| Win rate / profit factor | **NOT REPORTED IN SOURCE** |
| Trading performance of the derived bands | **NOT TESTED IN SOURCE** |
| Comparison of derived bands vs. ±1σ practice, in P&L | **NOT PERFORMED** |

The paper contrasts its approach against "the conventional practice… where the entry/exit levels are
set as ±1 standard deviation from the long-run mean," but does **not** run a horse race between the
two. That comparison is the obvious and still-missing empirical test, and it is queued as a Wave 6
adversarial-review item for this library.

## 5. Where the framework applies vs. fails

**Applies when:**
- The spread genuinely is OU — verified, not assumed. The paper's own simulate-and-refit procedure is
  the right check and is cheap to run.
- Mean reversion is fast relative to the intended holding period, so `μ` is estimable and the
  discounting does not dominate.
- A stop-loss is actually in use. Without one, the framework simplifies and the distinctive
  disconnected-entry result disappears.
- Transaction costs are material enough to matter — which is when deriving bands beats guessing them.
- One spread is being optimised at a time, with capital not binding across positions.

**Fails when:**
- The cointegrating relationship breaks. The model has no mechanism to distinguish a temporary
  dislocation from a permanent regime change — the same fundamental limitation as every convergence
  strategy in this category.
- `μ` is badly estimated, which is the normal case on short windows. The bands inherit the error.
- Parameters drift. OU with constant `μ`, `θ`, `σ` is a strong assumption over any long sample.
- A portfolio of many spreads competes for capital — the framework is single-asset.
- Costs are more complex than a constant `c`: borrow fees, financing, and market impact are absent.

## 6. Decay and current status

**`decay_status: intact`.**

This is mathematics, not a measured anomaly, so it cannot decay in the way pairs trading did. The
optimal double stopping solution remains correct given its assumptions, and the two structural
findings — the bounded entry region above the stop-loss, and the stop-loss/take-profit coupling —
are properties of the problem rather than of a particular market period.

What has changed is the environment those bands are applied in. The underlying convergence edge that
makes any of this profitable has substantially decayed (see the parent entries, both graded
`substantially-decayed`). Optimal thresholds on a spread with no remaining edge produce optimally
sized nothing. This entry improves *how* a convergence strategy is executed; it does not restore the
edge that has been competed away.

**How to use this entry.** As the correct answer to "where do I put my bands," replacing the
2σ and s-score-1.25 conventions in the parent entries. Three concrete takeaways that do not require
implementing the full free-boundary solution:

1. **Stop and target must be set jointly**, never independently — raising the stop lowers the optimal
   target.
2. **Do not enter close to your stop.** The entry region is bounded below as well as above; the
   trades nearest the stop are the ones the optimal policy refuses.
3. **Check the OU fit before trusting any of it**, using the paper's simulate-and-refit procedure,
   and treat the `μ` estimate as the weakest link in the chain.
