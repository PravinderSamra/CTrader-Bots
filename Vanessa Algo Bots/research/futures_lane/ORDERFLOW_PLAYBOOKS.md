# Futures lane: order-flow playbooks (for later)

These are strategies we can't run as cTrader bots on FTMO. They read the real order book or real
exchange volume, and FTMO CFDs have neither. They need futures (NQ / ES / MNQ / MES) plus an
order-flow platform (Bookmap, DeepCharts, ATAS, Sierra Chart and similar).
Kept here for when Vanessa moves into discretionary futures scalping.

Every entry lists: market, timing, the rules as the trader gave them, risk handling, and
what to practise first. The short version of each is also in research/IDEAS_BACKLOG.md.

---

## 1. Fabio Valentino: two-model NQ scalping (Chart Fanatics)
Top-3 in the Robbins World Cup futures division (500%+ in 12 months). Trades NQ, mostly the New York session.
Platform in the episode: DeepCharts (volume profile with delta per price, big-trade bubbles, CVD).

**Building blocks**
- Market state: *balance* (price rotating inside a value area) or *imbalance* (price has left it and
  is looking for a new balance). Auction market theory.
- Volume profile: POC (price with most volume), value area high / low, low-volume nodes (LVN:
  thin prices that act as reaction levels).
- Big-trade filter: show only market orders of at least 30 contracts on NQ in New York
  (20 in London; he raised it to 40 on a busy open). These show as bubbles.
- CVD (cumulative volume delta): running total of aggressive buying minus aggressive selling.

**Model 1: trend / imbalance (New York session only)**
1. Timing: New York cash session. No trades in the 10-20 minutes before the open. The day's direction
   usually shows in the first 15-30 minutes. Flat by the close; no overnight.
2. State: the market must be out of balance (broken out of the previous balance / previous day's value).
   No trades while it is in balance.
3. Location: draw a profile over the impulse leg (swing start to swing end) and find the low-volume node.
   Set an alert just before it; no resting limit order.
4. Trigger: aggression at that level in your direction (a big bubble, e.g. a large red bubble for a short).
   For breakout entries: wait for a full-body 1-minute candle close beyond the level ("the second
   drive", never the first).
5. Stop: just beyond the big aggressive order. Tip: put it 1-2 ticks inside the obvious high/low
   to avoid the slippage when stops there get run.
6. Target: the previous balance area's POC; take the whole position off there (about 70% of the time the market reacts there).
   If there is no POC in the way (value moving up), trail instead.
7. Move to break-even quickly: once the next breakout happens, or once CVD is pushing strongly in your favour.

**Model 2: mean reversion (London session, quiet / summer months)**
1. State: balance (simple version: use the previous day's profile).
2. Price breaks out of the value area and fails. Do not take the first move; wait for the second swing / retest.
3. Location: the LVN on that swing. Trigger: big aggressive orders back towards value.
4. Target: the POC (where most volume traded), not the far side of the range.
5. Stop: just beyond the big orders; be wrong immediately.
He says this model gets "destroyed" in New York volatility, so use it only in London / compression.

**Risk rules he gave**
- 0.25% of the account per trade (personal account); 0.5% in the competition; up to 1% only when far up.
- Max daily loss 2% (about 8 stops). Worst run seen: 11 losses in a row; up to 9 losses in a day.
- Build profit for the day first; riskier setups only with the day's profit ("house money").
- Take partials; don't hold for the home run (he once watched a $28k day reverse into a loss).
- Win/loss: 1:2.5 minimum, 1:4-5 common, 1:10+ only on 2-3% trend days.
- Commission matters at about 2,400 trades a year.
- Monday and Friday are his weakest days (choppy). Stop after 2-3 losses on a compression day.

**Live example in the episode:** about +$1,000 on one NQ contract in about 1.5 hours (one winner,
one -$255 loss, one small locked-in winner). Most of the day was chop.

**What to practise first:** replay NQ in New York with the 30-lot bubble filter. Only mark
(a) the balance / imbalance state and (b) the LVN on each impulse. Don't trade until the
marking matches what price does afterwards.

---

## 2. Carmine Rosato: order-flow scalping on ES (Chart Fanatics)
Platform: Bookmap (heat map of resting limit orders) plus footprint charts.

**Building blocks**
- Passive orders (limits, the resting liquidity) vs aggressive orders (market orders that hit them).
- DOM, heat map, footprint.
- Absorption: heavy aggression into a level that does not move price, so the passive side is winning.
- Stop runs.
- P-shape and b-shape profiles: short covering vs long liquidation.
- Zero prints / single prints: unfinished auction, price tends to come back.

**Rule: CLC**
- Context: what is the day doing (trend, balance, news)?
- Location: a pre-marked level (prior-day high/low, value edges, LVN, big heat-map liquidity).
- Confirmation: order flow at that level (absorption, aggression with follow-through).
No location = no trade.

**Entry and risk:** enter on the order flow, not on a candle close. This keeps the stop tight,
and his trades target 4-10R. He reviews his data every week.


**Episode 2 (his exact strategy): the low-volume-node (LVN) pullback**
1. Mark a supply/demand zone or support/resistance: the consolidation right before an impulsive move (15m-30m chart).
2. Wait for price to come back to the zone and react strongly (the bounce proves buyers are there). Don't buy the zone itself.
3. Volume profile over that reaction leg: find the LVN, the thin price area the move went through quickly.
   Prefer the LVN near the start of the move (just off the zone), not one at the top of an extended move.
   (His losing example: buying an LVN at the day's high after an extended rally.)
4. Wait for the pullback into the LVN and for order-flow confirmation there: passive buyers on the heat map actually
   getting filled (big sell prints that don't push price lower = absorption), or a large delta outlier against the move.
   Enter on that, before the 1-5 minute candle closes (that's where the 4-6R comes from).
5. Stop: a few points beyond the low of the entry candle / the absorption. Target: low/high of day, the next LVN,
   or the next level where the other side could take profit. Scale out at the next LVN; hold more only if it's reclaimed.
- Risk: fixed dollar risk per trade (he uses $3.5-4.5k), contracts sized to the stop distance, so every loss is the same size.
- Rule CLC: Context, Location, Confirmation. First 2-3 hours of the session only. Label every trade with its setup name.
- Tools: volume profile (volume by price), heat map (Bookmap), footprint/delta. His YouTube order-flow series explains them.
- His results shown: +$15k (4.5R), +$21.75k (5.5R), +$17k (3.5R), and one -$4.3k loss (1R).

**What to practise first:** pre-mark 2-3 levels before the open and only watch the order flow when price
reaches one. Journal (TradeZella) whether absorption at the level held.

---

## 3. Jay Ortani: 'market DNA' (Bookmap, news / earnings stocks)
- One or two "levels of significance" per day; read the live order book and time & sales there.
- Mechanical parts we could test (next-day continuation, Camarilla R4/S4) showed no edge
  (screens/jay.py), so the edge, if any, is in the live reading.

## 4. Forrest Knight: volume-profile edges
- High-volume doji / hammer / shooting star that sweeps the prior-day or overnight high/low:
  trade back into value, target the next level. Prior-day VAL / POC retests in an uptrend.
- Lost money on NAS100 CFD tick volume (screens/forrest.py), but CFD tick volume is not exchange volume.
  His A-grade trades use 4-hour / weekly candles. Worth re-checking on real NQ volume.

---

## Common threads (worth keeping in mind even for the bots)
- Trade only at pre-marked levels; the rest of the day is noise.
- Wait for the second drive / retest, not the first break.
- Be wrong quickly and small; move to break-even fast; take partials.
- Daily loss cap and "stop after N losses": the same idea as our bots' Daily Guard.
- Weekly data review (TradeZella).

## Practical notes for when she starts
- Market: micro contracts first (MNQ $2/point, MES $5/point) so a 10-point NQ stop costs $20, not $200.
- Data: real-time CME depth is a paid add-on on most platforms. Check what the prop firm's
  platform includes before buying anything separately.
- Prop firm rules differ from FTMO (trailing drawdown, consistency rules, news rules). Read them before choosing a setup.
