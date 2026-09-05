#!/usr/bin/env python3
"""
Download GexBot's end-of-day report for a ticker.

Why this exists: the Classic *live* endpoint serves only a current snapshot,
which led to an early wrong conclusion that history was unavailable at all
(see ../research/volume-vs-open-interest.md). It is not. `/hist/eod/{TICKER}`
returns a zip of the last completed session at 1-2 second resolution with the
full strike ladder on every sample -- roughly 15,000 samples a day, against
the recorder's 78.

Two limits, both verified rather than assumed:
  * The `date` query parameter is IGNORED. Every date returns the same file;
    confirmed by reading content-disposition, which names the latest session
    whatever is asked for. So this must run daily to build an archive.
  * The dated archive `/v2/hist/{TICKER}/{PACKAGE}/{CATEGORY}/{DATE}` returns
    403 on the Classic package -- that one is genuinely gated to Quant.

Usage:
    python3 fetch_eod.py --ticker nq_ndx --out-dir /path/to/archive
    python3 fetch_eod.py --ticker nq_ndx --stdout-summary
"""

from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import os
import re
import sys
import urllib.error
import urllib.request
import zipfile

BASE_URL = "https://api.gex.bot"
TOKEN_ENV_VAR = "GEX_BOT_API_TOKEN"
DEFAULT_TIMEOUT = 300  # the payload is ~20 MB


class EodError(RuntimeError):
    pass


def download(ticker: str, token: str | None = None,
             timeout: int = DEFAULT_TIMEOUT) -> tuple[bytes, str]:
    """Fetch the EOD zip. Returns (bytes, server-supplied filename)."""
    token = token or os.environ.get(TOKEN_ENV_VAR)
    if not token:
        raise EodError(f"{TOKEN_ENV_VAR} is not set.")

    req = urllib.request.Request(
        f"{BASE_URL}/hist/eod/{ticker.lower()}",
        headers={"Authorization": f"Bearer {token}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            blob = resp.read()
            disp = resp.headers.get("content-disposition", "")
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", "replace")[:300]
        raise EodError(f"HTTP {exc.code} for {ticker}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise EodError(f"Could not reach {BASE_URL}: {exc.reason}") from exc

    # The server names the session it actually served. Trust that over any
    # date we might have asked for, since the date parameter is ignored.
    m = re.search(r'filename=([^;]+)', disp)
    name = m.group(1).strip('"') if m else f"eod_report_{ticker.upper()}.zip"
    return blob, name


def summarise(blob: bytes) -> dict:
    """Describe the archive without holding every sample in memory at once."""
    z = zipfile.ZipFile(__import__("io").BytesIO(blob))
    out: dict = {"files": [], "sessions": {}}
    for name in z.namelist():
        out["files"].append({"name": name, "size": z.getinfo(name).file_size})
        if not name.endswith(".json.gz"):
            continue
        samples = json.loads(gzip.decompress(z.read(name)))
        if not isinstance(samples, list) or not samples:
            continue
        ts = [s["timestamp"] for s in samples]
        out["sessions"][name.split("/")[-1]] = {
            "samples": len(samples),
            "first": dt.datetime.fromtimestamp(min(ts), dt.timezone.utc).isoformat(),
            "last": dt.datetime.fromtimestamp(max(ts), dt.timezone.utc).isoformat(),
            "strikes": len(samples[0].get("strikes", [])),
        }
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ticker", default="nq_ndx")
    ap.add_argument("--out-dir", default=None,
                    help="where to save the zip (default: Gex-Bot/data/eod)")
    ap.add_argument("--stdout-summary", action="store_true",
                    help="describe the archive instead of saving it")
    args = ap.parse_args()

    try:
        blob, name = download(args.ticker)
    except EodError as exc:
        print(f"FATAL: {exc}", file=sys.stderr)
        return 1

    if args.stdout_summary:
        print(json.dumps(summarise(blob), indent=2))
        return 0

    out_dir = args.out_dir or os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "eod")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)

    if os.path.exists(path) and os.path.getsize(path) == len(blob):
        print(f"{name}: already held, unchanged ({len(blob):,} bytes)")
        return 0

    with open(path, "wb") as f:
        f.write(blob)
    print(f"{path}: {len(blob):,} bytes")
    return 0


if __name__ == "__main__":
    sys.exit(main())
