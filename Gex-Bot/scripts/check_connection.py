#!/usr/bin/env python3
"""
Phase 1 connectivity check for the GexBot API.

Verifies, in order:
  1. the token is present in the environment
  2. the API host is reachable (public /tickers endpoint)
  3. the token authenticates against a protected endpoint
  4. a real gamma snapshot comes back with sane values
  5. the tickers this project cares about are all accessible

Usage:
    export GEX_BOT_API_TOKEN=...
    python3 check_connection.py
    python3 check_connection.py --ticker nq_ndx --scope zero

Exit code 0 = all checks passed.
"""

from __future__ import annotations

import argparse
import datetime as dt
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gexbot_client import (  # noqa: E402
    SCOPES,
    TOKEN_ENV_VAR,
    GexBotAuthError,
    GexBotClient,
    GexBotError,
)

# Symbols this project trades or references.
KEY_TICKERS = ["spx", "ndx", "nq_ndx", "es_spx", "spy", "qqq", "vix"]

PASS, FAIL, INFO = "PASS", "FAIL", "  ->"


def line(status: str, msg: str) -> None:
    print(f"[{status}] {msg}" if status in (PASS, FAIL) else f"{status} {msg}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ticker", default="spx", help="ticker for the snapshot check")
    ap.add_argument("--scope", default="zero", choices=SCOPES)
    args = ap.parse_args()

    failures = 0

    print("=" * 62)
    print("GexBot API connectivity check")
    print("=" * 62)

    # 1. token present
    token = os.environ.get(TOKEN_ENV_VAR)
    if not token:
        line(FAIL, f"{TOKEN_ENV_VAR} is not set in the environment")
        return 1
    line(PASS, f"{TOKEN_ENV_VAR} found ({len(token)} chars)")

    try:
        client = GexBotClient()
    except GexBotAuthError as exc:
        line(FAIL, str(exc))
        return 1

    # 2. host reachable via the public endpoint
    try:
        tickers = client.tickers()
    except GexBotError as exc:
        line(FAIL, f"API unreachable: {exc}")
        return 1
    total = sum(len(v) for v in tickers.values())
    line(PASS, f"API reachable -- /tickers lists {total} symbols")
    for group, syms in tickers.items():
        line(INFO, f"{group}: {len(syms)}")

    # 3 + 4. authenticated snapshot
    try:
        snap = client.gex(args.ticker, args.scope)
    except GexBotAuthError as exc:
        line(FAIL, f"Authentication failed: {exc}")
        return 1
    except GexBotError as exc:
        line(FAIL, f"Snapshot request failed: {exc}")
        return 1

    line(PASS, f"Token authenticated -- fetched {snap.ticker} classic/{snap.scope}")

    age = dt.datetime.now(dt.timezone.utc) - dt.datetime.fromtimestamp(
        snap.timestamp, dt.timezone.utc
    )
    stamp = dt.datetime.fromtimestamp(snap.timestamp, dt.timezone.utc).isoformat()
    line(INFO, f"snapshot time : {stamp} ({int(age.total_seconds())}s old)")
    line(INFO, f"spot          : {snap.spot}")
    line(INFO, f"call wall (+G): {snap.call_wall}")
    line(INFO, f"put wall  (-G): {snap.put_wall}")
    line(INFO, f"zero gamma    : {snap.zero_gamma}")
    line(INFO, f"sum gex (OI)  : {snap.sum_gex_oi}")
    line(INFO, f"sum gex (vol) : {snap.sum_gex_vol}")
    line(INFO, f"strikes       : {len(snap.strikes)}")

    # sanity: spot must be positive and inside the strike ladder
    if snap.spot <= 0:
        line(FAIL, "spot price is not positive -- payload looks wrong")
        failures += 1
    elif snap.strikes:
        lo, hi = snap.strikes[0][0], snap.strikes[-1][0]
        if lo <= snap.spot <= hi:
            line(PASS, f"payload sane -- spot {snap.spot} sits inside ladder {lo}-{hi}")
        else:
            line(FAIL, f"spot {snap.spot} outside strike ladder {lo}-{hi}")
            failures += 1

    if snap.sum_gex_vol == 0:
        line(INFO, "note: volume-based fields are 0 -- expected outside US cash hours")

    # 5. project tickers
    print("-" * 62)
    print("Access check on project tickers:")
    for tk in KEY_TICKERS:
        try:
            s = client.gex(tk, "zero")
            line(PASS, f"{tk:<8} spot={s.spot:<12} +G={s.call_wall:<12} -G={s.put_wall}")
        except GexBotError as exc:
            line(FAIL, f"{tk:<8} {exc}")
            failures += 1

    print("=" * 62)
    if failures:
        print(f"RESULT: {failures} check(s) FAILED")
        return 1
    print("RESULT: all checks passed -- GexBot connectivity confirmed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
