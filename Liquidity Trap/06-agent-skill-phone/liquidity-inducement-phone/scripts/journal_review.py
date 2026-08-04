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

def _find_journal():
    """Locate trade-journal/ by walking up from this file.

    Counting ".." hops was wrong once already (it landed on
    "Liquidity Trap/trade-journal" and the review silently reported "no
    journal files"), and the count differs again in the .claude/skills
    mirror. Searching upward works from either copy.
    """
    d = os.path.dirname(os.path.abspath(__file__))
    while True:
        cand = os.path.join(d, "trade-journal")
        if os.path.isdir(cand):
            return cand
        parent = os.path.dirname(d)
        if parent == d:
            return cand          # not found: report the top-level guess
        d = parent


DEFAULT_JOURNAL = _find_journal()
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


def excursion(bars, ref, direction):
    """Favourable and adverse excursion, in points, from a reference price.

    Returns (favourable, adverse, edge) where edge = favourable - adverse.

    Favourable excursion ALONE is worthless and actively misleading, which is
    why adverse is returned beside it. Reviewing two ideas logged at the same
    moment on the same instrument — one long, one short — gave +71.4 and +49.2
    respectively. Both cannot have been the right read. All that number was
    measuring was the day's range: over a 30h window, a wide-ranging session
    hands a flattering figure to whichever direction you happened to write
    down. Reading it as "the direction was right, the entry was wrong" was a
    real mistaken conclusion drawn from exactly that.

    `edge` is the honest single number: it only goes positive when price spent
    more of its extent in the idea's favour than against it.

    Always pass the FULL forward window, never the post-trigger slice. Slicing
    made the figure non-monotonic: one entry reclassified from never_triggered
    to watch_only on a later review and its excursion *fell* from +5.0 to
    +2.4pts on strictly more data, because the measurement window had silently
    moved. Same anchor, same window, every time — otherwise two reviews of the
    same entry are not comparable.
    """
    if not bars or ref is None or direction not in ("long", "short"):
        return None, None, None
    hi = max(b["high"] for b in bars)
    lo = min(b["low"] for b in bars)
    fav, adv = (hi - ref, ref - lo) if direction == "long" else (ref - lo, hi - ref)
    return round(fav, 3), round(adv, 3), round(fav - adv, 3)


def _set_excursion(out, bars, entry, direction):
    fav, adv, edge = excursion(bars, entry.get("price_at_idea"), direction)
    out["excursion_pts"] = fav
    out["adverse_pts"] = adv
    out["edge_pts"] = edge


def score(entry, bars):
    """Walk forward from as_of and decide what became of this idea.

    Every result carries `max_rr_reached` and `verdict`, including the ones
    that never filled — the reporting reads those fields unconditionally.
    """
    out = _score_raw(entry, bars)
    if out is None:
        return None
    out.setdefault("mfe_r", 0.0)
    out["max_rr_reached"] = out["mfe_r"]
    out["verdict"] = verdict_for(out)
    return out


def _score_raw(entry, bars):
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
            _set_excursion(out, fwd, entry, direction)
            return out
    rest = fwd[i:]

    # Without a concrete entry/stop the idea was a watch, not a plan: record
    # whether it triggered and what the excursion was, but not an R figure.
    if not (entry_zone and stop and target and direction):
        out["outcome"] = "watch_only"
        _set_excursion(out, fwd, entry, direction)
        return out

    fill_i = None
    for j, b in enumerate(rest):
        if in_zone(b, entry_zone):
            fill_i = j
            break
    if fill_i is None:
        out["outcome"] = "no_fill"
        _set_excursion(out, fwd, entry, direction)
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


# How far in favour a trade must run before the direction is credited. A trade
# that never clears 0.3R never worked; one that clears 1R was right and was
# then given back. The gap between those two numbers is the whole argument for
# managing rather than letting it run.
DIRECTION_RIGHT = 1.0
DIRECTION_MARGINAL = 0.3


def verdict_for(r):
    """Was the IDEA right, separately from whether the destination was hit?"""
    if r["outcome"] == "target":
        return "target_hit"
    if not r.get("filled"):
        return "not_taken"
    mfe = r.get("mfe_r", 0.0)
    if mfe >= DIRECTION_RIGHT:
        # Direction and entry were right; only the exit failed.
        return "direction_right_destination_missed"
    if mfe >= DIRECTION_MARGINAL:
        return "direction_marginal"
    return "direction_wrong"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("instrument", nargs="?",
                    help="only review entries for this instrument")
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

    print(f"journal: {args.journal}")
    print(f"files:   {', '.join(os.path.basename(f) for f in files)}")

    reviewed, scored, too_recent = 0, [], []
    for path in files:
        lines = [l for l in open(path).read().splitlines() if l.strip()]
        entries = [json.loads(l) for l in lines]
        changed = False
        for e in entries:
            if e.get("review"):
                continue
            if args.instrument and e["instrument"] != args.instrument:
                continue
            bars = bars_for(e["instrument"], args.days)
            if not bars:
                print(f"  ! no bars for {e['instrument']}: {ct.last_error()}")
                continue
            r = score(e, bars)
            if r is None:
                too_recent.append(e)   # no forward bars yet
                continue
            e["review"] = r
            changed = True
            reviewed += 1
            scored.append((e, r))
        if changed and args.write:
            with open(path, "w") as fh:
                for e in entries:
                    fh.write(json.dumps(e, default=str) + "\n")
            print(f"updated {os.path.basename(path)}")

    if too_recent:
        print(f"\n{len(too_recent)} entries too recent to judge (no bars after "
              f"as_of yet): "
              + ", ".join(e["id"] for e in too_recent))

    if not scored:
        print("nothing new to review")
        return

    # An idea logged minutes ago has barely any forward data; saying so beats
    # presenting a 20-minute look-ahead as a verdict.
    thin = [e["id"] for e, r in scored if r["bars_available"] < 24]
    if thin:
        print(f"\nWARNING: {len(thin)} entries have <2h of forward data — "
              f"their verdicts are provisional: " + ", ".join(thin))

    print(f"\nreviewed {reviewed} entries")
    print("=" * 92)
    for e, r in scored:
        exc, adv, edge = (r.get("excursion_pts"), r.get("adverse_pts"),
                          r.get("edge_pts"))
        tail = (f"{r.get('verdict', '-')}" if r["filled"]
                else (f"unfilled  fav={exc:+.1f} adv={adv:+.1f} "
                      f"edge={edge:+.1f}pts"
                      if exc is not None else "unfilled"))
        print(f"  {e['as_of'][:16]} {e['instrument']:<7} {e['kind']:<11} "
              f"{str(e.get('direction')):<5} {e['state']:<8} -> "
              f"{r['outcome']:<15} r={r['r']:+5.2f} "
              f"maxRR={r.get('max_rr_reached', 0):.2f}R  {tail}")

    filled = [r for _, r in scored if r["filled"]]
    if filled:
        tot = sum(r["r"] for r in filled)
        wins = [r for r in filled if r["outcome"] == "target"]
        mfes = [r["mfe_r"] for r in filled]
        print("\n" + "=" * 92)
        print(f"filled={len(filled)}  win={len(wins)}  totalR={tot:+.2f}  "
              f"median MFE={statistics.median(mfes):.2f}R")
        # The management question: losers that were well onside first.
        # The question this journal exists to answer: when a trade lost, was
        # the IDEA wrong, or only the exit?
        losers = [r for r in filled if r["outcome"] != "target"]
        if losers:
            right = [r for r in losers
                     if r["verdict"] == "direction_right_destination_missed"]
            marg = [r for r in losers if r["verdict"] == "direction_marginal"]
            wrong = [r for r in losers if r["verdict"] == "direction_wrong"]
            print("\nWHY THE LOSERS LOST")
            rr_list = ", ".join(f"{r['mfe_r']:.1f}R" for r in right) or "-"
            print(f"  direction right, destination missed : {len(right):<3}"
                  f"  (max RR reached: {rr_list})")
            print(f"  direction marginal (0.3-1.0R)       : {len(marg)}")
            print(f"  direction wrong (<0.3R)             : {len(wrong)}")
            if right:
                give_back = sum(r["mfe_r"] for r in right)
                print(f"\n  {len(right)}/{len(losers)} losses were correct calls that were "
                      f"given back.")
                print(f"  Those trades showed {give_back:.1f}R of unrealised profit in "
                      f"total before stopping for {len(right)}R of loss.")
                print("  That is an exit problem, not a selection problem "
                      "(reference 05).")
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
