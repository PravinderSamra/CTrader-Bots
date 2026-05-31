"""
Twelve Data Fetcher — Forex & Spot Commodities (Tier 2)

Used for forex pairs and spot commodity prices (XAU/USD, etc.).
Free tier: 800 API credits/day, 8 credits per request.
Max ~100 requests/day on free plan. Shared across all symbols.

Key advantage over Yahoo: returns spot forex prices (not futures),
matching what retail brokers (Pepperstone, etc.) display.
"""

import urllib.request
import urllib.parse
import json
import os
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://api.twelvedata.com/time_series"

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


def _get_api_key() -> str:
    key = os.environ.get("TWELVE_DATA_API_KEY", "")
    if not key:
        raise ValueError(
            "TWELVE_DATA_API_KEY not set. Add it to your .env file or environment."
        )
    return key


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 120,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch OHLCV candles from Twelve Data.

    symbol: Twelve Data symbol (e.g. 'EUR/USD', 'GBP/USD', 'XAU/USD', 'USD/JPY')
    interval: '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'
    limit: number of candles (max 5000 on paid, ~500 on free)
    """
    try:
        api_key = _get_api_key()
    except ValueError:
        return []

    params = {
        "symbol":   symbol,
        "interval": INTERVAL_MAP.get(interval, interval),
        "outputsize": str(min(limit, 500)),
        "apikey":   api_key,
        "timezone": "UTC",
        "order":    "ASC",
    }

    url = BASE_URL + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    if data.get("status") == "error" or "values" not in data:
        return []

    label = symbol_label or symbol
    candles = []
    for bar in data["values"]:
        try:
            o = float(bar["open"])
            h = float(bar["high"])
            l = float(bar["low"])
            c = float(bar["close"])
        except (KeyError, TypeError, ValueError):
            continue
        ts = datetime.strptime(bar["datetime"], "%Y-%m-%d %H:%M:%S").replace(
            tzinfo=timezone.utc
        )
        candles.append(Candle(
            timestamp=ts,
            open=o, high=h, low=l, close=c,
            volume=float(bar.get("volume", 0) or 0),
            timeframe=interval,
            symbol=label,
            data_tier=2,
        ))

    return candles[-limit:]


def fetch_current_price(symbol: str) -> Optional[float]:
    candles = fetch_klines(symbol, "1h", limit=2)
    return candles[-1].close if candles else None
