"""
Order Flow Analysis System — Main Entry Point

Usage:
  python main.py                     # Full pre-session report for all assets
  python main.py --symbol BTCUSDT    # Single asset deep dive
  python main.py --symbol EURUSD     # Forex structural analysis
  python main.py --test              # Test with live Binance data for BTCUSDT

The system clearly labels every output with its data tier:
  Tier 1 = TRUE ORDER FLOW (crypto via Binance taker volume)
  Tier 2 = STRUCTURAL ANALYSIS ONLY (forex, indices, commodities)
"""

import sys
import argparse
from typing import Dict, List

from data.fetchers.binance_fetcher import fetch_klines as binance_klines
from data.fetchers.yahoo_fetcher import fetch_klines as yahoo_klines
from data.fetchers.coingecko_fetcher import fetch_klines as coingecko_klines
from data.models import Candle
from reports.pre_session_report import generate_full_report, generate_asset_report
from config import WATCHLIST


def _fetch_crypto_klines(symbol: str, interval: str, limit: int):
    """
    Try Binance first (Tier 1 — taker delta), then Bybit (Tier 1 with enrichment),
    then CoinGecko (Tier 2 — structural only) as final fallback.
    """
    for fetcher_name, fetcher in [
        ("Binance", lambda: binance_klines(symbol, interval, limit=limit)),
        ("Bybit",   lambda: __import__("data.fetchers.bybit_fetcher", fromlist=["fetch_klines"]).fetch_klines(symbol, interval, limit=limit)),
        ("CoinGecko", lambda: coingecko_klines(symbol, interval, limit=limit)),
    ]:
        try:
            candles = fetcher()
            if candles:
                tier = candles[0].data_tier
                print(f"    [{fetcher_name}] Fetched {len(candles)} candles | Tier {tier} data")
                return candles
        except Exception:
            continue
    return []


def fetch_asset_data(symbol: str, config: dict) -> Dict[str, List[Candle]]:
    """
    Fetch multi-timeframe data for an asset based on its config.
    Returns {"htf": [...], "mtf": [...], "ltf": [...]}
    """
    data_tier = config.get("data_tier", 2)
    source    = config.get("source", "binance")
    ticker    = config.get("ticker", symbol)

    if data_tier == 1:
        # Crypto: Binance with Bybit fallback — Tier 1 order flow data
        print(f"  Fetching {symbol} (Tier 1 — real delta, Binance→Bybit fallback)...")
        return {
            "htf": _fetch_crypto_klines(symbol, "1d",  60),
            "mtf": _fetch_crypto_klines(symbol, "1h",  168),
            "ltf": _fetch_crypto_klines(symbol, "15m", 96),
        }
    elif source == "yahoo":
        # Indices / commodities: Yahoo Finance — Tier 2
        print(f"  Fetching {symbol} ({ticker}) from Yahoo Finance (Tier 2 — structural)...")
        return {
            "htf": yahoo_klines(ticker, "1d",  limit=60,  symbol_label=symbol),
            "mtf": yahoo_klines(ticker, "1h",  limit=120, symbol_label=symbol),
            "ltf": yahoo_klines(ticker, "15m", limit=96,  symbol_label=symbol),
        }
    else:
        # Forex and others: Alpha Vantage or Yahoo fallback — Tier 2
        yahoo_ticker = symbol[:3] + symbol[3:] + "=X"   # e.g. EURUSD → EURUSD=X
        print(f"  Fetching {symbol} from Yahoo Finance fallback (Tier 2 — structural)...")
        return {
            "htf": yahoo_klines(yahoo_ticker, "1d",  limit=60,  symbol_label=symbol),
            "mtf": yahoo_klines(yahoo_ticker, "1h",  limit=120, symbol_label=symbol),
            "ltf": yahoo_klines(yahoo_ticker, "15m", limit=96,  symbol_label=symbol),
        }


def run_full_report():
    """Run the complete pre-session report for all configured markets."""
    print("\nOrder Flow Analysis System — Fetching market data...\n")

    assets: Dict[str, Dict[str, List[Candle]]] = {}

    for category, symbols in WATCHLIST.items():
        print(f"[{category.upper()}]")
        for symbol, cfg in symbols.items():
            try:
                data = fetch_asset_data(symbol, cfg)
                if data["htf"] and data["mtf"]:
                    assets[symbol] = data
                else:
                    print(f"  ⚠️  {symbol}: No data returned — skipping")
            except Exception as e:
                print(f"  ⚠️  {symbol}: Failed to fetch — {e}")
        print()

    if not assets:
        print("No data fetched. Check internet connection and data sources.")
        return

    print("\nGenerating report...\n")
    report = generate_full_report(assets)
    print(report)

    # Save report to file
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    filename = f"Order Flow System/reports/report_{ts}.txt"
    try:
        with open(filename, "w") as f:
            f.write(report)
        print(f"\nReport saved to: {filename}")
    except Exception:
        pass


def run_single_asset(symbol: str):
    """Run a deep-dive report for a single asset."""
    # Find config
    cfg = {}
    for category, symbols in WATCHLIST.items():
        if symbol in symbols:
            cfg = symbols[symbol]
            break

    if not cfg:
        # Default to crypto on Binance
        cfg = {"data_tier": 1, "source": "binance"}

    print(f"\nFetching data for {symbol}...\n")
    try:
        data = fetch_asset_data(symbol, cfg)
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return

    if not data["htf"] or not data["mtf"]:
        print("No data returned.")
        return

    report = generate_asset_report(symbol, data["htf"], data["mtf"], data.get("ltf"))
    print(report)


def run_test():
    """Quick test with BTCUSDT — tries Binance, Bybit, then CoinGecko fallback."""
    print("\nRunning test with BTCUSDT...\n")
    try:
        candles = _fetch_crypto_klines("BTCUSDT", "1h", 48)
        from data.fetchers.binance_fetcher import compute_session_delta
        print(f"Fetched {len(candles)} hourly candles")
        if candles:
            last = candles[-1]
            print(f"Latest close : {last.close:.2f}")
            print(f"Data tier    : {last.data_tier} ({'True order flow' if last.data_tier == 1 else 'Structural only — no taker delta available'})")
            if last.delta is not None:
                print(f"Latest delta : {last.delta:.2f} (positive = net buying aggression)")
            else:
                print("Delta        : Not available (exchange API geo-blocked; using CoinGecko OHLCV)")
            delta_summary = compute_session_delta(candles)
            print(f"\nSession delta summary:")
            for k, v in delta_summary.items():
                print(f"  {k}: {v}")
    except Exception as e:
        print(f"Test failed: {e}")
        return

    print("\nRunning structural analysis...")
    try:
        from analysis.structure import detect_order_blocks, detect_fvgs, detect_liquidity_pools
        obs  = detect_order_blocks(candles)
        fvgs = detect_fvgs(candles)
        pools = detect_liquidity_pools(candles)
        print(f"Order blocks found : {len(obs)}  (unmitigated: {sum(1 for o in obs if not o.is_mitigated)})")
        print(f"FVGs found         : {len(fvgs)} (unmitigated: {sum(1 for f in fvgs if not f.is_mitigated)})")
        print(f"Liquidity pools    : {len(pools)}")
    except Exception as e:
        print(f"Structural analysis failed: {e}")

    print("\nTest complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Order Flow Analysis System")
    parser.add_argument("--symbol", type=str, help="Single asset to analyse (e.g. BTCUSDT, EURUSD)")
    parser.add_argument("--test",   action="store_true", help="Run a quick test with live Binance data")
    args = parser.parse_args()

    if args.test:
        run_test()
    elif args.symbol:
        run_single_asset(args.symbol.upper())
    else:
        run_full_report()
