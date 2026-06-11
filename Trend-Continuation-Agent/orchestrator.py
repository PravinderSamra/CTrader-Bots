#!/usr/bin/env python3
"""
/Trend-Continuation-Agent — Orchestrator (main entry point)

Spec §1 (swing pipeline) / Day Trade Pipeline Upgrade v1.1 §6 (day trade
pipeline). Drives both scan pipelines (Sub-Agents 1-4) and the explicit
risk-sized execution flow (Execution Agent, spec §6 / v1.1 §5).

This script performs all the deterministic numeric work — data retrieval,
gates, scoring, ranking, SL/TP/entry-zone calculation, and order placement —
and emits JSON. The invoking skill (see SKILL.md) renders that JSON into the
§9 / v1.1 §4 trade-card format, including Claude's analytical commentary, and
drives the CONFIRM/CANCEL execution conversation.

Usage:
    python orchestrator.py [--symbols UK100,GER40,US500]
                            [--full-universe] [--full-universe-all]

    python orchestrator.py execute [--pipeline {swing,day}] --card N --risk 450 [--confirm]
    python orchestrator.py execute [--pipeline {swing,day}] --symbol UK100 --risk 450 [--confirm]

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


def _enrich_plan(data: InstrumentData, plan: dict, pipeline: str) -> dict:
    return {
        **plan,
        "pipeline": pipeline,
        "sb_symbol": data.sb_symbol,
        "symbol_id": data.symbol_id,
        "point_size": data.point_size,
        "spot_bid": data.spot_bid,
        "spot_ask": data.spot_ask,
    }


def _watchlist_entry(sc: dict, pipeline: str) -> dict:
    return {
        "pipeline": pipeline,
        "symbol": sc["symbol"],
        "direction": sc["direction"],
        "total_score": sc["total_score"],
        "scores": sc["scores"],
    }


# ── Day trade universe selection (v1.1 §2.5/§2.4) ───────────────────────────
def _day_trade_symbols(data_by_symbol: dict[str, InstrumentData], log: list[str]) -> list[str]:
    """DAY_TRADE_UNIVERSE instruments that were fetched as part of the swing
    scan (no second 4H/1H fetch — v1.1 §6.2 step 4). Crypto symbols are
    flagged (and excluded from this run) if the live spread exceeds 0.15% of
    price (v1.1 §2.5)."""
    symbols: list[str] = []
    for symbol in config.DAY_TRADE_UNIVERSE:
        data = data_by_symbol.get(symbol)
        if data is None:
            continue
        if symbol in ("BTCUSD", "ETHUSD") and data.spot_bid:
            spread_pct = abs(data.spot_ask - data.spot_bid) / data.spot_bid * 100
            if spread_pct > 0.15:
                log.append(f"WIDE_SPREAD_DAY: {symbol} (spread={spread_pct:.3f}% of price)")
                continue
        symbols.append(symbol)
    return symbols


# ── Scan pipeline (spec §1 / v1.1 §6.2) ─────────────────────────────────────
def run_scan(args: argparse.Namespace) -> tuple[dict, list[str]]:
    symbols, skipped_known = build_universe(args)
    print(f"/Trend-Continuation-Agent — scanning {len(symbols)} instruments...", file=sys.stderr)

    log: list[str] = [f"SKIPPED (known unavailable): {s}" for s in skipped_known]

    # Sub-Agent 1: Data Retrieval (sequential, per spec §2) — 4H + 1H bars,
    # shared by both pipelines (v1.1 §6.2 steps 1-2).
    data_by_symbol: dict[str, InstrumentData] = {}
    for i, symbol in enumerate(symbols, 1):
        result = data_retrieval.fetch_instrument(symbol, log)
        status = "ok" if result is not None else "skip"
        print(f"  [{i}/{len(symbols)}] {symbol}: {status}", file=sys.stderr)
        if result is not None:
            data_by_symbol[symbol] = result

    # ── Swing pipeline (spec §3-§5, unchanged) ────────────────────────────────
    gate_passed: list[tuple[InstrumentData, dict]] = []
    for symbol, data in data_by_symbol.items():
        gr = gate_layer.evaluate_gates(data)
        if gr["passed"]:
            gate_passed.append((data, gr))
        else:
            log.append(f"GATE_FAIL: {symbol} ({gr['fail_gate']})")

    scored: list[tuple[InstrumentData, dict]] = []
    for data, gr in gate_passed:
        sc = scoring_ranking.score_instrument(data, gr)
        if sc["tier"] is None:
            log.append(f"BELOW_WATCH: {data.symbol} (score={sc['total_score']})")
        else:
            scored.append((data, sc))

    swing_by_symbol = {sc["symbol"]: data for data, sc in scored}
    swing_ranking = scoring_ranking.rank_instruments([sc for _, sc in scored])

    swing_ranked_plans = []
    for sc in swing_ranking["ranked"]:
        data = swing_by_symbol[sc["symbol"]]
        plan = trade_card.build_trade_plan(data, sc)
        swing_ranked_plans.append(_enrich_plan(data, plan, "swing"))

    swing_watchlist = [_watchlist_entry(sc, "swing") for sc in swing_ranking["watchlist"]]

    swing_tier_a = sum(1 for _, sc in scored if sc["tier"] == "A")
    swing_tier_b = sum(1 for _, sc in scored if sc["tier"] == "B")
    swing_tier_c = len(swing_watchlist)

    swing_output = {
        "universe_count": len(symbols),
        "gates_passed_count": len(gate_passed),
        "scored_count": swing_tier_a + swing_tier_b + swing_tier_c,
        "tier_counts": {"A": swing_tier_a, "B": swing_tier_b, "C": swing_tier_c},
        "ranked": swing_ranked_plans,
        "watchlist": swing_watchlist,
    }

    # ── Day trade pipeline (v1.1 §3) ──────────────────────────────────────────
    day_symbols = _day_trade_symbols(data_by_symbol, log)
    print(f"/Trend-Continuation-Agent — day trade gate pre-filter on {len(day_symbols)} instruments...", file=sys.stderr)

    day_gate_passed: list[tuple[InstrumentData, dict]] = []
    for symbol in day_symbols:
        data = data_by_symbol[symbol]
        gr = gate_layer.day_trade_gates(data)
        if gr["passed"]:
            day_gate_passed.append((data, gr))
        else:
            log.append(f"DAY_GATE_FAIL: {symbol} ({gr['fail_gate']})")

    # 15M bars fetched ONLY for day-trade-gate-passed instruments (v1.1 §2.4).
    day_scored: list[tuple[InstrumentData, dict]] = []
    for data, gr in day_gate_passed:
        bars_15m = data_retrieval.fetch_15m_bars(data.symbol, log)
        if bars_15m is None:
            continue
        sc = scoring_ranking.score_day_trade(data, gr, bars_15m)
        if sc["tier"] is None:
            log.append(f"BELOW_WATCH_DAY: {data.symbol} (score={sc['total_score']})")
        else:
            day_scored.append((data, sc))

    day_by_symbol = {sc["symbol"]: data for data, sc in day_scored}
    day_ranking = scoring_ranking.rank_instruments([sc for _, sc in day_scored])

    day_ranked_plans = []
    for sc in day_ranking["ranked"]:
        data = day_by_symbol[sc["symbol"]]
        plan = trade_card.build_day_trade_plan(data, sc)
        day_ranked_plans.append(_enrich_plan(data, plan, "day"))

    day_watchlist = [_watchlist_entry(sc, "day") for sc in day_ranking["watchlist"]]

    day_tier_a = sum(1 for _, sc in day_scored if sc["tier"] == "A")
    day_tier_b = sum(1 for _, sc in day_scored if sc["tier"] == "B")
    day_tier_c = len(day_watchlist)

    day_output = {
        "universe_count": len(day_symbols),
        "gates_passed_count": len(day_gate_passed),
        "scored_count": day_tier_a + day_tier_b + day_tier_c,
        "tier_counts": {"A": day_tier_a, "B": day_tier_b, "C": day_tier_c},
        "ranked": day_ranked_plans,
        "watchlist": day_watchlist,
    }

    scan_time = now_utc()
    session_name, session_note = current_session(scan_time)

    output = {
        "scan_time_utc": scan_time,
        "scan_time_uk": format_uk_full(scan_time),
        "session": {"name": session_name, "note": session_note},
        "fetched_count": len(data_by_symbol),
        "swing": swing_output,
        "day": day_output,
        "log_summary": _summarise_log(log),
    }
    return output, log


# ── Execution flow (spec §6 / v1.1 §5) ──────────────────────────────────────
def run_execute(args: argparse.Namespace) -> dict:
    if not os.path.exists(SCAN_OUTPUT_PATH):
        return {"error": f"No scan results found at {SCAN_OUTPUT_PATH} — run a scan first."}

    with open(SCAN_OUTPUT_PATH) as f:
        scan = json.load(f)

    pipeline_output = scan.get(args.pipeline)
    if pipeline_output is None:
        return {"error": f"No '{args.pipeline}' results in the last scan — run a scan first."}

    ranked = pipeline_output.get("ranked", [])
    plan = None
    if args.symbol:
        plan = next((p for p in ranked if p["symbol"].upper() == args.symbol.upper()), None)
    elif args.card:
        idx = args.card - 1
        if 0 <= idx < len(ranked):
            plan = ranked[idx]

    if plan is None:
        return {"error": f"Trade card not found in the last scan's '{args.pipeline}' results. Specify --card N or --symbol from that scan."}

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
    warnings = execution.order_plan_warnings(order_plan)
    issues += execution.check_margin(order_plan)

    result: dict = {"order_plan": order_plan, "issues": issues, "warnings": warnings}

    if args.confirm:
        if issues:
            result["result"] = {"error": "Not placed — resolve the issues above first."}
        elif args.retry_tps:
            if not order_plan["split_tps"]:
                result["result"] = {"error": "split_tps is false for this plan — nothing to retry."}
            else:
                result["result"] = execution.place_tp_legs(order_plan)
        else:
            result["result"] = execution.execute_order(order_plan)

    return result


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "execute":
        parser = argparse.ArgumentParser(prog="orchestrator.py execute")
        parser.add_argument("--pipeline", choices=["swing", "day"], default="swing", help="Which pipeline's ranked list to read (default: swing)")
        parser.add_argument("--card", type=int, help="Trade card number (1-based) from the last scan")
        parser.add_argument("--symbol", help="Instrument symbol from the last scan")
        parser.add_argument("--risk", type=float, required=True, help="Risk amount in GBP")
        parser.add_argument("--confirm", action="store_true", help="Place the order (omit for a dry-run confirmation)")
        parser.add_argument("--retry-tps", action="store_true", help="Skip the MARKET order and only (re)place the TP2/TP3 LIMIT legs for an already-open position")
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
