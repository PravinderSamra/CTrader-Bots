# The gexbot channel, read end to end

Analysis of every English transcript on the vendor's own YouTube channel
(37 videos found, 12 with English captions, ~87k words). Raw transcripts and
a manifest of what did and did not have captions are in
[`../transcripts/gexbot-channel/`](../transcripts/gexbot-channel/).

The 24 without captions are genuinely uncaptioned — mostly silent screen
recordings of trades and Spanish-language livestreams — not a fetch failure;
this was verified per video rather than assumed.

**Why this corpus outranks everything else we have.** The two videos this
project was built on are a trader describing how he uses the product. This is
the people who built it, plus one of them trading NQ — our instrument — and
being interviewed by that same trader. Where they disagree, the founders win.

The single most valuable item is the two-part **"Gexbot for Futures Execution
on NQ: Fredy S interviews Jass"** (2024-12-04). It is our exact use case:
GexBot's co-founder trades NQ off these levels, and spends 90 minutes saying
how.

---

## 1. How the founders use the majors — and a retraction

> **Retracted 2026-09-07.** This section originally claimed the majors are
> "exits, not entries", that our specification had it wrong, and that the
> touch test was "measuring a claim the vendor never made". **All three were
> overstatements.** They came from reading one founder's stated preference as
> doctrine, and from quoting Siento describing a single trade rather than his
> actual rule. The corrected version follows.

Siento's rule, from the source video, is unambiguous and it does treat the
majors as entries — he calls it one of his main setups. Don't sell in the
middle; wait for price to reach the level. Buy at major negative with the stop
below. *"This is how you use these two, major positive gamma and major
negative gamma, to enter a trade."*

He also, **in the same breath**, describes them as profit-taking places: go
short at major positive, "or if you've been long, this is the place you take
profit." Both uses were in our source material all along. There was no
conflict to correct, and the earlier claim that we had encoded the wrong one
was simply wrong.

**Where there is a real difference is between the two founders**, and neither
forbids entering at a major:

- **Jass** prefers trimming into them:

  > "major positive or major negative — they're really best for taking your
  > core off when you're heading towards the level … that just seems to be a
  > lot more effective than trying to actively fade against the level."

  Context matters: he says this about a specific ranging day where he judged
  *neither* the breakout nor the fade to have a clean entry, and he points to
  a smaller node where "someone is actively short" as the better entry. It is
  a claim about relative effectiveness, not a prohibition.

- **John** actively fades them:

  > "5835 has been a really big level all day, it's our major negative … every
  > time we come up into 35 it's worth a fade … that's more or less what I've
  > been doing all day."

  Note he is fading major *negative* approached from *below* — as resistance.
  That supports the pivot framing in §3 rather than contradicting the rule.

So the honest summary: **entering at the majors is a real, practitioner-backed
setup, and the touch test is a legitimate test of it.** What §2 adds is a
second entry method (transitions), not a replacement.

## 2. What they actually enter on: distributions and transitions

From *Gex Profile vs. Volume Profile*, the reading method is structural, not a
size ranking:

1. **Segment the ladder into distributions** — runs of consecutive call-gamma
   bars and runs of put-gamma bars.
2. **The sign flip between them is the level.** He calls it "my line in the
   sand": hold it and look for continuation; lose it and the thesis is dead.
3. **Majors are the targets** at the far end of a distribution — trim,
   flatten, or leave a runner.
4. **Convexity peaks inside a distribution** are intermediate trim points.
5. A bar sticking out against its neighbours' sign is itself a pivot.

The explicit analogy is volume profile, with one difference he stresses:

> "gex is the same thing. Literally the only difference is that these are
> **live positions and they're not historical**."

**This is not what our dashboard shows.** We rank the biggest strikes C1–C3 /
P1–P3 by size. The read that the founders actually use is about *where the
sign changes* and *how the bars group*, which is a different computation over
the same 142-strike ladder we already store. That is a concrete, buildable
improvement and it needs no new data.

## 3. Direction is not a property of the level

> "I try not to think about direction very much … you're looking at the most
> extreme ends or pivots — entries where you can define where your trade is
> wrong. Yes, if we're underneath it it's resistance, if we're above it it's
> support, but it's just an entry for looking for **spot price to go away from
> this level**."

They once considered rotating the chart sideways so users would stop reading
it directionally.

Our touch test hard-coded the opposite: a call wall was "respected" only if
price fell, whatever side price approached from. On a touch from the far side
that scores the correct outcome as a failure. **That was a real bug and it is
now fixed** — the script scores both framings side by side. See §8 for what
happened when it was re-run, which is not what I expected.

This one is unaffected by the §1 retraction: it is a scoring defect either
way, and John fading major negative *from below* as resistance is direct
evidence that which side price approaches from is what decides the
expectation.

## 4. Long gamma is a low-volume node; short gamma is a high-volume node

The cleanest mental model in the whole corpus:

> "long gamma is basically the equivalent of a low volume node, and short
> gamma is the quote-unquote equivalent of high volume areas … I literally
> only look at long gamma."

- **Long gamma** — someone lifted the vols there, so it is *less* liquid,
  people are unwilling to transact, price does not want to sit there →
  reversion, clean pivots, definable stops.
- **Short gamma** — vols depressed, *more* liquid, price is happy to sit and
  churn → momentum and chop, no place to put a stop → **avoid**.

There is a no-trade filter attached:

> "I find it best to not even actively trade unless I see a lot of long gamma …
> if I don't see a lot of long gamma then the tape is probably not worth
> trading."

**Caveat that limits this for us:** long-vs-short here means *customer* long
or short, which requires the classified (State) product. On Classic's naive
model every put is assumed bought and every call sold, so the distinction
collapses. We cannot compute this on our tier.

## 5. A wall's appearance is not a directional signal

This one survives, but narrower than first written — and it does **not**
contradict §1.

Siento sees a large put position appear intraday, reads it the retail way (a
magnet: dealers must sell futures into it, so price gets pulled down), and
cuts his long. Jass corrects that specific inference: the participant "is
lifting the volatility surface and making the option more expensive, so **less
likely the spot to go there**." Siento's own outcome: *"the price never went
there."*

The distinction that an earlier draft blurred:

| Claim | Verdict |
|---|---|
| Price reaches the level and reverses off it | **Stands** — this is Siento's rule and John trades it |
| The level is hard to push through; it pushes price away | **Stands** — this is the same claim as above, seen from the other side |
| A large position *appearing* means price will travel to it | **Fails** — this is what cost Siento the long |

"Repels" and "acts as support you can buy" are not competing descriptions.
A barrier both pushes price away when reached and is hard to get through.
What fails is using the wall's appearance as a forecast of *direction of
travel*.

## 6. The NDX question, substantially answered — and favourably

The 2023 walkthrough warned the naive assumption is "only true for SPX" and
does not hold for individual equities, which left NDX unaddressed. This corpus
resolves most of it:

- **The co-founder trades NQ himself**, daily, off these levels, and moved to
  NQ from ES deliberately.
- The reason he gives is the opposite of a worry:

  > "NQ … it's a really inefficient instrument. The options are very
  > inefficient — that's **why we can even see these pivots so clearly** —
  > because they're just so expensive and there are way more liquid
  > instruments you can use to make plays off the NDX value. So when they do
  > make these plays it's much more apparent, much more clear where the levels
  > are."

- NQ is **more institutional and less retail** than SPY or QQQ, and the tape
  is easier to classify than ES precisely because there is less noise.

So the SPX-only caveat was aimed at single stocks. NDX sits on the right side
of it, and the vendor's own trader prefers it. **This materially reduces the
risk flagged yesterday** — though it remains true that Classic cannot tell us
whether a given strike is customer-long or customer-short.

## 7. A technical defect in our own pipeline: the frozen premium

Directly from the interview, and this one is ours to fix:

> "this is not truly futures spot … these are the NDX options and spot price.
> What we do is we calculate the premium between NDX and NQ … **we calculate
> that pre-market and then we add it to our NDX levels** to translate them
> into NQ. Now that premium can vary on an intraday basis — maybe we translate
> the levels at plus five, but intraday that premium is actually ranging from
> plus three, or plus seven, or plus ten."

Consequences for us:

- **Every `NQ_NDX` strike we store carries a stale basis**, fixed at the open
  and drifting by several points through the session. Independently
  corroborated: the sign-convention reconstruction recovered a constant basis
  of **+30.82** for the whole of 2026-09-04, against a spot difference of
  **+29.32** at the close — a 1.5-point drift on a quiet day.
- **Our touch tolerance is contaminated.** Testing "within 5 points of the
  wall" is not meaningful when the wall itself carries up to ~10 points of
  translation error. The tight tolerances in the sweep may be measuring
  basis noise.
- **It affects the dashboard too**, since those levels are meant to be drawn
  on a NAS100 CFD chart.

Jass's own workaround is to add the current premium mentally and to treat the
*relative* distance as the real quantity. The vendor plans to remove the
problem by ingesting real futures data (they name Databento as the vendor).

For us the fix is available now: `ndx` and `nq_ndx` are separate tickers on
the same API, so we can store the raw NDX levels alongside and compute our
own live premium rather than inheriting a stale one.

## 8. Re-running the touch test with the vendor's framing — no rescue

Both defects above predict that our near-coin-flip result was partly
methodological. So the scoring was fixed (§3) and re-run on 2026-09-04:

| tol | wall | directional | away |
|---|---|---|---|
| 10 | volume call | 50% | 50% |
| 10 | volume put | 44% | 44% |
| 10 | OI call | 50% | 50% |
| 10 | OI put | 67% | 0% |
| 25 | volume call | 29% | 29% |
| 25 | volume put | 57% | 29% |
| 25 | OI call | 50% | 17% |
| 25 | OI put | 50% | 25% |

Baseline: 46.8% lower / 53.2% higher.

**The correction did not produce an edge.** The "away" framing is no better
than the directional one and at wider tolerance is worse — though it is also a
stricter test, since it requires price to clear the tolerance band rather than
merely drift. With 3–14 events per cell none of this is distinguishable from
noise, which remains the honest headline.

What it does mean: the coin-flip result was **not** simply an artefact of
scoring the wrong direction. That hypothesis is now eliminated. The remaining
candidates are sample size, the stale-premium contamination in §7, and — most
likely given §1 — that we are still testing the wrong claim, because the
vendor does not assert that price reverses at the majors in the first place.

## 9. Execution detail worth having on record

Concrete rules from the interview, none of which we had:

- **Stops are tight, not wide.** 10–15 points on NQ, hidden behind the
  long-gamma node. On the conventional wisdom that volatile tape needs wider
  stops: *"that is actually dangerously wrong."* If a 15-point stop is getting
  hit, *"it's because your entry is not proper"* — skip the trade rather than
  widen.
- **Entry trigger** is an impulse high / wick — visible liquidity-seeking where
  someone gets caught — not the level being touched on its own.
- **Regime** is either net convexity, or simply whether the tape is hot or
  cold on a tick chart, with a real participant pushing rather than HFT
  scalping.
- **Targets** are the next cluster of long-gamma nodes; majors are for
  trimming.
- **Win rate is explicitly not the point**: *"you can have a pretty awful win
  rate and be fine"* — the edge is in restricting where you interact at all.
- Trade management is discretionary: reduce, flatten or reverse depending on
  regime, and the founders themselves differ on runners.

## 10. Net convexity — the regime metric, and we cannot compute it

From *Metric Overview: Net Convexity*, the clearest thing on the channel:

- It is the sum of the whole classified convexity ladder: are customers, on
  net, long or short options today, gamma-weighted.
- **Positive** = customers buying volatility = expecting movement = *less*
  liquidity = whippy, choppy, and on SPX a warning against trend-up.
- **Negative** = customers selling volatility = **providing liquidity** =
  movement stifled, floor under the market, gentle grind up.
- Described as *"your 0DTE VIX"*, and used by the other founder as his
  headline **gauge of risk**.
- Event caveat: into FOMC-type events positive readings are normal, and if the
  event passes without a selloff the bought volatility unwinds and becomes
  fuel for upside.
- Cross-check SPY against SPX: SPY skews retail and more directional.

**This requires classified order flow, so it is State/Orderflow, not Classic.**
`sum_gex_vol` is not a substitute — it is the naive unsigned aggregate. If we
ever want a regime filter of this quality, it is a subscription decision, and
it is the most persuasive argument for an upgrade in the whole corpus.

## 11. Smaller confirmations and details

- **"Our view is customer view."** The profiles show customer positioning; the
  dealer is the mirror. Worth stating explicitly anywhere our UI implies
  dealer framing.
- **Skew / the vol dots are a liquidity map.** Volatility is the inverse of
  liquidity; the preferred image is spot as a ball on a slope rolling toward
  the low-vol (high-liquidity) side. High vols above spot make upside hard.
- **SPX's normal skew** — customers long puts below, short calls above (the
  classic collar) — is *inherently bullish*, because it is harder to push down
  into lifted vols.
- **Flat skew** is the momentum condition: moves travel easily.
- **0DTE is more than half of daily options flow**, which is the justification
  for the whole intraday approach.
- Gamma is largest at the money, which is why far-OTM strikes with big open
  interest contribute little.
- The convexity ladder does not separate puts from calls, because a put and a
  call at the same strike have the same gamma.
- Aggregate DEX measures the notional capital customers have effectively put
  into or taken out of the underlying via options — a different question from
  gamma, and also Orderflow-tier.

## 12. What should change in this project

| # | Change | Why |
|---|---|---|
| 1 | ~~Stop treating majors as entry signals~~ **Withdrawn** — majors are entries *and* targets, as the source always said | §1 — retracted overstatement |
| 2 | Compute **distributions and sign-transitions** from the stored ladder and show those *alongside* the size ranking | §2 — Jass's preferred entry; an addition, not a replacement |
| 3 | Store raw `ndx` levels alongside `nq_ndx` and derive a **live premium** | §7 — our levels currently carry a stale basis of several points |
| 4 | Re-examine the touch tolerances once §3 lands | §7–§8 — tight tolerances may be measuring basis error |
| 5 | Treat **net convexity** as the strongest argument for a State/Orderflow upgrade | §10 |
| 6 | Narrow the "magnet" language: a wall's *appearance* is not a forecast of travel, but reversal at the level stands | §5 |
| 7 | Drop the SPX-vs-NDX escalation | §6 — largely answered, and favourably |
