# Minimum stop width — tested properly, at M5, with an out-of-sample split

Run 2026-11-16. The one change with a measured rationale behind it: trades
killed by sequencing had a median stop of 0.223%, survivors 0.361%.

Three candidate fixes, all run through the **true intraday M5 simulation**
with spread included, and all split across the two halves of the 3 years so
nothing could be chosen by fitting:

- **A — WIDEN:** push the stop out to a floor, keep every trade
- **B — SKIP:** drop the trade if its natural stop is tighter than the floor
- **C — BUFFER:** place the stop a fixed extra margin below the breach low

## What replicated and what didn't

**A (widen) — noise.** 0.30% looked good in both halves (+0.571 / +0.519) but
0.20%, 0.40%, 0.50% and 0.60% were mixed or worse. No consistent pattern.
Widening also shrinks every R multiple, which cancels the benefit.

**C (buffer) — a wash.** The best setting returned +0.429R in the second half
against a baseline of +0.425R. Nothing there.

**B (skip tight trades) — replicated.** Every floor tested beat the baseline in
**both halves**, which is the first result in this whole exercise to do that:

| floor | 1st half avgR | 2nd half avgR |
|---|---|---|
| baseline | +0.512 | +0.425 |
| 0.20% | +0.671 | +0.525 |
| 0.25% | +0.816 | +0.652 |
| 0.30% | +0.951 | +0.572 |
| 0.35% | +0.876 | +0.692 |

It is the whole family improving, not one lucky parameter.

## Full period (NAS100, 3 years, M5, 1-pt spread)

| min stop | n | win% | avg R | total R | max DD | R/yr | ret ÷ DD |
|---|---|---|---|---|---|---|---|
| none | 179 | 38.5% | +0.468 | +83.7 | 10.3R | +27.9 | 2.70 |
| 0.20% | 127 | 41.7% | +0.590 | +75.0 | 9.1R | +25.0 | 2.73 |
| **0.25%** | **104** | **45.2%** | **+0.721** | **+75.0** | **8.2R** | **+25.0** | **3.06** |
| 0.30% | 85 | 45.9% | +0.737 | +62.7 | 9.1R | +20.9 | 2.28 |
| 0.35% | 68 | 47.1% | +0.768 | +52.2 | 7.1R | +17.4 | 2.44 |
| 0.40% | 55 | 43.6% | +0.611 | +33.6 | 7.1R | +11.2 | 1.58 |

Buy & hold over the same window: +24.9%/yr, 22.9% DD, ratio **1.09**.

## What it actually buys

**The robust part:** skipping tight-stop trades lifts the win rate 38.5% → 45%
and avg R from +0.47 to +0.72, and cuts max drawdown from 10.3R to 8.2R.

**The cost:** it removes 42% of the trades and about 10% of total return.
Return per unit of drawdown improves from 2.70 to 3.06 — real, but modest.

**Don't over-read 0.25% as "the" number.** The ratios across floors go
2.73 → 3.06 → 2.28 → 2.44 → 1.58, which is bumpy, not a clean plateau. The
honest reading is "somewhere around 0.2–0.3%", chosen as the best of five on
the full period. The *family* replicated; the precise optimum did not.

**Why it works, probably:** a shallow poke below yesterday's low that recovers
is not a failed breakdown, it is noise. A deep breach that then reclaims is an
actual rejection. The filter is selecting for signal, not just for room — note
that R is already normalised by risk, so a wider stop does not mechanically
produce a higher R.

## Does it change the verdict? Not really.

For a $100,000 account with a $90,000 floor:

| | at 1% risk/trade | at 0.5% risk/trade |
|---|---|---|
| no filter | +27.9%/yr, **10.3% DD** | +14.0%/yr, 5.2% DD |
| 0.25% filter | +25.0%/yr, **8.2% DD** | +12.5%/yr, 4.1% DD |

The filter pulls the 1% drawdown back from 10.3% to 8.2% — from "would have
failed the challenge" to "survives it with very little room". The bind is the
same, just slightly less tight: the leverage that makes the return attractive
is still the leverage that nearly fails you, and the safe leverage still loses
to simply holding the index.

And this is NAS100 over a +95% three-year run. ES tested weaker throughout.

## Status

Tested thoroughly, as intended. The filter is a genuine, replicated
improvement — worth keeping if this is ever built — but it is not the thing
that turns arm A into a strategy worth committing challenge capital to.

Still untested: arm A at M5 on ES, and weekend-gap exposure.
