"""Download EURUSD / GBPUSD H1 bars (2012-01 .. now) from the cTrader feed into research/data/.

Reuses the MCP client from the London Range Breakout study (needs CTRADER_MCP_SLUG).
Pages forward in 96-hour windows (the server returns at most 100 bars per call). Resumable.
Run from the repo root:  python3 "Vanessa Algo Bots/research/scripts/download_fx_h1.py"
"""
import csv
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "US30 London Range Breakout/scripts"))
import ctrader_client as cc  # noqa: E402

SYMBOLS = {"EURUSD": 1, "GBPUSD": 2}
DIVISOR = 100000
START = datetime(2012, 1, 1, tzinfo=timezone.utc)
WINDOW = timedelta(hours=96)
OUT = ROOT / "Vanessa Algo Bots/research/data"
FIELDS = ["timestamp_ms", "datetime_utc", "open", "high", "low", "close", "volume"]


def iso(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def download(name, sym_id):
    path = OUT / f"{name.lower()}_h1.csv"
    rows = {}
    if path.exists():
        for r in csv.DictReader(open(path)):
            rows[int(r["timestamp_ms"])] = r
    frm = datetime.fromtimestamp(max(rows) / 1000, timezone.utc) if rows else START
    end = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    calls = 0
    while frm < end:
        to = min(frm + WINDOW, end)
        for b in cc.get_trendbars(sym_id, "H_1", iso(frm), iso(to)):
            ts = b["timestamp"]
            rows[ts] = {"timestamp_ms": ts,
                        "datetime_utc": datetime.fromtimestamp(ts / 1000, timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        "open": b["open"] / DIVISOR, "high": b["high"] / DIVISOR,
                        "low": b["low"] / DIVISOR, "close": b["close"] / DIVISOR,
                        "volume": b.get("volume", 0)}
        calls += 1
        frm = to
        if calls % 100 == 0:
            print(f"[{name}] calls={calls} rows={len(rows)} reached={frm:%Y-%m-%d}", flush=True)
        time.sleep(0.1)
    with open(path, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        for ts in sorted(rows):
            w.writerow(rows[ts])
    print(f"[{name}] done: {len(rows)} bars -> {path.name}", flush=True)


if __name__ == "__main__":
    for n, sid in SYMBOLS.items():
        download(n, sid)
