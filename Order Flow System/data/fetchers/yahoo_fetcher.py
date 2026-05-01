"""
Yahoo Finance Fetcher — Tier 2 Structural Data

Used for indices (SPX, NDX, DAX), commodities (Gold, Oil), and
forex as a backup source. Returns Tier 2 Candle objects — no
delta data. Structural analysis only.

Uses Yahoo Finance JSON API directly via urllib — no external
dependencies required.
"""

import urllib.request
import json
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://query1.finance.yahoo.com/v8/finance/chart"

INTERVAL_MAP = {
    "1m":  "1m",
    "5m":  "5m",
    "15m": "15m",
    "30m": "30m",
    "1h":  "60m",
    "4h":  "1h",     # Yahoo doesn't have 4h — use 1h and aggregate
    "1d":  "1d",
    "1w":  "1wk",
}


def fetch_klines(
    ticker: str,
    interval: str,
    limit: int = 200,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch OHLCV candles from Yahoo Finance.
    Returns Tier 2 Candles — no delta data available.

    ticker: Yahoo Finance ticker (e.g. '^GSPC', 'GC=F', 'EURUSD=X')
    interval: '1m', '5m', '15m', '1h', '1d', '1w'
    limit: approximate number of candles (Yahoo uses period instead)
    """
    period_map = {200: "6mo", 100: "3mo", 50: "1mo", 20: "5d"}
    period = next((v for k, v in period_map.items() if limit <= k), "1y")

    url = (
        f"{BASE_URL}/{urllib.parse.quote(ticker)}"
        f"?interval={INTERVAL_MAP.get(interval, interval)}&range={period}"
    )

    headers = {"User-Agent": "Mozilla/5.0"}
    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception as e:
        return []

    result = data.get("chart", {}).get("result", [])
    if not result:
        return []

    r = result[0]
    timestamps = r.get("timestamp", [])
    ohlcv = r.get("indicators", {}).get("quote", [{}])[0]

    opens   = ohlcv.get("open",   [])
    highs   = ohlcv.get("high",   [])
    lows    = ohlcv.get("low",    [])
    closes  = ohlcv.get("close",  [])
    volumes = ohlcv.get("volume", [])

    label = symbol_label or ticker
    candles = []
    for i, ts in enumerate(timestamps):
        if i >= len(opens) or opens[i] is None:
            continue
        candle = Candle(
            timestamp=datetime.fromtimestamp(ts, tz=timezone.utc),
            open=float(opens[i]),
            high=float(highs[i]),
            low=float(lows[i]),
            close=float(closes[i]),
            volume=float(volumes[i]) if volumes[i] is not None else 0.0,
            timeframe=interval,
            symbol=label,
            data_tier=2,
        )
        candles.append(candle)

    return candles[-limit:]


def fetch_current_price(ticker: str) -> Optional[float]:
    """Fetch the latest closing price."""
    candles = fetch_klines(ticker, "1d", limit=2)
    return candles[-1].close if candles else None


# Need to import parse for URL encoding
import urllib.parse
