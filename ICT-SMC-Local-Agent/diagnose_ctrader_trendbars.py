"""
cTrader Local MCP — trendbar shape + index/commodity symbol diagnostic.

diagnose_ctrader_data.py revealed the correct .cash/.c symbol names for
indices/commodities and the get_spot_prices/get_symbol_details field
names, but get_trendbars for EURUSD returned an empty "bars" list
(markets closed — Sunday) before any bar fields could be seen.

This script:

  1. get_trendbars for BTCUSD (m15, last 5h, limit 5) — crypto trades
     24/7, so this should return real bars even on a weekend, revealing
     the bar field names (open/high/low/close/timestamp/volume etc.).
  2. get_trendbars for EURUSD (h1, last 5 days, limit 5) — covers
     Friday's session, as a cross-check on the bar shape for forex.
  3. get_symbol_details + get_spot_prices for the corrected index/
     commodity names (US500.cash, US100.cash, US30.cash, GER40.cash,
     UK100.cash, FRA40.cash, EU50.cash, JP225.cash, AUS200.cash,
     HK50.cash, USOIL.cash, UKOIL.cash, NATGAS.cash) — to confirm they
     resolve and to get digits/pipSize for each.

Usage:
    python diagnose_ctrader_trendbars.py
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
        print(f"  [{name} {arguments}] ERROR: {data}")
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

to_ts = datetime.now(tz=timezone.utc)

# 1) BTCUSD trendbars (24/7 market — should have data even on weekends)
from_ts = to_ts - timedelta(hours=5)
print("=== get_trendbars: BTCUSD m15 (last 5h) ===")
result, sid = call_tool("get_trendbars", {
    "symbolName": "BTCUSD",
    "timeframe": "m15",
    "from": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "to": to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "limit": 5,
}, sid)
print(json.dumps(result, indent=2))

# 2) EURUSD trendbars over last 5 days (covers Friday's session)
from_ts = to_ts - timedelta(days=5)
print("\n=== get_trendbars: EURUSD h1 (last 5 days) ===")
result, sid = call_tool("get_trendbars", {
    "symbolName": "EURUSD",
    "timeframe": "h1",
    "from": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "to": to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "limit": 5,
}, sid)
print(json.dumps(result, indent=2))

# 3) Corrected index/commodity symbol names — confirm details + spot prices
symbols = [
    "US500.cash", "US100.cash", "US30.cash", "GER40.cash", "UK100.cash",
    "FRA40.cash", "EU50.cash", "JP225.cash", "AUS200.cash", "HK50.cash",
    "USOIL.cash", "UKOIL.cash", "NATGAS.cash",
]
print("\n=== get_symbol_details + get_spot_prices for index/commodity symbols ===")
for name in symbols:
    details, sid = call_tool("get_symbol_details", {"symbolName": name}, sid)
    spot, sid = call_tool("get_spot_prices", {"symbolName": name}, sid)
    if details:
        print(f"{name}: digits={details.get('digits')} pipSize={details.get('pipSize')} "
              f"lotSize={details.get('lotSize')} minVolume={details.get('minVolume')}")
    else:
        print(f"{name}: get_symbol_details FAILED")
    if spot:
        print(f"  spot: bid={spot.get('bid')} ask={spot.get('ask')}")
    else:
        print(f"  spot: get_spot_prices FAILED")
