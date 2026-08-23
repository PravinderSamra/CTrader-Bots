#!/usr/bin/env python3
"""
session_context.py — what day is it, what session are we in, and is this a new
trading day since the last scan?

Exists so the brief never says "today's range" on a Saturday, never treats a
09:15 pre-open scan as a continuation of yesterday's 17:00 mid-session scan,
and always knows whether the US market is actually open.

    python3 session_context.py
"""
import json, sys
from datetime import datetime, timezone, timedelta, date, time as dtime
from zoneinfo import ZoneInfo

ET = ZoneInfo("America/New_York")
UK = ZoneInfo("Europe/London")

# NYSE/Nasdaq full closures. Extend yearly — a wrong entry here silently makes
# the brief think a closed day is a trading day, so it is deliberately explicit
# rather than computed from rules.
US_HOLIDAYS = {
    "2026-01-01", "2026-01-19", "2026-02-16", "2026-04-03", "2026-05-25",
    "2026-06-19", "2026-07-03", "2026-09-07", "2026-11-26", "2026-12-25",
    "2027-01-01", "2027-01-18", "2027-02-15", "2027-03-26", "2027-05-31",
    "2027-06-18", "2027-07-05", "2027-09-06", "2027-11-25", "2027-12-24",
}
# 13:00 ET early closes (half days)
US_HALF_DAYS = {"2026-11-27", "2026-12-24", "2027-11-26"}

# (name, start_et_hour, end_et_hour, what it means for the brief)
_WINDOWS = [
    ("OVERNIGHT",  17.0, 19.0, "Futures have just re-opened. Thin and gappy — levels only, no trades"),
    ("ASIA",       19.0,  3.0, "Asia session. Builds the Asia high/low that London usually sweeps"),
    ("LONDON",      3.0,  8.5, "London session. First real liquidity; often sweeps Asia and sets a false direction"),
    ("PRE_NY",      8.5,  9.5, "US pre-market. The 08:30 ET data lands in here — check the gate before anything else"),
    ("NY_OPEN",     9.5, 11.0, "NY opening drive. Highest volume of the day; the day's high or low forms here ~65% of the time"),
    ("NY_MIDDAY",  11.0, 13.5, "Midday lull. Volume dries up and price pins — downgrade breakouts, favour fades"),
    ("NY_PM",      13.5, 15.5, "NY afternoon. 0DTE gamma unwinds and the close imbalance builds"),
    ("NY_CLOSE",   15.5, 16.0, "Closing auction. No new entries"),
    ("POST_CLOSE", 16.0, 17.0, "After the bell. Earnings drop in here"),
]


def _in_window(h, lo, hi):
    return (lo <= h < hi) if lo < hi else (h >= lo or h < hi)


def trading_day_of(dt_utc):
    """The session date a timestamp belongs to. The futures/CFD day rolls at
    17:00 ET, so anything after that belongs to the NEXT calendar day."""
    et = dt_utc.astimezone(ET)
    d = et.date()
    return d + timedelta(days=1) if et.hour >= 17 else d


def is_trading_day(d: date):
    if d.weekday() >= 5:
        return False, "weekend"
    if d.isoformat() in US_HOLIDAYS:
        return False, "US market holiday"
    return True, "half day (13:00 ET close)" if d.isoformat() in US_HALF_DAYS else "regular session"


def next_trading_day(d: date):
    n = d + timedelta(days=1)
    for _ in range(10):
        ok, _r = is_trading_day(n)
        if ok:
            return n
        n += timedelta(days=1)
    return n


def context(now_utc=None, last_scan_iso=None):
    now = now_utc or datetime.now(timezone.utc)
    et, uk = now.astimezone(ET), now.astimezone(UK)
    h = et.hour + et.minute / 60.0

    tday = trading_day_of(now)
    open_today, why = is_trading_day(tday)

    window, window_note = "CLOSED", "Market closed"
    if open_today:
        for name, lo, hi, note in _WINDOWS:
            if _in_window(h, lo, hi):
                window, window_note = name, note
                break

    out = {
        "now_utc": now.isoformat(timespec="seconds"),
        "now_et": et.strftime("%Y-%m-%d %H:%M ET (%a)"),
        "now_uk": uk.strftime("%Y-%m-%d %H:%M %Z (%a)"),
        "trading_day": tday.isoformat(),
        "is_trading_day": open_today,
        "day_status": why,
        "session_window": window,
        "session_note": window_note,
    }

    if not open_today:
        nxt = next_trading_day(tday - timedelta(days=1) if tday.weekday() >= 5 else tday)
        out["next_trading_day"] = nxt.isoformat()
        out["headline"] = (
            f"{uk:%A} — **{why}**. This is a PREP scan, not a live one: the "
            f"numbers below are last session's close. Next session "
            f"{nxt:%A %d %b}.")
    else:
        opening = datetime.combine(tday, dtime(9, 30), tzinfo=ET)
        mins = round((opening - et).total_seconds() / 60)
        out["minutes_to_ny_open"] = mins
        if mins > 0:
            out["headline"] = (f"{uk:%A} — **{window}**, NY cash opens in "
                               f"{mins} min. {window_note}")
        else:
            out["headline"] = (f"{uk:%A} — **{window}**, "
                               f"{abs(mins)} min into the NY session. {window_note}")

    # --- relationship to the previous scan ---------------------------------
    if last_scan_iso:
        try:
            prev = datetime.fromisoformat(last_scan_iso)
            if prev.tzinfo is None:
                prev = prev.replace(tzinfo=timezone.utc)
            pday = trading_day_of(prev)
            gap_h = round((now - prev).total_seconds() / 3600, 1)
            same = pday == tday
            prev_et = prev.astimezone(ET)
            # The futures day rolls at 17:00 ET, so a scan at 17:30 Tuesday and
            # one at 09:15 Wednesday are the SAME session day. True, but it
            # reads as nonsense after a night's sleep — so when the calendar
            # date also changed, say both things.
            cal_changed = prev_et.date() != et.date()
            if same and cal_changed:
                rel = (f"Same session day (the futures day rolled at 17:00 ET "
                       f"on {prev_et:%a}), but it is now {et:%A} and the last "
                       f"scan was {gap_h}h ago at {prev_et:%a %H:%M ET}. "
                       f"Levels still stand; re-check what moved overnight.")
            elif same:
                rel = (f"Continuation — last scan {gap_h}h ago at "
                       f"{prev_et:%H:%M ET} today. Read the CHANGES, not the "
                       f"whole brief.")
            else:
                rel = (f"**New trading day.** Last scan was {gap_h}h ago "
                       f"({prev_et:%a %d %b %H:%M ET}) and covered "
                       f"{pday:%A %d %b}; everything below is fresh. That "
                       f"session's high/low are now the prior-day levels.")
            out["previous_scan"] = {
                "at_utc": prev.isoformat(timespec="seconds"),
                "at_et": prev_et.strftime("%Y-%m-%d %H:%M ET (%a)"),
                "trading_day": pday.isoformat(),
                "hours_ago": gap_h,
                "same_trading_day": same,
                "calendar_day_changed": cal_changed,
                "relation": rel,
            }
        except Exception as e:
            out["previous_scan"] = {"_error": str(e)}
    else:
        out["previous_scan"] = None
        out["first_scan"] = True
    return out


if __name__ == "__main__":
    last = sys.argv[1] if len(sys.argv) > 1 else None
    c = context(last_scan_iso=last)
    if "--json" in sys.argv:
        print(json.dumps(c, indent=2)); sys.exit(0)
    print(c["headline"]); print()
    for k in ("now_et", "now_uk", "trading_day", "is_trading_day", "day_status",
              "session_window", "minutes_to_ny_open", "next_trading_day"):
        if k in c:
            print(f"  {k:22} {c[k]}")
    if c.get("previous_scan"):
        print(f"\n  vs last scan: {c['previous_scan'].get('relation')}")
