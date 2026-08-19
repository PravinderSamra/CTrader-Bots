# Backtest & Data Summary — Pairs Trading (Distance Method)

## Verification

All figures below were read directly from the full text of Gatev, Goetzmann & Rouwenhorst (2006),
*Review of Financial Studies* 19(3), 797–827, retrieved in-session from
`stat.wharton.upenn.edu/~steele/Courses/434/434Context/PairsTrading/PairsTradingGGR.pdf`.
Table references are to that document. **Evidence grade: `verified-primary`.**

Returns are **monthly excess returns**, not annualised, unless stated otherwise.

---

## 1. Data sample

| Field | Value |
|---|---|
| Data source | CRSP daily files |
| Sample period | July 1963 – December 2002 (474 monthly observations); pairs formed from 1962 |
| Universe | All liquid CRSP stocks; stocks with missing trading days in the formation period screened out |
| Frequency | Daily prices; monthly return aggregation |
| Formation period | 12 months |
| Trading period | 6 months, overlapping (a new cohort starts each month) |
| Asset class | US equities |
| Avg. pairs in "all-pairs" portfolio | 2,057 |

Overlapping trading periods mean the monthly return series is autocorrelated by construction; GGR
correct with **Newey–West standard errors, six-lag**. Reported monthly serial correlation is 0.14
(top 5) and 0.24 (top 20).

## 2. Headline performance — Table 1

### Panel A — no waiting (open at close of divergence day)

| Metric | Top 5 | Top 20 | Pairs 101–120 | All pairs |
|---|---|---|---|---|
| Avg. monthly excess return (fully invested) | **1.308%** | **1.436%** | 1.081% | 1.104% |
| Newey–West standard error | 0.148% | 0.124% | 0.094% | 0.099% |
| t-statistic | 8.84 | 11.56 | 11.54 | 11.16 |
| Median | 1.194% | 1.235% | 0.955% | 0.728% |
| Standard deviation | 2.280% | 1.688% | 1.540% | 1.670% |
| Skewness | 0.62 | 1.39 | 1.34 | 3.42 |
| Kurtosis | 7.81 | 10.54 | 10.30 | 25.25 |
| Minimum monthly | −10.573% | −6.629% | −3.857% | −2.721% |
| Maximum monthly | 14.716% | 13.295% | 12.684% | 17.178% |
| % months negative | 26% | 15% | 21% | 17% |
| Avg. monthly excess return (committed capital) | **0.784%** | **0.805%** | 0.679% | 0.614% |

### Panel B — one-day waiting rule (the honest number)

Positions opened the day *after* divergence and closed the day *after* convergence, to strip out
bid–ask bounce.

| Metric | Top 5 | Top 20 | Pairs 101–120 | All pairs |
|---|---|---|---|---|
| Avg. monthly return (fully invested) | **0.745%** | **0.895%** | 0.795% | 0.715% |
| Newey–West standard error | 0.119% | 0.096% | 0.085% | 0.090% |
| t-statistic | 6.26 | 9.29 | 9.40 | 7.92 |
| Standard deviation | 2.101% | 1.527% | 1.438% | 1.577% |
| Skewness | 0.34 | 1.45 | 0.98 | 3.32 |
| Kurtosis | 10.64 | 16.13 | 7.78 | 25.66 |
| Minimum monthly | −12.628% | −8.218% | −4.266% | −2.951% |
| Maximum monthly | 14.350% | 13.490% | 10.464% | 16.325% |
| % months negative | 35% | 23% | 28% | 32% |
| Avg. excess return (committed capital) | **0.463%** | **0.520%** | 0.503% | 0.396% |

Waiting one day costs 30–55 bp per month on the fully-invested basis and 20–35 bp on committed
capital. That gap is the size of the microstructure illusion in the raw numbers.

## 3. Risk-adjusted performance — Table 4

Computed on the **wait-one-day** portfolios.

| Metric | Top 5 | Top 20 | 20 after top 100 | All | S&P 500 equity premium |
|---|---|---|---|---|---|
| Mean monthly excess return | 0.745% | 0.895% | 0.795% | 0.715% | 0.410% |
| Standard deviation | 2.101% | 1.527% | 1.438% | 1.577% | 4.509% |
| **Sharpe ratio (monthly)** | **0.35** | **0.59** | 0.55 | 0.45 | **0.09** |
| Monthly serial correlation | 0.14 | 0.24 | 0.19 | 0.12 | 0.05 |

GGR's summary: pairs-trading excess return is about twice the S&P 500's with one-half to one-third
of the standard deviation, so **Sharpe ratios are four to six times the market's**.

> ⚠️ These Sharpe ratios are **monthly**. Naïve annualisation (×√12) gives ≈2.04 for the top 20,
> but that overstates the truth because the overlapping-window construction leaves serial
> correlation of 0.24 in the series. Quote the monthly figure, or annualise with a
> serial-correlation correction. This library records the monthly number as published.

### Five-factor intercepts (Fama–French 3 + momentum + short-term reversal)

| Portfolio | Monthly alpha | t-stat | Market beta | t-stat |
|---|---|---|---|---|
| Top 5 | 0.545% | 3.81 | −0.067 | −1.03 |
| Top 20 | **0.764%** | **7.08** | −0.032 | −0.64 |
| 20 after top 100 | 0.714% | 8.66 | −0.077 | −1.77 |
| All | 0.512% | 5.30 | −0.145 | −3.10 |

The edge survives every standard factor control, and the market exposure is insignificant for the
concentrated portfolios — the market-neutrality claim holds empirically, not just by construction.

## 4. Trading statistics — Table 2

| Metric | Top 5 | Top 20 | 101–120 | All |
|---|---|---|---|---|
| Avg. price deviation triggering open | 4.758% | 5.284% | 7.560% | 16.888% |
| Avg. pairs traded per 6-month period | 4.81 | 19.30 | 19.41 | 1,944.22 |
| Avg. round trips per pair | 2.02 | 1.96 | 1.78 | 1.62 |
| Std dev of round trips per pair | 0.62 | 0.40 | 0.27 | 0.16 |
| Avg. time a pair is open | 3.75 months | — | — | — |

Almost every selected pair opens at least once (4.81 of the top 5), and the average holding period
of 3.75 months makes this a **medium-term** strategy, not a high-frequency one — a point routinely
misunderstood by practitioners who treat "stat arb" as synonymous with intraday.

## 5. Transaction costs — the decisive section

GGR derive costs indirectly from their own waiting-rule experiment:

- Waiting one day costs **324 bp per six months**, spread across ~2 round trips per pair.
- That implies **162 bp per pair per round trip**, i.e. an estimated **effective spread of 81 bp**
  (70 bp for the all-pairs portfolio).
- This is *conservative*: Peterson & Fialkowski (1994) measured the average CRSP effective spread
  at 37 bp in 1991, and 91% of top-20 pair stocks are in the top five CRSP size deciles.

Applying it:

| Item | Value (per 6 months) |
|---|---|
| Gross profit range across portfolios | 437 – 549 bp |
| Estimated transaction cost (162 bp × 2 round trips) | 324 bp |
| **Net profit range** | **113 – 225 bp** |

GGR conclude these net profits are "both economically and statistically significant" relative to
the reported standard errors. This is the strongest form of the result: the edge survives a
deliberately pessimistic cost estimate.

## 6. Where the strategy thrives vs. fails

**Thrives when:**
- Substitute pairs are genuinely substitutable — same sector, same rate sensitivity, same demand
  drivers. The utility concentration in GGR's selections is not an accident.
- Dislocations are liquidity-driven rather than information-driven: index rebalances, forced
  unwinds, flow imbalances that reverse.
- Spread volatility is stable, so the formation-period `σ_S` is a valid estimate of trading-period
  risk.
- The arbitrage capital pool is thin. GGR link profits to a latent factor consistent with
  compensation for enforcing the Law of One Price — the payment shrinks as more capital competes.

**Fails when:**
- The divergence is fundamental. Mergers, accounting fraud, regulatory shocks, and secular business
  divergence produce spreads that never revert. The mechanical rule has no way to detect this and
  holds to the end of the window.
- Correlation structure breaks in a deleveraging event. **August 2007** is the canonical case: the
  quant-equity unwind hit convergence strategies simultaneously across funds because the crowd held
  the same relative-value positions and liquidated into each other.
- Costs and short-borrow are realistic-to-bad. The short leg needs locatable, affordable borrow;
  hard-to-borrow names are exactly the ones that diverge most.
- The spread's half-life exceeds the trading window, so positions get force-closed at a loss before
  convergence.

## 7. Decay and current status

**`decay_status: substantially-decayed`** — but the decay story is more subtle than usually told,
and GGR's own evidence points the other way.

### What GGR actually found about decay

**The in-sample subperiod split (Table 8) does show decay in raw returns.** Splitting at the end of
1988, the top-20 raw excess return drops from **118 bp/month to about 38 bp/month**. But GGR
explicitly reject the "arbitraged away" reading, because the *risk-adjusted* return falls by only
about a third — from **67 to 42 bp/month** — and stays significant in both halves
(**t = 4.41** and **t = 3.77**). Changes in factor exposures and factor volatilities explain part
of the raw decline, not the risk-adjusted persistence.

**GGR's true out-of-sample test is positive, not negative.** The authors circulated the first
working-paper draft in 1999 using data through 1998, then tested the unchanged model on
**1999–2002**. Result: the fully invested top-20 portfolio averaged **10.4% per annum**, annual
standard deviation **3.8%**, Newey–West t-statistic **4.82** — which they describe as "consistent
with the long-term, in-sample results." They note they deliberately did not adjust the strategy
between drafts, precisely to avoid data-snooping criticism.

> This matters for how the entry is used. The common claim that "GGR's pairs trading stopped
> working out of sample" is **not supported by GGR**. Their holdout period worked. The decay
> evidence comes from later authors and later data.

### Where the decay evidence actually comes from

- **Do & Faff (2010), "Does Simple Pairs Trading Still Work?", *Financial Analysts Journal* 66(4),
  83–95.** Extends the GGR methodology on later data and confirms a **continuing downward trend in
  profitability**, while finding the strategy performs strongly during periods of prolonged
  turbulence, including the global financial crisis. Refinements to the pair-selection algorithm
  recovered meaningful profit (reported as ~22 bp/month for bank stocks).
- **Do & Faff (2012), "Are Pairs Trading Profits Robust to Trading Costs?", *Journal of Financial
  Research*.** The follow-up that puts realistic costs against the later-sample returns — the
  binding constraint on whether the residual edge is implementable.

*(These two are recorded at `verified-secondary` — the abstracts and reported findings were checked
in-session, but the full texts were not retrieved. Wave 2 should upgrade them to
`verified-primary` and ingest Do & Faff as its own entry, since the refined selection algorithm is a
distinct method.)*

### Mechanism of the decline

The decline does not require the original effect to have been spurious — it survived a genuine
holdout. Two structural changes are sufficient to explain it:

1. **Costs collapsed, and so did the gross edge that needed covering.** GGR's own indirect estimate
   was an 81 bp effective spread. Decimalisation and electronic execution took effective spreads
   toward single digits. That helps the strategy — but it equally lets far more participants
   compete for the same convergence, and the divergences now get closed before a 2σ daily-close
   trigger even fires.
2. **The arbitrage capital enforcing the Law of One Price grew by orders of magnitude.** If the
   profits are compensation for that enforcement — GGR's own interpretation — then the payment
   falls as the supply of enforcers rises. GGR anticipated this, observing that the latent factor
   driving pairs profitability "has been relatively dormant recently."

### How to use this entry

Treat it as the foundational reference for how a convergence strategy is constructed, evaluated,
and cost-adjusted — and as the correct baseline against which any modern stat-arb claim must be
benchmarked. Do not treat the 2σ daily-close distance rule as a live signal on liquid US
large-caps. The current-generation descendants (cointegration selection, OU-band optimal stopping,
factor-residual stat arb, and Do & Faff's refined selection) are queued for Wave 2 and should be
compared head-to-head against these numbers.
