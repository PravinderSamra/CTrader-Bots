"""Asia-range break -> pullback -> continuation entry (1m execution).

Mechanics (long side; short mirrored):
  - Asia range = 22:00-06:59 UTC high/low (a_hi, a_lo, rng).
  - BREAK: first 1m CLOSE beyond the range side, 07:00-16:00 UTC. First side to
    break gets the day (one trade/day max).
  - PULLBACK: after the break bar, price trades back to the broken level
    (low <= a_hi) within 120 minutes -> limit fill AT the level.
  - STOP: level -/+ k * rng   (k=0.50 == range mid; k=0.25 tighter)
  - TP:   entry +/- m * risk  (m in {None, 1.5, 2.0}); None = hold to 20:55 UTC.
  - Force-flat 20:55 UTC. Intrabar SL+TP both touched -> SL assumed first.
  - Cost $0.40/oz round trip. R = pnl / stop distance.
Variants: optional range filter (skip if rng < 0.25*ATR20 or > 1.25*ATR20).

Outputs: config grid table, session split (London vs NY break), walk-forward
(config picked on prior years only), Monte Carlo bootstrap of the WF stream.
"""
import os
from importlib import import_module

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
CH = os.path.join(os.path.dirname(__file__), "..", "charts")

m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40

d1 = d1.copy()
d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)

g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
g["tod"] = g.index.hour * 60 + g.index.minute

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

BREAK_START, BREAK_END = 7 * 60, 16 * 60
PULLBACK_MAX = 120           # minutes allowed for the retest
ENTRY_CUTOFF = 18 * 60       # no fills after 18:00
FLAT = 20 * 60 + 55

# ---- precompute per-day setup events once ----
day_setups = {}   # day -> dict(side, level, rng, atr, t_break_idx, arrays...)
for day, seg in g.groupby("day"):
    atr = atr_map.get(day)
    if pd.isna(atr):
        continue
    tod = seg["tod"].to_numpy()
    hi = seg["high"].to_numpy()
    lo = seg["low"].to_numpy()
    cl = seg["close"].to_numpy()
    asia_mask = (tod >= 22 * 60) | (tod < 7 * 60)
    if asia_mask.sum() < 60:
        continue
    a_hi, a_lo = hi[asia_mask].max(), lo[asia_mask].min()
    rng = a_hi - a_lo
    if rng <= 0:
        continue
    win = (tod >= BREAK_START) & (tod < BREAK_END)
    idx_win = np.where(win)[0]
    if len(idx_win) < 60:
        continue
    up = idx_win[cl[idx_win] > a_hi]
    dn = idx_win[cl[idx_win] < a_lo]
    i_up = up[0] if len(up) else None
    i_dn = dn[0] if len(dn) else None
    if i_up is None and i_dn is None:
        continue
    if i_dn is None or (i_up is not None and i_up < i_dn):
        side, ib, level = 1, i_up, a_hi
    else:
        side, ib, level = -1, i_dn, a_lo
    day_setups[day] = dict(side=side, ib=ib, level=level, rng=rng, atr=atr,
                           tod=tod, hi=hi, lo=lo, cl=cl,
                           t_break=tod[ib])

emit(f"days with a qualifying first break 07:00-16:00: {len(day_setups)} / 1290")

def run(k_stop, tp_mult, use_filter):
    rows = []
    for day, s in day_setups.items():
        if use_filter and not (0.25 * s["atr"] <= s["rng"] <= 1.25 * s["atr"]):
            continue
        side, ib, level, rng = s["side"], s["ib"], s["level"], s["rng"]
        tod, hi, lo, cl = s["tod"], s["hi"], s["lo"], s["cl"]
        t_break = tod[ib]
        risk = k_stop * rng
        stop = level - side * risk
        tp = level + side * tp_mult * risk if tp_mult else None
        # pullback search after break bar
        j = None
        for i in range(ib + 1, len(tod)):
            if tod[i] >= min(t_break + PULLBACK_MAX, ENTRY_CUTOFF) or tod[i] >= FLAT:
                break
            touched = lo[i] <= level if side == 1 else hi[i] >= level
            if touched:
                j = i
                break
        if j is None:
            continue
        pnl = None
        exit_tod = None
        for i in range(j, len(tod)):
            if tod[i] >= FLAT:
                break
            if side == 1:
                if lo[i] <= stop:
                    pnl = stop - level - COST
                    exit_tod = tod[i]
                    break
                if tp and hi[i] >= tp:
                    pnl = tp - level - COST
                    exit_tod = tod[i]
                    break
            else:
                if hi[i] >= stop:
                    pnl = level - stop - COST
                    exit_tod = tod[i]
                    break
                if tp and lo[i] <= tp:
                    pnl = level - tp - COST
                    exit_tod = tod[i]
                    break
        if pnl is None:
            last = np.where(tod < FLAT)[0][-1]
            pnl = side * (cl[last] - level) - COST
            exit_tod = tod[last]
        rows.append(dict(day=day, side=side, pnl=pnl, risk=risk, atr=s["atr"],
                         t_break=t_break, t_entry=tod[j], t_exit=exit_tod))
    t = pd.DataFrame(rows)
    if len(t) == 0:
        return t
    t["R"] = t.pnl / t.risk
    t["date"] = pd.to_datetime(t.day.astype(str))
    t["year"] = t.date.dt.year
    return t

def stats(t, label, per_year=False):
    if len(t) == 0:
        emit(f"{label}: no trades")
        return
    sharpe = t.R.mean() / t.R.std() * np.sqrt(252 * len(t) / t.date.nunique() if False else 252)
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    w = t[t.R > 0]
    emit(f"{label}: trades={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} "
         f"avgWin={w.R.mean():+.2f} avgLoss={t[t.R<=0].R.mean():+.2f} "
         f"Sharpe~{t.R.mean()/t.R.std()*np.sqrt(200):.2f} maxDD={dd:.1f}R totR={t.R.sum():+.0f}")
    if per_year:
        emit(t.groupby("year").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                                   totR=("R", "sum"), avgR=("R", "mean")).round(2).to_string())

emit("\n=== CONFIG GRID (R = on actual stop distance, net $0.40 cost) ===")
grid = {}
for k in (0.25, 0.50):
    for tp in (None, 1.5, 2.0):
        for filt in (False, True):
            name = f"k={k} tp={tp or 'none'} filter={'Y' if filt else 'N'}"
            t = run(k, tp, filt)
            grid[(k, tp, filt)] = t
            stats(t, name)

# ---- chosen base config detail ----
emit("\n=== DETAIL: k=0.5, tp=2.0, no filter ===")
best = grid[(0.5, 2.0, False)]
stats(best, "base", per_year=True)

emit("\n=== SESSION OF BREAK: London break (07:00-11:59) vs NY break (12:00-15:59) ===")
for cfg, lbl in [((0.5, 2.0, False), "k=0.5 tp=2"), ((0.5, None, False), "k=0.5 no-tp")]:
    t = grid[cfg]
    t = t.copy()
    t["sess"] = np.where(t.t_break < 12 * 60, "London", "NY")
    emit(f"-- {lbl} --")
    emit(t.groupby("sess").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                               avgR=("R", "mean"), totR=("R", "sum")).round(3).to_string())
    emit("by side:")
    emit(t.groupby(["sess", "side"]).agg(n=("R", "size"), avgR=("R", "mean")).round(3).to_string())

# ---- walk-forward: pick config on prior years, trade next year ----
emit("\n=== WALK-FORWARD (config chosen each year on ALL PRIOR data by avgR*sqrt(n)) ===")
years = [2022, 2023, 2024, 2025, 2026]
wf_parts = []
for y in years:
    scores = {}
    for cfg, t in grid.items():
        pri = t[t.year < y]
        if len(pri) < 60:
            continue
        scores[cfg] = pri.R.mean() / pri.R.std() * np.sqrt(len(pri))
    pick = max(scores, key=scores.get)
    oos = grid[pick][grid[pick].year == y]
    wf_parts.append(oos)
    emit(f"  {y}: picked k={pick[0]} tp={pick[1] or 'none'} filter={'Y' if pick[2] else 'N'} "
         f"-> OOS n={len(oos)} win%={(oos.R>0).mean()*100:.1f} totR={oos.R.sum():+.1f} avgR={oos.R.mean():+.3f}")
wf = pd.concat(wf_parts).sort_values("date")
stats(wf, "\nWALK-FORWARD combined OOS", per_year=False)

# daily / monthly R for WF stream
daily = wf.groupby("date")["R"].sum()
wf["ym"] = wf.date.dt.to_period("M")
monthly = wf.groupby("ym")["R"].sum()
emit(f"\nWF trades/week~{len(wf)/ (wf.date.nunique()/5):.1f}  R/day: mean={daily.mean():+.3f} "
     f"| R/month: mean={monthly.mean():+.2f} med={monthly.median():+.2f} best={monthly.max():+.1f} "
     f"worst={monthly.min():+.1f} pos-months={(monthly>0).mean()*100:.0f}% of {len(monthly)}")

# ---- Monte Carlo bootstrap on WF trade stream ----
emit("\n=== MONTE CARLO (5,000 bootstrap years of 190 trades, sampled from WF OOS R's) ===")
rs = wf.R.to_numpy()
np.random.seed(42)
N_TRADES, N_SIM = 190, 5000
ann_ret, max_dds, worst_streaks = [], [], []
for _ in range(N_SIM):
    path = np.random.choice(rs, N_TRADES, replace=True)
    eq = np.cumsum(path)
    ann_ret.append(eq[-1])
    max_dds.append((eq - np.maximum.accumulate(eq)).min())
    # longest losing streak
    streak = best_s = 0
    for r in path:
        streak = streak + 1 if r <= 0 else 0
        best_s = max(best_s, streak)
    worst_streaks.append(best_s)
ann_ret, max_dds = np.array(ann_ret), np.array(max_dds)
pct = lambda a, q: np.percentile(a, q)
emit(f"annual R:  p5={pct(ann_ret,5):+.0f}  p25={pct(ann_ret,25):+.0f}  median={pct(ann_ret,50):+.0f}  "
     f"p75={pct(ann_ret,75):+.0f}  p95={pct(ann_ret,95):+.0f}   P(negative year)={(ann_ret<0).mean()*100:.1f}%")
emit(f"max DD  :  p5(worst)={pct(max_dds,5):.1f}R  p25={pct(max_dds,25):.1f}R  median={pct(max_dds,50):.1f}R  p95(best)={pct(max_dds,95):.1f}R")
emit(f"longest losing streak: median={np.median(worst_streaks):.0f}  p95={np.percentile(worst_streaks,95):.0f} trades")
for risk_pct in (0.5, 1.0, 2.0):
    dd_pct = max_dds * risk_pct
    ann_pct = ann_ret * risk_pct
    emit(f"  at {risk_pct}%/trade: median year {np.median(ann_pct):+.1f}% | median maxDD {np.median(dd_pct):.1f}% | p5 maxDD {pct(dd_pct,5):.1f}%")

# ---- charts ----
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
ax[0].plot(wf.date, wf.R.cumsum(), lw=1, color="#4477aa", label="walk-forward OOS")
b = grid[(0.5, 2.0, False)]
ax[0].plot(b.date, b.R.cumsum(), lw=1, color="#ee7733", alpha=0.7, label="k=0.5 tp=2 full")
ax[0].set_title("Asia break->pullback scalp — equity (R)")
ax[0].legend()
ax[1].hist(max_dds, bins=50, color="#cc3311", alpha=0.8)
ax[1].set_title(f"MC max drawdown distribution ({N_TRADES}-trade years)")
ax[1].set_xlabel("R")
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(os.path.join(CH, "asia_pullback.png"), dpi=120)
emit("\nsaved charts/asia_pullback.png")

with open(os.path.join(OUT, "06_asia_pullback.txt"), "w") as f:
    f.write("\n".join(lines))
