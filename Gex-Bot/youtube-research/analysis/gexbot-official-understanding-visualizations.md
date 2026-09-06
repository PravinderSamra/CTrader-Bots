# gexbot — "Understanding Our Visualizations" (official)

| | |
|---|---|
| **Channel** | gexbot (the vendor's own) |
| **Speakers** | John and Jasper — the founders |
| **Published** | 2023-10-14 |
| **Length** | 44:01 |
| **Video** | https://youtu.be/pz5oIhQEJOs |
| **Transcript** | [`.txt`](../transcripts/gexbot-official-understanding-visualizations-pz5oIhQEJOs.txt) |

**Why this one matters more than the others.** The other two videos in this
folder are traders describing how they *use* the product. This is the people
who *built* it describing what it computes. On the question this project has
spent the most effort on — volume versus open interest — it is the primary
source, and it answers it directly.

**Caveat on age.** Recorded 2023-10-14, before the current Classic / State /
Orderflow / Quant packaging, and Jasper says "so far our classic gexbot",
implying the naive model was expected to change. The current FAQ still
describes Classic as naive, so the substance holds, but treat specifics as
possibly dated.

---

## 1. The sign convention, from the founder's mouth

> **[13:24]** "with this classification model … part of the reason really is
> that so far our classic gexbot, we're making the assumption where **all puts
> are bought and all calls are sold**, and therefore the naive gex still works
> generally well"

> **[07:17]** "assuming that, you know, **puts are negative gamma and calls
> are positive gamma**"

Customers buy puts and sell calls ⟹ dealers are short puts (negative gamma)
and long calls (positive gamma). That is exactly convention A, and it is now
confirmed three independent ways: measured from free public data at r ≈ 0.97
(`../../research/volume-vs-open-interest.md` Part 3), stated in the vendor's
FAQ as "naive GEX", and stated here by the founder.

## 2. The caveat nobody had flagged — and it applies to us

> **[13:59]** "but this is really something that's **only true for SPX**, due
> to the nature of the agents who are actually trading SPX. Now **for
> individual equities, generally that assumption does not hold**, and so
> making an assumption like that can really distort what the actual landscape
> looks like … of course we're applying this classification to SPX as well, so
> generally we have found that assumption to hold"

The naive assumption is not claimed to be universally valid. It is claimed to
hold **for SPX**, because of who trades SPX, and explicitly not to hold for
individual equities.

**We trade `NQ_NDX`.** NDX is an index, so it sits on the SPX side of that
line rather than the single-stock side — but it is not SPX, its participant
mix is not SPX's, and the founder makes no claim about it. At the time of
this video the product covered SPX, SPY, QQQ and a handful of mega-caps;
NDX was not among them.

This is a **genuine open risk that this project had not identified**, and it
is a better question for the vendor than any drafted so far: *does the
"all puts bought, all calls sold" assumption hold for NDX the way it does for
SPX?* If it does not, our walls are distorted in a way no amount of touch
testing on our own archive will reveal — because the archive inherits the
same assumption.

Note also that Freddy Siento (the other two videos) trades **SPX levels** and
executes on NQ, rather than using NDX levels. That may not be a stylistic
preference. It may be the correct response to exactly this caveat.

## 3. Is the volume reading actionable, or a rough stand-in?

> **[14:35]** "if you're looking at naive — classic gex, gex by volume —
> **high volume options nodes are still going to be very effective in terms
> of giving you good levels to trade off of.** That isn't the issue. The
> issue is **how well does the gex model actually apply in terms of
> determining market direction**"

This is the answer to the question this project was about to ask the Discord,
and it is more precise than either side of the argument we had been having:

- **Levels: endorsed.** High-volume nodes are good places to trade from.
- **Direction: not endorsed.** The naive model's weakness is inferring which
  way the market should go, not where the levels are.

That distinction maps cleanly onto our own findings. The touch test in
`analyse_vol_vs_oi.py` is a *levels* test and is the right test. The 43% of
the session where the two readings disagree about the **regime sign** is a
*direction* disagreement — and the founder is saying, in effect, that the
naive regime read is the weak part. We had been treating that disagreement as
the alarming headline; the vendor treats it as the known limitation of the
free-of-classification model.

## 4. The failure mode of a volume node

> **[15:10]** "sometimes there are nodes that seem really relevant in terms of
> classic gex that actually **all those orders are matched** — meaning even
> though there's a lot of volume, that level isn't necessarily super important,
> because there's no disagreement about that level. Everyone is very happy to
> transact there … there's no outsize influence"

A high-volume strike can be a *non-event*: if buyers and sellers are matched,
nobody is left holding an imbalance that must be hedged. Naive volume GEX
cannot distinguish that from a real imbalance; State's classification is
precisely the filter that can.

This is a concrete, testable prediction rather than marketing: **some fraction
of large volume walls should behave like nothing at all.** It is a plausible
explanation for the near-coin-flip touch results in Part 2 that does not
require the whole approach to be wrong — the sample may be diluted with
matched-order phantoms.

## 5. Other confirmations worth having on record

- **[01:11]** Bright bars = GEX by volume; dark bars = GEX by open interest.
  The dots are prior samples of the same strike.
- **[07:17]** "the volume ones **in day** have a tendency to be a lot more
  useful, obviously, because **volume's live**; open interest got reported at
  the beginning of the day and then didn't change as much anymore." Direct
  confirmation of the OI-is-frozen point that the FAQ states and that
  `strategy-synthesis.md` §5 now relies on.
- **[06:10–07:17]** Major positive = the call strike with the greatest
  concentration of gamma; major negative = the same for puts; zero gamma =
  the neutral point between them. Defined for both readings.
- **[10:03]** `full` = "three months aggregated gex" — the 90-day scope,
  confirmed by the vendor rather than inferred.
- **[18:02]** GEX profile carries full and next expiries; the classified
  volume distribution is **near-term only** (0DTE or next expiry).

## 6. What this changes

| Was | Now |
|---|---|
| "Is Classic volume actionable or a rough stand-in?" — the question to ask the Discord | **Answered by the vendor**: actionable for levels, not for direction |
| Volume vs OI framed as a contest | Framed by the vendor as live-vs-frozen, with different jobs |
| The 43% regime disagreement was the headline worry | It is the vendor's own known limitation of naive GEX; the *levels* claim is separate and survives it |
| No known instrument-specific risk | **The naive assumption is claimed for SPX, not NDX.** New open risk, and the best remaining question for the vendor |
| Touch test results looked simply weak | Matched-order phantom walls give a testable reason why a naive-volume touch sample would be diluted |
