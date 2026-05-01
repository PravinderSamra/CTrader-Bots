"""
Session Analysis — Kill Zones, Asian Range, Session Bias

Tracks the three trading sessions (Asia, London, New York),
marks the Asian range for manipulation detection, identifies
kill zones, and computes session bias from the midnight open.
"""

from datetime import datetime, timezone, time
from typing import List, Optional
from data.models import Candle, SessionLevels


# EST offsets in hours from UTC
SESSION_HOURS_EST = {
    "asia_start":   20,  # 20:00 EST prior day
    "asia_end":      0,  # 00:00 EST
    "london_start":  2,
    "london_end":   11,
    "ny_start":      7,
    "ny_end":       16,
}

KILL_ZONE_EST = {
    "london":          (2,  5),
    "ny":              (7, 10),
    "silver_bullet_1": (3,  4),
    "silver_bullet_2": (10, 11),
    "silver_bullet_3": (14, 15),
}

EST_UTC_OFFSET = -5   # UTC-5 (no DST adjustment for simplicity)


def _to_est_hour(dt: datetime) -> int:
    """Convert UTC datetime to EST hour."""
    return (dt.hour + EST_UTC_OFFSET) % 24


def compute_session_levels(
    candles: List[Candle],
    date_str: Optional[str] = None,
) -> SessionLevels:
    """
    Compute session high/low/open levels from intraday candles.
    Expects 1h or 15m candles covering at least the prior 24 hours.
    """
    symbol = candles[0].symbol if candles else ""
    levels = SessionLevels(symbol=symbol, date=date_str or "")

    asia_candles   = []
    london_candles = []
    ny_candles     = []

    for c in candles:
        h = _to_est_hour(c.timestamp)

        # Asia: 20:00–00:00 EST (prior evening)
        if h >= 20 or h < 0:
            asia_candles.append(c)
        # London: 02:00–11:00 EST
        elif 2 <= h < 11:
            london_candles.append(c)
        # NY: 07:00–16:00 EST
        if 7 <= h < 16:
            ny_candles.append(c)

    if asia_candles:
        levels.asia_high = max(c.high for c in asia_candles)
        levels.asia_low  = min(c.low  for c in asia_candles)

    if london_candles:
        levels.london_high = max(c.high for c in london_candles)
        levels.london_low  = min(c.low  for c in london_candles)

    if ny_candles:
        levels.ny_open = ny_candles[0].open

    # Midnight open (00:00 EST) — ICT daily bias filter
    midnight_candles = [c for c in candles if _to_est_hour(c.timestamp) == 0]
    if midnight_candles:
        levels.midnight_open = midnight_candles[0].open

    # Prior day high/low (the full prior session: all candles before midnight)
    prior_candles = [c for c in candles if c.timestamp < candles[-1].timestamp]
    if prior_candles:
        levels.prior_day_high = max(c.high for c in prior_candles)
        levels.prior_day_low  = min(c.low  for c in prior_candles)

    # Session bias from midnight open
    if levels.midnight_open and candles:
        current_price = candles[-1].close
        levels.in_premium = current_price > levels.midnight_open

    # Did London sweep the Asian range?
    if levels.asia_high and levels.asia_low and london_candles:
        london_high = max(c.high for c in london_candles)
        london_low  = min(c.low  for c in london_candles)
        if london_high > levels.asia_high and london_low < levels.asia_low:
            levels.asia_swept = "both"  # Unusual — note it
        elif london_high > levels.asia_high:
            levels.asia_swept = "high"  # London swept ASH → watch for bearish reversal
        elif london_low < levels.asia_low:
            levels.asia_swept = "low"   # London swept ASL → watch for bullish reversal

    return levels


def current_kill_zone(dt: Optional[datetime] = None) -> Optional[str]:
    """
    Returns the name of the current kill zone, or None if outside all zones.
    """
    dt = dt or datetime.now(timezone.utc)
    h  = _to_est_hour(dt)
    m  = dt.minute
    h_frac = h + m / 60.0

    for name, (start, end) in KILL_ZONE_EST.items():
        if start <= h_frac < end:
            return name
    return None


def is_in_kill_zone(dt: Optional[datetime] = None) -> bool:
    return current_kill_zone(dt) is not None


def session_bias_note(levels: SessionLevels) -> str:
    """
    Generate a plain-English session bias summary.
    """
    parts = []

    if levels.in_premium is not None:
        if levels.in_premium:
            parts.append(
                f"Price is ABOVE midnight open ({levels.midnight_open:.5f}) → "
                "ICT bias: PREMIUM — favour SHORTS."
            )
        else:
            parts.append(
                f"Price is BELOW midnight open ({levels.midnight_open:.5f}) → "
                "ICT bias: DISCOUNT — favour LONGS."
            )

    if levels.asia_swept == "low":
        parts.append(
            f"London SWEPT Asian session low ({levels.asia_low:.5f}) → "
            "Manipulation phase likely complete. Watch for BULLISH reversal (long setups)."
        )
    elif levels.asia_swept == "high":
        parts.append(
            f"London SWEPT Asian session high ({levels.asia_high:.5f}) → "
            "Manipulation phase likely complete. Watch for BEARISH reversal (short setups)."
        )
    elif levels.asia_high and levels.asia_low:
        parts.append(
            f"Asian range intact: {levels.asia_low:.5f} – {levels.asia_high:.5f}. "
            "Watch for London to sweep one side before the true move begins."
        )

    kz = current_kill_zone()
    if kz:
        parts.append(f"Currently in {kz.replace('_', ' ').upper()} KILL ZONE — elevated setup probability.")
    else:
        parts.append("Outside kill zones — wait for London (02:00) or NY (07:00) EST.")

    return "\n".join(parts)
