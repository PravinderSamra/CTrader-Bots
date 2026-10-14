"""STRATEGY FACTORY v2: 1-hour and 4-hour bars (higher-frequency strategies). Same honesty rules as v1:
signal at a bar's close, fill at the NEXT bar's open, stop checked before target inside a bar, costs + swap.
R = initial stop distance, or 2 x ATR(20) of that timeframe when the exit has no stop.
New building blocks for intraday: time-of-day entries (seasonality), session filter (London / New York hours),
daily-trend filter. Pipeline adds a correlation filter against the live NAS bot.
Periods: BUILD .. 2020, CONFIRM 2021-2023, HOLDOUT 2024-2026 (opened once for the shortlist)."""
import csv, os, random
from datetime import datetime, timezone, date
from itertools import product
import numpy as np
from numpy.lib.stride_tricks import sliding_window_view as swv

R0 = "/home/user/CTrader-Bots/Vanessa Algo Bots/research"
BUILD_END, CONF_END = date(2020, 12, 31), date(2023, 12, 31)
GROUPS = {
    "IDX": ["us500", "nas100", "us30", "ger40", "uk100", "fra40", "eustx50", "aus200", "hk50", "jp225"],
    "FX": ["eurusd", "gbpusd", "usdjpy", "audusd", "usdcad", "eurjpy"],
    "COM": ["xauusd", "xagusd", "wti", "brent"],
}
COSTF = {"IDX": 0.00025, "FX": 0.00015, "COM": 0.0006}
COSTF_M = {"xauusd": 0.00018, "xagusd": 0.0012, "wti": 0.0005, "brent": 0.0005, "eurjpy": 0.00012}
SWAPY = {"IDX": 0.05, "FX": 0.02, "COM": 0.05}


def load(m, tf):
    rows = []
    for r in csv.DictReader(open(f"{R0}/data/factory_h1/{m}_h1.csv")):
        rows.append((int(r["timestamp_ms"]) // 1000, float(r["open"]), float(r["high"]), float(r["low"]), float(r["close"])))
    a = np.array(rows, dtype=float)
    if tf == 4:   # aggregate to 4-hour bars on UTC 0/4/8/12/16/20
        key = (a[:, 0] // (4 * 3600)).astype(np.int64)
        brk = np.flatnonzero(np.diff(key)) + 1
        starts = np.insert(brk, 0, 0); ends = np.append(brk, len(a))
        a = np.array([[a[s, 0], a[s, 1], a[s:e, 2].max(), a[s:e, 3].min(), a[e - 1, 4]] for s, e in zip(starts, ends)])
    return a


def roll(x, n, f):
    o = np.full(len(x), np.nan)
    if len(x) >= n: o[n - 1:] = f(swv(x, n), axis=1)
    return o


def sma(x, n): return roll(x, n, np.mean)


def rsi2(c):
    d = np.diff(c, prepend=c[0]); up = np.maximum(d, 0); dn = np.maximum(-d, 0)
    g = np.zeros(len(c)); l = np.zeros(len(c))
    for i in range(1, len(c)):
        g[i] = (g[i - 1] + up[i]) / 2; l[i] = (l[i - 1] + dn[i]) / 2
    with np.errstate(divide="ignore", invalid="ignore"):
        return np.where(l == 0, 100.0, 100 - 100 / (1 + g / l))


class Mkt:
    def __init__(self, name, group, tf):
        self.name, self.group, self.tf = name, group, tf
        a = load(name, tf)
        self.t = a[:, 0].astype(np.int64); self.o, self.h, self.l, self.c = a[:, 1], a[:, 2], a[:, 3], a[:, 4]
        c, h, l = self.c, self.h, self.l; n = len(c)
        self.dates = [datetime.fromtimestamp(x, timezone.utc).date() for x in self.t]
        self.hour = np.array([datetime.fromtimestamp(x, timezone.utc).hour for x in self.t])
        pc = np.insert(c[:-1], 0, c[0]); tr = np.maximum(h, pc) - np.minimum(l, pc)
        self.atr = sma(tr, 20)
        self.sma = {k: sma(c, k) for k in (5, 20, 50, 200)}
        self.sd20 = roll(c, 20, np.std)
        self.rsi = rsi2(c)
        prev = lambda x: np.insert(x[:-1], 0, np.nan)
        self.hiC = {k: prev(roll(c, k, np.max)) for k in (10, 20, 50, 100)}
        self.loC = {k: prev(roll(c, k, np.min)) for k in (10, 20, 50, 100)}
        self.loL = {k: prev(roll(l, k, np.min)) for k in (20, 50)}
        self.hiH = {k: prev(roll(h, k, np.max)) for k in (20, 50)}
        # daily trend from daily closes: yesterday's daily close vs its 50-day average
        dk = np.array([d.toordinal() for d in self.dates])
        last = {}
        for i in range(n): last[dk[i]] = c[i]
        days = sorted(last); dcl = np.array([last[d] for d in days]); d50 = sma(dcl, 50)
        prevtrend = {days[i]: (np.nan if i == 0 else (1.0 if dcl[i - 1] > d50[i - 1] else -1.0)) for i in range(len(days))}
        self.dtrend = np.array([prevtrend[x] for x in dk])
        self.cost = COSTF_M.get(name, COSTF[group]); self.swap = SWAPY[group] / 365


ENTRIES = [("BRK", (20, 50, 100)), ("BB", (2.0, 2.5, 3.0)), ("RSI", (5, 10, 20)), ("SOUP", (20, 50)),
           ("DOWN", (3, 4, 5)), ("TOD", (0, 3, 6, 9, 12, 15, 18, 21))]
FILTERS = ("none", "dtrend", "london", "newyork")
EXITS = [("TIME", (3, 6, 12, 24)), ("STOPTGT", ((1.5, 1.5), (1.5, 3.0), (3.0, 1.5))), ("MR", ("sma20",)), ("CHAN", (20,))]


def entry_signal(m, kind, p, side):
    c, n = m.c, len(m.c)
    with np.errstate(invalid="ignore"):
        if kind == "BRK": return (c > m.hiC[p]) if side > 0 else (c < m.loC[p])
        if kind == "BB": return (c < m.sma[20] - p * m.sd20) if side > 0 else (c > m.sma[20] + p * m.sd20)
        if kind == "RSI": return ((c > m.sma[200]) & (m.rsi < p)) if side > 0 else ((c < m.sma[200]) & (m.rsi > 100 - p))
        if kind == "SOUP": return ((m.l < m.loL[p]) & (c > m.loL[p])) if side > 0 else ((m.h > m.hiH[p]) & (c < m.hiH[p]))
        if kind == "DOWN":
            d = np.sign(np.diff(c, prepend=c[0])); want = -1 if side > 0 else 1
            return roll((d == want).astype(float), p, np.min) == 1
        if kind == "TOD":   # the bar whose close is at hour p (bar opening at p - tf hours)
            return ((m.hour + m.tf) % 24) == p
    raise ValueError(kind)


def filt(m, f, side):
    if f == "none": return np.ones(len(m.c), bool)
    if f == "dtrend": return m.dtrend == side
    nxt = (m.hour + m.tf) % 24   # hour at which the next bar (the fill) opens
    if f == "london": return (nxt >= 7) & (nxt < 15)
    if f == "newyork": return (nxt >= 13) & (nxt < 20)
    raise ValueError(f)


def simulate(m, sig, xk, xp, side, costmult=1.0):
    o, h, l, c, atr = m.o, m.h, m.l, m.c, m.atr; n = len(c); out = []; nxt = 0
    for s in np.flatnonzero(sig):
        if s < nxt or s + 1 >= n or not (atr[s] > 0): continue
        e = o[s + 1]; A = atr[s]
        if xk == "STOPTGT": stop_d, tgt_d, cap = xp[0] * A, xp[1] * A, 48
        elif xk == "MR": stop_d, tgt_d, cap = 3 * A, None, 24
        elif xk == "CHAN": stop_d, tgt_d, cap = 2 * A, None, 120
        else: stop_d, tgt_d, cap = None, None, xp
        R = stop_d if stop_d else 2 * A
        stop = e - side * stop_d if stop_d else None; tgt = e + side * tgt_d if tgt_d else None
        last = min(n - 1, s + cap); x = None; j = s + 1
        while j <= last:
            if stop is not None and ((side > 0 and l[j] <= stop) or (side < 0 and h[j] >= stop)):
                x = (min(stop, o[j]) if side > 0 else max(stop, o[j])) if j > s + 1 else stop; break
            if tgt is not None and ((side > 0 and h[j] >= tgt) or (side < 0 and l[j] <= tgt)): x = tgt; break
            if j < last:
                ex = False
                if xk == "MR": ex = (c[j] > m.sma[20][j]) if side > 0 else (c[j] < m.sma[20][j])
                elif xk == "CHAN": ex = (c[j] < m.loC[xp][j]) if side > 0 else (c[j] > m.hiC[xp][j])
                if ex: x = o[j + 1]; j += 1; break
            if j == last: x = c[j]; break
            j += 1
        if x is None: x = c[min(j, n - 1)]
        j = min(j, n - 1)
        nights = max(0, (m.dates[j] - m.dates[s + 1]).days)
        r = (side * (x - e) - costmult * m.cost * e - m.swap * e * nights) / R
        d = m.dates[s + 1]
        out.append((d, r, "B" if d <= BUILD_END else ("C" if d <= CONF_END else "H"))); nxt = j + 1
    return out


def all_specs():
    return [(ek, ep, f, xk, xp, side) for (ek, eps), f, (xk, xps), side in product(ENTRIES, FILTERS, EXITS, (1, -1))
            for ep in eps for xp in xps]


def spec_id(s, tf):
    return f"H{tf}|{s[0]}{s[1]}|{s[2]}|{s[3]}{s[4]}|{'L' if s[5] > 0 else 'S'}".replace(" ", "")


_M = {}


def _init(group, tf):
    global _M
    names = [x for x in GROUPS[group] if os.path.exists(f"{R0}/data/factory_h1/{x}_h1.csv")]
    _M = {group: [Mkt(x, group, tf) for x in names]}


def evaluate(args):
    group, spec, costmult = args
    ek, ep, f, xk, xp, side = spec
    pm = {}
    for m in _M[group]:
        pm[m.name] = simulate(m, entry_signal(m, ek, ep, side) & filt(m, f, side), xk, xp, side, costmult)
    return spec, pm


def stats(tr):
    if not tr: return dict(n=0, avg=0.0, pf=0.0, win=0.0)
    r = [t[1] for t in tr]; g = sum(x for x in r if x > 0); b = -sum(x for x in r if x <= 0)
    return dict(n=len(r), avg=sum(r) / len(r), pf=(g / b if b > 0 else 9.9), win=sum(x > 0 for x in r) / len(r))


def boot_lo(r, n=1000):
    if len(r) < 10: return -9
    rnd = random.Random(7); ms = sorted(sum(rnd.choices(r, k=len(r))) / len(r) for _ in range(n)); return ms[int(0.025 * n)]
