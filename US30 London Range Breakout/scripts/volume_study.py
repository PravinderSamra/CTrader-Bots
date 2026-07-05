"""
Volume investigation (cTrader tick volume).

1. Time-of-day tick-volume profile (Asia / London / pre-market / open / lunch).
2. For breakout candles of the base setup, relate volume (absolute + relative to
   trailing-20, pre-market, and z-score) to outcome (TP vs SL).
3. Find the volume threshold that best separates winners from losers, and quantify
   the win-rate / expectancy lift from a volume filter.

Note: cTrader volume is TICK volume (price-update count), not real contract volume.
"""
import os
import sys
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions
import backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")


def tod_profile(df):
    """Mean tick volume by NY-local hour with session labels."""
    g = df.groupby(df["ny"].dt.hour)["volume"].agg(["mean", "median", "std", "count"])
    g.index.name = "ny_hour"
    return g.round(1)


def outcome_by_volume(tdf, col):
    """Win-rate & expectancy by quintile of a volume metric."""
    d = tdf.dropna(subset=[col]).copy()
    if len(d) < 10:
        return pd.DataFrame()
    d["bucket"] = pd.qcut(d[col], 5, duplicates="drop")
    out = d.groupby("bucket", observed=True).agg(
        trades=("R", "size"),
        win_rate=("outcome", lambda s: (s == "TP").mean()),
        expectancy_R=("R", "mean"),
        total_R=("R", "sum"),
    ).round(3)
    return out


def threshold_scan(tdf, col):
    """Sweep a >= threshold on a volume metric; report filtered performance."""
    d = tdf.dropna(subset=[col])
    rows = []
    for q in np.arange(0.0, 0.91, 0.1):
        thr = d[col].quantile(q)
        sub = d[d[col] >= thr]
        if len(sub) < 15:
            continue
        rows.append({
            "metric": col, "min_pctile": round(q, 2), "threshold": round(float(thr), 3),
            "trades": len(sub), "kept_frac": round(len(sub) / len(d), 3),
            "win_rate": round((sub["outcome"] == "TP").mean(), 3),
            "expectancy_R": round(sub["R"].mean(), 3),
            "total_R": round(sub["R"].sum(), 2),
        })
    return pd.DataFrame(rows)


def run(inst):
    path = os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv")
    df = sessions.load_m5(path)
    prof = tod_profile(df)
    prof.to_csv(os.path.join(ANALYSIS, f"{inst}_volume_tod_profile.csv"))

    # base breakout set (no vol filter) with volume features attached
    cfg = bt.Config(instrument=inst, stop_pts=50, rr=2.0, vol_method="none")
    tdf, _ = bt.run(df, cfg)
    tdf.to_csv(os.path.join(ANALYSIS, f"{inst}_breakouts_with_volume.csv"), index=False)

    report = {}
    for col in ["bo_vol", "vol_trail_rel", "vol_pm_rel", "vol_z"]:
        q = outcome_by_volume(tdf, col)
        if len(q):
            q.to_csv(os.path.join(ANALYSIS, f"{inst}_outcome_by_{col}.csv"))
            report[col] = q
        t = threshold_scan(tdf, col)
        if len(t):
            t.to_csv(os.path.join(ANALYSIS, f"{inst}_threshold_{col}.csv"), index=False)
    print(f"\n===== {inst} volume study ({len(tdf)} breakouts) =====")
    print("\nTime-of-day tick-volume profile (NY hour):")
    print(prof.to_string())
    for col, q in report.items():
        print(f"\nOutcome by {col} quintile:")
        print(q.to_string())
        t = threshold_scan(tdf, col)
        if len(t):
            print(f"Threshold scan on {col} (best expectancy rows):")
            print(t.sort_values("expectancy_R", ascending=False).head(4).to_string(index=False))
    return tdf


if __name__ == "__main__":
    for inst in (sys.argv[1:] or ["US30", "NAS100"]):
        run(inst)
