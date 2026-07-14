#!/usr/bin/env python3
"""Parameter sweep: trigger distance x SL distance (TP fixed at 3RR), across
all 23 CPI events, to find the 'ideal setup' by historical expectancy."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from simulate_straddle import run_full_sim

TRIGGER_DISTS = [10, 15, 20, 25, 30, 35, 40]
SL_DISTS = [10, 15, 20, 25, 30]

for instrument in ("NAS100", "US500"):
    print(f"\n{'='*90}\n{instrument} -- expectancy (R) by trigger distance x SL distance, TP=3xSL\n{'='*90}")
    header = "SL\\Trig".ljust(8) + "".join(f"{t:>10}" for t in TRIGGER_DISTS)
    print(header)
    grid = {}
    for sl in SL_DISTS:
        row = f"{sl:<8}"
        for trig in TRIGGER_DISTS:
            res = run_full_sim(instrument, trig, sl, 3.0, verbose=False)
            grid[(trig, sl)] = res
            if res["n_resolved"] == 0:
                row += f"{'--':>10}"
            else:
                row += f"{res['expectancy']:>+9.2f}R"
        print(row)

    print(f"\n{instrument} -- win rate % by trigger distance x SL distance")
    print(header)
    for sl in SL_DISTS:
        row = f"{sl:<8}"
        for trig in TRIGGER_DISTS:
            res = grid[(trig, sl)]
            if res["n_resolved"] == 0:
                row += f"{'--':>10}"
            else:
                wr = 100 * (res["wins"] / res["n_resolved"])
                row += f"{wr:>9.0f}%"
        print(row)

    print(f"\n{instrument} -- resolved trade count (out of 23) by trigger distance x SL distance")
    print(header)
    for sl in SL_DISTS:
        row = f"{sl:<8}"
        for trig in TRIGGER_DISTS:
            res = grid[(trig, sl)]
            row += f"{res['n_resolved']:>10}"
        print(row)

    best = max(grid.items(), key=lambda kv: (kv[1]["expectancy"] if kv[1]["n_resolved"] >= 15 else -999))
    (trig, sl), res = best
    print(f"\nBest by expectancy (requiring >=15 resolved trades for reliability): "
          f"trigger={trig}pts, SL={sl}pts, TP={sl*3}pts -> {res['expectancy']:+.2f}R/trade, "
          f"{100*res['wins']/res['n_resolved']:.0f}% win rate, n={res['n_resolved']}")
