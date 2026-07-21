"""Intraday structure: volatility/volume by hour-of-day and day-of-week,
daily high/low formation timing, and session range statistics.

All times UTC. Sessions (approximate, DST smears +/-1h):
  Asia    22:00-06:59   London  07:00-11:59   NY  12:00-20:59
Key single events: London open ~07-08, COMEX open 13:30, London PM fix 15:00,
NY equity open 14:30, COMEX settle 18:30, close 21:00-22:00.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from importlib import import_module
prep = import_module("00_prep")

OUT = os.path.join(os.path.dirname(__file__), "..", "output")
CH = os.path.join(os.path.dirname(__file__), "..", "charts")

m1, m5, m15, h1, d1 = prep.load_all()

# ---- normalise ranges by daily ATR so 2021 and 2026 are comparable ----
d1 = d1.copy()
d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
day_key = (m1.index - pd.Timedelta(hours=22)).date  # dealing-day key on m1
atr_map = pd.Series(d1["atr20"].values, index=(d1.index - pd.Timedelta(hours=22)).date)

h1x = h1.copy()
h1x["hour"] = h1x.index.hour
h1x["dow"] = h1x.index.dayofweek
h1x["range"] = h1x.high - h1x.low
h1x["day"] = (h1x.index - pd.Timedelta(hours=22)).date
h1x["atr"] = h1x["day"].map(atr_map)
h1x = h1x.dropna(subset=["atr"])
h1x["nrange"] = h1x["range"] / h1x["atr"]          # hour range as fraction of daily ATR
h1x["ret"] = np.log(h1x.close / h1x.open)
h1x["nret"] = (h1x.close - h1x.open) / h1x.atr      # signed drift as fraction of ATR

lines = []
def emit(s=""):
    print(s)
    lines.append(s)

emit("=== HOURLY PROFILE (all years, range normalised by prior 20-day ATR) ===")
hp = h1x.groupby("hour").agg(nrange=("nrange", "mean"), nret_mean=("nret", "mean"),
                             nret_t=("nret", lambda x: x.mean() / (x.std() / np.sqrt(len(x)))),
                             vol_share=("volume", "sum"))
hp["vol_share"] = hp["vol_share"] / hp["vol_share"].sum() * 100
emit(hp.round(4).to_string())

emit("\n=== HOURLY DRIFT BY REGIME (mean close-open as % of ATR, t-stat) ===")
for label, seg in [("2021-2023", h1x[h1x.index.year <= 2023]), ("2024-2026", h1x[h1x.index.year >= 2024])]:
    g = seg.groupby("hour")["nret"]
    t = g.apply(lambda x: x.mean() / (x.std() / np.sqrt(len(x))))
    emit(f"-- {label} --")
    emit(pd.DataFrame({"mean_pct_atr": (g.mean() * 100).round(2), "t": t.round(2)}).T.to_string())

emit("\n=== DAY OF WEEK (daily bars) ===")
d1x = d1.dropna(subset=["atr20"]).copy()
d1x["dow"] = d1x.index.dayofweek  # note: dealing day labelled by close-side date
d1x["nret"] = (d1x.close - d1x.open) / d1x.atr20
d1x["nrange"] = d1x["range"] / d1x.atr20
dw = d1x.groupby("dow").agg(days=("nret", "size"), nrange=("nrange", "mean"),
                            nret_mean=("nret", "mean"),
                            up_pct=("nret", lambda x: (x > 0).mean() * 100))
dw.index = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][: len(dw)]
emit(dw.round(3).to_string())

# ---- timing of the daily high / low ----
emit("\n=== WHEN DOES THE DAY'S HIGH/LOW FORM? (dealing day 22:00->21:59 UTC) ===")
g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
hi_t = g.groupby("day")["high"].idxmax()
lo_t = g.groupby("day")["low"].idxmin()
hi_h = pd.Series(hi_t).dt.hour.value_counts(normalize=True).sort_index() * 100
lo_h = pd.Series(lo_t).dt.hour.value_counts(normalize=True).sort_index() * 100
tt = pd.DataFrame({"high_%": hi_h.round(2), "low_%": lo_h.round(2)}).fillna(0)
emit(tt.to_string())
ext_h = pd.concat([pd.Series(hi_t), pd.Series(lo_t)]).dt.hour.value_counts(normalize=True).sort_index() * 100
emit(f"\nP(extreme of day forms 12:00-16:59 UTC NY window): {ext_h.loc[12:16].sum():.1f}%")
emit(f"P(extreme of day forms 22:00-06:59 UTC Asia):        {ext_h.loc[22:23].sum() + ext_h.loc[0:6].sum():.1f}%")
emit(f"P(extreme of day forms 07:00-11:59 UTC London):      {ext_h.loc[7:11].sum():.1f}%")

# ---- session ranges as share of day ----
emit("\n=== SESSION SHARE OF DAILY RANGE (mean of session_range/day_range) ===")
def sess(df, h0, h1_):
    hrs = df.index.hour
    if h0 < h1_:
        return df[(hrs >= h0) & (hrs < h1_)]
    return df[(hrs >= h0) | (hrs < h1_)]

rows = []
for name, (a, b) in {"Asia 22-07": (22, 7), "London 07-12": (7, 12), "NY 12-21": (12, 21)}.items():
    s = sess(g, a, b).groupby("day").agg(hi=("high", "max"), lo=("low", "min"))
    day_rng = g.groupby("day").agg(hi=("high", "max"), lo=("low", "min"))
    share = ((s.hi - s.lo) / (day_rng.hi - day_rng.lo)).dropna()
    rows.append({"session": name, "mean_share_%": share.mean() * 100, "median_share_%": share.median() * 100})
emit(pd.DataFrame(rows).round(1).to_string(index=False))

with open(os.path.join(OUT, "01_intraday_structure.txt"), "w") as f:
    f.write("\n".join(lines))

# ---- charts ----
fig, ax = plt.subplots(1, 2, figsize=(13, 4.5))
hp["nrange"].plot(kind="bar", ax=ax[0], color="#4477aa")
ax[0].set_title("Avg hourly range (fraction of daily ATR20)")
ax[0].set_xlabel("UTC hour")
tt.plot(kind="bar", ax=ax[1], color=["#228833", "#cc3311"])
ax[1].set_title("Hour the daily HIGH / LOW forms (%)")
ax[1].set_xlabel("UTC hour")
fig.tight_layout()
fig.savefig(os.path.join(CH, "intraday_profile.png"), dpi=120)
print("\nsaved charts/intraday_profile.png")
