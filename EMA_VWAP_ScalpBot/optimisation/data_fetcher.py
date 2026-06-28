"""
Fetches and caches GER40/US500 OHLCV data from cTrader MCP.
Saves to CSV in data/ for fast repeated access.
Max 720h (30 days) per MCP call — uses sliding windows for full date range.
"""

import os
import csv
import time
import math
from datetime import datetime, timedelta, timezone, date
from typing import Optional

import mcp_client
from config import SYMBOL_IDS, PIP_DIGITS_FALLBACK, DATA_DIR, DATA_START, DATA_END

# ── Price conversion ─────────────────────────────────────────────────────────

_PRICE_RANGES = {
    "GER40":  (12_000, 30_000),   # pip_digits=5 (verified: raw ~1.96e9 → 19619.5)
    "US500":  (3_000,  12_000),
    "US30":   (25_000, 60_000),
    "NAS100": (8_000,  35_000),
}

_pip_digits_cache: dict[str, int] = {}


def _detect_pip_digits(symbol: str, raw_price: float) -> int:
    key = symbol.upper().replace("_SB", "")
    if key in _pip_digits_cache:
        return _pip_digits_cache[key]
    lo, hi = _PRICE_RANGES.get(key, (0, 0))
    if lo and hi and raw_price > 0:
        for n in range(0, 12):
            display = raw_price / (10 ** n)
            if lo <= display <= hi:
                _pip_digits_cache[key] = n
                return n
    return 7   # GER40/US500 fallback


# ── MCP fetching ──────────────────────────────────────────────────────────────

_PERIOD_MAP = {
    "1H": "H_1",
    "5M": "M_5",
    "1M": "M_1",
}


def _fetch_page(symbol: str, period: str, to_dt: datetime,
                pip_div: int = None, max_retries: int = 3) -> tuple[list[dict], int]:
    """
    Fetch one page (up to 100 bars) from cTrader MCP ending at to_dt.
    Returns (candles, pip_divisor). Uses backward pagination — most recent 100 bars
    with timestamp < to_dt. Caller advances to_dt using earliest returned timestamp.
    Uses a 30-day fromTimestamp window to keep API request range manageable.
    """
    sym_id     = SYMBOL_IDS.get(symbol)
    mcp_period = _PERIOD_MAP.get(period, period)
    if sym_id is None:
        return [], pip_div or 10 ** PIP_DIGITS_FALLBACK.get(symbol, 5)

    from_dt = to_dt - timedelta(days=30)  # 30-day window — within 720h API limit

    for attempt in range(max_retries):
        result = mcp_client.call_tool("get_trendbars", {
            "symbolId":      sym_id,
            "period":        mcp_period,
            "fromTimestamp": from_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "toTimestamp":   to_dt.strftime("%Y-%m-%dT%H:%M:%SZ"),
        })

        if result is None:
            wait = 2 ** attempt
            time.sleep(wait)
            continue

        bars = (result.get("trendbars") or result.get("trendBars")
                or result.get("bars") or [])
        if not bars:
            return [], pip_div or 10 ** PIP_DIGITS_FALLBACK.get(symbol, 5)

        # Auto-detect pip divisor once
        if pip_div is None:
            first_close = bars[0].get("close", 1)
            pip_div = 10 ** _detect_pip_digits(symbol, first_close)

        candles = []
        for b in bars:
            try:
                ts = b.get("timestamp") or b.get("utcTimestampInMinutes", 0) * 60_000
                candles.append({
                    "time":   datetime.fromtimestamp(ts / 1000, tz=timezone.utc),
                    "open":   b["open"]  / pip_div,
                    "high":   b["high"]  / pip_div,
                    "low":    b["low"]   / pip_div,
                    "close":  b["close"] / pip_div,
                    "volume": b.get("tickVolume") or b.get("volume") or 0,
                })
            except (KeyError, TypeError, ZeroDivisionError):
                continue

        candles.sort(key=lambda c: c["time"])
        return candles, pip_div

    return [], pip_div or 10 ** PIP_DIGITS_FALLBACK.get(symbol, 5)


# ── CSV cache layer ───────────────────────────────────────────────────────────

def _csv_path(symbol: str, period: str) -> str:
    return os.path.join(DATA_DIR, f"{symbol}_{period}_{DATA_START.year}_{DATA_END.year}.csv")


def _save_csv(path: str, candles: list[dict]) -> None:
    with open(path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["time", "open", "high", "low", "close", "volume"])
        for c in candles:
            w.writerow([c["time"].isoformat(), c["open"], c["high"],
                        c["low"], c["close"], c["volume"]])


def _load_csv(path: str) -> list[dict]:
    candles = []
    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candles.append({
                "time":   datetime.fromisoformat(row["time"]),
                "open":   float(row["open"]),
                "high":   float(row["high"]),
                "low":    float(row["low"]),
                "close":  float(row["close"]),
                "volume": float(row["volume"]),
            })
    return candles


# ── Public API ────────────────────────────────────────────────────────────────

def fetch_data(symbol: str, period: str, force_refresh: bool = False) -> list[dict]:
    """
    Return a list of OHLCV dicts for the full DATA_START–DATA_END range.
    Loads from CSV cache if available; fetches from cTrader MCP and saves otherwise.
    Saves a checkpoint every 200 pages so interrupted fetches can be resumed.
    """
    path            = _csv_path(symbol, period)
    checkpoint_path = path.replace(".csv", "_partial.csv")

    if not force_refresh and os.path.exists(path):
        # Validate the final CSV covers the full range (must have data near DATA_START)
        bars = _load_csv(path)
        if bars and bars[0]["time"].date() <= (DATA_START + timedelta(days=30)):
            print(f"  Loading cached {symbol} {period} from {path}")
            return bars
        print(f"  Cached file incomplete (earliest: {bars[0]['time'].date() if bars else 'empty'}). Re-fetching…")

    limit_dt = datetime(DATA_START.year, DATA_START.month, DATA_START.day, tzinfo=timezone.utc)
    cursor   = datetime(DATA_END.year,   DATA_END.month,   DATA_END.day, 23, 59, 59, tzinfo=timezone.utc)

    all_bars: list[dict] = []
    seen_times: set      = set()
    pip_div              = None

    # Resume from checkpoint if it exists and force_refresh is False
    if not force_refresh and os.path.exists(checkpoint_path):
        print(f"  Resuming from checkpoint: {checkpoint_path}")
        partial = _load_csv(checkpoint_path)
        for b in partial:
            t = b["time"]
            if t not in seen_times:
                seen_times.add(t)
                all_bars.append(b)
        if all_bars:
            earliest_saved = min(b["time"] for b in all_bars)
            cursor = earliest_saved - timedelta(seconds=1)
            print(f"  Checkpoint: {len(all_bars)} bars, resuming from {earliest_saved.date()}")

    print(f"  Fetching {symbol} {period} from cTrader MCP ({cursor.date()} → {limit_dt.date()}) [backward]…")

    page        = 0
    stall_count = 0

    while cursor > limit_dt:
        page_bars, pip_div = _fetch_page(symbol, period, cursor, pip_div)

        if not page_bars:
            stall_count += 1
            if stall_count >= 3:
                print(f"  No more bars returned. Stopping at cursor {cursor.date()}")
                break
            cursor -= timedelta(days=7)
            continue

        stall_count = 0
        new_bars = 0
        for c in page_bars:
            if c["time"] < limit_dt:
                continue
            k = c["time"]
            if k not in seen_times:
                seen_times.add(k)
                all_bars.append(c)
                new_bars += 1

        earliest = page_bars[0]["time"]
        cursor   = earliest - timedelta(seconds=1)
        page += 1

        if page % 10 == 0 or new_bars > 0:
            oldest = earliest.date() if page_bars else cursor.date()
            print(f"  Page {page:4d}: fetched up to {oldest} | total={len(all_bars):6d} bars")

        # Checkpoint every 200 pages so interrupted fetches can be resumed
        if page % 200 == 0:
            sorted_partial = sorted(all_bars, key=lambda c: c["time"])
            _save_csv(checkpoint_path, sorted_partial)
            print(f"  Checkpoint saved ({len(sorted_partial)} bars)")

        time.sleep(0.25)

    all_bars.sort(key=lambda c: c["time"])
    _save_csv(path, all_bars)
    print(f"  Saved {len(all_bars)} bars → {path}")

    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    return all_bars


def ensure_data(symbol: str = "GER40", periods: list[str] = None,
                force_refresh: bool = False) -> dict[str, list[dict]]:
    """Fetch all required timeframes for a symbol. Returns dict keyed by period."""
    if periods is None:
        periods = ["5M", "1H"]

    data = {}
    for period in periods:
        data[period] = fetch_data(symbol, period, force_refresh=force_refresh)
        print(f"  {symbol} {period}: {len(data[period])} bars total")
    return data
