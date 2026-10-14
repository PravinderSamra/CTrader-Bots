"""Break & Retest (Scarface & JDUB) on single US stocks, pre-registered 14 Oct 2026. Screening only.
20 stocks, 5-min regular-session bars Jan 2023 - Oct 2026 (cTrader feed, data/stocks_m5).
'Strength at the open': trade a stock only on days it gaps >= GAP% from the previous close, in the gap's
direction (main: GAP = 1.5%). Variant: all stocks, both directions (no gap filter).
Rules as the index version: first 5-min candle (09:30 NY) = zone; a 5-min close beyond it = break; a later bar
(not the next one) retests the zone edge; the next candle is strong (closes beyond the retest bar, body >= 50%)
-> enter at its close; stop beyond the retest + entry candles' extremes; target 2R (variant 3R);
entries 09:35-11:00, flat 16:00; one trade per stock per day. Cost 0.05% of price per round trip.
PASS: >= +0.10R per trade, positive in 2023-24 AND 2025-26, >= 150 trades."""
import csv, glob, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
D = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/stocks_m5"
COSTP = 0.0005


def load(f):
    out = []
    for r in csv.DictReader(open(f)):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        lt = t.astimezone(NY)
        if not ((9, 30) <= (lt.hour, lt.minute) < (16, 0)): continue
        out.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return out


def run(bars, gap_min, rr):
    by = defaultdict(list)
    for x in bars: by[x[0].astimezone(NY).date()].append(x)
    days = sorted(by); tr = []; prev_close = None
    for d in days:
        b = by[d]
        if len(b) < 70 or b[0][0].astimezone(NY).minute != 30:
            prev_close = b[-1][4] if b else prev_close; continue
        gap = (b[0][1] / prev_close - 1) if prev_close else 0
        prev_close = b[-1][4]
        if gap_min > 0:
            if abs(gap) < gap_min: continue
            sides = (1,) if gap > 0 else (-1,)
        else:
            sides = (1, -1)
        zh, zl = b[0][2], b[0][3]; cost = COSTP * b[0][1]; done = False
        for side in sides:
            if done: break
            brk = ret = None
            for k in range(1, len(b) - 1):
                t, o, h, l, c = b[k]; lt = t.astimezone(NY)
                if (lt.hour, lt.minute) >= (11, 0): break
                if brk is None:
                    if (side == 1 and c > zh) or (side == -1 and c < zl): brk = k
                    continue
                if ret is None:
                    if k > brk + 1 and ((side == 1 and l <= zh) or (side == -1 and h >= zl)): ret = k
                    continue
                if k != ret + 1: break
                rb = b[ret]
                strong = (side == 1 and c > o and c > rb[2] and (c - o) >= 0.5 * (h - l) > 0) or \
                         (side == -1 and c < o and c < rb[3] and (o - c) >= 0.5 * (h - l) > 0)
                if not strong: break
                e = c; stop = min(rb[3], l) if side == 1 else max(rb[2], h); r = abs(e - stop)
                if r <= 0: break
                tgt = e + side * rr * r; x = None
                for m in b[k + 1:]:
                    if side == 1:
                        if m[3] <= stop: x = stop; break
                        if m[2] >= tgt: x = tgt; break
                    else:
                        if m[2] >= stop: x = stop; break
                        if m[3] <= tgt: x = tgt; break
                if x is None: x = b[-1][4]
                tr.append((t, side * (x - e) / r - cost / r, cost / r)); done = True
                break
    return tr


def summ(name, tr):
    if not tr: print(f"  {name:40s} none"); return
    rs = [r for _, r, _ in tr]; yr = defaultdict(float)
    for t, r, _ in tr: yr[t.year] += r
    a = [r for t, r, _ in tr if t.year <= 2024]; z = [r for t, r, _ in tr if t.year >= 2025]
    print(f"  {name:40s} n={len(rs):5d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.3f}R tot={sum(rs):+7.1f}R "
          f"cost/trade={st.mean(c for *_, c in tr):.2f}R | 23-24 {st.mean(a) if a else 0:+.3f}R  25-26 {st.mean(z) if z else 0:+.3f}R  "
          + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    files = sorted(glob.glob(f"{D}/*_m5.csv"))
    data = {os.path.basename(f).split("_")[0].upper(): load(f) for f in files}
    print(f"{len(data)} stocks:", " ".join(sorted(data)))
    for gap, rr in ((0.015, 2.0), (0.015, 3.0), (0.03, 2.0), (0.0, 2.0)):
        allt = []; per = {}
        for s, b in data.items():
            t = run(b, gap, rr); allt += t; per[s] = (len(t), sum(r for _, r, _ in t))
        summ(f"gap>={gap:.1%} target {rr:.0f}R" if gap else f"no gap filter, both sides, {rr:.0f}R", sorted(allt))
        if gap == 0.015 and rr == 2.0:
            print("    per stock:", " ".join(f"{s}:{n}/{v:+.0f}R" for s, (n, v) in sorted(per.items())))
