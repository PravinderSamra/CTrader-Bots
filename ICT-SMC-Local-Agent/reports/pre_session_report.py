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
    PIP_VALUE_PER_LOT, INSTRUMENTS,
)

_GRADE_ORDER = {"A+": 0, "A": 1, "B": 2, "C": 3, "SKIP": 4}
_WIDTH = 65
_SEP   = "═" * _WIDTH
_DIV   = "─" * _WIDTH
_DOT   = "·" * _WIDTH

# Price units per pip for each instrument (used to convert raw gap to pips)
_PIP_SIZE: dict[str, float] = {
    "EURUSD": 0.0001, "GBPUSD": 0.0001,
    "USDJPY": 0.01,   "GBPJPY": 0.01,
    "SPX": 1.0, "NDX": 1.0, "DAX": 1.0, "US30": 1.0, "UK100": 1.0,
    "GOLD": 1.0,    # $1 per pip; PIP_VALUE_PER_LOT["GOLD"]=10 means $10 per $1 move per lot
    "OIL": 0.01,
    "BTCUSDT": 1.0, "ETHUSDT": 1.0, "SOLUSDT": 0.1,
}

# Minimum stop in pips to prevent nonsensical lot sizes from tiny FVG gaps
_MIN_STOP_PIPS: dict[str, float] = {
    "EURUSD": 15, "GBPUSD": 15, "USDJPY": 15, "GBPJPY": 20,
    "SPX": 8, "NDX": 12, "DAX": 10, "US30": 30, "UK100": 20,
    "GOLD": 5,   # $5 minimum stop for gold
    "OIL": 30,
    "BTCUSDT": 200, "ETHUSDT": 20, "SOLUSDT": 2,
}

# Build data source labels from INSTRUMENTS config once at import time
_DATA_SOURCE_LABEL: dict[str, tuple[str, str]] = {}
_SOURCE_DISPLAY = {"twelve_data": "Twelve Data", "yahoo": "Yahoo Finance", "okx": "OKX"}
_SOURCE_WARN: dict[str, str] = {
    "yahoo": "⚠  Yahoo Finance (market-hours only). Verify levels on Pepperstone chart before trading.",
    "okx":   "ℹ  OKX spot feed. Pepperstone crypto levels typically match closely.",
    "twelve_data": "ℹ  Twelve Data spot. Levels should be close to Pepperstone (<1-2 pip variance).",
}
for _inst in INSTRUMENTS:
    _name = _inst["name"]
    _src  = _inst["source"]
    _fb   = _inst.get("fallback_source")
    _label = _SOURCE_DISPLAY.get(_src, _src)
    if _fb:
        _label += f" → {_SOURCE_DISPLAY.get(_fb, _fb)} fallback"
    _DATA_SOURCE_LABEL[_name] = (_SOURCE_WARN.get(_src, f"Source: {_label}"), _label)


def _grade_symbol(grade: str) -> str:
    return {"A+": "★ A+", "A": "▲ A", "B": "● B", "C": "○ C"}.get(grade, grade)


def _pct_str(val: float, current: float) -> str:
    pct = (val - current) / current * 100
    sign = "+" if pct >= 0 else ""
    direction = "ABOVE" if pct >= 0 else "BELOW"
    return f"({sign}{pct:.2f}%, {direction})"


def _position_size_hint(symbol: str, gap_price_units: float) -> str:
    """Calculate suggested lot size for $450 risk.

    Converts the FVG gap (raw price units) to pips, applies 1.5× for stop clearance,
    enforces a per-instrument minimum stop so forex micro-gaps don't produce absurd
    lot counts, then calculates position size.
    """
    pip_val  = PIP_VALUE_PER_LOT.get(symbol)
    pip_size = _PIP_SIZE.get(symbol)
    if not pip_val or not pip_size:
        return ""
    gap_pips  = (gap_price_units / pip_size) * 1.5
    min_stop  = _MIN_STOP_PIPS.get(symbol, 15)
    stop_pips = max(gap_pips, min_stop)
    if stop_pips <= 0:
        return ""
    lots = FTMO_RISK_PER_TRADE / (stop_pips * pip_val)
    return f"  → ${FTMO_RISK_PER_TRADE} risk @ {stop_pips:.0f}pt stop = {lots:.2f} lots"


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

    history_str = " | ".join(f"{d[5:10]}:{n:+,}" for d, n in cot.history[:4])
    lines.append(f"  4-week history: {history_str}")
    return lines


def _fvg_session_age(formed_at: datetime, now_utc: datetime) -> str:
    """Return a human label for when the FVG formed relative to now."""
    ts = formed_at if formed_at.tzinfo else formed_at.replace(tzinfo=timezone.utc)
    hours = (now_utc - ts).total_seconds() / 3600
    if hours < 12:
        return "CURRENT SESSION"
    if hours < 36:
        return "YESTERDAY"
    if hours < 168:
        return "THIS WEEK"
    return "OLDER"


def _fvg_lines(fvgs: list[FVGResult], current_price: float, symbol: str) -> list[str]:
    now_utc = datetime.now(timezone.utc)
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

        # Formation timestamp — helps user find the exact candle on their chart
        if fvg.formed_at:
            sess_age   = _fvg_session_age(fvg.formed_at, now_utc)
            formed_str = fvg.formed_at.strftime("%H:%M UTC %a %d %b")
            lines.append(f"    Formed: {formed_str}  [{sess_age}]  ← find this candle on your chart")

        # Add position size hint if FVG is close to price and actionable
        if abs(pct_from) < 1.0 and fvg.probability_grade in ("A+", "A", "B"):
            gap_size = abs(fvg.gap_high - fvg.gap_low)
            hint = _position_size_hint(symbol, gap_size)
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
        src_warn, src_label = _DATA_SOURCE_LABEL.get(ctx.symbol, ("", "Unknown"))
        lines += [
            "",
            _SEP,
            f"  {ctx.symbol}  |  Current: {price:.5f}  |  Feed: {src_label}",
            _DIV,
        ]
        if src_warn:
            lines.append(f"  {src_warn}")

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
