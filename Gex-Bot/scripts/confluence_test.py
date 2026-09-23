#!/usr/bin/env python3
"""
Does a level with other levels stacked on it behave differently?

The unconditioned test is finished: a gamma level scores what an arbitrary
horizontal line scores. The founders' own account says why that might be --
a node only matters when there is genuine size behind it, and much of what the
naive model ranks is matched flow that leaves nobody hedging.

Confluence is the cheapest observable proxy for that, and the one a trader
would actually use: when the volume ranking and the open-interest ranking
agree on a strike, or several ranked levels sit on top of each other, more of
the book is concentrated there.

PRE-SPECIFIED, to keep this honest. Two hypotheses, both reported whatever
they show:

  H1  Confluent touches (2+ ranked levels within the band) are respected more
      often than isolated ones.
  H2  The first touch of a level in a session is respected more often than
      later touches, the level having been "used up".

Both are measured against the same displaced-line placebo as the main test,
so a result has to beat an arbitrary line, not merely a coin.

Usage:
    python3 confluence_test.py --sessions /tmp/sessions.json --ticker NQ_NDX
"""

from __future__ import annotations

import argparse
import json
import math
import statistics

RANKED = [f"{t}{s}{i}" for t in ("v", "o") for s in ("c", "p") for i in (1, 2, 3)]


def side_of(series, i, L, tol):
    for j in range(i - 1, -1, -1):
        g = series[j]["spot"] - L
        if abs(g) > tol:
            return 1 if g > 0 else -1
    return 0


def outcome(series, i, L, side, stop, window_s):
    """True = bounced (stop points back) before breaking (stop points through)."""
    end = series[i]["t"] + window_s
    for k in range(i, len(series)):
        r = series[k]
        if r["t"] > end:
            return None
        d = (r["spot"] - L) * side
        if d >= stop: return True
        if d <= -stop: return False
    return None


def scan(sessions, tol, stop, window_s, cooldown_s, offset=0.0):
    """Every touch of every ranked level, tagged with confluence and ordinality."""
    events = []
    for s in sessions:
        series = sorted(s["series"], key=lambda r: r["t"])
        if not series or "vc1" not in series[0]:
            continue
        seen = {}
        for field in RANKED:
            armed = 0
            for i, r in enumerate(series):
                base = r.get(field, 0)
                if not base or base <= 0:
                    continue
                L = base + offset
                if abs(r["spot"] - L) > tol or r["t"] < armed:
                    continue
                side = side_of(series, i, L, tol)
                if not side:
                    continue
                res = outcome(series, i, L, side, stop, window_s)
                if res is None:
                    continue
                # how many OTHER ranked levels sit within the band of this one
                stack = sum(1 for f2 in RANKED if f2 != field
                            and r.get(f2, 0) > 0 and abs(r[f2] - base) <= tol)
                key = (s["date"], field)
                seen[key] = seen.get(key, 0) + 1
                events.append({"bounced": res, "stack": stack,
                               "first": seen[key] == 1})
                armed = r["t"] + cooldown_s
    return events


def rate(ev):
    return (100 * sum(e["bounced"] for e in ev) / len(ev)) if ev else 0.0


def z(a, b):
    if not a or not b: return 0.0
    na, nb = len(a), len(b)
    pa, pb = sum(e["bounced"] for e in a)/na, sum(e["bounced"] for e in b)/nb
    p = (pa*na + pb*nb) / (na + nb)
    se = math.sqrt(p*(1-p)*(1/na + 1/nb))
    return (pa - pb) / se if se else 0.0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    ap.add_argument("--scope", default="gex_zero")
    ap.add_argument("--tol", type=float, default=15.0)
    ap.add_argument("--stop", type=float, default=25.0)
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
    real = scan(sessions, args.tol, args.stop, w, c)
    rng = statistics.median([s["high"] - s["low"] for s in sessions])
    plac = []
    for f in (-0.55, -0.45, -0.35, -0.25, 0.25, 0.35, 0.45, 0.55):
        plac += scan(sessions, args.tol, args.stop, w, c, round(rng * f))

    print(f"{args.ticker} {args.scope}: {len(sessions)} sessions, "
          f"{len(real)} touches (placebo {len(plac)})")
    print(f"band {args.tol:g} / risk {args.stop:g} / {args.window:g}min\n")
    print(f"  {'group':<28} {'n':>6} {'bounce':>8} {'vs placebo':>11} {'z':>7}")

    def row(label, ev, ctrl):
        print(f"  {label:<28} {len(ev):>6} {rate(ev):>7.0f}% "
              f"{rate(ev)-rate(ctrl):>+10.1f} {z(ev, ctrl):>+7.2f}")

    row("ALL touches", real, plac)
    print()
    for lo, hi, label in ((0, 0, "H1  isolated (no stack)"),
                          (1, 1, "H1  1 other level stacked"),
                          (2, 99, "H1  2+ others stacked")):
        ev = [e for e in real if lo <= e["stack"] <= hi]
        ct = [e for e in plac if lo <= e["stack"] <= hi]
        if ev: row(label, ev, ct)
    print()
    row("H2  first touch of level", [e for e in real if e["first"]],
        [e for e in plac if e["first"]])
    row("H2  later touches", [e for e in real if not e["first"]],
        [e for e in plac if not e["first"]])
    print("\n  Both hypotheses were fixed before running. z beyond +/-1.96 is\n"
          "  significant at 5% for ONE test; six groups are shown, so the bar\n"
          "  for calling any of them real is nearer +/-2.6.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
