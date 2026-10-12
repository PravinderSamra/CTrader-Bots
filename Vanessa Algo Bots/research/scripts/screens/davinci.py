"""Marco (Chart Fanatics) 'Da Vinci' liquidity model, coded mechanically. Screening only.
Bias (H1): the most recent sweep of a confirmed H1 swing point (2 bars each side). Swept a low -> longs only,
           swept a high -> shorts only.
Long setup on M5 (swings 3 bars each side, used only once confirmed):
  1. Engineered liquidity: a new swing high H_e that stays below the previous swing high H_prev (respects it),
     H_prev no older than 1 day. Target = H_prev.
  2. L_origin = last swing low before H_e. Wait for a new swing low L_int after H_e with L_int > L_origin
     (internal low where early buyers sit).
  3. Entry: limit at L_int (filled when price trades below it). Stop: L_origin - buffer ('liquidity block').
     Only if reward/risk to the target >= minrr. Setup dies if price trades below L_origin or above H_prev
     before the fill.
  4. Exit: target, stop, or end of the session. Optional break-even at +be R.
Short = mirror (run on the inverted price series). One position at a time."""
import csv
import glob
import json
import statistics as st
import sys
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

UK = ZoneInfo("Europe/London")


def load(kind):
    rows = []
    if kind == "gold":
        for f in sorted(glob.glob("/home/user/CTrader-Bots/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
            cur = None
            for r in csv.DictReader(open(f)):
                t = datetime.strptime(r["datetime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                b = t.replace(minute=t.minute - t.minute % 5)
                o, h, l, c = float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])
                if cur and cur[0] == b:
                    cur[2] = max(cur[2], h); cur[3] = min(cur[3], l); cur[4] = c
                else:
                    if cur: rows.append(tuple(cur))
                    cur = [b, o, h, l, c]
            rows.append(tuple(cur))
    else:
        for r in csv.DictReader(open("/home/user/CTrader-Bots/US30 London Range Breakout/data/NAS100/nas100_m5.csv")):
            t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
            rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    return [(t.astimezone(UK),) + x[1:] for x in rows for t in [x[0]]]


def h1_bias(bars):
    """bias per M5 bar from H1 sweeps, using only finished H1 bars"""
    h1 = []
    for t, o, h, l, c in bars:
        k = t.replace(minute=0)
        if h1 and h1[-1][0] == k:
            h1[-1][2] = max(h1[-1][2], h); h1[-1][3] = min(h1[-1][3], l)
        else:
            h1.append([k, o, h, l, c])
    bias_at, sh, sl, bias = {}, [], [], 0
    for i in range(len(h1)):
        j = i - 2
        if j >= 2:
            if h1[j][2] == max(x[2] for x in h1[j - 2:j + 3]): sh.append(h1[j][2])
            if h1[j][3] == min(x[3] for x in h1[j - 2:j + 3]): sl.append(h1[j][3])
        hi, lo = h1[i][2], h1[i][3]
        if any(lo < s for s in sl[-6:]): bias = 1
        if any(hi > s for s in sh[-6:]): bias = -1 if not any(lo < s for s in sl[-6:]) else 0
        sl = [s for s in sl if s <= lo]; sh = [s for s in sh if s >= hi]
        bias_at[h1[i][0]] = bias
    out = []
    for t, *_ in bars:
        prev = t.replace(minute=0)
        out.append(bias_at.get(prev - timedelta(hours=1), 0))
    return out


def run_side(bars, bias, side, cost, buf, minrr, be, s0, s1, k=3):
    if side == -1:
        bars = [(t, -o, -l, -h, -c) for t, o, h, l, c in bars]
    trades, sh, sl = [], [], []
    setup = pend = pos = None
    for i, (t, o, h, l, c) in enumerate(bars):
        hr = t.hour + t.minute / 60
        day_end = hr >= s1 or (i + 1 < len(bars) and bars[i + 1][0].date() != t.date())
        if pos:
            e, stop, tgt, risk, d = pos
            ex = None
            if l <= stop: ex = stop
            elif h >= tgt: ex = tgt
            elif day_end: ex = c
            if ex is None and be and h >= e + be * risk: pos = (e, max(stop, e), tgt, risk, d)
            if ex is not None:
                trades.append((d, side, (ex - e - cost) / risk)); pos = None
            continue
        if pend:
            e, stop, tgt = pend
            if l <= stop or h >= tgt or day_end or hr < s0:
                pend = None
            elif l <= e:
                fill = min(o, e)
                if fill > stop:
                    pos = (fill, stop, tgt, fill - stop, t.date()); pend = None
                    if l <= stop:
                        trades.append((t.date(), side, (stop - fill - cost) / (fill - stop))); pos = None
                    continue
        j = i - k
        if j >= k:
            if bars[j][2] == max(x[2] for x in bars[j - k:j + k + 1]): sh.append((j, bars[j][2]))
            if bars[j][3] == min(x[3] for x in bars[j - k:j + k + 1]): sl.append((j, bars[j][3]))
            if sh and sh[-1][0] == j and len(sh) >= 2 and bias[i] == side:
                hp, he = sh[-2], sh[-1]
                lo_before = [x for x in sl if x[0] < he[0]]
                if he[1] < hp[1] and j - hp[0] <= 288 and lo_before:
                    setup = (hp[1], lo_before[-1][1], he[0])
            if setup and sl and sl[-1][0] == j and j > setup[2]:
                tgt, lorig, _ = setup
                lint = sl[-1][1]
                if lint > lorig and not pend and not pos:
                    stop = lorig - buf
                    if (tgt - lint) >= minrr * (lint - stop) and s0 <= hr < s1 and lint - stop > 0:
                        pend = (lint, stop, tgt)
                setup = None
        if setup and (l < setup[1] or h > setup[0]):
            setup = None
    return trades


def report(name, t, bot):
    if not t:
        print(name, "no trades"); return
    rs = [x[2] for x in t]
    yr = defaultdict(float)
    for x in t: yr[x[0].year] += x[2]
    eq = pk = dd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    dv = defaultdict(float)
    for x in t: dv[x[0].strftime("%Y%m%d")] += x[2]
    com = [d for d in dv if d in bot]
    corr = st.correlation([bot[d] for d in com], [dv[d] for d in com]) if len(com) > 5 else float("nan")
    print(f"{name:30s} n={len(rs):4d} win={sum(r > 0 for r in rs) / len(rs):4.0%} avg={st.mean(rs):+.3f}R "
          f"tot={sum(rs):+6.1f}R dd={dd:5.1f}R corr={corr:+.2f} | "
          + " ".join(f"{y}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    kind = sys.argv[1]
    bars = load(kind)
    bias = h1_bias(bars)
    bot = dict(zip(*json.load(open(sys.argv[2])).values()))
    if kind == "gold":
        buf, costs, s0, s1 = 0.3, (0.0, 0.3, 0.5), 7, 20
    else:
        buf, costs, s0, s1 = 2.0, (0.0, 1.2, 1.8), 7, 20.5
    for cost in costs:
        for minrr, be in ((3, 0), (3, 2), (2, 0), (5, 0)):
            t = run_side(bars, bias, 1, cost, buf, minrr, be, s0, s1) + run_side(bars, bias, -1, cost, buf, minrr, be, s0, s1)
            t.sort(key=lambda x: x[0])
            report(f"{kind} cost {cost} rr>={minrr} be{be}", t, bot)
    t = run_side(bars, [1] * len(bars), 1, costs[1], buf, 3, 0, s0, s1) + run_side(bars, [-1] * len(bars), -1, costs[1], buf, 3, 0, s0, s1)
    report(f"{kind} no bias rr>=3", sorted(t, key=lambda x: x[0]), bot)
