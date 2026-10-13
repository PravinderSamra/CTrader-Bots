"""Alex Temiz (Chart Fanatics) 'first red day' short, daily-bar approximation. Screening only.
Setup: at least K consecutive higher closes ending yesterday, total gain over that run >= G.
Trigger (today): price trades below yesterday's close (the 'red to green' line).
Entry: yesterday's close, or the open if it gapped below it. Optional: only days that gapped up.
Exit: today's close (day trade), or the close 2 days later (hold 3 days). The intraday 'reclaim the line' stop
can't be modelled on daily bars; a close back above the line shows up as a loss at the close.
One trade per run. Universe: FTMO's US stock CFDs (Yahoo daily, scratchpad/ep) and crypto (scratchpad/crypto).
Run: python3 -I first_red_day.py <scratchpad dir>"""
import glob
import json
import os
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timezone


def load(f):
    r = json.load(open(f))["chart"]["result"][0]
    q = r["indicators"]["quote"][0]
    out = []
    for i, t in enumerate(r["timestamp"]):
        o, h, l, c = q["open"][i], q["high"][i], q["low"][i], q["close"][i]
        if None in (o, h, l, c):
            continue
        out.append((datetime.fromtimestamp(t, timezone.utc), o, h, l, c))
    return out


def run(bars, K, G, gap_only, hold, cost):
    tr = []
    i = K + 1
    while i < len(bars) - hold:
        y = i - 1
        ok = all(bars[y - j][4] > bars[y - j - 1][4] for j in range(K))
        if ok and bars[y][4] / bars[y - K][4] - 1 >= G:
            t, o, h, l, c = bars[i]
            line = bars[y][4]
            if l < line and (not gap_only or o > line):
                e = min(o, line)
                x = bars[i + hold][4]
                tr.append((t, (e - x) / e - cost))
                # skip until the run is broken (one trade per run)
                i += 1
                while i < len(bars) and bars[i][4] > bars[i - 1][4]:
                    i += 1
                continue
        i += 1
    return tr


def summ(name, tr):
    if not tr:
        print(f"{name:44s} no trades"); return
    rs = [r for _, r in tr]
    yr = defaultdict(float)
    for t, r in tr:
        yr[t.year] += r
    print(f"{name:44s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs) * 100:+.2f}% "
          f"med={st.median(rs) * 100:+.2f}% worst={min(rs) * 100:+.1f}%  "
          + " ".join(f"{y % 100:02d}:{v * 100:+.0f}" for y, v in sorted(yr.items()) if v))


if __name__ == "__main__":
    sp = sys.argv[1]
    groups = {"stocks": (sorted(f for f in glob.glob(f"{sp}/ep/*.json") if os.path.basename(f) != "aapl.json"), 0.0015),
              "crypto": (sorted(glob.glob(f"{sp}/crypto/*.json")), 0.002)}
    for g, (files, cost) in groups.items():
        data = {os.path.basename(f)[:-5]: load(f) for f in files}
        print(f"== {g}: {len(data)} symbols")
        for K in (3, 4):
            for G in ((0.25, 0.5) if g == "stocks" else (0.3, 0.6)):
                for gap in (False, True):
                    for hold in (0, 2):
                        tr = []
                        for s, b in data.items():
                            tr += [(t, r) for t, r in run(b, K, G, gap, hold, cost)]
                        summ(f"K>={K} G>={G:.0%} gapup={int(gap)} hold={hold}", sorted(tr))
