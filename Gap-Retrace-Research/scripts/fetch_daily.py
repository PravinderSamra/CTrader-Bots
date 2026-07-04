"""
Download multi-year D_1 history for the gap candidate instruments and save to CSV.
Run: python3 fetch_daily.py
"""
import csv
import os
import sys
from ctrader_client import fetch_ohlcv_window

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

# symbolId map confirmed from repo integration guide; all use pip_div 1e5 (verified live)
SYMBOLS = {
    "US500":  220,
    "US30":   219,
    "NAS100": 205,
    "GER40":  200,
    "UK100":  217,
    "XAUUSD": 241,
}
PIP_DIV = 1e5
DAYS_BACK = 1095  # ~3 years

def main():
    for name, sid in SYMBOLS.items():
        print(f"Fetching {name} (id={sid}) D_1 {DAYS_BACK}d ...", flush=True)
        bars = fetch_ohlcv_window(sid, "D_1", DAYS_BACK, PIP_DIV, chunk_hours=700, pause=0.3)
        if not bars:
            print(f"  !! no data for {name}", flush=True)
            continue
        path = os.path.join(DATA_DIR, f"{name}_D1.csv")
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "time", "open", "high", "low", "close", "volume"])
            w.writeheader()
            w.writerows(bars)
        print(f"  saved {len(bars)} bars -> {os.path.relpath(path)}  ({bars[0]['time'][:10]} .. {bars[-1]['time'][:10]})", flush=True)

if __name__ == "__main__":
    main()
