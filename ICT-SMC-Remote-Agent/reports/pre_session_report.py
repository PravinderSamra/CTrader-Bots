"""
Pre-Session Report Generator

Formats the full market scan output in a readable, actionable format.
Per-FVG trade plans: SL, TP1/2/3, confluence scoring (OB, trend, session bias,
Asian sweep, liq.grab, post-BOS, COT, premium/discount, OTE).
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
_WIDTH = 70
_SEP   = "═" * _WIDTH
_DIV   = "─" * _WIDTH
_DOT   = "·" * _WIDTH

# Price units per pip for every supported instrument
_PIP_SIZE: dict[str, float] = {
    # Forex majors
    "EURUSD": 0.0001, "GBPUSD": 0.0001, "AUDUSD": 0.0001, "NZDUSD": 0.0001,
    "USDJPY": 0.01,   "USDCHF": 0.0001, "USDCAD": 0.0001,
    # Forex crosses
    "GBPJPY": 0.01,  "EURJPY": 0.01,  "AUDJPY": 0.01,
    "EURGBP": 0.0001, "GBPAUD": 0.0001, "EURCAD": 0.0001, "GBPCAD": 0.0001,
    # US indices (1 point = 1 pip)
    "SPX": 1.0, "NDX": 1.0, "US30": 1.0,
    # European indices
    "DAX": 1.0, "UK100": 1.0, "FRA40": 1.0, "EUSTX50": 1.0,
    # Asian indices
    "JPN225": 1.0, "AUS200": 1.0, "HK50": 1.0,
    # Metals
    "GOLD": 1.0, "SILVER": 0.01,
    # Commodities
    "OIL": 0.01, "BRENT": 0.01, "NATGAS": 0.001,
    # Crypto
    "BTCUSDT": 1.0, "ETHUSDT": 1.0, "SOLUSDT": 0.1,
}

# Minimum stop in price units (to prevent nonsensical lot sizes from tiny gaps)
_MIN_STOP: dict[str, float] = {
    # Forex majors (pips × pip_size)
    "EURUSD": 0.0015, "GBPUSD": 0.0015, "AUDUSD": 0.0015, "NZDUSD": 0.0015,
    "USDJPY": 0.15,   "USDCHF": 0.0015, "USDCAD": 0.0015,
    # Forex crosses
    "GBPJPY": 0.20,  "EURJPY": 0.20,  "AUDJPY": 0.15,
    "EURGBP": 0.0010, "GBPAUD": 0.0020, "EURCAD": 0.0015, "GBPCAD": 0.0020,
    # US indices
    "SPX": 8.0, "NDX": 12.0, "US30": 30.0,
    # European indices
    "DAX": 10.0, "UK100": 15.0, "FRA40": 10.0, "EUSTX50": 8.0,
    # Asian indices
    "JPN225": 50.0, "AUS200": 10.0, "HK50": 30.0,
    # Metals
    "GOLD": 5.0, "SILVER": 0.30,
    # Commodities
    "OIL": 0.30, "BRENT": 0.30, "NATGAS": 0.05,
    # Crypto
    "BTCUSDT": 200.0, "ETHUSDT": 20.0, "SOLUSDT": 2.0,
}

# Build data source labels from INSTRUMENTS config once at import time
_DATA_SOURCE_LABEL: dict[str, str] = {}
_SOURCE_DISPLAY = {"twelve_data": "Twelve Data", "yahoo": "Yahoo Finance", "okx": "OKX"}
_SOURCE_WARN: dict[str, str] = {
    "yahoo":      "⚠  Yahoo Finance (market-hours only). Verify levels on Pepperstone chart before trading.",
    "okx":        "ℹ  OKX spot feed. Pepperstone crypto levels typically match closely.",
    "twelve_data":"ℹ  Twelve Data spot. Levels should be close to Pepperstone (<1-2 pip variance).",
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


def _pips(price_units: float, symbol: str) -> float:
    pip = _PIP_SIZE.get(symbol, 0.0001)
    return price_units / pip if pip else 0.0


def _fmt_price(v: float, symbol: str) -> str:
    """Format price with appropriate decimal places per instrument."""
    pip = _PIP_SIZE.get(symbol, 0.0001)
    if pip >= 1.0:
        return f"{v:.1f}"
    if pip >= 0.01:
        return f"{v:.3f}"
    if pip >= 0.001:
        return f"{v:.4f}"
    return f"{v:.5f}"


def _position_size(symbol: str, stop_price_units: float) -> str:
    pip_val = PIP_VALUE_PER_LOT.get(symbol)
    pip_size = _PIP_SIZE.get(symbol)
    if not pip_val or not pip_size:
        return ""
    stop_pips = stop_price_units / pip_size
    if stop_pips <= 0:
        return ""
    lots = FTMO_RISK_PER_TRADE / (stop_pips * pip_val)
    return f"{lots:.2f} lots"


# ── Confluence check ──────────────────────────────────────────────────────────

def _confluence_checks(fvg: FVGResult, ctx: MarketContext) -> list[tuple[bool, str]]:
    """
    Returns a list of (passed, description) tuples for each confluence check.
    Used to build the per-FVG confluence block in the report.
    """
    is_bull = fvg.direction == "BULL"
    checks = []

    # 1. Higher-TF trend aligned
    htf = ctx.higher_tf_trend
    aligned_htf = (is_bull and htf == "BULLISH") or (not is_bull and htf == "BEARISH")
    checks.append((aligned_htf, f"HTF (daily) trend: {htf}"))

    # 2. Intraday trend aligned
    intra = ctx.intraday_trend
    aligned_intra = (is_bull and intra == "BULLISH") or (not is_bull and intra == "BEARISH")
    checks.append((aligned_intra, f"Intraday (1H) trend: {intra}"))

    # 3. Session bias from midnight open
    if ctx.midnight_open:
        price_vs_mid = ctx.current_price < ctx.midnight_open
        mid_aligned = (is_bull and price_vs_mid) or (not is_bull and not price_vs_mid)
        bias_label = "DISCOUNT (below midnight open)" if price_vs_mid else "PREMIUM (above midnight open)"
        checks.append((mid_aligned, f"Session bias: {bias_label}"))
    else:
        checks.append((False, "Session bias: midnight open unavailable"))

    # 4. Asian manipulation swept in setup direction
    asian_swept = ctx.asian_swept
    if asian_swept:
        swept_aligned = (is_bull and asian_swept == "LOW") or (not is_bull and asian_swept == "HIGH")
        swept_label = f"Asian {'low' if asian_swept == 'LOW' else 'high'} swept — manipulation complete"
        checks.append((swept_aligned, swept_label))
    else:
        checks.append((False, "Asian manipulation: range intact (watch for sweep before entry)"))

    # 5. In discount (bull) or premium (bear)
    pd_status = ctx.premium_discount_status
    in_discount = "DISCOUNT" in pd_status or "OTE" in pd_status
    in_premium  = "PREMIUM"  in pd_status or "OTE" in pd_status
    pd_aligned = (is_bull and in_discount) or (not is_bull and in_premium)
    checks.append((pd_aligned, f"P/D zone: {pd_status.split('—')[0].strip()}"))

    # 6. In OTE zone (61.8–78.6% Fibonacci retracement — highest probability entry)
    in_ote = ctx.ote_low <= ctx.current_price <= ctx.ote_high
    checks.append((in_ote, f"OTE zone: {'IN OTE ({:.5f}–{:.5f})'.format(ctx.ote_low, ctx.ote_high) if in_ote else 'NOT in OTE'}"))

    # 7. FVG liquidity grab context
    has_liq_grab = "liq.grab" in fvg.context_flags
    checks.append((has_liq_grab, "Liquidity grab before FVG formation" + (" ✓" if has_liq_grab else " (not detected)")))

    # 8. FVG post-BOS context
    has_bos = "post-BOS" in fvg.context_flags
    checks.append((has_bos, "Break of Structure before FVG" + (" ✓" if has_bos else " (not detected)")))

    # 9. Nearby unmitigated Order Block in same direction
    pip_size = _PIP_SIZE.get(ctx.symbol, 0.0001)
    # ATR-based proximity: 10% of recent price range (adapts per instrument)
    range_size = (ctx.range_high - ctx.range_low) if (ctx.range_high and ctx.range_low) else 0
    proximity_threshold = range_size * 0.10 if range_size > 0 else pip_size * 50
    nearby_ob = None
    for ob in ctx.order_blocks:
        if ob.direction != fvg.direction:
            continue
        ob_dist = abs(ob.mid - fvg.gap_low) if is_bull else abs(ob.mid - fvg.gap_high)
        if ob_dist < proximity_threshold:
            nearby_ob = ob
            break
    if nearby_ob:
        checks.append((True, f"Order Block confluence: {_fmt_price(nearby_ob.ob_low, ctx.symbol)}–{_fmt_price(nearby_ob.ob_high, ctx.symbol)} (Q:{nearby_ob.quality}/5{'  liq-grab OB' if nearby_ob.preceded_by_liq_grab else ''})"))
    else:
        checks.append((False, "Order Block: no nearby OB in setup direction"))

    # 10. COT macro alignment (omitted entirely when data unavailable — don't penalise missing data)
    if ctx.cot:
        cot_aligned = (is_bull and ctx.cot.bias == "BULLISH") or (not is_bull and ctx.cot.bias == "BEARISH")
        cot_warn = ""
        if (is_bull and ctx.cot.rank_8wk >= 90) or (not is_bull and ctx.cot.rank_8wk <= 10):
            cot_warn = "  ⚠ CROWDED — contrarian risk"
        checks.append((cot_aligned, f"COT: {ctx.cot.bias} ({ctx.cot.rank_8wk}th pct, {ctx.cot.report_date}){cot_warn}"))
    # else: COT unavailable — omit check so score is out of 9, not penalised as 0/10

    return checks


def _compute_fvg_setup(fvg: FVGResult, ctx: MarketContext) -> Optional[dict]:
    """
    Compute SL, entry zone, TP1/TP2/TP3, lot size, and confluence score.
    Returns None if pip data is unavailable.
    """
    symbol = ctx.symbol
    pip_size = _PIP_SIZE.get(symbol)
    if not pip_size:
        return None

    is_bull = fvg.direction == "BULL"
    gap_low, gap_high = fvg.gap_low, fvg.gap_high
    gap_size = gap_high - gap_low

    # SL: just beyond the FVG edge, minimum 10% of gap beyond it
    min_stop = _MIN_STOP.get(symbol, pip_size * 15)
    buffer   = max(gap_size * 0.10, pip_size * 3)
    entry    = (gap_low + gap_high) / 2   # mid-FVG OTE entry

    # Compute initial stop from FVG edge + buffer, then enforce minimum
    initial_stop = (entry - (gap_low - buffer)) if is_bull else ((gap_high + buffer) - entry)
    stop_size    = max(initial_stop, min_stop)

    # SL is always exactly stop_size away from entry
    sl = entry - stop_size if is_bull else entry + stop_size

    # TP1: 1:1 RR
    tp1 = entry + stop_size if is_bull else entry - stop_size

    # TP2: nearest unswept liquidity pool in trade direction
    tp2 = None
    tp2_label = ""
    if is_bull:
        bsl = sorted([p for p in ctx.liquidity_pools if p.direction == "BSL" and p.price > entry],
                     key=lambda p: p.price)
        if bsl:
            tp2 = bsl[0].price
            tp2_label = f"BSL ({bsl[0].test_count}× tested)"
    else:
        ssl = sorted([p for p in ctx.liquidity_pools if p.direction == "SSL" and p.price < entry],
                     key=lambda p: p.price, reverse=True)
        if ssl:
            tp2 = ssl[0].price
            tp2_label = f"SSL ({ssl[0].test_count}× tested)"

    # TP3: prior day high (bull) / prior day low (bear)
    tp3 = ctx.prior_day_high if is_bull else ctx.prior_day_low
    tp3_label = "prior day high (BSL)" if is_bull else "prior day low (SSL)"

    # Confluences
    checks = _confluence_checks(fvg, ctx)
    score  = sum(1 for passed, _ in checks if passed)

    # Position size
    size_str = _position_size(symbol, stop_size)

    # RR ratios
    rr_tp1 = abs(tp1 - entry) / stop_size if stop_size > 0 else 0
    rr_tp2 = abs(tp2 - entry) / stop_size if (tp2 and stop_size > 0) else None
    rr_tp3 = abs(tp3 - entry) / stop_size if (tp3 and stop_size > 0) else None

    return {
        "entry_low": gap_low,
        "entry_high": gap_high,
        "entry_mid": entry,
        "current_price": ctx.current_price,
        "sl": sl,
        "stop_pips": stop_size / pip_size,
        "tp1": tp1,
        "tp2": tp2,
        "tp2_label": tp2_label,
        "tp3": tp3,
        "tp3_label": tp3_label,
        "rr_tp1": rr_tp1,
        "rr_tp2": rr_tp2,
        "rr_tp3": rr_tp3,
        "size_str": size_str,
        "confluences": checks,
        "confluence_score": score,
        "total_checks": len(checks),
    }


def _format_setup_block(setup: dict, symbol: str) -> list[str]:
    """Format the trade plan lines for one FVG."""
    fp = lambda v: _fmt_price(v, symbol)
    lines = []

    is_bull = setup["tp1"] > setup["entry_mid"]

    # Current price relative to entry zone
    curr = setup.get("current_price")
    if curr is not None:
        entry_low, entry_high = setup["entry_low"], setup["entry_high"]
        if curr < entry_low:
            dist = fp(entry_low - curr)
            pos = f"{dist} below entry zone ↓  (price must drop to fill)"
        elif curr > entry_high:
            dist = fp(curr - entry_high)
            pos = f"{dist} above entry zone ↑  (price must rally to fill)"
        else:
            pos = "AT LEVEL — price inside FVG now"
        lines.append(f"    Current     : {fp(curr)}  ({pos})")

    # Entry zone
    lines.append(f"    Entry zone  : {fp(setup['entry_low'])} → {fp(setup['entry_high'])}  (enter anywhere in FVG)")

    # SL
    stop_pips = setup["stop_pips"]
    lines.append(f"    SL          : {fp(setup['sl'])}  ({stop_pips:.0f}pt stop from entry midpoint)")

    # TP1 — partial close (take 50% off)
    lines.append(f"    TP1 (partial 50%) : {fp(setup['tp1'])}  [R/R {setup['rr_tp1']:.1f}:1]")

    # TP2 — primary target (run remaining 50% to liquidity)
    if setup["tp2"]:
        rr = f"  [R/R {setup['rr_tp2']:.1f}:1]" if setup["rr_tp2"] else ""
        lines.append(f"    TP2 ★ PRIMARY     : {fp(setup['tp2'])}  {setup['tp2_label']}{rr}")

    # TP3
    if setup["tp3"]:
        rr = f"  [R/R {setup['rr_tp3']:.1f}:1]" if setup["rr_tp3"] else ""
        lines.append(f"    TP3 (PDH/L) : {fp(setup['tp3'])}  {setup['tp3_label']}{rr}")

    # Size
    if setup["size_str"]:
        lines.append(f"    Size        : ${FTMO_RISK_PER_TRADE} risk = {setup['size_str']} @ {stop_pips:.0f}pt stop")

    # Confluences
    score = setup["confluence_score"]
    total = setup["total_checks"]
    bar = "█" * score + "░" * (total - score)
    lines.append(f"    Confluences : {score}/{total}  [{bar}]")
    for passed, desc in setup["confluences"]:
        tick = "  ✓" if passed else "  ✗"
        lines.append(f"    {tick} {desc}")

    return lines


def _fvg_session_age(formed_at: datetime, now_utc: datetime) -> str:
    ts = formed_at if formed_at.tzinfo else formed_at.replace(tzinfo=timezone.utc)
    hours = (now_utc - ts).total_seconds() / 3600
    if hours < 12:
        return "CURRENT SESSION"
    if hours < 36:
        return "YESTERDAY"
    if hours < 168:
        return "THIS WEEK"
    return "OLDER"


def _fvg_lines(fvgs: list, ctx: MarketContext) -> list[str]:
    now_utc = datetime.now(timezone.utc)
    symbol  = ctx.symbol
    price   = ctx.current_price
    fp      = lambda v: _fmt_price(v, symbol)

    # Kill zone flag — marks live KZ opportunities
    kz = active_kill_zone()

    # Trend alignment gate: if HTF and intraday trends disagree, cap A/A+ grades at B
    trends_aligned = (
        ctx.higher_tf_trend in ("BULLISH", "BEARISH") and
        ctx.intraday_trend  in ("BULLISH", "BEARISH") and
        ctx.higher_tf_trend == ctx.intraday_trend
    )

    # Session bias from midnight open — used to suppress counter-trend FVGs
    session_bull_bias = None  # None = ambiguous (no midnight open data)
    if ctx.midnight_open:
        session_bull_bias = price < ctx.midnight_open  # True = discount → bull bias

    displayable = [f for f in fvgs if f.probability_grade not in SKIP_GRADES]
    # Sort: grade first, then nearest to current price within the same grade
    displayable.sort(key=lambda f: (
        _GRADE_ORDER.get(f.probability_grade, 9),
        abs((f.gap_low if f.direction == "BULL" else f.gap_high) - price)
    ))

    # Split into session-aligned vs counter-trend (no display limit applied yet)
    if session_bull_bias is not None:
        aligned_fvgs  = [f for f in displayable if (f.direction == "BULL") == session_bull_bias]
        counter_fvgs  = [f for f in displayable if (f.direction == "BULL") != session_bull_bias]
    else:
        aligned_fvgs  = displayable
        counter_fvgs  = []

    aligned_fvgs = aligned_fvgs[:MAX_FVG_DISPLAY]

    if not aligned_fvgs and not counter_fvgs:
        return ["  No high-probability FVGs detected."]

    lines = []

    if not aligned_fvgs:
        lines.append("  No session-aligned FVGs. See counter-trend summary below.")
        lines.append("")

    for fvg in aligned_fvgs:
        # Trend alignment gate: downgrade A/A+ to B when HTF ≠ intraday
        display_grade = fvg.probability_grade
        trend_capped  = False
        if not trends_aligned and display_grade in ("A+", "A"):
            display_grade = "B"
            trend_capped  = True

        direction = "Bullish" if fvg.direction == "BULL" else "Bearish"
        ref_price = fvg.gap_low if fvg.direction == "BULL" else fvg.gap_high
        pct_from  = (ref_price - price) / price * 100
        pos_str   = f"({pct_from:+.2f}%, {'ABOVE' if pct_from >= 0 else 'BELOW'} price)"
        at_level  = "  ← PRICE AT LEVEL" if abs(pct_from) < 0.20 else ""
        ctx_str   = "  [" + ", ".join(fvg.context_flags) + "]" if fvg.context_flags else ""
        fill_str  = f"  {fvg.partial_fill_pct:.0f}% filled" if fvg.touch_count > 0 else "  virgin"
        touched   = f"  {fvg.touch_count}× tested" if fvg.touch_count > 0 else "  untouched"

        kz_flag   = f"  ⚡ {kz}" if kz else ""
        cap_note  = f"  ⚠ trend split → {fvg.probability_grade} capped at B" if trend_capped else ""

        # Header line
        lines.append(
            f"  ┌─ [{direction} FVG | {fvg.timeframe}]  "
            f"{fp(fvg.gap_low)} → {fp(fvg.gap_high)}  "
            f"{_grade_symbol(display_grade)}{kz_flag}{cap_note}"
        )

        # ── FVG DETAILS — evaluate these before looking at the trade plan ──
        lines.append("  │  ── FVG DETAILS ─────────────────────────────────────────────")
        if fvg.formed_at:
            sess_age   = _fvg_session_age(fvg.formed_at, now_utc)
            formed_str = fvg.formed_at.strftime("%Y-%m-%d %H:%M UTC")
            gap_size   = fvg.gap_high - fvg.gap_low
            lines.append(f"  │  Formed   : {formed_str}  [{sess_age}]")
            lines.append(f"  │  Range    : {fp(fvg.gap_low)} → {fp(fvg.gap_high)}  (gap = {fp(gap_size)})")
        lines.append(
            f"  │  Status   : {fvg.age_label} ({fvg.candles_ago}c ago){fill_str}{touched}"
        )
        lines.append(f"  │  vs Price : {pos_str}{at_level}{ctx_str}")

        # Trade plan
        setup = _compute_fvg_setup(fvg, ctx)
        if setup:
            lines.append("  │")
            lines.append("  │  ── TRADE PLAN ──────────────────────────────────────────")
            for tl in _format_setup_block(setup, symbol):
                lines.append(f"  │  {tl.lstrip()}")
        else:
            lines.append(f"  │  (No pip data for position sizing on {symbol})")

        lines.append("  └" + "─" * 60)
        lines.append("")

    # Counter-trend summary — suppressed from main view, noted for awareness
    if counter_fvgs:
        bias_dir = "BULL (discount)" if session_bull_bias else "BEAR (premium)"
        lines.append(
            f"  ↓ {len(counter_fvgs)} counter-trend FVG(s) suppressed "
            f"(session bias: {bias_dir} from midnight open)"
        )
        lines.append("")

    return lines


def _ob_lines(obs: list[OrderBlock], current_price: float, symbol: str) -> list[str]:
    if not obs:
        return []
    fp = lambda v: _fmt_price(v, symbol)
    lines = []
    for ob in obs[:MAX_OB_DISPLAY]:
        direction = "BULL OB" if ob.direction == "BULL" else "BEAR OB"
        pct = (ob.mid - current_price) / current_price * 100
        pos = f"({'above' if pct >= 0 else 'below'} price, {pct:+.2f}%)"
        liq = "  ← Preceded by liquidity grab" if ob.preceded_by_liq_grab else ""
        formed = f"  Formed: {ob.formed_at.strftime('%Y-%m-%d %H:%M UTC')}" if ob.formed_at else ""
        lines.append(
            f"  [{direction} | {ob.timeframe}] "
            f"{fp(ob.ob_low)}–{fp(ob.ob_high)}  {pos}  Q:{ob.quality}/5{liq}{formed}"
        )
    return lines


def _liq_lines(pools: list[LiquidityPool], current_price: float, symbol: str) -> list[str]:
    if not pools:
        return []
    fp = lambda v: _fmt_price(v, symbol)
    bsl = [p for p in pools if p.direction == "BSL"][:MAX_LIQ_DISPLAY // 2 + 1]
    ssl = [p for p in pools if p.direction == "SSL"][:MAX_LIQ_DISPLAY // 2 + 1]
    lines = []
    for p in sorted(bsl, key=lambda x: x.price):
        pct = (p.price - current_price) / current_price * 100
        lines.append(f"  BSL above: {fp(p.price)}  ({pct:+.2f}%)  [{p.test_count}× tested, {p.strength} strength]")
    for p in sorted(ssl, key=lambda x: x.price, reverse=True):
        pct = (p.price - current_price) / current_price * 100
        lines.append(f"  SSL below: {fp(p.price)}  ({pct:+.2f}%)  [{p.test_count}× tested, {p.strength} strength]")
    return lines


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


def generate_report(markets: list[MarketContext]) -> str:
    now_utc = datetime.now(timezone.utc)
    now_str = now_utc.strftime("%Y-%m-%d %H:%M UTC")
    kz   = active_kill_zone()
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
        "",
        "  FVG TRADE PLAN NOTES",
        _DIV,
        "  • Entry zone  = entire FVG (enter at any price within gap)",
        "  • SL          = just beyond the FVG edge (10% of gap + small buffer)",
        "  • TP1 (partial 50%) = 1:1 RR — close half position here",
        "  • TP2 ★ PRIMARY     = nearest unswept BSL/SSL — run remaining 50%",
        "  • TP3 (PDH/L)       = prior day high/low — full extension target",
        "  • Confluences       = 9-10 factor ICT/SMC scoring (COT excluded when unavailable)",
        _SEP,
    ]

    for ctx in markets:
        price = ctx.current_price
        src_warn, src_label = _DATA_SOURCE_LABEL.get(ctx.symbol, ("", "Unknown"))
        fp = lambda v: _fmt_price(v, ctx.symbol)

        lines += [
            "",
            _SEP,
            f"  {ctx.symbol}  |  Current: {fp(price)}  |  Feed: {src_label}",
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
            f"  Range: {fp(ctx.range_low)} – {fp(ctx.range_high)}",
            f"  Equilibrium: {fp(ctx.equilibrium)}",
            f"  {ctx.premium_discount_status}",
            f"  OTE zone: {fp(ctx.ote_low)} – {fp(ctx.ote_high)}",
        ]

        # Session Levels
        lines += [
            "",
            "  SESSION LEVELS",
            f"  Prior day high : {fp(ctx.prior_day_high)}  ← BSL target",
            f"  Prior day low  : {fp(ctx.prior_day_low)}  ← SSL target",
        ]
        if ctx.asian_high is not None:
            lines.append(f"  Asian high     : {fp(ctx.asian_high)}")
        if ctx.asian_low is not None:
            lines.append(f"  Asian low      : {fp(ctx.asian_low)}")
        if ctx.midnight_open is not None:
            mid_open = ctx.midnight_open
            disc = "DISCOUNT — favour LONGS" if price < mid_open else "PREMIUM — favour SHORTS"
            lines.append(f"  Midnight open  : {fp(mid_open)}  [{disc}]")

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
                f"  POC : {fp(ctx.poc)}  ← magnetic level",
            ]
            if ctx.vah:
                lines.append(f"  VAH : {fp(ctx.vah)}  ← resistance / target")
            if ctx.val:
                lines.append(f"  VAL : {fp(ctx.val)}  ← support / target")
            if ctx.lvns:
                lines.append(f"  LVNs: {', '.join(fp(v) for v in ctx.lvns[:5])}")

        # Order Blocks
        ob_lines = _ob_lines(ctx.order_blocks, price, ctx.symbol)
        if ob_lines:
            lines += ["", "  ACTIVE ORDER BLOCKS (unmitigated)"] + ob_lines

        # FVGs with full trade plans inline
        lines += ["", "  FAIR VALUE GAPS + TRADE PLANS (SKIP-grade filtered)"]
        lines += _fvg_lines(ctx.fvgs, ctx)

        # Liquidity pools
        liq = _liq_lines(ctx.liquidity_pools, price, ctx.symbol)
        if liq:
            lines += ["", "  LIQUIDITY POOLS (unswept — primary TP targets)"] + liq

        # COT
        if ctx.cot:
            lines += ["", "  SMART MONEY POSITIONING — CFTC COT (Tier 3 / weekly)"]
            lines += _cot_section(ctx.cot)

        lines.append(_DOT)

    lines += ["", _SEP, "  END OF REPORT", _SEP, ""]
    return "\n".join(lines)
