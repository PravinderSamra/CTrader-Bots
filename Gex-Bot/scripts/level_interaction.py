#!/usr/bin/env python3
"""
How does price actually interact with the gamma walls?

"Respect rate" is a thin description: it collapses an interaction into one
binary and needs ~100 events a cell before it says anything. This asks the
question four other ways, two of which are well-powered on the archive we
already have because they use every sample rather than only touch events.

  1. LEVEL STABILITY -- how far does each wall move during a session? The
     vendor documents open interest as recomputed once near the open and fixed
     thereafter, while volume moves all day. That is checkable, and it decides
     which levels are worth drawing on a chart and leaving there.

  2. MAGNET OR REPELLENT -- does price spend more time near a real wall than
     near an arbitrary nearby price? Uses every sample, with a placebo control:
     the same wall displaced by a few offsets. If walls attract, time-near-real
     exceeds time-near-placebo; if they repel, the reverse.

  3. REACH -- how often does price get to each wall at all during a session?
     A level price never visits cannot be traded, however well it "works".

  4. WHAT HAPPENS ON CONTACT -- direction, and separately the SIZE of the
     forward move against the session's own baseline. Size is a continuous
     outcome, so it extracts more from the same handful of touches than a
     win/lose flag does.

Usage:
    python3 level_interaction.py --sessions /tmp/sessions.json
"""

from __future__ import annotations

import argparse
import json
import random
import statistics
from collections import defaultdict

WALLS = [("pv", "volume call"), ("nv", "volume put"),
         ("po", "OI call"), ("no", "OI put")]


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


def stability(series, field):
    """Distinct values a wall takes, and how far it travels, in a session."""
    vals = [r[field] for r in series if r.get(field, 0) > 0]
    if not vals: return None
    moves = sum(1 for a, b in zip(vals, vals[1:]) if a != b)
    return {"distinct": len(set(vals)), "moves": moves,
            "span": max(vals) - min(vals),
            "first": vals[0], "last": vals[-1]}


def time_near(series, field, tol, offset=0.0):
    """Fraction of session samples within `tol` of the wall (optionally moved)."""
    n = near = 0
    for r in series:
        w = r.get(field, 0)
        if not w or w <= 0: continue
        n += 1
        if abs(r["spot"] - (w + offset)) <= tol: near += 1
    return (near / n) if n else None


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sessions", default="/tmp/sessions.json")
    ap.add_argument("--ticker", default="NQ_NDX")
    ap.add_argument("--tol-pct", type=float, default=2.0,
                    help="touch band as %% of the session's range")
    ap.add_argument("--horizon", type=float, default=15.0)
    ap.add_argument("--cooldown", type=float, default=15.0)
    args = ap.parse_args()

    sessions = [s for s in json.load(open(args.sessions))
                if s["ticker"] == args.ticker]
    sessions.sort(key=lambda s: s["date"])
    horizon_s, cooldown_s = args.horizon * 60, args.cooldown * 60
    rng = random.Random(7)

    print(f"{args.ticker}: {len(sessions)} sessions, "
          f"{sessions[0]['date']} to {sessions[-1]['date']}")

    # ── 1. stability ────────────────────────────────────────────────────
    print(f"\n{'='*70}\n1. LEVEL STABILITY — how much does each wall move intraday?\n{'='*70}")
    print(f"  {'wall':<12} {'median distinct values':>22} {'median span (pts)':>19}")
    for field, name in WALLS:
        rows = [stability(sorted(s["series"], key=lambda r: r["t"]), field)
                for s in sessions]
        rows = [r for r in rows if r]
        if not rows: continue
        print(f"  {name:<12} {statistics.median(r['distinct'] for r in rows):>22.0f}"
              f" {statistics.median(r['span'] for r in rows):>19.1f}")

    # ── 2. magnet or repellent ──────────────────────────────────────────
    print(f"\n{'='*70}\n2. MAGNET OR REPELLENT — time spent near the wall vs a placebo\n{'='*70}")
    print(f"  {'wall':<12} {'near real':>11} {'near placebo':>14} {'ratio':>8}")
    for field, name in WALLS:
        real, plac = [], []
        for s in sessions:
            series = sorted(s["series"], key=lambda r: r["t"])
            tol = (s["high"] - s["low"]) * args.tol_pct / 100
            rv = time_near(series, field, tol)
            if rv is None: continue
            real.append(rv)
            # Placebo: the same wall displaced by +/-2..6 tolerance widths.
            offs = [tol * k for k in (-6, -4, -2, 2, 4, 6)]
            pv = [time_near(series, field, tol, o) for o in offs]
            pv = [x for x in pv if x is not None]
            if pv: plac.append(statistics.fmean(pv))
        if not real or not plac: continue
        r, p = statistics.fmean(real), statistics.fmean(plac)
        print(f"  {name:<12} {100*r:>10.1f}% {100*p:>13.1f}% {r/p if p else 0:>8.2f}")

    # ── 3. reach ────────────────────────────────────────────────────────
    print(f"\n{'='*70}\n3. REACH — sessions in which price came within the band at all\n{'='*70}")
    for field, name in WALLS:
        hits = 0
        for s in sessions:
            series = sorted(s["series"], key=lambda r: r["t"])
            tol = (s["high"] - s["low"]) * args.tol_pct / 100
            if any(r.get(field, 0) > 0 and abs(r["spot"] - r[field]) <= tol
                   for r in series):
                hits += 1
        print(f"  {name:<12} {hits}/{len(sessions)} sessions")

    # ── 4. contact ──────────────────────────────────────────────────────
    print(f"\n{'='*70}\n4. ON CONTACT — direction, and size of the move vs baseline\n{'='*70}")
    print(f"  {'wall':<12} {'touches':>8} {'moved away':>11} "
          f"{'|move| after':>13} {'|move| baseline':>16}")
    for field, name in WALLS:
        n_ev = away = 0
        sizes, bases = [], []
        for s in sessions:
            series = sorted(s["series"], key=lambda r: r["t"])
            tol = (s["high"] - s["low"]) * args.tol_pct / 100
            # session baseline for |forward move|
            step = max(1, len(series) // 300)
            for i in range(0, len(series), step):
                a = spot_after(series, i, horizon_s)
                if a is not None: bases.append(abs(a - series[i]["spot"]))
            armed = 0
            for i, r in enumerate(series):
                w = r.get(field, 0)
                if not w or w <= 0 or r["t"] < armed: continue
                if abs(r["spot"] - w) > tol: continue
                a = spot_after(series, i, horizon_s)
                if a is None: continue
                # which side did it come from?
                side = 0
                for j in range(i - 1, -1, -1):
                    ww = series[j].get(field, 0)
                    if not ww or ww <= 0: continue
                    g = series[j]["spot"] - ww
                    if abs(g) > tol: side = 1 if g > 0 else -1; break
                n_ev += 1
                sizes.append(abs(a - r["spot"]))
                if side and (a - w) * side > 0 and abs(a - w) > tol: away += 1
                armed = r["t"] + cooldown_s
        if not n_ev: continue
        print(f"  {name:<12} {n_ev:>8} {100*away/n_ev:>10.0f}% "
              f"{statistics.median(sizes):>13.1f} {statistics.median(bases):>16.1f}")
    print("\n  'moved away' = price ended up back on the side it approached from,\n"
          "  clear of the band. Compare |move| columns: a level that halts price\n"
          "  should show a SMALLER forward move than the session's baseline.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
