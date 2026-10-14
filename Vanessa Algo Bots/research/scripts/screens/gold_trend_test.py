"""Pre-registered 14 Oct 2026: is Deni Fib on gold an edge or just gold's 2021-26 uptrend?
Unseen data: gold H1 2012-01 .. 2021-06 (cTrader download, data/xauusd_h1_2012_2021).
Frozen Deni rules (H1, 50-bar top, 0.618 limit, stop top + 0.1 ATR, target -0.272, order 30 bars, max hold 120),
HONEST fills: a bar that reaches the entry fills even if it also runs through the stop (then it is a loss).
A 'with the trend': buys only when the last daily close > its 200-day SMA, sells only when below.
B 'buys only' (no filter): is it just gold drifting up?   C all trades (no filter), for reference.
PASS (A): >= +0.10R per trade over 2012-2021 and positive in most years."""
import csv, statistics as st
from collections import defaultdict
from datetime import datetime, timezone
from tradingcafe import atr_of, fractals, inv
from fib_tune import summ

F = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/xauusd_h1_2012_2021/xauusd_h1.csv"
COST, SWAP = 0.35, 0.06 / 365


def load():
    b = []
    for r in csv.DictReader(open(F)):
        b.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc), float(r["open"]), float(r["high"]),
                  float(r["low"]), float(r["close"])))
    return b


def trend_map(b):
    """date -> +1 if the previous completed day's close > its 200-day SMA, -1 if below"""
    dc = {}
    for t, *_, c in b: dc[t.date()] = c
    days = sorted(dc); out = {}
    for i in range(201, len(days)):
        prev = [dc[d] for d in days[i - 200:i]]
        out[days[i]] = 1 if dc[days[i - 1]] > sum(prev) / 200 else -1
    return out


def fib_honest(b, sign, allow):
    """sign -1: sells on raw bars; +1: buys on inverted bars. allow(date) -> bool"""
    bb = b if sign < 0 else inv(b)
    A = atr_of(bb); hi, lo = fractals(bb); tr = []; busy = -1
    for H in hi:
        if H <= busy or H < 50 or A[H] is None: continue
        if bb[H][2] < max(x[2] for x in bb[H - 50:H]): continue
        prior = [j for j in lo if H - 50 < j < H]
        if not prior: continue
        sl = bb[prior[-1]][3]; top = bb[H][2]; brk = None
        for m in range(H + 1, min(H + 40, len(bb))):
            if bb[m][2] > top: break
            if bb[m][4] < sl: brk = m; break
        if brk is None or not allow(bb[brk][0].date()): continue
        L = min(x[3] for x in bb[H:brk + 1]); fill = None; e = None
        for m in range(brk + 1, min(brk + 31, len(bb))):
            lvl = L + 0.618 * (top - L)
            if bb[m][2] >= lvl: fill = m; e = max(lvl, bb[m][1]); break
            if bb[m][2] > top: break
            L = min(L, bb[m][3])
        if fill is None: continue
        rng = top - L; stop = top + 0.1 * A[H]; r = stop - e
        if r <= 0: continue
        tgt = L - 0.272 * rng; x = None; xi = fill
        if bb[fill][2] >= stop: x = stop
        else:
            for k in range(fill + 1, min(fill + 121, len(bb))):
                xi = k
                if bb[k][2] >= stop: x = stop; break
                if bb[k][3] <= tgt: x = tgt; break
            if x is None: x = bb[xi][4]
        nights = (bb[xi][0] - bb[fill][0]).days
        tr.append((bb[fill][0], (e - x - COST - abs(e) * SWAP * nights) / r, 0)); busy = xi
    return tr


if __name__ == "__main__":
    b = load(); tm = trend_map(b)
    lo_, hi_ = datetime(2012, 1, 1, tzinfo=timezone.utc), datetime(2021, 7, 1, tzinfo=timezone.utc)
    cut = lambda tr: sorted(t for t in tr if lo_ <= t[0] < hi_)
    A = cut(fib_honest(b, 1, lambda d: tm.get(d) == 1) + fib_honest(b, -1, lambda d: tm.get(d) == -1))
    B = cut(fib_honest(b, 1, lambda d: True))
    S = cut(fib_honest(b, -1, lambda d: True))
    print("gold H1 2012-01..2021-06 (unseen), honest fills, costs + swap")
    print(summ("A with the 200-day trend", A))
    print(summ("B buys only", B))
    print(summ("  sells only (reference)", S))
    print(summ("C all trades (reference)", sorted(B + S)))
    # gold's own drift over the period, for context
    print(f"gold {b[0][4]:.0f} (mid-2011) -> {b[-1][4]:.0f} (mid-2021)")
