# ICT/SMC Market Scanner — Local Agent (Mac / Desktop)

## What This Is

The Local Agent is the full-capability version of the ICT/SMC scanner. It scans the same 32 FTMO-eligible instruments as the Remote Agent, fetching CFD candles via its **own cTrader MCP connection to a separate FTMO account** (see "cTrader Data Connection" below). It also runs on your Mac with cTrader desktop installed, giving access to the cTrader Local MCP server — chart control, live price feeds, DOM/Level 2 data (Phase 3), and direct trade execution.

**This is the Local Agent** — for Mac desktop use with Claude Code.
**The Remote Agent** is in `/ICT-SMC-Remote-Agent/` — for phone/web use, connected to a different (Pepperstone demo) cTrader account.

Both agents share identical analysis logic. Bugs fixed in `analysis/` should be applied to both.

---

## cTrader Data Connection (FTMO account — Local Agent only)

This agent fetches 24/7 CFD candles via `data/fetchers/ctrader_fetcher.py`, which talks to a cTrader MCP HTTP endpoint — **a separate FTMO account, distinct from the Remote Agent's connection**.

### Setup
1. Get your FTMO cTrader MCP endpoint URL and bearer token (from your cTrader AI Agent Connect setup for the FTMO account).
2. Copy `.env.example` to `.env` (already gitignored).
3. Add to `.env`:
   ```
   CTRADER_MCP_URL=<your FTMO MCP endpoint URL>
   CTRADER_MCP_TOKEN=<your FTMO bearer token>
   ```

### 🔒 Security — read before touching this
- **`.env` is gitignored** (`.gitignore` includes `.env` and `**/.env`). Never `git add` it.
- **Never hardcode `CTRADER_MCP_URL` or `CTRADER_MCP_TOKEN`** anywhere in `ctrader_fetcher.py` or any other tracked file — these belong to a live FTMO account.
- **Never paste the URL or token into chat, commit messages, issues, or PRs.**
- If `CTRADER_MCP_URL` is unset, `ctrader_fetcher.py` no-ops (`_call_tool` returns `None` immediately) and every instrument falls back to its `fallback_source` (Twelve Data / Yahoo / OKX). This is the expected state for a fresh checkout.
- `CTRADER_MCP_TOKEN` is optional — leave it unset for a local cTrader desktop MCP server (e.g. `http://127.0.0.1:<port>/mcp/`) that authenticates via the desktop app session and doesn't issue a bearer token. When set, it's sent as `Authorization: Bearer <token>`.

### How it works
`_MCP_URL` and `_MCP_HOST`/`_MCP_PORT`/`_MCP_PATH`/`_MCP_SECURE` are derived from `CTRADER_MCP_URL` via `urlparse()`, so this fetcher works with any cTrader MCP HTTP endpoint (different host/port/path than the Remote Agent's). The rest of the logic (symbol resolution, pip-digit auto-detection, candle parsing) is identical to the Remote Agent's `ctrader_fetcher.py`.

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
├── config/settings.py          FTMO params, 32-instrument list (AGENT_VERSION = "Local")
├── analysis/
│   ├── structure.py            FVG/OB/liq detection, session gap filter, trend
│   └── sessions.py             Session/kill zone detection
├── data/
│   ├── models.py               Candle, FVGResult, OrderBlock, MarketContext
│   └── fetchers/
│       ├── yahoo_fetcher.py    Indices + oil (fallback)
│       ├── twelve_data_fetcher.py  Forex + metals fallback
│       ├── okx_fetcher.py      Crypto OHLCV
│       ├── cot_fetcher.py      CFTC COT macro data
│       ├── ctrader_fetcher.py  cTrader MCP — primary feed (FTMO account, env-configured)
│       └── calendar_fetcher.py ForexFactory economic calendar / news-risk
└── reports/pre_session_report.py   Formatted report output (incl. news/risk section)
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

## Instruments Scanned (32 total — all FTMO Swing eligible)

Primary source `ctrader` = this agent's own FTMO cTrader MCP connection (24/7 CFD feed, data_tier=1). Falls back automatically if `CTRADER_MCP_URL`/`CTRADER_MCP_TOKEN` are unset or the request fails.

| Symbol | Asset Class | FTMO Symbol | Leverage | Primary Source | Fallback |
|---|---|---|---|---|---|
| BTCUSDT | Crypto | BTCUSD | 1:1 | OKX | — |
| ETHUSDT | Crypto | ETHUSD | 1:1 | OKX | — |
| SOLUSDT | Crypto | SOLUSD | 1:1 | OKX | — |
| EURUSD | Forex | EURUSD | 1:30 | cTrader EURUSD | Twelve Data |
| GBPUSD | Forex | GBPUSD | 1:30 | cTrader GBPUSD | Twelve Data |
| USDJPY | Forex | USDJPY | 1:30 | cTrader USDJPY | Twelve Data |
| USDCHF | Forex | USDCHF | 1:30 | cTrader USDCHF | Twelve Data |
| USDCAD | Forex | USDCAD | 1:30 | cTrader USDCAD | Twelve Data |
| AUDUSD | Forex | AUDUSD | 1:30 | cTrader AUDUSD | Twelve Data |
| NZDUSD | Forex | NZDUSD | 1:30 | cTrader NZDUSD | Twelve Data |
| GBPJPY | Forex | GBPJPY | 1:30 | cTrader GBPJPY | Twelve Data |
| EURJPY | Forex | EURJPY | 1:30 | cTrader EURJPY | Twelve Data |
| AUDJPY | Forex | AUDJPY | 1:30 | cTrader AUDJPY | Twelve Data |
| EURGBP | Forex | EURGBP | 1:30 | cTrader EURGBP | Twelve Data |
| GBPAUD | Forex | GBPAUD | 1:30 | cTrader GBPAUD | Twelve Data |
| EURCAD | Forex | EURCAD | 1:30 | cTrader EURCAD | Twelve Data |
| GBPCAD | Forex | GBPCAD | 1:30 | cTrader GBPCAD | Twelve Data |
| SPX | Indices | US500.cash | 1:15 | cTrader US500 | Yahoo ^GSPC |
| NDX | Indices | US100.cash | 1:15 | cTrader NAS100 | Yahoo ^NDX |
| US30 | Indices | US30.cash | 1:15 | cTrader US30 | Yahoo ^DJI |
| DAX | Indices | GER40.cash | 1:15 | cTrader GER40 | Yahoo ^GDAXI |
| UK100 | Indices | UK100.cash | 1:15 | cTrader UK100 | Yahoo ^FTSE |
| FRA40 | Indices | FRA40.cash | 1:15 | cTrader FRA40 | Yahoo ^FCHI |
| EUSTX50 | Indices | EUSTX50.cash | 1:15 | cTrader EUSTX50 | Yahoo ^STOXX50E |
| JPN225 | Indices | JPN225.cash | 1:15 | cTrader JPN225 | Yahoo ^N225 |
| AUS200 | Indices | AUS200.cash | 1:15 | cTrader AUS200 | Yahoo ^AXJO |
| HK50 | Indices | HK50.cash | 1:10 | cTrader HK50 | Yahoo ^HSI |
| GOLD | Metals | XAUUSD | 1:9 | cTrader XAUUSD | Twelve Data |
| SILVER | Metals | XAGUSD | 1:9 | cTrader XAGUSD | Twelve Data |
| OIL | Commodities | USOIL.cash | 1:9 | cTrader WTOIL-PERP | Yahoo CL=F |
| BRENT | Commodities | BRENTOIL.cash | 1:9 | cTrader BRENTOIL-PERP | Yahoo BZ=F |
| NATGAS | Commodities | NatGas | 1:9 | cTrader NatGas | Yahoo NG=F |

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

## Economic Calendar / News Risk

`data/fetchers/calendar_fetcher.py` pulls the ForexFactory weekly calendar feed
(`nfs.faireconomy.media` — free, no API key) and is wired into the report:

- **Global section** — "NEWS & RISK EVENTS" near the top of the report lists
  today's HIGH-impact events across all currencies (NFP, FOMC, CPI, etc.).
- **Per-instrument** — each symbol's block shows:
  - `⚠ NEWS BLACKOUT` if a HIGH-impact event affecting that symbol is within
    30 min before / 15 min after right now (`is_news_blackout()`).
  - An "ECONOMIC CALENDAR — next 12h" mini-section of upcoming events that
    affect that symbol, via `CURRENCY_TO_SYMBOLS` (e.g. USD events affect
    EURUSD, GOLD, SPX, etc.).

`CURRENCY_TO_SYMBOLS` in `calendar_fetcher.py` uses **this agent's instrument
names** (e.g. `OIL`, `US30`, `GOLD` — not ForexFactory's `USOIL`/`DOW`/`XAUUSD`).
If new instruments are added to `config/settings.py`, add them to the relevant
currency lists in `CURRENCY_TO_SYMBOLS` too.

`fetch_events()` caches results for the lifetime of the process (one scan run),
so adding this check per-instrument doesn't multiply HTTP requests.

---

## Known Issues & Fixes

| Issue | Fix Applied |
|---|---|
| Phantom FVGs on US indices from Yahoo overnight gap | Session gap filter in structure.py |
| USDJPY/GBPJPY null values from Yahoo | None-check on all OHLC fields in yahoo_fetcher.py |
| Price discrepancy vs broker chart | Resolved by cTrader feed (data_tier=1) once `.env` is configured |
| OKX crypto marked Tier 2 | Authenticated WebSocket needed for taker delta — Phase 3 |
| OIL/BRENT cTrader demo limited history | Falls back to Yahoo — WTOIL-PERP / BRENTOIL-PERP have limited demo history |

---

## For AI Agents Picking This Up

1. `python main.py` to verify everything works before changes
2. **DO NOT** remove `_is_session_gap()` from `analysis/structure.py` — critical phantom FVG fix
3. Analysis code in `analysis/` must match the Remote Agent exactly — sync both when fixing bugs
4. **NEVER hardcode `CTRADER_MCP_URL` or `CTRADER_MCP_TOKEN`** (or any FTMO credential) in `ctrader_fetcher.py` or any tracked file. They come from a local, gitignored `.env` only — see "cTrader Data Connection" above. If `CTRADER_MCP_URL`/`CTRADER_MCP_TOKEN` are unset, `_call_tool()` returns `None` immediately and every instrument falls back to `fallback_source` — this is correct, expected behaviour, not a bug to "fix" by adding a default token.
5. To extend Phase 3 (DOM): implement `subscribe_dom()` in `data/fetchers/ctrader_fetcher.py`
6. FTMO rules in `config/settings.py` — check before modifying risk parameters
7. **FVG pick card format**: Every FVG trade plan block MUST follow this exact format. `Direction` is the first line (LONG/SHORT), followed by `Current` price with distance/direction to entry zone. Required format:
   ```
   ── TRADE PLAN ──────────────────────────────────────────
   Direction   : ▼ SHORT (SELL)
   Current     : 4462.5  (3.7pts above entry zone  (price must drop ↓ to fill))
   Entry zone  : 4456.2 → 4458.8  (enter anywhere in FVG)
   SL          : 4452.5  (5pt stop from entry midpoint)
   TP1 (partial 50%) : 4458.7  [R/R 1.0:1]
   TP2 ★ PRIMARY     : 4445.0  SSL (2× tested)  [R/R 2.1:1]
   TP3 (PDH/L) : 4420.0  prior day low (SSL)  [R/R 5.5:1]
   Size        : $450 risk = 9.00 lots @ 5pt stop
   Confluences : 7/9  [███████░░]
   ```
   This is implemented in `_format_setup_block()`. Do not remove `Direction` or `Current` lines.
   Direction text: `▲ LONG  (BUY)` for bullish FVGs, `▼ SHORT (SELL)` for bearish.
   Current price distance: "below entry zone (price must rally ↑ to fill)" when price is below zone; "above entry zone (price must drop ↓ to fill)" when price is above zone.
8. FVG header format: `Bullish/Bearish FVG | Timeframe | gap_low → gap_high`

## Phase Roadmap

| Phase | Description | Status |
|---|---|---|
| 1 | Full scan pipeline, all FTMO instruments, FTMO risk context | ✅ Complete |
| 1.5 | 32-instrument cTrader-primary config + economic calendar/news-risk section | ✅ Complete |
| 2 | cTrader MCP data (24/7 CFD, exact FTMO prices) — needs `.env` with `CTRADER_MCP_URL`/`CTRADER_MCP_TOKEN` | 🔜 Needs FTMO MCP credentials |
| 2.5 | Trade execution via cTrader MCP (FTMO account) | 🔜 After Phase 2 |
| 3 | DOM/Level 2 heatmap for indices & commodities | 🔜 After Phase 2 |
