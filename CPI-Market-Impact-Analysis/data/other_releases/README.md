# Release Magnitude Comparison — PPI, Retail Sales, Jobless Claims, ADP

Companion study to the CPI analysis: which of the other major US scheduled
releases moves **NAS100** / **US500** the most, and by how many points in the
first 10 minutes. Last 6 completed instances of each (before 2026-07-14),
same instruments as the CPI study.

## Method

For each event: `P0` = price at release, `P10` = price 10 minutes later,
`spike_range` = high−low across the whole 10-minute window (captures the
whipsaw/spike size, not just net drift), `net_move` = `P10 − P0`. All times
converted from US Eastern release time (8:30 or 8:15am ET) to UTC using the
same DST-aware logic as the CPI study — see `analyze_spike_magnitude.py`.

This is a **magnitude study, not a directional hit-rate study** — unlike the
CPI dataset, this one doesn't classify expected-vs-actual surprise, since the
ask was "which moves more," not "which direction."

## Results (avg 10-min spike range, points)

| Release | NAS100 | US500 |
|---|---|---|
| **PPI** | **91.3** | **16.7** |
| Jobless Claims | 89.3 | 13.2 |
| Retail Sales | 61.9 | 12.9 |
| ADP Employment | 42.5 | 8.2 |

For reference, the CPI study (`../data/price_reaction.csv`) showed NAS100
30-minute net moves averaging ~57-89 pts on clean directional reactions —
so PPI and Jobless Claims spikes are in the same ballpark as CPI's, just
measured over a tighter 10-minute window.

## Known data overlaps (same underlying release window, can't be disentangled)

- **PPI 2026-06-11 == Jobless Claims 2026-06-11** (PPI landed on a Thursday, same day as that week's claims data)
- **Retail Sales 2026-04-01 == ADP Employment 2026-04-01** (Retail Sales Feb-2026 data release coincided with that week's ADP print — see the Feb-2026 Retail Sales shutdown-delay note below)

Both are flagged inline in `analyze_spike_magnitude.py`'s output. These
overlaps mean the "PPI vs Jobless Claims" and "Retail Sales vs ADP"
comparisons share one data point each — worth keeping in mind since it's
1 of 6 instances (~17% of the sample) for the affected pairs.

## Known data quality caveat: 2025 shutdown disruption

Several PPI and Retail Sales releases in the "last 6" window were delayed by
the Oct-Nov 2025 government shutdown's knock-on backlog (same disruption
documented in the main CPI dataset):

- **PPI**: Dec-2025 and Jan-2026 reference-month releases were pushed back
  ~2 weeks from their normal schedule.
- **Retail Sales**: Dec-2025 through Mar-2026 reference-month releases were
  all delayed; the series didn't return to its normal one-month lag until
  the May-2026 data release (2026-06-17).

This doesn't affect the price-reaction magnitude measurement itself (the
market still reacted normally to whatever hit the tape that day), but it
means the release *dates* don't follow the usual mid-month cadence for that
stretch — noted here in case reference-month-to-release-date mapping matters
for future extensions of this dataset.

## Files

- `raw_candles/{ReleaseType}_{date}_{instrument}.json` — raw 1-min OHLC,
  ~12-minute window per event (release −1min to +11min).
- `analyze_spike_magnitude.py` — regenerates the comparison from raw candles.
