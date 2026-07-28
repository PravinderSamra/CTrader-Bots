# US30 — 45-Day Sample: Rule Update Impact

Sample: **2026-05-13 → 2026-07-03** (46 trading days, 10,314 M5 bars). First qualifying
breakout per day. Stop 50 / TP 100 (2R) unless noted. cTrader tick volume.

## Updated rules (this run)
1. Loading range is built **up to 09:30 ET** (NY open).
2. **No trading in the first 30 minutes** — 09:30–10:00 ET is skipped.
3. From **10:00 ET**, the **first high-volume 5m candle** that closes beyond the range is the entry.

## Results

| Variant | Trades | Win% | Expectancy | Total R | PF | Avg hold | MaxDD |
|---|---|---|---|---|---|---|---|
| OLD base (range 03–08 London, break from 09:30, no vol) | 28 | 25% | −0.250R | −7.0 | 0.67 | 15.5m | −7.0R |
| NEW structure (range→09:30 ET, exec 10:00–12:00 ET), no vol | 31 | 42% | +0.258R | +8.0 | 1.44 | 20.0m | −5.0R |
| NEW + vol ≥ 1.2× trailing-20 | 18 | 50% | +0.500R | +9.0 | 2.00 | 17.8m | −2.0R |
| NEW + vol z-score ≥ 1.0 | 17 | 47% | +0.412R | +7.0 | 1.78 | 15.9m | −2.0R |
| NEW + vol ≥ 1.5× trailing-20 | 7 | 43% | +0.286R | +2.0 | 1.50 | 15.0m | −2.0R |
| NEW + vol ≥ 2.0× trailing-20 | 0 | — | — | — | — | — | — |
| NEW + vol ≥ 1.5× pre-open(09:30–10:00) | 0 | — | — | — | — | — | — |

RR sensitivity (NEW structure + 1.5× trailing vol, stop 50, n=7):

| RR | Win% | Expectancy | Total R | PF |
|---|---|---|---|---|
| 1.0 | 71% | +0.429R | +3.0 | 2.50 |
| 2.0 | 43% | +0.286R | +2.0 | 1.50 |
| 2.5 | 43% | +0.500R | +3.5 | 1.88 |
| 3.0 | 43% | +0.714R | +5.0 | 2.25 |
| 3.5 | 43% | +0.929R | +6.5 | 2.63 |

## Read-out
- **Waiting to 10:00 ET is the single biggest fix**: on its own it flips the sample from
  −7R (PF 0.67) to +8R (PF 1.44). The 09:30–10:00 window generated false breaks.
- **The high-volume requirement adds real edge**: ≥1.2× trailing-20 lifts win rate 42%→50%,
  expectancy +0.26R→+0.50R, PF 1.44→2.00, and halves max drawdown (−5R→−2R).
- **≥1.2× trailing-20** is the usable threshold on this window; ≥1.5×/≥2.0× and the
  pre-open baseline starve the sample (7 and 0 trades) — reserve judgement until the full
  3-year run.
- High-RR targets look strong but rest on 7 trades here; confirm on full history.

> Caveat: 46 days is a small sample; treat as directional. The full 3-year sweep
> (Phase 3) is the basis for final conclusions. This new rule set is now the study's base.
