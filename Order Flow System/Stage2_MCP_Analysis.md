# STAGE 2: FREE MCP DATA SOURCES — ANALYSIS AND CAPABILITY MAPPING
## Order Flow Trading System — Data Infrastructure

---

## OVERVIEW

This document catalogues all free MCP servers available to Claude for use in the order flow trading analysis system, maps their capabilities against the order flow strategy requirements from Stage 1, and identifies gaps to fill.

---

## CONNECTED MCPs (Confirmed Available)

### 1. CoinGecko MCP (`mcp__coingecko`)
**Cost:** Free tier available  
**Authentication:** Pre-authenticated SDK client via `execute` tool  

**Capabilities:**
- Cryptocurrency prices (spot and historical OHLCV)
- Market capitalisation, volume, circulating supply
- Price change percentages (1h, 24h, 7d, 30d)
- Trending coins and tokens
- Exchange data (volumes, order book depth on supported exchanges)
- Token metadata and project information
- Market dominance data

**Order Flow Relevance:**
| Order Flow Need | Coverage |
|----------------|---------|
| Crypto price levels for OB/FVG identification | ✅ Full historical OHLCV |
| Session highs/lows (identify NY session levels) | ✅ Via hourly OHLCV |
| Volume data for volume profile approximation | ✅ Volume by timeframe |
| Identifying premium/discount zones | ✅ Via price range analysis |
| Real-time DOM / order book depth | ⚠️ Partial (some exchanges) |
| Delta / bid-ask volume split | ❌ Not available |
| Footprint chart data | ❌ Not available |

**Best Use:** Identifying key price levels, session highs/lows, and volume zones for BTC, ETH, and altcoins. Supplement with exchange-specific APIs for execution-level data.

---

### 2. Alpha Vantage MCP (`mcp__alpha-vantage`) *(currently disconnected but accessible)*
**Cost:** Free tier (25 requests/day on free plan)  
**Authentication:** API key via MCP config  

**Capabilities:**
- Stocks: Full OHLCV (intraday 1min–60min, daily, weekly, monthly)
- Forex: OHLCV for all major pairs (EUR/USD, GBP/USD, USD/JPY, etc.)
- Crypto: OHLCV for major cryptocurrencies
- Technical indicators: RSI, MACD, Bollinger Bands, EMA, SMA, VWAP, and 50+ others
- Economic indicators: GDP, CPI, inflation, unemployment, retail sales
- Earnings data

**Order Flow Relevance:**
| Order Flow Need | Coverage |
|----------------|---------|
| Forex pair price levels (EUR/USD, GBP/USD, etc.) | ✅ Full intraday OHLCV |
| VWAP calculation | ✅ Built-in VWAP indicator |
| RSI divergence for confluence | ✅ Built-in RSI |
| Session high/low identification | ✅ Via intraday data |
| Economic calendar data (CPI, NFP timing) | ✅ Economic indicators |
| Volume profile approximation | ✅ Volume data available |
| Real-time tick data | ❌ Not available |
| Footprint / delta data | ❌ Not available |

**Limitation:** 25 requests/day on free plan is very restrictive. Best used for pre-session preparation and level identification, not real-time monitoring.

---

### 3. AKTools MCP (`mcp__aktools`) *(currently disconnected)*
**Cost:** Free  
**Authentication:** None required  

**Capabilities:**
- OKX prices and market data (crypto)
- OKX taker volume — **critical for delta approximation**
- OKX loan ratios (funding/sentiment data)
- Binance AI market report
- US stock prices (OHLCV)
- US stock technical indicators
- HK and A-share stock indicators
- Stock sector fund flow rankings — **institutional money flow data**
- Stock news (domestic and global)
- Trading suggestions (AI-generated)
- Stock information and fundamentals

**Order Flow Relevance:**
| Order Flow Need | Coverage |
|----------------|---------|
| OKX crypto price levels for key structure | ✅ Direct OKX data |
| **Taker volume (buy vs. sell aggression)** | ✅ OKX taker volume — best free delta proxy |
| Funding rates as sentiment/positioning indicator | ✅ Loan ratios |
| Stock sector fund flows (which sectors institutions favour) | ✅ Fund flow rankings |
| Binance market intelligence | ✅ AI report |
| Market news for catalyst identification | ✅ Global news feed |
| Footprint data | ❌ Not available |

**Key Value:** The OKX taker volume tool is the closest free approximation to delta data available. Taker volume = aggressive buy/sell volume = the core input for delta analysis.

---

### 4. Tavily MCP (`mcp__tavily`) *(currently disconnected)*
**Cost:** Free tier (1,000 searches/month)  
**Authentication:** API key via MCP config  

**Capabilities:**
- Real-time web search
- Deep web crawl and content extraction
- Research aggregation
- Financial news search

**Order Flow Relevance:**
| Order Flow Need | Coverage |
|----------------|---------|
| Real-time financial news for catalyst identification | ✅ |
| Economic calendar events (FOMC, CPI, NFP dates/times) | ✅ Via search |
| Market commentary and sentiment | ✅ |
| Price levels and analyst targets | ✅ Via search |
| DOM/footprint data | ❌ |

**Best Use:** Economic calendar monitoring, news catalyst identification before session, market sentiment research.

---

### 5. News MCP (`mcp__newsmcp`) *(currently disconnected)*
**Cost:** Free  
**Authentication:** None required  

**Capabilities:**
- News articles filtered by topic
- News articles filtered by region
- News detail extraction

**Order Flow Relevance:**
- Economic data release monitoring
- Geopolitical event tracking
- Central bank announcement tracking
- Sector-specific news for fundamental context

---

### 6. PineScript Docs MCP (`mcp__pinescript-docs`) *(currently disconnected)*
**Cost:** Free  
**Authentication:** None required  

**Capabilities:**
- Access to complete Pine Script v5/v6 documentation
- Function validation
- Strategy builder integration

**Order Flow Relevance:**
- Build TradingView indicators for: volume profile, VWAP, order blocks, FVGs, CVD approximation
- Generate Pine Script code for session high/low levels, premium/discount zones, BOS/CHoCH markers
- Custom alerts based on order flow criteria

---

### 7. GitHub MCP (`mcp__github`)
**Cost:** Free  
**Authentication:** Pre-authenticated  

**Capabilities:**
- Repository management
- File creation and updates
- Code review and PR management

**Order Flow Relevance:**
- Version control for all strategy code and analysis scripts
- Publishing analysis reports
- Collaborative development of the trading system

---

### 8. File Operations MCP (`mcp__ff8ae4c9-1d98-4857-b484-556f7528ad79`)
**Cost:** Free (local)  
**Authentication:** None required  

**Capabilities:**
- Read, write, copy, and search files
- File metadata
- Download file content

**Order Flow Relevance:**
- Persistent storage of analysis results
- Saving pre-session level reports
- Storing trade logs and historical analysis

---

## CAPABILITY GAP ANALYSIS

### What We Can Do With Current MCPs

| Order Flow Analysis Task | Available Tool | Quality |
|--------------------------|---------------|---------|
| Crypto price levels (BTC, ETH) — OB/FVG identification | CoinGecko | ✅ Good |
| Forex price levels (EUR/USD, GBP/USD, etc.) | Alpha Vantage | ✅ Good |
| Session highs/lows (prior day, prior week) | Alpha Vantage + CoinGecko | ✅ Good |
| VWAP calculation | Alpha Vantage | ✅ Good |
| Volume data for profile approximation | Alpha Vantage + CoinGecko | ⚠️ Approximate |
| **Buy/Sell volume split (delta proxy)** | **AKTools OKX taker volume** | **⚠️ Approximate** |
| Funding rate / sentiment for crypto | AKTools | ✅ Good |
| Economic calendar — news catalysts | Tavily + News MCP | ✅ Good |
| Market news and context | AKTools + News MCP | ✅ Good |
| Sector/institutional fund flows | AKTools | ✅ Good |
| Premium/discount zone calculation | Computed from price data | ✅ Good |
| BOS/CHoCH identification | Computed from OHLCV | ✅ Good |
| Order block identification | Computed from OHLCV | ✅ Good |
| FVG identification | Computed from OHLCV | ✅ Good |
| Liquidity pool identification | Computed from OHLCV | ✅ Good |

### Critical Gaps (Not Available in Free MCPs)

| Missing Capability | Why It Matters | Potential Solution |
|-------------------|---------------|-------------------|
| **Real-time tick data** | Required for precise entry timing and live DOM reading | Broker API integration (Stage 3) |
| **True footprint chart data** | Bid/ask volume at every price tick | Futures exchange data feeds (NinjaTrader, Sierra Chart) |
| **Level 2 DOM data** | Live order book depth | Broker/exchange WebSocket APIs |
| **True cumulative delta** | Needs tick-by-tick bid/ask classification | Exchange tick data feeds |
| **Real-time futures data (ES, NQ)** | Primary order flow markets | CME datafeed or broker API |
| **Options flow / dark pool prints** | Institutional positioning signals | Paid services (unusual whales, etc.) |

---

## RECOMMENDED FREE ADDITIONAL MCPs TO ADD

### Priority 1 — High Value, Free, Easy to Connect

**Binance Public API (via custom MCP or direct WebFetch)**
- Free, no API key required for public endpoints
- Provides: OHLCV for all pairs, aggregate trade data (taker buy/sell volume), order book snapshots, kline data
- Taker buy/sell volume directly available — excellent delta proxy for crypto
- WebSocket streams available for real-time data

**Bybit Public API**
- Free public endpoints
- Similar to Binance — OHLCV, taker volume, funding rates, order book

**Yahoo Finance (via yfinance or direct scrape)**
- Free historical OHLCV for stocks, forex, indices
- Useful for indices (^GSPC = S&P 500, ^NDX = Nasdaq 100) when CME futures data is unavailable
- Can approximate daily/weekly structure for ES/NQ context

**Federal Reserve Economic Data (FRED) API**
- Free API
- Economic indicators: CPI, Fed Funds Rate, Unemployment, Retail Sales
- Critical for understanding macro context that drives institutional order flow

**Investing.com Economic Calendar (via scrape)**
- Free economic calendar with all high-impact events
- FOMC dates, CPI release dates, NFP dates — essential for avoiding news risk

### Priority 2 — Moderate Value, Free

**CryptoCompare API**
- Free tier: historical OHLCV, volume by exchange, market cap
- Complements CoinGecko for cross-exchange volume data

**Exchange-Specific Public APIs (Direct WebFetch)**
- OKX REST API: order book, taker volume, funding rates (complements AKTools)
- Deribit API: options data for crypto — useful for gauging institutional positioning via put/call ratios

**Stooq (via pandas-datareader / WebFetch)**
- Free historical data for indices, commodities, forex
- Useful for DAX, gold, crude oil data

### Priority 3 — Supporting Data

**Reddit API / Social Sentiment**
- Free tier
- WallStreetBets, CryptoMarkets sentiment as contrarian indicator (extreme sentiment = potential reversal)

**Fear & Greed Index API**
- Free, no authentication
- CNN Fear & Greed (stocks) and Crypto Fear & Greed
- Sentiment extremes align with Wyckoff accumulation/distribution and capitulation setups

---

## SYSTEM ARCHITECTURE — WHAT CLAUDE CAN DO WITH THESE MCPs

### Pre-Session Analysis Workflow (Automated)

```
1. CONTEXT LAYER (Higher Timeframe)
   ├── Alpha Vantage: Pull daily OHLCV for forex pairs (EUR/USD, GBP/USD, USD/JPY)
   ├── CoinGecko: Pull daily OHLCV for BTC, ETH
   ├── Yahoo Finance / Stooq: Pull daily data for ES, NQ, DAX context
   └── Compute: Weekly/daily trend direction, premium/discount zones, macro bias

2. LEVEL IDENTIFICATION
   ├── Identify prior day high/low, prior week high/low
   ├── Identify Asian session range (if applicable)
   ├── Compute approximate volume profile from hourly OHLCV
   ├── Mark unmitigated order blocks (last opposing candle before impulse)
   ├── Mark fair value gaps (three-candle imbalances)
   └── Mark key VWAP levels (Alpha Vantage)

3. LIQUIDITY POOL MAPPING
   ├── Identify equal highs/equal lows (liquidity magnets)
   ├── Mark prior session extremes
   ├── Mark round number levels
   └── Identify likely stop hunt targets

4. ORDER FLOW DATA LAYER
   ├── AKTools: OKX taker volume — assess buy/sell aggression over last N sessions
   ├── CoinGecko: Volume trends — is buying or selling volume dominating?
   ├── AKTools: Funding rates — are traders overleveraged long or short?
   └── Compute: CVD approximation from taker volume data

5. NEWS / CATALYST CHECK
   ├── Tavily: Search for upcoming economic events today/this week
   ├── News MCP: Pull recent market news for the target asset
   └── Flag: Any high-impact events within trading window?

6. BIAS DETERMINATION
   └── Output: Bullish / Bearish / Neutral bias with confidence level
       Key levels to watch (support, resistance, targets)
       Order flow alignment summary
       Recommended session to trade (London / NY)
       Risk warning if news events imminent
```

### Trade Signal Generation Workflow

```
1. Price arrives at a pre-marked level
2. Pull latest OHLCV candles (5-min, 15-min)
3. Check:
   ├── Is this level unmitigated? (OB/FVG check)
   ├── Is price in the correct premium/discount zone?
   ├── Is market structure (BOS/CHoCH) aligned?
   ├── Is there a preceding liquidity grab?
   └── What does taker volume / delta proxy show at this level?
4. Score the setup (A+/B/C)
5. If A+ or B:
   ├── Calculate entry price, stop loss, targets
   ├── Calculate position size based on 1% risk
   └── Output: Trade Signal Report
6. Monitor for invalidation
```

---

## STAGE 3 PREVIEW — WHAT WE NEED TO BUILD

Based on Stage 1 (strategy) and Stage 2 (data), Stage 3 will involve building:

1. **Market Scanner** — Automatically scans configured markets (indices, forex, crypto, commodities) and identifies which assets are at key order flow levels.

2. **Pre-Session Report Generator** — Runs before each trading session and outputs a structured report with: session bias, key levels, order flow context, news risks, and setup candidates.

3. **Setup Scorer** — Takes a specific price level and scores the quality of a setup based on the confluence framework (3-layer context/location/confirmation).

4. **Trade Calculator** — Given entry, stop, and account size: calculates position size, risk in dollars, risk:reward, and profit targets.

5. **Order Flow Dashboard** — Aggregates taker volume data, delta approximations, funding rates, and news into a single view per asset.

6. **Alert System** — Monitors when price approaches key pre-marked levels and triggers analysis.

---

---

## MAJOR ADDITION: TradingView MCP (`mcp__tradingview-mcp`)

**Cost:** Free tier (configured in .mcp.json)  
**Status:** ✅ Connected  
**Assessment: This is the most powerful MCP in our stack for order flow analysis.**

### Full Tool Inventory

| Tool | Order Flow Use |
|------|---------------|
| `get_live_price` | Real-time price for any symbol — critical for live level monitoring |
| `get_multi_price` | Simultaneous prices across multiple markets (scan all watchlist symbols) |
| `multi_timeframe_analysis` | **Automated top-down analysis across multiple TFs — core workflow tool** |
| `combined_analysis` | Full technical + order flow combined analysis for a symbol |
| `market_snapshot` | Broad market overview including sector performance |
| `market_sentiment` | Sentiment data — useful for identifying capitulation/exhaustion |
| `get_global_market_overview` | Global macro context across all asset classes |
| `financial_news` | Live financial news per symbol — catalyst identification |
| `recognize_market_pattern` | **Automated pattern recognition including order flow patterns** |
| `advanced_candle_pattern` | Candle pattern detection (engulfing, hammers, shooting stars, etc.) |
| `smart_volume_scanner` | **Volume anomaly detection — identifies unusual institutional volume** |
| `volume_breakout_scanner` | Scans for volume-confirmed breakouts |
| `volume_confirmation_analysis` | Confirms if a move has volume behind it or is low-conviction |
| `consecutive_candles_scan` | Identifies momentum runs (useful for exhaustion detection) |
| `bollinger_scan` | Bollinger squeeze detection — volatility compression before breakout |
| `rating_filter` | Filter symbols by technical rating (strong buy/sell) |
| `bse_fibonacci_retracement` | Fibonacci levels for premium/discount/OTE zone calculation |
| `nse_fibonacci_retracement` | Same for NSE |
| `egx_fibonacci_retracement` | Same for EGX |
| `assess_liquidity_for_trade` | **Liquidity assessment for a trade — directly maps to order flow liquidity analysis** |
| `assess_trade_risk_full` | Full risk analysis including market context |
| `assess_portfolio_trade_risk` | Portfolio-level risk assessment |
| `calculate_trade_metrics` | Entry, stop, target metrics calculation |
| `risk_based_position_size` | Position sizing based on account risk — 1% rule implementation |
| `get_kelly_position_size` | Kelly criterion position sizing |
| `kelly_position_size` | Kelly criterion variant |
| `portfolio_position_size` | Portfolio-aware position sizing |
| `get_trade_levels` | Support/resistance levels — maps to key order flow levels |
| `list_trade_signals` | Active trade signals |
| `save_trade_signal` | Save and track trade setups |
| `dispatch_trade_alert` | Send trade alerts |
| `create_price_alert` | Set price level alerts for when price reaches key levels |
| `get_active_price_alerts` | Monitor active alerts |
| `set_user_alert_preferences` | Configure alert settings |
| `record_trade` | Trade journal logging |
| `get_user_trade_history` | Historical trade performance |
| `get_portfolio_trade_history` | Portfolio-level trade history |
| `get_user_portfolio` | Current portfolio positions |
| `execute_order` | Order execution (if broker connected) |
| `execute_portfolio_trade` | Portfolio trade execution |
| `close_trade` | Close a position |
| `coin_analysis` | Deep crypto analysis |
| `top_gainers` | Top gaining assets (momentum screening) |
| `top_losers` | Top losing assets (potential capitulation candidates) |
| `detect_market_anomalies` | **Anomaly detection — flags unusual market behaviour** |
| `generate_pinescript_strategy` | Auto-generate Pine Script strategy code |
| `backtest_strategy` | Backtest a strategy on historical data |
| `backtest_pinescript_multi_symbol` | Backtest across multiple symbols simultaneously |
| `optimize_strategy` | Optimise strategy parameters |
| `optimize_pinescript_strategy` | Optimise Pine Script strategy |
| `walk_forward_backtest_strategy` | Walk-forward testing (most robust validation method) |
| `compare_strategies` | Compare performance of multiple strategies |
| `get_open_strategy_schema` | Get current strategy structure |
| `multi_agent_analysis` | Multi-agent analysis framework |
| `compute_portfolio_correlation` | Portfolio correlation analysis |
| `yahoo_price` | Yahoo Finance price data |
| `market_sentiment` | Broader market sentiment assessment |
| NSE/BSE/EGX tools | Indian and Egyptian market analysis (specialised markets) |

### TradingView MCP — Order Flow Coverage Update

| Order Flow Analysis Task | TradingView MCP Tool | Quality |
|--------------------------|---------------------|---------|
| **Multi-timeframe top-down analysis** | `multi_timeframe_analysis` | ✅ Excellent |
| Price levels — support/resistance/key levels | `get_trade_levels` | ✅ Excellent |
| Real-time price monitoring | `get_live_price`, `get_multi_price` | ✅ Excellent |
| Volume analysis — anomalies and confirmation | `smart_volume_scanner`, `volume_confirmation_analysis` | ✅ Excellent |
| Volume breakouts (LVN breakout detection) | `volume_breakout_scanner` | ✅ Excellent |
| Pattern recognition (OB, FVG-type patterns) | `recognize_market_pattern`, `advanced_candle_pattern` | ✅ Good |
| Fibonacci levels (premium/discount/OTE) | `bse_fibonacci_retracement` (adaptable) | ✅ Good |
| Liquidity assessment | `assess_liquidity_for_trade` | ✅ Excellent |
| Trade risk assessment | `assess_trade_risk_full` | ✅ Excellent |
| Market sentiment and anomaly detection | `detect_market_anomalies`, `market_sentiment` | ✅ Excellent |
| Position sizing (1% risk rule) | `risk_based_position_size` | ✅ Excellent |
| Trade metrics (entry/stop/target) | `calculate_trade_metrics` | ✅ Excellent |
| News catalysts | `financial_news` | ✅ Excellent |
| Price alerts at key levels | `create_price_alert` | ✅ Excellent |
| Pine Script strategy generation + backtesting | `generate_pinescript_strategy`, `backtest_strategy` | ✅ Excellent |
| Trade journaling | `record_trade`, `get_user_trade_history` | ✅ Excellent |
| Global market context | `get_global_market_overview` | ✅ Excellent |
| Footprint chart data (bid/ask delta) | ❌ Not available | ❌ Still a gap |
| True Level 2 DOM data | ❌ Not available | ❌ Still a gap |

**The TradingView MCP closes the majority of our data gaps and provides a nearly complete free stack for order flow analysis.**

---

## REVISED CAPABILITY ASSESSMENT

### With TradingView MCP Added — Complete Stack Coverage

**Fully Covered (Free, No-Cost):**
- ✅ Multi-timeframe analysis for any symbol (indices, forex, crypto, commodities)
- ✅ Live price monitoring across all markets
- ✅ Volume analysis, anomaly detection, volume confirmation
- ✅ Key support/resistance/structural level identification
- ✅ Pattern recognition (candle patterns, market patterns)
- ✅ Fibonacci premium/discount/OTE zones
- ✅ Liquidity assessment
- ✅ Risk management (position sizing, trade metrics)
- ✅ News catalyst monitoring
- ✅ Price alerts at key levels
- ✅ Strategy backtesting and optimisation
- ✅ Trade logging and performance tracking
- ✅ Market sentiment and global context
- ✅ Crypto analysis (CoinGecko + TradingView + AKTools)
- ✅ Forex analysis (Alpha Vantage + TradingView)
- ✅ Stock/indices analysis (TradingView + AKTools)

**Remaining Gaps (Require Broker/Exchange Integration in Stage 3):**
- ❌ True tick-by-tick footprint data (bid/ask at every tick)
- ❌ Live Level 2 DOM order book
- ❌ True cumulative delta (requires tick data)
- ❌ Iceberg order detection (requires Bookmap-level data)

**Mitigation for Gaps:**
- AKTools taker volume = best free proxy for aggressive buy/sell (delta approximation)
- TradingView volume confirmation = identifies if a move has institutional backing
- Smart volume scanner = detects unusual volume that often correlates with institutional activity
- These proxies are sufficient for identifying high-quality setups on higher timeframes (15M and above)

---

## MCP CONNECTION STATUS SUMMARY

| MCP | Status | Priority | Key Data for Order Flow |
|-----|--------|----------|------------------------|
| **TradingView MCP** | ✅ Connected | **Critical** | Multi-TF analysis, volume, live prices, patterns, risk management, backtesting |
| CoinGecko | ✅ Connected | High | Crypto OHLCV + volume |
| Alpha Vantage | ⚠️ Reconnecting | High | Forex + stocks OHLCV + VWAP |
| AKTools | ⚠️ Reconnecting | High | **Taker volume (delta proxy)** + OKX data + fund flows |
| Tavily | ⚠️ Reconnecting | Medium | Deep news research + economic calendar |
| PineScript Docs | ⚠️ Reconnecting | Medium | TradingView Pine Script indicator building |
| News MCP | ⚠️ Reconnecting | Medium | Market news feed |
| GitHub MCP | ✅ Connected | High | Version control + publishing |
| File Ops MCP | ✅ Connected | High | Persistent storage + analysis files |

*Note: "Reconnecting" MCPs are configured in .mcp.json and reconnect automatically between sessions.*
