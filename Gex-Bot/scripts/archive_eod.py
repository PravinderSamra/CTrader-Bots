#!/usr/bin/env python3
"""
Download a session's EOD report, derive what the research needs, store that.

The raw report is ~20 MB of paid vendor data per ticker per day. It is
deliberately NOT kept: this repository is public, and a Firestore document
caps at 1 MiB anyway. What is kept is two things, both small:

  * the session's agreement statistics and a touch-test parameter sweep
  * a downsampled series of spot and the four wall levels

The series is the important choice. Storing only summary statistics would
freeze today's analysis parameters into the archive forever; keeping spot and
the walls every `--step` seconds means the touch test can be re-run later with
any tolerance or horizon, on every session ever archived, without re-fetching
anything. At 10-second steps a full session is a few thousand rows -- well
inside the document cap, and the whole point is that one session was never
going to be enough (see ../research/volume-vs-open-interest.md).

Usage:
    python3 archive_eod.py --ticker nq_ndx --firestore
    python3 archive_eod.py --ticker nq_ndx --stdout
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import io
import json
import os
import sys
import zipfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from analyse_vol_vs_oi import agreement, analyse, base_rate  # noqa: E402
from fetch_eod import EodError, download  # noqa: E402

SESSIONS_COLLECTION = "gex_sessions"

# Parameters the touch test is swept over, so a later reader can see the
# result was not one lucky setting. Widening tolerance mostly just admits
# more marginal touches; if a real edge exists it should survive the sweep.
SWEEP = [(5, 15), (10, 15), (25, 15), (50, 5)]


def derive(samples: list[dict], step_s: int) -> dict:
    ts = [s["timestamp"] for s in samples]
    spots = [s["spot"] for s in samples]
    day = dt.datetime.fromtimestamp(ts[0], dt.timezone.utc)

    series, last = [], 0
    for s in samples:
        if s["timestamp"] - last < step_s:
            continue
        last = s["timestamp"]
        series.append({
            "t": s["timestamp"],
            "spot": s["spot"],
            "pv": s.get("major_pos_vol", 0),
            "nv": s.get("major_neg_vol", 0),
            "po": s.get("major_pos_oi", 0),
            "no": s.get("major_neg_oi", 0),
            "zg": s.get("zero_gamma", 0),
            "gv": s.get("sum_gex_vol", 0),
            "go": s.get("sum_gex_oi", 0),
        })

    sweep = []
    for tol, cooldown in SWEEP:
        sweep.append({
            "tol": tol, "cooldown": cooldown, "horizon": 15,
            "walls": analyse(samples, tol, 15, cooldown, 15),
        })

    return {
        "ticker": samples[0]["ticker"],
        "date": day.strftime("%Y-%m-%d"),
        "samples": len(samples),
        "first_ts": ts[0],
        "last_ts": ts[-1],
        "open": spots[0], "close": spots[-1],
        "high": max(spots), "low": min(spots),
        "agreement": agreement(samples),
        "baseline_15m": base_rate(samples, 15 * 60, 15),
        "sweep": sweep,
        "series_step_s": step_s,
        "series": series,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ticker", default="nq_ndx")
    ap.add_argument("--scope", default="gex_zero")
    ap.add_argument("--step", type=int, default=10, help="series step, seconds")
    ap.add_argument("--firestore", action="store_true")
    ap.add_argument("--stdout", action="store_true")
    ap.add_argument("--zip", default=None, help="use a local zip instead of fetching")
    args = ap.parse_args()

    if args.zip:
        blob = open(args.zip, "rb").read()
    else:
        try:
            blob, _ = download(args.ticker)
        except EodError as exc:
            print(f"FATAL: {exc}", file=sys.stderr)
            return 1

    z = zipfile.ZipFile(io.BytesIO(blob))
    names = [n for n in z.namelist() if args.scope in n and n.endswith(".json.gz")]
    if not names:
        print(f"FATAL: no {args.scope} in report", file=sys.stderr)
        return 1
    samples = json.loads(gzip.decompress(z.read(names[0])))
    samples.sort(key=lambda s: s["timestamp"])

    doc = derive(samples, args.step)
    size = len(json.dumps(doc))
    print(f"{doc['ticker']} {doc['date']}: {doc['samples']:,} samples -> "
          f"{len(doc['series']):,} series rows, {size/1024:.0f} KB derived")

    if size > 900_000:
        # Firestore's hard cap is 1 MiB; fail loudly rather than half-write.
        print("FATAL: derived doc too large; raise --step", file=sys.stderr)
        return 1

    if args.stdout:
        print(json.dumps({k: v for k, v in doc.items() if k != "series"}, indent=2))

    if args.firestore:
        from firestore_sink import FirestoreError, FirestoreSink
        try:
            sink = FirestoreSink()
            doc_id = f"{doc['ticker']}_{args.scope}_{doc['date']}"
            sink.commit([sink.make_write(SESSIONS_COLLECTION, doc_id, doc)])
            print(f"Firestore: wrote {SESSIONS_COLLECTION}/{doc_id}")
        except FirestoreError as exc:
            print(f"FATAL: {exc}", file=sys.stderr)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
