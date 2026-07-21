"""Fix + deep-dive of the overnight effect, working purely in chronological time.

Decompose the 24h drift into segments:
  A 20:00 -> 20:59 close   (last hour of NY)
  B 20:59 close -> 22:00 reopen (the maintenance-break gap)
  C 22:00 -> 02:00         (Asia early)
  D 02:00 -> 07:00         (Asia late)
  E 07:00 -> 12:00         (London)
  F 12:00 -> 20:00         (NY)
Then proper backtests:
  S1-fix long 20:00 -> next day 02:00 (holds the gap)   [skip-Friday variant]
  S4-fix at 12:00 beyond Asian range -> 20:55, stop=range mid
Also: weekend gap fill stats.
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

# ---- build a per-calendar-date table of marker prices ----
px = m1[["open", "close"]].copy()
px["date"] = px.index.date
px["tod"] = px.index.hour * 60 + px.index.minute

def first_open_at_or_after(minute):
    sel = px[px.tod >= minute].groupby("date")["open"].first()
    return sel

def last_close_before(minute):
    sel = px[px.tod < minute].groupby("date")["close"].last()
    return sel

p20 = first_open_at_or_after(20 * 60)
p_close = last_close_before(21 * 60 + 5)          # ~20:59 close
p22 = px[px.tod >= 22 * 60].groupby("date")["open"].first()  # 22:00 reopen same calendar date
p02 = first_open_at_or_after(2 * 60)
p07 = first_open_at_or_after(7 * 60)
p12 = first_open_at_or_after(12 * 60)

cal = pd.DataFrame({"p20": p20, "pclose": p_close, "p22": p22, "p02": p02, "p07": p07, "p12": p12})
cal.index = pd.to_datetime(cal.index)
cal["atr"] = pd.Series(cal.index.date, index=cal.index).map(atr_map)
cal["next_p02"] = cal.p02.shift(-1)
cal["next_p07"] = cal.p07.shift(-1)
cal["next_date"] = pd.Series(cal.index, index=cal.index).shift(-1)
cal["gap_days"] = (cal.next_date - cal.index).dt.days

emit("=== 24h DRIFT DECOMPOSITION (mean segment move as % of ATR20, with t) ===")
segs = {
    "A 20:00->close": (cal.pclose - cal.p20),
    "B close->22:00 reopen": (cal.p22 - cal.pclose),
    "C 22:00->02:00(nxt)": (cal.next_p02 - cal.p22),
    "D 02:00->07:00": (cal.p07 - cal.p02),
    "E 07:00->12:00": (cal.p12 - cal.p07),
    "F 12:00->20:00": (cal.p20 - cal.p12),
}
for name, s in segs.items():
    x = (s / cal.atr).dropna()
    x = x[np.abs(x) < 5]
    t = x.mean() / (x.std() / np.sqrt(len(x)))
    emit(f"  {name:<24} mean={x.mean()*100:+6.2f}% ATR  t={t:+5.2f}  N={len(x)}")

emit("\nsegment B (maintenance-break gap) by year:")
b = ((cal.p22 - cal.pclose) / cal.atr).dropna()
for y in range(2021, 2027):
    x = b[b.index.year == y]
    if len(x) == 0:
        continue
    t = x.mean() / (x.std() / np.sqrt(len(x)))
    emit(f"  {y}: mean={x.mean()*100:+6.2f}% ATR  t={t:+5.2f}  N={len(x)}  P(gap up)={(x>0).mean()*100:.0f}%")

emit("\nsegment C (22:00->02:00) by year:")
c = ((cal.next_p02 - cal.p22) / cal.atr).dropna()
c = c[c.index.to_series().dt.dayofweek < 5]
for y in range(2021, 2027):
    x = c[c.index.year == y]
    if len(x) == 0:
        continue
    t = x.mean() / (x.std() / np.sqrt(len(x)))
    emit(f"  {y}: mean={x.mean()*100:+6.2f}% ATR  t={t:+5.2f}  N={len(x)}")

# ---- proper S1: long 20:00 -> next calendar day's 02:00, weekdays ----
def run_s1(hold_gap: bool, label: str):
    rows = []
    for dt_, row in cal.iterrows():
        if pd.isna(row.atr):
            continue
        if dt_.dayofweek == 4 or dt_.dayofweek >= 5:  # skip Friday & weekend entries
            continue
        entry = row.p20 if hold_gap else row.p22
        exitp = row.next_p02
        if pd.isna(entry) or pd.isna(exitp) or row.gap_days != 1:
            continue
        rows.append({"day": dt_.date(), "pnl": exitp - entry - COST, "atr": row.atr})
    t = pd.DataFrame(rows).dropna()
    t["year"] = pd.to_datetime(t.day.astype(str)).dt.year
    t["R"] = t.pnl / t.atr
    sharpe = t.R.mean() / t.R.std() * np.sqrt(252)
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    emit(f"\n--- {label} ---")
    emit(f"trades={len(t)}  win%={(t.pnl>0).mean()*100:.1f}  avg $/oz={t.pnl.mean():+.2f}  "
         f"expectancy={t.R.mean()*100:+.2f}% ATR  Sharpe~{sharpe:.2f}  maxDD={dd:.1f}R")
    emit(t.groupby("year").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                               total=("pnl", "sum"), avg_R=("R", "mean")).round(2).to_string())

run_s1(True, "S1-fix long 20:00 -> next-day 02:00 (holds break gap), Mon-Thu entries")
run_s1(False, "S1-alt long 22:00 reopen -> next-day 02:00, Mon-Thu entries")

# ---- proper S4: London->NY continuation ----
g = m1.copy()
g["day"] = (g.index - pd.Timedelta(hours=22)).date
g["tod"] = g.index.hour * 60 + g.index.minute
rows = []
for day, seg in g.groupby("day"):
    atr = atr_map.get(day)
    if pd.isna(atr):
        continue
    asia = seg[(seg.tod >= 22 * 60) | (seg.tod < 7 * 60)]
    day_sess = seg[(seg.tod >= 7 * 60) & (seg.tod < 21 * 60)]  # tod window excludes 22:00 block
    if len(asia) < 60 or len(day_sess) < 120:
        continue
    a_hi, a_lo = asia.high.max(), asia.low.min()
    chk = day_sess[day_sess.tod >= 12 * 60]
    if len(chk) == 0:
        continue
    px0 = chk.iloc[0].open
    side = 1 if px0 > a_hi else (-1 if px0 < a_lo else 0)
    if side == 0:
        continue
    live = day_sess[(day_sess.tod >= 12 * 60) & (day_sess.tod < 20 * 60 + 55)]
    entry = live.iloc[0].open
    stop = (a_hi + a_lo) / 2
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
    rows.append({"day": day, "pnl": pnl, "atr": atr, "side": side})
t = pd.DataFrame(rows).dropna()
t["year"] = pd.to_datetime(t.day.astype(str)).dt.year
t["R"] = t.pnl / t.atr
sharpe = t.R.mean() / t.R.std() * np.sqrt(252 * len(t) / 1290)
eq = t.R.cumsum()
dd = (eq - eq.cummax()).min()
emit(f"\n--- S4-fix London->NY continuation (12:00 beyond Asian range -> 20:55, stop=mid) ---")
emit(f"trades={len(t)}  win%={(t.pnl>0).mean()*100:.1f}  avg $/oz={t.pnl.mean():+.2f}  "
     f"expectancy={t.R.mean()*100:+.2f}% ATR  Sharpe~{sharpe:.2f}  maxDD={dd:.1f}R  "
     f"longs={len(t[t.side==1])} shorts={len(t[t.side==-1])}")
emit(t.groupby("year").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                           total=("pnl", "sum"), avg_R=("R", "mean")).round(2).to_string())
emit("by side:")
emit(t.groupby("side").agg(n=("pnl", "size"), win=("pnl", lambda x: (x > 0).mean() * 100),
                           avg_R=("R", "mean")).round(3).to_string())

# ---- weekend gaps ----
fri_close = cal.pclose[cal.index.dayofweek == 4].dropna()
sun_open = cal.p22[cal.index.dayofweek == 6].dropna()
wk = pd.DataFrame({"fri": fri_close})
wk["sun"] = pd.Series(sun_open.values, index=sun_open.index - pd.Timedelta(days=2)).reindex(wk.index)
wk["atr"] = pd.Series(wk.index.date, index=wk.index).map(atr_map)
wk = wk.dropna()
wk["gap"] = wk.sun - wk.fri
wk["ngap"] = wk.gap / wk.atr
emit(f"\n=== WEEKEND GAPS (Fri 20:59 close -> Sun 22:00 open), N={len(wk)} ===")
emit(f"mean gap={wk.gap.mean():+.2f} $/oz ({wk.ngap.mean()*100:+.1f}% ATR)  P(gap up)={(wk.gap>0).mean()*100:.0f}%  "
     f"mean |gap|={wk.gap.abs().mean():.2f} $/oz")
# gap fill: does Sunday/Monday trade back to Friday close within 24h of reopen?
fill = []
for dt_, row in wk.iterrows():
    start = dt_ + pd.Timedelta(days=2, hours=22)
    seg = m1[(m1.index >= start) & (m1.index < start + pd.Timedelta(hours=24))]
    if len(seg) == 0:
        continue
    if row.gap > 0:
        fill.append((seg.low <= row.fri).any())
    elif row.gap < 0:
        fill.append((seg.high >= row.fri).any())
big = wk[wk.gap.abs() > 0.15 * wk.atr]
fill_big = []
for dt_, row in big.iterrows():
    start = dt_ + pd.Timedelta(days=2, hours=22)
    seg = m1[(m1.index >= start) & (m1.index < start + pd.Timedelta(hours=24))]
    if len(seg) == 0:
        continue
    if row.gap > 0:
        fill_big.append((seg.low <= row.fri).any())
    else:
        fill_big.append((seg.high >= row.fri).any())
emit(f"P(gap fills within 24h) all gaps: {np.mean(fill)*100:.0f}%   large gaps (>15% ATR, N={len(big)}): {np.mean(fill_big)*100:.0f}%")

with open(os.path.join(OUT, "04_overnight_decomp.txt"), "w") as f:
    f.write("\n".join(lines))
