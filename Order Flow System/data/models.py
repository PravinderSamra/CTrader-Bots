"""
Core data models for the Order Flow Analysis System.
All analysis is built on top of these structures.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List


# ─── CANDLE ──────────────────────────────────────────────────────────────────

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

    # Tier 1 fields — only populated when data comes from exchange APIs (Binance/Bybit)
    taker_buy_volume: Optional[float] = None
    taker_sell_volume: Optional[float] = None
    delta: Optional[float] = None           # taker_buy - taker_sell
    data_tier: int = 2                      # 1 = true order flow, 2 = structural only

    @property
    def body_size(self) -> float:
        return abs(self.close - self.open)

    @property
    def upper_wick(self) -> float:
        return self.high - max(self.open, self.close)

    @property
    def lower_wick(self) -> float:
        return min(self.open, self.close) - self.low

    @property
    def is_bullish(self) -> bool:
        return self.close > self.open

    @property
    def midpoint(self) -> float:
        return (self.high + self.low) / 2

    @property
    def delta_pct(self) -> Optional[float]:
        """Percentage of volume that was aggressive buying (Tier 1 only)."""
        if self.taker_buy_volume is None or self.volume == 0:
            return None
        return self.taker_buy_volume / self.volume


# ─── ORDER BLOCK ─────────────────────────────────────────────────────────────

@dataclass
class OrderBlock:
    symbol: str
    timeframe: str
    direction: str              # 'bullish' or 'bearish'
    high: float
    low: float
    formed_at: datetime
    midpoint: float = field(init=False)

    # Quality factors
    preceded_by_liquidity_grab: bool = False
    displacement_atr_multiple: float = 0.0   # How strong was the impulse after
    caused_bos: bool = False
    is_mitigated: bool = False
    touch_count: int = 0        # Decreases quality on each touch
    quality_score: int = 0      # 1–5, computed on creation

    def __post_init__(self):
        self.midpoint = (self.high + self.low) / 2

    @property
    def mitigation_price(self) -> float:
        """Price at which this OB is considered mitigated."""
        if self.direction == "bullish":
            return self.low     # Closed below the OB low
        return self.high        # Closed above the OB high

    def compute_quality(self):
        score = 1  # Base
        if self.preceded_by_liquidity_grab:
            score += 2
        if self.caused_bos:
            score += 1
        if self.displacement_atr_multiple >= 1.5:
            score += 1
        self.quality_score = min(score, 5)


# ─── FAIR VALUE GAP ──────────────────────────────────────────────────────────

@dataclass
class FairValueGap:
    symbol: str
    timeframe: str
    direction: str              # 'bullish' or 'bearish'
    gap_high: float
    gap_low: float
    formed_at: datetime
    impulse_volume: float = 0.0
    is_mitigated: bool = False
    quality_score: int = 0

    @property
    def midpoint(self) -> float:
        return (self.gap_high + self.gap_low) / 2

    @property
    def size(self) -> float:
        return self.gap_high - self.gap_low


# ─── LIQUIDITY POOL ──────────────────────────────────────────────────────────

@dataclass
class LiquidityPool:
    symbol: str
    price: float
    pool_type: str              # 'BSL' (buy-side) or 'SSL' (sell-side)
    timeframe: str
    formed_at: datetime
    test_count: int = 1         # More tests = more stops resting here = stronger pool
    is_swept: bool = False
    swept_at: Optional[datetime] = None

    @property
    def strength(self) -> str:
        if self.test_count >= 3:
            return "HIGH"
        elif self.test_count == 2:
            return "MEDIUM"
        return "LOW"


# ─── SWING POINT ─────────────────────────────────────────────────────────────

@dataclass
class SwingPoint:
    price: float
    timestamp: datetime
    swing_type: str             # 'high' or 'low'
    timeframe: str
    caused_bos: bool = False


# ─── DELTA / ORDER FLOW ──────────────────────────────────────────────────────

@dataclass
class DeltaBar:
    """Tier 1 data only — populated from exchange taker volume."""
    symbol: str
    timestamp: datetime
    timeframe: str
    delta: float                # taker_buy_volume - taker_sell_volume
    cumulative_delta: float     # Running total from session start
    taker_buy_pct: float        # taker_buy / total_volume — 0.5 = balanced
    bearish_divergence: bool = False   # Price HH but delta LH
    bullish_divergence: bool = False   # Price LL but delta HL
    absorption_signal: bool = False    # Large volume, minimal price movement
    data_source: str = "binance"


# ─── VOLUME PROFILE ──────────────────────────────────────────────────────────

@dataclass
class VolumeProfileLevel:
    price: float
    volume: float
    is_poc: bool = False        # Point of Control
    is_vah: bool = False        # Value Area High
    is_val: bool = False        # Value Area Low
    is_hvn: bool = False        # High Volume Node
    is_lvn: bool = False        # Low Volume Node


@dataclass
class VolumeProfile:
    symbol: str
    timeframe: str
    period_start: datetime
    period_end: datetime
    levels: List[VolumeProfileLevel] = field(default_factory=list)
    poc: Optional[float] = None
    vah: Optional[float] = None
    val: Optional[float] = None
    total_volume: float = 0.0
    data_note: str = (
        "Volume profile approximated from OHLCV. "
        "Precise level requires tick data from Bookmap/Sierra Chart."
    )

    def get_lvns(self) -> List[float]:
        return [l.price for l in self.levels if l.is_lvn]

    def get_hvns(self) -> List[float]:
        return [l.price for l in self.levels if l.is_hvn]


# ─── MARKET STRUCTURE ────────────────────────────────────────────────────────

@dataclass
class MarketStructure:
    symbol: str
    timeframe: str
    trend: str                  # 'bullish', 'bearish', 'neutral'
    last_bos_price: Optional[float] = None
    last_bos_direction: Optional[str] = None
    last_choch_price: Optional[float] = None
    choch_confirmed: bool = False
    recent_swing_highs: List[SwingPoint] = field(default_factory=list)
    recent_swing_lows: List[SwingPoint] = field(default_factory=list)


# ─── SESSION LEVELS ──────────────────────────────────────────────────────────

@dataclass
class SessionLevels:
    symbol: str
    date: str
    asia_high: Optional[float] = None
    asia_low: Optional[float] = None
    london_high: Optional[float] = None
    london_low: Optional[float] = None
    prior_day_high: Optional[float] = None
    prior_day_low: Optional[float] = None
    prior_day_poc: Optional[float] = None
    midnight_open: Optional[float] = None   # 00:00 EST — ICT bias filter
    ny_open: Optional[float] = None         # 08:30 EST
    in_premium: Optional[bool] = None       # True = above midnight open
    asia_swept: Optional[str] = None        # 'high', 'low', or None


# ─── SETUP SIGNAL ────────────────────────────────────────────────────────────

@dataclass
class SetupSignal:
    symbol: str
    direction: str              # 'long' or 'short'
    entry_price: float
    stop_price: float
    target_1: float
    target_2: float
    target_3: Optional[float] = None
    quality_grade: str = "C"   # 'A+', 'B+', 'B', 'C', 'SKIP'
    confidence_score: int = 0  # 0–100
    data_tier: int = 2
    data_tier_label: str = ""
    conditions_met: List[str] = field(default_factory=list)
    risk_warnings: List[str] = field(default_factory=list)
    order_block: Optional[OrderBlock] = None
    fvg: Optional[FairValueGap] = None
    delta_confirmation: Optional[str] = None   # Tier 1 note if available
    position_size: Optional[float] = None
    risk_usd: Optional[float] = None
    risk_reward_1: Optional[float] = None
    risk_reward_2: Optional[float] = None
    generated_at: datetime = field(default_factory=datetime.utcnow)

    @property
    def stop_distance(self) -> float:
        return abs(self.entry_price - self.stop_price)

    @property
    def is_tradeable(self) -> bool:
        return self.quality_grade not in ("C", "SKIP") and not any(
            "DO NOT TRADE" in w for w in self.risk_warnings
        )
