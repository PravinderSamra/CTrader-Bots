# Confluence Guide — RSI-ADX Rejection Scanner

This document explains *why* each signal in `AgentSkill.md`'s scoring rubric exists,
why it's weighted the way it is, and what it's actually telling you about the market.
Read this if a scan result seems wrong, or before changing the rubric.

---

## The core thesis

Standard mean-reversion ("RSI is oversold, buy") fails constantly because RSI can sit
at an extreme for a long time *while the trend that put it there is still strong*. The
fix isn't a better RSI threshold — it's recognising that an extreme only matters when
the **force that created it is fading**. That's what ADX-declining-from-a-peak adds:
it doesn't ask "is price stretched?" (RSI's job) — it asks "is the move that stretched
it running out of energy, right now?" Only when both are true does a rejection candle
mean something — it becomes the visible moment buyers/sellers actively step in and
repel a now-weakening attempt to extend the move, rather than just noise inside an
ongoing trend.

In short: **RSI finds the extreme. ADX confirms the extreme is exhausting, not just
extending. The rejection candle is the live evidence that the exhaustion is being
acted on, right now, at a price.** All three must agree, or you're trading on one
indicator while pretending you have three.

---

## Signal-by-signal rationale

### RSI extreme (gate: ≤30 / ≥70; bonus: ≤25 / ≥75)
RSI measures the speed and magnitude of recent price changes. At extremes it shows the
move has been unusually fast/large relative to its own recent history — a necessary
(not sufficient) condition for "this has gone far enough that a snap-back is
plausible." The deeper the extreme, the more the move has outrun its own average pace,
and the more "coiled" the snap-back potential — hence the bonus for ≤25/≥75 over the
baseline ≤30/≥70.

**Why it's not enough alone**: in a strong trend, RSI can print 25 repeatedly for
hours while price keeps falling. This is the single most common reason naive
RSI-reversal strategies lose money — they're fighting a trend, not catching its end.

### ADX declining from a recent peak (gate: peaked ≥25, now declining, still >18)
ADX measures trend *strength* (not direction — that's what +DI/-DI are for). A
declining ADX after a peak means the trend that drove price to the RSI extreme is
losing conviction — fewer participants pushing in the same direction, momentum
fading. This is the filter that separates "exhaustion" from "extension":
- If ADX is still climbing: the trend has fuel left — an RSI extreme here is a trap.
- If ADX has collapsed below ~18: there's no trend to exhaust — you're in chop, and a
  "rejection" here is just random noise inside a range, not a real reversal signal.
- The sweet spot — peaked meaningfully (≥25, ideally ≥30 for the bonus), now rolling
  over, but still showing some directional structure (>18) — is the moment a real,
  identifiable trend is running out of steam. That's the highest-probability window
  to fade it.

This is why the skill calls this gate **non-negotiable**: remove it, and you've built
a slower, worse version of an RSI-reversal scanner that already exists in this repo
(Trade Picker). ADX is what makes this agent a *distinct* edge.

### Rejection wick (gate: matches direction; bonus: ≥65% wick / ≤30% body)
A long wick with a small body shows that price *attempted* to extend the move and was
firmly rejected within the same candle — buyers/sellers actively absorbed the
attempt and pushed price back. This is concrete, visible evidence that the exhaustion
thesis is being acted upon right now, by real participants, at a real price — as
opposed to RSI/ADX merely suggesting it's "due." The cleaner the wick (long, with a
small body showing the rejection dominated the candle), the more decisive that
rejection was.

**Why it must match direction**: a bullish (lower-wick) rejection during what should
be a *short* setup means buyers showed up exactly where you'd want sellers to —
your thesis and the candle are contradicting each other. Treat any mismatch as a hard
disqualifier, not a "weaker" signal — see the Sanity Check in `AgentSkill.md`.

### Location precision (bonus: wick within ~0.05–0.10% of a swing high/low)
A textbook rejection candle in the middle of a range, with no level behind it, is much
weaker evidence than the same candle printing exactly at a recent swing high/low —
because the latter is where other market participants (institutional orders, stops,
liquidity pools) are actually concentrated. A rejection *at* a level says "this is
where the crowd was positioned, and the crowd just got rejected." A rejection in open
air says "price wiggled." This is the difference between a setup with structural
logic behind it and one that merely *looks* like a setup.

### Volume confirmation (bonus: rejection candle ≥1.2× the 20-bar average volume)
A wick on light volume could just be a quiet period where a small order moved price
disproportionately (wide-spread noise). A wick on elevated volume means real
participation fought at that price — a much stronger tell that an active battle
occurred and was decisively won by the side you're betting on.

### Multi-timeframe alignment (bonus: H1 RSI also recently extreme in the same direction)
The M15 chart is noisy by nature — confirming the extreme also shows up a level up
(H1) tells you this isn't a blip that the higher timeframe will simply absorb. It
substantially raises confidence that the M15 reversal has room to actually develop
into a tradeable move rather than fizzling immediately back into the H1 trend.

### DI confirmation (bonus: the driving DI is fading too, not just the ADX average)
ADX is the *average* of the directional movement — it can lag a turn in the underlying
+DI/-DI relationship. If you're fading a downtrend (LONG setup), you want to see -DI
itself declining (the actual selling pressure easing), not just "ADX happens to be a
bit lower than its peak while -DI is still climbing." This bonus rewards confirmation
from the more responsive, underlying series rather than its smoothed average.

---

## Why the minimum threshold is 6/10

The three baseline "present" gates (RSI extreme, ADX exhaustion, matching rejection)
already account for roughly 3 of the 10 points just to *qualify* for scoring at all —
a setup that barely clears the gate with no depth, no clean wick, no good location, no
volume, and no confirmation will land around 3–4. Requiring 6/10 means you need real
*quality* on top of the bare minimum — at least two or three of the bonus dimensions
(depth, wick cleanliness, location, volume, MTF alignment, DI confirmation) firing
alongside the baseline. That's the difference between "technically meets the
definition" and "this is genuinely high-probability."

---

## A note on iterating this rubric

Log every trade in `TradeLog.md` — including the score and which specific signals
fired. Over enough samples, you'll be able to see which bonus signals actually
correlate with winners (worth keeping/raising the weight of) versus which ones fire on
both winners and losers indiscriminately (candidates for removal or re-weighting).
Don't guess at the "right" weights in the abstract — let the logged outcomes tell you.
