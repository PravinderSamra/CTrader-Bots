"""
Order Flow Analysis System — Main Entry Point

Usage:
  python main.py                     # Full pre-session report for all assets
  python main.py --symbol BTCUSDT    # Single asset deep dive
  python main.py --symbol EURUSD     # Forex structural analysis
  python main.py --test              # Run a quick connectivity and data test

The system auto-detects which exchange APIs are accessible at runtime:
  Claude platform : OKX → Kraken → CoinGecko  (Binance/Bybit geo-blocked)
  Local computer  : Binance → OKX → Kraken → CoinGecko

Data tier labels in every output:
  Tier 1 = TRUE ORDER FLOW  (taker buy/sell delta from exchange APIs)
  Tier 2 = STRUCTURAL ONLY  (OHLCV-derived OBs, FVGs, volume profile approx.)
"""

import sys
import argparse
from typing import Dict, List

from data.fetchers.yahoo_fetcher import fetch_klines as yahoo_klines
from data.fetchers.coingecko_fetcher import fetch_klines as coingecko_klines
from data.models import Candle
from reports.pre_session_report import generate_full_report, generate_asset_report
from config import WATCHLIST


def _fetch_crypto_klines(symbol: str, interval: str, limit: int):
    """
    Fetch crypto klines using the best available Tier 1 source for this platform.

    Detection order (runtime-probed at first call, then cached):
      Binance  — local computer, built-in taker volume in klines (cleanest Tier 1)
      OKX      — Claude platform, taker volume via trade aggregation (Tier 1)
      Kraken   — EU-based fallback, taker volume via trade aggregation (Tier 1)
      Bybit    — secondary fallback, taker volume via trade aggregation (Tier 1)
      CoinGecko — last resort, OHLCV only (Tier 2, structural analysis only)
    """
    from data.platform_detector import detect_sources

    # Map source names to (label, fetcher_callable) pairs
    def _binance():
        from data.fetchers.binance_fetcher import fetch_klines
        return fetch_klines(symbol, interval, limit=limit)

    def _okx():
        from data.fetchers.okx_fetcher import fetch_klines
        return fetch_klines(symbol, interval, limit=limit)

    def _kraken():
        from data.fetchers.kraken_fetcher import fetch_klines
        return fetch_klines(symbol, interval, limit=limit)

    def _bybit():
        from data.fetchers.bybit_fetcher import fetch_klines
        return fetch_klines(symbol, interval, limit=limit)

    def _coingecko():
        return coingecko_klines(symbol, interval, limit=limit)

    source_map = {
        "binance":   ("Binance",   _binance),
        "okx":       ("OKX",       _okx),
        "kraken":    ("Kraken",    _kraken),
        "bybit":     ("Bybit",     _bybit),
        "deribit":   None,   # perpetuals only, skip for general klines
    }

    ordered = detect_sources()

    for source in ordered:
        entry = source_map.get(source)
        if entry is None:
            continue
        label, fetcher = entry
        try:
            candles = fetcher()
            if candles:
                tier = candles[0].data_tier
                print(f"    [{label}] Fetched {len(candles)} candles | Tier {tier} data")
                return candles
        except Exception:
            continue

    # Absolute last resort — Tier 2 only
    try:
        candles = _coingecko()
        if candles:
            print(f"    [CoinGecko] Fetched {len(candles)} candles | Tier 2 (structural only — no taker delta)")
            return candles
    except Exception:
        pass

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
        # Crypto: platform-detected source (Binance local / OKX+Kraken on Claude platform)
        print(f"  Fetching {symbol} (Tier 1 — real delta, auto-detected source)...")
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
    """Quick connectivity test — auto-detects best available data source."""
    from data.platform_detector import detect_sources, platform_summary
    print("\nOrder Flow Analysis System — Connectivity Test\n")
    print(f"Platform detection: {platform_summary()}")
    sources = detect_sources()
    print(f"Available sources : {sources or ['none — will use CoinGecko Tier 2']}\n")

    print("Fetching BTCUSDT hourly data (48 candles)...")
    try:
        candles = _fetch_crypto_klines("BTCUSDT", "1h", 48)
        if not candles:
            print("No candles returned.")
            return
        last = candles[-1]
        print(f"Fetched {len(candles)} hourly candles")
        print(f"Latest close : {last.close:.2f}")
        print(f"Data tier    : {last.data_tier} ({'True order flow — taker delta available' if last.data_tier == 1 else 'Structural only — no taker delta available'})")
        if last.delta is not None:
            print(f"Latest delta : {last.delta:+.4f} (positive = net buying aggression)")
        else:
            print("Delta        : Not available for this data source")

        # Delta summary — only meaningful for Tier 1 candles
        tier1_candles = [c for c in candles if c.data_tier == 1]
        if tier1_candles:
            try:
                from data.fetchers.binance_fetcher import compute_session_delta
                delta_summary = compute_session_delta(candles)
                print(f"\nSession delta summary ({len(tier1_candles)}/{len(candles)} candles with Tier 1 data):")
                for k, v in delta_summary.items():
                    print(f"  {k}: {v}")
            except Exception:
                pass
        else:
            print("\nNo Tier 1 candles — delta summary unavailable")
    except Exception as e:
        print(f"Data fetch failed: {e}")
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
