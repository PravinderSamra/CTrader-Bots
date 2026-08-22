"""Mathematician/physicist diagnostics of the XAUUSD price process.

 1. Variance ratios VR(q) on 5m returns (random-walk test across scales) + by session/year
 2. Hurst exponent via aggregated-variance scaling
 3. Volatility clustering: ACF of |returns| and of daily range; next-day range predictability
 4. Jump dynamics: 4-sigma 1m jumps, timing, post-jump drift
 5. Ornstein-Uhlenbeck fit in Asia (mean reversion half-life vs session VWAP)
 6. Tail exponent (Hill) of 5m returns
 7. Runs analysis: P(next bar same sign | k-bar streak), 15m and 1h
 8. Trend-day anatomy: close location in range; conditional range extension
 9. Compression->expansion: narrow-range days and next-day range
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

r5 = np.log(m5.close).diff().dropna()
r1 = np.log(m1.close).diff().dropna()

# ------------------------------------------------ 1. variance ratios
emit("=== 1. VARIANCE RATIOS VR(q) on 5m log returns (VR>1 trending, <1 mean-reverting) ===")
def vr(x, q):
    x = x.dropna()
    v1 = x.var()
    vq = x.rolling(q).sum().dropna()[::q].var()
    return vq / (q * v1)
for q in (2, 4, 8, 16, 32, 64, 128):
    emit(f"  q={q:>3} ({q*5:>4}min): VR={vr(r5,q):.3f}")
emit("\nby session (q=8 -> 40min):")
hrs = r5.index.hour
for name, mask in {"Asia 22-07": (hrs >= 22) | (hrs < 7), "London 07-12": (hrs >= 7) & (hrs < 12),
                   "NY 12-21": (hrs >= 12) & (hrs < 21)}.items():
    emit(f"  {name:<13} VR(8)={vr(r5[mask],8):.3f}  VR(32)={vr(r5[mask],32):.3f}")
emit("by year (q=8):")
for y in range(2021, 2027):
    emit(f"  {y}: VR(8)={vr(r5[r5.index.year==y],8):.3f}  VR(64)={vr(r5[r5.index.year==y],64):.3f}")

# ------------------------------------------------ 2. Hurst
emit("\n=== 2. HURST EXPONENT (aggregated variance method, 5m base) ===")
qs = np.array([1, 2, 4, 8, 16, 32, 64, 128])
vs = [r5.rolling(q).sum().dropna()[::q].std() for q in qs]
slope = np.polyfit(np.log(qs), np.log(vs), 1)[0]
emit(f"  H = {slope:.3f}  (0.5 = random walk)")
for y in (2022, 2024, 2026):
    seg = r5[r5.index.year == y]
    vs = [seg.rolling(q).sum().dropna()[::q].std() for q in qs]
    emit(f"  {y}: H = {np.polyfit(np.log(qs), np.log(vs), 1)[0]:.3f}")

# ------------------------------------------------ 3. vol clustering
emit("\n=== 3. VOLATILITY CLUSTERING ===")
a5 = r5.abs()
emit(f"ACF of |5m ret|: lag1={a5.autocorr(1):.3f} lag12(1h)={a5.autocorr(12):.3f} lag288(1d)={a5.autocorr(288):.3f}")
d1x = d1.copy()
d1x["range"] = d1x.high - d1x.low
rng = d1x["range"]
emit(f"ACF of daily range: lag1={rng.autocorr(1):.3f} lag5={rng.autocorr(5):.3f} lag20={rng.autocorr(20):.3f}")
# next-day range predictability
X = pd.DataFrame({"atr5": rng.rolling(5).mean().shift(1), "atr20": rng.rolling(20).mean().shift(1)}).dropna()
y_ = rng.reindex(X.index)
X_ = np.column_stack([np.ones(len(X)), X.atr5, X.atr20])
beta, *_ = np.linalg.lstsq(X_, y_, rcond=None)
pred = X_ @ beta
ss_res = ((y_ - pred) ** 2).sum(); ss_tot = ((y_ - y_.mean()) ** 2).sum()
emit(f"next-day range ~ ATR5+ATR20: R^2 = {1-ss_res/ss_tot:.3f}   (direction R^2 for comparison: ~0.00)")

# ------------------------------------------------ 4. jumps
emit("\n=== 4. JUMP DYNAMICS (1m |ret| > 4*rolling-1d sigma) ===")
sig1 = r1.rolling(1440).std()
jumps = r1[np.abs(r1) > 4 * sig1].dropna()
emit(f"N jumps={len(jumps):,} ({len(jumps)/len(r1)*100:.2f}% of bars; Gaussian would be 0.006%)")
jh = jumps.index.hour.value_counts(normalize=True).sort_index() * 100
top = jh.sort_values(ascending=False).head(5)
emit("jump timing (top hours UTC): " + ", ".join(f"{h}:00={v:.1f}%" for h, v in top.items()))
# post-jump drift
c1 = np.log(m1.close)
for horizon in (5, 15, 30, 60):
    fwd = c1.diff(horizon).shift(-horizon).reindex(jumps.index)
    aligned = (fwd * np.sign(jumps)).dropna()
    tstat = aligned.mean() / (aligned.std() / np.sqrt(len(aligned)))
    emit(f"  post-jump {horizon:>2}m drift (jump dir): {aligned.mean()*1e4:+.2f}bp  t={tstat:+.2f}  cont.rate={(aligned>0).mean()*100:.1f}%")
# clustering of jumps
jt = jumps.index.to_series().diff().dt.total_seconds().div(60)
emit(f"P(next jump within 60min of a jump) = {(jt<=60).mean()*100:.1f}% (uniform would be ~{len(jumps)/len(r1)*60*100:.1f}%)")

# ------------------------------------------------ 5. OU in Asia
emit("\n=== 5. ORNSTEIN-UHLENBECK FIT, ASIA SESSION (5m, vs session cum-VWAP) ===")
m5x = m5.copy()
m5x["day"] = (m5x.index - pd.Timedelta(hours=22)).date
m5x["tp"] = (m5x.high + m5x.low + m5x.close) / 3
asia = m5x[(m5x.index.hour >= 22) | (m5x.index.hour < 7)].copy()
asia["cumpv"] = (asia.tp * asia.volume).groupby(asia.day).cumsum()
asia["cumv"] = asia.volume.groupby(asia.day).cumsum()
asia["vwap"] = asia.cumpv / asia.cumv
asia["dev"] = asia.close - asia.vwap
asia["ddev"] = asia.groupby("day")["dev"].diff().shift(-1)
ok = asia.dropna(subset=["dev", "ddev"])
b = np.polyfit(ok.dev, ok.ddev, 1)[0]
half_life = -np.log(2) / np.log(1 + b) if b > -1 else np.inf
emit(f"  ddev = {b:+.4f} * dev  ->  mean-reversion half-life ~ {half_life*5:.0f} minutes")
# is it tradeable? deviation threshold response
for k in (1.0, 1.5, 2.0):
    sd = ok.groupby("day")["dev"].transform(lambda x: x.expanding().std())
    sel = ok[np.abs(ok.dev) > k * sd].dropna(subset=["ddev"])
    rev = (-np.sign(sel.dev) * sel.ddev)
    emit(f"  |dev|>{k}sd: N={len(sel):,}  next-5m move toward VWAP: {rev.mean()*100:.2f} cents avg")

# ------------------------------------------------ 6. tails
emit("\n=== 6. TAIL EXPONENT (Hill, 5m returns, top 1%) ===")
for name, x in [("right", r5[r5 > 0]), ("left", -r5[r5 < 0])]:
    xs = np.sort(x.values)[::-1]
    k = int(len(xs) * 0.01)
    hill = 1 / np.mean(np.log(xs[:k] / xs[k]))
    emit(f"  {name} tail alpha = {hill:.2f}  (<3 = infinite skew/kurt territory; equities ~3)")

# ------------------------------------------------ 7. runs
emit("\n=== 7. RUNS: P(next same sign | k consecutive same-sign bars) ===")
for name, df in [("15m", m15), ("1h", h1)]:
    s = np.sign(df.close.diff()).dropna()
    for k in (2, 3, 4, 5):
        run_mask = pd.Series(True, index=s.index)
        for i in range(k):
            run_mask &= (s.shift(i) == s.shift(k - 1)).fillna(False) if False else (s.shift(i) == s).fillna(False)
        # simpler: rolling window all equal
        eq_run = s.rolling(k).apply(lambda w: float(len(set(w)) == 1), raw=False).fillna(0).astype(bool)
        nxt = (s.shift(-1) == s)[eq_run]
        emit(f"  {name} k={k}: P(cont)={nxt.mean()*100:.1f}%  N={eq_run.sum():,}")

# ------------------------------------------------ 8. trend-day anatomy
emit("\n=== 8. TREND-DAY ANATOMY (daily bars, dealing day) ===")
d1x["clv"] = (d1x.close - d1x.low) / d1x["range"]  # close location 0..1
emit(f"close in top/bottom 10% of range: {((d1x.clv>0.9)|(d1x.clv<0.1)).mean()*100:.1f}% of days (uniform: 20%)")
emit(f"close in top/bottom 25%: {((d1x.clv>0.75)|(d1x.clv<0.25)).mean()*100:.1f}% (uniform: 50%)")
# conditional extension: range used by 15:00 vs final range
g1 = m1.copy()
g1["day"] = (g1.index - pd.Timedelta(hours=22)).date
g1["tod"] = g1.index.hour * 60 + g1.index.minute
atr_map = pd.Series(d1x["range"].rolling(20).mean().shift(1).values, index=(d1x.index - pd.Timedelta(hours=22)).date)
rows = []
for day, seg in g1.groupby("day"):
    atr = atr_map.get(day)
    if pd.isna(atr):
        continue
    upto = seg[seg.tod < 15 * 60]
    upto = upto[~((upto.tod >= 21 * 60) & (upto.tod < 22 * 60))]
    if len(upto) < 300:
        continue
    r_sofar = (upto.high.max() - upto.low.min()) / atr
    r_final = (seg.high.max() - seg.low.min()) / atr
    rows.append({"sofar": r_sofar, "final": r_final, "ext": r_final - r_sofar})
ext = pd.DataFrame(rows)
ext["bucket"] = pd.cut(ext.sofar, [0, 0.5, 0.75, 1.0, 1.5, 10])
emit("\nrange used by 15:00 (xATR) -> additional range added after 15:00 (xATR):")
emit(ext.groupby("bucket", observed=True).agg(days=("ext", "size"), mean_ext=("ext", "mean"),
                                              med_ext=("ext", "median")).round(2).to_string())

# ------------------------------------------------ 9. compression -> expansion
emit("\n=== 9. COMPRESSION -> EXPANSION ===")
d1x["nr4"] = d1x["range"] < d1x["range"].rolling(4).min().shift(1) * 1.0001
d1x["r_atr"] = d1x["range"] / d1x["range"].rolling(20).mean().shift(1)
d1x["next_r_atr"] = d1x.r_atr.shift(-1)
lowv = d1x[d1x.r_atr < 0.6]
hiv = d1x[d1x.r_atr > 1.4]
emit(f"after a <0.6xATR day (N={len(lowv)}): next-day range = {lowv.next_r_atr.mean():.2f}xATR")
emit(f"after a >1.4xATR day (N={len(hiv)}): next-day range = {hiv.next_r_atr.mean():.2f}xATR")
emit(f"after NR4 day (N={d1x.nr4.sum()}): next-day range = {d1x[d1x.nr4].next_r_atr.mean():.2f}xATR vs all-day avg {d1x.next_r_atr.mean():.2f}xATR")
# does compression predict ORB quality? (tie-in for strategies)
emit(f"corr(today r_atr, next r_atr) = {d1x.r_atr.corr(d1x.next_r_atr):.3f}")

with open(os.path.join(OUT, "08_math_physics.txt"), "w") as f:
    f.write("\n".join(lines))
