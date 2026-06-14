"""
cTrader Local MCP connection diagnostic.

ctrader_fetcher.py swallows connection errors silently (so the agent can fall
back to Yahoo/Twelve Data without crashing). This script makes the same
"initialize" call but prints the raw HTTP status, headers, and body — or the
exact exception — so connection problems are visible.

Usage:
    python diagnose_ctrader.py
"""

import os
import sys
import json
import http.client
import ssl
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()

mcp_url = os.environ.get("CTRADER_MCP_URL")
token = os.environ.get("CTRADER_MCP_TOKEN")

print(f"CTRADER_MCP_URL   = {mcp_url!r}")
print(f"CTRADER_MCP_TOKEN = {'<set>' if token else '<empty>'}")

if not mcp_url:
    print("\nCTRADER_MCP_URL is not set in .env — nothing to test.")
    sys.exit(1)

parsed = urlparse(mcp_url)
host = parsed.hostname
port = parsed.port or (80 if parsed.scheme == "http" else 443)
path = parsed.path or "/"
secure = parsed.scheme != "http"

print(f"\nConnecting to host={host} port={port} path={path!r} secure={secure} ...")

payload = {
    "jsonrpc": "2.0",
    "method": "initialize",
    "params": {
        "protocolVersion": "2024-11-05",
        "capabilities": {},
        "clientInfo": {"name": "diagnostic", "version": "1.0"},
    },
    "id": 0,
}
body = json.dumps(payload)
headers = {
    "Accept": "application/json, text/event-stream",
    "Content-Type": "application/json",
}
if token:
    headers["Authorization"] = f"Bearer {token}"

try:
    if secure:
        conn = http.client.HTTPSConnection(host, port, context=ssl.create_default_context(), timeout=10)
    else:
        conn = http.client.HTTPConnection(host, port, timeout=10)

    conn.request("POST", path, body, headers)
    resp = conn.getresponse()

    print(f"\nHTTP status: {resp.status} {resp.reason}")
    print("Response headers:")
    for k, v in resp.getheaders():
        print(f"  {k}: {v}")

    raw = resp.read().decode(errors="replace")
    print("\nResponse body (first 2000 chars):")
    print(raw[:2000])

except Exception as e:
    print(f"\nConnection FAILED: {type(e).__name__}: {e}")
