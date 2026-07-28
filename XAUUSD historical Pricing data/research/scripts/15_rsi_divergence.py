"""Price / RSI swing relationships — full combination matrix and outcome probabilities.

METHOD (the part that matters):
  * Pivots are fractal: bar i is a pivot high if high[i] is the max of [i-k, i+k].
    A pivot is only KNOWABLE at bar i+k. Every outcome below is measured from the
    CLOSE OF BAR i+k (the confirmation bar) -- no look-ahead.
  * RSI(14) computed on the same timeframe, read at the pivot bar itself.
  * Each pivot high is compared with the previous pivot high; each pivot low with
    the previous pivot low, giving four classes per side:
        HIGHS: HH+RSI_HH (confirmed up) | HH+RSI_LH (regular bearish div)
               LH+RSI_HH (hidden bearish div) | LH+RSI_LH (confirmed down)
        LOWS : LL+RSI_LL (confirmed down) | LL+RSI_HL (regular bullish div)
               HL+RSI_LL (hidden bullish div) | HL+RSI_HL (confirmed up)
  * TREND CONTEXT (the user's scenario): optionally require the prior structure to
    be a genuine uptrend (prev pivot high > the one before AND prev pivot low >
    the one before) / downtrend, before the signal pivot.

OUTCOMES measured from the confirmation close:
  1. Barrier race: does price travel -1*ATR before +1*ATR (down-first) -- the
     tradeable "did it actually reverse" question. Also 0.5 and 2.0 ATR.
  2. Structure break: does price break the prior opposing pivot (trend reversal in
     the Dow sense) BEFORE exceeding the signal pivot's extreme?
  3. Forward returns at 6, 12, 24, 48 bars, in ATR units.
  4. Everything is compared with the BASE RATE across all pivots of that side.
Timeframes: 5m and 15m. RSI level conditioning (>70 / <30) also reported.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")

m1, m5, m15, h1, d1 = prep.load_all()

lines = []
def emit(s=""):
    print(s)
    lines.append(s)


def rsi(series, n=14):
    d = series.diff()
    up = d.clip(lower=0).ewm(alpha=1 / n, adjust=False).mean()
    dn = (-d.clip(upper=0)).ewm(alpha=1 / n, adjust=False).mean()
    return 100 - 100 / (1 + up / dn)


def atr(df, n=14):
    tr = np.maximum(df.high - df.low,
                    np.maximum((df.high - df.close.shift()).abs(),
                               (df.low - df.close.shift()).abs()))
    return tr.ewm(alpha=1 / n, adjust=False).mean()


def find_pivots(h, l, k):
    """returns (pivot_high_idx, pivot_low_idx) as sorted arrays."""
    n = len(h)
    ph, pl = [], []
    for i in range(k, n - k):
        w_h = h[i - k:i + k + 1]
        if h[i] == w_h.max() and (w_h[:k] < h[i]).all() and (w_h[k + 1:] < h[i]).all():
            ph.append(i)
        w_l = l[i - k:i + k + 1]
        if l[i] == w_l.min() and (w_l[:k] > l[i]).all() and (w_l[k + 1:] > l[i]).all():
            pl.append(i)
    return np.array(ph), np.array(pl)


def analyse(df, tf_name, k=3, max_gap=60):
    emit("\n" + "=" * 78)
    emit(f"### TIMEFRAME {tf_name}   (fractal k={k}, confirmation lag {k} bars, "
         f"max {max_gap} bars between compared pivots)")
    emit("=" * 78)

    df = df.copy()
    df["rsi"] = rsi(df.close)
    df["atr"] = atr(df)
    h = df.high.to_numpy(); l = df.low.to_numpy(); c = df.close.to_numpy()
    r = df.rsi.to_numpy(); a = df.atr.to_numpy()
    n = len(df)
    ph, pl = find_pivots(h, l, k)
    emit(f"pivot highs: {len(ph):,}   pivot lows: {len(pl):,}   bars: {n:,}")

    def outcomes(i_conf, direction, ref_extreme, opp_pivot_price):
        """direction=-1 tests DOWN-first (bearish), +1 tests UP-first (bullish)."""
        if i_conf >= n - 1 or np.isnan(a[i_conf]) or a[i_conf] <= 0:
            return None
        entry = c[i_conf]
        A = a[i_conf]
        out = {}
        for mult in (0.5, 1.0, 2.0):
            tgt = entry + direction * mult * A
            adv = entry - direction * mult * A
            hit = np.nan
            for j in range(i_conf + 1, min(i_conf + 400, n)):
                if direction == -1:
                    if l[j] <= tgt:
                        hit = 1; break
                    if h[j] >= adv:
                        hit = 0; break
                else:
                    if h[j] >= tgt:
                        hit = 1; break
                    if l[j] <= adv:
                        hit = 0; break
            out[f"race{mult}"] = hit
        # structure break before extreme exceeded
        sb = np.nan
        if opp_pivot_price is not None and not np.isnan(opp_pivot_price):
            for j in range(i_conf + 1, min(i_conf + 400, n)):
                if direction == -1:
                    if l[j] <= opp_pivot_price:
                        sb = 1; break
                    if h[j] >= ref_extreme:
                        sb = 0; break
                else:
                    if h[j] >= opp_pivot_price:
                        sb = 1; break
                    if l[j] <= ref_extreme:
                        sb = 0; break
        out["struct"] = sb
        for hz in (6, 12, 24, 48):
            j = min(i_conf + hz, n - 1)
            out[f"fwd{hz}"] = direction * (c[j] - entry) / A
        return out

    recs = []
    # ---- pivot highs ----
    for idx in range(1, len(ph)):
        i, i_prev = ph[idx], ph[idx - 1]
        if i - i_prev > max_gap:
            continue
        i_conf = i + k
        if i_conf >= n:
            continue
        price_hh = h[i] > h[i_prev]
        rsi_hh = r[i] > r[i_prev]
        if np.isnan(r[i]) or np.isnan(r[i_prev]):
            continue
        cls = ("HH" if price_hh else "LH") + "+RSI_" + ("HH" if rsi_hh else "LH")
        # trend context: prior swing structure rising
        prev_lows = pl[pl < i]
        ctx_up = False
        opp = np.nan
        if len(prev_lows) >= 2:
            opp = l[prev_lows[-1]]
            if idx >= 2 and len(prev_lows) >= 2:
                ctx_up = (h[ph[idx - 1]] > h[ph[idx - 2]]) and (l[prev_lows[-1]] > l[prev_lows[-2]])
        o = outcomes(i_conf, -1, h[i], opp)
        if o is None:
            continue
        recs.append(dict(side="high", cls=cls, ctx=ctx_up, rsi_val=r[i],
                         year=df.index[i].year, **o))
    # ---- pivot lows ----
    for idx in range(1, len(pl)):
        i, i_prev = pl[idx], pl[idx - 1]
        if i - i_prev > max_gap:
            continue
        i_conf = i + k
        if i_conf >= n:
            continue
        price_ll = l[i] < l[i_prev]
        rsi_ll = r[i] < r[i_prev]
        if np.isnan(r[i]) or np.isnan(r[i_prev]):
            continue
        cls = ("LL" if price_ll else "HL") + "+RSI_" + ("LL" if rsi_ll else "HL")
        prev_highs = ph[ph < i]
        ctx_dn = False
        opp = np.nan
        if len(prev_highs) >= 2:
            opp = h[prev_highs[-1]]
            if idx >= 2:
                ctx_dn = (l[pl[idx - 1]] < l[pl[idx - 2]]) and (h[prev_highs[-1]] < h[prev_highs[-2]])
        o = outcomes(i_conf, +1, l[i], opp)
        if o is None:
            continue
        recs.append(dict(side="low", cls=cls, ctx=ctx_dn, rsi_val=r[i],
                         year=df.index[i].year, **o))

    t = pd.DataFrame(recs)

    for side, base_lbl, order in [
        ("high", "DOWN-first", ["HH+RSI_HH", "HH+RSI_LH", "LH+RSI_HH", "LH+RSI_LH"]),
        ("low", "UP-first", ["LL+RSI_LL", "LL+RSI_HL", "HL+RSI_LL", "HL+RSI_HL"]),
    ]:
        s = t[t.side == side]
        emit(f"\n--- PIVOT {side.upper()}S — probability of {base_lbl} move "
             f"(1 ATR barrier race), N={len(s):,} ---")
        base = s["race1.0"].mean()
        emit(f"BASE RATE (all {side} pivots): {base*100:.1f}%   "
             f"struct-break base: {s['struct'].mean()*100:.1f}%")
        rows = []
        for cl in order:
            g = s[s.cls == cl]
            if len(g) < 30:
                continue
            rows.append({
                "class": cl,
                "N": len(g),
                "race0.5%": g["race0.5"].mean() * 100,
                "race1.0%": g["race1.0"].mean() * 100,
                "race2.0%": g["race2.0"].mean() * 100,
                "edge_vs_base": (g["race1.0"].mean() - base) * 100,
                "struct%": g["struct"].mean() * 100,
                "fwd12": g["fwd12"].mean(),
                "fwd48": g["fwd48"].mean(),
            })
        emit(pd.DataFrame(rows).round(2).to_string(index=False))

        # with trend context required (the user's exact scenario)
        emit(f"  [with prior trend structure confirmed]")
        rows = []
        for cl in order:
            g = s[(s.cls == cl) & (s.ctx)]
            if len(g) < 30:
                continue
            rows.append({"class": cl, "N": len(g), "race1.0%": g["race1.0"].mean() * 100,
                         "edge_vs_base": (g["race1.0"].mean() - base) * 100,
                         "struct%": g["struct"].mean() * 100, "fwd48": g["fwd48"].mean()})
        emit(pd.DataFrame(rows).round(2).to_string(index=False) if rows else "   (insufficient N)")

        # RSI level conditioning on the divergence classes
        div_cls = "HH+RSI_LH" if side == "high" else "LL+RSI_HL"
        g = s[s.cls == div_cls]
        if len(g) > 50:
            if side == "high":
                sub = g[g.rsi_val > 70]; lbl = "RSI>70 at pivot"
            else:
                sub = g[g.rsi_val < 30]; lbl = "RSI<30 at pivot"
            if len(sub) >= 30:
                emit(f"  [{div_cls} + {lbl}] N={len(sub)} race1.0={sub['race1.0'].mean()*100:.1f}% "
                     f"(edge {(sub['race1.0'].mean()-base)*100:+.1f}pp) struct={sub['struct'].mean()*100:.1f}%")

        # year stability of the headline divergence class
        g = s[s.cls == div_cls]
        yr = g.groupby("year")["race1.0"].agg(["size", "mean"])
        yr["mean"] = (yr["mean"] * 100).round(1)
        emit(f"  [{div_cls} by year] " + "  ".join(f"{y}:{r['mean']}%(n={int(r['size'])})"
                                                   for y, r in yr.iterrows()))
    return t


t5 = analyse(m5, "5-MINUTE", k=3, max_gap=60)
t15 = analyse(m15, "15-MINUTE", k=3, max_gap=60)
t5b = analyse(m5, "5-MINUTE (wider swings)", k=6, max_gap=90)

with open(os.path.join(OUT, "15_rsi_divergence.txt"), "w") as f:
    f.write("\n".join(lines))
