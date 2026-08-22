#!/usr/bin/env python3
"""
Bulk historical OHLCV fetcher (any instrument) — cTrader over direct HTTPS.

    Generalised from fetch_xauusd_history.py: adds --instrument and --divisor so the
    same resumable engine works for XAUUSD, NAS100, US30, etc. Output goes to
    <out-dir>/<INSTRUMENT>/<INSTRUMENT>_<PERIOD>_<YEAR>.csv

WHAT THIS DOES
    Pulls many years of 1-minute (or any timeframe) OHLCV candles for XAUUSD
    from the cTrader MCP server, over a single persistent HTTPS connection, and
    writes them to per-year CSV files with columns:
        datetime,open,high,low,close,volume
    datetime is ISO-8601 UTC (bar OPEN time). Prices are display prices
    (pipettes / 10^5). volume is broker TICK volume (see README "Feed & caveats").

WHY IT IS SHAPED THIS WAY (empirically verified 2026-07-16 against the live API)
    cTrader's get_trendbars has TWO hard, silent limits that compound:
      1. It returns at most **100 bars per request**, always the 100 bars that
         END at `toTimestamp` (widening `fromTimestamp` does nothing).
      2. The requested window must be **<= 720 hours (30 days)** or it returns
         an EMPTY list with no error.
    So you cannot grab a wide span in one call. The only way to get contiguous
    history is to walk BACKWARD 100 bars at a time, moving `toTimestamp` to just
    before the earliest bar of the previous page. For 5 years of 1-minute gold
    that is ~18,000 requests — which is exactly why this is a self-contained
    looping SCRIPT (run once, it paces + checkpoints + resumes itself) and NOT a
    sequence of model-issued tool calls. Driving 18k tool calls from a model
    would be absurdly slow and token-expensive; this keeps token cost ~zero.

    History depth verified: M_1 available >= 6 years back, D_1 >= 8 years back.

ANTI-BLOCK / RESILIENCE DESIGN
    - ONE keep-alive HTTPS connection (same load-balanced backend; a fresh
      connection per request causes ~60% "session not found" failures — this is
      cTrader integration-guide Lesson 1).
    - Polite pacing: a small sleep between requests (default 0.12s).
    - Append-only raw log (_raw_bars.jsonl) + checkpoint (_checkpoint.json):
      the network phase is crash-safe and resumable. Re-run with the same args
      to continue from where it stopped.
    - Reconnect + exponential backoff (2/4/8/16s) on transient socket errors.
    - HTTP 401 is FATAL (expired token — a credential problem, not retryable).
    - A no-progress guard and an empty-page-at-max-window guard both stop the
      loop cleanly at the true history floor instead of looping forever.

USAGE
    export CTRADER_MCP_SLUG=...        # or CTRADER_MCP_TOKEN
    # 1) fetch (resumable). Default: XAUUSD, M_1, 5 years:
    python3 fetch_xauusd_history.py
    # variants:
    python3 fetch_xauusd_history.py --years 5 --period M_1
    python3 fetch_xauusd_history.py --years 5 --period M_5     # ~5x fewer requests
    # 2) build the final per-year CSVs from the raw log (idempotent; also runs
    #    automatically when the fetch loop finishes):
    python3 fetch_xauusd_history.py --finalize-only

    Long runs: launch detached so a dropped shell can't kill it, e.g.
        nohup python3 fetch_xauusd_history.py > fetch.log 2>&1 &
        tail -f fetch.log
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

_HOST = "mcp.ctrader.com"
_PATH = "/trading/mcp"
_PIP = 10 ** 5                     # XAUUSD_SB pipDigits = 5 (verified)
_XAUUSD_SB = 241                   # symbolId on this Pepperstone UK SB account

# Milliseconds per bar, per period — used to step the cursor cleanly past a page.
_PERIOD_MS = {
    "M_1": 60_000, "M_5": 300_000, "M_15": 900_000, "M_30": 1_800_000,
    "H_1": 3_600_000, "H_4": 14_400_000, "D_1": 86_400_000,
}


def _log(msg: str):
    print(f"[{datetime.now(timezone.utc):%Y-%m-%d %H:%M:%S}Z] {msg}", flush=True)


def _die(msg: str, code: int = 1):
    print(f"FETCH FAILED: {msg}", file=sys.stderr, flush=True)
    sys.exit(code)


def _token() -> str:
    tok = (os.environ.get("CTRADER_MCP_SLUG") or os.environ.get("CTRADER_MCP_TOKEN") or "").strip()
    if not tok:
        _die("neither CTRADER_MCP_SLUG nor CTRADER_MCP_TOKEN is set in the environment.")
    return tok


def _iso(ms: int) -> str:
    return datetime.fromtimestamp(ms / 1000, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _ssl_ctx() -> ssl.SSLContext:
    ctx = ssl.create_default_context()
    for ca in (os.environ.get("SSL_CERT_FILE"), "/root/.ccr/ca-bundle.crt"):
        if ca and os.path.exists(ca):
            try:
                ctx.load_verify_locations(ca)
            except Exception:
                pass
    return ctx


class Client:
    """Persistent keep-alive MCP client (integration-guide Lesson 1)."""

    def __init__(self, token: str):
        self.token = token
        self.sid = None
        self._connect()

    def _connect(self):
        ctx = _ssl_ctx()
        proxy = os.environ.get("HTTPS_PROXY") or os.environ.get("https_proxy")
        if proxy:
            p = urlparse(proxy)
            self.conn = http.client.HTTPSConnection(p.hostname, p.port or 443, context=ctx, timeout=40)
            self.conn.set_tunnel(_HOST, 443)
        else:
            self.conn = http.client.HTTPSConnection(_HOST, 443, context=ctx, timeout=40)

    def _post(self, payload: dict) -> dict | None:
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/json, text/event-stream",
            "Content-Type": "application/json",
        }
        if self.sid:
            headers["Mcp-Session-Id"] = self.sid
        self.conn.request("POST", _PATH, json.dumps(payload), headers)
        r = self.conn.getresponse()
        ns = r.getheader("Mcp-Session-Id") or r.getheader("mcp-session-id")
        if ns:
            self.sid = ns
        body = r.read().decode()
        if r.status == 401:
            _die("HTTP 401 — broker token unauthorized/expired. Refresh CTRADER_MCP_SLUG "
                 "(credential issue, not retryable).")
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

    def reconnect(self):
        try:
            self.conn.close()
        except Exception:
            pass
        self.sid = None
        self._connect()
        self.init()

    def init(self):
        d = self._post({
            "jsonrpc": "2.0", "id": 0, "method": "initialize",
            "params": {"protocolVersion": "2024-11-05", "capabilities": {},
                       "clientInfo": {"name": "xauusd-history", "version": "1.0"}},
        })
        if not (d and d.get("result")):
            _die(f"initialize handshake failed: {str(d)[:200]}")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}})

    def trendbars(self, symbol_id: int, period: str, frm_ms: int, to_ms: int) -> list:
        """One page. Retries transient errors with reconnect + exponential backoff."""
        args = {"symbolId": symbol_id, "period": period,
                "fromTimestamp": _iso(frm_ms), "toTimestamp": _iso(to_ms)}
        delay = 2
        for attempt in range(5):
            try:
                d = self._post({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
                                "params": {"name": "get_trendbars", "arguments": args}})
                if d and d.get("error"):
                    raise RuntimeError(f"tool error: {d['error']}")
                result = (d or {}).get("result") or {}
                content = result.get("content")
                if content and content[0].get("type") == "text":
                    payload = json.loads(content[0]["text"])
                    return payload.get("trendbars") or payload.get("bars") or []
                return []
            except SystemExit:
                raise
            except Exception as e:
                if attempt == 4:
                    _die(f"get_trendbars failed after 5 attempts (last: {type(e).__name__}: {e})")
                _log(f"  transient error ({type(e).__name__}: {e}) — reconnecting, backoff {delay}s")
                time.sleep(delay)
                delay = min(delay * 2, 16)
                try:
                    self.reconnect()
                except SystemExit:
                    raise
                except Exception:
                    pass
        return []


# ── file paths ────────────────────────────────────────────────────────────────
def _paths(out_dir: str, period: str, instrument: str = "XAUUSD"):
    raw = os.path.join(out_dir, f"_raw_bars_{instrument}_{period}.jsonl")
    ckpt = os.path.join(out_dir, f"_checkpoint_{instrument}_{period}.json")
    return raw, ckpt


def fetch(args):
    out_dir = args.out_dir
    os.makedirs(os.path.join(out_dir, args.instrument), exist_ok=True)
    raw_path, ckpt_path = _paths(out_dir, args.period, args.instrument)
    period_ms = _PERIOD_MS[args.period]

    now = datetime.now(timezone.utc)
    target_start_ms = int((now - timedelta(days=int(args.years * 365))).timestamp() * 1000)

    # Resume from checkpoint if present, else start at "now".
    cursor_to_ms = int(now.timestamp() * 1000)
    total = 0
    if os.path.exists(ckpt_path):
        try:
            ck = json.load(open(ckpt_path))
            cursor_to_ms = int(ck["cursor_to_ms"])
            total = int(ck.get("total", 0))
            _log(f"RESUMING {args.period} from checkpoint: cursor={_iso(cursor_to_ms)} total_so_far={total}")
        except Exception:
            _log("checkpoint unreadable — starting fresh")

    cli = Client(_token())
    cli.init()

    window_ms = int(args.window_hours * 3_600_000)
    max_window_ms = 720 * 3_600_000
    raw_fh = open(raw_path, "a")
    pages = 0
    t0 = time.time()

    try:
        while cursor_to_ms > target_start_ms:
            frm_ms = cursor_to_ms - window_ms
            bars = cli.trendbars(args.symbol_id, args.period, frm_ms, cursor_to_ms)

            if not bars:
                # Empty page. Could be a closure gap wider than our window, OR the
                # true history floor. Escalate to the 720h max once to disambiguate.
                wide_frm = cursor_to_ms - max_window_ms
                bars = cli.trendbars(args.symbol_id, args.period, wide_frm, cursor_to_ms)
                if not bars:
                    _log(f"empty page even at 720h window ending {_iso(cursor_to_ms)} — "
                         f"treating as history floor. Stopping.")
                    break

            earliest_ms = min(int(b["timestamp"]) for b in bars)
            for b in bars:
                raw_fh.write(json.dumps(b) + "\n")
            total += len(bars)
            pages += 1

            # No-progress guard: the cursor must strictly move back.
            next_cursor = earliest_ms - period_ms
            if next_cursor >= cursor_to_ms:
                _log("no backward progress — stopping to avoid an infinite loop.")
                break
            cursor_to_ms = next_cursor

            if pages % 50 == 0:
                raw_fh.flush()
                json.dump({"cursor_to_ms": cursor_to_ms, "total": total}, open(ckpt_path, "w"))
                rate = pages / max(time.time() - t0, 1e-9)
                _log(f"{args.period}: {pages} pages, {total} bars, at {_iso(cursor_to_ms)} "
                     f"({rate:.1f} req/s)")

            time.sleep(args.sleep)
    finally:
        raw_fh.flush()
        raw_fh.close()
        json.dump({"cursor_to_ms": cursor_to_ms, "total": total}, open(ckpt_path, "w"))

    _log(f"FETCH DONE ({args.period}): {pages} pages this run, {total} raw bars total, "
         f"reached {_iso(cursor_to_ms)}.")
    finalize(args)


def finalize(args):
    """Dedup + sort + convert raw jsonl into per-year CSVs. Idempotent."""
    out_dir = args.out_dir
    raw_path, _ = _paths(out_dir, args.period, args.instrument)
    if not os.path.exists(raw_path):
        _die(f"no raw file to finalize: {raw_path}")

    seen = {}   # ts_ms -> bar (dedup, last wins)
    with open(raw_path) as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                b = json.loads(line)
            except Exception:
                continue
            if b.get("high") is None or b.get("low") is None:
                continue
            seen[int(b["timestamp"])] = b

    if not seen:
        _die("raw file contained no usable bars.")

    target_start_ms = int((datetime.now(timezone.utc) - timedelta(days=int(args.years * 365))).timestamp() * 1000)
    rows_by_year = {}
    for ts in sorted(seen):
        if ts < target_start_ms:
            continue
        b = seen[ts]
        dt = datetime.fromtimestamp(ts / 1000, tz=timezone.utc)
        o = b.get("open", b.get("close", 0)) / args.divisor
        c = b.get("close", b.get("open", 0)) / args.divisor
        row = (dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
               round(o, 5), round(b["high"] / args.divisor, 5), round(b["low"] / args.divisor, 5),
               round(c, 5), b.get("volume", 0))
        rows_by_year.setdefault(dt.year, []).append(row)

    written = []
    for year, rows in sorted(rows_by_year.items()):
        os.makedirs(os.path.join(out_dir, args.instrument), exist_ok=True)
        path = os.path.join(out_dir, args.instrument, f"{args.instrument}_{args.period}_{year}.csv")
        with open(path, "w") as fh:
            fh.write("datetime,open,high,low,close,volume\n")
            for r in rows:
                fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]},{r[5]}\n")
        written.append((path, len(rows)))

    total_rows = sum(n for _, n in written)
    span = f"{datetime.fromtimestamp(min(seen)/1000, tz=timezone.utc):%Y-%m-%d} .. " \
           f"{datetime.fromtimestamp(max(seen)/1000, tz=timezone.utc):%Y-%m-%d}"
    _log(f"FINALIZE DONE ({args.period}): {total_rows} rows across {len(written)} year-files. "
         f"Raw span {span}.")
    for path, n in written:
        _log(f"  {os.path.relpath(path, out_dir)}: {n} rows")


def main():
    ap = argparse.ArgumentParser(description="Bulk XAUUSD historical OHLCV fetcher (cTrader HTTP).")
    ap.add_argument("--years", type=float, default=5.0, help="how many years back (default 5)")
    ap.add_argument("--period", default="M_1", choices=sorted(_PERIOD_MS), help="timeframe (default M_1)")
    ap.add_argument("--symbol-id", type=int, default=_XAUUSD_SB, help="cTrader symbolId (default 241 XAUUSD_SB)")
    ap.add_argument("--instrument", default="XAUUSD", help="instrument name; sets output subfolder and filenames")
    ap.add_argument("--divisor", type=float, default=float(_PIP), help="price divisor (pipettes -> price). 100000 for XAUUSD/US30/NAS100 on this account")
    ap.add_argument("--window-hours", type=float, default=336.0,
                    help="request window width in hours, must be <=720 (default 336 = 14d, "
                         "always straddles weekend/holiday gaps)")
    ap.add_argument("--sleep", type=float, default=0.12, help="seconds between requests (default 0.12)")
    ap.add_argument("--out-dir", default=os.path.dirname(os.path.abspath(__file__)),
                    help="output directory (default: this script's folder)")
    ap.add_argument("--finalize-only", action="store_true",
                    help="skip fetching; just (re)build per-year CSVs from the existing raw log")
    args = ap.parse_args()

    if args.window_hours > 720:
        _die("--window-hours must be <= 720 (the API silently returns 0 bars for wider windows).")

    if args.finalize_only:
        finalize(args)
    else:
        fetch(args)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        _log("interrupted — checkpoint saved; re-run the same command to resume.")
    except Exception as e:  # noqa: BLE001
        _die(f"unexpected error: {type(e).__name__}: {e}")
