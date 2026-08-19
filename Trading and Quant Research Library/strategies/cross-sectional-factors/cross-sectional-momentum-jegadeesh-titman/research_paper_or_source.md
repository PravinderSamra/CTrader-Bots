# Cross-Sectional Momentum (Relative Strength)

**Category:** Cross-Sectional Equity Factors
**Anchor paper:** Jegadeesh, N., & Titman, S. (1993). "Returns to Buying Winners and Selling Losers:
Implications for Stock Market Efficiency." *The Journal of Finance*, 48(1), 65–91.

---

## 1. Abstract / summary of the core edge

Rank stocks by their return over the past 3–12 months. Buy the top decile, short the bottom decile,
hold for 3–12 months. The winners keep winning.

This is the paper that made momentum a fact rather than a folk belief, and it remains one of the
most robust findings in empirical finance — surviving out-of-sample in later decades, in
international markets, across asset classes, and in data going back to the Victorian era.

The headline result over January 1965 – December 1989 on CRSP NYSE/AMEX stocks: the best of the 32
strategies tested — 12-month formation, 3-month holding — yields **1.31% per month**, rising to
**1.49% per month** when a one-week gap is inserted between formation and holding. The 6-month
formation strategies deliver **about 1% per month regardless of holding period**.

What makes the paper important is not the return but the diagnosis. Jegadeesh and Titman go looking
for the mundane explanations and eliminate them one at a time:

- **It is not systematic risk.** The winners-minus-losers portfolio has a **negative** beta.
- **It is not the short-term reversal of Lehmann (1990) and Lo & MacKinlay.** Momentum is a
  distinct, opposite-signed phenomenon at a different horizon; the 1-week gap version performs
  *better*, ruling out bid-ask bounce and short-horizon microstructure effects as the source.
- **It is not size or a lead-lag effect in factor returns.** The decomposition in the paper's
  Section III attributes the profits to the idiosyncratic component of returns, not to serial
  correlation in common factors.

And then the finding that constrains every theory built on top of it: **the profits reverse.**
Cumulative returns to the zero-cost portfolio peak at **9.5% at the end of 12 months** and decay to
about **4% by month 36**. The strategy does not select stocks with permanently higher expected
returns; it captures a temporary price movement that partially unwinds.

## 2. Source links

| Source | Type | Link |
|---|---|---|
| Jegadeesh & Titman (1993), Journal of Finance — full text (verified in-session) | paper | https://www.bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf |
| JSTOR record | paper | https://www.jstor.org/stable/2328882 |
| Jegadeesh & Titman (2001) — the out-of-sample confirmation | paper | https://onlinelibrary.wiley.com/doi/10.1111/0022-1082.00342 |
| Fama & French (2012) — international evidence | paper | https://www.sciencedirect.com/science/article/abs/pii/S0304405X12000931 |
| Asness, Moskowitz & Pedersen (2013) — "Value and Momentum Everywhere" | paper | https://www.aqr.com/Insights/Research/Journal-Article/Value-and-Momentum-Everywhere |
| Kenneth French data library — the UMD/momentum factor | dataset | https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html |

## 3. Mathematical and logical foundation

### 3.1 The J/K strategy construction

The notation used ever since comes from this paper. A **J-month/K-month** strategy:

```
1. At the end of each month t, rank all eligible stocks by their cumulative
   return over the previous J months.
2. Form an equally weighted portfolio of the TOP decile (the "buy" or
   winners portfolio) and an equally weighted portfolio of the BOTTOM
   decile (the "sell" or losers portfolio).
3. Hold for K months. The zero-cost portfolio is LONG winners, SHORT losers.
4. OVERLAPPING PORTFOLIOS: at any time, K cohorts are live. The month-t
   return is the equal-weighted average across the K cohorts formed in
   months t-1, t-2, ..., t-K. Each month, 1/K of the book is rebalanced.
```

Jegadeesh and Titman test `J, K ∈ {3, 6, 9, 12}` — 16 combinations, each in two versions (with and
without a one-week gap), for the 32 strategies referenced in the paper.

The overlapping-cohort construction matters practically: it means the strategy trades only 1/K of
the portfolio each month, which is what keeps turnover — and therefore cost — tolerable.

### 3.2 The skip-week convention

Panel B skips one week between the end of the formation period and the start of holding. This is
now standard practice (usually as the "12-2" or skip-month convention in modern factor
construction), and the reason is important:

Short-horizon returns exhibit **reversal**, driven partly by bid-ask bounce and partly by
liquidity provision. A stock that closed at the ask on the last day of the formation period looks
like a marginally bigger winner than it is, and mechanically reverts. Buying it immediately means
buying that noise. Skipping a week removes the contamination — and the returns go **up**, from
1.31% to 1.49% for the 12/3 strategy.

> That the profits *increase* when you remove the microstructure effect is the cleanest possible
> evidence that momentum is not a microstructure artefact. Contrast with pairs trading, where
> imposing a one-day wait *cut* returns substantially (see the statistical-arbitrage entry) —
> there, the microstructure effect was a meaningful part of the measured edge.

### 3.3 Why the edge should exist

The paper is careful not to over-claim, but the pattern it documents — **positive returns for 12
months, then partial reversal over years 2 and 3** — is the signature of *initial under-reaction
followed by delayed over-reaction*. Prices respond too slowly to news, then overshoot.

This is the same mechanism that Moskowitz, Ooi & Pedersen (2012) later document in the time series
of individual futures contracts (see the trend-following entry). The two literatures converge on
the same behavioural story from opposite directions.

Standard behavioural candidates developed later: the **disposition effect** (investors sell winners
too early and hold losers too long, slowing price adjustment), **anchoring** on stale reference
prices, and **slow information diffusion** across investor populations.

### 3.4 Cross-sectional vs. time-series momentum

Worth stating explicitly, because the two get conflated constantly:

| | Cross-sectional (this entry) | Time-series (TSMOM entry) |
|---|---|---|
| Signal | Return **relative to other stocks** | Sign of an instrument's **own** return |
| Net exposure | Roughly dollar-neutral by construction | Can be net long or short everything at once |
| Payoff shape | **Negatively skewed** — crashes | **Positively convex** — straddle-like |
| Behaviour in a market rebound | Worst case (see the momentum-crashes entry) | Loses, but bounded by the monthly rebalance |

They are related — Moskowitz, Ooi & Pedersen measure a beta of 0.66 between them — but they are not
substitutes, and their tail behaviour is close to opposite.

## 4. Known criticisms and limitations

1. **The January effect is severe and structural.** The strategy loses **about 7% on average in each
   January**, while the average non-January return is **1.66% per month**, positive in **71% of
   months** when January is excluded. Much of the year-2/3 reversal also occurs in Januaries. Any
   live implementation has to have an explicit January policy, and the standard explanation
   (tax-loss selling in December followed by a January bounce in beaten-down losers) implies the
   effect is a feature of the calendar, not of the signal.
2. **Momentum crashes.** The most serious limitation, and severe enough to warrant its own library
   entry: the strategy suffers rare, enormous, persistent losses concentrated in market rebounds
   following crashes. See `../momentum-crashes-daniel-moskowitz/`. The 1993 paper's sample
   (1965–1989) contains no episode on the scale of 1932 or 2009, which makes its risk picture
   materially incomplete.
3. **The reversal undercuts a pure risk explanation — and is itself weakly measured.** The negative
   year-2/3 returns have a t-statistic of only **−1.27**, and the 36-month abnormal return is not
   statistically distinguishable from zero. The authors are appropriately candid: they "cannot rule
   out the possibility that the positive returns over the first 12 months is entirely temporary."
4. **Turnover and costs.** The strategy trades 1/K of the book monthly and concentrates in
   high-volatility, often smaller and less liquid names. The 1993 paper does not model transaction
   costs; later work (notably Korajczyk & Sadka, Lesmond, Schill & Zhou) argues costs consume a
   substantial share of the paper profits, particularly on the short leg.
5. **The short leg needs borrow.** Past losers are disproportionately hard-to-borrow, expensive to
   short, and prone to squeezes — precisely the names the strategy wants maximum short exposure to.
6. **Data-mining exposure.** 32 strategies are tested. The authors address this directly with a
   Bonferroni bound — the probability of a single t-statistic as large as **4.28** arising by chance
   across 32 non-independent tests is **less than 0.0006** — which is a genuinely rigorous treatment
   for 1993 and much better than most contemporaneous work. The stronger defence is the three
   decades of out-of-sample and international confirmation that followed.
