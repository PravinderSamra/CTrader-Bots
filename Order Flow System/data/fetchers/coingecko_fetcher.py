"""
CoinGecko Public API Fetcher

Provides OHLCV data for cryptocurrencies.
Note: CoinGecko does NOT provide taker buy/sell volume split.
All data from this fetcher is Tier 2 (structural analysis only).

The CoinGecko MCP (when available in Claude sessions) can be used
for richer data, but the public REST API is used here for the
standalone Python system.

Exchange-level delta data (Tier 1) would require Binance/Bybit
access, which may be geo-restricted in some environments.
"""

import urllib.request
import json
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://api.coingecko.com/api/v3"

COIN_IDS = {
    "BTCUSDT": "bitcoin",
    "ETHUSDT":  "ethereum",
    "SOLUSDT":  "solana",
    "BTC":      "bitcoin",
    "ETH":      "ethereum",
    "SOL":      "solana",
}

DAYS_MAP = {
    "1m":  1,
    "5m":  1,
    "15m": 2,
    "1h":  7,
    "4h":  30,
    "1d":  90,
    "1w":  365,
}


def _get(endpoint: str, params: dict = None) -> object:
    query = ("?" + "&".join(f"{k}={v}" for k, v in params.items())) if params else ""
    url   = f"{BASE_URL}{endpoint}{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "accept": "application/json"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
) -> List[Candle]:
    """
    Fetch OHLCV candles from CoinGecko.

    CoinGecko OHLC endpoint returns [timestamp, open, high, low, close].
    Volume is fetched separately from market_chart endpoint.

    Returns Tier 2 candles — no taker buy/sell volume available.
    """
    coin_id = COIN_IDS.get(symbol.upper())
    if not coin_id:
        # Try stripping USDT suffix
        base = symbol.replace("USDT", "").replace("USD", "").upper()
        coin_id = COIN_IDS.get(base, base.lower())

    days = DAYS_MAP.get(interval, 7)

    try:
        # OHLC data
        ohlc_data = _get(f"/coins/{coin_id}/ohlc", {"vs_currency": "usd", "days": days})

        # Volume data (from market_chart — gives [timestamp, volume] pairs)
        market_data = _get(
            f"/coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": days, "interval": "daily" if "d" in interval else "hourly"}
        )
        volumes = {int(v[0]): float(v[1]) for v in market_data.get("total_volumes", [])}

    except Exception as e:
        return []

    candles = []
    for row in ohlc_data:
        ts_ms = int(row[0])
        # Find nearest volume entry (within 1 hour)
        vol = 0.0
        for vts, vv in volumes.items():
            if abs(vts - ts_ms) < 3_600_000:
                vol = vv
                break

        candle = Candle(
            timestamp=datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=vol,
            timeframe=interval,
            symbol=symbol,
            data_tier=2,  # CoinGecko has no taker buy/sell — structural only
        )
        candles.append(candle)

    # Sort chronologically and limit
    candles.sort(key=lambda c: c.timestamp)
    return candles[-limit:]


def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetch current price for a crypto symbol."""
    coin_id = COIN_IDS.get(symbol.upper(), symbol.lower().replace("usdt", ""))
    try:
        data = _get("/simple/price", {"ids": coin_id, "vs_currencies": "usd"})
        return data.get(coin_id, {}).get("usd")
    except Exception:
        return None


def fetch_market_sentiment(symbol: str) -> dict:
    """
    Fetch broad market data — useful for sentiment and volume trend context.
    Not Tier 1 order flow, but useful as confluence (Tier 3).
    """
    coin_id = COIN_IDS.get(symbol.upper(), symbol.lower().replace("usdt", ""))
    try:
        data = _get(f"/coins/{coin_id}", {
            "localization": "false",
            "tickers": "false",
            "market_data": "true",
            "community_data": "false",
            "developer_data": "false",
        })
        md = data.get("market_data", {})
        return {
            "data_tier": 3,  # Sentiment/confluence only
            "price_change_24h_pct": md.get("price_change_percentage_24h", 0),
            "price_change_7d_pct":  md.get("price_change_percentage_7d", 0),
            "volume_24h":  md.get("total_volume", {}).get("usd", 0),
            "market_cap":  md.get("market_cap",   {}).get("usd", 0),
            "note": "CoinGecko volume is total traded volume — not buy/sell split. Tier 3 confluence only.",
        }
    except Exception:
        return {"data_tier": 3, "error": "Failed to fetch sentiment data"}
