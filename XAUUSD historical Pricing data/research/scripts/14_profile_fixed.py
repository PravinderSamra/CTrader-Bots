"""CORRECTED volume-profile backtests. Supersedes 13_profile_strategies.py, whose
results were invalidated by two bugs (kept for the audit trail):
  (1) "touch" tested high>=level / low<=level, which is true whenever price is
      merely beyond the level -> phantom fills far from market;
  (2) the 20:55 flatten check fired on the 22:00-23:59 evening bars (tod wraps),
      instantly closing evening entries.
Here: a touch/cross requires the bar to trade AT the level (low<=lvl<=high),
level entries fill only when approached from the correct side, and the flatten
window is exactly 20:55-20:59. Cost $0.40/oz RT. Levels = prior dealing day.
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

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

def is_flat_time(tod_val):
    return 20 * 60 + 55 <= tod_val < 21 * 60

def sim(tod, h, l, c, i0, side, entry, stop, tp, check_entry_bar_stop=True):
    """Simulate from bar i0. Entry assumed filled during bar i0.
    Conservative: stop checked on the entry bar itself (adverse-first)."""
    n = len(tod)
    for i in range(i0, n):
        if is_flat_time(tod[i]):
            px = c[i - 1] if i > i0 else c[i]
            return side * (px - entry) - COST
        if i == i0 and not check_entry_bar_stop:
            continue
        if side == 1:
            if l[i] <= stop:
                return stop - entry - COST
            if tp is not None and i > i0 and h[i] >= tp:
                return tp - entry - COST
        else:
            if h[i] >= stop:
                return entry - stop - COST
            if tp is not None and i > i0 and l[i] <= tp:
                return entry - tp - COST
    return side * (c[-1] - entry) - COST

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

def true_touch_idx(l, h, level, start=0):
    for i in range(start, len(l)):
        if l[i] <= level <= h[i]:
            return i
    return None

# ---------------- S1 corrected: POC displacement rotation ----------------
def s1(use_tp, label):
    rows = []
    ambiguous = 0
    for day, row in P.iterrows():
        seg = day_bars.get(day)
        if seg is None or len(seg) < 300:
            continue
        tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy()
        c = seg.close.to_numpy()
        half = row.p_vaw / 2
        cu, cd = row.p_poc + 0.3 * half, row.p_poc - 0.3 * half
        j = true_touch_idx(l, h, row.p_poc)
        if j is None:
            continue
        # at close of touch bar decide state
        if c[j] >= cu:
            side, i0, entry = 1, j, c[j]           # already displaced up -> market at close
        elif c[j] <= cd:
            side, i0, entry = -1, j, c[j]
        else:
            side = 0
            for i in range(j + 1, len(seg)):
                if is_flat_time(tod[i]):
                    break
                hit_u = h[i] >= cu
                hit_d = l[i] <= cd
                if hit_u and hit_d:
                    ambiguous += 1
                    side = 1 if c[i] >= row.p_poc else -1
                    i0, entry = i, (cu if side == 1 else cd)
                    break
                if hit_u:
                    side, i0, entry = 1, i, cu
                    break
                if hit_d:
                    side, i0, entry = -1, i, cd
                    break
            if side == 0:
                continue
        if side == 1:
            tp = row.p_vah if use_tp else None
            stop = cd
            if use_tp and (row.p_vah - entry) <= 0.3:
                continue
        else:
            tp = row.p_val if use_tp else None
            stop = cu
            if use_tp and (entry - row.p_val) <= 0.3:
                continue
        risk = abs(entry - stop)
        if risk <= 0:
            continue
        pnl = sim(tod, h, l, c, i0 if entry in (cu, cd) else i0 + 1, side, entry, stop, tp)
        rows.append(dict(day=day, pnl=pnl, risk=risk))
    t = stats(rows, label)
    if ambiguous:
        emit(f"(ambiguous both-sides bars resolved by close: {ambiguous})")
    return t

s1(True, "S1-fix POC displacement -> TP at VA edge")
s1(False, "S1b-fix POC displacement, no TP")

# ---------------- S2 corrected: open outside VA -> fade to nearer edge ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    op = seg.open.iloc[0]
    if row.p_val <= op <= row.p_vah:
        continue
    above = op > row.p_vah
    side = -1 if above else 1
    tp = row.p_vah if above else row.p_val
    stop = op + (0.5 * row.p_vaw if above else -0.5 * row.p_vaw)
    risk = abs(op - stop)
    if risk <= 0 or abs(op - tp) < 0.3:
        continue
    pnl = sim(tod, h, l, c, 0, side, op, stop, tp)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S2-fix open outside VA -> fade to nearer edge")

# ---------------- S3 corrected: inside open, trade toward POC ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    op = seg.open.iloc[0]
    if not (row.p_val <= op <= row.p_vah):
        continue
    d = op - row.p_poc
    if abs(d) < 0.25 * row.p_vaw:
        continue
    side = -1 if d > 0 else 1
    stop = op - side * 0.35 * row.p_vaw
    risk = abs(op - stop)
    pnl = sim(tod, h, l, c, 0, side, op, stop, row.p_poc)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S3-fix inside open far from POC -> trade to POC")

# ---------------- S4 corrected: 80% rule ----------------
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
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    if is_flat_time(tod[i0]):
        continue
    entry = c[i0]
    side = -1 if above else 1
    tp = row.p_val if above else row.p_vah
    near = row.p_vah if above else row.p_val
    stop = near + (0.5 * row.p_vaw if above else -0.5 * row.p_vaw)
    risk = abs(entry - stop)
    if risk <= 0 or abs(entry - tp) <= 0.3:
        continue
    pnl = sim(tod, h, l, c, i0 + 1, side, entry, stop, tp)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S4-fix '80% rule' acceptance rotation")

# ---------------- S5 corrected: VA-edge rejection fade after 12:00 ----------------
rows = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    if not (row.p_val <= op <= row.p_vah):
        continue
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    day_part = np.where((tod >= 12 * 60) & (tod < 20 * 60))[0]
    if len(day_part) == 0:
        continue
    start = day_part[0]
    # price must still be inside VA at 12:00 for a limit at the edge to be valid
    if not (row.p_val <= c[start] <= row.p_vah):
        continue
    ivah = true_touch_idx(l, h, row.p_vah, start)
    ival = true_touch_idx(l, h, row.p_val, start)
    if ivah is not None and (ival is None or ivah < ival):
        side, i0, entry = -1, ivah, row.p_vah
        stop = row.p_vah + 0.25 * row.p_vaw
    elif ival is not None:
        side, i0, entry = 1, ival, row.p_val
        stop = row.p_val - 0.25 * row.p_vaw
    else:
        continue
    if tod[i0] >= 20 * 60:
        continue
    risk = abs(entry - stop)
    if risk <= 0 or abs(entry - row.p_poc) < 0.5:
        continue
    pnl = sim(tod, h, l, c, i0, side, entry, stop, row.p_poc)
    rows.append(dict(day=day, pnl=pnl, risk=risk))
stats(rows, "S5-fix VA-edge rejection fade after 12:00 -> TP POC")

# ---------------- corrected descriptive: displacement-confirm probability ----------------
emit("\n=== CORRECTED descriptive: POC displacement outcome (true-touch logic) ===")
wins = tot = 0
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    tod = seg.tod.to_numpy(); h = seg.high.to_numpy(); l = seg.low.to_numpy(); c = seg.close.to_numpy()
    half = row.p_vaw / 2
    cu, cd = row.p_poc + 0.3 * half, row.p_poc - 0.3 * half
    j = true_touch_idx(l, h, row.p_poc)
    if j is None or c[j] >= cu or c[j] <= cd:
        continue
    side = 0
    for i in range(j + 1, len(seg)):
        if h[i] >= cu and l[i] <= cd:
            break
        if h[i] >= cu:
            side, i0 = 1, i
            break
        if l[i] <= cd:
            side, i0 = -1, i
            break
    if side == 0:
        continue
    tgt = row.p_vah if side == 1 else row.p_val
    back = cd if side == 1 else cu
    if side * (tgt - (cu if side == 1 else cd)) <= 0:
        continue
    outcome = None
    for i in range(i0 + 1, len(seg)):
        if side == 1:
            if l[i] <= back:
                outcome = 0
                break
            if h[i] >= tgt:
                outcome = 1
                break
        else:
            if h[i] >= back:
                outcome = 0
                break
            if l[i] <= tgt:
                outcome = 1
                break
    if outcome is not None:
        wins += outcome
        tot += 1
emit(f"P(reach displaced-side VA edge before opposite confirm level) = {wins/tot*100:.1f}% (N={tot}, decided cases only)")

with open(os.path.join(OUT, "14_profile_fixed.txt"), "w") as f:
    f.write("\n".join(lines))
