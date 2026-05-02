"""
Twelve Data REST API Fetcher — 5m/15m/1h intraday data for Forex, Indices, Crypto

Sign up free at: https://twelvedata.com/register
Free tier: 800 API credits/day, 8 requests/minute.
No credit card required.

After signing up, add your key to config.py:
  TWELVE_DATA_API_KEY = "your_key_here"
Or set environment variable: TWELVE_DATA_API_KEY

Covers:
  Forex  : EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD, XAU/USD (gold)
  Indices: SPX (S&P 500), NDX (NASDAQ 100), DJI (Dow), DAX, FTSE
  Crypto : BTC/USD, ETH/USD, SOL/USD (lower priority — OKX/Kraken better for order flow)
  ETFs   : SPY, QQQ, GLD

Data tier: 2 — OHLCV only, no taker volume split.
Advantage over Yahoo Finance: finer resolution (5m), more reliable intraday feeds,
better forex symbol coverage, up to 5000 candles per request.
"""

import urllib.request
import urllib.parse
import json
import os
from datetime import datetime, timezone
from typing import List, Optional

from data.models import Candle

BASE_URL = "https://api.twelvedata.com"

# Interval mapping — our labels to Twelve Data format
INTERVAL_MAP = {
    "1m":  "1min",
    "5m":  "5min",
    "15m": "15min",
    "30m": "30min",
    "1h":  "1h",
    "4h":  "4h",
    "1d":  "1day",
    "1w":  "1week",
}

# Symbol mapping — our labels to Twelve Data symbols
SYMBOL_MAP = {
    # Forex
    "EURUSD":  "EUR/USD",
    "GBPUSD":  "GBP/USD",
    "USDJPY":  "USD/JPY",
    "USDCHF":  "USD/CHF",
    "AUDUSD":  "AUD/USD",
    "USDCAD":  "USD/CAD",
    "NZDUSD":  "NZD/USD",
    "EURGBP":  "EUR/GBP",
    "EURJPY":  "EUR/JPY",
    "GBPJPY":  "GBP/JPY",
    # Commodities (spot)
    "XAUUSD":  "XAU/USD",
    "XAGUSD":  "XAG/USD",
    # Indices
    "SPX":     "SPX",
    "NDX":     "NDX",
    "DJI":     "DJI",
    "DAX":     "DAX",
    "FTSE":    "FTSE",
    "NKY":     "N225",
    # ETFs (fallback for index intraday when index direct not available)
    "SPY":     "SPY",
    "QQQ":     "QQQ",
    "GLD":     "GLD",
    # Crypto (lower priority — use OKX/Kraken for Tier 1)
    "BTCUSDT": "BTC/USD",
    "ETHUSDT": "ETH/USD",
    "SOLUSDT": "SOL/USD",
    "BTC":     "BTC/USD",
    "ETH":     "ETH/USD",
}


def _get_api_key() -> Optional[str]:
    """Read API key from env var or config."""
    key = os.environ.get("TWELVE_DATA_API_KEY")
    if key:
        return key
    try:
        from config import TWELVE_DATA_API_KEY
        return TWELVE_DATA_API_KEY
    except (ImportError, AttributeError):
        return None


def _get(endpoint: str, params: dict) -> dict:
    query = "&".join(f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items())
    url   = f"{BASE_URL}{endpoint}?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch OHLCV candles from Twelve Data.

    Returns Candle objects with data_tier=2 (no taker volume).
    Falls back to empty list if API key missing or request fails.
    """
    api_key = _get_api_key()
    if not api_key:
        raise ValueError(
            "Twelve Data API key not set. "
            "Sign up free at https://twelvedata.com/register then add "
            "TWELVE_DATA_API_KEY to config.py or set as environment variable."
        )

    td_symbol   = SYMBOL_MAP.get(symbol.upper(), symbol.upper())
    td_interval = INTERVAL_MAP.get(interval, "1h")
    label       = symbol_label or symbol

    data = _get("/time_series", {
        "symbol":     td_symbol,
        "interval":   td_interval,
        "outputsize": min(limit, 5000),
        "order":      "ASC",
        "apikey":     api_key,
    })

    if data.get("status") == "error":
        raise RuntimeError(f"Twelve Data error: {data.get('message', 'unknown')}")

    values = data.get("values", [])

    candles = []
    for row in values:
        try:
            dt = datetime.fromisoformat(row["datetime"]).replace(tzinfo=timezone.utc)
            candles.append(Candle(
                timestamp  = dt,
                open       = float(row["open"]),
                high       = float(row["high"]),
                low        = float(row["low"]),
                close      = float(row["close"]),
                volume     = float(row.get("volume") or 0),
                timeframe  = interval,
                symbol     = label,
                data_tier  = 2,
            ))
        except (KeyError, ValueError):
            continue

    return candles[-limit:]


def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetch latest price from Twelve Data."""
    api_key = _get_api_key()
    if not api_key:
        return None
    try:
        td_symbol = SYMBOL_MAP.get(symbol.upper(), symbol.upper())
        data = _get("/price", {"symbol": td_symbol, "apikey": api_key})
        price = data.get("price")
        return float(price) if price else None
    except Exception:
        return None


def is_configured() -> bool:
    """Return True if the API key is set and the service is usable."""
    return _get_api_key() is not None


def test_connection() -> dict:
    """Quick connectivity and auth test. Returns status dict."""
    key = _get_api_key()
    if not key:
        return {
            "ok": False,
            "message": (
                "API key not configured. "
                "Sign up free at https://twelvedata.com/register "
                "then add TWELVE_DATA_API_KEY to config.py"
            ),
        }
    try:
        data = _get("/price", {"symbol": "EUR/USD", "apikey": key})
        if "price" in data:
            return {
                "ok": True,
                "message": f"Connected. EUR/USD = {data['price']}",
            }
        return {"ok": False, "message": str(data)}
    except Exception as e:
        return {"ok": False, "message": str(e)}
