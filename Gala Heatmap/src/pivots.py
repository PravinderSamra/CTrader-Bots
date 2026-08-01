#!/usr/bin/env python3
"""
Hourly pivot detection and level clustering.

Mirrors what you do by hand: mark the swing highs and lows on the H1 chart, then
treat several pivots that landed at effectively the same price as ONE level
(because that is how price treats them).

Two knobs matter:
  strength  — how many bars either side must be lower/higher for a bar to count
              as a pivot. 2 is loose (lots of levels), 3–4 is what a human marks.
  tol_pct   — how close two pivots must be to merge into one level. Expressed as
              a fraction of price so it scales across UK100 / XAUUSD / US30.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Pivot:
    ts: int
    price: float
    kind: str  # "high" | "low"


@dataclass
class Level:
    price: float
    kind: str                      # "resistance" | "support" | "both"
    pivots: list[Pivot] = field(default_factory=list)

    @property
    def touch_count(self) -> int:
        return len(self.pivots)

    @property
    def first_ts(self) -> int:
        return min(p.ts for p in self.pivots)

    @property
    def last_ts(self) -> int:
        return max(p.ts for p in self.pivots)


def find_pivots(bars: list[dict], strength: int = 3) -> list[Pivot]:
    """Fractal swing highs/lows on the given bar series.

    A bar is a pivot high if its high is >= the highs of `strength` bars on both
    sides (and strictly greater than at least one, so flat runs don't all qualify).
    """
    out: list[Pivot] = []
    n = len(bars)
    for i in range(strength, n - strength):
        h = bars[i]["h"]
        l = bars[i]["l"]
        window = bars[i - strength: i + strength + 1]
        others = window[:strength] + window[strength + 1:]

        if all(h >= b["h"] for b in others) and any(h > b["h"] for b in others):
            out.append(Pivot(bars[i]["ts"], h, "high"))
        if all(l <= b["l"] for b in others) and any(l < b["l"] for b in others):
            out.append(Pivot(bars[i]["ts"], l, "low"))
    return out


def cluster_levels(pivots: list[Pivot], tol_pct: float = 0.0006) -> list[Level]:
    """Merge pivots that sit at effectively the same price into single levels.

    Greedy single-linkage on sorted prices: walk up the price ladder and start a
    new cluster whenever the gap to the previous pivot exceeds tolerance.
    """
    if not pivots:
        return []
    ordered = sorted(pivots, key=lambda p: p.price)
    clusters: list[list[Pivot]] = [[ordered[0]]]
    for p in ordered[1:]:
        ref = clusters[-1][-1].price
        if abs(p.price - ref) <= ref * tol_pct:
            clusters[-1].append(p)
        else:
            clusters.append([p])

    levels: list[Level] = []
    for c in clusters:
        price = sum(p.price for p in c) / len(c)
        kinds = {p.kind for p in c}
        kind = "both" if len(kinds) > 1 else ("resistance" if "high" in kinds else "support")
        levels.append(Level(price=price, kind=kind, pivots=sorted(c, key=lambda p: p.ts)))
    return sorted(levels, key=lambda lv: lv.price)


def significant_levels(bars: list[dict], strength: int = 3, tol_pct: float = 0.0006,
                       min_touches: int = 1) -> list[Level]:
    """Convenience: pivots → clusters → filter to levels worth marking."""
    levels = cluster_levels(find_pivots(bars, strength), tol_pct)
    return [lv for lv in levels if lv.touch_count >= min_touches]
