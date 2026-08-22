"""Stress-test the best-looking RSI divergence cases from script 15.

  A. Statistical significance of every class edge (binomial z vs base rate).
  B. Divergence MAGNITUDE: does a bigger RSI/price disagreement predict better?
  C. Session conditioning (Asia / London / NY).
  D. Triple divergence (3 consecutive pivots diverging) vs double.
  E. Costed backtest of the strongest class: 15m regular bearish/bullish divergence,
     entry at confirmation close, stop beyond the pivot extreme, targets 1R/2R/none.
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


def find_pivots(h, l, k):
    n = len(h)
    ph, pl = [], []
    for i in range(k, n - k):
        w = h[i - k:i + k + 1]
        if (w[:k] < h[i]).all() and (w[k + 1:] < h[i]).all():
            ph.append(i)
        w = l[i - k:i + k + 1]
        if (w[:k] > l[i]).all() and (w[k + 1:] > l[i]).all():
            pl.append(i)
    return np.array(ph), np.array(pl)


def build(df, k=3, max_gap=60):
    df = df.copy()
    df["rsi"] = rsi(df.close); df["atr"] = atr(df)
    h = df.high.to_numpy(); l = df.low.to_numpy(); c = df.close.to_numpy()
    r = df.rsi.to_numpy(); a = df.atr.to_numpy()
    n = len(df)
    ph, pl = find_pivots(h, l, k)
    recs = []

    def race(i_conf, direction, mult=1.0):
        if i_conf >= n - 1 or np.isnan(a[i_conf]) or a[i_conf] <= 0:
            return np.nan
        e = c[i_conf]; A = a[i_conf]
        tgt = e + direction * mult * A
        adv = e - direction * mult * A
        for j in range(i_conf + 1, min(i_conf + 400, n)):
            if direction == -1:
                if l[j] <= tgt: return 1
                if h[j] >= adv: return 0
            else:
                if h[j] >= tgt: return 1
                if l[j] <= adv: return 0
        return np.nan

    for side, piv, other in (("high", ph, pl), ("low", pl, ph)):
        for idx in range(2, len(piv)):
            i, i1, i2 = piv[idx], piv[idx - 1], piv[idx - 2]
            if i - i1 > max_gap:
                continue
            i_conf = i + k
            if i_conf >= n or np.isnan(r[i]) or np.isnan(r[i1]) or np.isnan(a[i]) or a[i] <= 0:
                continue
            if side == "high":
                price_up = h[i] > h[i1]
                rsi_up = r[i] > r[i1]
                cls = ("HH" if price_up else "LH") + "+RSI_" + ("HH" if rsi_up else "LH")
                is_div = price_up and not rsi_up
                trip = is_div and (h[i1] > h[i2]) and (r[i1] < r[i2])
                pmag = (h[i] - h[i1]) / a[i]
                direction = -1
                ext = h[i]
            else:
                price_dn = l[i] < l[i1]
                rsi_dn = r[i] < r[i1]
                cls = ("LL" if price_dn else "HL") + "+RSI_" + ("LL" if rsi_dn else "HL")
                is_div = price_dn and not rsi_dn
                trip = is_div and (l[i1] < l[i2]) and (r[i1] > r[i2])
                pmag = (l[i1] - l[i]) / a[i]
                direction = +1
                ext = l[i]
            recs.append(dict(side=side, cls=cls, is_div=is_div, triple=trip,
                             rsi_gap=abs(r[i] - r[i1]), price_mag=pmag,
                             rsi_val=r[i], hour=df.index[i].hour, year=df.index[i].year,
                             i_conf=i_conf, entry=c[i_conf], atr=a[i_conf], ext=ext,
                             direction=direction,
                             race1=race(i_conf, direction, 1.0)))
    return pd.DataFrame(recs), df


def ztest(p, n, p0):
    if n == 0:
        return np.nan
    se = np.sqrt(p0 * (1 - p0) / n)
    return (p - p0) / se if se > 0 else np.nan


for tf_name, tf_df, k in (("5m", m5, 3), ("15m", m15, 3)):
    t, dfx = build(tf_df, k=k)
    emit("\n" + "=" * 74)
    emit(f"### {tf_name}  (N={len(t):,} pivot events)")
    emit("=" * 74)

    emit("\nA. SIGNIFICANCE OF EACH CLASS EDGE (z vs that side's base rate)")
    for side in ("high", "low"):
        s = t[t.side == side].dropna(subset=["race1"])
        base = s.race1.mean()
        emit(f"  {side}s: base={base*100:.1f}% (N={len(s):,})")
        for cl in sorted(s.cls.unique()):
            g = s[s.cls == cl]
            z = ztest(g.race1.mean(), len(g), base)
            flag = "SIGNIFICANT" if abs(z) > 2.58 else ("marginal" if abs(z) > 1.96 else "noise")
            emit(f"    {cl:<12} N={len(g):>6,} p={g.race1.mean()*100:5.2f}%  "
                 f"edge={(g.race1.mean()-base)*100:+5.2f}pp  z={z:+5.2f}  {flag}")

    emit("\nB. DIVERGENCE MAGNITUDE (regular divergences only)")
    for side in ("high", "low"):
        s = t[(t.side == side)].dropna(subset=["race1"])
        base = s.race1.mean()
        d = s[s.is_div]
        if len(d) < 200:
            continue
        d = d.copy()
        d["rsi_q"] = pd.qcut(d.rsi_gap, 4, labels=["Q1 small", "Q2", "Q3", "Q4 large"])
        agg = d.groupby("rsi_q", observed=True).agg(N=("race1", "size"), p=("race1", "mean"))
        agg["p%"] = (agg.p * 100).round(2)
        agg["edge_pp"] = ((agg.p - base) * 100).round(2)
        agg["z"] = [round(ztest(p, n, base), 2) for p, n in zip(agg.p, agg.N)]
        emit(f"  {side}s by RSI-gap quartile (base {base*100:.1f}%):")
        emit(agg[["N", "p%", "edge_pp", "z"]].to_string())

    emit("\nC. SESSION (regular divergences, 1-ATR race)")
    for side in ("high", "low"):
        s = t[t.side == side].dropna(subset=["race1"])
        base = s.race1.mean()
        d = s[s.is_div].copy()
        d["sess"] = np.where((d.hour >= 22) | (d.hour < 7), "Asia",
                             np.where(d.hour < 12, "London", np.where(d.hour < 21, "NY", "close")))
        agg = d.groupby("sess").agg(N=("race1", "size"), p=("race1", "mean"))
        agg["p%"] = (agg.p * 100).round(2)
        agg["edge_pp"] = ((agg.p - base) * 100).round(2)
        agg["z"] = [round(ztest(p, n, base), 2) for p, n in zip(agg.p, agg.N)]
        emit(f"  {side}s (base {base*100:.1f}%):")
        emit(agg[["N", "p%", "edge_pp", "z"]].to_string())

    emit("\nD. TRIPLE vs DOUBLE DIVERGENCE")
    for side in ("high", "low"):
        s = t[t.side == side].dropna(subset=["race1"])
        base = s.race1.mean()
        for lbl, g in (("double", s[s.is_div & ~s.triple]), ("triple", s[s.triple])):
            if len(g) < 30:
                continue
            z = ztest(g.race1.mean(), len(g), base)
            emit(f"  {side:<5} {lbl}: N={len(g):>5,} p={g.race1.mean()*100:5.2f}% "
                 f"edge={(g.race1.mean()-base)*100:+5.2f}pp z={z:+5.2f}")

    # ---------------- E. costed backtest ----------------
    emit("\nE. COSTED BACKTEST — trade every regular divergence "
         "(entry=confirmation close, stop beyond pivot extreme)")
    h = dfx.high.to_numpy(); l = dfx.low.to_numpy(); c = dfx.close.to_numpy()
    n = len(dfx)
    for tp_mult in (1.0, 2.0, None):
        rows = []
        for _, e in t[t.is_div].dropna(subset=["race1"]).iterrows():
            i0 = int(e.i_conf); direction = int(e.direction)
            entry = e.entry
            buf = 0.10 * e.atr
            stop = e.ext + (buf if direction == -1 else -buf)
            risk = abs(entry - stop)
            if risk <= 0 or risk > 3 * e.atr:
                continue
            tp = entry + direction * tp_mult * risk if tp_mult else None
            pnl = None
            for j in range(i0 + 1, min(i0 + 200, n)):
                if direction == -1:
                    if h[j] >= stop: pnl = entry - stop - COST; break
                    if tp and l[j] <= tp: pnl = entry - tp - COST; break
                else:
                    if l[j] <= stop: pnl = stop - entry - COST; break
                    if tp and h[j] >= tp: pnl = tp - entry - COST; break
            if pnl is None:
                j = min(i0 + 200, n - 1)
                pnl = direction * (c[j] - entry) - COST
            rows.append(dict(pnl=pnl, risk=risk, year=e.year))
        r = pd.DataFrame(rows)
        r["R"] = r.pnl / r.risk
        eq = r.R.cumsum(); dd = (eq - eq.cummax()).min()
        emit(f"  TP={tp_mult or 'none (200-bar timeout)'}: n={len(r):,} "
             f"win%={(r.R>0).mean()*100:.1f} avgR={r.R.mean():+.3f} "
             f"totR={r.R.sum():+.0f} maxDD={dd:.0f}R")
        yr = r.groupby("year")["R"].mean().round(3)
        emit("     by year: " + "  ".join(f"{y}:{v:+.3f}" for y, v in yr.items()))

with open(os.path.join(OUT, "16_rsi_div_stress.txt"), "w") as f:
    f.write("\n".join(lines))
