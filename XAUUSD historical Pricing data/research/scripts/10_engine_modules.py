"""Module research for a multi-strategy scalping engine (5m execution).

Tested candidate detectors:
  T1  Trend ignition = Donchian(24) 5m close breakout; manage with chandelier
      trail (highest close since entry - k*ATR14); flat at 20:55; variants by
      session window and trail width k.
  T2  Same but require expansion confirmation (breakout bar range > 1.5x ATR14).
  R1  Reversal module: when a T1 trend trade that gained >= 1.0 ATR14 gets
      trailed out, enter the OPPOSITE direction (the "trend has reversed" bet),
      stop beyond the trend extreme, chandelier-managed.
  R2  London RSI(2) mean reversion: RSI2 < 10 (long) / > 90 (short) during
      07:00-11:55, exit at EMA20 touch or 12:00, stop 1*ATR14.
Costs $0.40/oz RT. R measured on initial stop distance.
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

df = m5.copy()
df["tod"] = df.index.hour * 60 + df.index.minute
df["day"] = (df.index - pd.Timedelta(hours=22)).date
tr = np.maximum(df.high - df.low,
                np.maximum((df.high - df.close.shift()).abs(), (df.low - df.close.shift()).abs()))
df["atr"] = tr.ewm(alpha=1 / 14).mean()
df["dhi"] = df.high.rolling(24).max().shift(1)
df["dlo"] = df.low.rolling(24).min().shift(1)
df["ema20"] = df.close.ewm(span=20).mean()
delta = df.close.diff()
up = delta.clip(lower=0).ewm(alpha=1 / 2).mean()
dn = (-delta.clip(upper=0)).ewm(alpha=1 / 2).mean()
df["rsi2"] = 100 - 100 / (1 + up / dn)

tod = df.tod.to_numpy()
day = df.day.to_numpy()
o = df.open.to_numpy(); h = df.high.to_numpy(); l = df.low.to_numpy(); c = df.close.to_numpy()
atr = df.atr.to_numpy(); dhi = df.dhi.to_numpy(); dlo = df.dlo.to_numpy()
ema = df.ema20.to_numpy(); rsi = df.rsi2.to_numpy()
ts = df.index
N = len(df)
FLAT = 20 * 60 + 55

def stats(rows, label, yearly=True):
    t = pd.DataFrame(rows)
    if len(t) == 0:
        emit(f"{label}: no trades")
        return t
    t["R"] = t.pnl / t.risk
    t["year"] = pd.to_datetime(t.day.astype(str)).dt.year
    eq = t.R.cumsum(); dd = (eq - eq.cummax()).min()
    hold = t.bars.mean() * 5 if "bars" in t else np.nan
    emit(f"\n--- {label} ---")
    emit(f"n={len(t)} win%={(t.R>0).mean()*100:.1f} avgR={t.R.mean():+.3f} "
         f"avgWin={t[t.R>0].R.mean():+.2f} avgLoss={t[t.R<=0].R.mean():+.2f} "
         f"totR={t.R.sum():+.1f} maxDD={dd:.1f}R avgHold={hold:.0f}min")
    if yearly:
        emit(t.groupby("year").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                                   totR=("R", "sum"), avgR=("R", "mean")).round(2).to_string())
    return t

def run_trend(k_trail, sess, confirm_exp, label, collect_reversals=False):
    """sess = (start_min, end_min) entry window; exit forced at FLAT of each day."""
    rows, revs = [], []
    pos = 0
    for i in range(30, N):
        if pos != 0:
            # day rollover or flat time -> force exit at close of prev bar handled below
            if day[i] != day[i - 1] or tod[i] >= FLAT:
                pnl = pos * (c[i - 1] - entry) - COST
                rows.append(dict(day=day[i - 1], pnl=pnl, risk=risk0, bars=i - 1 - i0))
                pos = 0
                continue
            # update trail
            if pos == 1:
                peak = max(peak, c[i - 1])
                trail = peak - k_trail * atr[i - 1]
                if l[i] <= trail:
                    px = min(o[i], trail)
                    pnl = px - entry - COST
                    rows.append(dict(day=day[i], pnl=pnl, risk=risk0, bars=i - i0))
                    if collect_reversals and (peak - entry) >= 1.0 * atr[i]:
                        revs.append(dict(i=i, side=-1, extreme=peak))
                    pos = 0
            else:
                peak = min(peak, c[i - 1])
                trail = peak + k_trail * atr[i - 1]
                if h[i] >= trail:
                    px = max(o[i], trail)
                    pnl = entry - px - COST
                    rows.append(dict(day=day[i], pnl=pnl, risk=risk0, bars=i - i0))
                    if collect_reversals and (entry - peak) >= 1.0 * atr[i]:
                        revs.append(dict(i=i, side=1, extreme=peak))
                    pos = 0
        if pos == 0:
            if not (sess[0] <= tod[i] < sess[1]):
                continue
            if np.isnan(dhi[i]) or np.isnan(atr[i]) or atr[i] <= 0:
                continue
            long_sig = c[i] > dhi[i]
            short_sig = c[i] < dlo[i]
            if confirm_exp and (h[i] - l[i]) < 1.5 * atr[i]:
                long_sig = short_sig = False
            if long_sig or short_sig:
                pos = 1 if long_sig else -1
                entry = c[i]
                peak = c[i]
                risk0 = k_trail * atr[i]
                i0 = i
    t = stats(rows, label)
    return t, revs

emit("=== T1: Donchian(24) breakout + chandelier trail ===")
run_trend(2.5, (0, 24 * 60), False, "T1a all-day, trail 2.5*ATR")
run_trend(2.5, (12 * 60, 19 * 60), False, "T1b NY-only entries 12:00-19:00, trail 2.5*ATR")
run_trend(1.5, (12 * 60, 19 * 60), False, "T1c NY-only, tight trail 1.5*ATR")
t1d, revs = run_trend(3.0, (12 * 60, 19 * 60), False, "T1d NY-only, wide trail 3.0*ATR", collect_reversals=True)
run_trend(2.5, (12 * 60, 19 * 60), True, "T2 NY-only + expansion-bar confirmation")

# ---- R1: reversal after a profitable trend gets trailed out ----
emit("\n=== R1: enter OPPOSITE after a >=1-ATR trend is trailed out (from T1d events) ===")
rows = []
for ev in revs:
    i0, side, extreme = ev["i"], ev["side"], ev["extreme"]
    if i0 + 2 >= N:
        continue
    entry = c[i0]
    stop = extreme  # beyond the trend's peak/trough
    risk = abs(entry - stop)
    if risk <= 0 or risk > 3 * atr[i0]:
        continue
    pnl = None
    peak = entry
    for i in range(i0 + 1, min(i0 + 96, N)):
        if day[i] != day[i0] or tod[i] >= FLAT:
            pnl = side * (c[i - 1] - entry) - COST
            break
        if side == 1:
            if l[i] <= stop:
                pnl = stop - entry - COST
                break
            peak = max(peak, c[i])
            tr_ = peak - 2.5 * atr[i]
            if tr_ > stop and l[i] <= tr_:
                pnl = tr_ - entry - COST
                break
        else:
            if h[i] >= stop:
                pnl = entry - stop - COST
                break
            peak = min(peak, c[i])
            tr_ = peak + 2.5 * atr[i]
            if tr_ < stop and h[i] >= tr_:
                pnl = entry - tr_ - COST
                break
    if pnl is None:
        pnl = side * (c[min(i0 + 95, N - 1)] - entry) - COST
    rows.append(dict(day=day[i0], pnl=pnl, risk=risk))
stats(rows, "R1 reversal-after-trend")

# ---- R2: London RSI2 mean reversion ----
emit("\n=== R2: London RSI(2) extremes, exit EMA20/12:00, stop 1*ATR ===")
rows = []
i = 30
while i < N:
    if 7 * 60 <= tod[i] < 11 * 60 + 55 and not np.isnan(rsi[i]) and atr[i] > 0:
        side = 1 if rsi[i] < 10 else (-1 if rsi[i] > 90 else 0)
        if side:
            entry = c[i]
            stop = entry - side * 1.0 * atr[i]
            risk = 1.0 * atr[i]
            pnl = None
            for j in range(i + 1, N):
                if day[j] != day[i] or tod[j] >= 12 * 60:
                    pnl = side * (c[j - 1] - entry) - COST
                    j_end = j
                    break
                if side == 1 and l[j] <= stop:
                    pnl = stop - entry - COST; j_end = j; break
                if side == -1 and h[j] >= stop:
                    pnl = entry - stop - COST; j_end = j; break
                if (side == 1 and h[j] >= ema[j]) or (side == -1 and l[j] <= ema[j]):
                    pnl = side * (c[j] - entry) - COST; j_end = j; break
            if pnl is not None:
                rows.append(dict(day=day[i], pnl=pnl, risk=risk))
                i = j_end + 1
                continue
    i += 1
stats(rows, "R2 London RSI2 fade")

with open(os.path.join(OUT, "10_engine_modules.txt"), "w") as f:
    f.write("\n".join(lines))
