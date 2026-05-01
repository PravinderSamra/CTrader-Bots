"""
Volume Profile from OHLCV Data

Approximates a volume profile by distributing each candle's volume
across its high-low range. This is NOT footprint-level accuracy —
it is an OHLCV approximation.

The output note makes this explicitly clear so the trader knows
when to rely on this vs when to check a proper volume profile tool.
"""

import statistics
from typing import List, Tuple
from data.models import Candle, VolumeProfile, VolumeProfileLevel
from config import VOLUME_PROFILE_BINS


def build_volume_profile(
    candles: List[Candle],
    bins: int = VOLUME_PROFILE_BINS,
) -> VolumeProfile:
    """
    Build an approximate volume profile from OHLCV candles.

    Distribution method: each candle's volume is distributed uniformly
    across its high-low range (simplified). More accurate methods
    (e.g. Gaussian around midpoint) available but add minimal value
    without tick data.
    """
    if not candles:
        return VolumeProfile(
            symbol="",
            timeframe="",
            period_start=None,
            period_end=None,
        )

    symbol    = candles[0].symbol
    timeframe = candles[0].timeframe
    low_all   = min(c.low  for c in candles)
    high_all  = max(c.high for c in candles)

    if high_all == low_all:
        high_all += 0.0001  # Avoid division by zero

    bin_size  = (high_all - low_all) / bins
    bin_vol   = [0.0] * bins

    for candle in candles:
        candle_range = candle.high - candle.low
        if candle_range == 0:
            # Point candle: all volume in one bin
            idx = min(int((candle.close - low_all) / bin_size), bins - 1)
            bin_vol[idx] += candle.volume
            continue

        # Distribute volume across all bins that fall within this candle's range
        low_bin  = int((candle.low  - low_all) / bin_size)
        high_bin = int((candle.high - low_all) / bin_size)
        high_bin = min(high_bin, bins - 1)
        low_bin  = max(low_bin, 0)

        span = high_bin - low_bin + 1
        vol_per_bin = candle.volume / span

        for b in range(low_bin, high_bin + 1):
            bin_vol[b] += vol_per_bin

    # Build level objects
    total_vol = sum(bin_vol)
    levels    = []
    poc_idx   = bin_vol.index(max(bin_vol))

    for i, vol in enumerate(bin_vol):
        price = low_all + (i + 0.5) * bin_size
        levels.append(VolumeProfileLevel(price=round(price, 6), volume=vol))

    # Mark POC
    levels[poc_idx].is_poc = True
    poc_price = levels[poc_idx].price

    # Mark Value Area (70% of total volume expanding from POC)
    va_vol_target = total_vol * 0.70
    va_vol = bin_vol[poc_idx]
    lower_idx = poc_idx - 1
    upper_idx = poc_idx + 1

    while va_vol < va_vol_target:
        expand_down = (lower_idx >= 0 and bin_vol[lower_idx] > 0)
        expand_up   = (upper_idx < bins and bin_vol[upper_idx] > 0)

        if not expand_down and not expand_up:
            break

        if expand_down and expand_up:
            if bin_vol[lower_idx] >= bin_vol[upper_idx]:
                va_vol += bin_vol[lower_idx]; lower_idx -= 1
            else:
                va_vol += bin_vol[upper_idx]; upper_idx += 1
        elif expand_down:
            va_vol += bin_vol[lower_idx]; lower_idx -= 1
        else:
            va_vol += bin_vol[upper_idx]; upper_idx += 1

    val_idx = max(lower_idx + 1, 0)
    vah_idx = min(upper_idx - 1, bins - 1)

    levels[val_idx].is_val = True
    levels[vah_idx].is_vah = True
    val_price = levels[val_idx].price
    vah_price = levels[vah_idx].price

    # Mark HVN and LVN (relative to mean volume per bin)
    mean_vol = statistics.mean(v for v in bin_vol if v > 0) if any(v > 0 for v in bin_vol) else 0
    for i, level in enumerate(levels):
        if level.volume > mean_vol * 1.5:
            level.is_hvn = True
        elif level.volume < mean_vol * 0.4 and level.volume > 0:
            level.is_lvn = True

    profile = VolumeProfile(
        symbol=symbol,
        timeframe=timeframe,
        period_start=candles[0].timestamp,
        period_end=candles[-1].timestamp,
        levels=levels,
        poc=poc_price,
        vah=vah_price,
        val=val_price,
        total_volume=total_vol,
        data_note=(
            "⚠️  APPROXIMATED from OHLCV — volume distributed uniformly across "
            "each candle's range. For precise volume profile, use Sierra Chart "
            "Numbers Bars, ATAS, or NinjaTrader Volumetric Bars."
        ),
    )
    return profile


def find_nearest_lvn(profile: VolumeProfile, price: float) -> Tuple[float, float]:
    """Return (price, distance) of the nearest LVN to a given price."""
    lvns = [(l.price, abs(l.price - price)) for l in profile.levels if l.is_lvn]
    if not lvns:
        return (0.0, float("inf"))
    return min(lvns, key=lambda x: x[1])


def find_nearest_hvn(profile: VolumeProfile, price: float) -> Tuple[float, float]:
    """Return (price, distance) of the nearest HVN above or below a given price."""
    hvns = [(l.price, abs(l.price - price)) for l in profile.levels if l.is_hvn]
    if not hvns:
        return (0.0, float("inf"))
    return min(hvns, key=lambda x: x[1])


def is_price_at_lvn(profile: VolumeProfile, price: float, tolerance_pct: float = 0.002) -> bool:
    """Check if a price is at or near a Low Volume Node."""
    for level in profile.levels:
        if level.is_lvn and abs(level.price - price) / price <= tolerance_pct:
            return True
    return False
