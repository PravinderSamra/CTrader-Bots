"""
Phase 2 data extension. Pull longer intraday history for:
  - GER40 M15  (deeper history for robust fill/fade + walk-forward)
  - US500 M15  (for the US cash-open / RTH gap reconstruction)
  - US30  M15  (ditto)

cTrader caps each call at 100 bars, so M15 uses 24h windows. Writes each symbol's
CSV as it completes so a mid-run drop still leaves usable partial data.
Run: python3 fetch_phase2.py
"""
import csv
import os
from ctrader_client import fetch_ohlcv_window

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)
PIP_DIV = 1e5

JOBS = [
    ("GER40", 200, "M_15", 730, "GER40_M15_2y.csv"),
    ("US500", 220, "M_15", 730, "US500_M15_2y.csv"),
    ("US30",  219, "M_15", 730, "US30_M15_2y.csv"),
]

def main():
    for name, sid, period, days, out in JOBS:
        print(f"[{name}] fetching {period} {days}d ...", flush=True)
        bars = fetch_ohlcv_window(sid, period, days, PIP_DIV, chunk_hours=24, pause=0.15)
        if not bars:
            print(f"[{name}] NO DATA", flush=True)
            continue
        path = os.path.join(DATA_DIR, out)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "time", "open", "high", "low", "close", "volume"])
            w.writeheader(); w.writerows(bars)
        print(f"[{name}] saved {len(bars)} bars -> {out}  ({bars[0]['time'][:10]} .. {bars[-1]['time'][:10]})", flush=True)
    print("DONE", flush=True)

if __name__ == "__main__":
    main()
