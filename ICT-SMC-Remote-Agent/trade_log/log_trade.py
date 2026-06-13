"""
Trade Log — persistent record of every setup recommended by the ICT/SMC
Remote Agent and every trade the user actually takes.

File: trade_log/trades.json (JSON array of trade records, newest last)

Schema (all fields present; use None/null if not applicable):
  trade_id              str   "YYYYMMDD-INSTRUMENT-DIRECTION" (append "-2", "-3"
                              if more than one same-day setup for a symbol+direction)
  scan_timestamp_utc    str   ISO timestamp of the scan that produced this setup
  logged_at_utc         str   ISO timestamp when this record was first created
  instrument            str   e.g. "GBPCAD"
  direction             str   "LONG" | "SHORT"
  fvg_type              str   "Bullish FVG" | "Bearish FVG"
  timeframe             str   e.g. "1h"
  fvg_low               float
  fvg_high              float
  grade                 str   e.g. "B (A+ capped - trend split)"
  confluence_score      str   e.g. "7/9"
  entry_price           float
  stop_loss             float
  tp1                   float | None
  tp1_rr                float | None
  tp_primary            float | None
  tp_primary_rr         float | None
  tp3                   float | None
  tp3_rr                float | None
  recommendation_status str   "recommended" | "watch_only" | "not_recommended"
  recommendation_notes  str
  action_status         str   "taken" | "not_taken"
  order_id              int | None
  position_id           int | None
  order_volume          int | None
  order_type            str | None
  outcome_status        str   "pending" | "filled_open" | "expired_unfilled" |
                               "would_not_have_filled" | "closed_win" |
                               "closed_loss" | "closed_breakeven"
  outcome_notes         str
  pnl_usd               float | None
  last_reviewed_utc     str | None

Usage (from sub-agents):

    import sys
    sys.path.insert(0, '/home/user/CTrader-Bots/ICT-SMC-Remote-Agent')
    from trade_log.log_trade import add_trade, update_trade, get_pending_trades

    add_trade({...})                 # append new record (or merge if trade_id exists)
    update_trade(trade_id, {...})    # merge updates into an existing record
    get_pending_trades()             # records needing an outcome review
"""

import json
import os
from datetime import datetime, timezone

_LOG_PATH = os.path.join(os.path.dirname(__file__), "trades.json")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_log() -> list:
    if not os.path.exists(_LOG_PATH):
        return []
    with open(_LOG_PATH) as f:
        return json.load(f)


def save_log(records: list) -> None:
    with open(_LOG_PATH, "w") as f:
        json.dump(records, f, indent=2)
        f.write("\n")


def add_trade(record: dict) -> dict:
    """Append a new record, or merge into an existing one with the same trade_id."""
    records = load_log()
    record.setdefault("logged_at_utc", _now())
    for existing in records:
        if existing.get("trade_id") == record.get("trade_id"):
            existing.update(record)
            save_log(records)
            return existing
    records.append(record)
    save_log(records)
    return record


def update_trade(trade_id: str, updates: dict) -> dict:
    """Merge updates into an existing record, stamping last_reviewed_utc."""
    records = load_log()
    for existing in records:
        if existing.get("trade_id") == trade_id:
            existing.update(updates)
            existing["last_reviewed_utc"] = _now()
            save_log(records)
            return existing
    raise ValueError(f"No trade found with trade_id={trade_id}")


def get_pending_trades() -> list:
    """Records whose outcome still needs to be reviewed against price history."""
    return [r for r in load_log() if r.get("outcome_status") in ("pending", "filled_open")]


def get_all_trades() -> list:
    return load_log()
