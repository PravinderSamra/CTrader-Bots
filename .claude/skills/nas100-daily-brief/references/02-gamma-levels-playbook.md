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

## Honest limits
- CBOE data is ~15 minutes delayed. This is a map, not a live feed.
- Dealer positioning is *assumed* (long calls / short puts), not observed.
  Levels and regime are robust; absolute dollar figures are approximate.
  Nobody — free or paid — actually knows dealer inventory.
