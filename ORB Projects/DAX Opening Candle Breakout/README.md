# DAX Opening Candle Breakout

An opening-range breakout on GER40 at the **Frankfurt cash open (09:00 CET)**, built as an
enhancement of `ORB Projects/ORB Volume Breakout Bot/ORB_Volume_Breakout_Bot_v2.cs`.

## Why this instrument and this session

The point of this bot is **decorrelation**, not extra return. The two bots currently live
(US500 15m ORB and the NAS100 volume breakout) both trade the New York open and correlate
at **+0.50**; their combined drawdown is 18.1R against the 18.6R they would produce if they
were literally the same bot. Adding a third New York index bot would add risk and no
diversification.

Measured daily-return correlation, GER40 Frankfurt open vs the US500 New York bot: **-0.04**.
Both bots lose together on 32% of days, exactly what independence predicts.

Sized at a fixed pass probability, uncorrelated bots roughly halve the time to pass a
challenge; correlated ones do not improve it at all.

## Instrument viability

Median 15-minute opening range against a round-trip spread:

| | Price | OR15 | Spread as % of OR15 |
|---|---|---|---|
| US30 | 42,259 | 122.7 | 1.6% |
| NAS100 | 20,406 | 73.4 | 2.0% |
| **GER40** | 20,849 | 56.8 | **2.6%** |
| UK100 | 8,398 | 21.7 | 6.9% |

GER40 is a fair fight. **UK100 is not** — same spread in points against a third of the
range — and is not part of this project.

## What has already been rejected

The 5-minute-candle + 12 EMA variant was tested and **failed**. With costs included in the
parameter selection, the in-sample pick returned +30.0R out-of-sample at t = 0.88, and the
best-of-25 permutation test gave p = 0.77. See `analysis/dax_final.py`.

The failure mode is the one to design against: the no-cost winner used a ~9-point stop, so
a 1.5-point spread was 17% of risk per trade. **Include costs from the start.**

## The plan

Base structure: `ORB_Volume_Breakout_Bot_v2.cs` (has the volume filter and the two-timezone
session handling; `ORB Bot/ORB_Bot.cs` has neither).

Enhancement: a time-of-day-normalised relative-volume filter — see
`analysis/RVOL_FILTER_SPEC.md`. The existing trailing-bars filter cannot work at an opening
range, because the preceding bars are pre-auction: on GER40 the median opening bar is 3.77x
the preceding 20 minutes, so a 1.2 threshold passes 100% of days.

Starting parameters (`analysis/TEST_PLAN.md`):

```
Range:      09:00-09:05 CET (also test 09:00-09:15)
Entry:      close 10-15 pts beyond the range, in the range's direction
Stop:       25 pts, or 10% of the 14-day ATR dynamically
Target:     3R
Filter:     relative opening volume, test 1.0-1.2
Costs:      1.5 pts round trip, from the start
Years:      tune 2022-2024, do not touch 2025-2026
```

## Data

`US30 London Range Breakout/data/GER40/` — M5 and D1 from cTrader, 2023-07-02 onward.
cTrader history does not reach 2022, so the 2022 portion of any in-sample run can only be
verified from cTrader's own backtest, not cross-checked locally.

Note that cTrader CFD "volume" is tick count, not contracts.

## Layout

```
analysis/   research, test plan, filter spec, rejected-strategy scripts
src/        bot source
config/     .cbotset files
```
