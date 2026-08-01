# Retrospective — what the skill actually does, and what's wrong with it

Written 2026-08-01 after building the whole stack. Every claim below is measured
against XAUUSD 4,049.44 over the 14 days to 2026-08-01 unless stated otherwise.

> **Status: §2.1, §2.2, §2.3 and §2.4 have since been fixed** — see §6. The
> findings are left in place because they are the evidence for the fixes, and
> because the measurements are the useful part.

---

## 1. What works

### The basis handling — the best thing here

GC futures trade at a premium to spot that decays into expiry and **steps at the
roll**. Measured: +12.74 (3 Jul) → +0.07 (28 Jul) → **+58.27 (29 Jul)**.

The module measures this live from overlapping hourly bars, detects the roll, and
converts **each futures bar at that day's basis** before building the profile.
With a single current offset the POC came out at 4,014.77; done properly, 4,047.37
— 33 points, and right where price actually was.

This is non-obvious, it is the kind of thing that silently poisons a whole
analysis, and it is correct.

### Measuring constants instead of assuming them

The GLD ratio is 10.9008, not the conventional 10. That difference is 335 points
at current gold prices. It also surfaced the same bug sitting in
`GEX&OI/agent_skill/data_fetchers/yfinance_options.py`, which still hardcodes 10.

Related: quantifying the *precision* of each mapping rather than just its value.
Futures→spot has stdev 1.23 pts; GLD strike→spot has stdev ±7.6 pts against a
strike spacing of 10.9. So individual strikes cannot be pinned to individual spot
prices, and the tool now says so instead of implying false precision.

### The `--as-of` discipline

Truncating every series to a past instant is what made "what could you have told
me at 15:30" answerable rather than a retrofit. It also surfaced that the options
layer **cannot** be reconstructed at all, which is the entire justification for
the journal.

### Path-dependent replay

Stop checked before target, stop assumed hit first within a bar. The first
version measured best- and worst-case excursion independently and reported
setups at "48R". Everything downstream of that would have been fiction.

### Honest gaps

Unavailable layers report as UNAVAILABLE and cap the score, rather than silently
scoring zero and looking like a considered judgement.

---

## 2. What doesn't work

### 2.1 Pseudo-replication — the worst flaw

The score treats every touch event as an independent observation. They are not.

| At level 4,049.44 | Count |
|---|---|
| "Touch events" the score counts | **60** |
| Genuine visits (events <60 min apart merged) | **16** |
| Distinct days with any touch | **7** |
| Days in the scored bucket | **4** |

One visit contained 17 events. The sample-weight table gives `n≥15 → 1.00`, so a
bucket of 23 events gets **full statistical confidence** when the independent
sample is four days.

Outcomes cluster hard within a day — 31 July was 6 losses in 7; 23 July was 7
wins in 9. Day-level regime dominates, so events within a day are close to one
observation repeated.

**Mitigating detail:** the *point estimate* is robust. Expectancy is +1.06R at
n=23 events, +1.12R at n=11 visits, +1.00R at n=4 days. So the number isn't
inflated — the **confidence in it is**. That is still serious: it is the
difference between "TAKE" and "interesting, tiny size".

### 2.2 The entry model isn't the one you trade

The replay enters **at the level**, blind, with a stop derived from p90
wick-through. Your described method is different: wait for the wick and the
rejection, *then* enter with the stop beyond the deepest printed wick.

I built that second model and ran it:

| Model | n | Win | Median risk | Spread as % of risk | Expectancy |
|---|---|---|---|---|---|
| A — enter at level, 2.77pt stop *(what the tool models)* | 23 | 57% | 2.77 | 13% | **+1.06R** |
| B — enter on rejection, stop just beyond that wick *(what you described)* | 30 | 17% | 1.61 | 22% | **−0.33R** |

So the tool's positive expectancy comes from an entry model you may not be using.

### 2.3 "Stop just beyond the deepest wick" is too tight for gold

Same rejection-entry model, varying only the minimum stop:

| Stop floor | Win rate | Median risk | Spread % | Expectancy |
|---|---|---|---|---|
| none (just beyond the wick) | 17% | 1.61 | 22% | −0.33R |
| 2.5 pts | 40% | 2.50 | 14% | +0.38R |
| 5.0 pts | 63% | 5.00 | 7% | **+0.52R** |
| 7.0 pts | 83% | 7.00 | 5% | **+0.62R** |
| 10.0 pts | 93% | 10.00 | 3% | +0.55R |

The entry timing was never the problem — **the stop was**. A 1-minute wick on
gold gives you ~1.6 points of room, and normal noise takes it out. The data says
5–7 points. This is the most directly actionable finding in the whole project and
it contradicts the stated rule of the strategy.

### 2.4 The volume profile is built at the wrong granularity

I used **hourly** GC bars, spreading each bar's volume evenly across its
high–low range. For a 1–2 minute strategy that is mush: an hour of gold can span
20+ points, and the profile smears volume across all of it.

Yahoo serves finer data free, and I simply didn't check:

| Range / interval | Bars | Volume-bearing | Total contracts |
|---|---|---|---|
| 1mo / 1h *(what I used)* | 624 | 486 | 2,757,533 |
| 60d / 5m | 17,280 | **13,737** | 6,617,683 |
| 5d / 1m | 7,195 | 6,480 | 704,164 |

**60d at 5-minute resolution is a 12× improvement in node placement for free.**

### 2.5 No execution costs anywhere

Spread is never modelled. At the tool's own 2.77-point stop, the ~0.35 gold
spread is **13% of risk**; on wick-tight stops it's 22%. Slippage on a market
entry after a rejection is also ignored, and "entry at the level" quietly assumes
a resting limit fill.

### 2.6 No event filter

Gold is dominated by CPI, NFP, FOMC and the LBMA fixes. A level test three
minutes before CPI is not the same trade as one at 11:00 on a quiet Tuesday, and
nothing in the stack knows the difference. This is the largest blind spot.

### 2.7 Gamma is used as one global number

Net GEX is computed per strike but only the market-wide total drives the regime
flag. What should matter for *your* level is the gamma density near it. The data
is already there; the scoring doesn't use it.

### 2.8 Smaller things

- **Sessions are fixed UTC hours** — no DST handling, and no awareness of the
  10:30/15:00 London LBMA fixes, which are real intraday events for gold.
- **Day bias is measured at the moment of the touch** and can flip intraday, so
  a level can be scored under one regime and traded under another.
- **The 60-minute horizon and 3R cap are arbitrary** and interact mechanically
  with stop width — a wider stop pushes the 3R target further away, which is why
  expectancy falls with stop size in the sensitivity table. That is an artefact
  of the measurement, not a property of the market.
- **Levels are treated as prices, not zones.** You draw zones.
- **Score weights are unvalidated.** The confluence modifiers total +40, enough
  to carry a level from WEAK to TAKE on components that have never been tested.

---

## 3. Missing data that would actually give an edge

Ranked by value per unit of effort.

1. **Economic calendar.** Biggest blind spot, and cheap. FRED needs a free API
   key; several calendar sources are scrapeable. Even a static list of CPI/NFP/
   FOMC dates and times would let the tool refuse to score a level inside a
   news window.
2. **Finer futures volume — already free, just unused.** 60d/5m as above.
3. **CME OG options** (options on GC futures). Removes the GLD proxy *and* its
   ±7.6-point mapping error, since OG strikes sit on the futures price and map by
   the stable basis. CME 403s from this environment but should work from your
   machine.
4. **DXY and real yields.** Gold's two main macro drivers, free from Yahoo/FRED,
   entirely absent. A level fading into a dollar breakout is a different
   proposition.
5. **The DOM probe has still never been run.** `dom_recorder.py --probe` takes
   60 seconds and settles whether Pepperstone gives usable depth on XAUUSD. It
   is the only unresolved *known unknown* in the stack.
6. **Daily OI change**, rather than a static snapshot. Rising OI into a level
   means new positioning; falling OI means unwinding. Different trades.

---

## 4. What I'd do differently starting over

**1. Build the journal first, and only trade forward from it.**
The whole historical-statistics layer is a retrofit onto levels you drew knowing
what price had already done. There is unavoidable selection bias in that. Logged
forward calls have none. I built the sophisticated part first and the clean part
last; that was backwards.

**2. Count independent observations from day one.**
Events per *day* or per *visit*, never per bar-cluster. This one decision would
have prevented the worst flaw in the current scoring, and it is a small change.

**3. Model the entry you actually use, and treat the stop rule as a parameter.**
Not as an assertion inherited from the strategy description. The stop-floor table
above is the single most useful output of this entire project, and it only exists
because I questioned the rule rather than implementing it.

**4. Ship the evidence table; add the score later.**
The itemised breakdown is genuinely useful. The 0–100 total is a compression of
it using weights nothing has validated, and a single number invites more trust
than it has earned. I would show the components and withhold the total until the
journal could calibrate it.

**5. Start at 5-minute resolution everywhere.**
Hourly was a default I never revisited.

**6. Treat levels as zones.**
A width parameter per level, with the touch band derived from *that* rather than
a fixed fraction of price.

---

## 5. Honest summary

The **infrastructure** is sound: the basis handling, the measured constants, the
as-of discipline, the path-dependent replay and the journal schema are all things
I would keep unchanged.

The **statistics** overstate confidence (pseudo-replication) and model an entry
that may not be yours.

The **score** is a plausible-looking number resting on unvalidated weights, and
should be treated as a structured summary of evidence rather than a probability.

The most valuable thing the project produced is not the score. It is two
measured facts: that the futures basis will silently misplace every level by ~58
points across a roll, and that a stop "just beyond the wick" on gold is roughly
three times too tight.


---

## 6. Implemented (2026-08-01)

### Independent-sample counting — fixes §2.1

`independent_counts()` reports events, visits (merged under 60 min) and distinct
days. Sample weight now keys on **days**:

```
12+ days → 1.00 | 8–11 → 0.80 | 5–7 → 0.60 | 3–4 → 0.40 | <3 → 0.20
```

At 4,049.44 that moved the base from +30.8 (weight 1.00 on 23 events) to +9.6
(weight 0.40 on 4 days), and the overall score from 79/TAKE to 48/WEAK. The
report prints all three counts so the dilution is visible rather than implied.

### Rejection entry model — fixes §2.2 and §2.3

`replay_rejection()` waits for a bar to wick through the level and close back
inside, enters at that close, charges the spread, and stops beyond the printed
wick subject to a floor (default 0.125% of spot, ~5 pts on gold). It is now the
**default**; `--entry level` keeps the old limit-at-the-level model for
comparison.

Visits that never produced a rejection are marked `triggered=False` and excluded
from win rate and expectancy — averaging a no-signal visit in as a zero would
dilute the edge toward nothing. Hold rate still counts every visit, because that
is a property of the level rather than of the trade.

Same level, same 14 days, identical data:

| Model | Win | Expectancy | Spread as % of risk | Score |
|---|---|---|---|---|
| Rejection, 5.06pt floor *(default)* | 67% | +0.60R | 7% | 48 |
| Rejection, 7pt floor | 73% | +0.45R | 5% | 47 |
| Limit at level, 2.77pt stop | 57% | +1.06R | 13% | 60 |

### 5-minute volume profile — fixes §2.4

The profile now builds from 5-minute GC bars: **6,887 volume-bearing bars against
486 hourly**, a 14× resolution gain.

Two things had to be fixed to make it safe rather than merely finer:

- **The basis window must cover the profile window.** It is now derived from
  `--vp-range` rather than `--days`. Without this, bars outside the measured
  basis silently borrowed a stale offset.
- **`futures_to_spot` now refuses to borrow a basis across a roll**, and drops
  bars more than 4 days from any measured basis rather than placing their volume
  at a price they never traded at. It reports how many it dropped.

The lookback stayed at 30 days deliberately. 60 days spans a 235-point range on
gold and moved the POC by 25 points between runs — the gain here is *resolution*,
not history.

### Still open

§2.5 (spread is now charged on entry, but slippage is not modelled), §2.6 (no
event/news filter), §2.7 (gamma still used as a market-wide total), §2.8, and
everything in §3 except the volume granularity.
