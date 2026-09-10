#!/usr/bin/env python3
"""
Pool the archived sessions and ask whether price respects the gamma walls.

Single-session results were never going to answer this: at a usable tolerance
one day yields single-digit touches per wall. This walks every session in the
archive, pools the events, and reports each cell's count alongside its rate so
an eye-catching percentage on four events cannot be mistaken for a finding.

Three things it does that the single-session script did not:

  * **Pools across sessions**, per instrument.
  * **Scores both framings.** `directional` = price fell from a call wall or
    rose from a put wall. `away` = price returned the way it came, whichever
    wall it is. The sources disagree about which is claimed, so both are shown.
  * **Conditions on the window.** The strategy is explicitly a first-two-hours
    method; testing the whole session tests something nobody claims.

Every rate is quoted against that session's own baseline for the same horizon,
because on a day that fell all afternoon, "price was lower 15 minutes later"
is true of almost any moment.

Usage:
    python3 analyse_sessions.py --sessions /tmp/sessions.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
from collections import defaultdict

WALLS = [("pv", "volume", "call", -1), ("nv", "volume", "put", +1),
         ("po", "oi", "call", -1), ("no", "oi", "put", +1)]


def spot_after(series, i, horizon_s):
    target = series[i]["t"] + horizon_s
    if series[-1]["t"] < target:
        return None
    lo, hi = i, len(series) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if series[mid]["t"] < target: lo = mid + 1
        else: hi = mid
    return series[lo]["spot"]


def approach_side(series, i, field, tol):
    for j in range(i - 1, -1, -1):
        w = series[j].get(field)
        if not w or w <= 0: continue
        gap = series[j]["spot"] - w
        if abs(gap) > tol: return 1 if gap > 0 else -1
    return 0


def touches(series, field, want, tol, cooldown_s, horizon_s, window_s):
    """Discrete touch events. `window_s` limits how far into the session."""
    t0 = series[0]["t"]
    events, armed = [], 0
    for i, s in enumerate(series):
        if window_s and s["t"] - t0 > window_s: break
        w = s.get(field)
        if not w or w <= 0 or s["t"] < armed: continue
        if abs(s["spot"] - w) > tol: continue
        after = spot_after(series, i, horizon_s)
        if after is None: continue
        side = approach_side(series, i, field, tol)
        move = after - s["spot"]
        events.append({
            "directional": (move < 0) == (want < 0) and move != 0,
            "away": bool(side) and (after - w) * side > 0 and abs(after - w) > tol,
            "sided": bool(side),
        })
        armed = s["t"] + cooldown_s
    return events


def baseline(series, horizon_s, window_s):
    t0 = series[0]["t"]
    down = total = 0
    step = max(1, len(series) // 400)
    for i in range(0, len(series), step):
        if window_s and series[i]["t"] - t0 > window_s: break
        after = spot_after(series, i, horizon_s)
        if after is None: continue
        total += 1
        if after < series[i]["spot"]: down += 1
    return (100 * down / total if total else 0), total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--tol", type=float, default=10.0,
                    help="touch tolerance in POINTS; ignored if --tol-pct is set")
    ap.add_argument("--tol-pct", type=float, default=None,
                    help="touch tolerance as a %% of that session's own range. "
                         "Prefer this over --tol whenever more than one "
                         "instrument is in the archive.")
    ap.add_argument("--horizon", type=float, default=15.0)
    ap.add_argument("--cooldown", type=float, default=15.0)
    args = ap.parse_args()

    sessions = json.load(open(args.sessions))
    horizon_s, cooldown_s = args.horizon * 60, args.cooldown * 60

    by_ticker = defaultdict(list)
    for s in sessions:
        by_ticker[s["ticker"]].append(s)

    for window_name, window_s in (("whole session", 0), ("first 2 hours", 2 * 3600)):
        label = (f"{args.tol_pct:g}% of range" if args.tol_pct is not None
                 else f"{args.tol:g}pts")
        print(f"\n{'='*74}\n{window_name.upper()}   "
              f"tol {label}, outcome {args.horizon:g}min later\n{'='*74}")
        for ticker, group in sorted(by_ticker.items()):
            group.sort(key=lambda s: s["date"])
            base_rates = []
            pooled = defaultdict(lambda: {"n": 0, "dir": 0, "away": 0, "sided": 0})
            for s in group:
                series = sorted(s["series"], key=lambda r: r["t"])
                # A fixed point tolerance is not comparable across
                # instruments. 10 points is 4% of an NQ session's range and
                # 20-27% of an SPX one, so the same number asks a strict
                # question of one and a meaningless question of the other.
                tol = (args.tol if args.tol_pct is None
                       else (s["high"] - s["low"]) * args.tol_pct / 100)
                b, bn = baseline(series, horizon_s, window_s)
                if bn: base_rates.append(b)
                for field, reading, kind, want in WALLS:
                    ev = touches(series, field, want, tol,
                                 cooldown_s, horizon_s, window_s)
                    c = pooled[(reading, kind)]
                    c["n"] += len(ev)
                    c["dir"] += sum(e["directional"] for e in ev)
                    c["away"] += sum(e["away"] for e in ev)
                    c["sided"] += sum(e["sided"] for e in ev)
            avg_base = sum(base_rates) / len(base_rates) if base_rates else 0
            print(f"\n  {ticker}  ({len(group)} sessions)   "
                  f"baseline: price lower {avg_base:.0f}% of the time")
            print(f"    {'wall':<16} {'touches':>8} {'directional':>13} {'away':>10}")
            for (reading, kind), c in sorted(pooled.items()):
                if not c["n"]:
                    print(f"    {reading+' '+kind:<16} {0:>8}")
                    continue
                d = f"{100*c['dir']/c['n']:.0f}%"
                a = f"{100*c['away']/c['sided']:.0f}%" if c["sided"] else "-"
                print(f"    {reading+' '+kind:<16} {c['n']:>8} {d:>13} {a:>10}")
    print("\nEvery cell's touch count is shown because that is the binding "
          "constraint.\nA rate on fewer than ~30 events is not evidence of "
          "anything.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
