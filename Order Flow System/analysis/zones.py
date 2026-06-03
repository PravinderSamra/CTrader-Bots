"""
Premium / Discount Zones and Fibonacci OTE Levels

ICT concepts applied to any dealing range:
- Premium zone: above the 50% of the range (look for shorts)
- Discount zone: below the 50% of the range (look for longs)
- OTE (Optimal Trade Entry): 62%–79% Fibonacci retracement

Also handles session-based premium/discount using the midnight open.
"""

from dataclasses import dataclass
from typing import Optional
from data.models import Candle


@dataclass
class PremiumDiscountZone:
    swing_high: float
    swing_low: float
    equilibrium: float          # 50% level
    ote_low: float              # 62% retracement
    ote_high: float             # 79% retracement
    in_premium: bool            # Current price is above equilibrium
    in_discount: bool           # Current price is below equilibrium
    in_ote: bool                # Current price is in OTE zone
    current_price: float
    zone_label: str


def compute_premium_discount(
    swing_high: float,
    swing_low: float,
    current_price: float,
) -> PremiumDiscountZone:
    """
    Compute the premium/discount zone for a given dealing range.

    For LONGS (bullish context):
      - Discount = below equilibrium (below 50%)
      - OTE = 62%–79% retracement from the high back toward the low
        (i.e. current_price between low + 21% of range and low + 38% of range)

    For SHORTS (bearish context):
      - Premium = above equilibrium
      - OTE = same levels but from the low back toward the high
    """
    span = swing_high - swing_low
    equilibrium = swing_low + span * 0.50

    # OTE zone (Fibonacci 0.62–0.79 retracement of the range)
    # From the HIGH down to LOW (for pullback longs):
    ote_low_long  = swing_high - span * 0.79   # Deeper in discount
    ote_high_long = swing_high - span * 0.62   # Shallower in discount

    in_premium  = current_price > equilibrium
    in_discount = current_price < equilibrium
    in_ote      = ote_low_long <= current_price <= ote_high_long

    if in_premium:
        label = f"PREMIUM — above equilibrium ({equilibrium:.5f}). Look for SHORTS."
    elif in_ote:
        label = f"OTE ZONE (Optimal Trade Entry) — {ote_low_long:.5f}–{ote_high_long:.5f}. Highest-probability LONG zone."
    elif in_discount:
        label = f"DISCOUNT — below equilibrium ({equilibrium:.5f}). Look for LONGS."
    else:
        label = f"AT EQUILIBRIUM — {equilibrium:.5f}."

    return PremiumDiscountZone(
        swing_high=swing_high,
        swing_low=swing_low,
        equilibrium=equilibrium,
        ote_low=ote_low_long,
        ote_high=ote_high_long,
        in_premium=in_premium,
        in_discount=in_discount,
        in_ote=in_ote,
        current_price=current_price,
        zone_label=label,
    )


def is_correct_zone_for_trade(zone: PremiumDiscountZone, direction: str) -> bool:
    """
    Returns True if the current price is in the correct zone for the trade.
    Longs should be in discount. Shorts should be in premium.
    Trading in the wrong zone is a red flag.
    """
    if direction == "long":
        return zone.in_discount or zone.in_ote
    elif direction == "short":
        return zone.in_premium
    return False


def compute_fibonacci_levels(
    swing_low: float,
    swing_high: float,
) -> dict:
    """
    Standard Fibonacci retracement and extension levels.
    Used for target identification and OTE zone confirmation.
    """
    span = swing_high - swing_low
    return {
        "0.0":   round(swing_high, 6),
        "0.236": round(swing_high - span * 0.236, 6),
        "0.382": round(swing_high - span * 0.382, 6),
        "0.5":   round(swing_high - span * 0.500, 6),
        "0.618": round(swing_high - span * 0.618, 6),   # OTE lower bound
        "0.705": round(swing_high - span * 0.705, 6),
        "0.786": round(swing_high - span * 0.786, 6),   # OTE upper bound
        "1.0":   round(swing_low, 6),
        "1.272": round(swing_low  - span * 0.272, 6),   # Extension targets
        "1.618": round(swing_low  - span * 0.618, 6),
    }
