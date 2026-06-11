#!/usr/bin/env python3
"""
/Trend-Continuation-Agent — Orchestrator (main entry point)

Spec §1. Drives the scan pipeline (Sub-Agents 1-4) and the explicit
risk-sized execution flow (Execution Agent, spec §6).

This script performs all the deterministic numeric work — data retrieval,
gates, scoring, ranking, SL/TP/entry-zone calculation, and order placement —
and emits JSON. The invoking skill (see SKILL.md) renders that JSON into the
§9 trade-card format, including Claude's analytical commentary, and drives
the CONFIRM/CANCEL execution conversation.

Usage:
    python orchestrator.py [--symbols UK100,GER40,US500]
                            [--full-universe] [--full-universe-all]

    python orchestrator.py execute --card N --risk 450 [--confirm]
    python orchestrator.py execute --symbol UK100 --risk 450 [--confirm]

Must be run from the /Trend-Continuation-Agent directory (so `config` and
`utils`/`agents` resolve as top-level packages).
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime

import config
from agents import data_retrieval, execution, gate_layer, scoring_ranking, trade_card
from agents.data_retrieval import InstrumentData
from utils import mcp_client
from utils.time_utils import current_session, format_uk_full, now_utc

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
SCAN_OUTPUT_PATH = os.path.join(DATA_DIR, "last_scan.json")
SCAN_LOG_PATH = os.path.join(DATA_DIR, "last_scan.log")


def _json_default(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Not JSON serialisable: {type(obj)!r}")


# ── Universe construction (spec §12 deviation, see CLAUDE.md) ──────────────
def build_universe(args: argparse.Namespace) -> tuple[list[str], list[str]]:
    if args.symbols:
        symbols = [s.strip().upper() for s in args.symbols.split(",") if s.strip()]
    else:
        symbols = list(config.CORE_INSTRUMENTS)
        if args.full_universe or args.full_universe_all:
            symbols += [s for s in config.EXTENDED_UNIVERSE if s not in symbols]
        if args.full_universe_all:
            symbols += [s for s in mcp_client.list_base_names() if s not in symbols]

    skipped_known = [s for s in symbols if s in config.KNOWN_UNAVAILABLE]
    symbols = [s for s in symbols if s not in config.KNOWN_UNAVAILABLE]
    return symbols, skipped_known


def _summarise_log(log: list[str]) -> dict[str, int]:
    summary: dict[str, int] = {}
    for line in log:
        key = line.split(":", 1)[0]
        summary[key] = summary.get(key, 0) + 1
    return summary


# ── Scan pipeline (spec §1 steps 1-9) ───────────────────────────────────────
def run_scan(args: argparse.Namespace) -> tuple[dict, list[str]]:
    symbols, skipped_known = build_universe(args)
    print(f"/Trend-Continuation-Agent — scanning {len(symbols)} instruments...", file=sys.stderr)

    log: list[str] = [f"SKIPPED (known unavailable): {s}" for s in skipped_known]

    # Sub-Agent 1: Data Retrieval (sequential, per spec §2)
    data_by_symbol: dict[str, InstrumentData] = {}
    for i, symbol in enumerate(symbols, 1):
        result = data_retrieval.fetch_instrument(symbol, log)
        status = "ok" if result is not None else "skip"
        print(f"  [{i}/{len(symbols)}] {symbol}: {status}", file=sys.stderr)
        if result is not None:
            data_by_symbol[symbol] = result

    # Sub-Agent 2: Gate Layer (spec §3 / §7)
    gate_passed: list[tuple[InstrumentData, dict]] = []
    for symbol, data in data_by_symbol.items():
        gr = gate_layer.evaluate_gates(data)
        if gr["passed"]:
            gate_passed.append((data, gr))
        else:
            log.append(f"GATE_FAIL: {symbol} ({gr['fail_gate']})")

    # Sub-Agent 3: Scoring & Ranking (spec §4 / §8)
    scored: list[tuple[InstrumentData, dict]] = []
    for data, gr in gate_passed:
        sc = scoring_ranking.score_instrument(data, gr)
        if sc["tier"] is None:
            log.append(f"BELOW_WATCH: {data.symbol} (score={sc['total_score']})")
        else:
            scored.append((data, sc))

    by_symbol = {sc["symbol"]: data for data, sc in scored}
    ranking = scoring_ranking.rank_instruments([sc for _, sc in scored])

    # Sub-Agent 4: Trade Card maths (spec §5) for the top-10 ranked instruments
    ranked_plans = []
    for sc in ranking["ranked"]:
        data = by_symbol[sc["symbol"]]
        plan = trade_card.build_trade_plan(data, sc)
        ranked_plans.append({
            **plan,
            "sb_symbol": data.sb_symbol,
            "symbol_id": data.symbol_id,
            "point_size": data.point_size,
            "spot_bid": data.spot_bid,
            "spot_ask": data.spot_ask,
        })

    watchlist = [
        {
            "symbol": sc["symbol"],
            "direction": sc["direction"],
            "total_score": sc["total_score"],
            "scores": sc["scores"],
        }
        for sc in ranking["watchlist"]
    ]

    tier_a = sum(1 for _, sc in scored if sc["tier"] == "A")
    tier_b = sum(1 for _, sc in scored if sc["tier"] == "B")
    tier_c = len(watchlist)

    scan_time = now_utc()
    session_name, session_note = current_session(scan_time)

    output = {
        "scan_time_utc": scan_time,
        "scan_time_uk": format_uk_full(scan_time),
        "session": {"name": session_name, "note": session_note},
        "universe_count": len(symbols),
        "fetched_count": len(data_by_symbol),
        "gates_passed_count": len(gate_passed),
        "scored_count": tier_a + tier_b + tier_c,
        "tier_counts": {"A": tier_a, "B": tier_b, "C": tier_c},
        "ranked": ranked_plans,
        "watchlist": watchlist,
        "log_summary": _summarise_log(log),
    }
    return output, log


# ── Execution flow (spec §6) ────────────────────────────────────────────────
def run_execute(args: argparse.Namespace) -> dict:
    if not os.path.exists(SCAN_OUTPUT_PATH):
        return {"error": f"No scan results found at {SCAN_OUTPUT_PATH} — run a scan first."}

    with open(SCAN_OUTPUT_PATH) as f:
        scan = json.load(f)

    ranked = scan.get("ranked", [])
    plan = None
    if args.symbol:
        plan = next((p for p in ranked if p["symbol"].upper() == args.symbol.upper()), None)
    elif args.card:
        idx = args.card - 1
        if 0 <= idx < len(ranked):
            plan = ranked[idx]

    if plan is None:
        return {"error": "Trade card not found in the last scan. Specify --card N (1-3) or --symbol from that scan."}

    spot = mcp_client.get_spot_price(plan["symbol"])
    if spot is None:
        return {"error": f"Could not fetch a live price for {plan['symbol']}."}

    data = InstrumentData(
        symbol=plan["symbol"],
        sb_symbol=plan["sb_symbol"],
        symbol_id=plan["symbol_id"],
        point_size=plan["point_size"],
        bars_4h=[],
        bars_1h=[],
        spot_bid=spot[0],
        spot_ask=spot[1],
    )

    order_plan = execution.build_order_plan(data, plan, args.risk)
    issues = execution.validate_order_plan(order_plan)

    result: dict = {"order_plan": order_plan, "issues": issues}

    if args.confirm:
        if issues:
            result["result"] = {"error": "Not placed — resolve the issues above first."}
        else:
            result["result"] = execution.execute_order(order_plan)

    return result


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "execute":
        parser = argparse.ArgumentParser(prog="orchestrator.py execute")
        parser.add_argument("--card", type=int, help="Trade card number (1-based) from the last scan")
        parser.add_argument("--symbol", help="Instrument symbol from the last scan")
        parser.add_argument("--risk", type=float, required=True, help="Risk amount in GBP")
        parser.add_argument("--confirm", action="store_true", help="Place the order (omit for a dry-run confirmation)")
        args = parser.parse_args(sys.argv[2:])
        print(json.dumps(run_execute(args), indent=2, default=_json_default))
        return

    parser = argparse.ArgumentParser(prog="orchestrator.py")
    parser.add_argument("--symbols", help="Comma-separated instrument override (e.g. UK100,GER40,US500)")
    parser.add_argument("--full-universe", action="store_true", help="Also scan EXTENDED_UNIVERSE")
    parser.add_argument("--full-universe-all", action="store_true", help="Scan every enabled SB symbol (slow)")
    args = parser.parse_args(sys.argv[1:])

    output, log = run_scan(args)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(SCAN_OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2, default=_json_default)
    with open(SCAN_LOG_PATH, "w") as f:
        f.write("\n".join(log))

    print(json.dumps(output, indent=2, default=_json_default))


if __name__ == "__main__":
    main()
