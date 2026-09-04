# Analysis — Chart Fanatics: Freddy Siento on options-flow trading

**Video:** "STEAL This INSANE 1-Minute Market Maker Trading Strategy (75% Win Rate)"
**Channel:** Chart Fanatics · **Published:** 2026-08-23 · **Runtime:** 2h 29m
**URL:** https://youtu.be/35cyqDz-ej8
**Transcript:** `../transcripts/chart-fanatics-35cyqDz-ej8.txt` (~25,600 words)

**Speaker:** Freddy Siento — ~20 years institutional, market-made FX outright
swaps/forwards in London, junior broker in Australia through 2008. Retail
trader for ~3.5 years at time of recording. Trades NQ futures off SPX/NDX
options levels. Coaches in Spanish-speaking South America.

He describes himself not as a GEX trader but as *"an options flow trader
which trades futures based on options flows."* He is explicitly dismissive
of the "gamma exposure" label as too narrow — his read includes implied
volatility, skew and the volatility surface, not just gamma.

---

## 1. The causal chain (why the levels work at all)

This is the spine of the whole episode. He builds it on a whiteboard before
showing a single chart.

1. **Institutions are forced hedgers.** Pension funds, endowments, mutual
   funds are structurally long the market and must buy protection. He dates
   the behaviour to Black Monday 1987 and the 1973 launch of standardised
   CBOE options + Black-Scholes. Post-2000 and post-2008 this became
   universal. Key word he repeats: *forced*. They are not expressing a view,
   they are discharging a mandate.
2. **Market makers take the other side and cannot refuse.** Their job is to
   provide liquidity and earn the spread, not to take a view. He draws on his
   own desk experience: he could not decline a quote.
3. **That leaves the MM with unbounded risk**, so they hedge with the Greeks.
   Delta first — sell a call, buy futures. Then gamma: as spot moves, delta
   changes, so the hedge must be resized continuously.
4. **The hedge is self-reinforcing.** MM buys futures → price ticks up →
   delta rises → must buy more futures. He calls it a snowball, and says
   this is why indices sometimes grind up relentlessly. His personal
   epiphany: hedging £1.5bn of sterling derivatives, he watched *his own
   hedge* move spot. *"My edge is to enter the market when the big guys
   enter the market."*
5. **0DTE compresses all of this into one session.** Since the SEC allowed
   0DTE in 2021 they've gone from ~21% to ~60-70% of daily index option
   volume. His analogy: with monthly options the MM hedges like a car at
   80km/h and can steer gently; with 0DTE he's in an F1 car at 300km/h,
   braking and steering at speed. Same hedging, vastly compressed.

**The tradeable consequence:** the futures order flow that moves NQ/ES
intraday is substantially a *by-product* of options hedging. If you know
where the options are stacked, you know where the hedging flow must appear.

Note his counter-intuitive claim: 0DTE has **stabilised** rather than
destabilised markets, contrary to early academic worry.

---

## 2. Why the biggest level reverses price — the actual edge

This is the part that distinguishes him from generic "GEX levels" content,
and it's the answer to *"how does he get an edge out of this."* It is a
**two-actor** story, not a wall-as-obstacle story.

Take a call the institution bought out-of-the-money, now approaching the
strike:

- **Convexity means the institution's profit decelerates at the strike.**
  Below the strike the option gains value exponentially; at/above it the
  payoff goes roughly 1:1. His illustration: the run *up to* the strike
  makes ~$100k, the same distance beyond makes maybe ~$60k. So at the strike
  you are *"risking 100 to make 60."*
- **Reversal risk.** Having made that money, a pullback gives most of it
  back.
- **Theta decay.** In 0DTE, decay accelerates hard from roughly midday into
  1:30pm. He frames it as *"the government taxing your position"* every
  minute.

So the informed institution **takes profit at the strike** — the rational
move given all three. Peak gamma is also delta ~0.50, the peak of their
profit curve.

**Then the mechanical part.** The institution sells the call back. The MM's
options book goes flat — but he is now left holding the futures hedge he
accumulated on the way up. That hedge is now an unwanted imbalance. To get
back to delta-neutral he must **dump those futures**. That forced selling is
the reversal.

> The level is not resistance. The level is where the informed money takes
> profit, which *forces* the market maker to unwind his hedge in the futures
> market — and that unwind is the move you're trading.

This is why he insists understanding matters: *"people who come to trade
gamma... through GexBot, if they don't understand what's happening, they
probably going to make a lot of mistakes trading those levels."*

He also notes a reflexive second layer: other informed traders now
anticipate this and pre-position (e.g. buying calls below the level), which
sharpens the reaction further.

---

## 3. The strategy as actually traded

**Instrument split — this is important.**
Read the levels on **SPX** (and NDX); execute on **NQ** (he trades full-size
NQ, not micros; occasionally ES). Rationale: SPX is the biggest options
market, so institutions do their analysis and position there; SPX/SPY/ES/
NDX/QQQ/NQ all move together via the same MM hedging. He notes SPX walls and
NQ walls don't always align exactly — NDX traders likely take their cue from
SPX. GexBot converts NDX strikes to NQ prices for him, so he reads NQ-priced
levels directly.

**Which level:** only the **single largest** gamma concentration — the
maximum positive (call) or maximum negative (put) gamma strike. *"We trade
the main biggest line."* Secondary large levels become **targets**, not
entries.

**Which data view:** **90-day open interest**, checked at 9:30am ET. He
wants the full picture of how the market is positioned for the day, not just
today's expiry. This works best in the **first two hours**, and he says
there's a mathematical reason for that.

**Session window:** first two hours only. He deliberately avoids the
afternoon because charm (time-decay hedging) and vanna (vol hedging) dominate
into the close, and he considers that far less predictable than the delta/
gamma dynamic he trades. He is candid: *"we are still learning how to trade
charm."*

**Entry trigger — the slope rule.** He does not simply buy the touch:
- **Fast/steep approach** → likely to punch through ("it's physics"). Wait
  for the level to be **reclaimed**, then enter on the recovery.
- **Slow/gentle approach** → expect it to hold; take the level directly.

**Direction rule:** the level itself is not directional — position relative
to it decides. Approaching from below → look to sell at the level;
approaching from above → look to buy. His research is that these levels are
predominantly **reversal** points.

**Stops:** 30-50 ticks NQ, placed structurally (below the swing low that
formed at the level). Rationale is elegant: the MM is in an F1 car — if the
level is going to work, it works *immediately*. If it doesn't move, something
unseen is happening and you're out cheaply.

**Targets:** the next large gamma level. Typical winners quoted: 300-800
ticks. He is explicit that he takes the reversal move and does not hold for
a trend.

**Management:** scale in with 2+ contracts, take profit on one, move the
other to break-even.

**Frequency:** one to two setups a day from this model — sometimes none, in
which case he doesn't trade it. He has four or five models in total; this is
the one presented here.

**Claimed stats:** 75% win rate; risk ~$150-200 to make ~$2,000 on NQ (he
frames it as roughly 1:10); a stop only every 2-3 weeks. He uses it to pass
prop-firm evaluations, sizing up to 10 NQ contracts for ~$6,000 on a move.

**Failure mode he names:** the level doesn't fail randomly — it fails when
*another* institution positions at a lower/further level, which then
magnetises price through. Response: wait for price to reach the *new*
maximum-gamma level and trade that instead. Levels also migrate intraday
(he shows a put wall moving 5550 → 5530) and his response to that chop is
**do nothing** until price reaches the level.

---

## 4. The second model — convexity levels

Distinct from the OI levels above and, he concedes, harder to read.

- Derived from the **volatility surface** rather than open interest.
- **Cyan bars = positive convexity** (institutions *buying* volatility).
  Price is drawn to them and rejects. His analogy: a ball rolled up a
  mountain rolls back down.
- **Purple/red bars = negative convexity** (selling volatility). Price falls
  through these easily — he does **not** trade them.
- He trades **positive convexity → positive convexity**, i.e. from one cyan
  peak to the next.
- Bar size is not the tell — a visually small bar can still be billions of
  dollars.
- He describes the whole thing as *"a map of liquidity"* — where institutions
  take liquidity vs. provide it.

Timing split worth noting: **OI levels work best in the first two hours;
convexity levels relate more to the volatility surface** and are what he
turns to for the choppier open.

---

## 5. Supporting reads he mentions

- **IV skew as a floor/ceiling filter.** He recounts telling Fabio Valentini
  that skew showed the market wasn't going lower, so take profit — it
  reversed. Skew is used as a "don't expect continuation" filter.
- **Order flow / footprint as confluence.** He uses ATAS. His point: "big
  trades" and apparent "trap sellers" at a major options level are usually
  just the market maker bidding, because he knows in advance he'll need to
  buy back the futures he sold on the way down. Big-trade signals have a
  much higher hit rate *when they coincide with a major options level*.
- **Psychology.** A substantial chunk of the episode. Eight years of
  mindfulness practice; monitors his own heart rate; shuts the platform down
  after a stop because he's "used to winning" and knows the amygdala/cortisol
  response will drive revenge trades. His view: humans are not built to be
  traders, and the successful ones are all excellent risk managers.

---

## 6. GexBot specifics from the transcript

Auto-captions mangle the product name throughout ("guestbot", "guess what",
"Gexot") — worth knowing when searching the file.

- He uses the **Classic** subscription (named explicitly at 01:27:22).
- He stresses Classic is **not just raw data** — there is real computation
  behind it, specifically because the MM nets off offsetting client orders
  and only hedges the residual. A naive OI sum would overstate hedging need.
- Red bars = puts, green bars = calls, dashed line = the major wall.
- Platform converts NDX strikes to NQ prices — no manual basis adjustment.
- He views charts on **1-minute** (sometimes 5-minute) candles.
- Chart Fanatics say in the outro they'll arrange a GexBot affiliate offer.

---

## 7. Honest caveats

- **All performance claims are self-reported.** 75% win rate, 1:10 R:R and
  a stop every 2-3 weeks are unverified, presented via selected screenshots
  of winning trades on a sponsored podcast. This is marketing-adjacent
  content. Treat the numbers as a hypothesis to test, not a baseline.
- **The mechanism is sound and checkable even if the stats aren't.** The
  causal chain in §1-2 is standard dealer-hedging theory and is the part
  worth building on.
- **Survivorship in the examples.** He shows the trades that worked. The
  failure mode is acknowledged but not quantified.
- **Definitional ambiguity to resolve.** He says "90-day open interest",
  which does not map cleanly onto GexBot's `zero`/`one`/`full` scopes —
  `full` (all expiries) is the closest but is not a 90-day window. This
  needs pinning down before any implementation.
- **The convexity model is under-specified.** Not reproducible from the
  transcript alone, and likely requires a higher GexBot tier than we have.
