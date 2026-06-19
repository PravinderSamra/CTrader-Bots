# GEX & OI — STAGE 1: DATA SOURCES & FEASIBILITY RESEARCH

---

## WHAT ARE WE BUILDING?

A pre-session and intra-session intelligence briefing agent that:
1. Pulls live GEX and OI data for each instrument
2. Generates simple charts with commentary
3. Produces a structured trade plan with scenarios and pivot points
4. Gives chart-marking instructions for key levels

---

## INSTRUMENT MAPPING: SPREAD BET → UNDERLYING OPTIONS MARKET

| Pepperstone Symbol | Underlying Index | Options Market | Primary Ticker for GEX |
|-------------------|-----------------|----------------|------------------------|
| US500 / S&P500    | S&P 500         | CBOE (SPX, SPXW, SPY) | **SPX** (index options) / **SPY** (ETF) |
| UK100             | FTSE 100        | ICE/LIFFE (UKX) | **EWU / ISF** (ETF proxy) |
| Ger40             | DAX 40          | EUREX (FDAX)   | **EWG / DXGE** (ETF proxy) |
| XAUUSD            | Gold Spot       | COMEX futures + CBOE (GLD options) | **GLD** (ETF) |

### Reality Check by Instrument

**US500 / SPX — EXCELLENT data availability**
- SPX and SPY options on CBOE — deepest options market in the world
- Alpha Vantage REALTIME_OPTIONS provides: strike, expiry, OI, gamma, delta, vega, theta, IV, bid/ask
- GEX can be calculated precisely
- Put/call ratio available
- VIX (SPX 30-day implied vol) available for free

**XAUUSD — GOOD data availability**
- GLD ETF options are heavily traded on CBOE
- Alpha Vantage REALTIME_OPTIONS covers GLD
- Gold OI from COMEX futures also available via free sources
- Alpha Vantage GOLD_SILVER_SPOT gives live spot price
- Reasonable GEX proxy via GLD options

**UK100 — LIMITED free data**
- FTSE 100 index options trade on ICE/LIFFE — NOT available on Alpha Vantage
- No direct free API for FTSE options with Greeks
- Best free approach: 
  - Use EWU (iShares MSCI UK ETF) as limited proxy for options sentiment
  - Supplement with: RSP put/call ratio trend, news sentiment, VIX co-movement
  - Use SPX GEX as cross-market risk indicator (high correlation on risk-off days)

**Ger40 — LIMITED free data**
- DAX 40 options trade on EUREX — NOT available via free APIs
- Best free approach:
  - Use EWG (iShares MSCI Germany ETF) as limited proxy
  - Use DAX futures OI from public CME/EUREX reports (weekly, not real-time)
  - Use broader European sentiment proxies

---

## AVAILABLE FREE DATA SOURCES (via MCP)

### 1. Alpha Vantage (PRIMARY — requires free API key)
**Sign up at:** alphavantage.co/support/#api-key (completely free)
**Free tier:** 25 API calls per day, 5 calls per minute

| Tool | What it provides | Instruments |
|------|-----------------|-------------|
| REALTIME_OPTIONS | Full options chain with Greeks (gamma, delta, OI, IV) | SPX, SPY, GLD, QQQ |
| HISTORICAL_OPTIONS | Historical options chain with Greeks | All of above |
| GLOBAL_QUOTE | Live equity/ETF price | SPY, GLD, QQQ |
| GOLD_SILVER_SPOT | Live gold and silver spot price | XAUUSD |
| NEWS_SENTIMENT | Market news + AI sentiment scores | All major |
| TREASURY_YIELD | 3M, 2Y, 5Y, 10Y, 30Y yields | Macro context |
| VIX (via GLOBAL_QUOTE on ^VIX) | Volatility index | Risk gauge |
| MARKET_STATUS | Global market open/closed status | Session awareness |

### 2. TradingView MCP (SECONDARY — no API key needed)
| Tool | What it provides |
|------|-----------------|
| get_live_price | Live prices for major symbols |
| market_sentiment | Bullish/bearish sentiment reading |
| multi_timeframe_analysis | Technical analysis across timeframes |
| market_snapshot | Global market overview |
| financial_news | Recent market headlines |
| smart_volume_scanner | Volume anomaly detection |

### 3. News MCP (SUPPLEMENTARY)
- Real-time market news by topic and region
- Useful for pre-session macro context

### 4. Tavily Search (RESEARCH)
- Web search for additional data not available via APIs
- Can scrape VIX futures term structure, CBOE data pages

---

## GEX CALCULATION METHODOLOGY

### Formula:
```
GEX per strike = Gamma × Open_Interest × Spot_Price² × Contract_Multiplier

Net GEX = Σ(Call GEX) - Σ(Put GEX)

Total Absolute GEX = Σ|GEX per strike|
```

For SPX options: contract_multiplier = 100

### Interpretation:
| GEX Value | Market Condition | Implication |
|-----------|-----------------|-------------|
| Large Positive | Dealers are long gamma | Price pinned — dealers sell rallies/buy dips → low volatility, mean reversion |
| Near Zero | Gamma neutral | Price can move freely in either direction |
| Large Negative | Dealers are short gamma | Dealers amplify moves — buy rallies/sell dips → trending, high volatility |

### Key GEX Levels:
- **Max GEX Strike**: Strongest "gravity" level — price tends to gravitate here
- **Zero GEX Crossover**: Where dealer positioning flips — crossing this unlocks volatility
- **Put Wall**: Cluster of large put OI — natural support (dealers delta hedge by buying)
- **Call Wall**: Cluster of large call OI — natural resistance (dealers delta hedge by selling)

---

## OPEN INTEREST ANALYSIS

### What to measure:
1. **OI by strike** (distribution across strikes): Reveals where market participants have concentrated bets
2. **OI change vs prior session**: Rising OI = new positions (confirmation); falling OI = position unwinding
3. **Put/Call OI ratio**: > 1.0 = more puts than calls (defensive/bearish hedging dominant)
4. **OI concentration at key strikes**: Magnetic levels for price

### Key OI Concepts:
- **Max Pain**: The strike where the maximum number of options contracts expire worthless — price has magnetic pull toward this strike near expiry
- **High OI Put strikes below spot**: Support levels (market makers delta hedge by holding long futures)
- **High OI Call strikes above spot**: Resistance levels (market makers delta hedge by holding short futures)

---

## COMPLEMENTARY DATA LAYERS FOR CONFLUENCE

| Data Layer | Source | Value Added |
|-----------|--------|-------------|
| VIX Level + Term Structure | Alpha Vantage + Tavily | Overall regime: low VIX = rangebound; high VIX = trending |
| Treasury Yields (2Y, 10Y) | Alpha Vantage | Macro risk-off/on; correlates with SPX direction |
| USD Index direction | TradingView / Alpha Vantage FX | Inverse correlation with Gold, affects indices |
| News Sentiment Score | Alpha Vantage NEWS_SENTIMENT | Pre-session bias check |
| Volume Profile (VWAP, POC) | TradingView | Where price accepted value; key levels |
| Multi-TF Technical Analysis | TradingView | Structure context for GEX levels |
| Economic Calendar | Tavily search | Know when to stand aside (FOMC, NFP, CPI) |
| CME COT Report | Tavily/CFTC | Large spec positioning for gold and indices |

---

## PEPPERSTONE SPREAD BET SPECIFICS

### Price Mapping:
- Pepperstone US500 tracks SPX with a small spread (~0.4 pts typical)
- Pepperstone UK100 tracks FTSE 100 cash index
- Pepperstone Ger40 tracks DAX 40 cash index  
- Pepperstone XAUUSD tracks gold spot (XAU/USD)

### Key Adjustments:
- GEX levels from SPX options are in SPX index points → directly applicable to US500
- GLD options-derived GEX: GLD price ≈ Gold price / 10, so multiply GLD strikes by 10 for XAUUSD levels
- UK100 and Ger40: No direct GEX — use broader analysis + cross-market context

### Session Times (London-based trader):
| Session | GMT | Key Events |
|---------|-----|-----------|
| Pre-London | 06:00–08:00 | Asian close, overnight data review |
| London Open | 08:00–10:00 | Primary session for UK100, Ger40 |
| NY Open | 13:30–16:00 | Primary session for US500 — GEX most active |
| London/NY Overlap | 13:30–16:00 | Highest liquidity across all instruments |
| Gold | Most active 13:30–18:00 | Follows NY session, COMEX open |

---

## DATA CALL BUDGET (25 API calls/day on Alpha Vantage free tier)

### Morning Session (8 calls):
1. MARKET_STATUS — is market open?
2. REALTIME_OPTIONS SPX — GEX + OI calculation
3. REALTIME_OPTIONS SPY — cross-reference
4. GLOBAL_QUOTE ^VIX — volatility regime
5. GOLD_SILVER_SPOT — XAUUSD spot
6. REALTIME_OPTIONS GLD — gold GEX + OI
7. TREASURY_YIELD (10Y) — macro context
8. NEWS_SENTIMENT — pre-session headlines

### Intra-session Update (5 calls):
9. REALTIME_OPTIONS SPX — refreshed GEX
10. GLOBAL_QUOTE ^VIX — updated VIX
11. REALTIME_OPTIONS GLD — updated gold
12. NEWS_SENTIMENT — mid-session headlines
13. GLOBAL_QUOTE SPY — live price for reference

### Reserve (12 calls): Historical lookups, additional analysis

**Note:** Upgrading to Alpha Vantage premium ($50/month) gives unlimited calls and is recommended once the workflow is proven.

---

## DATA SOURCES REQUIRING SIGN-UP (ALL FREE)

| Service | URL | What you get | Setup time |
|---------|-----|-------------|-----------|
| **Alpha Vantage** | alphavantage.co | Primary options + GEX data | 2 min |
| **CBOE** (optional) | cboe.com/delayed_quotes | Free delayed options data for verification | 5 min |
| **CME Group** (optional) | cmegroup.com | Futures OI reports (weekly) | 5 min |

---

## INSTRUMENTS WHERE GEX IS NOT APPLICABLE (use alternative approach)

For UK100 and Ger40 where direct GEX data is unavailable, we substitute:

1. **Dealer Positioning Proxy**: SPX GEX regime (positive/negative) as cross-market risk indicator
2. **Futures OI**: Weekly CME/EUREX reports for broad positioning
3. **ETF Options**: EWG, EWU as imperfect but usable proxies
4. **Sentiment + Structure**: TradingView multi-TF analysis + news sentiment
5. **Correlation Matrix**: SPX/DAX correlation typically 0.85+ — SPX GEX regime applies
