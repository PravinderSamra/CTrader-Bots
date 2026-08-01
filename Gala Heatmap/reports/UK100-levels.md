# Level Reaction Report — UK100

Generated 2026-08-01 16:32Z · symbolId 113 · last 14 days · spot 10,870.00

Pivot strength 3 · cluster tol 0.060% · touch band ±3.80 pts · break buffer 2.72 pts (needs 2 consecutive closes) · horizon 60m · target cap 3R

> **Data note.** cTrader `volume` is TICK volume (quote updates), not traded contracts,
> and these are Pepperstone CFD/spread-bet prices, not exchange prints. `efficiency` is
> an absorption **proxy**, not a measurement. Every R figure below is a path-dependent
> replay with the stop checked before the target, so it is not inflated by trades that
> would have been stopped out first.

## Overall — every level, every touch

- **193 touch events** across 8 levels
- Level held (no 2-close break): **66%**
- Wick-through beyond the level: median 4.14 · p75 7.30 · p90 9.90 · max 25.50
- Trading it mechanically: win rate 49%, stopped 50%, **expectancy +0.91R**

### Absorption proxy — tick efficiency

Net price progress per 1,000 ticks during the touch. Lower = more churn for less
movement = the signature you are looking for when wicks are being absorbed.

| Outcome | Median efficiency |
|---|---|
| Touches that HELD | 4.274 |
| Touches that BROKE | 4.515 |
| All touches | 4.290 |

**No separation.** Holds and breaks churn about the same. Tick efficiency adds nothing here; you need the DOM layer for a real absorption read.

## Conditioned on day bias

Day bias = price vs that day's opening print at the moment of the touch. A resistance
test on a bearish day is your short setup; a support test on a bullish day is your long.

| Day bias | Side | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|---|
| bearish | resistance ← | 39 | 56% | 44% | +0.64R | 9.05 |
| bearish | support | 38 | 66% | 55% | +1.15R | 8.50 |
| flat | resistance | 5 | 60% | 20% | -0.20R | 9.20 |
| flat | support | 17 | 82% | 29% | -0.00R | 7.00 |
| bullish | resistance | 49 | 59% | 49% | +0.94R | 10.70 |
| bullish | support ← | 45 | 76% | 60% | +1.37R | 11.10 |

Rows marked ← are the with-bias setups: the ones your strategy actually takes.

## Conditioned on session (UTC)

| Session | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|
| asia | 53 | 66% | 43% | +0.59R | 7.26 |
| late | 22 | 77% | 68% | +1.66R | 7.70 |
| london | 73 | 62% | 47% | +0.86R | 12.20 |
| us | 45 | 67% | 51% | +1.01R | 10.15 |

## Per level

Sorted by distance from spot — the ones near the top are the ones in play.

| Level | Kind | H1 pivots | Touches | Held | Win rate | Expectancy | Stop (pts) | Dist from spot |
|---|---|---|---|---|---|---|---|---|
| **10,870.70** | support | 2 | 32 | 62% | 50% | +0.97R | 6.10 | 0.70 |
| **10,911.00** | resistance | 3 | 36 | 64% | 28% | +0.07R | 6.70 | 41.00 |
| **10,818.94** | both | 5 | 21 | 76% | 76% | +2.05R | 5.74 | -51.06 |
| **10,792.40** | both | 2 | 27 | 67% | 33% | +0.29R | 8.40 | -77.60 |
| **10,967.95** | resistance | 2 | 8 | 50% | 75% | +2.00R | 3.80 | 97.95 |
| **10,754.52** | both | 4 | 15 | 87% | 93% | +2.73R | 3.80 | -115.48 |
| **10,702.00** | support | 3 | 28 | 75% | 57% | +1.08R | 7.30 | -168.00 |
| **10,557.05** | both | 2 | 26 | 46% | 31% | +0.16R | 6.55 | -312.95 |

## Trade guidance — nearest levels

### 10,870.70 (support)

- Sample: 32 touches, held 62% — confidence **HIGH**
- Stop: **6.10 pts beyond 10,870.70** (p90 wick-through on non-break visits; deepest ever 25.50)
- Mechanical result: win rate 50%, stopped 47%, expectancy **+0.97R**, median best-case 2.6R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 19:11 | resistance | bearish | 8.20 | 8.10 | yes | +0.0R |
| 2026-07-31 18:10 | resistance | bearish | 3.40 | 2.70 | no | -1.0R (stopped) |
| 2026-07-31 17:11 | resistance | bearish | 6.40 | 5.30 | yes | +1.6R |
| 2026-07-31 16:21 | resistance | bearish | 2.90 | 2.30 | no | -1.0R (stopped) |
| 2026-07-31 15:52 | resistance | bearish | 1.40 | 0.00 | no | +2.5R |
| 2026-07-31 15:16 | support | bearish | 25.50 | 19.10 | yes | -1.0R (stopped) |

### 10,911.00 (resistance)

- Sample: 36 touches, held 64% — confidence **MEDIUM**
- Stop: **6.70 pts beyond 10,911.00** (p90 wick-through on non-break visits; deepest ever 13.00)
- Mechanical result: win rate 28%, stopped 72%, expectancy **+0.07R**, median best-case 1.7R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 12:09 | resistance | bearish | 2.20 | 1.50 | no | +3.0R |
| 2026-07-31 11:55 | resistance | bearish | 0.00 | 0.00 | no | +2.9R |
| 2026-07-31 11:24 | support | bearish | 10.50 | 9.80 | yes | -1.0R (stopped) |
| 2026-07-31 11:07 | support | bearish | 8.20 | 7.00 | yes | -1.0R (stopped) |
| 2026-07-31 11:02 | support | bearish | 0.00 | 0.00 | no | -1.0R (stopped) |
| 2026-07-31 07:03 | resistance | bearish | 13.00 | 10.40 | yes | -1.0R (stopped) |

### 10,818.94 (both)

- Sample: 21 touches, held 76% — confidence **HIGH**
- Stop: **5.74 pts beyond 10,818.94** (p90 wick-through on non-break visits; deepest ever 10.46)
- Mechanical result: win rate 76%, stopped 24%, expectancy **+2.05R**, median best-case 3.2R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 14:15 | support | bearish | 1.44 | 0.00 | no | +3.0R |
| 2026-07-30 06:16 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-30 06:02 | resistance | bearish | 10.46 | 10.26 | yes | -1.0R (stopped) |
| 2026-07-30 02:35 | support | bearish | 5.74 | 5.54 | no | -1.0R (stopped) |
| 2026-07-30 00:37 | support | bearish | 2.44 | 1.34 | no | +3.0R |
| 2026-07-29 19:39 | support | bearish | 5.64 | 3.64 | no | +3.0R |

### 10,792.40 (both)

- Sample: 27 touches, held 67% — confidence **MEDIUM**
- Stop: **8.40 pts beyond 10,792.40** (p90 wick-through on non-break visits; deepest ever 12.30)
- Mechanical result: win rate 33%, stopped 67%, expectancy **+0.29R**, median best-case 1.3R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-30 05:36 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-30 05:15 | resistance | bearish | 7.60 | 7.30 | no | -1.0R (stopped) |
| 2026-07-30 04:37 | support | bearish | 7.10 | 5.70 | yes | -1.0R (stopped) |
| 2026-07-30 04:10 | support | bearish | 0.00 | 0.00 | no | -1.0R (stopped) |
| 2026-07-30 03:40 | support | bearish | 0.00 | 0.00 | no | +2.1R |
| 2026-07-28 13:07 | support | bullish | 0.00 | 0.00 | no | +3.0R |

### 10,967.95 (resistance)

- Sample: 8 touches, held 50% — confidence **MEDIUM**
- Stop: **3.80 pts beyond 10,967.95** (p90 wick-through on non-break visits; deepest ever 13.45)
- Mechanical result: win rate 75%, stopped 25%, expectancy **+2.00R**, median best-case 3.2R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 09:01 | support | bullish | 13.45 | 9.65 | yes | -1.0R (stopped) |
| 2026-07-31 08:49 | resistance | bullish | 5.85 | 5.55 | yes | -1.0R (stopped) |
| 2026-07-31 08:15 | resistance | bullish | 6.85 | 4.75 | yes | +3.0R |
| 2026-07-31 07:25 | resistance | bullish | 10.85 | 7.55 | yes | +3.0R |
| 2026-07-30 13:07 | resistance | bullish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-30 09:16 | resistance | bullish | 1.45 | 0.55 | no | +3.0R |

---

**How to use this live.** When price returns to one of these levels you already know
how often it has held, how deep the wicks normally go (so your stop is sized from
evidence rather than nerve), and what fading it has actually paid. What this cannot
tell you is whether sellers are stacked there *right now* — that is what the DOM
recorder in `src/dom_recorder.py` adds once you register a cTrader Open API app.
