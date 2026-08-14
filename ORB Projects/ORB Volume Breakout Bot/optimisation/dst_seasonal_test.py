#!/usr/bin/env python3
"""
Does the bot's fixed-UTC clock split it into two different strategies?

The live config sets UseFixedUtcTimes=true with range 08:00-14:30 UTC and first
entry 14:31 UTC. The source (ORB_Volume_Breakout_Bot_v2.cs:955) then skips all DST
handling: ConvertConfiguredTimeToUtc returns `sessionDate + configuredTime`.

But the NYSE cash open moves in UTC:
    US winter (EST) -> open 14:30 UTC -> range ends at the bell, entry 09:31 ET
    US summer (EDT) -> open 13:30 UTC -> range ends 10:30 ET, entry 10:31 ET

So for ~7 months a year the bot trades an hour after the open, off a range that
already contains the opening expansion. For the other ~5 it trades one minute
after the bell, in what the repo's earlier M5 study found to be the noisiest
window of the day.

This script rebuilds the trade ledger from stored M5 data under three clocks and
compares them, overall and split by DST season, to see how much of the 2024 vs
2025 gap that mechanism explains.

    python dst_seasonal_test.py

Approximation notes (stated so results are not over-read):
  * Engine is M5; the live bot uses M1 bars for the ORB and confirmation. Entry
    timing is therefore granular to 5 minutes and the volume lookback covers
    100 minutes rather than 20.
  * Tick volume, not contract volume.
  * Same-bar SL-before-TP is assumed (pessimistic), matching the earlier study.
  * Spread/commission applied as a configurable per-trade drag.
"""
import os
import numpy as np
import pandas as pd
from zoneinfo import ZoneInfo

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.normpath(os.path.join(
    HERE, "..", "..", "..", "US30 London Range Breakout", "data", "US30", "us30_m5.csv"))
OUT = os.path.join(HERE, "results")

NY = ZoneInfo("America/New_York")

# --- live config, transcribed from the .cbotset -------------------------------
RANGE_START_UTC = 8.0        # RangeStartTimeUtcStr  08:00:00
RANGE_END_UTC = 14.5         # RangeEndTimeUtcStr    14:30:00
TRADE_START_UTC = 14.5167    # TradingStartTimeUtcStr 14:31:00
KILL_UTC = 16.5167           # KillSwitchTimeUtcStr  16:31:00, ClosePositionsAtKillSwitch=true
STOP_PTS = 50.0              # FixedStopPoints
VOL_MULT = 1.4               # VolumeMultiplier
# The bot runs VolumeLookbackBars=20 on M1 bars, i.e. a 20-MINUTE trailing mean.
# On M5 that is 4 bars, not 20 - using 20 M5 bars stretches the window to 100
# minutes, drags the opening volume spike into the average and makes the 1.4x
# test far harder to pass late in the window. Match the bot in wall-clock time.
VOL_LOOKBACK = 4             # 4 M5 bars = 20 minutes
BE_TRIGGER_R = 0.6           # BreakEvenTriggerR
BE_EXTRA_PTS = 4.5           # BreakEvenExtraPips
STEP_R = 1.0                 # DynamicStepR
EARLY_TRIGGER_R = 0.5        # EarlyRiskReductionTriggerR
EARLY_REMAIN = 0.50          # EarlyRiskReductionRemainingRiskPercent
MAX_RANGE_PTS = 500.0        # MaxOrbRangePips
ALLOW_SHORT = False          # AllowShort
SPREAD_PTS = 1.5             # not modelled by the bot; realistic US30 spread-bet


def load():
    df = pd.read_csv(DATA, parse_dates=["datetime_utc"])
    df = df.rename(columns={"datetime_utc": "ts"}).set_index("ts").sort_index()
    df["date"] = df.index.date
    df["hour_utc"] = df.index.hour + df.index.minute / 60.0
    return df


def ny_open_utc_hour(day):
    """UTC hour of the 09:30 ET cash open for a given date (13.5 EDT / 14.5 EST)."""
    local = pd.Timestamp(f"{day} 09:30:00", tz=NY)
    return local.tz_convert("UTC").hour + local.tz_convert("UTC").minute / 60.0


def is_us_dst(day):
    return ny_open_utc_hour(day) == 13.5


def simulate_day(bars, range_end_h, entry_from_h, kill_h, diag=None):
    """One day, long-only, first qualifying M5 close above the range high.

    Returns a trade dict or None. R is measured against the initial 50pt stop so
    trades stay comparable across clocks. `diag` collects the stand-down reason so
    we can see which filter is actually suppressing trades, not just guess.
    """
    def stand_down(reason, width=None):
        if diag is not None:
            diag.append({"date": bars.date.iloc[0], "reason": reason, "range_width": width})
        return None

    rng = bars[(bars.hour_utc >= RANGE_START_UTC) & (bars.hour_utc < range_end_h)]
    if len(rng) < 12:
        return stand_down("no_range_data")
    hi, lo = rng.high.max(), rng.low.min()
    width = hi - lo
    if width <= 0:
        return stand_down("degenerate_range", width)
    if width >= MAX_RANGE_PTS:
        return stand_down("range_too_wide", width)  # NO TRADE TODAY: range >= max

    scan = bars[(bars.hour_utc >= entry_from_h) & (bars.hour_utc < kill_h)]
    if scan.empty:
        return stand_down("no_scan_bars", width)

    # trailing volume average over the preceding bars, as the bot computes it
    vol_avg = bars.volume.rolling(VOL_LOOKBACK).mean().shift(1)

    entry_i = None
    saw_breakout = False
    for i in range(len(scan)):
        bar = scan.iloc[i]
        if bar.close <= hi:
            continue
        saw_breakout = True
        avg = vol_avg.get(scan.index[i], np.nan)
        if not np.isfinite(avg) or avg <= 0:
            continue
        if bar.volume < VOL_MULT * avg:
            continue  # VOLUME FILTER rejection
        entry_i = i
        break
    if entry_i is None:
        # Separating these two matters: "never broke out" is the range window's
        # fault, "broke out but volume failed" is the filter's.
        return stand_down("vol_filter_rejected" if saw_breakout else "no_breakout", width)

    entry_bar = scan.iloc[entry_i]
    entry = entry_bar.close + SPREAD_PTS  # pay the spread on entry
    stop = entry_bar.close - STOP_PTS
    risk = entry - stop

    # walk forward to the kill switch, applying the bot's stop ladder
    fwd = scan.iloc[entry_i + 1:]
    sl = stop
    peak_r = 0.0
    early_done = False
    be_done = False
    steps = 0
    exit_px, reason = None, "KILL"

    for _, b in fwd.iterrows():
        # pessimistic: assume the low is reached before the high within the bar
        if b.low <= sl:
            exit_px, reason = sl, "SL"
            break
        r_now = (b.high - entry) / risk
        peak_r = max(peak_r, r_now)

        if not early_done and peak_r >= EARLY_TRIGGER_R:
            sl = max(sl, entry - risk * EARLY_REMAIN)
            early_done = True
        if not be_done and peak_r >= BE_TRIGGER_R:
            sl = max(sl, entry + BE_EXTRA_PTS)
            be_done = True
        if peak_r >= STEP_R:
            k = int(peak_r // STEP_R)
            if k > steps:
                steps = k
                sl = max(sl, entry + risk * (k - 1) * STEP_R)

    if exit_px is None:
        exit_px = fwd.iloc[-1].close if len(fwd) else entry_bar.close

    r = (exit_px - entry) / risk
    return {
        "date": bars.date.iloc[0],
        "entry_utc": scan.index[entry_i],
        "range_width": width,
        "entry": entry,
        "exit": exit_px,
        "reason": reason,
        "R": r,
        "peak_R": peak_r,
    }


def run_clock(df, name, dst_aware, wait_minutes):
    """dst_aware=False -> the bot's fixed 14:30/14:31 UTC.
       dst_aware=True  -> range ends at the real cash open, entry `wait_minutes` later."""
    rows, diag = [], []
    for day, bars in df.groupby("date"):
        if pd.Timestamp(day).weekday() >= 5:
            continue
        if dst_aware:
            open_h = ny_open_utc_hour(day)
            range_end = open_h
            entry_from = open_h + wait_minutes / 60.0
            kill = entry_from + 2.0  # keep the bot's 2-hour hold window
        else:
            range_end, entry_from, kill = RANGE_END_UTC, TRADE_START_UTC, KILL_UTC
        season = "summer (EDT)" if is_us_dst(day) else "winter (EST)"
        meta = {"clock": name, "dst": season, "year": pd.Timestamp(day).year}

        d = []
        t = simulate_day(bars, range_end, entry_from, kill, diag=d)
        if t:
            t.update(meta)
            rows.append(t)
        for row in d:
            row.update(meta)
            diag.append(row)
    return pd.DataFrame(rows), pd.DataFrame(diag)


def summarise(t, by):
    if t.empty:
        return pd.DataFrame()
    g = t.groupby(by)["R"]
    out = pd.DataFrame({
        "trades": g.size(),
        "win%": g.apply(lambda s: 100.0 * (s > 0).mean()).round(1),
        "totalR": g.sum().round(1),
        "expectancy": g.mean().round(3),
    })
    pf = t.groupby(by)["R"].apply(
        lambda s: s[s > 0].sum() / abs(s[s < 0].sum()) if (s < 0).any() else np.inf)
    out["PF"] = pf.round(2)
    return out


def main():
    os.makedirs(OUT, exist_ok=True)
    df = load()
    print(f"Loaded {len(df):,} M5 bars  {df.index[0]} -> {df.index[-1]}\n")

    specs = [("as-is", False, 0), ("dst_open", True, 1),
             ("dst_30", True, 30), ("dst_60", True, 60)]
    trades, diags = [], []
    for nm, aware, wait in specs:
        t, d = run_clock(df, nm, aware, wait)
        trades.append(t)
        diags.append(d)

    all_t = pd.concat(trades, ignore_index=True)
    all_d = pd.concat(diags, ignore_index=True)
    all_t.to_csv(os.path.join(OUT, "dst_trades.csv"), index=False)
    all_d.to_csv(os.path.join(OUT, "dst_standdowns.csv"), index=False)

    print("=" * 78)
    print("OVERALL BY CLOCK")
    print("=" * 78)
    print(summarise(all_t, "clock").to_string(), "\n")

    print("=" * 78)
    print("THE KEY SPLIT: same bot, two seasons (as-is clock only)")
    print("=" * 78)
    asis = all_t[all_t.clock == "as-is"]
    print(summarise(asis, "dst").to_string(), "\n")

    print("=" * 78)
    print("BY YEAR x SEASON (as-is clock) - is 2024 concentrated in winter?")
    print("=" * 78)
    print(summarise(asis, ["year", "dst"]).to_string(), "\n")

    print("=" * 78)
    print("BY YEAR x CLOCK - would a DST fix have saved 2024?")
    print("=" * 78)
    print(summarise(all_t, ["year", "clock"])["totalR"].unstack().round(1).to_string(), "\n")

    print("=" * 78)
    print("WHY NO TRADE? stand-down reasons, as-is clock, by season")
    print("=" * 78)
    dz = all_d[all_d.clock == "as-is"]
    tab = dz.pivot_table(index="reason", columns="dst", values="date",
                         aggfunc="count", fill_value=0)
    taken = asis.groupby("dst").size().rename("TRADE TAKEN").to_frame().T
    tab = pd.concat([tab, taken.reindex(columns=tab.columns, fill_value=0)])
    print(tab.to_string(), "\n")

    print("=" * 78)
    print("ORB range width by season (as-is clock) - does summer blow the 500pt cap?")
    print("=" * 78)
    w = all_d[(all_d.clock == "as-is") & all_d.range_width.notna()]
    print(w.groupby("dst").range_width.describe()[
        ["count", "mean", "50%", "75%", "max"]].round(0).to_string(), "\n")

    print(f"Trade ledger  -> {os.path.join(OUT, 'dst_trades.csv')}")
    print(f"Stand-downs   -> {os.path.join(OUT, 'dst_standdowns.csv')}")


if __name__ == "__main__":
    main()
