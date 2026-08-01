#!/usr/bin/env python3
"""
cTrader MCP client over direct HTTPS, with trendbar paging.

Reuses the connection pattern proven in ICT-SMC-Local-Agent/ctrader_http_fetch.py
(see ctrader-mcp-integration-guide.md, Lesson 1): a single keep-alive
HTTPSConnection so every request lands on the same load-balanced backend.
Using Connection: close causes ~60% "session not found" 404s.

Adds the one thing the other fetchers do ad hoc: generic backwards paging around
the server's silent 100-bar response cap, so callers can ask for an arbitrary
window of M1 bars and get all of them.

Auth: CTRADER_MCP_SLUG (preferred) or CTRADER_MCP_TOKEN.
"""

from __future__ import annotations

import http.client
import json
import os
import ssl
import sys
import time
from datetime import datetime, timezone
from urllib.parse import urlparse

_HOST = "mcp.ctrader.com"
_PATH = "/trading/mcp"

# The server silently truncates a trendbar response to the most recent N bars of
# the requested window. Measured at exactly 100 on 2026-08-01 against
# pepperstoneuk/demo. Paging assumes this value; if the broker raises it the
# paging still works, it just does more requests than strictly necessary.
BAR_CAP = 100

PERIOD_MS = {
    "M_1": 60_000,
    "M_5": 300_000,
    "M_15": 900_000,
    "M_30": 1_800_000,
    "H_1": 3_600_000,
    "H_4": 14_400_000,
    "D_1": 86_400_000,
}

# cTrader quotes prices in pipettes; every symbol on this account is pipDigits=5.
PIPETTE = 10 ** 5


class CTraderError(RuntimeError):
    pass


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    for ca in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if ca and os.path.exists(ca):
            try:
                ctx.load_verify_locations(ca)
            except Exception:
                pass
    return ctx


def _token() -> str:
    tok = (os.environ.get("CTRADER_MCP_SLUG") or os.environ.get("CTRADER_MCP_TOKEN") or "").strip()
    if not tok:
        raise CTraderError(
            "Neither CTRADER_MCP_SLUG nor CTRADER_MCP_TOKEN is set. "
            "Build the slug per ctrader-mcp-integration-guide.md."
        )
    return tok


class CTraderClient:
    def __init__(self, token: str | None = None, timeout: int = 30):
        self.token = token or _token()
        self.sid: str | None = None
        ctx = _ssl_ctx()
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            p = urlparse(proxy)
            self.conn = http.client.HTTPSConnection(
                p.hostname, p.port or 443, context=ctx, timeout=timeout
            )
            self.conn.set_tunnel(_HOST, 443)
        else:
            self.conn = http.client.HTTPSConnection(_HOST, 443, context=ctx, timeout=timeout)
        self._init()

    # ---------------------------------------------------------------- transport

    def _post(self, payload: dict) -> dict | None:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid

        for attempt in range(2):
            try:
                self.conn.request("POST", _PATH, json.dumps(payload), headers)
                r = self.conn.getresponse()
                ns = r.getheader("Mcp-Session-Id") or r.getheader("mcp-session-id")
                if ns:
                    self.sid = ns
                body = r.read().decode()
                if r.status == 401:
                    raise CTraderError("HTTP 401 — token unauthorised or expired (not retryable).")
                # SSE framing: rejoin all data: lines within one event.
                for event in body.split("\n\n"):
                    lines = [l[5:].lstrip() for l in event.splitlines() if l.startswith("data:")]
                    if lines:
                        try:
                            return json.loads("\n".join(lines))
                        except Exception:
                            pass
                try:
                    return json.loads(body)
                except Exception:
                    return None
            except (http.client.HTTPException, OSError):
                if attempt == 0:
                    try:
                        self.conn.close()
                    except Exception:
                        pass
                    self.conn.connect()
                    continue
                raise
        return None

    def _init(self) -> None:
        d = self._post({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "gala-heatmap", "version": "1.0"},
            },
        })
        if not (d and d.get("result")):
            raise CTraderError(f"initialize handshake failed: {str(d)[:200]}")
        # Required — some tools silently fail without it.
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def call(self, name: str, args: dict) -> dict:
        d = self._post({
            "jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": args},
        })
        if d and d.get("error"):
            raise CTraderError(f"{name}: {d['error']}")
        content = ((d or {}).get("result") or {}).get("content") or []
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except Exception:
                raise CTraderError(f"{name}: unparseable response {content[0]['text'][:200]}")
        raise CTraderError(f"{name}: unexpected response shape {str(d)[:200]}")

    # ------------------------------------------------------------------- market

    def spot(self, symbol_ids: list[int]) -> dict:
        return self.call("get_spot_prices", {"symbolId": symbol_ids})

    def symbols(self) -> dict:
        return self.call("get_symbols", {})

    def trendbars(self, symbol_id: int, period: str, start_ms: int, end_ms: int,
                  verbose: bool = False) -> list[dict]:
        """All bars in [start_ms, end_ms), paging backwards around the 100-bar cap.

        Returns display-priced bars sorted ascending by timestamp:
            {"ts": int_ms, "o": float, "h": float, "l": float, "c": float, "v": int}

        `v` is cTrader TICK volume (count of quote updates in the bar), NOT traded
        contracts. See research/02-DATA-SOURCE-INVESTIGATION.md — this distinction
        matters for every inference built on top of it.
        """
        if period not in PERIOD_MS:
            raise CTraderError(f"unsupported period {period}")
        step = PERIOD_MS[period]
        out: dict[int, dict] = {}
        cursor = end_ms
        # Each request yields at most BAR_CAP bars ending at `cursor`.
        window = BAR_CAP * step
        guard = 0
        while cursor > start_ms:
            guard += 1
            if guard > 2000:
                raise CTraderError("trendbar paging exceeded 2000 requests — aborting")
            frm = max(start_ms, cursor - window)
            raw = self.call("get_trendbars", {
                "symbolId": symbol_id,
                "period": period,
                # The tool schema types these as strings; ints are rejected.
                "fromTimestamp": str(int(frm)),
                "toTimestamp": str(int(cursor)),
            })
            bars = raw.get("trendbars") or []
            if not bars:
                # Market-closed gap (weekend/holiday). Step the cursor back a full
                # window and keep going rather than terminating the whole scan.
                cursor = frm
                continue
            for b in bars:
                out[b["timestamp"]] = {
                    "ts": b["timestamp"],
                    "o": b["open"] / PIPETTE,
                    "h": b["high"] / PIPETTE,
                    "l": b["low"] / PIPETTE,
                    "c": b["close"] / PIPETTE,
                    "v": b.get("volume", 0),
                }
            oldest = min(b["timestamp"] for b in bars)
            if verbose:
                print(f"  … {len(out):>6} bars, back to {iso(oldest)}", file=sys.stderr)
            if oldest <= start_ms:
                break
            # Two cases, and conflating them stalls the walk:
            #   full response  → we were truncated by the cap, so there is more
            #                    data between frm and oldest. Resume at oldest.
            #   short response → we got everything the window holds; the rest is
            #                    a market-closed gap. Jump the whole window.
            # Requesting a window that is mostly gap returns the single boundary
            # bar at toTimestamp, so "resume at oldest" would make no progress.
            cursor = oldest if (len(bars) >= BAR_CAP and oldest < cursor) else frm
            time.sleep(0.05)  # be polite to the backend
        return [out[k] for k in sorted(out) if start_ms <= k < end_ms]


def iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M")


def now_ms() -> int:
    return int(time.time() * 1000)
