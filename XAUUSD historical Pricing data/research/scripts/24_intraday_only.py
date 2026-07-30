"""V5 — INTRADAY-ONLY rebuild. Constraint: every position opens and closes inside
the same trading day. CARRY (20:00 -> 02:00 overnight) is therefore disqualified,
so its contribution must be replaced by intraday modules.

Tests, all DEV-only (2021-07 -> 2025-07):
  A  cost of the day-trading constraint (NYX alone vs NYX+CARRY)
  B  systematic session-ORB sweep: which opening ranges in the day carry expansion
     edge, using the frozen V4 engineering
  C  NYX refinements: re-entry, structural targets, regime & day filters,
     quality-weighted sizing
  D  Asia-break NY continuation as an intraday module
  E  intraday-only portfolio + walk-forward within DEV (fresh OOS evidence that
     does not burn the holdout further)
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

v2 = import_module("20_v2_engine")
v3 = import_module("21_v3_engineered")
v4 = import_module("22_v4_portfolio")
score, account = v2.score, v4.account
OUT, DAYS, DKEYS, DEV_END = v2.OUT, v2.DAYS, v2.DKEYS, v2.DEV_END
COST_MKT = v2.COST_MKT
FROZEN_ORB = v4.FROZEN_ORB

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))


def sess_orb(holdout=False, or_start=13 * 60 + 30, or_len=30, exit_min=20 * 60 + 55,
             stop_atr=0.25, t1_mult=1.0, scale=0.33, be=True, gap_filter=True,
             or_min=0.04, or_max=0.50, max_trades=1, t2_struct=False,
             min_atr_pct=None, dow_skip=(), qual_size=False, cost_mult=1.0,
             tag="ORB"):
    """Generalised opening-range module with V4 engineering. Fully intraday."""
    rows = []
    atr_hist = [DAYS[d]["atr"] for d in DKEYS]
    atr_lo = np.percentile(atr_hist, 20) if min_atr_pct else None
    for dk in DKEYS:
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        if pd.Timestamp(dk).weekday() in dow_skip:
            continue
        if min_atr_pct is not None and D["atr"] < atr_lo:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        atr = D["atr"]
        oi = np.where((tod >= or_start) & (tod < or_start + or_len))[0]
        if len(oi) < or_len - 3:
            continue
        o_hi, o_lo = h[oi].max(), l[oi].min()
        orw = o_hi - o_lo
        if orw <= 0 or orw > or_max * atr or orw < or_min * atr:
            continue
        loc = "inside"
        if not pd.isna(D["vah"]) and not pd.isna(D["val"]):
            if D["open_px"] > D["vah"]:
                loc = "above"
            elif D["open_px"] < D["val"]:
                loc = "below"

        scan_from = or_start + or_len
        n_done = 0
        used = set()
        while n_done < max_trades:
            ri = np.where((tod >= scan_from) & (tod < exit_min))[0]
            if len(ri) < 20:
                break
            hu = ri[h[ri] >= o_hi]; hd = ri[l[ri] <= o_lo]
            tu = hu[0] if len(hu) else None
            td = hd[0] if len(hd) else None
            cands = [(t, s) for t, s in ((tu, 1), (td, -1)) if t is not None and s not in used]
            if not cands:
                break
            i0, side = min(cands, key=lambda x: x[0])
            entry = o_hi if side == 1 else o_lo
            if gap_filter and loc != "inside" and ((loc == "above") != (side == 1)):
                used.add(side); scan_from = tod[i0] + 1
                continue
            risk = stop_atr * atr
            stop = entry - side * risk
            t1 = entry + side * t1_mult * risk if t1_mult else None
            t2 = None
            if t2_struct:
                cand_lvls = [x for x in (D["pdh"] if side == 1 else D["pdl"], D["poc"])
                             if x is not None and not pd.isna(x) and side * (x - entry) > 0.5 * risk]
                if cand_lvls:
                    t2 = min(cand_lvls) if side == 1 else max(cand_lvls)
            w = 1.0
            if qual_size and loc == "inside":
                w = 1.5
            realised, remaining, cur, got = 0.0, 1.0, stop, False
            x_i = None
            for k in range(i0, len(c)):
                if tod[k] >= exit_min:
                    x_i = k; break
                if (l[k] <= cur) if side == 1 else (h[k] >= cur):
                    realised += remaining * side * (cur - entry); remaining = 0.0; x_i = k; break
                if t1 is not None and not got and k > i0:
                    if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                        realised += scale * side * (t1 - entry); remaining -= scale
                        got = True
                        if be:
                            cur = entry
                if t2 is not None and remaining > 0 and k > i0:
                    if (h[k] >= t2) if side == 1 else (l[k] <= t2):
                        realised += remaining * side * (t2 - entry); remaining = 0.0; x_i = k; break
            if x_i is None:
                x_i = len(c) - 1
            if remaining > 0:
                realised += remaining * side * (c[x_i] - entry)
            pnl = (realised - COST_MKT * cost_mult) * w
            rows.append(dict(dkey=dk, t=D["t"][i0], side=side, entry=entry, stop=stop,
                             risk=risk * w, pnl=pnl, R=pnl / (risk * w),
                             cost_pct=COST_MKT / risk * 100, got_t1=got,
                             dur=x_i - i0, year=D["t"][i0].year, module=tag, loc=loc))
            used.add(side); n_done += 1
            scan_from = tod[x_i] + 1
    return pd.DataFrame(rows)


def asia_break(holdout=False, exit_min=20 * 60 + 55, stop_atr=0.25, t1_mult=1.0,
               scale=0.33, be=True, cost_mult=1.0):
    """Asia range survives London, breaks in NY, entered on the pullback. Intraday."""
    rows = []
    for dk in DKEYS:
        D = DAYS[dk]
        if (D["ts"] > DEV_END) != holdout:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        lon = (tod >= 7 * 60) & (tod < 12 * 60)
        if lon.sum() < 60:
            continue
        if (c[lon] > D["asia_h"]).any() or (c[lon] < D["asia_l"]).any():
            continue
        ny = np.where((tod >= 12 * 60) & (tod < 16 * 60))[0]
        if len(ny) < 30:
            continue
        bu = ny[c[ny] > D["asia_h"]]; bd = ny[c[ny] < D["asia_l"]]
        tu = bu[0] if len(bu) else None; td = bd[0] if len(bd) else None
        if tu is None and td is None:
            continue
        if td is None or (tu is not None and tu < td):
            side, ib, lvl = 1, tu, D["asia_h"]
        else:
            side, ib, lvl = -1, td, D["asia_l"]
        e_i = None
        for k in range(ib + 1, len(c)):
            if tod[k] >= exit_min or (k - ib) > 120:
                break
            if (l[k] <= lvl) if side == 1 else (h[k] >= lvl):
                e_i = k; break
        if e_i is None:
            continue
        entry = lvl
        risk = stop_atr * D["atr"]
        stop = entry - side * risk
        t1 = entry + side * t1_mult * risk if t1_mult else None
        realised, remaining, cur, got = 0.0, 1.0, stop, False
        x_i = None
        for k in range(e_i + 1, len(c)):
            if tod[k] >= exit_min:
                x_i = k; break
            if (l[k] <= cur) if side == 1 else (h[k] >= cur):
                realised += remaining * side * (cur - entry); remaining = 0.0; x_i = k; break
            if t1 is not None and not got:
                if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                    realised += scale * side * (t1 - entry); remaining -= scale; got = True
                    if be:
                        cur = entry
        if x_i is None:
            x_i = len(c) - 1
        if remaining > 0:
            realised += remaining * side * (c[x_i] - entry)
        pnl = realised - COST_MKT * cost_mult
        rows.append(dict(dkey=dk, t=D["t"][e_i], side=side, entry=entry, stop=stop,
                         risk=risk, pnl=pnl, R=pnl / risk, cost_pct=COST_MKT / risk * 100,
                         got_t1=got, dur=x_i - e_i, year=D["t"][e_i].year,
                         module="ASIA", loc="-"))
    return pd.DataFrame(rows)


if __name__ == "__main__":
    emit("=" * 104)
    emit("V5 — INTRADAY-ONLY (no overnight holds). DEV 2021-07 → 2025-07")
    emit("=" * 104)

    emit("\n### A — what the day-trading constraint costs")
    nyx = v3.orb(**FROZEN_ORB)
    car = v3.carry(**v4.FROZEN_CARRY)
    s_n = score(nyx, "NYX alone (intraday, compliant)", emit)
    s_c = score(car, "CARRY (OVERNIGHT — disqualified)", emit)
    s_p = score(pd.concat([nyx, car]).sort_values("t"), "old V4 portfolio (non-compliant)", emit)
    emit(f"  -> dropping CARRY removes {s_c['tot']:.0f}R of {s_p['tot']:.0f}R dev profit. "
         f"That gap must be filled with intraday modules.")

    emit("\n### B — SESSION ORB SWEEP: where else in the day does expansion pay?")
    emit(f"{'window':<34}{'n':>6}{'win%':>8}{'exp':>10}{'PF':>7}{'totR':>9}{'DD':>8}")
    sess = {}
    for name, st, ln in (("London 07:00 +30m", 7 * 60, 30), ("London 08:00 +30m", 8 * 60, 30),
                         ("Pre-NY 12:00 +30m", 12 * 60, 30), ("COMEX 13:30 +30m (NYX)", 13 * 60 + 30, 30),
                         ("NYSE 14:30 +30m", 14 * 60 + 30, 30), ("PMfix 15:00 +30m", 15 * 60, 30),
                         ("London 07:00 +60m", 7 * 60, 60), ("COMEX 13:30 +45m", 13 * 60 + 30, 45)):
        t = sess_orb(or_start=st, or_len=ln, tag=name)
        s = score(t, name, emit)
        if s:
            sess[name] = (t, s)

    emit("\n### C — NYX refinements (each vs the frozen baseline +0.086R)")
    for lbl, kw in (
        ("C0 frozen baseline", dict()),
        ("C1 allow 2nd trade (re-entry)", dict(max_trades=2)),
        ("C2 structural T2 (PDH/PDL/POC)", dict(t2_struct=True)),
        ("C3 skip lowest-20% ATR days", dict(min_atr_pct=20)),
        ("C4 skip Fridays", dict(dow_skip=(4,))),
        ("C5 skip Mondays", dict(dow_skip=(0,))),
        ("C6 1.5x size on inside-value opens", dict(qual_size=True)),
        ("C7 exit 19:00 (earlier flat)", dict(exit_min=19 * 60)),
        ("C8 exit 17:00", dict(exit_min=17 * 60)),
        ("C9 tighter width gate 0.06-0.35", dict(or_min=0.06, or_max=0.35)),
        ("C10 stop 0.20xATR", dict(stop_atr=0.20)),
        ("C11 stop 0.30xATR", dict(stop_atr=0.30)),
        ("C12 T1 at 1.25R", dict(t1_mult=1.25)),
    ):
        score(sess_orb(**kw, tag="NYX"), lbl, emit)

    emit("\n### D — Asia-break NY continuation (intraday)")
    score(asia_break(), "D1 ASIA break+pullback", emit)
    score(asia_break(stop_atr=0.35), "D2 ASIA stop 0.35xATR", emit)

    with open(os.path.join(OUT, "24_intraday.txt"), "w") as f:
        f.write("\n".join(lines))
