#!/usr/bin/env python3
"""
RSI-ADX Rejection Scanner — full watchlist sweep via direct cTrader MCP HTTP client.

Pulls M15 trendbars for every instrument in the watchlist, runs each through the
RSI/ADX/rejection analyser (indicators.py), and prints a compact per-instrument
summary plus a shortlist of first-pass candidates (the "Step 1" gate from
AgentSkill.md: RSI extreme + ADX declining-from-peak + matching rejection wick).

Usage:
    python3 scan.py                      # full 32-instrument sweep, M15
    python3 scan.py --classes forex,metals
    python3 scan.py --period H_1 --hours 200
"""

import sys
import json
import argparse
import time
from datetime import datetime, timedelta, timezone

from ctrader_client import call_tool, close
import indicators as ind

WATCHLIST = [
    ("EURUSD",   185,  "forex"),
    ("GBPUSD",   199,  "forex"),
    ("USDJPY",   226,  "forex"),
    ("USDCHF",   222,  "forex"),
    ("USDCAD",   221,  "forex"),
    ("AUDUSD",   158,  "forex"),
    ("NZDUSD",   211,  "forex"),
    ("GBPJPY",   192,  "forex"),
    ("EURJPY",   177,  "forex"),
    ("AUDJPY",   155,  "forex"),
    ("EURGBP",   175,  "forex"),
    ("GBPAUD",   189,  "forex"),
    ("EURCAD",   172,  "forex"),
    ("GBPCAD",   190,  "forex"),
    ("US500",    220,  "indices"),
    ("NAS100",   205,  "indices"),
    ("US30",     219,  "indices"),
    ("GER40",    200,  "indices"),
    ("UK100",    217,  "indices"),
    ("FRA40",    188,  "indices"),
    ("EUSTX50",  187,  "indices"),
    ("JPN225",   203,  "indices"),
    ("AUS200",   159,  "indices"),
    ("HK50",     201,  "indices"),
    ("XAUUSD",   241,  "metals"),
    ("XAGUSD",   238,  "metals"),
    ("WTOIL-PERP",    7328, "commodities"),
    ("BRENTOIL-PERP", 7329, "commodities"),
    ("NatGas",   254,  "commodities"),
    ("BTCUSD",   160,  "crypto"),
    ("ETHUSD",   170,  "crypto"),
    ("SOLUSD",   1616, "crypto"),
]


def iso(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def fetch_and_analyse(name, symbol_id, period, from_ts, to_ts):
    raw = call_tool("get_trendbars", {
        "symbolId": symbol_id,
        "period": period,
        "fromTimestamp": from_ts,
        "toTimestamp": to_ts,
    })
    if not raw or "trendbars" not in raw:
        return {"symbol": name, "error": "fetch_failed", "raw": raw}

    raw["symbol"] = name
    try:
        return ind.analyse(raw, name)
    except Exception as e:
        return {"symbol": name, "error": f"analysis_failed: {e}"}


def first_pass_signal(summary):
    if "error" in summary:
        return None
    rsi, adx, rej = summary["rsi"], summary["adx"], summary["rejection"]
    if rsi["oversold"] and adx.get("exhaustion_signal") and rej["type"] == "bullish_rejection":
        return "LONG"
    if rsi["overbought"] and adx.get("exhaustion_signal") and rej["type"] == "bearish_rejection":
        return "SHORT"
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--classes", default="", help="Comma-separated asset classes to include (default: all)")
    ap.add_argument("--period", default="M_15", choices=["M_5", "M_15", "M_30", "H_1", "H_4", "D_1"])
    ap.add_argument("--hours", type=int, default=30, help="How many hours of history to pull")
    args = ap.parse_args()

    classes = set(c.strip().lower() for c in args.classes.split(",") if c.strip())
    watchlist = [w for w in WATCHLIST if not classes or w[2] in classes]

    to_dt = datetime.now(timezone.utc)
    from_dt = to_dt - timedelta(hours=args.hours)
    from_ts, to_ts = iso(from_dt), iso(to_dt)

    print(f"# RSI-ADX scan — {len(watchlist)} instruments — {args.period} — "
          f"{from_ts} -> {to_ts}\n", file=sys.stderr)

    results = []
    candidates = []
    for i, (name, sid, cls) in enumerate(watchlist, 1):
        summary = fetch_and_analyse(name, sid, args.period, from_ts, to_ts)
        results.append((name, cls, summary))

        signal = first_pass_signal(summary)
        if signal:
            candidates.append((name, cls, signal, summary))

        # Progress line to stderr so stdout stays clean JSON-per-line
        if "error" in summary:
            print(f"[{i:>2}/{len(watchlist)}] {name:<14} ERROR: {summary['error']}", file=sys.stderr)
        else:
            r, a, rj = summary["rsi"], summary["adx"], summary["rejection"]
            tag = f" <-- {signal} CANDIDATE" if signal else ""
            print(f"[{i:>2}/{len(watchlist)}] {name:<14} RSI {r['value']:>5} | "
                  f"ADX {a.get('value')!s:>5} (peak {a.get('recent_peak')!s:>5}, "
                  f"{'declining' if a.get('declining_from_peak') else 'not declining'}) | "
                  f"rejection: {rj['type']:<18}{tag}", file=sys.stderr)

        time.sleep(0.3)  # gentle pacing — avoid hammering the load-balanced backend

    close()

    print(json.dumps({
        "scan_period": args.period,
        "from": from_ts,
        "to": to_ts,
        "candidates": [
            {"symbol": n, "class": c, "direction": d, "summary": s} for n, c, d, s in candidates
        ],
        "all_results": [
            {"symbol": n, "class": c, "summary": s} for n, c, s in results
        ],
    }, indent=2))


if __name__ == "__main__":
    main()
