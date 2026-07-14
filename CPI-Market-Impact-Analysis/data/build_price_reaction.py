#!/usr/bin/env python3
"""Deterministic builder for price_reaction.csv from raw cTrader candles + cpi_calendar.csv.

Implements the classification methodology in METHODOLOGY.md exactly:
- expected label from actual-vs-forecast surprise (MoM + YoY combined)
- actual label from price action (P0..P30, threshold = 0.05% of P0, reversal check)
"""
import json
import csv
import os

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")

# release_utc per reference_month, computed from US Eastern DST rules (verified earlier)
RELEASE_UTC = {
    "2024-06": "2024-07-11T12:30:00Z",
    "2024-07": "2024-08-14T12:30:00Z",
    "2024-08": "2024-09-11T12:30:00Z",
    "2024-09": "2024-10-10T12:30:00Z",
    "2024-10": "2024-11-13T13:30:00Z",
    "2024-11": "2024-12-11T13:30:00Z",
    "2024-12": "2025-01-15T13:30:00Z",
    "2025-01": "2025-02-12T13:30:00Z",
    "2025-02": "2025-03-12T12:30:00Z",
    "2025-03": "2025-04-10T12:30:00Z",
    "2025-04": "2025-05-13T12:30:00Z",
    "2025-05": "2025-06-11T12:30:00Z",
    "2025-06": "2025-07-15T12:30:00Z",
    "2025-07": "2025-08-12T12:30:00Z",
    "2025-08": "2025-09-11T12:30:00Z",
    "2025-09": "2025-10-24T12:30:00Z",
    "2025-11": "2025-12-18T13:30:00Z",
    "2025-12": "2026-01-13T13:30:00Z",
    "2026-01": "2026-02-13T13:30:00Z",
    "2026-02": "2026-03-11T12:30:00Z",
    "2026-03": "2026-04-10T12:30:00Z",
    "2026-04": "2026-05-12T12:30:00Z",
    "2026-05": "2026-06-10T12:30:00Z",
}

import datetime as dt

def to_epoch_ms(iso):
    return int(dt.datetime.strptime(iso, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc).timestamp() * 1000)

def load_calendar():
    rows = {}
    with open(os.path.join(BASE, "cpi_calendar.csv")) as f:
        for row in csv.DictReader(f):
            rows[row["reference_month"]] = row
    return rows

def parse_float(s):
    return float(s) if s not in (None, "", "null") else None

def load_candles(ref_month, instrument):
    path = os.path.join(RAW, f"{ref_month}_{instrument}.json")
    if not os.path.exists(path):
        return None
    with open(path) as f:
        data = json.load(f)
    bars = {b["timestamp"]: b for b in data["trendbars"]}
    return bars

def nearest_bar(bars, target_ms, search_ms=(0, -60000, 60000, -120000, 120000)):
    for offset in search_ms:
        t = target_ms + offset
        if t in bars:
            return bars[t]
    # widen search
    closest = min(bars.keys(), key=lambda t: abs(t - target_ms))
    if abs(closest - target_ms) <= 180000:
        return bars[closest]
    return None

def price(bar, field="open"):
    return bar[field] / 100000.0

def classify_expected(mom_actual, mom_forecast, yoy_actual, yoy_forecast):
    def contrib(actual, forecast):
        if actual is None or forecast is None:
            return None
        if actual > forecast:
            return "Bearish"
        elif actual < forecast:
            return "Bullish"
        else:
            return "Neutral"

    c_mom = contrib(mom_actual, mom_forecast)
    c_yoy = contrib(yoy_actual, yoy_forecast)
    contribs = [c for c in (c_mom, c_yoy) if c is not None]
    if not contribs:
        return "Unknown"
    non_neutral = [c for c in contribs if c != "Neutral"]
    if not non_neutral:
        return "Whipsaw"
    if len(set(non_neutral)) > 1:
        return "Whipsaw"
    return non_neutral[0]

def classify_actual(P0, P1, P5, P15, P30, high_30m, low_30m):
    net_move = P30 - P0
    initial_move = P5 - P0
    threshold = 0.0005 * P0  # 0.05%

    if abs(net_move) < threshold:
        return "Whipsaw", net_move, initial_move, threshold

    if (initial_move > 0) != (net_move > 0):
        # reversal: check excursion opposite net_move direction
        if net_move > 0:
            adverse_excursion = P0 - low_30m
        else:
            adverse_excursion = high_30m - P0
        if adverse_excursion > threshold:
            return "Whipsaw", net_move, initial_move, threshold

    label = "Bullish" if net_move > 0 else "Bearish"
    return label, net_move, initial_move, threshold

def main():
    calendar = load_calendar()
    out_rows = []
    events = sorted(RELEASE_UTC.keys())

    for ref_month in events:
        cal = calendar.get(ref_month)
        if cal is None:
            continue
        mom_actual = parse_float(cal["mom_actual"])
        mom_forecast = parse_float(cal["mom_forecast"])
        yoy_actual = parse_float(cal["yoy_actual"])
        yoy_forecast = parse_float(cal["yoy_forecast"])
        expected_label = classify_expected(mom_actual, mom_forecast, yoy_actual, yoy_forecast)

        release_iso = RELEASE_UTC[ref_month]
        release_ms = to_epoch_ms(release_iso)
        release_date = release_iso[:10]

        for instrument in ("US500", "NAS100"):
            bars = load_candles(ref_month, instrument)
            row = {
                "reference_month": ref_month,
                "release_date": release_date,
                "release_utc": release_iso,
                "instrument": instrument,
                "expected_label": expected_label,
            }
            if bars is None:
                row.update({k: "" for k in
                    ["P0","P1","P5","P15","P30","net_move_points","initial_move_points",
                     "points_moved","spike_range_5m","actual_label","hit"]})
                row["actual_label"] = "NO_DATA"
                out_rows.append(row)
                continue

            b0 = nearest_bar(bars, release_ms)
            b1 = nearest_bar(bars, release_ms + 60000)
            b5 = nearest_bar(bars, release_ms + 5*60000)
            b15 = nearest_bar(bars, release_ms + 15*60000)
            b30 = nearest_bar(bars, release_ms + 30*60000)

            if not all([b0, b1, b5, b15, b30]):
                row.update({k: "" for k in
                    ["P0","P1","P5","P15","P30","net_move_points","initial_move_points",
                     "points_moved","spike_range_5m","actual_label","hit"]})
                row["actual_label"] = "NO_DATA"
                out_rows.append(row)
                continue

            P0 = price(b0, "open")
            P1 = price(b1, "open")
            P5 = price(b5, "open")
            P15 = price(b15, "open")
            P30 = price(b30, "open")

            # high/low across release -> +30min window, and first 5 min for spike range
            window_bars = [b for t, b in bars.items() if release_ms <= t <= release_ms + 30*60000]
            spike_bars = [b for t, b in bars.items() if release_ms <= t <= release_ms + 5*60000]
            high_30m = max(price(b, "high") for b in window_bars) if window_bars else P0
            low_30m = min(price(b, "low") for b in window_bars) if window_bars else P0
            high_5m = max(price(b, "high") for b in spike_bars) if spike_bars else P0
            low_5m = min(price(b, "low") for b in spike_bars) if spike_bars else P0

            actual_label, net_move, initial_move, threshold = classify_actual(P0, P1, P5, P15, P30, high_30m, low_30m)
            points_moved = round(abs(net_move), 2) if actual_label in ("Bullish", "Bearish") else ""
            spike_range_5m = round(high_5m - low_5m, 2) if actual_label == "Whipsaw" else ""

            hit = ""
            if expected_label != "Unknown":
                hit = (actual_label == expected_label)

            row.update({
                "P0": round(P0, 2), "P1": round(P1, 2), "P5": round(P5, 2),
                "P15": round(P15, 2), "P30": round(P30, 2),
                "net_move_points": round(net_move, 2),
                "initial_move_points": round(initial_move, 2),
                "points_moved": points_moved,
                "spike_range_5m": spike_range_5m,
                "actual_label": actual_label,
                "hit": hit,
            })
            out_rows.append(row)

    fieldnames = ["reference_month","release_date","release_utc","instrument","P0","P1","P5","P15","P30",
                  "net_move_points","initial_move_points","points_moved","spike_range_5m",
                  "expected_label","actual_label","hit"]
    out_path = os.path.join(BASE, "price_reaction.csv")
    with open(out_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    print(f"Wrote {len(out_rows)} rows to {out_path}")
    no_data = [r for r in out_rows if r["actual_label"] == "NO_DATA"]
    print(f"NO_DATA rows: {len(no_data)}")
    for r in no_data:
        print("  ", r["reference_month"], r["instrument"])

if __name__ == "__main__":
    main()
