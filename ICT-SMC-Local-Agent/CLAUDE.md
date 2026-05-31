# ICT/SMC Market Scanner — Local Agent (Mac / Desktop)

## What This Is

The Local Agent is the full-capability version of the ICT/SMC scanner. It runs on your Mac with cTrader desktop installed, giving access to the cTrader Local MCP server — chart control, live price feeds, DOM/Level 2 data (Phase 3), and direct trade execution.

**This is the Local Agent** — for Mac desktop use with Claude Code.
**The Remote Agent** is in `/ICT-SMC-Remote-Agent/` — for phone/web use (lighter, no Local MCP needed).

Both agents share identical analysis logic. Bugs fixed in `analysis/` should be applied to both.

---

## Quick Start (New Machine / Reinstall)

```bash
cd ICT-SMC-Local-Agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add TWELVE_DATA_API_KEY
python main.py
```

---

## Local MCP Setup (Mac)

1. Install **cTrader** desktop app (Mac version from ctrader.com)
2. Log in with your FTMO cTrader account
3. Go to **Settings → AI Agent Connect → Local MCP**
4. Follow the setup wizard — it installs the local MCP server and gives you the config path
5. Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "ctrader-local": {
      "type": "stdio",
      "command": "/Applications/cTrader.app/Contents/MacOS/ctrader-mcp-server"
    }
  }
}
```

*(Exact command path provided by cTrader after setup)*

6. Restart Claude Code — the `ctrader-local` MCP tools will appear

---

## What Local MCP Adds (vs Remote Agent)

| Capability | Remote Agent | Local Agent |
|---|---|---|
| Market scan (FVG/OB/levels) | ✅ | ✅ |
| FTMO risk context | ✅ | ✅ |
| Live prices | ✅ | ✅ |
| Historical candles | ✅ (Yahoo/Twelve Data) | ✅ + cTrader (Phase 2) |
| Chart control | ❌ | ✅ (open, navigate, change symbol) |
| Indicator values | ❌ | ✅ (read EMA, RSI, etc. from chart) |
| Trade execution | ❌ | ✅ (Phase 2) |
| DOM / Level 2 heatmap | ❌ | ✅ (Phase 3) |
| Workspace management | ❌ | ✅ |

---

## Architecture

```
ICT-SMC-Local-Agent/
├── main.py                     Entry point — run this
├── config/settings.py          FTMO params, instrument list (AGENT_VERSION = "Local")
├── analysis/
│   ├── structure.py            FVG/OB/liq detection, session gap filter, trend
│   └── sessions.py             Session/kill zone detection
├── data/
│   ├── models.py               Candle, FVGResult, OrderBlock, MarketContext
│   └── fetchers/
│       ├── yahoo_fetcher.py    Indices + oil (fallback)
│       ├── twelve_data_fetcher.py  Forex spot + XAU/USD
│       ├── okx_fetcher.py      Crypto OHLCV
│       ├── cot_fetcher.py      CFTC COT macro data
│       └── ctrader_fetcher.py  cTrader Open API (Phase 2 data + Phase 3 DOM)
└── reports/pre_session_report.py   Formatted report output
```

---

## Phase 3 — DOM Heatmap (Indices & Commodities)

When cTrader Open API credentials are configured, the Local Agent will build a real-time bid/ask liquidity heatmap using `ctrader_fetcher.subscribe_dom()`.

### What it shows
- **Colour intensity** = order volume at each price level (brighter = more liquidity)
- **Order walls** = where institutions are quoting heavy liquidity (likely to act as S/R)
- **Absorption** = large order disappears as price passes through = continuation signal
- **Rejection** = large order holds at a level = reversal signal

### Asset class suitability
| Instrument | DOM Quality | Reason |
|---|---|---|
| US500 / NAS100 / US30 | ⭐⭐⭐ High | Tracks CME E-mini futures depth in real time |
| XAUUSD (Gold) | ⭐⭐⭐ High | Tracks COMEX futures depth |
| USOIL | ⭐⭐⭐ High | Tracks NYMEX WTI futures depth |
| Forex (GBPUSD etc.) | ⭐⭐ Moderate | LP-aggregated — not CME. Still shows where banks quote heavy liquidity |
| Crypto | ⭐ Use OKX | OKX exchange-level data is superior — DOM not needed |

### To implement Phase 3
1. Get cTrader Open API credentials from Pepperstone
2. `pip install ctrader_open_api`
3. Set env vars in `.env` (CTRADER_CLIENT_ID, CLIENT_SECRET, ACCESS_TOKEN, ACCOUNT_ID)
4. Implement `subscribe_dom()` in `data/fetchers/ctrader_fetcher.py` (template is provided in the file)
5. Build heatmap renderer in `reports/dom_heatmap.py`
6. Integrate heatmap output into scan report alongside FVG levels

---

## Instruments Scanned (all FTMO Swing eligible)

| Symbol | FTMO Symbol | Leverage | Data Source | Phase 2 Source |
|---|---|---|---|---|
| BTCUSDT | BTCUSD | 1:1 | OKX | OKX (no change) |
| ETHUSDT | ETHUSD | 1:1 | OKX | OKX |
| SOLUSDT | SOLUSD | 1:1 | OKX | OKX |
| EURUSD | EURUSD | 1:30 | Twelve Data | cTrader (Pepperstone) |
| GBPUSD | GBPUSD | 1:30 | Twelve Data | cTrader |
| USDJPY | USDJPY | 1:30 | Twelve Data | cTrader |
| GBPJPY | GBPJPY | 1:30 | Twelve Data | cTrader |
| SPX | US500.cash | 1:15 | Yahoo ^GSPC | cTrader US500 (24/7) |
| NDX | US100.cash | 1:15 | Yahoo ^NDX | cTrader US100 (24/7) |
| US30 | US30.cash | 1:15 | Yahoo ^DJI | cTrader US30 (24/7) |
| DAX | GER40.cash | 1:15 | Yahoo ^GDAXI | cTrader GER40 |
| UK100 | UK100.cash | 1:15 | Yahoo ^FTSE | cTrader UK100 |
| GOLD | XAUUSD | 1:9 | Twelve Data | cTrader XAUUSD |
| OIL | USOIL.cash | 1:9 | Yahoo CL=F | cTrader USOIL |

---

## FTMO Swing Challenge Rules

| Rule | Value |
|---|---|
| Account | $200,000 |
| Risk/trade | $450 (0.225%) |
| Max daily loss | $10,000 — stop trading for the day |
| Max total loss | $20,000 — account terminated |
| Phase 1 target | $20,000 |
| Phase 2 target | $10,000 |
| Min trading days | 4 per phase |
| Time limit | None |
| News trading | Allowed |
| Overnight/weekend | Allowed |

---

## ICT/SMC Concepts Reference

### Kill Zones (Eastern Time)
- **NY Kill Zone 07:00–10:00 ET** — highest-probability day trade window
- **Silver Bullet 09:50–10:10 ET** — ICT Silver Bullet setup window
- **London KZ 02:00–05:00 ET** — London expansion, GBP/EUR setups

### Setup Checklist (use before every entry)
- [ ] Are we in a Kill Zone?
- [ ] Is price in DISCOUNT (for longs) or PREMIUM (for shorts)?
- [ ] Has London swept the Asian session high or low? (confirms manipulation complete)
- [ ] Is there a Grade A or B FVG in the direction of bias at a reasonable distance?
- [ ] Is there an Order Block near the FVG adding confluence?
- [ ] What is the nearest BSL/SSL target? Is R:R ≥ 2:1?
- [ ] Is there a high-impact news event in the next hour? (If on Normal FTMO — no. Swing — fine.)

### FVG Display Format
Always display as: `Bullish/Bearish FVG | Timeframe | gap_low → gap_high`
Example: `Bullish FVG | 1H | 1.34251 → 1.34318`

### Session Gap Filter
Yahoo Finance market-hours data creates phantom FVGs overnight. `structure._is_session_gap()` filters these. **Never remove this function.** When Phase 2 cTrader data is live, it becomes redundant (24/7 data has no gaps) but causes no harm.

---

## Known Issues & Fixes

| Issue | Fix Applied |
|---|---|
| Phantom FVGs on US indices from Yahoo overnight gap | Session gap filter in structure.py |
| USDJPY/GBPJPY null values from Yahoo | None-check on all OHLC fields in yahoo_fetcher.py |
| Price discrepancy vs Pepperstone chart | Fundamental data source difference — resolved in Phase 2 with cTrader feed |
| OKX crypto marked Tier 2 | Authenticated WebSocket needed for taker delta — Phase 3 |

---

## For AI Agents Picking This Up

1. `python main.py` to verify everything works before changes
2. **DO NOT** remove `_is_session_gap()` from `analysis/structure.py` — critical phantom FVG fix
3. Analysis code in `analysis/` must match the Remote Agent exactly — sync both when fixing bugs
4. To extend Phase 3 (DOM): implement `subscribe_dom()` in `data/fetchers/ctrader_fetcher.py`
5. The ctrader_fetcher.py contains full implementation templates in comments
6. FTMO rules in `config/settings.py` — check before modifying risk parameters
7. FVG report format: `Bullish/Bearish FVG | Timeframe | gap_low → gap_high`

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Full scan pipeline, all FTMO instruments, FTMO risk context | ✅ Complete |
| 2 | cTrader Open API data (24/7 CFD, exact prices) + trade execution | 🔜 Needs cTrader credentials |
| 3 | DOM/Level 2 heatmap for indices & commodities | 🔜 After Phase 2 |
