"""V4 HOLDOUT — scored ONCE on 2025-07-17 -> 2026-07-16, config frozen in
FROZEN-CONFIG-V4.md (committed before this script was run). No re-tuning.
"""
import os
from importlib import import_module
import numpy as np, pandas as pd

v2 = import_module("20_v2_engine"); v3 = import_module("21_v3_engineered")
v4 = import_module("22_v4_portfolio")
orb, carry, score, account = v3.orb, v3.carry, v2.score, v4.account
FROZEN_ORB, FROZEN_CARRY = v4.FROZEN_ORB, v4.FROZEN_CARRY
OUT = v2.OUT

lines=[]
def emit(s=""):
    print(s, flush=True); lines.append(str(s))

emit("="*100); emit("V4 HOLDOUT — 2025-07-17 → 2026-07-16 (never used in development)"); emit("="*100)

dev_o, dev_c = orb(**FROZEN_ORB), carry(**FROZEN_CARRY)
ho_o = orb(holdout=True, **FROZEN_ORB)
ho_c = carry(holdout=True, **FROZEN_CARRY)
emit(f"holdout span: {ho_o.t.min()} → {ho_o.t.max()}")

emit("\n--- MODULE RESULTS ---")
s_do = score(dev_o, "NYX   DEV", emit);  s_ho = score(ho_o, "NYX   HOLDOUT", emit)
s_dc = score(dev_c, "CARRY DEV", emit);  s_hc = score(ho_c, "CARRY HOLDOUT", emit)
dev_p = pd.concat([dev_o, dev_c]).sort_values("t")
ho_p  = pd.concat([ho_o, ho_c]).sort_values("t")
s_dp = score(dev_p, "PORT  DEV", emit); s_hp = score(ho_p, "PORT  HOLDOUT", emit)

emit("\n--- PRE-DECLARED PASS/FAIL CRITERIA ---")
c1 = s_hp["exp"] > 0
c2 = s_hp["exp"] >= 0.5*s_dp["exp"]
c3 = s_ho["exp"] > 0
emit(f"  1. portfolio expectancy > 0 after costs        : {s_hp['exp']:+.4f}R  -> {'PASS' if c1 else 'FAIL'}")
emit(f"  2. portfolio expectancy >= 50% of dev (+{0.5*s_dp['exp']:.4f}R): {s_hp['exp']:+.4f}R  -> {'PASS' if c2 else 'FAIL'}")
emit(f"  3. NYX individually > 0                        : {s_ho['exp']:+.4f}R  -> {'PASS' if c3 else 'FAIL'}")

emit("\n--- $100,000 @ 1% RISK, HOLDOUT YEAR ---")
_, aA = account(ho_p, "VARIANT A — 1% both modules")
# Variant B: 1% NYX, 0.5% CARRY -> scale CARRY R contribution by half
hb = ho_p.copy()
hb.loc[hb.module=="CARRY","risk"] = hb.loc[hb.module=="CARRY","risk"]*2   # half size == double risk denom
_, aB = account(hb, "VARIANT B — 1% NYX / 0.5% CARRY")
dd_dev = 25.7
c4 = abs(aA["mdd"]) <= 1.5*dd_dev
emit(f"\n  4. max equity DD <= 1.5x dev ({1.5*dd_dev:.1f}%)          : {aA['mdd']:.1f}%  -> {'PASS' if c4 else 'FAIL'}")
emit(f"\n  OVERALL: {'*** VALIDATED ***' if (c1 and c2 and c3 and c4) else '*** FAILED ***'}")

emit("\n--- monthly P&L, holdout (Variant A) ---")
cv,_ = account(ho_p, "(recompute)")
mo = cv.pnl.resample("ME").sum()
for d,v_ in mo.items():
    emit(f"    {d.strftime('%Y-%m')}: ${v_:+,.0f}")

with open(os.path.join(OUT,"23_v4_holdout.txt"),"w") as f: f.write("\n".join(lines))
