"""
Robustness / walk-forward check. ~100 configs were swept, so the top performer is
partly luck. Here we take a small set of candidate configs per instrument and
break each down by year to confirm the edge is stable, not period-driven.
Also persists trade logs + yearly tables for the final report and charts.
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions, backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")

VOL = dict(vol_method="trailing", vol_mult=1.2)

CANDIDATES = {
    "US30": {
        "base 50/2R":        bt.Config(instrument="US30", range_ref="ny", lon_start=3.0, lon_end=9.5, bo_start=10.0, bo_end=12.0, stop_method="fixed", stop_pts=50, rr=2.0, **VOL),
        "fixed75 / 3.0R":    bt.Config(instrument="US30", range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0, stop_method="fixed", stop_pts=75, rr=3.0, **VOL),
        "atr2.0 / 2.0R":     bt.Config(instrument="US30", range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0, stop_method="atr", atr_mult=2.0, rr=2.0, **VOL),
        "fixed60 / 2.5R":    bt.Config(instrument="US30", range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0, stop_method="fixed", stop_pts=60, rr=2.5, **VOL),
    },
    "NAS100": {
        "base 50/2R":        bt.Config(instrument="NAS100", range_ref="ny", lon_start=3.0, lon_end=9.5, bo_start=10.0, bo_end=12.0, stop_method="fixed", stop_pts=50, rr=2.0, **VOL),
        "fixed40 / 3.0R":    bt.Config(instrument="NAS100", range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0, stop_method="fixed", stop_pts=40, rr=3.0, **VOL),
        "fixed60 / 2.0R":    bt.Config(instrument="NAS100", range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0, stop_method="fixed", stop_pts=60, rr=2.0, **VOL),
        "fixed40 / 3.5R":    bt.Config(instrument="NAS100", range_ref="ny", lon_start=2.0, lon_end=9.5, bo_start=10.0, bo_end=11.0, stop_method="fixed", stop_pts=40, rr=3.5, **VOL),
    },
}


def yearly(tdf):
    tdf = tdf.copy()
    tdf["yr"] = pd.to_datetime(tdf["date"]).dt.year
    rows = []
    for yr, g in tdf.groupby("yr"):
        w = (g["outcome"] == "TP").sum()
        gl = -g[g["R"] < 0]["R"].sum()
        gw = g[g["R"] > 0]["R"].sum()
        rows.append({"year": yr, "trades": len(g), "win%": round((g["outcome"] == "TP").mean() * 100, 1),
                     "exp_R": round(g["R"].mean(), 3), "total_R": round(g["R"].sum(), 1),
                     "PF": round(gw / gl, 2) if gl else float("inf")})
    return pd.DataFrame(rows)


def main():
    dfs = {i: sessions.load_m5(os.path.join(ROOT, "data", i, f"{i.lower()}_m5.csv"))
           for i in CANDIDATES}
    all_rows = []
    for inst, cands in CANDIDATES.items():
        print(f"\n########## {inst} ##########")
        for label, cfg in cands.items():
            tdf, s = bt.run(dfs[inst], cfg)
            tag = f"{inst}__{label}".replace("/", "").replace(" ", "_").replace(".", "")
            tdf.to_csv(os.path.join(ANALYSIS, f"cand_{tag}.csv"), index=False)
            yt = yearly(tdf)
            print(f"\n--- {label} ---  n={s['trades']} win%={s['win_rate']*100:.0f} "
                  f"exp={s['expectancy_R']:+.3f}R total={s['total_R']:+.1f}R PF={s['profit_factor']} maxDD={s['max_dd_R']}R")
            print(yt.to_string(index=False))
            r = {"instrument": inst, "config": label, **{k: s[k] for k in
                 ["trades", "win_rate", "expectancy_R", "total_R", "profit_factor", "max_dd_R", "avg_mins_held", "long_share"]}}
            # consistency: fraction of years profitable
            r["years_profitable"] = f"{(yt['total_R'] > 0).sum()}/{len(yt)}"
            all_rows.append(r)
    summ = pd.DataFrame(all_rows)
    summ.to_csv(os.path.join(ANALYSIS, "candidate_summary.csv"), index=False)
    print("\n\n===== CANDIDATE SUMMARY (full 3yr) =====")
    print(summ.to_string(index=False))


if __name__ == "__main__":
    main()
