"""
OKX Public REST API Fetcher — Tier 1 Order Flow Data

OKX is accessible in the Claude platform environment (Binance is geo-blocked).
Provides genuine taker buy/sell volume via trade history aggregation.

OKX kline format (9 columns):
  [ts, open, high, low, close, vol, volCcy, volCcyQuote, confirm]
  vol = base currency volume (no taker split in klines)

Taker split comes from aggregating /api/v5/market/trades:
  side='buy'  → taker is aggressive buyer (hit the ask)
  side='sell' → taker is aggressive seller (hit the bid)
"""

import urllib.request
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from data.models import Candle

BASE_URL = "https://www.okx.com"

# OKX bar intervals
INTERVAL_MAP = {
    "1m":  "1m",
    "5m":  "5m",
    "15m": "15m",
    "30m": "30m",
    "1h":  "1H",
    "4h":  "4H",
    "1d":  "1D",
    "1w":  "1W",
}

# Map our generic symbols to OKX instrument IDs
SYMBOL_MAP = {
    "BTCUSDT": "BTC-USDT-SWAP",
    "ETHUSDT":  "ETH-USDT-SWAP",
    "SOLUSDT":  "SOL-USDT-SWAP",
    "BTC":      "BTC-USDT-SWAP",
    "ETH":      "ETH-USDT-SWAP",
    "SOL":      "SOL-USDT-SWAP",
}


def _get(endpoint: str, params: dict) -> dict:
    query = "&".join(f"{k}={v}" for k, v in params.items())
    url   = f"{BASE_URL}{endpoint}?{query}"
    req   = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read())


def _inst_id(symbol: str) -> str:
    return SYMBOL_MAP.get(symbol.upper(), f"{symbol[:3].upper()}-USDT-SWAP")


def fetch_klines(symbol: str, interval: str, limit: int = 200) -> List[Candle]:
    """
    Fetch OHLCV candles from OKX, then enrich with taker buy/sell
    volume from the recent trades endpoint.

    Returns Candle objects. data_tier=1 for candles where taker
    volume was successfully computed from trade aggregation.
    """
    inst = _inst_id(symbol)
    bar  = INTERVAL_MAP.get(interval, "1H")

    data = _get("/api/v5/market/candles", {
        "instId": inst,
        "bar":    bar,
        "limit":  min(limit, 300),
    })
    rows = data.get("data", [])
    rows = list(reversed(rows))   # OKX returns newest first

    candles = []
    for row in rows:
        # [ts, o, h, l, c, vol, volCcy, volCcyQuote, confirm]
        candle = Candle(
            timestamp=datetime.fromtimestamp(int(row[0]) / 1000, tz=timezone.utc),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
            timeframe=interval,
            symbol=symbol,
            data_tier=2,   # Will upgrade to Tier 1 after enrichment
        )
        candles.append(candle)

    # Enrich the most recent candles with Tier 1 taker volume
    _enrich_with_taker_volume(candles, inst, interval)
    return candles[-limit:]


def _enrich_with_taker_volume(candles: List[Candle], inst_id: str, interval: str):
    """
    Fetch recent trades and aggregate taker buy/sell volume per candle.
    Upgrades enriched candles from data_tier=2 to data_tier=1.
    """
    try:
        # Fetch up to 500 most recent trades
        data   = _get("/api/v5/market/trades", {"instId": inst_id, "limit": 500})
        trades = data.get("data", [])
        if not trades:
            return

        # Determine candle duration in milliseconds
        dur_map = {
            "1m": 60_000, "5m": 300_000, "15m": 900_000, "30m": 1_800_000,
            "1h": 3_600_000, "4h": 14_400_000, "1d": 86_400_000,
        }
        candle_ms = dur_map.get(interval, 3_600_000)

        # Bucket trades by candle start time
        buy_vol:  Dict[int, float] = {}
        sell_vol: Dict[int, float] = {}

        for t in trades:
            ts_ms    = int(t["ts"])
            bucket   = (ts_ms // candle_ms) * candle_ms
            size     = float(t["sz"])
            side     = t.get("side", "")
            if side == "buy":
                buy_vol[bucket]  = buy_vol.get(bucket, 0.0)  + size
            elif side == "sell":
                sell_vol[bucket] = sell_vol.get(bucket, 0.0) + size

        # Assign taker volume to matching candles
        for candle in candles:
            bucket = int(candle.timestamp.timestamp() * 1000)
            bucket = (bucket // candle_ms) * candle_ms
            bv = buy_vol.get(bucket)
            sv = sell_vol.get(bucket)
            if bv is not None or sv is not None:
                candle.taker_buy_volume  = bv or 0.0
                candle.taker_sell_volume = sv or 0.0
                candle.delta             = (bv or 0.0) - (sv or 0.0)
                candle.data_tier         = 1

    except Exception:
        pass  # Leave as Tier 2 if enrichment fails


def parse_aktools_taker_volume(csv_text: str) -> List[dict]:
    """
    Parse the CSV output from mcp__aktools__okx_taker_volume.
    Format: 时间,卖出量,买入量  (timestamp, sell_vol, buy_vol)

    Returns list of dicts with sell_vol, buy_vol, delta, buy_pct.
    The AKTools MCP returns data newest-first (most recent row = index 0).
    """
    rows = []
    lines = csv_text.strip().split("\n")
    for line in lines[1:]:  # Skip header
        parts = line.split(",")
        if len(parts) >= 3:
            try:
                sell = float(parts[1].strip())
                buy  = float(parts[2].strip())
                total = buy + sell
                rows.append({
                    "sell_vol": sell,
                    "buy_vol":  buy,
                    "delta":    buy - sell,
                    "buy_pct":  buy / total if total > 0 else 0.5,
                    "total_vol": total,
                })
            except (ValueError, IndexError):
                continue
    return rows  # Index 0 = most recent


def compute_delta_from_aktools(rows: List[dict], lookback: int = 24) -> dict:
    """
    Compute delta summary from AKTools OKX taker volume rows.
    lookback = number of hourly periods to analyse (default 24 = last day).

    This is GENUINE Tier 1 data — real OKX aggressive buy/sell volume.
    """
    recent = rows[:lookback]
    if not recent:
        return {"available": False}

    total_buy  = sum(r["buy_vol"]  for r in recent)
    total_sell = sum(r["sell_vol"] for r in recent)
    total_vol  = total_buy + total_sell
    buy_pct    = total_buy / total_vol if total_vol > 0 else 0.5

    # Cumulative delta (newest first → reverse for chronological CVD)
    chrono   = list(reversed(recent))
    cvd      = []
    running  = 0.0
    for r in chrono:
        running += r["delta"]
        cvd.append(running)

    # CVD trend: is cumulative delta rising or falling?
    cvd_rising = cvd[-1] > cvd[0] if len(cvd) > 1 else True

    # Detect divergence over recent 6 hours (if we have enough data)
    recent_6 = rows[:6]
    buy_pct_6h = (
        sum(r["buy_vol"] for r in recent_6) /
        sum(r["total_vol"] for r in recent_6)
        if recent_6 and sum(r["total_vol"] for r in recent_6) > 0
        else 0.5
    )

    # Spot any recent hour where sell dominated strongly (>60%)
    sell_dominant_hours = sum(1 for r in recent if r["buy_pct"] < 0.40)
    buy_dominant_hours  = sum(1 for r in recent if r["buy_pct"] > 0.60)

    if buy_pct > 0.55:
        bias = f"BUYERS dominating — {buy_pct:.1%} taker buys over {lookback}h"
    elif buy_pct < 0.45:
        bias = f"SELLERS dominating — {1 - buy_pct:.1%} taker sells over {lookback}h"
    else:
        bias = f"BALANCED — {buy_pct:.1%} buy / {1 - buy_pct:.1%} sell over {lookback}h"

    most_recent = rows[0]
    latest_bias = (
        "Latest hour: BUYERS aggressive" if most_recent["buy_pct"] > 0.55
        else "Latest hour: SELLERS aggressive" if most_recent["buy_pct"] < 0.45
        else "Latest hour: BALANCED"
    )

    return {
        "available":          True,
        "data_tier":          1,
        "source":             "OKX Contracts (via AKTools MCP)",
        "periods_analysed":   lookback,
        "total_buy_vol":      round(total_buy,  2),
        "total_sell_vol":     round(total_sell, 2),
        "buy_pct_24h":        round(buy_pct,    4),
        "buy_pct_6h":         round(buy_pct_6h, 4),
        "cvd_direction":      "rising (net buying pressure)" if cvd_rising else "falling (net selling pressure)",
        "cvd_final":          round(cvd[-1], 2) if cvd else 0,
        "buy_dominant_hours": buy_dominant_hours,
        "sell_dominant_hours": sell_dominant_hours,
        "latest_hour":        {
            "buy_vol":  round(most_recent["buy_vol"],  2),
            "sell_vol": round(most_recent["sell_vol"], 2),
            "delta":    round(most_recent["delta"],    2),
            "buy_pct":  round(most_recent["buy_pct"],  4),
        },
        "bias":        bias,
        "latest_bias": latest_bias,
    }


def fetch_current_price(symbol: str) -> Optional[float]:
    """Fetch latest price from OKX."""
    try:
        inst = _inst_id(symbol)
        data = _get("/api/v5/market/tickers", {"instId": inst})
        items = data.get("data", [])
        if items:
            return float(items[0].get("last", 0))
    except Exception:
        return None
