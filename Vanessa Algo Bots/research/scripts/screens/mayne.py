"""Trader Mayne (Chart Fanatics) HTF order block + LTF breaker framework, coded mechanically. Screening only.
HTF = daily (day starts 22:00 UTC), LTF = H1. 3-candle swings on both. Long side; shorts = same code on inverted prices.
  1. Daily market structure break (MSB): daily close above the last confirmed daily swing high.
  2. Range: the lowest low since that swing high (L) up to the highest high since (RH, keeps extending until entry).
  3. Order block: last down daily candle at or before L; zone = L .. that candle's high.
     Optional filter: zone top in the discount half of the range.
  4. Entry, version 'htf': limit buy at the zone top; stop under L.
     Entry, version 'ltf' (his breaker): once price is in the zone, wait on H1 for a confirmed swing low, a sweep
     below it, then an H1 close above the last H1 swing high before the sweep. Enter at that close, stop under
     the sweep low.
  5. Only if reward to RH >= 2x risk. Target RH. Variant: stop to break-even at +2R. Up to 2 shots per setup.
  6. Setup dies on a daily close below L, a new MSB either way, or 40 days.
Costs are a round-trip spread+commission in price units per market."""
import csv
import glob
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone

ROOT = "/home/user/CTrader-Bots"


def h1_from(rows):
    out = []
    for t, o, h, l, c in rows:
        k = t.replace(minute=0, second=0)
        if out and out[-1][0] == k:
            out[-1][2] = max(out[-1][2], h); out[-1][3] = min(out[-1][3], l); out[-1][4] = c
        else:
            out.append([k, o, h, l, c])
    return [tuple(x) for x in out]


def load(m):
    rows = []
    if m in ("EURUSD", "GBPUSD"):
        for r in csv.DictReader(open(f"{ROOT}/Vanessa Algo Bots/research/data/{m.lower()}_h1.csv")):
            rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc),
                         float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
        return rows
    if m == "NAS100":
        for f in (f"{ROOT}/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv",
                  f"{ROOT}/US30 London Range Breakout/data/NAS100/nas100_m5.csv"):
            for r in csv.DictReader(open(f)):
                t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
                if rows and t <= rows[-1][0]:
                    continue
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
        return h1_from(rows)
    for f in sorted(glob.glob(f"{ROOT}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
        for r in csv.DictReader(open(f)):
            t = datetime.strptime(r["datetime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return h1_from(rows)


COST = {"EURUSD": 0.00007, "GBPUSD": 0.0001, "NAS100": 1.5, "XAUUSD": 0.35}


def daily_of(h1):
    d, idx = [], []
    for t, o, h, l, c in h1:
        k = (t + timedelta(hours=2)).date()
        if d and d[-1][0] == k:
            d[-1][2] = max(d[-1][2], h); d[-1][3] = min(d[-1][3], l); d[-1][4] = c
        else:
            d.append([k, o, h, l, c])
        idx.append(len(d) - 1)
    return d, idx


def run(h1, cost, mode, discount, be):
    d, didx = daily_of(h1)
    trades = []
    setup = None          # dict
    sh = None             # last confirmed daily swing high (price, index), unbroken
    sl_ = None            # last confirmed daily swing low (price, index), unbroken
    pos = None
    ltf = None            # LTF state inside zone
    last_day = -1
    for i, (t, o, h, l, c) in enumerate(h1):
        di = didx[i]
        # --- manage open position on this H1 bar
        if pos:
            if l <= pos["stop"]:
                trades.append((pos["t"], (pos["stop"] - pos["e"] - cost) / pos["r"])); pos = None
            elif h >= pos["tp"]:
                trades.append((pos["t"], (pos["tp"] - pos["e"] - cost) / pos["r"])); pos = None
            else:
                if be and h >= pos["e"] + 2 * pos["r"]:
                    pos["stop"] = max(pos["stop"], pos["e"])
                if (t - pos["t"]).days > 40:
                    trades.append((pos["t"], (c - pos["e"] - cost) / pos["r"])); pos = None
        # --- daily close processing when a new day starts
        if di != last_day and di >= 1:
            j = di - 1   # finished day
            dj = d[j]
            if j >= 2:   # confirm swings centred at j-1
                a, b, cc = d[j - 2], d[j - 1], d[j]
                if b[2] > a[2] and b[2] > cc[2]:
                    sh = (b[2], j - 1)
                if b[3] < a[3] and b[3] < cc[3]:
                    sl_ = (b[3], j - 1)
            if setup:
                if dj[4] < setup["L"] or j - setup["day"] > 40:
                    setup = None; ltf = None
                elif sl_ and dj[4] < sl_[0]:            # bearish MSB: trend changed
                    setup = None; ltf = None
            if sh and dj[4] > sh[0]:                    # bullish MSB
                lo_k = min(range(sh[1], j + 1), key=lambda k: d[k][3])
                L = d[lo_k][3]
                k = lo_k
                while k > 0 and not d[k][4] < d[k][1]:
                    k -= 1
                top = d[k][2]
                rh = max(d[k2][2] for k2 in range(lo_k, j + 1))
                if top > L:
                    setup = {"L": L, "top": top, "rh": rh, "day": j, "shots": 0, "touched": False}
                    ltf = None
                sh = None
            last_day = di
        if not setup or pos:
            continue
        s = setup
        if not s["touched"]:
            s["rh"] = max(s["rh"], h)
        mid = (s["L"] + s["rh"]) / 2
        if l <= s["top"] and not s["touched"]:
            s["touched"] = True
            if discount and s["top"] > mid:
                setup = None; continue
            ltf = {"bars": [], "swl": None, "swh": None, "swept": None}
            if mode == "htf":
                stop = s["L"] - cost
                e = min(s["top"], o)
                r = e - stop
                if r > 0 and (s["rh"] - e) >= 2 * r:
                    pos = {"t": t, "e": e, "stop": stop, "tp": s["rh"], "r": r}
                    if l <= stop:
                        trades.append((t, (stop - e - cost) / r)); pos = None
                setup = None
                continue
        if mode == "ltf" and s["touched"] and ltf is not None:
            bars = ltf["bars"]
            bars.append((h, l, c))
            n = len(bars)
            if n >= 3:
                a, b, cc = bars[-3], bars[-2], bars[-1]
                if b[0] > a[0] and b[0] > cc[0]:
                    ltf["swh"] = b[0]
                if b[1] < a[1] and b[1] < cc[1]:
                    ltf["swl"] = b[1]
            if ltf["swl"] is not None and l < ltf["swl"] and ltf["swept"] is None:
                ltf["swept"] = l; ltf["trig"] = ltf["swh"]
            if ltf["swept"] is not None:
                ltf["swept"] = min(ltf["swept"], l)
                if ltf["trig"] is not None and c > ltf["trig"]:
                    stop = ltf["swept"] - cost
                    r = c - stop
                    if r > 0 and (s["rh"] - c) >= 2 * r:
                        pos = {"t": t, "e": c, "stop": stop, "tp": s["rh"], "r": r}
                        s["shots"] += 1
                        if s["shots"] >= 2:
                            setup = None
                    ltf = {"bars": [], "swl": None, "swh": None, "swept": None}
    return trades


def inv(h1):
    return [(t, -o, -l, -h, -c) for t, o, h, l, c in h1]


def summ(name, tr):
    if not tr:
        print(f"{name:42s} no trades"); return
    rs = [r for _, r in tr]
    yr = defaultdict(float)
    for t, r in tr:
        yr[t.year] += r
    print(f"{name:42s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.2f}R tot={sum(rs):+7.1f}R  "
          + " ".join(f"{y % 100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    for m in sys.argv[1:] or ["EURUSD", "GBPUSD", "NAS100", "XAUUSD"]:
        h1 = load(m)
        print(f"== {m} {h1[0][0]:%Y-%m} .. {h1[-1][0]:%Y-%m}")
        for mode in ("htf", "ltf"):
            for disc in (False, True):
                for be in (False, True):
                    lg = run(h1, COST[m], mode, disc, be)
                    sh = run(inv(h1), COST[m], mode, disc, be)
                    tag = f"{mode} disc={int(disc)} be={int(be)}"
                    summ(tag + " long", lg)
                    summ(tag + " short", sh)
                    summ(tag + " both", sorted(lg + sh))
