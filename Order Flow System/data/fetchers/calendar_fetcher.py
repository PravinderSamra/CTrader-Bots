"""
Economic Calendar Fetcher — ForexFactory JSON Feed

Source: nfs.faireconomy.media (unofficial ForexFactory community endpoint)
Free, no API key required. Updated weekly.

Returns high/medium/low impact events for the current and next week.
Critical for day trading: always check for upcoming high-impact events
before entering a position — news can instantly invalidate a setup.

Impact levels:
  High   — NFP, FOMC, CPI, GDP, PMI, central bank rate decisions
  Medium — Trade balance, retail sales, housing data
  Low    — Minor economic releases

Currency mapping (which assets are affected):
  USD → all USD pairs, Gold, Oil, all indices
  EUR → EUR/USD, EUR/GBP, DAX
  GBP → GBP/USD, EUR/GBP
  JPY → USD/JPY, EUR/JPY
  etc.
"""

import urllib.request
import json
from datetime import datetime, timezone, timedelta
from typing import List, Optional, Dict
from zoneinfo import ZoneInfo

BASE_URL_THIS_WEEK = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
BASE_URL_NEXT_WEEK = "https://nfs.faireconomy.media/ff_calendar_nextweek.json"

# Map event currencies to the symbols they affect
CURRENCY_TO_SYMBOLS: Dict[str, List[str]] = {
    "USD": ["EURUSD", "GBPUSD", "USDJPY", "USDCHF", "AUDUSD", "USDCAD",
            "XAUUSD", "USOIL", "UKOIL", "SPX", "NDX", "DOW"],
    "EUR": ["EURUSD", "EURGBP", "EURJPY", "NDX"],  # DAX also USD-correlated
    "GBP": ["GBPUSD", "EURGBP", "GBPJPY"],
    "JPY": ["USDJPY", "EURJPY", "GBPJPY"],
    "CHF": ["USDCHF", "EURCHF"],
    "AUD": ["AUDUSD", "AUDNZD"],
    "CAD": ["USDCAD", "CADJPY"],
    "NZD": ["NZDUSD", "AUDNZD"],
    "CNY": ["AUDUSD", "USOIL", "XAUUSD"],  # Chinese data moves commodities
    "ALL": ["EURUSD", "GBPUSD", "USDJPY", "XAUUSD", "USOIL", "SPX", "NDX"],
}

ET_ZONE = ZoneInfo("America/New_York")


def _fetch_raw(url: str) -> list:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read())


def _parse_event(raw: dict) -> Optional[dict]:
    """Parse a raw ForexFactory event dict into a clean structure."""
    try:
        title    = raw.get("title", "")
        country  = raw.get("country", "").upper()
        impact   = raw.get("impact", "Low")
        forecast = raw.get("forecast", "")
        previous = raw.get("previous", "")

        # Parse the date string (FF uses ET timezone offset)
        date_str = raw.get("date", "")
        if not date_str:
            return None
        dt = datetime.fromisoformat(date_str).astimezone(timezone.utc)

        # Normalise impact level
        impact_map = {
            "High":    "HIGH",
            "Medium":  "MEDIUM",
            "Low":     "LOW",
            "Holiday": "HOLIDAY",
            "Non-Economic": "LOW",
        }
        impact_norm = impact_map.get(impact, "LOW")

        return {
            "title":    title,
            "currency": country,
            "impact":   impact_norm,
            "time_utc": dt.isoformat(),
            "time_et":  dt.astimezone(ET_ZONE).strftime("%H:%M ET"),
            "forecast": forecast,
            "previous": previous,
            "affects":  CURRENCY_TO_SYMBOLS.get(country, []),
            "timestamp": dt,
        }
    except Exception:
        return None


def fetch_events(include_next_week: bool = False) -> List[dict]:
    """
    Fetch this week's (and optionally next week's) economic events.
    Returns list of parsed event dicts, sorted by time ascending.
    """
    events = []
    try:
        raw = _fetch_raw(BASE_URL_THIS_WEEK)
        events.extend(e for e in (_parse_event(r) for r in raw) if e)
    except Exception:
        pass

    if include_next_week:
        try:
            raw = _fetch_raw(BASE_URL_NEXT_WEEK)
            events.extend(e for e in (_parse_event(r) for r in raw) if e)
        except Exception:
            pass

    events.sort(key=lambda e: e["timestamp"])
    return events


def get_events_today(impact_filter: Optional[str] = None) -> List[dict]:
    """
    Return today's events, optionally filtered by impact level.
    impact_filter: 'HIGH', 'MEDIUM', 'LOW' or None for all.
    """
    now = datetime.now(timezone.utc)
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    today_end   = today_start + timedelta(days=1)

    events = fetch_events()
    today  = [e for e in events if today_start <= e["timestamp"] < today_end]

    if impact_filter:
        today = [e for e in today if e["impact"] == impact_filter.upper()]

    return today


def get_upcoming_events(hours_ahead: int = 4, impact_filter: Optional[str] = None) -> List[dict]:
    """
    Return events in the next `hours_ahead` hours.
    Useful for checking if a trade entry is about to run into a news event.
    """
    now      = datetime.now(timezone.utc)
    cutoff   = now + timedelta(hours=hours_ahead)
    events   = fetch_events()
    upcoming = [e for e in events if now <= e["timestamp"] <= cutoff]

    if impact_filter:
        upcoming = [e for e in upcoming if e["impact"] == impact_filter.upper()]

    return upcoming


def is_news_blackout(
    symbol: str,
    minutes_before: int = 30,
    minutes_after: int  = 15,
    min_impact: str     = "HIGH",
) -> dict:
    """
    Check whether the current time is inside a news blackout window for a symbol.

    Returns:
      {"in_blackout": bool, "reason": str, "event": dict or None}

    Use before entering any intraday trade. If in_blackout is True, stand aside.
    Default: 30 min before / 15 min after any HIGH-impact event that affects this symbol.
    """
    now    = datetime.now(timezone.utc)
    sym_up = symbol.upper()

    # Collect all events that affect this symbol
    events = fetch_events()
    impact_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1, "HOLIDAY": 0}
    min_level    = impact_order.get(min_impact.upper(), 3)

    relevant = [
        e for e in events
        if (sym_up in [s.upper() for s in e["affects"]] or sym_up in e["currency"].upper())
        and impact_order.get(e["impact"], 0) >= min_level
    ]

    for event in relevant:
        event_time  = event["timestamp"]
        window_open = event_time - timedelta(minutes=minutes_before)
        window_close = event_time + timedelta(minutes=minutes_after)

        if window_open <= now <= window_close:
            if now < event_time:
                mins_to = int((event_time - now).total_seconds() / 60)
                reason = (
                    f"{event['impact']} impact event in {mins_to} min: "
                    f"{event['title']} ({event['currency']}) at {event['time_et']}"
                )
            else:
                mins_ago = int((now - event_time).total_seconds() / 60)
                reason = (
                    f"{event['impact']} impact event {mins_ago} min ago: "
                    f"{event['title']} ({event['currency']}) at {event['time_et']}"
                )
            return {"in_blackout": True, "reason": reason, "event": event}

    return {"in_blackout": False, "reason": "No high-impact events in window", "event": None}


def format_calendar_section(symbol: Optional[str] = None, hours_ahead: int = 12) -> str:
    """
    Format upcoming economic events as a report section.
    If symbol is given, only shows events that affect it.
    """
    events = get_upcoming_events(hours_ahead=hours_ahead)
    if symbol:
        sym_up = symbol.upper()
        events = [e for e in events
                  if sym_up in [s.upper() for s in e["affects"]]
                  or sym_up in e["currency"].upper()]

    if not events:
        return f"  No significant economic events in next {hours_ahead}h"

    lines = [f"  ECONOMIC CALENDAR — next {hours_ahead}h"]
    impact_icon = {"HIGH": "🔴", "MEDIUM": "🟡", "LOW": "⚪", "HOLIDAY": "📅"}
    for e in events:
        icon = impact_icon.get(e["impact"], "⚪")
        forecast_str = f"  Forecast: {e['forecast']}" if e["forecast"] else ""
        prev_str     = f"  Prev: {e['previous']}"     if e["previous"] else ""
        lines.append(
            f"  {icon} {e['time_et']}  [{e['impact']}]  {e['currency']}  {e['title']}"
            + forecast_str + prev_str
        )

    return "\n".join(lines)


def format_todays_high_impact(symbol: Optional[str] = None) -> str:
    """Return today's HIGH impact events, formatted as a pre-session alert."""
    events = get_events_today(impact_filter="HIGH")
    if symbol:
        sym_up = symbol.upper()
        events = [e for e in events
                  if sym_up in [s.upper() for s in e["affects"]]
                  or sym_up in e["currency"].upper()]

    if not events:
        return "  No HIGH-impact events today"

    lines = ["  TODAY'S HIGH-IMPACT EVENTS ⚠"]
    for e in events:
        forecast_str = f"  F:{e['forecast']}" if e["forecast"] else ""
        prev_str     = f"  P:{e['previous']}"  if e["previous"] else ""
        lines.append(
            f"  🔴 {e['time_et']}  {e['currency']}  {e['title']}"
            + forecast_str + prev_str
        )
    return "\n".join(lines)
