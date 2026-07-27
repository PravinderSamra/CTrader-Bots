#!/usr/bin/env python3
"""
journal_review.py — score logged trade ideas against what price actually did.

The replay harness built earlier gave three different answers depending on how
I parameterised it, because it had no ground truth. This does: it takes ideas
that were actually written down at the time, with no hindsight in their
construction, and asks what happened next.

For each unreviewed entry it walks M5 bars forward from `as_of` and answers, in
order:
  1. did price reach the trigger zone at all?
  2. if so, did it reach the entry zone?
  3. once filled, did the target or the stop come first?
  4. how far in favour did it get before resolving (MFE, in R)?

A bar touching both target and stop is scored a LOSS — intrabar order is
unknowable from OHLC, so the pessimistic reading is the honest one.

Entries with state NO_TRADE are scored too: "what did the setup I passed on go
on to do" is exactly as informative as the ones taken.

Usage:
    python3 journal_review.py [--month YYYY-MM] [--write] [--journal DIR]
"""

import argparse
import glob
import json
import os
import statistics
import sys
from datetime import datetime, timedelta, timezone

try:
    import ctrader_http as ct
except Exception:
    sys.path.insert(0, __file__.rsplit("/", 1)[0])
    import ctrader_http as ct

DEFAULT_JOURNAL = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))), "trade-journal")
HORIZON_HOURS = 30          # how long an idea is given to play out
_bars_cache: dict = {}


def _parse(ts):
    return datetime.fromisoformat(ts.replace("Z", "+00:00"))


def bars_for(instrument, days):
    key = (instrument, days)
    if key not in _bars_cache:
        _bars_cache[key] = ct.fetch_ohlcv_paged(instrument, "M_5", days=days)
    return _bars_cache[key]


def in_zone(bar, zone):
    return bar["low"] <= zone[1] and bar["high"] >= zone[0]


def score(entry, bars):
    """Walk forward from as_of and decide what became of this idea."""
    t0 = _parse(entry["as_of"])
    fwd = [b for b in bars
           if t0 < b["time"] <= t0 + timedelta(hours=HORIZON_HOURS)]
    if not fwd:
        return None

    direction = entry.get("direction")
    trigger = entry.get("trigger_zone")
    entry_zone = entry.get("entry_zone")
    target = entry.get("target_zone")
    stop = entry.get("stop")

    out = {"reviewed_at": datetime.now(tz=timezone.utc)
           .strftime("%Y-%m-%dT%H:%M:%SZ"),
           "triggered": False, "filled": False,
           "outcome": "never_triggered", "r": 0.0, "mfe_r": 0.0,
           "bars_to_outcome": 0, "bars_available": len(fwd)}

    i = 0
    if trigger:
        for i, b in enumerate(fwd):
            if in_zone(b, trigger):
                out["triggered"] = True
                break
        if not out["triggered"]:
            return out
    rest = fwd[i:]

    # Without a concrete entry/stop the idea was a watch, not a plan: record
    # whether it triggered and what the excursion was, but not an R figure.
    if not (entry_zone and stop and target and direction):
        out["outcome"] = "watch_only"
        ref = entry.get("price_at_idea")
        if ref:
            ext = (max(b["high"] for b in rest) if direction == "long"
                   else min(b["low"] for b in rest))
            out["excursion_pts"] = round(abs(ext - ref), 3)
        return out

    fill_i = None
    for j, b in enumerate(rest):
        if in_zone(b, entry_zone):
            fill_i = j
            break
    if fill_i is None:
        out["outcome"] = "no_fill"
        return out
    out["filled"] = True

    fill = entry_zone[1] if direction == "long" else entry_zone[0]
    risk = abs(fill - stop)
    if risk <= 0:
        out["outcome"] = "bad_entry_data"
        return out
    tgt = target[0] if direction == "long" else target[1]

    mfe = 0.0
    for n, b in enumerate(rest[fill_i + 1:], start=1):
        fav = (b["high"] - fill) if direction == "long" else (fill - b["low"])
        mfe = max(mfe, fav / risk)
        hit_stop = b["low"] <= stop if direction == "long" else b["high"] >= stop
        hit_tgt = b["high"] >= tgt if direction == "long" else b["low"] <= tgt
        if hit_stop:                      # pessimistic when both in one bar
            out.update(outcome="stop", r=-1.0, bars_to_outcome=n)
            break
        if hit_tgt:
            out.update(outcome="target", r=round(abs(tgt - fill) / risk, 2),
                       bars_to_outcome=n)
            break
    else:
        out["outcome"] = "expired"
        last = rest[-1]["close"]
        pnl = (last - fill) if direction == "long" else (fill - last)
        out["r"] = round(pnl / risk, 2)
        out["bars_to_outcome"] = len(rest) - fill_i
    out["mfe_r"] = round(mfe, 2)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--journal", default=DEFAULT_JOURNAL)
    ap.add_argument("--month", help="YYYY-MM (default: all)")
    ap.add_argument("--write", action="store_true",
                    help="write the review back into the journal")
    ap.add_argument("--days", type=int, default=45,
                    help="history to pull per instrument")
    args = ap.parse_args()

    pattern = f"{args.month}.jsonl" if args.month else "*.jsonl"
    files = sorted(glob.glob(os.path.join(args.journal, pattern)))
    if not files:
        print(f"no journal files in {args.journal}")
        return

    reviewed, scored = 0, []
    for path in files:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
        entries = [json.loads(l) for l in lines]
        changed = False
        for e in entries:
            if e.get("review"):
                continue
            bars = bars_for(e["instrument"], args.days)
            if not bars:
                print(f"  ! no bars for {e['instrument']}: {ct.last_error()}")
                continue
            r = score(e, bars)
            if r is None:
                continue           # too recent to judge yet
            e["review"] = r
            changed = True
            reviewed += 1
            scored.append((e, r))
        if changed and args.write:
            with open(path, "w") as fh:
                for e in entries:
                    fh.write(json.dumps(e, default=str) + "\n")
            print(f"updated {os.path.basename(path)}")

    if not scored:
        print("nothing new to review")
        return

    print(f"\nreviewed {reviewed} entries")
    print("=" * 92)
    for e, r in scored:
        print(f"  {e['as_of'][:16]} {e['instrument']:<7} {e['kind']:<10} "
              f"{str(e.get('direction')):<5} {e['state']:<8} -> "
              f"{r['outcome']:<15} r={r['r']:+5.2f} mfe={r['mfe_r']:.2f}R")

    filled = [r for _, r in scored if r["filled"]]
    if filled:
        tot = sum(r["r"] for r in filled)
        wins = [r for r in filled if r["outcome"] == "target"]
        mfes = [r["mfe_r"] for r in filled]
        print("\n" + "=" * 92)
        print(f"filled={len(filled)}  win={len(wins)}  totalR={tot:+.2f}  "
              f"median MFE={statistics.median(mfes):.2f}R")
        # The management question: losers that were well onside first.
        squandered = [r for r in filled
                      if r["outcome"] == "stop" and r["mfe_r"] >= 1.5]
        if squandered:
            print(f"  {len(squandered)} stopped trades reached >=1.5R first — "
                  f"that is management, not selection (reference 05)")
    by_kind = {}
    for e, r in scored:
        by_kind.setdefault(e["kind"], []).append(r)
    print("\nby kind")
    for k, rs in by_kind.items():
        f = [x for x in rs if x["filled"]]
        print(f"  {k:<12} n={len(rs):<3} filled={len(f):<3} "
              f"totalR={sum(x['r'] for x in f):+.2f}")


if __name__ == "__main__":
    main()
