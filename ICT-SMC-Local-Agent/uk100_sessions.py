"""
Europe/London session map for the UK100 index — built around the 15-minute
Opening Range Breakout (ORB) at London cash open (08:00).

NOT in analysis/ — this is UK100-specific and does not participate in the
Local/Remote-Agent sync rule in CLAUDE.md (that rule covers the shared
XAUUSD structure engine only).

Sessions (Europe/London, DST-aware via zoneinfo):
  PRE_OPEN     : 06:00 – 08:00  (pre-market positioning, overnight range set)
  OPENING_HOUR : 08:00 – 09:00  (ORB forms 08:00–08:15, first break/retest)
  MORNING      : 09:00 – 13:00  (EZ data 09:30, trend continuation window)
  PRE_US       : 13:00 – 14:30  (US data 13:30, morning move often complete)
  US_OVERLAP   : 14:30 – 16:30  (US cash open 14:30 can reverse the day)
  POST_CLOSE   : everything else (UK100 cash close 16:30)
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from data.models import Candle

_LDN = ZoneInfo("Europe/London")

_SESSIONS = {
    "PRE_OPEN":     ((6, 0),  (8, 0)),
    "OPENING_HOUR": ((8, 0),  (9, 0)),
    "MORNING":      ((9, 0),  (13, 0)),
    "PRE_US":       ((13, 0), (14, 30)),
    "US_OVERLAP":   ((14, 30), (16, 30)),
}


def _now_london() -> datetime:
    return datetime.now(tz=_LDN)


def _in_range(now_h: int, now_m: int, start: tuple, end: tuple) -> bool:
    """True if (now_h, now_m) falls within [start, end), handling midnight crossing."""
    s_h, s_m = start
    e_h, e_m = end
    now_mins = now_h * 60 + now_m
    start_mins = s_h * 60 + s_m
    end_mins = e_h * 60 + e_m
    if start_mins <= end_mins:
        return start_mins <= now_mins < end_mins
    return now_mins >= start_mins or now_mins < end_mins


def current_session(reference: datetime | None = None) -> str:
    """Return the current UK100 session name, or POST_CLOSE outside all of them."""
    ld = (reference or _now_london()).astimezone(_LDN)
    h, m = ld.hour, ld.minute
    for name, (start, end) in _SESSIONS.items():
        if _in_range(h, m, start, end):
            return name
    return "POST_CLOSE"


def cash_open_today(reference: datetime | None = None) -> datetime:
    """08:00 London on the date of `reference` (default: now), tz-aware."""
    ld = (reference or _now_london()).astimezone(_LDN)
    return ld.replace(hour=8, minute=0, second=0, microsecond=0)


def orb_mode(reference: datetime | None = None) -> str:
    """PRE_OPEN / ORB_FORMING / POST_ORB / CLOSED — mirrors the TS orbContext.mode
    computation in fetch-uk100-data.ts exactly, so the mechanical hourly snapshot
    and the skill's live read never disagree."""
    ld = (reference or _now_london()).astimezone(_LDN)
    hh = ld.hour + ld.minute / 60
    if hh < 8:
        return "PRE_OPEN"
    if hh < 8.25:
        return "ORB_FORMING"
    if hh < 16.5:
        return "POST_ORB"
    return "CLOSED"


def orb_window(
    m5_candles: list[Candle],
    orb_m5_candles: list[Candle] | None = None,
    overnight_h1_candles: list[Candle] | None = None,
    reference: datetime | None = None,
) -> dict:
    """
    m5_candles: the general rolling M5 window (used only for post-ORB break
    detection — it reaches back ~500 minutes from now, which always covers
    08:00-now on a same-day run).

    orb_m5_candles / overnight_h1_candles: dedicated exact-timestamp fetches
    for the 08:00-08:15 ORB window and the 22:00(prev)-08:00 overnight window
    respectively. Pass these when available (ctrader_http_fetch.py --instrument
    uk100 always supplies them) — the general m5 window alone cannot reach
    back to 22:00 the previous day once it's later than ~mid-morning, and
    silently truncates at cTrader's 100-bar cap. Falls back to slicing
    m5_candles for both when the dedicated series are absent (e.g. unit tests).

    Returns cash-open time, overnight high/low, ORB high/low, and
    orb_broken_direction (UP/DOWN/None) — the direction of the first
    post-08:15 M5 candle (from m5_candles) to close outside the ORB range.
    """
    if not m5_candles and not orb_m5_candles and not overnight_h1_candles:
        return {}

    cash_open = cash_open_today(reference)
    overnight_start = cash_open - timedelta(hours=10)  # 22:00 the previous day
    orb_end = cash_open + timedelta(minutes=15)

    if overnight_h1_candles is not None:
        overnight = overnight_h1_candles
    else:
        overnight = [c for c in m5_candles if overnight_start <= c.timestamp.astimezone(_LDN) < cash_open]

    if orb_m5_candles is not None:
        orb = orb_m5_candles
    else:
        orb = [c for c in m5_candles if cash_open <= c.timestamp.astimezone(_LDN) < orb_end]

    post_orb = [c for c in m5_candles if c.timestamp.astimezone(_LDN) >= orb_end]

    orb_high = max((c.high for c in orb), default=None)
    orb_low = min((c.low for c in orb), default=None)

    broken = None
    if orb_high is not None and orb_low is not None:
        for c in sorted(post_orb, key=lambda c: c.timestamp):
            if c.close > orb_high:
                broken = "UP"
                break
            if c.close < orb_low:
                broken = "DOWN"
                break

    return {
        "mode": orb_mode(reference),
        "cash_open_london": cash_open.strftime("%H:%M %Z"),
        "overnight_high": max((c.high for c in overnight), default=None),
        "overnight_low": min((c.low for c in overnight), default=None),
        "orb_high": orb_high,
        "orb_low": orb_low,
        "orb_broken_direction": broken,
    }


def prior_day_levels(d1_candles: list[Candle]) -> dict:
    """Previous COMPLETED daily candle's high/low/close (d1_candles[-1] is
    treated as today's possibly-partial candle, same convention as
    skill_adapter._reference_levels)."""
    if not d1_candles or len(d1_candles) < 2:
        return {}
    prev = d1_candles[-2]
    return {
        "prior_day_high": prev.high,
        "prior_day_low": prev.low,
        "prior_close": prev.close,
    }


def adr14(d1_candles: list[Candle]) -> float | None:
    """14-day average true range (simplified: high-low, no gap component —
    consistent with the TS side's adr14 in fetch-uk100-data.ts)."""
    completed = d1_candles[:-1] if len(d1_candles) > 1 else d1_candles
    sample = completed[-14:]
    if not sample:
        return None
    return round(sum(c.high - c.low for c in sample) / len(sample), 1)


def session_bias_note(orb: dict, prior: dict, current_price: float | None) -> list[str]:
    """Session-specific bias notes for the brief: gap direction, ORB break
    status, and current session/time-of-day context."""
    notes: list[str] = []
    sess = current_session()
    notes.append(f"Current session: {sess} ({_now_london().strftime('%H:%M %Z')})")

    prior_close = prior.get("prior_close")
    if prior_close is not None and current_price is not None:
        gap = current_price - prior_close
        gap_pct = (gap / prior_close) * 100 if prior_close else 0
        if abs(gap_pct) >= 0.1:
            direction = "UP" if gap > 0 else "DOWN"
            notes.append(f"Gap {direction} {gap:+.1f}pts ({gap_pct:+.2f}%) vs prior close {prior_close:.1f}.")

    orb_high, orb_low = orb.get("orb_high"), orb.get("orb_low")
    broken = orb.get("orb_broken_direction")
    if orb_high is not None and orb_low is not None:
        if broken:
            notes.append(f"ORB ({orb_low:.1f}–{orb_high:.1f}) has broken {broken}.")
        else:
            notes.append(f"ORB ({orb_low:.1f}–{orb_high:.1f}) intact — no break yet.")
    elif sess in ("PRE_OPEN",):
        notes.append("ORB not yet formed — cash open at 08:00 London.")

    overnight_high, overnight_low = orb.get("overnight_high"), orb.get("overnight_low")
    if overnight_high is not None and overnight_low is not None and current_price is not None:
        if current_price > overnight_high:
            notes.append("Price trading ABOVE the overnight range — overnight high already swept.")
        elif current_price < overnight_low:
            notes.append("Price trading BELOW the overnight range — overnight low already swept.")
        else:
            notes.append("Price still INSIDE the overnight range — no sweep yet.")

    return notes
