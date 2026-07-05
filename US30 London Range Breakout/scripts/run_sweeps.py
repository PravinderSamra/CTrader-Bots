"""
Staged parameter sweeps for the London Range Breakout study.

Staged (not full-grid) to limit overfitting:
  Stage 1  session structure : London window  x  breakout window   (base stop/rr, no vol)
  Stage 2  risk structure     : stop method/size  x  RR target
  Stage 3  volume filter       : (handled in volume_study.py)
Outputs CSV tables to ../analysis/ and per-config trade logs for the base cases.
"""
import os
import sys
import itertools
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions
import backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANALYSIS = os.path.join(ROOT, "analysis")
os.makedirs(ANALYSIS, exist_ok=True)

# London range candidate windows (LONDON local hours)
LON_WINDOWS = {
    "LR-A 03-08": (3.0, 8.0),
    "LR-B 06-09": (6.0, 9.0),
    "LR-C 08-13": (8.0, 13.0),
    "LR-D 00-08": (0.0, 8.0),
    "LR-E 02-0830": (2.0, 8.5),
    "LR-F 07-12": (7.0, 12.0),
}
# breakout scan windows (NY local hours) measured from the 09:30 open
BO_WINDOWS = {
    "first 5m": (9.5, 9.5834),
    "first 30m": (9.5, 10.0),
    "first 60m": (9.5, 10.5),
    "first 90m": (9.5, 11.0),
    "first 2h": (9.5, 11.5),
    "whole session": (9.5, 16.0),
}


def stage1(df, inst):
    rows = []
    for lw, (ls, le) in LON_WINDOWS.items():
        for bw, (bs, be) in BO_WINDOWS.items():
            cfg = bt.Config(instrument=inst, lon_start=ls, lon_end=le,
                            bo_start=bs, bo_end=be, stop_pts=50, rr=2.0,
                            vol_method="none")
            _, s = bt.run(df, cfg)
            if s.get("trades", 0) == 0:
                continue
            s["lon_window"] = lw
            s["bo_window"] = bw
            rows.append(s)
    out = pd.DataFrame(rows).sort_values("expectancy_R", ascending=False)
    out.to_csv(os.path.join(ANALYSIS, f"{inst}_stage1_session.csv"), index=False)
    return out


def stage2(df, inst, lw, bw):
    """Given a chosen London+breakout window, sweep stop method x RR."""
    ls, le = LON_WINDOWS[lw]
    bs, be = BO_WINDOWS[bw]
    rows = []
    rr_targets = [1.0, 1.5, 2.0, 2.5, 3.0, 3.5]
    # fixed stops
    for sp in [30, 40, 50, 60, 75, 100]:
        for rr in rr_targets:
            cfg = bt.Config(instrument=inst, lon_start=ls, lon_end=le, bo_start=bs, bo_end=be,
                            stop_method="fixed", stop_pts=sp, rr=rr, vol_method="none")
            _, s = bt.run(df, cfg)
            if s.get("trades", 0) == 0:
                continue
            s.update({"stop_method": "fixed", "stop_param": sp, "rr": rr})
            rows.append(s)
    # ATR stops
    for am in [1.0, 1.5, 2.0, 2.5]:
        for rr in rr_targets:
            cfg = bt.Config(instrument=inst, lon_start=ls, lon_end=le, bo_start=bs, bo_end=be,
                            stop_method="atr", atr_mult=am, rr=rr, vol_method="none")
            _, s = bt.run(df, cfg)
            if s.get("trades", 0) == 0:
                continue
            s.update({"stop_method": "atr", "stop_param": am, "rr": rr})
            rows.append(s)
    # structure (range edge) stop
    for rr in rr_targets:
        cfg = bt.Config(instrument=inst, lon_start=ls, lon_end=le, bo_start=bs, bo_end=be,
                        stop_method="range_edge", range_buffer_pts=5, rr=rr, vol_method="none")
        _, s = bt.run(df, cfg)
        if s.get("trades", 0) == 0:
            continue
        s.update({"stop_method": "range_edge", "stop_param": "edge+5", "rr": rr})
        rows.append(s)
    out = pd.DataFrame(rows).sort_values("expectancy_R", ascending=False)
    out.to_csv(os.path.join(ANALYSIS, f"{inst}_stage2_risk.csv"), index=False)
    return out


def base_case_log(df, inst):
    """Persist the literal-spec base-case trade log for the record."""
    cfg = bt.Config(instrument=inst, stop_pts=50, rr=2.0)
    tdf, s = bt.run(df, cfg)
    tdf.to_csv(os.path.join(ANALYSIS, f"{inst}_basecase_trades.csv"), index=False)
    return s


if __name__ == "__main__":
    insts = sys.argv[1:] or ["US30", "NAS100"]
    for inst in insts:
        path = os.path.join(ROOT, "data", inst, f"{inst.lower()}_m5.csv")
        if not os.path.exists(path):
            print("missing data:", path); continue
        df = sessions.load_m5(path)
        print(f"\n===== {inst}: {len(df)} bars, {df['ny_date'].nunique()} days, "
              f"{df['dt'].min()} -> {df['dt'].max()} =====")
        bs = base_case_log(df, inst)
        print("BASE CASE (50/100, 3-8 lon, first 90m):", bs)
        s1 = stage1(df, inst)
        print("\nStage1 top session structures:")
        print(s1[["lon_window", "bo_window", "trades", "win_rate", "expectancy_R", "total_R", "profit_factor"]].head(8).to_string(index=False))
        best = s1.iloc[0]
        s2 = stage2(df, inst, best["lon_window"], best["bo_window"])
        print(f"\nStage2 top risk structures (window={best['lon_window']} / {best['bo_window']}):")
        print(s2[["stop_method", "stop_param", "rr", "trades", "win_rate", "expectancy_R", "total_R", "profit_factor", "max_dd_R"]].head(12).to_string(index=False))
