"""Combine Dukascopy daily minute files (seconds-from-midnight UTC, o, h, l, c, volume) into one 5-minute CSV
(timestamp_ms, datetime_utc, open, high, low, close, volume) for noise_band.py. Usage: duka_to_m5.py indir out.csv"""
import os, sys, csv
from datetime import datetime, timezone, date
src, out = sys.argv[1], sys.argv[2]; n = 0
with open(out, "w", newline="") as fo:
    w = csv.writer(fo); w.writerow(["timestamp_ms", "datetime_utc", "open", "high", "low", "close", "volume"])
    for fn in sorted(f for f in os.listdir(src) if f.endswith(".csv")):
        d = date.fromisoformat(fn[:10]); base = int(datetime(d.year, d.month, d.day, tzinfo=timezone.utc).timestamp())
        buckets = {}
        for line in open(os.path.join(src, fn)):
            p = line.strip().split(",")
            if len(p) < 6: continue
            t, o, h, l, c, v = int(p[0]), float(p[1]), float(p[2]), float(p[3]), float(p[4]), float(p[5])
            if h == l == o == c and v == 0: continue
            k = t - t % 300; b = buckets.get(k)
            if b is None: buckets[k] = [o, h, l, c, v]
            else: b[1] = max(b[1], h); b[2] = min(b[2], l); b[3] = c; b[4] += v
        for k in sorted(buckets):
            o, h, l, c, v = buckets[k]; ts = base + k
            w.writerow([ts * 1000, datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%d %H:%M"), o, h, l, c, round(v * 1e6)])
            n += 1
print(n, "five-minute bars")
