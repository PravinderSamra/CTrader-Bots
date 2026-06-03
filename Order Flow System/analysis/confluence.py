"""
Confluence Scoring Engine

Implements the 3-layer framework from Stage 1 research:
  Layer 1 — Context (higher-timeframe trend, premium/discount)
  Layer 2 — Location (OB, FVG, volume profile level, session level)
  Layer 3 — Confirmation (Tier 1 delta, CHoCH, volume, kill zone)

Every score is labelled with the data quality underlying it.
Tier 2 setups explicitly tell the trader what to confirm manually.
"""

from dataclasses import dataclass, field
from typing import List, Optional
from data.models import (
    OrderBlock, FairValueGap, LiquidityPool,
    MarketStructure, SessionLevels, SetupSignal
)
from analysis.zones import PremiumDiscountZone, is_correct_zone_for_trade
from analysis.sessions import is_in_kill_zone
from config import SCORE_THRESHOLDS, DATA_TIER_LABELS, ACCOUNT_SIZE_USD, RISK_PER_TRADE_PCT, RISK_A_PLUS_PCT


@dataclass
class SetupContext:
    """All inputs needed to score a setup."""
    symbol: str
    direction: str                      # 'long' or 'short'
    entry_price: float
    stop_price: float
    target_1: float
    target_2: float
    data_tier: int                      # 1 or 2

    # Layer 1 — Context
    htf_trend: Optional[str] = None    # 'bullish', 'bearish', 'neutral'
    premium_discount: Optional[PremiumDiscountZone] = None
    market_structure: Optional[MarketStructure] = None

    # Layer 2 — Location
    order_block: Optional[OrderBlock] = None
    fvg: Optional[FairValueGap] = None
    at_volume_profile_level: bool = False
    at_lvn: bool = False
    preceded_by_liquidity_grab: bool = False

    # Layer 3 — Confirmation (Tier 1 only)
    tier1_delta_confirmed: bool = False       # 60%+ taker buys at level (long) or sells (short)
    tier1_cvd_divergence: bool = False        # CVD divergence in setup direction
    tier1_absorption: bool = False            # High volume, small body at level

    # Layer 3 — Confirmation (Tier 2 proxies)
    choch_on_lower_tf: bool = False           # CHoCH on 5M/1M confirming the level holds
    volume_spike_at_level: bool = False       # Above-average volume at the level
    in_kill_zone: bool = False                # Price is reacting within a kill zone window
    multi_tf_agreement: bool = False          # 4H and 1H trend both agree with direction
    vwap_confluence: bool = False             # Level aligns with VWAP or AVWAP

    # Risk flags
    major_news_imminent: bool = False
    order_block_mitigated: bool = False
    fvg_mitigated: bool = False
    counter_trend_no_choch: bool = False


@dataclass
class SetupScore:
    total_score: int
    grade: str                          # 'A+', 'B+', 'B', 'C', 'SKIP'
    conditions_met: List[str]
    risk_warnings: List[str]
    data_tier: int
    data_tier_label: str
    manual_confirmation_needed: List[str]   # For Tier 2 setups
    confidence_pct: int                     # 0–100


def score_setup(ctx: SetupContext) -> SetupScore:
    """
    Score a trading setup against the 10-condition confluence framework.
    Returns a SetupScore with grade, conditions, warnings, and data quality label.
    """
    score = 0
    conditions: List[str] = []
    warnings:   List[str] = []
    manual_checks: List[str] = []

    # ── LAYER 1: CONTEXT ────────────────────────────────────────────────────

    # HTF trend aligned
    if ctx.htf_trend and ctx.htf_trend == _expected_trend(ctx.direction):
        score += 2
        conditions.append(f"✅ Higher-TF trend aligned ({ctx.htf_trend})")
    elif ctx.htf_trend and ctx.htf_trend != "neutral":
        warnings.append(f"⚠️  Counter-trend trade — HTF trend is {ctx.htf_trend}")
        if not ctx.market_structure or not ctx.market_structure.choch_confirmed:
            warnings.append("⚠️  No CHoCH confirmation for counter-trend — HIGH RISK")
            ctx.counter_trend_no_choch = True
    else:
        conditions.append("⬜ HTF trend: neutral or unknown")

    # Premium/discount zone alignment
    if ctx.premium_discount:
        if is_correct_zone_for_trade(ctx.premium_discount, ctx.direction):
            score += 2
            conditions.append(f"✅ Correct zone: {ctx.premium_discount.zone_label}")
        else:
            warnings.append(
                f"⚠️  WRONG ZONE — trading {'long' if ctx.direction == 'long' else 'short'} "
                f"in {'PREMIUM' if ctx.premium_discount.in_premium else 'DISCOUNT'} zone. "
                "This works against institutional order flow."
            )

    # Multi-timeframe agreement
    if ctx.multi_tf_agreement:
        score += 1
        conditions.append("✅ Multi-timeframe agreement (4H + 1H aligned)")

    # ── LAYER 2: LOCATION ───────────────────────────────────────────────────

    # Order block
    if ctx.order_block and not ctx.order_block.is_mitigated:
        ob_score = ctx.order_block.quality_score
        score += min(ob_score, 2)
        conditions.append(
            f"✅ Unmitigated {ctx.order_block.direction} order block "
            f"({ctx.order_block.low:.5f}–{ctx.order_block.high:.5f}) "
            f"[Quality: {ob_score}/5]"
        )
    elif ctx.order_block and ctx.order_block.is_mitigated:
        warnings.append("⚠️  Order block already mitigated — first-touch probability lost")

    # FVG
    if ctx.fvg and not ctx.fvg.is_mitigated:
        score += 1
        conditions.append(
            f"✅ Unmitigated {ctx.fvg.direction} FVG "
            f"({ctx.fvg.gap_low:.5f}–{ctx.fvg.gap_high:.5f}, midpoint {ctx.fvg.midpoint:.5f})"
        )
    elif ctx.fvg and ctx.fvg.is_mitigated:
        warnings.append("⚠️  FVG already mitigated")

    # Liquidity grab preceding the setup
    if ctx.preceded_by_liquidity_grab:
        score += 2
        conditions.append("✅ Preceding liquidity grab — stop hunt before this level")

    # Volume profile level (POC, VAH, VAL, LVN)
    if ctx.at_lvn:
        score += 1
        conditions.append("✅ Entry at Low Volume Node — fast transit zone expected")
    elif ctx.at_volume_profile_level:
        score += 1
        conditions.append("✅ Volume profile level confluence (POC / VAH / VAL)")

    # ── LAYER 3: CONFIRMATION ───────────────────────────────────────────────

    if ctx.data_tier == 1:
        # Real order flow confirmation available
        if ctx.tier1_delta_confirmed:
            score += 2
            conditions.append(
                f"✅ TIER 1 CONFIRMED — Real taker volume shows "
                f"{'buyers' if ctx.direction == 'long' else 'sellers'} "
                f"defending this level (>58% aggression from expected side)"
            )
        else:
            manual_checks.append(
                "Delta at this level is NOT confirming. "
                "Taker buy/sell ratio does not show clear institutional aggression. "
                "Reduce size or wait."
            )

        if ctx.tier1_cvd_divergence:
            score += 1
            div_type = "bullish" if ctx.direction == "long" else "bearish"
            conditions.append(f"✅ TIER 1 CVD divergence ({div_type}) — price and CVD diverging")

        if ctx.tier1_absorption:
            score += 1
            conditions.append("✅ TIER 1 Absorption signal — high volume, small body at level")
    else:
        # Tier 2 — structural only, list everything the trader must check manually
        manual_checks.append(
            "⚠️  NO TIER 1 DATA AVAILABLE for this market (forex/indices/commodities). "
            "Before entering, manually confirm ALL of the following on Bookmap, "
            "Sierra Chart, ATAS, or your footprint platform:"
        )
        manual_checks.append(
            f"  → Footprint: Look for absorption at {ctx.entry_price:.5f} — "
            f"large volume hitting the {'bid' if ctx.direction == 'short' else 'ask'} "
            "with price NOT moving through the level"
        )
        manual_checks.append(
            f"  → Delta: {'Positive' if ctx.direction == 'long' else 'Negative'} delta "
            "at this level (aggressive buyers/sellers defending)"
        )
        manual_checks.append(
            f"  → CVD: {'Rising' if ctx.direction == 'long' else 'Falling'} CVD even "
            "as price tests this level"
        )
        manual_checks.append(
            f"  → DOM: Large {'bids' if ctx.direction == 'long' else 'offers'} "
            "appearing and being refilled at this level"
        )

    # CHoCH on lower timeframe (Tier 2 proxy confirmation)
    if ctx.choch_on_lower_tf:
        score += 1
        conditions.append("✅ CHoCH on lower timeframe — structure flipped, level holding")
    else:
        manual_checks.append(
            f"  → Wait for CHoCH on the 5M/1M chart before entering — "
            "a lower-TF structure flip confirms the level is defended"
        )

    # Kill zone timing
    if ctx.in_kill_zone:
        score += 1
        conditions.append("✅ Active kill zone — institutional participation elevated")
    else:
        conditions.append("⬜ Outside kill zone (02:00–05:00 or 07:00–10:00 EST preferred)")

    # VWAP confluence
    if ctx.vwap_confluence:
        score += 1
        conditions.append("✅ VWAP/AVWAP confluence at entry level")

    # ── RISK FLAGS ──────────────────────────────────────────────────────────

    if ctx.major_news_imminent:
        warnings.append(
            "🔴 HIGH-IMPACT NEWS IMMINENT — DO NOT ENTER. "
            "Wait until 15 minutes after the release."
        )
    if ctx.counter_trend_no_choch:
        warnings.append("🔴 Counter-trend trade without structural confirmation — SKIP or extreme caution")

    # ── GRADE AND CONFIDENCE ────────────────────────────────────────────────

    grade = "SKIP"
    for g, threshold in sorted(SCORE_THRESHOLDS.items(), key=lambda x: -x[1]):
        if score >= threshold:
            grade = g
            break

    max_possible = 16  # Rough maximum across all conditions
    confidence = min(100, int((score / max_possible) * 100))

    # Demote grade if hard risk flags are present
    if ctx.major_news_imminent or ctx.counter_trend_no_choch:
        grade = "SKIP"
        confidence = max(0, confidence - 30)

    return SetupScore(
        total_score=score,
        grade=grade,
        conditions_met=conditions,
        risk_warnings=warnings,
        data_tier=ctx.data_tier,
        data_tier_label=DATA_TIER_LABELS[ctx.data_tier],
        manual_confirmation_needed=manual_checks,
        confidence_pct=confidence,
    )


def _expected_trend(direction: str) -> str:
    return "bullish" if direction == "long" else "bearish"


def compute_position_size(
    entry: float,
    stop: float,
    account_size: float = ACCOUNT_SIZE_USD,
    risk_pct: float = RISK_PER_TRADE_PCT,
    point_value: float = 1.0,
) -> dict:
    """
    Calculate position size based on fixed-risk model (1% rule).
    point_value: dollar value per 1 unit of price movement (1 for crypto, 10 for forex mini lot, etc.)
    """
    risk_dollars  = account_size * (risk_pct / 100)
    stop_distance = abs(entry - stop)
    if stop_distance == 0:
        return {"error": "Stop distance is zero — check entry and stop prices"}

    units = risk_dollars / (stop_distance * point_value)

    return {
        "account_size":    account_size,
        "risk_pct":        risk_pct,
        "risk_dollars":    round(risk_dollars, 2),
        "stop_distance":   round(stop_distance, 6),
        "units":           round(units, 4),
        "point_value":     point_value,
    }
