#!/usr/bin/env python3
"""
When price reaches a gamma level, does it bounce or break — and is either tradeable?

This asks the question as a trade rather than as a statistic. For every touch
it simulates BOTH plans with a fixed stop and measures what actually happened,
so the output is win rates at 1R/2R/3R rather than a "respect rate" that says
nothing about whether you would have made money.

  MEAN REVERSION: enter at the level, stop `--stop` points BEYOND it (the side
    price is heading), target measured in multiples of that risk. Resolves as a
    stop-out or as the best multiple reached first.

  CONTINUATION: only armed once price has broken `--stop` points through the
    level. Entry on the RETEST (price returning to the level), stop back on the
    far side. This is the break-and-retest plan, and it is only counted when a
    retest actually occurs — breaks that never come back are reported
    separately, because you could not have taken them this way.

Every touch is also classified BOUNCE / BREAK / CHOP on what happened first,
which is the thing to watch for live.

Approach side decides everything: a level met from below is resistance, met
from above it is support. Nothing here assumes a call wall means "down".

Usage:
    python3 level_playbook.py --sessions /tmp/sessions.json --stop 15
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict

LEVELS = [("pv", "volume call"), ("nv", "volume put"),
          ("po", "OI call"), ("no", "OI put"), ("zg", "zero gamma")]


def classify(series, i, field, tol, stop, window_s):
    """What happened after this touch. Returns a dict or None."""
    L = series[i].get(field, 0)
    if not L or L <= 0:
        return None
    # Which side did price approach from? +1 = from above, -1 = from below.
    side = 0
    for j in range(i - 1, -1, -1):
        w = series[j].get(field, 0)
        if not w or w <= 0:
            continue
        g = series[j]["spot"] - w
        if abs(g) > tol:
            side = 1 if g > 0 else -1
            break
    if not side:
        return None

    end_t = series[i]["t"] + window_s
    # Mean reversion: we are fading back toward the approach side.
    # Stop sits `stop` points through the level.
    mr_stop = L - side * stop
    mr_mfe = 0.0          # best favourable excursion, in points
    mr_done = False
    outcome = None        # BOUNCE / BREAK / CHOP, whichever happens first

    broke_at = None
    retest_result = None

    for k in range(i, len(series)):
        r = series[k]
        if r["t"] > end_t:
            break
        d = (r["spot"] - L) * side      # >0 means on the approach side

        if not mr_done:
            if d <= -stop:              # stopped out of the fade
                mr_done = True
                mr_mfe = max(mr_mfe, 0.0)
            else:
                mr_mfe = max(mr_mfe, d)

        if outcome is None:
            if d <= -stop:
                outcome = "BREAK"
                broke_at = k
            elif d >= stop:
                outcome = "BOUNCE"

        # Continuation: after a break, wait for price to come back to the level.
        if broke_at is not None and retest_result is None and k > broke_at:
            if abs(r["spot"] - L) <= tol:
                # Retest reached. Enter in the break direction, stop back
                # through the level by `stop`.
                cont_mfe = 0.0
                for m in range(k, len(series)):
                    rr = series[m]
                    if rr["t"] > end_t:
                        break
                    dd = (L - rr["spot"]) * side   # >0 = break direction
                    if dd <= -stop:
                        break
                    cont_mfe = max(cont_mfe, dd)
                retest_result = cont_mfe
    if outcome is None:
        outcome = "CHOP"
    return {"outcome": outcome, "mr_mfe": mr_mfe,
            "broke": broke_at is not None,
            "retest_mfe": retest_result}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    ap.add_argument("--tol", type=float, default=10.0, help="touch band, points")
    ap.add_argument("--stop", type=float, default=15.0, help="risk, points")
    ap.add_argument("--window", type=float, default=30.0, help="minutes forward")
    ap.add_argument("--cooldown", type=float, default=20.0, help="minutes")
    ap.add_argument("--placebo", type=float, default=0.0,
                    help="displace every level by this many points before "
                         "testing. The control: if a fake level scores like a "
                         "real one, the level is not what produced the score.")
    args = ap.parse_args()

    sessions = [s for s in json.load(open(args.sessions))
                if s["ticker"] == args.ticker]
    sessions.sort(key=lambda s: s["date"])
    window_s, cooldown_s = args.window * 60, args.cooldown * 60

    agg = defaultdict(lambda: {"n": 0, "BOUNCE": 0, "BREAK": 0, "CHOP": 0,
                               "mr": [], "retests": 0, "cont": []})
    for s in sessions:
        series = sorted(s["series"], key=lambda r: r["t"])
        if args.placebo:
            # Shift the level itself, keeping the price path untouched, so the
            # only thing that changes is whether the line means anything.
            series = [dict(r, **{f: (r[f] + args.placebo if r.get(f, 0) > 0 else 0)
                                 for f, _ in LEVELS}) for r in series]
        for field, name in LEVELS:
            armed = 0
            for i, r in enumerate(series):
                L = r.get(field, 0)
                if not L or L <= 0 or r["t"] < armed:
                    continue
                if abs(r["spot"] - L) > args.tol:
                    continue
                res = classify(series, i, field, args.tol, args.stop, window_s)
                if not res:
                    continue
                a = agg[name]
                a["n"] += 1
                a[res["outcome"]] += 1
                a["mr"].append(res["mr_mfe"])
                if res["retest_mfe"] is not None:
                    a["retests"] += 1
                    a["cont"].append(res["retest_mfe"])
                armed = r["t"] + cooldown_s

    R = args.stop
    print(f"{args.ticker}: {len(sessions)} sessions  |  touch band {args.tol:g}pts, "
          f"risk {R:g}pts, {args.window:g}min window\n")

    print("WHAT HAPPENS FIRST")
    print(f"  {'level':<13} {'touches':>8} {'bounce':>8} {'break':>7} {'chop':>7}")
    for _, name in LEVELS:
        a = agg[name]
        if not a["n"]:
            continue
        n = a["n"]
        print(f"  {name:<13} {n:>8} {100*a['BOUNCE']/n:>7.0f}% "
              f"{100*a['BREAK']/n:>6.0f}% {100*a['CHOP']/n:>6.0f}%")

    print(f"\nMEAN REVERSION — fade at the level, {R:g}pt stop through it")
    print(f"  {'level':<13} {'trades':>7} {'hit 1R':>8} {'hit 2R':>8} {'hit 3R':>8}")
    for _, name in LEVELS:
        a = agg[name]
        if not a["mr"]:
            continue
        m = a["mr"]
        f = lambda k: 100 * sum(1 for x in m if x >= k * R) / len(m)
        print(f"  {name:<13} {len(m):>7} {f(1):>7.0f}% {f(2):>7.0f}% {f(3):>7.0f}%")

    print(f"\nCONTINUATION — break, then enter on the retest, {R:g}pt stop")
    print(f"  {'level':<13} {'breaks':>7} {'retested':>9} {'hit 1R':>8} {'hit 2R':>8}")
    for _, name in LEVELS:
        a = agg[name]
        if not a["BREAK"]:
            continue
        c = a["cont"]
        if not c:
            print(f"  {name:<13} {a['BREAK']:>7} {0:>9} {'-':>8} {'-':>8}")
            continue
        f = lambda k: 100 * sum(1 for x in c if x >= k * R) / len(c)
        print(f"  {name:<13} {a['BREAK']:>7} {len(c):>9} {f(1):>7.0f}% {f(2):>7.0f}%")

    print("\n  'hit 1R' = reached one multiple of risk in favour before the stop.\n"
          "  Not a strategy result: no costs, no slippage, best-case exit.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
