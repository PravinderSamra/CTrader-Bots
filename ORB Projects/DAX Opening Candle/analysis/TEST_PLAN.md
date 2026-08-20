# Test plan: ORB variants on GER40 / UK100

## Instrument viability (measured, not assumed)

Median high-low of the first 15 minutes after each instrument's own cash open,
against a round-trip spread:

| | Price | OR15 | OR15 as % of price | Spread as % of OR15 |
|---|---|---|---|---|
| US30 | 42,259 | 122.7 | 0.29% | 1.6% |
| NAS100 | 20,406 | 73.4 | 0.36% | 2.0% |
| GER40 | 20,849 | 56.8 | 0.27% | **2.6%** |
| UK100 | 8,398 | 21.7 | 0.26% | **6.9%** |

All four move about the same in percentage terms. FTSE's problem is its price
level: the same spread in points against a third of the range.

**GER40 is worth testing. UK100 starts with a 3.5x cost handicap** and would
need an edge roughly three times larger than NAS100's to net the same. Given
the US500 edge is only +0.072R, FTSE is a poor candidate.

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
