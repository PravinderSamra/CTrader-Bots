"""Ali Crooks 'Trendline Break Pocket' (TradeZella), daily, coded mechanically. Pre-registered 14 Oct 2026.
Short side (longs = mirrored prices):
 1. Uptrend top: a daily swing high HH (2 bars each side) above the previous swing high.
 2. Key level: an earlier swing high (10-250 bars before) between HH - 1.0 ATR and HH + 0.5 ATR
    (price is at resistance; one overshoot allowed). Variant 'nolevel' skips this.
 3. Momentum/structure break: within 20 bars, a daily CLOSE below the last swing low before HH
    (the trendline from that higher low is necessarily broken first). Void if price trades above HH first.
 4. Entry 1: sell limit at the 21 EMA (yesterday's value) when price pulls back up to it; order lives 20 bars,
    void on a close above HH. Target = the low formed after the break (updated until filled).
    Stop = half the distance to the target above entry (fixed 2R). Same-bar fill + stop = loss (honest fills).
 5. Max hold 40 bars. Costs: spread + commission per round trip, swap per night.
PASS: >= +0.10R per trade over all markets 2012-2026, and positive in both 2012-18 and 2019-26."""
import csv, glob, os, statistics as st
from collections import defaultdict
from datetime import datetime, timezone

D = "/home/user/CTrader-Bots/Vanessa Algo Bots/research/data/fx_d1_2010_2026"
COST = {"eurusd": 0.0001, "gbpusd": 0.00012, "audusd": 0.00012, "nzdusd": 0.00015, "usdcad": 0.00015, "usdchf": 0.00015,
        "eurgbp": 0.00012, "usdjpy": 0.012, "eurjpy": 0.018, "gbpjpy": 0.025, "audjpy": 0.018, "xauusd": 0.35}
SWAP = {k: 0.02 / 365 for k in COST}; SWAP["xauusd"] = 0.06 / 365


def load(name):
    out = []
    for r in csv.DictReader(open(f"{D}/{name}_d1.csv")):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
        if out and out[-1][0].weekday() == 6:          # fold the Sunday stub into Monday
            p = out.pop(); o = p[1]; h = max(h, p[2]); l = min(l, p[3])
        out.append((t, o, h, l, c))
    return out


def inv(b): return [(t, -o, -l, -h, -c) for t, o, h, l, c in b]


def run(b, cost, swap, uselevel=True):
    n = len(b); K = 2
    atr = [None] * n
    for i in range(15, n):
        atr[i] = st.mean(max(b[j][2], b[j - 1][4]) - min(b[j][3], b[j - 1][4]) for j in range(i - 13, i + 1))
    ema = [None] * n; e = None
    for i in range(n):
        e = b[i][4] if e is None else e + (2 / 22) * (b[i][4] - e); ema[i] = e
    sh = [i for i in range(K, n - K) if b[i][2] >= max(x[2] for x in b[i - K:i + K + 1])]
    sl = [i for i in range(K, n - K) if b[i][3] <= min(x[3] for x in b[i - K:i + K + 1])]
    tr = []; busy = -1
    for a, H in zip(sh, sh[1:]):
        if H <= busy or H < 260 or atr[H] is None: continue
        top = b[H][2]; A = atr[H]
        if not top > b[a][2]: continue
        if uselevel and not any(top - 1.0 * A <= b[j][2] <= top + 0.5 * A for j in sh if H - 250 <= j <= H - 10): continue
        lows = [j for j in sl if a <= j < H]
        if not lows: continue
        hl = b[lows[-1]][3]; brk = None
        for m in range(H + 1, min(H + 21, n)):
            if b[m][2] > top: break
            if b[m][4] < hl: brk = m; break
        if brk is None: continue
        L = min(x[3] for x in b[H:brk + 1]); fill = None
        for m in range(brk + 1, min(brk + 21, n)):
            lim = ema[m - 1]
            if lim <= L or lim >= top: L = min(L, b[m][3]); continue
            if b[m][2] >= lim: fill = m; ent = max(lim, b[m][1]); break
            if b[m][4] > top: break
            L = min(L, b[m][3])
        if fill is None: continue
        tgt = L; risk = (ent - tgt) / 2; stop = ent + risk
        if risk <= 0: continue
        x = None; xi = fill
        if b[fill][2] >= stop: x = stop
        else:
            for k in range(fill + 1, min(fill + 41, n)):
                xi = k
                if b[k][1] >= stop: x = b[k][1]; break
                if b[k][2] >= stop: x = stop; break
                if b[k][3] <= tgt: x = tgt; break
            if x is None: x = b[xi][4]
        nights = (b[xi][0] - b[fill][0]).days
        tr.append((b[fill][0], (ent - x - cost - abs(ent) * swap * nights) / risk)); busy = xi
    return tr


def summ(name, tr):
    if not tr: return f"  {name:28s} none"
    rs = [r for _, r in tr]; yr = defaultdict(float)
    for t, r in tr: yr[t.year] += r
    a = [r for t, r in tr if t.year <= 2018]; c = [r for t, r in tr if t.year >= 2019]
    return (f"  {name:28s} n={len(rs):4d} win={sum(r > 0 for r in rs)/len(rs):4.0%} avg={st.mean(rs):+.3f}R tot={sum(rs):+6.1f}R  "
            f"2012-18 {st.mean(a) if a else 0:+.3f}R ({len(a)})  2019-26 {st.mean(c) if c else 0:+.3f}R ({len(c)})")


if __name__ == "__main__":
    for uselevel in (True, False):
        allt = []
        print("== key level filter ON (pre-registered)" if uselevel else "== key level filter OFF (reference)")
        for name in sorted(COST):
            b = load(name)
            t = [x for x in run(b, COST[name], SWAP[name], uselevel) + run(inv(b), COST[name], SWAP[name], uselevel)
                 if x[0].year >= 2012]
            allt += t
            print(summ(name.upper(), sorted(t)))
        print(summ("ALL MARKETS", sorted(allt)))
