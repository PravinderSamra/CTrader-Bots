# Gold — Spot, Futures and Options Data

Investigation date: 2026-08-01. All endpoints below were tested live from this
environment unless marked otherwise.

**Headline: gold is a much better instrument for this than an index CFD.** For
UK100 the honest conclusion was "there is no free order flow". For gold there is
real traded volume, real committed options size, and real positioning data — all
free. What there still isn't is a live order book.

---

## 1. What's available, tested

| Layer | Source | Status | What you get |
|---|---|---|---|
| **Spot XAUUSD** | cTrader MCP | ✅ working | M1/H1 OHLCV. Volume is tick count — see doc 02 §4. |
| **Futures OHLCV + real volume** | Yahoo `GC=F` | ✅ **2.76M contracts over 30d** | Hourly bars with genuine COMEX contract volume |
| **Micro gold** | Yahoo `MGC=F` | ✅ working | Same price, retail-sized contract |
| **Options chain** | CBOE `delayed_quotes/GLD.json` | ✅ **7,672 contracts** | OI, volume, IV **and greeks incl. gamma** |
| **Positioning** | CFTC Socrata `72hh-3qpy` | ✅ working | Weekly COMEX gold COT, disaggregated |
| Options on GC futures (OG) | CME public endpoints | ❌ **403 from here** | Would be better than GLD — see §5 |
| Yahoo options | `v7/finance/options` | ❌ **401** | Now requires cookie+crumb. CBOE is better anyway. |
| Futures L2 depth | Databento `GLBX.MDP3` | 💰 $125 credit then paid | Real COMEX order book |

---

## 2. The finding that matters most — the basis is not constant

This is the thing that will silently ruin a futures-derived level if you don't
handle it.

GC trades at a premium to spot (carry: rates + storage). That premium **decays to
zero as the contract approaches expiry, then jumps when the front month rolls**.
Measured hourly against XAUUSD over 30 days:

| Date | Median basis (GC − spot) |
|---|---|
| 2026-07-03 | +12.74 |
| 2026-07-14 | +6.67 |
| 2026-07-23 | +2.78 |
| 2026-07-28 | +0.07 |
| **2026-07-29** | **+58.27** ← roll |
| 2026-07-31 | +56.62 |

Two consequences:

1. **A fixed offset is wrong.** Anyone overlaying a GC volume profile onto an
   XAUUSD chart with "futures ≈ spot" would have been right on 28 July and 58
   points wrong on 29 July. On gold that is the difference between a valid level
   and a stop that never had a chance.
2. **A single *current* offset is also wrong** for anything historical. A 30-day
   volume profile spans the roll, so pre-roll volume must be converted at the
   pre-roll basis.

`gold_context.py` measures the basis from overlapping hourly bars every run,
flags the roll when the day-over-day step exceeds 15 points, and converts **each
futures bar at that day's basis** before building the profile. The difference is
not academic: the POC came out at 4,014.77 with a single current offset, and
4,047.37 done properly — 33 points, right where price actually is.

GC roll months are Feb/Apr/Jun/Aug/Oct/Dec, so expect this roughly every two
months. The tool will tell you when it happens.

---

## 3. Real volume profile — the biggest upgrade over a CFD

`GC=F` hourly bars carry actual traded contract volume — 2,757,533 contracts over
30 days in the test run. That supports a genuine volume profile: POC, value area,
HVN and LVN computed from volume that really transacted, rather than from quote
updates.

This is the closest free thing to the question "is there real business at this
level". A pivot sitting on an HVN will grind and chop; one sitting on an LVN will
run once it goes. That is directly actionable for stop and target placement.

**Caveat on precision.** Each bar's volume is spread evenly across its high–low
range, because OHLCV can't say where inside the bar it traded. Node placement is
good to about a bar's range, not to the tick. True per-price volume would need
tick or footprint data (Databento).

**Caveat on what it isn't.** This is volume, not *delta*. It says how much traded
at a price, not whether buyers or sellers were the aggressor. Free data does not
classify gold aggressors anywhere.

---

## 4. Options — where size is actually committed

CBOE publishes the full delayed GLD chain free, with greeks already computed, so
no Black-Scholes and no scipy needed. 7,672 contracts in the test pull.

Two readings come out of it:

**Open interest by strike** — where contracts are actually held. Large OI acts as
a magnet into expiry and a shelf on the way through, because dealers hedging those
positions trade against price near the strike. In the test run, with spot at
4,046: a 4,233-contract put wall at 4,033 spot just underneath, and call walls at
4,088 (3,365) and 4,142 (4,794).

**Net dealer gamma** — sign matters more than magnitude:

- **Positive** (test run: +30.4M per 1% move): dealers hedge *against* price.
  Expect pinning and mean reversion — levels hold more, breakouts fail more. A
  good regime for fading your pivots.
- **Negative**: dealers hedge *with* price. Expect acceleration — levels break
  more easily. Fading is more dangerous; favour break-and-retest.

The **gamma flip** (where cumulative net gamma crosses zero, 4,142 in the test
run) marks where that regime changes.

### The GLD ratio — second calibration trap

GLD holds a decaying quantity of gold per share (0.4% expense ratio), so
spot/GLD drifts upward over time. Measured from 144 overlapping hours on
2026-08-01: **10.9008**.

The existing `GEX&OI/agent_skill/data_fetchers/yfinance_options.py` in this repo
hardcodes `MULTIPLIER = {"XAUUSD": 10}`. At GLD 371.54 that maps to 3,715 spot
instead of 4,050 — **335 points out**. It was flagged in that file's own comment
as approximate, but at today's gold price the approximation has broken down badly.
Worth fixing there too; `gold_context.py` measures it live.

---

## 5. What would be better, and why it's not here

**Options on COMEX gold futures (OG)** are the right instrument rather than GLD:
strikes sit directly on the futures price (no ETF ratio), and it is the same
underlying the volume profile comes from. CME publishes daily volume and open
interest by strike free.

Every CME endpoint tried returned **HTTP 403** from this environment — CME blocks
datacenter IPs. It will very likely work from your own machine. If you come to
lean on the options layer, that's the upgrade:

- Volume & OI reports: <https://www.cmegroup.com/market-data/volume-open-interest.html>
- Gold volume page: <https://www.cmegroup.com/markets/metals/precious/gold.volume.html>
- QuikStrike OI heatmap (free tools account): <https://www.cmegroup.com/tools-information/quikstrike/open-interest-heatmap.html>

Until then GLD is a legitimate proxy — it tracks gold tightly and its options
market is deep — it is just one translation step removed.

---

## 6. Does the DOM story change for gold?

Partly. Everything in doc 02 §2 still applies: cTrader Open API depth is real, the
MCP doesn't expose it, and XAUUSD is a CFD so the book is your broker's LP
aggregate rather than COMEX. `dom_recorder.py --probe` still answers whether it's
usable, and gold is one of the instruments it probes by default.

But for gold the DOM matters *less*, because the futures volume profile and the
options OI already answer "where is size committed" with better data than a CFD
book would. For UK100 the DOM was the only route to that question. For gold it's
a third opinion.

---

## 7. Practical stack for XAUUSD day trading

| Question | Tool | Data quality |
|---|---|---|
| How has this level behaved before? | `level_stats.py --symbol XAUUSD` | Real spot price history |
| Where did volume actually trade? | `gold_context.py` → volume profile | **Real COMEX contract volume** |
| Where is size committed? | `gold_context.py` → options OI | Real OI, GLD proxy |
| Pin or accelerate today? | `gold_context.py` → net gamma | Real greeks |
| Is spec positioning stretched? | `gold_context.py` → COT | Real, weekly |
| Is anyone resting size *right now*? | `dom_recorder.py --probe` first | Broker LP book, unproven |

Run `gold_context.py` once pre-session and `level_stats.py` weekly. The first
tells you which of your levels have a reason to hold; the second tells you whether
they historically have.

---

## Sources

- [Yahoo Finance chart API](https://query1.finance.yahoo.com/v8/finance/chart/GC=F) (`GC=F`, `MGC=F`, `GLD`)
- [CBOE delayed option quotes](https://cdn.cboe.com/api/global/delayed_quotes/options/GLD.json)
- [CFTC public reporting API](https://publicreporting.cftc.gov/resource/72hh-3qpy.json) — disaggregated COT
- [CME Volume & Open Interest reports](https://www.cmegroup.com/market-data/volume-open-interest.html)
- [CME Gold volume & OI](https://www.cmegroup.com/markets/metals/precious/gold.volume.html)
- [Databento GLBX.MDP3](https://databento.com/datasets/GLBX.MDP3)
