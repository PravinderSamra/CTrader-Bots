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
import math
import statistics
from collections import defaultdict

# C1-C3 / P1-P3 as the platform ranks them, for both readings, plus zero
# gamma. Sessions archived before 2026-09-16 carry only the C1/P1 majors;
# rows without the ranked fields are skipped rather than treated as zero.
LEVELS = [(f"{t}{s}{i}", f"{n} {s.upper()}{i}")
          for t, n in (("v", "volume"), ("o", "OI"))
          for s in ("c", "p")
          for i in (1, 2, 3)] + [("zg", "zero gamma")]


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


def collect(sessions, args, placebo: float):
    """Run the simulation over every session, optionally on displaced lines."""
    window_s, cooldown_s = args.window * 60, args.cooldown * 60

    agg = defaultdict(lambda: {"n": 0, "BOUNCE": 0, "BREAK": 0, "CHOP": 0,
                               "mr": [], "retests": 0, "cont": []})
    for s in sessions:
        series = sorted(s["series"], key=lambda r: r["t"])
        if placebo:
            # Shift the level itself, keeping the price path untouched, so the
            # only thing that changes is whether the line means anything.
            series = [dict(r, **{f: (r[f] + placebo if r.get(f, 0) > 0 else 0)
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
    return agg


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    # Without this the collection pools 0DTE and 90-day sessions, which are
    # different levels entirely -- the 0DTE OI wall jumps hundreds of points a
    # session while the 90-day one drifts about ten.
    ap.add_argument("--scope", default="gex_zero",
                    choices=["gex_zero", "gex_full"])
    ap.add_argument("--tol", type=float, default=15.0, help="touch band, points")
    ap.add_argument("--stop", type=float, default=25.0, help="risk, points")
    ap.add_argument("--window", type=float, default=30.0, help="minutes forward")
    ap.add_argument("--cooldown", type=float, default=20.0, help="minutes")
    args = ap.parse_args()

    sessions = [s for s in json.load(open(args.sessions))
                if s["ticker"] == args.ticker
                and s.get("scope", "gex_zero") == args.scope]
    sessions.sort(key=lambda s: s["date"])
    if not sessions:
        print(f"no {args.ticker} {args.scope} sessions"); return 1
    ranked = [s for s in sessions
              if s["series"] and "vc1" in s["series"][0]]

    real = collect(sessions, args, 0.0)
    # The control is not optional. Every real number is printed beside what the
    # same test scores on lines displaced from the level, because a bounce rate
    # with no placebo measures the instrument, not the level.
    # Offsets scale with the instrument. Fixed point offsets displaced an SPX
    # level clean out of the day's 45-point range, so the control registered
    # almost no touches and reported "thin" -- the same mistake as a fixed
    # touch tolerance, one level up.
    rng = statistics.median([s["high"] - s["low"] for s in sessions])
    OFFSETS = tuple(round(rng * f) for f in
                    (-0.55, -0.45, -0.35, -0.25, 0.25, 0.35, 0.45, 0.55))
    plac = defaultdict(lambda: {"n": 0, "BOUNCE": 0, "BREAK": 0, "CHOP": 0,
                                "mr": [], "retests": 0, "cont": []})
    for off in OFFSETS:
        for k, v in collect(sessions, args, off).items():
            t = plac[k]
            for f in ("n", "BOUNCE", "BREAK", "CHOP", "retests"):
                t[f] += v[f]
            t["mr"] += v["mr"]; t["cont"] += v["cont"]

    R = args.stop
    print(f"{args.ticker} {args.scope}: {len(sessions)} sessions "
          f"({len(ranked)} with C1-C3)  |  band {args.tol:g}pts, "
          f"risk {R:g}pts, {args.window:g}min window")
    print(f"placebo: lines displaced {OFFSETS} pts "
          f"(0.25-0.55 x the {rng:.0f}pt median range)\n")

    print(f"  {'level':<14} {'touches':>8} {'bounce':>8} "
          f"{'placebo':>9} {'diff':>7} {'z':>6}")
    tot_r = tot_rb = tot_p = tot_pb = 0
    for _, name in LEVELS:
        a, b = real.get(name), plac.get(name)
        if not a or not a["n"]:
            continue
        rn, rb = a["n"], a["BOUNCE"]
        pn, pb = (b["n"], b["BOUNCE"]) if b else (0, 0)
        tot_r += rn; tot_rb += rb; tot_p += pn; tot_pb += pb
        if pn < 20:
            print(f"  {name:<14} {rn:>8} {100*rb/rn:>7.0f}% {'thin':>9} {'-':>7} {'-':>6}")
            continue
        d = 100*rb/rn - 100*pb/pn
        pp = (rb+pb)/(rn+pn)
        se = math.sqrt(pp*(1-pp)*(1/rn+1/pn))*100
        print(f"  {name:<14} {rn:>8} {100*rb/rn:>7.0f}% {100*pb/pn:>8.0f}% "
              f"{d:>+6.1f} {d/se if se else 0:>+6.2f}")
    if tot_r and tot_p:
        d = 100*tot_rb/tot_r - 100*tot_pb/tot_p
        pp = (tot_rb+tot_pb)/(tot_r+tot_p)
        se = math.sqrt(pp*(1-pp)*(1/tot_r+1/tot_p))*100
        print(f"  {'ALL POOLED':<14} {tot_r:>8} {100*tot_rb/tot_r:>7.0f}% "
              f"{100*tot_pb/tot_p:>8.0f}% {d:>+6.1f} {d/se if se else 0:>+6.2f}")

    print(f"\n  bounce = reached {R:g}pts back toward the approach side before "
          f"{R:g}pts through.\n  z beyond +/-1.96 is significant at 5%. "
          f"Anything less is the instrument,\n  not the level.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
