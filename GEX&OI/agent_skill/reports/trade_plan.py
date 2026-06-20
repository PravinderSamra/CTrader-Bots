"""
Trade plan generator.
Produces an educational, structured session briefing aimed at new traders.
Format: explain WHY each level matters, give precise entry/stop/target, flag risks.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import zoneinfo

UK_TZ = zoneinfo.ZoneInfo("Europe/London")


@dataclass
class TradePlan:
    instrument: str
    session_date: str
    session_time_uk: str
    spot_price: float
    gex_regime: str
    gex_value: float
    primary_bias: str
    primary_scenario: dict
    alternative_scenarios: list[dict] = field(default_factory=list)
    key_levels: dict = field(default_factory=dict)
    chart_instructions: list[str] = field(default_factory=list)
    risk_notes: list[str] = field(default_factory=list)
    confluence_score: int = 5
    session_structure: Optional[dict] = None
    iv_skew: Optional[dict] = None
    opex: Optional[dict] = None


def generate_trade_plan(
    instrument: str,
    spot_price: float,
    gex_result,
    oi_result,
    macro: dict,
    session: str = "LONDON_NY",
    session_structure: Optional[dict] = None,
    iv_skew: Optional[dict] = None,
) -> TradePlan:
    now_uk = datetime.now(tz=UK_TZ)
    key_levels = _build_key_levels(gex_result, oi_result, spot_price, session_structure)
    # Inject macro scalars for the formatter
    key_levels["_vix"] = macro.get("_vix") or macro.get("vix")
    key_levels["_yield_10y"] = macro.get("_yield_10y") or macro.get("yield_10y")
    key_levels["_dxy"] = macro.get("_dxy") or macro.get("dxy")
    bias = _determine_bias(gex_result, oi_result, macro, spot_price)
    primary = _build_primary_scenario(bias, spot_price, gex_result, oi_result)
    alternatives = _build_alternatives(spot_price, gex_result, oi_result)
    chart_instructions = _build_chart_instructions(gex_result, oi_result, spot_price)
    risk_notes = _build_risk_notes(gex_result, oi_result, macro)
    confluence = _score_confluence(gex_result, oi_result, macro, bias)

    return TradePlan(
        instrument=instrument,
        session_date=now_uk.strftime("%A %d %B %Y"),
        session_time_uk=now_uk.strftime("%H:%M %Z"),
        spot_price=spot_price,
        gex_regime=gex_result.regime,
        gex_value=gex_result.total_gex,
        primary_bias=bias,
        primary_scenario=primary,
        alternative_scenarios=alternatives,
        key_levels=key_levels,
        chart_instructions=chart_instructions,
        risk_notes=risk_notes,
        confluence_score=confluence,
        session_structure=session_structure,
        iv_skew=iv_skew,
        opex=macro.get("opex"),
    )


def format_trade_plan(plan: TradePlan) -> str:
    """Format TradePlan as an educational briefing for a new trader."""
    L = []
    sep = "=" * 68
    thin = "─" * 68

    L.append(sep)
    L.append(f"  GEX & OI TRADE PLAN — {plan.instrument}")
    L.append(f"  {plan.session_date}  |  {plan.session_time_uk}  |  Spot: {plan.spot_price:,.2f}")
    L.append(sep)

    # ── 1. WHAT IS GEX TELLING US? ──────────────────────────────────────
    L.append("")
    L.append("WHAT IS GEX TELLING US?")
    L.append(thin)
    regime_colour_map = {
        "PINNED":   f"PINNED (+${plan.gex_value:.1f}B)",
        "NEUTRAL":  f"NEUTRAL (${plan.gex_value:.1f}B)",
        "TRENDING": f"TRENDING (${plan.gex_value:.1f}B)",
    }
    L.append(f"  Net GEX: {regime_colour_map.get(plan.gex_regime, plan.gex_regime)}")
    L.append("")

    if plan.gex_regime == "TRENDING":
        L.append("  Dealers (options market makers) are SHORT GAMMA.")
        L.append("  When price RISES: they must BUY futures to stay hedged → amplifies the rally.")
        L.append("  When price FALLS: they must SELL futures to stay hedged → amplifies the drop.")
        L.append("  Plain English: DO NOT fight momentum. Wait for direction, then trade WITH it.")
        L.append("  ✗ Avoid: fading moves, picking tops/bottoms, holding against strong trend")
        L.append("  ✓ Do:    trade breakouts, ride momentum, honour your stops quickly")
    elif plan.gex_regime == "PINNED":
        L.append("  Dealers are LONG GAMMA — they act as shock absorbers.")
        L.append("  When price RISES: they SELL futures → dampens the rally.")
        L.append("  When price FALLS: they BUY futures → cushions the drop.")
        L.append("  Plain English: The market tends to REVERT to the mean. Fade extremes.")
        L.append("  ✓ Do:    fade moves to the GEX walls, target the mid-range / max pain")
        L.append("  ✗ Avoid: chasing breakouts — they tend to snap back")
    else:
        L.append("  GEX is near neutral — no strong dealer influence on direction.")
        L.append("  Price is free to move on technical and macro signals alone.")

    # ── 2. MACRO ENVIRONMENT ─────────────────────────────────────────────
    L.append("")
    L.append("MARKET ENVIRONMENT")
    L.append(thin)
    vix = plan.opex and plan.opex or {}
    # (macro context is passed in via plan, extracted below from the key_levels or direct)
    # We pass macro into key_levels so it's accessible
    kl = plan.key_levels
    vix_val = kl.get("_vix")
    yield_10y = kl.get("_yield_10y")
    dxy = kl.get("_dxy")
    opex = plan.opex or {}

    if vix_val is not None:
        vix_label = (
            "LOW — cheap options, market is calm. Breakouts can be clean."
            if vix_val < 15 else
            "NORMAL — standard volatility environment."
            if vix_val < 20 else
            "ELEVATED — reduce position size by 25-50%. Moves are larger than usual."
            if vix_val < 30 else
            "HIGH — high-risk environment. Specialist setups only, small size."
        )
        L.append(f"  VIX {vix_val:.1f} — {vix_label}")
        L.append(f"  Why it matters: VIX measures how much the options market expects the S&P 500")
        L.append(f"  to move over the next 30 days. Higher = bigger expected swings.")

    if yield_10y is not None:
        headwind = yield_10y > 4.5
        L.append(f"  10Y Yield {yield_10y:.2f}% — {'mild headwind for equities (above 4.5%)' if headwind else 'acceptable level'}")
        L.append(f"  Why it matters: Higher yields = bonds become more attractive vs stocks, drawing")
        L.append(f"  money away from equities. Above 4.5% tends to pressure the S&P 500.")

    if dxy is not None:
        L.append(f"  DXY {dxy:.2f} — {'Strong dollar = headwind for gold/risk assets' if dxy > 103 else 'Neutral dollar environment'}")

    if opex:
        days = opex.get('days_to_monthly_opex', '?')
        opex_date = opex.get('monthly_opex_date', 'N/A')
        L.append(f"")
        L.append(f"  OPEX (Options Expiry): {opex_date} — {days} days away")
        L.append(f"  Why it matters: As expiry approaches (especially the last 3 days), dealers")
        L.append(f"  hedge more aggressively. GEX levels become stronger 'magnets' near OPEX.")
        L.append(f"  Reliability: {opex.get('gex_reliability', 'Unknown')}")

    # ── 3. IV SKEW ───────────────────────────────────────────────────────
    if plan.iv_skew and plan.iv_skew.get("skew_ratio"):
        L.append("")
        L.append("IMPLIED VOLATILITY SKEW")
        L.append(thin)
        sk = plan.iv_skew
        put_iv = sk.get("put_iv_pct", 0)
        call_iv = sk.get("call_iv_pct", 0)
        ratio = sk.get("skew_ratio", 1)
        L.append(f"  5% OTM Put IV: {put_iv:.1f}%  |  5% OTM Call IV: {call_iv:.1f}%  |  Ratio: {ratio:.2f}")
        L.append(f"  {sk.get('description', '')}")
        L.append("")
        L.append("  What is IV skew? It's the difference in 'price' (implied volatility) between")
        L.append("  put options (bets on a fall) and call options (bets on a rise) at equal")
        L.append("  distances from current price. When puts are much more expensive than calls,")
        L.append("  the market is paying a big premium to protect against a drop — signalling")
        L.append("  institutional caution even if price appears to be rising.")

    # ── 4. SESSION STRUCTURE ─────────────────────────────────────────────
    ss = plan.session_structure
    if ss:
        L.append("")
        L.append("SESSION STRUCTURE (from Pepperstone/CTrader candles)")
        L.append(thin)
        if "prev_day_high" in ss:
            L.append(f"  Prior Day High:  {ss['prev_day_high']:>10,.1f}  ← bulls must clear this to confirm upside")
            L.append(f"  Prior Day Low:   {ss['prev_day_low']:>10,.1f}  ← bears target this; break = next level down")
        if "prev_day_close" in ss:
            L.append(f"  Prior Day Close: {ss['prev_day_close']:>10,.1f}")
        if "today_open" in ss:
            L.append(f"  Today's Open:    {ss['today_open']:>10,.1f}  ← above/below tells you who is in control at open")
        if "weekly_open" in ss:
            L.append(f"  Weekly Open:     {ss['weekly_open']:>10,.1f}  ← above = weekly bullish bias")
        if "session_high" in ss:
            L.append(f"  Session High:    {ss['session_high']:>10,.1f}")
            L.append(f"  Session Low:     {ss['session_low']:>10,.1f}")
        L.append("")
        L.append("  Why these matter: Prior day's high and low are where institutions placed")
        L.append("  their largest orders. A break above PDH = new buyers stepping in. A break")
        L.append("  below PDL = sellers taking control. These levels combine with GEX walls")
        L.append("  to create your highest-probability zones.")

    # ── 5. KEY LEVELS ────────────────────────────────────────────────────
    L.append("")
    L.append("KEY LEVELS — WHAT EACH ONE DOES")
    L.append(thin)
    spot = plan.spot_price
    gex = plan.key_levels

    # Build level table sorted high to low
    level_items = [
        ("GEX Resistance", gex.get("gex_resistance_levels", []), "#", "orange"),
        ("Call Wall",      [gex.get("call_wall")],               "CALL WALL — dealer selling ceiling", "orange"),
        ("Max GEX Pin",    [gex.get("max_gex_strike")],          "MAX GEX PIN — gravity level", "white"),
        ("Spot",           [spot],                                f"◄ YOU ARE HERE", "white"),
        ("Max Pain",       [gex.get("max_pain")],                "MAX PAIN — expiry magnet", "yellow"),
        ("Zero GEX",       [gex.get("zero_gex_strike")],         "ZERO GEX — below here moves accelerate", "red"),
        ("GEX Support",    gex.get("gex_support_levels", []),    "#", "blue"),
        ("Put Wall",       [gex.get("put_wall")],                "PUT WALL — dealer buying floor", "blue"),
    ]

    all_levels = []
    for name, values, label, colour in level_items:
        if not values:
            continue
        for v in values:
            if v is None:
                continue
            if name in ("GEX Resistance", "GEX Support"):
                display_label = f"GEX {'Resistance' if name == 'GEX Resistance' else 'Support'} — dealer {'selling' if name == 'GEX Resistance' else 'buying'} cluster"
            else:
                display_label = label
            all_levels.append((v, name, display_label))

    all_levels.sort(key=lambda x: x[0], reverse=True)

    for price_val, name, label in all_levels:
        at_spot = "  ◄◄ SPOT" if abs(price_val - spot) < 3 else ""
        rel = "above spot" if price_val > spot else "below spot" if price_val < spot else "at spot"
        L.append(f"  {price_val:>9,.0f}  {label}{at_spot}")

    L.append("")
    L.append("  EXPLANATION OF KEY LEVELS:")
    L.append("  Call Wall: The strike with the highest call open interest ABOVE spot. Dealers")
    L.append("    who sold these calls must sell futures as price approaches, creating resistance.")
    L.append("    A sustained CLOSE above = forced dealer buying (breakout accelerates).")
    L.append("  Put Wall: Same logic below spot. Dealers who sold puts must BUY futures as")
    L.append("    price falls toward it. Natural floor. A break BELOW = dealers stop buying.")
    L.append("  Max Pain: The strike where option sellers (dealers) lose the least money.")
    L.append("    The market tends to drift toward this level as expiry approaches.")
    L.append("  Max GEX Pin: Where dealer delta (hedging need) is most concentrated.")
    L.append("    Strong gravitational pull. Often becomes a magnet intraday.")
    L.append("  Zero GEX Line: Where net GEX flips from positive to negative. Crossing")
    L.append("    this level changes dealer behaviour — moves accelerate beyond it.")

    # ── 5b. LEVEL CONFLUENCE (session structure + GEX) ──────────────────
    if ss and ss.get("prev_day_high"):
        L.append("")
        L.append("LEVEL CONFLUENCE — Where Session Structure Meets GEX")
        L.append(thin)
        pdh = ss.get("prev_day_high", 0)
        pdl = ss.get("prev_day_low", 0)
        today_open = ss.get("today_open", spot)
        call_wall_l = kl.get("call_wall", 0)
        put_wall_l = kl.get("put_wall", 0)
        max_pain_l = kl.get("max_pain", 0)

        # Check if PDH is near call wall
        if call_wall_l and abs(pdh - call_wall_l) / call_wall_l < 0.005:
            L.append(f"  ★ STRONG RESISTANCE: Prior Day High ({pdh:,.1f}) ≈ Call Wall ({call_wall_l:,.0f})")
            L.append(f"    Two independent resistance forces at the same level = very difficult to break.")
        elif pdh > call_wall_l > spot:
            L.append(f"  Note: PDH ({pdh:,.1f}) sits ABOVE the Call Wall ({call_wall_l:,.0f}).")
            L.append(f"    Prior day closed above the call wall then retreated. This is significant:")
            L.append(f"    → The market proved it can trade above {call_wall_l:,.0f} but chose not to hold there.")
            L.append(f"    → Watch for dealers to defend this level again on the retest.")
        elif pdh < call_wall_l:
            L.append(f"  PDH ({pdh:,.1f}) is BELOW the Call Wall ({call_wall_l:,.0f}).")
            L.append(f"    The market has not tested the call wall recently. First touch tends to be strongest.")

        if today_open > call_wall_l:
            L.append(f"  Today opened ABOVE the Call Wall ({today_open:,.1f} vs {call_wall_l:,.0f}).")
            L.append(f"    If current spot is below it, the market has since retreated — this is a flag.")
        elif today_open < call_wall_l:
            L.append(f"  Today opened BELOW the Call Wall at {today_open:,.1f}.")
            L.append(f"    A move up to {call_wall_l:,.0f} would be testing fresh resistance.")

        # Max pain vs session levels
        if pdl and max_pain_l and abs(pdl - max_pain_l) / pdl < 0.008:
            L.append(f"  ★ PDL ({pdl:,.1f}) is near Max Pain ({max_pain_l:,.0f}) — double support zone.")
            L.append(f"    If price reaches here, expect strong buying interest.")

    # ── 6. TODAY'S SCENARIOS ─────────────────────────────────────────────
    L.append("")
    L.append("TODAY'S TRADE SCENARIOS")
    L.append(thin)

    # Context paragraph
    call_wall = gex.get("call_wall", spot * 1.03)
    put_wall = gex.get("put_wall", spot * 0.97)
    max_pain = gex.get("max_pain", spot)
    max_gex = gex.get("max_gex_strike", spot)
    zero_gex = gex.get("zero_gex_strike", spot)
    dist_to_call = call_wall - spot
    dist_to_put = spot - put_wall

    L.append(f"  Context: Spot {spot:,.0f} sits {dist_to_call:+.0f} pts from Call Wall ({call_wall:,.0f})")
    L.append(f"  and {dist_to_put:,.0f} pts above Put Wall ({put_wall:,.0f}).")

    now_uk = datetime.now(tz=UK_TZ)
    hour = now_uk.hour
    if hour < 7:
        session_note = "Asian session (low liquidity). Best to observe only — levels form during EU/NY."
    elif hour < 10:
        session_note = "London open window (07:00-10:00 BST) — EU levels can test pre-NY. Watch PDH/PDL."
    elif hour < 13:
        session_note = "London mid-session. Quieter period. NY open at 14:30 BST is the catalyst."
    elif hour < 17:
        session_note = "NY open / overlap window (14:30-17:00 BST) — HIGHEST probability for breakouts."
    else:
        session_note = "NY afternoon / closing session. Look for close above/below key levels."
    L.append(f"  Now: {now_uk.strftime('%H:%M %Z')} — {session_note}")

    L.append("")
    for i, scenario in enumerate([plan.primary_scenario] + plan.alternative_scenarios, 1):
        name = scenario.get("name", f"Scenario {i}")
        L.append(f"  {'PRIMARY — ' if i == 1 else ''}{name}")
        L.append(f"  {'─' * 62}")
        trigger = scenario.get("trigger", "")
        L.append(f"  Trigger:    {trigger}")
        why = scenario.get("why", "")
        if why:
            L.append(f"  Why:        {why}")
        entry = scenario.get("entry_zone", "")
        if entry:
            L.append(f"  Entry:      {entry}")
        stop = scenario.get("stop", "")
        if stop:
            L.append(f"  Stop:       {stop}")
        t1 = scenario.get("target_1", "")
        t2 = scenario.get("target_2", "")
        rr = scenario.get("rr", "")
        if t1:
            L.append(f"  Target 1:   {t1}")
        if t2:
            L.append(f"  Target 2:   {t2}")
        if rr:
            L.append(f"  R:R:        {rr}")
        note = scenario.get("note", "")
        if note:
            L.append(f"  Note:       {note}")
        L.append("")

    # ── 7. CHART INSTRUCTIONS ────────────────────────────────────────────
    L.append("CHART MARKING INSTRUCTIONS")
    L.append(thin)
    L.append("  Mark these on your CTrader chart before the session:")
    for i, instruction in enumerate(plan.chart_instructions, 1):
        L.append(f"  {i:>2}. {instruction}")

    # ── 8. CONFLUENCE SCORE + RISK ───────────────────────────────────────
    L.append("")
    L.append("CONFLUENCE & RISK")
    L.append(thin)
    stars = "★" * plan.confluence_score + "☆" * (10 - plan.confluence_score)
    L.append(f"  Signal Strength: {stars} ({plan.confluence_score}/10)")
    L.append(f"  Bias: {plan.primary_bias}")
    L.append("")
    for note in plan.risk_notes:
        L.append(f"  ⚠  {note}")

    L.append("")
    L.append(sep)

    return "\n".join(L)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _determine_bias(gex_result, oi_result, macro: dict, spot: float) -> str:
    """
    Determine directional bias from the combined signals.
    Returns a descriptive string rather than a single word, since GEX itself
    is a regime indicator (TRENDING/PINNED), not a direction indicator.
    """
    max_pain = oi_result.max_pain
    call_wall = gex_result.call_wall
    put_wall = gex_result.put_wall
    pcr = oi_result.put_call_ratio
    regime = gex_result.regime

    # Distance context
    pct_to_call = (call_wall - spot) / spot * 100 if call_wall else None
    pct_above_pain = (spot - max_pain) / spot * 100 if max_pain else 0

    if regime == "PINNED":
        if spot > max_pain * 1.005:
            return "RANGE SHORT — above max pain, gravitational pull lower. Fade rally to call wall."
        elif spot < max_pain * 0.995:
            return "RANGE LONG — below max pain, gravitational pull higher. Fade dips to put wall."
        else:
            return "RANGE NEUTRAL — at max pain. Price likely to oscillate between walls."

    # TRENDING regime — direction comes from structure, not GEX
    if pct_to_call is not None and pct_to_call < 0.2:
        return f"BREAKOUT WATCH — spot pressing Call Wall ({call_wall:,.0f}). Break = long; rejection = short."
    elif pct_to_call is not None and pct_to_call < 0.5:
        return f"CALL WALL TEST IMMINENT — {pct_to_call:.1f}% to key resistance at {call_wall:,.0f}."
    elif pcr < 0.7:
        return "TREND LONG — low P/C ratio (call heavy) + TRENDING regime. Follow upside momentum."
    elif pcr > 1.3:
        return "TREND SHORT — high P/C ratio (put heavy) + TRENDING regime. Follow downside momentum."
    else:
        return "TRENDING — wait for session open to reveal direction. Do not pre-bias."


def _build_key_levels(gex_result, oi_result, spot: float, ss: Optional[dict]) -> dict:
    """Collect all key levels including macro refs for the formatter."""
    # Note: macro scalars are injected as _prefixed keys
    return {
        "call_wall":           gex_result.call_wall,
        "put_wall":            gex_result.put_wall,
        "max_gex_strike":      gex_result.max_gex_strike,
        "zero_gex_strike":     gex_result.zero_gex_strike,
        "max_pain":            oi_result.max_pain,
        "gex_support_levels":  gex_result.support_levels,
        "gex_resistance_levels": gex_result.resistance_levels,
    }


def _build_primary_scenario(bias: str, spot: float, gex_result, oi_result) -> dict:
    call_wall = gex_result.call_wall
    put_wall = gex_result.put_wall
    max_gex = gex_result.max_gex_strike
    max_pain = oi_result.max_pain
    zero_gex = gex_result.zero_gex_strike
    regime = gex_result.regime

    dist_to_call = call_wall - spot

    if regime == "TRENDING" and dist_to_call < spot * 0.005:
        # Spot pressing into Call Wall — this is the primary setup
        entry_long = round(call_wall + 3, 0)
        stop_long = round(call_wall - 12, 0)
        t1_long = max_gex if max_gex > call_wall else round(call_wall + 50, 0)
        # T2 must be different from T1 — pick the next resistance level above T1
        res_above_t1 = [r for r in gex_result.resistance_levels if r > t1_long]
        t2_long = res_above_t1[0] if res_above_t1 else round(t1_long + 50, 0)
        rr1 = round((t1_long - entry_long) / (entry_long - stop_long), 1) if entry_long > stop_long else "N/A"
        rr2 = round((t2_long - entry_long) / (entry_long - stop_long), 1) if entry_long > stop_long else "N/A"
        return {
            "name": "LONG BREAKOUT above Call Wall",
            "trigger": f"15-min candle CLOSES above {call_wall:,.0f} (not just a wick — body must close above)",
            "why": (f"A close above the Call Wall forces dealers to buy futures to re-hedge their short calls. "
                    f"This self-reinforcing buying pressure is what makes breakouts here run fast."),
            "entry_zone": f"{entry_long:,.0f} — confirmed close above the wall",
            "stop": f"{stop_long:,.0f} — back inside the wall = breakout failed",
            "target_1": f"{t1_long:,.0f} — Max GEX pin (take 50% here)",
            "target_2": f"{t2_long:,.0f} — next GEX resistance cluster",
            "rr": f"~{rr1}:1 to T1  |  ~{rr2}:1 to T2. Trail stop to breakeven after T1.",
            "note": "If price spikes above then immediately closes back below the wall, that is a bull trap — stand aside or look for the short.",
        }
    elif regime == "TRENDING":
        # General trending — follow momentum from structure levels
        entry = round(put_wall * 1.001, 0)
        stop = round(put_wall * 0.998, 0)
        t1 = max_pain if max_pain > put_wall else round(put_wall + (call_wall - put_wall) * 0.3, 0)
        t2 = max_gex if max_gex > t1 else call_wall
        rr1 = round((t1 - entry) / (entry - stop), 1) if entry > stop and entry > t1 else "N/A"
        return {
            "name": "TREND LONG from Put Wall Support",
            "trigger": f"Price tests {put_wall:,.0f} (put wall) and a 15-min candle closes green with buyers",
            "why": f"In a TRENDING regime, moves are amplified. The put wall at {put_wall:,.0f} is where dealers must buy futures — it's the strongest structural support available.",
            "entry_zone": f"{put_wall:,.0f} – {round(put_wall * 1.002, 0):,.0f}",
            "stop": f"{stop:,.0f} — below the put wall = dealer support removed",
            "target_1": f"{t1:,.0f} — max pain / mid-range",
            "target_2": f"{t2:,.0f} — max GEX pin",
            "rr": f"~2:1 to T1",
        }
    else:
        # PINNED — fade to walls
        mid = round((call_wall + put_wall) / 2, 0)
        return {
            "name": "RANGE FADE — long from put wall, short from call wall",
            "trigger": f"Price reaches put wall ({put_wall:,.0f}) OR call wall ({call_wall:,.0f})",
            "why": f"Positive GEX means dealers stabilise price. Fading moves to the walls and targeting max pain ({max_pain:,.0f}) is the statistically dominant strategy.",
            "entry_zone": f"Longs: {put_wall:,.0f} – {round(put_wall * 1.003, 0):,.0f} | Shorts: {round(call_wall * 0.997, 0):,.0f} – {call_wall:,.0f}",
            "stop": f"Longs: below {round(put_wall * 0.998, 0):,.0f} | Shorts: above {round(call_wall * 1.002, 0):,.0f}",
            "target_1": f"{mid:,.0f} — midpoint",
            "target_2": f"{max_pain:,.0f} — max pain (expiry magnet)",
            "rr": "~2:1",
        }


def _build_alternatives(spot: float, gex_result, oi_result) -> list[dict]:
    call_wall = gex_result.call_wall
    put_wall = gex_result.put_wall
    zero_gex = gex_result.zero_gex_strike
    max_pain = oi_result.max_pain
    regime = gex_result.regime

    rejection_entry = round(call_wall * 0.9985, 0)
    rejection_stop = round(call_wall * 1.002, 0)
    rejection_t1 = max_pain
    rejection_t2 = put_wall if put_wall < max_pain else round(max_pain - (call_wall - max_pain) * 0.5, 0)
    rr_rej = round((rejection_entry - rejection_t1) / (rejection_stop - rejection_entry), 1) if rejection_stop > rejection_entry else "N/A"

    # Better T2 for rejection short: first GEX support below max_pain (more realistic than put_wall)
    gex_supports = [s for s in gex_result.support_levels if s < max_pain]
    rejection_t2_near = gex_supports[0] if gex_supports else round(max_pain - 30, 0)
    rr_rej_t2 = round((rejection_entry - rejection_t2_near) / (rejection_stop - rejection_entry), 1) if rejection_stop > rejection_entry else "N/A"

    alts = [
        {
            "name": "REJECTION SHORT at Call Wall",
            "trigger": f"Price spikes into {call_wall:,.0f}–{round(call_wall * 1.003, 0):,.0f}, then 15-min candle closes back below {round(call_wall - 8, 0):,.0f}",
            "why": (f"A failed breakout at the call wall traps bulls who bought the spike. "
                    f"Their stops cluster just above {call_wall:,.0f}. Dealers also stop buying futures. "
                    f"These two forces accelerate the move lower."),
            "entry_zone": f"{rejection_entry:,.0f} — on break of the rejection candle's low",
            "stop": f"{rejection_stop:,.0f} — above the rejection spike",
            "target_1": f"{rejection_t1:,.0f} — max pain (take 60% here)",
            "target_2": f"{rejection_t2_near:,.0f} — nearest GEX support (trail remainder)",
            "rr": f"~{rr_rej}:1 to T1  |  ~{rr_rej_t2}:1 to T2",
        },
        {
            "name": "STAND ASIDE / WAIT",
            "trigger": f"Price grinds between {round(call_wall - 30, 0):,.0f} and {call_wall:,.0f} for 90+ minutes without a decisive close",
            "why": "Tight oscillation without commitment means neither buyers nor sellers have conviction. This is the market 'waiting' — usually for a news event or the next session open.",
            "entry_zone": "N/A — no trade",
            "stop": "N/A",
            "target_1": f"Reassess at London open (08:00 BST) or NY open (14:30 BST)",
            "note": "Patience is a position. Missing a setup costs nothing. Forcing a trade in noise costs capital.",
        },
    ]

    if zero_gex and zero_gex < spot:
        # Use nearest GEX support as realistic T1, not the put wall (which may be hundreds of pts away)
        near_support = gex_result.support_levels[0] if gex_result.support_levels else round(zero_gex - 40, 0)
        breakdown_stop = round(zero_gex + 12, 0)
        breakdown_entry = round(zero_gex - 3, 0)
        rr_break = round((breakdown_entry - near_support) / (breakdown_stop - breakdown_entry), 1) if breakdown_stop > breakdown_entry else "N/A"
        alts.append({
            "name": "BREAKDOWN below Zero GEX Line",
            "trigger": f"Price closes a 15-min candle below {zero_gex:,.0f} (the Zero GEX crossover)",
            "why": (f"Below {zero_gex:,.0f}, net GEX turns more negative. Dealer selling accelerates. "
                    f"Think of it as removing the last brake pad — once broken, moves speed up with less to slow them."),
            "entry_zone": f"{breakdown_entry:,.0f} on confirmed close below",
            "stop": f"{breakdown_stop:,.0f} — back above the crossover",
            "target_1": f"{near_support:,.0f} — nearest GEX support",
            "rr": f"~{rr_break}:1",
        })

    return alts


def _build_chart_instructions(gex_result, oi_result, spot: float) -> list[str]:
    call_wall = gex_result.call_wall
    put_wall = gex_result.put_wall
    max_pain = oi_result.max_pain
    max_gex = gex_result.max_gex_strike
    zero_gex = gex_result.zero_gex_strike

    instructions = [
        f"ORANGE thick line at {call_wall:,.0f} — CALL WALL (dealer resistance ceiling)",
        f"BLUE thick line at {put_wall:,.0f} — PUT WALL (dealer support floor)",
        f"YELLOW dashed line at {max_pain:,.0f} — MAX PAIN (expiry gravitational target)",
        f"WHITE dashed line at {max_gex:,.0f} — MAX GEX PIN (strongest gravitational level)",
        f"RED dotted line at {zero_gex:,.0f} — ZERO GEX CROSSOVER (volatility trigger — break here = moves accelerate)",
    ]

    for i, lvl in enumerate(gex_result.support_levels[:3], 1):
        instructions.append(f"LIGHT BLUE line at {lvl:,.0f} — GEX Support #{i} (dealer buying cluster)")
    for i, lvl in enumerate(gex_result.resistance_levels[:3], 1):
        instructions.append(f"LIGHT ORANGE line at {lvl:,.0f} — GEX Resistance #{i} (dealer selling cluster)")

    for item in oi_result.top_put_strikes[:2]:
        instructions.append(
            f"BLUE zone at {item['strike']:,.0f} — High OI Put ({item['oi']:,} contracts) — max support strike")
    for item in oi_result.top_call_strikes[:2]:
        instructions.append(
            f"ORANGE zone at {item['strike']:,.0f} — High OI Call ({item['oi']:,} contracts) — max resistance strike")

    return instructions


def _build_risk_notes(gex_result, oi_result, macro: dict) -> list[str]:
    notes = []
    vix = macro.get("vix", 20)
    opex = macro.get("opex", {})

    if gex_result.total_gex < -1.0:
        notes.append(
            "STRONGLY NEGATIVE GEX: Dealers amplify every move. Do NOT fade momentum. "
            "Honour stops immediately — losses can compound fast in this regime.")

    if isinstance(vix, float) and vix > 25:
        notes.append(
            f"VIX {vix:.1f} — elevated volatility. Reduce position size by 30-50%. "
            "Stops need to be wider, which means smaller lots for the same £ risk.")

    if oi_result.put_call_ratio > 1.5:
        notes.append(
            f"P/C ratio {oi_result.put_call_ratio:.2f} — very heavy put positioning. "
            "Market is over-hedged. If support holds and shorts squeeze, the move UP can be sharp.")

    if oi_result.put_call_ratio < 0.6:
        notes.append(
            f"P/C ratio {oi_result.put_call_ratio:.2f} — extreme call dominance (complacency). "
            "Limited downside protection. Market is vulnerable to a sharp pullback on any negative catalyst.")

    days_to_opex = opex.get("days_to_monthly_opex", 30)
    if isinstance(days_to_opex, int) and days_to_opex <= 3:
        notes.append(
            "OPEX THIS WEEK: GEX pinning effects are at maximum. Max Pain acts as a very strong "
            "gravitational level. Expect price to oscillate around it heading into expiry.")

    notes.append(
        "Economic calendar: CHECK before every session. Stand aside 15 min before and 5 min after "
        "major US releases (FOMC, NFP, CPI, PPI). GEX levels do not protect against news-driven gaps.")

    notes.append(
        f"Pepperstone spread on this instrument: factor into your stop placement. "
        "Entry → Stop distance should be at least 3× the spread to avoid being stopped by noise.")

    return notes


def _score_confluence(gex_result, oi_result, macro: dict, bias: str) -> int:
    score = 5

    if abs(gex_result.total_gex) > 1.0:
        score += 1  # clear regime
    if gex_result.put_wall and gex_result.call_wall:
        score += 1  # defined walls

    pcr = oi_result.put_call_ratio
    if pcr > 1.2 or pcr < 0.8:
        score += 1  # directional lean

    vix = macro.get("vix", 20)
    if isinstance(vix, (int, float)) and vix < 15:
        score += 1  # low vol = cleaner setups
    elif isinstance(vix, (int, float)) and vix > 30:
        score -= 1  # high vol = noisy

    mp = oi_result.max_pain
    spot = gex_result.spot_price
    if mp and abs(spot - mp) / spot < 0.015:
        score += 1  # near max pain = strong expiry influence

    return min(10, max(1, score))
