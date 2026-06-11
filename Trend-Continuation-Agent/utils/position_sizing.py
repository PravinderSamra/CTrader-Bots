"""
/Trend-Continuation-Agent — Position sizing (Spread Betting)

Spec §6:
  SL distance (points) = |entry price - stop loss price|
  Stake (£/pt) = Risk Amount (£) / SL distance (points)
  Round DOWN to the nearest £0.50/pt for clean sizing — never round up.

DEVIATION (see CLAUDE.md / config.py): the live cTrader MCP `volume` field
for this account is in units of £0.01/pt with a minimum and step of 100
(= £1.00/pt). A £0.50/pt stake is not placeable, so the broker-executable
stake is rounded down again to the nearest whole £1/pt.
"""

from __future__ import annotations

import math

from config import BROKER_MIN_VOLUME, BROKER_VOLUME_STEP, SPEC_STAKE_ROUND_INCREMENT


def calc_stake(risk_amount: float, sl_distance_points: float) -> dict:
    """
    Returns:
      raw_stake      - unrounded £/pt implied by the risk amount
      spec_stake     - §6 display stake, rounded down to £0.50/pt
      broker_stake   - actual order stake, rounded down to the broker's
                       £1/pt step
      volume         - cTrader `volume` units (£0.01/pt) for create_order
      max_loss       - broker_stake x sl_distance_points
      below_minimum  - True if `volume` is below BROKER_MIN_VOLUME
    """
    if sl_distance_points <= 0:
        raise ValueError("sl_distance_points must be positive")
    if risk_amount <= 0:
        raise ValueError("risk_amount must be positive")

    raw_stake = risk_amount / sl_distance_points

    spec_stake = math.floor(raw_stake / SPEC_STAKE_ROUND_INCREMENT) * SPEC_STAKE_ROUND_INCREMENT

    broker_increment = BROKER_VOLUME_STEP / 100.0  # £/pt per broker volume step
    broker_stake = math.floor(spec_stake / broker_increment) * broker_increment

    volume = int(round(broker_stake * 100))  # cTrader volume = £0.01/pt
    # Snap to the broker step in case of floating-point drift.
    volume = (volume // BROKER_VOLUME_STEP) * BROKER_VOLUME_STEP

    return {
        "raw_stake": raw_stake,
        "spec_stake": spec_stake,
        "broker_stake": broker_stake,
        "volume": volume,
        "max_loss": broker_stake * sl_distance_points,
        "below_minimum": volume < BROKER_MIN_VOLUME,
    }
