# Pre-release straddle simulation — buy stop / sell stop OCO

Simulates: 2 minutes before each CPI release, place a Buy Stop and Sell Stop
`trigger_dist` points either side of spot. First one hit cancels the other
(OCO). Fixed SL `sl_dist` points against entry, TP at `RR x sl_dist` (3RR by
default). No trailing — a static bracket. Runs on the same 23 saved CPI-release
NAS100/US500 candle files as the main study (Jun 2024 – May 2026, headline
CPI, 2025-10 excluded — no release occurred).

See `data/simulate_straddle.py` (single setup) and
`data/sweep_straddle_params.py` (parameter grid).

## Your exact setup: 20pt trigger, 15pt SL, 3RR (45pt) TP

| | NAS100 | US500 |
|---|---|---|
| Resolved trades | 23/23 | 10/23 (6 no-trigger, 7 still open at +45min) |
| Win rate | 78.3% (18W / 5L) | 20.0% (2W / 8L) |
| Total R | +49.0R | ‑2.0R |
| Expectancy/trade | **+2.13R** | ‑0.20R |
| Total points | +735 | ‑30 |

**Critical caveat — read before trusting the NAS100 number**: 20 of the 23
NAS100 triggers were the **Buy Stop** side (87%), only 3 were Sell Stop. This
straddle isn't capturing a balanced "whichever way CPI surprises" edge — it's
overwhelmingly a long-breakout system, and it looks spectacular here because
**NAS100 rose ~41% across this exact 2-year sample** (20,663 → 29,142). A
system that goes long on any 20pt upside poke, in a market that mostly went
up, will look great almost regardless of CPI. This result is not clean
evidence of a repeatable CPI-specific edge — it's entangled with the trend
regime of this specific backtest window. Treat the 78%/+2.13R figure as an
upper bound that assumes the trend continues, not a stable expectancy.

US500's poor showing is explained by its point scale: on the primary CPI
study, US500's clean directional moves average only ~15-17 pts (vs NAS100's
~57-89 pts) — a 20pt trigger is often too wide for it to even fire (6
no-triggers), and a 45pt target is often too far to reach in 45 minutes even
when it does (7 still-open).

## Parameter sweep — "ideal" trigger distance and SL, TP fixed at 3RR

Grids below: expectancy in R (top), win rate % (middle), resolved-trade count
out of 23 (bottom), across trigger distance (10-40pts) x SL distance
(10-30pts).

### NAS100

```
expectancy (R)
SL\Trig   10      15      20      25      30      35      40
10      +1.61   +1.78   +2.13   +2.13   +1.78   +1.96   +1.78
15      +1.78   +1.78   +2.13   +2.27   +1.91   +1.78   +1.78
20      +1.73   +1.91   +2.00   +2.24   +2.09   +1.91   +1.78
25      +1.67   +1.86   +2.20   +2.40   +2.00   +1.80   +1.60
30      +2.00   +1.74   +2.11   +2.06   +2.00   +1.50   +1.35

win rate %
SL\Trig   10    15    20    25    30    35    40
10        65%   70%   78%   78%   70%   74%   70%
15        70%   70%   78%   82%   73%   70%   70%
20        68%   73%   75%   81%   77%   73%   70%
25        67%   71%   80%   85%   75%   70%   65%
30        75%   68%   78%   76%   75%   62%   59%
```

Best cell (requiring ≥15 resolved trades for reliability): **trigger=25pts,
SL=25pts, TP=75pts → +2.40R/trade, 85% win rate, n=20**. But every cell in
this grid inherits the same long-side trend bias described above — tuning
the parameters doesn't remove it, since it's the same underlying price series
driving every combination. The grid is more useful for its *shape* than its
single best cell: expectancy is fairly stable (+1.6R to +2.4R) across a wide
range of trigger/SL combos, which suggests the choice of exact distance
matters less than being long-biased in this sample. **Wider SL (20-25pts)
paired with a mid-size trigger (20-25pts) is the most consistently strong
region** — very tight stops (10pts) get shaken out more (lower win rate at
similar trigger distances).

### US500

```
expectancy (R)
SL\Trig   10      15      20      25      30      35      40
10      +0.20   -0.43   -0.33   -0.33   -0.11   +0.14   +1.00
15      +0.14   +0.14   -0.20   -0.20   -0.43   -1.00   -1.00
20      +0.60   +0.00   -1.00   -1.00   -1.00   -1.00   -1.00
25      -1.00   -1.00   -1.00   -1.00   -1.00   -1.00   -1.00
30      -1.00   -1.00   -1.00   -1.00   -1.00   -1.00   -1.00
```

No US500 combination reaches even 15 resolved trades out of 23 — sample sizes
are too thin (4-14 trades depending on parameters) to trust any single cell.
Qualitatively: tight triggers (10-15pts) with tight SL (10-15pts) are the
only region that's ever positive, and even then barely (+0.14R to +0.20R).
US500 does not support this strategy at any tested parameter combination as
well as NAS100 does — consistent with its smaller absolute point moves.

## Methodology notes / assumptions

- **Entry price** = open of the candle timestamped exactly 2 minutes before
  release.
- **Same-candle ambiguity, order trigger**: if a single 1-min candle's range
  touches both the Buy Stop and Sell Stop levels, the level closer to that
  candle's open is assumed to trigger first.
- **Same-candle ambiguity, SL/TP**: if a single candle's range touches both
  the stop-loss and take-profit of an open trade, **stop-loss is assumed to
  hit first** (conservative bias — standard backtesting convention to avoid
  overstating performance).
- **No trailing** — this is a static bracket (fixed SL, fixed TP), matching
  "take profit at 3RR" as stated, not the confirmation+trail strategy from
  the earlier NAS100-vs-gold analysis.
- **Unresolved trades** (neither SL nor TP hit by release+45min) are excluded
  from win-rate/expectancy and reported separately as still-open with a
  mark-to-market R at the last available price.
- Small sample (23 events, fewer when many no-triggers/opens) — treat
  precise numbers as indicative, not statistically robust.
