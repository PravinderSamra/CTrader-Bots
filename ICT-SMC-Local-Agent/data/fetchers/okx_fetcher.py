"""
OKX Fetcher — Crypto OHLCV (Tier 2, public endpoint)

OKX public market data API — no authentication required.
Returns Tier 2 candles (OHLCV only — taker delta not available on free endpoint).

Note: True Tier 1 taker buy/sell volume requires authenticated OKX WebSocket.
For now, all crypto candles are marked data_tier=2.
"""

import urllib.request
import urllib.parse
import json
from datetime import datetime, timezone
from typing import List, Optional
from data.models import Candle

BASE_URL = "https://www.okx.com/api/v5/market/candles"
HISTORY_URL = "https://www.okx.com/api/v5/market/history-candles"

BAR_MAP = {
    "1m":  "1m",
    "5m":  "5m",
    "15m": "15m",
    "30m": "30m",
    "1h":  "1H",
    "4h":  "4H",
    "1d":  "1Dutc",
    "1w":  "1Wutc",
}


def fetch_klines(
    inst_id: str,
    interval: str,
    limit: int = 100,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch OHLCV candles from OKX.

    inst_id: OKX instrument ID (e.g. 'BTC-USDT', 'ETH-USDT', 'SOL-USDT')
    interval: '1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w'
    limit: number of candles (max 300 per request)
    """
    bar = BAR_MAP.get(interval, interval)
    all_candles: List[Candle] = []
    label = symbol_label or inst_id

    # OKX returns max 300 per request — paginate if needed
    requests_needed = (limit // 300) + 1
    after_ts: Optional[str] = None

    for _ in range(requests_needed):
        batch_limit = min(300, limit - len(all_candles))
        if batch_limit <= 0:
            break

        params: dict = {"instId": inst_id, "bar": bar, "limit": str(batch_limit)}
        if after_ts:
            params["after"] = after_ts

        url = BASE_URL + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read())
        except Exception:
            break

        rows = data.get("data", [])
        if not rows:
            break

        batch: List[Candle] = []
        for row in rows:
            try:
                ts_ms = int(row[0])
                o, h, l, c, vol = (float(row[k]) for k in range(1, 6))
            except (IndexError, ValueError, TypeError):
                continue
            batch.append(Candle(
                timestamp=datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc),
                open=o, high=h, low=l, close=c, volume=vol,
                timeframe=interval,
                symbol=label,
                data_tier=2,
            ))

        # OKX returns newest first — reverse for chronological order
        batch.reverse()
        all_candles = batch + all_candles
        if rows:
            after_ts = rows[-1][0]

    all_candles.sort(key=lambda c: c.timestamp)
    return all_candles[-limit:]


def fetch_current_price(inst_id: str) -> Optional[float]:
    url = f"https://www.okx.com/api/v5/market/ticker?instId={urllib.parse.quote(inst_id)}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        return float(data["data"][0]["last"])
    except Exception:
        return None
