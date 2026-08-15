"""Asia-range breakout — strategy construction from the 25_ study findings.

Study said (dev set):
  * baseline sustain (+1 range before -0.5 range) = 26.1%, BELOW the 33.3% a 2:1
    payoff needs. So the naive breakout loses.
  * median MFE after a break is only 0.49 x range -> a 1.0-range target is wrong.
  * range size matters hugely: <0.35 ATR sustains 31-34%, >0.60 ATR only 10-17%.
  * prior-day level 0-0.5 range AHEAD sustains 32.8%; already-cleared only 21-22%.
  * Asia inside the prior day's range: 30.0% vs 21.6%.
  * Sunday breaks are poor (17.9%); breaks after 12:00 UTC are poor.

Therefore the design must (a) filter hard on range size + magnet, and (b) get a
much better entry price so the payoff works against a ~0.5-range move. That is
exactly the user's retrace idea, and it is tested here against alternatives.

Entry models   : break | retrace | retrace_confirm
Stop models    : swing30 | swing60 | range_mid | range_far | atr | frac
Targets        : none(time) | 0.5R | 1R | pdlevel | partial+runner
DEV SET ONLY.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

v2 = import_module("20_v2_engine")
score = v2.score
OUT, DAYS, DKEYS, DEV_END = v2.OUT, v2.DAYS, v2.DKEYS, v2.DEV_END
COST = 0.25          # user trades a Razor / raw-spread account

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))

BREAK_START, BREAK_END = 7 * 60, 16 * 60
FLAT = 20 * 60 + 55


def run(holdout=False, entry="retrace", stop_model="swing60", target="partial",
        rng_max=None, rng_min=None, magnet=None, inside_pd_only=False,
        skip_sun=False, break_before=None, t1_mult=1.0, scale=0.5, be=True,
        max_wait=120, stop_floor_atr=0.08, cost=COST, tag="ASIA"):
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
        if rng_max is not None and r_atr > rng_max:
            continue
        if rng_min is not None and r_atr < rng_min:
            continue
        pdh, pdl = D["pdh"], D["pdl"]
        if inside_pd_only:
            if pdh is None or pdl is None or pd.isna(pdh) or pd.isna(pdl):
                continue
            if not (a_hi <= pdh and a_lo >= pdl):
                continue

        win = np.where((tod >= BREAK_START) & (tod < BREAK_END))[0]
        if len(win) < 60:
            continue
        up = win[h[win] > a_hi]; dn = win[l[win] < a_lo]
        iu = up[0] if len(up) else None
        idn = dn[0] if len(dn) else None
        if iu is None and idn is None:
            continue
        if idn is None or (iu is not None and iu < idn):
            side, ib, lvl = 1, iu, a_hi
        else:
            side, ib, lvl = -1, idn, a_lo
        if break_before is not None and tod[ib] >= break_before:
            continue

        fwd = pdh if side == 1 else pdl
        mag = np.nan
        if fwd is not None and not pd.isna(fwd):
            mag = side * (fwd - lvl) / rng
        if magnet is not None:
            lo_m, hi_m = magnet
            if np.isnan(mag) or not (lo_m <= mag <= hi_m):
                continue

        # ---------------- entry ----------------
        if entry == "break":
            e_i, ent = ib, lvl
        else:
            e_i, ent = None, None
            for k in range(ib + 1, len(c)):
                if tod[k] >= FLAT or (k - ib) > max_wait:
                    break
                # invalidate if price closes back well inside the range
                if side * (c[k] - lvl) < -0.25 * rng:
                    break
                touched = (l[k] <= lvl) if side == 1 else (h[k] >= lvl)
                if touched:
                    if entry == "retrace":
                        e_i, ent = k, lvl
                        break
                    else:   # retrace_confirm: need a close back beyond the level
                        for k2 in range(k, min(k + 30, len(c))):
                            if tod[k2] >= FLAT:
                                break
                            if side * (c[k2] - lvl) > 0:
                                e_i, ent = k2, c[k2]
                                break
                        break
            if e_i is None:
                continue

        # ---------------- stop ----------------
        if stop_model in ("swing30", "swing60"):
            back = 30 if stop_model == "swing30" else 60
            s0 = max(0, ib - back)
            sw = l[s0:ib + 1].min() if side == 1 else h[s0:ib + 1].max()
            stop = sw - side * 0.05 * atr
        elif stop_model == "range_mid":
            stop = (a_hi + a_lo) / 2
        elif stop_model == "range_far":
            stop = a_lo if side == 1 else a_hi
        elif stop_model == "atr":
            stop = ent - side * 0.25 * atr
        else:                       # frac of range
            stop = lvl - side * 0.35 * rng
        risk = abs(ent - stop)
        floor = stop_floor_atr * atr
        if risk < floor:            # never let cost dominate a micro stop
            stop = ent - side * floor
            risk = floor
        if risk <= 0 or risk > 1.5 * atr:
            continue

        # ---------------- targets ----------------
        t1 = t2 = None
        if target == "0.5R":
            t2 = lvl + side * 0.5 * rng
        elif target == "1R":
            t2 = lvl + side * 1.0 * rng
        elif target == "pdlevel":
            if not np.isnan(mag) and mag > 0.1:
                t2 = fwd
        elif target == "partial":
            t1 = ent + side * t1_mult * risk

        realised, remaining, cur, got = 0.0, 1.0, stop, False
        x_i = None
        for k in range(e_i + (0 if entry == "break" else 1), len(c)):
            if tod[k] >= FLAT:
                x_i = k; break
            if (l[k] <= cur) if side == 1 else (h[k] >= cur):
                realised += remaining * side * (cur - ent); remaining = 0.0; x_i = k; break
            if t1 is not None and not got and k > e_i:
                if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                    realised += scale * side * (t1 - ent); remaining -= scale; got = True
                    if be:
                        cur = ent
            if t2 is not None and remaining > 0 and k > e_i:
                if (h[k] >= t2) if side == 1 else (l[k] <= t2):
                    realised += remaining * side * (t2 - ent); remaining = 0.0; x_i = k; break
        if x_i is None:
            x_i = len(c) - 1
        if remaining > 0:
            realised += remaining * side * (c[x_i] - ent)
        pnl = realised - cost
        rows.append(dict(dk=dk, t=D["t"][e_i], side=side, risk=risk, pnl=pnl,
                         R=pnl / risk, cost_pct=cost / risk * 100, rng_atr=r_atr,
                         magnet=mag, dur=x_i - e_i, year=D["t"][e_i].year,
                         module=tag, got_t1=got))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    emit("=" * 104)
    emit("ASIA RANGE BREAKOUT — STRATEGY BUILD (DEV, Razor costs $0.25/oz)")
    emit("=" * 104)

    emit("\n### 1 — ENTRY MODEL (stop = pre-break swing, partial+runner)")
    for e in ("break", "retrace", "retrace_confirm"):
        score(run(entry=e), f"  entry={e}", emit)

    emit("\n### 2 — STOP MODEL (entry = retrace)")
    for s in ("swing30", "swing60", "range_mid", "range_far", "atr", "frac"):
        score(run(stop_model=s), f"  stop={s}", emit)

    emit("\n### 3 — TARGET MODEL (entry=retrace, stop=swing60)")
    for t in ("partial", "none", "0.5R", "1R", "pdlevel"):
        score(run(target=t), f"  target={t}", emit)

    emit("\n### 4 — CONFLUENCE STACK (added one at a time)")
    base = dict(entry="retrace", stop_model="swing60", target="partial")
    stack = [
        ("S0 no filters", {}),
        ("S1 + range < 0.60 ATR", dict(rng_max=0.60)),
        ("S2 + range < 0.45 ATR", dict(rng_max=0.45)),
        ("S3 + range 0.15-0.45", dict(rng_max=0.45, rng_min=0.15)),
        ("S4 S3 + PD level 0-1R ahead", dict(rng_max=0.45, rng_min=0.15, magnet=(0.0, 1.0))),
        ("S5 S3 + PD level 0-0.5R ahead", dict(rng_max=0.45, rng_min=0.15, magnet=(0.0, 0.5))),
        ("S6 S4 + skip Sunday", dict(rng_max=0.45, rng_min=0.15, magnet=(0.0, 1.0), skip_sun=True)),
        ("S7 S6 + break before 12:00", dict(rng_max=0.45, rng_min=0.15, magnet=(0.0, 1.0),
                                            skip_sun=True, break_before=12 * 60)),
        ("S8 S7 + Asia inside prior day", dict(rng_max=0.45, rng_min=0.15, magnet=(0.0, 1.0),
                                               skip_sun=True, break_before=12 * 60,
                                               inside_pd_only=True)),
    ]
    for lbl, kw in stack:
        t = score(run(**base, **kw), f"  {lbl}", emit)

    emit("\n### 5 — refine the survivor (target & partial variants)")
    best = dict(entry="retrace", stop_model="swing60", rng_max=0.45, rng_min=0.15,
                magnet=(0.0, 1.0), skip_sun=True, break_before=12 * 60)
    for lbl, kw in (("T1 1R 50% + BE + runner", dict(target="partial", t1_mult=1.0, scale=0.5)),
                    ("T1 1R 33% + BE + runner", dict(target="partial", t1_mult=1.0, scale=0.33)),
                    ("T1 1.5R 50% + BE", dict(target="partial", t1_mult=1.5, scale=0.5)),
                    ("no target, time exit", dict(target="none")),
                    ("single target 0.5 range", dict(target="0.5R")),
                    ("single target PD level", dict(target="pdlevel"))):
        score(run(**best, **kw), f"  {lbl}", emit)

    with open(os.path.join(OUT, "26_asia_strategy.txt"), "w") as f:
        f.write("\n".join(lines))
