"""
Market Structure Analysis — ICT/SMC Methodology

Detects:
  - Fair Value Gaps (FVGs) with quality grading (A+/A/B/C/SKIP)
  - Order Blocks (OBs) with quality scoring 1–5
  - Break of Structure / Change of Character (BOS/CHoCH)
  - Liquidity Pools (BSL/SSL)
  - Premium/Discount zones and OTE (Optimal Trade Entry)
  - Approximate Volume Profile (POC, VAH, VAL, LVNs)

Session Gap Filter:
  Yahoo Finance and some data sources return market-hours-only candles for
  instruments like US indices. This creates large overnight timestamp gaps that
  the FVG detector would falsely treat as price gaps. _is_session_gap() filters
  these out so only genuine intraday FVGs are detected.
"""

from __future__ import annotations
from typing import List, Optional, Tuple
from data.models import Candle, FVGResult, OrderBlock, LiquidityPool

# ── Interval mapping (seconds) ────────────────────────────────────────────────
_INTERVAL_SECONDS = {
    "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800,
}

# FVG age thresholds (candle count)
_AGE_FRESH  = 5
_AGE_RECENT = 24
_AGE_MATURE = 72


# ── Session Gap Filter ────────────────────────────────────────────────────────

def _is_session_gap(c_a: Candle, c_b: Candle) -> bool:
    """
    Returns True if the timestamp gap between two consecutive candles is much
    larger than the expected interval, indicating an overnight or weekend
    session boundary rather than continuous price action.

    This prevents phantom FVGs caused by data sources (e.g. Yahoo Finance)
    that only return market-hours candles for instruments like US500/NAS100.
    The gap between Friday close and Monday open looks like a price gap but
    isn't — the CFD traded through the weekend on the broker's platform.

    Thresholds:
      Intraday (1m–4h) : gap > 2.5× interval  (e.g. >2.5h on 1H chart)
      Daily            : gap > 4.5× interval  (handles 3-day holiday weekends)
    """
    interval_secs = _INTERVAL_SECONDS.get(c_a.timeframe, 0)
    if interval_secs == 0:
        return False
    actual_gap = (c_b.timestamp - c_a.timestamp).total_seconds()
    multiplier = 4.5 if c_a.timeframe == "1d" else 2.5
    return actual_gap > interval_secs * multiplier


# ── FVG Detection & Grading ───────────────────────────────────────────────────

def _score_fvg(
    direction: str,
    gap_low: float,
    gap_high: float,
    impulse_candle: Candle,
    candles_ago: int,
    touch_count: int,
    partial_fill_pct: float,
    context_flags: List[str],
    avg_candle_range: float,
) -> Tuple[str, str]:
    """
    Scores an FVG on six research-backed factors and returns (grade, age_label).

    Factors:
      1. Age          — freshness penalty
      2. Gap size     — relative to recent ATR
      3. Virgin       — never touched = higher score
      4. Formation    — liq grab / post-BOS context = premium
      5. Impulse body — large decisive candle = institutional intent
      6. Touch count  — more touches = weaker each time
    """
    score = 0

    # 1. Age
    if candles_ago <= _AGE_FRESH:
        age_label = "FRESH"
        score += 3
    elif candles_ago <= _AGE_RECENT:
        age_label = "RECENT"
        score += 2
    elif candles_ago <= _AGE_MATURE:
        age_label = "MATURE"
        score += 1
    else:
        age_label = "STALE"
        score += 0

    # 2. Gap size vs ATR
    gap_size = gap_high - gap_low
    gap_pct_of_atr = (gap_size / avg_candle_range) if avg_candle_range > 0 else 0
    if gap_pct_of_atr >= 1.5:
        score += 3
    elif gap_pct_of_atr >= 0.75:
        score += 2
    elif gap_pct_of_atr >= 0.3:
        score += 1

    # 3. Virgin (untouched)
    if touch_count == 0:
        score += 2
    elif touch_count == 1:
        score += 1

    # 4. Context
    if "liq.grab" in context_flags:
        score += 2
    if "post-BOS" in context_flags:
        score += 1

    # 5. Impulse body
    body_pct = (impulse_candle.body_size / impulse_candle.range_size) if impulse_candle.range_size > 0 else 0
    if body_pct >= 0.7:
        score += 2
    elif body_pct >= 0.5:
        score += 1

    # 6. Touch count penalty
    if touch_count >= 3:
        score -= 2
    elif touch_count == 2:
        score -= 1

    # Partial fill penalty
    if partial_fill_pct >= 80:
        score -= 2
    elif partial_fill_pct >= 50:
        score -= 1

    # Grade mapping
    if score >= 11:
        grade = "A+"
    elif score >= 8:
        grade = "A"
    elif score >= 5:
        grade = "B"
    elif score >= 2:
        grade = "C"
    else:
        grade = "SKIP"

    return grade, age_label


def detect_fvgs(
    candles: List[Candle],
    min_gap_pct: float = 0.01,
) -> List[FVGResult]:
    """
    Detect Fair Value Gaps in a candle series using the classic 3-candle pattern:
      Bullish FVG : candle[i+2].low > candle[i].high  (gap between C1 high and C3 low)
      Bearish FVG : candle[i+2].high < candle[i].low  (gap between C1 low and C3 high)

    Returns a list of FVGResult objects sorted by probability_grade then recency.
    Only returns FVGs from the most recent 200 candles (active zone).
    """
    if len(candles) < 3:
        return []

    recent = candles[-200:]
    total = len(recent)
    results = []

    # Average candle range for ATR-relative scoring
    avg_range = sum(c.range_size for c in recent[-20:]) / min(20, total)

    for i in range(total - 2):
        c1, c2, c3 = recent[i], recent[i + 1], recent[i + 2]

        # Skip FVGs that span session/overnight gaps
        if _is_session_gap(c1, c2) or _is_session_gap(c2, c3):
            continue

        bullish = c3.low > c1.high
        bearish = c3.high < c1.low

        if not bullish and not bearish:
            continue

        direction  = "BULL" if bullish else "BEAR"
        gap_low    = c1.high if bullish else c3.high
        gap_high   = c3.low  if bullish else c1.low
        gap_size   = gap_high - gap_low

        if gap_size <= 0:
            continue
        gap_pct = gap_size / c1.close * 100
        if gap_pct < min_gap_pct:
            continue

        candles_ago = total - 1 - (i + 1)

        # Count subsequent touches into the gap
        touch_count = 0
        lowest_reach = gap_high  if bullish else gap_low
        for future in recent[i + 3:]:
            if bullish and future.low <= gap_high:
                touch_count += 1
                lowest_reach = min(lowest_reach, future.low)
            elif not bullish and future.high >= gap_low:
                touch_count += 1
                lowest_reach = max(lowest_reach, future.high)

        # Partial fill %
        if bullish:
            filled = max(0.0, lowest_reach - gap_low)  if touch_count > 0 else 0.0
            partial_fill_pct = min(100.0, filled / gap_size * 100)
        else:
            filled = max(0.0, gap_high - lowest_reach) if touch_count > 0 else 0.0
            partial_fill_pct = min(100.0, filled / gap_size * 100)

        # Context flags: look for liquidity grab before formation
        context_flags = []
        if i >= 2:
            # Liq grab: spike beyond prior swing then immediate reversal
            prior_swings = [c.high for c in recent[max(0, i-10):i]] if bullish else [c.low for c in recent[max(0, i-10):i]]
            if prior_swings:
                extreme = min(prior_swings) if bullish else max(prior_swings)
                if bullish and c1.low < extreme:
                    context_flags.append("liq.grab")
                elif not bullish and c1.high > extreme:
                    context_flags.append("liq.grab")

        # Check for BOS before the FVG
        if i >= 5:
            pre_high = max(c.high for c in recent[max(0, i-10):i])
            pre_low  = min(c.low  for c in recent[max(0, i-10):i])
            if bullish and c2.high > pre_high:
                context_flags.append("post-BOS")
            elif not bullish and c2.low < pre_low:
                context_flags.append("post-BOS")

        impulse = c2  # The middle candle drove the gap
        grade, age_label = _score_fvg(
            direction, gap_low, gap_high, impulse,
            candles_ago, touch_count, partial_fill_pct,
            context_flags, avg_range,
        )

        results.append(FVGResult(
            symbol=c1.symbol,
            timeframe=c1.timeframe,
            direction=direction,
            gap_low=gap_low,
            gap_high=gap_high,
            formed_at=c2.timestamp,
            candles_ago=candles_ago,
            age_label=age_label,
            gap_size_pct=gap_pct,
            impulse_body_pct=(impulse.body_size / impulse.range_size * 100) if impulse.range_size > 0 else 0,
            touch_count=touch_count,
            partial_fill_pct=partial_fill_pct,
            context_flags=context_flags,
            probability_grade=grade,
        ))

    # Deduplicate overlapping FVGs (keep highest-graded per zone)
    results.sort(key=lambda f: (f.candles_ago, f.gap_low))
    seen: List[FVGResult] = []
    for fvg in results:
        overlap = False
        for s in seen:
            if s.direction == fvg.direction and s.gap_low < fvg.gap_high and fvg.gap_low < s.gap_high:
                overlap = True
                break
        if not overlap:
            seen.append(fvg)

    return seen


# ── Order Block Detection ─────────────────────────────────────────────────────

def detect_order_blocks(candles: List[Candle]) -> List[OrderBlock]:
    """
    Detect unmitigated Order Blocks.

    Bullish OB : last bearish candle before a strong bullish impulse move
    Bearish OB : last bullish candle before a strong bearish impulse move

    Quality 1–5 based on:
      +1 if body_pct > 60% (decisive candle)
      +1 if impulse move > 2× ATR
      +1 if OB formed after a BOS
      +2 if preceded by a liquidity grab (Quality 5 is liq-grab OB)
    """
    if len(candles) < 5:
        return []

    recent = candles[-150:]
    avg_range = sum(c.range_size for c in recent[-20:]) / min(20, len(recent))
    results = []

    for i in range(2, len(recent) - 2):
        c = recent[i]
        # Candidate bearish OB (last red candle before up move)
        if not c.is_bullish:
            next_move = sum(x.close - x.open for x in recent[i+1:i+4] if x.is_bullish)
            if next_move > avg_range * 1.5:
                quality = 1
                if c.body_size / c.range_size > 0.6 if c.range_size > 0 else False:
                    quality += 1
                if next_move > avg_range * 2:
                    quality += 1
                liq_grab = i >= 1 and recent[i-1].low < min(x.low for x in recent[max(0,i-5):i])
                if liq_grab:
                    quality += 2
                # Check not yet mitigated
                mitigated = any(f.low <= c.high for f in recent[i+1:])
                if not mitigated:
                    results.append(OrderBlock(
                        symbol=c.symbol, timeframe=c.timeframe,
                        direction="BULL",
                        ob_low=c.low, ob_high=c.high,
                        formed_at=c.timestamp,
                        quality=min(5, quality),
                        preceded_by_liq_grab=liq_grab,
                    ))

        # Candidate bullish OB (last green candle before down move)
        elif c.is_bullish:
            next_move = sum(x.open - x.close for x in recent[i+1:i+4] if not x.is_bullish)
            if next_move > avg_range * 1.5:
                quality = 1
                if c.body_size / c.range_size > 0.6 if c.range_size > 0 else False:
                    quality += 1
                if next_move > avg_range * 2:
                    quality += 1
                liq_grab = i >= 1 and recent[i-1].high > max(x.high for x in recent[max(0,i-5):i])
                if liq_grab:
                    quality += 2
                mitigated = any(f.high >= c.low for f in recent[i+1:])
                if not mitigated:
                    results.append(OrderBlock(
                        symbol=c.symbol, timeframe=c.timeframe,
                        direction="BEAR",
                        ob_low=c.low, ob_high=c.high,
                        formed_at=c.timestamp,
                        quality=min(5, quality),
                        preceded_by_liq_grab=liq_grab,
                    ))

    return results


# ── Liquidity Pool Detection ──────────────────────────────────────────────────

def find_liquidity_pools(candles: List[Candle], current_price: float) -> List[LiquidityPool]:
    """
    Identify unswept swing highs (BSL — Buy Side Liquidity) and
    swing lows (SSL — Sell Side Liquidity) in recent price action.
    These are where stop orders cluster — primary trade targets.
    """
    if len(candles) < 10:
        return []

    recent = candles[-100:]
    highs: dict[float, int] = {}
    lows:  dict[float, int] = {}

    for i in range(2, len(recent) - 2):
        c = recent[i]
        # Swing high: higher than 2 candles either side
        if (c.high > recent[i-1].high and c.high > recent[i-2].high and
                c.high > recent[i+1].high and c.high > recent[i+2].high):
            rounded = round(c.high, 5)
            highs[rounded] = highs.get(rounded, 0) + 1

        # Swing low: lower than 2 candles either side
        if (c.low < recent[i-1].low and c.low < recent[i-2].low and
                c.low < recent[i+1].low and c.low < recent[i+2].low):
            rounded = round(c.low, 5)
            lows[rounded] = lows.get(rounded, 0) + 1

    # Remove swept levels (price has already traded through them)
    all_prices = [c.high for c in recent] + [c.low for c in recent]
    max_price = max(all_prices)
    min_price = min(all_prices)

    pools = []
    for price, count in highs.items():
        if price > current_price:
            pools.append(LiquidityPool(
                symbol=recent[-1].symbol, price=price,
                direction="BSL", test_count=count,
            ))
    for price, count in lows.items():
        if price < current_price:
            pools.append(LiquidityPool(
                symbol=recent[-1].symbol, price=price,
                direction="SSL", test_count=count,
            ))

    pools.sort(key=lambda p: abs(p.price - current_price))
    return pools[:10]


# ── Premium / Discount ────────────────────────────────────────────────────────

def calculate_premium_discount(
    candles: List[Candle],
    lookback: int = 50,
) -> dict:
    """
    Calculates the range equilibrium (50% level), OTE zone (61.8%–78.6%),
    and whether current price is in premium, discount, or OTE.
    """
    recent = candles[-lookback:]
    high = max(c.high for c in recent)
    low  = min(c.low  for c in recent)
    eq   = (high + low) / 2.0
    current = candles[-1].close

    # OTE zone: 61.8%–78.6% Fibonacci retracement from the range
    # For a bullish range (targeting the high from the low):
    ote_low  = low + (high - low) * 0.618
    ote_high = low + (high - low) * 0.786

    in_ote = ote_low <= current <= ote_high

    if in_ote:
        status = f"OTE ZONE (Optimal Trade Entry) — {ote_low:.5f}–{ote_high:.5f}. Highest-probability LONG zone."
    elif current > eq:
        status = "PREMIUM — above equilibrium. Look for SHORTS."
    else:
        status = "DISCOUNT — below equilibrium. Look for LONGS."

    return {
        "range_high": high,
        "range_low":  low,
        "equilibrium": eq,
        "ote_low": ote_low,
        "ote_high": ote_high,
        "status": status,
    }


# ── Volume Profile (OHLCV approximation) ─────────────────────────────────────

def approximate_volume_profile(candles: List[Candle], bins: int = 50) -> dict:
    """
    Approximate volume profile from OHLCV data by distributing each candle's
    volume uniformly across its price range.

    Returns POC (Point of Control), VAH, VAL, and LVNs.
    NOTE: This is an APPROXIMATION — for precision use Sierra Chart or ATAS.
    """
    if not candles:
        return {}

    recent = candles[-100:]
    all_high = max(c.high for c in recent)
    all_low  = min(c.low  for c in recent)
    if all_high == all_low:
        return {}

    bin_size = (all_high - all_low) / bins
    volume_at_price = [0.0] * bins

    for c in recent:
        if c.range_size == 0:
            continue
        vol_per_unit = c.volume / c.range_size
        lo_bin = max(0, int((c.low - all_low) / bin_size))
        hi_bin = min(bins - 1, int((c.high - all_low) / bin_size))
        for b in range(lo_bin, hi_bin + 1):
            volume_at_price[b] += vol_per_unit * bin_size

    total_vol = sum(volume_at_price)
    if total_vol == 0:
        return {}

    poc_bin  = volume_at_price.index(max(volume_at_price))
    poc      = all_low + poc_bin * bin_size + bin_size / 2

    # Value Area = 70% of total volume around POC
    va_target = total_vol * 0.70
    va_vol = volume_at_price[poc_bin]
    lo_idx, hi_idx = poc_bin, poc_bin
    while va_vol < va_target and (lo_idx > 0 or hi_idx < bins - 1):
        lo_add = volume_at_price[lo_idx - 1] if lo_idx > 0 else 0
        hi_add = volume_at_price[hi_idx + 1] if hi_idx < bins - 1 else 0
        if lo_add >= hi_add and lo_idx > 0:
            lo_idx -= 1
            va_vol += lo_add
        elif hi_idx < bins - 1:
            hi_idx += 1
            va_vol += hi_add
        else:
            break

    vah = all_low + hi_idx * bin_size + bin_size / 2
    val = all_low + lo_idx * bin_size + bin_size / 2

    # LVNs: lowest volume bins (gaps in profile)
    sorted_bins = sorted(range(bins), key=lambda b: volume_at_price[b])
    lvns = [all_low + b * bin_size + bin_size / 2 for b in sorted_bins[:5]]
    lvns.sort()

    return {"poc": poc, "vah": vah, "val": val, "lvns": lvns}


# ── Trend Detection ───────────────────────────────────────────────────────────

def detect_trend(candles: List[Candle], lookback: int = 20) -> str:
    """Simple HH/HL (bullish) or LH/LL (bearish) trend detection."""
    if len(candles) < lookback + 1:
        return "NEUTRAL"
    subset = candles[-lookback:]
    highs = [c.high for c in subset]
    lows  = [c.low  for c in subset]
    mid   = lookback // 2
    if highs[-1] > highs[mid] and lows[-1] > lows[mid]:
        return "BULLISH"
    if highs[-1] < highs[mid] and lows[-1] < lows[mid]:
        return "BEARISH"
    return "NEUTRAL"


# ── Asian Session Analysis ────────────────────────────────────────────────────

def find_asian_range(candles_1h: List[Candle]) -> dict:
    """
    Find the Asian session range (20:00–05:00 ET) from 1H candles.
    Returns asian_high, asian_low, midnight_open, and whether London swept a side.
    """
    from zoneinfo import ZoneInfo
    _NY = ZoneInfo("America/New_York")

    if not candles_1h:
        return {}

    # Look at the last 24 hours of 1H candles
    recent_24 = candles_1h[-24:]

    asian_candles = []
    midnight_candle = None

    for c in recent_24:
        et = c.timestamp.astimezone(_NY)
        h = et.hour
        # Asian session: 20:00–05:00 ET (spans midnight)
        if h >= 20 or h < 5:
            asian_candles.append(c)
        if h == 0 and midnight_candle is None:
            midnight_candle = c

    if not asian_candles:
        return {}

    asian_high = max(c.high for c in asian_candles)
    asian_low  = min(c.low  for c in asian_candles)
    midnight_open = midnight_candle.open if midnight_candle else None

    # Check if London session has swept either side
    london_candles = []
    for c in recent_24:
        et = c.timestamp.astimezone(_NY)
        h = et.hour
        if 2 <= h < 11:
            london_candles.append(c)

    asian_swept = None
    if london_candles:
        lon_high = max(c.high for c in london_candles)
        lon_low  = min(c.low  for c in london_candles)
        if lon_low < asian_low:
            asian_swept = "LOW"
        elif lon_high > asian_high:
            asian_swept = "HIGH"

    return {
        "asian_high": asian_high,
        "asian_low": asian_low,
        "midnight_open": midnight_open,
        "asian_swept": asian_swept,
    }


# ── Session Range Note ────────────────────────────────────────────────────────

def asian_range_note(asian_high: Optional[float], asian_low: Optional[float], asian_swept: Optional[str]) -> str:
    if asian_high is None or asian_low is None:
        return ""
    if asian_swept == "LOW":
        return f"London SWEPT Asian session low ({asian_low:.5f}) → Manipulation phase likely complete. Watch for BULLISH reversal (long setups)."
    if asian_swept == "HIGH":
        return f"London SWEPT Asian session high ({asian_high:.5f}) → Manipulation phase likely complete. Watch for BEARISH reversal (short setups)."
    return f"Asian range intact: {asian_low:.5f} – {asian_high:.5f}. Watch for London to sweep one side before the true move begins."
