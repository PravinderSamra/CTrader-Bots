# Data Source Investigation — Can We Replace Bookmap For Free?

Investigation date: 2026-08-01. Account tested: Pepperstone UK GBP spread betting
(demo), plant `pepperstoneuk`, via the cTrader MCP endpoint and the public
cTrader Open API documentation.

---

## 1. What Bookmap actually consumes

Worth being precise, because it determines what a substitute needs.

Bookmap's heatmap is built from **Level 2 market-by-price data**: for every price
level, the quantity of *resting limit orders*, updated on every change. It stores
that history and draws it as price × time × brightness. Everything people
associate with Bookmap follows from that one feed:

| Bookmap feature | Underlying data |
|---|---|
| The heatmap itself | L2 depth snapshots over time |
| Iceberg detection | A level whose size keeps refilling after being hit |
| Absorption | Large resting size that gets traded into but does not disappear |
| Spoof detection | Large size that vanishes *before* price arrives |
| Volume dots / CVD | Separate **trade** feed with size and aggressor side |

Note the split. The first four need **depth**. The last one needs the **tape**
(executed trades, with which side was the aggressor). They are different feeds,
and — importantly for your question — they are available to different degrees.

Your specific question — *"are there more sellers than buyers at this level"* —
is a **depth** question. That is good news, because depth turns out to be the one
we can actually get.

---

## 2. Option A — cTrader Open API depth quotes ✅ **This is the answer**

**Verdict: viable, free, and the only route that gives genuine resting-liquidity
data for the exact instruments you trade at the exact prices you get filled at.**

The cTrader Open API exposes:

| Message | What it does |
|---|---|
| `ProtoOASubscribeDepthQuotesReq` | Subscribe to depth of market for a symbol |
| `ProtoOADepthEvent` | Fires whenever the book changes |
| `ProtoOAUnsubscribeDepthQuotesReq` | Stop |

`ProtoOADepthEvent` carries `newQuotes` (each a `ProtoOADepthQuote` with `id`,
`size`, and exactly one of `bid`/`ask`) and `deletedQuotes` (ids to remove). It is
an **incremental** feed — you maintain the book yourself by applying inserts and
deletes. Prices divide by 100,000; sizes divide by 100 to get units.

That is precisely the Bookmap input. Record it, and you can draw the same picture.
That is what `src/dom_recorder.py` and `src/heatmap_render.py` do.

### The catch you must test before relying on it

**The cTrader MCP server does not expose depth.** Its tool surface is
`get_symbols`, `get_spot_prices`, `get_trendbars`, plus orders/positions/deals —
confirmed by enumerating the live tool schemas this session. Depth is only
available on the **Open API protobuf endpoint** (`demo.ctraderapi.com:5035` /
`live.ctraderapi.com:5035`), which needs its own free app registration at
<https://openapi.ctrader.com/> for a Client ID + Secret and an OAuth access token.

**More importantly: Pepperstone is a CFD/spread-bet broker, not an exchange.**
The depth returned is its aggregated liquidity-provider book. In practice:

- FX pairs usually carry genuine multi-level depth.
- Index and commodity CFDs (UK100, US30, XAUUSD) are quoted by far fewer LPs and
  may return only one or two levels per side — or nothing.

I could not test this empirically from here (no Open API client credentials in
this environment — the `CTRADER_MCP_SLUG` token authenticates the MCP endpoint
only). **So `dom_recorder.py --probe` exists specifically to answer it**: it
subscribes to each of your instruments for 60 seconds and reports how many depth
events and levels each one actually delivered. Run that before building anything
on top of it. If UK100 returns one level per side, the heatmap will be thin and
you should lean on §7 and §8 instead.

Also worth internalising: even at its best, this is *your broker's available
liquidity*, not total market volume. That is not a weakness for your use case —
it is the size you can actually get filled against, and it is the book your stop
will be executed in — but it is not FTSE futures depth and should not be
described as such.

---

## 3. Option B — cTrader historical tick data ⚠️ Useful, but not delta

`ProtoOAGetTickDataReq` returns historical ticks for a symbol. Response is
`ProtoOATickData` with a delta-encoded timestamp (first tick absolute, the rest
are millisecond differences) and a price, with `hasMore` for chunked paging, and
a `type` parameter selecting **BID or ASK**.

**This is quote data, not trade data.** There is no size field and no aggressor
flag, because a CFD broker's feed has no consolidated tape to report. So:

- ✅ You can reconstruct sub-second price action, spread behaviour, and quote
  intensity around your levels far more precisely than M1 bars allow.
- ❌ You **cannot** compute true delta or CVD from it. Any "delta" built on this
  would be the tick rule applied to quotes, which is not the same thing and
  should not be presented as order flow.

Worth having for precision work. Not the answer to "who is bigger at this level".

---

## 4. Option C — cTrader bar volume ❌ It is tick volume

Confirmed empirically this session. UK100 M1 bars returned `volume` values of
80–190 per minute. FTSE 100 does not trade 120 contracts a minute at your broker —
these are **quote-update counts**. cTrader's own documentation is explicit:
"Tick volume is the number of ticks that occurred on a given trend bar, it's not
the real buy/sell volume."

I tested whether it is nonetheless *useful* as an absorption proxy, on the theory
that lots of ticks with no price progress = churn = absorption. Result, across two
instruments (see §8):

| Instrument | Efficiency on holds | On breaks | Separation |
|---|---|---|---|
| UK100, 193 touches | 4.274 | 4.515 | none (5%) |
| XAUUSD, 422 touches | 1.264 | 1.335 | none (5%) |

**Negative result, and it is a useful one.** Tick-volume efficiency does not
distinguish a level that holds from one that breaks. Do not build confidence on
it, and be sceptical of any indicator that claims to give you order flow from
cTrader bar volume — it is working from the same non-signal.

---

## 5. Option D — TradingView ❌ For this purpose

You have TradingView data, so it's worth stating clearly why it can't do this.

- Pine Script has **no access to the order book**. There is no DOM, no L2, no
  market-depth namespace. It cannot be scripted into a heatmap at any subscription tier.
- TradingView's own **Volume Footprint** charts exist on paid tiers, but only for
  instruments with real exchange volume (futures, equities) — and they render
  *trades*, not resting depth. They also cannot be exported or reached by API, so
  they can't feed an automated confluence layer.
- The CFD symbols you trade carry the same tick-volume limitation as §4.

TradingView remains the right place to *draw* your levels. It is not a source of
order flow data.

---

## 6. Option E — Where true order flow IS free (and why it doesn't help you)

Complete, genuine, free bid/ask aggressor data exists — in crypto. Binance klines
carry `takerBuyBaseAssetVolume` directly, so real delta and CVD are a subtraction
away, and Binance/Bybit/OKX all publish full order books over free WebSockets.
The existing `Order Flow System/` project in this repo already documents and
implements this.

It is genuinely Tier 1 data. It is also for BTC and ETH, which you do not trade.
Listing it for completeness, not as a recommendation.

**For your instruments** the true tape lives in the underlying futures — FTSE 100
futures on ICE for UK100, YM on CBOT for US30, GC on COMEX for XAUUSD — and that
data is not free:

| Route | Cost | Note |
|---|---|---|
| Databento (`GLBX.MDP3`) | $125 free credit, then usage-based | Full L2/L3 CME historical. Licensed distributor. Best for a **one-off validation study**. |
| Rithmic / Tradovate / CQG | ~$10–100/mo + exchange fees | Live futures L2 |
| Bookmap Global | $16–79/mo | The thing you're replacing |
| ICE FTSE futures depth | Expensive, licensed | Effectively closed to retail |

The Databento free credit is the interesting one — not as an ongoing feed, but as
a way to *check your premise once*: pull a few sessions of real CME depth around
equivalent levels and see whether resting-size imbalance genuinely predicts
rejection. If it doesn't there, it won't in a CFD book either.

---

## 7. Option F — Free correlated tape as a confluence layer ⚠️ Partial

Where a free feed with real trade sizes exists, it's for US equities:

| Source | Free tier | Coverage |
|---|---|---|
| **Finnhub** | Real-time trade WebSocket, 50 symbols, 60 calls/min | Real trades with size |
| **Alpaca** | Real-time WebSocket, IEX feed only | Real trades, but IEX is ~2% of consolidated volume |
| Polygon.io | Delayed on free tier | Not useful live |

This gives a genuine tape on **ETF proxies** — `SPY`/`DIA` for US30, `GLD` for
gold, `EWU`/`ISF.L` loosely for FTSE. Real sizes, real aggressor classification.

Caveats that matter: it only covers US cash hours (so nothing for your London
morning on UK100), the correlation is decent but not tight, and IEX-only depth
makes Alpaca's version noisy. Treat as a **confluence tiebreaker during the US
session**, never as the primary read.

---

## 8. Option G — What we can build from data you already have ✅ **Built**

The route that needs no new credentials at all, and the one I'd start with.

You do not strictly need to see the sellers to gain confidence at a level. You
need to know **what happened the last N times price did exactly this here**. That
is fully derivable from cTrader M1 + H1 bars, which the MCP already serves.

`src/level_stats.py` does this. It marks H1 pivots, clusters them into levels,
finds every discrete M1 visit to each, and measures how deep the wicks went,
whether price ever *closed* through, and what fading the level actually paid —
replayed bar by bar with the stop checked before the target, so it isn't inflated
by trades that would have been stopped out first.

**Verified working against the live account, 2026-08-01:**

| Instrument | M1 bars | Days | Levels | Touch events |
|---|---|---|---|---|
| UK100 | 11,931 | 10 trading days | 8 | 193 |
| XAUUSD | ~12,000 | 10 trading days | 10 | 422 |

This is what turns "I think this level is strong" into "this level has held 57%
of 14 tests, the wick goes 3.8 points through it at the 90th percentile, and
fading it has returned +1.57R". That is the confidence you asked for — it is just
sourced from history rather than from the live book.

### Implementation notes worth keeping

- `get_trendbars` **silently caps responses at 100 bars**, returning the *most
  recent* 100 of whatever range you ask for. Requesting 14 days of M1 in one call
  looks like it works and quietly gives you 100 minutes.
- Paging must distinguish a *truncated* response from an *exhausted* one. A window
  landing mostly in the overnight gap returns a single bar at `toTimestamp`;
  naively resuming from "oldest bar returned" makes no progress and the walk
  stalls. Rule: if the response is full, resume at the oldest bar; if it's short,
  you already have everything in that window, so jump the whole window.
- `fromTimestamp`/`toTimestamp` must be passed as **strings**; integers are rejected.

---

## 9. Option H — Platforms that could do it off the shelf

| Platform | Cost | Verdict |
|---|---|---|
| **Quantower** | Free tier exists; **footprint/DOM-surface/volume analysis are paid** | Connects to cTrader, but the free tier deliberately excludes the order-flow tools — which are the whole reason you'd use it |
| ATAS | ~$85/mo | Full footprint, limited free tier |
| Sierra Chart | ~$36/mo + feed | Best value for real order flow, needs a real data feed |
| Bookmap | $16–79/mo | Free tier is crypto-only |

Quantower looked like the obvious free win and isn't. Worth knowing before you
spend an evening on it.

---

## 10. Summary

| Option | Free? | Gives real resting liquidity? | Verdict |
|---|---|---|---|
| cTrader Open API depth | ✅ | ✅ (broker LP book — **probe first**) | **Primary route** |
| cTrader statistical level study | ✅ | ❌ (historical behaviour instead) | **Build first — done** |
| cTrader tick data | ✅ | ❌ quotes only, no size | Precision work only |
| cTrader bar volume | ✅ | ❌ tick counts | Tested, no signal |
| TradingView | — | ❌ no book access at any tier | Draw levels only |
| Crypto exchange APIs | ✅ | ✅ but wrong market | N/A |
| Futures L2 (Databento) | $125 credit | ✅ genuinely | One-off validation study |
| Finnhub / Alpaca ETF tape | ✅ | Trades, not depth; US hours | US-session tiebreaker |
| Quantower free | ✅ | ❌ order flow tools are paid | Dead end |

**The plan that follows from this:** run `level_stats.py` now — it works today and
gives you evidence-based stops and expectancy per level. In parallel, register a
cTrader Open API app and run `dom_recorder.py --probe` to find out whether your
instruments carry real depth. If they do, the heatmap layer is a weekend's work
and you have your Bookmap substitute. If they don't, you have lost an hour and
still have the statistical layer, which is the part that most directly answers
"should I be confident taking this short".

---

## Sources

- [cTrader Open API — Messages](https://help.ctrader.com/open-api/messages/)
- [cTrader Open API — Model messages](https://help.ctrader.com/open-api/model-messages/)
- [cTrader — Depth of Market](https://help.ctrader.com/trading-with-ctrader/depth-of-market/)
- [cTrader — Tick Volume indicator](https://help.ctrader.com/knowledge-base/indicators/volume/tick-volume/)
- [cTrader Open API portal](https://openapi.ctrader.com/)
- [Pepperstone cTrader platform](https://pepperstone.com/en-gb/platforms/ctrader)
- [Databento — CME Globex MDP 3.0](https://databento.com/datasets/GLBX.MDP3) · [pricing](https://databento.com/pricing)
- [Finnhub pricing](https://finnhub.io/pricing)
- [Alpaca market data](https://docs.alpaca.markets/us/docs/about-market-data-api)
- [Quantower volume analysis tools](https://www.quantower.com/volumeanalysistools)
- [Gala's price action strategy write-up](https://www.tradezella.com/strategies/price-action-strategy)
