"""
Local candlestick-pattern cross-check.

Deterministic replacement for the tradingview-mcp `recognize_market_pattern`
tool. That server runs as a stdio MCP process (`uvx tradingview-mcp`) and
frequently fails to register in remote Claude sessions — unlike the cTrader
MCP there is no HTTP endpoint to fall back to, so the reliable equivalent is
to compute the cross-check locally from candles we already hold. Same inputs
(recent candles), same shape of answer (pattern / direction / confidence /
RSI / volatility), zero external dependencies: every session — fresh or
long-lived — gets an identical cross-check from identical data.

This is intentionally a NON-ICT read (classical candlestick patterns + RSI),
so it remains an independent second opinion against the structural bias.
"""

from typing import List, Optional

from data.models import Candle


def rsi_14(closes: List[float], period: int = 14) -> Optional[float]:
    """Simple-average RSI over the last `period` deltas (deterministic)."""
    if len(closes) < period + 1:
        return None
    gains = 0.0
    losses = 0.0
    for i in range(-period, 0):
        d = closes[i] - closes[i - 1]
        if d >= 0:
            gains += d
        else:
            losses -= d
    if losses == 0:
        return 100.0
    rs = gains / losses
    return round(100.0 - 100.0 / (1.0 + rs), 1)


def _volatility_label(candles: List[Candle]) -> str:
    """Recent (5-bar) average range vs the 20-bar baseline."""
    if len(candles) < 20:
        return "MEDIUM"
    base = sum(c.high - c.low for c in candles[-20:]) / 20
    recent = sum(c.high - c.low for c in candles[-5:]) / 5
    if base <= 0:
        return "MEDIUM"
    ratio = recent / base
    if ratio > 1.3:
        return "HIGH"
    if ratio < 0.7:
        return "LOW"
    return "MEDIUM"


def _body(c: Candle) -> float:
    return abs(c.close - c.open)


def _range(c: Candle) -> float:
    return max(c.high - c.low, 1e-12)


def _is_bull(c: Candle) -> bool:
    return c.close > c.open


def _is_bear(c: Candle) -> bool:
    return c.close < c.open


def recognize_pattern(candles: List[Candle]) -> dict:
    """
    Classify the most recent candlestick pattern from the last ~15 candles.
    Priority: 3-bar momentum > engulfing > pin bars > doji > inside bar.
    Confidence values are fixed per pattern so the answer is reproducible.
    """
    if len(candles) < 3:
        return {"pattern": "NONE", "direction": "NEUTRAL", "confidence": 0.0,
                "rsi14": None, "volatility": "MEDIUM",
                "note": "insufficient candles"}

    window = candles[-15:] if len(candles) >= 15 else candles
    c1, c2, c3 = candles[-3], candles[-2], candles[-1]
    closes = [c.close for c in candles]

    pattern = "NONE"
    direction = "NEUTRAL"
    confidence = 0.4

    three_up = (_is_bull(c1) and _is_bull(c2) and _is_bull(c3)
                and c3.close > c2.close > c1.close
                and all(_body(c) > 0.5 * _range(c) for c in (c1, c2, c3)))
    three_dn = (_is_bear(c1) and _is_bear(c2) and _is_bear(c3)
                and c3.close < c2.close < c1.close
                and all(_body(c) > 0.5 * _range(c) for c in (c1, c2, c3)))
    # Open compares with <=/>= : in 24h markets each candle opens at the prior
    # close, so a strict inequality would make engulfings all but undetectable.
    engulf_bull = (_is_bear(c2) and _is_bull(c3)
                   and c3.close > max(c2.open, c2.close)
                   and c3.open <= min(c2.open, c2.close))
    engulf_bear = (_is_bull(c2) and _is_bear(c3)
                   and c3.close < min(c2.open, c2.close)
                   and c3.open >= max(c2.open, c2.close))
    lower_wick = min(c3.open, c3.close) - c3.low
    upper_wick = c3.high - max(c3.open, c3.close)
    hammer = (lower_wick >= 2 * _body(c3)
              and c3.close >= c3.low + 0.6 * _range(c3))
    shooting_star = (upper_wick >= 2 * _body(c3)
                     and c3.close <= c3.high - 0.6 * _range(c3))
    doji = _body(c3) <= 0.1 * _range(c3)
    inside = c3.high < c2.high and c3.low > c2.low

    if three_up:
        pattern, direction, confidence = "THREE_WHITE_SOLDIERS", "BULLISH", 0.75
    elif three_dn:
        pattern, direction, confidence = "THREE_BLACK_CROWS", "BEARISH", 0.75
    elif engulf_bull:
        pattern, direction, confidence = "BULLISH_ENGULFING", "BULLISH", 0.7
    elif engulf_bear:
        pattern, direction, confidence = "BEARISH_ENGULFING", "BEARISH", 0.7
    elif hammer:
        pattern, direction, confidence = "HAMMER", "BULLISH", 0.65
    elif shooting_star:
        pattern, direction, confidence = "SHOOTING_STAR", "BEARISH", 0.65
    elif doji:
        pattern, direction, confidence = "DOJI", "NEUTRAL", 0.5
    elif inside:
        pattern, direction, confidence = "INSIDE_BAR", "NEUTRAL", 0.55
    else:
        net = window[-1].close - window[0].close
        avg_rng = sum(_range(c) for c in window) / len(window)
        if net > avg_rng:
            direction = "BULLISH"
        elif net < -avg_rng:
            direction = "BEARISH"

    rsi = rsi_14(closes)
    note_bits = [f"pattern={pattern}"]
    if rsi is not None:
        if rsi >= 70:
            note_bits.append(f"RSI {rsi} stretched high")
        elif rsi <= 30:
            note_bits.append(f"RSI {rsi} stretched low")
        else:
            note_bits.append(f"RSI {rsi}")

    return {
        "pattern": pattern,
        "direction": direction,
        "confidence": confidence,
        "rsi14": rsi,
        "volatility": _volatility_label(candles),
        "note": ", ".join(note_bits),
    }
