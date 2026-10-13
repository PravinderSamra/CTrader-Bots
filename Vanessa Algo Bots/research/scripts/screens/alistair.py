"""Alistair Crooks (Chart Fanatics) forex 'trend line break' swing setup, coded mechanically on daily bars. Screening.
Long (short = mirror on inverted prices). Swings: k = 3 bars each side.
 1. Key level: a swing low L (bar lx) within 0.5 x ATR(14) of at least `touches` earlier swing lows from the last 250 bars,
    with no close below that band in between (frequency + proximity).
 2. Trend line: through the two most recent swing highs before lx that are falling (lower highs).
 3. Within 30 bars after lx (and before any close below L): a close above the trend line, then a close above the last
    lower high (structure break).
 4. Entry: limit buy at the 21 EMA on the first pull-back within 20 bars of the structure break.
 5. Target: the highest high of the 60 bars before lx (back to the top of the range). Stop: half the entry-target distance
    below entry (2:1). Same-bar stop and target counts as a loss. Time limit 60 bars.
Data: Yahoo daily FX 2005-2026, 18 pairs. Costs: spread 1.5 pips majors / 2.5 pips crosses, swap 3%/yr of price.
Control: same entries without the key-level condition."""
import glob, json, os, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone

MAJ = {"EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "USDCHF"}


def load(f):
    r = json.load(open(f))["chart"]["result"][0]; q = r["indicators"]["quote"][0]
    rows = []
    for t, o, h, l, c in zip(r["timestamp"], q["open"], q["high"], q["low"], q["close"]):
        if None in (o, h, l, c) or not (l <= min(o, c) and h >= max(o, c)) or h > 1.2 * c or l < 0.8 * c: continue
        rows.append((datetime.fromtimestamp(t, timezone.utc).date(), o, h, l, c))
    return rows


def run(rows, side, pip, keylevel=True, touches=1):
    if side == -1: rows = [(d, -o, -l, -h, -c) for d, o, h, l, c in rows]
    n = len(rows); O = [r[1] for r in rows]; H = [r[2] for r in rows]; L = [r[3] for r in rows]; C = [r[4] for r in rows]
    tr = [0] + [max(H[i], C[i - 1]) - min(L[i], C[i - 1]) for i in range(1, n)]
    a = 2 / 22; E = [C[0]]
    for x in C[1:]: E.append(E[-1] + a * (x - E[-1]))
    k = 3
    sh = [i for i in range(k, n - k) if H[i] == max(H[i - k:i + k + 1])]
    sl = [i for i in range(k, n - k) if L[i] == min(L[i - k:i + k + 1])]
    out = []; busy = -1
    for lx in sl:
        if lx < 260 or lx <= busy: continue
        atr = st.mean(tr[lx - 13:lx + 1]); lvl = L[lx]
        if keylevel:
            prev = [j for j in sl if lx - 250 <= j < lx - 5 and abs(L[j] - lvl) <= 0.5 * atr]
            if len(prev) < touches: continue
            if min(C[prev[0]:lx]) < lvl - 0.5 * atr: continue
        hs = [j for j in sh if j < lx][-2:]
        if len(hs) < 2 or not H[hs[1]] < H[hs[0]]: continue
        (a1, a2) = hs; slope = (H[a2] - H[a1]) / (a2 - a1)
        tgt = max(H[lx - 60:lx]); lh = H[a2]
        brk = sbrk = None
        for j in range(lx + k, min(lx + 31, n)):
            if C[j] < lvl: break
            if brk is None and C[j] > H[a2] + slope * (j - a2): brk = j
            if brk is not None and C[j] > lh: sbrk = j; break
        if sbrk is None: continue
        for m in range(sbrk + 1, min(sbrk + 21, n)):
            if H[m] >= tgt: break
            if L[m] <= E[m - 1]:
                e = min(O[m], E[m - 1]); stop = e - (tgt - e) / 2; risk = e - stop
                if risk <= 0: break
                cost = (1.5 if side else 0) * 0 + pip
                res = None
                for q in range(m, min(m + 60, n)):
                    if L[q] <= stop: res = stop; break
                    if q > m and H[q] >= tgt: res = tgt; break
                if res is None: q = min(m + 59, n - 1); res = C[q]
                sw = abs(e) * 0.03 / 365 * (rows[q][0] - rows[m][0]).days
                out.append((rows[m][0], (res - e - cost - sw) / risk)); busy = q
                break
    return out


def rep(name, t):
    if not t: print(name, "none"); return
    r = [x[1] for x in t]; yr = defaultdict(float)
    for d, x in t: yr[d.year] += x
    eq = pk = dd = 0
    for x in sorted(t): eq += x[1]; pk = max(pk, eq); dd = max(dd, pk - eq)
    pos = sum(v > 0 for v in yr.values())
    print(f"{name:34s} n={len(r):4d} win={sum(x > 0 for x in r)/len(r):4.0%} avg={st.mean(r):+.3f}R tot={sum(r):+6.1f}R dd={dd:4.1f}R "
          f"years+ {pos}/{len(yr)} | " + " ".join(f"{y % 100}:{v:+.0f}" for y, v in sorted(yr.items()) if y >= 2014))


allt = defaultdict(list); per = {}
for f in sorted(glob.glob(os.path.join(sys.argv[1], "*.json"))):
    s = os.path.basename(f)[:-5]; rows = load(f)
    pip = (0.01 if "JPY" in s else 0.0001) * (1.5 if s in MAJ else 2.5)
    for key, kl, tch in (("keylevel x2", True, 1), ("keylevel x3", True, 2), ("control (no level)", False, 0)):
        t = run(rows, 1, pip, kl, tch) + run(rows, -1, pip, kl, tch)
        allt[key] += t
        if key == "keylevel x2": per[s] = t
for k, v in allt.items(): rep(k, sorted(v))
print()
for s, t in per.items():
    if t: print(f"  {s}: n={len(t)} avg={st.mean(x[1] for x in t):+.2f}R")
