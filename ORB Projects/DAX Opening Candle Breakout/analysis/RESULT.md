# Result: rejected

Tested on GER40, 2022-2024 in-sample. **2025-2026 were never run** — the reserve is intact.

## The three runs

| Setting | Trades | Gross R/trade | Cost R/trade | **Net R/trade** | t (net) | 90% CI | Max DD |
|---|---|---|---|---|---|---|---|
| RVOL 1.10 | 296 | +0.017 | 0.056 | **-0.039** | -0.38 | -0.208 .. +0.131 | 37.9R |
| RVOL 1.05 | 347 | +0.093 | 0.056 | **+0.037** | +0.38 | -0.121 .. +0.197 | 32.7R |
| Filter OFF | 731 | +0.036 | 0.056 | **-0.020** | -0.30 | -0.128 .. +0.088 | 73.6R |

Every confidence interval spans zero. The pre-registered bar was t > 2.

## Why this is noise, not a near-miss

**The best setting is an interior point.** 1.05 beats both 1.10 (stricter) and OFF (looser).
There is no mechanism under which a filter helps at 1.05, hurts at 1.10, and hurts again
when removed. A real effect produces an ordering; this produces a bump.

**The mechanism we proposed was falsified.** Comparing 1.10 against 1.05 showed that 88% of
1.05's advantage (+24.0R of +27.2R) came from 49 shared dates where the looser threshold
entered *earlier in the morning* and won more often (45% vs 33%) — not from the extra 51
days it traded. That suggested the filter was delaying entry rather than selecting quality,
which predicts that removing the filter entirely should be best of all.

It was not. Filter OFF came in below 1.05. The prediction failed, and the paired permutation
test on those 49 dates had already given p = 0.064 — each flipped date is close to a coin
toss between -1R and +3R, and 49 tosses is not many.

## The structural problem

Spread costs **0.056R per trade**, measured from the logs by solving the systematic gap
between the implied point value on winners (1.0213) and losers (1.0966): about $5.19 per
trade, roughly 1.5 GER40 points on a median 4.28-lot position.

No configuration produced a gross edge reliably above that. The best gross figure found was
+0.093R at t = 0.95 — itself not distinguishable from zero.

This is the same wall the 5-minute opening-candle test hit, and the failure mode Mesfin
(2026) documents across fourteen signal families on MNQ: the signal measures something, but
what it measures is smaller than the cost of acting on it.

**A design error contributed.** The instrument viability check compared the spread against
the 15-minute opening range (~57 points) and got 2.6% — a fair fight. But the ATR stop sizes
risk at ~21 points, so the real figure is ~7% of risk per trade. The instrument was assessed
correctly and then a stop was chosen that made the cost far worse.

## Year by year (gross R, before costs)

| Setting | 2022 | 2023 | 2024 |
|---|---|---|---|
| 1.10 | +1.4 | -20.6 | +24.1 |
| 1.05 | +10.5 | -18.4 | +39.9 |
| Filter OFF | +44.0 | -62.4 | +44.7 |

2023 is heavily negative under every setting. That is not an edge having a bad year.

## What was verified, and is worth keeping

The build itself was correct throughout, which is why the negative result can be trusted:

- Average loss **-1.02R**, stop overshoot 0.64 points (3% of risk) — clean execution.
- Average win **+3.03R** against a 3R target.
- RVOL median 1.01 inside the entry window, 14 baseline days on every evaluation.
- ATR window never included the current session across 757 verified sessions.
- Session times correct across both DST conventions.

The RVOL filter implementation, the ATR stop, and the data-derived entry cutoff are all
reusable. The strategy is what failed, not the machinery.

## Status

**Stopped, per the rule agreed before testing.** Five variants were tried across this and
the opening-candle work; none cleared the bar. 2025-2026 remain unused and can still serve
as a clean test for a future GER40 idea.
