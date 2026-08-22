"""V4 — frozen configuration, dev-set portfolio result, and the gates that killed CRT.

FROZEN CONFIG (declared here; script 23 runs exactly this on the untouched holdout):

  MODULE 1 "NYX" — NY opening-range expansion
    OR      = 13:30-14:00 UTC high/low
    gate    = 0.04 <= OR width / ATR20 <= 0.50
    filter  = profile gap-trap: on an outside-value open, no contra-side break
    entry   = stop order at the OR edge, first fill wins
    stop    = 0.25 x ATR20  (NOT the OR far side -- this is the cost fix)
    T1      = 1R, take 33%, then stop to break-even
    exit    = runner flat 20:55 UTC
  MODULE 2 "CARRY" — overnight flow drift
    entry   = long 20:00 UTC, Mon-Thu
    stop    = 0.50 x ATR20
    exit    = 02:00 UTC next dealing day, no target

  Sizing: 1% of current equity per trade, risk measured to the initial stop.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

v2 = import_module("20_v2_engine")
v3 = import_module("21_v3_engineered")
orb, carry, score = v3.orb, v3.carry, v2.score
OUT, DAYS, DKEYS = v2.OUT, v2.DAYS, v2.DKEYS
ACCOUNT0, RISK_PCT, COST_MKT = v2.ACCOUNT0, v2.RISK_PCT, v2.COST_MKT

FROZEN_ORB = dict(stop_mode="atr", stop_floor_atr=0.25, exit_min=20 * 60 + 55,
                  t1_mult=1.0, scale=0.33, be_after_t1=True, gap_filter=True,
                  or_min=0.04, or_max=0.50)
FROZEN_CARRY = dict(stop_atr=0.5, t1_mult=None, be_after_t1=False)

lines = []
def emit(s=""):
    print(s, flush=True); lines.append(str(s))


def account(t, label, risk_pct=RISK_PCT, start=ACCOUNT0):
    t = t.sort_values("t").reset_index(drop=True)
    eq = start
    rows = []
    for _, r in t.iterrows():
        oz = (eq * risk_pct) / r.risk
        pnl = oz * r.pnl
        eq += pnl
        rows.append(dict(t=r.t, pnl=pnl, equity=eq))
    cv = pd.DataFrame(rows).set_index("t")
    peak = cv.equity.cummax()
    mdd = ((cv.equity - peak) / peak).min() * 100
    yrs = (t.t.max() - t.t.min()).days / 365.25
    cagr = ((eq / start) ** (1 / yrs) - 1) * 100
    emit(f"\n{label}")
    emit(f"  final equity ${eq:,.0f}   net ${eq-start:+,.0f}   "
         f"total {(eq/start-1)*100:+.1f}%   CAGR {cagr:+.1f}%   max equity DD {mdd:.1f}%")
    wk = cv.pnl.resample("W").agg(["sum", "size"])
    mo = cv.pnl.resample("ME").agg(["sum", "size"])
    emit(f"  WEEKLY  mean ${wk['sum'].mean():+,.0f}  median ${wk['sum'].median():+,.0f}  "
         f"best ${wk['sum'].max():+,.0f}  worst ${wk['sum'].min():+,.0f}  "
         f"{(wk['sum']>0).mean()*100:.0f}% positive of {len(wk)}  {wk['size'].mean():.1f} trades/wk")
    emit(f"  MONTHLY mean ${mo['sum'].mean():+,.0f}  median ${mo['sum'].median():+,.0f}  "
         f"best ${mo['sum'].max():+,.0f}  worst ${mo['sum'].min():+,.0f}  "
         f"{(mo['sum']>0).mean()*100:.0f}% positive of {len(mo)}  {mo['size'].mean():.1f} trades/mo")
    return cv, dict(final=eq, cagr=cagr, mdd=mdd)


if __name__ == "__main__":
    emit("=" * 100)
    emit("V4 — FROZEN CONFIG, DEV-SET RESULT (2021-07 → 2025-07)")
    emit("=" * 100)

    t_orb = orb(**FROZEN_ORB)
    t_car = carry(**FROZEN_CARRY)
    s_orb = score(t_orb, "MODULE 1 · NYX (NY opening-range expansion)", emit, yearly=True)
    s_car = score(t_car, "MODULE 2 · CARRY (overnight drift)", emit, yearly=True)

    port = pd.concat([t_orb, t_car]).sort_values("t").reset_index(drop=True)
    s_p = score(port, "PORTFOLIO (NYX + CARRY)", emit, yearly=True)
    emit(f"\nreturn/DD  NYX {s_orb['tot']/abs(s_orb['dd']):.2f}   "
         f"CARRY {s_car['tot']/abs(s_car['dd']):.2f}   "
         f"PORTFOLIO {s_p['tot']/abs(s_p['dd']):.2f}")
    corr = None
    a = t_orb.set_index(t_orb.t.dt.date).R
    b = t_car.set_index(t_car.t.dt.date).R
    j = pd.concat([a.groupby(level=0).sum(), b.groupby(level=0).sum()], axis=1).dropna()
    if len(j) > 30:
        corr = j.iloc[:, 0].corr(j.iloc[:, 1])
    emit(f"daily R correlation between modules: {corr:+.3f} (near zero = genuine diversification)")

    emit("\n" + "=" * 100)
    emit("GATE — RANDOM-ENTRY NULL (the test that killed CRT v1), applied to NYX")
    emit("=" * 100)
    rng = np.random.default_rng(7)
    pool = []
    for _ in range(15000):
        dk = DKEYS[rng.integers(len(DKEYS))]
        D = DAYS[dk]
        if D["ts"] > v2.DEV_END:
            continue
        tod, h, l, c = D["tod"], D["h"], D["l"], D["c"]
        idx = np.where((tod >= 14 * 60) & (tod < 20 * 60))[0]
        if len(idx) < 30:
            continue
        i0 = int(rng.choice(idx))
        side = 1 if rng.random() < 0.5 else -1
        risk = 0.25 * D["atr"]
        entry = c[i0]; stop = entry - side * risk; t1 = entry + side * risk
        realised, remaining, cur, got = 0.0, 1.0, stop, False
        x = len(c) - 1
        for k in range(i0 + 1, len(c)):
            if tod[k] >= 20 * 60 + 55:
                x = k; break
            if (l[k] <= cur) if side == 1 else (h[k] >= cur):
                realised += remaining * side * (cur - entry); remaining = 0.0; x = k; break
            if not got and ((h[k] >= t1) if side == 1 else (l[k] <= t1)):
                realised += 0.33 * side * (t1 - entry); remaining -= 0.33; got = True; cur = entry
        if remaining > 0:
            realised += remaining * side * (c[x] - entry)
        pool.append((realised - COST_MKT) / risk)
    pool = np.array(pool)
    sims = np.array([rng.choice(pool, len(t_orb), replace=True).mean() for _ in range(2000)])
    p95 = np.percentile(sims, 95)
    emit(f"  null (identical geometry/session/costs, random entry & side, n={len(pool):,} pool):")
    emit(f"    p5={np.percentile(sims,5):+.4f}R  median={np.median(sims):+.4f}R  p95={p95:+.4f}R")
    emit(f"  NYX expectancy: {t_orb.R.mean():+.4f}R")
    emit(f"  VERDICT: {'PASS — beats the 95th percentile of random entry' if t_orb.R.mean() > p95 else 'FAIL'}")

    emit("\n### COST STRESS (spec requirement: survive 2x)")
    for cm in (1.0, 1.5, 2.0):
        e_o = orb(**{**FROZEN_ORB, "cost_mult": cm}).R.mean()
        e_c = carry(**{**FROZEN_CARRY, "cost_mult": cm}).R.mean()
        emit(f"  {cm:.1f}x cost:  NYX {e_o:+.4f}R   CARRY {e_c:+.4f}R")

    emit("\n" + "=" * 100)
    emit("$100,000 ACCOUNT @ 1% RISK — DEV SET")
    emit("=" * 100)
    account(t_orb, "MODULE 1 · NYX only")
    account(t_car, "MODULE 2 · CARRY only")
    account(port, "PORTFOLIO (both modules)")

    with open(os.path.join(OUT, "22_v4_portfolio.txt"), "w") as f:
        f.write("\n".join(lines))
