#!/usr/bin/env python3
"""
cTrader direct-HTTP fetcher for the /gold-session skill.

WHY THIS EXISTS
    The `mcp__ctrader__*` MCP tools are flaky — the stdio/SSE connector
    frequently fails to register in remote sessions or drops mid-run. The
    cTrader server itself, reached directly over HTTPS, is stable. This script
    is the reliable path: it performs the full STEP 0 Phase A+B cTrader data
    pull in one process (persistent keep-alive connection, per the integration
    guide's Lesson 1) and writes exactly the files the engine expects, so a
    session NEVER has to fall back to fabricating data when the MCP is down.

USAGE (from anywhere)
    python3 ICT-SMC-Local-Agent/ctrader_http_fetch.py
    # then run the engine:
    python3 ICT-SMC-Local-Agent/skill_adapter.py < /tmp/gold_session_input.json

WHAT IT DOES
    - Reads the account token from $CTRADER_MCP_SLUG (preferred) or
      $CTRADER_MCP_TOKEN. Fails loudly if neither is set.
    - Fetches: spot (XAUUSD 241, EURUSD 1), positions, balance, and trendbars
      H_1 / M_5 / M_1 / D_1 for gold plus M_5 for the EURUSD SMT proxy.
    - Writes raw per-timeframe files to /tmp/gs_*.json AND the assembled,
      pipette-divided engine input to /tmp/gold_session_input.json.
    - Prints a JSON summary (spot, mid, positions, balance, bar counts) to
      stdout for the ACCOUNT CONTEXT / Phase B section of the brief.
    - Exits non-zero with a clear message on any failure — the correct
      response to which is a failure report and NO dashboard record, never
      recycled data.

The output timestamps are genuine cTrader candle times, so the freshness gates
in skill_adapter.py and save-gold-session.ts pass naturally on a live pull and
trip only when the market is genuinely stale (weekend / holiday).
"""

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

# Broker symbolIds on this account (Pepperstone _SB variants). XAUUSD=241
# confirmed; EURUSD=1 for the SMT proxy. pipDigits=5 for both.
_SYM_XAU = 241
_SYM_EUR = 1
_PIP = 10 ** 5

# Trendbar windows (ms back from spot) → matches the skill's Phase B ranges.
_TF = [
    ("h1",  "H_1", 360_000_000,   _SYM_XAU),
    ("m5",  "M_5", 30_000_000,    _SYM_XAU),
    ("m1",  "M_1", 3_600_000,     _SYM_XAU),
    ("d1",  "D_1", 1_900_800_000, _SYM_XAU),
    ("smt", "M_5", 30_000_000,    _SYM_EUR),  # EURUSD proxy
]

_TMP = "/tmp"
_INPUT_PATH = os.path.join(_TMP, "gold_session_input.json")


def _die(msg: str, code: int = 1):
    print(f"CTRADER HTTP FETCH FAILED: {msg}", file=sys.stderr)
    sys.exit(code)


def _token() -> str:
    tok = os.environ.get("CTRADER_MCP_SLUG") or os.environ.get("CTRADER_MCP_TOKEN") or ""
    tok = tok.strip()
    if not tok:
        _die("neither CTRADER_MCP_SLUG nor CTRADER_MCP_TOKEN is set in the environment.")
    return tok


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    for ca in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if ca and os.path.exists(ca):
            try:
                ctx.load_verify_locations(ca)
            except Exception:
                pass
    return ctx


class _Client:
    """Persistent keep-alive connection so every request hits the same
    load-balanced backend (integration guide Lesson 1)."""

    def __init__(self, token: str):
        self.token = token
        self.sid = None
        ctx = _ssl_ctx()
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            p = urlparse(proxy)
            self.conn = http.client.HTTPSConnection(p.hostname, p.port or 443, context=ctx, timeout=30)
            self.conn.set_tunnel(_HOST, 443)
        else:
            self.conn = http.client.HTTPSConnection(_HOST, 443, context=ctx, timeout=30)

    def _post(self, payload: dict) -> dict | None:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        # One retry on transient socket errors (reconnect + replay).
        for attempt in range(2):
            try:
                self.conn.request("POST", _PATH, json.dumps(payload), headers)
                r = self.conn.getresponse()
                ns = r.getheader("Mcp-Session-Id") or r.getheader("mcp-session-id")
                if ns:
                    self.sid = ns
                body = r.read().decode()
                if r.status == 401:
                    _die("HTTP 401 — the broker token is unauthorized/expired. "
                         "Refresh CTRADER_MCP_SLUG (this is a credential issue, not retryable).")
                # SSE: rejoin all data: lines within an event before parsing.
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

    def init(self):
        d = self._post({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "gold-session-http", "version": "1.0"}},
        })
        if not (d and d.get("result")):
            _die(f"initialize handshake failed: {str(d)[:200]}")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def call(self, name: str, args: dict):
        d = self._post({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                        "params": {"name": name, "arguments": args}})
        if d and d.get("error"):
            return {"_error": d["error"]}
        result = (d or {}).get("result") or {}
        content = result.get("content")
        if content and content[0].get("type") == "text":
            try:
                return json.loads(content[0]["text"])
            except Exception:
                return {"_raw": content[0]["text"]}
        return {"_raw": str(d)[:200]}


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def main():
    # Purge any previous run's temp files so a partial failure can never leave
    # stale data behind for the assembler to pick up.
    for f in ("gs_h1.json", "gs_m5.json", "gs_m1.json", "gs_d1.json", "gs_smt.json",
              "gold_session_input.json"):
        try:
            os.remove(os.path.join(_TMP, f))
        except OSError:
            pass

    cli = _Client(_token())
    cli.init()

    spot = cli.call("get_spot_prices", {"symbolId": [_SYM_XAU, _SYM_EUR]})
    prices = {p["symbolId"]: p for p in spot.get("prices", [])} if isinstance(spot, dict) else {}
    xau = prices.get(_SYM_XAU)
    if not xau or not xau.get("bid"):
        _die(f"no spot price for XAUUSD (symbolId {_SYM_XAU}): {str(spot)[:200]}")
    spot_ts = xau.get("timestamp") or int(time.time() * 1000)
    bid, ask = xau["bid"], xau.get("ask", xau["bid"])
    mid = round((bid + ask) / 2 / _PIP, 5)

    positions = cli.call("get_positions", {})
    balance = cli.call("get_balance", {})

    counts = {}
    for key, period, back, symid in _TF:
        res = cli.call("get_trendbars", {
            "symbolId": symid, "period": period,
            "fromTimestamp": _iso(spot_ts - back), "toTimestamp": _iso(spot_ts),
        })
        with open(os.path.join(_TMP, f"gs_{key}.json"), "w") as fh:
            json.dump(res, fh)
        bars = res.get("trendbars", res.get("bars", [])) if isinstance(res, dict) else []
        counts[key] = len(bars)

    if counts.get("h1", 0) < 2 or counts.get("m5", 0) < 2 or counts.get("m1", 0) < 2:
        _die(f"insufficient trendbar data (counts={counts}). Market may be closed, or the fetch partially failed.")

    # Assemble the engine input (divide OHLC by 10^5, keep ms-epoch timestamps).
    def load(key):
        d = json.load(open(os.path.join(_TMP, f"gs_{key}.json")))
        bars = d.get("trendbars") or d.get("bars") or []
        out = []
        for b in bars:
            if b.get("high") is None or b.get("low") is None:
                continue
            o = b.get("open", b.get("close", 0))
            c = b.get("close", b.get("open", 0))
            out.append({"timestamp": int(b["timestamp"]), "open": o / _PIP, "high": b["high"] / _PIP,
                        "low": b["low"] / _PIP, "close": c / _PIP, "volume": b.get("volume", 0)})
        return out

    payload = {"symbol": "XAUUSD", "current_price": mid}
    keymap = {"h1": "h1", "m5": "m5", "m1": "m1", "d1": "d1", "smt": "smt_symbol_m5"}
    for key in ("h1", "m5", "m1", "d1", "smt"):
        series = load(key)
        if series:
            payload[keymap[key]] = series
    with open(_INPUT_PATH, "w") as fh:
        json.dump(payload, fh)

    eur = prices.get(_SYM_EUR)
    summary = {
        "ok": True,
        "engine_input": _INPUT_PATH,
        "spot_ts": spot_ts,
        "spot_iso": _iso(spot_ts),
        "XAUUSD": {"bid": round(bid / _PIP, 2), "ask": round(ask / _PIP, 2), "mid": mid,
                   "high": round(xau["high"] / _PIP, 2) if xau.get("high") else None,
                   "low": round(xau["low"] / _PIP, 2) if xau.get("low") else None},
        "EURUSD_mid": round((eur["bid"] + eur.get("ask", eur["bid"])) / 2 / _PIP, 5) if eur else None,
        "trendbar_counts": counts,
        "positions": positions,
        "balance": balance,
    }
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — top-level guard: any failure must be loud, never silent
        _die(f"unexpected error: {type(e).__name__}: {e}")
