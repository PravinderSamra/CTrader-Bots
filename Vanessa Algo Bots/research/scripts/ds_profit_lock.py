"""Daily Systems profit-lock test (pre-registered 13 Oct 2026): 2020-2023 ONLY, daily bars (Pepperstone D1 via cTrader).
A Pavel MR: close < SMA5 and (SMA5 - close) > 2.5 x mean |close - SMA5| of the previous 20 days, close > SMA200;
  exit on a close > SMA5 or after 4 days.  D Naoufel: RSI(2) < 20 and close > SMA200; exit RSI(2) > 70.
Entry/exit at the next day's open (the bot trades ~60 min after the open). Catastrophe stop 3 x ATR(20) below entry.
$13,000 notional per position; spread per round trip (NAS 1.5, US30 2.5, GER40 1.5, US500 0.6, gold 0.35);
swap 8%/yr of notional per night.
Switches: BE = once the high is >= entry + 1 x ATR(20), stop moves to entry.
          TRAIL = stop follows the highest close since entry minus 2 x ATR(20) (never loosens, never below the cat stop).
Keep a switch only if profit rises or max drawdown falls, and the win rate stays >= 65%."""
import csv, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone, date

D = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/d1_2019_2023"
MK = {"US500": 0.6, "NAS100": 1.5, "US30": 2.5, "GER40": 1.5, "XAUUSD": 0.35}
NOTIONAL, SWAP = 13000, 0.08 / 365


def load(m):
    out = []
    for r in csv.DictReader(open(f"{D}/{m.lower()}_d1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
        # fold the short Sunday session into Monday
        if out and t.weekday() == 0 and out[-1][0].weekday() == 6:
            p = out.pop(); o = p[1]; h = max(h, p[2]); l = min(l, p[3])
        out.append((t, o, h, l, c))
    return out


def rsi2(c):
    o = [None] * len(c); g = l = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if i <= 2: g += max(d, 0) / 2; l += max(-d, 0) / 2
        else: g = (g + max(d, 0)) / 2; l = (l + max(-d, 0)) / 2
        if i >= 2: o[i] = 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    return o


def run(b, spread, system, be, trail, be_k=1.0, tr_k=2.0):
    c = [x[4] for x in b]; n = len(b)
    sma = lambda i, k: sum(c[i - k + 1:i + 1]) / k
    atr = [None] * n
    for i in range(21, n):
        atr[i] = st.mean(max(b[j][2], b[j - 1][4]) - min(b[j][3], b[j - 1][4]) for j in range(i - 19, i + 1))
    R = rsi2(c); trades = []; i = 220
    while i < n - 2:
        d = b[i][0].date()
        if not (date(2020, 1, 1) <= d <= date(2023, 12, 31)): i += 1; continue
        s5, s200 = sma(i, 5), sma(i, 200)
        if system == "A":
            gaps = [abs(c[j] - sma(j, 5)) for j in range(i - 20, i)]
            sig = c[i] < s5 and (s5 - c[i]) > 2.5 * st.mean(gaps) and c[i] > s200
        else:
            sig = R[i] is not None and R[i] < 20 and c[i] > s200
        if not sig: i += 1; continue
        k = i + 1; e = b[k][1]; a = atr[i]; units = NOTIONAL / e
        stop = e - 3 * a; hc = e; x = None; held = 0
        j = k
        while j < n - 1:
            t, o, h, l, cl = b[j]
            if j > k and o <= stop: x = o; break          # gapped through the stop
            if l <= stop: x = stop; break
            if be and h >= e + be_k * a: stop = max(stop, e)
            hc = max(hc, cl)
            if trail: stop = max(stop, hc - tr_k * a)
            if system == "A": done = cl > sma(j, 5) or j - i >= 4
            else: done = R[j] is not None and R[j] > 70
            if done: x = b[j + 1][1]; j += 1; break
            j += 1
        if x is None: x = b[j][4]
        nights = (b[j][0].date() - b[k][0].date()).days
        pnl = units * (x - e) - units * spread - NOTIONAL * SWAP * nights
        trades.append((b[j][0].date(), pnl)); i = j
    return trades


def stats(tr):
    tr = sorted(tr); eq = pk = dd = 0.0
    for _, p in tr: eq += p; pk = max(pk, eq); dd = max(dd, pk - eq)
    by = defaultdict(float)
    for d, p in tr: by[d.year] += p
    return len(tr), sum(p > 0 for _, p in tr) / len(tr), sum(p for _, p in tr), dd, by


if __name__ == "__main__":
    bars = {m: load(m) for m in MK}
    variants = [("baseline (live settings)", False, False, 1, 2), ("BE at 1 ATR", True, False, 1, 2),
                ("TRAIL 2 ATR", False, True, 1, 2), ("BE 1 ATR + TRAIL 2 ATR", True, True, 1, 2),
                ("sens: BE 0.5 ATR", True, False, 0.5, 2), ("sens: BE 1.5 ATR", True, False, 1.5, 2),
                ("sens: TRAIL 1.5 ATR", False, True, 1, 1.5), ("sens: TRAIL 3 ATR", False, True, 1, 3)]
    for name, be, trl, bk, tk in variants:
        allt = []; per = {}
        for m, sp in MK.items():
            t = run(bars[m], sp, "A", be, trl, bk, tk) + run(bars[m], sp, "D", be, trl, bk, tk)
            allt += t; per[m] = sum(p for _, p in t)
        n, w, tot, dd, by = stats(allt)
        print(f"{name:26s} n={n:3d} win={w:4.0%} total=${tot:+8,.0f} maxDD=${dd:6,.0f}  "
              + " ".join(f"{y}:{v:+6,.0f}" for y, v in sorted(by.items())) + "  | "
              + " ".join(f"{m}:{v:+,.0f}" for m, v in per.items()))
