# The Strategy, And What Confluence Actually Has To Prove

## The strategy as you described it

1. Mark key pivot points on the **hourly** chart.
2. Wait for price to return to those levels, watching on the **1–2 minute** chart.
3. Read the reaction:
   - On a **bearish day**, look for rejection, or a break-and-retest, and go short.
   - On a **bullish day**, the mirror image.
4. Stop goes **just beyond the deepest wick**.

This matches the publicly described Gala approach closely — including the detail
that levels are drawn from candle **bodies and opens** as much as from wick
extremes, on the reasoning that the open of a strong impulsive candle marks where
one side first took control. Targets are modest and consistent (~1.5R–2R) with
partial scaling as price moves. Worth noting because it sets the bar for what
"good enough" confluence means: you are not hunting 10R, so a filter that costs
you half your setups to gain a little accuracy is a bad trade.

## The specific moment you want help with

> Price moves up to a level I marked, starts printing wicks through it but fails
> to break. I want to be confident those wicks are sellers absorbing buyers, not
> just noise before a breakout.

This is a real and well-defined question, and it has a real answer. The wick
pattern alone is genuinely ambiguous — the tape of a level about to hold and a
level about to break look similar on a 1-minute chart. That ambiguity is exactly
what a heatmap resolves for Bookmap users: you can *see* whether size is resting
above and whether it is being eaten or refilled.

## Two different things could resolve it, and they're worth separating

**(a) Live evidence — "is there size resting there right now?"**
This is a Level 2 depth question. It's what Bookmap answers. Section 2 of
`02-DATA-SOURCE-INVESTIGATION.md` establishes that cTrader's Open API can supply
this for free, with the important caveat that a CFD broker's book may be thin on
indices — which is why the probe tool exists.

**(b) Historical evidence — "what happened the last N times this exact thing occurred?"**
This needs no order book at all. If this level has been tested 14 times, held 8 of
them, and the wick went more than 3.8 points through it only once in ten, then you
know both how much conviction to have *and* where the stop genuinely belongs.

(b) is available today from data you already have, and it directly sizes your
stop — which was the other half of your question. (a) is the better live signal
but depends on a probe result we cannot get from here.

**So the project builds (b) first and (a) second.** That ordering isn't a
compromise; (b) is what tells you whether the setup is worth taking at all, and
it's the layer that keeps working even if the depth feed turns out to be thin.

## What this cannot become

A caution worth writing down at the start, because it's the failure mode that
makes these projects worse than useless:

- **cTrader bar volume is not volume.** It is a count of quote updates. Any
  "delta", "CVD" or "buy vs sell volume" computed from it is a fiction. This was
  tested — §4 of the investigation — and it carries no signal separating levels
  that hold from levels that break.
- **CFD depth is not exchange depth.** It is the liquidity your broker can fill
  you against. For sizing a stop that's arguably the more relevant number, but it
  is not "the market", and a level with no size in Pepperstone's book may still
  have plenty in the FTSE futures book.
- **A statistical edge is not a prediction.** "Held 8 of 14" means it breaks
  often. The value is in sizing and selection, not certainty.

Everything the tooling outputs is labelled with which of these it is.
