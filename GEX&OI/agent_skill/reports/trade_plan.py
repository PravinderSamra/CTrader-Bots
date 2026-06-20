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
    vol_profile: Optional[dict] = None
    cta_data: Optional[dict] = None


def generate_trade_plan(
    instrument: str,
    spot_price: float,
    gex_result,
    oi_result,
    macro: dict,
    session: str = "LONDON_NY",
    session_structure: Optional[dict] = None,
    iv_skew: Optional[dict] = None,
    vol_profile: Optional[dict] = None,
    cta_data: Optional[dict] = None,
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
        vol_profile=vol_profile,
        cta_data=cta_data,
    )


def format_trade_plan(plan: TradePlan) -> str:
    """Format TradePlan as an educational briefing for a new trader."""
    L = []
    sep = "=" * 68
    thin = "─" * 68
    thick = "━" * 68

    kl = plan.key_levels
    vix_val = kl.get("_vix")
    yield_10y = kl.get("_yield_10y")
    dxy = kl.get("_dxy")
    opex = plan.opex or {}
    ss = plan.session_structure
    spot = plan.spot_price

    call_wall = kl.get("call_wall", spot * 1.03)
    put_wall = kl.get("put_wall", spot * 0.97)
    max_pain = kl.get("max_pain", spot)
    max_gex = kl.get("max_gex_strike", spot)
    zero_gex = kl.get("zero_gex_strike")

    sk = plan.iv_skew or {}
    skew_ratio = sk.get("skew_ratio")
    skew_bullish = skew_ratio is not None and skew_ratio < 0.95
    skew_bearish = skew_ratio is not None and skew_ratio > 1.10

    # ── HEADER ───────────────────────────────────────────────────────────
    L.append(sep)
    L.append(f"  GEX & OI TRADE PLAN — {plan.instrument}")
    L.append(f"  {plan.session_date}  |  {plan.session_time_uk}  |  Spot: {plan.spot_price:,.2f}")
    L.append(sep)

    # ── SITUATION AT A GLANCE ────────────────────────────────────────────
    L.append("")
    L.append("SITUATION AT A GLANCE")
    L.append(thin)

    # Quick-reference levels table
    L.append(f"  {'Level':<20}  {'Value':>9}   Significance")
    L.append(f"  {'─'*20}  {'─'*9}   {'─'*32}")

    def _sig(val, spot_p):
        diff = val - spot_p
        arrow = "▲" if diff > 0 else "▼"
        return f"{arrow} {abs(diff):,.0f} pts {'above' if diff > 0 else 'below'} spot"

    vp = plan.vol_profile or {}
    vp_poc      = vp.get("poc")
    vp_hvn      = vp.get("hvn_levels", [])
    vp_lvn      = vp.get("lvn_levels", [])
    vp_bucket   = vp.get("bucket_size", 5)

    def _vol_tag(price: float) -> str:
        if not vp:
            return ""
        if vp_poc and abs(price - vp_poc) < vp_bucket * 1.5:
            return " [POC]"
        if any(abs(price - h) < vp_bucket * 1.5 for h in vp_hvn):
            return " [HVN]"
        if any(abs(price - l) < vp_bucket * 1.5 for l in vp_lvn):
            return " [LVN — thin]"
        return ""

    glance_levels = []
    glance_levels.append(("Live Spot", spot, "◄ Current price"))
    if call_wall:
        glance_levels.append(("Call Wall", call_wall,
            f"Dealer resistance  ({_sig(call_wall, spot)}){_vol_tag(call_wall)}"))
    if put_wall:
        glance_levels.append(("Put Wall", put_wall,
            f"Dealer support floor  ({_sig(put_wall, spot)}){_vol_tag(put_wall)}"))
    if max_gex:
        glance_levels.append(("Max GEX Pin", max_gex,
            f"Gravitational magnet  ({_sig(max_gex, spot)}){_vol_tag(max_gex)}"))
    if max_pain:
        glance_levels.append(("Max Pain", max_pain,
            f"Expiry magnet  ({_sig(max_pain, spot)}){_vol_tag(max_pain)}"))
    if zero_gex:
        glance_levels.append(("Zero GEX", zero_gex,
            f"Volatility trigger  ({_sig(zero_gex, spot)}){_vol_tag(zero_gex)}"))
    if vp_poc:
        glance_levels.append(("Volume POC", vp_poc,
            f"Highest-volume price  ({_sig(vp_poc, spot)}) — price revisits this"))
    if ss:
        if ss.get("prev_day_high"):
            glance_levels.append(("Prior Day High", ss["prev_day_high"],
                f"Inst. sell zone yesterday  ({_sig(ss['prev_day_high'], spot)}){_vol_tag(ss['prev_day_high'])}"))
        if ss.get("prev_day_low"):
            glance_levels.append(("Prior Day Low", ss["prev_day_low"],
                f"Inst. buy zone yesterday  ({_sig(ss['prev_day_low'], spot)}){_vol_tag(ss['prev_day_low'])}"))

    glance_levels.sort(key=lambda x: x[1], reverse=True)
    for name, val, sig in glance_levels:
        at = "  ◄ HERE" if abs(val - spot) < 5 else ""
        L.append(f"  {name:<20}  {val:>9,.0f}   {sig}{at}")

    if vp_hvn:
        nearby_hvn = [h for h in vp_hvn if abs(h - spot) / spot < 0.02]
        if nearby_hvn:
            L.append(f"  {'HVN nodes (nearby)':<20}  {'':>9}   "
                     f"{', '.join(f'{h:,.0f}' for h in sorted(nearby_hvn, reverse=True))} — thick volume zones")
    if vp_lvn:
        nearby_lvn = [l for l in vp_lvn if abs(l - spot) / spot < 0.02]
        if nearby_lvn:
            L.append(f"  {'LVN zones (nearby)':<20}  {'':>9}   "
                     f"{', '.join(f'{l:,.0f}' for l in sorted(nearby_lvn, reverse=True))} — thin; fast moves here")

    # Narrative summary — synthesises the situation and what could unfold
    L.append("")
    dist_to_call = call_wall - spot if call_wall else 0
    dist_to_put = spot - put_wall if put_wall else 0
    regime_str = {
        "TRENDING": f"TRENDING (Net GEX ${plan.gex_value:.0f}B — dealers short gamma, amplifying moves)",
        "PINNED":   f"PINNED (Net GEX +${plan.gex_value:.0f}B — dealers long gamma, dampening moves)",
        "NEUTRAL":  f"NEUTRAL (Net GEX ${plan.gex_value:.0f}B)",
    }.get(plan.gex_regime, plan.gex_regime)
    L.append(f"  GEX Regime: {regime_str}.")
    L.append("")

    # Build a specific narrative based on how close spot is to the call wall
    if call_wall and dist_to_call < spot * 0.005:
        L.append(f"  The {call_wall:,.0f} Call Wall is right at spot — this is the most critical")
        L.append(f"  level on the chart right now. You are just {dist_to_call:.0f} pts below it.")
        if plan.gex_regime == "TRENDING":
            next_res = max_gex if max_gex and max_gex > call_wall else round(call_wall + 50, 0)
            next_res2 = [r for r in kl.get("gex_resistance_levels", []) if r > next_res]
            L.append(f"  A decisive 15-min CLOSE above {call_wall:,.0f} forces dealers to buy futures")
            L.append(f"  (re-hedging their short calls) — that buying adds fuel to any breakout,")
            L.append(f"  opening a run to {next_res:,.0f} (Max GEX Pin) and then {next_res2[0]:,.0f} if momentum holds.")
            L.append(f"  A REJECTION at {call_wall:,.0f} and close back below {zero_gex:,.0f} (Zero GEX)")
            L.append(f"  removes the last brake pad — dealer selling then accelerates the drop")
            L.append(f"  toward the GEX Support at {kl.get('gex_support_levels', [round(call_wall-60,0)])[0]:,.0f}.")
        else:
            L.append(f"  In a PINNED regime, a spike to {call_wall:,.0f} tends to be faded — dealers")
            L.append(f"  sell futures as price rises, capping the move. Target: Max Pain {max_pain:,.0f}.")
    elif call_wall and dist_to_call < spot * 0.015:
        L.append(f"  Spot is {dist_to_call:.0f} pts below the {call_wall:,.0f} Call Wall — close enough")
        L.append(f"  that a test is likely this session. The call wall is where dealer selling")
        L.append(f"  concentrates; watch for a break-and-hold above, or a fade from it.")
        L.append(f"  Below {zero_gex:,.0f} (Zero GEX), moves accelerate — that is the line to watch")
        L.append(f"  on the downside. Support below: {kl.get('gex_support_levels', [put_wall])[0]:,.0f}.")
    else:
        L.append(f"  Spot is {dist_to_call:.0f} pts below the {call_wall:,.0f} Call Wall")
        L.append(f"  and {dist_to_put:.0f} pts above the {put_wall:,.0f} Put Wall.")
        L.append(f"  Primary trade zone: between these two walls. Watch Zero GEX at {zero_gex:,.0f}")
        L.append(f"  — a break below it shifts dealer hedging from dampening to amplifying drops.")

    # ── CONFLUENCE SCENARIO MATRIX ───────────────────────────────────────
    L.append("")
    L.append(thick)
    L.append("  CONFLUENCE SCENARIO MATRIX")
    L.append(thick)
    scenario_id, matched_signals, scenario_tactic = _identify_confluence_scenario(
        plan, spot, call_wall, put_wall, zero_gex, vp, vp_bucket, skew_ratio
    )

    scenarios_ref = [
        ("A", "MEAN REVERSION / CEILING",
         ["Positive GEX (PINNED regime)", "High OI cluster at level", "HVN at resistance"],
         "Dealers AND volume both cap the move. Fade to resistance, target Max Pain.",
         "Short the bounce from resistance OR long from support. Take profits at midpoint."),
        ("B", "DIRECTIONAL ACCELERATION",
         ["Negative GEX (TRENDING regime)", "IV Skew > 1.10", "Price at key structural level"],
         "Whichever direction breaks holds and accelerates. Dealer flow adds fuel.",
         "Wait for confirmed 15-min close, trade WITH direction, trail stops. No fading."),
        ("C", "FAST-THROUGH ZONE (LVN)",
         ["Price approaching Low Volume Node", "Thin volume = few resting orders"],
         "Price moves quickly through LVN with little resistance to slow it.",
         "Set wider targets. Do not take profits early while inside an LVN zone."),
        ("D", "STRUCTURAL ACCUMULATION / SQUEEZE SETUP",
         ["OI cluster building at support", "High P/C ratio (heavy put positioning)", "CTA short trigger near"],
         "Large positions being built. Market is over-hedged. Short squeeze setup forming.",
         "Look for low-risk longs near OI cluster. Target Max GEX Pin on the squeeze."),
    ]

    for sid, sname, sig_list, behavior, tactic in scenarios_ref:
        marker = "  ★ TODAY'S MATCH ►" if sid == scenario_id else "   "
        L.append(f"{marker} SCENARIO {sid}: {sname}")
        L.append(f"     Data required:  {' + '.join(sig_list)}")
        L.append(f"     Behavior:       {behavior}")
        L.append(f"     Tactic:         {tactic}")
        if sid == scenario_id:
            L.append(f"")
            L.append(f"     TODAY'S SIGNALS PRESENT:")
            for sig in matched_signals:
                L.append(f"       ✓ {sig}")
            L.append(f"     WHAT TO DO: {scenario_tactic}")
        L.append("")

    # ── 1. GEX REGIME BRIEFING ───────────────────────────────────────────
    L.append("")
    L.append("MARKET REGIME — WHAT THIS MEANS IN PRACTICE")
    L.append(thin)

    if plan.gex_regime == "TRENDING":
        L.append(f"  Net GEX: ${plan.gex_value:.1f}B — dealers are SHORT GAMMA. In plain English:")
        L.append("")
        L.append("  → Price goes UP:   dealers must BUY futures to stay hedged — adds fuel")
        L.append("    to the rally. The more price rises, the more they must buy.")
        L.append("  → Price goes DOWN: dealers must SELL futures to stay hedged — adds")
        L.append("    pressure to the drop. The more price falls, the more they sell.")
        L.append("")
        L.append("  This is why TRENDING regimes produce sharp, sustained directional moves")
        L.append("  rather than the choppy up-and-down you see in a calm market.")
        L.append("")
        L.append("  RULE: Do NOT fight momentum. Do NOT try to pick tops or bottoms.")
        L.append("  Wait for a key level to act as a trigger (Call Wall, Zero GEX, PDH/PDL),")
        L.append("  get a confirmed 15-min candle close, then trade WITH the direction.")
        L.append("")
        if call_wall:
            L.append(f"  Specifically today: a BREAK above the {call_wall:,.0f} Call Wall forces dealer")
            L.append(f"  buying → breakout accelerates. A FALL through the {zero_gex:,.0f} Zero GEX")
            L.append(f"  triggers dealer selling → drop accelerates. These are your two triggers.")
        if vix_val is not None and vix_val < 20 and plan.gex_value < -0.5:
            L.append("")
            L.append(f"  IMPORTANT — VIX {vix_val:.1f} (low) yet GEX is deeply negative: the options")
            L.append(f"  market is not pricing in big moves, but dealer positioning WILL amplify")
            L.append(f"  any move that does occur. This means breakouts can be sharper and faster")
            L.append(f"  than VIX alone suggests. Low VIX = cheap stop distance, so keep stops tight.")
    elif plan.gex_regime == "PINNED":
        L.append(f"  Net GEX: +${plan.gex_value:.1f}B — dealers are LONG GAMMA. In plain English:")
        L.append("")
        L.append("  → Price goes UP:   dealers SELL futures to re-hedge → caps the rally.")
        L.append("  → Price goes DOWN: dealers BUY futures to re-hedge → cushions the drop.")
        L.append("")
        L.append("  The market acts like it has springs attached — moves away from the centre")
        L.append("  get pushed back. This creates the rangebound, mean-reverting environment.")
        L.append("")
        L.append("  RULE: Fade moves to the walls. The trade is: sell into the Call Wall,")
        L.append("  buy into the Put Wall, target Max Pain in the middle. Avoid chasing")
        L.append(f"  breakouts — in a PINNED regime they tend to snap back within 1-2 candles.")
    else:
        L.append(f"  Net GEX: ${plan.gex_value:.1f}B — near neutral. Dealers have no strong hedging")
        L.append("  obligation. This session is driven by technical levels and macro news,")
        L.append("  not dealer flow. Use PDH/PDL as your primary reference.")

    # ── 2. MACRO SNAPSHOT ────────────────────────────────────────────────
    L.append("")
    L.append("MACRO SNAPSHOT — WHAT EACH DATA POINT MEANS FOR YOUR TRADE")
    L.append(thin)

    if vix_val is not None:
        vix_label = (
            "LOW — calm market. Options are cheap. Breakouts tend to be clean, sustained runs."
            if vix_val < 15 else
            "NORMAL — standard volatility environment. No size adjustment needed."
            if vix_val < 20 else
            "ELEVATED — reduce your lot size by 25-50%. Candle ranges are wider."
            if vix_val < 30 else
            "HIGH — high-risk environment. Small size only. Specialist setups."
        )
        L.append(f"  VIX {vix_val:.1f} — {vix_label}")
        L.append(f"  Why: VIX is the market's 30-day expected move forecast for the S&P 500.")
        L.append(f"  Low VIX = small expected moves = stops can be tighter = better R:R.")
        L.append(f"  High VIX = large expected moves = your stop must be wider = smaller lots.")

    if yield_10y is not None:
        headwind = yield_10y > 4.5
        if headwind:
            L.append(f"  10Y Yield {yield_10y:.2f}% — ABOVE 4.5% — mild headwind for equities.")
            L.append(f"  Why: When yields are above ~4.5%, bonds pay investors enough that some")
            L.append(f"  money rotates OUT of stocks INTO bonds. This creates a persistent")
            L.append(f"  ceiling on equity rallies. If yields spike today, cap your long targets.")
        else:
            L.append(f"  10Y Yield {yield_10y:.2f}% — below 4.5% — not a headwind for equities.")
            L.append(f"  Why: At this level, bonds are not attractive enough to pull money away")
            L.append(f"  from stocks. The yield environment supports the long side today.")

    if dxy is not None:
        if dxy > 103:
            L.append(f"  DXY {dxy:.2f} — STRONG DOLLAR. Headwind for gold and risk assets.")
            L.append(f"  Why: A strong dollar makes US assets more expensive for foreign buyers")
            L.append(f"  and compresses gold (priced in dollars). If you are also trading XAUUSD,")
            L.append(f"  the strong dollar adds a headwind to any gold long.")
        else:
            L.append(f"  DXY {dxy:.2f} — neutral dollar. No significant currency drag today.")

    if opex:
        days = opex.get('days_to_monthly_opex', '?')
        opex_date = opex.get('monthly_opex_date', 'N/A')
        rel = opex.get('gex_reliability', '')
        L.append(f"  OPEX (monthly options expiry): {opex_date} — {days} days away.")
        L.append(f"  Why: As expiry approaches, dealers hedge more aggressively. GEX walls")
        L.append(f"  become stronger 'magnets' and Max Pain becomes more magnetic. Within")
        L.append(f"  3 days of OPEX, pin risk is very high — price often converges on Max Pain.")
        L.append(f"  Reliability today: {rel}")

    cta = plan.cta_data or {}
    if cta:
        L.append(f"  CTA Positioning ({cta.get('etf_ticker', 'ETF')} MAs): {cta.get('signal', '')}")
        sma_50  = cta.get("sma_50")
        sma_200 = cta.get("sma_200")
        etf_cur = cta.get("current_etf")
        if sma_50 and etf_cur:
            dist_50 = etf_cur - sma_50
            L.append(f"  ETF price {etf_cur:.2f} vs 50-day MA {sma_50:.2f} "
                     f"({'above' if dist_50 > 0 else 'below'} by {abs(dist_50):.2f})")
        if sma_200 and etf_cur:
            dist_200 = etf_cur - sma_200
            L.append(f"  ETF price vs 200-day MA {sma_200:.2f} "
                     f"({'above' if dist_200 > 0 else 'below'} by {abs(dist_200):.2f})")
        L.append(f"  Why: CTAs are large systematic funds that buy when trend is up (above 50-day MA)")
        L.append(f"  and sell when trend turns down. Their flows amplify moves in the trend direction.")
        L.append(f"  Today: {cta.get('implication', '')}")

    if skew_ratio is not None:
        put_iv = sk.get("put_iv_pct", 0)
        call_iv = sk.get("call_iv_pct", 0)
        L.append("")
        L.append(f"  IV SKEW: Put IV {put_iv:.1f}%  vs  Call IV {call_iv:.1f}%  →  ratio {skew_ratio:.2f}")
        L.append(f"  {sk.get('description', '')}")
        L.append("")
        L.append(f"  What this is: IV (implied volatility) is the 'price' of an option.")
        L.append(f"  The skew compares put options 5% below spot vs call options 5% above")
        L.append(f"  spot. A ratio above 1.0 means puts cost MORE than equivalent calls.")
        L.append("")
        if skew_ratio > 1.10:
            L.append(f"  What is CAUSING this: Institutions are paying {skew_ratio:.2f}× more to hedge")
            L.append(f"  against a fall than to position for a rise. This is an insurance premium.")
            L.append(f"  Think of it like a building owner paying extra for flood insurance —")
            L.append(f"  they don't KNOW a flood is coming, but they are worried enough to pay up.")
            L.append("")
            L.append(f"  What this MEANS for your trade:")
            L.append(f"  → The rejection short at {call_wall:,.0f} has institutional backing.")
            L.append(f"    Smart money is hedged for a fall from this level.")
            L.append(f"  → If the breakout long fires, move your stop to breakeven quickly —")
            L.append(f"    institutions may use any rally above {call_wall:,.0f} to add puts.")
            L.append(f"  → This does NOT mean the market WILL fall, but the probability")
            L.append(f"    of a meaningful rejection is higher than usual.")
        elif skew_ratio < 0.95:
            L.append(f"  What is CAUSING this: Calls are MORE expensive than puts — the market")
            L.append(f"  is pricing in a sharp UPSIDE move. This is unusual (equities normally")
            L.append(f"  have put skew). Institutions may be buying calls ahead of a catalyst.")
            L.append(f"  What this MEANS: The breakout long above {call_wall:,.0f} has extra fuel.")
            L.append(f"  Dealer hedging + call buying pressure = breakouts can run far and fast.")

    # ── 3. SESSION STRUCTURE ─────────────────────────────────────────────
    if ss:
        L.append("")
        L.append("SESSION STRUCTURE")
        L.append(thin)
        if "prev_day_high" in ss:
            L.append(f"  Prior Day High (PDH):  {ss['prev_day_high']:>10,.1f}")
            L.append(f"  Prior Day Low  (PDL):  {ss['prev_day_low']:>10,.1f}")
        if "prev_day_close" in ss:
            L.append(f"  Prior Day Close:       {ss['prev_day_close']:>10,.1f}")
        if "today_open" in ss:
            L.append(f"  Today's Open:          {ss['today_open']:>10,.1f}")
        if "weekly_open" in ss:
            L.append(f"  Weekly Open:           {ss['weekly_open']:>10,.1f}")
        if "session_high" in ss:
            L.append(f"  Session High:          {ss['session_high']:>10,.1f}")
            L.append(f"  Session Low:           {ss['session_low']:>10,.1f}")
        L.append("")
        L.append("  PDH and PDL mark where institutions placed their biggest orders yesterday.")
        L.append("  A break and CLOSE above PDH = new buyers are stepping in — bullish.")
        L.append("  A break and CLOSE below PDL = sellers taking control — bearish.")

    # ── 4. KEY LEVELS — LEVEL-CENTRIC NARRATIVE ──────────────────────────
    L.append("")
    L.append(thick)
    L.append("  KEY LEVELS — WHAT EACH ONE MEANS & WHAT TO DO THERE")
    L.append(thick)

    # Build sorted list of all levels (high to low) for the narrative
    all_levels = []
    special_levels = {call_wall, put_wall, max_gex, max_pain, zero_gex}
    for v in kl.get("gex_resistance_levels", [])[:3]:
        if v and v not in special_levels:
            all_levels.append((v, "GEX_RES"))
    if call_wall:
        all_levels.append((call_wall, "CALL_WALL"))
    if max_gex and max_gex != call_wall and max_gex != put_wall:
        all_levels.append((max_gex, "MAX_GEX"))
    if max_pain and max_pain != max_gex:
        all_levels.append((max_pain, "MAX_PAIN"))
    if zero_gex and zero_gex != max_pain:
        all_levels.append((zero_gex, "ZERO_GEX"))
    for v in kl.get("gex_support_levels", [])[:3]:
        if v and v not in special_levels:
            all_levels.append((v, "GEX_SUP"))
    if put_wall:
        all_levels.append((put_wall, "PUT_WALL"))

    # Add session structure levels if available
    if ss:
        pdh = ss.get("prev_day_high")
        pdl = ss.get("prev_day_low")
        weekly_open = ss.get("weekly_open")
        if pdh:
            all_levels.append((pdh, "PDH"))
        if pdl:
            all_levels.append((pdl, "PDL"))
        if weekly_open:
            all_levels.append((weekly_open, "WEEKLY_OPEN"))

    all_levels.sort(key=lambda x: x[0], reverse=True)

    for level_price, level_type in all_levels:
        _append_level_block(L, level_price, level_type, spot, kl, ss, vix_val, yield_10y, skew_ratio, plan.gex_regime, opex, thin)

    # ── 5. TRADE SCENARIOS ───────────────────────────────────────────────
    L.append("")
    L.append(thick)
    L.append("  TODAY'S TRADE SCENARIOS")
    L.append(thick)

    now_uk = datetime.now(tz=UK_TZ)
    hour = now_uk.hour
    if hour < 7:
        session_note = "Asian session — low liquidity. Observe only. Levels form during EU/NY."
    elif hour < 10:
        session_note = "London open (07:00-10:00 BST) — watch PDH/PDL first, GEX walls second."
    elif hour < 13:
        session_note = "London mid-session. Quieter. NY open (14:30 BST) is the key catalyst."
    elif hour < 17:
        session_note = "NY open / overlap (14:30-17:00 BST) — HIGHEST probability for decisive moves."
    else:
        session_note = "NY afternoon. Look for closes above/below key levels for next-day bias."
    L.append(f"  {now_uk.strftime('%H:%M %Z')} — {session_note}")
    L.append("")

    for i, scenario in enumerate([plan.primary_scenario] + plan.alternative_scenarios, 1):
        name = scenario.get("name", f"Scenario {i}")
        label = "  PRIMARY" if i == 1 else f"  ALTERNATIVE {i-1}"
        L.append(f"{label} — {name}")
        L.append(f"  {thin}")
        trigger = scenario.get("trigger", "")
        if trigger:
            L.append(f"  Trigger:  {trigger}")
        why = scenario.get("why", "")
        if why:
            L.append(f"  Why:      {why}")
        entry = scenario.get("entry_zone", "")
        if entry:
            L.append(f"  Entry:    {entry}")
        stop = scenario.get("stop", "")
        if stop:
            L.append(f"  Stop:     {stop}")
        t1 = scenario.get("target_1", "")
        t2 = scenario.get("target_2", "")
        rr = scenario.get("rr", "")
        if t1:
            L.append(f"  Target 1: {t1}")
        if t2:
            L.append(f"  Target 2: {t2}")
        if rr:
            L.append(f"  R:R:      {rr}")
        note = scenario.get("note", "")
        if note:
            L.append(f"  Note:     {note}")

        # Weave macro into scenarios where relevant
        macro_notes = []
        if i == 1 and skew_bearish:
            macro_notes.append(
                f"IV Skew {skew_ratio:.2f} — institutions paying above-average for downside "
                f"protection. If this is a long scenario, recognise smart money is hedging against you."
            )
        if i == 2 and skew_bearish:
            macro_notes.append(
                f"IV Skew {skew_ratio:.2f} reinforces this scenario — the options market "
                f"is paying a large premium for downside protection, aligning with a rejection short."
            )
        if yield_10y is not None and yield_10y > 4.5 and "LONG" in name.upper():
            macro_notes.append(
                f"10Y yield at {yield_10y:.2f}% (above 4.5%) is a headwind for this long. "
                f"Reduce size by 25% and be quick to take profit at T1."
            )
        for mn in macro_notes:
            L.append(f"  [MACRO]: {mn}")

        L.append("")

    # ── 6. CHART INSTRUCTIONS ────────────────────────────────────────────
    L.append("CHART MARKING INSTRUCTIONS")
    L.append(thin)
    L.append("  Mark these on your CTrader chart before the session:")
    for i, instruction in enumerate(plan.chart_instructions, 1):
        L.append(f"  {i:>2}. {instruction}")

    # ── 7. CONFLUENCE + RISK ─────────────────────────────────────────────
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


def _append_level_block(
    L: list, price: float, level_type: str, spot: float, kl: dict,
    ss: Optional[dict], vix_val, yield_10y, skew_ratio, regime: str, opex: dict, thin: str
) -> None:
    """Append a level-centric narrative block for one key level."""
    rel = "ABOVE spot" if price > spot else "BELOW spot" if price < spot else "AT spot"
    at_spot = "  ◄ CURRENT PRICE" if abs(price - spot) / spot < 0.003 else f"  ({rel})"

    # Level type definitions
    type_labels = {
        "CALL_WALL":   "CALL WALL",
        "PUT_WALL":    "PUT WALL",
        "MAX_GEX":     "MAX GEX PIN",
        "MAX_PAIN":    "MAX PAIN",
        "ZERO_GEX":    "ZERO GEX LINE",
        "GEX_RES":     "GEX RESISTANCE",
        "GEX_SUP":     "GEX SUPPORT",
        "PDH":         "PRIOR DAY HIGH",
        "PDL":         "PRIOR DAY LOW",
        "WEEKLY_OPEN": "WEEKLY OPEN",
    }

    label = type_labels.get(level_type, level_type)
    L.append("")
    L.append(f"  ┌─ {price:,.0f} — {label}{at_spot}")

    # WHY DOES THIS LEVEL EXIST?
    if level_type == "CALL_WALL":
        L.append(f"  │  WHY: Highest concentration of call open interest above spot. Dealers who")
        L.append(f"  │  sold these calls must SELL futures as price approaches — creating a ceiling.")
        L.append(f"  │  If the call wall holds, that selling pressure keeps price capped here.")
        if ss and ss.get("today_open"):
            today_open = ss["today_open"]
            if today_open > price:
                L.append(f"  │  TODAY: Opened above ({today_open:,.0f}) then retreated below — dealers")
                L.append(f"  │  defended successfully. Second test is usually weaker.")
        if skew_ratio and skew_ratio > 1.10:
            L.append(f"  │  MACRO: IV skew {skew_ratio:.2f} — institutions are buying put protection,")
            L.append(f"  │  not call spreads. Suggests smart money is cautious about upside follow-through.")

        call_wall_above = round(price + 3, 0)
        call_wall_stop = round(price - 12, 0)
        max_gex_l = kl.get("max_gex_strike", price + 50)
        t1 = max_gex_l if max_gex_l and max_gex_l > price else round(price + 50, 0)
        res_above = [r for r in kl.get("gex_resistance_levels", []) if r > t1]
        t2 = res_above[0] if res_above else round(t1 + 50, 0)

        rej_entry = round(price * 0.9985, 0)
        rej_stop = round(price * 1.002, 0)
        max_pain_l = kl.get("max_pain", price * 0.99)
        gex_sups = [s for s in kl.get("gex_support_levels", []) if s < (max_pain_l or price)]
        rej_t1 = max_pain_l
        rej_t2 = gex_sups[0] if gex_sups else round((max_pain_l or price) - 30, 0)

        L.append(f"  │")
        L.append(f"  │  ── IF PRICE BREAKS AND CLOSES A 15-MIN CANDLE ABOVE {price:,.0f}:")
        L.append(f"  │     Entry:    {call_wall_above:,.0f}  (on confirmed close above)")
        L.append(f"  │     Stop:     {call_wall_stop:,.0f}  (back inside the wall = failed breakout)")
        L.append(f"  │     Target 1: {t1:,.0f}  (Max GEX pin — take 50% here)")
        L.append(f"  │     Target 2: {t2:,.0f}  (next resistance — trail remainder)")
        rr1 = round((t1 - call_wall_above) / (call_wall_above - call_wall_stop), 1) if call_wall_above > call_wall_stop else "N/A"
        rr2 = round((t2 - call_wall_above) / (call_wall_above - call_wall_stop), 1) if call_wall_above > call_wall_stop else "N/A"
        L.append(f"  │     R:R:      {rr1}:1 to T1  |  {rr2}:1 to T2")
        L.append(f"  │     Why: A close above forces dealers to BUY futures (re-hedging short calls).")
        L.append(f"  │     That buying pressure is self-reinforcing — breakouts here run fast.")
        if yield_10y and yield_10y > 4.5:
            L.append(f"  │     [MACRO]: Yields at {yield_10y:.2f}% (above 4.5%) — take T1 quickly,")
            L.append(f"  │     the yield headwind may limit how far the breakout runs.")

        L.append(f"  │")
        L.append(f"  │  ── IF PRICE IS REJECTED AT {price:,.0f} (spike up, closes back below):")
        L.append(f"  │     Entry:    {rej_entry:,.0f}  (on break below the rejection candle's low)")
        L.append(f"  │     Stop:     {rej_stop:,.0f}  (above the rejection spike)")
        L.append(f"  │     Target 1: {rej_t1:,.0f}  (Max Pain — take 60% here)")
        L.append(f"  │     Target 2: {rej_t2:,.0f}  (nearest GEX support — trail remainder)")
        rr_rej = round((rej_entry - (rej_t1 or rej_entry)) / (rej_stop - rej_entry), 1) if rej_stop > rej_entry and rej_t1 else "N/A"
        L.append(f"  │     R:R:      ~{rr_rej}:1 to T1")
        L.append(f"  │     Why: A failed breakout traps bulls. Their stops cluster just above {price:,.0f}.")
        L.append(f"  │     Dealers also stop buying futures — two forces pushing price lower.")
        if skew_ratio and skew_ratio > 1.10:
            L.append(f"  │     [MACRO]: IV skew {skew_ratio:.2f} reinforces this — options market is")
            L.append(f"  │     paying above-average for downside protection. Aligns with short.")

    elif level_type == "PUT_WALL":
        L.append(f"  │  WHY: Highest concentration of put open interest below spot. Dealers who")
        L.append(f"  │  sold these puts must BUY futures as price falls toward it — natural floor.")

        long_entry = round(price * 1.001, 0)
        long_stop = round(price * 0.998, 0)
        max_pain_l = kl.get("max_pain", price * 1.01)
        t1 = max_pain_l if max_pain_l and max_pain_l > price else round(price + (kl.get("call_wall", price * 1.03) - price) * 0.4, 0)
        max_gex_l = kl.get("max_gex_strike")
        t2 = max_gex_l if max_gex_l and max_gex_l > t1 else kl.get("call_wall", round(price * 1.03, 0))

        L.append(f"  │")
        L.append(f"  │  ── IF PRICE TESTS {price:,.0f} AND SHOWS BUYING (green candle close):")
        L.append(f"  │     Entry:    {long_entry:,.0f}  (on first green 15-min candle above the wall)")
        L.append(f"  │     Stop:     {long_stop:,.0f}  (below the put wall — dealer support removed)")
        L.append(f"  │     Target 1: {t1:,.0f}  (Max Pain — expiry magnet)")
        L.append(f"  │     Target 2: {t2:,.0f}  (Max GEX pin / call wall)")
        L.append(f"  │     Why: Dealer buying at the put wall acts as a cushion. In a TRENDING regime,")
        L.append(f"  │     this support can spark a sharp bounce as short-sellers cover.")

        L.append(f"  │")
        L.append(f"  │  ── IF PRICE CLOSES BELOW {price:,.0f} ON A 15-MIN CANDLE:")
        L.append(f"  │     Dealer support is removed. Moves accelerate lower.")
        gex_sups = [s for s in kl.get("gex_support_levels", []) if s < price]
        next_level = gex_sups[0] if gex_sups else round(price * 0.97, 0)
        L.append(f"  │     Next support: {next_level:,.0f} (next GEX support cluster)")
        L.append(f"  │     Short entry: {round(price - 3, 0):,.0f}  Stop: {round(price + 12, 0):,.0f}")
        if skew_ratio and skew_ratio > 1.10:
            L.append(f"  │     [MACRO]: IV skew {skew_ratio:.2f} — smart money hedged for this break.")
            L.append(f"  │     A put wall break with heavy put OI = aggressive move lower likely.")

    elif level_type == "MAX_GEX":
        L.append(f"  │  WHY: The strike where dealer delta hedging is most concentrated.")
        L.append(f"  │  Acts like a gravitational pin — price is repeatedly drawn back here.")
        L.append(f"  │  Think of it as a magnet: even if price moves away, it often returns.")
        L.append(f"  │")
        L.append(f"  │  USE: Primary profit target for directional trades. If price is trading")
        L.append(f"  │  near this level, expect choppy, mean-reverting action.")

    elif level_type == "MAX_PAIN":
        days_to_opex = opex.get("days_to_monthly_opex", 30) if opex else 30
        L.append(f"  │  WHY: The strike where option SELLERS (primarily dealers) lose the least money")
        L.append(f"  │  at expiry. The market drifts toward this level as expiry approaches.")
        strength = "STRONG" if isinstance(days_to_opex, int) and days_to_opex <= 5 else "moderate"
        L.append(f"  │  OPEX in {days_to_opex} days → {strength} gravitational pull to {price:,.0f}.")
        L.append(f"  │")
        L.append(f"  │  USE: Primary T1 for short trades; secondary T1 for longs from put wall.")
        L.append(f"  │  Near OPEX week, this level often acts as a 'end of day parking spot'.")

    elif level_type == "ZERO_GEX":
        L.append(f"  │  WHY: Where net GEX flips from positive (dealers buying) to negative")
        L.append(f"  │  (dealers selling). Crossing this removes the last brake pad.")
        L.append(f"  │")
        L.append(f"  │  ── IF PRICE CLOSES BELOW {price:,.0f}:")
        L.append(f"  │     Dealer behaviour shifts from dampening → amplifying drops.")
        gex_sups = [s for s in kl.get("gex_support_levels", []) if s < price]
        next_sup = gex_sups[0] if gex_sups else round(price * 0.97, 0)
        L.append(f"  │     Short entry: {round(price - 3, 0):,.0f}  Stop: {round(price + 12, 0):,.0f}")
        L.append(f"  │     Target:      {next_sup:,.0f} (next GEX support)")
        rr = round((round(price - 3, 0) - next_sup) / 15, 1)
        L.append(f"  │     R:R:         ~{rr}:1")

    elif level_type == "GEX_RES":
        L.append(f"  │  WHY: A GEX resistance cluster — multiple strikes with concentrated call OI.")
        L.append(f"  │  Dealers must sell futures here. Secondary resistance above the call wall.")
        L.append(f"  │  If a breakout through the call wall extends, this is where to take profits.")
        L.append(f"  │  USE: Partial T2 exit target for call wall breakout longs.")

    elif level_type == "GEX_SUP":
        L.append(f"  │  WHY: A GEX support cluster — concentrated put OI where dealers must buy.")
        L.append(f"  │  Secondary support below the put wall. In a trending down move,")
        L.append(f"  │  this is where to expect a temporary bounce or profit-take level.")
        L.append(f"  │  USE: T1 or T2 exit target for put wall breakdown shorts.")

    elif level_type == "PDH":
        L.append(f"  │  WHY: Yesterday's high — institutions had sell orders here.")
        L.append(f"  │  A break and CLOSE above PDH signals new buyers stepping in (bullish).")
        call_wall_l = kl.get("call_wall")
        if call_wall_l and abs(price - call_wall_l) / call_wall_l < 0.005:
            L.append(f"  │  ★ PDH aligns with Call Wall ({call_wall_l:,.0f}) — DOUBLE RESISTANCE.")
            L.append(f"  │    Two independent forces at the same level. Extremely hard to break.")
        L.append(f"  │  USE: Long above PDH close with stop below it. Target next GEX resistance.")

    elif level_type == "PDL":
        L.append(f"  │  WHY: Yesterday's low — institutions had buy orders here.")
        L.append(f"  │  A break and CLOSE below PDL signals sellers taking control (bearish).")
        put_wall_l = kl.get("put_wall")
        if put_wall_l and abs(price - put_wall_l) / put_wall_l < 0.005:
            L.append(f"  │  ★ PDL aligns with Put Wall ({put_wall_l:,.0f}) — DOUBLE SUPPORT.")
            L.append(f"  │    Expect a very strong bounce here. High-probability long setup.")
        L.append(f"  │  USE: Short below PDL close with stop above it. Target Max Pain next.")

    elif level_type == "WEEKLY_OPEN":
        L.append(f"  │  WHY: The price at Monday's open — a macro reference for the whole week.")
        if price < spot:
            L.append(f"  │  Current spot is ABOVE weekly open → week is bullish so far.")
        else:
            L.append(f"  │  Current spot is BELOW weekly open → week is bearish so far.")
        L.append(f"  │  USE: Directional context only — not a trading level by itself.")

    L.append(f"  └{'─' * 65}")


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _identify_confluence_scenario(
    plan, spot: float, call_wall, put_wall, zero_gex,
    vp: dict, vp_bucket: float, skew_ratio
) -> tuple[str, list[str], str]:
    """
    Match today's data to one of four standard confluence scenarios.
    Returns (scenario_id, matched_signals_list, tactical_note).
    """
    regime = plan.gex_regime
    gex_val = plan.gex_value
    pcr = plan.key_levels.get("pcr", 1.0)
    cta_bias = (plan.cta_data or {}).get("bias", "NEUTRAL")
    vp_hvn = vp.get("hvn_levels", [])
    vp_lvn = vp.get("lvn_levels", [])

    dist_to_call = (call_wall - spot) / spot if call_wall else 1.0
    call_at_hvn = call_wall and any(abs(call_wall - h) < vp_bucket * 2 for h in vp_hvn)
    near_lvn = any(abs(spot - l) < vp_bucket * 2 for l in vp_lvn)
    skew_elevated = skew_ratio is not None and skew_ratio > 1.10

    # Scenario B: Directional Acceleration
    if regime == "TRENDING" and abs(dist_to_call) < 0.008 and skew_elevated:
        signals = [
            f"Negative GEX (${gex_val:.0f}B) — dealers short gamma",
            f"IV Skew {skew_ratio:.2f} — elevated put premium (smart money hedged)",
            f"Spot {spot:,.0f} pressing Call Wall {call_wall:,.0f} ({dist_to_call*100:.1f}% away)",
        ]
        if cta_bias in ("LONG", "MILD_LONG"):
            signals.append(f"CTA positioning: {cta_bias} — systematic tailwind for longs")
        if call_at_hvn:
            signals.append(f"Call Wall at HVN — thick volume confirms resistance strength")
        return ("B", signals,
                f"This is a DIRECTIONAL ACCELERATION setup. The {call_wall:,.0f} Call Wall is "
                f"the trigger. A confirmed break above sends dealers buying → breakout accelerates. "
                f"A rejection sends dealers selling → drop accelerates. Trade the direction, not the range.")

    # Scenario A: Mean Reversion
    if regime == "PINNED":
        signals = [f"Positive GEX (+${gex_val:.0f}B) — dealers long gamma, dampening moves"]
        if call_at_hvn:
            signals.append(f"Call Wall at HVN — thick volume confirms ceiling")
        signals.append("PINNED regime → statistically favours mean-reversion trades")
        return ("A", signals,
                "Fade moves to the walls. Short into the Call Wall, long into the Put Wall. "
                "Target Max Pain in the middle. Avoid chasing breakouts — they snap back.")

    # Scenario C: Fast-Through LVN
    if near_lvn:
        near = [l for l in vp_lvn if abs(l - spot) < vp_bucket * 2]
        signals = [
            f"Spot near LVN at {near[0]:,.0f} — thin volume zone" if near else "Spot in thin volume zone",
            "Low volume = few resting orders = fast directional move through here",
        ]
        return ("C", signals,
                "Price is in (or approaching) a low-volume zone. Do not take profits early. "
                "Set wider targets — LVN zones are where price travels fast. "
                "Wait for the next HVN or GEX wall before exiting.")

    # Scenario D: Structural Accumulation
    pcr_val = 0
    try:
        pcr_val = plan.key_levels.get("_pcr", 0) or 0
    except Exception:
        pass
    if regime == "TRENDING" and cta_bias == "SHORT":
        signals = [
            f"Negative GEX (${gex_val:.0f}B) with CTA SHORT trigger",
            "Systematic selling aligns with dealer amplification — double pressure downward",
        ]
        return ("D", signals,
                "CTA selling + negative GEX = strongest downside setup. "
                "If price breaks below Zero GEX, the move can be sharp and sustained. "
                "Do not fight this combination — wait for a GEX support level to long.")

    # Default fallback → B (trending at a level)
    signals = [
        f"Negative GEX (${gex_val:.0f}B) — dealer flows amplify moves",
        f"Price near key level — waiting for directional trigger",
    ]
    return ("B", signals,
            "Watch for a confirmed candle close above/below a key level. Trade WITH the break.")


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
