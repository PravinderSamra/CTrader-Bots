"""
Direct HTTP client for the cTrader Remote MCP server.

Bypasses the `mcp__ctrader__*` Claude-tool session layer, which the other agents in
this repo have found to be unreliable (frequent "session expired" / "not connected"
errors — see ctrader-mcp-integration-guide.md, Lesson 1 and Lesson 6). This client
uses a persistent keep-alive HTTPS connection plus the documented MCP handshake
(`initialize` -> `notifications/initialized`), which the guide identifies as the
combination that actually works against the load-balanced MCP backend.

Usage:
    from ctrader_client import call_tool
    result = call_tool("get_trendbars", {"symbolId": 185, "period": "M_15",
                                          "fromTimestamp": "...", "toTimestamp": "..."})
"""

import http.client
import ssl
import json
import os
import time
from typing import Optional

_MCP_HOST = "mcp.ctrader.com"
_MCP_PATH = "/trading/mcp"

_TOKEN = os.environ.get(
    "CTRADER_MCP_TOKEN",
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0",
)

_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(_MCP_HOST, context=ssl.create_default_context(), timeout=30)
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
            new_sid = resp.getheader("Mcp-Session-Id") or resp.getheader("mcp-session-id") or session_id
            raw = resp.read().decode()

            if resp.status == 404:
                return {"_session_expired": True}, None
            if resp.status >= 500:
                raise ConnectionError(f"HTTP {resp.status}")

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
            if attempt == 1:
                return None, session_id
            time.sleep(1.5)

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
            "clientInfo": {"name": "rsi-adx-scanner", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        # REQUIRED — completes the MCP handshake; some tools silently fail without it
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def call_tool(tool: str, arguments: dict, retries: int = 2) -> Optional[dict]:
    """Call an MCP tool and return its parsed JSON result, or None on failure."""
    global _session_id

    for outer_attempt in range(retries + 1):
        if not _ensure_session():
            time.sleep(2 * (outer_attempt + 1))
            continue

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
            "id": 1,
        }
        data, new_sid = _post(payload, _session_id)

        expired = (
            (data and data.get("_session_expired"))
            or (data and "error" in data and "session" in data.get("error", {}).get("message", "").lower())
        )
        if expired:
            _session_id = None
            continue

        if new_sid:
            _session_id = new_sid

        if not data or "result" not in data:
            time.sleep(2 * (outer_attempt + 1))
            continue

        content = data["result"].get("content", [])
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except (json.JSONDecodeError, KeyError):
                return None
        return None

    return None


def close():
    global _conn
    try:
        if _conn:
            _conn.close()
    except Exception:
        pass
    _conn = None


if __name__ == "__main__":
    # Smoke test
    bal = call_tool("get_balance", {})
    print(json.dumps(bal, indent=2))
