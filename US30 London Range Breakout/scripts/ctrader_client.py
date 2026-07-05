"""
cTrader MCP client — direct HTTPS with keep-alive session.

The injected mcp__ctrader__* tools expire frequently; this module talks to the
MCP endpoint directly over a persistent connection with re-init on 404, as
recommended in ../../ctrader-mcp-integration-guide.md (Lesson 1 & 6).

Auth: reads the base64url slug from env CTRADER_MCP_SLUG.
"""
import http.client
import ssl
import json
import os
import time
from typing import Optional

_HOST = "mcp.ctrader.com"
_PATH = "/trading/mcp"
_TOKEN = os.environ.get("CTRADER_MCP_SLUG") or os.environ.get("CTRADER_MCP_TOKEN")

_conn: Optional[http.client.HTTPSConnection] = None
_sid: Optional[str] = None

# Confirmed enabled symbol ids on this Pepperstone UK GBP spread-bet demo account.
SYMBOLS = {"US30": 219, "NAS100": 205, "US500": 220}


def _post(payload: dict, session_id: Optional[str] = None):
    global _conn
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {_TOKEN}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id
    for attempt in range(3):
        try:
            if _conn is None:
                _conn = http.client.HTTPSConnection(
                    _HOST, context=ssl.create_default_context(), timeout=30
                )
            _conn.request("POST", _PATH, body, headers)
            resp = _conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id") or session_id)
            raw = resp.read().decode()
            if resp.status == 404:
                return {"_expired": True}, None
            for line in raw.split("\n"):
                if line.startswith("data: "):
                    return json.loads(line[6:]), new_sid
            return None, session_id
        except Exception:
            try:
                if _conn:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 2:
                return None, session_id
            time.sleep(1.5 * (attempt + 1))
    return None, session_id


def _ensure_session() -> bool:
    global _sid
    if _sid:
        return True
    data, sid = _post({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                   "clientInfo": {"name": "lrb-research", "version": "1.0"}},
        "id": 0,
    })
    if data and "result" in data and sid:
        _sid = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def call_tool(tool: str, arguments: dict, retries: int = 4):
    """Call an MCP tool, returning the parsed JSON payload (or None)."""
    global _sid
    for attempt in range(retries):
        if not _ensure_session():
            time.sleep(2 * (attempt + 1))
            continue
        data, nsid = _post({
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": tool, "arguments": arguments}, "id": 1,
        }, _sid)
        if data and data.get("_expired"):
            _sid = None
            continue
        if nsid:
            _sid = nsid
        if data and "result" in data:
            content = data["result"].get("content", [])
            if content and content[0].get("type") == "text":
                try:
                    return json.loads(content[0]["text"])
                except (json.JSONDecodeError, KeyError):
                    return content[0]["text"]
            return data["result"]
        # transient miss — brief backoff and retry
        time.sleep(1.5 * (attempt + 1))
    return None


def get_trendbars(symbol_id: int, period: str, from_iso: str, to_iso: str):
    """Range-mode fetch (the only mode this server supports). <=100 bars/call."""
    r = call_tool("get_trendbars", {
        "symbolId": symbol_id, "period": period,
        "fromTimestamp": from_iso, "toTimestamp": to_iso,
    })
    if isinstance(r, dict):
        return r.get("trendbars") or r.get("trendBars") or r.get("bars") or []
    return []
