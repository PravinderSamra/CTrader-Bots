"""
CTrader Remote MCP fetcher for GEX & OI agent.

Provides live Pepperstone spread bet prices and recent candles for:
  US500, UK100, GER40, XAUUSD

Uses the same persistent-HTTPS + JSON-RPC-2.0 pattern established in
ICT-SMC-Remote-Agent/data/fetchers/ctrader_fetcher.py.

Critical: Must use http.client.HTTPSConnection (keep-alive) — NOT requests or
urllib with Connection:close. The MCP server is load-balanced; closing the TCP
connection between calls routes to a different backend with no session state.
"""

import http.client
import ssl
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

# ── Auth ──────────────────────────────────────────────────────────────────────
_MCP_HOST = "mcp.ctrader.com"
_MCP_PATH = "/trading/mcp"

_TOKEN = (
    os.environ.get("CTRADER_MCP_TOKEN")
    or "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

# ── Instrument map: our label → Pepperstone _SB suffix symbol ─────────────────
SYMBOL_MAP = {
    "US500":  "US500",
    "UK100":  "UK100",
    "GER40":  "GER40",
    "XAUUSD": "XAUUSD",
}

# Pip digits: raw pipette price ÷ 10^digits = display price
PIP_DIGITS = {
    "US500": 3, "NAS100": 4, "US30": 4,
    "UK100": 3, "GER40":  3,
    "XAUUSD": 3, "XAGUSD": 3,
}

# Plausible display price ranges for auto-detection of pip digits
PRICE_RANGES = {
    "US500":  (3_000, 12_000),
    "NAS100": (8_000, 30_000),
    "UK100":  (6_000, 13_000),
    "GER40":  (12_000, 30_000),
    "XAUUSD": (1_400, 8_000),
}

# cTrader period strings
PERIOD_MAP = {
    "1m": "M_1", "5m": "M_5", "15m": "M_15", "30m": "M_30",
    "1h": "H_1", "4h": "H_4", "1d":  "D_1",  "1w":  "W_1",
}

HOURS_PER_PERIOD = {
    "M_1": 1/60, "M_5": 5/60, "M_15": 15/60, "M_30": 0.5,
    "H_1": 1.0,  "H_4": 4.0,  "D_1":  24.0,  "W_1":  168.0,
}

# ── Connection state ──────────────────────────────────────────────────────────
_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None
_symbol_id_cache: dict[str, int] = {}
_symbols_loaded: bool = False
_pip_digits_cache: dict[str, int] = {}


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            _MCP_HOST,
            context=ssl.create_default_context(),
            timeout=20,
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    global _conn, _session_id
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {_TOKEN}",
        "Accept":        "application/json, text/event-stream",
        "Content-Type":  "application/json",
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

    return None, session_id


def _ensure_session() -> bool:
    global _session_id
    if _session_id:
        return True

    data, sid = _post({
        "jsonrpc": "2.0", "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "gex-oi-agent", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def _call_tool(tool: str, arguments: dict) -> Optional[dict]:
    global _session_id
    if not _ensure_session():
        return None

    payload = {
        "jsonrpc": "2.0", "method": "tools/call",
        "params": {"name": tool, "arguments": arguments},
        "id": 1,
    }
    data, new_sid = _post(payload, _session_id)

    expired = (
        (data and data.get("_session_expired")) or
        (data and "error" in data and "session" in str(data.get("error", {}).get("message", "")).lower())
    )
    if expired:
        _session_id = None
        if not _ensure_session():
            return None
        data, new_sid = _post(payload, _session_id)

    if new_sid:
        _session_id = new_sid

    if not data or "result" not in data:
        return None

    content = data["result"].get("content", [])
    if content and content[0].get("type") == "text":
        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError):
            pass
    return None


def _strip_suffix(name: str) -> str:
    for suffix in ("_SBE", "_SB", "-F_SB", "-F"):
        if name.upper().endswith(suffix):
            return name.upper()[: -len(suffix)]
    return name.upper()


def _load_symbols() -> None:
    global _symbols_loaded
    if _symbols_loaded:
        return
    result = _call_tool("get_symbols", {})
    if not result:
        return
    for sym in result.get("symbols", []):
        if not sym.get("enabled", False):
            continue
        raw_name = (sym.get("name") or sym.get("symbolName") or "").upper()
        sid = sym.get("symbolId")
        if raw_name and sid is not None:
            _symbol_id_cache[raw_name] = int(sid)
            base = _strip_suffix(raw_name)
            if base != raw_name:
                _symbol_id_cache.setdefault(base, int(sid))
    _symbols_loaded = True


def _get_symbol_id(name: str) -> Optional[int]:
    _load_symbols()
    key = name.upper().strip()
    if key in _symbol_id_cache:
        return _symbol_id_cache[key]
    base = _strip_suffix(key)
    if base in _symbol_id_cache:
        return _symbol_id_cache[base]
    for cached_name, sid in _symbol_id_cache.items():
        if _strip_suffix(cached_name) == base:
            return sid
    return None


def _auto_pip_digits(name: str, raw_sample: float) -> int:
    key = _strip_suffix(name)
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]
    hint = PIP_DIGITS.get(key, 5)
    lo, hi = PRICE_RANGES.get(key, (0, 0))
    if lo and hi and raw_sample > 0:
        for digits in range(0, 9):
            display = raw_sample / (10 ** digits)
            if lo <= display <= hi:
                _pip_digits_cache[key] = digits
                return digits
    return hint


# ── Public API ────────────────────────────────────────────────────────────────

def get_live_price(instrument: str) -> Optional[dict]:
    """
    Return live bid/ask/mid price for a Pepperstone spread bet instrument.

    instrument: 'US500', 'UK100', 'GER40', 'XAUUSD'
    Returns: {'bid': float, 'ask': float, 'mid': float, 'spread': float, 'symbol': str}
    """
    ct_name = SYMBOL_MAP.get(instrument, instrument)
    symbol_id = _get_symbol_id(ct_name)
    if symbol_id is None:
        return None

    result = _call_tool("get_spot_prices", {"symbolId": [symbol_id]})
    if not result:
        return None

    prices = result.get("prices") or result.get("spotPrices") or []
    if not prices:
        return None

    raw_bid = prices[0].get("bid", 0)
    raw_ask = prices[0].get("ask", 0)
    digits = _auto_pip_digits(ct_name, raw_bid or raw_ask)
    div = 10 ** digits

    bid = raw_bid / div
    ask = raw_ask / div
    mid = (bid + ask) / 2
    spread = round(ask - bid, digits)

    return {
        "instrument": instrument,
        "symbol": ct_name,
        "bid": bid,
        "ask": ask,
        "mid": mid,
        "spread": spread,
    }


def get_all_live_prices() -> dict[str, dict]:
    """Fetch live prices for all four trading instruments in one session."""
    prices = {}
    for instrument in ["US500", "UK100", "GER40", "XAUUSD"]:
        result = get_live_price(instrument)
        if result:
            prices[instrument] = result
    return prices


def get_recent_candles(instrument: str, interval: str = "1h", limit: int = 50) -> list[dict]:
    """
    Fetch recent OHLCV candles from Pepperstone via cTrader MCP.

    instrument: 'US500', 'UK100', 'GER40', 'XAUUSD'
    interval: '1m', '5m', '15m', '1h', '4h', '1d'
    limit: number of candles to return

    Returns list of {'ts': datetime, 'o': float, 'h': float, 'l': float, 'c': float, 'v': float}
    """
    ct_name = SYMBOL_MAP.get(instrument, instrument)
    symbol_id = _get_symbol_id(ct_name)
    if symbol_id is None:
        return []

    period = PERIOD_MAP.get(interval)
    if not period:
        return []

    hours = HOURS_PER_PERIOD.get(period, 1.0) * limit
    hours = min(hours, 720.0)  # API hard cap
    to_ts   = datetime.now(tz=timezone.utc)
    from_ts = to_ts - timedelta(hours=hours)

    result = _call_tool("get_trendbars", {
        "symbolId":      symbol_id,
        "period":        period,
        "fromTimestamp": from_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toTimestamp":   to_ts.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })

    if not result:
        return []

    bars = (
        result.get("trendbars") or result.get("trendBars") or
        result.get("bars")      or result.get("data")      or []
    )
    if not bars:
        return []

    # Auto-detect pip digits from first bar
    first_close = bars[0].get("close", 0) if bars else 0
    digits = _auto_pip_digits(ct_name, first_close)
    div = 10 ** digits

    candles = []
    for bar in bars:
        ts_raw = (
            bar.get("utcTimestamp") or bar.get("timestamp") or
            bar.get("utcTimestampInMinutes") or bar.get("time") or 0
        )
        ts_int = int(ts_raw)
        if ts_int > 1_000_000_000_000:
            ts = datetime.fromtimestamp(ts_int / 1000, tz=timezone.utc)
        elif ts_int > 1_000_000_000:
            ts = datetime.fromtimestamp(float(ts_int), tz=timezone.utc)
        else:
            ts = datetime.fromtimestamp(ts_int * 60.0, tz=timezone.utc)

        o = bar.get("open",  0) / div
        h = bar.get("high",  0) / div
        l = bar.get("low",   0) / div
        c = bar.get("close", 0) / div
        v = float(bar.get("tickVolume") or bar.get("volume") or 0)

        if l > 0 and h >= l:
            candles.append({"ts": ts, "o": o, "h": h, "l": l, "c": c, "v": v})

    candles.sort(key=lambda x: x["ts"])
    return candles[-limit:]


def compute_volume_profile(instrument: str, bucket_size: float = None, lookback_candles: int = 168) -> dict:
    """
    Compute a volume profile from H1 CTrader candles.
    lookback_candles=168 covers ~7 days of H1 bars (includes overnight gaps).

    Returns:
        poc         : Point of Control — price bucket with highest tick volume
        hvn_levels  : High Volume Nodes — price areas with above-average volume
        lvn_levels  : Low Volume Nodes  — thin areas where price moves fast
        bucket_size : bucket width used
    """
    candles = get_recent_candles(instrument, "1h", lookback_candles)
    if not candles or len(candles) < 10:
        return {}

    mid_price = (candles[-1]["h"] + candles[-1]["l"]) / 2

    if bucket_size is None:
        raw = mid_price * 0.001
        for snap in (0.5, 1, 2, 5, 10, 25, 50, 100):
            if raw <= snap:
                bucket_size = snap
                break
        else:
            bucket_size = 100.0

    profile: dict[float, float] = {}
    for c in candles:
        h, l, v = c["h"], c["l"], c["v"]
        if h <= l or v <= 0:
            continue
        low_b  = round(round(l  / bucket_size) * bucket_size, 4)
        high_b = round(round(h  / bucket_size) * bucket_size, 4)
        if high_b < low_b:
            high_b = low_b
        n = max(1, round((high_b - low_b) / bucket_size) + 1)
        vpb = v / n
        price = low_b
        for _ in range(n):
            key = round(price, 4)
            profile[key] = profile.get(key, 0.0) + vpb
            price += bucket_size

    if len(profile) < 5:
        return {}

    poc = max(profile, key=profile.get)
    vals = list(profile.values())

    import statistics
    mean_v = statistics.mean(vals)
    std_v  = statistics.stdev(vals) if len(vals) > 1 else 0.0

    hvn_thresh = mean_v + 0.3 * std_v
    lvn_thresh = mean_v - 0.5 * std_v

    current = candles[-1]["c"]
    hvn = sorted(
        [p for p, v in profile.items() if v >= hvn_thresh and abs(p - poc) > bucket_size],
        key=lambda p: -profile[p],
    )[:8]
    lvn = sorted(
        [p for p, v in profile.items() if v <= max(lvn_thresh, 0)],
        key=lambda p: abs(p - current),
    )[:5]

    return {
        "poc":            poc,
        "hvn_levels":     sorted(hvn, reverse=True),
        "lvn_levels":     sorted(lvn, reverse=True),
        "bucket_size":    bucket_size,
        "lookback_bars":  len(candles),
    }


def get_session_structure(instrument: str) -> dict:
    """
    Fetch key structural levels from Pepperstone candles:
    prior day H/L, weekly open, current day open, recent swing H/L.
    """
    daily = get_recent_candles(instrument, "1d", 10)
    hourly = get_recent_candles(instrument, "1h", 48)

    result = {}

    if daily and len(daily) >= 2:
        prev_day = daily[-2]
        result["prev_day_high"]  = prev_day["h"]
        result["prev_day_low"]   = prev_day["l"]
        result["prev_day_close"] = prev_day["c"]
        result["today_open"]     = daily[-1]["o"] if daily else None

    if len(daily) >= 6:
        result["weekly_open"] = daily[-5]["o"]  # approx 5 trading days

    if hourly:
        highs = [c["h"] for c in hourly[-24:]]
        lows  = [c["l"] for c in hourly[-24:]]
        result["session_high"] = max(highs) if highs else None
        result["session_low"]  = min(lows)  if lows  else None
        result["current_price"] = hourly[-1]["c"]

    return result
