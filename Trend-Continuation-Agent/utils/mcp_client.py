"""
cTrader MCP HTTP client — /Trend-Continuation-Agent

Spec §2 / §11: "Use CTrader MCP via HTTP as the ONLY data and execution route."

Connection pattern is the proven one from `ctrader-mcp-integration-guide.md`
(persistent HTTPS connection + session handshake) — the same approach used by
ICT-SMC-Remote-Agent and the Trade Picker skill.
"""

from __future__ import annotations

import http.client
import json
import os
import ssl
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import (
    CTRADER_MCP_HOST,
    CTRADER_MCP_PATH,
    CTRADER_MCP_TOKEN,
    SB_SYMBOL_CACHE,
)


# ── Bar model ────────────────────────────────────────────────────────────────
@dataclass
class Bar:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


# ── Plausible display-price ranges, used to auto-detect pip/point divisors ───
# Raw quotes from get_trendbars / get_spot_prices are in "pipettes" (large
# integers). display_price = raw / 10^N. N is detected per-symbol the first
# time a quote is seen, by finding the N that puts the value in this range.
PRICE_RANGES: dict[str, tuple[float, float]] = {
    # Forex majors
    "EURUSD": (0.80, 1.60), "GBPUSD": (1.00, 1.70),
    "AUDUSD": (0.50, 1.10), "NZDUSD": (0.40, 0.90),
    "USDCHF": (0.75, 1.20), "USDCAD": (1.10, 1.65),
    "USDJPY": (100, 200),
    # Forex crosses
    "GBPJPY": (150, 260), "EURJPY": (110, 190), "AUDJPY": (60, 130),
    "CADJPY": (85, 130), "EURGBP": (0.70, 0.95), "GBPAUD": (1.60, 2.30),
    "EURCAD": (1.30, 1.90), "GBPCAD": (1.60, 2.20), "EURAUD": (1.40, 1.90),
    "EURCHF": (0.85, 1.10), "EURNZD": (1.50, 2.10), "GBPCHF": (1.05, 1.35),
    "GBPNZD": (1.90, 2.50), "AUDCAD": (0.85, 1.00), "AUDCHF": (0.50, 0.70),
    "AUDNZD": (1.00, 1.20), "NZDCAD": (0.75, 0.95), "NZDCHF": (0.45, 0.65),
    "CADCHF": (0.60, 0.80), "USDSEK": (8, 12), "USDNOK": (9, 13),
    "USDMXN": (15, 25),
    # Metals
    "XAUUSD": (1_400, 8_000), "XAGUSD": (15, 200),
    "XPDUSD": (700, 3_000), "XPTUSD": (700, 2_200),
    # Indices
    "US500": (3_000, 12_000), "NAS100": (8_000, 35_000),
    "US30": (25_000, 60_000), "US2000": (1_200, 3_500),
    "GER40": (12_000, 30_000), "UK100": (6_000, 13_000),
    "FRA40": (5_000, 12_000), "EUSTX50": (3_000, 8_000),
    "EU50": (3_000, 8_000), "JPN225": (15_000, 100_000),
    "AUS200": (5_000, 12_000), "HK50": (13_000, 35_000),
    # Commodities
    "USOIL": (30, 130), "UKOIL": (30, 140), "CRUDE": (30, 130),
    "BRENT": (30, 140), "NATGAS": (1.0, 20.0), "CORN": (300, 900),
    # Crypto
    "BTCUSD": (10_000, 250_000), "ETHUSD": (500, 15_000),
}


# ── Connection + session state ────────────────────────────────────────────────
_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None

_symbol_by_name: dict[str, dict] = {}     # SYMBOLNAME -> {symbol_id, symbol_name, base_name, point_size}
_symbols_by_base: dict[str, list[dict]] = {}  # BASE -> [entries]
_pip_digits_cache: dict[str, int] = {}


def _get_conn() -> http.client.HTTPSConnection:
    global _conn
    if _conn is None:
        _conn = http.client.HTTPSConnection(
            CTRADER_MCP_HOST,
            context=ssl.create_default_context(),
            timeout=20,
        )
    return _conn


def _post(payload: dict, session_id: Optional[str] = None) -> tuple[Optional[dict], Optional[str]]:
    global _conn, _session_id
    body = json.dumps(payload)
    headers = {
        "Authorization": f"Bearer {CTRADER_MCP_TOKEN}",
        "Accept": "application/json, text/event-stream",
        "Content-Type": "application/json",
    }
    if session_id:
        headers["Mcp-Session-Id"] = session_id

    for attempt in range(2):
        try:
            conn = _get_conn()
            conn.request("POST", CTRADER_MCP_PATH, body, headers)
            resp = conn.getresponse()
            new_sid = (resp.getheader("Mcp-Session-Id")
                       or resp.getheader("mcp-session-id")
                       or session_id)
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
        "jsonrpc": "2.0",
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "trend-continuation-agent", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def call_tool(tool: str, arguments: dict, retries: int = 1) -> Optional[dict]:
    """
    Call a cTrader MCP tool. Reinitialises session once on expiry.
    Retries once after a 2s delay on total failure (spec §2 error handling).

    Returns the parsed tool result on success. On a JSON-RPC error or an
    MCP tool-execution error (`result.isError`), returns {"error": <message>}
    so callers placing orders can surface the broker's actual rejection
    reason verbatim (spec §6). Returns None only on a transport/session
    failure (no response received at all).
    """
    global _session_id

    for attempt in range(retries + 1):
        if not _ensure_session():
            if attempt < retries:
                time.sleep(2)
                continue
            return None

        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {"name": tool, "arguments": arguments},
            "id": 1,
        }

        data, new_sid = _post(payload, _session_id)

        expired = (
            (data and data.get("_session_expired"))
            or (data and "error" in data and "session" in data.get("error", {}).get("message", "").lower())
        )
        if expired:
            _session_id = None
            if not _ensure_session():
                if attempt < retries:
                    time.sleep(2)
                    continue
                return None
            data, new_sid = _post(payload, _session_id)

        if new_sid:
            _session_id = new_sid

        if data and "error" in data:
            return {"error": data["error"].get("message", data["error"])}

        if data and "result" in data:
            result = data["result"]
            content = result.get("content", [])
            text = content[0]["text"] if content and content[0].get("type") == "text" else None

            if result.get("isError"):
                return {"error": text if text is not None else result}

            if text is not None:
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    return {"error": text}

            return None

        if attempt < retries:
            time.sleep(2)
            continue

    return None


# ── Symbol resolution ──────────────────────────────────────────────────────────
def _strip_suffix(name: str) -> str:
    for suffix in ("_SBE", "_SB", "-F_SB", "-F"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def load_symbols(force_refresh: bool = False) -> None:
    """Load the enabled-symbol map from the cached JSON, or fetch live if missing/forced."""
    global _symbol_by_name, _symbols_by_base

    if _symbol_by_name and not force_refresh:
        return

    entries: list[dict] = []

    if not force_refresh and os.path.exists(SB_SYMBOL_CACHE):
        try:
            with open(SB_SYMBOL_CACHE) as f:
                entries = json.load(f).get("symbols", [])
        except (OSError, json.JSONDecodeError):
            entries = []

    if not entries:
        result = call_tool("get_symbols", {})
        if result:
            for sym in result.get("symbols", []):
                if not sym.get("enabled", False):
                    continue
                name = sym.get("symbolName") or ""
                sid = sym.get("symbolId")
                if not name or sid is None:
                    continue
                desc = sym.get("description", "")
                point_size = None
                if "bet in 1 GBP per (" in desc:
                    try:
                        point_size = float(desc.split("bet in 1 GBP per (")[1].split(")")[0])
                    except (ValueError, IndexError):
                        point_size = None
                entries.append({
                    "symbol_id": int(sid),
                    "symbol_name": name,
                    "base_name": _strip_suffix(name.upper()),
                    "point_size": point_size,
                    "description": desc,
                })

    for entry in entries:
        _symbol_by_name[entry["symbol_name"].upper()] = entry
        _symbols_by_base.setdefault(entry["base_name"].upper(), []).append(entry)


def list_base_names() -> list[str]:
    """All distinct base instrument names available in the enabled SB symbol
    map (used for --full-universe-all)."""
    load_symbols()
    return sorted(_symbols_by_base.keys())


def resolve_symbol(base_name: str) -> Optional[dict]:
    """
    Resolve a config instrument name (e.g. 'UK100', 'EU50') to its enabled SB
    symbol entry: {symbol_id, symbol_name, base_name, point_size}.

    Prefers non-forward ('-F') variants when multiple matches exist.
    """
    load_symbols()
    key = base_name.upper().replace(" ", "")

    # Config name -> broker base_name special-cases (per spec: fuzzy match on
    # base name). This broker lists the EU index as "EUSTX50" and oil as
    # "Crude" (WTI) / "Brent" rather than "USOIL" / "UKOIL".
    aliases = {"EU50": "EUSTX50", "USOIL": "CRUDE", "UKOIL": "BRENT"}
    candidates_keys = [key, aliases.get(key, key)]

    for k in candidates_keys:
        # Exact symbol name match: KEY_SB
        exact = _symbol_by_name.get(f"{k}_SB")
        if exact:
            return exact

        matches = _symbols_by_base.get(k, [])
        if matches:
            non_forward = [m for m in matches if "-F" not in m["symbol_name"].upper()]
            return (non_forward or matches)[0]

    # Fuzzy fallback: any base_name starting with / contained in key
    for base, matches in _symbols_by_base.items():
        if base.startswith(key) or key.startswith(base):
            non_forward = [m for m in matches if "-F" not in m["symbol_name"].upper()]
            return (non_forward or matches)[0]

    return None


def _pip_digits(base_name: str, raw_sample: Optional[float]) -> int:
    key = base_name.upper()
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]

    lo, hi = PRICE_RANGES.get(key, (0, 0))
    if raw_sample and lo and hi:
        for digits in range(0, 8):
            display = raw_sample / (10 ** digits)
            if lo <= display <= hi:
                _pip_digits_cache[key] = digits
                return digits

    # Sensible default: 5 for FX-style, 2 for everything else
    default = 5 if key.endswith("USD") or key.endswith("JPY") or "JPY" in key or len(key) == 6 else 2
    _pip_digits_cache[key] = default
    return default


def get_pip_digits(base_name: str) -> int:
    """Public accessor — ensures pip-digit detection has run for `base_name`
    (fetches a live quote as a side effect if not already cached)."""
    sym = resolve_symbol(base_name)
    key = (sym["base_name"] if sym else base_name).upper()
    if key not in _pip_digits_cache:
        get_spot_price(base_name)
    return _pip_digits_cache.get(key, 5 if len(key) == 6 else 2)


def to_raw_points(base_name: str, display_distance: float) -> int:
    """Convert a display-price distance to raw 'points' (pipettes), as
    required by `relativeStopLoss` / `relativeTakeProfit` on MARKET orders."""
    digits = get_pip_digits(base_name)
    return max(1, round(display_distance * (10 ** digits)))


def round_price(base_name: str, price: float) -> float:
    """Round an absolute price to the symbol's allowed display precision
    (pip digits), as required by `limitPrice`/`stopPrice`/`stopLoss`/
    `takeProfit` on LIMIT/STOP orders — the broker rejects prices with more
    decimal places than the symbol allows."""
    digits = get_pip_digits(base_name)
    return round(price, digits)


def _ts_to_utc(raw: int) -> datetime:
    if raw > 1_000_000_000_000:
        ts = raw / 1000
    elif raw > 1_000_000_000:
        ts = float(raw)
    else:
        ts = raw * 60.0
    return datetime.fromtimestamp(ts, tz=timezone.utc)


# ── Market data ─────────────────────────────────────────────────────────────────
# The live get_trendbars tool rejects `count` alone ("fromTimestamp: must not
# be null") despite its description — fromTimestamp+toTimestamp is required,
# capped at 720h (30 days) per call ("Split into 720h-or-smaller windows and
# call this tool multiple times" — confirmed via a live HTTP 400). 210 x 4H
# bars need ~840h of calendar range, so we walk back in <=720h windows and
# merge until `count` bars are collected.
_MAX_RANGE_HOURS = 720.0
_MAX_WINDOWS = 4  # 4 x 720h = 120 days back — comfortably covers 210 x 4H bars


def get_trendbars(base_name: str, period: str, count: int) -> Optional[list[Bar]]:
    """
    Fetch the most recent `count` bars for `base_name` (e.g. 'UK100', '4H'/'1H').
    period: '4H' or '1H' (mapped to cTrader 'H_4' / 'H_1').
    Returns None on resolution/data failure (caller applies §2 error handling).
    """
    sym = resolve_symbol(base_name)
    if sym is None:
        return None

    period_map = {"4H": "H_4", "1H": "H_1", "H4": "H_4", "H1": "H_1"}
    ctrader_period = period_map.get(period.upper(), period)

    bars_by_ts: dict[int, Bar] = {}
    pip_div: Optional[float] = None
    window_end = datetime.now(timezone.utc)

    for _ in range(_MAX_WINDOWS):
        window_start = window_end - timedelta(hours=_MAX_RANGE_HOURS)

        result = call_tool("get_trendbars", {
            "symbolId": sym["symbol_id"],
            "period": ctrader_period,
            "fromTimestamp": window_start.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toTimestamp": window_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "count": count,
        }, retries=1)

        if not result:
            break

        bars_raw = (result.get("trendbars") or result.get("trendBars")
                    or result.get("bars") or result.get("data") or [])
        if not bars_raw:
            break

        if pip_div is None:
            pip_div = 10 ** _pip_digits(sym["base_name"], bars_raw[0].get("close", 0))

        for b in bars_raw:
            try:
                ts_raw = (b.get("utcTimestamp") or b.get("timestamp")
                          or b.get("utcTimestampInMinutes") or b.get("time") or 0)
                o = b.get("open", 0) / pip_div
                h = b.get("high", 0) / pip_div
                l = b.get("low", 0) / pip_div
                c = b.get("close", 0) / pip_div
                v = float(b.get("tickVolume") or b.get("volume") or 0)
                if not (l > 0 and h >= l and o >= l and c >= l):
                    continue
                bars_by_ts[int(ts_raw)] = Bar(
                    timestamp=_ts_to_utc(int(ts_raw)),
                    open=o, high=h, low=l, close=c, volume=v,
                )
            except (KeyError, TypeError, ValueError, OSError):
                continue

        if len(bars_by_ts) >= count:
            break
        window_end = window_start

    if not bars_by_ts:
        return None

    bars = sorted(bars_by_ts.values(), key=lambda x: x.timestamp)
    return bars[-count:]


def get_spot_price(base_name: str) -> Optional[tuple[float, float]]:
    """Returns (bid, ask) in display price, or None."""
    sym = resolve_symbol(base_name)
    if sym is None:
        return None

    result = call_tool("get_spot_prices", {"symbolId": [sym["symbol_id"]]}, retries=1)
    if not result:
        return None

    prices = result.get("prices") or result.get("spotPrices") or []
    if not prices:
        return None

    p = prices[0]
    raw_bid = p.get("bid", 0)
    raw_ask = p.get("ask", 0)
    if not raw_bid or not raw_ask:
        return None

    pip_div = 10 ** _pip_digits(sym["base_name"], raw_bid)
    return (raw_bid / pip_div, raw_ask / pip_div)


def get_balance() -> Optional[dict]:
    result = call_tool("get_balance", {})
    if not result:
        return None
    divisor = 10 ** result.get("moneyDigits", 2)
    return {
        "balance": result["balance"] / divisor,
        "equity": result["equity"] / divisor,
        "free_margin": result["freeMargin"] / divisor,
    }


def get_open_positions() -> list[dict]:
    result = call_tool("get_positions", {})
    if not result:
        return []
    return result.get("positions", [])


def create_market_order(symbol_id: int, trade_side: str, volume: int,
                         relative_sl_points: int, relative_tp_points: int,
                         label: str = "TREND-CONTINUATION") -> Optional[dict]:
    """Place a MARKET order with SL/TP1 as relative point distances (per cTrader API for MARKET orders)."""
    return call_tool("create_order", {
        "symbolId": symbol_id,
        "orderType": "MARKET",
        "tradeSide": trade_side,
        "volume": volume,
        "relativeStopLoss": relative_sl_points,
        "relativeTakeProfit": relative_tp_points,
        "label": label,
    })


def create_limit_order(symbol_id: int, trade_side: str, volume: int,
                        limit_price: float, label: str = "TREND-CONTINUATION") -> Optional[dict]:
    """Place a LIMIT order (used for TP2/TP3 partial-close legs)."""
    return call_tool("create_order", {
        "symbolId": symbol_id,
        "orderType": "LIMIT",
        "tradeSide": trade_side,
        "volume": volume,
        "limitPrice": limit_price,
        "label": label,
    })
