"""
Session Analysis — Kill Zones, Asian Range, Session Bias

Tracks the three trading sessions (Asia, London, New York),
marks the Asian range for manipulation detection, identifies
kill zones, and computes session bias from the midnight open.
"""

from datetime import datetime, timezone, time, timedelta, date as date_type
from typing import List, Optional
from data.models import Candle, SessionLevels

try:
    from zoneinfo import ZoneInfo
    _EASTERN = ZoneInfo("America/New_York")
except ImportError:
    _EASTERN = None  # Python < 3.9 fallback


# US Eastern session boundaries (applies to both EST and EDT — same clock times)
KILL_ZONE_ET = {
    "london":          (2,  5),
    "ny":              (7, 10),
    "silver_bullet_1": (3,  4),
    "silver_bullet_2": (10, 11),
    "silver_bullet_3": (14, 15),
}

SESSION_RANGES_ET = {
    "asia":    ((20, 0), (0, 0)),   # 20:00–00:00 ET
    "london":  ((2,  0), (11, 0)),  # 02:00–11:00 ET
    "ny":      ((7,  0), (16, 0)),  # 07:00–16:00 ET
}


def _to_et_hour(dt: datetime) -> int:
    """Convert UTC datetime to US Eastern hour, respecting DST automatically."""
    if _EASTERN is not None:
        return dt.astimezone(_EASTERN).hour
    # Fallback: approximate EDT Apr–Nov (UTC-4), EST Nov–Mar (UTC-5)
    month = dt.month
    offset = -4 if 3 < month < 11 else -5
    return (dt.hour + offset) % 24


def _to_et_hour_frac(dt: datetime) -> float:
    """Return ET hour as a float including minutes (e.g. 9.5 = 09:30)."""
    if _EASTERN is not None:
        et = dt.astimezone(_EASTERN)
        return et.hour + et.minute / 60.0
    month = dt.month
    offset = -4 if 3 < month < 11 else -5
    return (dt.hour + offset) % 24 + dt.minute / 60.0


def _trading_day(dt: datetime) -> date_type:
    """
    Return the forex trading day this timestamp belongs to.
    Forex days run 17:00 ET → 17:00 ET (NY close convention).
    A candle at 18:00 ET Monday belongs to Tuesday's trading day.
    """
    if _EASTERN is not None:
        et = dt.astimezone(_EASTERN)
    else:
        month = dt.month
        offset = -4 if 3 < month < 11 else -5
        et = dt.replace(tzinfo=None).replace(hour=(dt.hour + offset) % 24)

    if et.hour >= 17:
        return (et + timedelta(days=1)).date()
    return et.date()


def compute_session_levels(
    candles: List[Candle],
    date_str: Optional[str] = None,
) -> SessionLevels:
    """
    Compute session high/low/open levels from intraday candles.

    Uses the NY close (17:00 ET) daily boundary — the standard forex/CFD
    convention used by Pepperstone, IC Markets, and all major retail brokers.
    A trading day runs 17:00 ET → 17:00 ET, so the Asian session
    (17:00–00:00 ET) belongs to the NEXT calendar day's trading session.

    Expects 1h or 15m candles covering at least the prior 48 hours.
    """
    if not candles:
        return SessionLevels(symbol="", date=date_str or "")

    symbol   = candles[0].symbol
    now_utc  = candles[-1].timestamp
    today_td = _trading_day(now_utc)
    prev_td  = today_td - timedelta(days=1)

    levels = SessionLevels(symbol=symbol, date=date_str or str(today_td))

    # Bucket every candle by its trading day and ET hour
    today_candles = [c for c in candles if _trading_day(c.timestamp) == today_td]
    prior_candles = [c for c in candles if _trading_day(c.timestamp) == prev_td]

    # Prior day high / low  ← NOW CORRECTLY SCOPED TO YESTERDAY ONLY
    if prior_candles:
        levels.prior_day_high = max(c.high for c in prior_candles)
        levels.prior_day_low  = min(c.low  for c in prior_candles)

    # Today's session sub-ranges (scoped to today's trading day)
    asia_candles   = [c for c in today_candles if _to_et_hour(c.timestamp) >= 17
                      or _to_et_hour(c.timestamp) < 2]
    london_candles = [c for c in today_candles if 2 <= _to_et_hour(c.timestamp) < 11]
    ny_candles     = [c for c in today_candles if 7 <= _to_et_hour(c.timestamp) < 17]

    if asia_candles:
        levels.asia_high = max(c.high for c in asia_candles)
        levels.asia_low  = min(c.low  for c in asia_candles)

    if london_candles:
        levels.london_high = max(c.high for c in london_candles)
        levels.london_low  = min(c.low  for c in london_candles)

    if ny_candles:
        levels.ny_open = ny_candles[0].open

    # Midnight open (00:00 ET) — ICT daily bias filter, scoped to today
    midnight_candles = [c for c in today_candles if _to_et_hour(c.timestamp) == 0]
    if midnight_candles:
        levels.midnight_open = midnight_candles[0].open

    # Session bias from midnight open
    if levels.midnight_open and today_candles:
        levels.in_premium = today_candles[-1].close > levels.midnight_open

    # Did London sweep today's Asian range?
    if levels.asia_high and levels.asia_low and london_candles:
        london_high = max(c.high for c in london_candles)
        london_low  = min(c.low  for c in london_candles)
        if london_high > levels.asia_high and london_low < levels.asia_low:
            levels.asia_swept = "both"
        elif london_high > levels.asia_high:
            levels.asia_swept = "high"
        elif london_low < levels.asia_low:
            levels.asia_swept = "low"

    return levels


def current_session(dt: Optional[datetime] = None) -> Optional[str]:
    """Returns the current trading session name: 'asia', 'london', 'ny', or None."""
    dt = dt or datetime.now(timezone.utc)
    h = _to_et_hour(dt)
    if h >= 20 or h == 0:
        return "asia"
    if 2 <= h < 11:
        return "london"
    if 7 <= h < 16:
        return "ny"
    return None


def current_kill_zone(dt: Optional[datetime] = None) -> Optional[str]:
    """
    Returns the name of the current kill zone, or None if outside all zones.
    """
    dt = dt or datetime.now(timezone.utc)
    h_frac = _to_et_hour_frac(dt)

    for name, (start, end) in KILL_ZONE_ET.items():
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

    now = datetime.now(timezone.utc)
    kz  = current_kill_zone(now)
    ses = current_session(now)

    if kz:
        parts.append(f"Currently in {kz.replace('_', ' ').upper()} KILL ZONE — elevated setup probability.")
    elif ses == "london":
        parts.append("London session active (02:00–11:00 ET). Kill zone passed — watch for continuation or reversal setups.")
    elif ses == "ny":
        parts.append("New York session active (07:00–16:00 ET). Outside kill zone — monitor for NY kill zone (07:00–10:00 ET) setups.")
    elif ses == "asia":
        parts.append("Asian session active (20:00–00:00 ET). Low volatility expected — note the range for London manipulation targets.")
    else:
        parts.append("Inter-session period. Next session: London opens 02:00 ET, NY opens 07:00 ET.")

    return "\n".join(parts)
