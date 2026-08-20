# Trading & Quant Research Library

A local, data-backed research library of trading and quantitative strategies. Every entry is
sourced from a public academic paper, an open-source codebase, or a rigorous empirical study —
and every performance number carries a citation back to the primary document it came from.

## What this library is not

It is not a collection of trade ideas, signal services, or blog heuristics. Nothing enters the
library on narrative alone. An entry must have a stated data sample, a reproducible rule, and
published results — or it does not get a folder.

## Layout

```
Trading and Quant Research Library/
├── README.md                     <- you are here
├── TAXONOMY.md                   <- category tree + wave roadmap
├── INGESTION_STANDARD.md         <- the ingestion contract every entry must satisfy
├── _schema/metadata.schema.json  <- JSON Schema for metadata.json (machine validation)
├── _index/library_index.csv      <- flat index of every ingested strategy
└── strategies/
    └── <category>/<strategy-slug>/
        ├── research_paper_or_source.md   <- edge, sources, mathematical foundation
        ├── backtest_and_data_summary.md  <- performance, data, regime behaviour
        ├── source_or_pseudo_code.txt     <- reference implementation / pseudo-code
        └── metadata.json                 <- structured tags for automated filtering
```

## Ingested strategies

**Wave 1 — one anchor per mechanism family**

| Category | Strategy | Decay | Status |
|---|---|---|---|
| Statistical Arbitrage | [Pairs Trading — Distance Method](strategies/statistical-arbitrage/pairs-trading-distance-method/) | substantially-decayed | Verified |
| Trend Following | [Time Series Momentum (TSMOM)](strategies/trend-following/time-series-momentum-futures/) | partially-decayed | Verified |
| Market Making / Microstructure | [Avellaneda–Stoikov Optimal Quoting](strategies/market-making-microstructure/avellaneda-stoikov-optimal-quoting/) | intact | Verified + reproduced |
| Volatility & Variance | [Variance Risk Premium Harvesting](strategies/volatility-and-variance/variance-risk-premium-harvesting/) | partially-decayed | Verified + reproduced |
| Cross-Sectional Factors | [Cross-Sectional Momentum](strategies/cross-sectional-factors/cross-sectional-momentum-jegadeesh-titman/) | partially-decayed | Verified |

**Wave 2 — depth entries that pair with a Wave 1 anchor**

| Category | Strategy | Pairs with | Status |
|---|---|---|---|
| Cross-Sectional Factors | [Momentum Crashes & Dynamic Weighting](strategies/cross-sectional-factors/momentum-crashes-daniel-moskowitz/) | Cross-Sectional Momentum | Verified |
| Statistical Arbitrage | [Factor-Residual Stat Arb (PCA & ETF)](strategies/statistical-arbitrage/factor-residual-statistical-arbitrage/) | Pairs Trading | Verified + reproduced |
| Statistical Arbitrage | [Optimal Mean-Reversion Bands (OU)](strategies/statistical-arbitrage/ornstein-uhlenbeck-optimal-bands/) | Pairs Trading, Factor-Residual | Verified + reproduced |
| Market Making | [Bounded-Inventory Market Making](strategies/market-making-microstructure/gueant-lehalle-fernandez-tapia-bounded-inventory/) | Avellaneda–Stoikov | Verified + reproduced |
| Market Making | [Limit *and* Market Orders](strategies/market-making-microstructure/guilbaud-pham-limit-and-market-orders/) | Avellaneda–Stoikov | Verified + reproduced |
| Microstructure | [Order Flow Imbalance & Price Impact](strategies/market-making-microstructure/order-flow-imbalance-price-impact/) | all market-making entries | Verified |

**Wave 3 — opening the remaining categories**

| Category | Strategy | Why it matters | Status |
|---|---|---|---|
| **Execution & Cost** | [Optimal Execution (Almgren–Chriss)](strategies/execution-and-cost/almgren-chriss-optimal-execution/) | The cost layer that decides which entries above are implementable | Verified + reproduced |
| **Carry & Term Structure** | [Carry Across Asset Classes](strategies/carry-and-term-structure/carry-across-asset-classes/) | Unifies bond roll-down, commodity basis, FX differentials and dividend yield into one measurement | Verified + reproduced |

"Verified" means every quoted statistic was read out of the primary source document, not recalled or
paraphrased from secondary commentary. "Reproduced" means the reference implementation was executed
and its output checked against the paper or against a known ground truth. See
`INGESTION_STANDARD.md`.

### Entries that must be read together

Two anchors are incomplete on their own, and the library says so explicitly rather than leaving a
reader to find out the hard way:

- **Cross-Sectional Momentum → Momentum Crashes.** The 1965–1989 sample contains no crash on the
  scale the strategy can produce. The companion entry supplies the missing risk picture (loser decile
  +232% in two months, 1932).
- **Pairs Trading → Factor-Residual Stat Arb.** The distance method's key weakness is that it cannot
  filter on mean-reversion speed. The companion entry is what that filter looks like implemented.
- **Pairs Trading / Factor-Residual → Optimal Mean-Reversion Bands.** Both parents set their
  thresholds by assertion (2σ; s-score 1.25) and say so. The companion entry *derives* them, and
  shows the stop and the take-profit cannot be chosen independently.
- **Any market-making model → Order Flow Imbalance.** Avellaneda–Stoikov, Guéant et al. and
  Guilbaud–Pham all assume order arrivals are uninformative. OFI is the measurement that says
  otherwise, and supplies the adverse-selection layer all three lack.
- **Every strategy entry → Optimal Execution.** Several entries report gross results (TSMOM's Sharpe
  ratios are explicitly gross; Jegadeesh–Titman models no costs at all). The execution entry supplies
  the cost model needed to judge whether an edge survives its own turnover.
- **Carry ↔ Time Series Momentum.** Carry is concave and crisis-negative; trend is convex and
  crisis-positive. They are the two great cross-asset systematic families and their tails point in
  opposite directions, which is why they are usually run together.

## Validating the library

```bash
cd "Trading and Quant Research Library"
python3 _index/build_index.py
```

Checks every `metadata.json` against the schema, confirms all four required files exist in each
strategy folder, and regenerates `_index/library_index.csv`. Exits non-zero on any failure, so it
can be wired into a pre-commit hook. Run it after every ingestion wave.

## Reading an entry

Start with `research_paper_or_source.md` for the economic mechanism, then
`backtest_and_data_summary.md` for whether the evidence survives contact with costs and regimes.
`source_or_pseudo_code.txt` is the implementation contract. `metadata.json` is what automation
should filter on — never parse the prose.

## Honest-use warning

Published backtests are the upper bound of what a strategy ever did, not a forecast. Most entries
here document effects measured before widespread electronic arbitrage; several have decayed
materially since publication, and the entry says so explicitly in its "Decay and current status"
section. Treat that section as the most important part of the file.
