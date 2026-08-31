# Test plan: ORB variants on GER40 / UK100

## Instrument viability

**Correction:** the first version of this table applied an assumed flat 1.5pt
spread to all four instruments. That was wrong — the US500 backtest logs show
a real variable spread with a median of 0.50 (25 distinct values, 0.10 to
1.03), because cTrader backtests use real historical spread rather than a
fixed parameter. The absolute percentages below have been replaced with the
metric that matters: spread as a share of the stop distance.

| | Median stop | Spread | % of risk |
|---|---|---|---|
| US500 (measured) | 22.5 pts | 0.50 | **2.2%** |
| GER40 (estimated) | ~40 pts | ~1.2 | ~3% |
| UK100 (estimated) | ~16 pts | ~1.0 | ~6% |

The US500 edge (+0.072R) survives 2.2% friction. GER40 and UK100 spreads are
still estimates and need confirming from a real backtest log before the FTSE
verdict is final.

Median high-low of the first 15 minutes after each instrument's own cash open:

| | Price | OR15 | OR15 as % of price |
|---|---|---|---|
| US30 | 42,259 | 122.7 | 0.29% |
| NAS100 | 20,406 | 73.4 | 0.36% |
| GER40 | 20,849 | 56.8 | 0.27% |
| UK100 | 8,398 | 21.7 | 0.26% |

All four move about the same in percentage terms. The structural concern with
FTSE is that European indices attract broadly similar spreads in *points*,
while FTSE's opening range is a third of DAX's — the same toll on a shorter
road. That reasoning is robust to the exact spread figures; the percentages
above are not, until measured.

**Next step:** run a short GER40 and UK100 backtest, read the `spreadPts=`
values from the logs, and redo this table with real numbers.

## Year split

**In-sample (tune freely): 2022, 2023, 2024**
**Out-of-sample (touch once, at the end): 2025, 2026**

Tune on the past, test forward. Tuning on 2025-26 and validating on 2022-24
cannot detect decay — a strategy that broke in 2024 still passes, because the
test period predates the break. The question being asked is whether the edge
works *now*.

Cost: ~1.7 years out-of-sample, roughly 250-400 trades for a daily ORB.
Enough to test.

## Rules

1. Do not look at 2025-26 until parameters are locked.
2. Write the pass criteria down first: positive out-of-sample, degradation
   under 50%, survives the multiple-testing correction.
3. Record how many variants were tried — that is the correction factor.
4. One shot. A failed out-of-sample test cannot be re-tuned and re-run;
   doing so turns the reserve years into in-sample data.

## Design notes

- Run the DAX ORB at the **Frankfurt open (09:00 CET)**, not the New York
  open. It is DAX's own auction, and the session is uncorrelated with the
  US500 New York open bot (measured r = -0.04).
- Set a realistic backtest spread from the start. Bolting costs on afterwards
  is what exposed the opening-candle strategy as unviable.

## Data coverage

Local GER40/UK100 M5 starts 2023-07-02, so the 2022 portion of any in-sample
run can only be verified from cTrader's own backtest, not cross-checked here.

## Entry cutoff — derived, not chosen (analysis/entry_window.py)

Measured on in-sample GER40 only (<= 2024-12-31): when the first close 10 points beyond
the 09:00-09:05 range actually occurs. Timing distribution, not returns — choosing a
cutoff from which hours were profitable would select on the thing under test.

| Last entry | Breakouts captured |
|---|---|
| 10:00 | 84.5% |
| 10:30 | 93.2% |
| **11:00** | **96.6%** |
| 11:30 | 96.6% |
| 12:00 | 96.9% |
| 14:00 | 99.0% |

A breakout occurs on 99.7% of days; the median arrives 25 minutes after the open and the
90th percentile by 10:15. **11:00 is the knee** — 11:30 adds nothing and 12:00 adds one day
in 381 for an extra hour of exposure. Default set to 11:00.

## Stop: ATR mode implemented

`StopDistanceMode.AtrMultiple` computes the stop as AtrStopPercent% of the AtrStopDays-day
ATR from completed daily bars, once per session, clamped to [AtrStopMinPoints,
AtrStopMaxPoints]. Defaults 10% / 14 days, which is ~25pt against GER40's 249-point median
ATR14 — deliberately the same starting distance as the FixedPoints default, so switching
modes isolates the effect of letting the stop float with volatility rather than confounding
it with a change of size.

Today's daily bar is excluded: at 09:05 it holds five minutes and would drag the average
down exactly when the stop is set.

Note the prior: a volatility-scaled stop (50% of ORB) was tested across five NAS100 years
and was materially worse (+$3,567 vs +$8,859, PF 1.19 vs 1.34), because with dollar-fixed
risk a wider stop buys a smaller position. FixedPoints vs AtrMultiple is a real comparison
to run, not a foregone conclusion — and it is two variants, not one.
