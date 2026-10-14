"""STRATEGY FACTORY v1 (daily bars). Our own SQX-style generator + filter, following research/QUANT_PROCESS.md.

Every strategy = ENTRY x FILTER x EXIT x DIRECTION, run on a whole GROUP of markets with the same rules
(so 'works on related markets' is built in). Signals use the daily close; orders fill at the NEXT open; stops and
targets are checked inside each bar with the stop first. Costs (spread + commission) and swap on every trade.
Risk unit R = the initial stop distance (or 2 x ATR(20) when the exit has no stop).

Periods: BUILD = start .. 2020, CONFIRM = 2021-2023, HOLDOUT = 2024-2026 (only opened for the final shortlist).
Pipeline (pre-registered 14 Oct 2026):
 1. BUILD: >= 100 pooled trades, avg >= +0.10R (or PF >= 1.2 with avg > 0 for win rates >= 60%),
    >= 60% of markets and >= 60% of years positive.
 2. Robustness on BUILD: >= 2/3 of parameter neighbours positive; avg still > 0 with doubled costs.
 3. CONFIRM (unseen): avg >= +0.05R and the bootstrap 95% range's lower end > -0.05R... reported; keep if avg > 0.05.
 4. De-duplicate (daily P/L correlation > 0.7 -> keep the better one).
 5. HOLDOUT once for the shortlist: must be positive. Then correlation with the live bots."""
import csv, glob, json, math, os, random, statistics as st, sys
from collections import defaultdict
from datetime import datetime, timezone, date
from itertools import product
from multiprocessing import Pool
import numpy as np

R0 = "/home/user/CTrader-Bots/Vanessa Algo Bots/research"
BUILD_END, CONF_END = date(2020, 12, 31), date(2023, 12, 31)

GROUPS = {
    "IDX": ["us500", "nas100", "us30", "us2000", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50"],
    "FX": ["eurusd", "gbpusd", "usdjpy", "audusd", "nzdusd", "usdcad", "usdchf", "eurgbp", "eurjpy", "gbpjpy", "audjpy"],
    "MET": ["xauusd", "xagusd", "xptusd", "copper"],
    "ENG": ["wti", "brent", "natgas"],
}
# round-trip cost as a fraction of price, swap per night as a fraction of price
COSTF = {"IDX": 0.00025, "FX": 0.00015, "MET": 0.0006, "ENG": 0.0008}
COSTF_M = {"xauusd": 0.00018, "xagusd": 0.0012, "xptusd": 0.0020, "copper": 0.0012, "natgas": 0.0020, "wti": 0.0005, "brent": 0.0005,
           "gbpjpy": 0.00015, "eurjpy": 0.00012, "audjpy": 0.00015, "nzdusd": 0.0002}
SWAPY = {"IDX": 0.05, "FX": 0.02, "MET": 0.04, "ENG": 0.05}


def path(m):
    for d in ("data/factory_d1", "data/fx_d1_2010_2026"):
        p = f"{R0}/{d}/{m}_d1.csv"
        if os.path.exists(p): return p


def load(m):
    rows = []
    for r in csv.DictReader(open(path(m))):
        t = datetime.fromtimestamp(int(r["timestamp_ms"]) / 1000, timezone.utc)
        o, h, l, c = (float(r[k]) for k in ("open", "high", "low", "close"))
        if rows and rows[-1][0].weekday() == 6:   # fold the Sunday stub into Monday
            p = rows.pop(); o = p[1]; h = max(h, p[2]); l = min(l, p[3])
        rows.append((t, o, h, l, c))
    # session date = bar open + 5h (bars open the evening before)
    d = [(x[0].timestamp() + 5 * 3600) for x in rows]
    dates = [datetime.fromtimestamp(z, timezone.utc).date() for z in d]
    a = np.array([[x[1], x[2], x[3], x[4]] for x in rows], dtype=float)
    return dates, a[:, 0], a[:, 1], a[:, 2], a[:, 3]


# ---------------- indicators ----------------
def sma(x, n):
    o = np.full(len(x), np.nan); c = np.cumsum(np.insert(x, 0, 0.0))
    o[n - 1:] = (c[n:] - c[:-n]) / n; return o


def rolling(f, x, n):
    o = np.full(len(x), np.nan)
    for i in range(n - 1, len(x)): o[i] = f(x[i - n + 1:i + 1])
    return o


def rsi(c, n):
    o = np.full(len(c), np.nan); g = l = 0.0
    for i in range(1, len(c)):
        d = c[i] - c[i - 1]
        if i <= n: g += max(d, 0) / n; l += max(-d, 0) / n
        else: g = (g * (n - 1) + max(d, 0)) / n; l = (l * (n - 1) + max(-d, 0)) / n
        if i >= n: o[i] = 100.0 if l == 0 else 100 - 100 / (1 + g / l)
    return o


class Mkt:
    def __init__(self, name, group):
        self.name, self.group = name, group
        self.dates, self.o, self.h, self.l, self.c = load(name)
        c, h, l = self.c, self.h, self.l; n = len(c)
        pc = np.insert(c[:-1], 0, c[0])
        tr = np.maximum(h, pc) - np.minimum(l, pc)
        self.atr = sma(tr, 20)
        self.sma = {k: sma(c, k) for k in (5, 10, 20, 50, 100, 200)}
        self.sd20 = rolling(np.std, c, 20)
        self.rsi2 = rsi(c, 2)
        self.hiC = {k: np.concatenate([[np.nan], rolling(np.max, c, k)[:-1]]) for k in (10, 20, 55, 100)}  # max of the previous k closes
        self.loC = {k: np.concatenate([[np.nan], rolling(np.min, c, k)[:-1]]) for k in (10, 20, 55, 100)}
        self.loL = {k: np.concatenate([[np.nan], rolling(np.min, l, k)[:-1]]) for k in (10, 20, 55)}
        self.hiH = {k: np.concatenate([[np.nan], rolling(np.max, h, k)[:-1]]) for k in (10, 20, 55)}
        rng = h - l
        self.nr = {k: rolling(lambda w: 1.0 if w[-1] == w.min() else 0.0, rng, k) for k in (4, 7)}
        self.atr_med = rolling(np.median, np.nan_to_num(self.atr), 100)
        self.cost = COSTF_M.get(name, COSTF[group]); self.swap = SWAPY[group] / 365
        # month-end position: trading days left in the month
        self.left = np.zeros(n, dtype=int)
        for i in range(n):
            k = 0; j = i + 1
            while j < n and self.dates[j].month == self.dates[i].month: k += 1; j += 1
            self.left[i] = k
        self.year = np.array([d.year for d in self.dates])


# ---------------- building blocks ----------------
ENTRIES = [("BRK", (20, 55, 100)), ("MAX", ((10, 50), (20, 100), (50, 200))), ("PB", (5, 10, 20)), ("BB", (1.5, 2.0, 2.5)),
           ("SOUP", (10, 20, 55)), ("DOWN", (3, 4, 5)), ("NR", (4, 7)), ("TOM", (1, 2, 3))]
FILTERS = ("none", "trend", "calm")
EXITS = [("TIME", (1, 3, 5, 10, 20)), ("STOPTGT", ((1.5, 1.5), (1.5, 3.0), (1.5, 0), (3.0, 1.5), (3.0, 3.0), (3.0, 0))),
         ("CHAN", (10, 20)), ("MR", ("sma5", "rsi70")), ("MAEXIT", (20,))]


def entry_signal(m, kind, p, side):
    """boolean array: signal at the close of bar i (long logic on side=+1, mirrored for side=-1)"""
    c, n = m.c, len(m.c)
    with np.errstate(invalid="ignore"):
        if kind == "BRK":
            return (c > m.hiC[p]) if side > 0 else (c < m.loC[p])
        if kind == "MAX":
            f, s = m.sma[p[0]], m.sma[p[1]]; up = f > s; prev = np.insert(up[:-1], 0, False)
            return (up & ~prev) if side > 0 else (~up & prev)
        if kind == "PB":
            return ((c > m.sma[200]) & (m.rsi2 < p)) if side > 0 else ((c < m.sma[200]) & (m.rsi2 > 100 - p))
        if kind == "BB":
            return (c < m.sma[20] - p * m.sd20) if side > 0 else (c > m.sma[20] + p * m.sd20)
        if kind == "SOUP":
            return ((m.l < m.loL[p]) & (c > m.loL[p])) if side > 0 else ((m.h > m.hiH[p]) & (c < m.hiH[p]))
        if kind == "DOWN":
            d = np.diff(c, prepend=c[0]); s = np.zeros(n, bool)
            for i in range(p, n):
                w = d[i - p + 1:i + 1]
                s[i] = (w < 0).all() if side > 0 else (w > 0).all()
            return s
        if kind == "NR":
            prev_nr = np.insert(m.nr[p][:-1] == 1.0, 0, False); ph = np.insert(m.h[:-1], 0, np.nan); pl = np.insert(m.l[:-1], 0, np.nan)
            return (prev_nr & (c > ph)) if side > 0 else (prev_nr & (c < pl))
        if kind == "TOM":
            return m.left == p   # month-end flow; side decides long/short
    raise ValueError(kind)


def filt(m, f, side):
    with np.errstate(invalid="ignore"):
        if f == "none": return np.ones(len(m.c), bool)
        if f == "trend": return (m.c > m.sma[200]) if side > 0 else (m.c < m.sma[200])
        if f == "calm": return m.atr < m.atr_med
    raise ValueError(f)


def simulate(m, sig, xk, xp, side, costmult=1.0):
    """returns list of (entry date, R, period tag)"""
    o, h, l, c, atr = m.o, m.h, m.l, m.c, m.atr; n = len(c); out = []; i = 0
    idx = np.flatnonzero(sig)
    nxt = 0
    for s in idx:
        if s < nxt or s + 1 >= n or not (atr[s] > 0): continue
        e = o[s + 1]; A = atr[s]
        if xk == "STOPTGT": stop_d, tgt_d, cap = xp[0] * A, (xp[1] * A if xp[1] else None), 20
        elif xk == "CHAN": stop_d, tgt_d, cap = 2 * A, None, 120
        elif xk == "MR": stop_d, tgt_d, cap = 3 * A, None, 10
        elif xk == "MAEXIT": stop_d, tgt_d, cap = 2 * A, None, 120
        else: stop_d, tgt_d, cap = None, None, xp
        R = stop_d if stop_d else 2 * A
        stop = e - side * stop_d if stop_d else None
        tgt = e + side * tgt_d if tgt_d else None
        x = None; j = s + 1
        last = min(n - 1, s + cap) if xk != "TIME" else min(n - 1, s + xp)
        while j <= last:
            if stop is not None:
                if side > 0 and l[j] <= stop: x = min(stop, o[j]) if j > s + 1 else stop; break
                if side < 0 and h[j] >= stop: x = max(stop, o[j]) if j > s + 1 else stop; break
            if tgt is not None:
                if side > 0 and h[j] >= tgt: x = tgt; break
                if side < 0 and l[j] <= tgt: x = tgt; break
            if j < n - 1 and j > s:
                ex = False
                if xk == "CHAN": ex = (c[j] < m.loC[xp][j]) if side > 0 else (c[j] > m.hiC[xp][j])
                elif xk == "MR": ex = ((c[j] > m.sma[5][j]) if side > 0 else (c[j] < m.sma[5][j])) if xp == "sma5" else \
                                      ((m.rsi2[j] > 70) if side > 0 else (m.rsi2[j] < 30))
                elif xk == "MAEXIT": ex = (c[j] < m.sma[xp][j]) if side > 0 else (c[j] > m.sma[xp][j])
                if ex and j + 1 < n: x = o[j + 1]; j = j + 1; break
            if j == last: x = c[j]; break
            j += 1
        if x is None: x = c[min(j, n - 1)]
        nights = max(0, (m.dates[min(j, n - 1)] - m.dates[s + 1]).days)
        r = (side * (x - e) - costmult * m.cost * e - m.swap * e * nights) / R
        d = m.dates[s + 1]
        tag = "B" if d <= BUILD_END else ("C" if d <= CONF_END else "H")
        out.append((d, r, tag)); nxt = j + 1
    return out


def all_specs():
    specs = []
    for (ek, eps), f, (xk, xps), side in product(ENTRIES, FILTERS, EXITS, (1, -1)):
        for ep in eps:
            for xp in xps:
                specs.append((ek, ep, f, xk, xp, side))
    return specs


def spec_id(s):
    return f"{s[0]}{s[1]}|{s[2]}|{s[3]}{s[4]}|{'L' if s[5] > 0 else 'S'}".replace(" ", "")


_M = {}


def _init(group):
    global _M
    _M = {g: [Mkt(x, g) for x in names] for g, names in GROUPS.items() if group in (g, "ALL")}


def evaluate(args):
    group, spec, costmult = args
    ek, ep, f, xk, xp, side = spec
    per_mkt = {}
    for m in _M[group]:
        sig = entry_signal(m, ek, ep, side) & filt(m, f, side)
        per_mkt[m.name] = simulate(m, sig, xk, xp, side, costmult)
    return group, spec, costmult, per_mkt


def stats(trades):
    if not trades: return dict(n=0, avg=0, pf=0, win=0)
    r = [t[1] for t in trades]; g = sum(x for x in r if x > 0); b = -sum(x for x in r if x <= 0)
    return dict(n=len(r), avg=sum(r) / len(r), pf=(g / b if b > 0 else 9.9), win=sum(x > 0 for x in r) / len(r))


def boot_lo(r, n=1000):
    if len(r) < 10: return -9
    rnd = random.Random(7); ms = sorted(sum(rnd.choices(r, k=len(r))) / len(r) for _ in range(n)); return ms[int(0.025 * n)]
