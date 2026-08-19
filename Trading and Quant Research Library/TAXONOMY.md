# Library Taxonomy & Wave Roadmap

## Category tree

The library is organised by *mechanism of edge*, not by instrument or timeframe. A strategy lives
under the category describing why it makes money, so that a reader can compare substitutes.

```
strategies/
├── statistical-arbitrage/        Relative-value convergence; market-neutral by construction
├── trend-following/              Time-series persistence; convex, crisis-positive payoff
├── volatility-and-variance/      Risk premia embedded in options and variance markets
├── market-making-microstructure/ Compensation for liquidity provision and adverse selection
├── cross-sectional-factors/      Long-short factor premia across a cross-section of assets
├── event-and-flow-driven/        Index rebalances, earnings drift, institutional flow footprints
├── carry-and-term-structure/     Roll yield, curve shape, funding differentials
├── machine-learning-alpha/       Empirical-risk-minimisation approaches with published protocols
└── execution-and-cost/           Not alpha itself; the cost model that decides if alpha survives
```

## Wave 1 — target categories (this session)

Wave 1 establishes one anchor entry in each of five mechanism families. Anchors are chosen for
being *foundational* — heavily cited, independently replicated, and the paper that every later
refinement in the family cites.

| # | Category | Mechanism of edge | Wave 1 anchor |
|---|---|---|---|
| 1 | Statistical Arbitrage & Relative Value | Temporary mispricing between close substitutes; convergence | Gatev, Goetzmann & Rouwenhorst (2006) — pairs trading distance method |
| 2 | Trend Following & Time-Series Momentum | Under-reaction then delayed over-reaction to information | Moskowitz, Ooi & Pedersen (2012) — TSMOM |
| 3 | Market Making & Order-Flow Microstructure | Compensation for providing liquidity, priced against inventory and adverse-selection risk | Avellaneda & Stoikov (2008) — optimal quoting |
| 4 | Volatility & Variance Risk Premium | Implied variance systematically exceeds realised variance | Carr & Wu (2009) — variance risk premia ✅ |
| 5 | Cross-Sectional Equity Factors | Dispersion in expected returns across a cross-section | Jegadeesh & Titman (1993) — cross-sectional momentum ✅ |

**Wave 1 complete.** All five mechanism families have a verified anchor entry.

## Wave roadmap (proposed, pending confirmation)

Each wave deepens the categories rather than only widening them, so the library builds families of
related work rather than a scatter of disconnected papers.

**Wave 2 — complete the Wave 1 families (depth).** *In progress.*
Ingested so far:
- ✅ **Momentum Crashes & Dynamic Weighting** (Daniel & Moskowitz, 2016) — pairs with the
  cross-sectional momentum anchor; supplies the crash-risk picture that anchor's sample cannot show.
- ✅ **Factor-Residual Statistical Arbitrage** (Avellaneda & Lee, 2009) — pairs with the pairs-trading
  anchor; the modern PCA/ETF generalisation with an explicit mean-reversion-speed filter.

Still queued for Wave 2: cointegration pairs (Engle–Granger / Johansen selection), Ornstein–Uhlenbeck
optimal stopping bands, dispersion trading, volatility carry and term structure, Kyle's lambda and
PIN, order-flow imbalance, queue-position models, Guéant–Lehalle–Fernandez-Tapia bounded-inventory
market making, Cartea–Jaimungal adverse-selection quoting.

**Wave 3 — carry, term structure, and event/flow.**
Commodity roll yield and backwardation, FX carry and the forward premium puzzle, bond term
premium, post-earnings-announcement drift, index-rebalance front-running, merger arbitrage
spreads, short-interest and lending-fee signals.

**Wave 4 — machine-learning alpha with credible protocols.**
Only entries with an explicit walk-forward protocol, an out-of-sample discipline, and a published
comparison against a linear baseline. Deep-learning trend models, gradient-boosted return
prediction, and the empirical-asset-pricing literature (Gu, Kelly & Xiu style methodology).

**Wave 5 — execution, capacity, and the cost layer.**
Almgren–Chriss optimal execution, square-root market impact, capacity decay, and the
transaction-cost models that determine which of Waves 1–4 are actually implementable at size.

**Wave 6 — adversarial review.**
No new ingestion. Every existing entry is re-examined for replication failures, out-of-sample
decay, and p-hacking exposure (multiple-testing corrections in the sense of Harvey, Liu & Zhu).
Entries that fail get a decay warning or are demoted, not silently kept.

## Slug conventions

- Lowercase, hyphen-separated, no dates, no author names unless the method is universally known
  by them (`avellaneda-stoikov-optimal-quoting` is acceptable; `gatev-2006` is not).
- Name the *method*, not the paper: `pairs-trading-distance-method`, not `pairs-trading`.
- One method per folder. A refinement of an existing method gets its own folder and cross-links to
  its parent in `metadata.json` via `related_strategies`.
