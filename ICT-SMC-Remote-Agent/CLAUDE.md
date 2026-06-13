# ICT/SMC Market Scanner — Remote Agent

## What This Is

An AI-powered market scanner for day trading using ICT/Smart Money Concepts (SMC) methodology. It scans 13 instruments across forex, indices, commodities, and crypto — all FTMO Swing Challenge eligible — and produces a pre-session report identifying actionable setups: Fair Value Gaps (FVGs), Order Blocks (OBs), and liquidity levels.

**This is the Remote Agent** — runs via `python main.py` from any machine. Uses Yahoo Finance, Twelve Data, and OKX as data sources. Designed to work on mobile (via Claude app with Remote MCP) and as a standalone script.

**The Local Agent** is in `/ICT-SMC-Local-Agent/` — adds cTrader Local MCP capabilities (chart control, DOM data, Phase 3 heatmap).

---

## Quick Start (New Machine / Reinstall)

```bash
cd ICT-SMC-Remote-Agent
pip install -r requirements.txt
cp .env.example .env
# Edit .env — add TWELVE_DATA_API_KEY at minimum
python main.py
```

The scan takes ~30–60 seconds and prints the full report to stdout.

---

## Environment Variables

Set in `.env` (copy from `.env.example`):

| Variable | Required | Where to get |
|---|---|---|
| `TWELVE_DATA_API_KEY` | Yes (for forex/gold) | Free at twelvedata.com |
| `CTRADER_CLIENT_ID` | Phase 2 only | From Pepperstone / cTrader Open API portal |
| `CTRADER_CLIENT_SECRET` | Phase 2 only | Same |
| `CTRADER_ACCESS_TOKEN` | Phase 2 only | OAuth2 from cTrader |
| `CTRADER_ACCOUNT_ID` | Phase 2 only | Your FTMO cTrader account ID |

---

## Architecture

```
ICT-SMC-Remote-Agent/
├── main.py                     Entry point — run this
├── config/settings.py          FTMO params, instrument list
├── analysis/
│   ├── structure.py            FVG detection, OB detection, premium/discount, trend
│   └── sessions.py             Session/kill zone detection (ICT methodology)
├── data/
│   ├── models.py               Candle, FVGResult, OrderBlock, MarketContext dataclasses
│   └── fetchers/
│       ├── yahoo_fetcher.py    Indices + oil (market-hours data, session gap filter applied)
│       ├── twelve_data_fetcher.py  Forex spot + XAU/USD
│       ├── okx_fetcher.py      Crypto OHLCV (public API, no auth needed)
│       ├── cot_fetcher.py      CFTC COT data (weekly macro positioning)
│       └── ctrader_fetcher.py  PLACEHOLDER: cTrader Open API (Phase 2)
└── reports/pre_session_report.py   Formatted report output
```

---

## Instruments Scanned (32 total — all FTMO Swing eligible)

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

## FTMO Swing Challenge Rules (built into report)

| Rule | Value |
|---|---|
| Account size | $200,000 |
| Risk per trade | $450 (0.225%) |
| Max daily loss | $10,000 (5%) — HARD STOP if hit, no more trades today |
| Max total loss | $20,000 (10%) — account terminated |
| Phase 1 target | $20,000 (10%) |
| Phase 2 target | $10,000 (5%) |
| Min trading days | 4 per phase |
| Time limit | None |
| News trading | Allowed (Swing account) |
| Overnight/weekend | Allowed (Swing account) |

---

## ICT/SMC Methodology Used

### Sessions & Kill Zones (all times Eastern / New York)
- **Asia KZ**: 20:00–00:00 ET (manipulation phase)
- **London KZ**: 02:00–05:00 ET (primary London expansion)
- **NY Kill Zone**: 07:00–10:00 ET — **highest probability window for day trades**
- **Silver Bullet**: 09:50–10:10 ET and 13:50–14:10 ET (ICT Silver Bullet setups)

### Setup Logic
1. **Session bias**: Price vs midnight open → discount (buy) or premium (sell)
2. **Manipulation check**: Did London sweep the Asian high or low? Swept = reversal expected
3. **FVG entry**: Find unmitigated Fair Value Gap in the bias direction at a key structural level
4. **Order Block confirmation**: OB near the FVG adds confluence
5. **Liquidity target**: PDH (BSL) or PDL (SSL) as the take-profit target
6. **Kill zone timing**: Only enter during active kill zones

### FVG Quality Grades
- **A+** (score ≥ 11): Virgin, liq-grab + post-BOS context, fresh, large gap
- **A** (score ≥ 8): Fresh or recent, good context, untouched or minimal fill
- **B** (score ≥ 5): Moderate quality — valid but watch for confirmation
- **C** (score ≥ 2): Lower quality — use only with strong supporting confluence
- **SKIP** (score < 2): Filtered from report — too weak to trade

### Session Gap Filter (critical bug fix)
Yahoo Finance returns market-hours-only candles for US indices. The overnight gap (e.g. Friday close to Monday open) looks like a price gap but doesn't exist on CFD charts (US500 trades 24/7 on Pepperstone). `structure._is_session_gap()` filters these phantom FVGs by checking if the timestamp gap between consecutive candles is >2.5× the expected interval.

---

## Position Sizing Guide ($200k account, $450 risk)

**Formula**: `Lot size = $450 / (stop_points × pip_value_per_lot)`

| Instrument | Stop (pts) | Suggested Lots | Notes |
|---|---|---|---|
| GBPUSD | 20 pips | 2.25 lots | $10/pip/lot |
| GBPUSD | 30 pips | 1.50 lots | |
| EURUSD | 20 pips | 2.25 lots | |
| USDJPY | 20 pips | ~2.0 lots | Pip value varies |
| US500 | 10 pts | 1.80 contracts | $25/pt/contract |
| US500 | 15 pts | 1.20 contracts | |
| XAUUSD | 5 pts | ~9 lots | $1/pt × 100oz |
| BTC | varies | $450 / price_move | 1:1 leverage — size in USD |

---

## Known Issues

| Issue | Status | Fix |
|---|---|---|
| Yahoo returns null candle values for some JPY pairs | Mitigated | All OHLC None-checks in yahoo_fetcher.py; falls back to Twelve Data |
| US index data is market-hours only (phantom FVGs) | Fixed | Session gap filter in structure.py |
| OIL/BRENT cTrader demo limited | Known | Falls back to Yahoo — WTOIL-PERP and BRENTOIL-PERP have limited demo history |
| Crypto OKX data marked Tier 2 | Known | OKX public endpoint doesn't include taker delta — need authenticated WebSocket |
| COT data for DAX/UK100 unavailable | By design | CFTC only covers US markets |

---

## Trade Log System

Every setup the agent presents, and every trade the user takes, is recorded in
`trade_log/trades.json` (full schema + helper functions in `trade_log/log_trade.py`).

**Logging must never block or slow down the user-facing response.** Workflow:

1. **After posting scan recommendations in chat** — spawn a background Agent
   (`run_in_background: true`, `subagent_type: general-purpose`) that:
   - Calls `add_trade()` for each setup presented this scan (one record per
     setup, `recommendation_status` = `recommended` | `watch_only` |
     `not_recommended`), using the exact entry/SL/TP/confluence numbers from
     the trade card just shown to the user.
   - Calls `get_pending_trades()` to find prior records still
     `pending`/`filled_open`, fetches price history since each record's
     `scan_timestamp_utc` via `ctrader_fetcher.fetch_klines()` (see "Always
     use HTTP" section below), determines whether the entry zone was reached
     and whether SL/TP was hit, then calls `update_trade()` with the
     resulting `outcome_status`, `pnl_usd`, and `outcome_notes`.

2. **After confirming a trade entry in chat** (user says "enter trade X") —
   place the order and confirm in chat first as normal, THEN spawn a
   background Agent that calls `update_trade(trade_id, {...})` to set
   `action_status: "taken"` plus `order_id` / `position_id` / `order_volume` /
   `order_type`. If the trade wasn't previously logged as a recommendation
   (ad-hoc entry), create a new record via `add_trade()` instead.

3. `pnl_usd` is computed with the same `$450 risk / stop_pts` sizing model
   used in trade cards — scale by how far price moved from `entry_price`
   toward `stop_loss` or the relevant TP (pro-rate for TP1 partials).

`trades.json` lives in this repo so it can also be reviewed/queried directly
(`cat trade_log/trades.json` or `get_all_trades()`).

---

## Phase Roadmap

| Phase | What's Built | Status |
|---|---|---|
| Phase 1 | Data pipeline, FVG/OB/liq detection, FTMO risk context, all instruments | ✅ Complete |
| Phase 2 | cTrader Remote MCP data source (24/7 CFD prices), expanded to 32 instruments | ✅ Complete |
| Phase 3 | cTrader DOM/Level 2 heatmap (Local Agent only — indices & commodities) | 🔜 After live account token |

---

## For AI Agents Picking This Up

If you are an AI agent reading this to reinstall or extend this system:

### ⚠ CRITICAL — Always use HTTP, never wait for cTrader MCP tools

**Do NOT wait for `mcp__ctrader__*` tools to reconnect.** Always use the HTTP method directly:

```python
import sys
sys.path.insert(0, '/home/user/CTrader-Bots/ICT-SMC-Remote-Agent')
from data.fetchers.ctrader_fetcher import _call_tool, _ensure_session, _get_symbol_id, fetch_current_price, fetch_klines

_ensure_session()  # establish persistent HTTPS connection

# Get symbol ID
sym_id = _get_symbol_id("NZDUSD")

# Current price
price = fetch_current_price("NZDUSD")

# Candles
candles = fetch_klines("XAUUSD", "1h", limit=100)

# Place order (SELL LIMIT example)
result = _call_tool("create_order", {
    "symbolId":        sym_id,
    "orderType":       "LIMIT",        # MARKET | LIMIT | STOP | STOP_LIMIT
    "tradeSide":       "SELL",         # BUY | SELL
    "volume":          30000000,       # lots × lotSize × 100 (forex lotSize=100000)
    "limitPrice":      0.59143,        # display price (not pipettes)
    "stopLossPrice":   0.59323,        # display price
    "takeProfitPrice": 0.59024,        # display price
    "label":           "SYMBOL-SIDE-SETUP",
    "comment":         "ICT FVG entry | confluence score | SL TP details",
})
```

**Token**: Demo token is hardcoded in `ctrader_fetcher.py` line 28. When user is ready for live/FTMO trading, set `CTRADER_MCP_TOKEN` in `.env` — the fetcher will use it automatically.

**Volume formula**: `lots × lotSize × 100`
- Forex (EURUSD, NZDUSD etc): lotSize = 100,000 → 1 lot = 10,000,000
- Metals (XAUUSD): lotSize = 100 → 1 lot = 10,000
- Indices (US500): lotSize = 1 → 1 lot = 100

**Order prices** are in **display price format** (not pipettes).

---

1. **Run `python main.py`** to verify the system works before making changes
2. **The most sensitive file is `analysis/structure.py`** — especially `_is_session_gap()` which prevents phantom FVGs
3. **Never remove the session gap filter** — it exists because Yahoo Finance returns market-hours-only data for US indices
4. **FVG pick card format**: Every FVG trade plan block MUST follow this exact format. `Direction` is the first line (LONG/SHORT), followed by `Current` price with distance/direction to entry zone. Required format:
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
5. **FVG display format**: Always show header as `Bullish/Bearish FVG | Timeframe | gap_low → gap_high`
5. **FTMO rules are in `config/settings.py`** — check there before modifying risk parameters
6. **To add a new instrument**: Add an entry to the `INSTRUMENTS` list in `config/settings.py` — no other files need changing
7. **Twelve Data free tier**: ~800 credits/day, 8 credits/request, ~100 requests/day limit. Don't add many new instruments without upgrading the plan
8. **The Local Agent** (`/ICT-SMC-Local-Agent/`) has identical analysis logic — keep both in sync when fixing bugs in `analysis/` or `data/models.py`
