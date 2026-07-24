"""
ctrader_http.py — read-only cTrader MCP data client over a persistent HTTPS
keep-alive connection. Phone-safe: uses direct HTTP (NOT the mcp__ctrader__*
injected Claude tools, which expire on iPhone/browser — see the repo's
ctrader-mcp-integration-guide.md, Lesson 6).

READ ONLY. This module deliberately exposes no order-placement functions — the
skill produces trade *ideas*, it does not execute.

Auth: set CTRADER_MCP_TOKEN to your account's bearer token. The stale demo
token is NOT bundled — without a valid token every tool call returns a clear
auth error that analyze.py surfaces to you (instead of a silent None).

Endpoint / field shapes are documented in ctrader-mcp-integration-guide.md.
"""

import http.client
import ssl
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

_MCP_HOST = "mcp.ctrader.com"
_MCP_PATH = "/trading/mcp"

_TOKEN = os.environ.get("CTRADER_MCP_TOKEN", "").strip()

_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None
_last_error: Optional[str] = None   # human-readable reason the last call failed


def last_error() -> Optional[str]:
    return _last_error


class CTraderAuthError(RuntimeError):
    pass


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            _MCP_HOST, context=ssl.create_default_context(), timeout=25
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None):
    """Returns (parsed_json_or_None, session_id, http_status)."""
    global _conn
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {_TOKEN}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(2):
        try:
            conn = _get_conn()
            conn.request("POST", _MCP_PATH, body, headers)
            resp = conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id") or session_id)
            raw = resp.read().decode()
            status = resp.status
            if status == 404:
                return {"_session_expired": True}, None, status
            parsed = None
            for line in raw.split("\n"):
                if line.startswith("data: "):
                    parsed = json.loads(line[6:])
                    break
            if parsed is None and raw.strip():
                # non-SSE body (often an error envelope like 401)
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError:
                    parsed = {"_raw": raw[:300]}
            return parsed, new_sid, status
        except Exception as exc:  # dropped connection — reset + retry once
            try:
                if _conn:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 1:
                return {"_transport_error": str(exc)}, session_id, 0
    return None, session_id, 0


def _ensure_session() -> bool:
    global _session_id, _last_error
    if not _TOKEN:
        _last_error = ("CTRADER_MCP_TOKEN is not set. Export your cTrader bearer "
                       "token before running (see SKILL.md §Setup).")
        return False
    if _session_id:
        return True
    data, sid, status = _post({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "liquidity-phone", "version": "1.0"}},
        "id": 0,
    })
    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized",
               "params": {}}, sid)
        return True
    _last_error = f"MCP initialize failed (status {status}): {str(data)[:200]}"
    return False


def _call_tool(tool: str, arguments: dict) -> Optional[dict]:
    global _session_id, _last_error
    if not _ensure_session():
        return None
    payload = {"jsonrpc": "2.0", "method": "tools/call",
               "params": {"name": tool, "arguments": arguments}, "id": 1}
    data, new_sid, status = _post(payload, _session_id)

    expired = (data and data.get("_session_expired")) or (
        data and "error" in data
        and "session" in str(data.get("error", {}).get("message", "")).lower())
    if expired:
        _session_id = None
        if not _ensure_session():
            return None
        data, new_sid, status = _post(payload, _session_id)
    if new_sid:
        _session_id = new_sid

    if not data:
        _last_error = f"{tool}: empty response (status {status})"
        return None
    if status == 401 or (isinstance(data, dict) and "error" in data
                         and "auth" in str(data.get("error", {})).lower()):
        _last_error = (f"{tool}: auth failed (status {status}). Your "
                       f"CTRADER_MCP_TOKEN is invalid or expired: "
                       f"{str(data.get('error', data))[:160]}")
        return None
    if "result" not in data:
        _last_error = f"{tool}: no result ({str(data)[:200]})"
        return None

    content = data["result"].get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            _last_error = f"{tool}: unparseable content"
            return None
    return data["result"]


# ── symbol resolution (enabled symbols only; strips _SB / -F suffixes) ────────
_symbol_id_cache: dict = {}
_pip_digits_cache: dict = {}
_symbols_loaded = False

_PRICE_RANGES = {
    "EURUSD": (0.80, 1.60), "GBPUSD": (1.00, 1.70), "AUDUSD": (0.50, 1.10),
    "NZDUSD": (0.40, 0.90), "USDCHF": (0.75, 1.20), "USDCAD": (1.10, 1.65),
    "USDJPY": (100, 200), "GBPJPY": (150, 260), "EURJPY": (110, 190),
    "AUDJPY": (60, 130), "EURGBP": (0.70, 0.95), "GBPAUD": (1.60, 2.30),
    "XAUUSD": (1400, 8000), "XAGUSD": (15, 200), "US500": (3000, 12000),
    "NAS100": (8000, 35000), "US30": (25000, 60000), "GER40": (12000, 30000),
    "UK100": (6000, 13000), "FRA40": (5000, 12000), "EUSTX50": (3000, 8000),
    "JPN225": (15000, 100000), "AUS200": (5000, 12000), "HK50": (13000, 35000),
    "CRUDE": (30, 130), "BRENT": (30, 140), "NATGAS": (1.0, 20.0),
}


def _strip_suffix(name: str) -> str:
    for suffix in ("_SBE", "-F_SB", "_SB", "-F"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _load_symbols() -> None:
    global _symbols_loaded
    if _symbols_loaded:
        return
    result = _call_tool("get_symbols", {})
    if not result:
        return
    for sym in result.get("symbols", []):
        if not sym.get("enabled", False):
            continue
        raw = (sym.get("symbolName") or "").upper()
        sid = sym.get("symbolId")
        if raw and sid is not None:
            _symbol_id_cache[raw] = int(sid)
            base = _strip_suffix(raw)
            if base != raw:
                _symbol_id_cache.setdefault(base, int(sid))
    _symbols_loaded = True


def get_symbol_id(instrument: str) -> Optional[int]:
    _load_symbols()
    key = instrument.upper().split(".")[0]
    if key in _symbol_id_cache:
        return _symbol_id_cache[key]
    base = _strip_suffix(key)
    if base in _symbol_id_cache:
        return _symbol_id_cache[base]
    for name, sid in _symbol_id_cache.items():
        if _strip_suffix(name) == base:
            return sid
    return None


def detect_pip_digits(symbol_base: str, raw_price: float) -> int:
    key = _strip_suffix(symbol_base.upper())
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]
    lo, hi = _PRICE_RANGES.get(key, (0, 0))
    if lo and hi and raw_price > 0:
        for n in range(0, 10):
            if lo <= raw_price / (10 ** n) <= hi:
                _pip_digits_cache[key] = n
                return n
    return 5


# ── public read-only fetchers ────────────────────────────────────────────────
def fetch_ohlcv(instrument: str, period: str = "H_1", hours_back: int = 100) -> list:
    """OHLCV candles (oldest→newest). period in
    M_1 M_5 M_15 M_30 H_1 H_4 D_1 W_1. Each dict: time, open, high, low,
    close, volume. Returns [] on failure (see last_error())."""
    sym_id = get_symbol_id(instrument)
    if sym_id is None:
        return []
    to_dt = datetime.now(tz=timezone.utc)
    from_dt = to_dt - timedelta(hours=min(hours_back, 720))
    result = _call_tool("get_trendbars", {
        "symbolId": sym_id, "period": period,
        "fromTimestamp": from_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toTimestamp": to_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    if not result:
        return []
    bars = (result.get("trendbars") or result.get("trendBars")
            or result.get("bars") or [])
    if not bars:
        return []
    base = _strip_suffix(instrument.upper())
    pip_div = 10 ** detect_pip_digits(base, bars[0].get("close", 1))
    out = []
    for b in bars:
        try:
            ts = b.get("timestamp") or b.get("time")
            out.append({
                "time": datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                "open": b["open"] / pip_div, "high": b["high"] / pip_div,
                "low": b["low"] / pip_div, "close": b["close"] / pip_div,
                "volume": b.get("tickVolume") or b.get("volume") or 0,
            })
        except (KeyError, TypeError, ZeroDivisionError):
            continue
    out.sort(key=lambda c: c["time"])
    return out


def get_live_price(instrument: str):
    """Returns (bid, ask) display price, or None."""
    sym_id = get_symbol_id(instrument)
    if sym_id is None:
        return None
    result = _call_tool("get_spot_prices", {"symbolId": [sym_id]})
    if not result or not result.get("prices"):
        return None
    p = result["prices"][0]
    raw_bid = p.get("bid", 0)
    if not raw_bid:
        return None
    pip_div = 10 ** detect_pip_digits(_strip_suffix(instrument.upper()), raw_bid)
    return (raw_bid / pip_div, p.get("ask", raw_bid) / pip_div)


def get_open_positions(instrument: Optional[str] = None) -> list:
    """Open positions (entry/SL/TP already in display price). Optional filter
    by instrument symbolId."""
    result = _call_tool("get_positions", {})
    if not result:
        return []
    positions = result.get("positions", [])
    if instrument:
        sid = get_symbol_id(instrument)
        positions = [p for p in positions if p.get("symbolId") == sid]
    return positions
