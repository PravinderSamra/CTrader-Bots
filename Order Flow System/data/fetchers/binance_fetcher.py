"""
Binance Public REST API Fetcher — Tier 1 Order Flow Data

Binance kline data includes 'takerBuyBaseAssetVolume' per candle.
This gives us real aggressive buy volume vs total volume, which is
genuine delta data — not an approximation.

No API key required for public endpoints.
"""

import urllib.request
import json
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://api.binance.com"

INTERVAL_MAP = {
    "1m":  "1m",
    "5m":  "5m",
    "15m": "15m",
    "1h":  "1h",
    "4h":  "4h",
    "1d":  "1d",
    "1w":  "1w",
}


def _get(endpoint: str, params: dict) -> list:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url = f"{BASE_URL}{endpoint}?{query}"
    with urllib.request.urlopen(url, timeout=10) as resp:
        return json.loads(resp.read())


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
    start_time: Optional[int] = None,
    end_time: Optional[int] = None,
) -> List[Candle]:
    """
    Fetch OHLCV candles from Binance with taker buy volume.

    Returns Candle objects with data_tier=1 and real delta values.

    Binance kline columns:
      0  open_time, 1 open, 2 high, 3 low, 4 close,
      5  volume,    6 close_time,
      7  quote_asset_volume,
      8  number_of_trades,
      9  taker_buy_base_asset_volume,   ← aggressive buy volume
      10 taker_buy_quote_asset_volume,
      11 ignore
    """
    params = {
        "symbol": symbol.upper(),
        "interval": INTERVAL_MAP.get(interval, interval),
        "limit": limit,
    }
    if start_time:
        params["startTime"] = start_time
    if end_time:
        params["endTime"] = end_time

    raw = _get("/api/v3/klines", params)
    candles = []
    for row in raw:
        total_vol   = float(row[5])
        taker_buy   = float(row[9])
        taker_sell  = total_vol - taker_buy
        delta       = taker_buy - taker_sell

        candle = Candle(
            timestamp=datetime.fromtimestamp(row[0] / 1000, tz=timezone.utc),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=total_vol,
            timeframe=interval,
            symbol=symbol,
            taker_buy_volume=taker_buy,
            taker_sell_volume=taker_sell,
            delta=delta,
            data_tier=1,
        )
        candles.append(candle)

    return candles


def fetch_aggregate_trades(symbol: str, limit: int = 500) -> list:
    """
    Fetch recent aggregate trades with buyer/seller maker flag.
    'm': True = buyer is the maker (i.e. the taker was a SELLER).
    'm': False = buyer is the taker (i.e. the taker was a BUYER).

    Returns raw list of trade dicts for tape reading approximation.
    """
    params = {"symbol": symbol.upper(), "limit": limit}
    return _get("/api/v3/aggTrades", params)


def fetch_order_book_snapshot(symbol: str, depth: int = 20) -> dict:
    """
    Fetch current order book snapshot (NOT live streaming DOM).
    Provides the best available free approximation of DOM depth.
    Note: This is a point-in-time snapshot, not a live feed.
    """
    params = {"symbol": symbol.upper(), "limit": depth}
    return _get("/api/v3/depth", params)


def fetch_ticker_24h(symbol: str) -> dict:
    """24-hour price and volume statistics."""
    params = {"symbol": symbol.upper()}
    return _get("/api/v3/ticker/24hr", params)


def fetch_current_price(symbol: str) -> float:
    """Current best price."""
    params = {"symbol": symbol.upper()}
    result = _get("/api/v3/ticker/price", params)
    return float(result["price"])


def compute_session_delta(candles: List[Candle]) -> dict:
    """
    Compute delta metrics across a list of Tier 1 candles.
    Returns a summary dict with cumulative delta, taker buy ratio, and divergence flags.
    """
    if not candles or candles[0].data_tier != 1:
        return {"error": "Tier 1 data required — not available for this symbol"}

    total_buy  = sum(c.taker_buy_volume  or 0 for c in candles)
    total_sell = sum(c.taker_sell_volume or 0 for c in candles)
    total_vol  = total_buy + total_sell

    cumulative_delta = [0.0]
    for c in candles:
        cumulative_delta.append(cumulative_delta[-1] + (c.delta or 0))

    cvd_series = cumulative_delta[1:]

    # Detect CVD divergence across the full series
    price_highs = [c.high for c in candles]
    price_lows  = [c.low  for c in candles]

    bearish_divergence = (
        price_highs[-1] > price_highs[-3] and
        cvd_series[-1]  < cvd_series[-3]
    ) if len(candles) >= 3 else False

    bullish_divergence = (
        price_lows[-1] < price_lows[-3] and
        cvd_series[-1] > cvd_series[-3]
    ) if len(candles) >= 3 else False

    taker_buy_pct = total_buy / total_vol if total_vol > 0 else 0.5

    return {
        "data_tier": 1,
        "total_buy_volume": round(total_buy, 4),
        "total_sell_volume": round(total_sell, 4),
        "taker_buy_pct": round(taker_buy_pct, 4),
        "taker_sell_pct": round(1 - taker_buy_pct, 4),
        "cumulative_delta": round(cvd_series[-1], 4) if cvd_series else 0,
        "cvd_trend": "bullish" if cvd_series and cvd_series[-1] > 0 else "bearish",
        "bearish_divergence": bearish_divergence,
        "bullish_divergence": bullish_divergence,
        "bias": (
            "BUYERS dominating (>58% taker buys)" if taker_buy_pct > 0.58
            else "SELLERS dominating (>58% taker sells)" if taker_buy_pct < 0.42
            else "BALANCED (no clear aggression bias)"
        ),
    }
