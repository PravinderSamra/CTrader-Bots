# Level Reaction Report — XAUUSD

Generated 2026-08-01 17:01Z · symbolId 41 · last 14 days · spot 4,046.49

Pivot strength 3 · cluster tol 0.060% · touch band ±1.42 pts · break buffer 1.01 pts (needs 2 consecutive closes) · horizon 60m · target cap 3R

> **Data note.** cTrader `volume` is TICK volume (quote updates), not traded contracts,
> and these are Pepperstone CFD/spread-bet prices, not exchange prints. `efficiency` is
> an absorption **proxy**, not a measurement. Every R figure below is a path-dependent
> replay with the stop checked before the target, so it is not inflated by trades that
> would have been stopped out first.

## Overall — every level, every touch

- **60 touch events** across 1 levels
- Level held (no 2-close break): **62%**
- Wick-through beyond the level: median 1.82 · p75 3.58 · p90 4.61 · max 36.42
- Trading it mechanically: win rate 53%, stopped 45%, **expectancy +1.12R**

### Absorption proxy — tick efficiency

Net price progress per 1,000 ticks during the touch. Lower = more churn for less
movement = the signature you are looking for when wicks are being absorbed.

| Outcome | Median efficiency |
|---|---|
| Touches that HELD | 0.952 |
| Touches that BROKE | 1.344 |
| All touches | 1.144 |

**Signal present.** Holds churn 29% more per unit of progress than breaks — low tick-efficiency at your level is evidence for absorption.

## Conditioned on day bias

Day bias = price vs that day's opening print at the moment of the touch. A resistance
test on a bearish day is your short setup; a support test on a bullish day is your long.

| Day bias | Side | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|---|
| bearish | resistance ← | 23 | 70% | 70% | +1.71R | 3.87 |
| bearish | support | 15 | 40% | 27% | +0.13R | 5.89 |
| flat | resistance | 8 | 62% | 38% | +0.50R | 3.17 |
| bullish | resistance | 8 | 75% | 62% | +1.47R | 3.75 |
| bullish | support ← | 6 | 67% | 67% | +1.67R | 3.31 |

Rows marked ← are the with-bias setups: the ones your strategy actually takes.

## Conditioned on session (UTC)

| Session | n | Held | Win rate | Expectancy | p90 pierce |
|---|---|---|---|---|---|
| asia | 12 | 67% | 67% | +1.65R | 3.75 |
| late | 19 | 74% | 58% | +1.29R | 4.84 |
| london | 9 | 44% | 44% | +0.78R | 4.16 |
| us | 20 | 55% | 45% | +0.80R | 4.61 |

## Per level

Sorted by distance from spot — the ones near the top are the ones in play.

| Level | Kind | H1 pivots | Touches | Held | Win rate | Expectancy | Stop (pts) | Dist from spot |
|---|---|---|---|---|---|---|---|---|
| **4,049.44** | both | 3 | 60 | 62% | 53% | +1.12R | 2.05 | 2.95 |

## Trade guidance — nearest levels

### 4,049.44 (both)

- Sample: 60 touches, held 62% — confidence **HIGH**
- Stop: **2.05 pts beyond 4,049.44** (p90 wick-through on non-break visits; deepest ever 36.42)
- Mechanical result: win rate 53%, stopped 45%, expectancy **+1.12R**, median best-case 2.9R

| When (UTC) | Side | Day | Pierce | Closed thru | Broke | Result |
|---|---|---|---|---|---|---|
| 2026-07-31 20:53 | support | bearish | 4.84 | 3.13 | yes | +0.0R |
| 2026-07-31 20:40 | support | bearish | 0.00 | 0.00 | no | -1.0R (stopped) |
| 2026-07-31 20:18 | resistance | bearish | 2.58 | 2.58 | yes | -1.0R (stopped) |
| 2026-07-31 20:10 | resistance | bearish | 0.00 | 0.00 | no | -1.0R (stopped) |
| 2026-07-31 19:52 | support | bearish | 2.78 | 2.44 | no | -1.0R (stopped) |
| 2026-07-31 18:09 | support | bearish | 2.41 | 2.20 | yes | -1.0R (stopped) |

---

**How to use this live.** When price returns to one of these levels you already know
how often it has held, how deep the wicks normally go (so your stop is sized from
evidence rather than nerve), and what fading it has actually paid. What this cannot
tell you is whether sellers are stacked there *right now* — that is what the DOM
recorder in `src/dom_recorder.py` adds once you register a cTrader Open API app.
