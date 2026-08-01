# Gala Heatmap

Confluence data for the hourly-pivot / 1-minute-reaction strategy — replacing
what a Bookmap heatmap would tell you, using free data and the cTrader account
you already have.

**The question:** price returns to a marked H1 pivot and starts wicking through
it without breaking. Are those wicks sellers absorbing buyers, or noise before a
breakout? And where does the stop actually belong?

---

## The short answer

Two separate things can resolve this, and only one of them needs an order book.

**1. Historical evidence — built, verified, works today.**
What happened the last N times price did exactly this, at this level? That is
fully derivable from cTrader M1 + H1 bars via the MCP you already use. It gives
you a hold rate, an empirically-sized stop, and a realistic expectancy per level.

**2. Live resting liquidity — the real heatmap, needs one free registration.**
cTrader's **Open API** exposes `ProtoOASubscribeDepthQuotesReq` /
`ProtoOADepthEvent` — genuine Level 2 depth from your broker's LP book. That is
the same input Bookmap renders. The cTrader *MCP* server does not expose it, so
this needs a free app registration at <https://openapi.ctrader.com/>.

The catch is honest and important: Pepperstone is a CFD broker, not an exchange,
and index/commodity CFDs may return very thin depth. **Probe before you build on
it** — there's a tool for exactly that.

Everything else that looked promising was investigated and ruled out. Notably:
**cTrader bar volume is tick volume** (quote-update counts, not contracts), and
tested across 615 touch events on two instruments it carries **no signal**
separating levels that hold from levels that break. Full write-up in
[`research/02-DATA-SOURCE-INVESTIGATION.md`](research/02-DATA-SOURCE-INVESTIGATION.md).

---

## What's here

```
Gala Heatmap/
├── research/
│   ├── 01-THE-STRATEGY.md              the setup, and what confluence must prove
│   ├── 02-DATA-SOURCE-INVESTIGATION.md every option tested, with verdicts
│   └── 03-CTRADER-OPENAPI-REFERENCE.md depth + tick API, and MCP gotchas
├── design/ARCHITECTURE.md              how the three layers fit together
├── src/
│   ├── ctrader_http.py                 MCP client with correct trendbar paging
│   ├── pivots.py                       H1 pivot detection + level clustering
│   ├── level_stats.py                  ← the engine that works today
│   ├── dom_recorder.py                 Open API depth recorder (needs app reg)
│   └── heatmap_render.py               depth → HTML heatmap + level report
└── reports/                            generated output
```

---

## Layer 1 — run this now

No new credentials. Uses `CTRADER_MCP_SLUG`, same as your other projects.

```bash
python3 "Gala Heatmap/src/level_stats.py" --symbol UK100 --days 14
python3 "Gala Heatmap/src/level_stats.py" --symbol XAUUSD --days 14
python3 "Gala Heatmap/src/level_stats.py" --symbol UK100 --near 10880   # just levels near price
```

Takes a few minutes — M1 paging is the slow part. Writes to `reports/`.

**Verified against the live account, 2026-08-01:** UK100 gave 11,931 M1 bars over
10 trading days → 8 levels, 193 touch events. XAUUSD gave 422 touch events across
10 levels.

### What it tells you

```
| Level      | Kind       | H1 pivots | Touches | Held | Win rate | Expectancy | Stop (pts) |
|------------|------------|-----------|---------|------|----------|------------|------------|
| 10,870.70  | support    | 2         | 32      | 62%  | 50%      | +0.97R     | 6.10       |
| 10,911.00  | resistance | 3         | 36      | 64%  | 28%      | +0.07R     | 6.70       |
| 10,818.94  | both       | 5         | 21      | 76%  | 76%      | +2.05R     | 5.74       |
| 10,754.52  | both       | 4         | 15      | 87%  | 93%      | +2.73R     | 3.80       |
```

Read that fourth row: 10,754.52 has been tested 15 times, held 87% of them, the
wick goes 3.8 points through at the 90th percentile, and fading it returned
+2.73R. That is a level to take seriously. Row two — 10,911.00 — holds 64% of the
time but only wins 28% and returns +0.07R, because when it does break it goes.
Same-looking level on a chart, completely different trade.

**Every R figure is a path-dependent replay** with the stop checked before the
target, and the stop assumed hit first within a bar. It is not inflated by trades
that would have been stopped out before reaching the target.

The report also breaks results down by **day bias** (bearish/bullish, measured at
the moment of each touch) and by **session**, since both are stated parts of the
strategy and deserve measuring rather than assuming.

---

## Layer 2 — the actual heatmap

One-off setup, free:

1. Register an app at <https://openapi.ctrader.com/> → Client ID + Secret
2. Complete the OAuth flow for the Pepperstone account → Access Token
3. ```bash
   pip install ctrader-open-api twisted
   export CTRADER_OA_CLIENT_ID=... CTRADER_OA_CLIENT_SECRET=... CTRADER_OA_ACCESS_TOKEN=...
   ```

**Probe first — this is the step that decides whether the rest is worth doing:**

```bash
python3 "Gala Heatmap/src/dom_recorder.py" --probe
```

It subscribes to each of your instruments for 60 seconds and reports how many
depth events and levels each actually delivered. If UK100 comes back with one
level per side, the heatmap will be thin and Layer 1 is where your effort should
go. If it comes back with real depth, carry on:

```bash
python3 "Gala Heatmap/src/dom_recorder.py" --symbol-id 113 --minutes 120 --out data/uk100-dom.jsonl
python3 "Gala Heatmap/src/heatmap_render.py" --in data/uk100-dom.jsonl --level 10911 --band 5
```

You get a self-contained HTML heatmap plus the number you actually wanted:

```
RESTING LIQUIDITY AROUND 10,911.00  (±5 pts, 900 snapshots)
  Average resting BID size (buyers) :       13.2
  Average resting ASK size (sellers):      217.7
  → sellers outweigh buyers 16.45 : 1  (94% of size is on the offer)

  READ: supply-heavy. Consistent with wicks being absorbed and price
        failing to break. Supports a short from the level.
```

The renderer is verified end to end via `--selftest`, which draws a clearly
labelled synthetic book (a wall of offers that price tests three times and fails
to break) so the rendering path can be checked without waiting for a live
session. See `reports/selftest-heatmap.html`. **That file is synthetic and
labelled as such — it is not market data.**

---

## What this is not

- **Not tick-volume delta.** cTrader bar `volume` is quote-update counts. Any
  "CVD" built from it is fiction; measured, it separates holds from breaks by 5%,
  i.e. not at all.
- **Not exchange depth.** Layer 2 shows your broker's LP liquidity. For sizing a
  stop that's arguably the more relevant number — it's the book you get filled in
  — but a level thin in Pepperstone's book may be thick in FTSE futures.
- **Not a prediction.** "Held 24 of 32" means it breaks often. The value is in
  selection and sizing, not certainty.

Every generated report states which tier its numbers come from.

---

## Related work in this repo

- `Order Flow System/` — the Stage 1–3 order flow research this builds on;
  Stage 3's data-tier honesty model is reused here directly.
- `ctrader-mcp-integration-guide.md` — MCP connection patterns (the keep-alive
  lesson in particular). `research/03-CTRADER-OPENAPI-REFERENCE.md` extends it to
  the Open API and adds the trendbar paging gotchas found here.
- `ICT-SMC-Local-Agent/ctrader_http_fetch.py` — the fetch pattern `ctrader_http.py`
  is adapted from.
