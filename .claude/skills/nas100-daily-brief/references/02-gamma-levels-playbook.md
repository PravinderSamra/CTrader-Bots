# 02 — Gamma levels: what they are and how to trade them

Large options dealers hedge continuously. Their hedging is mechanical and
predictable, which makes these levels different from ordinary support and
resistance: price reacts to *flow*, not to sentiment.

## Gamma flip — the most important line on the chart
The price where dealer hedging switches sign.

**Above it** dealers hedge *against* the move — selling rallies, buying dips.
Volatility compresses, moves mean-revert, ranges hold. Sweeps genuinely fail.
**Below it** they hedge *with* the move — selling weakness, buying strength.
Volatility expands, trends persist, dips are not bought.

It is a **regime switch, not support/resistance**. Price crossing it is rarely
rejected cleanly; what changes is the character of everything after. Expect
visibly different 1m candles within 15–30 minutes of a cross.

Crossing it mid-trade is a management trigger: if you're in a Strategy-1 fade
and price breaks the flip against you, your edge just inverted. Tighten or exit.

## Call wall
The strike with the most call gamma above. Dealers must **sell** as price rises
into it, so rallies stall. The strongest magnetic ceiling on the board and a
prime Strategy-1 short-sweep level.

**Held break above inverts it.** The hedge flips to buying — a gamma squeeze.
A clean 1m close and hold above turns resistance into a launchpad. That's a
Strategy-2 long, not a fade.

## Put wall
The strike with the heaviest put gamma below.

**In positive gamma:** a defended floor. Price decelerates, wicks, reverses —
a prime Strategy-1 long-sweep level.
**In negative gamma it inverts, and this is what costs people money.** Dealers
short gamma must sell into the decline, so a break of the put wall is where
acceleration *happens*, not where it stops. Treat the break as a continuation
short trigger, never a bounce.

The brief states which case applies today. Follow it.

## Reading wall strength

Walls carry a strength scale and their gamma force:

```
CALL WALL ●●●●● 0.56bn        PUT WALL ●●●○○ 0.28bn
```

**The dots are gamma force ($GEX), not contract count**, and they are relative
to the strongest wall *of the same type* in that run.

Why not contract count — measured on real data:

| Wall | Contracts | Force | Distance | Force per 1k contracts |
|---|---|---|---|---|
| Weekly call | 8,657 | 0.56bn | +91 | **0.0647** |
| Weekly put | 7,091 | 0.28bn | −109 | 0.0392 |
| 45-day put | **168,275** | 1.01bn | **−609** | **0.0060** |

The structural wall holds **24× the contracts** of the weekly put wall but
produces only **3.6× the force** — and per contract it is **11× weaker** than
the at-the-money call wall. Gamma collapses with distance from spot, so a
distant wall can be enormous on paper and still barely move price.

**What the dots mean in practice:** ●●●●● is the wall dealers must trade
hardest to defend among its peers — expect the strongest reaction. ●○○○○ is
present but thin; treat it as a pause, not a floor.

**Scaling is within-group on purpose.** Comparing a structural wall's absolute
force against an intraday one made a level 609pts away render as the strongest
thing on the board. The absolute $bn is printed so you can still compare across
groups when you want to.

**Tenor confluence is the strongest signal.** When the weekly wall and the
45-day wall sit at the same strike, the level is defended across expiries — the
note says so explicitly ("It is ALSO the 45-day call wall"). Those are the
highest-quality walls on the board.

## Structural walls — what they actually do for a DAY trader

A 45-day wall several hundred points away is **not a level you will trade
today**. Price will not reach it inside one session's range. Be clear about
that: it is not support you can lean on intraday.

It earns its place for three indirect reasons, and only the third is a daily
decision input:

1. **It anchors the gamma flip.** The flip is computed from the whole book, so
   large distant open interest moves it. The structural wall is part of why
   today's flip sits where it does — and the flip decides which strategy works.
2. **It becomes relevant later.** As those contracts approach expiry their gamma
   rises and they start to bite. Irrelevant today, material in a few weeks.
3. **It marks where the corridor ends** — and the corridor is very much today's
   business. See below.

## The corridor read — the intraday translation

This is the part that matters for a day trade. The brief reports what sits
**between price and the next real barrier** in each direction:

```
- DOWNSIDE path: clear. Every options shelf from here to 28931.6
  (359pts, 0.76x ADR) is negative gamma — nothing structural to slow a
  breakdown. If it goes, it has room. Do not fade it.
- UPSIDE path: has friction. Expect a stall at 29381.6 (91pts away) —
  take partials into it rather than assuming a clean breakout.
```

**Only a positive gamma shelf actually brakes a move.** A run of negative
shelves is a low-friction corridor — an air pocket. So the useful daily
question is not "where is the big wall" but "is there anything between me and
it".

| Reading | What to do today |
|---|---|
| **Path clear** | A break has room. Don't fade it; give the trade space and trail rather than target |
| **Path mostly clear** | First brake is beyond today's budget — inside today's range there is little to stop it |
| **Path has friction** | Expect a stall at the named level. Take partials into it, don't assume a clean run |

## Structural walls on the board



`STRUCTURAL CALL/PUT WALL` rows come from the 45-day book and are usually far
outside today's range. That is the point: they are the **week/month** boundary,
not an intraday trigger. Mark them once and leave them — they are where a
multi-day move runs out of room.

They are deliberately exempt from the range-budget filter that removes other
distant levels, and they carry no `(stretch)` tag, because "partials only" is
the wrong framing for a boundary you are not trading toward today.

## Max pain
Where the most options expire worthless. A weak magnet on Monday, strong by
Thursday/Friday. **Coincident with the call wall = a hard pin.**

## Positive gamma shelves
Bins with large positive net gamma — price gets sticky. Good places to take
partials rather than push through.

Negative shelves are deliberately *not* on the board: price accelerates through
them, so there is nothing to trade at the level itself.

## Shape of the day — how the expiry buckets combine
Near-dated gamma decays *during* the session, so when the buckets disagree the
day has two regimes.

| Shape | What to do |
|---|---|
| `COHERENT_SHORT` | Whole book short gamma. Expansion, high conviction. ADR can be exceeded |
| `COHERENT_LONG` | Pinned range. Fade at the walls, keep targets modest |
| `PIN_THEN_EXPAND` | **Chop early, resolves late.** Be patient in the morning; save risk for after ~13:00 ET as 0DTE gamma decays |
| `SPIKE_THEN_REVERT` | Sharp move that mean-reverts. Fade extremes back to the middle only |
| `FRONT_FLAT_BACK_*` | Nothing pinning price today; the longer book sets the tone. Lower conviction |

## Secondary walls — why one call wall and one put wall is not enough

The headline walls come from `max(above, key=call_gex)` and
`max(below, key=put_gex)`. That leaves a blind spot: **call gamma sitting BELOW
spot**. It is not the call wall (that search only looks above spot) and it is
not the put wall (that search only reads put gamma), so it cannot be published
at all.

It is not a rare case. Those are in-the-money calls, and dealers long gamma
there **buy dips** — so the level behaves as *support*. On 2026-08-25 the
heaviest concentration anywhere near price was exactly this: **1.29bn across
43,299 contracts**, and price pivoted on it all afternoon while the board said
nothing about it.

The brief now prints an **Other gamma concentrations in range** block beneath
the level board. Each strike is ranked by whichever side actually dominates it,
labelled with what that implies, and de-duplicated against the main board.

Read the `what it does` column carefully — the sign convention is not intuitive:

| Where | Dominant | Behaviour |
|---|---|---|
| Below spot | CALL | **Support.** ITM calls, dealers buy dips into it |
| Below spot | PUT | Floor, while we remain in long gamma |
| Above spot | CALL | Resistance. Dealers sell into it, rallies stall |
| Above spot | PUT | OTM puts — thin, expect little reaction |

**Window:** ±0.75 × ADR14, deliberately *not* the range budget. The budget
forecasts how much further the RANGE can grow; these are levels price can still
REACH inside the range. On an exhausted day those are different questions, and
the second one is the one that has trades in it.

**A gamma wall is not a liquidity level.** It has no resting stops, so it is not
a Strategy-1 sweep trigger — its force is continuous dealer hedging, i.e.
absorption rather than a discrete break. Use liquidity (session highs/lows,
equal highs/lows, PDH/PDL) as the **sweep**, and a wall as the **reclaim
confirmation**. Sweeping into a wall and reclaiming it is a strong long; buying
a first touch of one is not.

## How option levels reach your CFD chart

Options are struck on a different instrument from the one you trade, so every
level is converted before it is printed. Three price series are involved:

| | What it is | Where it sits |
|---|---|---|
| **NDX** | the cash index — what options are actually struck on | the base |
| **NQ** | Nasdaq futures | NDX + basis (~+31pts at the time of writing) |
| **NAS100** | your broker's CFD | tracks NQ, plus the broker's own spread/markup |

**The conversion is a single additive offset, recomputed every scan:**

```
offset      = your_CFD_price − the_index_spot_the_levels_came_from
chart_level = option_level + offset
```

**Additive, not multiplicative, and that is deliberate.** Futures fair value is
`cash × e^((r−q)T)`, which is a *ratio*. Applying a ratio would scale distant
levels differently from near ones. The error from using an offset instead is
`(level − spot) × basis%`: with a ~0.1% basis, a level 400pts away is wrong by
**0.4pts**. Below the width of the spread, and far below the width of any level
worth marking.

**Which index you anchor to does not matter, and that is provable.** GEXBot
publishes both `NDX` and `NQ_NDX`, where `NQ_NDX = NDX + a constant`. Anchor to
either and the constant cancels:

```
NDX_level + (CFD − NDX_spot)  ==  (NDX_level + k) + (CFD − NDX_spot − k)
```

Verified live: both routes produced **29,472.5** to the decimal. So the choice
of endpoint is a matter of convenience, not accuracy.

### The part that DOES go wrong: mismatched timestamps

The offset is only meaningful if both prices are from **the same moment**.
Subtract a stale feed's spot from a live CFD price and the difference silently
absorbs every point price moved in between — and that error lands on **every
level equally**.

Measured 2026-09-05 against a 1,160-minute-old feed: the live-price offset was
−57.5, the correctly matched one −43.0. **14.5 points of error on every level**,
on a quiet weekend. Through a gap it would be far worse.

The brief now looks up the CFD price at the feed's own timestamp whenever the
feed is more than 10 minutes old, and prints which basis it used. This is the
same defect as the stale NDX cash print that once inverted a trade call, and it
is fixed the same way — by pairing like with like.

**Practically:** mark the levels exactly as printed. They are already in your
CFD's price space, and the header line tells you what offset was applied and
whether it was matched or live.

## Honest limits

**Open interest is T+1 — for everyone.** This is the single most important thing
to understand about every gamma level in this brief. Three different feeds with
three different freshnesses go into a wall:

| Input | Freshness | What we do |
|---|---|---|
| Quotes, IV, greeks | ~15 min delayed, updates all day | Repriced with Black-Scholes at the CURRENT spot |
| Volume | Live, intraday | Available but not used for walls (see below) |
| **Open interest** | **Updated ONCE, overnight** | Used as-is — there is no alternative |

Open interest is computed by the **OCC after the close**, from that day's
clearing. Nobody has it in real time. Not us, not SpotGamma, not any paid
vendor at any price — it is a property of how the options market clears, not a
limitation of a free data source.

**So yes, positions build during the day that the walls cannot see.** Measured
on 2026-08-26: contract `NDXP260826C29300000` traded **3,039 contracts against
an open interest of 35**. Across the whole book, 0DTE volume was **9.93×** its
open interest, and the top-6 strikes ranked by OI overlapped the top-6 ranked by
volume in only **2 of 6** cases.

Two things stop that being fatal:

1. **Most 0DTE volume never becomes open interest.** A contract bought at 10am
   and expiring at 4pm is born and dies inside the session. It is churn, not a
   standing wall. (It is still hedged while alive — the gamma is real for the
   hours it exists, which is why intraday pins can form that we cannot see.)
2. **The effect is concentrated in the near tenors.** Volume/OI by bucket:
   0DTE **9.93**, this-week **4.65**, 2–10 dte **0.36**, full-45dte **0.95**.
   The structural walls are large, slow positions at round strikes (30,000,
   29,500, 27,000) that a single day's trading barely moves. Today's volume
   clusters tightly around spot; OI clusters at round numbers.

**Impact, by what you are reading:**

| Level | Exposure to stale OI |
|---|---|
| Gamma flip / net-GEX regime | Negligible — dominated by large slow OI |
| Structural 45-day walls | Negligible |
| This-week call/put wall | Moderate |
| Intraday 0DTE pins | **Significant, and unfixable at any price** |

**Why we do not just weight by volume instead.** Volume has no sign. It does not
say whether a trade opened or closed a position, or who was buying. Open
interest at least has a standard convention to anchor it (dealers long calls,
short puts). Weighting walls by volume would stack a second assumption on top of
the first and call the result an improvement.

- CBOE data is ~15 minutes delayed. This is a map, not a live feed.
- Dealer positioning is *assumed* (long calls / short puts), not observed.
  Levels and regime are robust; absolute dollar figures are approximate.
  Nobody — free or paid — actually knows dealer inventory.
