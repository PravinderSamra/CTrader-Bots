"""
Pre-Session Report Generator

Formats the full market scan output in a readable, actionable format.
Includes FTMO risk context (account size, daily loss tracker, position sizing).
"""

from datetime import datetime, timezone
from typing import Optional
from data.models import MarketContext, FVGResult, OrderBlock, LiquidityPool, COTData
from analysis.sessions import (
    current_session, active_kill_zone, session_display_label, session_bias_note
)
from config.settings import (
    FTMO_ACCOUNT_SIZE, FTMO_RISK_PER_TRADE, FTMO_DAILY_LOSS_LIMIT,
    FTMO_TOTAL_LOSS_LIMIT, FTMO_PROFIT_TARGET_P1, AGENT_VERSION,
    SKIP_GRADES, MAX_FVG_DISPLAY, MAX_OB_DISPLAY, MAX_LIQ_DISPLAY,
    PIP_VALUE_PER_LOT,
)

_GRADE_ORDER = {"A+": 0, "A": 1, "B": 2, "C": 3, "SKIP": 4}
_WIDTH = 65
_SEP   = "═" * _WIDTH
_DIV   = "─" * _WIDTH
_DOT   = "·" * _WIDTH


def _grade_symbol(grade: str) -> str:
    return {"A+": "★ A+", "A": "▲ A", "B": "● B", "C": "○ C"}.get(grade, grade)


def _pct_str(val: float, current: float) -> str:
    pct = (val - current) / current * 100
    sign = "+" if pct >= 0 else ""
    direction = "ABOVE" if pct >= 0 else "BELOW"
    return f"({sign}{pct:.2f}%, {direction})"


def _position_size_hint(symbol: str, stop_pts: float) -> str:
    """Calculate suggested lot size for $450 risk at the given stop."""
    pip_val = PIP_VALUE_PER_LOT.get(symbol)
    if not pip_val or stop_pts <= 0:
        return ""
    lots = FTMO_RISK_PER_TRADE / (stop_pts * pip_val)
    return f"  → ${FTMO_RISK_PER_TRADE} risk @ {stop_pts:.1f}pt stop = {lots:.2f} lots"


def _cot_section(cot: Optional[COTData]) -> list[str]:
    if not cot:
        return ["  COT data unavailable (API timeout or no recent data)"]
    lines = []
    arrow = "▲" if cot.bias == "BULLISH" else ("▼" if cot.bias == "BEARISH" else "─")
    lines.append(
        f"  {arrow} {cot.bias}  |  Net {cot.net_contracts:+,} contracts"
        f"  ({cot.pct_of_oi:+.1f}% of OI)  |  Report: {cot.report_date}"
    )
    change_word = "Adding longs" if cot.weekly_change > 0 else "Adding shorts"
    if abs(cot.weekly_change) < 500:
        change_word = "Minimal change"
    lines.append(f"  {change_word} this week ({cot.weekly_change:+,} net change)")
    lines.append(f"  8-week position rank: {cot.rank_8wk}th percentile")

    if cot.rank_8wk >= 90:
        lines.append(f"  ⚠  CROWDED LONG — positioning at extreme, contrarian reversal risk")
    elif cot.rank_8wk <= 10:
        lines.append(f"  ⚠  CROWDED SHORT — positioning at extreme, contrarian squeeze risk")

    history_str = " | ".join(f"{d[:5]}:{n:+,}" for d, n in cot.history[:4])
    lines.append(f"  4-week history: {history_str}")
    return lines


def _fvg_lines(fvgs: list[FVGResult], current_price: float, symbol: str) -> list[str]:
    displayable = [f for f in fvgs if f.probability_grade not in SKIP_GRADES]
    displayable.sort(key=lambda f: (_GRADE_ORDER.get(f.probability_grade, 9), f.candles_ago))
    displayable = displayable[:MAX_FVG_DISPLAY]

    if not displayable:
        return ["  No high-probability FVGs detected."]

    lines = []
    for fvg in displayable:
        direction = "Bullish" if fvg.direction == "BULL" else "Bearish"
        pct_from  = (fvg.gap_high - current_price) / current_price * 100 if fvg.direction == "BEAR" else (fvg.gap_low - current_price) / current_price * 100
        pos_str   = f"({pct_from:+.2f}%, {'ABOVE' if pct_from >= 0 else 'BELOW'})"
        ctx_str   = "  [" + ", ".join(fvg.context_flags) + "]" if fvg.context_flags else ""
        fill_str  = f"  {fvg.partial_fill_pct:.0f}% filled" if fvg.touch_count > 0 else "  virgin"
        touched   = f"  {fvg.touch_count}x tested" if fvg.touch_count > 0 else "  untouched"
        at_level  = " ← PRICE AT LEVEL" if abs(pct_from) < 0.20 else ""

        line = (
            f"  [{direction} FVG | {fvg.timeframe}] "
            f"{fvg.gap_low:.5f} → {fvg.gap_high:.5f}  "
            f"{pos_str}  "
            f"{_grade_symbol(fvg.probability_grade)}  "
            f"{fvg.age_label}({fvg.candles_ago}c)"
            f"{fill_str}{touched}{ctx_str}{at_level}"
        )
        lines.append(line)

        # Add position size hint if FVG is close to price and actionable
        if abs(pct_from) < 1.0 and fvg.probability_grade in ("A+", "A", "B"):
            stop_distance = abs(fvg.gap_high - fvg.gap_low) * 1.5
            hint = _position_size_hint(symbol, stop_distance)
            if hint:
                lines.append(hint)

    return lines


def _ob_lines(obs: list[OrderBlock], current_price: float) -> list[str]:
    if not obs:
        return []
    lines = []
    for ob in obs[:MAX_OB_DISPLAY]:
        direction = "BULL OB" if ob.direction == "BULL" else "BEAR OB"
        pct = (ob.mid - current_price) / current_price * 100
        pos = f"({'above' if pct >= 0 else 'below'} current, {pct:+.2f}%)"
        liq = "  ← Preceded by liquidity grab" if ob.preceded_by_liq_grab else ""
        lines.append(
            f"  [{direction} | {ob.timeframe}] "
            f"{ob.ob_low:.5f}–{ob.ob_high:.5f}  {pos}  Q:{ob.quality}/5{liq}"
        )
    return lines


def _liq_lines(pools: list[LiquidityPool], current_price: float) -> list[str]:
    if not pools:
        return []
    bsl = [p for p in pools if p.direction == "BSL"][:MAX_LIQ_DISPLAY // 2 + 1]
    ssl = [p for p in pools if p.direction == "SSL"][:MAX_LIQ_DISPLAY // 2 + 1]
    lines = []
    for p in sorted(bsl, key=lambda x: x.price):
        pct = (p.price - current_price) / current_price * 100
        lines.append(f"  BSL above: {p.price:.5f}  ({pct:+.2f}%)  [{p.test_count}× tested, {p.strength} strength]")
    for p in sorted(ssl, key=lambda x: x.price, reverse=True):
        pct = (p.price - current_price) / current_price * 100
        lines.append(f"  SSL below: {p.price:.5f}  ({pct:+.2f}%)  [{p.test_count}× tested, {p.strength} strength]")
    return lines


def generate_report(markets: list[MarketContext]) -> str:
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    kz = active_kill_zone()
    sess = session_display_label()

    lines = [
        "",
        _SEP,
        f"  ICT/SMC ORDER FLOW REPORT — {AGENT_VERSION.upper()} AGENT",
        f"  Generated : {now_str}",
        f"  Session   : {sess}",
        f"  Kill Zone : {kz or 'None active'}",
        _SEP,
        "",
        "  FTMO SWING CHALLENGE — RISK PARAMETERS",
        _DIV,
        f"  Account      : ${FTMO_ACCOUNT_SIZE:,}",
        f"  Risk/trade   : ${FTMO_RISK_PER_TRADE}  ({FTMO_RISK_PER_TRADE/FTMO_ACCOUNT_SIZE*100:.3f}% per trade)",
        f"  Daily limit  : ${FTMO_DAILY_LOSS_LIMIT:,.0f}  (5% — hard stop for the day if hit)",
        f"  Total limit  : ${FTMO_TOTAL_LOSS_LIMIT:,.0f}  (10% — account terminated)",
        f"  P1 target    : ${FTMO_PROFIT_TARGET_P1:,.0f}  (10% — Phase 1 goal)",
        f"  Strategy     : Day trading via Swing account (news & weekend hold allowed)",
        "",
        "  DATA QUALITY KEY",
        _DIV,
        "  Tier 1: Exchange taker buy/sell volume (crypto — OKX).",
        "  Tier 2: OHLCV structural analysis only. Confirm order flow manually",
        "          on Bookmap / Sierra Chart / ATAS before entering.",
        "  Tier 3: CFTC COT — weekly macro positioning (~3-day lag).",
        _SEP,
    ]

    for ctx in markets:
        price = ctx.current_price
        lines += [
            "",
            _SEP,
            f"  {ctx.symbol}  |  Current: {price:.5f}",
            _DIV,
        ]

        # Trend
        lines += [
            "  MARKET STRUCTURE",
            f"  Higher-TF trend : {ctx.higher_tf_trend}",
            f"  Intraday trend  : {ctx.intraday_trend}",
        ]

        # Premium / Discount
        lines += [
            "",
            "  PREMIUM / DISCOUNT",
            f"  Range: {ctx.range_low:.5f} – {ctx.range_high:.5f}",
            f"  Equilibrium: {ctx.equilibrium:.5f}",
            f"  {ctx.premium_discount_status}",
            f"  OTE zone: {ctx.ote_low:.5f} – {ctx.ote_high:.5f}",
        ]

        # Session Levels
        lines += [
            "",
            "  SESSION LEVELS",
            f"  Prior day high : {ctx.prior_day_high:.5f}  ← BSL target",
            f"  Prior day low  : {ctx.prior_day_low:.5f}  ← SSL target",
        ]
        if ctx.asian_high is not None:
            lines.append(f"  Asian high     : {ctx.asian_high:.5f}")
        if ctx.asian_low is not None:
            lines.append(f"  Asian low      : {ctx.asian_low:.5f}")
        if ctx.midnight_open is not None:
            mid_open = ctx.midnight_open
            disc = "DISCOUNT — favour LONGS" if price < mid_open else "PREMIUM — favour SHORTS"
            lines.append(f"  Midnight open  : {mid_open:.5f}  [{disc}]")

        # Session bias notes
        bias_notes = session_bias_note(ctx.asian_swept, ctx.midnight_open, price)
        if bias_notes:
            lines.append("")
            for note in bias_notes:
                lines.append(f"  {note}")

        # Volume Profile
        if ctx.poc:
            lines += [
                "",
                "  VOLUME PROFILE (OHLCV approximation — not tick-level)",
                f"  POC : {ctx.poc:.5f}  ← magnetic level",
                f"  VAH : {ctx.vah:.5f}  ← resistance / target" if ctx.vah else "",
                f"  VAL : {ctx.val:.5f}  ← support / target" if ctx.val else "",
            ]
            if ctx.lvns:
                lines.append(f"  LVNs: {', '.join(f'{v:.5f}' for v in ctx.lvns[:5])}")

        # Order Blocks
        ob_lines = _ob_lines(ctx.order_blocks, price)
        if ob_lines:
            lines += ["", "  ACTIVE ORDER BLOCKS (unmitigated)"] + ob_lines

        # FVGs
        lines += ["", "  FAIR VALUE GAPS (SKIP-grade filtered)"]
        lines += _fvg_lines(ctx.fvgs, price, ctx.symbol)

        # Liquidity
        liq = _liq_lines(ctx.liquidity_pools, price)
        if liq:
            lines += ["", "  LIQUIDITY POOLS (unswept)"] + liq

        # COT
        if ctx.cot:
            lines += ["", "  SMART MONEY POSITIONING — CFTC COT (Tier 3 / weekly)"]
            lines += _cot_section(ctx.cot)

        lines.append(_DOT)

    lines += ["", _SEP, "  END OF REPORT", _SEP, ""]
    return "\n".join(l for l in lines)
