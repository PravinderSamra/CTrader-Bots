"""Run the pre-registered US30 ORB unseen test with the study's own engine (screens/orb_engine.py).
Usage: us30_orb_unseen.py m5.csv out_prefix  (costs 0.01% a round trip subtracted per trade in R)"""
import sys, json
sys.path.insert(0, "/home/user/CTrader-Bots/Vanessa Algo Bots/research/screens")
sys.path.insert(0, "/home/user/CTrader-Bots/US30 London Range Breakout/scripts")
import orb_engine as bt, sessions
from collections import defaultdict
df = sessions.load_m5(sys.argv[1])
for name, sm, sp, rr in (("A", "atr", 2.0, 2.0), ("B", "pct", 75.0, 3.0)):
    kw = dict(stop_pts=sp) if sm == "pct" else dict(atr_mult=sp)
    cfg = bt.Config(instrument="US30", range_ref="ny", lon_start=8.0, lon_end=9.5, bo_start=10.0, bo_end=13.0,
                    stop_method=sm, rr=rr, vol_method="trailing", vol_mult=1.2, **kw)
    t, s = bt.run(df, cfg)
    t["Rnet"] = t["R"] - 0.0001 * t["entry"] / t["stop_dist"]
    daily = t.groupby(t["date"].astype(str))["Rnet"].sum().to_dict()
    json.dump(daily, open(f"{sys.argv[2]}_{name}.json", "w"))
    R = t["Rnet"]; g = R[R > 0].sum(); l = -R[R < 0].sum(); eq = R.cumsum(); dd = (eq.cummax() - eq).max()
    yr = t.groupby(t["date"].astype(str).str[:4])["Rnet"].sum()
    print(f"{name}: trades {len(t)} total {R.sum():+.1f}R PF {g/l:.2f} maxDD {dd:.1f}R | " + "  ".join(f"{y} {v:+.1f}" for y, v in yr.items()))
