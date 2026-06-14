"""
cTrader Local MCP Fetcher — Tier 1 Data

Fetches exact CFD prices via the cTrader desktop app's Local MCP server
(http://127.0.0.1:<port>/mcp/, FTMO account — separate from the Remote
Agent's connection). Replaces Yahoo Finance (indices/oil) and Twelve Data
(forex/gold) with:
  - 24/7 CFD candles — no overnight market-hours gaps, no phantom FVGs
  - Exact broker price feed — matches your cTrader/TradingView chart
  - Candles marked data_tier=1 (direct broker feed, highest quality)

The Local MCP addresses everything by symbolName (e.g. "EURUSD",
"US500.cash") and returns plain decimal prices — no symbolId lookup and
no pipette/digit conversion required.

Configuration (set in your local, gitignored .env — NEVER commit these):
  CTRADER_MCP_URL   — Local MCP endpoint URL (e.g. http://127.0.0.1:9876/mcp/)
  CTRADER_MCP_TOKEN — bearer token (optional — leave unset for a local
                       cTrader desktop MCP server, which doesn't require one)

If CTRADER_MCP_URL is unset, all fetchers in this module no-op (return
None / []) and the agent falls back to Twelve Data / Yahoo for those
instruments.
"""

import http.client
import ssl
import json
import os
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from urllib.parse import urlparse
from data.models import Candle

# ── Config ────────────────────────────────────────────────────────────────────
# No hardcoded URL or token — both must come from the local .env file.
_MCP_URL = os.environ.get("CTRADER_MCP_URL")
_TOKEN   = os.environ.get("CTRADER_MCP_TOKEN")

if _MCP_URL:
    _parsed     = urlparse(_MCP_URL)
    _MCP_HOST   = _parsed.hostname or ""
    _MCP_PORT   = _parsed.port or (80 if _parsed.scheme == "http" else 443)
    _MCP_PATH   = _parsed.path or "/"
    _MCP_SECURE = _parsed.scheme != "http"
else:
    _MCP_HOST = _MCP_PORT = _MCP_PATH = _MCP_SECURE = None

# Our interval strings → cTrader Local MCP get_trendbars "timeframe" values
_PERIOD_MAP = {
    "1m": "m1", "5m": "m5", "15m": "m15", "30m": "m30",
    "1h": "h1", "4h": "h4", "1d": "d1", "1w": "w1",
}

# Calendar-day lookback window per timeframe — wide enough that the
# requested number of bars is available even across weekends/closures.
# get_trendbars(limit=N) returns the N most-recent bars within [from, to].
_RANGE_DAYS = {
    "m1": 2, "m5": 3, "m15": 5, "m30": 10,
    "h1": 20, "h4": 60, "d1": 60, "w1": 1460,
}

# ── Connection + Session State ─────────────────────────────────────────────────
# Persistent connection for session affinity (load-balanced MCP server
# routes to the same instance when keep-alive is used; Connection:close causes 404s).
_conn: Optional[http.client.HTTPConnection] = None
_session_id: Optional[str] = None


def _get_conn() -> http.client.HTTPConnection:
    """Return (or create) the persistent connection to the configured MCP endpoint."""
    global _conn
    if _conn is None:
        if _MCP_SECURE:
            _conn = http.client.HTTPSConnection(
                _MCP_HOST, _MCP_PORT,
                context=ssl.create_default_context(),
                timeout=20,
            )
        else:
            _conn = http.client.HTTPConnection(_MCP_HOST, _MCP_PORT, timeout=20)
    return _conn


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    """POST a JSON-RPC message over the persistent connection. Returns (parsed_data, session_id)."""
    global _conn, _session_id
    body = json.dumps(payload)
    headers = {
        "Accept":        "application/json, text/event-stream",
        "Content-Type":  "application/json",
    }
    if _TOKEN:
        headers["Authorization"] = f"Bearer {_TOKEN}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(2):
        try:
            conn = _get_conn()
            conn.request("POST", _MCP_PATH, body, headers)
            resp = conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id")
                       or session_id)
            raw = resp.read().decode()

            if resp.status == 404:
                return {"_session_expired": True}, None

            content_type = resp.getheader("Content-Type", "")
            if "application/json" in content_type:
                try:
                    return json.loads(raw), new_sid
                except json.JSONDecodeError:
                    return None, session_id

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

    if _MCP_URL is None:
        return None

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


def _parse_timestamp(raw: str) -> datetime:
    """Parse a cTrader trendbar timestamp ("2026-06-14T15:30:00Z") to a UTC datetime."""
    return datetime.strptime(raw, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)


def fetch_klines(
    symbol: str,
    interval: str,
    limit: int = 200,
    symbol_label: Optional[str] = None,
) -> List[Candle]:
    """
    Fetch historical OHLCV candles from the cTrader Local MCP.

    symbol: cTrader symbolName (e.g. 'EURUSD', 'US500.cash', 'XAUUSD')
    interval: '1h', '4h', '1d', etc. (see _PERIOD_MAP)
    limit: number of most-recent candles to return
    """
    timeframe = _PERIOD_MAP.get(interval)
    if not timeframe:
        return []

    to_ts = datetime.now(tz=timezone.utc)
    from_ts = to_ts - timedelta(days=_RANGE_DAYS.get(timeframe, 30))

    result = _call_tool("get_trendbars", {
        "symbolName": symbol,
        "timeframe":  timeframe,
        "from":       from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "to":         to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "limit":      limit,
    })

    if not result:
        return []

    bars = result.get("bars") or []
    if not bars:
        return []

    label = symbol_label or symbol
    candles: List[Candle] = []

    for bar in bars:
        try:
            ts = _parse_timestamp(bar["timestamp"])
            o = float(bar["open"])
            h = float(bar["high"])
            l = float(bar["low"])
            c = float(bar["close"])
            v = float(bar.get("volume", 0))

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
        except (KeyError, TypeError, ValueError):
            continue

    candles.sort(key=lambda c: c.timestamp)
    return candles[-limit:]


def fetch_current_price(symbol: str) -> Optional[float]:
    """Return current mid price (bid+ask)/2 for a cTrader symbol, or None if unavailable."""
    result = _call_tool("get_spot_prices", {"symbolName": symbol})
    if not result:
        return None

    bid = result.get("bid")
    ask = result.get("ask")
    if bid and ask:
        return (bid + ask) / 2
    return None
