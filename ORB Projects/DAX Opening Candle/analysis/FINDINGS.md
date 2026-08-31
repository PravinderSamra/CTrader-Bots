# DAX 5-minute opening candle + 12 EMA — REJECTED

Idea: at the Frankfurt cash open (09:00 CET), take the first 5-minute candle.
Close above the 12 EMA -> long, close below -> short. ATR-based stop,
trailing stop or end-of-day exit.

Data: GER40 M5 from cTrader (symbol 200, GBP spread-bet), 2023-07-02 to
2026-08-20, 198,996 bars. Selection window to 2025-03-31; out-of-sample
from 2025-04-01.

## Why it was rejected

**First pass (no costs) looked strong and was misleading.** The best variant
returned +98R with t=3.39. But it was best-of-16, and it risked only
~9 DAX points per trade (0.5 x ATR, median ATR14 at the open = 17.7 pts).

**Transaction costs kill it.** A 1.5pt round-trip spread is 17% of risk at
that stop width:

| Variant | 0 cost | 1.5pt | 4pt |
|---|---|---|---|
| ATR 0.5, trail 0.5 (the "winner") | +46.2R | **-3.1R** | -85.3R |
| ATR 1.0, trail 0.5 | +44.5R | +19.9R | -21.2R |
| ATR 2.0, trail 2.0 | +39.9R | +27.5R | +7.0R |

The apparent "tight trailing stop is better" dose-response was an artefact
of a frictionless backtest, not a mechanism.

**Redone with costs in the selection** (25 variants, 1.5pt round trip):

- Picked in-sample: ATR x3.0, trail 3.0xATR (+42.3R, t=1.12)
- Out-of-sample: +30.0R, expectancy +0.0852R, **t=0.88**
- Best-of-25 permutation **p = 0.8658 — FAILS**
- 16/25 variants positive out-of-sample vs ~12 from a coin flip

t=0.88 out-of-sample is noise. Compare the US500 15m ORB: p=0.014 with 764
out-of-sample trades and only -18% degradation. That is what a real edge
looks like; this is not one.

## The finding worth keeping

The Frankfurt morning session is genuinely uncorrelated with the US500
New York open:

- DAX opening-candle daily R vs US500 bot daily R: **-0.040**
- Raw DAX 09:00-11:00 CET move vs US500 bot daily R: **-0.011**
- Both lose together on 32% of days — exactly the independent expectation

**The session is right; this strategy is wrong.** A working Frankfurt-morning
strategy would be a genuinely diversifying second bot. Keep looking.
