# GEX & OI — MCP & API SETUP GUIDE

---

## STEP 1: Alpha Vantage Free API Key (REQUIRED)

This is the primary data source for all GEX and OI calculations.

1. Go to: **https://www.alphavantage.co/support/#api-key**
2. Enter your email address
3. You will receive your free API key immediately
4. Free tier gives you: **25 API calls per day, 5 calls per minute**

Once you have your key, set it as an environment variable:

```bash
# Add to your ~/.bashrc or ~/.zshrc
export ALPHA_VANTAGE_API_KEY="YOUR_KEY_HERE"
```

Or in a .env file in the agent_skill directory:
```
ALPHA_VANTAGE_API_KEY=YOUR_KEY_HERE
```

---

## STEP 2: Python Dependencies

```bash
pip install requests pandas numpy matplotlib python-dotenv
```

---

## STEP 3: Running the Agent

### Morning Session Briefing (full):
```bash
cd "GEX&OI/agent_skill"
python gex_oi_agent.py --instrument US500 --instrument XAUUSD --session morning
```

### Intra-session Update (quick refresh):
```bash
python gex_oi_agent.py --instrument US500 --session intraday
```

### All instruments:
```bash
python gex_oi_agent.py --all --session morning
```

---

## STEP 4: Using Within Claude AI Sessions (MCP-Powered)

When working in a Claude Code session with the available MCPs, you can ask:

> "Run a full GEX and OI briefing for US500 and XAUUSD for today's session"

Claude will use the **Alpha Vantage MCP** tools directly:
- `REALTIME_OPTIONS` for SPX and GLD options chains
- `GLOBAL_QUOTE` for spot prices and VIX
- `GOLD_SILVER_SPOT` for live gold price
- `NEWS_SENTIMENT` for pre-session headlines
- `TREASURY_YIELD` for macro context

Combined with **TradingView MCP** tools:
- `market_sentiment` for broader sentiment
- `multi_timeframe_analysis` for structure context
- `financial_news` for additional headlines

---

## STEP 5: Claude Session Workflow (Recommended Daily Flow)

### 8:00 AM GMT (Before London Open):
Ask Claude:
> "Start a morning GEX & OI briefing for [US500/XAUUSD/UK100/Ger40]"

Claude will:
1. Fetch SPX options chain → calculate GEX
2. Fetch GLD options chain → calculate gold GEX/OI
3. Pull VIX, yields, gold spot
4. Fetch latest news sentiment
5. Generate charts for each instrument
6. Produce trade plan with specific levels

### During Session (if picture changes):
Ask Claude:
> "Give me an intraday GEX update for US500 — has anything changed?"

---

## AVAILABLE MCP TOOLS IN CLAUDE SESSIONS

| MCP Server | Key Tools for GEX/OI |
|-----------|---------------------|
| alpha-vantage | REALTIME_OPTIONS, HISTORICAL_OPTIONS, GLOBAL_QUOTE, GOLD_SILVER_SPOT, NEWS_SENTIMENT, TREASURY_YIELD |
| tradingview-mcp | market_sentiment, multi_timeframe_analysis, financial_news, get_live_price, market_snapshot |
| newsmcp | get_news (by topic/region) |
| tavily | tavily_search (for CBOE data, VIX term structure, COT reports) |
| ctrader | get_spot_prices (live Pepperstone prices for spread bet mapping) |

---

## OPTIONAL: CBOE Free Data (for verification)

CBOE publishes free delayed options data:
- Website: **https://www.cboe.com/delayed_quotes/**
- Free GEX charts: **https://spotgamma.com** (limited free tier)
- VIX term structure: **https://vixcentral.com** (free)

---

## INSTRUMENT API MAPPING REFERENCE

| Pepperstone Symbol | Options Ticker (API) | Notes |
|-------------------|---------------------|-------|
| US500 | SPX | Direct — best data |
| XAUUSD | GLD | GLD strikes × 10 = Gold price levels |
| UK100 | EWU | Proxy only — limited usefulness |
| Ger40 | EWG | Proxy only — limited usefulness |

---

## API CALL BUDGET TRACKER

**Free tier: 25 calls/day**

| Call | Instrument | Purpose | Count |
|------|-----------|---------|-------|
| MARKET_STATUS | All | Is market open? | 1 |
| REALTIME_OPTIONS SPX | US500 | GEX + OI | 1 |
| REALTIME_OPTIONS GLD | XAUUSD | GEX + OI | 1 |
| GLOBAL_QUOTE VIX | All | Volatility regime | 1 |
| GOLD_SILVER_SPOT | XAUUSD | Live spot price | 1 |
| TREASURY_YIELD | All | Macro context | 1 |
| NEWS_SENTIMENT | All | Pre-session news | 1 |
| **Morning total** | | | **7** |
| REALTIME_OPTIONS SPX | US500 | Intraday refresh | 1 |
| REALTIME_OPTIONS GLD | XAUUSD | Intraday refresh | 1 |
| GLOBAL_QUOTE VIX | All | VIX check | 1 |
| **Intraday total** | | | **3** |
| **Daily total** | | | **10** |
| **Reserve** | | | **15** |

Upgrade to Alpha Vantage Premium ($50/month) for unlimited calls when workflow is proven.
