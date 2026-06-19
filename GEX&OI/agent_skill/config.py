"""
GEX & OI Agent Configuration
"""

import os

# --- API Keys ---
ALPHA_VANTAGE_API_KEY = os.environ.get("ALPHA_VANTAGE_API_KEY", "")

# --- Instrument Definitions ---
# Maps Pepperstone spread bet symbols to their underlying options market tickers
INSTRUMENTS = {
    "US500": {
        "pepperstone_symbol": "US500",
        "description": "S&P 500 Index",
        "options_ticker": "SPX",        # Primary: SPX index options (CBOE)
        "etf_ticker": "SPY",            # Secondary: SPY ETF options
        "spot_ticker": "SPX",
        "contract_multiplier": 100,     # SPX options control $100 per point
        "gex_available": True,
        "session": "NY",                # Primary session
    },
    "XAUUSD": {
        "pepperstone_symbol": "XAUUSD",
        "description": "Gold Spot",
        "options_ticker": "GLD",        # GLD ETF options (CBOE)
        "etf_ticker": "GLD",
        "spot_ticker": "GLD",
        "contract_multiplier": 100,     # GLD options control 100 shares
        "gld_to_gold_multiplier": 10,   # GLD price ≈ Gold/10; multiply strikes × 10 for XAUUSD levels
        "gex_available": True,
        "session": "LONDON_NY",         # Active in both
    },
    "UK100": {
        "pepperstone_symbol": "UK100",
        "description": "FTSE 100 Index",
        "options_ticker": "EWU",        # iShares MSCI UK ETF (proxy only)
        "etf_ticker": "EWU",
        "spot_ticker": None,            # No direct free spot data
        "contract_multiplier": 100,
        "gex_available": False,         # No direct free GEX data
        "proxy_approach": "cross_market_sentiment",
        "session": "LONDON",
    },
    "Ger40": {
        "pepperstone_symbol": "Ger40",
        "description": "DAX 40 Index",
        "options_ticker": "EWG",        # iShares MSCI Germany ETF (proxy only)
        "etf_ticker": "EWG",
        "spot_ticker": None,
        "contract_multiplier": 100,
        "gex_available": False,         # No direct free GEX data
        "proxy_approach": "cross_market_sentiment",
        "session": "LONDON",
    },
}

# --- Market Regime Thresholds ---
GEX_REGIME = {
    "strongly_positive": 1_000_000_000,  # $1B+ positive GEX → strong pin
    "positive": 0,                        # Any positive → moderate pin
    "negative": 0,                        # Below zero → dealers amplify moves
    "strongly_negative": -1_000_000_000, # $-1B+ → highly trending regime
}

VIX_REGIME = {
    "low": 15,       # Below 15: calm, rangebound → fade extremes
    "medium": 20,    # 15-20: normal volatility
    "elevated": 25,  # 20-25: heightened → be selective
    "high": 30,      # 25-30: high volatility → reduce size
    "extreme": 40,   # 30+: crisis → stand aside or specialist setups only
}

# --- Session Windows (UTC) ---
SESSIONS = {
    "ASIAN":       {"start": "00:00", "end": "08:00"},
    "LONDON":      {"start": "07:00", "end": "16:00"},
    "LONDON_OPEN": {"start": "07:00", "end": "10:00"},
    "NY":          {"start": "13:30", "end": "21:00"},
    "NY_OPEN":     {"start": "13:30", "end": "16:30"},
    "OVERLAP":     {"start": "13:30", "end": "16:00"},
    "GOLD_PRIME":  {"start": "13:30", "end": "19:00"},
}

# --- Alpha Vantage Call Budget ---
# Free tier: 25 calls/day, 5 calls/minute
MORNING_CALLS = [
    ("MARKET_STATUS", {}),
    ("REALTIME_OPTIONS", {"symbol": "SPX"}),
    ("REALTIME_OPTIONS", {"symbol": "GLD"}),
    ("GLOBAL_QUOTE", {"symbol": "^VIX"}),
    ("GOLD_SILVER_SPOT", {}),
    ("TREASURY_YIELD", {"maturity": "10year"}),
    ("NEWS_SENTIMENT", {"tickers": "SPY,GLD,^VIX", "limit": 10}),
]

INTRADAY_UPDATE_CALLS = [
    ("REALTIME_OPTIONS", {"symbol": "SPX"}),
    ("REALTIME_OPTIONS", {"symbol": "GLD"}),
    ("GLOBAL_QUOTE", {"symbol": "^VIX"}),
    ("NEWS_SENTIMENT", {"tickers": "SPY,GLD", "limit": 5}),
]
