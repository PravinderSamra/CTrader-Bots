"""
cTrader Remote MCP Fetcher — Tier 1 Data

Fetches exact Pepperstone CFD prices via the cTrader Remote MCP HTTP API.
Replaces Yahoo Finance (indices/oil) and Twelve Data (forex/gold) with:
  - 24/7 CFD candles — no overnight market-hours gaps, no phantom FVGs
  - Exact Pepperstone price feed — matches your cTrader/TradingView chart
  - Candles marked data_tier=1 (direct broker feed, highest quality)

Token priority:
  1. CTRADER_MCP_TOKEN env var (set in .env for live account)
  2. Demo account fallback (read-only market data, no trading)
"""

import urllib.request
import urllib.error
import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from data.models import Candle

# ── Config ────────────────────────────────────────────────────────────────────
_MCP_URL = "https://mcp.ctrader.com/trading/mcp"

_TOKEN = os.environ.get(
    "CTRADER_MCP_TOKEN",
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

# cTrader period strings — server uses underscore format (M_1, H_1, D_1, etc.)
_PERIOD_MAP = {
    "1m": "M_1",  "5m": "M_5",  "15m": "M_15", "30m": "M_30",
    "1h": "H_1",  "4h": "H_4",  "1d":  "D_1",  "1w":  "W_1",
}

# Our instrument labels → Pepperstone cTrader symbol names
# If a symbol doesn't match exactly, _get_symbol_id() falls back to partial matching
SYMBOL_MAP = {
    "EURUSD":  "EURUSD",
    "GBPUSD":  "GBPUSD",
    "USDJPY":  "USDJPY",
    "GBPJPY":  "GBPJPY",
    "GOLD":    "XAUUSD",
    "OIL":     "WTOIL-PERP",
    "SPX":     "US500",
    "NDX":     "NAS100",
    "US30":    "US30",
    "DAX":     "GER40",
    "UK100":   "UK100",
    "BTCUSDT": "BTCUSD",
    "ETHUSDT": "ETHUSD",
    "SOLUSDT": "SOLUSD",
}

# Pip digits per cTrader symbol — raw pipette price / 10^pipDigits = display price
# e.g. EURUSD raw 116305 / 100000 = 1.16305
# get_symbols does not return pipDigits; we auto-detect from price ranges (see below)
# These are starting guesses; _pip_digits() corrects them via _PRICE_RANGES auto-detect.
_PIP_DIGITS_HINT: dict[str, int] = {
    "EURUSD": 5, "GBPUSD": 5, "AUDUSD": 5, "NZDUSD": 5,
    "USDCHF": 5, "USDCAD": 5, "EURGBP": 5, "EURAUD": 5,
    "USDJPY": 3, "GBPJPY": 3, "EURJPY": 3, "AUDJPY": 3,
    "XAUUSD": 3, "XAGUSD": 3,
    "US500":  3, "US100":  4, "US30":   4,
    "GER40":  3, "UK100":  3, "AUS200": 3,
    "USOIL":  3, "UKOIL":  3,
    "BTCUSD": 3, "ETHUSD": 3, "SOLUSD": 3,
}

# Plausible display-price ranges per symbol — used to auto-detect pip digits
# from a live raw value. Ranges are intentionally wide.
_PRICE_RANGES: dict[str, tuple[float, float]] = {
    "EURUSD": (0.80, 1.60),   "GBPUSD": (1.00, 1.70),
    "AUDUSD": (0.50, 1.10),   "NZDUSD": (0.40, 0.90),
    "USDCHF": (0.80, 1.20),   "USDCAD": (1.10, 1.60),
    "USDJPY": (100, 180),     "GBPJPY": (150, 230),
    "EURJPY": (110, 175),
    "XAUUSD": (1_400, 6_000), "XAGUSD": (15, 60),
    "US500":  (3_000, 12_000),"US100":  (8_000, 30_000),
    "US30":   (25_000, 55_000),"GER40": (12_000, 30_000),
    "UK100":  (6_000, 13_000),"AUS200": (5_000, 10_000),
    "USOIL":  (40, 180),      "UKOIL":  (40, 180),
    "BTCUSD": (10_000, 250_000),"ETHUSD":(500, 15_000),
    "SOLUSD": (10, 600),
}

# Runtime pip-digits cache — populated on first successful candle fetch
_pip_digits_cache: dict[str, int] = {}

# ── Session State ─────────────────────────────────────────────────────────────
_session_id: Optional[str] = None
_symbol_id_cache: dict[str, int] = {}   # ctrader_symbol_name → symbolId
_symbols_loaded: bool = False


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    """POST a JSON-RPC message to the MCP endpoint. Returns (parsed_data, session_id)."""
    body = json.dumps(payload).encode()
    headers = {
        "Authorization":  f"Bearer {_TOKEN}",
        "Accept":         "application/json, text/event-stream",
        "Content-Type":   "application/json",
        # Connection: close required — Python's HTTP keep-alive reuses the SSE
        # connection which makes the server reject subsequent requests as orphaned.
        "Connection":     "close",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    req = urllib.request.Request(_MCP_URL, data=body, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            new_sid = (resp.headers.get("Mcp-Session-Id")
                       or resp.headers.get("mcp-session-id")
                       or session_id)
            raw = resp.read().decode()
            for line in raw.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:]), new_sid
    except urllib.error.HTTPError as e:
        if e.code == 404:
            # Session not found — signal caller to reinitialise
            return {"_session_expired": True}, None
    except Exception:
        pass
    return None, session_id


def _ensure_session() -> bool:
    """Initialize MCP session if not already active."""
    global _session_id
    if _session_id:
        return True

    data, sid = _post({
        "jsonrpc": "2.0",
        "method":  "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities":    {},
            "clientInfo":      {"name": "ict-smc-scanner", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        return True
    return False


def _call_tool(tool: str, arguments: dict) -> Optional[dict]:
    """Call a cTrader MCP tool. Reinitialises session once on expiry."""
    global _session_id

    if not _ensure_session():
        return None

    payload = {
        "jsonrpc": "2.0",
        "method":  "tools/call",
        "params":  {"name": tool, "arguments": arguments},
        "id":      1,
    }

    data, new_sid = _post(payload, _session_id)

    # Expired session (404 or JSON error) — reset and retry once
    expired = (
        (data and data.get("_session_expired")) or
        (data and data.get("error", {}).get("message", "").startswith("No valid session")) or
        (data is None)
    )
    if expired:
        _session_id = None
        if not _ensure_session():
            return None
        data, new_sid = _post(payload, _session_id)

    if new_sid:
        _session_id = new_sid

    if not data or "result" not in data:
        return None

    content = data["result"].get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def _load_symbols() -> None:
    """Fetch and cache the symbol list (called once per session)."""
    global _symbols_loaded
    if _symbols_loaded:
        return

    result = _call_tool("get_symbols", {})
    if not result:
        return

    for sym in result.get("symbols", []):
        raw_name = sym.get("name") or sym.get("symbolName") or ""
        sid = sym.get("symbolId")
        if raw_name and sid is not None:
            # Store both the exact name and an uppercase stripped version for matching
            _symbol_id_cache[raw_name] = int(sid)
            _symbol_id_cache[raw_name.upper().replace(" ", "")] = int(sid)

    _symbols_loaded = True


def _get_symbol_id(ctrader_name: str) -> Optional[int]:
    """
    Resolve a cTrader symbol name to its numeric symbolId.
    Tries exact match first, then without .cash suffix, then partial match.
    """
    _load_symbols()

    key = ctrader_name.upper().replace(" ", "")

    # Exact
    if key in _symbol_id_cache:
        return _symbol_id_cache[key]

    # Strip .cash/.futures suffix
    base = key.split(".")[0]
    if base in _symbol_id_cache:
        return _symbol_id_cache[base]

    # Partial match — find any symbol whose name starts with or contains base
    for name, sid in _symbol_id_cache.items():
        if name.startswith(base) or base in name:
            return sid

    return None


def _pip_digits(ctrader_name: str, raw_sample: Optional[float] = None) -> int:
    """
    Return pip digits for price conversion (pipettes → display price).
    If raw_sample is provided, auto-detects the correct divisor using _PRICE_RANGES.
    Falls back to _PIP_DIGITS_HINT, then 5.
    """
    key = ctrader_name.upper().split(".")[0]

    # Use cached value if already detected
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]

    hint = _PIP_DIGITS_HINT.get(key, 5)

    # Auto-detect from a live raw price sample
    if raw_sample and raw_sample > 0:
        lo, hi = _PRICE_RANGES.get(key, (0, 0))
        if lo and hi:
            for digits in range(0, 9):
                display = raw_sample / (10 ** digits)
                if lo <= display <= hi:
                    _pip_digits_cache[key] = digits
                    return digits

    return hint


def _ts_to_utc(raw: int) -> datetime:
    """Convert raw cTrader timestamp (ms, s, or minutes) to UTC datetime."""
    if raw > 1_000_000_000_000:     # milliseconds
        ts = raw / 1000
    elif raw > 1_000_000_000:       # seconds
        ts = float(raw)
    else:                           # minutes (cTrader raw protocol)
        ts = raw * 60.0
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# Hours per bar for each period — used to compute fromTimestamp
_HOURS_PER_BAR: dict[str, float] = {
    "M_1": 1/60, "M_5": 5/60, "M_15": 15/60, "M_30": 0.5,
    "H_1": 1.0,  "H_4": 4.0,  "D_1":  24.0,  "W_1":  168.0,
}
# API hard cap: toTimestamp - fromTimestamp must be ≤ 720h
_MAX_RANGE_HOURS = 720.0


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch historical OHLCV candles from cTrader Remote MCP.

    symbol: cTrader symbol name (e.g. 'EURUSD', 'US500', 'XAUUSD')
    interval: '1h', '4h', '1d', etc.
    limit: number of candles to return
    """
    period = _PERIOD_MAP.get(interval)
    if not period:
        return []

    symbol_id = _get_symbol_id(symbol)
    if symbol_id is None:
        return []

    # Build time range — API requires fromTimestamp + toTimestamp (not count alone)
    hours = _HOURS_PER_BAR.get(period, 1.0) * limit
    hours = min(hours, _MAX_RANGE_HOURS)  # hard cap: API rejects > 720h ranges
    to_ts   = datetime.now(tz=timezone.utc)
    from_ts = to_ts - timedelta(hours=hours)

    result = _call_tool("get_trendbars", {
        "symbolId":      symbol_id,
        "period":        period,
        "fromTimestamp": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toTimestamp":   to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    if not result:
        return []

    # Response key varies by MCP version — try all known variants
    bars = (
        result.get("trendbars")
        or result.get("trendBars")
        or result.get("bars")
        or result.get("data")
        or []
    )
    if not bars:
        return []

    # Auto-detect pip digits from the first bar's close (calibrates once per session)
    first_raw_close = bars[0].get("close", 0) if bars else 0
    pip_div = 10 ** _pip_digits(symbol, raw_sample=first_raw_close)
    label   = symbol_label or symbol
    candles: List[Candle] = []

    for bar in bars:
        try:
            ts_raw = (
                bar.get("utcTimestamp")
                or bar.get("timestamp")
                or bar.get("utcTimestampInMinutes")
                or bar.get("time")
                or 0
            )
            ts = _ts_to_utc(int(ts_raw))

            o = bar.get("open",  0) / pip_div
            h = bar.get("high",  0) / pip_div
            l = bar.get("low",   0) / pip_div
            c = bar.get("close", 0) / pip_div
            v = float(bar.get("tickVolume") or bar.get("volume") or 0)

            if not (l > 0 and h >= l and o >= l and c >= l):
                continue

            candles.append(Candle(
                timestamp=ts,
                open=o, high=h, low=l, close=c,
                volume=v,
                timeframe=interval,
                symbol=label,
                data_tier=1,   # Tier 1 — direct broker feed
            ))
        except (KeyError, TypeError, ValueError, OSError):
            continue

    candles.sort(key=lambda c: c.timestamp)
    return candles[-limit:]


def fetch_current_price(symbol: str) -> Optional[float]:
    """Return current mid price (bid+ask)/2 for a cTrader symbol."""
    symbol_id = _get_symbol_id(symbol)
    if symbol_id is None:
        return None

    result = _call_tool("get_spot_prices", {"symbolIds": [symbol_id]})
    if not result:
        return None

    prices = result.get("prices") or result.get("spotPrices") or []
    if not prices:
        return None

    raw_bid = prices[0].get("bid", 0)
    pip_div = 10 ** _pip_digits(symbol, raw_sample=raw_bid or None)
    bid = raw_bid / pip_div
    ask = prices[0].get("ask", 0) / pip_div
    if bid > 0 and ask > 0:
        return (bid + ask) / 2
    return None
