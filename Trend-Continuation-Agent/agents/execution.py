"""
/Trend-Continuation-Agent — Execution Agent

Spec §6. Explicitly invoked only — never fires automatically. Computes
risk-based stake sizing and the pre-execution confirmation block, then (only
once the user has typed CONFIRM) places the market order with SL/TP1, plus
TP2/TP3 as separate limit "close" legs.

Rendering of the confirmation block / final report is done by the
orchestrating skill (see SKILL.md) from the dicts returned here.
"""

from __future__ import annotations

from config import BROKER_MIN_VOLUME, BROKER_VOLUME_STEP
from agents.data_retrieval import InstrumentData
from utils import mcp_client
from utils.position_sizing import calc_stake


def build_order_plan(data: InstrumentData, plan: dict, risk_amount: float) -> dict:
    """Pure calculation — no MCP calls. Produces everything needed for the
    pre-execution confirmation block (spec §6)."""
    direction = plan["direction"]
    trade_side = "BUY" if direction == "LONG" else "SELL"
    close_side = "SELL" if direction == "LONG" else "BUY"

    # calc_stake works in "broker points" (the £/pt unit from the symbol's
    # "bet in 1 GBP per (X)" description, e.g. 0.0001 for AUDUSD, 1.0 for
    # UK100) — convert the raw price-distance SL into that unit. See
    # CLAUDE.md "Implementation Notes" (position sizing / point_size).
    point_size = data.point_size or 1.0
    sl_distance_points = plan["sl_distance"] / point_size
    sizing = calc_stake(risk_amount, sl_distance_points, point_size)
    entry_price = data.spot_ask if trade_side == "BUY" else data.spot_bid

    # Spec §6 steps 3-4: TP2 and TP3 close volume/3 each as separate limit
    # orders; the remainder stays on the position with TP1. If a third of
    # the stake would round below the broker's £1/pt-equivalent step for
    # this symbol (CLAUDE.md item 14), skip the split and let TP1 cover the
    # full position (see CLAUDE.md item 5).
    volume_step = int(round(BROKER_VOLUME_STEP / point_size))
    tp23_volume = (sizing["volume"] // 3 // volume_step) * volume_step
    split_tps = tp23_volume > 0
    tp1_volume = sizing["volume"] - (2 * tp23_volume if split_tps else 0)

    return {
        "symbol": data.symbol,
        "sb_symbol": data.sb_symbol,
        "symbol_id": data.symbol_id,
        "direction": direction,
        "trade_side": trade_side,
        "close_side": close_side,
        "entry_price": entry_price,
        "sl": plan["sl"],
        "sl_distance": plan["sl_distance"],
        "sl_distance_points": sl_distance_points,
        "tp1": plan["tp1"],
        "tp2": plan["tp2"],
        "tp3": plan["tp3"],
        "tp1_points": plan["tp1_points"],
        "risk_amount": risk_amount,
        "sizing": sizing,
        "tp1_volume": tp1_volume,
        "tp23_volume": tp23_volume,
        "split_tps": split_tps,
    }


def validate_order_plan(order_plan: dict) -> list[str]:
    """Spec §6 "Execution Error Handling" pre-checks. Returns a list of
    blocking issues (empty if the order is safe to place)."""
    issues: list[str] = []
    sizing = order_plan["sizing"]

    if sizing["below_minimum"]:
        issues.append(
            f"Stake £{sizing['broker_stake']:.2f}/pt is below the broker minimum "
            f"(£{BROKER_MIN_VOLUME / 100:.2f}/pt) — adjust risk or skip this trade."
        )

    direction = order_plan["direction"]
    entry = order_plan["entry_price"]
    sl = order_plan["sl"]
    if direction == "LONG" and entry <= sl:
        issues.append("Price has moved through the SL level — trade no longer valid. Abort.")
    elif direction == "SHORT" and entry >= sl:
        issues.append("Price has moved through the SL level — trade no longer valid. Abort.")

    return issues


def execute_order(order_plan: dict) -> dict:
    """Places the order(s) via cTrader MCP. Caller MUST have already shown
    the confirmation block and received an explicit 'CONFIRM' (spec §6:
    "Never execute an order without the explicit confirmation step")."""
    issues = validate_order_plan(order_plan)
    if issues:
        return {"error": " / ".join(issues)}

    symbol = order_plan["symbol"]
    sl_raw = mcp_client.to_raw_points(symbol, order_plan["sl_distance"])
    tp1_raw = mcp_client.to_raw_points(symbol, order_plan["tp1_points"])

    market_resp = mcp_client.create_market_order(
        symbol_id=order_plan["symbol_id"],
        trade_side=order_plan["trade_side"],
        volume=order_plan["sizing"]["volume"],
        relative_sl_points=sl_raw,
        relative_tp_points=tp1_raw,
    )
    if not market_resp:
        return {"error": "MCP create_order (MARKET) — no response from cTrader MCP (transport/session failure). Check get_positions before retrying."}
    if isinstance(market_resp, dict) and (market_resp.get("error") or market_resp.get("errorCode")):
        return {"error": market_resp.get("error", market_resp)}

    result: dict = {"market_order": market_resp}

    if order_plan["split_tps"]:
        for label, tp_price in (("tp2_order", order_plan["tp2"]), ("tp3_order", order_plan["tp3"])):
            result[label] = mcp_client.create_limit_order(
                symbol_id=order_plan["symbol_id"],
                trade_side=order_plan["close_side"],
                volume=order_plan["tp23_volume"],
                limit_price=tp_price,
            )

    return result
