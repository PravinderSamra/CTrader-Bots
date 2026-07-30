"""V3 — apply the V2 engineering lessons to a signal that HAS gross edge.

V2 conclusion: sweep-reversion's gross expectancy is ~0. Widening stops and adding
partials took net expectancy from -0.227R to -0.044R, i.e. all the way up to "no
edge" and no further. So the signal is replaced, the engineering is kept:

  KEEP  ATR-floored stops (cost/risk 3-6% instead of 27%)
  KEEP  partial at T1 + break-even + runner (win rate 31% -> 47%)
  KEEP  limit entries where they fill honestly (cheaper, better price)
  DROP  the sweep as a trigger; retain it only as an optional context flag

Signal = NY opening-range expansion (13:30 UTC + 30m), the strongest intraday edge
in this project, plus the profile gap-trap filter.

DEV SET ONLY (2021-07 -> 2025-07).
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
v2 = import_module("20_v2_engine")
OUT, CACHE = v2.OUT, v2.CACHE
DEV_END = v2.DEV_END
COST_MKT, COST_LMT = v2.COST_MKT, v2.COST_LMT

m1, m5, m15, h1, d1 = prep.load_all()
DAYS, DKEYS, DAY = v2.DAYS, v2.DKEYS, v2.DAY

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))


def orb(holdout=False, or_start=13 * 60 + 30, or_len=30, exit_min=20 * 60,
        stop_mode="orb_floor", stop_floor_atr=0.25, t1_mult=1.0, scale=0.5,
        be_after_t1=True, t2_mult=None, gap_filter=True, or_max=0.50,
        or_min=0.04, sweep_flag=False, cost_mult=1.0, risk_cap=None):
    """NY opening-range breakout with V2 exit engineering."""
    rows = []
    for dk in DKEYS:
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        atr = D["atr"]
        oi = np.where((tod >= or_start) & (tod < or_start + or_len))[0]
        ri = np.where((tod >= or_start + or_len) & (tod < exit_min))[0]
        if len(oi) < or_len - 3 or len(ri) < 30:
            continue
        o_hi, o_lo = h[oi].max(), l[oi].min()
        orw = o_hi - o_lo
        if orw <= 0 or orw > or_max * atr or orw < or_min * atr:
            continue

        # profile gap-trap filter: no contra-side breaks on outside-value opens
        loc = "inside"
        if not pd.isna(D["vah"]) and not pd.isna(D["val"]):
            if D["open_px"] > D["vah"]:
                loc = "above"
            elif D["open_px"] < D["val"]:
                loc = "below"

        hit_u = ri[h[ri] >= o_hi]
        hit_d = ri[l[ri] <= o_lo]
        tu = hit_u[0] if len(hit_u) else None
        td = hit_d[0] if len(hit_d) else None
        if tu is None and td is None:
            continue
        if td is None or (tu is not None and tu < td):
            side, i0, entry, far = 1, tu, o_hi, o_lo
        else:
            side, i0, entry, far = -1, td, o_lo, o_hi
        if gap_filter and loc != "inside" and ((loc == "above") != (side == 1)):
            continue
        if sweep_flag:
            # require the OR break to also reclaim/extend beyond a swept PD level
            lvl = D["pdh"] if side == 1 else D["pdl"]
            if pd.isna(lvl) or side * (entry - lvl) < 0:
                continue

        # ---- stop: structural, but never so tight that cost dominates ----
        struct = abs(entry - far)
        need = stop_floor_atr * atr
        if stop_mode == "orb":
            risk = struct
        elif stop_mode == "atr":
            risk = need
        else:                       # orb_floor
            risk = max(struct, need)
        if risk_cap is not None:
            risk = min(risk, risk_cap * atr)
        stop = entry - side * risk
        if risk <= 0:
            continue

        t1 = entry + side * t1_mult * risk if t1_mult else None
        t2 = entry + side * t2_mult * risk if t2_mult else None
        cost = COST_MKT * cost_mult

        realised, remaining, cur_stop, got_t1 = 0.0, 1.0, stop, False
        x_i = None
        for k in range(i0, len(c)):
            if tod[k] >= exit_min:
                x_i = k; break
            if (l[k] <= cur_stop) if side == 1 else (h[k] >= cur_stop):
                realised += remaining * side * (cur_stop - entry)
                remaining = 0.0; x_i = k; break
            if t1 is not None and not got_t1 and k > i0:
                if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                    realised += scale * side * (t1 - entry)
                    remaining -= scale; got_t1 = True
                    if be_after_t1:
                        cur_stop = entry
            if t2 is not None and remaining > 0 and k > i0:
                if (h[k] >= t2) if side == 1 else (l[k] <= t2):
                    realised += remaining * side * (t2 - entry)
                    remaining = 0.0; x_i = k; break
        if x_i is None:
            x_i = len(c) - 1
        if remaining > 0:
            realised += remaining * side * (c[x_i] - entry)
        pnl = realised - cost
        rows.append(dict(dkey=dk, t=D["t"][i0], side=side, entry=entry, stop=stop,
                         risk=risk, pnl=pnl, R=pnl / risk, cost_pct=cost / risk * 100,
                         got_t1=got_t1, dur=x_i - i0, year=D["t"][i0].year,
                         module="ORB"))
    return pd.DataFrame(rows)


def carry(holdout=False, entry_min=20 * 60, exit_min=2 * 60, stop_atr=0.5,
          t1_mult=None, scale=0.5, be_after_t1=False, cost_mult=1.0):
    """Overnight flow-drift carry: long at 20:00 UTC Mon-Thu, out 02:00."""
    rows = []
    for n, dk in enumerate(DKEYS):
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        wd = pd.Timestamp(dk).weekday()
        if wd >= 4:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        ei = np.where(tod >= entry_min)[0]
        if len(ei) == 0:
            continue
        i0 = ei[0]
        entry = c[i0]
        risk = stop_atr * D["atr"]
        stop = entry - risk
        # the exit is on the NEXT dealing day, 02:00 UTC
        if n + 1 >= len(DKEYS):
            continue
        D2 = DAYS[DKEYS[n + 1]]
        if (D2["ts"] - D["ts"]).days > 3:
            continue
        realised, remaining, cur_stop = 0.0, 1.0, stop
        # segment 1: rest of today
        px_last = c[-1]
        for k in range(i0 + 1, len(c)):
            if l[k] <= cur_stop:
                realised += remaining * (cur_stop - entry); remaining = 0.0
                break
        if remaining > 0:
            x2 = np.where(D2["tod"] >= exit_min)[0]
            if len(x2) == 0:
                continue
            j_end = x2[0]
            for k in range(0, j_end + 1):
                if D2["l"][k] <= cur_stop:
                    realised += remaining * (cur_stop - entry); remaining = 0.0
                    break
            if remaining > 0:
                realised += remaining * (D2["c"][j_end] - entry)
        pnl = realised - COST_MKT * cost_mult
        rows.append(dict(dkey=dk, t=D["t"][i0], side=1, entry=entry, stop=stop,
                         risk=risk, pnl=pnl, R=pnl / risk,
                         cost_pct=COST_MKT / risk * 100, got_t1=False, dur=360,
                         year=D["t"][i0].year, module="CARRY"))
    return pd.DataFrame(rows)


def aftershock(holdout=False, win=(12 * 60, 15 * 60 + 30), sigma=4.0, wait=5,
               width=0.15, stop_atr=0.30, t1_mult=1.0, scale=0.5, be_after_t1=True,
               max_hold=240, exit_min=20 * 60, cost_mult=1.0):
    """Post-jump expansion ride: bracket after the first 4-sigma M1 jump."""
    r1 = np.log(m1.close).diff()
    sig = r1.rolling(1440).std()
    jump = (np.abs(r1) > sigma * sig).reindex(m1.index).fillna(False)
    JM = pd.Series(jump.values, index=m1.index)
    rows = []
    for dk in DKEYS:
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        jm = JM.reindex(D["t"]).fillna(False).to_numpy()
        cand = np.where(jm & (tod >= win[0]) & (tod < win[1]))[0]
        if len(cand) == 0:
            continue
        ij = cand[0]
        bi = min(ij + wait, len(c) - 1)
        base = c[bi]
        up, dn = base + width * D["atr"], base - width * D["atr"]
        filled = None
        for k in range(bi + 1, len(c)):
            if tod[k] >= exit_min or (k - bi) > 60:
                break
            if h[k] >= up:
                filled = (1, k, up); break
            if l[k] <= dn:
                filled = (-1, k, dn); break
        if filled is None:
            continue
        side, i0, entry = filled
        risk = max(2 * width * D["atr"], stop_atr * D["atr"])
        stop = entry - side * risk
        t1 = entry + side * t1_mult * risk if t1_mult else None
        realised, remaining, cur_stop, got_t1 = 0.0, 1.0, stop, False
        x_i = None
        for k in range(i0 + 1, len(c)):
            if tod[k] >= exit_min or (k - i0) > max_hold:
                x_i = k; break
            if (l[k] <= cur_stop) if side == 1 else (h[k] >= cur_stop):
                realised += remaining * side * (cur_stop - entry)
                remaining = 0.0; x_i = k; break
            if t1 is not None and not got_t1:
                if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                    realised += scale * side * (t1 - entry)
                    remaining -= scale; got_t1 = True
                    if be_after_t1:
                        cur_stop = entry
        if x_i is None:
            x_i = len(c) - 1
        if remaining > 0:
            realised += remaining * side * (c[x_i] - entry)
        pnl = realised - COST_MKT * cost_mult
        rows.append(dict(dkey=dk, t=D["t"][i0], side=side, entry=entry, stop=stop,
                         risk=risk, pnl=pnl, R=pnl / risk,
                         cost_pct=COST_MKT / risk * 100, got_t1=got_t1,
                         dur=x_i - i0, year=D["t"][i0].year, module="SHOCK"))
    return pd.DataFrame(rows)


score = v2.score

if __name__ == "__main__":
    n_cfg = 34      # carried from script 20
    emit("=" * 108)
    emit("V3 — ENGINEERING APPLIED TO SIGNALS WITH REAL GROSS EDGE (DEV 2021-07 → 2025-07)")
    emit("=" * 108)

    emit("\n### A — NY ORB: does V2's exit engineering improve it?")
    for lbl, kw in (
        ("A1 baseline (struct stop, no TP)", dict(stop_mode="orb", t1_mult=None, be_after_t1=False, gap_filter=False)),
        ("A2 + gap-trap filter", dict(stop_mode="orb", t1_mult=None, be_after_t1=False)),
        ("A3 + ATR-floored stop", dict(stop_mode="orb_floor", t1_mult=None, be_after_t1=False)),
        ("A4 + T1 1R 50% + BE + runner", dict(stop_mode="orb_floor")),
        ("A5 + T1 1.5R 50% + BE", dict(stop_mode="orb_floor", t1_mult=1.5)),
        ("A6 + T1 1R 33% + BE", dict(stop_mode="orb_floor", scale=0.33)),
        ("A7 + T1 1R 50%, no BE", dict(stop_mode="orb_floor", be_after_t1=False)),
        ("A8 pure ATR stop", dict(stop_mode="atr")),
    ):
        n_cfg += 1
        score(orb(**kw), lbl, emit)

    emit("\n### B — stop floor sweep (the cost/risk lever)")
    for f in (0.0, 0.10, 0.15, 0.25, 0.35):
        n_cfg += 1
        score(orb(stop_floor_atr=f), f"B stop_floor={f}xATR20", emit)

    emit("\n### C — OR window & width gates")
    for lbl, kw in (
        ("C1 OR 30m @13:30 (default)", dict()),
        ("C2 OR 15m @13:30", dict(or_len=15)),
        ("C3 OR 60m @13:30", dict(or_len=60)),
        ("C4 OR 30m @12:00", dict(or_start=12 * 60)),
        ("C5 width gate 0.06-0.40", dict(or_min=0.06, or_max=0.40)),
        ("C6 width gate 0.08-0.35", dict(or_min=0.08, or_max=0.35)),
        ("C7 exit 21:00 not 20:00", dict(exit_min=20 * 60 + 55)),
        ("C8 + sweep context flag", dict(sweep_flag=True)),
    ):
        n_cfg += 1
        score(orb(**kw), lbl, emit)

    emit("\n### D — other validated modules with the same engineering")
    n_cfg += 1; score(carry(), "D1 CARRY overnight 20:00→02:00", emit)
    n_cfg += 1; score(carry(t1_mult=1.0, be_after_t1=True), "D2 CARRY + T1/BE", emit)
    n_cfg += 1; score(aftershock(), "D3 SHOCK post-jump + T1/BE", emit)
    n_cfg += 1; score(aftershock(t1_mult=None, be_after_t1=False), "D4 SHOCK no TP", emit)

    emit(f"\nDEV configurations evaluated (cumulative): {n_cfg}")
    with open(os.path.join(OUT, "21_v3_ladder.txt"), "w") as f:
        f.write("\n".join(lines))
