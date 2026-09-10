#!/usr/bin/env python3
"""
review_day.py — grade a past trading day's scans against what price actually did.

This is what the background sub-agent runs. It is deliberately a SCRIPT, not a
prompt: the arithmetic (did price touch the level, did it reject or slice, was
the range budget right) is deterministic and must not be re-derived by a model
each time. The sub-agent's job is to read this output and judge what it means.

    python3 review_day.py                # most recent unreviewed day
    python3 review_day.py 2026-08-21     # a specific day
    python3 review_day.py --json
"""
import json, os, sys
from datetime import datetime, timezone, timedelta

_HERE = os.path.dirname(os.path.abspath(__file__))
# Sibling skill relative to this file; see levels_fuel.py for why the
# hardcoded ~/CTrader-Bots path could not be relied on.
for _c in [_HERE,
           os.path.abspath(os.path.join(_HERE, "..", "..",
                                        "liquidity-inducement-phone",
                                        "scripts"))]:
    if os.path.isfile(os.path.join(_c, "ctrader_http.py")):
        sys.path.insert(0, os.path.abspath(_c)); break

import journal                                                   # noqa: E402
import ctrader_http as ct                                        # noqa: E402
import levels_fuel as LF                                         # noqa: E402

TOUCH_TOL = 8.0      # pts — "price reached the level"
REJECT_PTS = 25.0    # pts of adverse travel within the window to call it a rejection
REACT_BARS = 12      # M_5 bars (~1h) to judge the reaction


def fetch_day_bars(day):
    """M_5 bars for one trading day, bucketed on the 17:00 ET / 21:00 UTC roll."""
    target = datetime.fromisoformat(day).date()
    now = datetime.now(timezone.utc)
    days_back = max(2, (now.date() - target).days + 3)
    bars = ct.fetch_ohlcv_paged("NAS100", "M_5", days=min(days_back, 20))
    return [b for b in bars if LF.trading_day(b["time"]) == target]


SETTLE_TOL = 25.0    # pts of adverse excursion allowed once price picks a side
MIN_SETTLED_BARS = 6 # bars needed on one side before "it held" means anything


def settled_read(price, bars, tol=SETTLE_TOL):
    """Once price picked a side of this level, did the level hold it?

    THIS IS THE OFFICIAL VERDICT as of 2026-09-09. It replaced the first-touch
    read, which lost 0-of-8 against it on identical data (see the retrospective
    in HYPOTHESES.md). The first touch is the worst possible sample: on a
    news-driven open it grades the noise and ignores the rest of the day, and it
    has no concept of ROLE REVERSAL -- a wall that caps price, gets reclaimed,
    then acts as support is a level doing its job, and first-touch called that
    "chopped".

    Two cases settled it. C3 29,602 on 09-09: first touch said "broke DOWN,
    79pts"; the worst excursion was 0.8pts across 870 minutes with two rejected
    re-tests. C1 29,464 on 08-27: worst excursion -4.7pts over 430 minutes,
    which is the trader's own reading of that level reproduced to the point.
    """
    if not bars:
        return None
    # A level price never went near cannot have "held" anything. Without this a
    # strike 650pts away scored as SUPPORT with a +651.6 excursion, because the
    # minimum low was trivially above it. Untested is not passed.
    if not any(b["low"] - 6 <= price <= b["high"] + 6 for b in bars):
        return None
    last_far = None
    side_above = bars[-1]["close"] >= price
    for b in bars:
        if (b["close"] < price) if side_above else (b["close"] > price):
            last_far = b["time"]
    after = [b for b in bars if last_far is None or b["time"] > last_far]
    if len(after) < MIN_SETTLED_BARS:
        return None
    touches = [b for b in after if b["low"] - 6 <= price <= b["high"] + 6]
    if side_above:
        worst = min(b["low"] for b in after)
    else:
        worst = max(b["high"] for b in after)
    excursion = worst - price
    held = (worst >= price - tol) if side_above else (worst <= price + tol)
    return {
        "settled_side": "above" if side_above else "below",
        "settled_from": last_far.strftime("%H:%M") if last_far else "open",
        "minutes_held": len(after) * 5,
        "touches_after": len(touches),
        "worst_excursion": round(excursion, 1),
        "held": held,
        "acted_as": ("support" if side_above else "resistance") if held else "lost",
    }


def _first_touch(lv, bars, i_from=0):
    """The SUPERSEDED first-touch read. Kept, computed and reported, never the
    verdict -- so that re-graded history can always be compared against what
    the old instrument said rather than quietly overwritten."""
    price, name = lv["price"], lv["name"]
    for i in range(i_from, len(bars)):
        b = bars[i]
        if b["low"] - TOUCH_TOL <= price <= b["high"] + TOUCH_TOL:
            after = bars[i:i + REACT_BARS]
            if not after:
                break
            hi = max(x["high"] for x in after)
            lo = min(x["low"] for x in after)
            up, down = hi - price, price - lo
            through_up = hi > price + REJECT_PTS
            through_down = lo < price - REJECT_PTS
            if through_up and not through_down:
                react = "broke UP through it"
            elif through_down and not through_up:
                react = "broke DOWN through it"
            elif through_up and through_down:
                react = "traded both sides — chopped around it"
            else:
                react = "stalled at it (no clean break either way)"
            return {"touched": True, "at": b["time"].isoformat(),
                    "bar_index": i, "reaction": react,
                    "travel_up": round(up, 1), "travel_down": round(down, 1)}
    return {"touched": False, "reaction": "never reached"}


def grade_level(lv, bars, i_from=0):
    """The one grader. Verdict from settled_read; first-touch kept alongside.

    Returns the same keys consumers already read (`touched`, `reaction`,
    `travel_up`, `travel_down`), so track.py and gex_retro.py need no change --
    but `reaction` now comes from the settled read where one is available.
    """
    ft = _first_touch(lv, bars, i_from)
    st = settled_read(lv["price"], bars[i_from:] if i_from else bars)
    if not ft.get("touched"):
        return {**ft, "first_touch_reaction": ft["reaction"], "settled": None}
    if st is None:
        # Touched, but never settled on one side for long enough to judge.
        # Report it as such rather than borrowing the first-touch verdict.
        return {**ft, "first_touch_reaction": ft["reaction"], "settled": None,
                "reaction": "touched, no settled read (too few bars on one side)"}
    if st["held"]:
        react = (f"stalled at it — held as {st['acted_as']} for "
                 f"{st['minutes_held']}min, worst {st['worst_excursion']:+.1f}pts")
    else:
        react = (f"broke {'DOWN' if st['settled_side'] == 'above' else 'UP'} "
                 f"through it — lost by {abs(st['worst_excursion']):.1f}pts")
    return {**ft, "reaction": react,
            "first_touch_reaction": ft["reaction"], "settled": st}


def review(day, root=None):
    # Verification re-runs are excluded here for the same reason track.py
    # excludes them: they are one market state sampled once, journalled several
    # times. Left in, 2026-08-27 read "5 right / 0 wrong" off a single real
    # scan repeated four times while code was being fixed.
    scans = [s for s in journal.load_day(day, root) if not s.get("test_artefact")]
    n_art = sum(1 for s in journal.load_day(day, root) if s.get("test_artefact"))
    if not scans:
        return {"error": f"no journal entries for {day}"}
    # A weekend/holiday scan is a PREP read against the previous session's
    # frozen close, so there is no session to grade it against and its numbers
    # repeat across every run that day. Grading one would manufacture a
    # statistic out of a single stale observation.
    live = [s for s in scans if s.get("is_trading_day")]
    if not live:
        return {"status": "skipped", "trading_day": day,
                "reason": "not a trading day — PREP scans only, nothing to grade",
                "scans_found": len(scans)}
    scans = live
    bars = fetch_day_bars(day)
    if not bars:
        return {"error": f"no NAS100 bars for {day}",
                "detail": ct.last_error(), "scans_found": len(scans)}

    o, h, l, c = bars[0]["open"], max(b["high"] for b in bars), \
                 min(b["low"] for b in bars), bars[-1]["close"]
    actual = {"open": round(o, 1), "high": round(h, 1), "low": round(l, 1),
              "close": round(c, 1), "range": round(h - l, 1),
              "net_move": round(c - o, 1),
              "direction": 1 if c > o else (-1 if c < o else 0),
              "bars": len(bars)}

    results = []
    for sc in scans:
        pr = sc["prediction"]
        # only grade bars from the scan onward — a 13:00 scan can't be graded
        # on what happened at 09:00
        try:
            t0 = datetime.fromisoformat(sc["scan_utc"])
            i0 = next((i for i, b in enumerate(bars) if b["time"] >= t0), 0)
        except Exception:
            i0 = 0
        fwd = bars[i0:]
        if fwd:
            move = round(fwd[-1]["close"] - fwd[0]["open"], 1)
            dir_after = 1 if move > 0 else (-1 if move < 0 else 0)
        else:
            move, dir_after = 0.0, 0

        exp = pr["expected_direction"]
        call = ("no call (neutral)" if exp == 0 else
                "CORRECT" if exp == dir_after else "WRONG")

        levels = []
        for lv in pr["levels"]:
            g = grade_level(lv, bars, i0)
            levels.append({**{k: lv[k] for k in ("price", "name", "kind")}, **g})
        touched = [x for x in levels if x["touched"]]

        # Fuel must be graded on range EXTENSION, not on how far price roamed.
        #
        # The budget answers "how much further can the day's HIGH-LOW range
        # grow", not "how far will price travel". Those are wildly different
        # once a range is established: on 2026-08-24 the 13:45 scan published a
        # 0.0pt budget, the range then extended 5.3pts (essentially exact) —
        # while price traversed 284.4pts inside it. Grading against traversal
        # called that a 3.8x under-estimate when the model had been right.
        budget = pr["remaining_budget"]
        upto = bars[:i0] or bars[:1]
        range_at_scan = round(max(b["high"] for b in upto) - min(b["low"] for b in upto), 1)
        extension = round(actual["range"] - range_at_scan, 1)
        traversal = round(max(b["high"] for b in fwd) - min(b["low"] for b in fwd), 1) if fwd else 0
        tol = max(60.0, budget * 0.5)
        fuel_call = ("UNDER-estimated — the range grew more than budgeted"
                     if extension > budget + tol else
                     "OVER-estimated — the range grew far less than budgeted"
                     if extension < budget - tol else "about right")

        results.append({
            "scan_utc": sc["scan_utc"], "session": sc["session_window"],
            "predicted": {"bias": pr["bias_label"], "score": pr["bias_score"],
                          "direction": exp, "shape": pr["expiry_shape"],
                          "fuel_state": pr["fuel_state"], "budget": budget,
                          # Carried through so track.py can spot a scan whose
                          # fuel was measured across the 21:00 UTC rollover:
                          # >100% "used" before the session has bars means the
                          # figure describes the PREVIOUS day's finished range.
                          "adr_used_pct": pr.get("adr_used_pct")},
            "actual_after_scan": {"move": move, "direction": dir_after,
                                  "range_at_scan": range_at_scan,
                                  "range_extension": extension,
                                  "price_traversal": traversal},
            "direction_call": call,
            "fuel_call": fuel_call,
            "fuel_extension_vs_budget": (round(extension / budget, 2)
                                         if budget else None),
            # How much movement was available INSIDE the range. This is the
            # number that says whether there was a trade, independent of
            # whether the range grew.
            "traversal_vs_budget": (round(traversal / budget, 2) if budget else None),
            "levels_published": len(levels),
            "levels_touched": len(touched),
            "level_hit_rate": round(len(touched) / len(levels), 2) if levels else None,
            "levels_detail": levels,
        })

    return {"trading_day": day, "reviewed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "actual_session": actual, "scans": results, "test_artefacts": n_art,
            "summary": _summary(results, actual)}


def _summary(results, actual):
    calls = [r["direction_call"] for r in results]
    correct = calls.count("CORRECT"); wrong = calls.count("WRONG")
    hit = [r["level_hit_rate"] for r in results if r["level_hit_rate"] is not None]
    return {
        "scans": len(results),
        "direction_correct": correct, "direction_wrong": wrong,
        "direction_no_call": calls.count("no call (neutral)"),
        "mean_level_hit_rate": round(sum(hit) / len(hit), 2) if hit else None,
        "session_range": actual["range"], "session_net": actual["net_move"],
        "fuel_calls": [r["fuel_call"] for r in results],
    }


def latest_unreviewed(root=None):
    root = root or journal.JOURNAL_ROOT
    if not os.path.isdir(root):
        return None
    days = sorted(d for d in os.listdir(root) if os.path.isdir(os.path.join(root, d)))
    today = LF.trading_day(datetime.now(timezone.utc)).isoformat()
    past = [d for d in days if d < today]
    # walk back to the most recent day that actually has a gradeable scan
    for d in reversed(past):
        # M3: this filter must match the two at review():75 and track.py:82.
        # It used to test is_trading_day only, so it returned a day whose only
        # entries were artefacts and review() then answered "error" instead of
        # the "skipped" shape built for exactly that case.
        if any(s.get("is_trading_day") and not s.get("test_artefact")
               for s in journal.load_day(d, root)):
            return d
    return None


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    day = args[0] if args else latest_unreviewed()
    if not day:
        print(json.dumps({"status": "nothing to review",
                          "reason": "no completed trading day in the journal yet"},
                         indent=2)); sys.exit(0)
    r = review(day)
    # "status" covers the skipped/non-gradeable cases, which carry no session
    # data — without it the human path reached for r["actual_session"].
    if "--json" in sys.argv or "error" in r or "status" in r:
        print(json.dumps(r, indent=2, default=str)); sys.exit(0)
    a, s = r["actual_session"], r["summary"]
    print(f"REVIEW {r['trading_day']}  O {a['open']} H {a['high']} L {a['low']} "
          f"C {a['close']}  range {a['range']}  net {a['net_move']:+.1f}")
    print(f"  direction: {s['direction_correct']} right / {s['direction_wrong']} wrong "
          f"/ {s['direction_no_call']} no-call   levels touched: {s['mean_level_hit_rate']}")
    for sc in r["scans"]:
        print(f"\n  {sc['scan_utc'][11:16]} {sc['session']:<10} "
              f"{sc['predicted']['bias']} ({sc['predicted']['score']:+d}) "
              f"-> moved {sc['actual_after_scan']['move']:+.1f}  [{sc['direction_call']}]")
        a = sc["actual_after_scan"]
        print(f"     fuel: budget {sc['predicted']['budget']} vs range EXTENSION "
              f"{a['range_extension']} -> {sc['fuel_call']}")
        print(f"           (price traversed {a['price_traversal']} INSIDE the range)")
        for lv in sc["levels_detail"]:
            if lv["touched"]:
                print(f"       {lv['price']:>9} {lv['name'][:34]:<34} {lv['reaction']}")
