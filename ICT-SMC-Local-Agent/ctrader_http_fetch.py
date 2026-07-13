#!/usr/bin/env python3
"""
cTrader direct-HTTP fetcher for the /gold-session and /uk100-session skills.

WHY THIS EXISTS
    The `mcp__ctrader__*` MCP tools are flaky — the stdio/SSE connector
    frequently fails to register in remote sessions or drops mid-run. The
    cTrader server itself, reached directly over HTTPS, is stable. This script
    is the reliable path: it performs the full STEP 0 Phase A+B cTrader data
    pull in one process (persistent keep-alive connection, per the integration
    guide's Lesson 1) and writes exactly the files the engine expects, so a
    session NEVER has to fall back to fabricating data when the MCP is down.

USAGE (from anywhere)
    python3 ICT-SMC-Local-Agent/ctrader_http_fetch.py                    # gold (default)
    python3 ICT-SMC-Local-Agent/ctrader_http_fetch.py --instrument uk100 # UK100
    # then run the matching engine:
    python3 ICT-SMC-Local-Agent/skill_adapter.py  < /tmp/gold_session_input.json
    python3 ICT-SMC-Local-Agent/uk100_adapter.py  < /tmp/uk100_session_input.json

WHAT IT DOES
    - Reads the account token from $CTRADER_MCP_SLUG (preferred) or
      $CTRADER_MCP_TOKEN. Fails loudly if neither is set.
    - Fetches: spot (main + proxy symbolId, per INSTRUMENTS), positions,
      balance, and trendbars H_1 / M_5 / M_1 / D_1 for the main instrument
      plus M_5 for the SMT-proxy cross-check.
    - uk100 only (INSTRUMENTS["uk100"]["us_tape"]): one extra get_spot_prices
      call for US500/NAS100/VIX, printed in the summary under "us_tape".
      Fixes UK100-SESSION-REVIEW-2026-07-13.md §3.7 — the macro snapshot's
      US-linkage numbers can be ~2h stale by the time a session runs during
      US_OVERLAP (14:30+ London); this gives the skill a live US read instead.
    - Writes raw per-timeframe files to /tmp/{pfx}_*.json AND the assembled,
      pipette-divided engine input to the instrument's input path.
    - Prints a JSON summary (spot, mid, positions, balance, bar counts) to
      stdout for the ACCOUNT CONTEXT / Phase B section of the brief.
    - Exits non-zero with a clear message on any failure — the correct
      response to which is a failure report and NO dashboard record, never
      recycled data.

The output timestamps are genuine cTrader candle times, so the freshness gates
in skill_adapter.py/uk100_adapter.py and save-gold-session.ts pass naturally
on a live pull and trip only when the market is genuinely stale (weekend /
holiday).
"""

import argparse
import http.client
import json
import os
import ssl
import sys
import time
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

_HOST = "mcp.ctrader.com"
_PATH = "/trading/mcp"
_LDN = ZoneInfo("Europe/London")

# Broker symbolIds on this account. pipDigits=5 for everything below (verified
# per-instrument — see ctrader-mcp-integration-guide.md and UK100-BUILD-PLAN.md §1.1).
# "proxy" is the SMT-divergence cross-check symbol: EURUSD is positively
# correlated with XAUUSD (both rise as the dollar weakens); GBPUSD is the
# UK100 proxy but the read is INVERTED (weak GBP lifts FTSE) — uk100_adapter.py
# accounts for that with a dedicated _smt_divergence_inverse, not this script.
# "orb_context": uk100 only — the general 500-min M5 window below does not
# reach back to the 22:00-prev-day/08:00-cash-open ORB window when the skill
# runs later in the day, so two extra targeted fetches supply it (same fix
# already applied on the TS side in fetch-uk100-data.ts after hitting the
# cTrader get_trendbars 100-bar silent cap on a single wide window).
INSTRUMENTS = {
    "gold":  {"main": 241, "proxy": 1, "proxy_symbol": "EURUSD", "pfx": "gs", "input": "/tmp/gold_session_input.json", "symbol": "XAUUSD", "orb_context": False},
    "uk100": {"main": 113, "proxy": 2, "proxy_symbol": "GBPUSD", "pfx": "uk", "input": "/tmp/uk100_session_input.json", "symbol": "UK100", "orb_context": True,
              # Live US-linkage spots (§3.7 fix) — US500/NAS100/VIX, same
              # symbolIds as xauusd-dashboard's KNOWN_SYMBOL_IDS.
              "us_tape": {115: "US500", 116: "NAS100", 152: "VIX"}},
}
_PIP = 10 ** 5

# Trendbar windows (ms back from spot) → matches the skill's Phase B ranges.
# uk100 additionally needs a wider H_1 window (overnight range spans 22:00→08:00
# London = up to 10h) — handled via _tf_for() below rather than hardcoding here.
def _tf_for(cfg: dict) -> list:
    h1_back = 360_000_000 if cfg["symbol"] == "XAUUSD" else 396_000_000  # 100h / 110h
    return [
        ("h1",  "H_1", h1_back,       cfg["main"]),
        ("m5",  "M_5", 30_000_000,    cfg["main"]),
        ("m1",  "M_1", 3_600_000,     cfg["main"]),
        ("d1",  "D_1", 1_900_800_000, cfg["main"]),
        ("smt", "M_5", 30_000_000,    cfg["proxy"]),
    ]

_TMP = "/tmp"


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--instrument", choices=sorted(INSTRUMENTS), default="gold")
    args = parser.parse_args()
    cfg = INSTRUMENTS[args.instrument]
    pfx = cfg["pfx"]
    input_path = cfg["input"]
    main_sym, proxy_sym = cfg["main"], cfg["proxy"]

    # Purge any previous run's temp files so a partial failure can never leave
    # stale data behind for the assembler to pick up.
    for f in (f"{pfx}_h1.json", f"{pfx}_m5.json", f"{pfx}_m1.json", f"{pfx}_d1.json",
              f"{pfx}_smt.json", f"{pfx}_orb_h1.json", f"{pfx}_orb_m5.json", os.path.basename(input_path)):
        try:
            os.remove(os.path.join(_TMP, f))
        except OSError:
            pass

    cli = _Client(_token())
    cli.init()

    spot = cli.call("get_spot_prices", {"symbolId": [main_sym, proxy_sym]})
    prices = {p["symbolId"]: p for p in spot.get("prices", [])} if isinstance(spot, dict) else {}
    main_px = prices.get(main_sym)
    if not main_px or not main_px.get("bid"):
        _die(f"no spot price for {cfg['symbol']} (symbolId {main_sym}): {str(spot)[:200]}")
    spot_ts = main_px.get("timestamp") or int(time.time() * 1000)
    bid, ask = main_px["bid"], main_px.get("ask", main_px["bid"])
    mid = round((bid + ask) / 2 / _PIP, 5)

    # Live US-linkage tape (uk100 only) — one extra call, same connection.
    # Best-effort: a failure here never aborts the run (the macro snapshot's
    # US500/NAS100/VIX day% is still available as a fallback in the skill).
    us_tape_cfg = cfg.get("us_tape") or {}
    us_tape_prices = {}
    if us_tape_cfg:
        us_spot = cli.call("get_spot_prices", {"symbolId": list(us_tape_cfg.keys())})
        us_tape_prices = {p["symbolId"]: p for p in us_spot.get("prices", [])} if isinstance(us_spot, dict) else {}

    positions = cli.call("get_positions", {})
    balance = cli.call("get_balance", {})

    counts = {}
    for key, period, back, symid in _tf_for(cfg):
        res = cli.call("get_trendbars", {
            "symbolId": symid, "period": period,
            "fromTimestamp": _iso(spot_ts - back), "toTimestamp": _iso(spot_ts),
        })
        with open(os.path.join(_TMP, f"{pfx}_{key}.json"), "w") as fh:
            json.dump(res, fh)
        bars = res.get("trendbars", res.get("bars", [])) if isinstance(res, dict) else []
        counts[key] = len(bars)

    if counts.get("h1", 0) < 2 or counts.get("m5", 0) < 2 or counts.get("m1", 0) < 2:
        _die(f"insufficient trendbar data (counts={counts}). Market may be closed, or the fetch partially failed.")

    # ORB-context extra fetches (uk100 only) — exact timestamp windows, well
    # under the 100-bar cap, so the overnight range and ORB range are always
    # complete regardless of what time of day the skill runs.
    if cfg.get("orb_context"):
        spot_dt = datetime.fromtimestamp(spot_ts / 1000, tz=timezone.utc).astimezone(_LDN)
        cash_open = spot_dt.replace(hour=8, minute=0, second=0, microsecond=0)
        overnight_from_ms = int((cash_open - timedelta(hours=10)).timestamp() * 1000)
        overnight_to_ms = min(spot_ts, int(cash_open.timestamp() * 1000))
        orb_from_ms = int(cash_open.timestamp() * 1000)
        orb_to_ms = int((cash_open + timedelta(minutes=15)).timestamp() * 1000)

        res_h1 = cli.call("get_trendbars", {
            "symbolId": main_sym, "period": "H_1",
            "fromTimestamp": _iso(overnight_from_ms), "toTimestamp": _iso(overnight_to_ms),
        })
        with open(os.path.join(_TMP, f"{pfx}_orb_h1.json"), "w") as fh:
            json.dump(res_h1, fh)

        if spot_ts >= orb_from_ms:
            res_orb_m5 = cli.call("get_trendbars", {
                "symbolId": main_sym, "period": "M_5",
                "fromTimestamp": _iso(orb_from_ms), "toTimestamp": _iso(min(spot_ts, orb_to_ms)),
            })
        else:
            res_orb_m5 = {"trendbars": []}  # cash open hasn't happened yet today
        with open(os.path.join(_TMP, f"{pfx}_orb_m5.json"), "w") as fh:
            json.dump(res_orb_m5, fh)

    # Assemble the engine input (divide OHLC by 10^5, keep ms-epoch timestamps).
    def load(key):
        d = json.load(open(os.path.join(_TMP, f"{pfx}_{key}.json")))
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

    payload = {"symbol": cfg["symbol"], "current_price": mid}
    keymap = {"h1": "h1", "m5": "m5", "m1": "m1", "d1": "d1", "smt": "smt_symbol_m5"}
    for key in ("h1", "m5", "m1", "d1", "smt"):
        series = load(key)
        if series:
            payload[keymap[key]] = series

    if cfg.get("orb_context"):
        orb_h1_series = load("orb_h1")
        orb_m5_series = load("orb_m5")
        if orb_h1_series:
            payload["orb_h1"] = orb_h1_series
        if orb_m5_series:
            payload["orb_m5"] = orb_m5_series

    with open(input_path, "w") as fh:
        json.dump(payload, fh)

    proxy_px = prices.get(proxy_sym)
    summary = {
        "ok": True,
        "engine_input": input_path,
        "spot_ts": spot_ts,
        "spot_iso": _iso(spot_ts),
        cfg["symbol"]: {"bid": round(bid / _PIP, 2), "ask": round(ask / _PIP, 2), "mid": mid,
                        "high": round(main_px["high"] / _PIP, 2) if main_px.get("high") else None,
                        "low": round(main_px["low"] / _PIP, 2) if main_px.get("low") else None},
        f"{cfg['proxy_symbol']}_mid": round((proxy_px["bid"] + proxy_px.get("ask", proxy_px["bid"])) / 2 / _PIP, 5) if proxy_px else None,
        "trendbar_counts": counts,
        "positions": positions,
        "balance": balance,
    }

    # Live US-linkage tape (§3.7 fix) — quote this during US_OVERLAP instead
    # of the macro snapshot's day% numbers, which can be ~2h stale by then.
    if us_tape_cfg:
        us_tape_summary = {}
        for sid, name in us_tape_cfg.items():
            px = us_tape_prices.get(sid)
            if px and px.get("bid"):
                b, a = px["bid"], px.get("ask", px["bid"])
                us_tape_summary[name] = {"bid": round(b / _PIP, 2), "ask": round(a / _PIP, 2), "mid": round((b + a) / 2 / _PIP, 2)}
            else:
                us_tape_summary[name] = None
        summary["us_tape"] = us_tape_summary

    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001 — top-level guard: any failure must be loud, never silent
        _die(f"unexpected error: {type(e).__name__}: {e}")
