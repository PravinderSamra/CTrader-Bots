"""
Skill Adapter — bridges live cTrader MCP trendbar data (already fetched inside
a Claude Code session via mcp__ctrader__get_trendbars) into this repo's
existing ICT/SMC analysis engine (analysis/structure.py, analysis/sessions.py).

Used by .claude/commands/gold-session.md. Does not touch analysis/ — so the
"keep Local and Remote agents in sync" rule in CLAUDE.md does not apply here.

Usage:
    python3 skill_adapter.py < input.json > output.json

Input JSON (prices already converted to display units, not pipettes):
{
  "symbol": "XAUUSD",
  "current_price": 2375.50,
  "h1": [{"timestamp": "2025-01-01T00:00:00Z", "open": 0, "high": 0, "low": 0, "close": 0, "volume": 0}, ...],
  "m5": [...],
  "m1": [...]
}

Output JSON: computed trend, premium/discount, FVGs, order blocks, liquidity
pools, volume profile, Asian range, and session/kill-zone context for each
timeframe supplied. Pure read-only computation — no network calls, no trading.
"""

import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.models import Candle
from analysis import structure, sessions


def _parse_candles(raw_candles: list, timeframe: str, symbol: str) -> list[Candle]:
    candles = []
    for bar in raw_candles:
        try:
            ts_raw = bar["timestamp"]
            if isinstance(ts_raw, (int, float)):
                ts = datetime.fromtimestamp(ts_raw / 1000 if ts_raw > 1_000_000_000_000 else ts_raw, tz=timezone.utc)
            else:
                ts = datetime.fromisoformat(str(ts_raw).replace("Z", "+00:00"))
            candles.append(Candle(
                timestamp=ts,
                open=float(bar["open"]),
                high=float(bar["high"]),
                low=float(bar["low"]),
                close=float(bar["close"]),
                volume=float(bar.get("volume", 0) or 0),
                timeframe=timeframe,
                symbol=symbol,
            ))
        except (KeyError, TypeError, ValueError):
            continue
    candles.sort(key=lambda c: c.timestamp)
    return candles


def _fvg_to_dict(f) -> dict:
    return {
        "direction": f.direction,
        "gap_low": f.gap_low,
        "gap_high": f.gap_high,
        "ce": (f.gap_low + f.gap_high) / 2.0,
        "formed_at": f.formed_at.strftime("%Y-%m-%dT%H:%M:%SZ") if f.formed_at else None,
        "candles_ago": f.candles_ago,
        "age_label": f.age_label,
        "grade": f.probability_grade,
        "touch_count": f.touch_count,
        "partial_fill_pct": round(f.partial_fill_pct, 1),
        "context_flags": f.context_flags,
    }


def _ob_to_dict(ob) -> dict:
    return {
        "direction": ob.direction,
        "ob_low": ob.ob_low,
        "ob_high": ob.ob_high,
        "formed_at": ob.formed_at.strftime("%Y-%m-%dT%H:%M:%SZ") if ob.formed_at else None,
        "quality": ob.quality,
        "preceded_by_liq_grab": ob.preceded_by_liq_grab,
    }


def _liq_to_dict(p) -> dict:
    return {
        "direction": p.direction,
        "price": p.price,
        "test_count": p.test_count,
        "strength": p.strength,
    }


def _analyse_timeframe(candles: list[Candle], include_volume_profile: bool = False, include_asian: bool = False) -> dict:
    if not candles:
        return {}

    current_price = candles[-1].close
    result: dict = {
        "candle_count": len(candles),
        "trend": structure.detect_trend(candles, lookback=min(20, len(candles) - 1)) if len(candles) > 1 else "NEUTRAL",
        "premium_discount": structure.calculate_premium_discount(candles, lookback=min(50, len(candles))),
        "fvgs": [_fvg_to_dict(f) for f in structure.detect_fvgs(candles)[:10]],
        "order_blocks": [_ob_to_dict(ob) for ob in structure.detect_order_blocks(candles)[:10]],
        "liquidity_pools": [_liq_to_dict(p) for p in structure.find_liquidity_pools(candles, current_price)],
    }

    if include_volume_profile:
        vp = structure.approximate_volume_profile(candles)
        if vp:
            result["volume_profile"] = vp

    if include_asian:
        asian = structure.find_asian_range(candles)
        if asian:
            result["asian_range"] = asian
            result["asian_range_note"] = structure.asian_range_note(
                asian.get("asian_high"), asian.get("asian_low"), asian.get("asian_swept")
            )

    return result


def main():
    payload = json.load(sys.stdin)
    symbol = payload.get("symbol", "XAUUSD")
    current_price = payload.get("current_price")

    h1 = _parse_candles(payload.get("h1", []), "1h", symbol)
    m5 = _parse_candles(payload.get("m5", []), "5m", symbol)
    m1 = _parse_candles(payload.get("m1", []), "1m", symbol)

    if not h1 or not m5 or not m1:
        print(json.dumps({"error": "Missing or unparsable h1/m5/m1 candle data — cannot analyse."}), file=sys.stdout)
        sys.exit(1)

    if current_price is None:
        current_price = m1[-1].close

    h1_ctx = _analyse_timeframe(h1, include_volume_profile=True, include_asian=True)
    m5_ctx = _analyse_timeframe(m5)
    m1_ctx = _analyse_timeframe(m1)

    asian = h1_ctx.get("asian_range", {})
    bias_notes = sessions.session_bias_note(
        asian.get("asian_swept"), asian.get("midnight_open"), current_price
    )

    output = {
        "symbol": symbol,
        "current_price": current_price,
        "session": {
            "current_session": sessions.current_session(),
            "active_kill_zone": sessions.active_kill_zone(),
            "minutes_until_kz_closes": sessions.minutes_until_kill_zone_closes(),
            "bias_notes": bias_notes,
        },
        "h1": h1_ctx,
        "m5": m5_ctx,
        "m1": m1_ctx,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
