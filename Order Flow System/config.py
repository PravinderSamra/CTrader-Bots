"""
Order Flow Analysis System — Configuration
"""

from dataclasses import dataclass, field
from typing import Dict, List


# ─── DATA TIER LABELS ────────────────────────────────────────────────────────
# These are shown on every output so the trader knows exactly what data
# quality underlies each signal and what needs manual confirmation.

DATA_TIER_LABELS = {
    1: "TRUE ORDER FLOW — Real taker buy/sell volume from exchange. Delta and CVD are genuine.",
    2: "STRUCTURAL ANALYSIS ONLY — OHLCV-derived. No real-time bid/ask aggression data. "
       "Confirm order flow signals manually on Bookmap/Sierra Chart/ATAS before entering.",
    3: "CONFLUENCE FACTOR — Supporting context only. Not sufficient for entry decisions alone.",
}

# ─── API KEYS ────────────────────────────────────────────────────────────────
# Twelve Data: free tier at https://twelvedata.com/register (800 req/day, no card)
# Provides 5m/15m intraday data for forex, indices, gold — better than Yahoo for intraday.
TWELVE_DATA_API_KEY = ""   # ← paste your key here after signing up

# ─── ACCOUNT SETTINGS ────────────────────────────────────────────────────────

ACCOUNT_SIZE_USD = 10_000
RISK_PER_TRADE_PCT = 1.0        # 1% per trade (standard)
RISK_A_PLUS_PCT   = 1.5         # Scale up slightly for A+ setups
MAX_DAILY_LOSS_PCT = 3.0        # Stop trading for the day if hit


# ─── MARKET WATCHLIST ────────────────────────────────────────────────────────
# data_tier: 1 = true order flow available, 2 = structural only

WATCHLIST = {
    "crypto": {
        "BTCUSDT":  {"exchange": "binance", "data_tier": 1, "point_value": 1},
        "ETHUSDT":  {"exchange": "binance", "data_tier": 1, "point_value": 1},
        "SOLUSDT":  {"exchange": "binance", "data_tier": 1, "point_value": 1},
    },
    "forex": {
        # Alpha Vantage OHLCV — structural analysis only
        "EURUSD":   {"source": "alpha_vantage", "data_tier": 2, "pip_value": 10},
        "GBPUSD":   {"source": "alpha_vantage", "data_tier": 2, "pip_value": 10},
        "USDJPY":   {"source": "alpha_vantage", "data_tier": 2, "pip_value": 10},
        "GBPJPY":   {"source": "alpha_vantage", "data_tier": 2, "pip_value": 10},
    },
    "indices": {
        # Yahoo Finance — structural analysis only
        "SPX":      {"source": "yahoo", "ticker": "^GSPC",  "data_tier": 2, "point_value": 50},
        "NDX":      {"source": "yahoo", "ticker": "^NDX",   "data_tier": 2, "point_value": 20},
        "DAX":      {"source": "yahoo", "ticker": "^GDAXI", "data_tier": 2, "point_value": 25},
    },
    "commodities": {
        # Yahoo Finance — structural analysis only
        "GOLD":     {"source": "yahoo", "ticker": "GC=F",   "data_tier": 2, "point_value": 100},
        "OIL":      {"source": "yahoo", "ticker": "CL=F",   "data_tier": 2, "point_value": 1000},
    },
}

# ─── SESSION TIMES (EST) ─────────────────────────────────────────────────────

SESSIONS = {
    "asia":   {"start": "20:00", "end": "00:00"},    # Prior day EST
    "london": {"start": "02:00", "end": "11:00"},
    "ny":     {"start": "07:00", "end": "16:00"},
    "london_ny_overlap": {"start": "08:00", "end": "11:00"},
}

KILL_ZONES = {
    "london":        {"start": "02:00", "end": "05:00"},
    "ny":            {"start": "07:00", "end": "10:00"},
    "silver_bullet_1": {"start": "03:00", "end": "04:00"},
    "silver_bullet_2": {"start": "10:00", "end": "11:00"},
    "silver_bullet_3": {"start": "14:00", "end": "15:00"},
}

# ─── ANALYSIS PARAMETERS ─────────────────────────────────────────────────────

# Timeframes to fetch and analyse (for each market)
TIMEFRAMES = {
    "context":  ["1d", "4h"],    # Higher-TF bias
    "setup":    ["1h", "15m"],   # Setup identification
    "entry":    ["5m", "1m"],    # Entry confirmation
}

# Minimum impulse body size relative to ATR to qualify as displacement
DISPLACEMENT_ATR_MULTIPLIER = 1.5

# FVG minimum size as percentage of ATR to filter out noise
FVG_MIN_ATR_PCT = 0.3

# Volume profile bins (number of price levels to distribute volume across)
VOLUME_PROFILE_BINS = 100

# Swing detection: number of candles on each side for a swing to be significant
SWING_LOOKBACK = 5

# Delta imbalance threshold for Tier 1 confirmation (e.g. 0.6 = 60% taker buys)
DELTA_CONFIRMATION_THRESHOLD = 0.58

# Equal highs/lows tolerance (% of price) for liquidity pool identification
EQUAL_LEVEL_TOLERANCE_PCT = 0.001   # 0.1%

# ─── SCORING THRESHOLDS ──────────────────────────────────────────────────────

SCORE_THRESHOLDS = {
    "A+": 10,
    "B+": 7,
    "B":  5,
    "C":  3,
    # Below 3 = SKIP
}
