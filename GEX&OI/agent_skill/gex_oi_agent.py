"""
GEX & OI Agent — Main entry point.

Data sources:
  Options / GEX: yfinance (SPY for US500, GLD for XAUUSD) — free, no key
  Live prices:   CTrader Remote MCP (Pepperstone spread bet prices)
  Macro:         yfinance (^VIX, ^TNX, DX-Y.NYB)

Usage:
    python gex_oi_agent.py [--instrument US500] [--instrument XAUUSD] [--all]
"""

import argparse
import sys
import os
from datetime import datetime

import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

sys.path.insert(0, os.path.dirname(__file__))

from config import INSTRUMENTS, opex_status, uk_now
from data_fetchers.yfinance_options import fetch_options_for_gex, compute_iv_skew
from data_fetchers.ctrader_fetcher import get_live_price, get_session_structure, compute_volume_profile
from data_fetchers.yahoo_finance import describe_cross_market_proxy, gex_regime_applies
from analysis.gex_calculator import calculate_gex
from analysis.oi_analyzer import analyse_oi
from reports.chart_generator import plot_gex_by_strike, plot_oi_distribution, plot_combined_dashboard
from reports.trade_plan import generate_trade_plan, format_trade_plan


def run_session_briefing(instruments: list[str]) -> None:
    """Run a full pre-session briefing for the given instruments."""
    now_uk = uk_now()

    print(f"\n{'=' * 70}")
    print(f"  GEX & OI SESSION BRIEFING")
    print(f"  {now_uk.strftime('%Y-%m-%d %H:%M %Z')}")
    print(f"  Instruments: {', '.join(instruments)}")
    print(f"{'=' * 70}\n")

    # 1. Macro context (fetch once)
    print("Fetching macro context...")
    macro = _fetch_macro()
    _print_macro(macro)

    # Track US500 GEX for cross-market proxy
    us500_gex = None

    # 2. Per-instrument analysis
    for key in instruments:
        cfg = INSTRUMENTS.get(key)
        if not cfg:
            print(f"\n  Unknown instrument: {key}")
            continue

        print(f"\n{'─' * 70}")
        print(f"  {key} — {cfg['description']}")
        print(f"{'─' * 70}")

        if cfg["gex_available"]:
            gex_result = _analyse_with_gex(key, cfg, macro)
            if key == "US500" and gex_result:
                us500_gex = gex_result
        else:
            _analyse_proxy(key, cfg, macro, us500_gex)

    print(f"\n{'=' * 70}")
    print("  BRIEFING COMPLETE")
    opex = macro.get("opex", {})
    print(f"  OPEX reliability: {opex.get('gex_reliability', 'Unknown')}")
    print(f"  Monthly OPEX: {opex.get('monthly_opex_date', 'N/A')} "
          f"({opex.get('days_to_monthly_opex', '?')} days)")
    print(f"{'=' * 70}\n")


def _fetch_macro() -> dict:
    """Fetch macro context: VIX, 10Y yield, DXY."""
    macro = {}
    macro["opex"] = opex_status()

    try:
        macro["vix"] = float(yf.Ticker("^VIX").fast_info["last_price"])
    except Exception:
        macro["vix"] = 20.0

    try:
        macro["yield_10y"] = float(yf.Ticker("^TNX").fast_info["last_price"])
    except Exception:
        macro["yield_10y"] = None

    try:
        macro["dxy"] = float(yf.Ticker("DX-Y.NYB").fast_info["last_price"])
    except Exception:
        macro["dxy"] = None

    try:
        macro["gold_spot"] = float(yf.Ticker("GC=F").fast_info["last_price"])
    except Exception:
        macro["gold_spot"] = None

    return macro


def _analyse_with_gex(key: str, cfg: dict, macro: dict):
    """Full GEX + OI analysis for instruments with available options data."""
    multiplier = cfg.get("gld_to_gold_multiplier", 10 if key != "XAUUSD" else 10)
    # US500: SPY × 10 ≈ US500; XAUUSD: GLD × 10 ≈ XAUUSD
    # multiplier maps ETF scale → instrument scale

    # Live price from CTrader
    print(f"  Fetching live price (CTrader MCP)...")
    spot_live = None
    price_data = get_live_price(key)
    if price_data:
        spot_live = price_data["mid"]
        print(f"  Live: {spot_live:,.2f}  "
              f"(bid {price_data['bid']:,.2f} / ask {price_data['ask']:,.2f})")
    else:
        # Fallback: yfinance ETF × multiplier
        try:
            etf_price = float(yf.Ticker(cfg["etf_ticker"]).fast_info["last_price"])
            spot_live = etf_price * multiplier
            print(f"  CTrader unavailable — yfinance fallback: {spot_live:,.2f}")
        except Exception as e:
            print(f"  ERROR: Cannot determine spot price: {e}")
            return None

    # Fetch options
    print(f"  Fetching options chain (yfinance {cfg['etf_ticker']})...")
    try:
        options_df = fetch_options_for_gex(key, spot_live)
    except Exception as e:
        print(f"  ERROR fetching options: {e}")
        return None

    if options_df.empty:
        print("  No options data retrieved.")
        return None

    n = len(options_df)
    print(f"  {n:,} option contracts loaded")

    # ETF spot is used internally for GEX (gamma was computed at ETF scale)
    etf_spot = float(options_df["etf_spot"].iloc[0])

    # Calculate GEX (pass etf_spot — gamma and strikes are ETF-scale)
    print("  Calculating GEX...")
    gex = calculate_gex(
        options_df, etf_spot, cfg["etf_ticker"],
        contract_multiplier=cfg.get("contract_multiplier", 100)
    )

    # Scale GEX output levels from ETF scale → instrument scale
    for attr in ["put_wall", "call_wall", "max_gex_strike", "zero_gex_strike", "max_pain"]:
        val = getattr(gex, attr)
        if val:
            setattr(gex, attr, val * multiplier)
    gex.support_levels = [s * multiplier for s in gex.support_levels]
    gex.resistance_levels = [r * multiplier for r in gex.resistance_levels]
    if not gex.gex_by_strike.empty:
        gex.gex_by_strike = gex.gex_by_strike.copy()
        gex.gex_by_strike["strike"] = gex.gex_by_strike["strike"] * multiplier
    gex.spot_price = spot_live
    gex.symbol = key

    # Analyse OI (also ETF-scale internally)
    print("  Analysing Open Interest...")
    oi = analyse_oi(options_df, etf_spot, cfg["etf_ticker"])

    oi.max_pain = oi.max_pain * multiplier if oi.max_pain else 0
    oi.top_call_strikes = [{**s, "strike": s["strike"] * multiplier} for s in oi.top_call_strikes]
    oi.top_put_strikes = [{**s, "strike": s["strike"] * multiplier} for s in oi.top_put_strikes]
    if not oi.oi_by_strike.empty:
        oi.oi_by_strike = oi.oi_by_strike.copy()
        oi.oi_by_strike["strike"] = oi.oi_by_strike["strike"] * multiplier
    oi.spot_price = spot_live
    oi.symbol = key

    # Session structure from CTrader candles
    print("  Fetching session structure (CTrader)...")
    session_structure = get_session_structure(key)

    # Volume profile from CTrader H1 candles
    print("  Computing volume profile...")
    try:
        vol_profile = compute_volume_profile(key)
        if vol_profile:
            print(f"  POC: {vol_profile['poc']:,.1f}  |  "
                  f"HVN: {len(vol_profile['hvn_levels'])} nodes  |  "
                  f"LVN: {len(vol_profile['lvn_levels'])} thin zones")
    except Exception as e:
        vol_profile = {}
        print(f"  Volume profile unavailable: {e}")

    # IV skew
    iv_skew = compute_iv_skew(options_df, etf_spot)

    # CTA positioning from ETF moving averages
    cta_data = _compute_cta_levels(cfg.get("etf_ticker", "SPY"))

    # Print summary
    _print_gex_summary(key, spot_live, gex, oi)

    # Charts
    print("\n  Generating charts...")
    chart_files = []
    try:
        gex_chart = plot_gex_by_strike(gex)
        if gex_chart:
            chart_files.append(gex_chart)
            print(f"  GEX Chart:       {gex_chart}")
        oi_chart = plot_oi_distribution(oi)
        if oi_chart:
            chart_files.append(oi_chart)
            print(f"  OI Chart:        {oi_chart}")
        dashboard = plot_combined_dashboard(gex, oi, macro)
        if dashboard:
            chart_files.append(dashboard)
            print(f"  Dashboard:       {dashboard}")
        print(f"  CHARTS_GENERATED: {','.join(chart_files)}")
    except Exception as e:
        print(f"  Chart error: {e}")
        chart_files = []

    # Trade plan
    macro_for_plan = dict(macro)
    macro_for_plan["_vix"] = macro.get("vix")
    macro_for_plan["_yield_10y"] = macro.get("yield_10y")
    macro_for_plan["_dxy"] = macro.get("dxy")

    plan = generate_trade_plan(key, spot_live, gex, oi, macro_for_plan,
                               session_structure=session_structure, iv_skew=iv_skew,
                               vol_profile=vol_profile, cta_data=cta_data)
    print(f"\n{format_trade_plan(plan)}")

    return gex


def _compute_cta_levels(etf_ticker: str) -> dict:
    """
    Approximate CTA (systematic trend-follower) positioning from ETF moving averages.
    CTAs — large quant funds that follow price trends — go long when price is above
    their key MAs and short when below. This gives us a sense of whether systematic
    money is aligned with or against the current price direction.
    """
    try:
        hist = yf.Ticker(etf_ticker).history(period="1y", interval="1d")
        if hist.empty or len(hist) < 50:
            return {}
        close = hist["Close"]
        current = float(close.iloc[-1])
        sma_20  = float(close.rolling(20).mean().iloc[-1])
        sma_50  = float(close.rolling(50).mean().iloc[-1])
        sma_100 = float(close.rolling(100).mean().iloc[-1]) if len(hist) >= 100 else None
        sma_200 = float(close.rolling(200).mean().iloc[-1]) if len(hist) >= 200 else None

        # CTA stance classification
        above_50  = current > sma_50
        above_200 = sma_200 is None or current > sma_200
        ma_aligned = sma_100 is None or sma_50 > sma_100  # short MA above long MA = uptrend

        if above_50 and ma_aligned and above_200:
            bias = "LONG"
            signal = "CTAs positioned LONG — price above 50-day MA with trend aligned upward."
            implication = "Systematic funds are a tailwind for the long. If the call wall breaks, CTA buying adds further fuel."
        elif above_50 and not ma_aligned:
            bias = "MILD_LONG"
            signal = "CTAs mildly long — above 50-day MA but MAs not fully aligned."
            implication = "Moderate CTA support. Breakout longs have some systematic backing but not full conviction."
        elif not above_50 and not ma_aligned:
            bias = "SHORT"
            signal = "CTAs positioned SHORT — price below 50-day MA with trend turning down."
            implication = "Systematic funds are a headwind for longs. Rejection shorts have CTA selling behind them."
        else:
            bias = "NEUTRAL"
            signal = "CTAs near neutral — price at MA crossover zone. Systematic funds in transition."
            implication = "No strong CTA tailwind in either direction. Trade purely off GEX and price action."

        result = {
            "etf_ticker": etf_ticker,
            "current_etf": round(current, 2),
            "sma_20":  round(sma_20, 2),
            "sma_50":  round(sma_50, 2),
            "bias":    bias,
            "signal":  signal,
            "implication": implication,
        }
        if sma_100: result["sma_100"] = round(sma_100, 2)
        if sma_200: result["sma_200"] = round(sma_200, 2)
        return result
    except Exception:
        return {}


def _analyse_proxy(key: str, cfg: dict, macro: dict, us500_gex=None) -> None:
    """Proxy analysis for UK100 and Ger40 where direct GEX is unavailable."""
    # Live price from CTrader
    price_data = get_live_price(key)
    spot_live = price_data["mid"] if price_data else None
    if spot_live:
        print(f"  Live: {spot_live:,.1f}  "
              f"(bid {price_data['bid']:,.1f} / ask {price_data['ask']:,.1f})")

    # Session structure from CTrader candles
    structure = get_session_structure(key)
    if structure:
        print(f"\n  SESSION STRUCTURE:")
        if "prev_day_high" in structure:
            print(f"    Prev Day High: {structure['prev_day_high']:,.1f}")
            print(f"    Prev Day Low:  {structure['prev_day_low']:,.1f}")
        if "today_open" in structure:
            print(f"    Today Open:    {structure['today_open']:,.1f}")
        if "session_high" in structure:
            print(f"    Session High:  {structure['session_high']:,.1f}")
            print(f"    Session Low:   {structure['session_low']:,.1f}")

    # Cross-market GEX proxy
    if us500_gex:
        spx_regime = us500_gex.regime
        spx_gex_bn = us500_gex.total_gex
        print(f"\n  CROSS-MARKET PROXY (SPX → {key}):")
        print(f"  " + describe_cross_market_proxy(key, spx_regime, spx_gex_bn))

    vix = macro.get("vix", 20)
    vix_str = f"{vix:.1f}" if isinstance(vix, float) else str(vix)
    vix_label = (
        "Low vol: range bias" if isinstance(vix, float) and vix < 15 else
        "Normal" if isinstance(vix, float) and vix < 20 else
        "Elevated: trade directional breakouts" if isinstance(vix, float) and vix < 30 else
        "High — reduce size"
    )
    print(f"\n  VIX: {vix_str} — {vix_label}")

    print(f"\n  CHART INSTRUCTIONS FOR {key}:")
    print(f"  1. Mark prior day high and low")
    print(f"  2. Mark today's opening range (first 15 min)")
    print(f"  3. Mark weekly and monthly open")
    print(f"  4. Plot session VWAP")
    print(f"  5. Use SPX GEX levels as cross-market regime context")
    if spot_live and structure:
        if "prev_day_high" in structure:
            print(f"  6. Key levels: PDH {structure['prev_day_high']:,.1f}  /  "
                  f"PDL {structure['prev_day_low']:,.1f}")


def _print_macro(macro: dict) -> None:
    vix = macro.get("vix", "N/A")
    yield_10y = macro.get("yield_10y", "N/A")
    dxy = macro.get("dxy", "N/A")
    gold = macro.get("gold_spot", "N/A")
    opex = macro.get("opex", {})

    vix_label = (
        "LOW — range bias, fade extremes" if isinstance(vix, float) and vix < 15 else
        "NORMAL" if isinstance(vix, float) and vix < 20 else
        "ELEVATED — reduce position size" if isinstance(vix, float) and vix < 30 else
        "HIGH — specialist setups only"
    )

    print("MACRO SNAPSHOT:")
    if isinstance(vix, float):
        print(f"  VIX:        {vix:.1f} — {vix_label}")
    if isinstance(yield_10y, float):
        print(f"  10Y Yield:  {yield_10y:.2f}%")
    if isinstance(dxy, float):
        print(f"  DXY:        {dxy:.2f}")
    if isinstance(gold, float):
        print(f"  Gold:       ${gold:,.2f}")
    if opex:
        print(f"  OPEX:       {opex.get('monthly_opex_date', 'N/A')} "
              f"({opex.get('days_to_monthly_opex', '?')} days) — "
              f"{opex.get('gex_reliability', '')}")


def _print_gex_summary(key: str, spot: float, gex, oi) -> None:
    regime_indicator = {"PINNED": "PINNED (rangebound)", "TRENDING": "TRENDING (directional)",
                        "NEUTRAL": "NEUTRAL"}.get(gex.regime, gex.regime)
    thin = "─" * 68
    print(f"\n  GEX SUMMARY — {key}")
    print(f"  {thin}")
    print(f"    {'Metric':<18}  {'Value':>12}   Note")
    print(f"    {'─'*18}  {'─'*12}   {'─'*30}")
    print(f"    {'Spot Price':<18}  {spot:>12,.2f}")
    print(f"    {'Net GEX':<18}  ${gex.total_gex:>11.2f}B   {regime_indicator}")
    print(f"    {'Call GEX':<18}  +${gex.call_gex:>10.2f}B   dealer long gamma above spot")
    print(f"    {'Put GEX':<18}  -${gex.put_gex:>10.2f}B   dealer short gamma below spot")
    print(f"    {'─'*18}  {'─'*12}   {'─'*30}")
    print(f"    {'Call Wall':<18}  {gex.call_wall:>12,.0f}   ← primary resistance")
    print(f"    {'Max GEX Pin':<18}  {gex.max_gex_strike:>12,.0f}   ← gravitational pin / T1")
    print(f"    {'Zero GEX':<18}  {gex.zero_gex_strike:>12,.0f}   ← volatility trigger")
    print(f"    {'Max Pain':<18}  {oi.max_pain:>12,.0f}   ← expiry magnet")
    print(f"    {'Put Wall':<18}  {gex.put_wall:>12,.0f}   ← primary support")
    print(f"    {'─'*18}  {'─'*12}   {'─'*30}")
    print(f"    {'P/C Ratio':<18}  {oi.put_call_ratio:>12.2f}   {oi.sentiment}")
    if gex.resistance_levels:
        print(f"    {'GEX Resistance':<18}  {'':>12}   {', '.join(f'{r:,.0f}' for r in gex.resistance_levels[:4])}")
    if gex.support_levels:
        print(f"    {'GEX Support':<18}  {'':>12}   {', '.join(f'{s:,.0f}' for s in gex.support_levels[:4])}")

    # Top OI strikes breakdown
    print(f"\n  OPEN INTEREST — TOP STRIKES")
    print(f"  {thin}")
    print(f"    {'Strike':>8}   {'Type':<6}   {'OI Contracts':>14}   Note")
    print(f"    {'─'*8}   {'─'*6}   {'─'*14}   {'─'*28}")
    for item in oi.top_call_strikes[:4]:
        note = "← max call OI" if item == oi.top_call_strikes[0] else "call resistance"
        print(f"    {item['strike']:>8,.0f}   {'CALL':<6}   {item['oi']:>14,}   {note}")
    for item in oi.top_put_strikes[:4]:
        note = "← max put OI" if item == oi.top_put_strikes[0] else "put support"
        print(f"    {item['strike']:>8,.0f}   {'PUT':<6}   {item['oi']:>14,}   {note}")
    print(f"  {thin}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEX & OI Trading Session Briefing")
    parser.add_argument("--instrument", action="append", default=[],
                        choices=list(INSTRUMENTS.keys()),
                        help="Instrument to analyse (repeatable)")
    parser.add_argument("--all", action="store_true", help="Analyse all instruments")

    args = parser.parse_args()

    if args.all:
        instruments = list(INSTRUMENTS.keys())
    elif args.instrument:
        instruments = args.instrument
    else:
        instruments = ["US500", "XAUUSD"]

    run_session_briefing(instruments)
