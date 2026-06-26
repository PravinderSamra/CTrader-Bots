"""
Configuration — ICT/SMC Local Agent

FTMO Swing Challenge parameters and instrument definitions.
Update FTMO_ACCOUNT_SIZE and FTMO_RISK_PER_TRADE if your challenge details change.
"""

# ── FTMO Challenge Configuration ──────────────────────────────────────────────

FTMO_ACCOUNT_SIZE   = 200_000   # USD — your funded account size
FTMO_RISK_PER_TRADE = 450       # USD — fixed risk per setup

FTMO_DAILY_LOSS_LIMIT   = FTMO_ACCOUNT_SIZE * 0.05   # $10,000 — HARD STOP if hit
FTMO_TOTAL_LOSS_LIMIT   = FTMO_ACCOUNT_SIZE * 0.10   # $20,000 — account terminated
FTMO_PROFIT_TARGET_P1   = FTMO_ACCOUNT_SIZE * 0.10   # $20,000 — Phase 1 target
FTMO_PROFIT_TARGET_P2   = FTMO_ACCOUNT_SIZE * 0.05   # $10,000 — Phase 2 target
FTMO_MIN_TRADING_DAYS   = 4     # Per phase (not consecutive)

# FTMO Swing leverage by asset class
FTMO_LEVERAGE = {
    "forex":        30,
    "indices":      15,
    "metals":        9,
    "commodities":   9,
    "crypto":        1,   # 1:1 — no leverage
    "stocks":        1,
}

# Position size guidance (USD pip value at 1 standard lot)
# Use: lot_size = FTMO_RISK_PER_TRADE / (stop_pips × pip_value)
PIP_VALUE_PER_LOT = {
    # Forex — USD-quoted (exact: $10/pip/lot)
    "EURUSD":  10.0,
    "GBPUSD":  10.0,
    "AUDUSD":  10.0,
    "NZDUSD":  10.0,
    # Forex — USD-base (pip value = 10 / rate, approx)
    "USDJPY":   8.0,   # approx — varies with JPY rate
    "USDCHF":  11.0,   # approx — varies with CHF rate (~0.90)
    "USDCAD":   7.5,   # approx — varies with CAD rate (~1.36)
    # JPY-quoted crosses (pip value ≈ lot_size × 0.0001 × 1/USDJPY × base_rate)
    "GBPJPY":   8.0,   # approx
    "EURJPY":   8.0,   # approx
    "AUDJPY":   7.0,   # approx
    # Non-USD-quoted crosses
    "EURGBP":  13.0,   # approx — GBP-quoted × GBPUSD
    "GBPAUD":  10.0,   # approx
    "EURCAD":   7.5,   # approx — CAD-quoted
    # Indices ($per index point per contract)
    "SPX":     25.0,   # $25 per index point per contract
    "NDX":     20.0,
    "DAX":     25.0,
    "US30":    25.0,
    "UK100":   12.0,
    "FRA40":   10.0,   # approx — EUR-denominated, varies with EURUSD
    "EUSTX50": 10.0,   # approx
    "JPN225":   9.0,   # approx — JPY-denominated, varies with USDJPY
    "AUS200":   7.0,   # approx — AUD-denominated
    "HK50":     1.25,  # approx — HKD-denominated
    # Metals
    "GOLD":    10.0,   # $10 per $1 move per lot (100 oz)
    "SILVER":   5.0,   # approx — $5 per $0.01 move per lot
    # Commodities
    "OIL":     10.0,
    "BRENT":   10.0,
    "NATGAS":   5.0,   # approx
}

# ── Instrument Definitions ────────────────────────────────────────────────────
# All 32 instruments are FTMO Swing Challenge eligible.
# source/symbol = cTrader MCP symbol name (direct broker feed, 24/7).
# This agent connects to its own FTMO cTrader account via CTRADER_MCP_URL /
# CTRADER_MCP_TOKEN (set in a local, gitignored .env — see ctrader_fetcher.py).
# fallback_source/fallback_symbol = used if cTrader is unconfigured or fails.

INSTRUMENTS = [

    # ── Crypto (3) — OKX for best 24/7 data; cTrader demo has limited crypto history
    {
        "name": "BTCUSDT",
        "asset_class": "crypto",
        "source": "okx",
        "symbol": "BTC-USDT",
        "cot_key": None,
        "ftmo_leverage": 1,
        "ftmo_symbol": "BTCUSD",
        "note": "FTMO: 1:1 leverage — size positions accordingly",
    },
    {
        "name": "ETHUSDT",
        "asset_class": "crypto",
        "source": "okx",
        "symbol": "ETH-USDT",
        "cot_key": None,
        "ftmo_leverage": 1,
        "ftmo_symbol": "ETHUSD",
        "note": "FTMO: 1:1 leverage — size positions accordingly",
    },
    {
        "name": "SOLUSDT",
        "asset_class": "crypto",
        "source": "okx",
        "symbol": "SOL-USDT",
        "cot_key": None,
        "ftmo_leverage": 1,
        "ftmo_symbol": "SOLUSD",
        "note": "FTMO: 1:1 leverage — size positions accordingly",
    },

    # ── Forex Majors (7 G8 pairs) ─────────────────────────────────────────────
    {
        "name": "EURUSD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "EURUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "EUR/USD",
        "cot_key": "EURUSD",
        "ftmo_leverage": 30,
        "ftmo_symbol": "EURUSD",
    },
    {
        "name": "GBPUSD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "GBPUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "GBP/USD",
        "cot_key": "GBPUSD",
        "ftmo_leverage": 30,
        "ftmo_symbol": "GBPUSD",
    },
    {
        "name": "USDJPY",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "USDJPY",
        "fallback_source": "twelve_data",
        "fallback_symbol": "USD/JPY",
        "cot_key": "USDJPY",
        "ftmo_leverage": 30,
        "ftmo_symbol": "USDJPY",
    },
    {
        "name": "USDCHF",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "USDCHF",
        "fallback_source": "twelve_data",
        "fallback_symbol": "USD/CHF",
        "cot_key": "USDCHF",
        "ftmo_leverage": 30,
        "ftmo_symbol": "USDCHF",
    },
    {
        "name": "USDCAD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "USDCAD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "USD/CAD",
        "cot_key": "USDCAD",
        "ftmo_leverage": 30,
        "ftmo_symbol": "USDCAD",
    },
    {
        "name": "AUDUSD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "AUDUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "AUD/USD",
        "cot_key": "AUDUSD",
        "ftmo_leverage": 30,
        "ftmo_symbol": "AUDUSD",
    },
    {
        "name": "NZDUSD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "NZDUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "NZD/USD",
        "cot_key": "NZDUSD",
        "ftmo_leverage": 30,
        "ftmo_symbol": "NZDUSD",
    },

    # ── Forex Key Crosses (7 pairs) ───────────────────────────────────────────
    {
        "name": "GBPJPY",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "GBPJPY",
        "fallback_source": "twelve_data",
        "fallback_symbol": "GBP/JPY",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "GBPJPY",
    },
    {
        "name": "EURJPY",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "EURJPY",
        "fallback_source": "twelve_data",
        "fallback_symbol": "EUR/JPY",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "EURJPY",
    },
    {
        "name": "AUDJPY",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "AUDJPY",
        "fallback_source": "twelve_data",
        "fallback_symbol": "AUD/JPY",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "AUDJPY",
    },
    {
        "name": "EURGBP",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "EURGBP",
        "fallback_source": "twelve_data",
        "fallback_symbol": "EUR/GBP",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "EURGBP",
    },
    {
        "name": "GBPAUD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "GBPAUD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "GBP/AUD",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "GBPAUD",
    },
    {
        "name": "EURCAD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "EURCAD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "EUR/CAD",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "EURCAD",
    },
    {
        "name": "GBPCAD",
        "asset_class": "forex",
        "source": "ctrader",
        "symbol": "GBPCAD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "GBP/CAD",
        "cot_key": None,
        "ftmo_leverage": 30,
        "ftmo_symbol": "GBPCAD",
    },

    # ── US Indices (3) ────────────────────────────────────────────────────────
    {
        "name": "SPX",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "US500.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^GSPC",
        "cot_key": "SPX",
        "ftmo_leverage": 15,
        "ftmo_symbol": "US500.cash",
    },
    {
        "name": "NDX",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "US100.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^NDX",
        "cot_key": "NDX",
        "ftmo_leverage": 15,
        "ftmo_symbol": "US100.cash",
    },
    {
        "name": "US30",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "US30.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^DJI",
        "cot_key": "US30",
        "ftmo_leverage": 15,
        "ftmo_symbol": "US30.cash",
    },

    # ── European Indices (4) ──────────────────────────────────────────────────
    {
        "name": "DAX",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "GER40.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^GDAXI",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "GER40.cash",
    },
    {
        "name": "UK100",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "UK100.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^FTSE",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "UK100.cash",
    },
    {
        "name": "FRA40",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "FRA40.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^FCHI",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "FRA40.cash",
    },
    {
        "name": "EUSTX50",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "EU50.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^STOXX50E",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "EU50.cash",
    },

    # ── Asia-Pacific Indices (3) ──────────────────────────────────────────────
    {
        "name": "JPN225",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "JP225.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^N225",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "JP225.cash",
    },
    {
        "name": "AUS200",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "AUS200.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^AXJO",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "AUS200.cash",
    },
    {
        "name": "HK50",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "HK50.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "^HSI",
        "cot_key": None,
        "ftmo_leverage": 10,
        "ftmo_symbol": "HK50.cash",
    },

    # ── Metals (2) ────────────────────────────────────────────────────────────
    {
        "name": "GOLD",
        "asset_class": "metals",
        "source": "ctrader",
        "symbol": "XAUUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "XAU/USD",
        "cot_key": "GOLD",
        "ftmo_leverage": 9,
        "ftmo_symbol": "XAUUSD",
    },
    {
        "name": "SILVER",
        "asset_class": "metals",
        "source": "ctrader",
        "symbol": "XAGUSD",
        "fallback_source": "twelve_data",
        "fallback_symbol": "XAG/USD",
        "cot_key": "SILVER",
        "ftmo_leverage": 9,
        "ftmo_symbol": "XAGUSD",
    },

    # ── Commodities (3) ───────────────────────────────────────────────────────
    {
        "name": "OIL",
        "asset_class": "commodities",
        "source": "ctrader",
        "symbol": "USOIL.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "CL=F",
        "cot_key": "OIL",
        "ftmo_leverage": 9,
        "ftmo_symbol": "USOIL.cash",
    },
    {
        "name": "BRENT",
        "asset_class": "commodities",
        "source": "ctrader",
        "symbol": "UKOIL.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "BZ=F",
        "cot_key": None,
        "ftmo_leverage": 9,
        "ftmo_symbol": "UKOIL.cash",
    },
    {
        "name": "NATGAS",
        "asset_class": "commodities",
        "source": "ctrader",
        "symbol": "NATGAS.cash",
        "fallback_source": "yahoo",
        "fallback_symbol": "NG=F",
        "cot_key": None,
        "ftmo_leverage": 9,
        "ftmo_symbol": "NATGAS.cash",
    },
]

# ── Scan Timeframes ───────────────────────────────────────────────────────────
# Primary scan timeframe — 1H for ICT day trading setups
PRIMARY_TF  = "1h"
CONTEXT_TF  = "4h"    # Higher timeframe for trend/structure context
DAILY_TF    = "1d"    # Daily for PDH/PDL and HTF bias

CANDLE_LIMIT_PRIMARY  = 200   # 1H candles (~8 days)
CANDLE_LIMIT_CONTEXT  = 96    # 4H candles (~16 days)
CANDLE_LIMIT_DAILY    = 30    # Daily candles (~1 month)

# ── Report Settings ───────────────────────────────────────────────────────────
AGENT_VERSION = "Local"
SKIP_GRADES   = {"SKIP"}              # FVG grades to filter from report
MIN_FVG_GRADE = "C"                   # Minimum grade to show (C, B, A, A+)
MAX_FVG_DISPLAY = 5                   # Max FVGs shown per symbol
MAX_OB_DISPLAY  = 5                   # Max order blocks shown per symbol
MAX_LIQ_DISPLAY = 5                   # Max liquidity pools per symbol

# ── Scalp Quality Filters ──────────────────────────────────────────────────────
MIN_RR_SCALP          = 1.5    # Minimum R:R — if TP2 fails, escalate to TP3; if both fail, flag NO VIABLE TP
STANDBY_DISTANCE_PCT  = 0.80   # % from entry edge — suppress from scalp report if price is further than this
MAX_TOUCH_COUNT_SCALP = 3      # FVGs tested more than this are excluded (orders likely absorbed)
