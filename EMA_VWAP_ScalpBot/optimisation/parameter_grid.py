"""
Full optimisation parameter grid — Section 11 of specification.
Generates all valid parameter combinations (EMA constraint enforced).
Estimated ~2000–2500 valid combinations after constraint filtering.
"""

import itertools
from typing import Iterator


# ── Parameter ranges (Section 11) ────────────────────────────────────────────

EMA_FAST_RANGE   = range(7,  14, 1)     # 7,8,9,10,11,12,13
EMA_SLOW_RANGE   = range(18, 27, 1)     # 18,19,...,26
ATR_PERIOD_RANGE = range(10, 19, 2)     # 10,12,14,16,18
ATR_MULT_RANGE   = [1.0, 1.25, 1.5, 1.75, 2.0, 2.25, 2.5]
BODY_FILTER_RANGE = [30, 40, 50, 60]
MAX_ENTRY_DIST_RANGE = [0.5, 0.75, 1.0, 1.25, 1.5]
MAX_TRADES_RANGE = [2, 3, 4]

# Fixed (not optimised)
EMA_BIAS_PERIOD = 21
TP1_SD = 1.0
TP2_SD = 2.0


def _ema_constraint_valid(ema_fast: int, ema_slow: int) -> bool:
    """EMA Slow must be >= EMA Fast + 5 (spec §11 constraint)."""
    return ema_slow >= ema_fast + 5


def generate_grid(coarse: bool = False) -> Iterator[dict]:
    """
    Yield all valid parameter dictionaries.

    coarse=True: use step-2 on ATR mult and entry dist (reduces combinations by ~70%)
    for two-phase optimisation described in spec §11 callout.
    """
    atr_mult  = [1.0, 1.5, 2.0, 2.5]    if coarse else ATR_MULT_RANGE
    entry_d   = [0.5, 1.0, 1.5]          if coarse else MAX_ENTRY_DIST_RANGE
    body_f    = [30, 50]                  if coarse else BODY_FILTER_RANGE

    for (ef, es, ap, am, bf, ed, mt) in itertools.product(
        EMA_FAST_RANGE,
        EMA_SLOW_RANGE,
        ATR_PERIOD_RANGE,
        atr_mult,
        body_f,
        entry_d,
        MAX_TRADES_RANGE,
    ):
        if not _ema_constraint_valid(ef, es):
            continue
        yield {
            "ema_fast":            ef,
            "ema_slow":            es,
            "atr_period":          ap,
            "atr_multiplier":      am,
            "min_body_pct":        float(bf),
            "max_entry_dist_atr":  ed,
            "max_trades_per_day":  mt,
        }


def grid_size(coarse: bool = False) -> int:
    """Count the number of valid combinations."""
    return sum(1 for _ in generate_grid(coarse=coarse))


def get_neighbours(params: dict) -> list[dict]:
    """
    Generate all immediate neighbours for the stability surface check.
    Changes each variable parameter by ±1 step individually.
    """
    variations = {
        "ema_fast":           [-1, +1],
        "ema_slow":           [-1, +1],
        "atr_period":         [-2, +2],
        "atr_multiplier":     [-0.25, +0.25],
        "min_body_pct":       [-10.0, +10.0],
        "max_entry_dist_atr": [-0.25, +0.25],
        "max_trades_per_day": [-1, +1],
    }

    neighbours = []
    for key, deltas in variations.items():
        base = params[key]
        for d in deltas:
            candidate = dict(params)
            candidate[key] = round(base + d, 4)
            # Enforce EMA constraint
            if _ema_constraint_valid(candidate["ema_fast"], candidate["ema_slow"]):
                neighbours.append(candidate)

    return neighbours


if __name__ == "__main__":
    full = grid_size(coarse=False)
    coarse = grid_size(coarse=True)
    print(f"Full grid:   {full:,} combinations")
    print(f"Coarse grid: {coarse:,} combinations")
