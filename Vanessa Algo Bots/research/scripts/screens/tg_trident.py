"""TG Capital (Tyler, Chart Fanatics) 'trident' London setup, coded mechanically. Screening only.
30-minute bars, New York time. Long side as he trades it; shorts = same code on inverted prices.
  1. Bias: yesterday's daily close above the 200-day EMA (longs only then).
  2. EMA 5 > 9 > 13 > 21 on the 30m at the fair value gap candle.
  3. Bullish fair value gap (low of candle 3 > high of candle 1), candle 3 opening 02:30-06:00 NY.
  4. 'Doji': a later candle (by 06:30 NY) whose low reaches the gap's 50% (CE), closes above the CE, body <= 30% of range.
  5. The candle after the doji must close below the doji's high (else no trade). Enter at its close.
     Stop: below the doji low. Skip if the stop is under 0.5 x / over 3 x his typical size (10 pips FX).
  6. Exits: (a) target 20R; (b) target 5R; (c) trend ride: exit on a daily close below the daily EMA 9.
     All with the stop, max 20 trading days. One trade per day.
Costs per round trip: EURUSD 0.00007, XAUUSD 0.35, NAS100 1.5."""
import csv, glob, os, statistics as st, sys
RELAX = os.environ.get("RELAX") == "1"  # loose variant: body <= 50%, no EMA stack, no 200-EMA bias
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")
ROOT = "/home/user/CTrader-Bots"
COST = {"EURUSD": 0.00007, "XAUUSD": 0.35, "NAS100": 1.5}
TYP = {"EURUSD": 0.0010, "XAUUSD": 5.0, "NAS100": 40.0}


def load(m):
    rows = []
    if m == "NAS100":
        for r in csv.DictReader(open(f"{ROOT}/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
            rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc),
                         float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    else:
        pat = (f"{ROOT}/Vanessa Algo Bots/research/data/eurusd_m5/EURUSD_M_5_*.csv" if m == "EURUSD"
               else f"{ROOT}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")
        for f in sorted(glob.glob(pat)):
            for r in csv.DictReader(open(f)):
                t = datetime.strptime(r["datetime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    out = []
    for t, o, h, l, c in rows:
        k = t.replace(minute=t.minute - t.minute % 30, second=0)
        if out and out[-1][0] == k:
            out[-1][2] = max(out[-1][2], h); out[-1][3] = min(out[-1][3], l); out[-1][4] = c
        else:
            out.append([k, o, h, l, c])
    return [tuple(x) for x in out]


def ema_series(vals, n):
    a = 2 / (n + 1); out = []; e = None
    for v in vals:
        e = v if e is None else e + a * (v - e); out.append(e)
    return out


def run(bars, cost, typ, exit_mode):
    # daily bars on the NY 17:00 rollover
    dkey = [((t.astimezone(NY) + timedelta(hours=7)).date()) for t, *_ in bars]
    days, dclose = [], {}
    for i, k in enumerate(dkey):
        if not days or days[-1] != k: days.append(k)
        dclose[k] = bars[i][4]
    dc = [dclose[k] for k in days]
    e200 = dict(zip(days, ema_series(dc, 200))); e9 = dict(zip(days, ema_series(dc, 9)))
    didx = {k: i for i, k in enumerate(days)}
    closes = [b[4] for b in bars]
    E = {n: ema_series(closes, n) for n in (5, 9, 13, 21)}
    tr = []; i = 2; last_day = None
    while i < len(bars) - 3:
        t = bars[i][0].astimezone(NY); k = dkey[i]; j0 = didx[k]
        hm = t.hour * 60 + t.minute
        if not (150 <= hm <= 360) or j0 < 201 or k == last_day:
            i += 1; continue
        prev = days[j0 - 1]
        if not RELAX and not (dclose[prev] > e200[prev] and E[5][i] > E[9][i] > E[13][i] > E[21][i]):
            i += 1; continue
        h1 = bars[i - 2][2]; l3 = bars[i][3]
        if l3 <= h1:
            i += 1; continue
        ce = (h1 + l3) / 2; done = False
        for j in range(i + 1, min(i + 9, len(bars) - 2)):
            tj = bars[j][0].astimezone(NY); hmj = tj.hour * 60 + tj.minute
            if hmj > 390 or dkey[j] != k: break
            o, h, l, c = bars[j][1:]
            if l < h1: break                      # gap fully filled: setup gone
            if l <= ce and c > ce and h > l and abs(c - o) <= (0.5 if RELAX else 0.3) * (h - l):
                kk = j + 1
                if bars[kk][4] >= h:
                    break                         # closed above the doji high: invalid
                e = bars[kk][4]; stop = l - 0.1 * typ; r = e - stop
                if not (0.5 * typ <= r <= 3 * typ): break
                tgt = e + (20 if exit_mode == "20R" else 5) * r if exit_mode in ("20R", "5R") else None
                x = None
                for m in range(kk + 1, len(bars)):
                    if bars[m][3] <= stop: x = min(stop, bars[m][1]); break
                    if tgt and bars[m][2] >= tgt: x = max(tgt, bars[m][1]); break
                    km = dkey[m]
                    if exit_mode == "trend" and m + 1 < len(bars) and dkey[m + 1] != km and bars[m][4] < e9[km]:
                        x = bars[m][4]; break
                    if didx[km] - j0 > 20: x = bars[m][4]; break
                if x is None: x = bars[-1][4]
                tr.append((bars[kk][0], (x - e - cost) / r)); done = True
                break
        if done: last_day = k
        i += 1
    return tr


def inv(b):
    return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


if __name__ == "__main__":
    for m in sys.argv[1:] or ["EURUSD", "XAUUSD", "NAS100"]:
        b = load(m)
        print(f"== {m} {b[0][0]:%Y-%m} .. {b[-1][0]:%Y-%m}")
        for mode in ("20R", "5R", "trend"):
            for side, bb in (("long", b), ("short", inv(b))):
                t = run(bb, COST[m], TYP[m], mode)
                if not t: print(f"  {mode:5s} {side:5s} no trades"); continue
                rs = [r for _, r in t]; yr = defaultdict(float)
                for d, r in t: yr[d.year] += r
                print(f"  {mode:5s} {side:5s} n={len(rs):3d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.2f}R "
                      f"tot={sum(rs):+6.1f}R  " + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))
