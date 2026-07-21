"""Practical implementation tests + weekend gaps + regime stats + charts.

1) S1 overnight long with protective stops (does a stop kill the edge?)
2) S1 with trend filter (only when close > 20-day SMA)
3) NY ORB (S3a) equity curve + with 1.5R take-profit variant
4) Weekend gap stats (fixed ATR mapping)
5) Regime table: ATR by year/month, daily trend persistence
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
d1["sma20"] = d1.close.rolling(20).mean().shift(1)
# ATR/SMA lookup by calendar date, forward-filled so every weekday resolves
cal_idx = pd.date_range(m1.index[0].date(), m1.index[-1].date(), freq="D")
atr_daily = pd.Series(d1["atr20"].values, index=pd.to_datetime((d1.index - pd.Timedelta(hours=22)).date))
atr_ff = atr_daily.reindex(cal_idx).ffill()
sma_daily = pd.Series(d1["sma20"].values, index=pd.to_datetime((d1.index - pd.Timedelta(hours=22)).date))
sma_ff = sma_daily.reindex(cal_idx).ffill()

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

px = m1.copy()
px["date"] = pd.to_datetime(px.index.date)
px["tod"] = px.index.hour * 60 + px.index.minute

p20 = px[px.tod >= 20 * 60].groupby("date")["open"].first()
pclose = px[px.tod < 21 * 60 + 5].groupby("date")["close"].last()
p22 = px[px.tod >= 22 * 60].groupby("date")["open"].first()
p02 = px[px.tod >= 2 * 60].groupby("date")["open"].first()

# ------------------------------------------------ 1) S1 with stops
def s1_stops(stop_atr_frac, use_trend, label):
    rows = []
    dates = sorted(set(p20.index))
    for dt_ in dates:
        if dt_.dayofweek >= 4:  # Mon-Thu entries only
            continue
        nxt = dt_ + pd.Timedelta(days=1)
        atr = atr_ff.get(dt_)
        if pd.isna(atr):
            continue
        if use_trend:
            sma = sma_ff.get(dt_)
            e0 = p20.get(dt_)
            if pd.isna(sma) or pd.isna(e0) or e0 < sma:
                continue
        entry = p20.get(dt_)
        exitp = p02.get(nxt)
        if pd.isna(entry) or pd.isna(exitp):
            continue
        pnl = None
        if stop_atr_frac:
            stop = entry - stop_atr_frac * atr
            seg = m1[(m1.index >= pd.Timestamp(dt_, tz="UTC") + pd.Timedelta(hours=20)) &
                     (m1.index < pd.Timestamp(nxt, tz="UTC") + pd.Timedelta(hours=2))]
            if (seg.low <= stop).any():
                pnl = stop - entry - COST
        if pnl is None:
            pnl = exitp - entry - COST
        rows.append({"day": dt_, "pnl": pnl, "atr": atr})
    t = pd.DataFrame(rows).dropna()
    t["year"] = t.day.dt.year
    t["R"] = t.pnl / t.atr
    sharpe = t.R.mean() / t.R.std() * np.sqrt(252)
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    emit(f"\n--- {label} ---")
    emit(f"trades={len(t)}  win%={(t.pnl>0).mean()*100:.1f}  avg $/oz={t.pnl.mean():+.2f}  "
         f"exp={t.R.mean()*100:+.2f}% ATR  Sharpe~{sharpe:.2f}  maxDD={dd:.1f}R")
    emit(t.groupby("year").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                               total=("pnl", "sum"), avg_R=("R", "mean")).round(2).to_string())
    return t

t_nostop = s1_stops(None, False, "S1 no stop (baseline)")
t_stop50 = s1_stops(0.50, False, "S1 with 0.50*ATR stop")
t_stop33 = s1_stops(0.33, False, "S1 with 0.33*ATR stop")
t_trend = s1_stops(0.50, True, "S1 trend-filtered (close>SMA20) + 0.50*ATR stop")

# ------------------------------------------------ 2) NY ORB with TP variant
g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
g["tod"] = g.index.hour * 60 + g.index.minute
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)

def orb(tp_mult, label):
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        o_s = 13 * 60 + 30
        orb_ = seg[(seg.tod >= o_s) & (seg.tod < o_s + 30)]
        rest = seg[(seg.tod >= o_s + 30) & (seg.tod < 20 * 60)]
        if len(orb_) < 28 or len(rest) < 30:
            continue
        o_hi, o_lo = orb_.high.max(), orb_.low.min()
        hit_up = rest.index[rest.high >= o_hi]
        hit_dn = rest.index[rest.low <= o_lo]
        t_up = hit_up[0] if len(hit_up) else pd.NaT
        t_dn = hit_dn[0] if len(hit_dn) else pd.NaT
        if pd.isna(t_up) and pd.isna(t_dn):
            continue
        if pd.isna(t_dn) or (not pd.isna(t_up) and t_up < t_dn):
            side, t0, entry, stop = 1, t_up, o_hi, o_lo
        else:
            side, t0, entry, stop = -1, t_dn, o_lo, o_hi
        risk = abs(entry - stop)
        tp = entry + side * tp_mult * risk if tp_mult else None
        live = rest[rest.index >= t0]
        pnl = None
        for ts, bar in live.iterrows():
            if side == 1:
                if bar.low <= stop:
                    pnl = stop - entry - COST
                    break
                if tp and bar.high >= tp:
                    pnl = tp - entry - COST
                    break
            else:
                if bar.high >= stop:
                    pnl = entry - stop - COST
                    break
                if tp and bar.low <= tp:
                    pnl = entry - tp - COST
                    break
        if pnl is None:
            pnl = side * (live.iloc[-1].close - entry) - COST
        rows.append({"day": day, "pnl": pnl, "atr": atr, "risk": risk})
    t = pd.DataFrame(rows).dropna()
    t["year"] = pd.to_datetime(t.day.astype(str)).dt.year
    t["R"] = t.pnl / t.atr
    t["Rrisk"] = t.pnl / t.risk
    sharpe = t.R.mean() / t.R.std() * np.sqrt(252)
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    emit(f"\n--- {label} ---")
    emit(f"trades={len(t)}  win%={(t.pnl>0).mean()*100:.1f}  avg R-on-risk={t.Rrisk.mean():+.3f}  "
         f"exp={t.R.mean()*100:+.2f}% ATR  Sharpe~{sharpe:.2f}  maxDD={dd:.1f}R")
    emit(t.groupby("year").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                               avg_Rrisk=("Rrisk", "mean")).round(3).to_string())
    return t

t_orb = orb(None, "NY ORB baseline (no TP, exit 20:00)")
t_orb2 = orb(2.0, "NY ORB with 2R take-profit")

# ------------------------------------------------ 3) weekend gaps (fixed)
fri = pclose[pclose.index.dayofweek == 4]
sun = p22[p22.index.dayofweek == 6]
wk = pd.DataFrame({"fri": fri})
sun_shift = pd.Series(sun.values, index=sun.index - pd.Timedelta(days=2))
wk["sun"] = sun_shift.reindex(wk.index)
wk["atr"] = atr_ff.reindex(wk.index)
wk = wk.dropna()
wk["gap"] = wk.sun - wk.fri
wk["ngap"] = wk.gap / wk.atr
emit(f"\n=== WEEKEND GAPS (Fri close -> Sun 22:00 reopen), N={len(wk)} ===")
emit(f"mean={wk.gap.mean():+.2f} $/oz ({wk.ngap.mean()*100:+.1f}% ATR)  P(up)={(wk.gap>0).mean()*100:.0f}%  mean|gap|={wk.gap.abs().mean():.2f} $/oz ({wk.ngap.abs().mean()*100:.1f}% ATR)")
fills, fills_big = [], []
for dt_, row in wk.iterrows():
    start = pd.Timestamp(dt_ + pd.Timedelta(days=2, hours=22), tz="UTC")
    seg = m1[(m1.index >= start) & (m1.index < start + pd.Timedelta(hours=24))]
    if len(seg) == 0 or row.gap == 0:
        continue
    filled = (seg.low <= row.fri).any() if row.gap > 0 else (seg.high >= row.fri).any()
    fills.append(filled)
    if abs(row.gap) > 0.15 * row.atr:
        fills_big.append(filled)
emit(f"P(fill within 24h): all={np.mean(fills)*100:.0f}% (N={len(fills)})  large>15%ATR={np.mean(fills_big)*100:.0f}% (N={len(fills_big)})")

# ------------------------------------------------ 4) regime table
emit("\n=== REGIME: monthly ATR20 ($) at month end ===")
mtx = d1["atr20"].resample("ME").last().dropna()
emit(mtx.groupby([mtx.index.year, mtx.index.month]).last().round(1).unstack().to_string())
emit("\nDaily trend persistence P(sign(today)==sign(yesterday)):")
dr = np.sign(d1.close.diff())
emit(f"  all: {(dr == dr.shift(1)).mean()*100:.1f}%")
for y in range(2021, 2027):
    seg = dr[dr.index.year == y]
    emit(f"  {y}: {(seg == seg.shift(1)).mean()*100:.1f}%")

# ------------------------------------------------ charts
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
for t, lbl in [(t_nostop, "no stop"), (t_stop50, "0.5 ATR stop"), (t_trend, "trend-filtered")]:
    ax[0].plot(pd.to_datetime(t.day.astype(str)), t.R.cumsum(), label=lbl, lw=1)
ax[0].set_title("S1 overnight long 20:00→02:00 — equity (ATR units)")
ax[0].legend()
for t, lbl in [(t_orb, "no TP"), (t_orb2, "2R TP")]:
    ax[1].plot(pd.to_datetime(t.day.astype(str)), t.R.cumsum(), label=lbl, lw=1)
ax[1].set_title("NY ORB 13:30+30m — equity (ATR units)")
ax[1].legend()
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(os.path.join(CH, "equity_curves.png"), dpi=120)
emit("\nsaved charts/equity_curves.png")

with open(os.path.join(OUT, "05_practical.txt"), "w") as f:
    f.write("\n".join(lines))
