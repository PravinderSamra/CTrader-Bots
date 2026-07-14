#!/usr/bin/env python3
"""
Compares first-10-minute spike magnitude across 4 release types (Jobless Claims,
ADP, PPI, Retail Sales) on NAS100 and US500, using the last 6 instances of each.
Also applies the same confirmation-direction logic as the CPI study isn't
available here (no consensus/actual data collected for magnitude-only study) --
this script measures raw volatility/spike size, not directional hit rate.
"""
import json, os, datetime as dt
from collections import defaultdict

BASE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(BASE, "raw_candles")

EVENTS = {
    "Jobless Claims": [
        ("2026-07-09", "12:30"), ("2026-07-02", "12:30"), ("2026-06-25", "12:30"),
        ("2026-06-18", "12:30"), ("2026-06-11", "12:30"), ("2026-06-04", "12:30"),
    ],
    "ADP Employment": [
        ("2026-06-03", "12:30"), ("2026-05-06", "12:30"), ("2026-04-01", "12:30"),
        ("2026-03-04", "13:30"), ("2026-02-04", "13:30"), ("2026-01-07", "13:30"),
    ],
    "PPI": [
        ("2026-06-11", "12:30"), ("2026-05-13", "12:30"), ("2026-04-14", "12:30"),
        ("2026-03-18", "12:30"), ("2026-02-27", "13:30"), ("2026-01-30", "13:30"),
    ],
    "Retail Sales": [
        ("2026-06-17", "12:30"), ("2026-05-14", "12:30"), ("2026-04-21", "12:30"),
        ("2026-04-01", "12:30"), ("2026-03-06", "13:30"), ("2026-02-10", "13:30"),
    ],
}

# overlap notes: PPI 2026-06-11 == Jobless Claims 2026-06-11 (same release window)
#                Retail Sales 2026-04-01 == ADP 2026-04-01 (same release window)
OVERLAPS = {
    ("PPI", "2026-06-11"): "Jobless Claims 2026-06-11",
    ("Retail Sales", "2026-04-01"): "ADP Employment 2026-04-01",
}

def to_ms(date_str, time_str):
    d = dt.datetime.strptime(f"{date_str}T{time_str}:00", "%Y-%m-%dT%H:%M:%S").replace(tzinfo=dt.timezone.utc)
    return int(d.timestamp() * 1000)

def px(bar, f="open"):
    return bar[f] / 100000.0

def load(event_type, date, instrument):
    fname = f"{event_type.replace(' ', '')}_{date}_{instrument}.json"
    # normalize names used on disk
    name_map = {"JoblessClaims": "JoblessClaims", "ADPEmployment": "ADP", "PPI": "PPI", "RetailSales": "RetailSales"}
    prefix = name_map.get(event_type.replace(" ", ""), event_type.replace(" ", ""))
    fname = f"{prefix}_{date}_{instrument}.json"
    path = os.path.join(RAW, fname)
    with open(path) as f:
        return {b["timestamp"]: b for b in json.load(f)["trendbars"]}

def nearest_bar(bars, target_ms):
    for offset in (0, -60000, 60000, -120000, 120000):
        t = target_ms + offset
        if t in bars:
            return bars[t]
    closest = min(bars.keys(), key=lambda t: abs(t - target_ms))
    return bars[closest] if abs(closest - target_ms) <= 180000 else None

def spike_10min(event_type, date, time_str, instrument):
    bars = load(event_type, date, instrument)
    release_ms = to_ms(date, time_str)
    b0 = nearest_bar(bars, release_ms)
    P0 = px(b0, "open")
    window_bars = [b for t, b in bars.items() if release_ms <= t <= release_ms + 10 * 60000]
    high = max(px(b, "high") for b in window_bars)
    low = min(px(b, "low") for b in window_bars)
    b10 = nearest_bar(bars, release_ms + 10 * 60000)
    P10 = px(b10, "open")
    net_move = P10 - P0
    spike_range = high - low
    return {"P0": P0, "P10": P10, "net_move": net_move, "spike_range": spike_range,
            "high": high, "low": low}

def main():
    results = defaultdict(lambda: defaultdict(list))
    for event_type, dates in EVENTS.items():
        for date, time_str in dates:
            for instrument in ("NAS100", "US500"):
                r = spike_10min(event_type, date, time_str, instrument)
                results[event_type][instrument].append((date, r))

    print("=" * 100)
    print("FIRST-10-MINUTE SPIKE MAGNITUDE BY RELEASE TYPE (last 6 instances each)")
    print("=" * 100)
    summary = {}
    for event_type in EVENTS:
        print(f"\n--- {event_type} ---")
        for instrument in ("NAS100", "US500"):
            rows = results[event_type][instrument]
            spikes = [r["spike_range"] for _, r in rows]
            nets = [abs(r["net_move"]) for _, r in rows]
            avg_spike = sum(spikes) / len(spikes)
            avg_net = sum(nets) / len(nets)
            max_spike = max(spikes)
            summary[(event_type, instrument)] = (avg_spike, avg_net, max_spike)
            print(f"  {instrument:8s}: avg spike range (high-low, 10min) = {avg_spike:7.1f} pts | "
                  f"avg |net move| = {avg_net:7.1f} pts | max spike = {max_spike:7.1f} pts")
            for date, r in rows:
                overlap = OVERLAPS.get((event_type, date), "")
                overlap_note = f"  [OVERLAPS: {overlap}]" if overlap else ""
                print(f"    {date}: P0={r['P0']:.1f} P10={r['P10']:.1f} net={r['net_move']:+.1f} "
                      f"spike_range={r['spike_range']:.1f}{overlap_note}")

    print("\n" + "=" * 100)
    print("RANKING (by avg 10-min spike range, both instruments)")
    print("=" * 100)
    for instrument in ("NAS100", "US500"):
        print(f"\n{instrument}:")
        ranked = sorted(EVENTS.keys(), key=lambda e: -summary[(e, instrument)][0])
        for i, event_type in enumerate(ranked, 1):
            avg_spike, avg_net, max_spike = summary[(event_type, instrument)]
            print(f"  {i}. {event_type:16s} avg spike {avg_spike:7.1f} pts | avg net {avg_net:6.1f} pts | max {max_spike:7.1f} pts")

if __name__ == "__main__":
    main()
