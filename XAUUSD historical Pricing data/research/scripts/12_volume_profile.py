"""Session volume profile research.

Profile construction: per dealing day (22:00->21:59 UTC), each 1m bar's volume is
spread uniformly across its [low, high] into price bins of width ATR20/150
(min $0.05). POC = highest-volume bin; Value Area = 70% of volume expanded
around POC (standard alternating method). Volume = tick volume (proxy for
time-at-price / TPO).

PART 1 descriptive probabilities (all levels are PRIOR day's, tested on next day):
  - open location vs prior VA; touch probabilities of POC/VAH/VAL by open location
  - magnet stats: open outside VA -> P(return to VA edge), P(reach POC)
  - the "80% rule": open outside VA + acceptance (2 consecutive 15m closes inside)
    -> P(rotation to opposite VA edge)
  - POC rotation (user example): first POC touch -> which VA edge is hit first;
    displacement-confirmation version
  - naked POC revisit rates (within 1/5/20 days)
PART 2 (script 13) turns the best numbers into costed backtests.
"""
import os
import pickle
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

# ---------------- build daily profiles (cached) ----------------
pkl = os.path.join(CACHE, "profiles.pkl")
if os.path.exists(pkl):
    profiles = pd.read_pickle(pkl)
else:
    rows = []
    for day, seg in g.groupby("day"):
        atr = atr_map.get(day)
        if pd.isna(atr) or len(seg) < 300:
            continue
        w = max(0.05, round(atr / 150, 2))
        lo_all, hi_all = seg.low.min(), seg.high.max()
        nb = int(np.ceil((hi_all - lo_all) / w)) + 1
        if nb < 5 or nb > 20000:
            continue
        vols = np.zeros(nb)
        lo_i = np.floor((seg.low.to_numpy() - lo_all) / w).astype(int)
        hi_i = np.floor((seg.high.to_numpy() - lo_all) / w).astype(int)
        v = seg.volume.to_numpy().astype(float)
        for a, b, vv in zip(lo_i, hi_i, v):
            n = b - a + 1
            vols[a:b + 1] += vv / n
        poc_i = int(vols.argmax())
        tot = vols.sum()
        # 70% VA expansion
        va_lo = va_hi = poc_i
        acc = vols[poc_i]
        while acc < 0.70 * tot:
            up2 = vols[va_hi + 1:va_hi + 3].sum() if va_hi + 1 < nb else -1
            dn2 = vols[max(0, va_lo - 2):va_lo].sum() if va_lo - 1 >= 0 else -1
            if up2 >= dn2 and up2 >= 0:
                take = min(2, nb - 1 - va_hi)
                acc += vols[va_hi + 1:va_hi + 1 + take].sum()
                va_hi += take
            elif dn2 >= 0:
                take = min(2, va_lo)
                acc += vols[va_lo - take:va_lo].sum()
                va_lo -= take
            else:
                break
        ctr = lambda i: lo_all + (i + 0.5) * w
        rows.append(dict(day=day, poc=ctr(poc_i), vah=ctr(va_hi), val=ctr(va_lo),
                         day_hi=hi_all, day_lo=lo_all, close=seg.close.iloc[-1],
                         atr=atr, va_w=ctr(va_hi) - ctr(va_lo)))
    profiles = pd.DataFrame(rows).set_index("day")
    profiles.to_pickle(pkl)

emit(f"profiles built: {len(profiles)} days | median VA width = {profiles.va_w.median():.1f}$ "
     f"({(profiles.va_w/profiles.atr).median()*100:.0f}% of ATR)")

# prior-day levels joined to each day
P = profiles.copy()
P["p_poc"] = P.poc.shift(1); P["p_vah"] = P.vah.shift(1); P["p_val"] = P.val.shift(1)
P["p_vaw"] = P.va_w.shift(1)
P = P.dropna(subset=["p_poc"])

# per-day 1m arrays helper
day_bars = {day: seg for day, seg in g.groupby("day")}

def first_touch_time(seg, level, how):
    if how == "up":
        m = seg.index[seg.high >= level]
    else:
        m = seg.index[seg.low <= level]
    return m[0] if len(m) else pd.NaT

emit("\n=== 1. OPEN LOCATION vs PRIOR VALUE AREA ===")
opens = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    loc = "inside" if row.p_val <= op <= row.p_vah else ("above" if op > row.p_vah else "below")
    touch_poc = (seg.low.min() <= row.p_poc <= seg.high.max())
    touch_vah = (seg.high.max() >= row.p_vah) and (seg.low.min() <= row.p_vah)
    touch_val = (seg.low.min() <= row.p_val) and (seg.high.max() >= row.p_val)
    opens.append(dict(day=day, loc=loc, open=op, touch_poc=touch_poc,
                      close=row.close, p=row))
od = pd.DataFrame(opens).set_index("day")
loc_counts = od.loc[:, "loc"].value_counts(normalize=True) * 100
emit("open location: " + "  ".join(f"{k}={v:.1f}%" for k, v in loc_counts.items()))
for loc in ("inside", "above", "below"):
    sub = od[od.loc[:, "loc"] == loc]
    emit(f"  open {loc:>6} (N={len(sub)}): P(touch prior POC same day) = {sub.touch_poc.mean()*100:.1f}%")

emit("\n=== 2. MAGNET / ACCEPTANCE when open OUTSIDE prior VA ===")
res80 = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    op = seg.open.iloc[0]
    if row.p_val <= op <= row.p_vah:
        continue
    above = op > row.p_vah
    near_edge, far_edge = (row.p_vah, row.p_val) if above else (row.p_val, row.p_vah)
    t_edge = first_touch_time(seg, near_edge, "down" if above else "up")
    reached_edge = not pd.isna(t_edge)
    # acceptance: two consecutive 15m closes inside VA
    c15 = seg.close.resample("15min").last().dropna()
    inside = (c15 <= row.p_vah) & (c15 >= row.p_val)
    acc_idx = None
    vals = inside.to_numpy()
    for i in range(1, len(vals)):
        if vals[i] and vals[i - 1]:
            acc_idx = c15.index[i]
            break
    accepted = acc_idx is not None
    rotated = False
    stopped = False
    if accepted:
        after = seg[seg.index > acc_idx]
        t_far = first_touch_time(after, far_edge, "down" if above else "up")
        fail_lvl = near_edge + (0.5 * row.p_vaw if above else -0.5 * row.p_vaw)
        t_fail = first_touch_time(after, fail_lvl, "up" if above else "down")
        if not pd.isna(t_far) and (pd.isna(t_fail) or t_far < t_fail):
            rotated = True
        elif not pd.isna(t_fail):
            stopped = True
    res80.append(dict(day=day, above=above, reached_edge=reached_edge,
                      accepted=accepted, rotated=rotated, stopped=stopped,
                      touch_poc=od.touch_poc.get(day, np.nan)))
r8 = pd.DataFrame(res80)
emit(f"days opening outside VA: {len(r8)} ({len(r8)/len(P)*100:.0f}% of days)")
emit(f"P(price returns to nearer VA edge)          = {r8.reached_edge.mean()*100:.1f}%")
emit(f"P(reaches prior POC)                        = {r8.touch_poc.mean()*100:.1f}%")
emit(f"P(acceptance: 2 consecutive 15m closes in VA) = {r8.accepted.mean()*100:.1f}%")
acc = r8[r8.accepted]
emit(f"'80% rule': P(full rotation to FAR edge | accepted) = {acc.rotated.mean()*100:.1f}%  "
     f"(N={len(acc)}; failed-out first: {acc.stopped.mean()*100:.1f}%; rest = neither by close)")

emit("\n=== 3. POC ROTATION (user example) ===")
rot = []
for day, row in P.iterrows():
    seg = day_bars.get(day)
    if seg is None or len(seg) < 300:
        continue
    t_poc_u = first_touch_time(seg, row.p_poc, "up")
    t_poc_d = first_touch_time(seg, row.p_poc, "down")
    t_poc = min([t for t in (t_poc_u, t_poc_d) if not pd.isna(t)], default=pd.NaT)
    if pd.isna(t_poc):
        continue
    after = seg[seg.index >= t_poc]
    t_vah = first_touch_time(after, row.p_vah, "up")
    t_val = first_touch_time(after, row.p_val, "down")
    if pd.isna(t_vah) and pd.isna(t_val):
        first = "neither"
    elif pd.isna(t_val) or (not pd.isna(t_vah) and t_vah < t_val):
        first = "vah"
    else:
        first = "val"
    # displacement confirm: after POC touch, price moves 30% of half-VA toward an edge
    half = row.p_vaw / 2
    conf_up_lvl = row.p_poc + 0.3 * half
    conf_dn_lvl = row.p_poc - 0.3 * half
    t_cu = first_touch_time(after, conf_up_lvl, "up")
    t_cd = first_touch_time(after, conf_dn_lvl, "down")
    conf = None
    if not pd.isna(t_cu) and (pd.isna(t_cd) or t_cu < t_cd):
        conf = "up"
        af2 = after[after.index >= t_cu]
        t_tgt = first_touch_time(af2, row.p_vah, "up")
        t_back = first_touch_time(af2, row.p_poc - 0.3 * half, "down")
    elif not pd.isna(t_cd):
        conf = "dn"
        af2 = after[after.index >= t_cd]
        t_tgt = first_touch_time(af2, row.p_val, "down")
        t_back = first_touch_time(af2, row.p_poc + 0.3 * half, "up")
    conf_win = None
    if conf:
        conf_win = (not pd.isna(t_tgt)) and (pd.isna(t_back) or t_tgt < t_back)
    rot.append(dict(day=day, first=first, conf=conf, conf_win=conf_win))
rt = pd.DataFrame(rot)
emit(f"days touching prior POC: {len(rt)} ({len(rt)/len(P)*100:.0f}%)")
emit("after first POC touch, first VA edge hit: " +
     ", ".join(f"{k}={v*100:.1f}%" for k, v in rt["first"].value_counts(normalize=True).items()))
cw = rt.dropna(subset=["conf_win"])
emit(f"displacement-confirm (move 30% of half-VA off POC): P(reach that edge before re-crossing POC by 30%) = "
     f"{cw.conf_win.mean()*100:.1f}% (N={len(cw)})")

emit("\n=== 4. NAKED POC REVISITS ===")
prof_days = profiles.index.to_list()
naked = []
for i, day in enumerate(prof_days[:-1]):
    poc = profiles.poc.loc[day]
    revisit_in = None
    for j in range(i + 1, min(i + 21, len(prof_days))):
        seg = day_bars.get(prof_days[j])
        if seg is None:
            continue
        if seg.low.min() <= poc <= seg.high.max():
            revisit_in = j - i
            break
    naked.append(dict(day=day, rv=revisit_in))
nk = pd.DataFrame(naked)
emit(f"P(POC revisited next day) = {(nk.rv==1).mean()*100:.1f}%")
emit(f"P(revisited within 5 days) = {(nk.rv<=5).mean()*100:.1f}%")
emit(f"P(revisited within 20 days) = {(nk.rv<=20).mean()*100:.1f}%")
emit(f"still naked after 20 days: {nk.rv.isna().mean()*100:.1f}%")

with open(os.path.join(OUT, "12_volume_profile.txt"), "w") as f:
    f.write("\n".join(lines))
