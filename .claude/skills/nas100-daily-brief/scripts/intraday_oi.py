#!/usr/bin/env python3
"""
intraday_oi.py — estimate TODAY's open interest from today's volume.

RESEARCH ONLY. Nothing here feeds the brief. It writes snapshots and estimates
to research/, and oi_accuracy.py grades them against the real figures when the
OCC publishes the next morning.

--------------------------------------------------------------------------
The problem
--------------------------------------------------------------------------
Open interest is settled by the OCC after the close and published the next
morning. Every gamma level in the brief is therefore built on yesterday's
positioning. Volume is live, so today's activity IS observable — what is not
observable is whether each traded contract OPENED a position or CLOSED one.

That is the whole problem, and it is the same one the commercial vendors solve.
They train a classifier on it. We do not have training data yet, so we start
with something more honest and let it earn its way up.

--------------------------------------------------------------------------
The accounting, exactly
--------------------------------------------------------------------------
For a trade of size q, open interest moves by:

    both parties opening   -> +q
    both parties closing   -> -q
    one opens, one closes  ->  0

So for a contract with previous open interest OI and today's volume V:

    dOI is bounded by  [ max(-V, -OI) , +V ]

Those bounds are FREE — they need no model and they are never wrong. When
V >> OI the lower bound is -OI, which is often a small number, so heavy volume
on a thin strike is nearly always position BUILDING. That single observation
does most of the useful work.

--------------------------------------------------------------------------
The estimator
--------------------------------------------------------------------------
Inside the bounds we apply a shrinkage factor:

    dOI_est = clamp( V * k(dte_bucket, moneyness_bucket), bounds )

`k` is the net opening rate: the share of volume that survives as new open
interest. k = 1 means every contract opened a fresh position on both sides;
k = 0 means the day's trading netted out.

k is NOT guessed and left alone. Each snapshot is graded the next morning
against the published figure, and CALIBRATION.md is refitted from the observed
(V, dOI) pairs. The priors below are starting values only, chosen to be
deliberately conservative — they will be wrong, and being wrong on the record
is the point.

    python3 intraday_oi.py            # snapshot + estimate, writes to research/
    python3 intraday_oi.py --json
"""
import json, os, sys
from collections import defaultdict
from datetime import datetime, timezone

import cboe_gex as G
import gex_levels as gl

HERE = os.path.dirname(os.path.abspath(__file__))


def _research_root():
    d = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
    for base, dirs, _f in os.walk(d):
        if base.endswith("NAS100 Daily Brief agent skill"):
            return os.path.join(base, "research", "live-walls")
    return os.path.join(d, "research", "live-walls")


ROOT = _research_root()
SNAPS = os.path.join(ROOT, "snapshots")

# Starting values for the net opening rate. Conservative on purpose.
#
# 0DTE is near zero by construction: those contracts expire tonight, so almost
# nothing they trade survives into tomorrow's open interest. That is not a
# modelling choice, it is the calendar.
PRIOR_K = {
    ("0dte", "atm"): 0.02, ("0dte", "near"): 0.02, ("0dte", "far"): 0.02,
    ("1-5d", "atm"): 0.35, ("1-5d", "near"): 0.40, ("1-5d", "far"): 0.45,
    ("6-20d", "atm"): 0.40, ("6-20d", "near"): 0.45, ("6-20d", "far"): 0.50,
    ("21d+", "atm"): 0.45, ("21d+", "near"): 0.50, ("21d+", "far"): 0.55,
}


def dte_bucket(dte):
    return "0dte" if dte <= 0 else "1-5d" if dte <= 5 else "6-20d" if dte <= 20 else "21d+"


def money_bucket(strike, spot):
    r = abs(strike - spot) / spot
    return "atm" if r <= 0.01 else "near" if r <= 0.03 else "far"


def load_k():
    """Calibrated k if we have one, else the prior."""
    p = os.path.join(ROOT, "calibration.json")
    if os.path.exists(p):
        try:
            raw = json.load(open(p))
            return {tuple(k.split("|")): v["k"] for k, v in raw.get("buckets", {}).items()}, raw
        except Exception:
            pass
    return dict(PRIOR_K), None


def snapshot(max_dte=45, band_pct=0.06, min_activity=1):
    """Per-contract volume + prior open interest, near the money."""
    S, _ = G.spot_ndx()
    raw = G._get(G.CBOE_OPT.format("_NDX"))
    asof = raw.get("timestamp")
    today = datetime.now(timezone.utc).date()
    out = []
    for x in raw["data"]["options"]:
        try:
            exp, cp, k = G.parse_osi(x["option"])
        except Exception:
            continue
        dte = (exp - today).days
        if dte < 0 or dte > max_dte:
            continue
        if abs(k - S) / S > band_pct:
            continue
        oi = float(x.get("open_interest") or 0)
        vol = float(x.get("volume") or 0)
        if oi < min_activity and vol < min_activity:
            continue
        out.append({"osi": x["option"], "exp": str(exp), "dte": dte, "cp": cp,
                    "strike": k, "oi_prev": oi, "vol": vol,
                    "gamma": float(x.get("gamma") or 0)})
    return out, S, asof


def estimate(rows, spot, kmap=None):
    kmap = kmap or load_k()[0]
    est = []
    for r in rows:
        V, OI = r["vol"], r["oi_prev"]
        db, mb = dte_bucket(r["dte"]), money_bucket(r["strike"], spot)
        k = kmap.get((db, mb), PRIOR_K.get((db, mb), 0.4))
        lo, hi = max(-V, -OI), V
        raw = V * k
        d = max(lo, min(hi, raw))
        est.append({**r, "dte_bucket": db, "money_bucket": mb, "k": k,
                    "dOI_est": round(d, 1),
                    "dOI_lo": round(lo, 1), "dOI_hi": round(hi, 1),
                    "oi_est": round(OI + d, 1)})
    return est


def gex_shift(est, spot, bin_pts=50):
    """What the estimated positioning does to the per-strike gamma picture."""
    pub = defaultdict(float)
    new = defaultdict(float)
    for r in est:
        b = round(r["strike"] / bin_pts) * bin_pts
        g = r["gamma"] * 100 * spot * spot * 0.01
        sign = 1 if r["cp"] == "C" else -1
        pub[b] += sign * g * r["oi_prev"]
        new[b] += sign * g * r["oi_est"]
    keys = sorted(set(pub) | set(new))
    def wall(d, positive=True):
        c = {k: v for k, v in d.items() if (k > spot if positive else k < spot)}
        if not c:
            return None
        return (max(c, key=c.get) if positive else min(c, key=c.get))
    return {
        "published_call_wall": wall(pub, True), "estimated_call_wall": wall(new, True),
        "published_put_wall": wall(pub, False), "estimated_put_wall": wall(new, False),
        "published_net_$bn": round(sum(pub.values()) / 1e9, 3),
        "estimated_net_$bn": round(sum(new.values()) / 1e9, 3),
        "per_strike": [{"strike": k,
                        "published_$bn": round(pub.get(k, 0) / 1e9, 3),
                        "estimated_$bn": round(new.get(k, 0) / 1e9, 3)}
                       for k in keys],
    }


def run(write=True):
    rows, S, asof = snapshot()
    kmap, calib = load_k()
    est = estimate(rows, S, kmap)
    shift = gex_shift(est, S)
    now = datetime.now(timezone.utc)
    doc = {
        "schema": 1,
        "snapshot_utc": now.isoformat(timespec="seconds"),
        "cboe_asof": asof,
        "ndx_spot": round(S, 2),
        "calibration_source": ("fitted" if calib else "prior"),
        "calibration_updated": (calib or {}).get("updated"),
        "contracts": len(est),
        "total_volume": round(sum(r["vol"] for r in est)),
        "total_oi_prev": round(sum(r["oi_prev"] for r in est)),
        "total_dOI_est": round(sum(r["dOI_est"] for r in est)),
        "bounds": {"lo": round(sum(r["dOI_lo"] for r in est)),
                   "hi": round(sum(r["dOI_hi"] for r in est))},
        "wall_shift": shift,
        "rows": est,
    }
    if write:
        os.makedirs(SNAPS, exist_ok=True)
        p = os.path.join(SNAPS, now.strftime("%Y-%m-%d-%H%M") + ".json")
        json.dump(doc, open(p, "w"), indent=1)
        doc["_path"] = p
    return doc


if __name__ == "__main__":
    d = run()
    if "--json" in sys.argv:
        d.pop("rows", None)
        print(json.dumps(d, indent=1)); sys.exit(0)
    w = d["wall_shift"]
    print(f"INTRADAY OI ESTIMATE  {d['snapshot_utc']}  NDX {d['ndx_spot']}")
    print(f"  calibration: {d['calibration_source']}"
          f"{' (' + str(d['calibration_updated']) + ')' if d['calibration_updated'] else ''}")
    print(f"  {d['contracts']:,} contracts near the money")
    print(f"  prior OI {d['total_oi_prev']:,}  ·  today's volume {d['total_volume']:,}")
    print(f"  estimated net dOI {d['total_dOI_est']:+,} "
          f"(hard bounds {d['bounds']['lo']:+,} .. {d['bounds']['hi']:+,})")
    print(f"\n  net GEX  published {w['published_net_$bn']:+.2f}bn"
          f"  ->  estimated {w['estimated_net_$bn']:+.2f}bn")
    for side in ("call", "put"):
        a, b = w[f"published_{side}_wall"], w[f"estimated_{side}_wall"]
        move = f"moves {b-a:+,.0f}" if (a and b and a != b) else "unchanged"
        print(f"  {side} wall  published {a}  ->  estimated {b}   ({move})")
    print(f"\n  written: {d.get('_path')}")
