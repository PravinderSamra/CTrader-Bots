"""
ICT/SMC Market Scanner — Remote Agent
Entry point. Run: python main.py

Fetches data for all FTMO-eligible instruments, runs ICT/SMC analysis,
and prints the pre-session report with FTMO risk context.
"""

import sys
import os
from typing import Optional, List

# Load .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from data.models import Candle, MarketContext
from data.fetchers import yahoo_fetcher, twelve_data_fetcher, okx_fetcher, cot_fetcher, ctrader_fetcher
from analysis import structure, sessions
from reports.pre_session_report import generate_report
from config.settings import INSTRUMENTS, PRIMARY_TF, CONTEXT_TF, DAILY_TF
from config.settings import CANDLE_LIMIT_PRIMARY, CANDLE_LIMIT_DAILY


def _fetch_symbol(inst: dict) -> Optional[tuple[List[Candle], List[Candle], List[Candle], str]]:
    """
    Fetch primary (1H), context (4H), and daily candles for one instrument.
    Returns (candles_1h, candles_4h, candles_1d, actual_source) or None on failure.
    """
    name   = inst["name"]
    src    = inst["source"]
    sym    = inst["symbol"]
    label  = name

    def _try_fetch(source, symbol, tf, limit):
        try:
            if source == "okx":
                return okx_fetcher.fetch_klines(symbol, tf, limit, symbol_label=label)
            elif source == "twelve_data":
                return twelve_data_fetcher.fetch_klines(symbol, tf, limit, symbol_label=label)
            elif source == "yahoo":
                return yahoo_fetcher.fetch_klines(symbol, tf, limit, symbol_label=label)
            elif source == "ctrader":
                return ctrader_fetcher.fetch_klines(symbol, tf, limit, symbol_label=label)
        except Exception as e:
            print(f"    ⚠  {name} fetch error ({source}): {e}", file=sys.stderr)
            return []
        return []

    # Primary 1H
    candles_1h = _try_fetch(src, sym, PRIMARY_TF, CANDLE_LIMIT_PRIMARY)
    actual_source = src

    # Fallback for forex if cTrader fails
    if not candles_1h and inst.get("fallback_source"):
        print(f"    → Falling back to {inst['fallback_source']} for {name}", file=sys.stderr)
        candles_1h = _try_fetch(inst["fallback_source"], inst["fallback_symbol"], PRIMARY_TF, CANDLE_LIMIT_PRIMARY)
        if candles_1h:
            actual_source = inst["fallback_source"]

    if not candles_1h:
        print(f"  ⚠  {name}: Failed to fetch primary data — skipping.", file=sys.stderr)
        return None

    print(f"    ✓ {name}: {len(candles_1h)} × 1H candles", file=sys.stderr)

    # Daily for PDH/PDL (most accurate from the same source)
    candles_1d = _try_fetch(src, sym, DAILY_TF, CANDLE_LIMIT_DAILY)
    if not candles_1d and inst.get("fallback_source"):
        candles_1d = _try_fetch(inst["fallback_source"], inst["fallback_symbol"], DAILY_TF, CANDLE_LIMIT_DAILY)

    return candles_1h, [], candles_1d, actual_source   # 4H omitted for speed — use 1H and daily only


def _build_context(inst: dict, candles_1h: List[Candle], candles_1d: List[Candle], data_source: str) -> MarketContext:
    name = inst["name"]
    price = candles_1h[-1].close

    # Structure analysis on 1H
    pd  = structure.calculate_premium_discount(candles_1h, lookback=50)
    fvgs = structure.detect_fvgs(candles_1h)
    obs  = structure.detect_order_blocks(candles_1h)
    liq  = structure.find_liquidity_pools(candles_1h, price)
    vp   = structure.approximate_volume_profile(candles_1h)

    # Trend
    htf_trend   = structure.detect_trend(candles_1d, lookback=20) if candles_1d else "N/A"
    intra_trend = structure.detect_trend(candles_1h, lookback=20)

    # Session levels
    asian = structure.find_asian_range(candles_1h)
    pdh = max(c.high for c in candles_1d[-2:-1]) if len(candles_1d) >= 2 else max(c.high for c in candles_1h[-24:])
    pdl = min(c.low  for c in candles_1d[-2:-1]) if len(candles_1d) >= 2 else min(c.low  for c in candles_1h[-24:])

    # COT (only for supported instruments)
    cot = None
    if inst.get("cot_key"):
        try:
            cot = cot_fetcher.fetch_cot(inst["cot_key"])
        except Exception:
            pass

    return MarketContext(
        symbol=name,
        current_price=price,
        higher_tf_trend=htf_trend,
        intraday_trend=intra_trend,
        range_high=pd["range_high"],
        range_low=pd["range_low"],
        equilibrium=pd["equilibrium"],
        premium_discount_status=pd["status"],
        ote_low=pd["ote_low"],
        ote_high=pd["ote_high"],
        prior_day_high=pdh,
        prior_day_low=pdl,
        asian_high=asian.get("asian_high"),
        asian_low=asian.get("asian_low"),
        midnight_open=asian.get("midnight_open"),
        asian_swept=asian.get("asian_swept"),
        data_tier=candles_1h[-1].data_tier,
        data_source=data_source,
        fvgs=fvgs,
        order_blocks=obs,
        liquidity_pools=liq,
        cot=cot,
        poc=vp.get("poc"),
        vah=vp.get("vah"),
        val=vp.get("val"),
        lvns=vp.get("lvns", []),
    )


def run_scan():
    print("\nICT/SMC Remote Agent — Fetching market data...", file=sys.stderr)
    print(f"Instruments: {len(INSTRUMENTS)}\n", file=sys.stderr)

    markets = []
    for inst in INSTRUMENTS:
        name = inst["name"]
        print(f"  [{inst['asset_class'].upper()}] {name}...", file=sys.stderr)
        result = _fetch_symbol(inst)
        if result is None:
            continue
        candles_1h, _, candles_1d, actual_source = result
        try:
            ctx = _build_context(inst, candles_1h, candles_1d, actual_source)
            markets.append(ctx)
        except Exception as e:
            print(f"  ⚠  {name}: Analysis error — {e}", file=sys.stderr)
            continue

    print(f"\n  → {len(markets)}/{len(INSTRUMENTS)} instruments analysed successfully.", file=sys.stderr)
    print("\nGenerating report...\n", file=sys.stderr)

    report = generate_report(markets)
    print(report)


if __name__ == "__main__":
    run_scan()
