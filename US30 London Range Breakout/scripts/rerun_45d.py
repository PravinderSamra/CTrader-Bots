"""
Rerun of the 45-day US30 sample under the UPDATED rules:
  - range built up to 09:30 ET (NY open)
  - NO trading in the first 30 min (skip 09:30-10:00 ET)
  - from 10:00 ET, the FIRST HIGH-VOLUME 5m candle that breaks the range = entry
Compared against the original base rule and across volume-filter definitions.
"""
import os, sys
import pandas as pd
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import sessions, backtest as bt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INST = "US30"
SAMPLE_START = "2026-05-13"; SAMPLE_END = "2026-07-04"

df = sessions.load_m5(os.path.join(ROOT, "data", INST, f"{INST.lower()}_m5.csv"))
mask = (df["dt"] >= SAMPLE_START) & (df["dt"] < SAMPLE_END)
df = df[mask].reset_index(drop=True)
print(f"Sample: {df['dt'].min()} -> {df['dt'].max()}  ({df['ny_date'].nunique()} days, {len(df)} bars)\n")

def show(label, cfg):
    tdf, s = bt.run(df, cfg)
    print(f"--- {label} ---")
    if s.get("trades", 0) == 0:
        print("  no trades\n"); return None, s
    print(f"  trades={s['trades']}  win%={s['win_rate']*100:.0f}  exp={s['expectancy_R']:+.3f}R  "
          f"total={s['total_R']:+.1f}R  PF={s['profit_factor']}  avg_hold={s['avg_mins_held']}m  maxDD={s['max_dd_R']}R\n")
    return tdf, s

# 0) original base rule (reference)
show("OLD base: 03-08 London range, break from 09:30 ET, 50/100, no vol",
     bt.Config(instrument=INST, range_ref="london", lon_start=3, lon_end=8,
               bo_start=9.5, bo_end=11.0, stop_pts=50, rr=2.0, vol_method="none"))

# 1) new structure, no volume filter yet (isolate the effect of the 10:00 wait + 09:30 range)
new_base = dict(instrument=INST, range_ref="ny", lon_start=3.0, lon_end=9.5,
                bo_start=10.0, bo_end=12.0, stop_pts=50, rr=2.0)
show("NEW structure: range 03:00-09:30 ET, exec 10:00-12:00 ET, 50/100, NO vol filter",
     bt.Config(**new_base, vol_method="none"))

# 2) add the high-volume requirement, several definitions
for label, kw in [
    ("HIGH VOL: breakout candle >= 1.2x trailing-20", dict(vol_method="trailing", vol_mult=1.2)),
    ("HIGH VOL: breakout candle >= 1.5x trailing-20", dict(vol_method="trailing", vol_mult=1.5)),
    ("HIGH VOL: breakout candle >= 2.0x trailing-20", dict(vol_method="trailing", vol_mult=2.0)),
    ("HIGH VOL: breakout candle >= 1.5x pre-open(09:30-10:00)", dict(vol_method="premarket", vol_mult=1.5)),
    ("HIGH VOL: z-score >= 1.0 vs trailing-20", dict(vol_method="zscore", vol_z=1.0)),
]:
    show(label, bt.Config(**new_base, **kw))

# 3) quick RR sensitivity on the new structure + 1.5x trailing vol
print("== RR sensitivity (NEW structure + 1.5x trailing-vol, stop 50) ==")
for rr in [1.0, 2.0, 2.5, 3.0, 3.5]:
    cfg = bt.Config(**{**new_base, "rr": rr}, vol_method="trailing", vol_mult=1.5)
    _, s = bt.run(df, cfg)
    if s.get("trades", 0):
        print(f"  {rr}R: trades={s['trades']} win%={s['win_rate']*100:.0f} exp={s['expectancy_R']:+.3f}R total={s['total_R']:+.1f}R PF={s['profit_factor']}")
