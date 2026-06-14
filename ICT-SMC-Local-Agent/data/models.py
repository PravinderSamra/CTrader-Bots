"""
Core data models shared across the entire ICT/SMC analysis pipeline.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


@dataclass
class Candle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    timeframe: str
    symbol: str
    data_tier: int = 2
    taker_buy_volume: Optional[float] = None
    taker_sell_volume: Optional[float] = None

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def range_size(self) -> float:
        return self.high - self.low

    @property
    def is_bullish(self) -> bool:
        return self.close >= self.open

    @property
    def mid(self) -> float:
        return (self.high + self.low) / 2.0


@dataclass
class FVGResult:
    symbol: str
    timeframe: str
    direction: str          # "BULL" or "BEAR"
    gap_low: float
    gap_high: float
    formed_at: datetime
    candles_ago: int
    age_label: str          # FRESH / RECENT / MATURE / STALE
    gap_size_pct: float
    impulse_body_pct: float
    touch_count: int
    partial_fill_pct: float
    context_flags: List[str]   # e.g. ["liq.grab", "post-BOS"]
    probability_grade: str     # A+ / A / B / C / SKIP
    pct_from_price: float = 0.0
    is_at_price: bool = False

    @property
    def label(self) -> str:
        direction = "Bullish" if self.direction == "BULL" else "Bearish"
        return (
            f"{direction} FVG | {self.timeframe} | "
            f"{self.gap_low:.5f} → {self.gap_high:.5f}"
        )


@dataclass
class OrderBlock:
    symbol: str
    timeframe: str
    direction: str          # "BULL" or "BEAR"
    ob_low: float
    ob_high: float
    formed_at: datetime
    quality: int            # 1–5
    preceded_by_liq_grab: bool
    is_mitigated: bool = False

    @property
    def mid(self) -> float:
        return (self.ob_low + self.ob_high) / 2.0


@dataclass
class LiquidityPool:
    symbol: str
    price: float
    direction: str          # "BSL" (buy-side, above) or "SSL" (sell-side, below)
    test_count: int

    @property
    def strength(self) -> str:
        if self.test_count >= 4:
            return "HIGH"
        if self.test_count >= 2:
            return "MEDIUM"
        return "LOW"


@dataclass
class COTData:
    report_date: str
    net_contracts: int
    pct_of_oi: float
    weekly_change: int
    rank_8wk: int           # percentile 0–100
    category: str
    bias: str               # BULLISH / BEARISH / NEUTRAL
    history: List[tuple]    # [(date_str, net), ...]


@dataclass
class MarketContext:
    symbol: str
    current_price: float
    higher_tf_trend: str
    intraday_trend: str
    range_high: float
    range_low: float
    equilibrium: float
    premium_discount_status: str
    ote_low: float
    ote_high: float
    prior_day_high: float
    prior_day_low: float
    asian_high: Optional[float]
    asian_low: Optional[float]
    midnight_open: Optional[float]
    asian_swept: Optional[str]      # "HIGH" / "LOW" / None
    data_tier: int
    data_source: str                # actual source used: "ctrader", "twelve_data", "yahoo", "okx"
    fvgs: List[FVGResult] = field(default_factory=list)
    order_blocks: List[OrderBlock] = field(default_factory=list)
    liquidity_pools: List[LiquidityPool] = field(default_factory=list)
    cot: Optional[COTData] = None
    poc: Optional[float] = None
    vah: Optional[float] = None
    val: Optional[float] = None
    lvns: List[float] = field(default_factory=list)
