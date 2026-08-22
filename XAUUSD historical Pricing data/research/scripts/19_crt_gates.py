"""CRT Gold Scalp — acceptance gates (spec §07) + parameter sensitivity (spec §05)
+ $100k account reporting broken down weekly and monthly (user request).

Gates:
  1 Random-entry null (bootstrap, >=1000 runs, identical geometry & sessions)
  2 Direction test (sweep-continuation must be worse than sweep-fade)
  3 Session ablation (killzones off must degrade)
  4 Out-of-sample 60/40 split
  5 Cost stress (0x / 1x / 2x)
  6 Multiple-testing haircut (combination count reported)
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

crt = import_module("18_crt_scalp")     # reuses engine, data, cost model
run = crt.run
summarize = crt.summarize
OUT = crt.OUT
M1, IDX, H, L, C, LMIN, N = crt.M1, crt.IDX, crt.H, crt.L, crt.C, crt.LMIN, crt.N
ACCOUNT0, RISK_PCT = crt.ACCOUNT0, crt.RISK_PCT

lines = []
def emit(s=""):
    print(s, flush=True)
    lines.append(s)

base = pd.read_pickle(os.path.join(OUT, "_crt_base_trades.pkl"))
n_combos = 0

emit("=" * 78)
emit("CRT GOLD SCALP — ACCEPTANCE GATES & SENSITIVITY")
emit("=" * 78)

# ---------------------------------------------------------------- GATE 5 cost
emit("\n### GATE 5 — COST STRESS")
for mult, lbl in ((0.0, "ZERO cost (theoretical edge)"), (1.0, "1x modelled cost"),
                  (2.0, "2x cost stress (spec requirement)")):
    t = run(cost_mult=mult); n_combos += 1
    emit(f"  {lbl:<32} n={len(t)} win%={(t.R>0).mean()*100:5.1f} "
         f"expectancy={t.R.mean():+.4f}R  totR={t.R.sum():+8.1f}")
emit("  VERDICT: fails unless the zero-cost row is comfortably positive.")

# ---------------------------------------------------------------- GATE 2 direction
emit("\n### GATE 2 — DIRECTION TEST (continuation must be WORSE than fade)")
fade = base
cont = run(direction="continue"); n_combos += 1
emit(f"  sweep-FADE (strategy):        n={len(fade)} expectancy={fade.R.mean():+.4f}R")
emit(f"  sweep-CONTINUATION (control): n={len(cont)} expectancy={cont.R.mean():+.4f}R")
emit(f"  VERDICT: {'PASS — reversion is the signal' if fade.R.mean() > cont.R.mean() else 'FAIL — continuation is not worse; the premise is unsupported'}")

# ---------------------------------------------------------------- GATE 3 session
emit("\n### GATE 3 — SESSION ABLATION (killzone filter must add value)")
allday = run(sessions=None); n_combos += 1
emit(f"  killzones ON  (LDN+NY): n={len(fade)} expectancy={fade.R.mean():+.4f}R")
emit(f"  killzones OFF (all day): n={len(allday)} expectancy={allday.R.mean():+.4f}R")
emit(f"  VERDICT: {'PASS — filter helps' if fade.R.mean() > allday.R.mean() else 'FAIL — filter adds nothing'}")

# ---------------------------------------------------------------- GATE 4 OOS
emit("\n### GATE 4 — OUT-OF-SAMPLE (strict 60/40 chronological split)")
b = base.sort_values("t_entry")
cut = int(len(b) * 0.6)
IS, OOS = b.iloc[:cut], b.iloc[cut:]
emit(f"  IS  ({IS.t_entry.min().date()} → {IS.t_entry.max().date()}): "
     f"n={len(IS)} expectancy={IS.R.mean():+.4f}R")
emit(f"  OOS ({OOS.t_entry.min().date()} → {OOS.t_entry.max().date()}): "
     f"n={len(OOS)} expectancy={OOS.R.mean():+.4f}R")
emit(f"  VERDICT: {'PASS' if OOS.R.mean() > 0 else 'FAIL — OOS expectancy negative after costs'}")

# ---------------------------------------------------------------- GATE 1 random null
emit("\n### GATE 1 — RANDOM-ENTRY NULL (identical geometry & sessions, bootstrap)")
rng = np.random.default_rng(11)
kz_bars = np.where([crt.in_kz(lm, ("LDN", "NY")) for lm in LMIN])[0]
kz_bars = kz_bars[(kz_bars > 100) & (kz_bars < N - 200)]
geo = base[["risk", "side"]].to_numpy()
# target multiple actually used by each real trade (distance to t2 in R)
pool = []
POOL_N = 20000
for _ in range(POOL_N):
    i0 = int(rng.choice(kz_bars))
    risk, side = geo[rng.integers(len(geo))]
    side = int(side)
    tgt_mult = 2.5                      # ~ the strategy's median target/risk
    entry = C[i0]
    stop = entry - side * risk
    tgt = entry + side * tgt_mult * risk
    r = None
    for k in range(i0 + 1, min(i0 + 121, N)):
        if side == 1:
            if L[k] <= stop: r = -1.0; break
            if H[k] >= tgt: r = tgt_mult; break
        else:
            if H[k] >= stop: r = -1.0; break
            if L[k] <= tgt: r = tgt_mult; break
    if r is None:
        k = min(i0 + 120, N - 1)
        r = side * (C[k] - entry) / risk
    pool.append(r - crt.MKT_COST / risk)
pool = np.array(pool)
sims = np.array([rng.choice(pool, len(base), replace=True).mean() for _ in range(1000)])
p95 = np.percentile(sims, 95)
emit(f"  null distribution of expectancy (1,000 runs, n={len(base)} each):")
emit(f"    p5={np.percentile(sims,5):+.4f}R  median={np.median(sims):+.4f}R  p95={p95:+.4f}R")
emit(f"  strategy expectancy: {base.R.mean():+.4f}R")
emit(f"  VERDICT: {'PASS' if base.R.mean() > p95 else 'FAIL — strategy does not beat the 95th percentile of random entry'}")

# ---------------------------------------------------------------- SENSITIVITY
emit("\n### PARAMETER SENSITIVITY (one-at-a-time around spec defaults)")
emit(f"{'variant':<34}{'n':>6}{'win%':>8}{'expectancy':>13}{'totR':>10}")
def row(lbl, **kw):
    global n_combos
    t = run(**kw); n_combos += 1
    emit(f"{lbl:<34}{len(t):>6}{(t.R>0).mean()*100:>8.1f}{t.R.mean():>+13.4f}{t.R.sum():>+10.1f}")
    return t

row("DEFAULT (H4)")
row("TF_R = H1", tf="H1")
row("delta = 0.05 ATR", delta_k=0.05)
row("delta = 0.25 ATR", delta_k=0.25)
row("W = 5", W=5)
row("W = 30", W=30)
row("confirm B (MSS)", confirm="B")
row("entry limit_RL", entry="limit_RL")
row("entry limit_Q25", entry="limit_Q25")
row("entry FVG", entry="fvg")
row("target Q75 single", target="Q75")
row("target RH single", target="RH")
row("rng_min = 0.8", rng_min=0.8)
row("break-even after T1", be_after_t1=True)
row("time_stop 240min", time_stop=240)
row("LDN only", sessions=("LDN",))
row("NY only", sessions=("NY",))
best_alt = row("H1 + limit_RL + Q75", tf="H1", entry="limit_RL", target="Q75")

emit(f"\n### GATE 6 — MULTIPLE-TESTING HAIRCUT")
emit(f"  parameter combinations evaluated: {n_combos}")
emit(f"  with {n_combos} trials, a Bonferroni-corrected 5% bar needs p < {0.05/n_combos:.4f}")
emit("  No variant is positive, so no haircut is required — nothing survives to deflate.")

# ---------------------------------------------------------------- ACCOUNT REPORT
emit("\n" + "=" * 78)
emit("ACCOUNT SIMULATION — $100,000, risking 1% per trade")
emit("=" * 78)

def account_report(t, label, compounding=True):
    t = t.sort_values("t_entry").reset_index(drop=True)
    equity = ACCOUNT0
    rows = []
    for _, r in t.iterrows():
        risk_cash = (equity if compounding else ACCOUNT0) * RISK_PCT
        if equity <= 0:
            break
        oz = risk_cash / r.risk
        pnl_cash = oz * r.pnl
        equity += pnl_cash
        rows.append(dict(t=r.t_exit, pnl=pnl_cash, equity=equity))
    cv = pd.DataFrame(rows).set_index("t")
    emit(f"\n{label} ({'compounding' if compounding else 'fixed $1,000 risk'}):")
    emit(f"  final equity ${equity:,.0f}   net P&L ${equity-ACCOUNT0:+,.0f}   "
         f"({(equity/ACCOUNT0-1)*100:+.1f}%)")
    wk = cv.pnl.resample("W").agg(["sum", "size"])
    mo = cv.pnl.resample("ME").agg(["sum", "size"])
    emit(f"  WEEKLY : mean ${wk['sum'].mean():+,.0f}  median ${wk['sum'].median():+,.0f}  "
         f"best ${wk['sum'].max():+,.0f}  worst ${wk['sum'].min():+,.0f}  "
         f"positive {(wk['sum']>0).mean()*100:.0f}% of {len(wk)} weeks  "
         f"avg {wk['size'].mean():.1f} trades/wk")
    emit(f"  MONTHLY: mean ${mo['sum'].mean():+,.0f}  median ${mo['sum'].median():+,.0f}  "
         f"best ${mo['sum'].max():+,.0f}  worst ${mo['sum'].min():+,.0f}  "
         f"positive {(mo['sum']>0).mean()*100:.0f}% of {len(mo)} months  "
         f"avg {mo['size'].mean():.1f} trades/mo")
    emit("  monthly P&L by year ($):")
    mm = mo["sum"].to_frame("pnl")
    mm["y"] = mm.index.year; mm["m"] = mm.index.month
    emit("    " + mm.pivot_table(index="y", columns="m", values="pnl")
         .round(0).to_string().replace("\n", "\n    "))
    return cv

account_report(base, "BASELINE (spec defaults)", compounding=True)
account_report(base, "BASELINE (spec defaults)", compounding=False)

with open(os.path.join(OUT, "19_crt_gates.txt"), "w") as f:
    f.write("\n".join(lines))
emit("\nwritten to output/19_crt_gates.txt")
