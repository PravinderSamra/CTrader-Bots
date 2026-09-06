#!/usr/bin/env python3
"""
Does price respect the VOLUME-derived gamma walls or the OPEN-INTEREST ones?

The two sources this project is built on disagree (see
../youtube-research/analysis/strategy-synthesis.md §5), and the two readings
routinely point at different strikes -- sometimes at opposite regimes. This
settles it against data rather than assertion.

Method -- "touch and reaction":

  1. Walk the session. A *touch* is spot coming within `--tol` points of a
     wall. Consecutive samples near the same wall are one event, not
     hundreds, so a `--cooldown` gates re-arming.
  2. After each touch, look `--horizon` minutes forward.
  3. A wall is *respected* if price moved away from it in the direction the
     wall implies: down from a call wall (resistance), up from a put wall
     (support).
  4. Compare respect rates between the volume walls and the OI walls.

The control matters as much as the test. On a trending day "price fell after
touching resistance" can be true simply because price fell all afternoon, so
the report also gives the unconditional base rate of down-moves over the same
horizon. A wall that only matches the drift is not evidence of anything.

Usage:
    python3 analyse_vol_vs_oi.py --zip /path/to/eod_report_NQ_NDX_DATE.zip
    python3 analyse_vol_vs_oi.py --zip ... --tol 5 --horizon 15 --json out.json
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import json
import statistics
import sys
import zipfile

WALLS = [
    # (field, reading, kind, direction price should go if respected)
    ("major_pos_vol", "volume", "call wall", -1),
    ("major_neg_vol", "volume", "put wall", +1),
    ("major_pos_oi", "open interest", "call wall", -1),
    ("major_neg_oi", "open interest", "put wall", +1),
]


def load_session(zip_path: str, scope: str = "gex_zero") -> list[dict]:
    z = zipfile.ZipFile(zip_path)
    names = [n for n in z.namelist() if scope in n and n.endswith(".json.gz")]
    if not names:
        raise SystemExit(f"no {scope} file in {zip_path}: {z.namelist()}")
    samples = json.loads(gzip.decompress(z.read(names[0])))
    samples.sort(key=lambda s: s["timestamp"])
    return samples


def spot_after(samples: list[dict], i: int, horizon_s: int) -> float | None:
    """Spot `horizon_s` seconds after sample i, or None if the session ends."""
    target = samples[i]["timestamp"] + horizon_s
    if samples[-1]["timestamp"] < target:
        return None
    lo, hi = i, len(samples) - 1
    while lo < hi:                       # first sample at or past target
        mid = (lo + hi) // 2
        if samples[mid]["timestamp"] < target:
            lo = mid + 1
        else:
            hi = mid
    return samples[lo]["spot"]


def approach_side(samples, i, field, tol):
    """Which side spot came from, walking back to before the touch.

    Returns +1 if spot was above the level, -1 if below, 0 if undetermined
    (the session started inside the tolerance band).
    """
    for j in range(i - 1, -1, -1):
        wall = samples[j].get(field)
        if not wall or wall <= 0:
            continue
        gap = samples[j]["spot"] - wall
        if abs(gap) > tol:
            return 1 if gap > 0 else -1
    return 0


def find_touches(samples, field, tol, cooldown_s, horizon_s, min_move):
    """Discrete touch events for one wall, with the forward outcome.

    Two verdicts are recorded per touch, because the two sources disagree
    about what a gamma level even predicts:

      * `respected_directional` -- price fell from a call wall, rose from a
        put wall. This is the reading the strategy videos imply and the one
        this script originally tested alone.
      * `respected_away` -- price moved back the way it came, whatever the
        wall's type. This is the vendor's own framing: "spot wants to move
        away from these levels", with support/resistance decided by which
        side spot is on rather than by whether the strike is a call or a put.

    They are not the same test. On a touch from the far side they are exact
    opposites, so scoring only the first marks a correct outcome as a failure
    roughly half the time -- which is enough on its own to drag a real effect
    down to a coin flip.
    """
    events, armed_until = [], 0
    for i, s in enumerate(samples):
        wall = s.get(field)
        if not wall or wall <= 0:
            continue                     # 0 means "not computed", not "at zero"
        if s["timestamp"] < armed_until:
            continue
        if abs(s["spot"] - wall) > tol:
            continue

        after = spot_after(samples, i, horizon_s)
        if after is None:
            continue
        move = after - s["spot"]
        side = approach_side(samples, i, field, tol)
        events.append({
            "ts": s["timestamp"],
            "wall": wall,
            "spot": s["spot"],
            "move": move,
            "side": side,
            # Away = ended up back on the side it came from, and clear of the
            # band rather than still loitering in it.
            "away": bool(side) and (after - wall) * side > 0
                    and abs(after - wall) > tol,
            "decisive": abs(move) >= min_move,
        })
        armed_until = s["timestamp"] + cooldown_s
    return events


def base_rate(samples, horizon_s, min_move):
    """Unconditional forward move, sampled across the session.

    Without this a 'respect rate' is unreadable: on a day that fell all
    afternoon, every resistance touch 'works'.
    """
    downs = ups = decisive = total = 0
    step = max(1, len(samples) // 500)
    for i in range(0, len(samples), step):
        after = spot_after(samples, i, horizon_s)
        if after is None:
            continue
        move = after - samples[i]["spot"]
        total += 1
        if abs(move) >= min_move:
            decisive += 1
        if move < 0:
            downs += 1
        elif move > 0:
            ups += 1
    return {"samples": total, "down_pct": 100 * downs / total if total else 0,
            "up_pct": 100 * ups / total if total else 0,
            "decisive_pct": 100 * decisive / total if total else 0}


def analyse(samples, tol, horizon_min, cooldown_min, min_move):
    horizon_s, cooldown_s = horizon_min * 60, cooldown_min * 60
    results = []
    for field, reading, kind, want in WALLS:
        ev = find_touches(samples, field, tol, cooldown_s, horizon_s, min_move)
        if not ev:
            results.append({"field": field, "reading": reading, "kind": kind,
                            "touches": 0})
            continue
        respected = [e for e in ev if (e["move"] < 0) == (want < 0) and e["move"] != 0]
        dec = [e for e in ev if e["decisive"]]
        dec_ok = [e for e in dec if (e["move"] < 0) == (want < 0)]
        sided = [e for e in ev if e["side"]]
        results.append({
            "field": field, "reading": reading, "kind": kind,
            "touches": len(ev),
            "respect_pct": 100 * len(respected) / len(ev),
            "decisive_touches": len(dec),
            "decisive_respect_pct": 100 * len(dec_ok) / len(dec) if dec else None,
            "median_move": statistics.median(e["move"] for e in ev),
            "mean_abs_move": statistics.fmean(abs(e["move"]) for e in ev),
            # The vendor's framing, scored separately.
            "sided_touches": len(sided),
            "away_pct": (100 * sum(e["away"] for e in sided) / len(sided)
                         if sided else None),
        })
    return results


def agreement(samples):
    """How often do the two readings even point at the same strike?"""
    same_pos = sum(1 for s in samples if s.get("major_pos_vol") == s.get("major_pos_oi"))
    same_neg = sum(1 for s in samples if s.get("major_neg_vol") == s.get("major_neg_oi"))
    gaps_pos = [abs(s["major_pos_vol"] - s["major_pos_oi"]) for s in samples
                if s.get("major_pos_vol") and s.get("major_pos_oi")]
    gaps_neg = [abs(s["major_neg_vol"] - s["major_neg_oi"]) for s in samples
                if s.get("major_neg_vol") and s.get("major_neg_oi")]
    regime_same = sum(1 for s in samples
                      if (s.get("sum_gex_vol", 0) > 0) == (s.get("sum_gex_oi", 0) > 0))
    n = len(samples)
    return {
        "samples": n,
        "call_wall_same_pct": 100 * same_pos / n,
        "put_wall_same_pct": 100 * same_neg / n,
        "median_call_gap": statistics.median(gaps_pos) if gaps_pos else None,
        "median_put_gap": statistics.median(gaps_neg) if gaps_neg else None,
        "regime_agree_pct": 100 * regime_same / n,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--zip", required=True)
    ap.add_argument("--scope", default="gex_zero")
    ap.add_argument("--tol", type=float, default=5.0,
                    help="points from a wall that counts as a touch")
    ap.add_argument("--horizon", type=float, default=15.0, help="minutes forward")
    ap.add_argument("--cooldown", type=float, default=15.0,
                    help="minutes before the same wall can re-trigger")
    ap.add_argument("--min-move", type=float, default=15.0,
                    help="points that make a move decisive rather than noise")
    ap.add_argument("--json", default=None)
    args = ap.parse_args()

    samples = load_session(args.zip, args.scope)
    t0 = dt.datetime.fromtimestamp(samples[0]["timestamp"], dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(samples[-1]["timestamp"], dt.timezone.utc)
    spots = [s["spot"] for s in samples]

    print(f"{samples[0]['ticker']} {args.scope} — {t0:%Y-%m-%d} "
          f"{t0:%H:%M}→{t1:%H:%M} UTC, {len(samples):,} samples")
    print(f"session range {min(spots):,.2f}–{max(spots):,.2f} "
          f"(open {spots[0]:,.2f} close {spots[-1]:,.2f}, "
          f"net {spots[-1]-spots[0]:+,.2f})\n")

    ag = agreement(samples)
    print("Do the two readings agree?")
    print(f"  call wall same strike : {ag['call_wall_same_pct']:5.1f}% of samples")
    print(f"  put wall same strike  : {ag['put_wall_same_pct']:5.1f}%")
    print(f"  median gap            : call {ag['median_call_gap']}, put {ag['median_put_gap']} pts")
    print(f"  same regime sign      : {ag['regime_agree_pct']:5.1f}%\n")

    br = base_rate(samples, args.horizon * 60, args.min_move)
    print(f"Baseline over {args.horizon:g} min (any moment, no wall involved):")
    print(f"  price lower: {br['down_pct']:.1f}%   higher: {br['up_pct']:.1f}%   "
          f"moved >={args.min_move:g}pts: {br['decisive_pct']:.1f}%\n")

    res = analyse(samples, args.tol, args.horizon, args.cooldown, args.min_move)
    print(f"Touch within {args.tol:g} pts, outcome {args.horizon:g} min later:")
    print(f"  {'wall':<30} {'touches':>7} {'directional':>12} {'away':>8} "
          f"{'decisive':>9} {'dir.':>6}")
    for r in res:
        if not r["touches"]:
            print(f"  {r['reading']+' '+r['kind']:<30} {0:>7}")
            continue
        dr = f"{r['decisive_respect_pct']:.0f}%" if r["decisive_respect_pct"] is not None else "-"
        aw = f"{r['away_pct']:.0f}%" if r["away_pct"] is not None else "-"
        print(f"  {r['reading']+' '+r['kind']:<30} {r['touches']:>7} "
              f"{r['respect_pct']:>11.0f}% {aw:>8} {r['decisive_touches']:>9} {dr:>6}")
    print("\n  directional = fell from a call wall / rose from a put wall")
    print("  away        = moved back the way it came, whichever wall it is")

    if args.json:
        json.dump({"agreement": ag, "baseline": br, "walls": res,
                   "params": vars(args)}, open(args.json, "w"), indent=2)
        print(f"\nwrote {args.json}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
