"""The Trading Cafe book ('Six Figures From Scratch') strategies, coded mechanically. Screening only.
All on H1 unless said; both sides; costs per round trip in price (EURUSD 0.00007, GBPUSD 0.0001, gold 0.35, NAS 1.5).
Swings = 3-bar fractals, confirmed 3 bars later. ATR = 14-bar mean range.
1 SIMON M/W double top/bottom: run-up >= 2 ATR into peak 1; peak 2 within 5-40 bars, within 0.3 ATR of peak 1; neckline =
  lowest candle BODY between the peaks. After peak 2 is confirmed: sell stop at the neckline, stop = higher peak + 0.1 ATR,
  target 1:1. Cancel if price trades above the higher peak or 15 bars pass unfilled. Exit after 15 bars if not done.
2 DENI BOLLINGER pullback: H4 'strong move' = 2 of the last 3 H4 bars solid (body >= 60% of range, range >= 1.2 x H4 ATR)
  in one direction, H4 band width rising, H4 SMA20 sloping that way. Then within 24 H1 bars: an H1 bar touching the H1 SMA20
  (within 0.1 ATR) while H1 band width is below 5 bars ago, and an entry candle (engulfing or 50%-wick pin bar) -> enter at
  its close, stop beyond the 5-bar swing extreme, (a) target 1:1, (b) half at 1:1 then trail the rest on the outer band.
3 DENI FIBONACCI: an up-leg ending at a 50-bar high H is broken: price closes below the last swing low before H.
  Leg low L updates until filled. Sell limit at L + 0.618 (H - L), stop H + 0.1 ATR, target L - 0.272 (H - L) (~2.3R)
  or 1:1. Cancel if price trades above H or after 30 bars. Mirror for longs.
4 ALEX MORRIS supply/demand: consolidation = 2+ bars inside 1 ATR; breakout bar(s) push >= 1.5 ATR beyond it within 3 bars;
  zone = the last opposite-colour candle before the push (wick to wick). First return into a fresh zone + a reversal candle
  (pin bar / engulfer) closing back outside -> enter at its close, stop a few points beyond that candle, target just before
  the nearest fresh opposite zone; only if >= 2R. Zone dies when touched (traded or not) or closed through.
5 SID RSI/MACD (daily, also H1): RSI14 < 30 arms a long (low tracked while RSI <= 30); MACD(12,26,9) crosses up within
  10 bars -> buy at the close, stop = that low, exit at the first close with RSI >= 50. Shorts mirror at 70.
  Daily runs: 45 US stocks (Yahoo, cost 0.15%), NAS100 and gold, swap 0.03%/day."""
import csv, glob, json, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone

ROOT = "/home/user/CTrader-Bots"
SP = "/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad"
COST = {"EURUSD": 0.00007, "GBPUSD": 0.0001, "XAUUSD": 0.35, "NAS100": 1.5}


def agg(rows, hours):
    out = []
    for t, o, h, l, c in rows:
        k = t.replace(hour=t.hour - t.hour % hours, minute=0, second=0, microsecond=0)
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
    elif m == "NAS100":
        for f in (f"{ROOT}/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv",
                  f"{ROOT}/US30 London Range Breakout/data/NAS100/nas100_m5.csv"):
            for r in csv.DictReader(open(f)):
                t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
                if rows and t <= rows[-1][0]: continue
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    else:
        for f in sorted(glob.glob(f"{ROOT}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
            for line in open(f):
                if line[0] != "2": continue
                p = line.split(",")
                rows.append((datetime.strptime(p[0][:19], "%Y-%m-%dT%H:%M:%S").replace(tzinfo=timezone.utc),
                             float(p[1]), float(p[2]), float(p[3]), float(p[4])))
    return agg(rows, 1)


def atr_of(b, n=14):
    a = [None] * len(b)
    for i in range(n, len(b)):
        a[i] = st.mean(x[2] - x[3] for x in b[i - n + 1:i + 1])
    return a


def sma(v, n):
    o = [None] * len(v); s = 0
    for i, x in enumerate(v):
        s += x
        if i >= n: s -= v[i - n]
        if i >= n - 1: o[i] = s / n
    return o


def bbw(c, n=20):
    m = sma(c, n); w = [None] * len(c)
    for i in range(n - 1, len(c)):
        w[i] = st.pstdev(c[i - n + 1:i + 1])
    return m, w


def inv(b):
    return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


def fractals(b, k=3):
    hi = [i for i in range(k, len(b) - k) if b[i][2] == max(x[2] for x in b[i - k:i + k + 1])]
    lo = [i for i in range(k, len(b) - k) if b[i][3] == min(x[3] for x in b[i - k:i + k + 1])]
    return hi, lo


def manage(b, i0, e, stop, tgt, cost, maxbars, side=-1):
    """short-side manager on (possibly inverted) bars from bar i0 on; stop checked first. returns (exit_i, R)"""
    r = stop - e
    for m in range(i0, min(i0 + maxbars, len(b))):
        if b[m][2] >= stop: return m, (e - stop - cost) / r
        if b[m][3] <= tgt: return m, (e - tgt - cost) / r
    m = min(i0 + maxbars, len(b)) - 1
    return m, (e - b[m][4] - cost) / r


def is_pin_short(x):   # long upper wick, bearish rejection
    t, o, h, l, c = x; rng = h - l
    return rng > 0 and h - max(o, c) >= 0.5 * rng


def is_engulf_short(p, x):
    return x[4] < x[1] and p[4] > p[1] and x[4] <= p[1] and x[1] >= p[4]


# ---------- 1 Simon M top (short); W = inverted ----------
def simon_mw(b, cost):
    A = atr_of(b); hi, _ = fractals(b); tr = []; busy = -1
    for a_, z in zip(hi, hi[1:]):
        if z <= busy or A[a_] is None or not 5 <= z - a_ <= 40: continue
        p1, p2 = b[a_][2], b[z][2]; at = A[z]
        if abs(p1 - p2) > 0.3 * at: continue
        if a_ < 20 or p1 - min(x[3] for x in b[a_ - 20:a_]) < 2 * at: continue
        neck = min(min(x[1], x[4]) for x in b[a_ + 1:z])
        top = max(p1, p2); stop = top + 0.1 * at
        i = z + 3; fill = None
        for m in range(i + 1, min(i + 16, len(b))):
            if b[m][2] > top: break
            if b[m][3] <= neck: fill = m; break
        if fill is None: continue
        e = min(neck, b[fill][1]); r = stop - e
        if r <= 0: continue
        if b[fill][2] >= stop: tr.append((b[fill][0], (e - stop - cost) / r)); busy = fill; continue
        x, R = manage(b, fill + 1, e, stop, e - r, cost, 15)
        tr.append((b[fill][0], R)); busy = x
    return tr


# ---------- 2 Deni Bollinger pullback (short; long = inverted) ----------
def deni_bb(b, cost, trail):
    h4 = agg(b, 4); A4 = atr_of(h4); c4 = [x[4] for x in h4]; m4, w4 = bbw(c4)
    k4 = {x[0]: i for i, x in enumerate(h4)}
    A = atr_of(b); c = [x[4] for x in b]; m1, w1 = bbw(c)
    tr = []; i = 30; armed_until = -1
    while i < len(b) - 2:
        t = b[i][0]
        if t.hour % 4 == 0:   # a new H4 bar opens: evaluate the last 3 completed H4 bars
            j = k4.get(t) 
            if j and j >= 26 and A4[j - 1]:
                sol = sum(1 for x in h4[j - 3:j] if x[4] < x[1] and abs(x[4] - x[1]) >= 0.6 * (x[2] - x[3])
                          and x[2] - x[3] >= 1.2 * A4[j - 1])
                if sol >= 2 and w4[j - 1] > w4[j - 4] and m4[j - 1] < m4[j - 4]:
                    armed_until = i + 24
        if i <= armed_until and A[i] and w1[i] is not None and w1[i - 5] is not None:
            x = b[i]
            touch = x[2] >= m1[i] - 0.1 * A[i]
            if touch and w1[i] < w1[i - 5] and (is_pin_short(x) or is_engulf_short(b[i - 1], x)):
                e = x[4]; stop = max(y[2] for y in b[i - 4:i + 1]) + 0.05 * A[i]; r = stop - e
                if r > 0.2 * A[i]:
                    if not trail:
                        xi, R = manage(b, i + 1, e, stop, e - r, cost, 48)
                    else:   # half off at 1R, rest trails on the upper band (stop never loosens)
                        half = None; s = stop; xi = None
                        for m in range(i + 1, min(i + 120, len(b))):
                            if b[m][2] >= s:
                                rest = (e - s) / r; R = (half if half is not None else rest) * 0.5 + rest * 0.5; xi = m; break
                            if half is None and b[m][3] <= e - r: half = 1.0; s = min(s, e)
                            if half is not None and w1[m]: s = min(s, m1[m] + 2 * w1[m])
                        if xi is None:
                            xi = min(i + 119, len(b) - 1); rest = (e - b[xi][4]) / r
                            R = (half if half is not None else rest) * 0.5 + rest * 0.5
                        R -= cost / r
                    tr.append((t, R)); armed_until = -1; i = xi + 1; continue
        i += 1
    return tr


# ---------- 3 Deni Fibonacci 0.618 (short; long = inverted) ----------
def deni_fib(b, cost, tgt_mode):
    A = atr_of(b); hi, lo = fractals(b); tr = []
    lo_set = sorted(lo); busy = -1
    for H in hi:
        if H <= busy or H < 50 or A[H] is None: continue
        if b[H][2] < max(x[2] for x in b[H - 50:H]): continue
        prior = [j for j in lo_set if j < H and j > H - 50]
        if not prior: continue
        sl = b[prior[-1]][3]; top = b[H][2]
        # break of structure: a close below the last swing low before H
        brk = None
        for m in range(H + 1, min(H + 40, len(b))):
            if b[m][2] > top: break
            if b[m][4] < sl: brk = m; break
        if brk is None: continue
        L = min(x[3] for x in b[H:brk + 1]); fill = None
        for m in range(brk + 1, min(brk + 31, len(b))):
            ent = L + 0.618 * (top - L)
            if b[m][2] > top: break
            if b[m][2] >= ent: fill = m; break
            L = min(L, b[m][3])
        if fill is None: continue
        rng = top - L; e = max(L + 0.618 * rng, b[fill][1]); stop = top + 0.1 * A[H]; r = stop - e
        tgt = L - 0.272 * rng if tgt_mode == "fib" else e - r
        if b[fill][2] >= stop: tr.append((b[fill][0], (e - stop - cost) / r)); busy = fill; continue
        x, R = manage(b, fill + 1, e, stop, tgt, cost, 120)
        tr.append((b[fill][0], R)); busy = x
    return tr


# ---------- 4 Alex Morris supply & demand (both sides in one pass) ----------
def alex_sd(b, cost):
    A = atr_of(b); zones = []   # [side(+1 demand,-1 supply), lo, hi, born_i, alive]
    tr = []; i = 20; busy = -1
    while i < len(b) - 1:
        a = A[i - 1]
        if a:
            # new zones: consolidation ending at i-3..i-4, push in the next 3 bars
            j = i - 3
            base = b[j - 2:j + 1]
            if max(x[2] for x in base) - min(x[3] for x in base) <= a:
                bh = max(x[2] for x in base); bl = min(x[3] for x in base)
                push = b[j + 1:i + 1]
                if max(x[4] for x in push) >= bh + 1.5 * a:
                    reds = [x for x in b[j - 2:j + 2] if x[4] < x[1]]
                    if reds: zones.append([1, reds[-1][3], reds[-1][2], i, True])
                if min(x[4] for x in push) <= bl - 1.5 * a:
                    grn = [x for x in b[j - 2:j + 2] if x[4] > x[1]]
                    if grn: zones.append([-1, grn[-1][3], grn[-1][2], i, True])
        x = b[i]; p = b[i - 1]
        for z in zones:
            if not z[4] or z[3] >= i: continue
            side, zl, zh = z[0], z[1], z[2]
            if side == 1 and x[3] <= zh:
                z[4] = False
                if i <= busy or x[4] < zl: continue
                pin = (min(x[1], x[4]) - x[3]) >= 0.5 * (x[2] - x[3]) > 0
                eng = x[4] > x[1] and p[4] < p[1] and x[4] >= p[1] and x[1] <= p[4]
                if not (pin or eng) or x[4] <= zh: continue
                e = x[4]; stop = x[3] - 0.1 * a; r = e - stop
                opp = [y[1] for y in zones if y[4] and y[0] == -1 and y[1] > e]
                if not opp or r <= 0: continue
                tgt = min(opp) - 0.05 * a
                if tgt - e < 2 * r: continue
                xi, R = manage(inv(b[i + 1:i + 241]), 0, -e, -stop, -tgt, cost, 240)
                tr.append((x[0], R)); busy = i + 1 + xi
            elif side == -1 and x[2] >= zl:
                z[4] = False
                if i <= busy or x[4] > zh: continue
                pin = (x[2] - max(x[1], x[4])) >= 0.5 * (x[2] - x[3]) > 0
                eng = x[4] < x[1] and p[4] > p[1] and x[4] <= p[1] and x[1] >= p[4]
                if not (pin or eng) or x[4] >= zl: continue
                e = x[4]; stop = x[2] + 0.1 * a; r = stop - e
                opp = [y[2] for y in zones if y[4] and y[0] == 1 and y[2] < e]
                if not opp or r <= 0: continue
                tgt = max(opp) + 0.05 * a
                if e - tgt < 2 * r: continue
                xi, R = manage(b[i + 1:i + 241], 0, e, stop, tgt, cost, 240)
                tr.append((x[0], R)); busy = i + 1 + xi
        if len(zones) > 400: zones = [z for z in zones if z[4]][-200:]
        i += 1
    return tr


# ---------- 5 Sid RSI + MACD (long; short = inverted, RSI levels mirror automatically) ----------
def rsi(c, n=14):
    o = [None] * len(c); g = l = 0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if i <= n:
            g += max(d, 0) / n; l += max(-d, 0) / n
        else:
            g = (g * (n - 1) + max(d, 0)) / n; l = (l * (n - 1) + max(-d, 0)) / n
        if i >= n: o[i] = 100 if l == 0 else 100 - 100 / (1 + g / l)
    return o


def ema(v, n):
    a = 2 / (n + 1); e = None; o = []
    for x in v:
        e = x if e is None else e + a * (x - e); o.append(e)
    return o


def sid(b, cost_fn, swap_per_bar=0.0):
    """long side on b; for shorts pass inverted bars (RSI of -price = 100 - RSI)"""
    c = [x[4] for x in b]; R = rsi(c)
    mac = [x - y for x, y in zip(ema(c, 12), ema(c, 26))]; sig = ema(mac, 9)
    tr = []; i = 35; armed = None; low = None
    while i < len(b) - 1:
        if R[i] is not None and R[i] < 30:
            armed = i; low = b[i][3] if low is None else min(low, b[i][3])
        elif armed is not None and R[i] is not None and R[i] <= 30:
            low = min(low, b[i][3])
        if armed is not None and i - armed > 10: armed = None; low = None
        if armed is not None and mac[i] > sig[i] and mac[i - 1] <= sig[i - 1]:
            e = c[i]; stop = low; r = e - stop
            if r > 0:
                x = None
                for m in range(i + 1, len(b)):
                    if b[m][3] <= stop: x = stop; break
                    if R[m] >= 50: x = c[m]; break
                if x is None: m = len(b) - 1; x = c[m]
                held = m - i
                tr.append((b[i][0], (x - e - cost_fn(e) - abs(e) * swap_per_bar * held) / r))
                i = m + 1; armed = None; low = None; continue
        i += 1
    return tr


def summ(name, tr):
    if not tr: print(f"  {name:40s} no trades"); return
    tr = sorted(tr); rs = [r for _, r in tr]; yr = defaultdict(float)
    for t, r in tr: yr[t.year] += r
    eq = pk = dd = 0.0
    for r in rs: eq += r; pk = max(pk, eq); dd = max(dd, pk - eq)
    print(f"  {name:40s} n={len(rs):4d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.2f}R "
          f"tot={sum(rs):+6.1f}R dd={dd:5.1f}R  " + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))


def both(fn, b, *a):
    return fn(b, *a) + fn(inv(b), *a)


if __name__ == "__main__":
    which = sys.argv[1:] or ["EURUSD", "GBPUSD", "XAUUSD", "NAS100", "SID"]
    for m in which:
        if m == "SID":
            print("== SID daily")
            import first_red_day as frd
            tr = []
            for f in sorted(glob.glob(f"{SP}/ep/*.json")):
                d = frd.load(f)
                tr += sid(d, lambda e: 0.0015 * e, 0.0003) + sid(inv(d), lambda e: 0.0015 * abs(e), 0.0003)
            summ("Sid daily, 45 US stocks, longs+shorts", tr)
            tr = []
            for f in sorted(glob.glob(f"{SP}/ep/*.json")):
                tr += sid(frd.load(f), lambda e: 0.0015 * e, 0.0003)
            summ("Sid daily, 45 US stocks, longs only", tr)
            for mm in ("NAS100", "XAUUSD", "EURUSD", "GBPUSD"):
                h = load(mm); d = agg([(t.replace(hour=0), *x) for t, *x in h], 24)
                sw = 0.0 if mm in ("EURUSD", "GBPUSD") else 0.0003
                summ(f"Sid daily {mm} longs", sid(d, lambda e: COST[mm], sw))
                summ(f"Sid daily {mm} shorts", sid(inv(d), lambda e: COST[mm], sw))
                summ(f"Sid H1 {mm} both", sid(h, lambda e: COST[mm]) + sid(inv(h), lambda e: COST[mm]))
            continue
        b = load(m); cost = COST[m]
        print(f"== {m} H1 {b[0][0]:%Y-%m} .. {b[-1][0]:%Y-%m}")
        summ("Simon M/W, 1:1", both(simon_mw, b, cost))
        summ("Deni BB pullback, 1:1", both(deni_bb, b, cost, False))
        summ("Deni BB pullback, half 1:1 + band trail", both(deni_bb, b, cost, True))
        summ("Deni Fib 0.618, target -0.272", both(deni_fib, b, cost, "fib"))
        summ("Deni Fib 0.618, target 1:1", both(deni_fib, b, cost, "1r"))
        summ("Alex Morris S&D, >= 2R", alex_sd(b, cost))
