"""
Pre-Session Report Generator

Orchestrates all analysis modules and produces a structured,
trader-ready report before each trading session.

Every output is labelled with its data tier so the trader knows
exactly what is Tier 1 (true order flow) vs Tier 2 (structural only)
and what manual confirmation is required on their own platform.
"""

from datetime import datetime, timezone
from typing import List, Optional, Dict

from data.models import (
    Candle, SessionLevels, MarketStructure,
    OrderBlock, FairValueGap, LiquidityPool, SetupSignal
)
from analysis.structure import (
    detect_order_blocks, detect_fvgs, detect_liquidity_pools,
    detect_bos_choch, compute_atr
)
from analysis.delta import compute_session_summary, TIER1_UNAVAILABLE
from analysis.volume_profile import build_volume_profile
from analysis.sessions import compute_session_levels, session_bias_note, current_kill_zone
from analysis.zones import compute_premium_discount
from analysis.confluence import SetupContext, score_setup, compute_position_size
from config import DATA_TIER_LABELS, WATCHLIST, ACCOUNT_SIZE_USD


SEP  = "═" * 65
SEP2 = "─" * 65
SEP3 = "·" * 65


def generate_asset_report(
    symbol: str,
    candles_htf: List[Candle],     # Daily / 4H for context
    candles_mtf: List[Candle],     # 1H / 15M for setup identification
    candles_ltf: Optional[List[Candle]] = None,  # 5M for entry timing
    news_events: Optional[List[dict]] = None,
) -> str:
    """
    Generate a full pre-session analysis for one asset.
    Returns a formatted string report.
    """
    if not candles_htf or not candles_mtf:
        return f"[{symbol}] Insufficient data to generate report."

    data_tier  = candles_htf[0].data_tier
    tier_label = DATA_TIER_LABELS.get(data_tier, "Unknown")
    current    = candles_mtf[-1].close

    lines = []
    lines.append(SEP)
    lines.append(f"  {symbol}  |  Current: {current:.5f}")
    lines.append(f"  Data Quality: {tier_label}")
    lines.append(SEP2)

    # ── MARKET STRUCTURE ────────────────────────────────────────────────────
    structure_htf = detect_bos_choch(candles_htf)
    structure_mtf = detect_bos_choch(candles_mtf)
    atr           = compute_atr(candles_mtf)

    lines.append("  MARKET STRUCTURE")
    lines.append(f"  Higher-TF trend : {structure_htf.trend.upper()}")
    lines.append(f"  Intraday trend  : {structure_mtf.trend.upper()}")
    if structure_htf.choch_confirmed:
        lines.append(f"  ⚠️  CHoCH on higher TF at {structure_htf.last_choch_price:.5f} — possible trend reversal")
    if structure_mtf.choch_confirmed:
        lines.append(f"  CHoCH on intraday TF at {structure_mtf.last_choch_price:.5f} — watch for reversal")
    lines.append("")

    # ── PREMIUM / DISCOUNT ──────────────────────────────────────────────────
    if structure_htf.recent_swing_highs and structure_htf.recent_swing_lows:
        recent_high = max(s.price for s in structure_htf.recent_swing_highs[-3:])
        recent_low  = min(s.price for s in structure_htf.recent_swing_lows[-3:])
        zone = compute_premium_discount(recent_high, recent_low, current)
        lines.append("  PREMIUM / DISCOUNT")
        lines.append(f"  Range: {recent_low:.5f} – {recent_high:.5f}")
        lines.append(f"  Status: {zone.zone_label}")
        lines.append(f"  OTE zone: {zone.ote_low:.5f} – {zone.ote_high:.5f}")
        lines.append("")
    else:
        zone = None

    # ── SESSION LEVELS ──────────────────────────────────────────────────────
    session_lvls = compute_session_levels(candles_mtf)
    lines.append("  SESSION LEVELS")
    if session_lvls.prior_day_high:
        lines.append(f"  Prior day high : {session_lvls.prior_day_high:.5f}  ← BSL target")
    if session_lvls.prior_day_low:
        lines.append(f"  Prior day low  : {session_lvls.prior_day_low:.5f}  ← SSL target")
    if session_lvls.asia_high:
        lines.append(f"  Asian high     : {session_lvls.asia_high:.5f}")
    if session_lvls.asia_low:
        lines.append(f"  Asian low      : {session_lvls.asia_low:.5f}")
    if session_lvls.midnight_open:
        bias = "PREMIUM — favour SHORTS" if session_lvls.in_premium else "DISCOUNT — favour LONGS"
        lines.append(f"  Midnight open  : {session_lvls.midnight_open:.5f}  [{bias}]")
    lines.append("")

    # Session narrative
    bias_note = session_bias_note(session_lvls)
    for note_line in bias_note.split("\n"):
        lines.append(f"  {note_line}")
    lines.append("")

    # ── VOLUME PROFILE ──────────────────────────────────────────────────────
    vp = build_volume_profile(candles_mtf)
    lines.append("  VOLUME PROFILE (approximated from OHLCV)")
    if vp.poc:
        lines.append(f"  POC : {vp.poc:.5f}  ← magnetic level")
    if vp.vah:
        lines.append(f"  VAH : {vp.vah:.5f}  ← resistance / target")
    if vp.val:
        lines.append(f"  VAL : {vp.val:.5f}  ← support / target")
    lvns = vp.get_lvns()
    if lvns:
        lines.append(f"  LVNs: {', '.join(f'{p:.5f}' for p in sorted(lvns)[:5])}")
    lines.append(f"  Note: {vp.data_note}")
    lines.append("")

    # ── DELTA / ORDER FLOW ──────────────────────────────────────────────────
    lines.append("  ORDER FLOW ANALYSIS")
    if data_tier == 1:
        delta_summary = compute_session_summary(candles_mtf)
        if delta_summary.get("available"):
            lines.append(f"  Tier 1 data: {delta_summary['bias']}")
            lines.append(f"  CVD trend  : {delta_summary['cvd_direction'].upper()}")
            lines.append(f"  Taker buy  : {delta_summary['taker_buy_pct']:.1%} | "
                         f"Taker sell : {delta_summary['taker_sell_pct']:.1%}")
            if delta_summary["bearish_divergence"]:
                lines.append("  ⚠️  BEARISH CVD DIVERGENCE — price rising but CVD declining")
            if delta_summary["bullish_divergence"]:
                lines.append("  ⚠️  BULLISH CVD DIVERGENCE — price falling but CVD rising")
            if delta_summary["absorption_detected"]:
                lines.append("  ⚠️  Absorption signal detected (high volume, small body)")
        else:
            lines.append(f"  {delta_summary.get('reason', TIER1_UNAVAILABLE['reason'])}")
    else:
        lines.append(f"  {TIER1_UNAVAILABLE['reason']}")
        lines.append("  Manually check: footprint absorption, delta, CVD, DOM before entering.")
    lines.append("")

    # ── ORDER BLOCKS IN PLAY ────────────────────────────────────────────────
    obs = [ob for ob in detect_order_blocks(candles_mtf) if not ob.is_mitigated]
    if obs:
        lines.append("  ACTIVE ORDER BLOCKS (unmitigated)")
        for ob in sorted(obs, key=lambda x: abs(x.midpoint - current))[:4]:
            dist  = ((ob.midpoint - current) / current) * 100
            side  = "above" if ob.midpoint > current else "below"
            lines.append(
                f"  [{ob.direction.upper()[:4]} OB | {ob.timeframe}] "
                f"{ob.low:.5f}–{ob.high:.5f}  "
                f"({dist:+.2f}%, {side} current)  "
                f"Quality: {ob.quality_score}/5"
                + ("  ← Preceded by liquidity grab" if ob.preceded_by_liquidity_grab else "")
            )
        lines.append("")

    # ── FAIR VALUE GAPS ─────────────────────────────────────────────────────
    fvgs = [f for f in detect_fvgs(candles_mtf) if not f.is_mitigated]
    if fvgs:
        lines.append("  ACTIVE FAIR VALUE GAPS (unmitigated)")
        for fvg in sorted(fvgs, key=lambda x: abs(x.midpoint - current))[:4]:
            dist = ((fvg.midpoint - current) / current) * 100
            side = "above" if fvg.midpoint > current else "below"
            lines.append(
                f"  [{fvg.direction.upper()[:4]} FVG | {fvg.timeframe}] "
                f"{fvg.gap_low:.5f}–{fvg.gap_high:.5f}  "
                f"(midpoint {fvg.midpoint:.5f}, {dist:+.2f}%, {side})"
            )
        lines.append("")

    # ── LIQUIDITY POOLS ─────────────────────────────────────────────────────
    pools = [p for p in detect_liquidity_pools(candles_mtf) if not p.is_swept]
    bsl = sorted([p for p in pools if p.pool_type == "BSL"], key=lambda x: x.price)
    ssl = sorted([p for p in pools if p.pool_type == "SSL"], key=lambda x: x.price, reverse=True)

    if bsl or ssl:
        lines.append("  LIQUIDITY POOLS (unswept stops)")
        for p in bsl[-3:]:
            lines.append(f"  BSL above: {p.price:.5f}  [tests: {p.test_count}, strength: {p.strength}]")
        for p in ssl[:3]:
            lines.append(f"  SSL below: {p.price:.5f}  [tests: {p.test_count}, strength: {p.strength}]")
        lines.append("")

    # ── NEWS / RISK EVENTS ──────────────────────────────────────────────────
    if news_events:
        lines.append("  NEWS & RISK EVENTS")
        for event in news_events:
            impact = event.get("impact", "UNKNOWN")
            icon   = "🔴" if impact == "HIGH" else "🟡" if impact == "MEDIUM" else "⚪"
            lines.append(f"  {icon} {impact}: {event.get('title', '')} at {event.get('time', '')}")
        lines.append("")

    lines.append(SEP3)
    return "\n".join(lines)


def generate_full_report(
    assets: Dict[str, Dict[str, List[Candle]]],
    news_events: Optional[List[dict]] = None,
) -> str:
    """
    Generate the complete pre-session report for all configured assets.

    assets: {symbol: {"htf": [Candle, ...], "mtf": [Candle, ...]}}
    """
    now = datetime.now(timezone.utc)
    kz  = current_kill_zone(now)

    lines = []
    lines.append(SEP)
    lines.append("  ORDER FLOW PRE-SESSION REPORT")
    lines.append(f"  Generated: {now.strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"  Kill Zone: {kz.replace('_',' ').upper() if kz else 'None — outside high-probability windows'}")
    lines.append(SEP)
    lines.append("")
    lines.append("  DATA QUALITY NOTICE")
    lines.append(f"  {DATA_TIER_LABELS[1]}")
    lines.append(f"  Applies to: BTC, ETH, SOL (Binance taker volume)")
    lines.append("")
    lines.append(f"  {DATA_TIER_LABELS[2]}")
    lines.append(f"  Applies to: EUR/USD, GBP/USD, SPX, NDX, DAX, Gold, Oil")
    lines.append("  For these markets: analyse structural levels below, then confirm")
    lines.append("  order flow manually on Bookmap / Sierra Chart / ATAS before entering.")
    lines.append("")

    for symbol, data in assets.items():
        htf = data.get("htf", [])
        mtf = data.get("mtf", [])
        ltf = data.get("ltf")
        asset_report = generate_asset_report(symbol, htf, mtf, ltf, news_events)
        lines.append(asset_report)
        lines.append("")

    lines.append(SEP)
    lines.append("  END OF REPORT")
    lines.append(SEP)

    return "\n".join(lines)
