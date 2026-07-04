"""
Download intraday M15 (and M5 for a shorter window) history for the chosen
gap instrument (GER40 / DAX). The cTrader endpoint hard-caps each call at 100
bars, so M15 must be pulled in <=24h windows (96 bars). Saves to data/.

Run: python3 fetch_intraday.py
"""
import csv
import os
import sys
from ctrader_client import fetch_ohlcv_window

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
os.makedirs(DATA_DIR, exist_ok=True)

SYMBOL = "GER40"
SID = 200
PIP_DIV = 1e5

JOBS = [
    # (period, days_back, chunk_hours, out_name)
    ("M_15", 160, 24, "GER40_M15.csv"),
    ("M_5",   45, 8,  "GER40_M5.csv"),   # 8h*12=96 bars/call, tighter recent window
]

def main():
    for period, days_back, chunk_h, out in JOBS:
        print(f"Fetching {SYMBOL} {period} {days_back}d (chunk {chunk_h}h) ...", flush=True)
        bars = fetch_ohlcv_window(SID, period, days_back, PIP_DIV, chunk_hours=chunk_h, pause=0.2)
        if not bars:
            print(f"  !! no data", flush=True)
            continue
        path = os.path.join(DATA_DIR, out)
        with open(path, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["timestamp", "time", "open", "high", "low", "close", "volume"])
            w.writeheader()
            w.writerows(bars)
        print(f"  saved {len(bars)} bars -> {os.path.relpath(path)}  ({bars[0]['time'][:16]} .. {bars[-1]['time'][:16]})", flush=True)

if __name__ == "__main__":
    main()
