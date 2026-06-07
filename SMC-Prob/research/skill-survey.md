# Source Skill Survey — SMC-Prob

Notes from the research session that scoped this project: a survey of public Claude agent-skill repos for day trading, looking for skills that let Claude read price structure, judge entries, and estimate probability of trade success against a live cTrader connection.

Full survey covered ~12 repos; the two selected as the basis for SMC-Prob, plus the runners-up, are documented below.

---

## Selected — combined into SMC-Prob

### 1. [MobiusQuant/OpenMobius-skill](https://github.com/MobiusQuant/OpenMobius-skill) — structural lens (378★)

**What it does:** ICT/SMC (Smart Money Concepts) trading-knowledge skill. Identifies Break of Structure (BOS), Change of Character (CHoCH), Order Blocks, Fair Value Gaps, and premium/discount zones — the structural concepts that answer "where is price likely to go and where should I enter."

**How it works:** Retrieves from a 964-card curated knowledge base via local ChromaDB + `nomic-embed-text` vector embeddings (no API key needed). Pulls live crypto/stock/forex data from `api.mobiusquant.ai`. Renders/annotates charts via Playwright. Four workflows: knowledge Q&A, chart analysis, image annotation, K-line generation.

**Requirements:** Python 3.10+, ~550MB download (Playwright + embedding model), self-contained — no MCP server needed.

**What we're taking from it:** The *conceptual framework* — BOS/CHoCH/Order Blocks/FVGs/premium-discount zones as the lens for structural market reading. Not the implementation (their data feed is crypto/stock-oriented; we have live cTrader data already).

**Gap:** Explicitly does **not** do probability/confidence scoring — listed as roadmap-only ("per-event probability scoring as computable signals").

---

### 2. [agiprolabs/claude-trading-skills](https://github.com/agiprolabs/claude-trading-skills) — probability lens (50★, 62 skills)

**What it does:** Modular collection spanning market data, technical analysis (130+ indicators via pandas-ta), statistical regime/mean-reversion detection, **ML signal classification (XGBoost + walk-forward validation) for trade-confidence scoring**, market-microstructure/orderflow timing, Kelly-criterion position sizing, Sharpe/Sortino risk metrics.

**How it works:** Skills are independent `.md`/script modules; install via Claude Code plugin marketplace or copy into `~/.claude/skills/`.

**Requirements:** Python 3.9+/`uv`. Most skills run with no API key; some optionally use crypto-data APIs (Birdeye/CoinGecko/DexScreener) — the technical/statistical/ML skills themselves are instrument-agnostic and can run on OHLCV from any source, including cTrader.

**What we're taking from it:** The *concept* of layering quantitative confirmation — regime detection, statistical confluence, confidence/probability scoring, and risk-based position sizing — on top of a directional read. Not a direct dependency; SMC-Prob will implement an equivalent rules-based confluence-scoring approach first (see Build Log open question #3), informed by this collection's design.

**Gap:** No structural/SMC market-reading framework of its own — pure quant/statistical layer.

---

## Runners-up considered (not selected as primary sources)

| Repo | Why it was considered | Why not selected |
|---|---|---|
| [tradermonty/claude-trading-skills](https://github.com/tradermonty/claude-trading-skills) | Well-designed trade-planning & journaling skills, explicit "structure decisions, don't outsource them" philosophy | Aimed at swing/position trading on US equities, not intraday CFD/forex day trading |
| [mphinance/alpha-skills](https://github.com/mphinance/alpha-skills) | 113 skills incl. an "edge research pipeline" for strategy design/validation, conviction scoring, backtest bias detection | Stronger for offline strategy R&D than live intraday decision support |
| [roman-rr/trading-skills](https://github.com/roman-rr/trading-skills) | Produces exactly the entry/SL/TP/confidence output format we want, with a 0–100 confidence score | Hosted black-box signal service for crypto perpetuals only; free-during-beta with paid tiers planned — not Claude reasoning live over our own cTrader feed |
| [akinabudu/ctrader-mcp-server](https://github.com/akinabudu/ctrader-mcp-server) / [vonzelle-vzt/tradestack-mcp](https://github.com/vonzelle-vzt/tradestack-mcp) | Dedicated cTrader MCP bridges | Infrastructure layer, not analysis — we already have a working `ctrader` MCP connection providing trendbars/spot prices/symbols/orders |

---

## Why this combination

Neither selected repo alone answers the user's full brief ("knowing where would be good to enter and where that price will go" + "probability of trade success"):

- OpenMobius-skill answers **direction and entry** (structural read) but admits it has no probability layer.
- agiprolabs/claude-trading-skills answers **confidence/probability and sizing** but has no structural market-reading framework.

SMC-Prob's two-stage pipeline (structural read → probability scoring) is designed to close that gap by combining both lenses into one `/smc-prob` skill, reasoning live over the existing cTrader MCP connection — see `README.md` for the design direction and `BUILD-LOG.md` for current progress.
