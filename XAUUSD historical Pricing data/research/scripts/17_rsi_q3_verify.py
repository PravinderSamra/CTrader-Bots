"""Verification of the ONE apparently-significant divergence cell found in script 16:
15m regular bearish divergence with a MODERATE RSI gap (3.8-7.3 points), which
raced 1 ATR down-first 59.2% of the time (z=+3.44 vs a 50.1% base rate).

Checks: year stability, split-half, robustness to re-binning, and -- the decisive
test -- a costed backtest with the stop where it structurally must go (beyond the
pivot high). Conclusion: the directional call is genuinely better than chance, but
the stop sits ~1.5 ATR away while the target is 1 ATR, so the geometry loses money.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40

lines = []
def emit(s=""):
    print(s)
    lines.append(s)


def rsi(s, n=14):
    d = s.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def atr(df, n=14):
    tr = np.maximum(df.high - df.low,
                    np.maximum((df.high - df.close.shift()).abs(),
                               (df.low - df.close.shift()).abs()))
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def piv(h, l, k):
    ph, pl = [], []
    for i in range(k, len(h) - k):
        w = h[i - k:i + k + 1]
        if (w[:k] < h[i]).all() and (w[k + 1:] < h[i]).all():
            ph.append(i)
        w = l[i - k:i + k + 1]
        if (w[:k] > l[i]).all() and (w[k + 1:] > l[i]).all():
            pl.append(i)
    return np.array(ph), np.array(pl)


df = m15.copy()
df["rsi"] = rsi(df.close); df["atr"] = atr(df)
h = df.high.to_numpy(); l = df.low.to_numpy(); c = df.close.to_numpy()
r = df.rsi.to_numpy(); a = df.atr.to_numpy(); n = len(df)
ph, pl = piv(h, l, 3)
BASE = 0.501


def race(i0, d=-1, m=1.0):
    if i0 >= n - 1 or np.isnan(a[i0]) or a[i0] <= 0:
        return np.nan
    e = c[i0]; A = a[i0]
    tgt = e + d * m * A; adv = e - d * m * A
    for j in range(i0 + 1, min(i0 + 400, n)):
        if l[j] <= tgt: return 1
        if h[j] >= adv: return 0
    return np.nan


ev = []
for idx in range(1, len(ph)):
    i, i1 = ph[idx], ph[idx - 1]
    if i - i1 > 60:
        continue
    ic = i + 3
    if ic >= n or np.isnan(r[i]) or np.isnan(r[i1]) or np.isnan(a[ic]) or a[ic] <= 0:
        continue
    if h[i] > h[i1] and r[i] <= r[i1]:
        ev.append(dict(ic=ic, gap=r[i1] - r[i], ext=h[i], entry=c[ic],
                       atr=a[ic], year=df.index[i].year, race=race(ic)))
e = pd.DataFrame(ev).dropna(subset=["race"])
e["q"] = pd.qcut(e.gap, 4, labels=["Q1", "Q2", "Q3", "Q4"])
q3 = e[e.q == "Q3"]

emit("=== Q3 CELL: 15m bearish divergence, RSI gap 3.8-7.3 points ===")
emit(f"N={len(q3)}  P(1-ATR down before 1-ATR up) = {q3.race.mean()*100:.1f}%  (base {BASE*100:.1f}%)")
emit("\nby year:")
emit(q3.groupby("year")["race"].agg(["size", "mean"]).round(3).to_string())
emit(f"\nsplit-half: 2021-23 = {q3[q3.year<=2023].race.mean()*100:.1f}%  "
     f"2024-26 = {q3[q3.year>=2024].race.mean()*100:.1f}%")
emit("\nrobustness to re-binning (best bin per scheme):")
for nb in (3, 5, 6, 10):
    e["qq"] = pd.qcut(e.gap, nb, labels=False)
    gg = e.groupby("qq")["race"].agg(["size", "mean"])
    zs = [(m - BASE) / np.sqrt(BASE * (1 - BASE) / s) for s, m in zip(gg["size"], gg["mean"])]
    emit(f"  bins={nb:>2}: best p={gg['mean'].max()*100:.1f}% z={max(zs):+.2f} "
         f"monotonic={gg['mean'].is_monotonic_increasing}")
emit("\nNOTE: ~40 hypotheses were tested across scripts 15-16; Bonferroni alpha=0.05 needs |z|>3.02.")

emit("\n=== DECISIVE TEST: costed backtest of the Q3 cell ===")
emit(f"median stop distance (to pivot high + 0.1 ATR buffer) = "
     f"{((q3.ext + 0.10*q3.atr - q3.entry)/q3.atr).median():.2f} ATR  <-- the problem")
for tp in (1.0, 1.5, 2.0, 3.0, None):
    rows = []
    for _, x in q3.iterrows():
        i0 = int(x.ic); entry = x.entry; stop = x.ext + 0.10 * x.atr
        risk = stop - entry
        if risk <= 0 or risk > 3 * x.atr:
            continue
        tgt = entry - tp * risk if tp else None
        pnl = None
        for j in range(i0 + 1, min(i0 + 200, n)):
            if h[j] >= stop:
                pnl = entry - stop - COST; break
            if tgt and l[j] <= tgt:
                pnl = entry - tgt - COST; break
        if pnl is None:
            j = min(i0 + 200, n - 1); pnl = entry - c[j] - COST
        rows.append(dict(pnl=pnl, risk=risk, year=x.year))
    t = pd.DataFrame(rows); t["R"] = t.pnl / t.risk
    eq = t.R.cumsum(); dd = (eq - eq.cummax()).min()
    emit(f"TP={str(tp) if tp else 'timeout'}: n={len(t)} win%={(t.R>0).mean()*100:.1f} "
         f"avgR={t.R.mean():+.3f} totR={t.R.sum():+.1f} maxDD={dd:.1f}R")
    emit("   by year: " + "  ".join(f"{int(y)}:{v:+.3f}"
                                    for y, v in t.groupby('year')['R'].mean().items()))

with open(os.path.join(OUT, "17_rsi_q3_verify.txt"), "w") as f:
    f.write("\n".join(lines))
