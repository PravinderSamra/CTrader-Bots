"""
Session & Kill Zone Detection — ICT Methodology

Sessions (all times Eastern / New York):
  Sydney/Asia   : 20:00 – 00:00 ET (prior day) / 00:00 – 05:00 ET
  London        : 02:00 – 11:00 ET
  New York      : 07:00 – 16:00 ET
  NY Close      : 17:00 ET (trading day boundary for ICT)

Kill Zones (highest-probability entry windows):
  Asia KZ       : 20:00 – 00:00 ET
  London KZ     : 02:00 – 05:00 ET
  NY KZ         : 07:00 – 10:00 ET
  Silver Bullet : 09:50 – 10:10 ET (and 13:50–14:10 ET)

DST handling uses zoneinfo — no manual offset management needed.
"""

from datetime import datetime, timezone, time
from zoneinfo import ZoneInfo

_NY = ZoneInfo("America/New_York")

# Session boundaries in ET (hour, minute)
_SESSIONS = {
    "ASIA":   ((20, 0), (5, 0)),    # 20:00 prior day → 05:00
    "LONDON": ((2, 0),  (11, 0)),
    "NEW YORK": ((7, 0), (16, 0)),
}

_KILL_ZONES = {
    "ASIA KZ":          ((20, 0), (0, 0)),
    "LONDON KZ":        ((2, 0),  (5, 0)),
    "NY KZ":            ((7, 0),  (10, 0)),
    "SILVER BULLET 1":  ((9, 50), (10, 10)),
    "SILVER BULLET 2":  ((13, 50),(14, 10)),
    "LONDON CLOSE KZ":  ((11, 0), (12, 0)),
}

_SESSION_LABELS = {
    "ASIA":      "ASIA SESSION (20:00–05:00 ET)",
    "LONDON":    "LONDON SESSION (02:00–11:00 ET)",
    "NEW YORK":  "NEW YORK SESSION (07:00–16:00 ET)",
}


def _now_et() -> datetime:
    return datetime.now(tz=_NY)


def _in_range(now_h: int, now_m: int, start: tuple, end: tuple) -> bool:
    """True if (now_h, now_m) falls within [start, end), handling midnight crossing."""
    s_h, s_m = start
    e_h, e_m = end
    now_mins  = now_h * 60 + now_m
    start_mins = s_h * 60 + s_m
    end_mins   = e_h * 60 + e_m

    if start_mins <= end_mins:
        return start_mins <= now_mins < end_mins
    else:
        # Crosses midnight: e.g. 20:00 → 05:00
        return now_mins >= start_mins or now_mins < end_mins


def current_session() -> str:
    """Return the current primary session name (ASIA / LONDON / NEW YORK / OFF-HOURS)."""
    et = _now_et()
    h, m = et.hour, et.minute
    for name, (start, end) in _SESSIONS.items():
        if _in_range(h, m, start, end):
            return name
    return "OFF-HOURS"


def active_kill_zone() -> str | None:
    """Return the active kill zone name, or None if outside any kill zone."""
    et = _now_et()
    h, m = et.hour, et.minute
    for name, (start, end) in _KILL_ZONES.items():
        if _in_range(h, m, start, end):
            return name
    return None


def session_display_label() -> str:
    """Human-readable session label for report headers."""
    sess = current_session()
    return _SESSION_LABELS.get(sess, f"{sess} SESSION")


def minutes_until_kill_zone_closes() -> int | None:
    """Minutes remaining in the active kill zone, or None if not in one."""
    kz = active_kill_zone()
    if kz is None:
        return None
    _, (_, end) = list(_KILL_ZONES.items())[[k for k in _KILL_ZONES].index(kz)]
    et = _now_et()
    end_today = et.replace(hour=end[0], minute=end[1], second=0, microsecond=0)
    diff = (end_today - et).total_seconds()
    if diff < 0:
        return None
    return int(diff // 60)


def session_bias_note(
    asian_swept: str | None,
    midnight_open: float | None,
    current_price: float,
) -> list[str]:
    """
    Returns a list of session-specific bias notes:
      - Price vs midnight open → discount/premium bias
      - Asian session manipulation (swept high or low)
      - Kill zone status
    """
    notes = []
    kz = active_kill_zone()

    if midnight_open is not None:
        if current_price < midnight_open:
            notes.append(
                f"Price is BELOW midnight open ({midnight_open:.5f}) → "
                "ICT bias: DISCOUNT — favour LONGS."
            )
        else:
            notes.append(
                f"Price is ABOVE midnight open ({midnight_open:.5f}) → "
                "ICT bias: PREMIUM — favour SHORTS."
            )

    if asian_swept == "LOW":
        notes.append(
            f"London SWEPT Asian session low → "
            "Manipulation phase likely complete. Watch for BULLISH reversal (long setups)."
        )
    elif asian_swept == "HIGH":
        notes.append(
            f"London SWEPT Asian session high → "
            "Manipulation phase likely complete. Watch for BEARISH reversal (short setups)."
        )
    elif asian_swept is None and current_session() == "NEW YORK":
        notes.append(
            "Asian range intact. Watch for NY to sweep one side before the true move begins."
        )

    if kz:
        notes.append(f"Currently in {kz} — elevated setup probability.")

    return notes
