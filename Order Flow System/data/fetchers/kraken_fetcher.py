"""
Kraken Public REST API Fetcher — Tier 1 Order Flow Data

Kraken is EU-based and accessible broadly, including the Claude platform.
Trade data includes buy/sell side per trade, giving genuine delta.

Kraken trade format: [price, volume, time, side, type, misc]
  side: 'b' = buy (taker hit the ask), 's' = sell (taker hit the bid)
"""

import urllib.request
import json
from datetime import datetime, timezone
from typing import List, Optional, Dict
from data.models import Candle

BASE_URL = "https://api.kraken.com/0/public"

OHLC_INTERVAL_MAP = {
    "1m":  1,
    "5m":  5,
    "15m": 15,
    "30m": 30,
    "1h":  60,
    "4h":  240,
    "1d":  1440,
    "1w":  10080,
}

PAIR_MAP = {
    "BTCUSDT": "XBTUSD",
    "ETHUSDT":  "ETHUSD",
    "SOLUSDT":  "SOLUSD",
    "BTC":      "XBTUSD",
    "ETH":      "ETHUSD",
}


def _get(endpoint: str, params: dict) -> dict:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url   = f"{BASE_URL}/{endpoint}?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read())


def _pair(symbol: str) -> str:
    return PAIR_MAP.get(symbol.upper(), "XBTUSD")


def fetch_klines(symbol: str, interval: str, limit: int = 200) -> List[Candle]:
    """
    Fetch OHLCV candles from Kraken and enrich with taker volume
    from the recent trades endpoint.
    """
    pair     = _pair(symbol)
    interval_min = OHLC_INTERVAL_MAP.get(interval, 60)

    data   = _get("OHLC", {"pair": pair, "interval": interval_min})
    result = data.get("result", {})
    # Kraken returns data under the pair name (can differ)
    key    = next((k for k in result if k != "last"), None)
    if not key:
        return []

    rows = result[key]

    candles = []
    for row in rows:
        # [time, open, high, low, close, vwap, volume, count]
        candle = Candle(
            timestamp=datetime.fromtimestamp(int(row[0]), tz=timezone.utc),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[6]),
            timeframe=interval,
            symbol=symbol,
            data_tier=2,
        )
        candles.append(candle)

    # Enrich with taker volume from trades
    _enrich_with_taker_volume(candles, pair, interval)
    return candles[-limit:]


def _enrich_with_taker_volume(candles: List[Candle], pair: str, interval: str):
    """Aggregate recent trades into taker buy/sell per candle."""
    try:
        data   = _get("Trades", {"pair": pair, "count": 1000})
        result = data.get("result", {})
        key    = next((k for k in result if k != "last"), None)
        if not key:
            return
        trades = result[key]

        dur_map = {
            "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
            "1h": 3600, "4h": 14400, "1d": 86400,
        }
        candle_sec = dur_map.get(interval, 3600)

        buy_vol:  Dict[int, float] = {}
        sell_vol: Dict[int, float] = {}

        for t in trades:
            # [price, volume, time, side, type, misc]
            ts_sec = int(float(t[2]))
            bucket = (ts_sec // candle_sec) * candle_sec
            vol    = float(t[1])
            side   = t[3]  # 'b' = buy, 's' = sell
            if side == "b":
                buy_vol[bucket]  = buy_vol.get(bucket, 0.0)  + vol
            else:
                sell_vol[bucket] = sell_vol.get(bucket, 0.0) + vol

        for candle in candles:
            bucket = int(candle.timestamp.timestamp())
            bucket = (bucket // candle_sec) * candle_sec
            bv = buy_vol.get(bucket)
            sv = sell_vol.get(bucket)
            if bv is not None or sv is not None:
                candle.taker_buy_volume  = bv or 0.0
                candle.taker_sell_volume = sv or 0.0
                candle.delta             = (bv or 0.0) - (sv or 0.0)
                candle.data_tier         = 1

    except Exception:
        pass


def fetch_current_price(symbol: str) -> Optional[float]:
    try:
        pair   = _pair(symbol)
        data   = _get("Ticker", {"pair": pair})
        result = data.get("result", {})
        key    = next(iter(result), None)
        if key:
            return float(result[key]["c"][0])
    except Exception:
        return None
