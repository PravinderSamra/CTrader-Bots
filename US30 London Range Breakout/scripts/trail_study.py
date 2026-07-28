"""
Stop-loss management study. On the preferred config per instrument, across RR
targets 2.0/2.5/3.0/3.5, compare stop schemes:
  static      : initial -1R stop, no movement
  be1         : move to breakeven once +1R reached
  step S      : ratchet ladder — at k*S of favourable R, stop -> (k-1)*S
Fine step grid finds the optimum increment ("curve fit"). All $ net of dealing
spread. Produces trail_consolidated.json for the dashboard + a summary table.

Trade sim uses the engine's pessimistic intrabar rule (see backtest.simulate_trade).
"""
import os, sys, json
import pandas as pd, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions, backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "analysis", "trail")
os.makedirs(OUT, exist_ok=True)
RISK = 100.0
RRS = [2.0, 2.5, 3.0, 3.5]
SPREAD = {"US30": 2.0, "NAS100": 1.5}
BEST = {
    "US30":   dict(range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0,
                   stop_method="fixed", stop_pts=75, vol_method="trailing", vol_mult=1.2),
    "NAS100": dict(range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0,
                   stop_method="fixed", stop_pts=40, vol_method="trailing", vol_mult=1.2),
}
# schemes shown in the dashboard (full $ breakdown)
SCHEMES = {
    "static":  dict(trail_mode="none"),
    "be1":     dict(trail_mode="be", be_trigger=1.0),
    "step1p0": dict(trail_mode="step", trail_step=1.0),
    "step1p5": dict(trail_mode="step", trail_step=1.5),
    "step2p0": dict(trail_mode="step", trail_step=2.0),
    "step2p5": dict(trail_mode="step", trail_step=2.5),
}
SCHEME_LABEL = {"static": "Static (no trail)", "be1": "Breakeven @1R",
                "step1p0": "Step 1.0R", "step1p5": "Step 1.5R",
                "step2p0": "Step 2.0R", "step2p5": "Step 2.5R"}
# fine grid for the optimum-increment curve
CURVE_STEPS = [0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]


def enrich(tdf, inst, stop_pts):
    tdf = tdf.copy()
    tdf["dt"] = pd.to_datetime(tdf["date"]); tdf = tdf.sort_values("dt").reset_index(drop=True)
    costR = SPREAD[inst] / stop_pts
    tdf["R_net"] = tdf["R"] - costR
    tdf["usd_gross"] = (tdf["R"] * RISK).round(2)
    tdf["usd_net"] = (tdf["R_net"] * RISK).round(2)
    tdf["year"] = tdf["dt"].dt.year
    tdf["month"] = tdf["dt"].dt.to_period("M").astype(str)
    iso = tdf["dt"].dt.isocalendar()
    tdf["week"] = iso["year"].astype(str) + "-W" + iso["week"].astype(str).str.zfill(2)
    tdf["week_start"] = (tdf["dt"] - pd.to_timedelta(tdf["dt"].dt.weekday, unit="D")).dt.date
    return tdf, costR


def streaks(signs):
    bw = bl = cw = cl = 0
    for s in signs:
        if s > 0: cw += 1; cl = 0
        elif s < 0: cl += 1; cw = 0
        else: cw = cl = 0
        bw = max(bw, cw); bl = max(bl, cl)
    return bw, bl


def agg(tdf, rcol, ucol, by):
    rows = []
    for key, g in tdf.groupby(by):
        rows.append({by: key if not isinstance(key, tuple) else key[0],
                     "week_start": str(g["week_start"].iloc[0]) if by == "week" else None,
                     "trades": len(g), "wins": int((g[rcol] > 0).sum()),
                     "losses": int((g[rcol] < 0).sum()), "usd": round(g[ucol].sum(), 2)})
    df = pd.DataFrame(rows).sort_values(by)
    if by == "year":
        w, l = [], []
        for _, g in tdf.groupby("year"):
            a, b = streaks(np.sign(g[rcol]).tolist()); w.append(a); l.append(b)
        df["longest_win_streak"] = w; df["longest_loss_streak"] = l
        df["win_pct"] = (df["wins"] / df["trades"] * 100).round(1)
        df["cum_usd"] = df["usd"].cumsum().round(2)
        df["account_end"] = (100000 + df["cum_usd"]).round(2)
    return df.to_dict(orient="records")


def headline(tdf, rcol, ucol):
    n = len(tdf); eq = tdf.sort_values("dt")[rcol].cumsum()
    dd = float((eq - eq.cummax()).min())
    wins = int((tdf[rcol] > 0).sum()); be = int((tdf[rcol] == 0).sum()); loss = int((tdf[rcol] < 0).sum())
    tot = float(tdf[ucol].sum())
    return {"trades": n, "total_usd": round(tot, 2), "exp_R": round(tdf[rcol].mean(), 4),
            "win_pct": round(wins / n * 100, 1), "be": be, "wins": wins, "losses": loss,
            "maxdd_usd": round(dd * RISK, 2), "recovery": round(tot / abs(dd * RISK), 2) if dd else None,
            "tp": int((tdf["outcome"] == "TP").sum()), "trail_exits": int((tdf["outcome"] == "TRAIL").sum())}


def scheme_block(df, inst, rr, extra):
    tdf, _ = bt.run(df, bt.Config(instrument=inst, rr=rr, **BEST[inst], **extra))
    tdf, costR = enrich(tdf, inst, BEST[inst]["stop_pts"])
    hg = headline(tdf, "R", "usd_gross"); hn = headline(tdf, "R_net", "usd_net")
    return {"cost_per_trade_usd": round(costR * RISK, 2),
            "gross": {**hg, "yearly": agg(tdf, "R", "usd_gross", "year"),
                      "monthly": agg(tdf, "R", "usd_gross", "month"),
                      "weekly": agg(tdf, "R", "usd_gross", "week")},
            "net": {**hn, "yearly": agg(tdf, "R_net", "usd_net", "year"),
                    "monthly": agg(tdf, "R_net", "usd_net", "month"),
                    "weekly": agg(tdf, "R_net", "usd_net", "week")}}


def main():
    consol = {"risk_per_trade": RISK, "rrs": RRS, "spread_pts": SPREAD,
              "schemes": SCHEME_LABEL, "config": {i: dict(BEST[i]) for i in BEST}, "data": {}}
    for inst in BEST:
        df = sessions.load_m5(os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv"))
        consol["data"][inst] = {}
        for rr in RRS:
            key = f"{rr:.1f}"; consol["data"][inst][key] = {"schemes": {}, "curve": []}
            print(f"\n=== {inst} {rr}R ===")
            for sk, ex in SCHEMES.items():
                b = scheme_block(df, inst, rr, ex)
                consol["data"][inst][key]["schemes"][sk] = b
                n = b["net"]
                print(f"  {SCHEME_LABEL[sk]:20} net ${n['total_usd']:>7,.0f}  exp {n['exp_R']:+.3f}  "
                      f"win {n['win_pct']:>4}%  BE {n['be']:>3}  maxDD ${n['maxdd_usd']:>7,.0f}  rec {n['recovery']}")
            # curve: fine step grid (net summary only)
            for s in CURVE_STEPS:
                tdf, _ = bt.run(df, bt.Config(instrument=inst, rr=rr, **BEST[inst],
                                              trail_mode="step", trail_step=s))
                tdf, _ = enrich(tdf, inst, BEST[inst]["stop_pts"])
                h = headline(tdf, "R_net", "usd_net")
                consol["data"][inst][key]["curve"].append(
                    {"step": s, "net_usd": h["total_usd"], "recovery": h["recovery"],
                     "exp_R": h["exp_R"], "win_pct": h["win_pct"], "maxdd_usd": h["maxdd_usd"]})
            # add static as the step=inf reference point for the curve
            st = consol["data"][inst][key]["schemes"]["static"]["net"]
            consol["data"][inst][key]["static_ref"] = {
                "net_usd": st["total_usd"], "recovery": st["recovery"], "maxdd_usd": st["maxdd_usd"]}
    json.dump(consol, open(os.path.join(OUT, "trail_consolidated.json"), "w"), default=str)
    sz = os.path.getsize(os.path.join(OUT, "trail_consolidated.json"))
    print(f"\ntrail_consolidated.json written ({sz/1e6:.2f} MB)")
    return consol


if __name__ == "__main__":
    main()
