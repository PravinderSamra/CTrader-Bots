"""
/Trend-Continuation-Agent — UK time / DST handling

Spec §10: "The agent must always display times in UK local time, correctly
applying DST." `zoneinfo.ZoneInfo("Europe/London")` applies BST/GMT
automatically — no manual DST-window math required.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from config import UK_TZ

UK_ZONE = ZoneInfo(UK_TZ)


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def to_uk(dt_utc: datetime) -> datetime:
    if dt_utc.tzinfo is None:
        dt_utc = dt_utc.replace(tzinfo=timezone.utc)
    return dt_utc.astimezone(UK_ZONE)


def format_uk_full(dt_utc: datetime) -> str:
    """e.g. '14:32 BST (Wed 11 Jun 2025)' — used in the scan header (spec §9)."""
    uk = to_uk(dt_utc)
    return f"{uk.strftime('%H:%M')} {uk.tzname()} ({uk.strftime('%a %d %b %Y')})"


def format_uk_short(dt_utc: datetime) -> str:
    """e.g. '15:00 BST' — used for rescan recommendations (spec §10)."""
    uk = to_uk(dt_utc)
    return f"{uk.strftime('%H:%M')} {uk.tzname()}"


# ── Market sessions (spec §10) ───────────────────────────────────────────────
# (name, start_hour_uk, end_hour_uk, commentary). end_hour > 24 wraps past midnight.
SESSIONS: list[tuple[str, int, int, str]] = [
    ("Pre-London", 6, 8, "Low liquidity. Flag if trade card fires in this window — wider spreads."),
    ("London Open", 8, 10, "High volatility, strong continuation moves. Best session for index trends."),
    ("London Mid", 10, 14, "Steadier trending. Strong setups here are high quality."),
    ("NY Overlap", 14, 17, "Maximum liquidity. Trend continuation most reliable."),
    ("NY Only", 17, 21, "US indices relevant. UK100/GER40 lower volume after 17:30."),
    ("After Hours", 21, 30, "Flag explicitly. Do not recommend entry during this window."),  # 21:00-06:00
]


def current_session(dt_utc: datetime) -> tuple[str, str]:
    """Returns (session_name, commentary_note) for the UK-local hour of `dt_utc`."""
    hour = to_uk(dt_utc).hour
    for name, start, end, note in SESSIONS:
        if end <= 24:
            if start <= hour < end:
                return name, note
        else:
            if hour >= start or hour < (end - 24):
                return name, note
    return "After Hours", SESSIONS[-1][3]


# ── Rescan time calculation (spec §10) ───────────────────────────────────────
def compute_rescan_time(dt_utc: datetime) -> datetime:
    """
    Recommended rescan time = next 1H candle close + 1 hour (2 candles
    forward). If the next 1H close is within 10 minutes, use the *following*
    close as the base instead (i.e. push out one extra hour).
    """
    next_close = dt_utc.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
    if (next_close - dt_utc) <= timedelta(minutes=10):
        next_close += timedelta(hours=1)
    return next_close + timedelta(hours=1)
