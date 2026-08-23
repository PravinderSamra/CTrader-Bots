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
for _c in [_HERE,
           os.path.expanduser("~/CTrader-Bots/.claude/skills/"
                              "liquidity-inducement-phone/scripts")]:
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


def grade_level(lv, bars, i_from=0):
    """Did price reach this level, and what happened when it did?"""
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


def review(day, root=None):
    scans = journal.load_day(day, root)
    if not scans:
        return {"error": f"no journal entries for {day}"}
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

        # was the fuel/range estimate right?
        budget = pr["remaining_budget"]
        realised = round(max(b["high"] for b in fwd) - min(b["low"] for b in fwd), 1) if fwd else 0
        fuel_call = ("UNDER-estimated — price used more range than we budgeted"
                     if realised > budget * 1.25 else
                     "OVER-estimated — price used far less than budgeted"
                     if realised < budget * 0.5 else "about right")

        results.append({
            "scan_utc": sc["scan_utc"], "session": sc["session_window"],
            "predicted": {"bias": pr["bias_label"], "score": pr["bias_score"],
                          "direction": exp, "shape": pr["expiry_shape"],
                          "fuel_state": pr["fuel_state"], "budget": budget},
            "actual_after_scan": {"move": move, "direction": dir_after,
                                  "realised_range": realised},
            "direction_call": call,
            "fuel_call": fuel_call, "fuel_ratio": round(realised / budget, 2) if budget else None,
            "levels_published": len(levels),
            "levels_touched": len(touched),
            "level_hit_rate": round(len(touched) / len(levels), 2) if levels else None,
            "levels_detail": levels,
        })

    return {"trading_day": day, "reviewed_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "actual_session": actual, "scans": results,
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
    return past[-1] if past else None


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    day = args[0] if args else latest_unreviewed()
    if not day:
        print(json.dumps({"status": "nothing to review",
                          "reason": "no completed trading day in the journal yet"},
                         indent=2)); sys.exit(0)
    r = review(day)
    if "--json" in sys.argv or "error" in r:
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
        print(f"     fuel: budget {sc['predicted']['budget']} vs realised "
              f"{sc['actual_after_scan']['realised_range']} -> {sc['fuel_call']}")
        for lv in sc["levels_detail"]:
            if lv["touched"]:
                print(f"       {lv['price']:>9} {lv['name'][:34]:<34} {lv['reaction']}")
