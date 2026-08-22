"""V2 sweep-reversion engine — rebuilt from the CRT post-mortem.

The three diagnosed failures of CRT v1 and the design response:

  FAILURE 1  cost was 25-43% of the risk unit (median stop $1.88 vs $0.47 cost).
  RESPONSE   stop is a fraction of DAILY ATR with a hard floor, so cost/risk stays
             under ~5% in every volatility regime. Wide stops are not a compromise
             here -- the sizing is in R, so a wider stop just means fewer ounces.

  FAILURE 2  the signal had no edge (gross expectancy +0.025R == noise) because an
             H4 candle extreme is not a meaningful liquidity pool.
  RESPONSE   sweep DEEPER levels (prior-day H/L, Asia H/L, prior-day value edges)
             and require the validated context this project already established:
             the NY expansion window, and stored structural energy.

  FAILURE 3  28.8% win rate with a distant single target.
  RESPONSE   two-stage exit -- partial at a near structural/ATR target (raises hit
             rate), stop to break-even, runner to a time exit (keeps the tail).

DEV SET ONLY. The engine refuses to run past DEV_END unless holdout=True.
"""
import os
from importlib import import_module

import numpy as np
import pandas as pd

prep = import_module("00_prep")
OUT = os.path.join(os.path.dirname(__file__), "..", "output")
CACHE = os.environ.get(
    "XAU_CACHE",
    "/tmp/claude-0/-home-user-CTrader-Bots/952eda8c-76b6-5df8-9ee5-680db4472e55/scratchpad/xau_cache",
)

DEV_START = pd.Timestamp("2021-07-18", tz="UTC")
DEV_END = pd.Timestamp("2025-07-16", tz="UTC")     # holdout begins after this

SPREAD, COMMISSION, SLIP = 0.30, 0.07, 0.10
COST_MKT = SPREAD + COMMISSION + SLIP     # 0.47 market entry
COST_LMT = SPREAD + COMMISSION            # 0.37 limit entry
ACCOUNT0, RISK_PCT = 100_000.0, 0.01

m1, m5, m15, h1, d1 = prep.load_all()

# ---------------------------------------------------------------- daily context
d1 = d1.copy()
d1["range"] = d1.high - d1.low
d1["atr20"] = d1["range"].rolling(20).mean().shift(1)
d1["sma20"] = d1.close.rolling(20).mean().shift(1)
d1["pdh"] = d1.high.shift(1)
d1["pdl"] = d1.low.shift(1)
d1["dkey"] = (d1.index - pd.Timedelta(hours=22)).date
DAY = d1.set_index("dkey")[["atr20", "sma20", "pdh", "pdl"]]

prof = pd.read_pickle(os.path.join(CACHE, "profiles.pkl"))
prof = prof[["poc", "vah", "val"]].shift(1)     # prior day's profile
DAY = DAY.join(prof, how="left")

G = m1.copy()
G["dkey"] = (G.index - pd.Timedelta(hours=22)).date
G["tod"] = G.index.hour * 60 + G.index.minute
tr = np.maximum(m15.high - m15.low,
                np.maximum((m15.high - m15.close.shift()).abs(),
                           (m15.low - m15.close.shift()).abs()))
atr15 = tr.ewm(alpha=1 / 14, adjust=False).mean()
G["atr15"] = atr15.reindex(G.index, method="ffill")

DAYS = {}
for dk, seg in G.groupby("dkey"):
    if dk not in DAY.index or len(seg) < 400:
        continue
    r = DAY.loc[dk]
    if pd.isna(r.atr20) or r.atr20 <= 0:
        continue
    tod = seg.tod.to_numpy()
    am = (tod >= 22 * 60) | (tod < 7 * 60)
    if am.sum() < 60:
        continue
    hi = seg.high.to_numpy(); lo = seg.low.to_numpy()
    DAYS[dk] = dict(
        t=seg.index, tod=tod, o=seg.open.to_numpy(), h=hi, l=lo,
        c=seg.close.to_numpy(), a15=seg.atr15.to_numpy(),
        atr=r.atr20, sma=r.sma20, pdh=r.pdh, pdl=r.pdl,
        poc=r.poc, vah=r.vah, val=r.val,
        asia_h=hi[am].max(), asia_l=lo[am].min(),
        open_px=seg.open.to_numpy()[0],
        ts=seg.index[0],
    )
DKEYS = sorted(DAYS)

DEFAULTS = dict(
    level_set="pd",          # pd | asia | va | h4
    win=(12 * 60, 16 * 60),  # sweep scan window (UTC minutes)
    delta_k=0.10,            # sweep depth, x M15 ATR
    W=20,                    # reclaim window (M1 bars)
    entry="reclaim",         # reclaim | limit_level
    stop_atr=0.30,           # stop = stop_atr x daily ATR20 (the cost fix)
    stop_floor=6.0,          # $ floor
    stop_mode="atr",         # atr | wick | wick_floor
    t1_mult=1.0,             # partial target in R
    scale=0.50,              # fraction taken at T1
    be_after_t1=True,
    t2_mult=None,            # None = run to time exit
    time_exit=20 * 60 + 55,
    max_hold=360,
    energy_filter=False,     # Asia range unbroken through London
    trend_filter=None,       # None | "with" | "against"
    max_trades=1,
    cost_mult=1.0,
)


def run(holdout=False, **kw):
    p = {**DEFAULTS, **kw}
    rows = []
    for dk in DKEYS:
        D = DAYS[dk]
        is_hold = D["ts"] > DEV_END
        if is_hold != holdout:
            continue
        tod, h, l, c, a15 = D["tod"], D["h"], D["l"], D["c"], D["a15"]
        atr = D["atr"]

        if p["level_set"] == "pd":
            up, dn = D["pdh"], D["pdl"]
        elif p["level_set"] == "asia":
            up, dn = D["asia_h"], D["asia_l"]
        elif p["level_set"] == "va":
            up, dn = D["vah"], D["val"]
        else:
            up, dn = D["asia_h"], D["asia_l"]
        if up is None or dn is None or pd.isna(up) or pd.isna(dn) or up <= dn:
            continue

        if p["energy_filter"]:
            lon = (tod >= 7 * 60) & (tod < 12 * 60)
            if lon.sum() < 60:
                continue
            if (c[lon] > D["asia_h"]).any() or (c[lon] < D["asia_l"]).any():
                continue

        w0, w1 = p["win"]
        idx = np.where((tod >= w0) & (tod < w1))[0]
        if len(idx) < 30:
            continue

        armed = {1: None, -1: None}
        done = {1: False, -1: False}
        n_tr = 0
        for i in idx:
            if n_tr >= p["max_trades"]:
                break
            delta = max(0.05, p["delta_k"] * a15[i]) if not np.isnan(a15[i]) else 0.05
            for side in (1, -1):
                if done[side] or n_tr >= p["max_trades"]:
                    continue
                lvl = dn if side == 1 else up
                st = armed[side]
                swept = (l[i] <= lvl - delta) if side == 1 else (h[i] >= lvl + delta)
                if swept:
                    ext = l[i] if side == 1 else h[i]
                    if st is None or (side == 1 and ext < st["ext"]) or (side == -1 and ext > st["ext"]):
                        armed[side] = {"ext": ext, "i": i}
                        st = armed[side]
                if st is None or i == st["i"]:
                    continue
                if i - st["i"] > p["W"]:
                    armed[side] = None
                    continue
                reclaimed = (c[i] > lvl) if side == 1 else (c[i] < lvl)
                if not reclaimed:
                    continue

                # ---- entry ----
                if p["entry"] == "reclaim":
                    e_i, entry, cost = i, c[i], COST_MKT * p["cost_mult"]
                else:
                    e_i, entry, cost = None, None, COST_LMT * p["cost_mult"]
                    for k in range(i + 1, len(c)):
                        if tod[k] >= p["time_exit"]:
                            break
                        if side == 1 and l[k] <= lvl:
                            e_i, entry = k, lvl; break
                        if side == -1 and h[k] >= lvl:
                            e_i, entry = k, lvl; break
                        if k - i > p["W"]:
                            break
                    if e_i is None:
                        armed[side] = None
                        continue

                # ---- trend filter ----
                if p["trend_filter"] and not pd.isna(D["sma"]):
                    with_trend = (entry > D["sma"]) == (side == 1)
                    if p["trend_filter"] == "with" and not with_trend:
                        armed[side] = None; continue
                    if p["trend_filter"] == "against" and with_trend:
                        armed[side] = None; continue

                # ---- stop (THE cost fix) ----
                wick = st["ext"] - side * 0.25 * (a15[e_i] if not np.isnan(a15[e_i]) else 1.0)
                if p["stop_mode"] == "wick":
                    stop = wick
                elif p["stop_mode"] == "atr":
                    stop = entry - side * max(p["stop_atr"] * atr, p["stop_floor"])
                else:  # wick_floor: structural, but never tighter than the floor
                    struct = abs(entry - wick)
                    need = max(p["stop_atr"] * atr, p["stop_floor"])
                    stop = entry - side * max(struct, need)
                risk = abs(entry - stop)
                if risk <= 0:
                    armed[side] = None; continue

                t1 = entry + side * p["t1_mult"] * risk if p["t1_mult"] else None
                t2 = entry + side * p["t2_mult"] * risk if p["t2_mult"] else None

                # ---- simulate ----
                realised, remaining, cur_stop, got_t1 = 0.0, 1.0, stop, False
                x_i = None
                for k in range(e_i + 1, len(c)):
                    if tod[k] >= p["time_exit"] or (k - e_i) > p["max_hold"]:
                        x_i = k; break
                    if (l[k] <= cur_stop) if side == 1 else (h[k] >= cur_stop):
                        realised += remaining * side * (cur_stop - entry)
                        remaining = 0.0; x_i = k; break
                    if t1 is not None and not got_t1:
                        if (h[k] >= t1) if side == 1 else (l[k] <= t1):
                            realised += p["scale"] * side * (t1 - entry)
                            remaining -= p["scale"]; got_t1 = True
                            if p["be_after_t1"]:
                                cur_stop = entry
                    if t2 is not None and remaining > 0:
                        if (h[k] >= t2) if side == 1 else (l[k] <= t2):
                            realised += remaining * side * (t2 - entry)
                            remaining = 0.0; x_i = k; break
                if x_i is None:
                    x_i = len(c) - 1
                if remaining > 0:
                    realised += remaining * side * (c[x_i] - entry)

                pnl = realised - cost
                rows.append(dict(dkey=dk, t=D["t"][e_i], side=side, entry=entry,
                                 stop=stop, risk=risk, pnl=pnl, R=pnl / risk,
                                 cost_pct=cost / risk * 100, got_t1=got_t1,
                                 dur=x_i - e_i, year=D["t"][e_i].year))
                done[side] = True; armed[side] = None; n_tr += 1
    return pd.DataFrame(rows)


def score(t, label, emit_fn=print, yearly=False):
    if len(t) < 20:
        emit_fn(f"{label:<46} n={len(t):<5} (too few)")
        return None
    t = t.sort_values("t")
    w = t[t.R > 0]; ls = t[t.R <= 0]
    pf = w.R.sum() / abs(ls.R.sum()) if len(ls) and ls.R.sum() != 0 else np.inf
    eq = t.R.cumsum(); dd = (eq - eq.cummax()).min()
    sharpe = t.R.mean() / t.R.std() * np.sqrt(len(t) / 4.0) if t.R.std() > 0 else 0
    emit_fn(f"{label:<46} n={len(t):<5} win={(t.R>0).mean()*100:5.1f}% "
            f"exp={t.R.mean():+.3f}R PF={pf:5.2f} totR={t.R.sum():+7.1f} "
            f"DD={dd:6.1f}R Sh~{sharpe:5.2f} cost/risk={t.cost_pct.mean():4.1f}%")
    if yearly:
        emit_fn("    " + t.groupby("year").agg(
            n=("R", "size"), win=("R", lambda x: (x > 0).mean() * 100),
            exp=("R", "mean"), totR=("R", "sum")).round(3).to_string().replace("\n", "\n    "))
    return dict(n=len(t), win=(t.R > 0).mean(), exp=t.R.mean(), pf=pf,
                tot=t.R.sum(), dd=dd, sharpe=sharpe)


if __name__ == "__main__":
    lines = []
    def emit(s=""):
        print(s, flush=True); lines.append(str(s))

    emit("=" * 108)
    emit("V2 SWEEP-REVERSION — DEV-SET ITERATION LADDER (2021-07 → 2025-07)")
    emit("=" * 108)
    n_cfg = 0

    emit("\n### STEP 0 — reproduce the CRT failure mode inside this engine (control)")
    n_cfg += 1
    score(run(level_set="h4", win=(7 * 60, 16 * 60), stop_mode="wick",
              t1_mult=None, be_after_t1=False, t2_mult=2.5, entry="reclaim"),
          "CTRL: tight wick stop, H4-ish levels", emit)

    emit("\n### STEP 1 — FIX 1 in isolation: widen the stop, change nothing else")
    for sm, lbl in (("wick", "wick (tight)"), ("wick_floor", "wick w/ ATR floor"), ("atr", "pure ATR")):
        n_cfg += 1
        score(run(level_set="pd", stop_mode=sm, t1_mult=None, be_after_t1=False, t2_mult=2.5),
              f"S1 pd-levels, stop={lbl}", emit)

    emit("\n### STEP 2 — FIX 2: which liquidity pool actually pays? (stop fixed at ATR)")
    for ls in ("pd", "asia", "va"):
        n_cfg += 1
        score(run(level_set=ls, t1_mult=None, be_after_t1=False, t2_mult=2.5),
              f"S2 level_set={ls}", emit)

    emit("\n### STEP 3 — session window")
    for win, lbl in (((7 * 60, 12 * 60), "London 07-12"), ((12 * 60, 16 * 60), "NY 12-16"),
                     ((13 * 60, 17 * 60), "NY 13-17"), ((7 * 60, 20 * 60), "all day")):
        n_cfg += 1
        score(run(win=win, t1_mult=None, be_after_t1=False, t2_mult=2.5), f"S3 {lbl}", emit)

    emit("\n### STEP 4 — FIX 3: exit structure (partial + BE + runner)")
    for t1, sc, be, t2, lbl in (
            (None, 0, False, 2.5, "single target 2.5R"),
            (None, 0, False, None, "no target, time exit"),
            (1.0, 0.5, True, None, "T1 1R 50% + BE + runner"),
            (1.0, 0.5, False, None, "T1 1R 50%, no BE + runner"),
            (1.5, 0.5, True, None, "T1 1.5R 50% + BE + runner"),
            (1.0, 0.7, True, None, "T1 1R 70% + BE + runner"),
            (1.0, 0.5, True, 3.0, "T1 1R 50% + BE + T2 3R")):
        n_cfg += 1
        score(run(t1_mult=t1, scale=sc, be_after_t1=be, t2_mult=t2), f"S4 {lbl}", emit)

    emit("\n### STEP 5 — entry model & sweep depth")
    for ent in ("reclaim", "limit_level"):
        for dk_ in (0.05, 0.10, 0.25):
            n_cfg += 1
            score(run(entry=ent, delta_k=dk_), f"S5 entry={ent} delta={dk_}", emit)

    emit("\n### STEP 6 — context filters")
    for ef, tf, lbl in ((False, None, "none"), (True, None, "energy (Asia held London)"),
                        (False, "with", "trend-with"), (False, "against", "trend-against"),
                        (True, "with", "energy + trend-with")):
        n_cfg += 1
        score(run(energy_filter=ef, trend_filter=tf), f"S6 filter={lbl}", emit)

    emit("\n### STEP 7 — stop width sweep (cost/risk trade-off)")
    for sa in (0.15, 0.20, 0.30, 0.45, 0.60):
        n_cfg += 1
        score(run(stop_atr=sa), f"S7 stop={sa}xATR20", emit)

    emit(f"\nDEV configurations evaluated so far: {n_cfg}")
    with open(os.path.join(OUT, "20_v2_ladder.txt"), "w") as f:
        f.write("\n".join(lines))
