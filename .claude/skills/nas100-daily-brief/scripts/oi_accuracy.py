#!/usr/bin/env python3
"""
oi_accuracy.py — grade yesterday's OI estimate against what the OCC published,
then refit the calibration.

This is the half that makes the estimator honest. intraday_oi.py guesses; this
records how wrong the guess was and moves k toward the truth.

TIMING MATTERS AND THE TOOL ENFORCES IT.
Open interest published on the morning of D+1 reflects clearing through D's
close, and it does not change again until D+2. So a snapshot taken on day D can
only be graded on D+1. Grade it on D+2 and the "actual" figure already contains
another session's trading, and every error is attributed to the wrong day.

    python3 oi_accuracy.py                 # grade every gradeable snapshot
    python3 oi_accuracy.py --fit           # ... and rewrite calibration.json
"""
import json, glob, os, sys
from collections import defaultdict
from datetime import datetime, timezone, timedelta

import cboe_gex as G
import intraday_oi as I

MIN_SAMPLE = 200          # contracts needed before a bucket's k is refitted
MAX_STEP = 0.15           # most k may move in one day


def _trading_days_between(a, b):
    """Weekday count. US holidays are handled by session_context elsewhere;
    a holiday simply makes a snapshot ungradeable and it is skipped."""
    n, d = 0, a
    while d < b:
        d += timedelta(days=1)
        if d.weekday() < 5:
            n += 1
    return n


def current_oi():
    raw = G._get(G.CBOE_OPT.format("_NDX"))
    return ({x["option"]: float(x.get("open_interest") or 0)
             for x in raw["data"]["options"]}, raw.get("timestamp"))


def grade(snap_path, oi_now):
    d = json.load(open(snap_path))
    snap_day = datetime.fromisoformat(d["snapshot_utc"]).date()
    today = datetime.now(timezone.utc).date()
    gap = _trading_days_between(snap_day, today)
    if gap != 1:
        return {"path": snap_path, "skipped":
                f"snapshot is {gap} trading day(s) old — gradeable only at 1"}
    rows, hits = [], 0
    for r in d["rows"]:
        now = oi_now.get(r["osi"])
        if now is None:
            continue                      # expired and cleared off the chain
        actual = now - r["oi_prev"]
        rows.append({**r, "dOI_actual": actual,
                     "err": r["dOI_est"] - actual,
                     "in_bounds": r["dOI_lo"] - 1 <= actual <= r["dOI_hi"] + 1})
        hits += 1
    if not rows:
        return {"path": snap_path, "skipped": "no contracts matched"}
    tot_est = sum(r["dOI_est"] for r in rows)
    tot_act = sum(r["dOI_actual"] for r in rows)
    tot_vol = sum(r["vol"] for r in rows)
    abs_err = sum(abs(r["err"]) for r in rows)
    net_move = sum(abs(r["dOI_actual"]) for r in rows) or 1
    return {
        "path": os.path.basename(snap_path), "snapshot_day": str(snap_day),
        "contracts": hits,
        "total_volume": round(tot_vol),
        "dOI_estimated": round(tot_est), "dOI_actual": round(tot_act),
        "net_error": round(tot_est - tot_act),
        "net_error_pct_of_move": round((tot_est - tot_act) / net_move * 100, 1),
        "mean_abs_error_per_contract": round(abs_err / hits, 1),
        "within_hard_bounds_pct": round(
            100 * sum(1 for r in rows if r["in_bounds"]) / hits, 1),
        "implied_k_overall": round(tot_act / tot_vol, 3) if tot_vol else None,
        "_rows": rows,
    }


def refit(graded, prior):
    """k per bucket = observed net dOI / observed volume, damped."""
    agg = defaultdict(lambda: [0.0, 0.0, 0])
    for g in graded:
        for r in g.get("_rows", []):
            a = agg[(r["dte_bucket"], r["money_bucket"])]
            a[0] += r["dOI_actual"]; a[1] += r["vol"]; a[2] += 1
    out, notes = {}, []
    for key, (dsum, vsum, n) in sorted(agg.items()):
        old = prior.get(key, I.PRIOR_K.get(key, 0.4))
        if n < MIN_SAMPLE or vsum <= 0:
            out["|".join(key)] = {"k": round(old, 3), "n": n, "status": "held (thin sample)"}
            continue
        fit = dsum / vsum
        # Damp the step. One day is one day, and a bucket that happened to see
        # a big roll should not swing the whole model.
        k = max(old - MAX_STEP, min(old + MAX_STEP, fit))
        k = max(-0.2, min(1.0, k))
        out["|".join(key)] = {"k": round(k, 3), "n": n,
                              "raw_fit": round(fit, 3), "prev": round(old, 3),
                              "status": "fitted"}
        if abs(k - old) > 0.05:
            notes.append(f"{key[0]}/{key[1]}: {old:.2f} -> {k:.2f} (raw {fit:.2f}, n={n})")
    return out, notes


def main():
    oi_now, asof = current_oi()
    snaps = sorted(glob.glob(os.path.join(I.SNAPS, "*.json")))
    if not snaps:
        print("no snapshots yet — run intraday_oi.py first"); return
    graded, skipped = [], []
    for p in snaps:
        g = grade(p, oi_now)
        (skipped if "skipped" in g else graded).append(g)

    print(f"OI ESTIMATE ACCURACY   (chain as of {asof})")
    print(f"  {len(graded)} gradeable snapshot(s), {len(skipped)} skipped\n")
    for g in graded:
        print(f"  {g['snapshot_day']}  {g['contracts']:,} contracts, "
              f"volume {g['total_volume']:,}")
        print(f"     estimated dOI {g['dOI_estimated']:+,}  vs  "
              f"actual {g['dOI_actual']:+,}   error {g['net_error']:+,} "
              f"({g['net_error_pct_of_move']:+.1f}% of the day's move)")
        print(f"     mean abs error {g['mean_abs_error_per_contract']} contracts · "
              f"within hard bounds {g['within_hard_bounds_pct']}% · "
              f"implied k {g['implied_k_overall']}")
    for s in skipped:
        print(f"  - {os.path.basename(s['path'])}: {s['skipped']}")

    if "--fit" in sys.argv and graded:
        prior, _ = I.load_k()
        buckets, notes = refit(graded, prior)
        doc = {"updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
               "graded_days": [g["snapshot_day"] for g in graded],
               "min_sample": MIN_SAMPLE, "max_step": MAX_STEP,
               "buckets": buckets}
        json.dump(doc, open(os.path.join(I.ROOT, "calibration.json"), "w"), indent=1)
        print("\n  calibration.json rewritten")
        for n in notes:
            print(f"     {n}")
        if not notes:
            print("     no bucket moved more than 0.05")


if __name__ == "__main__":
    main()
