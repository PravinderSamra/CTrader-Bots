"""
cTrader MCP client — persistent keep-alive HTTP, per the repo integration guide.

Uses direct HTTPS (http.client) rather than the injected mcp__ctrader__* Claude
tools, which the guide documents as session-flaky. Keep-alive keeps every request
on the same load-balanced backend so the MCP session survives.

Exposes: get_trendbars_range(), fetch_ohlcv_window(), get_symbols().
"""
import http.client
import ssl
import json
import os
import time
from datetime import datetime, timezone, timedelta
from typing import Optional

_MCP_HOST = "mcp.ctrader.com"
_MCP_PATH = "/trading/mcp"

# Token slug: prefer the live env var used by .mcp.json; fall back to legacy names.
_TOKEN = (
    os.environ.get("CTRADER_MCP_SLUG")
    or os.environ.get("CTRADER_MCP_TOKEN")
    or "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            _MCP_HOST, context=ssl.create_default_context(), timeout=30
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None):
    global _conn, _session_id
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
            new_sid = (
                resp.getheader("Mcp-Session-Id")
                or resp.getheader("mcp-session-id")
                or session_id
            )
            raw = resp.read().decode()
            if resp.status == 404:
                return {"_session_expired": True}, None
            for line in raw.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:]), new_sid
            # plain JSON (non-SSE) fallback
            if raw.strip().startswith("{"):
                return json.loads(raw), new_sid
            return None, session_id
        except Exception:
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
    global _session_id
    if _session_id:
        return True
    data, sid = _post({
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "gap-retrace-research", "version": "1.0"},
        },
        "id": 0,
    })
    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def _call_tool(tool: str, arguments: dict, retries: int = 3):
    global _session_id
    if not _ensure_session():
        return None
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
        "id": 1,
    }
    for attempt in range(retries):
        data, new_sid = _post(payload, _session_id)
        expired = (data and data.get("_session_expired")) or (
            data and "error" in data
            and "session" in str(data.get("error", {}).get("message", "")).lower()
        )
        if expired:
            _session_id = None
            if not _ensure_session():
                time.sleep(1.5 * (attempt + 1))
                continue
            data, new_sid = _post(payload, _session_id)
        if new_sid:
            _session_id = new_sid
        if data and "result" in data:
            content = data["result"].get("content", [])
            if content and content[0].get("type") == "text":
                try:
                    return json.loads(content[0]["text"])
                except (json.JSONDecodeError, KeyError):
                    return None
            return data["result"]
        time.sleep(1.5 * (attempt + 1))
    return None


def get_symbols():
    return _call_tool("get_symbols", {})


def get_trendbars_range(symbol_id: int, period: str, from_iso: str, to_iso: str):
    """Raw trendbars for a <=720h window. Returns list of raw bar dicts (pipette prices)."""
    result = _call_tool("get_trendbars", {
        "symbolId": symbol_id,
        "period": period,
        "fromTimestamp": from_iso,
        "toTimestamp": to_iso,
    })
    if not result:
        return []
    return result.get("trendbars") or result.get("trendBars") or result.get("bars") or []


def fetch_ohlcv_window(symbol_id: int, period: str, days_back: int, pip_div: float,
                       chunk_hours: int = 700, pause: float = 0.4):
    """
    Fetch OHLCV over `days_back` days using <=720h sliding windows (API hard limit).
    Returns bars sorted ascending with display prices. Dedupes on timestamp.
    """
    to_dt = datetime.now(tz=timezone.utc)
    from_target = to_dt - timedelta(days=days_back)
    seen = {}
    cursor_to = to_dt
    while cursor_to > from_target:
        cursor_from = max(from_target, cursor_to - timedelta(hours=chunk_hours))
        raw = get_trendbars_range(
            symbol_id, period,
            cursor_from.strftime("%Y-%m-%dT%H:%M:%SZ"),
            cursor_to.strftime("%Y-%m-%dT%H:%M:%SZ"),
        )
        for b in raw:
            ts = b.get("timestamp")
            if ts is None:
                continue
            seen[ts] = {
                "timestamp": ts,
                "time": datetime.fromtimestamp(ts / 1000, tz=timezone.utc).isoformat(),
                "open": b["open"] / pip_div,
                "high": b["high"] / pip_div,
                "low": b["low"] / pip_div,
                "close": b["close"] / pip_div,
                "volume": b.get("tickVolume") or b.get("volume") or 0,
            }
        cursor_to = cursor_from
        time.sleep(pause)
    return [seen[k] for k in sorted(seen)]
