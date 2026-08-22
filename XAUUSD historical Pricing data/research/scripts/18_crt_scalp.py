"""CRT Gold Scalp — implementation of the supplied Backtest Specification v1.0.

Failed-breakout liquidity-sweep reversion. H4/H1 candle defines the dealing range;
sweep of a range extreme inside a killzone is the trigger; M1 refines entry.

CAUSALITY (spec 06): the engine walks M1 forward inside each range candle's trading
window and acts only on closed-bar information. The range candle R is the PREVIOUS
closed TF_R bar; its levels are active during the FOLLOWING TF_R period. The sweep
extreme, the return-inside close, and every exit are detected bar-by-bar.

TIME (spec 06): killzones are evaluated in Europe/London local time via tz_convert,
so BST/GMT is handled exactly rather than drifting an hour twice a year.

COSTS (spec 06): spread + commission + entry slippage, all per-oz, with a 2x stress
run. Market entries pay slippage; limit entries do not (but require a genuine
through-trade to fill).

ACCOUNT: $100,000, risking 1% of CURRENT equity per trade (compounding).
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")

m1, m5, m15, h1_unused, d1 = prep.load_all()

# ---------------------------------------------------------------- cost model
SPREAD = 0.30        # $/oz round trip
COMMISSION = 0.07    # $/oz round trip (~$7 per 100oz lot)
SLIPPAGE = 0.10      # $/oz adverse, market entries only
BASE_COST = SPREAD + COMMISSION          # 0.37 paid by every trade
MKT_COST = BASE_COST + SLIPPAGE          # 0.47 for market entries

ACCOUNT0 = 100_000.0
RISK_PCT = 0.01

lines = []
def emit(s=""):
    print(s)
    lines.append(s)


# ---------------------------------------------------------------- data prep
def atr_series(df, n=14):
    tr = np.maximum(df.high - df.low,
                    np.maximum((df.high - df.close.shift()).abs(),
                               (df.low - df.close.shift()).abs()))
    return tr.ewm(alpha=1 / n, adjust=False).mean()


M1 = m1.copy()
M1["atr"] = atr_series(M1)
lon = M1.index.tz_convert("Europe/London")
M1["lmin"] = lon.hour * 60 + lon.minute          # UK local minutes (DST-exact)
M1["date"] = M1.index.date

OHLC = {"open": "first", "high": "max", "low": "min", "close": "last"}
TF = {
    "H4": m1.resample("4h").agg(OHLC).dropna(),
    "H1": m1.resample("1h").agg(OHLC).dropna(),
}
for k in TF:
    TF[k]["atr"] = atr_series(TF[k])

KZ = {  # UK local minutes
    "LDN": (7 * 60, 10 * 60),
    "NY": (13 * 60 + 30, 16 * 60 + 30),
}

# numpy views for the hot loop
IDX = M1.index
O = M1.open.to_numpy(); H = M1.high.to_numpy()
L = M1.low.to_numpy(); C = M1.close.to_numpy()
A1 = M1.atr.to_numpy(); LMIN = M1.lmin.to_numpy()
N = len(M1)


def in_kz(lm, sessions):
    for s in sessions:
        a, b = KZ[s]
        if a <= lm < b:
            return True
    return False


DEFAULTS = dict(tf="H4", delta_k=0.10, W=15, confirm="A", entry="market",
                target="EQ_RH", sessions=("LDN", "NY"), rng_min=0.5,
                scale_pct=0.50, time_stop=120, be_after_t1=False,
                cost_mult=1.0, direction="fade")


def run(**kw):
    """Returns a trades DataFrame. Every field is causal."""
    p = {**DEFAULTS, **kw}
    tf = TF[p["tf"]]
    tf_bars = 240 if p["tf"] == "H4" else 60
    rows = []

    tf_idx = tf.index
    tf_hi = tf.high.to_numpy(); tf_lo = tf.low.to_numpy(); tf_atr = tf.atr.to_numpy()
    starts = IDX.searchsorted(tf_idx, side="left")

    for j in range(20, len(tf) - 1):
        RH, RL = tf_hi[j], tf_lo[j]
        RNG = RH - RL
        if RNG <= 0 or np.isnan(tf_atr[j]):
            continue
        if RNG < p["rng_min"] * tf_atr[j]:      # dead range -> skip (spec step 1)
            continue
        EQ = (RH + RL) / 2
        Q25 = RL + 0.25 * RNG
        Q75 = RL + 0.75 * RNG

        # trading window = the NEXT TF_R period
        w0 = starts[j + 1]
        w1 = min(w0 + tf_bars, N)
        if w0 >= N:
            break

        done = {1: False, -1: False}     # max one trade per R per direction
        armed = {1: None, -1: None}      # side -> dict(ext, ext_i, swing)

        i = w0
        while i < w1:
            lm = LMIN[i]
            live_kz = in_kz(lm, p["sessions"]) if p["sessions"] else True
            delta = max(0.05, p["delta_k"] * A1[i]) if not np.isnan(A1[i]) else 0.05

            for side in (1, -1):
                if done[side]:
                    continue
                st = armed[side]
                # ---- arm on killzone sweep (spec step 2) ----
                swept = (L[i] <= RL - delta) if side == 1 else (H[i] >= RH + delta)
                if swept and live_kz:
                    ext = L[i] if side == 1 else H[i]
                    if st is None or (side == 1 and ext < st["ext"]) or (side == -1 and ext > st["ext"]):
                        armed[side] = {"ext": ext, "ext_i": i, "swing": None}
                        st = armed[side]
                if st is None:
                    continue
                if i - st["ext_i"] > p["W"]:     # window expired
                    armed[side] = None
                    continue
                if i == st["ext_i"]:
                    continue

                # ---- confirm the failure (spec step 3) ----
                if p["confirm"] == "A":
                    ok = (C[i] > RL) if side == 1 else (C[i] < RH)
                else:  # Model B: market-structure shift vs swing formed during sweep
                    if st["swing"] is None:
                        # last M1 swing high(low) since the sweep extreme
                        seg = slice(st["ext_i"], i + 1)
                        st["swing"] = H[seg].max() if side == 1 else L[seg].min()
                    ok = (C[i] > st["swing"]) if side == 1 else (C[i] < st["swing"])
                    if not ok:
                        # keep the swing fresh as the sweep develops
                        seg = slice(st["ext_i"], i + 1)
                        st["swing"] = H[seg].max() if side == 1 else L[seg].min()
                if not ok:
                    continue

                # ---- entry (spec step 4) ----
                buf = 0.25 * A1[i] if not np.isnan(A1[i]) else 0.25
                stop = st["ext"] - buf if side == 1 else st["ext"] + buf
                cost = (MKT_COST if p["entry"] == "market" else BASE_COST) * p["cost_mult"]
                e_i, entry = None, None

                if p["entry"] == "market":
                    e_i, entry = i, C[i]
                else:
                    if p["entry"] == "limit_RL":
                        lvl = RL if side == 1 else RH
                    elif p["entry"] == "limit_Q25":
                        lvl = Q25 if side == 1 else Q75
                    else:  # fvg: displacement gap from the confirm bar
                        if i - 2 < 0:
                            continue
                        lvl = (H[i - 2] if side == 1 else L[i - 2])
                        if side == 1 and not (L[i] > H[i - 2]):
                            continue
                        if side == -1 and not (H[i] < L[i - 2]):
                            continue
                    # walk forward for a genuine through-trade fill
                    for k2 in range(i + 1, min(i + 1 + p["W"], w1)):
                        if side == 1 and L[k2] <= lvl:
                            e_i, entry = k2, lvl
                            break
                        if side == -1 and H[k2] >= lvl:
                            e_i, entry = k2, lvl
                            break
                        if side == 1 and L[k2] <= stop:
                            break
                        if side == -1 and H[k2] >= stop:
                            break
                    if e_i is None:
                        armed[side] = None
                        continue

                if p["direction"] == "continue":     # gate 2: trade the breakout instead
                    side_eff = -side
                    stop = entry + side * (abs(entry - stop))
                else:
                    side_eff = side

                risk = abs(entry - stop)
                if risk <= 0 or risk > 5 * (A1[i] if not np.isnan(A1[i]) else 1):
                    armed[side] = None
                    continue

                # ---- targets (spec step 6) ----
                if p["target"] == "EQ_RH":
                    t1 = EQ if side_eff == 1 else EQ
                    t2 = RH if side_eff == 1 else RL
                elif p["target"] == "Q75":
                    t1 = None
                    t2 = Q75 if side_eff == 1 else Q25
                else:  # RH
                    t1 = None
                    t2 = RH if side_eff == 1 else RL
                if t1 is not None and side_eff * (t1 - entry) <= 0:
                    t1 = None
                if side_eff * (t2 - entry) <= 0:
                    armed[side] = None
                    continue

                # ---- manage (spec step 7) ----
                filled_t1 = False
                realised = 0.0
                remaining = 1.0
                exit_i = None
                cur_stop = stop
                for k2 in range(e_i + 1, min(e_i + 1 + p["time_stop"], N)):
                    hit_stop = (L[k2] <= cur_stop) if side_eff == 1 else (H[k2] >= cur_stop)
                    if hit_stop:
                        realised += remaining * side_eff * (cur_stop - entry)
                        remaining = 0.0
                        exit_i = k2
                        break
                    if t1 is not None and not filled_t1:
                        hit1 = (H[k2] >= t1) if side_eff == 1 else (L[k2] <= t1)
                        if hit1:
                            realised += p["scale_pct"] * side_eff * (t1 - entry)
                            remaining -= p["scale_pct"]
                            filled_t1 = True
                            if p["be_after_t1"]:
                                cur_stop = entry
                    hit2 = (H[k2] >= t2) if side_eff == 1 else (L[k2] <= t2)
                    if hit2:
                        realised += remaining * side_eff * (t2 - entry)
                        remaining = 0.0
                        exit_i = k2
                        break
                if remaining > 0:
                    exit_i = min(e_i + p["time_stop"], N - 1)
                    realised += remaining * side_eff * (C[exit_i] - entry)

                pnl = realised - cost
                rows.append(dict(
                    t_entry=IDX[e_i], t_exit=IDX[exit_i], side=side_eff,
                    entry=entry, stop=stop, risk=risk, pnl=pnl, R=pnl / risk,
                    kz="LDN" if in_kz(LMIN[e_i], ("LDN",)) else "NY",
                    tf=p["tf"], rng=RNG,
                    dur=(exit_i - e_i), year=IDX[e_i].year))
                done[side] = True
                armed[side] = None
            i += 1
    return pd.DataFrame(rows)


def summarize(t, label, account=True):
    if len(t) == 0:
        emit(f"{label}: NO TRADES")
        return None
    t = t.sort_values("t_entry").reset_index(drop=True)
    wins = t[t.R > 0]; losses = t[t.R <= 0]
    pf = wins.R.sum() / abs(losses.R.sum()) if len(losses) and losses.R.sum() != 0 else np.inf
    eq = t.R.cumsum()
    dd = (eq - eq.cummax()).min()
    # longest losing run
    run = best = 0
    for r in t.R:
        run = run + 1 if r <= 0 else 0
        best = max(best, run)
    sharpe = t.R.mean() / t.R.std() * np.sqrt(len(t) / 5.0) if t.R.std() > 0 else np.nan
    downside = t.R[t.R < 0].std()
    sortino = t.R.mean() / downside * np.sqrt(len(t) / 5.0) if downside and downside > 0 else np.nan
    emit(f"\n--- {label} ---")
    emit(f"trades={len(t)}  win%={len(wins)/len(t)*100:.1f}  expectancy={t.R.mean():+.4f}R  "
         f"PF={pf:.2f}  avgWin={wins.R.mean() if len(wins) else 0:+.2f}R  "
         f"avgLoss={losses.R.mean() if len(losses) else 0:+.2f}R")
    emit(f"totR={t.R.sum():+.1f}  maxDD={dd:.1f}R  Sharpe~{sharpe:.2f}  Sortino~{sortino:.2f}  "
         f"longest losing run={best}  avg duration={t.dur.mean():.0f}min")
    if account:
        equity = ACCOUNT0
        curve = []
        for _, r in t.iterrows():
            risk_cash = equity * RISK_PCT
            oz = risk_cash / r.risk
            pnl_cash = oz * r.pnl
            equity += pnl_cash
            curve.append(dict(t=r.t_exit, pnl=pnl_cash, equity=equity))
        cv = pd.DataFrame(curve).set_index("t")
        emit(f"$100k @1% risk (compounding): final equity ${equity:,.0f}  "
             f"net P&L ${equity-ACCOUNT0:+,.0f}  return {(equity/ACCOUNT0-1)*100:+.1f}% over 5 yrs")
        peak = cv.equity.cummax()
        emit(f"  max equity drawdown: {((cv.equity - peak)/peak).min()*100:.1f}%")
        return cv
    return None


emit("=" * 78)
emit("CRT GOLD SCALP — BACKTEST vs SPECIFICATION v1.0")
emit("=" * 78)
emit(f"data: {IDX[0]} -> {IDX[-1]}  ({N:,} M1 bars)")
emit(f"costs: spread ${SPREAD} + commission ${COMMISSION} + slippage ${SLIPPAGE} "
     f"= ${MKT_COST}/oz market entries, ${BASE_COST}/oz limit entries")

base = run()
cv_base = summarize(base, "BASELINE (spec defaults: H4, δ=0.10ATR, W=15, confirm A, "
                          "market entry, EQ→RH, LDN+NY)")

emit("\nby year:")
emit(base.groupby("year").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                              totR=("R", "sum"), expectancy=("R", "mean")).round(3).to_string())
emit("\nby killzone:")
emit(base.groupby("kz").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                            expectancy=("R", "mean")).round(3).to_string())
emit("\nby side:")
emit(base.groupby("side").agg(n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
                              expectancy=("R", "mean")).round(3).to_string())

base.to_pickle(os.path.join(OUT, "_crt_base_trades.pkl"))

with open(os.path.join(OUT, "18_crt_scalp.txt"), "w") as f:
    f.write("\n".join(lines))
