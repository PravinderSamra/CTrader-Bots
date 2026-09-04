# Analysis — "Master Gexbot Classic" (Freddy Siento's own channel)

**Video:** "Master Gexbot Classic – Trade Like a Pro with This Simple Yet Powerful Tool!"
**Channel:** GexFuture Trading (Freddy Siento) · **Published:** 2025-03-16 · **Runtime:** 49:48
**URL:** https://youtu.be/6r2329ybeb8
**Transcript:** `../transcripts/gexfuture-master-classic-6r2329ybeb8.txt` (~8,300 words)

This is the **operational** video. Where the Chart Fanatics episode explains
*why* the levels work over 2.5 hours, this is Siento at his own desk walking
through the actual GexBot Classic screen and the rules he trades. It is 17
months older but far more precise, and it is the more useful of the two for
implementation.

His framing: newcomers rush to the advanced tiers (State, Orderflow), but
Classic alone is enough. *"I use this every day... this is my main one."*

**Everything here is Classic tier — the tier our token already holds.**

---

## 1. What the Classic screen shows

A horizontal histogram of gamma exposure by strike:

- **Green bars right** = call gamma (bullish)
- **Red bars left** = put gamma (bearish)
- **Major positive gamma** = biggest green = ceiling/resistance
- **Major negative gamma** = biggest red = floor/support
- **Zero gamma** = the dividing line, in the middle
- Side panel: **net GEX** and the **max-change** readings

Two readings of every level: **by open interest** and **by volume**.

> At 00:01:09 he says plainly that **the volume reading is the one they
> track**. At 00:43:24 he confirms Classic *"calculates gamma by netting out
> calls and put volume at each strike."*

**This contradicts the Chart Fanatics episode**, where he says he reads
*"90-day open interest"* at 09:30. See §6 — it is the one genuine conflict
between the two sources and it is not resolved by either.

---

## 2. The two core trades

Simple and symmetric:

| | Trade |
|---|---|
| **At major positive gamma** | **Sell.** Ceiling. If already long, take profit here. |
| **At major negative gamma** | **Buy.** Floor. If already short, take profit here. |

*"Don't sell in the middle here — just wait for the price to reach these
important and critical levels."*

The mechanism matches the Chart Fanatics explanation but he names it
precisely: **gamma 25 / gamma 50** (i.e. 25-delta and 50-delta). An option's
value appreciates most steeply between 0 and 50 delta; past that the payoff
flattens. So the options desk takes profit at the 25/50 gamma level, because
beyond it returns diminish *and* theta is eating them. Their liquidation
forces the market maker to unwind his futures hedge — that unwind is the
move.

Two groups buy at the major negative level, which is why it reacts: the
options traders taking profit, **and** other sophisticated traders who watch
the same level.

---

## 3. Zero gamma — the regime filter

The most developed idea in the video, and the piece missing from the Chart
Fanatics episode.

He explicitly analogises zero gamma to the **volume-profile POC**: it is
where buyers and sellers are in balance, so **you do not trade there**.

- **Price above zero gamma** → positive/bullish regime
- **Price below zero gamma** → negative/bearish regime
- **A cross of zero gamma** = regime change, and a trade in that direction,
  with the stop just the other side of the zero-gamma line.

**Clustering.** When the zero-gamma line plots as a clean line, one side has
won. When it plots as a "cloud" or cluster — jittering up and down — the
battle is live. Rules:

- **Do not enter during clustering.**
- Clustering signals that control is *shifting*.
- After it resolves, price tends to take a clear direction — that's the
  trade.

---

## 4. The bad-trade filter (the most actionable rule)

This is his stated answer to "how do you avoid bad trades", and it's a clean
three-condition regime gate:

**If net GEX is negative AND the max-change readings are red AND price is
below zero gamma:**
→ **take no longs**, anywhere — *except* at the major negative gamma level.

**If net GEX is positive AND max-change is green AND price is above zero
gamma:**
→ **take no shorts**, anywhere — *except* at the major positive gamma level.

*"If you try to sell in any other level... you would take a little bit
profit, maybe a stop out, a little bit profit, a stop out."*

## 5. Entry confirmation via max-change

The max-change panel shows the largest gamma change over the last **1, 5,
10, 15 and 30 minutes**. He uses it as a trigger confirmation:

- Buying at major negative gamma → **want max-change to flip positive**
  (options sellers are buying back).
- Selling at major positive gamma → **want max-change to flip negative**.

**Verified against the API.** Each strike row carries a `priors` array of
exactly **5** values — matching his 1/5/10/15/30 lookbacks — and those values
track the **volume** column, not OI (e.g. strike 7450: `gex_vol` -0.36,
`priors` all -0.36, while `gex_oi` is -3.79). The top-level `max_priors` is 6
× `[strike, change]` — the panel itself. This closes an open question from
Phase 1: `max_priors` is the max-change panel, and it is volume-based.

---

## 6. Level migration

Same observation as Chart Fanatics, but here with a rule attached.

If price reaches the major negative gamma and instead of bouncing **the
level itself shifts lower**, that is a continuation signal, not a failed
trade. His response: don't chase. Wait for price to retrace and **test zero
gamma**, then enter short there. If it never retests, there's no trade.

He also uses the relative size of the profile as a confidence read — if the
red side is visibly bigger than the green while price is falling, expect the
major negative target to be reached.

---

## 7. Timing and theta

Time is a first-class input, not an afterthought:

- A level hit at 10:00-11:00 is **not** the same trade as the same level hit
  at 15:00. 0DTE options have an hour left at 15:00 and theta is brutal.
- Targets get progressively less reachable as expiry approaches — if price
  hasn't reached the level by ~15:00, take what's there.
- He is typically done before 11:00 ET.

## 8. Instrument and expiry selection

- **Trading ES → follow SPX. Trading NQ → he still keeps his Classic on
  SPX**, because SPX is the hedging instrument for institutions and gives
  the cleaner profile and better targets. The platform can convert SPX to ES
  prices.
- The UI offers three expiry selections: **90 days, 0DTE, and 1DTE**. He
  watches 0DTE primarily and toggles to 1DTE during the day to see where
  those traders are positioned. He notes 90-day and 0DTE *"might give you
  more or less the same profile."*

> **This resolves the Phase 1 blocker.** "90-day" is an *expiry selector in
> the UI*, not an OI lookback window. It maps to the API's three scopes:
> `zero` = 0DTE, `one` = 1DTE, **`full` = the 90-day view**. Worth confirming
> by comparing profiles, but the mapping is now clear.

---

## 9. How Classic is computed

Useful for knowing what we can and can't reproduce:

> Nets **call and put volume at each strike**, then applies **spline
> interpolation** to build a smooth "curve of dominance". Crossover points on
> that curve reveal which side has control.

The interpolated curve is computed server-side and is not exposed in the API
payload — we get the levels it produces, not the curve.

---

## 10. Trade management

- Scale out: take profits on part, leave runners.
- Stops beyond the zero-gamma line, or below the structure at the level.
- Targets: the opposite major gamma level, or the zero-gamma line for a
  runner.
- Expect 1-2 quality trades a day, often done before 11:00 ET.
- Missed the move? Don't chase — wait for the major level and take the
  reversal instead.

---

## 11. Caveats

- **Same self-reported-performance problem.** *"Nine out of ten times you're
  going to have a winning position, I promise, that's the statistics"* — no
  statistics are shown. This is a promotional video for a product he is
  affiliated with, walking through hand-picked days (7, 10, 12 March 2025).
- **The examples are all winners**, annotated after the fact.
- **The volume-vs-OI conflict with the Chart Fanatics episode is real and
  unresolved.** This video says volume; the later one says 90-day OI. Live
  data shows why it matters: at one sample `sum_gex_vol` was **+311,384**
  while `sum_gex_oi` was **-5,669** — opposite signs, opposite regime calls.
  The two readings also disagreed on wall placement (`major_pos_oi` 7715 vs
  `major_pos_vol` 7720). **This must be settled before anything is built.**
- The spline/curve-of-dominance is proprietary and not reproducible from the
  API payload.
