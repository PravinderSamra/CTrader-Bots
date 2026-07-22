"""
Skill Adapter — UK100 variant. Bridges live cTrader trendbar data (fetched via
ctrader_http_fetch.py --instrument uk100) into this repo's existing ICT/SMC
analysis engine (analysis/structure.py, analysis/sessions.py) plus the
UK100-specific session/ORB map (uk100_sessions.py).

Copied from skill_adapter.py (the gold engine) — the differences are:
  - No Asian-range block (irrelevant to a London cash-open index).
  - Adds `orb` (uk100_sessions.orb_window) and `session` (uk100_sessions,
    NOT analysis/sessions — UK100 has its own London session map).
  - `reference_levels` gains `adr14`/`prior_close` from uk100_sessions.
  - SMT divergence is checked against GBPUSD with an INVERTED read (weak GBP
    is bullish for UK100, so a same-direction UK100/GBP swing is the
    divergence signal here, not an opposite-direction one — see
    _smt_divergence_inverse).

analysis/structure.py and analysis/patterns.py are used unmodified — do not
fork them here. Keep this file and skill_adapter.py in sync on any
structure/patterns call-signature changes, but their instrument-specific
logic (Asian range vs ORB, SMT direction) is intentionally different.

Usage:
    python3 uk100_adapter.py < uk100_session_input.json > output.json
"""

import sys
import os
import json
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from data.models import Candle
from analysis import structure, patterns
import uk100_sessions


def _parse_candles(raw_candles: list, timeframe: str, symbol: str) -> list[Candle]:
    candles = []
    skipped = 0
    for bar in raw_candles:
        try:
            ts_raw = bar["timestamp"]
            if isinstance(ts_raw, (int, float)):
                ts = datetime.fromtimestamp(ts_raw / 1000 if ts_raw > 1_000_000_000_000 else ts_raw, tz=timezone.utc)
            elif isinstance(ts_raw, str) and ts_raw.strip().lstrip("-").isdigit():
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
            f"[uk100_adapter] WARNING: skipped {skipped}/{len(raw_candles)} candles"
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
    """Previous day/week high-low + today's daily open — identical logic to
    skill_adapter._reference_levels (kept separate per file to avoid coupling
    the two engines, per the module docstring)."""
    if not d1 or len(d1) < 2:
        return {}

    out: dict = {
        "daily_open":    d1[-1].open,
        "prev_day_high": d1[-2].high,
        "prev_day_low":  d1[-2].low,
    }

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


def _smt_divergence_inverse(uk_m5: list[Candle], gbp_m5: list[Candle]) -> str | None:
    """
    SMT divergence between UK100 and GBPUSD — INVERTED relative to gold's
    _smt_divergence, because UK100 and GBP are inversely correlated (weak
    GBP lifts FTSE-heavy exporters; strong GBP is a headwind).

    A UK100 move is "confirmed" by GBP moving in the OPPOSITE direction (its
    normal inverse relationship). When GBP instead moves in the SAME
    direction as UK100, that's the divergence — UK100's move lacks its usual
    fundamental driver and is more likely a stop hunt / liquidity grab than
    a real break:

      UK100 LOWER low + GBPUSD LOWER low (GBP also weak — weak GBP should
        LIFT FTSE, not confirm a fall) → BULLISH divergence (expect reversal up).
      UK100 HIGHER high + GBPUSD HIGHER high (GBP also strong — strong GBP
        should hurt FTSE, not confirm a rise) → BEARISH divergence.

    Returns "BULLISH" / "BEARISH" / None. Needs ≥2 confirmed swings per side.
    """
    if len(uk_m5) < 6 or len(gbp_m5) < 6:
        return None

    uk_highs, uk_lows = structure.find_swing_points(uk_m5)
    gbp_highs, gbp_lows = structure.find_swing_points(gbp_m5)

    if len(uk_lows) >= 2 and len(gbp_lows) >= 2:
        uk_lower_low  = uk_lows[-1][1]  < uk_lows[-2][1]
        gbp_lower_low = gbp_lows[-1][1] < gbp_lows[-2][1]
        if uk_lower_low and gbp_lower_low:
            return "BULLISH"

    if len(uk_highs) >= 2 and len(gbp_highs) >= 2:
        uk_higher_high  = uk_highs[-1][1]  > uk_highs[-2][1]
        gbp_higher_high = gbp_highs[-1][1] > gbp_highs[-2][1]
        if uk_higher_high and gbp_higher_high:
            return "BEARISH"

    return None


def _analyse_timeframe(candles: list[Candle], include_volume_profile: bool = False) -> dict:
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

    return result


def main():
    payload = json.load(sys.stdin)
    symbol = payload.get("symbol", "UK100")
    current_price = payload.get("current_price")

    h1 = _parse_candles(payload.get("h1", []), "1h", symbol)
    m5 = _parse_candles(payload.get("m5", []), "5m", symbol)
    m1 = _parse_candles(payload.get("m1", []), "1m", symbol)
    d1 = _parse_candles(payload.get("d1", []), "1d", symbol)
    gbp_m5 = _parse_candles(payload.get("smt_symbol_m5", []), "5m", "GBPUSD")
    orb_h1 = _parse_candles(payload.get("orb_h1", []), "1h", symbol)
    orb_m5 = _parse_candles(payload.get("orb_m5", []), "5m", symbol)

    if not h1 or not m5 or not m1:
        print(json.dumps({"error": "Missing or unparsable h1/m5/m1 candle data — cannot analyse."}), file=sys.stdout)
        sys.exit(1)

    # ── Freshness gate — IDENTICAL to skill_adapter.py (see its comment for
    # the 2026-07-09 stale-reuse incident this guards against). Same limits:
    # a stale UK100 pull is exactly as dangerous as a stale gold pull.
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

    h1_ctx = _analyse_timeframe(h1, include_volume_profile=True)
    m5_ctx = _analyse_timeframe(m5)
    m1_ctx = _analyse_timeframe(m1)

    orb = uk100_sessions.orb_window(
        m5,
        orb_m5_candles=orb_m5 or None,
        overnight_h1_candles=orb_h1 or None,
    )
    prior = uk100_sessions.prior_day_levels(d1)

    reference_levels = _reference_levels(d1)
    adr14 = uk100_sessions.adr14(d1)
    if adr14 is not None:
        reference_levels["adr14"] = adr14
    if prior.get("prior_close") is not None:
        reference_levels["prior_close"] = prior["prior_close"]

    output = {
        "symbol": symbol,
        "current_price": current_price,
        "data_age_minutes": data_age,
        "session": {
            "current_session": uk100_sessions.current_session(),
            "bias_notes": uk100_sessions.session_bias_note(
                orb, prior, current_price, reference_levels.get("daily_open")),
        },
        "orb": orb,
        "reference_levels": reference_levels,
        "smt_divergence": _smt_divergence_inverse(m5, gbp_m5) if gbp_m5 else None,
        # Local candlestick cross-check on M5 — deterministic stand-in for the
        # flaky tradingview-mcp recognize_market_pattern stdio server, same
        # role as in skill_adapter.py's gold pipeline.
        "pattern_check": patterns.recognize_pattern(m5),
        "h1": h1_ctx,
        "m5": m5_ctx,
        "m1": m1_ctx,
    }

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
