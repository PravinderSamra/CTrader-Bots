"""
Structural Analysis Engine

Identifies: Order Blocks, Fair Value Gaps, BOS/CHoCH,
Swing Points, Liquidity Pools, Market Structure.

All Tier 2 — derived from OHLCV. No real-time order flow data.
Outputs clearly labelled with this limitation.
"""

import statistics
from datetime import datetime
from typing import List, Optional, Tuple
from data.models import (
    Candle, OrderBlock, FairValueGap, LiquidityPool,
    SwingPoint, MarketStructure
)
from config import (
    DISPLACEMENT_ATR_MULTIPLIER, FVG_MIN_ATR_PCT,
    SWING_LOOKBACK, EQUAL_LEVEL_TOLERANCE_PCT
)


def compute_atr(candles: List[Candle], period: int = 14) -> float:
    """Average True Range — used for displacement and FVG size filtering."""
    if len(candles) < 2:
        return 0.0
    true_ranges = []
    for i in range(1, min(period + 1, len(candles))):
        c = candles[i]
        p = candles[i - 1]
        tr = max(c.high - c.low, abs(c.high - p.close), abs(c.low - p.close))
        true_ranges.append(tr)
    return statistics.mean(true_ranges) if true_ranges else 0.0


def find_swing_points(candles: List[Candle], lookback: int = SWING_LOOKBACK) -> List[SwingPoint]:
    """
    Identify significant swing highs and swing lows.
    A swing high: highest high among [i-lookback : i+lookback+1].
    A swing low:  lowest low among  [i-lookback : i+lookback+1].
    """
    swings = []
    n = len(candles)
    for i in range(lookback, n - lookback):
        window = candles[i - lookback: i + lookback + 1]
        is_swing_high = candles[i].high == max(c.high for c in window)
        is_swing_low  = candles[i].low  == min(c.low  for c in window)
        if is_swing_high:
            swings.append(SwingPoint(
                price=candles[i].high,
                timestamp=candles[i].timestamp,
                swing_type="high",
                timeframe=candles[i].timeframe,
            ))
        if is_swing_low:
            swings.append(SwingPoint(
                price=candles[i].low,
                timestamp=candles[i].timestamp,
                swing_type="low",
                timeframe=candles[i].timeframe,
            ))
    return sorted(swings, key=lambda s: s.timestamp)


def detect_bos_choch(candles: List[Candle]) -> MarketStructure:
    """
    Detect Break of Structure (BOS) and Change of Character (CHoCH).
    Builds the MarketStructure object with trend, last BOS, and CHoCH signals.
    """
    symbol    = candles[0].symbol    if candles else ""
    timeframe = candles[0].timeframe if candles else ""
    swings    = find_swing_points(candles)

    highs = [s for s in swings if s.swing_type == "high"]
    lows  = [s for s in swings if s.swing_type == "low"]

    structure = MarketStructure(
        symbol=symbol,
        timeframe=timeframe,
        trend="neutral",
        recent_swing_highs=highs[-5:],
        recent_swing_lows=lows[-5:],
    )

    if len(highs) < 2 or len(lows) < 2:
        return structure

    # Determine trend from last 2 swing highs and lows
    hh = highs[-1].price > highs[-2].price   # Higher high
    hl = lows[-1].price  > lows[-2].price    # Higher low
    lh = highs[-1].price < highs[-2].price   # Lower high
    ll = lows[-1].price  < lows[-2].price    # Lower low

    if hh and hl:
        structure.trend = "bullish"
    elif lh and ll:
        structure.trend = "bearish"
    else:
        structure.trend = "neutral"

    # BOS detection: most recent close vs last swing in trend direction
    last_close = candles[-1].close
    if structure.trend == "bullish" and last_close > highs[-2].price:
        structure.last_bos_price     = highs[-2].price
        structure.last_bos_direction = "bullish"
    elif structure.trend == "bearish" and last_close < lows[-2].price:
        structure.last_bos_price     = lows[-2].price
        structure.last_bos_direction = "bearish"

    # CHoCH detection: breaks against the current trend
    if structure.trend == "bullish" and last_close < lows[-1].price:
        structure.last_choch_price = lows[-1].price
        structure.choch_confirmed  = True
    elif structure.trend == "bearish" and last_close > highs[-1].price:
        structure.last_choch_price = highs[-1].price
        structure.choch_confirmed  = True

    return structure


def detect_order_blocks(candles: List[Candle]) -> List[OrderBlock]:
    """
    Identify order blocks: the last opposing candle before a strong
    impulsive move that caused a displacement.

    Bullish OB: last bearish candle before a strong bullish impulse.
    Bearish OB: last bullish candle before a strong bearish impulse.
    """
    if len(candles) < 5:
        return []

    atr    = compute_atr(candles)
    swings = find_swing_points(candles)
    swing_highs = {s.timestamp: s.price for s in swings if s.swing_type == "high"}
    swing_lows  = {s.timestamp: s.price for s in swings if s.swing_type == "low"}
    order_blocks = []

    for i in range(2, len(candles) - 1):
        impulse = candles[i]
        prev    = candles[i - 1]

        displacement = impulse.body_size / atr if atr > 0 else 0

        # Only consider meaningful displacement
        if displacement < DISPLACEMENT_ATR_MULTIPLIER:
            continue

        # Bullish impulse: look back for the last bearish candle as the OB
        if impulse.is_bullish and impulse.close > max(c.high for c in candles[max(0, i-5):i]):
            # Find last bearish candle in the 1–5 candles before the impulse
            for j in range(i - 1, max(0, i - 5), -1):
                if not candles[j].is_bullish:
                    ob_candle = candles[j]
                    preceded_by_grab = _check_liquidity_grab(candles, j, "bullish")
                    ob = OrderBlock(
                        symbol=candles[0].symbol,
                        timeframe=candles[0].timeframe,
                        direction="bullish",
                        high=ob_candle.high,
                        low=ob_candle.low,
                        formed_at=ob_candle.timestamp,
                        preceded_by_liquidity_grab=preceded_by_grab,
                        displacement_atr_multiple=displacement,
                        caused_bos=displacement >= 2.0,
                    )
                    ob.compute_quality()
                    ob = _check_mitigation(ob, candles[i:])
                    order_blocks.append(ob)
                    break

        # Bearish impulse: look back for the last bullish candle as the OB
        elif not impulse.is_bullish and impulse.close < min(c.low for c in candles[max(0, i-5):i]):
            for j in range(i - 1, max(0, i - 5), -1):
                if candles[j].is_bullish:
                    ob_candle = candles[j]
                    preceded_by_grab = _check_liquidity_grab(candles, j, "bearish")
                    ob = OrderBlock(
                        symbol=candles[0].symbol,
                        timeframe=candles[0].timeframe,
                        direction="bearish",
                        high=ob_candle.high,
                        low=ob_candle.low,
                        formed_at=ob_candle.timestamp,
                        preceded_by_liquidity_grab=preceded_by_grab,
                        displacement_atr_multiple=displacement,
                        caused_bos=displacement >= 2.0,
                    )
                    ob.compute_quality()
                    ob = _check_mitigation(ob, candles[i:])
                    order_blocks.append(ob)
                    break

    return order_blocks


def detect_fvgs(candles: List[Candle]) -> List[FairValueGap]:
    """
    Identify Fair Value Gaps (three-candle imbalances).

    Bullish FVG: candle[i].high < candle[i+2].low
    Bearish FVG: candle[i].low  > candle[i+2].high

    Each FVG is scored 0–10 with a probability grade (A+/A/B/C/SKIP)
    based on age, gap size, touch count, impulse strength, and context.
    """
    if len(candles) < 3:
        return []

    atr  = compute_atr(candles)
    total = len(candles)
    fvgs = []

    # Pre-compute BOS candle indices for context scoring
    bos_indices = _find_bos_candle_indices(candles)

    for i in range(total - 2):
        c1, c2, c3 = candles[i], candles[i + 1], candles[i + 2]

        # Skip FVGs that span session/overnight gaps (market-hours-only data
        # like Yahoo Finance ^GSPC creates phantom gaps at the open/close boundary)
        if _is_session_gap(c1, c2) or _is_session_gap(c2, c3):
            continue

        # Bullish FVG
        if c1.high < c3.low:
            gap_size = c3.low - c1.high
            if gap_size >= atr * FVG_MIN_ATR_PCT:
                subsequent = candles[i + 3:]
                candles_ago = total - 1 - (i + 1)  # candles since the impulse (c2)
                liq_grab = _check_liquidity_grab(candles, i, "bullish")
                after_bos = i in bos_indices or (i - 1) in bos_indices
                fvg = FairValueGap(
                    symbol=c1.symbol,
                    timeframe=c1.timeframe,
                    direction="bullish",
                    gap_high=c3.low,
                    gap_low=c1.high,
                    formed_at=c2.timestamp,
                    impulse_volume=c2.volume,
                    impulse_body_size=c2.body_size,
                    candles_ago=candles_ago,
                    preceded_by_liquidity_grab=liq_grab,
                    formed_after_bos=after_bos,
                )
                fvg = _check_fvg_mitigation(fvg, subsequent)
                _score_fvg(fvg, atr)
                fvgs.append(fvg)

        # Bearish FVG
        elif c1.low > c3.high:
            gap_size = c1.low - c3.high
            if gap_size >= atr * FVG_MIN_ATR_PCT:
                subsequent = candles[i + 3:]
                candles_ago = total - 1 - (i + 1)
                liq_grab = _check_liquidity_grab(candles, i, "bearish")
                after_bos = i in bos_indices or (i - 1) in bos_indices
                fvg = FairValueGap(
                    symbol=c1.symbol,
                    timeframe=c1.timeframe,
                    direction="bearish",
                    gap_high=c1.low,
                    gap_low=c3.high,
                    formed_at=c2.timestamp,
                    impulse_volume=c2.volume,
                    impulse_body_size=c2.body_size,
                    candles_ago=candles_ago,
                    preceded_by_liquidity_grab=liq_grab,
                    formed_after_bos=after_bos,
                )
                fvg = _check_fvg_mitigation(fvg, subsequent)
                _score_fvg(fvg, atr)
                fvgs.append(fvg)

    return fvgs


def detect_liquidity_pools(
    candles: List[Candle],
    swing_lookback: int = SWING_LOOKBACK
) -> List[LiquidityPool]:
    """
    Identify buy-side (BSL) and sell-side (SSL) liquidity pools.

    BSL: above swing highs, equal highs, prior session highs
    SSL: below swing lows, equal lows, prior session lows
    """
    tolerance = EQUAL_LEVEL_TOLERANCE_PCT
    swings    = find_swing_points(candles, lookback=swing_lookback)
    pools: List[LiquidityPool] = []

    swing_highs = sorted([s for s in swings if s.swing_type == "high"], key=lambda s: s.timestamp)
    swing_lows  = sorted([s for s in swings if s.swing_type == "low"],  key=lambda s: s.timestamp)

    # Mark all swing highs as BSL (stops cluster above obvious highs)
    for s in swing_highs:
        test_count = sum(
            1 for other in swing_highs
            if abs(other.price - s.price) / s.price <= tolerance and other != s
        ) + 1
        pools.append(LiquidityPool(
            symbol=candles[0].symbol,
            price=s.price,
            pool_type="BSL",
            timeframe=candles[0].timeframe,
            formed_at=s.timestamp,
            test_count=test_count,
        ))

    # Mark all swing lows as SSL
    for s in swing_lows:
        test_count = sum(
            1 for other in swing_lows
            if abs(other.price - s.price) / s.price <= tolerance and other != s
        ) + 1
        pools.append(LiquidityPool(
            symbol=candles[0].symbol,
            price=s.price,
            pool_type="SSL",
            timeframe=candles[0].timeframe,
            formed_at=s.timestamp,
            test_count=test_count,
        ))

    # Check which pools have been swept by subsequent price action
    last_prices = [c.close for c in candles[-10:]]
    for pool in pools:
        if pool.pool_type == "BSL":
            pool.is_swept = any(p > pool.price for p in last_prices)
        else:
            pool.is_swept = any(p < pool.price for p in last_prices)

    # Deduplicate pools at similar price levels (keep highest test_count)
    deduplicated = _deduplicate_pools(pools, tolerance)
    return deduplicated


# ─── PRIVATE HELPERS ─────────────────────────────────────────────────────────

_INTERVAL_SECONDS = {
    "1m": 60, "5m": 300, "15m": 900, "30m": 1800,
    "1h": 3600, "4h": 14400, "1d": 86400, "1w": 604800,
}


def _is_session_gap(c_a: Candle, c_b: Candle) -> bool:
    """
    Returns True if the time gap between two consecutive candles is much
    larger than the expected interval — meaning the candles span an
    overnight or weekend session boundary rather than continuous trading.

    Without this, Yahoo Finance market-hours-only data (US indices) produces
    phantom FVGs from the overnight gap between the last candle before close
    and the first candle at the next open.

    Thresholds:
      Intraday (1m–4h) : gap > 2.5× interval  (e.g. >2.5h on 1H chart)
      Daily            : gap > 4.5× interval  (handles 3-day weekends)
    """
    interval_secs = _INTERVAL_SECONDS.get(c_a.timeframe, 0)
    if interval_secs == 0:
        return False
    actual_gap = (c_b.timestamp - c_a.timestamp).total_seconds()
    multiplier = 4.5 if c_a.timeframe == "1d" else 2.5
    return actual_gap > interval_secs * multiplier

def _check_liquidity_grab(candles: List[Candle], ob_index: int, direction: str) -> bool:
    """
    Checks if the candles just before the OB swept a prior swing
    (i.e. there was a stop hunt immediately preceding the OB's impulse).
    """
    if ob_index < 3:
        return False
    lookback = candles[max(0, ob_index - 5): ob_index]
    swing_points = find_swing_points(candles[max(0, ob_index - 20): ob_index])
    if not swing_points:
        return False

    if direction == "bullish":
        recent_lows = [s.price for s in swing_points if s.swing_type == "low"]
        if not recent_lows:
            return False
        prior_low = min(recent_lows)
        return any(c.low < prior_low for c in lookback)
    else:
        recent_highs = [s.price for s in swing_points if s.swing_type == "high"]
        if not recent_highs:
            return False
        prior_high = max(recent_highs)
        return any(c.high > prior_high for c in lookback)


def _check_mitigation(ob: OrderBlock, subsequent_candles: List[Candle]) -> OrderBlock:
    """Mark OB as mitigated if price has returned to its zone."""
    for c in subsequent_candles:
        if ob.direction == "bullish" and c.low <= ob.high and c.low >= ob.low:
            ob.touch_count += 1
        elif ob.direction == "bearish" and c.high >= ob.low and c.high <= ob.high:
            ob.touch_count += 1
        # Fully mitigated: price closed through the OB
        if ob.direction == "bullish" and c.close < ob.low:
            ob.is_mitigated = True
        elif ob.direction == "bearish" and c.close > ob.high:
            ob.is_mitigated = True
    return ob


def _check_fvg_mitigation(fvg: FairValueGap, subsequent_candles: List[Candle]) -> FairValueGap:
    """
    Track mitigation, touch count, and partial fill depth.

    Touch: price enters the gap on a wick but candle does not close through.
    Partial fill: how deep into the gap price has traded (as a fraction of gap size).
    Mitigated: price closes fully through the gap.
    """
    if not subsequent_candles or fvg.size == 0:
        return fvg

    deepest_penetration = 0.0  # measured from the near edge of the gap

    for c in subsequent_candles:
        if fvg.direction == "bullish":
            # Full mitigation: close below the gap low
            if c.close < fvg.gap_low:
                fvg.is_mitigated = True
                fvg.partial_fill_pct = 1.0
                break
            # Entered the gap from above (price dipped into it)
            if c.low < fvg.gap_high:
                fvg.touch_count += 1
                penetration = fvg.gap_high - max(c.low, fvg.gap_low)
                deepest_penetration = max(deepest_penetration, penetration)
        else:  # bearish
            # Full mitigation: close above the gap high
            if c.close > fvg.gap_high:
                fvg.is_mitigated = True
                fvg.partial_fill_pct = 1.0
                break
            # Entered the gap from below
            if c.high > fvg.gap_low:
                fvg.touch_count += 1
                penetration = min(c.high, fvg.gap_high) - fvg.gap_low
                deepest_penetration = max(deepest_penetration, penetration)

    if not fvg.is_mitigated and fvg.size > 0:
        fvg.partial_fill_pct = min(deepest_penetration / fvg.size, 0.99)

    return fvg


def _find_bos_candle_indices(candles: List[Candle]) -> set:
    """Return set of candle indices where a BOS (break of structure) occurred."""
    if len(candles) < 10:
        return set()
    swings = find_swing_points(candles)
    highs = sorted([s for s in swings if s.swing_type == "high"], key=lambda s: s.timestamp)
    lows  = sorted([s for s in swings if s.swing_type == "low"],  key=lambda s: s.timestamp)
    bos_indices = set()
    ts_to_idx   = {c.timestamp: i for i, c in enumerate(candles)}

    for k in range(1, len(highs)):
        if highs[k].price > highs[k - 1].price:
            idx = ts_to_idx.get(highs[k].timestamp)
            if idx is not None:
                bos_indices.add(idx)
    for k in range(1, len(lows)):
        if lows[k].price < lows[k - 1].price:
            idx = ts_to_idx.get(lows[k].timestamp)
            if idx is not None:
                bos_indices.add(idx)
    return bos_indices


def _score_fvg(fvg: FairValueGap, atr: float) -> None:
    """
    Score FVG 0–10 and assign probability grade.

    Factors:
      Age          0–3  (fresh = same session = highest probability)
      Gap size     0–2  (optimal 0.5–2× ATR)
      Touch count  0–2  (virgin = untouched = best)
      Impulse body 0–2  (strong displacement = institutional)
      Context      0–2  (liquidity grab / BOS = smart money confirmation)

    Grade: A+ (9–10) | A (7–8) | B (5–6) | C (3–4) | SKIP (0–2)
    """
    score = 0

    # 1. Age
    age = fvg.candles_ago
    if age <= 5:
        score += 3
        fvg.age_label = "FRESH"
    elif age <= 20:
        score += 2
        fvg.age_label = "RECENT"
    elif age <= 50:
        score += 1
        fvg.age_label = "MATURE"
    else:
        score += 0
        fvg.age_label = "STALE"

    # 2. Gap size vs ATR
    if atr > 0:
        ratio = fvg.size / atr
        if 0.5 <= ratio <= 2.0:
            score += 2
        elif 0.2 <= ratio < 0.5 or 2.0 < ratio <= 3.0:
            score += 1

    # 3. Touch count (first test is always strongest)
    if fvg.touch_count == 0:
        score += 2
    elif fvg.touch_count == 1:
        score += 1

    # 4. Impulse body strength
    if atr > 0 and fvg.impulse_body_size > 0:
        body_ratio = fvg.impulse_body_size / atr
        if body_ratio >= 1.5:
            score += 2
        elif body_ratio >= 0.8:
            score += 1

    # 5. Formation context
    if fvg.preceded_by_liquidity_grab:
        score += 1
    if fvg.formed_after_bos:
        score += 1

    # 6. Penalties — fill consumption and excessive testing
    if fvg.partial_fill_pct >= 0.75:
        score -= 2   # Mostly consumed — institutional orders largely filled
    elif fvg.partial_fill_pct >= 0.50:
        score -= 1   # Over half filled — diminished
    if fvg.touch_count >= 6:
        score -= 1   # Heavily contested — no longer clean

    fvg.quality_score = max(0, min(score, 10))

    # Assign grade
    if fvg.quality_score >= 9:
        fvg.probability_grade = "A+"
    elif fvg.quality_score >= 7:
        fvg.probability_grade = "A"
    elif fvg.quality_score >= 5:
        fvg.probability_grade = "B"
    elif fvg.quality_score >= 3:
        fvg.probability_grade = "C"
    else:
        fvg.probability_grade = "SKIP"


def _deduplicate_pools(pools: List[LiquidityPool], tolerance: float) -> List[LiquidityPool]:
    """Merge pools within tolerance, keeping the strongest."""
    if not pools:
        return []
    result = []
    used = set()
    for i, p in enumerate(pools):
        if i in used:
            continue
        cluster = [p]
        for j, other in enumerate(pools):
            if j != i and j not in used and other.pool_type == p.pool_type:
                if abs(other.price - p.price) / p.price <= tolerance:
                    cluster.append(other)
                    used.add(j)
        best = max(cluster, key=lambda x: x.test_count)
        result.append(best)
        used.add(i)
    return result
