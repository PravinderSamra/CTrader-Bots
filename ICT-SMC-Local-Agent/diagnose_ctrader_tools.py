"""
cTrader Local MCP — full protocol diagnostic.

diagnose_ctrader.py only checks the "initialize" handshake. This script
goes further: it completes the handshake on a single persistent connection
(required for session affinity), then calls "tools/list" to print every
tool name the Local MCP server actually exposes, and finally calls
"tools/call" for "get_symbols" (the tool ctrader_fetcher.py assumes exists)
so we can see its raw response.

Usage:
    python diagnose_ctrader_tools.py
"""

import os
import json
import http.client
import ssl
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

mcp_url = os.environ.get("CTRADER_MCP_URL")
token = os.environ.get("CTRADER_MCP_TOKEN")

print(f"CTRADER_MCP_URL   = {mcp_url!r}")
print(f"CTRADER_MCP_TOKEN = {'<set>' if token else '<empty>'}\n")

if not mcp_url:
    print("CTRADER_MCP_URL is not set in .env — nothing to test.")
    raise SystemExit(1)

parsed = urlparse(mcp_url)
host = parsed.hostname
port = parsed.port or (80 if parsed.scheme == "http" else 443)
path = parsed.path or "/"
secure = parsed.scheme != "http"

if secure:
    conn = http.client.HTTPSConnection(host, port, context=ssl.create_default_context(), timeout=20)
else:
    conn = http.client.HTTPConnection(host, port, timeout=20)


def post(payload, session_id=None):
    headers = {
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    conn.request("POST", path, json.dumps(payload), headers)
    resp = conn.getresponse()
    sid = resp.getheader("Mcp-Session-Id") or resp.getheader("mcp-session-id") or session_id
    raw = resp.read().decode()

    print(f"--- {payload.get('method')} ---")
    print(f"status: {resp.status}   session: {sid}")
    print(raw[:4000])
    print()

    try:
        return json.loads(raw), sid
    except json.JSONDecodeError:
        return None, sid


# 1) initialize
data, sid = post({
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "diagnostic", "version": "1.0"},
    },
    "id": 0,
})

if not (data and "result" in data and sid):
    print("Handshake failed — stopping here.")
    raise SystemExit(1)

# 2) notifications/initialized
post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)

# 3) tools/list — shows every tool name this server actually exposes
post({"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}, sid)

# 4) tools/call get_symbols — the tool ctrader_fetcher.py expects for symbol lookup
post({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "get_symbols", "arguments": {}},
    "id": 2,
}, sid)
