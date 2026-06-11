"""
/Trend-Continuation-Agent — Sub-Agent 1: Data Retrieval

Spec §2. Fetches 4H + 1H OHLCV and a live spot price for each instrument via
cTrader MCP HTTP, sequentially per instrument (per spec, to keep the HTTP
session stable).

Error handling (spec §2):
  - Symbol not found in the SB symbol map -> "SYMBOL_NOT_FOUND" -> skip silently.
  - MCP call fails (after mcp_client's internal 2s retry) -> "DATA_FAIL" -> skip.
  - Fewer than MIN_BARS completed bars on either timeframe -> "INSUFFICIENT_DATA" -> skip.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from config import BARS_4H, BARS_4H_USED, BARS_1H, BARS_1H_USED
from utils import mcp_client
from utils.mcp_client import Bar
from utils.time_utils import now_utc

# Spec §2: "Partial data (< 150 bars) -> Skip — ADX/EMA calculations are unreliable."
MIN_BARS = 150


@dataclass
class InstrumentData:
    symbol: str            # config name, e.g. "UK100"
    sb_symbol: str         # resolved SB symbol name, e.g. "UK100_SB"
    symbol_id: int
    point_size: Optional[float]
    bars_4h: list[Bar]     # last BARS_4H_USED completed bars, oldest first
    bars_1h: list[Bar]     # last BARS_1H_USED completed bars, oldest first
    spot_bid: float
    spot_ask: float


def _drop_incomplete_bar(bars: list[Bar], tf_minutes: int) -> list[Bar]:
    """Drop the trailing bar if its close time is still in the future, i.e.
    it's the currently-forming bar. Spec §12: index -1 must be the latest
    COMPLETED bar."""
    if not bars:
        return bars
    close_time = bars[-1].timestamp.timestamp() + tf_minutes * 60
    if close_time > now_utc().timestamp():
        return bars[:-1]
    return bars


def fetch_instrument(symbol: str, log: list[str]) -> Optional[InstrumentData]:
    """Fetch 4H + 1H bars and live price for one instrument."""
    sym = mcp_client.resolve_symbol(symbol)
    if sym is None:
        log.append(f"SYMBOL_NOT_FOUND: {symbol}")
        return None

    bars_4h_raw = mcp_client.get_trendbars(symbol, "4H", BARS_4H)
    if not bars_4h_raw:
        log.append(f"DATA_FAIL: {symbol} (4H bars)")
        return None
    bars_4h = _drop_incomplete_bar(bars_4h_raw, 240)[-BARS_4H_USED:]
    if len(bars_4h) < MIN_BARS:
        log.append(f"INSUFFICIENT_DATA: {symbol} (4H, {len(bars_4h)} bars)")
        return None

    bars_1h_raw = mcp_client.get_trendbars(symbol, "1H", BARS_1H)
    if not bars_1h_raw:
        log.append(f"DATA_FAIL: {symbol} (1H bars)")
        return None
    bars_1h = _drop_incomplete_bar(bars_1h_raw, 60)[-BARS_1H_USED:]
    if len(bars_1h) < MIN_BARS:
        log.append(f"INSUFFICIENT_DATA: {symbol} (1H, {len(bars_1h)} bars)")
        return None

    spot = mcp_client.get_spot_price(symbol)
    if spot is None:
        log.append(f"DATA_FAIL: {symbol} (spot price)")
        return None

    return InstrumentData(
        symbol=symbol,
        sb_symbol=sym["symbol_name"],
        symbol_id=sym["symbol_id"],
        point_size=sym.get("point_size"),
        bars_4h=bars_4h,
        bars_1h=bars_1h,
        spot_bid=spot[0],
        spot_ask=spot[1],
    )


def fetch_all(symbols: list[str]) -> tuple[dict[str, InstrumentData], list[str]]:
    """Sequentially fetch data for all symbols. Returns (data_by_symbol, log)."""
    data: dict[str, InstrumentData] = {}
    log: list[str] = []
    for symbol in symbols:
        result = fetch_instrument(symbol, log)
        if result is not None:
            data[symbol] = result
    return data, log
