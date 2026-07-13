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
from analysis import structure, sessions, patterns


def _parse_candles(raw_candles: list, timeframe: str, symbol: str) -> list[Candle]:
    candles = []
    skipped = 0
    for bar in raw_candles:
        try:
            ts_raw = bar["timestamp"]
            if isinstance(ts_raw, (int, float)):
                ts = datetime.fromtimestamp(ts_raw / 1000 if ts_raw > 1_000_000_000_000 else ts_raw, tz=timezone.utc)
            elif isinstance(ts_raw, str) and ts_raw.strip().lstrip("-").isdigit():
                # Numeric string e.g. "1782684000000" — treat as ms epoch
                ts_int = int(ts_raw)
                ts = datetime.fromtimestamp(ts_int / 1000 if abs(ts_int) > 1_000_000_000_000 else ts_int, tz=timezone.utc)
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
            skipped += 1
            continue
    if skipped:
        print(
            f"[skill_adapter] WARNING: skipped {skipped}/{len(raw_candles)} candles"
            f" in {timeframe} due to parse errors",
            file=sys.stderr,
        )
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


def _reference_levels(d1: list[Candle]) -> dict:
    """
    Standing ICT reference liquidity from daily candles: previous day high/low,
    previous (completed) week high/low, and today's daily open. The last d1
    candle is treated as the current (possibly partial) day.
    """
    if not d1 or len(d1) < 2:
        return {}

    out: dict = {
        "daily_open":    d1[-1].open,
        "prev_day_high": d1[-2].high,
        "prev_day_low":  d1[-2].low,
    }

    # Previous completed ISO week high/low.
    weeks: dict = {}
    for c in d1:
        y, w, _ = c.timestamp.isocalendar()
        weeks.setdefault((y, w), []).append(c)
    keys = sorted(weeks.keys())
    if len(keys) >= 2:
        prev_week = weeks[keys[-2]]
        out["prev_week_high"] = max(c.high for c in prev_week)
        out["prev_week_low"]  = min(c.low  for c in prev_week)

    return out


def _smt_divergence(xau_m5: list[Candle], proxy_m5: list[Candle]) -> str | None:
    """
    Smart-Money-Technique divergence between XAUUSD and a positively-correlated
    USD proxy (EURUSD — both rise as the dollar weakens).

      Gold prints a LOWER low while the proxy prints a HIGHER low  → BULLISH SMT
        (gold's new low is unconfirmed by USD strength — likely a false break).
      Gold prints a HIGHER high while the proxy prints a LOWER high → BEARISH SMT.

    Returns "BULLISH" / "BEARISH" / None. Needs ≥2 confirmed swings per side.
    """
    if len(xau_m5) < 6 or len(proxy_m5) < 6:
        return None

    x_highs, x_lows = structure.find_swing_points(xau_m5)
    p_highs, p_lows = structure.find_swing_points(proxy_m5)

    if len(x_lows) >= 2 and len(p_lows) >= 2:
        gold_ll  = x_lows[-1][1] < x_lows[-2][1]
        proxy_hl = p_lows[-1][1] > p_lows[-2][1]
        if gold_ll and proxy_hl:
            return "BULLISH"

    if len(x_highs) >= 2 and len(p_highs) >= 2:
        gold_hh  = x_highs[-1][1] > x_highs[-2][1]
        proxy_lh = p_highs[-1][1] < p_highs[-2][1]
        if gold_hh and proxy_lh:
            return "BEARISH"

    return None


def _analyse_timeframe(candles: list[Candle], include_volume_profile: bool = False, include_asian: bool = False) -> dict:
    if not candles:
        return {}

    current_price = candles[-1].close
    trend = structure.detect_trend(candles, lookback=min(20, len(candles) - 1)) if len(candles) > 1 else "NEUTRAL"
    result: dict = {
        "candle_count": len(candles),
        "trend": trend,
        # Pass the trend just computed above rather than letting
        # calculate_premium_discount re-derive its own over a different
        # lookback window — a second independent derivation is a source of
        # drift, and the OTE-zone direction (UK100-SESSION-REVIEW-2026-07-13.md
        # §3.1) must agree with the trend this TF's structure read reports.
        "premium_discount": structure.calculate_premium_discount(candles, lookback=min(50, len(candles)), trend=trend),
        "fvgs": [_fvg_to_dict(f) for f in structure.detect_fvgs(candles)[:10]],
        "order_blocks": [_ob_to_dict(ob) for ob in structure.detect_order_blocks(candles)[:10]],
        "liquidity_pools": [_liq_to_dict(p) for p in structure.find_liquidity_pools(candles, current_price)],
        "structure_breaks": structure.detect_structure_breaks(candles),
        "displacement": structure.detect_displacement(candles),
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
    # Optional inputs (Phase 3): daily candles for reference levels, and an
    # EURUSD M5 series for SMT divergence. Absent → those sections are omitted.
    d1  = _parse_candles(payload.get("d1", []), "1d", symbol)
    smt = _parse_candles(payload.get("smt_symbol_m5", []), "5m", "PROXY")

    if not h1 or not m5 or not m1:
        print(json.dumps({"error": "Missing or unparsable h1/m5/m1 candle data — cannot analyse."}), file=sys.stdout)
        sys.exit(1)

    # ── Freshness gate ────────────────────────────────────────────────────────
    # Refuse to analyse stale candles. On 2026-07-09 a session whose live fetch
    # failed recycled the previous day's data (from old temp files / prior saved
    # records) and published a "fresh" brief built on it — wrong Asian range,
    # phantom sweeps, day-old structure. Instructions alone didn't prevent it,
    # so the engine now mechanically rejects inputs whose newest candle is older
    # than the timeframe's tolerance. Limits are generous enough for normal run
    # latency and the daily 17:00–18:00 ET trading break, but far below the
    # hours-to-days gap of any stale-reuse scenario. (Weekend note: gold is
    # closed Fri 21:00 UTC → Sun 22:00 UTC, so a weekend run trips this gate by
    # design — there is no live session to analyse.)
    _LIMITS_MIN = {"m1": 45, "m5": 90, "h1": 180}
    _now = datetime.now(timezone.utc)
    data_age = {}
    for _name, _series in (("h1", h1), ("m5", m5), ("m1", m1)):
        _age = (_now - _series[-1].timestamp).total_seconds() / 60
        data_age[_name] = round(_age, 1)
    stale = {n: a for n, a in data_age.items() if a > _LIMITS_MIN[n]}
    if stale:
        print(json.dumps({
            "error": "STALE DATA — refusing to analyse. Newest candle age (minutes): "
                     + ", ".join(f"{n}={a}" for n, a in stale.items())
                     + f" (limits: {_LIMITS_MIN}). Re-fetch live trendbars from cTrader; "
                       "NEVER reuse a previous run's temp files or previously saved session records.",
            "data_age_minutes": data_age,
        }))
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
        "data_age_minutes": data_age,
        "session": {
            "current_session": sessions.current_session(),
            "active_kill_zone": sessions.active_kill_zone(),
            "minutes_until_kz_closes": sessions.minutes_until_kill_zone_closes(),
            "bias_notes": bias_notes,
        },
        "reference_levels": _reference_levels(d1),
        "smt_divergence": _smt_divergence(m5, smt) if smt else None,
        # Local candlestick cross-check on M5 — deterministic stand-in for the
        # flaky tradingview-mcp recognize_market_pattern stdio server, so the
        # STEP 7 cross-check is always present regardless of MCP availability.
        "pattern_check": patterns.recognize_pattern(m5),
        "h1": h1_ctx,
        "m5": m5_ctx,
        "m1": m1_ctx,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
