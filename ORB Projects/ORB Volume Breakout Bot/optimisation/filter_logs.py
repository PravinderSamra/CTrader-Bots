#!/usr/bin/env python3
"""
Shrink a huge ORB Volume Breakout Bot cTrader log down to the lines that
carry analytical signal, so it can be attached to a chat / committed to git.

A 300 MB debug log is overwhelmingly per-bar noise (self-heal ticks, backfill
chatter, verbose diagnostics). Everything needed to reconstruct the trade
ledger AND the "why was no trade taken" decision tree lives in ~20 tags.

Usage
-----
    python filter_logs.py 2024.txt 2025.txt 2026.txt
    python filter_logs.py *.txt --outdir filtered

Writes <name>.filtered.txt next to each input (or into --outdir) and prints
the compression achieved.
"""
import argparse
import gzip
import io
import os
import re
import sys

# Ordered roughly by analytical value. Anything matching is kept verbatim.
KEEP_PATTERNS = [
    # --- trade lifecycle: the ledger itself ---
    r"TRADE ENTERED",
    r"ENTRY_DIAG",
    r"POSITION CLOSED",
    r"CLOSE_DIAG",
    r"partial close",
    r"CLOSE OK",
    # --- stop management: how winners were cut / losers reduced ---
    r"BREAK EVEN",
    r"TRAIL:",
    r"EARLY RISK REDUCTION",
    # --- the daily setup: range and signal ---
    r"ORB LOCKED",
    r"SIGNAL:",
    r"New day reset",
    # --- rejections: the counterfactual trades (why the filters fired) ---
    r"VOLUME FILTER",
    r"TREND_FILTER",
    r"Trend filter blocked",
    r"NO TRADE TODAY",
    r"ENTRY BLOCKED",
    r"SAFETY:",
    r"AMBIGUOUS",
    r"NEAR MISS",
    # --- execution quality / failures ---
    r"ORDER FAILED",
    r"EXECUTION_RISK",
    r"PROTECTION",
    r"SANITY",
    # --- config provenance: needed to trust the run ---
    r"SESSION_TIMEZONE",
    r"ORB Bot started",
    r"ORB Bot stopped",
    r"ERROR",
    r"WARNING",
]

KEEP_RE = re.compile("|".join(KEEP_PATTERNS))


def _open_maybe_gzip(path):
    """Read plain text or .gz transparently, tolerating cTrader's encoding."""
    if path.endswith(".gz"):
        raw = gzip.open(path, "rb")
    else:
        raw = open(path, "rb")
    return io.TextIOWrapper(raw, encoding="utf-8", errors="replace")


def filter_file(path, outdir=None, compress=False):
    base = os.path.basename(path)
    for ext in (".gz", ".txt", ".log"):
        if base.endswith(ext):
            base = base[: -len(ext)]
    out_name = base + ".filtered.txt" + (".gz" if compress else "")
    out_path = os.path.join(outdir or os.path.dirname(path) or ".", out_name)

    kept = total = 0
    opener = gzip.open if compress else open
    mode = "wt" if compress else "w"
    with _open_maybe_gzip(path) as fin, opener(out_path, mode, encoding="utf-8") as fout:
        for line in fin:
            total += 1
            if KEEP_RE.search(line):
                fout.write(line)
                kept += 1

    in_mb = os.path.getsize(path) / 1e6
    out_mb = os.path.getsize(out_path) / 1e6
    pct = (100.0 * kept / total) if total else 0.0
    print(
        f"{base:<28} {total:>10,} lines -> {kept:>8,} kept ({pct:5.2f}%)   "
        f"{in_mb:8.1f} MB -> {out_mb:6.2f} MB   {out_path}"
    )
    return out_path


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("logs", nargs="+", help="cTrader log files (.txt, .log or .gz)")
    ap.add_argument("--outdir", help="write filtered files here instead of alongside input")
    ap.add_argument("--gzip", action="store_true", dest="compress",
                    help="also gzip the output (use if still too big to attach)")
    args = ap.parse_args()

    if args.outdir:
        os.makedirs(args.outdir, exist_ok=True)

    missing = [p for p in args.logs if not os.path.isfile(p)]
    if missing:
        sys.exit("Not found: " + ", ".join(missing))

    for path in args.logs:
        filter_file(path, args.outdir, args.compress)


if __name__ == "__main__":
    main()
