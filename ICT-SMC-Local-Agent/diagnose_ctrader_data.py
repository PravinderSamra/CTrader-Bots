"""
cTrader Local MCP — data shape diagnostic.

Gathers everything needed to rewrite ctrader_fetcher.py against the
Local MCP's real API (symbolName-based, not symbolId-based):

  1. get_symbols filtered for "cash"/"oil"/"gas"/"brent" — to find the
     correct symbol names for indices and commodities.
  2. get_symbol_details for EURUSD and XAUUSD — to see digits/pipSize/
     lotSize fields.
  3. get_trendbars for EURUSD (h1, last ~10 hours, limit 3) — to see the
     raw bar field names (open/high/low/close/timestamp/volume).
  4. get_spot_prices for EURUSD — to see the raw quote field names.

Usage:
    python diagnose_ctrader_data.py
"""

import os
import json
import http.client
import ssl
from datetime import datetime, timezone, timedelta
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


def call_tool(name, arguments, sid):
    data, sid = post({
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {"name": name, "arguments": arguments},
        "id": 99,
    }, sid)
    if not data or "result" not in data:
        print(f"  [{name}] ERROR: {data}")
        return None, sid
    content = data["result"].get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"]), sid
        except json.JSONDecodeError:
            print(f"  [{name}] non-JSON text: {content[0]['text'][:500]}")
            return None, sid
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

# 1) Find index / commodity symbol names
for kw in ("cash", "oil", "gas", "brent", "spot", "30", "500", "100", "225", "200", "40", "50"):
    result, sid = call_tool("get_symbols", {"filter": kw}, sid)
    if result:
        names = [s["name"] for s in result.get("symbols", [])]
        print(f"get_symbols(filter={kw!r}): {names}")

# 2) Symbol details
print("\n=== get_symbol_details: EURUSD ===")
result, sid = call_tool("get_symbol_details", {"symbolName": "EURUSD"}, sid)
print(json.dumps(result, indent=2))

print("\n=== get_symbol_details: XAUUSD ===")
result, sid = call_tool("get_symbol_details", {"symbolName": "XAUUSD"}, sid)
print(json.dumps(result, indent=2))

# 3) Trendbars
to_ts = datetime.now(tz=timezone.utc)
from_ts = to_ts - timedelta(hours=10)
print("\n=== get_trendbars: EURUSD h1 ===")
result, sid = call_tool("get_trendbars", {
    "symbolName": "EURUSD",
    "timeframe": "h1",
    "from": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "to": to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "limit": 3,
}, sid)
print(json.dumps(result, indent=2))

# 4) Spot prices
print("\n=== get_spot_prices: EURUSD ===")
result, sid = call_tool("get_spot_prices", {"symbolName": "EURUSD"}, sid)
print(json.dumps(result, indent=2))
