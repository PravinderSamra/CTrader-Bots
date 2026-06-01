"""
Configuration — ICT/SMC Remote Agent

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
    "EURUSD":  10.0,   # $10 per pip per lot
    "GBPUSD":  10.0,
    "USDJPY":   8.0,   # approx — varies with JPY rate
    "GBPJPY":   8.0,
    "SPX":     25.0,   # $25 per index point per contract
    "NDX":     20.0,
    "DAX":     25.0,
    "US30":    25.0,
    "UK100":   12.0,
    "GOLD":    10.0,   # $10 per $1 move per lot (100 oz)
    "OIL":     10.0,
}

# ── Instrument Definitions ────────────────────────────────────────────────────
# Each entry: (display_name, asset_class, primary_source, primary_symbol, fallback_source, fallback_symbol, cot_key)

INSTRUMENTS = [
    # Crypto — OKX (no FTMO leverage, 1:1)
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

    # Forex — cTrader Remote MCP (exact Pepperstone prices, 24/7)
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

    # Indices — cTrader Remote MCP (24/7 CFD data — no overnight gaps)
    {
        "name": "SPX",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "US500",
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
        "symbol": "NAS100",
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
        "symbol": "US30",
        "fallback_source": "yahoo",
        "fallback_symbol": "^DJI",
        "cot_key": "US30",
        "ftmo_leverage": 15,
        "ftmo_symbol": "US30.cash",
    },
    {
        "name": "DAX",
        "asset_class": "indices",
        "source": "ctrader",
        "symbol": "GER40",
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
        "symbol": "UK100",
        "fallback_source": "yahoo",
        "fallback_symbol": "^FTSE",
        "cot_key": None,
        "ftmo_leverage": 15,
        "ftmo_symbol": "UK100.cash",
    },

    # Commodities — cTrader Remote MCP
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
        "name": "OIL",
        "asset_class": "commodities",
        "source": "ctrader",
        "symbol": "WTOIL-PERP",
        "fallback_source": "yahoo",
        "fallback_symbol": "CL=F",
        "cot_key": "OIL",
        "ftmo_leverage": 9,
        "ftmo_symbol": "USOIL.cash",
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
AGENT_VERSION = "Remote"
SKIP_GRADES   = {"SKIP"}              # FVG grades to filter from report
MIN_FVG_GRADE = "C"                   # Minimum grade to show (C, B, A, A+)
MAX_FVG_DISPLAY = 5                   # Max FVGs shown per symbol
MAX_OB_DISPLAY  = 5                   # Max order blocks shown per symbol
MAX_LIQ_DISPLAY = 5                   # Max liquidity pools per symbol
