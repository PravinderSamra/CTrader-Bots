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

## Instruments Scanned (all FTMO Swing eligible)

| Symbol | Asset Class | FTMO Symbol | Leverage | Data Source |
|---|---|---|---|---|
| BTCUSDT | Crypto | BTCUSD | 1:1 | OKX |
| ETHUSDT | Crypto | ETHUSD | 1:1 | OKX |
| SOLUSDT | Crypto | SOLUSD | 1:1 | OKX |
| EURUSD | Forex | EURUSD | 1:30 | Twelve Data |
| GBPUSD | Forex | GBPUSD | 1:30 | Twelve Data |
| USDJPY | Forex | USDJPY | 1:30 | Twelve Data → Yahoo |
| GBPJPY | Forex | GBPJPY | 1:30 | Twelve Data → Yahoo |
| SPX | Index | US500.cash | 1:15 | Yahoo ^GSPC |
| NDX | Index | US100.cash | 1:15 | Yahoo ^NDX |
| US30 | Index | US30.cash | 1:15 | Yahoo ^DJI |
| DAX | Index | GER40.cash | 1:15 | Yahoo ^GDAXI |
| UK100 | Index | UK100.cash | 1:15 | Yahoo ^FTSE |
| GOLD | Metals | XAUUSD | 1:9 | Twelve Data XAU/USD |
| OIL | Commodities | USOIL.cash | 1:9 | Yahoo CL=F |

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
| cTrader fetcher not implemented | Planned Phase 2 | ctrader_fetcher.py is a documented placeholder |
| Crypto OKX data marked Tier 2 | Known | OKX public endpoint doesn't include taker delta — need authenticated WebSocket |
| COT data for DAX/UK100 unavailable | By design | CFTC only covers US markets |

---

## Phase Roadmap

| Phase | What's Built | Status |
|---|---|---|
| Phase 1 | Data pipeline, FVG/OB/liq detection, FTMO risk context, all instruments | ✅ Complete |
| Phase 2 | cTrader Remote MCP data source (24/7 CFD data, exact broker prices) + trade execution | 🔜 Pending cTrader credentials |
| Phase 3 | cTrader DOM/Level 2 heatmap (Local Agent only — indices & commodities) | 🔜 After Phase 2 |

---

## For AI Agents Picking This Up

If you are an AI agent reading this to reinstall or extend this system:

1. **Run `python main.py`** to verify the system works before making changes
2. **The most sensitive file is `analysis/structure.py`** — especially `_is_session_gap()` which prevents phantom FVGs
3. **Never remove the session gap filter** — it exists because Yahoo Finance returns market-hours-only data for US indices
4. **FVG format**: Always show as `Bullish/Bearish FVG | Timeframe | gap_low → gap_high`
5. **FTMO rules are in `config/settings.py`** — check there before modifying risk parameters
6. **To add a new instrument**: Add an entry to the `INSTRUMENTS` list in `config/settings.py` — no other files need changing
7. **Twelve Data free tier**: ~800 credits/day, 8 credits/request, ~100 requests/day limit. Don't add many new instruments without upgrading the plan
8. **The Local Agent** (`/ICT-SMC-Local-Agent/`) has identical analysis logic — keep both in sync when fixing bugs in `analysis/` or `data/models.py`
