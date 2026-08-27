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
from datetime import datetime, timedelta, timezone

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


def _day_complete(day, bars, min_bars=240):
    """Has this trading day ended? It runs to 21:00 UTC on its own date."""
    try:
        d = datetime.strptime(day, "%Y-%m-%d")
    except ValueError:
        return False
    end = d.replace(hour=21, minute=0, tzinfo=timezone.utc)
    if datetime.now(timezone.utc) < end:
        return False
    return bars >= min_bars


def collect(root=None):
    root = root or journal.JOURNAL_ROOT
    days = sorted(d for d in os.listdir(root)
                  if os.path.isdir(os.path.join(root, d)))
    rows, per_day, excluded, unfinished = [], {}, [], []
    for day in days:
        scans = [s for s in journal.load_day(day, root) if s.get("is_trading_day")]
        if not scans:
            continue
        rev = R.review(day, root)
        if "scans" not in rev:
            continue
        # Only grade a day that has actually FINISHED.
        #
        # This used to test `bars < 150`, which does not work: the trading day
        # starts at 21:00 UTC the previous evening, so 150 M_5 bars accumulate
        # by 09:30 UTC — four hours before NY even opens. On 2026-08-26 at
        # 13:23 UTC it admitted a day with 185 bars (complete days have 276),
        # whose "close" was just the last tick and whose range had not finished
        # extending. That single unfinished day flipped H1's mean error from
        # +46.6 to -19.9 — a SIGN CHANGE — and turned `actionable` to YES while
        # HYPOTHESES.md still correctly said nothing was actionable.
        #
        # A day is done when the clock says so. Bars are kept only as a
        # secondary sanity check against a broken or gappy feed.
        sess = rev.get("actual_session") or {}
        if not _day_complete(day, sess.get("bars", 0)):
            per_day[day] = {**sess, "_excluded": "session not finished"}
            unfinished.append({"day": day, "bars": sess.get("bars", 0)})
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
            # The corruption is FIELD-level, so the quarantine is too.
            #
            # A scan taken across the 21:00 UTC rollover had no bars for the
            # new day, so its FUEL described yesterday's finished range. Its
            # direction call is untouched by that — fuel reports and never
            # votes, which D1 establishes and the bias components confirm.
            # Dropping the whole row therefore threw away good evidence: both
            # quarantined scans carried WRONG direction calls, so the
            # scoreboard read 1 right / 1 wrong when the honest tally was
            # 1 right / 2 wrong. Worse, the SESSION_PENDING branch would have
            # done that to EVERY future overnight scan — precisely the
            # population H7 exists to study.
            fuel_bad = (p.get("fuel_state") == "SESSION_PENDING" or
                        _rollover_corrupt(sc["scan_utc"], p.get("adr_used_pct")))
            if fuel_bad:
                excluded.append({"scan": sc["scan_utc"][:16].replace("T", " "),
                                 "day": day, "session": sc["session"],
                                 "why": "fuel measured across the day rollover "
                                        "— fuel fields dropped, direction kept"})
            rows.append({
                "day": day, "time": sc["scan_utc"][11:16], "session": sc["session"],
                "scan_utc": sc["scan_utc"], "fuel_bad": fuel_bad,
                "budget": p["budget"], "extension": a["range_extension"],
                "traversal": a["price_traversal"], "fuel_state": p["fuel_state"],
                "bias": p["score"], "call": sc["direction_call"],
                "hit_rate": sc["level_hit_rate"],
            })
        per_day[day] = rev["actual_session"]
    return rows, per_day, excluded, unfinished


def summarise(rows):
    n_days = len({r["day"] for r in rows})
    calls = [r["call"] for r in rows]
    hits = [r["hit_rate"] for r in rows if r["hit_rate"] is not None]

    # H1/H5 read the fuel fields, so they use only rows whose fuel is sound.
    # Direction and level stats above use EVERY row — a rollover scan's call
    # is perfectly good evidence.
    fuel_rows = [r for r in rows if not r.get("fuel_bad")]
    ext_err = [(r["extension"] - r["budget"]) for r in fuel_rows]
    # A scan-pooled mean is not one observation per day.
    #
    # 24 Aug contributes FOUR rows, three carrying an identical budget (88.7)
    # against an identical extension (168.5) — one budget reading graded three
    # times. Not a stale-fuel defect: the live range genuinely was 362.4 at all
    # three timestamps. The 15-minute dedupe cannot see it either, because the
    # scans are hours apart. A day with more scans simply votes more often.
    #
    # Both are reported now. Per-scan answers "how wrong is a typical scan";
    # per-day answers "how wrong is the model on a typical day", and a
    # hypothesis about the MODEL should be read against the second.
    by_day = defaultdict(list)
    for r in fuel_rows:
        by_day[r["day"]].append(r["extension"] - r["budget"])
    day_err = [sum(v) / len(v) for v in by_day.values()]
    early = [r for r in fuel_rows if r["session"] in ("ASIA", "LONDON", "PRE_NY")]
    late = [r for r in fuel_rows
            if r["session"] in ("NY_OPEN", "NY_MIDDAY", "NY_PM", "NY_CLOSE")]

    def mean(xs):
        return round(sum(xs) / len(xs), 1) if xs else None

    return {
        "trading_days": n_days, "scans": len(rows),
        "scans_with_sound_fuel": len(fuel_rows),
        "actionable": n_days >= MIN_SESSIONS,
        "min_sessions_required": MIN_SESSIONS,
        "direction": {"correct": calls.count("CORRECT"),
                      "wrong": calls.count("WRONG"),
                      "no_call": calls.count("no call (neutral)")},
        "mean_level_hit_rate": (round(sum(hits) / len(hits), 2) if hits else None),
        "H1_budget_vs_extension": {
            "mean_error_pts": mean(ext_err),
            "mean_error_per_day": mean(day_err),
            "days": len(day_err),
            "per_day": {d: round(sum(v) / len(v), 1) for d, v in sorted(by_day.items())},
            "note": "positive = range grew MORE than budgeted; read per_day for "
                    "claims about the model, per-scan for claims about a scan",
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
            for r in fuel_rows if r["fuel_state"] in ("LOW_FUEL", "EXHAUSTED")
        ],
    }


if __name__ == "__main__":
    rows, per_day, excluded, unfinished = collect()
    s = summarise(rows)
    if "--json" in sys.argv:
        print(json.dumps({"rows": rows, "days": per_day, "summary": s,
                          "excluded": excluded},
                         indent=2, default=str)); sys.exit(0)
    print(f"EVIDENCE TO DATE — {s['trading_days']} trading day(s), "
          f"{s['scans']} scans (deduped)")
    # "actionable: YES" was a global day-count gate and read far more
    # permissively than the individual thresholds: it shouted YES on 3 days
    # while H4/H6 need 5, H8 needs 10, and H5 had one late-session scan to fit
    # a time-of-day term to. A banner that overstates readiness is how a model
    # gets tuned early.
    print(f"  {s['trading_days']} of {MIN_SESSIONS} days for the 3-day hypotheses "
          f"(H1/H2/H3/H5/H7) \u2014 "
          f"{'threshold met, read the evidence before proposing' if s['actionable'] else 'keep observing'}")
    print(f"  H4/H6 need 5 days \u00b7 H8 needs 10. Day count alone is not "
          f"evidence.\n")
    print(f"{'day':<12}{'time':>6} {'session':<10}{'budget':>8}{'extension':>11}"
          f"{'traversal':>11}{'err':>7}  {'bias':>5} {'call':<10}")
    for r in rows:
        flag = " *" if r.get("fuel_bad") else ""
        print(f"{r['day']:<12}{r['time']:>6} {r['session']:<10}{r['budget']:>8.1f}"
              f"{r['extension']:>11.1f}{r['traversal']:>11.1f}"
              f"{r['extension']-r['budget']:>7.1f}  {r['bias']:>+5d} "
              f"{r['call']:<10}{flag}")
    h1 = s["H1_budget_vs_extension"]
    print("\nH1 budget vs range EXTENSION  (+ = range grew more than budgeted)")
    print(f"   per scan {h1['mean_error_pts']:>8} pts  (n={s['scans_with_sound_fuel']} scans)")
    print(f"   per DAY  {h1['mean_error_per_day']:>8} pts  (n={h1['days']} days)"
          f"   <- read this for claims about the model")
    print("   " + "   ".join(f"{d[5:]} {e:+.1f}" for d, e in h1["per_day"].items()))
    h5 = s["H5_early_vs_late"]
    print(f"H5 early ({h5['early_n']}) mean err {h5['early_mean_error']}  vs  "
          f"late ({h5['late_n']}) mean err {h5['late_mean_error']}")
    d = s["direction"]
    print(f"direction: {d['correct']} right / {d['wrong']} wrong / "
          f"{d['no_call']} no-call   levels touched {s['mean_level_hit_rate']}")
    if unfinished:
        # D3 again: an exclusion the reader is never told about is a silent one.
        print("\nHELD BACK - day not finished (grades after 21:00 UTC on its own date):")
        for u in unfinished:
            print(f"  {u['day']}  {u['bars']} bars so far")
    if excluded:
        print("\n* FUEL fields excluded (corrupt input, not a failed forecast).")
        print("  Direction calls from these scans ARE counted.")
        for x in excluded:
            print(f"  scanned {x['scan']}Z  (trading day {x['day']}, "
                  f"{x['session']})")
    if s["H2_exhausted_scans"]:
        print("\nH2 — low-fuel / exhausted scans (does fading beat continuation?):")
        for x in s["H2_exhausted_scans"]:
            print(f"  {x['day']} {x['time']}  bias {x['bias']:+d}  {x['call']:<10}"
                  f"  extension {x['extension']:.1f}  traversal {x['traversal']:.1f}")
