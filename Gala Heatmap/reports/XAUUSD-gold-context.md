# Gold Context — futures volume, options positioning, spot-mapped

Generated 2026-08-01 17:03Z · XAUUSD spot 4,046.49 · lookback 30d

## 1. Basis — how futures prices map to your chart

- **Current basis: +57.12 points** (GC front month − XAUUSD spot), median of the last 24 overlapping hours
- 30-day median +6.43 · recent stdev 1.23 · 469 aligned hours

To convert a futures price yourself right now: `spot = futures − 57.12`.

> ⚠️ **Contract roll detected on 2026-07-29** — the basis jumped +58.20 points (+0.07 → +58.27) as GC rolled
> to the next active contract.
>
> **The volume profile below already accounts for this.** Each futures bar is
> converted to spot using *that day's* measured basis, not the current one, so
> pre-roll and post-roll volume land at the correct spot prices. Applying a single
> offset across the roll would misplace a month of volume by ~58 points.

Recent daily basis:

| Date | Median basis |
|---|---|
| 2026-07-23 | +2.78 |
| 2026-07-24 | +2.50 |
| 2026-07-26 | +2.61 |
| 2026-07-27 | +1.94 |
| 2026-07-28 | +0.07 |
| 2026-07-29 | +58.27 |
| 2026-07-30 | +58.20 |
| 2026-07-31 | +56.62 |

## 2. Real volume profile — COMEX gold futures

This is **actual traded contract volume**, not the tick-count that CFD feeds
report. It is the single biggest data upgrade gold has over an index CFD.

All prices are **XAUUSD spot**, converted per bar at that day's measured basis.

| Node | XAUUSD spot | Meaning |
|---|---|---|
| POC | **4,047.37** | most volume traded here — magnet, and a level that grinds |
| VAH | **4,120.02** | top of the 70% value area |
| VAL | **4,018.94** | bottom of the 70% value area |

**High volume nodes** — price slows and chops here; good targets, poor breakout levels.

| XAUUSD spot | Relative volume |
|---|---|
| **4,047.37** | ██████████████ |
| **4,066.32** | ██████████████ |
| **4,025.26** | ███████████ |
| **4,034.73** | ███████████ |
| **4,107.38** | ████████ |
| **4,120.02** | ███████ |
| **4,113.70** | ███████ |
| **4,006.31** | ███████ |

## 3. Options positioning — where size is committed

Source: CBOE delayed GLD chain, 3 nearest expiries (2026-08-03, 2026-08-05, 2026-08-07). GLD 371.54 × **10.901** (measured, not assumed) → spot 4,050.07.

- **Net dealer gamma: +30.4M per 1% move**
  - Positive → dealers hedge *against* the move. Expect **pinning and mean
    reversion**: levels hold more often, breakouts fail more often. This is a
    good regime for fading your pivots.
- **Gamma flip ≈ 4,142.29 spot** — regime changes across this level

### Strikes in intraday reach (±2.5% of spot)

These are the ones that matter for a day trade. Larger OI = more hedging flow
anchored there = a stronger pin.

| XAUUSD spot | Call OI | Put OI | Net gamma | |
|---|---|---|---|---|
| **3,956.98** | 29 | 523 | -1.9M | █ |
| **3,967.88** | 28 | 559 | -2.2M | █ |
| **3,978.78** | 101 | 704 | -2.8M | ██ |
| **3,989.68** | 186 | 593 | -2.2M | ██ |
| **4,000.58** | 98 | 1,243 | -7.9M | ███ |
| **4,011.48** | 117 | 277 | -1.3M | █ |
| **4,022.38** | 1,015 | 678 | +1.6M | ████ |
| **4,033.29** | 1,176 | 4,233 | -31.3M | ████████████ |
| **4,044.19** | 374 | 435 | +0.3M | ██ ← spot |
| **4,055.09** | 350 | 1,004 | -8.4M | ███ ← spot |
| **4,065.99** | 1,516 | 410 | +14.0M | ████ |
| **4,076.89** | 796 | 300 | +5.5M | ██ |
| **4,087.79** | 3,365 | 655 | +21.9M | █████████ |
| **4,098.69** | 2,299 | 147 | +14.8M | █████ |
| **4,109.59** | 493 | 160 | +1.7M | █ |
| **4,120.49** | 707 | 160 | +2.6M | ██ |
| **4,131.39** | 241 | 70 | +0.7M | █ |
| **4,142.29** | 4,794 | 143 | +16.4M | ███████████ |

**Largest open interest overall — call side** (overhead supply, incl. far strikes):

| Strike | XAUUSD spot | Call OI |
|---|---|---|
| 380.0 | **4,142.29** | 4,794 |
| 385.0 | **4,196.80** | 4,361 |
| 400.0 | **4,360.31** | 3,905 |
| 390.0 | **4,251.30** | 3,570 |
| 408.0 | **4,447.51** | 3,367 |
| 375.0 | **4,087.79** | 3,365 |

**Largest open interest — put side** (downside support / pinning magnets):

| Strike | XAUUSD spot | Put OI |
|---|---|---|
| 370.0 | **4,033.29** | 4,233 |
| 340.0 | **3,706.26** | 3,817 |
| 350.0 | **3,815.27** | 3,082 |
| 351.0 | **3,826.17** | 2,124 |
| 360.0 | **3,924.28** | 1,947 |
| 335.0 | **3,651.76** | 1,488 |

> GLD options are a **proxy**. They track gold closely but they are not options on
> COMEX gold futures (OG), whose strikes sit directly on the futures price. CME
> publishes OG open interest by strike daily — it was not reachable from this
> environment (403), but it is worth pulling locally if you lean on this layer.

## 4. Positioning — CFTC Commitment of Traders

Weekly, Tuesday snapshot published Friday. Macro context, not entry timing.

| Week | Open interest | Managed money net | Producers net | Swap dealers net |
|---|---|---|---|---|
| 2026-07-28 | 384,603 | +119,795 | -20,549 | -191,760 |
| 2026-07-21 | 383,368 | +124,831 | -19,321 | -193,878 |
| 2026-07-14 | 383,689 | +120,779 | -19,149 | -195,639 |
| 2026-07-07 | 371,776 | +116,161 | -20,986 | -201,296 |

Producers and swap dealers are structurally short (they hedge physical and
dealer flow); managed money is the speculative side. The reading that matters is
the *change* and the extremes, not the sign.

Managed money is net **+119,795** and cut longs by 5,036 week over week.
Long/short ratio is stretched — crowded long. Fuel for a downside flush if
a support level fails, and a reason to respect resistance.

## 5. Your levels, cross-referenced

A level with a volume node *and* committed options size behind it has a reason to
hold beyond the fact you drew a line there.

| Your level | Nearest volume node | Nearest significant OI | Read |
|---|---|---|---|
| **4,049.44** | 4,047.37 (POC, -2.1) | 4,055.09 (1,354 OI, +5.6) | **strong confluence** |

---

## How to use this with the level engine

`level_stats.py` tells you how a level has behaved. This tells you *why* it might.
A pivot that also sits on the futures POC, inside a large call-OI strike, with
dealers long gamma, is a level with a reason to hold — and the historical hold rate
should confirm it. When the two disagree, trust the history and shrink the size.

**Tiering.** Futures volume profile is real traded volume (Tier 1 for *where volume
happened*, though not aggressor-classified, so it is not delta). Options OI is real
committed size on a proxy instrument. COT is Tier 3 macro context. None of it is a
live order book.
