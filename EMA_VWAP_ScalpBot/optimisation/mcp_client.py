"""
cTrader MCP HTTP client.
Uses persistent HTTPS connection (keep-alive) to avoid session-not-found errors
on the load-balanced MCP backend. Implements automatic session reinitialisation.

Adapted from: CTrader-Bots/ctrader-mcp-integration-guide.md
"""

import http.client
import ssl
import json
import os
from typing import Optional

from config import MCP_HOST, MCP_PATH, MCP_TOKEN

_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            MCP_HOST,
            context=ssl.create_default_context(),
            timeout=30,
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    global _conn, _session_id
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {MCP_TOKEN}",
        "Accept":        "application/json, text/event-stream",
        "Content-Type":  "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(3):
        try:
            conn = _get_conn()
            conn.request("POST", MCP_PATH, body, headers)
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

        except Exception as e:
            try:
                if _conn:
                    _conn.close()
            except Exception:
                pass
            _conn = None
            if attempt == 2:
                return None, session_id

    return None, session_id


def _ensure_session() -> bool:
    global _session_id
    if _session_id:
        return True

    data, sid = _post({
        "jsonrpc": "2.0",
        "method":  "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities":    {},
            "clientInfo":      {"name": "ema-vwap-wfo", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def call_tool(tool: str, arguments: dict) -> Optional[dict]:
    """Call a cTrader MCP tool. Returns parsed JSON result or None on failure."""
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

    expired = (
        (data and data.get("_session_expired")) or
        (data and "error" in data and "session" in str(data.get("error", {}).get("message", "")).lower())
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
