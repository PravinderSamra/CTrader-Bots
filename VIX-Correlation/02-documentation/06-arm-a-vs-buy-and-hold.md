# Arm A vs buy and hold — with the sequencing bias measured properly

Run 2026-11-16, answering Vanessa's question: does the plain previous-day-low
reclaim beat buy and hold, or is there no point continuing?

## First: my earlier sequencing estimate was wrong

Stages 2a/2b spot-checked sessions at **M30** and found 1 winner in 9 killed by
sequencing — about **11%**. I used that to project arm A's degradation.

Re-running the same test on **M5** bars, over the 3 years of NAS100 data
already in the repo (`US30 London Range Breakout/data/NAS100/nas100_m5.csv`),
gives a very different number on 179 events:

| method | win% | avg R | total R |
|---|---|---|---|
| DAILY (what stages 1–3 used) | 53.6% | +1.097 | +196.4 |
| **INTRADAY, M5 (true)** | **38.5%** | **+0.505** | **+90.4** |

**36 of 96 winners — 37.5% — are killed by sequencing, and 54% of the apparent
edge disappears.** Not 11%.

**Why M30 was too optimistic:** when the breach and the reclaim fall inside the
same 30-minute bar, that bar's low is the deepest point of the whole half hour,
so the stop gets placed deeper — wider, safer, less likely to be hit. At M5 the
fill is located properly and the stop sits at the shallower low actually made
*before* entry. Tighter stop, more stop-outs. The coarser the bars, the more
flattering the result.

The trades sequencing kills have a **median stop of 0.223%**; the survivors
**0.361%**. Tight stops are where it bites, which is consistent with stage 2a —
the magnitude was just far larger than a 13-event sample could show.

## The honest comparison (NAS100, 3 years, true M5 simulation, spread included)

| | Return/yr | Max drawdown | Return ÷ DD |
|---|---|---|---|
| **Buy & hold NAS100** | +24.9% | **22.9%** | 1.09 |
| **Arm A @ 1.0% risk/trade** | **+27.9%** | **10.0%** | **2.79** |
| **Arm A @ 0.5% risk/trade** | +14.0% | 5.0% | 2.80 |

179 trades, 60/yr, 38.5% win rate, +0.468R per trade after a 1-point spread.
Worst run of losses: 10R.

## Answer to the question

**Risk-adjusted: yes, clearly — about 2.6× the return per unit of drawdown**,
and that holds at either risk level because the ratio is leverage-invariant.

**On raw return: marginal, and it depends on leverage and instrument.** At 1%
risk it beats buy and hold by 3 points a year; at 0.5% it loses by 11.

**And the instrument matters more than I'd like.** The ES figures from stage 3
are weaker than NAS100's: daily-method +0.438R against NAS100's +1.097R. Apply
the same 54% haircut and ES lands near **+0.20R**, which at 1% risk is roughly
**+11.6%/yr against ES buy-and-hold's +13.1%** — i.e. **below** it on raw
return, though still on half the drawdown.

Part of that gap is the period: NAS100's three years ran +95%, and a long-only
mean-reversion strategy flatters itself in a strong uptrend. Neither test says
anything about a sustained decline.

## What this means for the account

At **1% risk** the worst run is **10R = 10% of the account**. On a $100,000
challenge with a $90,000 floor that is the entire budget in one bad stretch,
and it happened inside a 3-year sample. **Not viable at that size.**

At **0.5% risk** the drawdown is a comfortable 5%, but the return (+14%/yr on
NAS100, less on ES) no longer beats simply holding the index.

That is the real bind: the risk level that makes the return attractive is the
one that can fail the challenge.

## Verdict

Arm A is a **real but modest edge** — genuinely positive after sequencing and
costs, with far better drawdown characteristics than holding the index, but not
the free lunch the daily-bar numbers suggested. It is worth more work only if
the goal is risk-adjusted return at low leverage, not headline return.

## Still untested

- Arm A on **ES at M5** (only NAS100 M5 is on disk; ES was tested at daily and
  spot-checked at M30, which is now known to flatter).
- Out-of-sample on NAS100 — the 3 years is a single sample.
- Weekend-gap exposure (outstanding since Vanessa raised it).
- Whether a **minimum stop width** helps, now that the failure mechanism is
  measured: killed trades median 0.223%, survivors 0.361%. This is the one
  change with a measured rationale behind it, and it is cheap to test on the
  M5 data already here.
