"""
Trade plan generator.
Combines GEX, OI, macro data and produces a structured session briefing
with primary scenario, alternatives, pivot rules, and chart-marking instructions.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradePlan:
    instrument: str
    session_date: str
    spot_price: float
    gex_regime: str
    primary_bias: str               # "LONG" / "SHORT" / "NEUTRAL"
    primary_scenario: dict
    alternative_scenarios: list[dict]
    key_levels: dict
    chart_instructions: list[str]
    risk_notes: list[str]
    confluence_score: int           # 0–10


def generate_trade_plan(
    instrument: str,
    spot_price: float,
    gex_result,
    oi_result,
    macro: dict,
    session: str = "LONDON_NY",
) -> TradePlan:
    """
    Generate a full trade plan from GEX, OI and macro data.
    """
    # --- Determine primary bias ---
    bias, bias_reason = _determine_bias(gex_result, oi_result, macro)

    # --- Key levels ---
    key_levels = _build_key_levels(gex_result, oi_result, spot_price)

    # --- Primary scenario ---
    primary = _build_primary_scenario(bias, spot_price, key_levels, gex_result, oi_result)

    # --- Alternative scenarios ---
    alternatives = _build_alternatives(bias, spot_price, key_levels, gex_result, oi_result)

    # --- Chart marking instructions ---
    chart_instructions = _build_chart_instructions(key_levels, gex_result, oi_result, spot_price)

    # --- Risk notes ---
    risk_notes = _build_risk_notes(gex_result, oi_result, macro)

    # --- Confluence score ---
    confluence = _score_confluence(gex_result, oi_result, macro, bias)

    return TradePlan(
        instrument=instrument,
        session_date=datetime.now().strftime("%Y-%m-%d"),
        spot_price=spot_price,
        gex_regime=gex_result.regime,
        primary_bias=bias,
        primary_scenario=primary,
        alternative_scenarios=alternatives,
        key_levels=key_levels,
        chart_instructions=chart_instructions,
        risk_notes=risk_notes,
        confluence_score=confluence,
    )


def format_trade_plan(plan: TradePlan) -> str:
    """Format TradePlan as a readable text report."""
    lines = []

    lines.append("=" * 70)
    lines.append(f"  GEX & OI TRADE PLAN — {plan.instrument}")
    lines.append(f"  {plan.session_date}  |  Spot: {plan.spot_price:,.2f}")
    lines.append("=" * 70)

    # Regime and bias
    lines.append("")
    lines.append(f"GEX REGIME:     {plan.gex_regime}")
    lines.append(f"PRIMARY BIAS:   {plan.primary_bias}")
    lines.append(f"CONFLUENCE:     {'★' * plan.confluence_score}{'☆' * (10 - plan.confluence_score)} ({plan.confluence_score}/10)")

    # Key levels
    lines.append("")
    lines.append("─" * 70)
    lines.append("  KEY LEVELS")
    lines.append("─" * 70)
    for name, level in plan.key_levels.items():
        if isinstance(level, float):
            lines.append(f"  {name:<25} {level:>10,.2f}")
        elif isinstance(level, list):
            for i, lvl in enumerate(level[:3]):
                label = name if i == 0 else ""
                lines.append(f"  {label:<25} {lvl:>10,.2f}")

    # Primary scenario
    lines.append("")
    lines.append("─" * 70)
    lines.append("  PRIMARY SCENARIO")
    lines.append("─" * 70)
    p = plan.primary_scenario
    lines.append(f"  Direction:    {p.get('direction', 'N/A')}")
    lines.append(f"  Trigger:      {p.get('trigger', 'N/A')}")
    lines.append(f"  Entry zone:   {p.get('entry_zone', 'N/A')}")
    lines.append(f"  Stop:         {p.get('stop', 'N/A')}")
    lines.append(f"  Target 1:     {p.get('target_1', 'N/A')}")
    lines.append(f"  Target 2:     {p.get('target_2', 'N/A')}")
    lines.append(f"  Est R:R:      {p.get('rr', 'N/A')}")
    lines.append(f"  Rationale:    {p.get('rationale', '')}")

    # Alternative scenarios
    for i, alt in enumerate(plan.alternative_scenarios, 1):
        lines.append("")
        lines.append(f"  SCENARIO {chr(64 + i + 1)} — {alt.get('name', 'Alternative')}")
        lines.append(f"  Trigger:      {alt.get('trigger', '')}")
        lines.append(f"  Action:       {alt.get('action', '')}")
        lines.append(f"  Pivot:        {alt.get('pivot', '')}")

    # Chart instructions
    lines.append("")
    lines.append("─" * 70)
    lines.append("  CHART MARKING INSTRUCTIONS")
    lines.append("─" * 70)
    for i, instruction in enumerate(plan.chart_instructions, 1):
        lines.append(f"  {i}. {instruction}")

    # Risk notes
    lines.append("")
    lines.append("─" * 70)
    lines.append("  RISK & AWARENESS NOTES")
    lines.append("─" * 70)
    for note in plan.risk_notes:
        lines.append(f"  ⚠  {note}")

    lines.append("")
    lines.append("=" * 70)

    return "\n".join(lines)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _determine_bias(gex_result, oi_result, macro: dict) -> tuple[str, str]:
    """Derive primary directional bias from combined signals."""
    score = 0  # positive = bullish, negative = bearish

    # GEX regime
    if gex_result.total_gex > 0.5:
        score += 0  # Pinned = no strong directional edge from GEX
    elif gex_result.total_gex < -0.5:
        score += 0  # Trending = follow momentum, read structure

    # P/C ratio
    pcr = oi_result.put_call_ratio
    if pcr > 1.3:
        score -= 1  # Heavy put buying = bearish
    elif pcr > 1.0:
        score -= 0.5
    elif pcr < 0.7:
        score += 1  # Heavy call buying = bullish
    elif pcr < 0.9:
        score += 0.5

    # VIX regime
    vix = macro.get("vix", 20)
    if isinstance(vix, (int, float)):
        if vix < 15:
            score += 0.5  # Low vol = mild bullish
        elif vix > 25:
            score -= 1    # Elevated vol = risk-off

    # Yield context
    yield_10y = macro.get("yield_10y")
    if isinstance(yield_10y, float):
        if yield_10y > 4.5:
            score -= 0.5  # High yields = headwind for risk assets

    # Max pain proximity
    mp = oi_result.max_pain
    spot = gex_result.spot_price
    if spot > mp * 1.01:
        score -= 0.5  # Above max pain = gravitational pull down
    elif spot < mp * 0.99:
        score += 0.5  # Below max pain = gravitational pull up

    if score > 0.5:
        return "LONG", f"Bullish bias score: {score:.1f}"
    elif score < -0.5:
        return "SHORT", f"Bearish bias score: {score:.1f}"
    else:
        return "NEUTRAL", f"Balanced score: {score:.1f} — wait for structure"


def _build_key_levels(gex_result, oi_result, spot: float) -> dict:
    return {
        "Current Spot": spot,
        "Call Wall (resistance)": gex_result.call_wall,
        "Put Wall (support)": gex_result.put_wall,
        "Max GEX Strike (pin)": gex_result.max_gex_strike,
        "Max Pain": oi_result.max_pain,
        "GEX Support Levels": gex_result.support_levels,
        "GEX Resistance Levels": gex_result.resistance_levels,
        "Zero GEX Crossover": gex_result.zero_gex_strike,
    }


def _build_primary_scenario(bias: str, spot: float, levels: dict, gex_result, oi_result) -> dict:
    support = levels.get("Put Wall (support)", spot * 0.97)
    resistance = levels.get("Call Wall (resistance)", spot * 1.03)
    pin = levels.get("Max GEX Strike (pin)", spot)
    max_pain = levels.get("Max Pain", spot)

    if bias == "LONG":
        entry = (spot + support) / 2
        stop = support * 0.998
        t1 = pin if pin > spot else resistance
        t2 = resistance
        rr = round((t1 - entry) / (entry - stop), 1) if entry > stop else "N/A"
        return {
            "direction": "LONG",
            "trigger": f"Price holds above put wall ({support:,.0f}) with order flow confirmation",
            "entry_zone": f"{support:,.0f} – {spot:,.0f}",
            "stop": f"{stop:,.0f} (below put wall)",
            "target_1": f"{t1:,.0f} (max GEX / pin level)",
            "target_2": f"{t2:,.0f} (call wall)",
            "rr": f"~{rr}:1",
            "rationale": f"GEX regime is {gex_result.regime}. Put wall at {support:,.0f} provides dealer-backed support. Max pain at {max_pain:,.0f}.",
        }
    elif bias == "SHORT":
        entry = (spot + resistance) / 2
        stop = resistance * 1.002
        t1 = pin if pin < spot else support
        t2 = support
        rr = round((entry - t1) / (stop - entry), 1) if stop > entry else "N/A"
        return {
            "direction": "SHORT",
            "trigger": f"Price fails at call wall ({resistance:,.0f}) with rejection confirmation",
            "entry_zone": f"{spot:,.0f} – {resistance:,.0f}",
            "stop": f"{stop:,.0f} (above call wall)",
            "target_1": f"{t1:,.0f} (max GEX / pin level)",
            "target_2": f"{t2:,.0f} (put wall)",
            "rr": f"~{rr}:1",
            "rationale": f"GEX regime is {gex_result.regime}. Call wall at {resistance:,.0f} provides dealer-backed resistance. Max pain at {max_pain:,.0f}.",
        }
    else:
        return {
            "direction": "RANGE TRADE",
            "trigger": "Price reaches either put wall or call wall extreme",
            "entry_zone": f"Longs near {support:,.0f}, Shorts near {resistance:,.0f}",
            "stop": "Below put wall / above call wall",
            "target_1": f"Midpoint: {(support + resistance) / 2:,.0f}",
            "target_2": f"Opposite wall",
            "rr": "~2:1",
            "rationale": f"GEX ${gex_result.total_gex:.1f}B ({gex_result.regime}). Spot between put wall ({support:,.0f}) and call wall ({resistance:,.0f}) — wait for a break of either level to initiate.",
        }


def _build_alternatives(bias: str, spot: float, levels: dict, gex_result, oi_result) -> list[dict]:
    support = levels.get("Put Wall (support)", spot * 0.97)
    resistance = levels.get("Call Wall (resistance)", spot * 1.03)
    zero_gex = levels.get("Zero GEX Crossover", spot * 1.02)

    return [
        {
            "name": "Breakout above Call Wall",
            "trigger": f"Price closes decisively above {resistance:,.0f} with volume",
            "action": "Long breakout — target next GEX resistance level",
            "pivot": f"If price fails back below {resistance:,.0f} within 1 candle, trap reversal short",
        },
        {
            "name": "Break below Put Wall",
            "trigger": f"Price closes below {support:,.0f} — negative GEX activation",
            "action": "Sell breakdown — dealers now amplify the move lower",
            "pivot": f"If {gex_result.zero_gex_strike:,.0f} (zero GEX) breached, expect accelerated move",
        },
        {
            "name": "Consolidation / No Setup",
            "trigger": "Price oscillates between walls without clear commitment",
            "action": "Stand aside — wait for session open momentum",
            "pivot": "Re-evaluate at London open or NY open with refreshed data",
        },
    ]


def _build_chart_instructions(levels: dict, gex_result, oi_result, spot: float) -> list[str]:
    instructions = [
        f"Draw a BLUE horizontal zone at {gex_result.put_wall:,.0f} — PUT WALL (key support, dealer buying)",
        f"Draw an ORANGE horizontal zone at {gex_result.call_wall:,.0f} — CALL WALL (key resistance, dealer selling)",
        f"Draw a YELLOW dashed line at {oi_result.max_pain:,.0f} — MAX PAIN (expiry magnet)",
        f"Draw a WHITE dashed line at {gex_result.max_gex_strike:,.0f} — MAX GEX STRIKE (gravitational pin)",
        f"Draw a RED dotted line at {gex_result.zero_gex_strike:,.0f} — ZERO GEX CROSSOVER (volatility trigger)",
    ]

    for i, lvl in enumerate(gex_result.support_levels[:3], 1):
        instructions.append(f"Mark BLUE support at {lvl:,.0f} — GEX Support Level {i}")
    for i, lvl in enumerate(gex_result.resistance_levels[:3], 1):
        instructions.append(f"Mark ORANGE resistance at {lvl:,.0f} — GEX Resistance Level {i}")

    for item in oi_result.top_put_strikes[:2]:
        instructions.append(f"Mark LIGHT BLUE zone at {item['strike']:,.0f} — High OI Put ({item['oi']:,} contracts)")
    for item in oi_result.top_call_strikes[:2]:
        instructions.append(f"Mark LIGHT ORANGE zone at {item['strike']:,.0f} — High OI Call ({item['oi']:,} contracts)")

    return instructions


def _build_risk_notes(gex_result, oi_result, macro: dict) -> list[str]:
    notes = []
    vix = macro.get("vix", 20)

    if isinstance(vix, (int, float)) and vix > 25:
        notes.append(f"VIX at {vix:.1f} — elevated volatility. Reduce position size by 30–50%.")
    if gex_result.total_gex < -1.0:
        notes.append("Strongly negative GEX: dealers amplifying moves. Do NOT fade moves — trade breakouts only.")
    if oi_result.put_call_ratio > 1.5:
        notes.append("Very high P/C ratio: market is over-hedged. Watch for short squeeze if support holds.")
    if oi_result.put_call_ratio < 0.6:
        notes.append("Very low P/C ratio: complacency warning. Limited downside protection in the market.")

    notes.append("Always check economic calendar before entry — stand aside 15 min before/after major releases.")
    notes.append("GEX levels are most reliable within 7 days of options expiry (monthly/weekly OPEX).")
    notes.append("Pepperstone spread: account for ~0.4 pt spread on US500, ~1 pt on UK100/Ger40.")

    return notes


def _score_confluence(gex_result, oi_result, macro: dict, bias: str) -> int:
    score = 5  # baseline

    # GEX clarity
    if abs(gex_result.total_gex) > 1.0:
        score += 1  # Clear regime
    if gex_result.put_wall and gex_result.call_wall:
        score += 1  # Clear walls

    # OI conviction
    pcr = oi_result.put_call_ratio
    if pcr > 1.2 or pcr < 0.8:
        score += 1  # Directional lean

    # Macro alignment
    vix = macro.get("vix", 20)
    if isinstance(vix, (int, float)):
        if vix < 15 and bias == "LONG":
            score += 1
        elif vix > 25 and bias == "SHORT":
            score += 1

    # Max pain proximity
    mp = oi_result.max_pain
    spot = gex_result.spot_price
    if abs(spot - mp) / spot < 0.01:
        score += 1  # Near max pain = strong expiry influence

    return min(10, max(0, score))
