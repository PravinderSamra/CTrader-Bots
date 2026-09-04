# Strategy synthesis — Freddy Siento's gamma-level model

Combines both sources into one specification, with the parts we can build
separated from the parts still unresolved.

**Sources**
- [Master Gexbot Classic](gexfuture-master-gexbot-classic.md) — GexFuture Trading, 2025-03-16, 49min. The operational one.
- [Chart Fanatics interview](chart-fanatics-freddy-siento.md) — 2026-08-23, 2h30m. The explanatory one.

Where they conflict, §5 says so rather than picking a winner.

---

## 1. The thesis in one paragraph

Institutions are forced to hedge with options. Market makers must take the
other side and hedge their resulting risk in the futures market. That
hedging flow is a large part of what moves index futures intraday. At the
largest gamma strike, the institution's option stops appreciating (past
50-delta the payoff flattens) while theta accelerates — so they take profit.
Their liquidation leaves the market maker holding a futures hedge he no
longer needs, and he must dump it. **That forced unwind is the trade.** The
level is not resistance; it is where the dealer is compelled to reverse.

---

## 2. Setup

| Parameter | Value |
|---|---|
| **Level source** | SPX (institutional hedging instrument, cleanest profile) |
| **Execution** | NQ futures (or ES). Platform converts strikes to futures prices |
| **Our symbol** | `NQ_NDX` — futures-basis, correct for NAS100 CFD |
| **Expiry scope** | 0DTE primary; toggle 1DTE intraday. (`zero` / `one`) |
| **Chart** | 1-minute (occasionally 5-minute) |
| **Session** | First two hours ET; usually finished by 11:00 |
| **Frequency** | 1-2 trades/day, sometimes none |

## 3. The levels

| Level | API field | Role |
|---|---|---|
| Major positive gamma (call wall) | `major_pos_vol` / `major_pos_oi` | Ceiling — **sell** here |
| Major negative gamma (put wall) | `major_neg_vol` / `major_neg_oi` | Floor — **buy** here |
| Zero gamma | `zero_gamma` | Regime divider — **never trade here** |
| Net GEX | `sum_gex_vol` / `sum_gex_oi` | Regime direction |
| Max-change panel | `max_priors`, per-strike `priors` | 1/5/10/15/30-min gamma change |

Only the **single largest** level is an entry. Secondary large levels are
**targets**.

---

## 4. The rules

### 4.1 Regime gate (check first — this is the filter that kills bad trades)

```
IF net GEX < 0 AND max-change readings red AND price < zero gamma:
    NO LONGS  — except at major negative gamma
IF net GEX > 0 AND max-change readings green AND price > zero gamma:
    NO SHORTS — except at major positive gamma
```

### 4.2 Zero gamma state

- Clean line → one side has won; regime is the side price sits on.
- **Clustering / "cloud"** → battle live. **No entries.** Control is
  shifting; wait for resolution, then trade the direction that emerges.
- Cross of zero gamma → regime change; trade that direction, stop just the
  other side of the line.

### 4.3 Entry at a major level

1. Price reaches the largest positive (short) or negative (long) gamma level.
2. **Slope rule** — how it arrives decides the entry:
   - **Fast/steep** → expect it to punch through. Wait for the level to be
     **reclaimed**, then enter.
   - **Slow/gentle** → expect it to hold. Take the level directly.
3. **Max-change confirmation**: long at major negative wants max-change
   flipping **positive**; short at major positive wants it flipping
   **negative**.
4. Direction is set by which side you approach from — these are **reversal**
   points.

### 4.4 Risk and management

- Stop **30-50 ticks** NQ, placed structurally (beyond the swing formed at
  the level, or beyond zero gamma).
- Rationale: the dealer hedge is fast. If the level is going to work it works
  immediately; if it doesn't move, something unseen is happening — get out.
- Scale out; leave a runner.
- Target the next major gamma level, or zero gamma for the runner.

### 4.5 Time

- A level at 10:00 ≠ the same level at 15:00. Theta accelerates from midday.
- After ~15:00, targets are progressively less reachable — take what's there.
- Missed the move? Don't chase. Wait for the major level and take the
  reversal.

### 4.6 When the level fails

It usually fails because another institution has positioned further out and
is magnetising price. Levels also migrate intraday (a put wall moving
5550 → 5530).

- **Do not chase.** A level shifting *away* is a continuation signal.
- Wait for price to retest **zero gamma** and enter there, or wait for the
  new largest level.

---

## 5. Unresolved: volume vs open interest

The single most important open question, and the two sources disagree.

| Source | Says |
|---|---|
| Master Gexbot Classic (2025) | *"The one by volume is the one we are tracking"*; Classic nets **call and put volume** per strike |
| Chart Fanatics (2026) | *"I'm looking into the 90-day open interest"* — to see how the whole market is positioned for the day |

**Why it matters — from live data, 2026-09-04 20:00 UTC:**

```
sum_gex_vol  = +311,384      sum_gex_oi   =  -5,669     <- opposite signs
major_pos_vol=    7720       major_pos_oi =    7715
major_neg_vol=    7710       major_neg_oi =    7720
```

The two readings gave **opposite regime calls** and disagreed on wall
placement. A system built on the wrong one is not a slightly worse system,
it is an inverted one.

**Most likely reconciliation** (untested): OI answers *"where is the market
positioned for today"* — a pre-open, structural read, which is what he
describes at 09:30 in the interview. Volume answers *"what is happening
now"* — the intraday read, which is what the Classic screen and the
max-change panel track. They are complementary rather than contradictory,
and he may simply have been describing different moments.

Supporting evidence for the volume side: the per-strike `priors` series
tracks the `gex_vol` column, so the max-change panel — which he uses for
entry confirmation — is definitively volume-based.

**Resolve before building anything.**

---

## 6. What we can build today

Our **Classic** token covers the entire primary model. Nothing here needs an
upgrade:

- ✅ Major positive / negative gamma levels (both readings)
- ✅ Zero gamma
- ✅ Net GEX
- ✅ Max-change panel (`max_priors`, per-strike `priors`)
- ✅ `NQ_NDX` / `ES_SPX` futures-basis symbols
- ✅ 0DTE / 1DTE / 90-day scopes (`zero` / `one` / `full`)

Not available on Classic, and not required by this model:

- ❌ Per-strike delta/gamma/vanna/charm (State) — needed only for his
  secondary *convexity* model
- ❌ Orderflow, historical download, WebSocket

Not obtainable at all: the spline "curve of dominance" is computed
server-side and only its outputs are exposed.

---

## 7. What to verify before trusting any of it

1. **Settle volume vs OI** (§5).
2. **Confirm `full` = the 90-day UI view** by comparing profiles.
3. **Measure the RTH refresh cadence** — determines whether this can drive
   intraday entries or only level marking.
4. **Backtest the core claim**: does price reverse at the largest gamma level
   in the first two hours, often enough to matter?
5. **Quantify the slope rule** — it is the one discretionary element and
   needs a numeric definition.
6. **Define "clustering"** numerically from the `zero_gamma` time series.
7. **Cross-check against the existing CBOE pipeline** in `GEX&OI/`.

## 8. Health warning

Both sources are promotional. The 75% win rate, the 1:10 reward:risk, "nine
out of ten times", and "a stop every two or three weeks" are **all
self-reported**, illustrated with hand-picked winning days, by someone
affiliated with the product. No statistics are shown in either video.

The *mechanism* (§1) is standard dealer-hedging theory and is sound and
independently checkable. The *edge numbers* are not evidence. Treat the
rules above as a well-specified hypothesis to test, not a validated system.
