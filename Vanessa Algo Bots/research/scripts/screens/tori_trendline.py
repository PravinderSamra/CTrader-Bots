"""Tori Trades trend-line break, 4-hour, coded mechanically. Screening only.
Short side on a break of a rising 'action line' (longs = same code on inverted prices).
  Action line: from A = the lowest low of the last LOOK bars, the steepest line that no earlier low (up to the previous
    bar) sits below by more than TOL x ATR - i.e. the support tangent, which pivots to each new low (her 'fan' of
    lines, previous point B becomes the pivot). Touches = swing lows (2 bars each side) within TOL x ATR of the line.
  Break: a 4h close below the line by > 0.1 x ATR.
  Safety line: from the highest high of the last LOOK bars (before the break), the falling resistance tangent over
    later highs. Needs at least one lower swing high (no lower high = no safety line = no trade, as she says).
  Entry rules (her playbook): touches >= MINT (3 = A+, 2 = second playbook); A at least 30 bars (~1 week) before the
    break; 'low risk' = safety line no more than MAXR x ATR above the entry.
  Stop: on the safety line + 0.2 ATR, trailed along it every bar (never loosened); exit when hit; max 120 bars.
Costs per round trip: EURUSD 0.00007, XAUUSD 0.35, NAS100 1.5, XPTUSD 2.0."""
import csv, glob, json, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone

ROOT = "/home/user/CTrader-Bots"
SP = "/tmp/claude-0/-home-user-CTrader-Bots/05dd4dd7-22e7-57bf-8cec-d6a0c9610eea/scratchpad"
COST = {"EURUSD": 0.00007, "XAUUSD": 0.35, "NAS100": 1.5, "XPTUSD": 2.0}
LOOK, TOL = 180, 0.3


def to4h(rows):
    out = []
    for t, o, h, l, c in rows:
        k = t.replace(hour=t.hour - t.hour % 4, minute=0, second=0)
        if out and out[-1][0] == k:
            out[-1][2] = max(out[-1][2], h); out[-1][3] = min(out[-1][3], l); out[-1][4] = c
        else:
            out.append([k, o, h, l, c])
    return [tuple(x) for x in out]


def load(m):
    rows = []
    if m == "EURUSD":
        for r in csv.DictReader(open(f"{ROOT}/Vanessa Algo Bots/research/data/eurusd_h1.csv")):
            rows.append((datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc),
                         float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    elif m == "NAS100":
        for f in (f"{ROOT}/Vanessa Algo Bots/research/data/nas100_m30/nas100_m30_2021_2023.csv",
                  f"{ROOT}/US30 London Range Breakout/data/NAS100/nas100_m5.csv"):
            for r in csv.DictReader(open(f)):
                t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
                if rows and t <= rows[-1][0]: continue
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    elif m == "XAUUSD":
        for f in sorted(glob.glob(f"{ROOT}/XAUUSD historical Pricing data/data/XAUUSD_M_1_*.csv")):
            for r in csv.DictReader(open(f)):
                t = datetime.strptime(r["datetime"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                rows.append((t, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    else:
        r = json.load(open(f"{SP}/plat/pl_1h.json"))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
        for t, o, h, l, c in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"]):
            if None not in (o, h, l, c):
                rows.append((datetime.fromtimestamp(t, timezone.utc), o, h, l, c))
    return to4h(rows)


def run(b, cost, mint, maxr):
    n = len(b); atr = [None] * n
    for i in range(15, n):
        atr[i] = st.mean(max(b[j][2], b[j - 1][4]) - min(b[j][3], b[j - 1][4]) for j in range(i - 13, i + 1))
    piv_lo = [2 <= i < n - 2 and b[i][3] <= min(b[j][3] for j in range(i - 2, i + 3)) for i in range(n)]
    piv_hi = [2 <= i < n - 2 and b[i][2] >= max(b[j][2] for j in range(i - 2, i + 3)) for i in range(n)]
    tr = []; i = LOOK + 20
    while i < n - 1:
        a = atr[i - 1]; lo0 = i - LOOK
        A = min(range(lo0, i), key=lambda k: b[k][3])
        if i - A < 30 or A >= i - 3:
            i += 1; continue
        # support tangent from A over lows A+1 .. i-1 (pivots must be confirmed: use lows up to i-1)
        s = min((b[k][3] + TOL * a - b[A][3]) / (k - A) for k in range(A + 1, i))
        if s <= 0:
            i += 1; continue
        line = lambda k: b[A][3] + s * (k - A)
        if not b[i][4] < line(i) - 0.1 * a:
            i += 1; continue
        touches = sum(1 for k in range(A, i - 2) if piv_lo[k] and abs(b[k][3] - line(k)) <= TOL * a)
        # safety line: resistance tangent from the highest high before the break
        H = max(range(lo0, i), key=lambda k: b[k][2])
        later = [k for k in range(H + 3, i - 2) if piv_hi[k]]
        if not later or touches < mint:
            i += 1; continue
        hs = max((b[k][2] - TOL * a - b[H][2]) / (k - H) for k in range(H + 1, i))
        if hs >= 0:
            i += 1; continue
        safe = lambda k: b[H][2] + hs * (k - H)
        e = b[i][4]; stop = safe(i) + 0.2 * a; risk = stop - e
        if not (0.3 * a <= risk <= maxr * a):
            i += 1; continue
        x = None
        for k in range(i + 1, min(i + 121, n)):
            stop = min(stop, safe(k) + 0.2 * a)
            if b[k][2] >= stop: x = max(stop, b[k][1]); break
        if x is None: k = min(i + 120, n - 1); x = b[k][4]
        tr.append((b[i][0], (e - x - cost) / risk))
        i = k + 1
    return tr


def inv(b):
    return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


if __name__ == "__main__":
    for m in sys.argv[1:] or ["XPTUSD", "XAUUSD", "NAS100", "EURUSD"]:
        b = load(m)
        print(f"== {m} {b[0][0]:%Y-%m} .. {b[-1][0]:%Y-%m}  ({len(b)} 4h bars)")
        for mint in (3, 2):
            for maxr in (2.0, 4.0):
                for side, bb in (("short", b), ("long", inv(b))):
                    t = run(bb, COST[m], mint, maxr)
                    if not t: print(f"  touches>={mint} risk<={maxr}ATR {side:5s} no trades"); continue
                    rs = [r for _, r in t]; yr = defaultdict(float)
                    for d, r in t: yr[d.year] += r
                    print(f"  touches>={mint} risk<={maxr}ATR {side:5s} n={len(rs):3d} win={sum(r > 0 for r in rs)/len(rs):4.0%} "
                          f"avg={st.mean(rs):+.2f}R tot={sum(rs):+6.1f}R  " + " ".join(f"{y%100:02d}:{v:+.0f}" for y, v in sorted(yr.items())))
