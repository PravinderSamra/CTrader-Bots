"""Backtests of candidate strategies on 1-minute data with realistic costs.

Cost model: $0.40/oz round trip (typical raw-spread XAUUSD ~$0.20-0.30 + slippage).
Sizing: 1 oz per trade for $/oz stats + ATR-normalised R stats (risk unit = ATR20).
Strategies:
  S1 Overnight drift  : long 20:00 UTC -> exit 02:00 (variants; skip/keep Friday)
  S2 Asian breakout   : stop orders at Asian range +/- buffer from 07:00, time exit 20:55
  S3 NY ORB           : 13:30 open, 30-min opening range, breakout to 20:00
  S4 London->NY cont. : at 12:00 if price beyond Asian range, ride to 20:55
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")

m1, m5, m15, h1, d1 = prep.load_all()
COST = 0.40  # $/oz round trip

d1 = d1.copy()
d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)

g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
g["tod"] = g.index.hour * 60 + g.index.minute  # minutes past midnight UTC

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

def summarize(name, trades: pd.DataFrame):
    """trades: DataFrame with columns [day, pnl, atr]; pnl in $/oz net of cost."""
    if len(trades) == 0:
        emit(f"{name}: no trades")
        return
    t = trades.dropna(subset=["pnl"]).copy()
    t["year"] = pd.to_datetime(t["day"]).dt.year
    t["R"] = t.pnl / t.atr
    exp_R = t.R.mean()
    sd_R = t.R.std()
    sharpe = exp_R / sd_R * np.sqrt(252) if sd_R > 0 else np.nan
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    emit(f"\n--- {name} ---")
    emit(f"trades={len(t)}  win%={(t.pnl>0).mean()*100:.1f}  avg $/oz={t.pnl.mean():+.2f}  "
         f"median $/oz={t.pnl.median():+.2f}")
    emit(f"expectancy={exp_R*100:+.2f}% of ATR/trade  ann.Sharpe~{sharpe:.2f}  maxDD={dd:.1f} ATR-units")
    yr = t.groupby("year").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                               total=("pnl", "sum"), avg_R=("R", "mean"))
    emit(yr.round(2).to_string())

# ---------------------------------------------------------------- S1 overnight
def s1(entry_min, exit_min, skip_fri, label):
    rows = []
    for day, seg in g.groupby("day"):
        wd = pd.Timestamp(day).weekday()
        if skip_fri and wd == 4:
            continue
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        e = seg[seg.tod >= entry_min]
        if len(e) == 0:
            continue
        entry = e.iloc[0].open
        # exit belongs to the NEXT dealing day (after 22:00 boundary)
        nxt = g[g.day == day + pd.Timedelta(days=1 if wd < 4 else 3)]
        if len(nxt) == 0:
            continue
        x = nxt[nxt.tod >= exit_min]
        if len(x) == 0:
            continue
        exitp = x.iloc[0].open
        rows.append({"day": day, "pnl": exitp - entry - COST, "atr": atr})
    summarize(label, pd.DataFrame(rows))

s1(20 * 60, 2 * 60, skip_fri=False, label="S1a Overnight long 20:00->02:00 (incl. Fri->Mon)")
s1(20 * 60, 2 * 60, skip_fri=True, label="S1b Overnight long 20:00->02:00 (skip Friday)")
s1(20 * 60, 0, skip_fri=True, label="S1c Overnight long 20:00->00:00 (skip Friday)")

# S1d: enter at 22:00 reopen instead (avoids holding through the close auction)
def s1_reopen(exit_min, label):
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        e = seg[seg.tod >= 22 * 60]  # 22:00 of the *previous* calendar evening = start of dealing day
        if len(e) == 0:
            continue
        entry = e.iloc[0].open
        x = seg[(seg.tod >= exit_min) & (seg.tod < 21 * 60)]
        if len(x) == 0:
            continue
        exitp = x.iloc[0].open
        rows.append({"day": day, "pnl": exitp - entry - COST, "atr": atr})
    summarize(label, pd.DataFrame(rows))

s1_reopen(2 * 60, "S1d Long at 22:00 reopen -> exit 02:00")

# ------------------------------------------------------- S2 asian breakout
def s2(buffer_frac, stop_mode, label, entry_start=7 * 60, entry_end=14 * 60 + 30, exit_min=20 * 60 + 55):
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        asia = seg[(seg.tod >= 22 * 60) | (seg.tod < 7 * 60)]
        rest = seg[(seg.tod >= entry_start) & (seg.tod < exit_min)]
        if len(asia) < 60 or len(rest) < 60:
            continue
        a_hi, a_lo = asia.high.max(), asia.low.min()
        rng = a_hi - a_lo
        if rng <= 0:
            continue
        buf = buffer_frac * rng
        up_lvl, dn_lvl = a_hi + buf, a_lo - buf
        win = rest[rest.tod < entry_end]
        hit_up = win.index[win.high >= up_lvl]
        hit_dn = win.index[win.low <= dn_lvl]
        t_up = hit_up[0] if len(hit_up) else pd.NaT
        t_dn = hit_dn[0] if len(hit_dn) else pd.NaT
        if pd.isna(t_up) and pd.isna(t_dn):
            continue
        if pd.isna(t_dn) or (not pd.isna(t_up) and t_up < t_dn):
            side, t0, entry = 1, t_up, up_lvl
            stop = a_lo - buf if stop_mode == "range" else entry - 0.33 * atr
        else:
            side, t0, entry = -1, t_dn, dn_lvl
            stop = a_hi + buf if stop_mode == "range" else entry + 0.33 * atr
        live = rest[rest.index >= t0]
        pnl = None
        for ts, bar in live.iterrows():
            if side == 1 and bar.low <= stop:
                pnl = stop - entry - COST
                break
            if side == -1 and bar.high >= stop:
                pnl = entry - stop - COST
                break
        if pnl is None:
            pnl = side * (live.iloc[-1].close - entry) - COST
        rows.append({"day": day, "pnl": pnl, "atr": atr})
    summarize(label, pd.DataFrame(rows))

s2(0.0, "range", "S2a Asian breakout, stop=far side of range, entries 07:00-14:30, exit 20:55")
s2(0.1, "atr", "S2b Asian breakout +10% buffer, stop=0.33*ATR, entries 07:00-14:30")

# ------------------------------------------------------- S3 NY ORB
def s3(or_start, or_len, label, exit_min=20 * 60):
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        orb = seg[(seg.tod >= or_start) & (seg.tod < or_start + or_len)]
        rest = seg[(seg.tod >= or_start + or_len) & (seg.tod < exit_min)]
        if len(orb) < or_len - 2 or len(rest) < 30:
            continue
        o_hi, o_lo = orb.high.max(), orb.low.min()
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
        live = rest[rest.index >= t0]
        pnl = None
        for ts, bar in live.iterrows():
            if side == 1 and bar.low <= stop:
                pnl = stop - entry - COST
                break
            if side == -1 and bar.high >= stop:
                pnl = entry - stop - COST
                break
        if pnl is None:
            pnl = side * (live.iloc[-1].close - entry) - COST
        rows.append({"day": day, "pnl": pnl, "atr": atr})
    summarize(label, pd.DataFrame(rows))

s3(13 * 60 + 30, 30, "S3a NY ORB: 13:30 open, 30m range, breakout->20:00, stop far side")
s3(14 * 60 + 30, 30, "S3b NYSE ORB: 14:30 open, 30m range, breakout->20:00")

# ------------------------------------------------------- S4 London->NY continuation
def s4(check_min, label, exit_min=20 * 60 + 55):
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr):
            continue
        asia = seg[(seg.tod >= 22 * 60) | (seg.tod < 7 * 60)]
        if len(asia) < 60:
            continue
        a_hi, a_lo = asia.high.max(), asia.low.min()
        at_chk = seg[seg.tod >= check_min]
        if len(at_chk) == 0:
            continue
        px = at_chk.iloc[0].open
        if px > a_hi:
            side = 1
        elif px < a_lo:
            side = -1
        else:
            continue
        live = seg[(seg.tod >= check_min) & (seg.tod < exit_min)]
        if len(live) < 30:
            continue
        entry = live.iloc[0].open
        stop = (a_hi + a_lo) / 2  # range mid as invalidation
        pnl = None
        for ts, bar in live.iterrows():
            if side == 1 and bar.low <= stop:
                pnl = stop - entry - COST
                break
            if side == -1 and bar.high >= stop:
                pnl = entry - stop - COST
                break
        if pnl is None:
            pnl = side * (live.iloc[-1].close - entry) - COST
        rows.append({"day": day, "pnl": pnl, "atr": atr})
    summarize(label, pd.DataFrame(rows))

s4(12 * 60, "S4a At 12:00 beyond Asian range -> hold to 20:55, stop=range mid")

with open(os.path.join(OUT, "03_backtests.txt"), "w") as f:
    f.write("\n".join(lines))
