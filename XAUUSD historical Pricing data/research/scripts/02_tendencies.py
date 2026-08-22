"""Statistical tendencies:
  A) momentum vs mean-reversion by timeframe and by session (return autocorr)
  B) Asian-range interaction with London/NY: breakout follow-through vs sweep-reversal
  C) prior-day high/low touch + reaction stats
  D) round-number ($50/$100) behaviour
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

# ---------------------------------------------------------------- A: autocorr
emit("=== A) RETURN AUTOCORRELATION (lag-1, log returns) ===")
for name, df in [("1m", m1), ("5m", m5), ("15m", m15), ("1h", h1)]:
    r = np.log(df.close).diff().dropna()
    emit(f"{name:>3}: ac1 = {r.autocorr(1):+.4f}   (N={len(r):,})")

emit("\n5m lag-1 autocorr by session:")
r5 = np.log(m5.close).diff().dropna()
hrs = r5.index.hour
for name, mask in {
    "Asia 22-07": (hrs >= 22) | (hrs < 7),
    "London 07-12": (hrs >= 7) & (hrs < 12),
    "NY 12-21": (hrs >= 12) & (hrs < 21),
}.items():
    seg = r5[mask]
    emit(f"  {name:<13} ac1 = {seg.autocorr(1):+.4f}")

emit("\n5m autocorr by year (regime stability):")
for y in range(2021, 2027):
    seg = r5[r5.index.year == y]
    emit(f"  {y}: ac1 = {seg.autocorr(1):+.4f}")

# big-move continuation: after a 5m bar > k*sigma, what does the next 30m do?
emit("\nAfter a large 5m bar (|ret| > 3*rolling sigma), next-30m in same direction:")
sig = r5.rolling(288).std()
big = r5[np.abs(r5) > 3 * sig]
fwd = np.log(m5.close).diff(6).shift(-6)  # next 30 minutes
al = fwd.reindex(big.index)
same = (np.sign(al) == np.sign(big))
cont = same.mean()
mfwd = (al * np.sign(big)).mean()
emit(f"  N={len(big):,}  continuation rate={cont*100:.1f}%  mean aligned fwd ret={mfwd*1e4:+.2f} bp")

# ---------------------------------------------------------------- B: asian range
emit("\n=== B) ASIAN RANGE (22:00-06:59 UTC) vs REST OF DAY ===")
g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
h = g.index.hour
asia = g[(h >= 22) | (h < 7)]
rest = g[(h >= 7) & (h < 21)]
ar = asia.groupby("day").agg(a_hi=("high", "max"), a_lo=("low", "min"), a_close=("close", "last"))
rd = rest.groupby("day").agg(r_hi=("high", "max"), r_lo=("low", "min"),
                             r_open=("open", "first"), r_close=("close", "last"))
j = ar.join(rd, how="inner").dropna()
j["a_rng"] = j.a_hi - j.a_lo
j["broke_hi"] = j.r_hi > j.a_hi
j["broke_lo"] = j.r_lo < j.a_lo
both = (j.broke_hi & j.broke_lo)
emit(f"days: {len(j)}")
emit(f"P(break Asian high during Lon/NY)      = {j.broke_hi.mean()*100:.1f}%")
emit(f"P(break Asian low)                     = {j.broke_lo.mean()*100:.1f}%")
emit(f"P(break BOTH sides)                    = {both.mean()*100:.1f}%")
emit(f"P(break at least one side)             = {(j.broke_hi | j.broke_lo).mean()*100:.1f}%")
one_side = j[(j.broke_hi ^ j.broke_lo)]
up = one_side[one_side.broke_hi]
dn = one_side[one_side.broke_lo]
emit(f"one-side-only days: {len(one_side)} ({len(one_side)/len(j)*100:.0f}%)  up-only {len(up)}, down-only {len(dn)}")
emit(f"  up-only days:   close beyond Asian high by day end: {(up.r_close > up.a_hi).mean()*100:.1f}%")
emit(f"  down-only days: close beyond Asian low  by day end: {(dn.r_close < dn.a_lo).mean()*100:.1f}%")

# sweep-and-reverse: first side broken in London (07-12) but day closes back inside/other side
lon = g[(h >= 7) & (h < 12)]
lo_first = {}
for day, seg in lon.groupby("day"):
    a = ar.a_hi.get(day), ar.a_lo.get(day)
    if a[0] is None or pd.isna(a[0]):
        continue
    hi_break = seg.index[seg.high > a[0]]
    lo_break = seg.index[seg.low < a[1]]
    t_hi = hi_break[0] if len(hi_break) else pd.NaT
    t_lo = lo_break[0] if len(lo_break) else pd.NaT
    if pd.isna(t_hi) and pd.isna(t_lo):
        first = "none"
    elif pd.isna(t_lo) or (not pd.isna(t_hi) and t_hi < t_lo):
        first = "hi"
    else:
        first = "lo"
    lo_first[day] = first
j["lon_first"] = pd.Series(lo_first)
sub = j.dropna(subset=["lon_first"])
for side, beyond, other in [("hi", "a_hi", "a_lo"), ("lo", "a_lo", "a_hi")]:
    s = sub[sub.lon_first == side]
    if side == "hi":
        closed_thru = (s.r_close > s[beyond]).mean() * 100
        reversed_ = (s.r_close < s.a_lo).mean() * 100
        mid_rev = (s.r_close < (s.a_hi + s.a_lo) / 2).mean() * 100
    else:
        closed_thru = (s.r_close < s[beyond]).mean() * 100
        reversed_ = (s.r_close > s.a_hi).mean() * 100
        mid_rev = (s.r_close > (s.a_hi + s.a_lo) / 2).mean() * 100
    emit(f"London breaks Asian {side.upper()} first (N={len(s)}): "
         f"closes through {closed_thru:.1f}% | closes past range MID (reversal) {mid_rev:.1f}% | closes through OPPOSITE side {reversed_:.1f}%")
emit(f"(no London break of either side: N={(sub.lon_first=='none').sum()})")

# ---------------------------------------------------------------- C: prior day levels
emit("\n=== C) PRIOR-DAY HIGH/LOW ===")
dd = d1.copy()
dd["pdh"] = dd.high.shift(1)
dd["pdl"] = dd.low.shift(1)
dd = dd.dropna()
touch_h = (dd.high >= dd.pdh)
touch_l = (dd.low <= dd.pdl)
emit(f"P(touch PDH) = {touch_h.mean()*100:.1f}%   P(touch PDL) = {touch_l.mean()*100:.1f}%   P(touch either) = {(touch_h|touch_l).mean()*100:.1f}%   P(inside day) = {(~touch_h & ~touch_l).mean()*100:.1f}%")
emit(f"P(close above PDH | touched PDH) = {(dd.close[touch_h] > dd.pdh[touch_h]).mean()*100:.1f}%")
emit(f"P(close below PDL | touched PDL) = {(dd.close[touch_l] < dd.pdl[touch_l]).mean()*100:.1f}%")

# ---------------------------------------------------------------- D: round numbers
emit("\n=== D) ROUND NUMBERS ($100 levels) — magnet or barrier? ===")
c5 = m5.close
lvl = (c5 / 100).round() * 100
dist = (c5 - lvl).abs()
near = dist < 3
fwd30 = np.log(m5.close).diff(6).shift(-6)
away = fwd30[~near.reindex(fwd30.index).fillna(False)]
close_ = fwd30[near.reindex(fwd30.index).fillna(False)]
emit(f"time spent within $3 of a $100 level: {near.mean()*100:.1f}% (uniform would be ~6%)")
emit(f"abs 30m fwd move | near $100 lvl: {close_.abs().mean()*1e4:.2f} bp  vs elsewhere: {away.abs().mean()*1e4:.2f} bp")
r1 = np.log(m5.close).diff()
cross = (np.sign(c5 - lvl) != np.sign(c5.shift(1) - lvl)) & (c5.shift(1).notna())
post_cross = fwd30[cross.reindex(fwd30.index).fillna(False)]
dircross = np.sign((c5 - c5.shift(1)))[cross]
aligned = (post_cross * dircross.reindex(post_cross.index)).mean()
emit(f"after crossing a $100 level, mean 30m follow-through in cross direction: {aligned*1e4:+.2f} bp (N={cross.sum():,})")

with open(os.path.join(OUT, "02_tendencies.txt"), "w") as f:
    f.write("\n".join(lines))
