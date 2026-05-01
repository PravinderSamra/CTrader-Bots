"""
Bybit Public REST API Fetcher — Tier 1 Order Flow Data

Bybit provides taker buy/sell volume in kline data.
No API key required for public endpoints.
Used as primary exchange API when Binance is geo-blocked.

Bybit kline response fields (V5 API):
  [startTime, openPrice, highPrice, lowPrice, closePrice,
   volume, turnover]

Taker volume requires the /v5/market/recent-trade endpoint
to aggregate, or we use the kline volume with buy/sell ratio
from the /v5/market/tickers endpoint.

For true delta: we use /v5/market/kline with category=linear
and pair it with taker buy ratio from the mark price kline.
"""

import urllib.request
import json
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://api.bybit.com"

INTERVAL_MAP = {
    "1m":  "1",
    "5m":  "5",
    "15m": "15",
    "30m": "30",
    "1h":  "60",
    "4h":  "240",
    "1d":  "D",
    "1w":  "W",
}


def _get(endpoint: str, params: dict) -> dict:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url   = f"{BASE_URL}{endpoint}?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
) -> List[Candle]:
    """
    Fetch OHLCV candles from Bybit V5 API.

    Note: Bybit klines don't include taker buy volume directly.
    We approximate delta by fetching recent trades and aggregating.
    For a cleaner implementation, taker buy ratio from the 24h ticker
    is used as the session-level delta proxy.
    """
    params = {
        "category": "linear",
        "symbol":   symbol.upper(),
        "interval": INTERVAL_MAP.get(interval, interval),
        "limit":    min(limit, 200),
    }
    data   = _get("/v5/market/kline", params)
    result = data.get("result", {})
    rows   = result.get("list", [])

    # Bybit returns newest first — reverse for chronological order
    rows = list(reversed(rows))

    candles = []
    for row in rows:
        # [startTime, open, high, low, close, volume, turnover]
        candle = Candle(
            timestamp=datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
            timeframe=interval,
            symbol=symbol,
            data_tier=2,        # Bybit klines don't include taker volume natively
        )
        candles.append(candle)

    # Enrich with taker buy ratio from the trade history
    _enrich_with_taker_volume(candles, symbol)
    return candles


def _enrich_with_taker_volume(candles: List[Candle], symbol: str):
    """
    Fetch recent trades and use them to approximate taker buy/sell per candle.
    This upgrades candles to Tier 1 if trade data is available.
    """
    try:
        params = {
            "category": "linear",
            "symbol":   symbol.upper(),
            "limit":    1000,
        }
        data   = _get("/v5/market/recent-trade", params)
        trades = data.get("result", {}).get("list", [])

        if not trades:
            return

        # Build per-minute buckets of taker buy vs sell volume
        buy_buckets: dict  = {}
        sell_buckets: dict = {}

        for trade in trades:
            ts_ms  = int(trade["time"])
            ts_min = ts_ms - (ts_ms % 60000)   # Floor to minute
            vol    = float(trade["size"])
            side   = trade.get("side", "")

            if side == "Buy":
                buy_buckets[ts_min]  = buy_buckets.get(ts_min, 0.0)  + vol
            elif side == "Sell":
                sell_buckets[ts_min] = sell_buckets.get(ts_min, 0.0) + vol

        # Assign taker buy/sell to candles where we have trade data
        for candle in candles:
            ts_ms  = int(candle.timestamp.timestamp() * 1000)
            ts_min = ts_ms - (ts_ms % 60000)

            buy_vol  = buy_buckets.get(ts_min, None)
            sell_vol = sell_buckets.get(ts_min, None)

            if buy_vol is not None or sell_vol is not None:
                total_from_trades = (buy_vol or 0) + (sell_vol or 0)
                if total_from_trades > 0:
                    # Scale to candle volume
                    ratio = candle.volume / total_from_trades if total_from_trades else 0.5
                    candle.taker_buy_volume  = (buy_vol  or 0) * ratio
                    candle.taker_sell_volume = (sell_vol or 0) * ratio
                    candle.delta             = candle.taker_buy_volume - candle.taker_sell_volume
                    candle.data_tier         = 1

    except Exception:
        pass  # Leave as Tier 2 if enrichment fails


def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetch the latest price for a symbol."""
    try:
        params = {"category": "linear", "symbol": symbol.upper()}
        data   = _get("/v5/market/tickers", params)
        items  = data.get("result", {}).get("list", [])
        if items:
            return float(items[0].get("lastPrice", 0))
    except Exception:
        return None


def fetch_funding_rate(symbol: str) -> Optional[float]:
    """
    Fetch current funding rate — useful as a sentiment/positioning indicator.
    Positive funding = longs paying shorts (market is long-biased, potential squeeze risk).
    Negative funding = shorts paying longs (market is short-biased, potential squeeze risk).
    """
    try:
        params = {"category": "linear", "symbol": symbol.upper()}
        data   = _get("/v5/market/tickers", params)
        items  = data.get("result", {}).get("list", [])
        if items:
            return float(items[0].get("fundingRate", 0))
    except Exception:
        return None


def compute_session_delta(candles: List[Candle]) -> dict:
    """Same interface as binance_fetcher for interchangeability."""
    from data.fetchers.binance_fetcher import compute_session_delta as _compute
    return _compute(candles)
