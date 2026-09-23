# Wall-reaction studies — 2026-09-23

Four scripts behind the P-E / H14 entries of the same date. Each re-derives its
numbers from the journal and from cTrader M5 bars; none writes to the journal.

| script | question | headline |
|---|---|---|
| `01_extremes_on_levels.py` | does the RTH high/low land on a pre-open OI level? | 2/14 at +/-8pts vs 1.1 expected — chance |
| `02_fade_first_tag.py` | fade the first post-open tag? | -932.7 over 12; worse than an off-grid control |
| `03_confirmed_pierce.py` | trade the confirmed break instead? | +569.7 over 12, but 09-21 alone is +94% of it |
| `04_penetration_by_regime.py` | does gamma regime change wall penetration? | 36.3% vs 39.5% of day range — no difference |

**Read the caveats in HYPOTHESES.md before quoting any of these.** All four run
on 12-14 trading days, and the positive-gamma days in this window are almost
exactly the days the index rallied, so regime and direction are confounded.

Levels come from each day's journal `prediction.levels` (`kind` in `gamma`,
`gamma-shelf`), taken from the last scan BEFORE 13:30Z, so nothing uses
information published after the open.
