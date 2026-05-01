# STAGE 3: SYSTEM ARCHITECTURE
## Order Flow Analysis System — Design Document

---

## HONEST DATA ASSESSMENT

Before building anything, we must be clear about what data we actually have and what it genuinely tells us. Confusing structural/technical analysis with true order flow leads to false confidence.

### Signal Tier Definitions

| Tier | Label | What It Means |
|------|-------|---------------|
| **Tier 1** | TRUE ORDER FLOW | Real bid/ask volume split at the tick level. Shows who is the aggressor. Available for crypto via exchange APIs. |
| **Tier 2** | STRUCTURAL ANALYSIS | Price pattern analysis — order blocks, FVGs, market structure. High quality but does not confirm institutional participation in real time. |
| **Tier 3** | CONFLUENCE FACTOR | Supporting evidence — volume direction, session levels, news context. Adds conviction but not standalone. |

---

## WHAT EACH DATA SOURCE ACTUALLY PROVIDES

### TRUE ORDER FLOW (Tier 1) — Crypto Only, via Exchange Public APIs

| Source | Data | What It Tells Us |
|--------|------|-----------------|
| Binance REST API (`/api/v3/aggTrades`) | Tick-by-tick aggregate trades with buyer/seller maker flag | Whether each trade was an aggressive buy (taker hit the ask) or aggressive sell (taker hit the bid). This IS delta. |
| Binance REST API (`/api/v3/klines`) with `takerBuyBaseAssetVolume` | Taker buy volume per candle | Aggressive buy volume vs total volume per bar. Delta = takerBuy − (total − takerBuy). |
| Bybit REST API (`/v5/market/recent-trade`) | Recent trades with side | Same as Binance — real buy/sell aggression split |
| OKX REST API (`/api/v5/market/trades`) | Trade history with side | Same |

**Key point:** Binance kline data includes `takerBuyBaseAssetVolume` directly in the OHLCV response. This gives us real delta without needing tick data. This is the foundation of our order flow analysis for crypto.

**What we CANNOT get for free (anywhere):**
- True Level 2 DOM (full order book depth with updates)
- Footprint charts (bid/ask volume at each individual price tick within a candle)
- Iceberg order detection
- Exchange-matched order flow for forex and futures (ES, NQ, DAX)

**For forex and futures:** We only have Tier 2 (structural) and Tier 3 (confluence). We must be transparent about this in all outputs.

### STRUCTURAL ANALYSIS (Tier 2) — All Markets

| Source | Data | Analysis |
|--------|------|---------|
| Any OHLCV source | Candle data | Order blocks, FVGs, BOS/CHoCH, liquidity pools, premium/discount zones |
| Alpha Vantage (when connected) | Forex + US stock OHLCV | Structural analysis for EUR/USD, GBP/USD, indices |
| CoinGecko MCP | Crypto OHLCV | Structural analysis for BTC, ETH, altcoins |
| TradingView MCP (when connected) | Multi-TF analysis | Broader structural picture, automated pattern detection |
| Yahoo Finance / Stooq (via WebFetch) | Indices, commodities OHLCV | ES/NQ/DAX/Gold/Oil structural levels |

### CONFLUENCE FACTORS (Tier 3)

| Source | Data | Confluence Use |
|--------|------|---------------|
| Binance kline volume | Total volume per bar | Volume profile approximation, HVN/LVN identification |
| Alpha Vantage VWAP indicator | Session VWAP | VWAP level identification |
| Tavily (when connected) | News search | Catalyst identification, news risk |
| News MCP (when connected) | News feed | Event monitoring |
| AKTools funding rates (when connected) | OKX/Binance funding | Sentiment extremes — contrarian signal |
| CoinGecko market data | Volume trends | Is buying or selling pressure dominant? |

---

## SYSTEM ARCHITECTURE

```
Order Flow Analysis System
├── data/
│   ├── fetchers/
│   │   ├── binance_fetcher.py        # Direct Binance REST API (Tier 1 + Tier 3)
│   │   ├── bybit_fetcher.py          # Direct Bybit REST API (Tier 1 backup)
│   │   ├── coingecko_fetcher.py      # CoinGecko MCP wrapper (Tier 2/3)
│   │   ├── alpha_vantage_fetcher.py  # Alpha Vantage MCP wrapper (Tier 2/3)
│   │   ├── yahoo_fetcher.py          # Yahoo Finance via WebFetch (Tier 2/3)
│   │   └── news_fetcher.py           # Tavily/News MCP wrapper
│   └── models.py                     # Data models (OHLCV, Delta, Signal, etc.)
│
├── analysis/
│   ├── structure.py                  # Order blocks, FVGs, BOS/CHoCH, liquidity pools
│   ├── delta.py                      # Delta calculation from taker volume (Tier 1)
│   ├── volume_profile.py             # Volume profile from OHLCV (POC, VAH, VAL, LVN, HVN)
│   ├── sessions.py                   # Session high/low, kill zones, Asia range
│   ├── zones.py                      # Premium/discount zones, Fibonacci OTE
│   └── confluence.py                 # Confluence scoring (3-tier framework)
│
├── signals/
│   ├── setup_scanner.py              # Scans markets for active setups
│   ├── setup_scorer.py               # A+/B/C scoring with data quality labels
│   └── trade_calculator.py           # Entry/stop/target/position size
│
├── reports/
│   ├── pre_session_report.py         # Generates pre-session analysis
│   └── signal_report.py              # Generates individual setup reports
│
├── config.py                         # Markets to watch, account settings
└── main.py                           # Entry point
```

---

## CORE DATA MODELS

```python
# The data at the heart of every analysis decision

class OHLCVCandle:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    taker_buy_volume: float    # Only available from exchange APIs — Tier 1 data
    taker_sell_volume: float   # Derived: volume - taker_buy_volume
    delta: float               # taker_buy_volume - taker_sell_volume
    data_tier: int             # 1 = true order flow, 2 = structural, 3 = confluence

class OrderBlock:
    timeframe: str
    direction: str             # 'bullish' or 'bearish'
    high: float
    low: float
    mitigation_price: float    # Price at which OB becomes mitigated
    is_mitigated: bool
    preceded_by_liquidity_grab: bool
    displacement_strength: float  # How strong was the impulse after this OB
    quality_score: int         # 1-5

class FairValueGap:
    timeframe: str
    direction: str
    gap_high: float
    gap_low: float
    midpoint: float
    is_mitigated: bool
    quality_score: int

class LiquidityPool:
    price: float
    type: str                  # 'BSL' or 'SSL'
    strength: int              # How many tests / how obvious the level is
    is_swept: bool

class DeltaBar:
    timestamp: datetime
    delta: float               # Tier 1 — only for crypto via exchange APIs
    cumulative_delta: float
    delta_divergence: bool     # Price and delta moving in opposite directions
    data_source: str           # 'binance', 'bybit', etc.

class SetupSignal:
    asset: str
    direction: str             # 'long' or 'short'
    entry_price: float
    stop_price: float
    target_1: float
    target_2: float
    quality: str               # 'A+', 'B', 'C'
    confidence_score: int      # 0-100
    data_quality: str          # 'Tier 1 confirmed', 'Structural only', 'Confluence only'
    conditions_met: list       # Which of the 10 confluence conditions are met
    risk_warnings: list        # Any disqualifying factors
```

---

## ANALYSIS MODULES — DETAILED DESIGN

### 1. Structural Analysis (`analysis/structure.py`)

**Order Block Detection:**
```
For each candle in the OHLCV series:
1. Look for a strong impulse move (body > 1.5x average body size, or close > prior high for bullish)
2. That impulse must cause a BOS (close beyond the most recent swing high/low)
3. The last opposing candle before that impulse = Order Block
4. Mark: OB high, OB low, preceded by liquidity grab (Y/N), mitigation status
5. Quality score:
   +2 if preceded by a liquidity grab (sweep of prior high/low)
   +1 if aligned with higher-TF trend
   +1 if first touch (unmitigated)
   +1 if displacement was exceptionally strong (>2x average body)
```

**Fair Value Gap Detection:**
```
For each 3-candle sequence:
1. Check: candle[i].high < candle[i+2].low (bullish FVG) OR candle[i].low > candle[i+2].high (bearish FVG)
2. The gap must be meaningful in size (> minimum threshold relative to ATR)
3. The middle candle (impulse) must be above-average size
4. Mark: gap_high, gap_low, midpoint, mitigation status
5. Quality score: displacement strength, volume during impulse, higher-TF alignment
```

**BOS / CHoCH Detection:**
```
1. Track swing highs and swing lows on the selected timeframe
2. BOS long: price closes above the most recent significant swing high
3. BOS short: price closes below the most recent significant swing low
4. CHoCH long: in a downtrend, price closes above the swing high created by the last BOS
5. CHoCH short: in an uptrend, price closes below the swing low created by the last BOS
```

**Liquidity Pool Identification:**
```
1. Find all significant swing highs and swing lows
2. Mark equal highs/equal lows (within 0.1% of each other) as high-strength pools
3. Mark prior day/week highs and lows
4. Mark round number levels (e.g., 1.0000, 1.0500 for forex; 50000, 100000 for BTC)
5. Assess strength: number of tests, proximity of stops
```

---

### 2. Delta Analysis (`analysis/delta.py`) — Tier 1, Crypto Only

**Inputs:** Raw kline data from Binance/Bybit with taker_buy_volume field

**Calculations:**
```
Per candle:
  taker_sell_volume = volume - taker_buy_volume
  delta = taker_buy_volume - taker_sell_volume
  
Running (session/daily):
  cumulative_delta = sum(delta) from session start
  
Delta divergence detection:
  bearish: price makes new high but delta does NOT make new high vs prior candle
  bullish: price makes new low but delta does NOT make new low vs prior candle
  
Delta at structural levels:
  When price approaches a marked OB or FVG:
    positive delta at support OB = Tier 1 confirmation of buyers defending
    negative delta at resistance OB = Tier 1 confirmation of sellers defending
```

**Output labels:**
- "Tier 1 Confirmed — Real buy/sell aggression data supporting this level"
- "Tier 1 Divergence — Delta diverging from price at this level"
- "No Tier 1 Data — Structural analysis only (forex/futures)"

---

### 3. Volume Profile (`analysis/volume_profile.py`)

**Approximation method (from OHLCV — no tick data needed):**
```
For each candle:
1. Distribute the candle's volume evenly across its high-low range (simplified TPO method)
2. More precise: use a bell-curve distribution centred at (high+low)/2
3. Sum across all candles in the session to build the profile
4. Identify:
   POC: price level with highest accumulated volume
   Value Area: price levels containing 70% of total volume (expand from POC outward)
   HVN: local peaks in the volume distribution
   LVN: local troughs in the volume distribution
```

**Note in output:** "Volume profile is approximated from OHLCV data. Precise footprint-level accuracy requires tick data."

---

### 4. Session Analysis (`analysis/sessions.py`)

```
Asian session:  20:00–00:00 EST → mark ASH (Asian Session High) and ASL (Asian Session Low)
London session: 02:00–11:00 EST → detect if London sweeps ASH or ASL in first 2 hours
NY session:     07:00–16:00 EST → NY open at 08:30 EST (economic data) and 09:30 EST (equities)

Kill zone windows (highest-probability entry times):
  London kill zone:  02:00–05:00 EST
  NY kill zone:      07:00–10:00 EST
  Silver Bullet 1:   03:00–04:00 EST
  Silver Bullet 2:   10:00–11:00 EST
  Silver Bullet 3:   14:00–15:00 EST

Session bias:
  Check if price is above or below the midnight open (00:00 EST)
  Above = premium → look for shorts
  Below = discount → look for longs
```

---

### 5. Confluence Scoring (`analysis/confluence.py`)

**The 10-point scoring framework from Stage 1:**

```python
def score_setup(setup, context) -> SetupScore:
    score = 0
    conditions_met = []
    risk_flags = []
    
    # HIGH WEIGHT (2 points each)
    if context.higher_tf_trend == setup.direction:
        score += 2; conditions_met.append("Higher-TF trend aligned")
    
    if is_correct_premium_discount_zone(setup):
        score += 2; conditions_met.append("Correct premium/discount zone")
    
    if setup.order_block and not setup.order_block.is_mitigated:
        score += 2; conditions_met.append("Unmitigated order block")
    
    if setup.fvg and not setup.fvg.is_mitigated:
        score += 1; conditions_met.append("Unmitigated FVG")
    
    if setup.preceded_by_liquidity_grab:
        score += 2; conditions_met.append("Preceding liquidity grab (stop hunt)")
    
    if setup.tier1_confirmed:  # Only possible for crypto
        score += 2; conditions_met.append("Tier 1 order flow confirmed (real delta)")
    
    # MEDIUM WEIGHT (1 point each)
    if setup.volume_profile_confluence:
        score += 1; conditions_met.append("Volume profile level confluence")
    
    if setup.in_kill_zone:
        score += 1; conditions_met.append("Kill zone timing")
    
    if setup.vwap_confluence:
        score += 1; conditions_met.append("VWAP/AVWAP confluence")
    
    if setup.multi_tf_agreement:
        score += 1; conditions_met.append("Multi-timeframe agreement")
    
    # RISK FLAGS (disqualifiers)
    if setup.major_news_imminent:
        risk_flags.append("HIGH-IMPACT NEWS WITHIN 30 MINUTES — DO NOT TRADE")
    
    if context.higher_tf_trend != setup.direction and not context.choch_confirmed:
        risk_flags.append("Counter-trend trade without CHoCH confirmation")
    
    if setup.order_block and setup.order_block.is_mitigated:
        risk_flags.append("Order block already mitigated — reduced probability")
    
    # Quality grade
    if score >= 10: quality = "A+"
    elif score >= 7: quality = "B+"
    elif score >= 5: quality = "B"
    elif score >= 3: quality = "C"
    else: quality = "SKIP"
    
    # Data quality label
    if setup.tier1_confirmed:
        data_quality = "Tier 1 + Structural — Highest confidence"
    elif setup.volume_profile_confluence:
        data_quality = "Structural + Volume confluence — Good confidence"
    else:
        data_quality = "Structural analysis only — No real-time order flow data available for this market"
    
    return SetupScore(score, quality, conditions_met, risk_flags, data_quality)
```

---

## MARKET WATCHLIST (Initial Configuration)

```python
WATCHLIST = {
    "crypto": {
        # Exchange APIs available — Tier 1 order flow data possible
        "BTCUSDT": {"exchange": "binance", "data_tier": 1},
        "ETHUSDT": {"exchange": "binance", "data_tier": 1},
        "SOLUSDT": {"exchange": "binance", "data_tier": 1},
    },
    "forex": {
        # Alpha Vantage OHLCV only — Tier 2 structural analysis only
        "EURUSD": {"source": "alpha_vantage", "data_tier": 2},
        "GBPUSD": {"source": "alpha_vantage", "data_tier": 2},
        "USDJPY": {"source": "alpha_vantage", "data_tier": 2},
        "GBPJPY": {"source": "alpha_vantage", "data_tier": 2},
    },
    "indices": {
        # Yahoo Finance / TradingView — Tier 2 structural analysis only
        "SPX":  {"source": "yahoo", "ticker": "^GSPC", "data_tier": 2},
        "NDX":  {"source": "yahoo", "ticker": "^NDX", "data_tier": 2},
        "DAX":  {"source": "yahoo", "ticker": "^GDAXI", "data_tier": 2},
    },
    "commodities": {
        # Yahoo Finance — Tier 2 structural analysis only
        "GOLD": {"source": "yahoo", "ticker": "GC=F", "data_tier": 2},
        "OIL":  {"source": "yahoo", "ticker": "CL=F", "data_tier": 2},
    }
}

# Data tier label for user output
DATA_TIER_LABELS = {
    1: "TRUE ORDER FLOW — Real taker buy/sell volume. Delta and CVD available.",
    2: "STRUCTURAL ANALYSIS ONLY — No real-time bid/ask data. Order flow inferred from price action and volume.",
    3: "CONFLUENCE ONLY — Supporting data. Not sufficient alone for entry decisions."
}
```

---

## PRE-SESSION REPORT FORMAT

```
═══════════════════════════════════════════════════════════
  ORDER FLOW PRE-SESSION REPORT
  {Date} | {Session}: London / New York
═══════════════════════════════════════════════════════════

⚠️  DATA QUALITY NOTICE
  Tier 1 (True Order Flow): BTC, ETH, SOL — real delta available
  Tier 2 (Structural Only): EUR/USD, GBP/USD, ES, NQ, Gold — no DOM/footprint data
  All Tier 2 signals are based on price structure. Real-time confirmation
  must be done on your own platform (Bookmap, Sierra Chart, ATAS, etc.)

──────────────────────────────────────────────────────────
  MACRO CONTEXT
──────────────────────────────────────────────────────────
  Weekly bias:     Bullish / Bearish / Neutral
  Premium/Discount: Price is currently in [PREMIUM/DISCOUNT] zone
  Next BSL target: [Level] — stops resting above [Prior High]
  Next SSL target: [Level] — stops resting below [Prior Low]
  Midnight open:   [Price] → Current price [above/below] → [Bullish/Bearish] bias

──────────────────────────────────────────────────────────
  NEWS & RISK EVENTS TODAY
──────────────────────────────────────────────────────────
  🔴 HIGH IMPACT: [Event] at [Time EST] — AVOID TRADING 15 min before/after
  🟡 MEDIUM: [Event] at [Time EST]

──────────────────────────────────────────────────────────
  SETUPS IN PLAY — [ASSET]
  Data Quality: [TIER 1 / TIER 2 / TIER 3]
──────────────────────────────────────────────────────────

  SETUP 1: [Asset] LONG — Grade: A+ | Confidence: 87/100
  ─────────────────────────────────────────────────────
  Entry zone:    [Price] — [Unmitigated Bullish OB on 15M]
  Stop:          [Price] (below OB low — structural invalidation)
  Target 1:      [Price] ([Prior day high / Next BSL] — 2.1R)
  Target 2:      [Price] ([Weekly liquidity target] — 3.8R)
  Position size: 0.1 BTC (1% risk on $10,000 account)

  Why this setup:
    ✅ Daily trend bullish (BOS above prior weekly high)
    ✅ Price in discount zone (below 50% of weekly range)
    ✅ Unmitigated bullish OB at entry zone
    ✅ Preceding liquidity grab — SSL swept at [Price] on [Date]
    ✅ [TIER 1] Delta bullish at this level — taker buy volume 67% of total
    ✅ Volume profile: LVN directly above entry — fast move likely
    ✅ NY kill zone timing

  Data quality: TIER 1 CONFIRMED — Real buy/sell aggression data supports this level.
  Delta note:    Taker buy volume 67% vs 33% sell over last 4 hours at this zone.
  CVD:           Higher lows on CVD while price made lower lows — bullish divergence.

  Risk warnings: None

  SETUP 2: EUR/USD SHORT — Grade: B | Confidence: 52/100
  ─────────────────────────────────────────────────────
  Entry zone:    1.0845 — [Bearish OB on 4H, aligns with prior day high]
  Stop:          1.0872 (above OB high)
  Target 1:      1.0790 (session low — 2.0R)
  Target 2:      1.0750 (prior week low / SSL — 3.5R)

  Why this setup:
    ✅ Daily trend bearish (lower highs, lower lows)
    ✅ Price in premium zone (above 61.8% of weekly range)
    ✅ Unmitigated bearish OB at 1.0845–1.0855
    ⬜ No preceding liquidity grab yet
    ⬜ Kill zone: wait for London open (02:00 EST)

  ⚠️  DATA QUALITY: STRUCTURAL ANALYSIS ONLY (Tier 2)
  No real-time order flow data available for EUR/USD.
  Before entering, confirm on your platform:
    → Absorption at the OB (large sellers absorbing buyers on footprint)
    → Negative delta at 1.0845–1.0855 zone
    → DOM showing large offers being defended
    → CVD declining as price tests the OB

  Risk warnings:
    → ECB rate decision tomorrow — elevated volatility risk
    → Setup is B grade due to missing liquidity grab confirmation

──────────────────────────────────────────────────────────
  ASIAN RANGE
──────────────────────────────────────────────────────────
  ASH: [Price] | ASL: [Price]
  Watch: If London sweeps ASL first → look for bullish reversal
         If London sweeps ASH first → look for bearish reversal

═══════════════════════════════════════════════════════════
```

---

## IMPLEMENTATION PLAN

### Phase 1 — Data Foundation (Build First)
1. `binance_fetcher.py` — OHLCV with taker buy volume + aggregate trades
2. `coingecko_fetcher.py` — wrapper around CoinGecko MCP
3. `yahoo_fetcher.py` — WebFetch calls to Yahoo Finance for indices/commodities
4. `models.py` — All data models

### Phase 2 — Analysis Engine
5. `structure.py` — OB, FVG, BOS/CHoCH, liquidity pools
6. `delta.py` — Delta, CVD, divergence detection
7. `volume_profile.py` — Volume profile from OHLCV
8. `sessions.py` — Session levels, kill zones, bias
9. `zones.py` — Premium/discount, Fibonacci OTE
10. `confluence.py` — Scoring engine

### Phase 3 — Output Layer
11. `setup_scanner.py` — Scans watchlist for active setups
12. `trade_calculator.py` — Entry/stop/target/sizing
13. `pre_session_report.py` — Full report generation
14. `main.py` — Orchestration

### Phase 4 — Integration
15. Wire up TradingView MCP (when connected) as additional Tier 2/3 data source
16. Wire up Alpha Vantage (when connected) for forex VWAP and indicators
17. Wire up Tavily (when connected) for news catalyst fetching
