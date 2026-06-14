"""
cTrader Local MCP — tool schema diagnostic (full, untruncated).

diagnose_ctrader_tools.py showed get_symbols works but its entries have
no "symbolId"/"enabled" fields, which ctrader_fetcher.py currently
requires, and its tools/list output was truncated before showing the
candle/price tools. This script prints:

  1. Every tool name the server exposes (short list, won't truncate).
  2. The full description + input schema for any tool whose name or
     description mentions price/candle/bar/chart/quote/history/symbol/tick.
  3. The full set of keys present across get_symbols entries, plus a
     sample entry and the EURUSD entry (to see its actual shape).

Usage:
    python diagnose_ctrader_schema.py
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
    try:
        return json.loads(raw), sid
    except json.JSONDecodeError:
        return None, sid


# Handshake
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
    print("Handshake failed:", data)
    raise SystemExit(1)

post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)

# tools/list
data, sid = post({"jsonrpc": "2.0", "method": "tools/list", "params": {}, "id": 1}, sid)
tools = data["result"]["tools"]

print(f"=== {len(tools)} tools ===")
for t in tools:
    print(f"- {t['name']}")

print("\n=== Schemas for likely price/candle/symbol tools ===")
keywords = ("price", "candle", "bar", "chart", "quote", "history", "symbol", "tick", "trend")
for t in tools:
    name = t["name"].lower()
    desc = t.get("description", "").lower()
    if any(k in name or k in desc for k in keywords):
        print(f"\n--- {t['name']} ---")
        print(t.get("description", ""))
        print(json.dumps(t.get("inputSchema", {}), indent=2))

# get_symbols sample
print("\n=== get_symbols sample ===")
data, sid = post({
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {"name": "get_symbols", "arguments": {}},
    "id": 2,
}, sid)
content = data["result"]["content"][0]["text"]
symbols = json.loads(content)["symbols"]

print(f"total symbols: {len(symbols)}")
all_keys = set()
for s in symbols:
    all_keys |= set(s.keys())
print(f"keys present across all entries: {sorted(all_keys)}")

print("\nfirst entry:")
print(json.dumps(symbols[0], indent=2))

print("\nEURUSD entry:")
for s in symbols:
    if s.get("name") == "EURUSD":
        print(json.dumps(s, indent=2))
        break
