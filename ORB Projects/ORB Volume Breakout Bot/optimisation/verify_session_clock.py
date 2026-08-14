#!/usr/bin/env python3
"""
Mirror of ComputeSessionTimesForDay, used to prove the two-zone schedule before
it goes anywhere near a live account.

There is no .NET toolchain in this environment, so the C# change cannot be
compiled here. This reimplements the same conversion in Python against the same
IANA tz database and checks the property that actually matters:

    the trading window must open one minute after the NYSE bell on EVERY
    trading day, including the four weekends a year when the UK and US change
    their clocks on different dates.

Run:  python verify_session_clock.py
Exits non-zero if any day violates the invariant.
"""
import sys
from datetime import datetime, time, timedelta
from zoneinfo import ZoneInfo

LON = ZoneInfo("Europe/London")
NY = ZoneInfo("America/New_York")
UTC = ZoneInfo("UTC")

# --- old config (the live .cbotset): UseFixedUtcTimes = true ------------------
OLD = {"range_start": time(8, 0), "range_end": time(14, 30),
       "trading_start": time(14, 31), "kill": time(16, 31)}

# --- new config: range start in London, everything from the bell on in NY -----
NEW = {"range_start": (time(8, 0), LON), "range_end": (time(9, 30), NY),
       "trading_start": (time(9, 31), NY), "kill": (time(11, 31), NY)}


def to_utc(session_date, t, tz):
    """C# ConvertConfiguredTimeToUtc: build the local wall time, then convert."""
    local = datetime.combine(session_date, t, tzinfo=tz)
    return local.astimezone(UTC)


def bell_utc(session_date):
    return datetime.combine(session_date, time(9, 30), tzinfo=NY).astimezone(UTC)


def main():
    start = datetime(2024, 1, 1).date()
    end = datetime(2026, 12, 31).date()

    failures = []
    transitions = []
    prev_sig = None
    day = start

    while day <= end:
        if day.weekday() < 5:
            bell = bell_utc(day)

            old_start = datetime.combine(day, OLD["trading_start"], tzinfo=UTC)
            old_lag = (old_start - bell).total_seconds() / 60.0

            new_start = to_utc(day, *NEW["trading_start"])
            new_lag = (new_start - bell).total_seconds() / 60.0

            new_rs = to_utc(day, *NEW["range_start"])
            new_re = to_utc(day, *NEW["range_end"])

            # invariant: new clock enters exactly 1 minute after the bell
            if abs(new_lag - 1.0) > 1e-6:
                failures.append((day, new_lag))
            # invariant: range must end at the bell and be non-degenerate
            if new_re != bell or new_re <= new_rs:
                failures.append((day, "range window malformed"))

            sig = (old_lag, round((new_re - new_rs).total_seconds() / 3600.0, 2))
            if sig != prev_sig:
                transitions.append((day, old_lag, new_rs, new_re, sig[1]))
                prev_sig = sig
        day += timedelta(days=1)

    print("Entry time relative to the NYSE bell, at each regime change")
    print("=" * 76)
    print(f"{'from':<12}{'OLD lag':>9}   {'NEW range (UTC)':<20}{'len':>6}   verdict")
    print("-" * 76)
    for d, old_lag, rs, re_, length in transitions:
        verdict = "on time" if abs(old_lag - 1.0) < 1e-6 else f"{old_lag - 1:+.0f} min late"
        print(f"{str(d):<12}{old_lag:>+7.0f}m   "
              f"{rs.strftime('%H:%M')}-{re_.strftime('%H:%M')}{'':<10}{length:>5.1f}h   {verdict}")

    print()
    if failures:
        print(f"FAIL: {len(failures)} day(s) violated the invariant")
        for f in failures[:10]:
            print("  ", f)
        return 1

    days = sum(1 for _ in range((end - start).days + 1))
    print(f"PASS: new clock enters exactly 1 min after the bell on every trading day "
          f"({start} to {end}).")
    print()
    print("Note the range length column: it is 6.5h normally but 5.5h during the")
    print("weeks when UK and US clocks disagree, because the London start is fixed")
    print("and the bell moves. That is a real consequence of anchoring the start in")
    print("London - correct by construction, but worth knowing it is not constant.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
