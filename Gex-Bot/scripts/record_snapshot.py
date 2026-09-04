#!/usr/bin/env python3
"""
Record GexBot gamma snapshots as a time series.

Purpose: the GexBot Classic API returns only a *live* snapshot -- there is no
history endpoint on our tier, so past sessions are unrecoverable. This script
captures the levels as they happen so we can answer, from our own data, the
question the two source videos disagree on: does price respect the
VOLUME-derived walls or the OPEN-INTEREST-derived walls?

It therefore records BOTH readings on every sample, side by side, and takes no
view on which is correct.

Storage is a JSON Lines file per UTC day -- append-only, one line per
(ticker, scope) sample, trivially greppable and safe to interrupt.

Usage:
    python3 record_snapshot.py                      # default tickers/scopes
    python3 record_snapshot.py --tickers spx nq_ndx --scopes zero one
    python3 record_snapshot.py --out-dir /path/to/data
    python3 record_snapshot.py --stdout             # print, don't write

Exit codes: 0 ok (including "nothing new"), 1 all fetches failed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gexbot_client import GexBotClient, GexBotError  # noqa: E402

DEFAULT_TICKERS = ["spx", "nq_ndx", "es_spx", "ndx"]
DEFAULT_SCOPES = ["zero"]
DEFAULT_OUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data"
)


def build_record(snap, fetched_at: str) -> dict:
    """Flatten a snapshot into one comparable row.

    Both the _vol and _oi readings are kept. `sum_gex_*` sign is the regime
    call in Siento's framework, and the two can disagree -- that disagreement
    is exactly what we are here to measure, so it is recorded, not resolved.
    """
    raw = snap.raw
    return {
        # identity
        "fetched_at": fetched_at,
        "source_ts": snap.timestamp,
        "source_time": dt.datetime.fromtimestamp(
            snap.timestamp, dt.timezone.utc
        ).isoformat(),
        "ticker": snap.ticker,
        "scope": snap.scope,
        # price
        "spot": snap.spot,
        "zero_gamma": snap.zero_gamma,
        # the contested pair -- volume reading
        "major_pos_vol": snap.major_pos_vol,
        "major_neg_vol": snap.major_neg_vol,
        "sum_gex_vol": snap.sum_gex_vol,
        # the contested pair -- open-interest reading
        "major_pos_oi": snap.major_pos_oi,
        "major_neg_oi": snap.major_neg_oi,
        "sum_gex_oi": snap.sum_gex_oi,
        # context
        "min_dte": raw.get("min_dte"),
        "sec_min_dte": raw.get("sec_min_dte"),
        "delta_risk_reversal": snap.delta_risk_reversal,
        # the max-change panel: [strike, change] at 1/5/10/15/30 min lookbacks
        "max_priors": raw.get("max_priors"),
        # derived, for convenience when analysing
        "regime_vol": _sign(snap.sum_gex_vol),
        "regime_oi": _sign(snap.sum_gex_oi),
        "regimes_agree": _sign(snap.sum_gex_vol) == _sign(snap.sum_gex_oi),
        "walls_agree": (
            snap.major_pos_vol == snap.major_pos_oi
            and snap.major_neg_vol == snap.major_neg_oi
        ),
        "spot_vs_zero_gamma": (
            None if not snap.zero_gamma else _sign(snap.spot - snap.zero_gamma)
        ),
    }


def _sign(x) -> int:
    if x is None:
        return 0
    return (x > 0) - (x < 0)


def existing_keys(path: str) -> set:
    """(ticker, scope, source_ts) already recorded, so re-runs don't duplicate.

    The feed is static outside cash hours and can repeat a timestamp between
    polls, so this is load-bearing, not just tidiness.
    """
    keys = set()
    if not os.path.exists(path):
        return keys
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                keys.add((r["ticker"], r["scope"], r["source_ts"]))
            except (json.JSONDecodeError, KeyError):
                continue  # never let one bad line stop a recording run
    return keys


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--tickers", nargs="+", default=DEFAULT_TICKERS)
    ap.add_argument("--scopes", nargs="+", default=DEFAULT_SCOPES)
    ap.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    ap.add_argument("--stdout", action="store_true", help="print instead of writing")
    args = ap.parse_args()

    now = dt.datetime.now(dt.timezone.utc)
    fetched_at = now.isoformat()

    try:
        client = GexBotClient()
    except GexBotError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1

    records, failures = [], 0
    for ticker in args.tickers:
        for scope in args.scopes:
            try:
                records.append(build_record(client.gex(ticker, scope), fetched_at))
            except GexBotError as exc:
                # One bad symbol must not cost us the whole sample.
                print(f"WARN: {ticker}/{scope}: {exc}", file=sys.stderr)
                failures += 1

    if not records:
        print("FATAL: every fetch failed", file=sys.stderr)
        return 1

    if args.stdout:
        for r in records:
            print(json.dumps(r))
        return 0

    os.makedirs(args.out_dir, exist_ok=True)
    path = os.path.join(args.out_dir, f"{now:%Y-%m-%d}.jsonl")

    seen = existing_keys(path)
    fresh = [
        r for r in records if (r["ticker"], r["scope"], r["source_ts"]) not in seen
    ]

    if fresh:
        with open(path, "a", encoding="utf-8") as f:
            for r in fresh:
                f.write(json.dumps(r) + "\n")

    skipped = len(records) - len(fresh)
    print(
        f"{path}: +{len(fresh)} new"
        + (f", {skipped} unchanged" if skipped else "")
        + (f", {failures} failed" if failures else "")
    )

    # Surface disagreement as it happens -- this is the whole point.
    for r in fresh:
        if not r["regimes_agree"]:
            print(
                f"  NOTE {r['ticker']}/{r['scope']}: regime disagreement -- "
                f"vol {r['sum_gex_vol']:+,.0f} vs oi {r['sum_gex_oi']:+,.0f}"
            )
    return 0


if __name__ == "__main__":
    sys.exit(main())
