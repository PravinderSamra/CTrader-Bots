"""
Download full M5 (+ D1) history for US30 and NAS100 from cTrader and store it
once under data/<INSTRUMENT>/ so all later analysis / strategy pivots reuse it
without re-downloading.

Pages backward in 8h windows (<=96 M5 bars, under the 100-bar/call server cap).
Resumable: re-running extends coverage (older + newer) and dedupes by timestamp.
"""
import os
import sys
import csv
import json
import time
from datetime import datetime, timezone, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ctrader_client as cc

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
START = datetime(2023, 7, 1, tzinfo=timezone.utc)   # ~3 years
WINDOW_H = 8

# plausible display-price ranges for divisor auto-detection
RANGES = {"US30": (25000, 60000), "NAS100": (8000, 35000), "US500": (3000, 12000)}


def detect_div(name, raw):
    lo, hi = RANGES[name]
    for n in range(0, 10):
        if lo <= raw / (10 ** n) <= hi:
            return 10 ** n
    return 100000


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def in_weekend_gap(win_start, win_end):
    """Skip windows fully inside the index CFD weekend closure (UTC).
    Closed ~Fri 21:00 UTC -> Sun 22:00 UTC. Conservative: skip Sat windows and
    Sunday windows ending by 21:00 UTC."""
    if win_start.weekday() == 5:  # Saturday
        return True
    if win_start.weekday() == 6 and win_end.hour <= 21 and win_end.weekday() == 6:
        return True
    return False


def load_existing(path):
    seen = {}
    if os.path.exists(path):
        with open(path) as f:
            r = csv.DictReader(f)
            for row in r:
                seen[int(row["timestamp_ms"])] = row
    return seen


def write_csv(path, rows_by_ts):
    fields = ["timestamp_ms", "datetime_utc", "open", "high", "low", "close", "volume"]
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for ts in sorted(rows_by_ts):
            w.writerow(rows_by_ts[ts])


def download_m5(name, sym_id):
    path = os.path.join(ROOT, "data", name, f"{name.lower()}_m5.csv")
    rows = load_existing(path)
    div = None
    now = datetime.now(timezone.utc).replace(second=0, microsecond=0)
    to = now
    calls = 0
    new = 0
    empty_streak = 0
    print(f"[{name}] M5 start; existing rows={len(rows)}", flush=True)
    while to > START:
        frm = to - timedelta(hours=WINDOW_H)
        if frm < START:
            frm = START
        if in_weekend_gap(frm, to):
            to = frm
            continue
        bars = cc.get_trendbars(sym_id, "M_5", iso(frm), iso(to))
        calls += 1
        if bars:
            empty_streak = 0
            if div is None:
                div = detect_div(name, bars[0]["close"])
                print(f"[{name}] divisor={div}", flush=True)
            for b in bars:
                ts = b["timestamp"]
                if ts in rows:
                    continue
                rows[ts] = {
                    "timestamp_ms": ts,
                    "datetime_utc": datetime.fromtimestamp(ts / 1000, timezone.utc)
                                            .strftime("%Y-%m-%d %H:%M:%S"),
                    "open": round(b["open"] / div, 2),
                    "high": round(b["high"] / div, 2),
                    "low": round(b["low"] / div, 2),
                    "close": round(b["close"] / div, 2),
                    "volume": b.get("volume", 0),
                }
                new += 1
        else:
            empty_streak += 1
        to = frm
        if calls % 40 == 0:
            write_csv(path, rows)
            print(f"[{name}] calls={calls} rows={len(rows)} new={new} "
                  f"reached={frm:%Y-%m-%d} empty_streak={empty_streak}", flush=True)
        time.sleep(0.15)
    write_csv(path, rows)
    print(f"[{name}] M5 DONE calls={calls} total_rows={len(rows)} new={new}", flush=True)
    return div


def download_d1(name, sym_id, div):
    """Daily bars back to START (few calls; 100/call ~ up to 100 days per window)."""
    path = os.path.join(ROOT, "data", name, f"{name.lower()}_d1.csv")
    rows = load_existing(path)
    to = datetime.now(timezone.utc)
    while to > START:
        frm = to - timedelta(days=95)
        if frm < START:
            frm = START
        bars = cc.get_trendbars(sym_id, "D_1", iso(frm), iso(to))
        if bars and div:
            for b in bars:
                ts = b["timestamp"]
                if ts in rows:
                    continue
                rows[ts] = {
                    "timestamp_ms": ts,
                    "datetime_utc": datetime.fromtimestamp(ts / 1000, timezone.utc)
                                            .strftime("%Y-%m-%d %H:%M:%S"),
                    "open": round(b["open"] / div, 2),
                    "high": round(b["high"] / div, 2),
                    "low": round(b["low"] / div, 2),
                    "close": round(b["close"] / div, 2),
                    "volume": b.get("volume", 0),
                }
        to = frm
        time.sleep(0.15)
    write_csv(path, rows)
    print(f"[{name}] D1 DONE rows={len(rows)}", flush=True)


def write_manifest(name, div):
    path = os.path.join(ROOT, "data", name, "manifest.json")
    m5 = os.path.join(ROOT, "data", name, f"{name.lower()}_m5.csv")
    n = 0
    first = last = None
    if os.path.exists(m5):
        with open(m5) as f:
            r = list(csv.DictReader(f))
            n = len(r)
            if r:
                first, last = r[0]["datetime_utc"], r[-1]["datetime_utc"]
    json.dump({
        "instrument": name, "symbol_id": SYM[name], "period_primary": "M_5",
        "price_divisor": div, "m5_bars": n,
        "coverage_first_utc": first, "coverage_last_utc": last,
        "source": "cTrader MCP (Pepperstone UK GBP spread-bet demo)",
        "volume_note": "tick volume (price-update count), not real contract volume",
        "downloaded_at": datetime.now(timezone.utc).isoformat(),
    }, open(path, "w"), indent=2)
    print(f"[{name}] manifest written ({n} bars, {first} -> {last})", flush=True)


SYM = cc.SYMBOLS

if __name__ == "__main__":
    targets = sys.argv[1:] or ["US30", "NAS100"]
    for name in targets:
        sym_id = SYM[name]
        div = download_m5(name, sym_id)
        download_d1(name, sym_id, div)
        write_manifest(name, div)
    print("ALL DONE", flush=True)
