# Backtest & Data Summary — Carry Across Asset Classes

## Verification

All figures below were read directly from Koijen, R. S. J., Moskowitz, T. J., Pedersen, L. H., &
Vrugt, E. B. (2018), "Carry," *Journal of Financial Economics* 127(2), 197–225, retrieved in-session
from the authors' hosted PDF. Table and section references are to that document.
**Evidence grade: `verified-primary`.**

---

## 1. Data sample

All series end **September 2012**.

| Asset class | Instruments | Start |
|---|---|---|
| **Global equities** | **13 country index futures** — US (S&P 500), Canada (S&P TSE 60), UK (FTSE 100), France (CAC), Germany (DAX), Spain (IBEX), Italy (FTSE MIB), Netherlands (AEX), Sweden (OMX), Switzerland (SMI), Japan (Nikkei), Hong Kong (Hang Seng), Australia (S&P ASX 200) | March 1988 |
| **Currencies** | **20 FX forward contracts** (some from Feb 1997; the Euro from Feb 1999) | November 1983 |
| **Commodities** | **24 commodity futures** — metals, energy, agriculture, livestock | January 1980 |
| **Global fixed income** | **10 government bonds**; also used for 10y−2y slope returns | November 1983 |
| **US Treasuries** | CRSP bond portfolios, maturities 1–12, 13–24, 25–36, 37–48, 49–60, 61–120 months | **August 1971** |
| **Credit** | Barclays corporate bond indices, intermediate (~5y duration) and long-term (~10y) | — |
| **Equity index options** | US index calls and puts across moneyness | — |

Bond yields for the Treasury carry come from Gürkaynak, Sack & Wright. The breadth is the point:
seven asset classes, and the US Treasury series reaches back to 1971, which is what makes the 1972–75
drawdown observable at all.

## 2. Headline performance

| Strategy | Annualised Sharpe ratio |
|---|---|
| Cross-sectional carry (long high-carry, short low-carry), **average across asset classes** | **0.8** |
| **Diversified portfolio of carry strategies across all asset classes** | **1.2** |
| Carry *timing* strategies (long when carry is positive / above its mean), average | **0.6** |
| **Global carry timing combining all asset classes** | **0.9** |

The gap between 0.8 (average single-asset-class) and 1.2 (diversified) is the diversification
benefit — the same structure as TSMOM, where per-instrument strategies combine into a portfolio with
a materially better ratio.

The gap between the cross-sectional strategies (0.8 / 1.2) and the timing strategies (0.6 / 0.9) says
the **cross-sectional** form of carry is the stronger one: ranking assets against each other beats
taking directional positions based on carry's own level.

## 3. The predictive coefficient — and why its sign matters

Panel regressions of future returns on carry give a positive coefficient in **every** asset class,
but the magnitude splits the classes into two economically distinct groups:

| Coefficient | Asset classes | Interpretation |
|---|---|---|
| **> 1** | **Global equities, global bonds, credit** | Carry predicts *additional* price appreciation on top of the carry itself — the opposite of what parity conditions predict |
| **< 1** (but > 0) | **Commodities, options** | "The market takes back part of the carry (although not all, as implied by UIP and the EH)" |

Both are profitable. The second group is the textbook carry story — collect the yield, give some back
in price, keep the difference. The first group is stronger and stranger: high-carry equities and
bonds *also* tend to appreciate.

This split is why the paper argues carry is a unifying concept rather than a single mechanism:
"there are commonly shared features across different carry strategies and also interesting
differences."

## 4. Carry's relation to other predictors

The paper's most consequential claim for anyone maintaining a factor library:

> "Carry provides unique return predictability. However, in many cases, the reverse is not true.
> **Carry often subsumes the return predictability of other known factors.**"

Carry generates positive and unexplained alpha within each asset class relative to that class's own
established predictors. The relation to value and momentum "everywhere" factors varies by asset class
— positive in some, negative in others — but **none of them explains carry**.

## 5. The drawdown structure — the most important section for risk

Carry returns are lower during global recessions, "which appears to hold uniformly across asset
classes." Identifying the worst episodes for the diversified strategy gives three **carry
drawdowns**:

| Episode | Period |
|---|---|
| 1 | **August 1972 – September 1975** |
| 2 | **March 1980 – June 1982** |
| 3 | **August 2008 – February 2009** |

All three "coincide with major global business cycle and macroeconomic events."

Two findings make this more serious than a list of bad periods:

1. **Everything fails together.** "During carry drawdowns all carry strategies perform poorly and,
   moreover, perform **significantly worse than passive exposures to these same markets and asset
   classes** during these times." Carry is not merely losing with the market — it is losing *more*.
2. **Monthly correlations hide it.** "This lower frequency co-movement is obscured when considering
   monthly returns. Hence, the modest unconditional pairwise correlations mask some important
   dynamics and some lower frequency co-movements."

> ⚠️ **This is the practical warning of the entry.** A risk model built on monthly correlations
> between carry strategies will show comfortable diversification across seven asset classes and will
> be wrong about the tail. The diversification is real in normal times and largely absent in the
> episodes that matter. Any capital allocation to a multi-asset carry programme should be sized
> against the *joint* drawdown, not the monthly covariance matrix.

## 6. Risk explanations tested

| Candidate | Verdict |
|---|---|
| Global recession risk | Related — carry loses in recessions, uniformly across classes |
| Liquidity risk | Related — positive exposure documented |
| Volatility risk | Related — positive exposure documented |
| **Any of them as a full explanation** | **No — "none fully explains carry's premium"** |

The authors leave the question open, noting the ambiguity between "macroeconomic risks and heightened
risk aversion" and "times of limited capital and arbitrage." This is the same unresolved tension as
in the momentum and VRP entries: the exposures are real but too small to justify the observed Sharpe
ratios.

## 6.1 Implementation check (run in-session)

The reference implementation was exercised on synthetic multi-asset panels with carry deliberately
built in as a return predictor. **This tests the code and the qualitative orderings, not the paper's
magnitudes** — synthetic data cannot validate an empirical Sharpe ratio.

| Asset class (synthetic) | Cross-sectional Sharpe | Timing Sharpe |
|---|---|---|
| Equities | 1.59 | 1.47 |
| FX | 1.59 | 1.24 |
| Commodities | 0.91 | 0.64 |
| Bonds | 1.15 | 1.07 |

**Two orderings from the paper reproduce, and both are the ones that drive implementation choices:**

1. **Cross-sectional beats timing in every single class** — matching the paper's 0.8 vs 0.6 average.
   The margin varies (widest in commodities, 0.91 vs 0.64) but the sign never flips.
2. **Diversification lifts the ratio substantially** — average single-class 1.31 → diversified
   **2.51**. The paper's 0.8 → 1.2 shows the same direction. The magnitude here is inflated because
   the synthetic asset classes were generated independently, whereas real carry strategies share the
   recession exposure documented in §5. **That difference is precisely the paper's warning.**

**On the `joint_drawdown_check` diagnostic:** it fired on this data (low-frequency correlation 3.9×
the monthly), but that is an artefact — with independently generated classes the monthly correlation
is near zero (0.013), so any ratio is unstable. The diagnostic is included because the paper's
finding demands it be run on *real* returns; this exercise confirms it computes, not that it
detected anything meaningful here.

## 7. Metrics not reported (and why)

| Metric | Status |
|---|---|
| Maximum drawdown, as a percentage | **NOT REPORTED IN SOURCE** — drawdowns are identified as date ranges, not magnitudes |
| Sortino ratio | **NOT REPORTED IN SOURCE** |
| Win rate / profit factor | **NOT REPORTED IN SOURCE** |
| Transaction and roll costs | **NOT MODELLED** in the headline Sharpe ratios |
| Turnover | Not reported |
| Capacity | Not addressed |

The unmodelled roll cost is the significant gap. A strategy holding futures across seven asset
classes must roll continuously, and roll cost in commodities in particular is not negligible. Price
it with `../../execution-and-cost/almgren-chriss-optimal-execution/` before treating 1.2 as
achievable net.

## 8. Where the strategy thrives vs. fails

**Thrives when:**
- Markets are calm and expansionary — the mirror image of the drawdown condition.
- Genuine cross-sectional dispersion in carry exists, so the long and short legs are meaningfully
  different.
- Diversification across all seven asset classes is available. The jump from 0.8 to 1.2 Sharpe is the
  entire case for running this as a multi-asset programme rather than a currency trade.
- Funding is stable and leverage is not called. Carry is short liquidity risk by construction.

**Fails when:**
- **A global recession arrives.** All three identified drawdowns are recessions, and carry does worse
  than passive exposure during them.
- Volatility spikes and liquidity withdraws — the documented exposures both turn against the trade at
  once.
- Positions are levered. The negative skew plus funding sensitivity is the classic carry-crash
  configuration documented at length in the currency literature.
- The operator relies on monthly correlations to size risk. See §5.

## 9. Decay and current status

**`decay_status: partially-decayed`.**

- **The mechanism is structural, not an anomaly.** Carry is observable, model-free, and reflects
  genuine differences in yields, convenience yields and curve slopes. Something has to compensate
  whoever bears recession, liquidity and volatility risk. That does not vanish through competition.
- **But the specific published premium is now widely harvested.** Carry is a standard sleeve in
  systematic multi-asset products, and the currency carry trade in particular has been institutional
  for decades. The 2018 publication is recent enough that clean post-publication out-of-sample
  evidence is still thin — a genuine limitation on judging decay here, and the reason this is graded
  `partially-decayed` rather than more confidently.
- **The crash risk has not decayed.** If anything, crowding sharpens it: a widely held carry book
  unwinds faster, and the paper's finding that all carry strategies fail together in recessions
  becomes more acute as more capital runs the same construction.

**How to use this entry.** As the unifying framework for the whole carry family — bond roll-down,
commodity basis, FX interest differentials and equity dividend yield are one measurement, not four
strategies. Three concrete takeaways: (1) the **cross-sectional** form beats the **timing** form
(0.8/1.2 versus 0.6/0.9); (2) **diversify across asset classes** — that is where the Sharpe
improvement comes from; and (3) **do not trust monthly correlations for tail sizing**, because the
paper's own analysis shows they conceal the joint drawdown. Pair it with
`../../trend-following/time-series-momentum-futures/`, whose convex, crisis-positive payoff is close
to the mirror image of carry's concave, crisis-negative one.
