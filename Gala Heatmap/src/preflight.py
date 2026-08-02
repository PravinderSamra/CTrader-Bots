#!/usr/bin/env python3
"""
PREFLIGHT — verify a fresh session can actually run the level-confidence stack.

Checks everything the scoring path depends on and prints a pass/fail line each,
so a session that is about to fail four minutes into an M1 pull finds out in
twenty seconds instead.

    python3 "Gala Heatmap/src/preflight.py"

Exit code 0 = ready, 1 = something required is broken.
"""

from __future__ import annotations

import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

OK, WARN, FAIL = "  ok  ", " warn ", " FAIL "
results: list[tuple[str, str, str]] = []


def check(label: str, fn, required: bool = True) -> None:
    t0 = time.time()
    try:
        detail = fn() or ""
        results.append((OK, label, f"{detail}  ({time.time()-t0:.1f}s)"))
    except Exception as e:                       # noqa: BLE001 — report anything
        results.append((FAIL if required else WARN, label, str(e)[:150]))


def c_python():
    v = sys.version_info
    if v < (3, 10):
        raise RuntimeError(f"Python {v.major}.{v.minor} — need 3.10+")
    return f"Python {v.major}.{v.minor}.{v.micro}"


def c_stdlib_only():
    import importlib
    for m in ("ctrader_http", "pivots", "level_stats", "gold_context",
              "level_confidence", "journal_review"):
        importlib.import_module(m)
    return "all 6 modules import (stdlib only)"


def c_layout():
    repo = os.path.dirname(os.path.dirname(HERE))
    missing = [p for p in ("Gala Heatmap/src", "trade-journal")
               if not os.path.isdir(os.path.join(repo, p))]
    if missing:
        raise RuntimeError(f"missing {missing} under {repo}")
    return f"repo root {repo}"


def c_token():
    tok = (os.environ.get("CTRADER_MCP_SLUG") or os.environ.get("CTRADER_MCP_TOKEN") or "").strip()
    if not tok:
        raise RuntimeError("CTRADER_MCP_SLUG / CTRADER_MCP_TOKEN not set")
    return f"token present ({len(tok)} chars)"


def c_ctrader():
    from ctrader_http import CTraderClient
    from level_stats import resolve_symbol
    cli = CTraderClient()
    data = cli.symbols()
    syms = data.get("symbols") or []
    variants = [(s.get("symbolId"), s.get("symbolName")) for s in syms
                if "XAUUSD" in (s.get("symbolName") or "").upper()]
    if not variants:
        raise RuntimeError("connected, but no XAUUSD instrument on this account")
    sid, sname = resolve_symbol(cli, "XAUUSD")
    if "-F" in sname.upper():
        raise RuntimeError(f"resolved to {sname}, which tracks futures not spot")
    return (f"{len(syms):,} symbols · {len(variants)} XAUUSD variants · "
            f"resolves to {sname} (id {sid})")


def c_freshness():
    from ctrader_http import CTraderClient, now_ms
    cli = CTraderClient()
    bars = cli.trendbars(241, "H_1", now_ms() - 5 * 86_400_000, now_ms())
    if not bars:
        raise RuntimeError("no XAUUSD H1 bars in the last 5 days")
    age_h = (now_ms() - bars[-1]["ts"]) / 3_600_000
    if age_h > 30:
        raise RuntimeError(f"newest bar is {age_h:.1f}h old — market closed or feed stale")
    return f"{len(bars)} H1 bars, newest {age_h:.1f}h old"


def c_yahoo_futures():
    import gold_context as gc
    bars = gc.yahoo_ohlcv("GC=F", "5d", "5m")
    vol = sum(b["v"] for b in bars)
    if vol <= 0:
        raise RuntimeError("GC=F returned no volume")
    return f"GC=F {len(bars)} 5m bars, {vol:,} contracts"


def c_cboe():
    import gold_context as gc
    d = gc.cboe_chain("GLD")
    n = len(d.get("options") or [])
    if n < 100:
        raise RuntimeError(f"only {n} contracts returned")
    return f"GLD chain {n:,} contracts, underlying {d.get('close')}"


def c_cftc():
    import gold_context as gc
    rows = gc.cftc_gold(1)
    if not rows:
        raise RuntimeError("no COT rows")
    return f"latest report {rows[0]['date']}"


def c_journal():
    repo = os.path.dirname(os.path.dirname(HERE))
    d = os.path.join(repo, "trade-journal")
    os.makedirs(d, exist_ok=True)
    if not os.access(d, os.W_OK):
        raise RuntimeError(f"{d} is not writable")
    return f"{d} writable"


def main() -> int:
    print("Preflight — gala-level-confidence\n" + "=" * 62)
    check("Python version", c_python)
    check("Module imports", c_stdlib_only)
    check("Repo layout", c_layout)
    check("cTrader token", c_token)
    check("cTrader connection", c_ctrader)
    # Not required: a closed market is normal at weekends, and the tool warns.
    check("Market data freshness", c_freshness, required=False)
    check("Yahoo futures (GC=F)", c_yahoo_futures, required=False)
    check("CBOE options (GLD)", c_cboe, required=False)
    check("CFTC COT", c_cftc, required=False)
    check("Journal writable", c_journal)

    for status, label, detail in results:
        print(f"[{status}] {label:<24} {detail}")

    fails = [r for r in results if r[0] == FAIL]
    warns = [r for r in results if r[0] == WARN]
    print("=" * 62)
    if fails:
        print(f"NOT READY — {len(fails)} required check(s) failed.")
        print("The scoring path will not run until these are resolved.")
        return 1
    if warns:
        print(f"READY, with {len(warns)} degraded layer(s).")
        print("Scoring will run; the affected components report as unavailable and")
        print("the score is capped rather than silently scoring zero.")
        return 0
    print("READY — all layers available.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
