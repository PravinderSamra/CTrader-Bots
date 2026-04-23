# Confluence Signal Guide

This document explains every confluence signal used by the Trade Picker system — what it measures, why it was chosen, and how its behaviour differs across forex, crypto, stocks, and indices.

---

## The Core Principle

The Trade Picker is a **mean reversion** system. The thesis is simple: price periodically overshoots statistical equilibrium, and when it does, the probability of a snap-back is higher than random. The confluence signals are not predicting the future — they are measuring how far price has deviated from equilibrium and counting how many independent indicators agree that the deviation is extreme.

The more independent signals that agree, the less likely the extreme is random noise, and the more likely it is a genuine reversal point.

---

## Universal Signals (Apply to All Markets)

These five signals work across forex, crypto, stocks, and indices because they are purely mathematical calculations on price data. Market structure does not change how they are calculated or interpreted.

---

### 1. Bollinger Band Extreme — +2 points

**What it measures**: Statistical distance from the mean. The lower band is 2 standard deviations below the 20-period moving average. The upper band is 2 standard deviations above it.

**Why +2 (highest weight)**: Statistically, price spends approximately 95% of its time *inside* the bands. Being outside them does not mean price will reverse immediately — but it does mean the current move is at a historical extreme. This is the most objective measure of "how extreme is this?" available without requiring any external data.

**Direction signal**:
- Price at/below BB lower → Long signal (+2)
- Price at/above BB upper → Short signal (+2)

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Very reliable on major pairs. Liquid, normally-distributed returns mean BB extremes genuinely represent statistical outliers. |
| Crypto | Still works but crypto trends more aggressively. BB extremes during strong downtrends can persist for days. The ADX filter (see below) is the safety valve — ADX < 20 confirms the market is ranging, not trending. |
| Stocks | Reliable. Individual stocks can have earnings-driven gaps through the bands — the earnings clearance filter (see disqualifiers) removes this risk. |
| Indices | Very reliable. Indices represent aggregated price behaviour, which smooths individual outliers and makes BB extremes particularly meaningful. |

---

### 2. EMA200 Confluence — +2 points

**What it measures**: Whether the current price is at the 200-period exponential moving average — the single most widely monitored long-term trend level globally.

**Why +2 (highest weight)**: This is the only signal in the system that is explicitly self-fulfilling. The EMA200 works because institutional participants — banks, hedge funds, algorithmic desks — all watch it and place orders around it. When price returns to EMA200 after an extended move away, there is a statistically disproportionate concentration of orders at that level. The level creates its own gravity.

It is assigned +2 not because of any mathematical property, but because of the **institutional consensus** that surrounds it. When a BB extreme and EMA200 coincide (as in the EURNZD trade — within 1 pip), you have both a statistical extreme and an institutional order concentration at the same price. This combination is the most powerful setup in the system.

**Condition**: Price within 0.05% of EMA200 (long or short, as it can be resistance too).

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Strongest market for this signal. Forex desks globally use EMA200 as a key level. The signal is particularly potent on daily/4H timeframes. |
| Crypto | Bitcoin and Ethereum traders heavily reference EMA200. Reliable on BTC, ETH, SOL. On smaller altcoins, thinner markets mean the self-fulfilling aspect is weaker. |
| Stocks | EMA200 is arguably *more* important in equities than forex. It is the standard institutional benchmark — fund managers refer to stocks being "above or below the 200" as a regime filter. |
| Indices | Same as stocks. The 200-day MA on SPX, NDX, DAX, FTSE is watched globally and represents the line between bull and bear regime. Touches of this level from above (potential long) are among the highest-probability setups in the system. |

---

### 3. Stochastic Oscillator Extreme — +2 points

**What it measures**: Where the current closing price sits within the recent high-low range, expressed as a percentage. Stoch %K below 15 means price closed near the very bottom of its recent range. Above 85 means it closed near the very top.

**Why +2 (highest weight)**: Stochastic and BB measure extremes from different angles — BB measures standard deviation from the mean, Stochastic measures position within the recent range. They are correlated but not identical. When both fire simultaneously, they are providing independent confirmation from two different mathematical frameworks that price is at an extreme. That independence justifies the equal weighting.

Stochastic at 5.6 (as in the EURNZD trade) means price is in the bottom 5.6% of its recent range. At that reading, short-term momentum is fully exhausted.

**Direction signal**:
- %K < 15 → Long signal (+2)
- %K > 85 → Short signal (+2)

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Excellent. Forex pairs oscillate predictably enough that Stochastic extremes have a high reversion rate, especially on 1H–4H timeframes in liquid pairs. |
| Crypto | Works but less reliable in strong trends. In a trending crypto market, Stoch can pin at 5 for days. Again, ADX < 20 is the filter that makes this safe to use. |
| Stocks | Reliable, particularly for stocks that follow index direction. A stock with Stoch at 8 while the broader index is stable is a strong signal. |
| Indices | Very reliable. Indices rarely pin at Stochastic extremes for extended periods — the diversification across components means extreme readings are genuinely statistical events. |

---

### 4. RSI Extreme — +1 point

**What it measures**: Relative Strength Index — the ratio of average up-closes to average down-closes over 14 periods, normalised to 0–100. Below 35 indicates recent selling pressure has been dominant. Above 65 indicates recent buying pressure has been dominant.

**Why +1 (lower weight than Stochastic)**: RSI and Stochastic measure similar things — short-term momentum — and are highly correlated. When Stochastic is at 5.6, RSI is almost always below 35. They rarely disagree. Because RSI adds corroborating rather than independent evidence when Stochastic is already firing, it is weighted lower to avoid double-counting the same underlying signal.

RSI also has a known limitation: in strong trending markets, it can sustain readings below 35 or above 65 for extended periods, making it less reliable as a pure reversal indicator when used alone.

**Direction signal**:
- RSI < 35 → Long signal (+1)
- RSI > 65 → Short signal (+1)

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Consistent. Forex major pairs rarely sustain RSI < 30 for more than a few sessions without a reversion. |
| Crypto | Unreliable alone. BTC has traded with RSI < 30 for weeks during bear markets. Always pair with ADX filter. |
| Stocks | Good at identifying oversold individual stocks. More powerful when sector peers are not equally oversold (relative weakness signal). |
| Indices | Reliable. Index RSI < 35 is historically a strong mean reversion signal — it tends to represent panic selling events that historically reverse. |

---

### 5. ADX Below 20 — +1 point (regime filter)

**What it measures**: Average Directional Index — the strength of the prevailing trend, regardless of direction. ADX does not indicate up or down. It indicates strong or weak. ADX > 25 = trending. ADX < 20 = ranging/oscillating.

**Why this signal is categorically different from the others**: ADX is not a directional signal — it is a **regime filter**. It does not tell you where price will go. It tells you whether the current market conditions are suitable for a mean reversion strategy at all.

Mean reversion works in ranging markets. In trending markets, what looks like a BB extreme at EMA200 might simply be price pulling back before continuing in the trend direction. ADX < 20 confirms the market is oscillating, not trending — which is the prerequisite for all the other signals to be meaningful.

Think of it this way: all the other signals identify *where* the extreme is. ADX identifies *whether the type of move that creates extremes is actually mean-reverting right now*.

**Direction signal**: +1 regardless of long or short (applies to both).

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Major pairs spend significant time in ADX < 20 regimes, particularly during Asian sessions and mid-week consolidation. This signal fires frequently and is highly applicable. |
| Crypto | The most important filter for crypto. Without ADX < 20, you risk fading moves in strong crypto trends, which have historically caused the largest losses in mean reversion strategies. |
| Stocks | Important but less decisive than in crypto. Individual stocks can have sector catalysts that create trends even with low ADX readings. Use alongside earnings clearance check. |
| Indices | Indices spend less time in ADX < 20 than individual instruments because they represent aggregated behaviour. When ADX < 20 does fire on an index, it is a high-conviction regime signal. |

---

### 6. MACD Crossover — +1 point

**What it measures**: The MACD line (12-period EMA minus 26-period EMA) crossing above or below its 9-period signal line. A bullish crossover means short-term momentum is turning up. A bearish crossover means it is turning down.

**Why +1 (lowest weight)**: MACD is a lagging indicator. It does not fire at the exact bottom or top — it fires after momentum has already begun turning. By the time MACD crosses, you have likely already missed 20–40% of the initial move from the extreme. This makes it useful as confirmation — "momentum has genuinely turned" — but not useful as the primary trigger.

MACD crossovers also generate noise in ranging markets because price oscillation causes frequent, small crossovers that do not represent meaningful direction changes. Its signal-to-noise ratio is lower than BB or Stochastic.

**Direction signal**:
- Bullish crossover → Long signal (+1)
- Bearish crossover → Short signal (+1)

**How it behaves by market**:
| Market | Behaviour |
|--------|-----------|
| Forex | Useful as a timing confirmation. If entry is triggered at a BB/EMA200 extreme and MACD is also crossing bullish, it provides extra confidence the move has started. |
| Crypto | Similar utility. Lagging nature means it misses the initial entry but confirms direction. |
| Stocks | Same as forex. More useful on daily timeframes for stocks than intraday, given the noisier intraday price action on individual equities. |
| Indices | Good confirmation signal. Index MACD crossovers on daily charts carry significant weight because the index represents aggregated institutional positioning. |

---

## Stock and Index Additional Signals

These two signals apply **only to stocks and indices**. They are not applied to forex or crypto.

---

### 7. Volume Spike at Extreme — +1 point (stocks/indices only)

**What it measures**: Whether volume on the current candle or session is above the 20-day average volume, measured at the point of the BB extreme. Threshold: current volume > 1.5× the 20-day average.

**Why it is stock/index specific**: Volume is largely meaningless in spot forex because forex is OTC — there is no central exchange and no true volume. What exists is tick count or notional estimates, which do not represent actual participation. In stocks and indices, volume is real and represents actual shares exchanged between buyers and sellers on exchange.

**What a volume spike at an extreme means**: When price hits BB lower with a volume spike, it indicates that a large number of participants are actively selling — often interpreted as **climax/capitulation selling**. Capitulation is historically associated with exhaustion of the dominant move. Sellers have not disappeared — they have accelerated to a peak and are now running out of supply. This is a mechanical turning point that has nothing to do with forecasting and everything to do with order flow exhaustion.

Without a volume spike, a BB extreme on stocks may simply reflect a slow drift lower with minimal participation — less likely to attract buyers aggressively.

**Direction signal**: +1 for both long (spike at BB lower) and short (spike at BB upper).

---

### 8. Index Regime Alignment — +1 point (stocks only, not indices themselves)

**What it measures**: Whether the broad market index (S&P 500 for US stocks, FTSE for UK stocks, etc.) is above or below its EMA50 at the time of the analysis.

**Why it is stock-specific**: Individual stocks move in correlation with their broader index. A stock at a perfect technical extreme with 8/12 confluence has a materially higher probability of reversal if the broad index is in a bullish regime (above EMA50) than if the broad index is itself in a downtrend. When the index is falling, it creates persistent selling pressure that can override individual stock mean reversion setups.

This signal is a macro tailwind check — it does not invalidate the setup, but it adds or withholds a point based on whether the environment is supportive.

**Direction signal**:
- Broad index above EMA50 → +1 for Long stock setups
- Broad index below EMA50 → +1 for Short stock setups

**Why not applied to indices themselves**: Indices are their own regime. Checking whether SPX is above EMA50 when you are analysing SPX itself creates a circular reference.

---

## Hard Disqualifiers (Non-Negotiable Filters)

These conditions eliminate a candidate entirely, regardless of confluence score:

| Disqualifier | Applies To | Reason |
|---|---|---|
| High-impact news within 4 hours | All markets | Scheduled macro events (central bank decisions, NFP, CPI) create binary directional moves that override technical levels. Mean reversion cannot compete with a catalyst. |
| Earnings within 5 trading days | Stocks only | Earnings reports cause gap moves that can be multiples of the stop distance. The strategy has no edge around earnings. |
| ADX > 30 | All markets | Strong trending regime. Mean reversion setups in strong trends have negative expectancy. |
| Bid-ask spread > 0.1% | Forex/Crypto | Elevated spread indicates unusual conditions (low liquidity session, market stress) and directly reduces R:R. |
| Average daily volume < 500k shares | Stocks | Illiquid stocks are subject to manipulation and wide spreads. The institutional order flow assumptions underlying the EMA200 signal do not apply. |
| Stablecoin or pegged currency | Crypto/Forex | By definition, these instruments do not mean revert — they are priced to a fixed peg. |

---

## Scoring Summary by Market

| Signal | Forex | Crypto | Stocks | Indices |
|--------|-------|--------|--------|---------|
| BB Extreme | +2 | +2 | +2 | +2 |
| EMA200 Confluence | +2 | +2 | +2 | +2 |
| Stochastic Extreme | +2 | +2 | +2 | +2 |
| RSI Extreme | +1 | +1 | +1 | +1 |
| ADX < 20 | +1 | +1 | +1 | +1 |
| MACD Crossover | +1 | +1 | +1 | +1 |
| Volume Spike | — | — | +1 | +1 |
| Index Regime | — | — | +1 | — |
| **Max Score** | **10** | **10** | **12** | **11** |
| **Min to Trade** | **6** | **6** | **7** | **7** |

---

## Cross-Market Normalisation

When comparing setups across different markets to find the single best trade, raw scores are normalised to a common scale:

```
Normalised Score = (Raw Score / Max Score for that market) × 10
```

Examples:
- Forex 8/10 → normalised 8.0
- Stock 10/12 → normalised 8.3
- Index 8/11 → normalised 7.3
- Crypto 7/10 → normalised 7.0

The highest normalised score wins, regardless of instrument type. This ensures the system does not have a built-in bias toward any single market.

---

## Why Mean Reversion Over Trend Following?

This system was designed for scalping — short duration, tight stops, targeting statistical snap-backs. Mean reversion was chosen over trend following for one practical reason: it is easier to define **where you are wrong**. 

In a mean reversion trade, the setup is invalidated the moment price moves beyond the statistical extreme and continues — stop placement is natural and mechanical. In trend following, continuation trades require larger stops relative to targets, which increases risk per trade.

The confluence scoring system is specifically calibrated for mean reversion. If the system is adapted in future for swing or trend-following setups, the signal weights and minimum thresholds would need to be reconsidered.

---

*Document maintained alongside Trade Picker AgentSkill.md. Update when confluence rules change.*
