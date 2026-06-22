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
import json
from datetime import datetime, timezone

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
        # Fallback: yfinance — use gold futures directly for XAUUSD (more accurate than GLD×10)
        try:
            if key == "XAUUSD":
                spot_live = float(yf.Ticker("GC=F").fast_info["last_price"])
            else:
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

    # Export to dashboard data file
    try:
        _export_dashboard_data(key, spot_live, gex, oi, macro, vol_profile, cta_data,
                               session_structure, plan)
    except Exception as e:
        print(f"\n  [Dashboard export skipped: {e}]")

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


def _export_dashboard_data(key: str, spot: float, gex, oi, macro: dict,
                           vol_profile: dict, cta_data: dict,
                           session_structure: dict, plan) -> None:
    """Export scan results as a JS variable file to the dashboard/data/ directory."""
    # Resolve dashboard/data path relative to this file
    agent_dir  = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(agent_dir)  # GEX&OI/
    data_dir   = os.path.join(project_dir, "dashboard", "data")
    os.makedirs(data_dir, exist_ok=True)

    now_iso = datetime.now(timezone.utc).astimezone().isoformat()

    # GEX by strike
    gex_strikes, gex_vals = [], []
    if gex.gex_by_strike is not None and not gex.gex_by_strike.empty:
        gex_strikes = [round(float(s), 1) for s in gex.gex_by_strike["strike"].tolist()]
        gex_vals    = [round(float(v) / 1e9, 4) for v in gex.gex_by_strike["total_gex"].tolist()]

    # OI by strike
    oi_strikes, call_oi_list, put_oi_list = [], [], []
    if oi.oi_by_strike is not None and not oi.oi_by_strike.empty:
        oi_strikes    = [round(float(s), 1) for s in oi.oi_by_strike["strike"].tolist()]
        call_oi_list  = [int(v) for v in oi.oi_by_strike.get("call_oi", [0]*len(oi_strikes))]
        put_oi_list   = [int(v) for v in oi.oi_by_strike.get("put_oi",  [0]*len(oi_strikes))]

    # Volume profile
    vp_export: dict = {}
    if vol_profile:
        vp_export = {
            "poc":          round(float(vol_profile.get("poc", 0)), 2),
            "hvn_levels":   [round(float(v), 2) for v in vol_profile.get("hvn_levels", [])],
            "lvn_levels":   [round(float(v), 2) for v in vol_profile.get("lvn_levels", [])],
            "bucket_size":  vol_profile.get("bucket_size", 5),
            "lookback_bars":vol_profile.get("lookback_bars", 168),
            "price_buckets":[round(float(b), 2) for b in vol_profile.get("price_buckets", [])],
            "volume":       [int(v) for v in vol_profile.get("volume", [])],
        }

    # CTA
    cta_export: dict = {}
    if cta_data:
        cta_export = {
            "bias":    cta_data.get("bias", "NEUTRAL"),
            "sma20":   cta_data.get("sma_20", 0),
            "sma50":   cta_data.get("sma_50", 0),
            "sma100":  cta_data.get("sma_100", 0),
            "sma200":  cta_data.get("sma_200", 0),
            "note":    cta_data.get("signal", ""),
        }

    # Macro
    mac_export = {
        "vix":          round(float(macro.get("vix", 0) or 0), 2),
        "vix_signal":   _vix_label(macro.get("vix")),
        "dxy":          round(float(macro.get("dxy") or 0), 2),
        "dxy_signal":   "DXY data",
        "us10y":        round(float(macro.get("yield_10y") or 0), 2),
        "us10y_signal": "US 10Y yield",
        "prev_day_high": round(float(session_structure.get("prev_day_high", 0) or 0), 2) if session_structure else 0,
        "prev_day_low":  round(float(session_structure.get("prev_day_low", 0) or 0), 2) if session_structure else 0,
        "weekly_open":   round(float(session_structure.get("weekly_open", 0) or 0), 2) if session_structure else 0,
    }

    # Trade plan → scenarios
    scenarios_export: dict = {}
    if plan:
        primary = plan.primary_scenario
        if primary:
            scenarios_export["primary"] = _scenario_export(primary, "A")
        alts = plan.alternative_scenarios or []
        if len(alts) > 0:
            scenarios_export["alt1"] = _scenario_export(alts[0], "B")
        if len(alts) > 1:
            scenarios_export["alt2"] = _scenario_export(alts[1], "C")

    # Assemble payload
    payload = {
        "instrument": key,
        "scan_time":  now_iso,
        "spot":       round(float(spot), 2),
        "metrics": {
            "net_gex":        round(gex.total_gex / 1e9, 3),
            "call_gex":       round(gex.call_gex / 1e9, 3),
            "put_gex":        round(gex.put_gex / 1e9, 3),
            "regime":         gex.regime,
            "call_wall":      round(float(gex.call_wall or 0), 1),
            "put_wall":       round(float(gex.put_wall or 0), 1),
            "max_gex_strike": round(float(gex.max_gex_strike or 0), 1),
            "zero_gex_strike":round(float(gex.zero_gex_strike or 0), 1),
            "max_pain":       round(float(oi.max_pain or 0), 1),
            "put_call_ratio": round(float(oi.put_call_ratio or 0), 3),
            "sentiment":      oi.sentiment,
            "iv_skew_ratio":  round(float(getattr(oi, "iv_skew_ratio", 1.0) or 1.0), 3),
            "iv_skew_bias":   getattr(oi, "iv_skew_bias", ""),
            "resistance_levels": [round(float(r), 1) for r in gex.resistance_levels[:4]],
            "support_levels":    [round(float(s), 1) for s in gex.support_levels[:4]],
        },
        "top_strikes": {
            "calls": [{"strike": round(float(c["strike"]), 1), "oi": int(c["oi"]), "note": c.get("note", "call")}
                      for c in oi.top_call_strikes[:4]],
            "puts":  [{"strike": round(float(p["strike"]), 1), "oi": int(p["oi"]), "note": p.get("note", "put")}
                      for p in oi.top_put_strikes[:4]],
        },
        "gex_by_strike": {"strikes": gex_strikes, "gex_values": gex_vals},
        "oi_by_strike":  {"strikes": oi_strikes,  "call_oi": call_oi_list, "put_oi": put_oi_list},
        "volume_profile": vp_export,
        "cta":            cta_export,
        "macro":          mac_export,
        "session_structure": {
            "london_open": "08:00",
            "ny_open":     "13:30",
            "ny_close":    "21:00",
            "key_time_events": [],
        },
        "situation": {
            "narrative":             "",
            "confluence_scenario":   plan.primary_bias if plan else "",
            "scenario_name":         plan.primary_scenario.get("name", "") if (plan and plan.primary_scenario) else "",
            "scenario_description":  plan.primary_scenario.get("why", "")  if (plan and plan.primary_scenario) else "",
            "levels_table":          [],
        },
        "key_levels": _build_key_levels_export(spot, gex, oi),
        "trade_scenarios": scenarios_export,
    }

    js_content = (
        f"// GEX & OI Dashboard Data — {key}\n"
        f"// Auto-generated by gex_oi_agent.py at {now_iso} — DO NOT EDIT MANUALLY\n"
        f"window.GEX_OI_DATA = window.GEX_OI_DATA || {{}};\n"
        f"window.GEX_OI_DATA[\"{key}\"] = "
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + ";\n"
    )

    out_path = os.path.join(data_dir, f"{key}_latest.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"  DASHBOARD_EXPORT: {out_path}")


def _export_proxy_dashboard_data(key: str, spot_live, macro: dict,
                                 structure: dict, us500_gex) -> None:
    """Export proxy dashboard data for UK100/GER40 (no direct options data)."""
    agent_dir   = os.path.dirname(os.path.abspath(__file__))
    project_dir = os.path.dirname(agent_dir)
    data_dir    = os.path.join(project_dir, "dashboard", "data")
    os.makedirs(data_dir, exist_ok=True)

    now_iso = datetime.now(timezone.utc).astimezone().isoformat()

    spot = round(float(spot_live), 2) if spot_live else 0.0

    # Session structure levels
    pdh = round(float(structure.get("prev_day_high", 0) or 0), 2) if structure else 0
    pdl = round(float(structure.get("prev_day_low", 0) or 0), 2) if structure else 0
    today_open  = round(float(structure.get("today_open", 0) or 0), 2) if structure else 0
    session_hi  = round(float(structure.get("session_high", 0) or 0), 2) if structure else 0
    session_lo  = round(float(structure.get("session_low", 0) or 0), 2) if structure else 0
    weekly_open = round(float(structure.get("weekly_open", 0) or 0), 2) if structure else 0

    # Cross-market narrative
    spx_regime  = us500_gex.regime    if us500_gex else "NEUTRAL"
    spx_gex_bn  = us500_gex.total_gex if us500_gex else 0.0
    narrative = describe_cross_market_proxy(key, spx_regime, spx_gex_bn) if us500_gex else (
        f"No direct options data for {key}. Use SPX GEX regime and PDH/PDL structure as primary context."
    )

    # VIX
    vix = macro.get("vix", 20)

    # Key levels from structure — full level-block format for dashboard renderLevelBlock()
    key_levels_export = []
    range_size = round(pdh - pdl, 1) if (pdh and pdl) else 0
    mid = round((pdh + pdl) / 2, 1) if (pdh and pdl) else 0

    if pdh:
        t1 = round(pdh + range_size * 0.5, 1) if range_size else round(pdh + 20, 1)
        t2 = round(pdh + range_size, 1) if range_size else round(pdh + 40, 1)
        stop = round(pdh - range_size * 0.15, 1) if range_size else round(pdh - 10, 1)
        key_levels_export.append({
            "level": pdh, "label": "PDH", "type": "resistance",
            "entry": f"15-min close above PDH ({pdh:,.1f})",
            "stop":  f"{stop:,.1f} — back below PDH (breakout failed)",
            "rr":    "~2:1",
            "target1": f"{t1:,.1f}",
            "target2": f"{t2:,.1f}",
            "context": "Prior Day High: the most watched resistance level. A confirmed close above triggers momentum buy stops. Below, it acts as resistance to fade from.",
        })
    if pdl:
        t1 = round(pdl - range_size * 0.5, 1) if range_size else round(pdl - 20, 1)
        t2 = round(pdl - range_size, 1) if range_size else round(pdl - 40, 1)
        stop = round(pdl + range_size * 0.15, 1) if range_size else round(pdl + 10, 1)
        key_levels_export.append({
            "level": pdl, "label": "PDL", "type": "support",
            "entry": f"15-min close below PDL ({pdl:,.1f})",
            "stop":  f"{stop:,.1f} — recovery above PDL (breakdown failed)",
            "rr":    "~2:1",
            "target1": f"{t1:,.1f}",
            "target2": f"{t2:,.1f}",
            "context": "Prior Day Low: the most watched support level. A confirmed close below triggers sell stops. Above, it acts as support to buy from.",
        })
    if today_open:
        key_levels_export.append({
            "level": today_open, "label": "Today Open", "type": "pin",
            "entry": f"Fade from Today Open ({today_open:,.1f}) as directional filter",
            "stop":  f"Sustained close through PDH or PDL",
            "rr":    "~2:1",
            "target1": f"{pdh:,.1f}" if pdh else "—",
            "target2": f"{pdl:,.1f}" if pdl else "—",
            "context": "Today's opening price acts as the session's intraday pivot — price above = bullish bias, price below = bearish bias. Use as a filter, not a standalone entry.",
        })
    if session_hi and session_hi != pdh:
        key_levels_export.append({
            "level": session_hi, "label": "Session High", "type": "resistance",
            "entry": f"Break above session high ({session_hi:,.1f})",
            "stop":  f"{round(session_hi - 10, 1):,.1f}",
            "rr":    "~2:1",
            "target1": f"{pdh:,.1f}" if (pdh and pdh > session_hi) else f"{round(session_hi + 20, 1):,.1f}",
            "target2": "—",
            "context": "Current session's intraday swing high — a break above signals intraday trend continuation.",
        })
    if session_lo and session_lo != pdl:
        key_levels_export.append({
            "level": session_lo, "label": "Session Low", "type": "support",
            "entry": f"Break below session low ({session_lo:,.1f})",
            "stop":  f"{round(session_lo + 10, 1):,.1f}",
            "rr":    "~2:1",
            "target1": f"{pdl:,.1f}" if (pdl and pdl < session_lo) else f"{round(session_lo - 20, 1):,.1f}",
            "target2": "—",
            "context": "Current session's intraday swing low — a break below signals intraday downside continuation.",
        })

    # Simple trade scenarios driven by regime + PDH/PDL
    scenarios_export: dict = {}
    if pdh and pdl and spot:
        range_size = round(pdh - pdl, 1)
        mid = round((pdh + pdl) / 2, 1)

        if spx_regime == "TRENDING":
            scenarios_export["primary"] = {
                "label": "Breakout above PDH",
                "probability": "MEDIUM",
                "bias": "LONG",
                "entry": f"Break and close above PDH ({pdh:,.1f}) on 15-min candle",
                "target": f"T1: PDH + {range_size * 0.5:,.0f}  |  T2: PDH + {range_size:,.0f}",
                "stop": f"Back below PDH ({pdh:,.1f}) — invalidation",
                "context": f"SPX in TRENDING regime (GEX ${spx_gex_bn:.1f}B). "
                           f"Dealers amplifying moves globally. Breakout above PDH has momentum backing.",
                "invalidation": f"Price reverses below today's open ({today_open:,.1f})",
            }
            scenarios_export["alt1"] = {
                "label": "Breakdown below PDL",
                "probability": "MEDIUM",
                "bias": "SHORT",
                "entry": f"Break and close below PDL ({pdl:,.1f}) on 15-min candle",
                "target": f"T1: PDL - {range_size * 0.5:,.0f}  |  T2: PDL - {range_size:,.0f}",
                "stop": f"Back above PDL ({pdl:,.1f})",
                "context": f"Trending regime favours breakouts in either direction. "
                           f"Trade the break, not the fade.",
                "invalidation": f"Price recovers back above today's open ({today_open:,.1f})",
            }
        elif spx_regime == "PINNED":
            fade_zone_top = round(pdh - (pdh - mid) * 0.1, 1)
            fade_zone_bot = round(pdl + (mid - pdl) * 0.1, 1)
            scenarios_export["primary"] = {
                "label": f"Fade at PDH ({pdh:,.1f})",
                "probability": "MEDIUM",
                "bias": "SHORT",
                "entry": f"Price rallies to PDH zone ({fade_zone_top:,.1f}–{pdh:,.1f}), wait for rejection candle",
                "target": f"T1: {mid:,.1f} (prior day mid)  |  T2: {pdl:,.1f} (PDL)",
                "stop": f"Above PDH ({pdh:,.1f}) + 10pts",
                "context": f"SPX in PINNED regime (GEX +${spx_gex_bn:.1f}B). "
                           f"Dealers are long gamma globally, damping volatility. "
                           f"Fade moves to range extremes — sell PDH, buy PDL.",
                "invalidation": f"Strong close above PDH — regime shift to TRENDING",
            }
            scenarios_export["alt1"] = {
                "label": f"Fade at PDL ({pdl:,.1f})",
                "probability": "MEDIUM",
                "bias": "LONG",
                "entry": f"Price dips to PDL zone ({pdl:,.1f}–{fade_zone_bot:,.1f}), wait for bounce candle",
                "target": f"T1: {mid:,.1f} (prior day mid)  |  T2: {pdh:,.1f} (PDH)",
                "stop": f"Below PDL ({pdl:,.1f}) - 10pts",
                "context": "Range environment — buy the dip at support. "
                           "Mean-reversion trade aligned with dealer hedging flow.",
                "invalidation": f"Strong close below PDL — structure breakdown",
            }
        else:
            scenarios_export["primary"] = {
                "label": "Follow price action vs Today Open",
                "probability": "MEDIUM",
                "bias": "NEUTRAL",
                "entry": f"If above today open ({today_open:,.1f}): look for long setups at support. "
                        f"If below: look for short setups at resistance.",
                "target": f"PDH ({pdh:,.1f}) for longs  |  PDL ({pdl:,.1f}) for shorts",
                "stop": f"Through today open in opposite direction",
                "context": f"SPX GEX near neutral — no strong dealer bias. "
                           f"Trade {key} on its own structure and price action.",
                "invalidation": "No clear setup — stand aside",
            }

    payload = {
        "instrument":   key,
        "scan_time":    now_iso,
        "spot":         spot,
        "proxy_mode":   True,
        "metrics": {
            "net_gex":         0,
            "call_gex":        0,
            "put_gex":         0,
            "regime":          spx_regime,
            "call_wall":       0,
            "put_wall":        0,
            "max_gex_strike":  0,
            "zero_gex_strike": 0,
            "max_pain":        0,
            "put_call_ratio":  0,
            "sentiment":       "No direct options data",
            "iv_skew_ratio":   0,
            "iv_skew_bias":    "",
            "resistance_levels": [pdh] if pdh else [],
            "support_levels":    [pdl] if pdl else [],
            "spx_regime":        spx_regime,
            "spx_gex_bn":        round(spx_gex_bn, 2),
        },
        "top_strikes":   {"calls": [], "puts": []},
        "gex_by_strike": {"strikes": [], "gex_values": []},
        "oi_by_strike":  {"strikes": [], "call_oi": [], "put_oi": []},
        "volume_profile": {},
        "cta":            {},
        "macro": {
            "vix":           round(float(vix or 0), 2),
            "vix_signal":    _vix_label(vix),
            "dxy":           round(float(macro.get("dxy") or 0), 2),
            "dxy_signal":    "DXY data",
            "us10y":         round(float(macro.get("yield_10y") or 0), 2),
            "us10y_signal":  "US 10Y yield",
            "prev_day_high": pdh,
            "prev_day_low":  pdl,
            "weekly_open":   weekly_open,
        },
        "session_structure": {
            "london_open":      "08:00",
            "ny_open":          "13:30",
            "ny_close":         "21:00",
            "today_open":       today_open,
            "session_high":     session_hi,
            "session_low":      session_lo,
            "key_time_events":  [],
        },
        "situation": {
            "narrative":             narrative,
            "confluence_scenario":   "A",
            "scenario_name":         f"{key} — Cross-Market Proxy",
            "scenario_description":  f"No direct options data. Levels derived from CTrader session structure. "
                                     f"GEX regime applied via SPX cross-market correlation.",
            "levels_table":          [],
        },
        "key_levels":     key_levels_export,
        "trade_scenarios": scenarios_export,
    }

    js_content = (
        f"// GEX & OI Dashboard Data — {key}\n"
        f"// Auto-generated by gex_oi_agent.py at {now_iso} — DO NOT EDIT MANUALLY\n"
        f"window.GEX_OI_DATA = window.GEX_OI_DATA || {{}};\n"
        f"window.GEX_OI_DATA[\"{key}\"] = "
        + json.dumps(payload, indent=2, ensure_ascii=False)
        + ";\n"
    )

    out_path = os.path.join(data_dir, f"{key}_latest.js")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(js_content)
    print(f"  DASHBOARD_EXPORT: {out_path}")


def _vix_label(vix) -> str:
    if not isinstance(vix, (int, float)):
        return "N/A"
    if vix < 15: return "Low vol — range bias, premium sellers in control"
    if vix < 20: return "Normal vol"
    if vix < 30: return "Elevated — consider reducing size"
    return "High vol — specialist setups only"


def _build_key_levels_export(spot: float, gex, oi) -> list:
    """Build the dashboard key_levels list from GEX/OI results."""
    levels = []

    call_wall = float(gex.call_wall or 0)
    put_wall  = float(gex.put_wall  or 0)
    max_gex   = float(gex.max_gex_strike  or 0)
    zero_gex  = float(gex.zero_gex_strike or 0)
    max_pain  = float(oi.max_pain or 0)

    # Call Wall
    if call_wall:
        entry = round(call_wall + 3, 0)
        stop  = round(call_wall - 12, 0)
        t1    = max_gex if max_gex > call_wall else round(call_wall + 50, 0)
        res_above = [r for r in gex.resistance_levels if r > t1]
        t2    = round(res_above[0], 0) if res_above else round(t1 + 50, 0)
        rr1   = round((t1 - entry) / max(entry - stop, 0.1), 1)
        levels.append({
            "level":   round(call_wall, 1),
            "label":   "Call Wall",
            "type":    "resistance",
            "entry":   f"15-min close above {call_wall:,.0f} → entry {entry:,.0f}",
            "stop":    f"{stop:,.0f} (back inside wall = failed breakout)",
            "rr":      f"~{rr1}:1 to T1",
            "target1": f"{t1:,.0f}",
            "target2": f"{t2:,.0f}",
            "context": (f"Dealers short calls at {call_wall:,.0f} must buy futures as price rises — "
                        f"creating overhead resistance. A confirmed 15-min close above triggers "
                        f"accelerating dealer buy flow (short-squeeze dynamics)."),
        })

    # Put Wall
    if put_wall:
        entry = round(put_wall + 3, 0)
        stop  = round(put_wall - 10, 0)
        t1    = max_pain if (max_pain and put_wall < max_pain < (call_wall or 1e9)) else (
                    round((call_wall + put_wall) / 2, 0) if call_wall else round(put_wall + 50, 0))
        rr1   = round((t1 - entry) / max(entry - stop, 0.1), 1)
        levels.append({
            "level":   round(put_wall, 1),
            "label":   "Put Wall",
            "type":    "support",
            "entry":   f"Bounce at {put_wall:,.0f} zone → entry {entry:,.0f}",
            "stop":    f"{stop:,.0f} (sustained break below put wall = support removed)",
            "rr":      f"~{rr1}:1 to T1",
            "target1": f"{t1:,.0f}",
            "target2": f"{call_wall:,.0f}" if call_wall else "—",
            "context": (f"Dealers long puts at {put_wall:,.0f} sell futures as price falls — "
                        f"natural buy pressure that cushions declines. Strongest structural "
                        f"support in the current GEX framework."),
        })

    # Max Pain
    if max_pain and abs(max_pain - call_wall) > 5 and abs(max_pain - put_wall) > 5:
        levels.append({
            "level":   round(max_pain, 1),
            "label":   "Max Pain",
            "type":    "pin",
            "entry":   f"Fade extremes back toward {max_pain:,.0f}",
            "stop":    f"Confirmed close through call or put wall",
            "rr":      "~2:1",
            "target1": f"{max_pain:,.0f}",
            "target2": "—",
            "context": (f"The price where total open interest (calls + puts) is worth the least — "
                        f"market makers have a structural incentive to drift price toward "
                        f"{max_pain:,.0f} into weekly expiry (Friday close)."),
        })

    # Zero GEX Trigger
    if zero_gex and abs(zero_gex - call_wall) > 5 and abs(zero_gex - put_wall) > 5:
        entry = round(zero_gex - 3, 0)
        stop  = round(zero_gex + 12, 0)
        near_supp = float(gex.support_levels[0]) if gex.support_levels else round(zero_gex - 50, 0)
        rr1   = round((entry - near_supp) / max(stop - entry, 0.1), 1)
        levels.append({
            "level":   round(zero_gex, 1),
            "label":   "Zero GEX",
            "type":    "trigger",
            "entry":   f"15-min close below {zero_gex:,.0f} → entry {entry:,.0f}",
            "stop":    f"{stop:,.0f} (recovery above Zero GEX)",
            "rr":      f"~{rr1}:1",
            "target1": f"{near_supp:,.0f}",
            "target2": f"{put_wall:,.0f}" if put_wall else "—",
            "context": (f"Below {zero_gex:,.0f} net dealer gamma turns negative — "
                        f"dealers begin amplifying moves rather than damping them. "
                        f"Moves accelerate and can run further than in a pinned regime."),
        })

    # Sort highest level first (resistance at top, support at bottom)
    levels.sort(key=lambda x: x["level"], reverse=True)
    return levels


def _scenario_export(scenario: dict, letter: str) -> dict:
    """Convert a TradePlan scenario dict to dashboard export format."""
    name = scenario.get("name", f"Scenario {letter}")

    name_upper = name.upper()
    if any(w in name_upper for w in ("LONG", "BREAKOUT", "BOUNCE", "BUY", "TREND")):
        bias = "LONG"
    elif any(w in name_upper for w in ("SHORT", "REJECTION", "FADE", "SELL", "BREAKDOWN")):
        bias = "SHORT"
    else:
        bias = "NEUTRAL"

    prob_map = {"A": "HIGH", "B": "MEDIUM", "C": "LOW"}
    probability = prob_map.get(letter, "MEDIUM")

    t1 = scenario.get("target_1", "")
    t2 = scenario.get("target_2", "")
    target = f"{t1}  |  T2: {t2}" if t1 and t2 else (t1 or t2 or "—")

    trigger = scenario.get("trigger", "")
    note    = scenario.get("note", "")

    return {
        "label":       name,
        "probability": probability,
        "bias":        bias,
        "entry":       scenario.get("entry_zone", trigger or "—"),
        "target":      target,
        "stop":        scenario.get("stop", "—"),
        "context":     scenario.get("why", note or ""),
        "invalidation": trigger or note or "—",
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GEX & OI Trading Session Briefing")
    parser.add_argument("--instrument", action="append", default=[],
                        choices=list(INSTRUMENTS.keys()),
                        help="Instrument to analyse (repeatable)")
    parser.add_argument("--all", action="store_true", help="Analyse all instruments")
    parser.add_argument("--output", choices=["chat", "dashboard", "both"],
                        default=None,
                        help="Output destination: chat (terminal only), dashboard (JS export only), both")

    args = parser.parse_args()

    if args.all:
        instruments = list(INSTRUMENTS.keys())
    elif args.instrument:
        instruments = args.instrument
    else:
        instruments = ["US500", "XAUUSD"]

    # Output destination selection
    output_dest = args.output
    if not output_dest:
        print("\n  Where would you like the output?")
        print("    [1] Chat / Terminal  (default)")
        print("    [2] Dashboard only   (updates dashboard/data/*.js, no terminal output)")
        print("    [3] Both")
        try:
            choice = input("  Choice [1/2/3, Enter=1]: ").strip() or "1"
        except (EOFError, KeyboardInterrupt):
            choice = "1"
        output_dest = {"1": "chat", "2": "dashboard", "3": "both"}.get(choice, "chat")

    # Suppress terminal output if dashboard-only
    if output_dest == "dashboard":
        import io
        sys.stdout = io.StringIO()

    run_session_briefing(instruments)

    if output_dest == "dashboard":
        # Restore stdout, confirm silently
        sys.stdout = sys.__stdout__
        print(f"  Dashboard updated for: {', '.join(instruments)}")
        print(f"  Open: GEX&OI/dashboard/index.html")
