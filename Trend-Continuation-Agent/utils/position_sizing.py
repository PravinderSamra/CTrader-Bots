"""
/Trend-Continuation-Agent — Position sizing (Spread Betting)

Spec §6:
  SL distance (points) = |entry price - stop loss price|
  Stake (£/pt) = Risk Amount (£) / SL distance (points)
  Round DOWN to the nearest £0.50/pt for clean sizing — never round up.

DEVIATION (see CLAUDE.md items 2 and 14): "Stake (£/pt)" and the cTrader
`volume` field are NOT the same unit except for `point_size == 1.0`
instruments (indices, XAU/XPD/XPT). `volume` is cTrader's "cents of base
asset" — converting a £/pt stake into it requires dividing by the symbol's
`point_size`: `volume = (stake_£/pt / point_size) * 100`. A £0.50/pt stake
is also not placeable, so the broker-executable stake is rounded down again
to the nearest whole £1/pt before this conversion.
"""

from __future__ import annotations

import math

from config import BROKER_MIN_VOLUME, BROKER_VOLUME_STEP, SPEC_STAKE_ROUND_INCREMENT


def calc_stake(risk_amount: float, sl_distance_points: float, point_size: float = 1.0) -> dict:
    """
    Returns:
      raw_stake      - unrounded £/pt implied by the risk amount
      spec_stake     - §6 display stake, rounded down to £0.50/pt
      broker_stake   - actual order stake (£/pt), rounded down to the
                       broker's whole £1/pt step
      volume         - cTrader `volume` units for create_order:
                       (broker_stake / point_size) * 100
      max_loss       - broker_stake x sl_distance_points
      below_minimum  - True if `volume` is below the point_size-scaled
                       broker minimum
    """
    if sl_distance_points <= 0:
        raise ValueError("sl_distance_points must be positive")
    if risk_amount <= 0:
        raise ValueError("risk_amount must be positive")

    raw_stake = risk_amount / sl_distance_points

    spec_stake = math.floor(raw_stake / SPEC_STAKE_ROUND_INCREMENT) * SPEC_STAKE_ROUND_INCREMENT

    broker_increment = BROKER_VOLUME_STEP / 100.0  # whole £/pt (point_size==1 baseline)
    broker_stake = math.floor(spec_stake / broker_increment) * broker_increment

    volume = int(round(broker_stake * 100 / point_size))
    min_volume = int(round(BROKER_MIN_VOLUME / point_size))

    return {
        "raw_stake": raw_stake,
        "spec_stake": spec_stake,
        "broker_stake": broker_stake,
        "volume": volume,
        "max_loss": broker_stake * sl_distance_points,
        "below_minimum": volume < min_volume,
    }
