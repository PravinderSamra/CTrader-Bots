"""
Yahoo Finance Fetcher — Tier 2 Structural Data

Used for indices (SPX, NDX, DAX, US30, UK100) and oil as a fallback source.
Returns Tier 2 Candle objects — no delta data. Structural analysis only.

IMPORTANT: Yahoo Finance returns market-hours-only candles for US indices.
The session gap filter in structure.py handles the phantom FVG problem this causes.
For instruments that trade 24/7 as CFDs (US500 on Pepperstone), the overnight gap
is an artefact of Yahoo's data, not real. Always verify FVGs on your broker chart.
"""

import urllib.request
import urllib.parse
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
    "4h":  "1h",
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

    ticker: Yahoo Finance ticker (e.g. '^GSPC', '^DJI', '^FTSE', 'GC=F')
    interval: '1m', '5m', '15m', '1h', '1d', '1w'
    limit: approximate number of candles returned
    """
    if interval == "1m":
        period = "7d"
    elif interval in ("5m", "15m", "30m"):
        period = "60d" if limit > 200 else ("30d" if limit > 96 else "7d")
    elif interval == "1h":
        period = "6mo" if limit >= 200 else ("3mo" if limit >= 100 else "1mo")
    else:
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
    except Exception:
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
        # Skip any candle where OHLC data is None (Yahoo occasionally returns null)
        if (i >= len(opens)  or opens[i]  is None or
            i >= len(highs)  or highs[i]  is None or
            i >= len(lows)   or lows[i]   is None or
            i >= len(closes) or closes[i] is None):
            continue
        candle = Candle(
            timestamp=datetime.fromtimestamp(ts, tz=timezone.utc),
            open=float(opens[i]),
            high=float(highs[i]),
            low=float(lows[i]),
            close=float(closes[i]),
            volume=float(volumes[i]) if (i < len(volumes) and volumes[i] is not None) else 0.0,
            timeframe=interval,
            symbol=label,
            data_tier=2,
        )
        candles.append(candle)

    return candles[-limit:]


def fetch_current_price(ticker: str) -> Optional[float]:
    candles = fetch_klines(ticker, "1d", limit=2)
    return candles[-1].close if candles else None
