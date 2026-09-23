#!/usr/bin/env python3
"""
Pierce, reclaim, or break: what a level does in the shape traders describe.

The bounce/break test called anything that travelled `stop` points through a
level a break. That merges two opposite things: a genuine breakdown, and a
probe that trades through, fails, and closes back -- the stop-run that
precedes a reversal. A trader watching the level sees those as different
setups, so the test should too.

Every touch is followed to the end of the window and classified by what
actually happened, not by whichever threshold was hit first:

  HELD               never pierced beyond `--pierce`; finished on the
                     approach side
  PIERCED, RECLAIMED went through, came back, finished on the approach side
                     -- a false break
  BROKE              went through and finished on the far side
  BROKE, RETESTED    went through, returned to the level, and finished on the
                     far side -- the break-and-retest continuation

The quantities that matter are conditional, because that is how the level
would be traded:

  P(pierce)            does price go through at all
  P(reclaim | pierce)  having gone through, how often does it fail
  pierce depth         how far through it gets before failing

If a gamma level is doing anything, a probe through it should fail more often,
or more shallowly, than a probe through an arbitrary line. Everything is
reported against the same displaced-line placebo, scaled to the instrument.

Usage:
    python3 pierce_reclaim.py --sessions /tmp/sessions.json --ticker NQ_NDX
"""

from __future__ import annotations

import argparse
import json
import math
import statistics

RANKED = [f"{t}{s}{i}" for t in ("v", "o") for s in ("c", "p") for i in (1, 2, 3)]


def follow(series, i, L, side, pierce, reclaim, window_s):
    """Walk the window and describe what happened. None if it runs off the end."""
    end = series[i]["t"] + window_s
    if series[-1]["t"] < end:
        return None
    pierced = False
    depth = 0.0
    retested = False
    last_d = 0.0
    for k in range(i, len(series)):
        r = series[k]
        if r["t"] > end:
            break
        d = (r["spot"] - L) * side        # >0 = approach side, <0 = through
        last_d = d
        if d <= -pierce:
            pierced = True
            depth = max(depth, -d)
        elif pierced and abs(d) <= reclaim:
            retested = True
    if not pierced:
        return {"state": "HELD", "depth": 0.0, "pierced": False}
    if last_d >= reclaim:
        return {"state": "PIERCED_RECLAIMED", "depth": depth, "pierced": True}
    if retested:
        return {"state": "BROKE_RETESTED", "depth": depth, "pierced": True}
    return {"state": "BROKE", "depth": depth, "pierced": True}


def scan(sessions, tol, pierce, reclaim, window_s, cooldown_s, offset=0.0):
    out = []
    for s in sessions:
        series = sorted(s["series"], key=lambda r: r["t"])
        if not series or "vc1" not in series[0]:
            continue
        for field in RANKED:
            armed = 0
            for i, r in enumerate(series):
                base = r.get(field, 0)
                if not base or base <= 0:
                    continue
                L = base + offset
                if abs(r["spot"] - L) > tol or r["t"] < armed:
                    continue
                side = 0
                for j in range(i - 1, -1, -1):
                    g = series[j]["spot"] - L
                    if abs(g) > tol:
                        side = 1 if g > 0 else -1
                        break
                if not side:
                    continue
                res = follow(series, i, L, side, pierce, reclaim, window_s)
                if res:
                    out.append(res)
                    armed = r["t"] + cooldown_s
    return out


def z(k1, n1, k2, n2):
    if not n1 or not n2:
        return 0.0
    p1, p2 = k1/n1, k2/n2
    p = (k1+k2)/(n1+n2)
    se = math.sqrt(p*(1-p)*(1/n1+1/n2))
    return (p1-p2)/se if se else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    ap.add_argument("--scope", default="gex_zero")
    ap.add_argument("--tol", type=float, default=15.0)
    ap.add_argument("--pierce", type=float, default=10.0,
                    help="points beyond the level that counts as through it")
    ap.add_argument("--reclaim", type=float, default=10.0,
                    help="points back past the level that counts as reclaimed")
    ap.add_argument("--window", type=float, default=30.0)
    ap.add_argument("--cooldown", type=float, default=20.0)
    args = ap.parse_args()

    sessions = [s for s in json.load(open(args.sessions))
                if s["ticker"] == args.ticker
                and s.get("scope", "gex_zero") == args.scope
                and s["series"] and "vc1" in s["series"][0]]
    sessions.sort(key=lambda s: s["date"])
    if not sessions:
        print("no ranked sessions"); return 1

    w, c = args.window * 60, args.cooldown * 60
    real = scan(sessions, args.tol, args.pierce, args.reclaim, w, c)
    rng = statistics.median([s["high"] - s["low"] for s in sessions])
    plac = []
    for f in (-0.55, -0.45, -0.35, -0.25, 0.25, 0.35, 0.45, 0.55):
        plac += scan(sessions, args.tol, args.pierce, args.reclaim, w, c,
                     round(rng * f))

    print(f"{args.ticker} {args.scope}: {len(sessions)} sessions | "
          f"band {args.tol:g}, pierce {args.pierce:g}, reclaim {args.reclaim:g}, "
          f"{args.window:g}min")
    print(f"{len(real)} touches vs {len(plac)} placebo "
          f"(lines displaced 0.25-0.55 x {rng:.0f}pt range)\n")

    print(f"  {'outcome':<22} {'real':>12} {'placebo':>12}")
    for st in ("HELD", "PIERCED_RECLAIMED", "BROKE_RETESTED", "BROKE"):
        a = sum(1 for e in real if e["state"] == st)
        b = sum(1 for e in plac if e["state"] == st)
        print(f"  {st:<22} {100*a/len(real):>11.0f}% {100*b/len(plac):>11.0f}%")

    rp = sum(1 for e in real if e["pierced"])
    pp = sum(1 for e in plac if e["pierced"])
    rr = sum(1 for e in real if e["state"] == "PIERCED_RECLAIMED")
    pr = sum(1 for e in plac if e["state"] == "PIERCED_RECLAIMED")
    print(f"\n  {'measure':<26} {'real':>9} {'placebo':>9} {'z':>7}")
    print(f"  {'P(pierce)':<26} {100*rp/len(real):>8.0f}% "
          f"{100*pp/len(plac):>8.0f}% {z(rp,len(real),pp,len(plac)):>+7.2f}")
    print(f"  {'P(reclaim | pierced)':<26} {100*rr/rp if rp else 0:>8.0f}% "
          f"{100*pr/pp if pp else 0:>8.0f}% {z(rr,rp,pr,pp):>+7.2f}")
    rd = [e["depth"] for e in real if e["pierced"]]
    pd = [e["depth"] for e in plac if e["pierced"]]
    print(f"  {'median pierce depth':<26} {statistics.median(rd) if rd else 0:>8.1f} "
          f"{statistics.median(pd) if pd else 0:>8.1f}")
    print("\n  A level that matters should be pierced less, or reclaimed more\n"
          "  often after a pierce, than an arbitrary line. z beyond +/-1.96\n"
          "  is significant at 5%.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
