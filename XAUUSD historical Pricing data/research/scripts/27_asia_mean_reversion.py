"""Asia range breakout FAILURE / mean-reversion study.

Same methodology as 25/26, inverted. The continuation study found only 26.1% of
breaks sustain, so 73.9% fail -- but failing to run is NOT the same as reverting
far enough to pay. This measures the reversion side directly.

PART 1 (descriptive) — from the first break of the Asia range:
    ext_max      how far beyond the level price extends before coming back (range units)
    back_to_lvl  does price return to the broken level at all?
    back_to_mid  does it reach the range midpoint?
    back_to_far  does it reach the OPPOSITE side of the range?
    failed_close does a bar close back inside the range after the break?
  sliced by every condition from the continuation study, so we can see which
  combinations produce genuine reversals rather than sideways chop.

PART 2 (strategy) — three fade entry models:
    A "extension fade"  : wait for +k range beyond the level, fade it
    B "reclaim fade"    : wait for a CLOSE back inside the range, fade on that
    C "level fade"      : fade at PDH/PDL when it sits just beyond the range
  with stop / target / confluence variants.

DEV SET ONLY.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

v2 = import_module("20_v2_engine")
score = v2.score
OUT, DAYS, DKEYS, DEV_END = v2.OUT, v2.DAYS, v2.DKEYS, v2.DEV_END
COST = 0.25

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))

BS, BE = 7 * 60, 16 * 60
FLAT = 20 * 60 + 55

# ------------------------------------------------------------------ PART 1
rows = []
for dk in DKEYS:
    D = DAYS[dk]
    if D["ts"] > DEV_END:
        continue
    tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
    atr = D["atr"]
    a_hi, a_lo = D["asia_h"], D["asia_l"]
    rng = a_hi - a_lo
    if rng <= 0 or pd.isna(atr) or atr <= 0:
        continue
    mid = (a_hi + a_lo) / 2
    win = np.where((tod >= BS) & (tod < BE))[0]
    if len(win) < 60:
        continue
    up = win[h[win] > a_hi]; dn = win[l[win] < a_lo]
    iu = up[0] if len(up) else None
    idn = dn[0] if len(dn) else None
    if iu is None and idn is None:
        continue
    if idn is None or (iu is not None and iu < idn):
        side, ib, lvl, far = 1, iu, a_hi, a_lo
    else:
        side, ib, lvl, far = -1, idn, a_lo, a_hi

    pdh, pdl = D["pdh"], D["pdl"]
    fwd = pdh if side == 1 else pdl
    mag = np.nan
    if fwd is not None and not pd.isna(fwd):
        mag = side * (fwd - lvl) / rng

    ext_max = 0.0
    back_lvl = back_mid = back_far = 0
    failed_close = 0
    t_fail = None
    for k in range(ib, len(c)):
        if tod[k] >= FLAT:
            break
        ex = side * (h[k] - lvl) if side == 1 else side * (l[k] - lvl)
        ext_max = max(ext_max, abs(ex) / rng if side * ex > 0 else 0)
        ext_now = (h[k] - lvl) / rng if side == 1 else (lvl - l[k]) / rng
        ext_max = max(ext_max, ext_now)
        if not back_lvl and ((l[k] <= lvl) if side == 1 else (h[k] >= lvl)):
            back_lvl = 1
        if not failed_close and side * (c[k] - lvl) < 0 and k > ib:
            failed_close = 1; t_fail = k
        if not back_mid and ((l[k] <= mid) if side == 1 else (h[k] >= mid)):
            back_mid = 1
        if not back_far and ((l[k] <= far) if side == 1 else (h[k] >= far)):
            back_far = 1
    rows.append(dict(dk=dk, side=side, rng_atr=rng / atr, magnet=mag,
                     ext_max=ext_max, back_lvl=back_lvl, back_mid=back_mid,
                     back_far=back_far, failed_close=failed_close,
                     t_break=tod[ib], dow=pd.Timestamp(dk).weekday(),
                     year=pd.Timestamp(dk).year))
S = pd.DataFrame(rows)

emit("=" * 100)
emit("ASIA BREAKOUT FAILURE / MEAN-REVERSION STUDY (DEV 2021-07 → 2025-07)")
emit("=" * 100)
emit(f"breaks analysed: {len(S)}")
emit(f"\nBASELINE reversion after the first break:")
emit(f"  P(returns to the broken level)      = {S.back_lvl.mean()*100:.1f}%")
emit(f"  P(a bar CLOSES back inside range)   = {S.failed_close.mean()*100:.1f}%")
emit(f"  P(reaches range MIDPOINT)           = {S.back_mid.mean()*100:.1f}%")
emit(f"  P(reaches the OPPOSITE side)        = {S.back_far.mean()*100:.1f}%")
emit(f"  median max extension beyond level   = {S.ext_max.median():.2f} x range")
emit(f"  75th pct extension                  = {S.ext_max.quantile(.75):.2f} x range")

emit("\n--- by RANGE SIZE (continuation was worst for large ranges) ---")
S["rq"] = pd.cut(S.rng_atr, [0, .30, .45, .60, .80, 10],
                 labels=["<0.30", "0.30-0.45", "0.45-0.60", "0.60-0.80", ">0.80"])
g = S.groupby("rq", observed=True).agg(days=("back_mid", "size"),
                                       back_lvl=("back_lvl", "mean"),
                                       back_mid=("back_mid", "mean"),
                                       back_far=("back_far", "mean"),
                                       ext=("ext_max", "median"))
for col in ("back_lvl", "back_mid", "back_far"):
    g[col] = (g[col] * 100).round(1)
emit(g.round(2).to_string())

emit("\n--- by MAGNET (prior-day level position) ---")
m = S.dropna(subset=["magnet"]).copy()
m["mq"] = pd.cut(m.magnet, [-99, 0, 0.5, 1.0, 99],
                 labels=["already cleared", "0-0.5R ahead", "0.5-1R ahead", ">1R ahead"])
g = m.groupby("mq", observed=True).agg(days=("back_mid", "size"),
                                       back_mid=("back_mid", "mean"),
                                       back_far=("back_far", "mean"),
                                       ext=("ext_max", "median"))
for col in ("back_mid", "back_far"):
    g[col] = (g[col] * 100).round(1)
emit(g.round(2).to_string())

emit("\n--- by BREAK TIME ---")
S["tq"] = pd.cut(S.t_break, [0, 8 * 60, 10 * 60, 12 * 60, 16 * 60],
                 labels=["07-08", "08-10", "10-12", "12-16"])
g = S.groupby("tq", observed=True).agg(days=("back_mid", "size"),
                                       back_mid=("back_mid", "mean"),
                                       back_far=("back_far", "mean"))
for col in ("back_mid", "back_far"):
    g[col] = (g[col] * 100).round(1)
emit(g.to_string())

emit("\n--- COMBINED: range size x magnet, P(reach range MIDPOINT) ---")
m["rq2"] = pd.cut(m.rng_atr, [0, .45, .60, 10], labels=["small<0.45", "mid", "large>0.60"])
m["mq2"] = np.where(m.magnet < 0, "cleared", np.where(m.magnet <= 1.0, "0-1R ahead", ">1R ahead"))
piv = m.pivot_table(index="rq2", columns="mq2", values="back_mid", aggfunc=["mean", "size"], observed=True)
emit((piv["mean"] * 100).round(1).to_string())
emit("counts:")
emit(piv["size"].to_string())

# ------------------------------------------------------------------ PART 2
def fade(holdout=False, model="ext", k_ext=0.20, stop_ext=0.45, target="mid",
         rng_min=None, rng_max=None, magnet=None, skip_sun=False,
         break_after=None, t1_mult=1.0, scale=0.5, be=True, cost=COST,
         max_wait=180, stop_floor_atr=0.08):
    rows = []
    for dk in DKEYS:
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        if skip_sun and pd.Timestamp(dk).weekday() == 6:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        atr = D["atr"]
        a_hi, a_lo = D["asia_h"], D["asia_l"]
        rng = a_hi - a_lo
        if rng <= 0 or pd.isna(atr) or atr <= 0:
            continue
        r_atr = rng / atr
        if rng_min is not None and r_atr < rng_min:
            continue
        if rng_max is not None and r_atr > rng_max:
            continue
        mid = (a_hi + a_lo) / 2
        win = np.where((tod >= BS) & (tod < BE))[0]
        if len(win) < 60:
            continue
        up = win[h[win] > a_hi]; dn = win[l[win] < a_lo]
        iu = up[0] if len(up) else None
        idn = dn[0] if len(dn) else None
        if iu is None and idn is None:
            continue
        if idn is None or (iu is not None and iu < idn):
            bside, ib, lvl, far = 1, iu, a_hi, a_lo
        else:
            bside, ib, lvl, far = -1, idn, a_lo, a_hi
        if break_after is not None and tod[ib] < break_after:
            continue
        pdh, pdl = D["pdh"], D["pdl"]
        fwd = pdh if bside == 1 else pdl
        mag = np.nan
        if fwd is not None and not pd.isna(fwd):
            mag = bside * (fwd - lvl) / rng
        if magnet is not None:
            lo_m, hi_m = magnet
            if np.isnan(mag) or not (lo_m <= mag <= hi_m):
                continue

        side = -bside          # we FADE the break
        e_i = ent = None
        if model == "ext":
            trig = lvl + bside * k_ext * rng
            for k in range(ib, len(c)):
                if tod[k] >= FLAT or (k - ib) > max_wait:
                    break
                if (h[k] >= trig) if bside == 1 else (l[k] <= trig):
                    e_i, ent = k, trig
                    break
        elif model == "reclaim":
            for k in range(ib + 1, len(c)):
                if tod[k] >= FLAT or (k - ib) > max_wait:
                    break
                if bside * (c[k] - lvl) < 0:      # closed back inside
                    e_i, ent = k, c[k]
                    break
        else:                                      # level fade at PDH/PDL
            if np.isnan(mag) or not (0 < mag <= 0.75):
                continue
            for k in range(ib, len(c)):
                if tod[k] >= FLAT or (k - ib) > max_wait:
                    break
                if (h[k] >= fwd) if bside == 1 else (l[k] <= fwd):
                    e_i, ent = k, fwd
                    break
        if e_i is None:
            continue

        if model == "reclaim":
            ext_so_far = max((h[ib:e_i + 1].max() - lvl) if bside == 1 else 0,
                             (lvl - l[ib:e_i + 1].min()) if bside == -1 else 0)
            stop = lvl + bside * (ext_so_far + 0.05 * atr)
        else:
            stop = lvl + bside * stop_ext * rng
        risk = abs(ent - stop)
        floor = stop_floor_atr * atr
        if risk < floor:
            stop = ent - side * floor
            risk = floor
        if risk <= 0 or risk > 1.5 * atr:
            continue

        t1 = t2 = None
        if target == "mid":
            t2 = mid
        elif target == "far":
            t2 = far
        elif target == "lvl":
            t2 = lvl
        elif target == "partial":
            t1 = ent + side * t1_mult * risk
        if t2 is not None and side * (t2 - ent) <= 0:
            continue

        realised, remaining, cur, got = 0.0, 1.0, stop, False
        x_i = None
        for k in range(e_i + 1, len(c)):
            if tod[k] >= FLAT:
                x_i = k; break
            if (l[k] <= cur) if side == 1 else (h[k] >= cur):
                realised += remaining * side * (cur - ent); remaining = 0.0; x_i = k; break
            if t1 is not None and not got:
                if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                    realised += scale * side * (t1 - ent); remaining -= scale; got = True
                    if be:
                        cur = ent
            if t2 is not None and remaining > 0:
                if (h[k] >= t2) if side == 1 else (l[k] <= t2):
                    realised += remaining * side * (t2 - ent); remaining = 0.0; x_i = k; break
        if x_i is None:
            x_i = len(c) - 1
        if remaining > 0:
            realised += remaining * side * (c[x_i] - ent)
        pnl = realised - cost
        rows.append(dict(dk=dk, t=D["t"][e_i], side=side, risk=risk, pnl=pnl,
                         R=pnl / risk, cost_pct=cost / risk * 100, rng_atr=r_atr,
                         magnet=mag, year=D["t"][e_i].year, module="FADE"))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    emit("\n" + "=" * 100)
    emit("PART 2 — FADE STRATEGY TESTS (Razor costs $0.25/oz)")
    emit("=" * 100)

    emit("\n### entry model (no filters, target = range mid)")
    for mdl in ("ext", "reclaim", "level"):
        score(fade(model=mdl), f"  model={mdl}", emit)

    emit("\n### extension-fade: how far to let it run before fading")
    for k in (0.10, 0.20, 0.30, 0.50):
        score(fade(model="ext", k_ext=k, stop_ext=k + 0.25), f"  fade at +{k} range", emit)

    emit("\n### target model (ext fade, k=0.20)")
    for tg in ("lvl", "mid", "far", "partial"):
        score(fade(model="ext", target=tg), f"  target={tg}", emit)

    emit("\n### CONFLUENCE STACK — fade the conditions that killed continuation")
    for lbl, kw in (
        ("F0 no filters", {}),
        ("F1 large range >0.60 ATR", dict(rng_min=0.60)),
        ("F2 large range >0.45 ATR", dict(rng_min=0.45)),
        ("F3 F2 + PD level already cleared", dict(rng_min=0.45, magnet=(-99, 0))),
        ("F4 F2 + late break (after 12:00)", dict(rng_min=0.45, break_after=12 * 60)),
        ("F5 large + cleared + late", dict(rng_min=0.45, magnet=(-99, 0), break_after=12 * 60)),
        ("F6 F3 + skip Sunday", dict(rng_min=0.45, magnet=(-99, 0), skip_sun=True)),
    ):
        score(fade(model="ext", **kw), f"  {lbl}", emit)

    emit("\n### best-looking cells with the RECLAIM entry (confirmed failure)")
    for lbl, kw in (("R1 large range >0.45", dict(rng_min=0.45)),
                    ("R2 large + cleared", dict(rng_min=0.45, magnet=(-99, 0))),
                    ("R3 large >0.60", dict(rng_min=0.60))):
        score(fade(model="reclaim", **kw), f"  {lbl}", emit)

    with open(os.path.join(OUT, "27_asia_reversion.txt"), "w") as f:
        f.write("\n".join(lines))
