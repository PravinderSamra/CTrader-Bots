"""Costed backtests of volume-profile strategies (levels = PRIOR dealing day).

  S1  POC displacement rotation (user's example): after first POC touch, price
      displaces 0.3*halfVA off POC -> stop-entry that direction, TP = that side's
      VA edge, stop = 0.3*halfVA beyond POC on the other side. S1b: same, no TP.
  S2  Gap-into-value fade: open outside prior VA -> enter at open toward VA,
      TP = nearer VA edge, stop = 0.5*VAwidth beyond open.
  S3  Inside-open POC magnet: open inside VA and >=0.25*VAwidth from POC ->
      enter toward POC, TP = POC, stop = 0.35*VAwidth beyond entry (away from POC).
  S4  '80% rule' rotation (for the record): acceptance entry at VA edge after
      outside open + 2x15m closes inside, TP far edge, stop 0.5*VAwidth back out.
  S5  VA-edge rejection fade: day opened inside VA; after 12:00 first touch of
      VAH (short) / VAL (long) -> limit at edge, TP = POC, stop 0.25*VAwidth out.
Cost $0.40/oz RT. R = pnl / initial stop distance. Flat 20:55 UTC.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
CACHE = os.environ.get(
    "XAU_CACHE",
    "/tmp/claude-0/-home-user-CTrader-Bots/952eda8c-76b6-5df8-9ee5-680db4472e55/scratchpad/xau_cache",
)

m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40
profiles = pd.read_pickle(os.path.join(CACHE, "profiles.pkl"))
P = profiles.copy()
P["p_poc"] = P.poc.shift(1); P["p_vah"] = P.vah.shift(1); P["p_val"] = P.val.shift(1)
P["p_vaw"] = P.va_w.shift(1)
P = P.dropna(subset=["p_poc", "p_vaw"])

g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
g["tod"] = g.index.hour * 60 + g.index.minute
day_bars = {day: seg for day, seg in g.groupby("day")}
FLAT = 20 * 60 + 55

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

def stats(rows, label, yearly=True):
    t = pd.DataFrame(rows)
    if len(t) == 0:
        emit(f"\n--- {label} ---\nno trades")
        return t
    t["R"] = t.pnl / t.risk
    t["year"] = pd.to_datetime(t.day.astype(str)).dt.year
    eq = t.R.cumsum(); dd = (eq - eq.cummax()).min()
    emit(f"\n--- {label} ---")
    emit(f"n={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} "
         f"avgWin={t[t.R>0].R.mean():+.2f} avgLoss={t[t.R<=0].R.mean():+.2f} "
         f"totR={t.R.sum():+.1f} maxDD={dd:.1f}R")
    if yearly:
        emit(t.groupby("year").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                                   totR=("R", "sum"), avgR=("R", "mean")).round(2).to_string())
    return t

def sim(seg, i0, side, entry, stop, tp):
    """simulate from bar index i0 (inclusive) on seg arrays; returns pnl."""
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    for i in range(i0, len(seg)):
        if tod[i] >= FLAT:
            return side * (c[i - 1] - entry) - COST if i > i0 else side * (c[i] - entry) - COST
        if side == 1:
            if l[i] <= stop:
                return stop - entry - COST
            if tp is not None and h[i] >= tp:
                return tp - entry - COST
        else:
            if h[i] >= stop:
                return entry - stop - COST
            if tp is not None and l[i] <= tp:
                return entry - tp - COST
    return side * (c[-1] - entry) - COST

def first_idx(seg, level, how, after_i=0):
    h = seg.high.to_numpy(); l = seg.low.to_numpy()
    n = len(seg)
    for i in range(after_i, n):
        if how == "up" and h[i] >= level:
            return i
        if how == "dn" and l[i] <= level:
            return i
    return None

# ---------------- S1 ----------------
def s1(use_tp, min_tp_dist_frac, label, entry_from=0):
    rows = []
    for day, row in P.iterrows():
        seg = day_bars.get(day)
        if seg is None or len(seg) < 300:
            continue
        half = row.p_vaw / 2
        i_poc = min([x for x in (first_idx(seg, row.p_poc, "up"), first_idx(seg, row.p_poc, "dn")) if x is not None], default=None)
        if i_poc is None:
            continue
        cu, cd = row.p_poc + 0.3 * half, row.p_poc - 0.3 * half
        iu = first_idx(seg, cu, "up", i_poc)
        idn = first_idx(seg, cd, "dn", i_poc)
        if iu is None and idn is None:
            continue
        if idn is None or (iu is not None and iu < idn):
            side, i0, entry = 1, iu, cu
            tp = row.p_vah if use_tp else None
            stop = row.p_poc - 0.3 * half
            tp_dist = row.p_vah - entry
        else:
            side, i0, entry = -1, idn, cd
            tp = row.p_val if use_tp else None
            stop = row.p_poc + 0.3 * half
            tp_dist = entry - row.p_val
        if seg.tod.iloc[i0] < entry_from:
            continue
        if use_tp and tp_dist < min_tp_dist_frac * row.p_vaw:
            continue  # degenerate skewed-VA geometry: target too close
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        pnl = sim(seg, i0, side, entry, stop, tp)
        rows.append(dict(day=day, pnl=pnl, risk=risk))
    return stats(rows, label)

s1(True, -1, "S1 POC displacement -> TP at VA edge (all geometries)")
s1(True, 0.25, "S1f POC displacement -> TP at edge, skip if target <0.25*VAwidth away")
s1(False, -1, "S1b POC displacement, no TP (stop + 20:55 exit)")

# ---------------- S2 ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    if row.p_val <= op <= row.p_vah:
        continue
    above = op > row.p_vah
    side = -1 if above else 1
    tp = row.p_vah if above else row.p_val
    stop = op + (0.5 * row.p_vaw if above else -0.5 * row.p_vaw)
    risk = abs(op - stop)
    tpd = abs(op - tp)
    if risk <= 0 or tpd < 0.3:
        continue
    pnl = sim(seg, 1, side, op, stop, tp)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S2 open outside VA -> fade to nearer edge (stop 0.5*VAw)")

# ---------------- S3 ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    if not (row.p_val <= op <= row.p_vah):
        continue
    d = op - row.p_poc
    if abs(d) < 0.25 * row.p_vaw:
        continue
    side = -1 if d > 0 else 1
    tp = row.p_poc
    stop = op - side * 0.35 * row.p_vaw
    risk = abs(op - stop)
    pnl = sim(seg, 1, side, op, stop, tp)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S3 inside open far from POC -> trade to POC")

# ---------------- S4 (80% rule) ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    if row.p_val <= op <= row.p_vah:
        continue
    above = op > row.p_vah
    c15 = seg.close.resample("15min").last().dropna()
    inside = ((c15 <= row.p_vah) & (c15 >= row.p_val)).to_numpy()
    acc_t = None
    for i in range(1, len(inside)):
        if inside[i] and inside[i - 1]:
            acc_t = c15.index[i]
            break
    if acc_t is None:
        continue
    i0 = int(seg.index.searchsorted(acc_t))
    if i0 >= len(seg) - 10:
        continue
    entry = seg.close.iloc[i0]
    side = -1 if above else 1
    tp = row.p_val if above else row.p_vah
    near = row.p_vah if above else row.p_val
    stop = near + (0.5 * row.p_vaw if above else -0.5 * row.p_vaw)
    risk = abs(entry - stop)
    tpd = abs(entry - tp)
    if risk <= 0 or tpd <= 0.3:
        continue
    pnl = sim(seg, i0 + 1, side, entry, stop, tp)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S4 '80% rule' acceptance rotation (for the record)")

# ---------------- S5 ----------------
def s5(stop_frac, tp_kind, label):
    rows = []
    for day, row in P.iterrows():
        seg = day_bars.get(day)
        if seg is None or len(seg) < 300:
            continue
        op = seg.open.iloc[0]
        if not (row.p_val <= op <= row.p_vah):
            continue
        tods = seg.tod.to_numpy()
        start = int(np.argmax(tods >= 12 * 60)) if (tods >= 12 * 60).any() else None
        if start is None:
            continue
        ivah = first_idx(seg, row.p_vah, "up", start)
        ival = first_idx(seg, row.p_val, "dn", start)
        if ivah is None and ival is None:
            continue
        if ival is None or (ivah is not None and ivah < ival):
            side, i0, entry = -1, ivah, row.p_vah
            stop = row.p_vah + stop_frac * row.p_vaw
        else:
            side, i0, entry = 1, ival, row.p_val
            stop = row.p_val - stop_frac * row.p_vaw
        tp = row.p_poc if tp_kind == "poc" else None
        if tp is not None and abs(entry - tp) < 0.5:
            continue
        risk = abs(entry - stop)
        pnl = sim(seg, i0, side, entry, stop, tp)
        rows.append(dict(day=day, pnl=pnl, risk=risk))
    return stats(rows, label)

s5(0.25, "poc", "S5 VA-edge rejection fade after 12:00 -> TP POC (stop 0.25*VAw)")
s5(0.40, "poc", "S5b same, wider stop 0.40*VAw")

with open(os.path.join(OUT, "13_profile_strategies.txt"), "w") as f:
    f.write("\n".join(lines))

# NOTE: RESULTS FROM THIS SCRIPT ARE INVALID — see 14_profile_fixed.py.
# Bug 1: first_idx used high>=level / low<=level as "touch", which is true
#        whenever price is merely beyond the level -> phantom fills far from market.
# Bug 2: sim()'s flatten check (tod >= 20:55) also fired on the 22:00-23:59
#        evening bars, instantly closing evening entries.
# Kept unmodified as the audit trail for VOLUME-PROFILE.md section 2.
