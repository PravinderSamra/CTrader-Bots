# cTrader MCP Integration Guide
## Complete Implementation for Python Trading Agents

---

## Account Context

| Setting | Value |
|---|---|
| MCP endpoint | `https://mcp.ctrader.com/trading/mcp` |
| Account type | Pepperstone UK GBP Spread Betting (demo) |
| Account currency | GBP (depositAssetId=6, moneyDigits=2) |
| Demo balance | ~£47,596 |
| Symbol suffix | All tradeable symbols end in `_SB` |
| Live token | Set via `CTRADER_MCP_TOKEN` env var — never hardcode |

**Demo bearer token** (already in `.mcp.json`):
```
eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0
```

---

## Lesson 1 — CRITICAL: Use Persistent HTTPS Connection

### What Failed

Using `urllib.request` with `"Connection: close"` header caused HTTP 404 "Session not found" errors on ~60% of tool calls. The MCP server is load-balanced. With `Connection: close`, each request lands on a different backend instance that has no record of the session. This presents as random intermittent failures and is very hard to debug.

### What Works

Use `http.client.HTTPSConnection` (keep-alive). All requests within the same Python process use the same TCP connection and hit the same backend instance.

Also critical: send `notifications/initialized` after `initialize` to complete the MCP handshake. Without it, some tools silently return session errors.

### Complete Working Connection Infrastructure

```python
import http.client
import ssl
import json
import os
from datetime import datetime, timezone, timedelta
from typing import Optional

_MCP_HOST = "mcp.ctrader.com"
_MCP_PATH = "/trading/mcp"

_TOKEN = os.environ.get(
    "CTRADER_MCP_TOKEN",
    "eyJwbGFudCI6InBlcHBlcnN0b25ldWsiLCJlbnZpcm9ubWVudCI6ImRlbW8iLCJ0b2tlbiI6IkliMEJzUERzSXBpZUJnTEtUWTluRjRpMEJ6a3R4V0pvSm1ZNVB3a1lIb2c9In0"
)

_conn: Optional[http.client.HTTPSConnection] = None
_session_id: Optional[str] = None


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
            # Connection dropped — reset and retry once on a fresh connection
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
        "method":  "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities":    {},
            "clientInfo":      {"name": "trade-picker", "version": "1.0"},
        },
        "id": 0,
    })

    if data and "result" in data and sid:
        _session_id = sid
        # REQUIRED — completes the MCP handshake; some tools fail without this
        _post({"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}}, sid)
        return True
    return False


def _call_tool(tool: str, arguments: dict) -> Optional[dict]:
    global _session_id

    if not _ensure_session():
        return None

    payload = {
        "jsonrpc": "2.0",
        "method":  "tools/call",
        "params":  {"name": tool, "arguments": arguments},
        "id":      1,
    }

    data, new_sid = _post(payload, _session_id)

    # Session expired — reinitialise and retry once
    expired = (
        (data and data.get("_session_expired")) or
        (data and "error" in data and "session" in data.get("error", {}).get("message", "").lower())
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
```

---

## Lesson 2 — Symbol Names: All Enabled Symbols Have `_SB` Suffix

On this Pepperstone UK spread betting account, every tradeable symbol ends in `_SB`. Non-`_SB` variants exist in `get_symbols()` but have `"enabled": false`.

> **Warning**: If you use a disabled symbolId you will get `"minimum volume = 999999999999"` errors. This is the sentinel value meaning the symbol is disabled — it is not a real volume limit.

### Confirmed symbolId Map

| Instrument | Symbol | symbolId |
|---|---|---|
| Dow Jones | US30_SB | 219 |
| S&P 500 | US500_SB | 220 |
| NASDAQ 100 | NAS100_SB | 205 |
| DAX | GER40_SB | 200 |
| FTSE 100 | UK100_SB | 217 |
| Nikkei 225 | JPN225_SB | 203 |
| ASX 200 | AUS200_SB | 159 |
| Hang Seng | HK50_SB | 201 |
| CAC 40 | FRA40_SB | 188 |
| Euro Stoxx 50 | EUSTX50_SB | 187 |
| EUR/USD | EURUSD_SB | 185 |
| GBP/USD | GBPUSD_SB | 199 |
| USD/JPY | USDJPY_SB | 226 |
| USD/CHF | USDCHF_SB | 222 |
| USD/CAD | USDCAD_SB | 221 |
| AUD/USD | AUDUSD_SB | 158 |
| NZD/USD | NZDUSD_SB | 211 |
| GBP/JPY | GBPJPY_SB | 192 |
| EUR/JPY | EURJPY_SB | 177 |
| AUD/JPY | AUDJPY_SB | 155 |
| EUR/GBP | EURGBP_SB | 175 |
| GBP/AUD | GBPAUD_SB | 189 |
| EUR/CAD | EURCAD_SB | 172 |
| GBP/CAD | GBPCAD_SB | 190 |
| Gold | XAUUSD_SB | 241 |
| Silver | XAGUSD_SB | 238 |
| WTI Crude | Crude_SB | 252 |
| Brent Crude | Brent_SB | 253 |
| Natural Gas | NatGas_SB | 254 |

> **Note**: Crypto (BTC, ETH, SOL) is **not available** on this spread betting account.

### Symbol Resolution Code

Only caches enabled symbols. Strips `_SB` suffix so `"US30"` automatically resolves to `US30_SB`.

```python
_symbol_id_cache: dict[str, int] = {}
_symbols_loaded: bool = False


def _strip_suffix(name: str) -> str:
    """Remove account-type suffixes. US30_SB -> US30, XAUUSD-F -> XAUUSD."""
    for suffix in ("_SBE", "_SB", "-F_SB", "-F"):
        if name.endswith(suffix):
            return name[: -len(suffix)]
    return name


def _load_symbols() -> None:
    """Cache ENABLED symbols only. Called once per session."""
    global _symbols_loaded
    if _symbols_loaded:
        return

    result = _call_tool("get_symbols", {})
    if not result:
        return

    for sym in result.get("symbols", []):
        if not sym.get("enabled", False):
            continue  # skip disabled — their symbolIds reject orders
        raw_name = sym.get("symbolName") or ""
        sid = sym.get("symbolId")
        if raw_name and sid is not None:
            sid_int = int(sid)
            _symbol_id_cache[raw_name.upper()] = sid_int
            base = _strip_suffix(raw_name.upper())
            if base != raw_name.upper():
                _symbol_id_cache.setdefault(base, sid_int)

    _symbols_loaded = True


def get_symbol_id(instrument: str) -> Optional[int]:
    """Resolve an instrument name to its cTrader symbolId (enabled only)."""
    _load_symbols()
    key = instrument.upper().split(".")[0]

    if key in _symbol_id_cache:
        return _symbol_id_cache[key]

    base = _strip_suffix(key)
    if base in _symbol_id_cache:
        return _symbol_id_cache[base]

    for name, sid in _symbol_id_cache.items():
        if _strip_suffix(name) == base:
            return sid

    return None
```

---

## Lesson 3 — Correct API Parameter Names

Several parameters differ from what you would expect. Wrong names produce silent 400 errors.

### `get_trendbars` — OHLCV Candles

```python
# CORRECT
result = _call_tool("get_trendbars", {
    "symbolId":      219,                        # integer, NOT a list
    "period":        "H_1",                      # NOT "timeframe", NOT "H1"
    "fromTimestamp": "2026-06-01T00:00:00Z",     # ISO string — REQUIRED
    "toTimestamp":   "2026-06-02T12:00:00Z",     # ISO string — REQUIRED
})

# WRONG — these all cause errors:
# "timeframe": "H1"          → 400 "Invalid option"
# "count": 100               → 400 "fromTimestamp must not be null"
# "fromTimestamp": 1780000000000  → 400 "expected string, received number"
```

Valid `period` values: `"M_1"` `"M_5"` `"M_15"` `"M_30"` `"H_1"` `"H_4"` `"D_1"` `"W_1"` `"MN_1"`

### `get_spot_prices` — Live Bid/Ask

```python
# CORRECT — key is "symbolId" (singular), value is an array
result = _call_tool("get_spot_prices", {"symbolId": [219, 185, 199]})

# WRONG — plural causes "received undefined" validation error
result = _call_tool("get_spot_prices", {"symbolIds": [219]})
```

### `get_balance` — Account Balance

```python
result = _call_tool("get_balance", {})
# Returns: {"balance": 4759674, "equity": 4759674, "freeMargin": 4759674,
#           "moneyDigits": 2, "depositAssetId": 6}
# Display: 4759674 / 10^2 = £47,596.74
```

### `get_positions` — Open Positions

```python
result = _call_tool("get_positions", {})
# Returns: {"positions": [...], "orders": [...]}
# IMPORTANT: entryPrice, stopLoss, takeProfit are ALREADY display prices
# Do NOT divide by pip divisor — they are not in pipettes
```

### `create_order` — Place a Trade

```python
result = _call_tool("create_order", {
    "symbolId":   219,          # integer
    "orderType":  "LIMIT",      # or "MARKET"
    "tradeSide":  "BUY",        # or "SELL"
    "volume":     1100,         # see Lesson 5 for sizing
    "limitPrice": 51200.0,      # display price (NOT pipettes)
    "stopLoss":   51159.0,      # display price
    "takeProfit": 51241.0,      # display price
    "label":      "MY-LABEL"
})
```

### Other Order Tools

```python
_call_tool("cancel_order",   {"orderId":    64923913})
_call_tool("close_position", {"positionId": 50202484})
```

---

## Lesson 4 — Price Format: Pipettes vs Display

**Raw prices from `get_spot_prices` and `get_trendbars` are in pipettes** (large integers). Divide by `10^N` to get the display price. `N` varies by symbol and must be auto-detected.

**Prices in `get_positions` responses and all order inputs are already in display format.**

| Symbol | Raw pipette price | N | Display price |
|---|---|---|---|
| EURUSD_SB | 116313 | 5 | 1.16313 |
| GBPUSD_SB | 130450 | 5 | 1.30450 |
| US30_SB | 5120200000 | 5 | 51202.0 |
| XAUUSD_SB | 448944000 | 5 | 4489.44 |
| NatGas_SB | 280000 | 4 | 28.00 |

### Auto-Detect Pip Digits

```python
_PRICE_RANGES = {
    "EURUSD": (0.80, 1.60),    "GBPUSD": (1.00, 1.70),
    "AUDUSD": (0.50, 1.10),    "NZDUSD": (0.40, 0.90),
    "USDCHF": (0.75, 1.20),    "USDCAD": (1.10, 1.65),
    "USDJPY": (100, 200),      "GBPJPY": (150, 260),
    "EURJPY": (110, 190),      "AUDJPY": (60,  130),
    "EURGBP": (0.70, 0.95),    "GBPAUD": (1.60, 2.30),
    "EURCAD": (1.30, 1.90),    "GBPCAD": (1.60, 2.20),
    "XAUUSD": (1400, 8000),    "XAGUSD": (15, 200),
    "US500":  (3000, 12000),   "NAS100": (8000, 35000),
    "US30":   (25000, 60000),  "GER40":  (12000, 30000),
    "UK100":  (6000, 13000),   "FRA40":  (5000, 12000),
    "EUSTX50":(3000, 8000),    "JPN225": (15000, 100000),
    "AUS200": (5000, 12000),   "HK50":   (13000, 35000),
    "CRUDE":  (30, 130),       "BRENT":  (30, 140),
    "NATGAS": (1.0, 20.0),
}

_pip_digits_cache: dict[str, int] = {}


def detect_pip_digits(symbol_base: str, raw_price: float) -> int:
    """Find N such that raw_price / 10^N falls in the known display range."""
    key = _strip_suffix(symbol_base.upper())
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]
    lo, hi = _PRICE_RANGES.get(key, (0, 0))
    if lo and hi and raw_price > 0:
        for n in range(0, 10):
            display = raw_price / (10 ** n)
            if lo <= display <= hi:
                _pip_digits_cache[key] = n
                return n
    return 5  # fallback
```

---

## Lesson 5 — Volume Sizing for Spread Betting

> This is **not** the standard cTrader forex formula (`lots × lotSize × 100`). Spread betting uses stake-per-point.

**Each 1 unit of volume = £1 per point movement.**

```
volume = round(risk_gbp / stop_distance_points) * 100
```

Minimum volume: `100` (= £1/point). Step size: `100`. Always use multiples of 100.

**Example — US30 LONG, £450 risk, 41-point stop:**
```
stake = 450 / 41 = 10.97 → round to 11
volume = 11 × 100 = 1100
actual risk = £11 × 41pts = £451 ✓
```

**Quick reference table (£450 risk):**

| Stop (pts) | Stake (£/pt) | Volume | Actual Risk |
|---|---|---|---|
| 20 | 22.5 → 23 | 2300 | £460 |
| 30 | 15.0 | 1500 | £450 |
| 40 | 11.25 → 11 | 1100 | £440 |
| 50 | 9.0 | 900 | £450 |
| 100 | 4.5 → 5 | 500 | £500 |

---

## Lesson 6 — Don't Use `mcp__ctrader__*` Claude Tools Programmatically

The `mcp__ctrader__*` tools injected via `.mcp.json` use a separate session layer that expires frequently in the Claude web app (especially on iPhone/browser). You will get `None` returns or "session expired" errors seemingly at random.

**Always use direct Python HTTP calls via `_call_tool()` instead.** This gives full session control, proper keep-alive, clean retry logic, and works reliably from any Python script or analysis pipeline.

---

## Lesson 7 — Timestamp Format for `get_trendbars`

`fromTimestamp` and `toTimestamp` must be ISO 8601 strings. Integer milliseconds cause a `"expected string, received number"` 400 error.

```python
from datetime import datetime, timezone, timedelta

def make_time_range(hours_back: int) -> tuple[str, str]:
    to_dt   = datetime.now(tz=timezone.utc)
    from_dt = to_dt - timedelta(hours=min(hours_back, 720))  # max 720h per request
    return (
        from_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        to_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    )
```

> API hard limit: maximum range is **720 hours (30 days)** per request. For more history, use sliding windows.

---

## Complete Ready-to-Use Functions

Paste these after the infrastructure from Lessons 1 and 2:

```python
def fetch_ohlcv(instrument: str, timeframe: str = "H_1", hours_back: int = 100) -> list[dict]:
    """
    Fetch OHLCV candles from cTrader.
    timeframe: "M_1", "M_5", "M_15", "M_30", "H_1", "H_4", "D_1", "W_1"
    Returns list of dicts with keys: time, open, high, low, close, volume
    """
    sym_id = get_symbol_id(instrument)
    if sym_id is None:
        return []

    to_dt   = datetime.now(tz=timezone.utc)
    from_dt = to_dt - timedelta(hours=min(hours_back, 720))

    result = _call_tool("get_trendbars", {
        "symbolId":      sym_id,
        "period":        timeframe,
        "fromTimestamp": from_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "toTimestamp":   to_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
    })
    if not result:
        return []

    bars = result.get("trendbars") or result.get("trendBars") or result.get("bars") or []
    if not bars:
        return []

    base    = _strip_suffix(instrument.upper())
    pip_div = 10 ** detect_pip_digits(base, bars[0].get("close", 1))

    candles = []
    for b in bars:
        try:
            candles.append({
                "time":   datetime.fromtimestamp(b["timestamp"] / 1000, tz=timezone.utc),
                "open":   b["open"]  / pip_div,
                "high":   b["high"]  / pip_div,
                "low":    b["low"]   / pip_div,
                "close":  b["close"] / pip_div,
                "volume": b.get("tickVolume") or b.get("volume") or 0,
            })
        except (KeyError, TypeError, ZeroDivisionError):
            continue

    candles.sort(key=lambda c: c["time"])
    return candles


def get_live_price(instrument: str) -> Optional[tuple[float, float]]:
    """Returns (bid, ask) in display price, or None if unavailable."""
    sym_id = get_symbol_id(instrument)
    if sym_id is None:
        return None

    result = _call_tool("get_spot_prices", {"symbolId": [sym_id]})
    if not result or not result.get("prices"):
        return None

    p = result["prices"][0]
    base    = _strip_suffix(instrument.upper())
    raw_bid = p.get("bid", 0)
    if not raw_bid:
        return None
    pip_div = 10 ** detect_pip_digits(base, raw_bid)
    return (raw_bid / pip_div, p["ask"] / pip_div)


def get_account_balance() -> Optional[dict]:
    """Returns balance info in GBP display values."""
    result = _call_tool("get_balance", {})
    if not result:
        return None
    divisor = 10 ** result.get("moneyDigits", 2)
    return {
        "balance_gbp":     result["balance"]   / divisor,
        "equity_gbp":      result["equity"]    / divisor,
        "free_margin_gbp": result["freeMargin"] / divisor,
    }


def get_open_positions() -> list[dict]:
    """
    Returns list of open positions.
    NOTE: entryPrice, stopLoss, takeProfit are already in display format.
    """
    result = _call_tool("get_positions", {})
    if not result:
        return []
    return result.get("positions", [])


def place_order(
    instrument: str,
    side: str,                    # "BUY" or "SELL"
    entry_price: float,
    stop_loss: float,
    take_profit: float,
    risk_gbp: float = 450.0,
    order_type: str = "LIMIT",    # "LIMIT" or "MARKET"
    label: str = "TRADE-PICKER",
) -> Optional[dict]:
    """
    Place a LIMIT or MARKET order with automatic GBP spread-bet position sizing.

    Sizing: volume = round(risk_gbp / |entry - stop_loss|) * 100
    Each 100 volume = £1/point stake.
    """
    sym_id = get_symbol_id(instrument)
    if sym_id is None:
        return None

    stop_pts = abs(entry_price - stop_loss)
    if stop_pts == 0:
        return None

    stake  = risk_gbp / stop_pts
    volume = max(100, round(stake) * 100)

    args = {
        "symbolId":   sym_id,
        "orderType":  order_type,
        "tradeSide":  side,
        "volume":     volume,
        "stopLoss":   stop_loss,
        "takeProfit": take_profit,
        "label":      label,
    }
    if order_type == "LIMIT":
        args["limitPrice"] = entry_price

    return _call_tool("create_order", args)


def cancel_order(order_id: int) -> Optional[dict]:
    return _call_tool("cancel_order", {"orderId": order_id})


def close_position(position_id: int) -> Optional[dict]:
    return _call_tool("close_position", {"positionId": position_id})
```

---

## Using cTrader Data for ICT/SMC Analysis

Because cTrader returns 24/7 CFD prices, the analysis is cleaner than Yahoo Finance:

- **No phantom FVGs** — Yahoo Finance returns market-hours-only data for US indices, creating fake FVGs across overnight gaps. cTrader data is continuous.
- **Exact broker prices** — what you see on your cTrader chart is exactly what the scanner analyses.

**Recommended data pull for full ICT/SMC analysis:**

```python
# 100 hourly candles for FVG/OB/liquidity detection
candles_1h = fetch_ohlcv(symbol, timeframe="H_1", hours_back=100)

# 20 daily candles for PDH/PDL and HTF trend
candles_1d = fetch_ohlcv(symbol, timeframe="D_1", hours_back=480)  # 480h = 20 days

# Live price for session bias and P/D zone
bid, ask = get_live_price(symbol)
current_price = (bid + ask) / 2
```

---

## Confirmed Working Live Trade (Reference)

Placed and filled on demo account:

| Field | Value |
|---|---|
| Symbol | US30_SB (symbolId 219) |
| Side | BUY LIMIT |
| Entry | 51200 (filled) |
| Stop Loss | 51159 (-41pts) |
| Take Profit | 51241 (+41pts, 1:1 R/R) |
| Volume | 1100 (= £11/point) |
| Risk | £451 |
| Order ID | 64923974 |
| Position ID | 50202484 |

**`create_order` response on success:**
```json
{
  "executionType": "ORDER_ACCEPTED",
  "position": {
    "positionId": 50202484,
    "tradeSide": "BUY",
    "volume": 1100,
    "entryPrice": 51200,
    "stopLoss": 51159,
    "takeProfit": 51241
  }
}
```

---

## Quick Start Checklist

- [ ] Copy connection infrastructure from Lesson 1 (`_post`, `_ensure_session`, `_call_tool`)
- [ ] Copy symbol resolution from Lesson 2 (`_strip_suffix`, `_load_symbols`, `get_symbol_id`)
- [ ] Copy `_PRICE_RANGES` and `detect_pip_digits` from Lesson 4
- [ ] Copy complete ready-to-use functions (`fetch_ohlcv`, `get_live_price`, `place_order`, etc.)
- [ ] Run confluence analysis on candles from `fetch_ohlcv()`
- [ ] Call `place_order()` when a setup is confirmed
- [ ] For live FTMO account: set `CTRADER_MCP_TOKEN` in `.env` — never hardcode it
- [ ] Do **not** use `mcp__ctrader__*` Claude tools for programmatic calls — use `_call_tool()` directly
