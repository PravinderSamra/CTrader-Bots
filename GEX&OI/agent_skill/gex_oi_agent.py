"""
GEX & OI Agent — Main Entry Point

Usage:
    python gex_oi_agent.py --instrument US500 --session morning
    python gex_oi_agent.py --instrument XAUUSD --session intraday
    python gex_oi_agent.py --instrument US500 --instrument XAUUSD --session morning

Requires: ALPHA_VANTAGE_API_KEY environment variable
"""

import argparse
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(__file__))

from config import ALPHA_VANTAGE_API_KEY, INSTRUMENTS
from data_fetchers.alpha_vantage import (
    get_options_chain, get_spot_price, get_gold_silver_spot,
    get_vix, get_treasury_yield, get_news_sentiment, get_market_status
)
from analysis.gex_calculator import calculate_gex
from analysis.oi_analyzer import analyse_oi
from reports.chart_generator import plot_gex_by_strike, plot_oi_distribution, plot_combined_dashboard
from reports.trade_plan import generate_trade_plan, format_trade_plan


def run_session_briefing(instruments: list[str], session_type: str = "morning") -> None:
    """Run a full pre-session or intra-session briefing."""

    if not ALPHA_VANTAGE_API_KEY:
        print("ERROR: ALPHA_VANTAGE_API_KEY environment variable not set.")
        print("Get your free key at: https://www.alphavantage.co/support/#api-key")
        sys.exit(1)

    print(f"\n{'=' * 70}")
    print(f"  GEX & OI SESSION BRIEFING — {datetime.now().strftime('%Y-%m-%d %H:%M')} UTC")
    print(f"  Session: {session_type.upper()} | Instruments: {', '.join(instruments)}")
    print(f"{'=' * 70}\n")

    # --- 1. Macro context (fetch once) ---
    print("Fetching macro context...")
    macro = _fetch_macro()
    _print_macro_summary(macro)

    # --- 2. News headlines ---
    if session_type == "morning":
        print("\nFetching pre-session news...")
        _print_news(macro.get("news", []))

    # --- 3. Per-instrument analysis ---
    for instrument_key in instruments:
        cfg = INSTRUMENTS.get(instrument_key)
        if not cfg:
            print(f"Unknown instrument: {instrument_key}")
            continue

        print(f"\n{'─' * 70}")
        print(f"  ANALYSING: {instrument_key} ({cfg['description']})")
        print(f"{'─' * 70}")

        if cfg["gex_available"]:
            _run_gex_analysis(instrument_key, cfg, macro, session_type)
        else:
            _run_proxy_analysis(instrument_key, cfg, macro)

    print(f"\n{'=' * 70}")
    print("  BRIEFING COMPLETE")
    print(f"  Charts saved to: {os.path.join(os.path.dirname(__file__), 'output')}")
    print(f"{'=' * 70}\n")


def _fetch_macro() -> dict:
    """Fetch all macro data in one pass."""
    macro = {}
    try:
        macro["vix"] = get_vix()
    except Exception as e:
        print(f"  VIX fetch failed: {e}")
        macro["vix"] = 20.0

    try:
        yield_data = get_treasury_yield("10year")
        macro["yield_10y"] = yield_data.get("yield_pct")
    except Exception as e:
        print(f"  Treasury yield fetch failed: {e}")
        macro["yield_10y"] = None

    try:
        gold_data = get_gold_silver_spot()
        macro["gold_spot"] = float(gold_data.get("XAU", {}).get("price", 0) or 0)
    except Exception as e:
        print(f"  Gold spot fetch failed: {e}")
        macro["gold_spot"] = None

    try:
        macro["news"] = get_news_sentiment("SPY,GLD,^VIX", limit=8)
    except Exception as e:
        print(f"  News fetch failed: {e}")
        macro["news"] = []

    return macro


def _run_gex_analysis(instrument_key: str, cfg: dict, macro: dict, session_type: str) -> None:
    """Full GEX + OI analysis for instruments with available options data."""
    options_ticker = cfg["options_ticker"]
    multiplier = cfg.get("gld_to_gold_multiplier", 1)  # For gold: ×10 to convert GLD → XAUUSD

    # Fetch options chain
    print(f"  Fetching options chain for {options_ticker}...")
    try:
        options_df = get_options_chain(options_ticker)
    except Exception as e:
        print(f"  ERROR fetching options: {e}")
        return

    print(f"  Retrieved {len(options_df):,} option contracts")

    # Get spot price
    try:
        if instrument_key == "XAUUSD":
            gold_price = macro.get("gold_spot")
            spot = float(gold_price) if gold_price else get_spot_price("GLD")["price"] * 10
        else:
            spot_data = get_spot_price(cfg["etf_ticker"])
            spot = spot_data["price"]
            print(f"  Spot price: {spot:,.2f} (via {cfg['etf_ticker']})")
    except Exception as e:
        print(f"  ERROR fetching spot: {e}")
        return

    # For GLD options used to proxy XAUUSD: use GLD price for calculations, adjust output labels
    options_spot = spot / multiplier if multiplier > 1 else spot

    # Calculate GEX
    print(f"  Calculating GEX...")
    gex = calculate_gex(
        options_df, options_spot, options_ticker,
        contract_multiplier=cfg.get("contract_multiplier", 100)
    )

    # Scale GEX levels back to XAUUSD if needed
    if multiplier > 1:
        gex.put_wall *= multiplier
        gex.call_wall *= multiplier
        gex.max_gex_strike *= multiplier
        gex.zero_gex_strike *= multiplier
        gex.max_pain *= multiplier
        gex.support_levels = [s * multiplier for s in gex.support_levels]
        gex.resistance_levels = [r * multiplier for r in gex.resistance_levels]
        gex.spot_price = spot
        gex.symbol = instrument_key
        gex.gex_by_strike["strike"] *= multiplier

    # Analyse OI
    print(f"  Analysing Open Interest...")
    oi = analyse_oi(options_df, options_spot, options_ticker)
    if multiplier > 1:
        oi.put_wall_adjusted = oi.put_wall * multiplier if hasattr(oi, "put_wall") else None
        oi.max_pain *= multiplier
        oi.top_call_strikes = [{**s, "strike": s["strike"] * multiplier} for s in oi.top_call_strikes]
        oi.top_put_strikes = [{**s, "strike": s["strike"] * multiplier} for s in oi.top_put_strikes]
        oi.spot_price = spot
        oi.symbol = instrument_key
        oi.oi_by_strike["strike"] *= multiplier

    # Print summary
    print(f"\n  GEX SUMMARY — {instrument_key}")
    print(f"  Spot:          {spot:,.2f}")
    print(f"  Net GEX:       ${gex.total_gex:.2f}B")
    print(f"  Regime:        {gex.regime}")
    print(f"  Call Wall:     {gex.call_wall:,.0f}")
    print(f"  Put Wall:      {gex.put_wall:,.0f}")
    print(f"  Max GEX:       {gex.max_gex_strike:,.0f}")
    print(f"  Max Pain:      {oi.max_pain:,.0f}")
    print(f"  P/C Ratio:     {oi.put_call_ratio:.2f}  ({oi.sentiment})")

    # Generate charts
    print(f"\n  Generating charts...")
    gex_chart = plot_gex_by_strike(gex)
    oi_chart = plot_oi_distribution(oi)
    dashboard = plot_combined_dashboard(gex, oi, macro)
    print(f"  Charts saved: {os.path.basename(dashboard)}")

    # Generate trade plan
    plan = generate_trade_plan(
        instrument=instrument_key,
        spot_price=spot,
        gex_result=gex,
        oi_result=oi,
        macro=macro,
    )
    print(f"\n{format_trade_plan(plan)}")

    # Save trade plan as text
    plan_file = os.path.join(
        os.path.dirname(__file__), "output",
        f"trade_plan_{instrument_key}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt"
    )
    os.makedirs(os.path.dirname(plan_file), exist_ok=True)
    with open(plan_file, "w") as f:
        f.write(format_trade_plan(plan))
    print(f"  Trade plan saved: {os.path.basename(plan_file)}")


def _run_proxy_analysis(instrument_key: str, cfg: dict, macro: dict) -> None:
    """Proxy analysis for UK100 and Ger40 where direct GEX is unavailable."""
    print(f"\n  NOTE: Direct GEX/OI data not available for {instrument_key}.")
    print(f"  Using cross-market proxy analysis.\n")

    vix = macro.get("vix", 20)
    yield_10y = macro.get("yield_10y")

    # Regime from SPX GEX as proxy (already fetched if US500 was in the list)
    lines = [
        f"  {instrument_key} ({cfg['description']}) — PROXY ANALYSIS",
        "",
        f"  VIX Level:     {vix:.1f}" if isinstance(vix, float) else f"  VIX Level:     {vix}",
        f"  VIX Signal:    {'Low vol → range bias' if isinstance(vix, float) and vix < 15 else 'Elevated → directional'}",
        "",
        "  APPROACH:",
        f"  1. SPX GEX regime (from US500 analysis) applies as cross-market risk indicator",
        f"  2. Use TradingView multi-timeframe analysis for structure context",
        f"  3. Key levels: prior day H/L/close, opening range, VWAP",
        f"  4. EU session timing: 07:00–10:00 GMT is primary window",
        "",
        "  CHART INSTRUCTIONS FOR {instrument_key}:",
        "  1. Mark prior day high and low",
        "  2. Mark opening range (first 15 min)",
        "  3. Mark weekly open and monthly open",
        "  4. Plot session VWAP",
        "  5. Use SPX GEX levels as broad risk-on/risk-off context",
    ]
    print("\n".join(lines))


def _print_macro_summary(macro: dict) -> None:
    vix = macro.get("vix", "N/A")
    yield_10y = macro.get("yield_10y", "N/A")
    gold = macro.get("gold_spot", "N/A")

    vix_label = "LOW (range bias)" if isinstance(vix, float) and vix < 15 else \
                "NORMAL" if isinstance(vix, float) and vix < 20 else \
                "ELEVATED (reduce size)" if isinstance(vix, float) and vix < 30 else \
                "HIGH (specialist only)"

    print("MACRO SNAPSHOT:")
    print(f"  VIX:          {vix:.1f} — {vix_label}" if isinstance(vix, float) else f"  VIX:          {vix}")
    print(f"  10Y Yield:    {yield_10y:.2f}%" if isinstance(yield_10y, float) else f"  10Y Yield:    {yield_10y}")
    print(f"  Gold Spot:    ${gold:,.2f}" if isinstance(gold, float) else f"  Gold Spot:    {gold}")


def _print_news(news: list) -> None:
    if not news:
        print("  No news available.")
        return
    print("  TOP HEADLINES:")
    for item in news[:5]:
        sentiment_icon = "🟢" if "Bullish" in str(item.get("overall_sentiment", "")) else \
                         "🔴" if "Bearish" in str(item.get("overall_sentiment", "")) else "⚪"
        print(f"  {sentiment_icon} [{item.get('source', 'N/A')}] {item.get('title', '')[:80]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEX & OI Trading Session Briefing Agent")
    parser.add_argument("--instrument", action="append", default=[],
                        choices=list(INSTRUMENTS.keys()),
                        help="Instrument to analyse (can be specified multiple times)")
    parser.add_argument("--session", default="morning",
                        choices=["morning", "intraday"],
                        help="Session type: morning (full briefing) or intraday (quick update)")
    parser.add_argument("--all", action="store_true", help="Analyse all instruments")

    args = parser.parse_args()

    if args.all:
        instruments = list(INSTRUMENTS.keys())
    elif args.instrument:
        instruments = args.instrument
    else:
        instruments = ["US500", "XAUUSD"]  # Default to the two with best data

    run_session_briefing(instruments, args.session)
