# Trade Picker

An AI-powered scalping analysis system that uses multiple MCP (Model Context Protocol) servers to scan live markets simultaneously across **forex, crypto, stocks, and indices** — identifying the single highest-probability mean reversion setup and outputting a structured trade card with entry, stop, and target prices.

---

## Overview

The Trade Picker runs as a Claude Code Agent Skill (`/trade-picker`). It scans all four market types in parallel and uses a normalised cross-market scoring system to identify the best setup regardless of instrument type. The pipeline:

1. **Parallel broad scan** — Screens forex, crypto, US stocks, and indices simultaneously for BB extremes, RSI oversold/overbought, and MACD crossovers
2. **Event filters** — News check for all instruments; earnings clearance check for stocks (no earnings within 5 trading days)
3. **Deep technical pull** — Full indicator suite on shortlisted candidates; volume data for stocks/indices
4. **Confluence scoring** — Market-aware scoring (max 10 for forex/crypto, max 12 for stocks, max 11 for indices)
5. **Cross-market normalisation** — All scores converted to a common /10 scale so the best setup wins regardless of instrument type
6. **Trade card output** — Direction, entry zone, stop, targets, R:R, and confidence score

---

## Connected MCP Servers

| Server | Type | Markets | What It Provides | Key Requirement |
|--------|------|---------|-----------------|-----------------|
| `tradingview-mcp` | stdio (uvx) | All | Live screener — BB/RSI/MACD scans, full technical analysis across forex, crypto, stocks, indices | None — free |
| `massive` | stdio | Stocks, Forex, Crypto | Real-time OHLCV, tick data, volume — used for volume spike signal on stocks | API key at massive.com |
| `alpha-vantage` | stdio (uvx) | Stocks | Earnings calendar, historical indicators, fundamentals | Free API key at alphavantage.co |
| `newsmcp` | stdio (npx) | All | Real-time news from hundreds of sources — macro event filter | None — free |
| `coingecko` | HTTP | Crypto | 15,000+ coins — real-time prices, OHLCV, market depth | None — free |
| `aktools` | stdio (uvx) | Stocks, Forex, Crypto | Supplementary macro, forex, and equity data | None — free |
| `tradingview-ohlcv` | stdio (uv) | All | Multi-timeframe OHLCV candles via bidouilles/mcp-tradingview-server | Clone repo first (see below) |
| `pinescript-docs` | stdio (uvx) | — | Pine Script v6 reference docs for strategy development | None — free |

### Setup

All servers are defined in `/.mcp.json` at the project root. To activate:

```bash
# Massive (formerly Polygon.io) — required for stock volume signals
claude mcp add massive -e MASSIVE_API_KEY=your_key -- mcp_massive

# Alpha Vantage — required for stock earnings clearance check
claude mcp add alpha-vantage -- uvx --from marketdata-mcp-server marketdata-mcp YOUR_KEY

# TradingView OHLCV — requires local clone
git clone https://github.com/bidouilles/mcp-tradingview-server /tmp/mcp-tradingview-server
cd /tmp/mcp-tradingview-server && uv venv --python 3.11 && uv pip install -e .
claude mcp add tradingview-ohlcv -- uv --directory /tmp/mcp-tradingview-server run mcp-tradingview

# All others (free, no key required)
claude mcp add tradingview-mcp -- uvx tradingview-mcp
claude mcp add coingecko -t http -- https://mcp.api.coingecko.com/mcp
claude mcp add aktools -- uvx mcp-aktools
claude mcp add newsmcp -- npx -y @newsmcp/server
claude mcp add pinescript-docs -- uvx pinescript-mcp
```

---

## Analysis Workflow

### Step 1 — Parallel Market Scan

All market scans fire simultaneously:

```
# Forex
mcp__tradingview-mcp__scan_bollinger_bands(market="forex")
mcp__tradingview-mcp__scan_rsi_extremes(market="forex")
mcp__tradingview-mcp__scan_macd_crossover(market="forex")

# Crypto
mcp__tradingview-mcp__scan_bollinger_bands(market="crypto")
mcp__tradingview-mcp__scan_rsi_extremes(market="crypto")
mcp__tradingview-mcp__scan_macd_crossover(market="crypto")

# US Stocks
mcp__tradingview-mcp__scan_bollinger_bands(market="america")
mcp__tradingview-mcp__scan_rsi_extremes(market="america")

# Indices
mcp__tradingview-mcp__scan_bollinger_bands(market="index")
mcp__tradingview-mcp__scan_rsi_extremes(market="index")
```

Immediate disqualification: illiquid instruments (zero volume), stablecoins, meme coins, spreads > 0.1%, stocks with < 500k daily volume, ADX > 30.

### Step 2 — Event Filters

- **All instruments**: `newsmcp` news check — disqualify if high-impact event within 4 hours
- **Stocks only**: `alpha-vantage` earnings calendar — disqualify if earnings within 5 trading days

### Step 3 — Deep Technical Pull

`mcp__tradingview-mcp__get_technical_analysis` for each candidate: RSI, Stoch %K/%D, MACD, BB upper/lower, EMA200, ADX, ATR, VWAP, ChaikinMoneyFlow, bid_ask_spread_pct.

**Stocks/indices additionally**: volume vs 20-day average (`massive`), and broad index EMA50 regime check (`tradingview-mcp` on SPX/FTSE/DAX).

### Step 4 — Confluence Scoring

#### Universal Signals (all markets)

| Signal | Long | Short |
|--------|:----:|:-----:|
| Price at/below BB lower | +2 | — |
| Price at/above BB upper | — | +2 |
| Stoch.K < 15 | +2 | — |
| Stoch.K > 85 | — | +2 |
| Price within 0.05% of EMA200 | +2 | +2 |
| RSI < 35 | +1 | — |
| RSI > 65 | — | +1 |
| MACD bullish crossover | +1 | — |
| MACD bearish crossover | — | +1 |
| ADX < 20 (weak trend) | +1 | +1 |

#### Stock and Index Additional Signals

| Signal | Long | Short | Applies To |
|--------|:----:|:-----:|-----------|
| Volume > 1.5× 20-day avg at extreme | +1 | +1 | Stocks, Indices |
| Broad index above EMA50 | +1 | — | Stocks only |
| Broad index below EMA50 | — | +1 | Stocks only |

#### Thresholds

| Market | Max Score | Min to Trade |
|--------|:---------:|:------------:|
| Forex | 10 | 6 |
| Crypto | 10 | 6 |
| Stocks | 12 | 7 |
| Indices | 11 | 7 |

### Step 5 — Cross-Market Normalisation

Scores are normalised to a common /10 scale before ranking:

```
Normalised Score = (Raw Score / Max Score) × 10
```

The single highest normalised score across all markets is selected as the trade. One output only.

### Step 6 — Trade Card Output

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TRADE PICKER — LIVE SIGNAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Market      : [Forex / Crypto / Stock / Index]
Direction   : LONG / SHORT
Instrument  : [SYMBOL — full name]
Entry Zone  : [price range]
Stop Loss   : [price]  (~X pips / points)
Target 1    : [price]  (+X pips) — close 50%
Target 2    : [price]  (+X pips) — close remainder
R:R         : ~XR blended
Confidence  : X/10 raw  (X.X/10 normalised)

Confluence signals:
  ✓ [Signal 1 — exact reading]
  ✓ [Signal 2 — exact reading]

Key levels:
  Support    : [price]
  Resistance : [price]

Invalidation: [specific price that cancels the trade]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## Invocation

Install the Agent Skill once, use in any session:

```bash
cp "Trade Picker/AgentSkill.md" ~/.claude/skills/trade-picker.md
```

| Command | Behaviour |
|---------|-----------|
| `/trade-picker` | Full scan — all markets |
| `/trade-picker forex` | Forex only |
| `/trade-picker crypto` | Crypto only |
| `/trade-picker stocks` | US equities and indices |
| `/trade-picker indices` | Major indices only |
| `/trade-picker account=10000` | Include position sizing at 1% risk |
| `/trade-picker account=10000 risk=2%` | Include position sizing at 2% risk |

---

## Documents in This Folder

| File | Purpose |
|------|---------|
| [README.md](./README.md) | This file — system overview and quick reference |
| [AgentSkill.md](./AgentSkill.md) | Full reusable Agent Skill definition — install to `~/.claude/skills/` |
| [ConfluenceGuide.md](./ConfluenceGuide.md) | Detailed rationale for every confluence signal — why it was chosen, its weight, and how it behaves per market |
| [TradeLog.md](./TradeLog.md) | Live trade log — all signals generated and their outcomes |
