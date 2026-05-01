"""
Platform Detector — Smart Data Source Selection

Determines at runtime which exchange APIs are accessible and returns
the optimal Tier 1 order flow source for the current environment.

Priority Logic:
  Claude platform (this env): OKX + Kraken directly accessible (Binance geo-blocked)
  Local computer:             Binance first (cleanest Tier 1 via kline takerBuyVol)

The detector runs once at startup and caches the result.
"""

import urllib.request
import json
import os
from typing import List, Tuple

_CACHE: dict = {}


def _probe(url: str, timeout: int = 5) -> bool:
    """Return True if the URL responds successfully."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            data = json.loads(r.read())
            return bool(data)
    except Exception:
        return False


def detect_sources() -> List[str]:
    """
    Test each exchange API and return a priority-ordered list of
    available Tier 1 sources.

    Returns list of source names: ['okx', 'kraken', 'binance', ...]
    Callers should use the first item as the primary source.
    """
    if _CACHE.get("sources") is not None:
        return _CACHE["sources"]

    sources = []

    # Binance — cleanest Tier 1 (takerBuyBaseAssetVolume built into klines)
    if _probe("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"):
        sources.append("binance")

    # OKX — accessible in Claude platform; taker volume via trade aggregation
    if _probe("https://www.okx.com/api/v5/market/trades?instId=BTC-USDT-SWAP&limit=5"):
        sources.append("okx")

    # Kraken — EU-based; accessible broadly; buy/sell per trade
    if _probe("https://api.kraken.com/0/public/Trades?pair=XBTUSD&count=10"):
        sources.append("kraken")

    # Bybit — fallback Tier 1 with trade aggregation
    if _probe("https://api.bybit.com/v5/market/recent-trade?category=linear&symbol=BTCUSDT&limit=5"):
        sources.append("bybit")

    # Deribit — BTC/ETH perpetuals only
    if _probe("https://www.deribit.com/api/v2/public/get_last_trades_by_instrument?instrument_name=BTC-PERPETUAL&count=5"):
        sources.append("deribit")

    _CACHE["sources"] = sources
    return sources


def primary_source() -> str:
    """Return the best available Tier 1 source name."""
    sources = detect_sources()
    return sources[0] if sources else "coingecko"


def is_binance_available() -> bool:
    return "binance" in detect_sources()


def is_okx_available() -> bool:
    return "okx" in detect_sources()


def platform_summary() -> str:
    sources = detect_sources()
    tier1 = [s for s in sources if s != "coingecko"]
    if not tier1:
        return "No Tier 1 exchange APIs accessible — using CoinGecko (Tier 2, structural only)"
    primary = sources[0]
    labels = {
        "binance": "Binance (kline taker volume — cleanest Tier 1)",
        "okx":     "OKX (trade aggregation — Tier 1)",
        "kraken":  "Kraken (trade aggregation — Tier 1)",
        "bybit":   "Bybit (trade aggregation — Tier 1)",
        "deribit": "Deribit (BTC/ETH perps — Tier 1)",
    }
    return f"Primary: {labels.get(primary, primary)} | Also available: {', '.join(sources[1:]) or 'none'}"
