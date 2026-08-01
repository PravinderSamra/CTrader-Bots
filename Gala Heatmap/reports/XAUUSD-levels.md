# Level Reaction Report — XAUUSD

Generated 2026-08-01 16:33Z · symbolId 41 · last 14 days · spot 4,046.49

Pivot strength 3 · cluster tol 0.060% · touch band ±1.42 pts · break buffer 1.01 pts (needs 2 consecutive closes) · horizon 60m · target cap 3R

> **Data note.** cTrader `volume` is TICK volume (quote updates), not traded contracts,
> and these are Pepperstone CFD/spread-bet prices, not exchange prints. `efficiency` is
> an absorption **proxy**, not a measurement. Every R figure below is a path-dependent
> replay with the stop checked before the target, so it is not inflated by trades that
> would have been stopped out first.

## Overall — every level, every touch

- **422 touch events** across 10 levels
- Level held (no 2-close break): **68%**
- Wick-through beyond the level: median 1.14 · p75 3.49 · p90 4.79 · max 39.22
- Trading it mechanically: win rate 50%, stopped 50%, **expectancy +0.84R**

### Absorption proxy — tick efficiency

Net price progress per 1,000 ticks during the touch. Lower = more churn for less
movement = the signature you are looking for when wicks are being absorbed.

| Outcome | Median efficiency |
|---|---|
| Touches that HELD | 1.264 |
| Touches that BROKE | 1.335 |
| All touches | 1.317 |

**No separation.** Holds and breaks churn about the same. Tick efficiency adds nothing here; you need the DOM layer for a real absorption read.

## Conditioned on day bias

Day bias = price vs that day's opening print at the moment of the touch. A resistance
test on a bearish day is your short setup; a support test on a bullish day is your long.

| Day bias | Side | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|---|
| bearish | resistance ← | 81 | 60% | 42% | +0.58R | 4.60 |
| bearish | support | 128 | 77% | 54% | +0.90R | 4.40 |
| flat | resistance | 23 | 65% | 39% | +0.57R | 5.36 |
| flat | support | 16 | 88% | 56% | +1.19R | 4.29 |
| bullish | resistance | 104 | 66% | 51% | +0.88R | 6.36 |
| bullish | support ← | 70 | 61% | 51% | +1.00R | 4.78 |

Rows marked ← are the with-bias setups: the ones your strategy actually takes.

## Conditioned on session (UTC)

| Session | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|
| asia | 151 | 69% | 47% | +0.80R | 4.77 |
| late | 95 | 75% | 64% | +1.23R | 4.45 |
| london | 66 | 62% | 36% | +0.37R | 4.21 |
| us | 110 | 65% | 49% | +0.85R | 5.94 |

## Per level

Sorted by distance from spot — the ones near the top are the ones in play.

| Level | Kind | H1 pivots | Touches | Held | Win rate | Expectancy | Stop (pts) | Dist from spot |
|---|---|---|---|---|---|---|---|---|
| **4,046.64** | both | 5 | 84 | 74% | 54% | +0.91R | 3.33 | 0.15 |
| **4,040.55** | both | 3 | 61 | 79% | 46% | +0.68R | 3.79 | -5.94 |
| **4,028.65** | both | 2 | 57 | 61% | 33% | +0.22R | 3.17 | -17.84 |
| **4,021.60** | support | 2 | 53 | 64% | 58% | +1.34R | 1.71 | -24.89 |
| **4,010.86** | support | 2 | 37 | 68% | 41% | +0.59R | 2.58 | -35.62 |
| **4,084.93** | both | 5 | 52 | 67% | 58% | +0.91R | 4.69 | 38.44 |
| **3,998.98** | support | 4 | 13 | 77% | 92% | +2.69R | 1.42 | -47.51 |
| **4,106.56** | both | 4 | 28 | 50% | 32% | +0.21R | 3.49 | 60.07 |
| **4,116.65** | resistance | 3 | 30 | 67% | 53% | +1.05R | 3.37 | 70.16 |
| **4,141.31** | resistance | 2 | 7 | 71% | 71% | +1.86R | 1.42 | 94.82 |

## Trade guidance — nearest levels

### 4,046.64 (both)

- Sample: 84 touches, held 74% — confidence **HIGH**
- Stop: **3.33 pts beyond 4,046.64** (p90 wick-through on non-break visits; deepest ever 39.22)
- Mechanical result: win rate 54%, stopped 45%, expectancy **+0.91R**, median best-case 1.9R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 20:53 | support | bearish | 2.04 | 0.33 | no | +0.0R |
| 2026-07-31 20:05 | support | bearish | 1.49 | 1.11 | no | +1.9R |
| 2026-07-31 19:11 | support | bearish | 0.00 | 0.00 | no | +2.7R |
| 2026-07-31 18:35 | support | bearish | 0.00 | 0.00 | no | +1.9R |
| 2026-07-31 18:13 | support | bearish | 0.00 | 0.00 | no | +1.9R |
| 2026-07-31 17:34 | support | bearish | 0.00 | 0.00 | no | +2.5R |

### 4,040.55 (both)

- Sample: 61 touches, held 79% — confidence **HIGH**
- Stop: **3.79 pts beyond 4,040.55** (p90 wick-through on non-break visits; deepest ever 9.98)
- Mechanical result: win rate 46%, stopped 54%, expectancy **+0.68R**, median best-case 2.1R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 17:09 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-31 16:43 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-31 16:06 | support | bearish | 0.00 | 0.00 | no | +2.4R |
| 2026-07-31 15:28 | support | bearish | 3.91 | 2.13 | yes | +2.4R |
| 2026-07-31 14:26 | resistance | bearish | 2.50 | 2.24 | yes | -1.0R (stopped) |
| 2026-07-31 13:21 | resistance | bearish | 6.25 | 4.77 | yes | +3.0R |

### 4,028.65 (both)

- Sample: 57 touches, held 61% — confidence **MEDIUM**
- Stop: **3.17 pts beyond 4,028.65** (p90 wick-through on non-break visits; deepest ever 8.53)
- Mechanical result: win rate 33%, stopped 67%, expectancy **+0.22R**, median best-case 1.9R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 13:54 | resistance | bearish | 4.35 | 3.48 | yes | -1.0R (stopped) |
| 2026-07-31 13:39 | support | bearish | 5.94 | 3.52 | yes | -1.0R (stopped) |
| 2026-07-30 06:28 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-30 05:55 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-30 05:38 | support | bearish | 0.13 | 0.00 | no | +3.0R |
| 2026-07-29 16:55 | resistance | bullish | 4.16 | 2.98 | no | -1.0R (stopped) |

### 4,021.60 (support)

- Sample: 53 touches, held 64% — confidence **HIGH**
- Stop: **1.71 pts beyond 4,021.60** (p90 wick-through on non-break visits; deepest ever 8.99)
- Mechanical result: win rate 58%, stopped 42%, expectancy **+1.34R**, median best-case 3.1R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 14:08 | support | bearish | 0.48 | 0.00 | no | +3.0R |
| 2026-07-31 13:49 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-31 13:43 | support | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-29 16:51 | resistance | bearish | 4.04 | 4.04 | yes | -1.0R (stopped) |
| 2026-07-29 13:22 | resistance | flat | 1.48 | 0.84 | no | +3.0R |
| 2026-07-29 12:38 | resistance | bearish | 4.73 | 3.31 | yes | +3.0R |

### 4,010.86 (support)

- Sample: 37 touches, held 68% — confidence **HIGH**
- Stop: **2.58 pts beyond 4,010.86** (p90 wick-through on non-break visits; deepest ever 9.75)
- Mechanical result: win rate 41%, stopped 59%, expectancy **+0.59R**, median best-case 2.7R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-29 15:43 | resistance | bearish | 4.79 | 4.31 | yes | -1.0R (stopped) |
| 2026-07-29 15:23 | resistance | bearish | 2.57 | 2.04 | no | -1.0R (stopped) |
| 2026-07-29 15:09 | resistance | bearish | 0.00 | 0.00 | no | -1.0R (stopped) |
| 2026-07-29 14:23 | resistance | bearish | 0.00 | 0.00 | no | +3.0R |
| 2026-07-29 13:45 | support | bearish | 4.24 | 2.86 | yes | -1.0R (stopped) |
| 2026-07-29 13:30 | support | bearish | 0.66 | 0.00 | no | -1.0R (stopped) |

---

**How to use this live.** When price returns to one of these levels you already know
how often it has held, how deep the wicks normally go (so your stop is sized from
evidence rather than nerve), and what fading it has actually paid. What this cannot
tell you is whether sellers are stacked there *right now* — that is what the DOM
recorder in `src/dom_recorder.py` adds once you register a cTrader Open API app.
