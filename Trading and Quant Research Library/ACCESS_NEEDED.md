# Source Access Needed

Papers this library needs but cannot reach openly. Every entry currently ingested was verified
against a freely available primary source; the items below are blocked, and each one names the
category it would fill.

**How to help:** most of these resolve with a single institutional login (a university library
account, or an employer's subscription). Alternatively, many authors post accepted manuscripts on
their personal pages — if you can reach a paper through any route, the PDF itself is all that is
needed.

---

## Priority 1 — Volatility & Variance (the thinnest category, 1 entry)

The variance-risk-premium entry has no companion, and dispersion trading cannot be ingested at all
because the only open source is pure theory with no data.

| Paper | Publisher / host | Why it matters |
|---|---|---|
| **Driessen, Maenhout & Vilkov (2009)**, "The Price of Correlation Risk: Evidence from Equity Options", *Journal of Finance* 64(3) | Wiley / onlinelibrary.wiley.com | **The** empirical dispersion-trading paper. Documents the implied-vs-realised correlation gap that dispersion harvests. Would open the dispersion entry directly. |
| **Bakshi & Kapadia (2003)**, "Delta-Hedged Gains and the Negative Market Volatility Risk Premium", *Review of Financial Studies* 16(2), 527–566 | Oxford Academic / academic.oup.com | The complementary measurement approach to Carr & Wu — VRP measured through delta-hedged option P&L rather than variance swaps. |
| **Bollerslev, Tauchen & Zhou (2009)**, "Expected Stock Returns and Variance Risk Premia", *RFS* 22(11) | Oxford Academic | VRP as a *predictor* of equity returns, not just a premium to harvest. A distinct entry. |
| **Carr & Wu (2009)**, "Variance Risk Premiums", *RFS* 22(3), 1311–1341 — **published version** | Oxford Academic | Already ingested from the **2004 working paper**. The published figures should be re-checked before the entry is cited as "Carr & Wu (2009)". Lower priority — the working paper is legitimate, just not final. |

**Sites needed:** `academic.oup.com` (Oxford Academic — RFS), `onlinelibrary.wiley.com` (Journal of
Finance).

## Priority 2 — Event & Flow Driven (empty category)

No entry exists. The foundational papers are all paywalled and the open material is review articles
(secondary evidence) rather than primary studies.

| Paper | Publisher / host | Why it matters |
|---|---|---|
| **Bernard & Thomas (1989)**, "Post-Earnings-Announcement Drift: Delayed Price Response or Risk Premium?", *Journal of Accounting Research* 27 | Wiley / JSTOR | The canonical PEAD paper. Would open the category. |
| **Bernard & Thomas (1990)**, "Evidence That Stock Prices Do Not Fully Reflect the Implications of Current Earnings for Future Earnings", *Journal of Accounting and Economics* 13(4) | Elsevier / sciencedirect.com | The follow-up establishing the mechanism. |
| **Shleifer (1986)**, "Do Demand Curves for Stocks Slope Down?", *Journal of Finance* 41(3) | Wiley / JSTOR | The index-effect / rebalance-flow foundation. |
| **Mitchell & Pulvino (2001)**, "Characteristics of Risk and Return in Risk Arbitrage", *Journal of Finance* 56(6) | Wiley / JSTOR | Merger arbitrage: the canonical risk-and-return study, including the crucial finding about its option-like payoff in down markets. |

**Sites needed:** `onlinelibrary.wiley.com`, `jstor.org`, `sciencedirect.com`.

*(An open review — Fink, J. (2020), "A Review of the Post-Earnings-Announcement Drift", University of
Graz Working Paper 2020-04, `static.uni-graz.at` — is available and could open the category at
`evidence_grade: verified-secondary`. Held back so far because a review is secondary evidence and the
category deserves a primary anchor. Say the word if you'd rather have the category opened now.)*

## Priority 3 — Microstructure theory

| Paper | Publisher / host | Why it matters |
|---|---|---|
| **Kyle (1985)**, "Continuous Auctions and Insider Trading", *Econometrica* 53(6), 1315–1335 | JSTOR / Wiley | The theoretical origin of linear price impact ("Kyle's lambda"). The order-flow-imbalance entry cites it as an ancestor but it is not ingested. |
| **Easley, Kiefer, O'Hara & Paperman (1996)**, "Liquidity, Information, and Infrequently Traded Stocks", *Journal of Finance* 51(4) | Wiley / JSTOR | The PIN model — probability of informed trading. The adverse-selection measure the market-making entries lack. |

**Sites needed:** `jstor.org`, `onlinelibrary.wiley.com`.

## Priority 4 — Statistical arbitrage depth

| Paper | Publisher / host | Why it matters |
|---|---|---|
| **Do & Faff (2010)**, "Does Simple Pairs Trading Still Work?", *Financial Analysts Journal* 66(4), 83–95 | Taylor & Francis / tandfonline.com | Currently cited at `verified-secondary` in the pairs-trading entry — the decay evidence rests on it, and the full text has not been read. |
| **Do & Faff (2012)**, "Are Pairs Trading Profits Robust to Trading Costs?", *Journal of Financial Research* | Wiley | The cost-adjusted follow-up. Would let the pairs entry's decay verdict be upgraded to primary. |
| **Elliott, van der Hoek & Malcolm (2005)**, "Pairs trading", *Quantitative Finance* 5(3) | Taylor & Francis | Earlier OU pairs formulation, predating the ingested Leung & Li entry. |

**Sites needed:** `tandfonline.com` (Taylor & Francis), `onlinelibrary.wiley.com`.

---

## Summary — the sites, ranked by how much they unblock

| Site | Papers unblocked | Categories affected |
|---|---|---|
| **`onlinelibrary.wiley.com`** (Journal of Finance, and others) | **6** | Event & flow, volatility, microstructure, stat arb |
| **`academic.oup.com`** (Oxford — Review of Financial Studies) | **3** | Volatility (all of Priority 1's core) |
| **`jstor.org`** | 4 (overlaps Wiley) | Event & flow, microstructure |
| **`tandfonline.com`** (Taylor & Francis) | 2 | Stat arb depth |
| **`sciencedirect.com`** (Elsevier) | 1 | Event & flow |

**If only one:** `academic.oup.com` — it unblocks the entire volatility priority list, which is the
library's weakest category.
**If two:** add `onlinelibrary.wiley.com` — it unblocks the empty event-and-flow category plus the
microstructure theory gaps.

## What is *not* blocked

For the record, so effort is not wasted: arXiv, NBER working papers, SSRN (sometimes),
author personal pages, and university repositories have all worked well. Every one of the
15 ingested entries came from one of those routes. Where a paywalled journal version exists
alongside a public working paper, the library cites the working paper and says so explicitly.
