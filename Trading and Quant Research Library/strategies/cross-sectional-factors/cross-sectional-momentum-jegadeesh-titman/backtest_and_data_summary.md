# Backtest & Data Summary — Cross-Sectional Momentum

## Verification

All figures below were read directly from the full text of Jegadeesh, N., & Titman, S. (1993),
"Returns to Buying Winners and Selling Losers: Implications for Stock Market Efficiency," *The
Journal of Finance* 48(1), 65–91, retrieved in-session from
`bauer.uh.edu/rsusmel/phd/jegadeesh-titman93.pdf`. Table references are to that document.
**Evidence grade: `verified-primary`.**

Returns are **average monthly returns**, not annualised, unless stated.

---

## 1. Data sample

| Field | Value |
|---|---|
| Data source | CRSP daily returns file |
| Exchange coverage | NYSE and AMEX |
| Underlying data range | July 1962 – December 1989 |
| **Portfolio return sample** | **January 1965 – December 1989** |
| Frequency | Monthly returns compounded from daily |
| Portfolio construction | Equal-weighted deciles, overlapping K-month cohorts |
| Strategies tested | 32 (J, K ∈ {3, 6, 9, 12}, with and without a 1-week skip) |

The sample starts in 1965 because the 12-month/12-month strategy needs 23 months of lagged data, so
1965 is the first full calendar year with complete coverage.

## 2. Headline performance — Table I

**Panel A** = no gap between formation and holding. **Panel B** = 1-week skip.
t-statistics in parentheses.

### The best strategy: 12-month formation / 3-month holding

| Version | Monthly return |
|---|---|
| Panel A (no skip) | **1.31%** |
| Panel B (1-week skip) | **1.49%** |

The t-statistic of 4.28 referenced for the 12/3 skip-week strategy is the basis of the paper's
multiple-testing defence (see §5).

### 6-month formation — the most-cited configuration

| K = | 3 | 6 | 9 | 12 |
|---|---|---|---|---|
| **Panel A: Sell (losers)** | 0.87% (1.67) | 0.79% (1.56) | 0.72% (1.48) | 0.80% (1.66) |
| **Panel A: Buy (winners)** | 1.71% (4.28) | 1.74% (4.33) | 1.74% (4.31) | 1.66% (4.13) |
| **Panel A: Buy − Sell** | **0.84%** (2.44) | **0.95%** (3.07) | **1.02%** (3.76) | **0.86%** (3.36) |
| **Panel B: Buy − Sell** | **1.14%** (3.37) | **1.10%** (3.61) | **1.08%** (4.01) | **0.90%** (3.54) |

The 6/6 strategy — the configuration the paper analyses in detail as "representative" — earns
**0.95% per month (t = 3.07)** with no skip and **1.10% (t = 3.61)** with the one-week skip.

### 3-month formation

| K = | 3 | 6 | 9 | 12 |
|---|---|---|---|---|
| Panel A: Buy − Sell | 0.32% (1.10) | 0.58% (2.29) | 0.61% (2.69) | 0.69% (3.53) |
| Panel B: Buy − Sell | 0.73% (2.61) | 0.78% (3.16) | 0.74% (3.36) | 0.77% (4.00) |

Note the pattern across the whole table: **the skip-week version is stronger nearly everywhere**,
and the improvement is largest at short formation horizons — exactly where short-term reversal
contamination would be worst.

### Where the return comes from

Look at the 6-month Panel A row: winners earn 1.71–1.74% with t-statistics above 4.1, while losers
earn 0.72–0.87% with t-statistics **below 1.7 and never significant**. In this sample the long leg
carries most of the statistical weight. (Daniel & Moskowitz later show that in the full 1927–2013
sample the *loser* leg is where the danger lives — see the momentum-crashes entry.)

## 3. The reversal — Table VII (event-time returns)

Tracking the zero-cost portfolio for 36 months after formation:

| Period | Behaviour |
|---|---|
| Month 1 | Negative (the short-term reversal effect) |
| Months 2–12 | Positive in every month |
| **Cumulative peak at month 12** | **+9.5%** |
| Year 2 | Negative in every month |
| First half of year 3 | Negative |
| Thereafter | Virtually zero |
| **Cumulative at month 36** | **≈ +4%** |

Roughly **half the gain earned in year 1 is given back** over the following two years.

**Statistical caveat, stated by the authors:** the year-2/3 negative returns have a t-statistic of
only **−1.27**, and the 36-month abnormal return is not statistically different from zero. Their own
conclusion — *"we cannot rule out the possibility that the positive returns over the first 12 months
is entirely temporary"* — is the honest reading. Cumulative t-statistics use Newey–West standard
errors because of the overlapping construction.

## 4. Seasonality — the January problem

| Metric | Value |
|---|---|
| Average January loss | **≈ −7%** |
| Average non-January monthly return | **+1.66%** |
| Share of non-January months positive | **71%** |

The paper also notes that the entire negative return in the year-2/3 reversal window occurs in
Januaries — outside January, the returns beyond the first year are close to zero.

This is not a minor seasonal wrinkle. A −7% single month against a +1.66% monthly average means
January alone consumes more than four months of typical gains, every year. Any implementation must
have a deliberate policy on it.

## 5. Multiple-testing defence

32 strategies are tested. Jegadeesh and Titman apply a **Bonferroni inequality** bound: the
probability of obtaining a single t-statistic as large as **4.28** with 32 not-necessarily-
independent tests is **less than 0.0006**.

This was unusually rigorous for 1993 and pre-dates the modern multiple-testing literature (Harvey,
Liu & Zhu, 2016) by two decades. The stronger defence, unavailable to the authors at the time, is
what happened next: the effect replicated out-of-sample in 1990–1998 (Jegadeesh & Titman, 2001),
internationally (Rouwenhorst, Fama & French), across asset classes (Asness, Moskowitz & Pedersen),
and in data back to 1801 (Geczy & Samonov).

## 6. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Sharpe ratio | **NOT REPORTED IN SOURCE** — the paper reports mean returns and t-statistics |
| Maximum drawdown | **NOT REPORTED IN SOURCE** (see the momentum-crashes entry, which does) |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Win rate | Partially — 71% of non-January months positive |
| Profit factor | **NOT REPORTED IN SOURCE** |
| Transaction costs | **NOT MODELLED** |
| Turnover | Not reported; implied at 1/K of the book per month |

The absent drawdown figure is the most consequential omission, and it is not the authors' fault: the
1965–1989 sample simply contains no momentum crash of the magnitude the strategy is capable of. The
risk picture only becomes visible in the longer sample — which is precisely why the next entry in
this category exists.

## 7. Where the strategy thrives vs. fails

**Thrives when:**
- Trends persist and information diffuses slowly — steady bull markets, sector rotations with
  staying power.
- Volatility is low to moderate and market direction is stable.
- Dispersion across stocks is high, so the winner and loser deciles are genuinely different.
- Applied with a skip period, which the paper's own Panel B shows improves returns everywhere.

**Fails when:**
- **The market rebounds sharply after a decline.** The single worst environment; the short leg of
  beaten-down, high-beta losers rockets. See the momentum-crashes entry for the magnitude.
- **January.** −7% on average, reliably.
- Sharp factor or style rotations invert the cross-sectional ranking.
- Trading costs and borrow are realistic. The strategy concentrates in volatile, less liquid names,
  and the short leg is disproportionately hard to borrow.
- Crowding is high. Momentum is among the most widely implemented factors in existence; the
  unwinding of crowded momentum books is itself a source of the crash risk.

## 8. Decay and current status

**`decay_status: partially-decayed`.**

- **The effect is genuinely robust and has replicated repeatedly.** Jegadeesh & Titman (2001)
  confirmed it out-of-sample on 1990–1998. It appears in international markets, in industry
  portfolios, in country indices, in currencies, commodities and bonds, and — per Geczy & Samonov —
  in data going back to 1801. Very few findings in finance have this much independent confirmation.
- **But the realised premium has compressed since publication.** Momentum is now a standard factor
  available in cheap ETF form, embedded in the Fama–French–Carhart framework, and run at scale by
  quant equity managers. Post-2000 realised returns are meaningfully below the 1965–1989 figures,
  and the strategy suffered severe drawdowns in 2009 and again in later reversal episodes.
- **The crash risk has not decayed at all.** If anything, crowding has increased it — a widely held
  momentum book unwinds faster.
- **Notably, momentum has failed to work in Japan** over long periods, which is the standard
  counter-example. Daniel & Moskowitz show their dynamic variant recovers profits even there.

**How to use this entry.** As the foundational construction reference for any cross-sectional
ranking strategy: J/K notation, decile portfolios, overlapping cohorts, the skip period. It is
deliberately incomplete as a risk document — read it together with `../momentum-crashes-daniel-
moskowitz/`, which supplies the drawdown picture this sample was too short to contain.
