#!/usr/bin/env python3
"""
track.py — roll every graded trading day into one evidence table.

Exists so that "watch it for a week" is a command rather than a memory. Each
review runs this, appends what it sees to journal/HYPOTHESES.md, and changes
nothing else. The point is to accumulate observations until a hypothesis has
enough of them to act on — not to react to the most recent session.

    python3 track.py            # human-readable
    python3 track.py --json
"""
import glob, json, os, sys
from collections import defaultdict
from datetime import datetime, timedelta

import journal, review_day as R

MIN_SESSIONS = 3          # nothing is actionable below this


def _dedupe(scans, window_min=15):
    """Collapse scans taken within `window_min` of each other.

    Four scans landed inside five minutes during testing. They observe one
    market state, so counting them four times inflates every statistic exactly
    the way weekend PREP scans would.
    """
    out, last = [], None
    for s in sorted(scans, key=lambda x: x["scan_utc"]):
        t = datetime.fromisoformat(s["scan_utc"])
        if last and (t - last).total_seconds() / 60 < window_min:
            continue
        out.append(s); last = t
    return out


def _rollover_corrupt(scan_utc, used_pct, window_min=90):
    """Was this scan's fuel measured across the 21:00 UTC day rollover?

    levels_fuel now reports SESSION_PENDING for this case, but entries written
    before that fix carry the previous day's finished range stamped as the new
    day's. Signature: the scan lands within `window_min` of the roll AND
    already claims >100% of ADR consumed. A real session cannot burn a full
    average day's range in its first 90 minutes; a genuine >100% reading later
    in the day is ordinary and must NOT be filtered (2026-08-24 13:45 was
    exactly that, and it is the cleanest H1 observation on record).
    """
    if (used_pct or 0) <= 100:
        return False
    t = datetime.fromisoformat(scan_utc)
    roll = t.replace(hour=21, minute=0, second=0, microsecond=0)
    if t.hour < 21:
        roll -= timedelta(days=1)
    return (t - roll).total_seconds() / 60 < window_min


def collect(root=None):
    root = root or journal.JOURNAL_ROOT
    days = sorted(d for d in os.listdir(root)
                  if os.path.isdir(os.path.join(root, d)))
    rows, per_day, excluded = [], {}, []
    for day in days:
        scans = [s for s in journal.load_day(day, root) if s.get("is_trading_day")]
        if not scans:
            continue
        rev = R.review(day, root)
        if "scans" not in rev:
            continue
        # A day still in progress has almost no forward data to grade against.
        # The first run of this caught a scan taken 56 minutes into a new
        # trading day being scored as "extension 0.0, traversal 26.1" — a
        # meaningless observation that would still have entered the averages.
        sess = rev.get("actual_session") or {}
        if sess.get("bars", 0) < 150:            # ~12.5h of M_5 bars
            per_day[day] = {**sess, "_excluded": "session incomplete"}
            continue
        kept = {s["scan_utc"] for s in _dedupe(scans)}
        for sc in rev["scans"]:
            if sc["scan_utc"] not in kept:
                continue
            a, p = sc["actual_after_scan"], sc["predicted"]
            # A scan taken across the 21:00 UTC rollover had no bars for the
            # new day, so its fuel figures described YESTERDAY's finished
            # range (levels_fuel now reports SESSION_PENDING instead). Such a
            # scan's budget is not a forecast that failed, it is a corrupt
            # input: 2026-08-24 21:56Z carried a 371pt "error" that on its own
            # dragged H1's mean from 46.6 to 100.7. Grading it would
            # manufacture a conclusion out of a bug — exactly what W1/W2 were
            # withdrawn for. Record it, exclude it from the statistics.
            if p.get("fuel_state") == "SESSION_PENDING" or \
                    _rollover_corrupt(sc["scan_utc"], p.get("adr_used_pct")):
                excluded.append({"day": day, "time": sc["scan_utc"][11:16],
                                 "why": "fuel measured across the day rollover"})
                continue
            rows.append({
                "day": day, "time": sc["scan_utc"][11:16], "session": sc["session"],
                "budget": p["budget"], "extension": a["range_extension"],
                "traversal": a["price_traversal"], "fuel_state": p["fuel_state"],
                "bias": p["score"], "call": sc["direction_call"],
                "hit_rate": sc["level_hit_rate"],
            })
        per_day[day] = rev["actual_session"]
    return rows, per_day, excluded


def summarise(rows):
    n_days = len({r["day"] for r in rows})
    calls = [r["call"] for r in rows]
    hits = [r["hit_rate"] for r in rows if r["hit_rate"] is not None]

    # H1: does the budget forecast range EXTENSION?
    ext_err = [(r["extension"] - r["budget"]) for r in rows]
    # H5: is it worse early in the session than late?
    early = [r for r in rows if r["session"] in ("ASIA", "LONDON", "PRE_NY")]
    late = [r for r in rows if r["session"] in ("NY_OPEN", "NY_MIDDAY", "NY_PM", "NY_CLOSE")]

    def mean(xs):
        return round(sum(xs) / len(xs), 1) if xs else None

    return {
        "trading_days": n_days, "scans": len(rows),
        "actionable": n_days >= MIN_SESSIONS,
        "min_sessions_required": MIN_SESSIONS,
        "direction": {"correct": calls.count("CORRECT"),
                      "wrong": calls.count("WRONG"),
                      "no_call": calls.count("no call (neutral)")},
        "mean_level_hit_rate": (round(sum(hits) / len(hits), 2) if hits else None),
        "H1_budget_vs_extension": {
            "mean_error_pts": mean(ext_err),
            "note": "positive = range grew MORE than budgeted",
        },
        "H5_early_vs_late": {
            "early_mean_error": mean([r["extension"] - r["budget"] for r in early]),
            "late_mean_error": mean([r["extension"] - r["budget"] for r in late]),
            "early_n": len(early), "late_n": len(late),
        },
        "H2_exhausted_scans": [
            {"day": r["day"], "time": r["time"], "bias": r["bias"],
             "call": r["call"], "extension": r["extension"],
             "traversal": r["traversal"]}
            for r in rows if r["fuel_state"] in ("LOW_FUEL", "EXHAUSTED")
        ],
    }


if __name__ == "__main__":
    rows, per_day, excluded = collect()
    s = summarise(rows)
    if "--json" in sys.argv:
        print(json.dumps({"rows": rows, "days": per_day, "summary": s,
                          "excluded": excluded},
                         indent=2, default=str)); sys.exit(0)
    print(f"EVIDENCE TO DATE — {s['trading_days']} trading day(s), "
          f"{s['scans']} scans (deduped)")
    print(f"  actionable at {MIN_SESSIONS}+ days: "
          f"{'YES' if s['actionable'] else 'NO — keep observing'}\n")
    print(f"{'day':<12}{'time':>6} {'session':<10}{'budget':>8}{'extension':>11}"
          f"{'traversal':>11}{'err':>7}  {'bias':>5} {'call':<10}")
    for r in rows:
        print(f"{r['day']:<12}{r['time']:>6} {r['session']:<10}{r['budget']:>8.1f}"
              f"{r['extension']:>11.1f}{r['traversal']:>11.1f}"
              f"{r['extension']-r['budget']:>7.1f}  {r['bias']:>+5d} {r['call']:<10}")
    print(f"\nH1 budget vs range EXTENSION: mean error "
          f"{s['H1_budget_vs_extension']['mean_error_pts']} pts "
          f"(+ = range grew more than budgeted)")
    h5 = s["H5_early_vs_late"]
    print(f"H5 early ({h5['early_n']}) mean err {h5['early_mean_error']}  vs  "
          f"late ({h5['late_n']}) mean err {h5['late_mean_error']}")
    d = s["direction"]
    print(f"direction: {d['correct']} right / {d['wrong']} wrong / "
          f"{d['no_call']} no-call   levels touched {s['mean_level_hit_rate']}")
    if excluded:
        print("\nEXCLUDED from the statistics (corrupt input, not a failed forecast):")
        for x in excluded:
            print(f"  {x['day']} {x['time']}  {x['why']}")
    if s["H2_exhausted_scans"]:
        print("\nH2 — low-fuel / exhausted scans (does fading beat continuation?):")
        for x in s["H2_exhausted_scans"]:
            print(f"  {x['day']} {x['time']}  bias {x['bias']:+d}  {x['call']:<10}"
                  f"  extension {x['extension']:.1f}  traversal {x['traversal']:.1f}")
