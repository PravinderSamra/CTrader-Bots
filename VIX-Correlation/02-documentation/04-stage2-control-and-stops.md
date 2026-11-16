# Stage 2b — control arm corrected, and the minimum-stop idea fails its test

Run 2026-11-16, continuing from `03-stage2-sequencing.md`.

## 1. Sequence-checking the control arm

**Key efficiency:** sequencing can only turn a winner into a loser, never the
reverse. So only the control arm's **18 winners** needed checking, not all 55.

The failure mechanism found in stage 2a was tight stops, so the 5 tightest
control winners were checked intraday (M30), plus the knowledge from stage 2a
that every wide-stop case survived comfortably.

| Date | entry | stop | risk% | min low after entry | verdict |
|---|---|---|---|---|---|
| 2025-09-04 | 6455.42 | 6444.20 | 0.174% | 6456.70 | survives (12.5 pts) |
| 2025-08-21 | 6363.30 | 6348.70 | 0.229% | 6359.80 | survives (11.1 pts) |
| 2025-10-30 | 6832.95 | 6816.20 | 0.245% | 6817.70 | survives (1.5 pts) |
| 2025-07-21 | 6305.11 | 6286.00 | 0.303% | 6294.80 | survives (8.8 pts) |
| 2025-09-30 | 6653.20 | 6631.40 | 0.328% | 6649.00 | survives (17.6 pts) |

**All five survive.** The remaining 13 control winners all have stops of 0.53%
or wider; stage 2a found every wide-stop case surviving with large margins, so
they are taken as surviving. That is an extrapolation, not a check.

## 2. The corrected comparison — and it is no longer significant

| | VIX weak | VIX confirmed |
|---|---|---|
| n | 13 | 55 |
| win rate (3R) | **8/13 = 61.5%** | 18/55 = 32.7% |
| avg R | **+1.53** | +0.20 |
| total R | +19.8 | +11.1 |

| | Fisher one-sided p |
|---|---|
| stage 1 (daily, 9/13) | 0.018 |
| **stage 2 (corrected, 8/13)** | **0.056** |
| Bonferroni threshold (3 targets tested) | 0.017 |

**Losing that single trade pushes the result from "marginally significant" to
"not significant".** At 8/13 vs 18/55 the win-rate difference no longer clears
p<0.05, let alone the corrected 0.017.

The avg-R gap stays large — +1.53 against +0.20, roughly sevenfold — but with
n=13 the confidence interval around that is wide enough to drive through.

**Honest verdict: the direction has survived every check so far, and the
magnitude has not been established. This is a promising lead with an
insufficient sample, not a validated edge.**

## 3. The minimum-stop idea cannot be tested this way (negative result)

The stage 2a finding suggested a minimum stop distance would convert fragile
tight-stop setups into robust ones. Tested two ways on daily bars:

**Widening the stop to a floor** (keeps every trade): essentially no effect up
to 0.40%, and at 0.50% it *hurts* the weak arm (69.2% → 61.5%, +1.83 → +1.42)
because the wider stop shrinks every R multiple.

**Skipping trades with a natural stop below the floor:** arm B goes 13 → 9 → 5
→ 3 events as the floor rises 0.20% → 0.30% → 0.40%, with win rate climbing
69% → 67% → 80% → 100%. **That is sample shrinkage, not edge.** n=3 at 100%
means nothing, and the control arm barely moves (32.7% → 32.6% → 36.1%),
which is what you see when a filter is thinning rather than selecting.

**Why neither test is informative:** the harm a tight stop causes is an
*intraday* retest. Daily bars cannot see it. So the daily test cannot measure
the thing the fix is meant to fix. Recorded so this is not re-attempted the
same way.

Testing it properly means re-running the full intraday simulation at each
candidate floor — which needs intraday data for all 68 events, not the 18
fetched so far.

## 4. Where this leaves the strategy

Survived: the null comparison, the regime check, the NQ-leg test (dead), the
sequencing bias, and the control-arm correction.

Not established: the size of the edge, and therefore whether it is worth
trading. The blocker is now **sample size, not method**. 13 events over 13
months is simply too few.

**The cheapest way forward is more history, not more cleverness.** Extending
the window from 13 months to 4–5 years would take the weak arm from ~13 events
to perhaps 50, which is enough to settle it. That is ~75 daily-bar calls plus
intraday for the winners.

## 5. Not yet done

- Weekend-gap exposure (Vanessa, 2026-11-16): how many of these trades were
  open over a weekend and what the gap did. A sizing question, not a yes/no.
- Minimum stop distance, tested properly on intraday data.
- M5 resolution for the sessions where M15/M30 left within-bar order ambiguous.
