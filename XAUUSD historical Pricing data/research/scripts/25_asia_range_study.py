"""Asia-range breakout — conditional study (descriptive, no strategy yet).

Asia range = 22:00 -> 06:59 UTC (11pm-8am UK summer). Breakout scan 07:00-16:00.

For every day we record the FIRST break of either side and then measure, causally:
  sustain  = from the break level, does price travel +1.0 x RANGE in the break
             direction BEFORE retracing -0.5 x RANGE back inside? (a 2:1 race)
  MFE/MAE  = best and worst excursion after the break, in range-multiples
  close_beyond = did the day close beyond the broken side

Then we slice those outcomes by the conditions the user asked about:
  A  range size (as a fraction of ATR20)
  B  PDH/PDL geometry - is the prior-day level beyond the break as a magnet, and
     how far away is it?
  C  range position vs prior day (inside day, overlap with prior value area)
  D  break timing, day of week, volatility regime, gap, Asia internal structure
DEV SET ONLY (2021-07 -> 2025-07).
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

v2 = import_module("20_v2_engine")
OUT = v2.OUT
DAYS, DKEYS, DEV_END = v2.DAYS, v2.DKEYS, v2.DEV_END

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))

BREAK_START, BREAK_END = 7 * 60, 16 * 60
FLAT = 20 * 60 + 55

rows = []
for n, dk in enumerate(DKEYS):
    D = DAYS[dk]
    if D["ts"] > DEV_END:
        continue
    tod, h, l, c, o = D["tod"], D["h"], D["l"], D["c"], D["o"]
    atr = D["atr"]
    a_hi, a_lo = D["asia_h"], D["asia_l"]
    rng = a_hi - a_lo
    if rng <= 0 or pd.isna(atr) or atr <= 0:
        continue
    mid = (a_hi + a_lo) / 2

    # Asia internal structure: where did Asia close within its own range?
    am = np.where((tod >= 22 * 60) | (tod < 7 * 60))[0]
    asia_close = c[am[-1]]
    asia_clv = (asia_close - a_lo) / rng          # 0 = at low, 1 = at high

    win = np.where((tod >= BREAK_START) & (tod < BREAK_END))[0]
    if len(win) < 60:
        continue
    up = win[h[win] > a_hi]
    dn = win[l[win] < a_lo]
    iu = up[0] if len(up) else None
    idn = dn[0] if len(dn) else None
    if iu is None and idn is None:
        rows.append(dict(dk=dk, broke=False))
        continue
    if idn is None or (iu is not None and iu < idn):
        side, i0, lvl = 1, iu, a_hi
    else:
        side, i0, lvl = -1, idn, a_lo

    # causal outcome race from the break bar forward
    tgt = lvl + side * 1.0 * rng
    inv = lvl - side * 0.5 * rng
    sustain, mfe, mae = np.nan, 0.0, 0.0
    for k in range(i0, len(c)):
        if tod[k] >= FLAT:
            break
        ex = (h[k] - lvl) * side if side == 1 else (lvl - l[k])
        ad = (lvl - l[k]) * side if side == 1 else (h[k] - lvl)
        mfe = max(mfe, ex / rng)
        mae = max(mae, ad / rng)
        if side == 1:
            if l[k] <= inv:
                sustain = 0; break
            if h[k] >= tgt:
                sustain = 1; break
        else:
            if h[k] >= inv:
                sustain = 0; break
            if l[k] <= tgt:
                sustain = 1; break
    if np.isnan(sustain):
        sustain = 0
    end = np.where(tod < FLAT)[0][-1]
    close_beyond = int(side * (c[end] - lvl) > 0)

    # PDH/PDL geometry relative to the break
    pdh, pdl = D["pdh"], D["pdl"]
    fwd_lvl = pdh if side == 1 else pdl
    magnet_ahead = np.nan
    if fwd_lvl is not None and not pd.isna(fwd_lvl):
        dist = side * (fwd_lvl - lvl)
        magnet_ahead = dist / rng      # >0 = prior-day level sits ahead of the break

    rows.append(dict(
        dk=dk, broke=True, side=side, rng=rng, rng_atr=rng / atr,
        sustain=sustain, mfe=mfe, mae=mae, close_beyond=close_beyond,
        t_break=tod[i0], dow=pd.Timestamp(dk).weekday(), atr=atr,
        asia_clv=asia_clv, magnet=magnet_ahead,
        inside_pd=int((a_hi <= (pdh if pdh is not None else 1e9)) and
                      (a_lo >= (pdl if pdl is not None else -1e9))),
        year=pd.Timestamp(dk).year))

df = pd.DataFrame(rows)
brk = df[df.broke == True].copy()

emit("=" * 96)
emit("ASIA RANGE BREAKOUT — CONDITIONAL STUDY (DEV 2021-07 → 2025-07)")
emit("=" * 96)
emit(f"days: {len(df)}   with a break 07:00-16:00: {len(brk)} ({len(brk)/len(df)*100:.1f}%)")
emit(f"\nBASELINE — after the first break:")
emit(f"  P(sustain: +1.0 range before -0.5 range retrace) = {brk.sustain.mean()*100:.1f}%")
emit(f"  P(close beyond the broken side)                  = {brk.close_beyond.mean()*100:.1f}%")
emit(f"  median MFE = {brk.mfe.median():.2f} x range   median MAE = {brk.mae.median():.2f} x range")
emit(f"  NOTE: a 2:1 payoff needs >33.3% to break even before costs. Baseline is "
     f"{'ABOVE' if brk.sustain.mean() > 0.333 else 'BELOW'} that.")

# ---------------------------------------------------------------- A range size
emit("\n" + "=" * 96)
emit("A — RANGE SIZE (user hypothesis: big ranges do not sustain)")
emit("=" * 96)
brk["rq"] = pd.cut(brk.rng_atr, [0, .25, .35, .45, .60, .80, 10],
                   labels=["<0.25", "0.25-0.35", "0.35-0.45", "0.45-0.60", "0.60-0.80", ">0.80"])
g = brk.groupby("rq", observed=True).agg(
    days=("sustain", "size"), sustain=("sustain", "mean"),
    close_beyond=("close_beyond", "mean"), mfe=("mfe", "median"), mae=("mae", "median"))
g["sustain"] = (g.sustain * 100).round(1); g["close_beyond"] = (g.close_beyond * 100).round(1)
emit(g.round(2).to_string())
emit(f"\n  median range = {brk.rng_atr.median():.2f} x ATR20")

# ---------------------------------------------------------------- B magnets
emit("\n" + "=" * 96)
emit("B — PDH/PDL AS A MAGNET (distance measured in range-multiples ahead of the break)")
emit("=" * 96)
m = brk.dropna(subset=["magnet"]).copy()
m["mq"] = pd.cut(m.magnet, [-99, -0.5, 0, 0.5, 1.0, 2.0, 99],
                 labels=["behind >0.5R", "behind 0-0.5R", "ahead 0-0.5R",
                         "ahead 0.5-1R", "ahead 1-2R", "ahead >2R"])
g = m.groupby("mq", observed=True).agg(days=("sustain", "size"), sustain=("sustain", "mean"),
                                       close_beyond=("close_beyond", "mean"), mfe=("mfe", "median"))
g["sustain"] = (g.sustain * 100).round(1); g["close_beyond"] = (g.close_beyond * 100).round(1)
emit(g.round(2).to_string())
emit("\n  'behind' = the prior-day level was already exceeded before the Asia break")
emit("  (i.e. the break is into open space); 'ahead' = it sits between price and the target.")

# ---------------------------------------------------------------- combined A x B
emit("\n" + "=" * 96)
emit("A x B — RANGE SIZE x MAGNET (the user's specific combined hypothesis)")
emit("=" * 96)
m["rq2"] = pd.cut(m.rng_atr, [0, .35, .60, 10], labels=["small <0.35", "mid 0.35-0.60", "large >0.60"])
m["mq2"] = np.where(m.magnet < 0, "level already cleared",
                    np.where(m.magnet <= 1.0, "level 0-1R ahead", "level >1R ahead"))
piv = m.pivot_table(index="rq2", columns="mq2", values="sustain", aggfunc=["mean", "size"], observed=True)
emit((piv["mean"] * 100).round(1).to_string())
emit("\ncounts:")
emit(piv["size"].to_string())

# ---------------------------------------------------------------- D other
emit("\n" + "=" * 96)
emit("D — OTHER CONDITIONS")
emit("=" * 96)
emit("\nbreak timing:")
brk["tq"] = pd.cut(brk.t_break, [0, 8 * 60, 10 * 60, 12 * 60, 14 * 60, 16 * 60],
                   labels=["07-08", "08-10", "10-12", "12-14", "14-16"])
g = brk.groupby("tq", observed=True).agg(days=("sustain", "size"), sustain=("sustain", "mean"),
                                         close_beyond=("close_beyond", "mean"))
emit((g.assign(sustain=(g.sustain * 100).round(1), close_beyond=(g.close_beyond * 100).round(1))).to_string())

emit("\nAsia close location within its own range (0=at low, 1=at high) vs break side:")
brk["clvq"] = pd.cut(brk.asia_clv, [0, .33, .67, 1.0], labels=["bottom third", "middle", "top third"])
emit(brk.groupby(["clvq", "side"], observed=True).agg(
    days=("sustain", "size"), sustain=("sustain", lambda x: round(x.mean() * 100, 1))).to_string())

emit("\nAsia range entirely inside the prior day's range?")
emit(brk.groupby("inside_pd").agg(days=("sustain", "size"),
                                  sustain=("sustain", lambda x: round(x.mean() * 100, 1)),
                                  close_beyond=("close_beyond", lambda x: round(x.mean() * 100, 1))).to_string())

emit("\nday of week (0=Mon):")
emit(brk.groupby("dow").agg(days=("sustain", "size"),
                            sustain=("sustain", lambda x: round(x.mean() * 100, 1))).to_string())

emit("\nbreak side:")
emit(brk.groupby("side").agg(days=("sustain", "size"),
                             sustain=("sustain", lambda x: round(x.mean() * 100, 1)),
                             close_beyond=("close_beyond", lambda x: round(x.mean() * 100, 1))).to_string())

emit("\nby year (stability of the base rate):")
emit(brk.groupby("year").agg(days=("sustain", "size"),
                             sustain=("sustain", lambda x: round(x.mean() * 100, 1))).to_string())

emit("\nMFE distribution (how far do breaks actually run, in range-multiples):")
emit(brk.mfe.describe(percentiles=[.25, .5, .75, .9]).round(2).to_string())

brk.to_pickle(os.path.join(OUT, "_asia_study.pkl"))
with open(os.path.join(OUT, "25_asia_study.txt"), "w") as f:
    f.write("\n".join(lines))
