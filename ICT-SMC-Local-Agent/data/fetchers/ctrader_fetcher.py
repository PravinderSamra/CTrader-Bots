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

import http.client
import ssl
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
    # Forex majors
    "EURUSD":  "EURUSD",   "GBPUSD":  "GBPUSD",   "USDJPY":  "USDJPY",
    "USDCHF":  "USDCHF",   "USDCAD":  "USDCAD",   "AUDUSD":  "AUDUSD",
    "NZDUSD":  "NZDUSD",
    # Forex crosses
    "GBPJPY":  "GBPJPY",   "EURJPY":  "EURJPY",   "AUDJPY":  "AUDJPY",
    "EURGBP":  "EURGBP",   "GBPAUD":  "GBPAUD",   "EURCAD":  "EURCAD",
    "GBPCAD":  "GBPCAD",
    # US indices
    "SPX":     "US500",    "NDX":     "NAS100",   "US30":    "US30",
    # European indices
    "DAX":     "GER40",    "UK100":   "UK100",    "FRA40":   "FRA40",
    "EUSTX50": "EUSTX50",
    # Asia-Pacific indices
    "JPN225":  "JPN225",   "AUS200":  "AUS200",   "HK50":    "HK50",
    # Metals
    "GOLD":    "XAUUSD",   "SILVER":  "XAGUSD",
    # Commodities
    "OIL":     "WTOIL-PERP", "BRENT": "BRENTOIL-PERP", "NATGAS": "NatGas",
    # Crypto (via OKX, listed here for reference only)
    "BTCUSDT": "BTCUSD",   "ETHUSDT": "ETHUSD",   "SOLUSDT": "SOLUSD",
}

# Pip digits per cTrader symbol — raw pipette price / 10^pipDigits = display price
# e.g. EURUSD raw 116305 / 100000 = 1.16305
# get_symbols does not return pipDigits; we auto-detect from price ranges (see below)
# These are starting guesses; _pip_digits() corrects them via _PRICE_RANGES auto-detect.
_PIP_DIGITS_HINT: dict[str, int] = {
    # Forex majors
    "EURUSD": 5, "GBPUSD": 5, "AUDUSD": 5, "NZDUSD": 5,
    "USDCHF": 5, "USDCAD": 5,
    # JPY pairs (3 decimal places — 100s)
    "USDJPY": 3, "GBPJPY": 3, "EURJPY": 3, "AUDJPY": 3, "CADJPY": 3, "NZDJPY": 3,
    # EUR/GBP/AUD crosses
    "EURGBP": 5, "EURAUD": 5, "EURCAD": 5, "EURCHF": 5,
    "GBPAUD": 5, "GBPCAD": 5, "GBPNZD": 5, "GBPCHF": 5,
    "AUDCAD": 5, "AUDCHF": 5, "AUDNZD": 5, "NZDCAD": 5, "NZDCHF": 5,
    # Metals
    "XAUUSD": 3, "XAGUSD": 3, "XPTUSD": 3, "XPDUSD": 3,
    # US indices
    "US500":  3, "NAS100": 4, "US30":   4,
    # European indices
    "GER40":  3, "UK100":  3, "FRA40":  3, "EUSTX50": 3,
    # Asia-Pacific indices
    "JPN225": 2, "AUS200": 3, "HK50":   2,
    # Commodities
    "USOIL":  3, "UKOIL":  3, "WTOIL-PERP": 3, "BRENTOIL-PERP": 3,
    "NATGAS": 3,
    # Crypto
    "BTCUSD": 3, "ETHUSD": 3, "SOLUSD": 3,
}

# Plausible display-price ranges per symbol — used to auto-detect pip digits
# from a live raw value. Ranges are intentionally wide.
_PRICE_RANGES: dict[str, tuple[float, float]] = {
    # Forex majors
    "EURUSD": (0.80, 1.60),   "GBPUSD": (1.00, 1.70),
    "AUDUSD": (0.50, 1.10),   "NZDUSD": (0.40, 0.90),
    "USDCHF": (0.75, 1.20),   "USDCAD": (1.10, 1.65),
    # JPY pairs
    "USDJPY": (100, 180),     "GBPJPY": (150, 240),
    "EURJPY": (110, 180),     "AUDJPY": (60,  120),
    "CADJPY": (85,  130),     "NZDJPY": (55,  100),
    # EUR/GBP/AUD crosses
    "EURGBP": (0.70, 0.95),   "GBPAUD": (1.70, 2.30),
    "EURCAD": (1.30, 1.90),   "GBPCAD": (1.65, 2.20),
    "GBPNZD": (1.80, 2.50),   "EURAUD": (1.50, 1.80),
    # Metals
    "XAUUSD": (1_400, 8_000), "XAGUSD": (15, 200),
    "XPTUSD": (700, 2_000),   "XPDUSD": (700, 3_000),
    # US indices
    "US500":  (3_000, 12_000), "NAS100": (8_000, 30_000),
    "US30":   (25_000, 55_000),
    # European indices
    "GER40":  (12_000, 30_000), "UK100":  (6_000, 13_000),
    "FRA40":  (5_000, 12_000),  "EUSTX50": (3_000, 8_000),
    # Asia-Pacific indices (JPN225 range extended — Nikkei at 65k+ in 2026)
    "JPN225": (15_000, 100_000), "AUS200": (5_000, 12_000),
    "HK50":   (13_000, 35_000),
    # Commodities
    "USOIL":  (30, 130),      "UKOIL":  (30, 130),
    "WTOIL-PERP": (30, 130),  "BRENTOIL-PERP": (30, 140),
    "NATGAS": (1.0, 15.0),
    # Crypto
    "BTCUSD": (10_000, 250_000), "ETHUSD": (500, 15_000),
    "SOLUSD": (10, 600),
}

# Runtime pip-digits cache — populated on first successful candle fetch
_pip_digits_cache: dict[str, int] = {}

# ── Connection + Session State ─────────────────────────────────────────────────
# Persistent HTTPS connection for session affinity (load-balanced MCP server
# routes to the same instance when keep-alive is used; Connection:close causes 404s).
_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None
_symbol_id_cache: dict[str, int] = {}   # ctrader_symbol_name → symbolId
_symbols_loaded: bool = False


def _get_conn() -> http.client.HTTPSConnection:
    """Return (or create) the persistent HTTPS connection."""
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            "mcp.ctrader.com",
            context=ssl.create_default_context(),
            timeout=20,
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    """POST a JSON-RPC message over the persistent connection. Returns (parsed_data, session_id)."""
    global _conn, _session_id
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {_TOKEN}",
        "Accept":        "application/json, text/event-stream",
        "Content-Type":  "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(2):
        try:
            conn = _get_conn()
            conn.request("POST", "/trading/mcp", body, headers)
            resp = conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id")
                       or session_id)
            raw = resp.read().decode()

            if resp.status == 404:
                return {"_session_expired": True}, None

            for line in raw.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:]), new_sid

            return None, session_id

        except Exception:
            # Connection dropped — reset and retry once on a fresh connection
            try:
                if _conn:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 1:
                return None, session_id

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
        # Complete the MCP handshake
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
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

    # Expired or lost session — reset and retry once
    expired = (
        (data and data.get("_session_expired")) or
        (data and "error" in data and "session" in data["error"].get("message", "").lower())
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


def _strip_suffix(name: str) -> str:
    """Remove broker/account suffixes for dict lookups. US30_SB -> US30, XAUUSD-F -> XAUUSD."""
    for suffix in ("_SBE", "_SB", "-F_SB", "-F"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _load_symbols() -> None:
    """Fetch and cache ENABLED symbols (called once per session)."""
    global _symbols_loaded
    if _symbols_loaded:
        return

    result = _call_tool("get_symbols", {})
    if not result:
        return

    for sym in result.get("symbols", []):
        if not sym.get("enabled", False):
            continue   # only cache tradeable symbols
        raw_name = sym.get("name") or sym.get("symbolName") or ""
        sid = sym.get("symbolId")
        if raw_name and sid is not None:
            sid_int = int(sid)
            # Exact name
            _symbol_id_cache[raw_name.upper()] = sid_int
            # Stripped name (US30_SB → US30) for broker-agnostic lookups
            base = _strip_suffix(raw_name.upper())
            if base != raw_name.upper():
                _symbol_id_cache.setdefault(base, sid_int)

    _symbols_loaded = True


def _get_symbol_id(ctrader_name: str) -> Optional[int]:
    """
    Resolve a cTrader symbol name to its numeric symbolId (enabled symbols only).
    Tries exact match, then suffix-stripped, then partial match.
    """
    _load_symbols()

    key = ctrader_name.upper().replace(" ", "").split(".")[0]

    # Exact match
    if key in _symbol_id_cache:
        return _symbol_id_cache[key]

    # Suffix-stripped (handles _SB variants pre-populated by _load_symbols)
    base = _strip_suffix(key)
    if base in _symbol_id_cache:
        return _symbol_id_cache[base]

    # Partial match — find any enabled symbol whose base name starts with key
    for name, sid in _symbol_id_cache.items():
        name_base = _strip_suffix(name)
        if name_base == base or name_base.startswith(base) or base.startswith(name_base):
            return sid

    return None


def _pip_digits(ctrader_name: str, raw_sample: Optional[float] = None) -> int:
    """
    Return pip digits for price conversion (pipettes → display price).
    If raw_sample is provided, auto-detects the correct divisor using _PRICE_RANGES.
    Falls back to _PIP_DIGITS_HINT, then 5.
    """
    key = _strip_suffix(ctrader_name.upper().split(".")[0])

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

    result = _call_tool("get_spot_prices", {"symbolId": [symbol_id]})
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
