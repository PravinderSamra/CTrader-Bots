# Wall-reaction studies — 2026-09-23, extended 2026-10-02 and 2026-10-04

Scripts 01-04 sit behind the P-E / H14 entries of 2026-09-23; 05-08 behind H24
of 2026-10-02; 09-10 behind H25 of 2026-10-04. Each re-derives its numbers from the journal and from cTrader M5
bars; none writes to the journal.

| script | question | headline |
|---|---|---|
| `01_extremes_on_levels.py` | does the RTH high/low land on a pre-open OI level? | 2/14 at +/-8pts vs 1.1 expected — chance |
| `02_fade_first_tag.py` | fade the first post-open tag? | -932.7 over 12; worse than an off-grid control |
| `03_confirmed_pierce.py` | trade the confirmed break instead? | +569.7 over 12, but 09-21 alone is +94% of it |
| `04_penetration_by_regime.py` | does gamma regime change wall penetration? | 36.3% vs 39.5% of day range — no difference |
| `05_sweep_reversal.py` | sweep → failed re-break → reversal, graded on CLOSES | 822 setups, 50% reach 1R, 63pt median move — the baseline everything below is measured against |
| `06_near_miss.py` | price turns SHORT of a level, never touching it | rejected: half the move, 77-86% stopped |
| `07_confluence.py` | do two different KINDS of level stacked reverse better? | not established; gamma+structure's 75% rests on 6 distinct pairs |
| `08_repeat_sweep.py` | is the 2nd sweep of a level better than the 1st? | no signal, flat through three attempts |
| `09_target_by_stop_size.py` | what target is reachable, given how wide the stop is? | the run is 48-79pts in EVERY stop bucket — target in R is roughly 55/stop |
| `10_exit_rules.py` | hard target, breakeven, or trail — which suits which stop? | tight: hard 3R. mid: trail. 76-100pts: 1R with BE@0.5R. >100pts: nothing pays |

**Read the caveats in HYPOTHESES.md before quoting any of these.**

01-04 run on 12-14 trading days, and the positive-gamma days in that window are
almost exactly the days the index rallied, so regime and direction are
confounded. Their levels come from each day's journal `prediction.levels`
(`kind` in `gamma`, `gamma-shelf`), taken from the last scan BEFORE 13:30Z, so
nothing uses information published after the open.

05-10 run on 19 trading days and take EVERY published level, not only the gamma
ones, excluding names containing `STRUCTURAL`. That is one month of a rising
tape, which flatters any setup that is long-biased — equal lows especially.

## Running 05-08

`05_sweep_reversal.py` must run first — it writes `/tmp/sw_plain.json` and
`/tmp/sw_conf.json`, which 06, 07 and 08 read. All four expect `/tmp/m5_all.json`
(cTrader M5 bars, `{t,o,h,l,c}` per bar) and the repo root as the working
directory, since they glob the journal by relative path.

`09` reads `/tmp/sw_conf.json` as well; `10` ignores it and re-derives the
setups from bars itself, because stop MOVEMENT needs the order events happened
in and `sw_conf.json` keeps only the furthest point reached. The two therefore
use different fill models on purpose — 09 measures targets on closes, 10 fills
resting orders on the wick and checks the stop first within a bar — so **their
numbers are not meant to agree.** 09 bounds what price did; 10 bounds what an
order would have got.

`07_confluence.py` prints its own tolerance sweep and same-day controls. **Read
both before quoting any bucket.** A confluence bucket's row count is not its
sample size: one level swept six times in a day is six rows and one observation,
so the script reports distinct day/level pairs beside every row count, and a
bucket can only be judged against the other levels on the days it appears on.
