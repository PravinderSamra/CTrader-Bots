#!/usr/bin/env python3
"""
JOURNAL REVIEW — grade what the confidence scores actually predicted.

Reads the entries `level_confidence.py --journal` wrote, walks price forward from
each entry's `as_of`, and records what really happened. Then aggregates so the
questions that matter become answerable from your own logged calls:

  * Do high scores actually win more than low ones? (Is the score worth anything?)
  * Does the positive-gamma "pinning" regime really produce higher hold rates?
  * Which score component is carrying the signal, and which is noise?

That last group is the point. Every weight in `score_level()` is currently a
judgement call. Nothing has validated them. This is the loop that eventually
does — and until it has run over enough entries, the score is a hypothesis with
a number attached, not a measurement.

The gamma answer in particular can ONLY come from here. There is no free
historical options chain, so a logged entry's `gamma` block is the only record
that a given regime existed at a given moment. Skip the journalling and that
question stays permanently unanswerable.

Usage
-----
    python3 journal_review.py                      # grade + summarise everything
    python3 journal_review.py --month 2026-08
    python3 journal_review.py --write              # persist outcomes back to the journal
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import statistics as stats
import sys
from collections import defaultdict
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ctrader_http import CTraderClient, CTraderError, iso  # noqa: E402
from level_confidence import parse_ts, resolve_symbol  # noqa: E402

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
JOURNAL_DIR = os.path.join(REPO, "trade-journal")
HORIZON_MIN = 60      # minutes to manage the trade once price arrives
TRIGGER_MIN = 300     # minutes the level call stays live waiting for price


def load(month: str | None, include_replays: bool = False) -> list[tuple[str, int, dict]]:
    """Live calls only by default.

    An --as-of replay is a useful check but it is NOT a real call: it was made
    with hindsight about which level to ask about, and its gamma layer is empty.
    Mixing replays into the calibration tables would quietly bias exactly the
    question the journal exists to answer.
    """
    pat = os.path.join(JOURNAL_DIR, f"{month}.jsonl" if month else "*.jsonl")
    out = []
    for path in sorted(glob.glob(pat)):
        with open(path) as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if e.get("source") != "gala-level-confidence":
                    continue
                if not include_replays and e.get("provenance") == "as_of_replay":
                    continue
                out.append((path, i, e))
    return out


def grade(entry: dict, bars: list[dict], trigger_window: int = TRIGGER_MIN,
          horizon: int = HORIZON_MIN) -> dict:
    """Walk M1 forward from as_of. Stop is checked before target, and assumed hit
    first within a bar — the same pessimistic convention the score was built on,
    so predicted and realised are measured the same way.

    Two separate clocks, and conflating them is wrong:
      trigger_window  how long the CALL stays valid — you marked a level and are
                      waiting for price to come to it, which can take hours.
      horizon         how long the TRADE is managed once price actually arrives.

    Using one 60-minute window for both marks a call as NEVER_TRIGGERED when
    price reached the level at minute 64 — which is a live setup, not a miss.
    """
    t0 = parse_ts(entry["as_of"])
    fwd = [b for b in bars if b["ts"] >= t0][:trigger_window]
    if not fwd:
        return {"state": "NO_DATA"}

    entry_px = entry["entry"]
    stop_px = entry["stop"]
    short = entry["direction"] == "short"
    risk = abs(stop_px - entry_px)
    if risk <= 0:
        return {"state": "BAD_ENTRY"}

    triggered = False
    trigger_idx = None
    best_r = 0.0
    for i, b in enumerate(fwd):
        if not triggered:
            # Price has to actually come back to the level for there to be a trade.
            if b["l"] <= entry_px <= b["h"]:
                triggered = True
                trigger_idx = i
            else:
                continue
        if i - trigger_idx > horizon:
            break
        if short:
            if b["h"] >= stop_px:
                return {"state": "STOPPED", "r": -1.0, "mfe_r": round(best_r, 2),
                        "triggered": True, "trigger_delay_min": trigger_idx}
            best_r = max(best_r, (entry_px - b["l"]) / risk)
        else:
            if b["l"] <= stop_px:
                return {"state": "STOPPED", "r": -1.0, "mfe_r": round(best_r, 2),
                        "triggered": True, "trigger_delay_min": trigger_idx}
            best_r = max(best_r, (b["h"] - entry_px) / risk)
        if best_r >= 3.0:
            return {"state": "TARGET", "r": 3.0, "mfe_r": round(best_r, 2),
                    "triggered": True, "trigger_delay_min": trigger_idx}
    if not triggered:
        return {"state": "NEVER_TRIGGERED", "r": None, "triggered": False}
    return {"state": "OPEN_AT_HORIZON", "r": round(min(best_r, 3.0), 2),
            "mfe_r": round(best_r, 2), "triggered": True,
            "trigger_delay_min": trigger_idx}


def summarise(rows: list[dict], key, label: str) -> list[str]:
    buckets: dict[str, list[dict]] = defaultdict(list)
    for r in rows:
        k = key(r)
        if k is not None:
            buckets[str(k)].append(r)
    out = [f"### By {label}", ""]
    out.append("| Bucket | n | Triggered | Win rate | Mean R |")
    out.append("|---|---|---|---|---|")
    for k, v in sorted(buckets.items()):
        trig = [x for x in v if x["outcome"].get("triggered")]
        if not trig:
            out.append(f"| {k} | {len(v)} | 0 | — | — |")
            continue
        wins = [x for x in trig if (x["outcome"].get("r") or 0) > 0]
        rs = [x["outcome"]["r"] for x in trig if x["outcome"].get("r") is not None]
        out.append(f"| {k} | {len(v)} | {len(trig)} | {len(wins)/len(trig)*100:.0f}% | "
                   f"{stats.mean(rs):+.2f}R |" if rs else f"| {k} | {len(v)} | {len(trig)} | — | — |")
    out.append("")
    return out


def score_band(r: dict) -> str:
    s = r["entry"].get("score", 0)
    if s >= 70:
        return "70+ (TAKE)"
    if s >= 50:
        return "50–69 (CAUTION)"
    if s >= 30:
        return "30–49 (WEAK)"
    return "<30 (SKIP)"


def main() -> int:
    p = argparse.ArgumentParser(description="Grade journalled level calls")
    p.add_argument("--month", default=None, help="YYYY-MM (default: all)")
    p.add_argument("--write", action="store_true", help="persist outcomes into the journal")
    p.add_argument("--include-replays", action="store_true",
                   help="also grade --as-of replay entries (excluded by default: they "
                        "are hindsight-selected and carry no gamma data)")
    p.add_argument("--out", default=None)
    args = p.parse_args()

    entries = load(args.month, args.include_replays)
    if not entries:
        print("No live gala-level-confidence entries found in trade-journal/.", file=sys.stderr)
        print("Run: level_confidence.py --level <price> --journal", file=sys.stderr)
        print("(--as-of replays are excluded; pass --include-replays to see them.)",
              file=sys.stderr)
        return 0
    print(f"Loaded {len(entries)} journalled level calls", file=sys.stderr)

    cli = CTraderClient()
    by_sym: dict[str, list] = defaultdict(list)
    for path, ln, e in entries:
        by_sym[e["instrument"]].append((path, ln, e))

    rows = []
    for sym, items in by_sym.items():
        sym_id, _ = resolve_symbol(cli, sym)
        lo = min(parse_ts(e["as_of"]) for _, _, e in items)
        hi = max(parse_ts(e["as_of"]) for _, _, e in items) + (TRIGGER_MIN + HORIZON_MIN) * 60_000
        bars = cli.trendbars(sym_id, "M_1", lo, hi)
        print(f"  {sym}: {len(bars)} M1 bars covering {iso(lo)} → {iso(hi)}", file=sys.stderr)
        for path, ln, e in items:
            rows.append({"path": path, "line": ln, "entry": e, "outcome": grade(e, bars)})

    L: list[str] = []
    a = L.append
    a("# Journal Review — level confidence calls")
    a("")
    a(f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M')}Z · "
      f"{len(rows)} calls · {TRIGGER_MIN}m trigger window · {HORIZON_MIN}m trade horizon")
    a("")

    trig = [r for r in rows if r["outcome"].get("triggered")]
    if trig:
        rs = [r["outcome"]["r"] for r in trig if r["outcome"].get("r") is not None]
        wins = [r for r in trig if (r["outcome"].get("r") or 0) > 0]
        a(f"- Triggered: **{len(trig)}/{len(rows)}**")
        a(f"- Win rate: **{len(wins)/len(trig)*100:.0f}%** · mean **{stats.mean(rs):+.2f}R**")
        a("")

    a("## Does the score predict anything?")
    a("")
    a("If the score is worth keeping, win rate and mean R should rise with the band.")
    a("If they don't, the weights in `score_level()` need changing — or dropping.")
    a("")
    L += summarise(rows, score_band, "score band")

    a("## The gamma question")
    a("")
    a("The hypothesis: positive net gamma → dealers hedge against moves → levels hold")
    a("more often. This table is the only way it can ever be tested, because no free")
    a("historical options chain exists to backtest it against.")
    a("")
    L += summarise(rows, lambda r: (r["entry"].get("gamma") or {}).get("regime"), "gamma regime")
    L += summarise(rows, lambda r: r["entry"].get("day_bias"), "day bias")
    L += summarise(rows, lambda r: r["entry"].get("session"), "session")
    L += summarise(rows, lambda r: r["entry"].get("direction"), "direction")

    a("## Every call")
    a("")
    a("| as_of | Level | Dir | Score | Verdict | Predicted | Outcome |")
    a("|---|---|---|---|---|---|---|")
    for r in sorted(rows, key=lambda x: x["entry"]["as_of"]):
        e, o = r["entry"], r["outcome"]
        pred = f"{e['history']['expectancy_r']:+.2f}R (n={e['history']['n']})"
        res = o["state"] + (f" {o['r']:+.1f}R" if o.get("r") is not None else "")
        a(f"| {e['as_of'][:16]} | {e['level']:,.2f} | {e['direction']} | {e['score']:.0f} | "
          f"{e['verdict']} | {pred} | {res} |")
    a("")

    n_trig = len(trig)
    if n_trig < 20:
        a(f"> ⚠️ **{n_trig} triggered calls is not enough to conclude anything.** These")
        a("> tables are wired up and correct, but treat them as plumbing until the sample")
        a("> is meaningful — 30+ per bucket before you change how you trade on them.")
        a("")

    report = "\n".join(L)
    print(report)

    if args.write:
        by_file: dict[str, dict[int, dict]] = defaultdict(dict)
        for r in rows:
            by_file[r["path"]][r["line"]] = r["outcome"]
        for path, updates in by_file.items():
            with open(path) as f:
                lines = f.readlines()
            for ln, outcome in updates.items():
                try:
                    obj = json.loads(lines[ln])
                except (json.JSONDecodeError, IndexError):
                    continue
                obj["outcome"] = outcome
                obj["reviewed_at"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
                lines[ln] = json.dumps(obj) + "\n"
            with open(path, "w") as f:
                f.writelines(lines)
            print(f"Updated {len(updates)} outcomes in {path}", file=sys.stderr)

    if args.out:
        with open(args.out, "w") as f:
            f.write(report + "\n")
        print(f"Wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except CTraderError as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
