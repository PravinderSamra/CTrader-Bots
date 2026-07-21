"""Strategies derived from the 08 diagnostics.

A) Asia VWAP fade      — OU reversion: fade >2sd deviations from session VWAP, 23:00-06:00
B) London VWAP fade    — VR(London)<1: fade >2sd deviations from 07:00-anchored VWAP
C) Post-jump straddle  — jump clustering: after first 4-sigma 1m jump 12:00-15:30,
                         bracket +/-0.15 ATR, stop = far bracket, TP 1.5R, 2h time-out
Costs $0.40/oz RT. R = pnl/stop distance.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")

m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40
d1 = d1.copy()
d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

def stats(rows, label, yearly=True):
    t = pd.DataFrame(rows)
    if len(t) == 0:
        emit(f"{label}: no trades")
        return t
    t["R"] = t.pnl / t.risk
    t["date"] = pd.to_datetime(t.day.astype(str))
    t["year"] = t.date.dt.year
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    emit(f"\n--- {label} ---")
    emit(f"n={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} "
         f"avgWin={t[t.R>0].R.mean():+.2f} avgLoss={t[t.R<=0].R.mean():+.2f} "
         f"totR={t.R.sum():+.1f} maxDD={dd:.1f}R")
    if yearly:
        emit(t.groupby("year").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                                   totR=("R", "sum"), avgR=("R", "mean")).round(2).to_string())
    return t

# ---------- shared VWAP-fade engine on 5m bars ----------
def vwap_fade(anchor_h, entry_from_min, entry_to_min, flat_min, sd_in, sd_stop, label, max_trades=2):
    m5x = m5.copy()
    m5x["day"] = (m5x.index - pd.Timedelta(hours=22)).date
    m5x["tod"] = m5x.index.hour * 60 + m5x.index.minute
    rows = []
    for day, seg in m5x.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        # session slice starting at anchor
        if anchor_h >= 22:
            sess = seg[(seg.tod >= anchor_h * 60) | (seg.tod < flat_min)]
        else:
            sess = seg[(seg.tod >= anchor_h * 60) & (seg.tod < flat_min)]
        if len(sess) < 24:
            continue
        tp_ = (sess.high + sess.low + sess.close) / 3
        cumv = sess.volume.cumsum()
        vwap = (tp_ * sess.volume).cumsum() / cumv
        dev = (sess.close - vwap).to_numpy()
        sd = pd.Series(dev).expanding().std().to_numpy()
        tod = sess.tod.to_numpy()
        cl = sess.close.to_numpy()
        hi = sess.high.to_numpy()
        lo = sess.low.to_numpy()
        vw = vwap.to_numpy()
        n_trades = 0
        i = 0
        while i < len(sess) and n_trades < max_trades:
            in_window = (tod[i] >= entry_from_min or tod[i] < entry_to_min) if anchor_h >= 22 \
                        else (entry_from_min <= tod[i] < entry_to_min)
            if in_window and i >= 12 and sd[i] > 0 and abs(dev[i]) > sd_in * sd[i]:
                side = -np.sign(dev[i])          # fade toward vwap
                entry = cl[i]
                risk = (sd_stop - sd_in) * sd[i]
                stop = entry - side * risk
                pnl = None
                for jj in range(i + 1, len(sess)):
                    if tod[jj] >= flat_min and anchor_h < 22:
                        break
                    if side == 1 and lo[jj] <= stop:
                        pnl = stop - entry - COST
                        break
                    if side == -1 and hi[jj] >= stop:
                        pnl = entry - stop - COST
                        break
                    crossed = (cl[jj] >= vw[jj]) if side == 1 else (cl[jj] <= vw[jj])
                    if crossed:
                        pnl = side * (cl[jj] - entry) - COST
                        break
                if pnl is None:
                    jj = len(sess) - 1
                    pnl = side * (cl[jj] - entry) - COST
                rows.append({"day": day, "pnl": pnl, "risk": risk})
                n_trades += 1
                i = jj + 3
            else:
                i += 1
    return stats(rows, label)

# A) Asia
vwap_fade(22, 23 * 60, 6 * 60, 7 * 60, 2.0, 3.5, "A) Asia VWAP fade  (in>2.0sd, stop 3.5sd, exit VWAP/07:00)")
vwap_fade(22, 23 * 60, 6 * 60, 7 * 60, 2.5, 4.0, "A2) Asia VWAP fade (in>2.5sd, stop 4.0sd)")
# B) London
vwap_fade(7, 8 * 60, 11 * 60 + 30, 12 * 60, 2.0, 3.5, "B) London VWAP fade (anchor 07:00, in>2sd, exit VWAP/12:00)")
vwap_fade(7, 8 * 60, 11 * 60 + 30, 12 * 60, 2.5, 4.0, "B2) London VWAP fade (in>2.5sd)")

# ---------- C) post-jump straddle on 1m ----------
r1 = np.log(m1.close).diff()
sig1 = r1.rolling(1440).std()
jump_mask = (np.abs(r1) > 4 * sig1)
g1 = m1.copy()
g1["day"] = (g1.index - pd.Timedelta(hours=22)).date
g1["tod"] = g1.index.hour * 60 + g1.index.minute
g1["jump"] = jump_mask.reindex(g1.index).fillna(False)

def straddle(width_atr, tp_R, timeout_min, label):
    rows = []
    for day, seg in g1.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        tod = seg.tod.to_numpy()
        hi = seg.high.to_numpy()
        lo = seg.low.to_numpy()
        cl = seg.close.to_numpy()
        jm = seg.jump.to_numpy()
        cand = np.where(jm & (tod >= 12 * 60) & (tod < 15 * 60 + 30))[0]
        if len(cand) == 0:
            continue
        ij = cand[0]
        base_i = min(ij + 5, len(seg) - 1)     # arm brackets 5 min after the jump bar
        base = cl[base_i]
        up, dn = base + width_atr * atr, base - width_atr * atr
        risk = 2 * width_atr * atr
        filled = None
        for i in range(base_i + 1, len(seg)):
            if tod[i] >= 20 * 60 or tod[i] - tod[base_i] > 60:
                break
            if hi[i] >= up:
                filled, side, entry, stop, t0 = True, 1, up, dn, i
                break
            if lo[i] <= dn:
                filled, side, entry, stop, t0 = True, -1, dn, up, i
                break
        if not filled:
            continue
        tp = entry + side * tp_R * risk
        pnl = None
        for i in range(t0, len(seg)):
            if tod[i] >= 20 * 60 or tod[i] - tod[t0] > timeout_min:
                pnl = side * (cl[i] - entry) - COST
                break
            if side == 1 and lo[i] <= stop:
                pnl = stop - entry - COST
                break
            if side == -1 and hi[i] >= stop:
                pnl = entry - stop - COST
                break
            if side == 1 and hi[i] >= tp:
                pnl = tp - entry - COST
                break
            if side == -1 and lo[i] <= tp:
                pnl = entry - tp - COST
                break
        if pnl is None:
            pnl = side * (cl[-1] - entry) - COST
        rows.append({"day": day, "pnl": pnl, "risk": risk})
    return stats(rows, label)

straddle(0.15, 1.5, 120, "C) Post-jump straddle (0.15 ATR brackets, TP 1.5R, 2h timeout)")
straddle(0.10, 2.0, 120, "C2) Post-jump straddle (0.10 ATR brackets, TP 2R)")
straddle(0.15, None if False else 10.0, 240, "C3) Post-jump straddle (0.15 ATR, no real TP, 4h timeout)")

with open(os.path.join(OUT, "09_physics_strategies.txt"), "w") as f:
    f.write("\n".join(lines))
