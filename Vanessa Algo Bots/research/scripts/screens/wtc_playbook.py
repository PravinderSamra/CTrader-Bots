"""Wealth Training Company playbook (Vanessa's photos, 14 Oct 2026), coded mechanically. Screening only.
Market orders at bar closes (no resting limits), stop checked first inside a bar, costs + swap included.

EMA STRATEGY (Guy & Harry Robinson), long side (shorts = mirrored prices):
  100 EMA crosses above the 200 EMA. Afterwards price must touch the EMA zone (low <= 100 EMA) at least twice
  (separate touches); entry from the second touch on. Trigger bar: RSI(14) crosses up through 50 having been
  below 40 within 10 bars, AND CCI(20) crossed up through -100 within the last 3 bars, AND a momentum candle
  (bullish, body >= 50% of range) -> buy at the close. Stop below both EMAs (min(EMA200, 5-bar low) - 0.1 ATR).
  Target = the highest high of the last 50 bars; skip if < 1.5R. Break-even once +0.75R; close at -0.8R
  ('manually close at 0.8R loss'). Setup ends when the 100 EMA crosses back below the 200.
  Timeframes: H1, H4 (EURUSD, GBPUSD 2012-26, gold 2021-26) and daily (11 FX pairs + gold 2012-26).

BREAK & RETEST (Scarface & JDUB), NAS100 / US500 / US30 5-min:
  First 5-min candle of the NYSE open (09:30 NY) = zone. A 5-min CLOSE above the zone high = break (long).
  Retest: a later bar (not the bar right after the break) trades back to the zone high. The next candle must be
  strong (bullish, closes above the retest bar's high, body >= 50% of range) -> buy at its close.
  Stop just below the retest and entry candles' lows. Target 2R (variant 3R). Entries 09:35-11:00, flat 16:00,
  one trade a day. Filter variant: skip days whose zone sits inside yesterday's high-low range ('choppy')."""
import csv, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

NY = ZoneInfo("America/New_York")


def inv(b): return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


def ema(v, n):
    a = 2 / (n + 1); e = None; o = []
    for x in v:
        e = x if e is None else e + a * (x - e); o.append(e)
    return o


def rsi(c, n=14):
    o = [None] * len(c); g = l = 0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if i <= n: g += max(d, 0) / n; l += max(-d, 0) / n
        else: g = (g * (n - 1) + max(d, 0)) / n; l = (l * (n - 1) + max(-d, 0)) / n
        if i >= n: o[i] = 100 if l == 0 else 100 - 100 / (1 + g / l)
    return o


def cci(b, n=20):
    tp = [(x[2] + x[3] + x[4]) / 3 for x in b]; o = [None] * len(b)
    for i in range(n - 1, len(b)):
        w = tp[i - n + 1:i + 1]; m = sum(w) / n; md = sum(abs(x - m) for x in w) / n
        o[i] = 0 if md == 0 else (tp[i] - m) / (0.015 * md)
    return o


def ema_strategy(b, cost, swap):
    c = [x[4] for x in b]; n = len(b)
    e100, e200 = ema(c, 100), ema(c, 200); R = rsi(c); C = cci(b)
    atr = [None] * n
    for i in range(14, n): atr[i] = st.mean(x[2] - x[3] for x in b[i - 13:i + 1])
    tr = []; i = 210; armed = False; touches = 0; inzone = False
    while i < n - 1:
        if e100[i] > e200[i] and e100[i - 1] <= e200[i - 1]:
            armed = True; touches = 0; inzone = False
        if e100[i] < e200[i]: armed = False
        if armed:
            if b[i][3] <= e100[i]:
                if not inzone: touches += 1
                inzone = True
            else:
                inzone = False
            rsi_ok = R[i] is not None and R[i - 1] is not None and R[i - 1] < 50 <= R[i] and min(x for x in R[i - 10:i] if x is not None) < 40
            cci_ok = any(C[k] is not None and C[k - 1] is not None and C[k - 1] < -100 <= C[k] for k in range(i - 2, i + 1))
            t, o, h, l, cl = b[i]
            mom = cl > o and (cl - o) >= 0.5 * (h - l) > 0
            if touches >= 2 and rsi_ok and cci_ok and mom:
                e = cl; stop = min(e200[i], min(x[3] for x in b[i - 4:i + 1])) - 0.1 * atr[i]; r = e - stop
                tgt = max(x[2] for x in b[i - 50:i])
                if r > 0 and tgt - e >= 1.5 * r:
                    s = stop; x = None; j = i + 1
                    while j < min(i + 200, n):
                        if b[j][1] <= s: x = b[j][1]; break
                        if b[j][3] <= s: x = s; break
                        if b[j][2] >= tgt: x = tgt; break
                        if b[j][4] <= e - 0.8 * r: x = b[j][4]; break
                        if b[j][2] >= e + 0.75 * r: s = max(s, e)
                        j += 1
                    if x is None: j = min(j, n - 1); x = b[j][4]
                    nights = (b[j][0] - b[i][0]).days
                    tr.append((b[i][0], (x - e - cost - abs(e) * swap * nights) / r))
                    armed = False; i = j + 1; continue
        i += 1
    return tr


def break_retest(bars, cost, rr, choppy_filter):
    by = defaultdict(list)
    for i, x in enumerate(bars): by[x[0].astimezone(NY).date()].append(i)
    days = sorted(by); tr = []; prev = None
    for d in days:
        idx = [i for i in by[d] if (9, 30) <= (bars[i][0].astimezone(NY).hour, bars[i][0].astimezone(NY).minute) < (16, 0)]
        if len(idx) < 60:
            prev = None; continue
        first = bars[idx[0]]
        if bars[idx[0]][0].astimezone(NY).minute != 30: prev = None; continue
        zh, zl = first[2], first[3]
        ph = max(bars[i][2] for i in idx); pl = min(bars[i][3] for i in idx)
        skip = choppy_filter and prev is not None and prev[1] <= zl and zh <= prev[0]
        prev_day = (ph, pl)
        if skip: prev = prev_day; continue
        done = False
        for side in (1, -1):
            if done: break
            brk = None; ret = None
            for k in range(1, len(idx) - 1):
                i = idx[k]; t, o, h, l, c = bars[i]; lt = t.astimezone(NY)
                if (lt.hour, lt.minute) >= (11, 0): break
                if brk is None:
                    if (side == 1 and c > zh) or (side == -1 and c < zl): brk = k
                    continue
                if ret is None:
                    if k > brk + 1 and ((side == 1 and l <= zh) or (side == -1 and h >= zl)): ret = k
                    continue
                if k != ret + 1: break
                rb = bars[idx[ret]]
                strong = (side == 1 and c > o and c > rb[2] and (c - o) >= 0.5 * (h - l) > 0) or \
                         (side == -1 and c < o and c < rb[3] and (o - c) >= 0.5 * (h - l) > 0)
                if not strong: break
                e = c
                stop = (min(rb[3], l) - 0.5 * cost) if side == 1 else (max(rb[2], h) + 0.5 * cost)
                r = abs(e - stop)
                if r <= 0: break
                tgt = e + side * rr * r; x = None
                for m in idx[k + 1:]:
                    mt = bars[m]
                    if side == 1:
                        if mt[3] <= stop: x = stop; break
                        if mt[2] >= tgt: x = tgt; break
                    else:
                        if mt[2] >= stop: x = stop; break
                        if mt[3] <= tgt: x = tgt; break
                if x is None: x = bars[idx[-1]][4]
                tr.append((t, side * (x - e) / r - cost / r)); done = True
                break
        prev = prev_day
    return tr


def summ(name, tr):
    if not tr: print(f"  {name:44s} none"); return
    tr = sorted(tr); rs = [r for _, r in tr]; yr = defaultdict(float)
    for t, r in tr: yr[t.year] += r
    print(f"  {name:44s} n={len(rs):4d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.3f}R tot={sum(rs):+6.1f}R  "
          + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    if what in ("all", "ema"):
        import tradingcafe as tc, ali_crooks as ac
        print("== EMA STRATEGY")
        for m in ("EURUSD", "GBPUSD", "XAUUSD"):
            h1 = tc.load(m); sw = (0.06 if m == "XAUUSD" else 0.02) / 365
            for tf, b in (("H1", h1), ("H4", tc.agg(h1, 4))):
                summ(f"{m} {tf}", ema_strategy(b, tc.COST[m], sw) + ema_strategy(inv(b), tc.COST[m], sw))
        allt = []
        for name in sorted(ac.COST):
            b = ac.load(name)
            t = [x for x in ema_strategy(b, ac.COST[name], ac.SWAP[name]) + ema_strategy(inv(b), ac.COST[name], ac.SWAP[name]) if x[0].year >= 2012]
            allt += t
        summ("daily, 11 FX pairs + gold, 2012-26", allt)
    if what in ("all", "br"):
        import rajan_jade as rj
        print("== BREAK & RETEST (NYSE open, first 5-min candle)")
        for m, f, cost in (("NAS100 2020-23", "NAS100_2020_2023/nas100_m5_2020_2023.csv", 1.5), ("NAS100 2023-26", "NAS100/nas100_m5.csv", 1.5),
                           ("US500 2023-26", "US500/us500_m5.csv", 0.6), ("US30 2023-26", "US30/us30_m5.csv", 2.5)):
            b = rj.load(f)
            for rr in (2.0, 3.0):
                for flt in (False, True):
                    summ(f"{m} target {rr:.0f}R{' + choppy-day filter' if flt else ''}", break_retest(b, cost, rr, flt))
