# Architecture

Four layers, deliberately independent. Each is useful alone, and the ones that
work today do not depend on the one that needs a probe result. Layers 1–3 apply to
any instrument; Layer 4 exists because gold has data an index CFD does not.

```
┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 1 — LEVELS            (works today, no new credentials)       │
│  pivots.py                                                           │
│  H1 bars ─▶ fractal swing pivots ─▶ price clustering ─▶ levels       │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│  LAYER 2 — HISTORICAL EVIDENCE   (works today · BUILT & VERIFIED)    │
│  level_stats.py                                                      │
│  M1 bars ─▶ touch events ─▶ path-dependent replay ─▶ per-level stats │
│  Answers: how often does it hold · how deep do the wicks go          │
│           (⇒ your stop) · what has fading it actually paid           │
└───────────────────────────────┬──────────────────────────────────────┘
                                │
┌───────────────────────────────▼──────────────────────────────────────┐
│  LAYER 3 — LIVE RESTING LIQUIDITY   (needs Open API app + probe)     │
│  dom_recorder.py ─▶ JSONL snapshots ─▶ heatmap_render.py             │
│  Answers: is there size resting there RIGHT NOW, and on which side   │
└──────────────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────────────┐
│  LAYER 4 — GOLD ONLY: REAL VOLUME & COMMITTED SIZE   (works today)   │
│  gold_context.py                                                     │
│  GC=F volume ──┐                                                     │
│  GLD options ──┼─▶ basis / ratio calibration ─▶ all mapped to XAUUSD │
│  CFTC COT    ──┘                                                     │
│  Answers: where did volume really trade · where is size committed ·  │
│           is today a pinning or a trending regime                    │
└──────────────────────────────────────────────────────────────────────┘
```

Layer 4 is instrument-specific and only exists because gold has data an index CFD
doesn't. It runs independently of Layers 1–3 and needs no new credentials.

---

## Layer 1 — Levels (`pivots.py`)

Fractal detection on H1: a bar is a pivot high if its high is ≥ the highs of
`strength` bars either side. `strength=3` approximates what a person marks by
hand; 2 gives many more levels, 4 gives only the obvious ones.

Pivots are then **clustered by price** — several swings at effectively the same
price are one level, because that is how price treats them. Greedy single-linkage
with tolerance expressed as a fraction of price, so the same setting works across
UK100, XAUUSD and US30.

Deliberately *not* modelled: candle-body and open-based levels, which the Gala
method also uses. Worth adding as a second detector — see Extensions.

## Layer 2 — Historical evidence (`level_stats.py`)

The layer that does the real work.

**Touch events.** Walk M1 bars, flag every bar whose range intersects a band
around the level, group consecutive flags into runs (tolerating gaps of up to 3
bars so one visit isn't split into five). Determine approach direction by looking
back for the last bar that closed clearly outside the band — that decides whether
this is a resistance test or a support test, independently of how the level was
originally classified. Levels flip; the analysis has to allow for it.

**Break definition.** A break requires **two consecutive closes** beyond the level
by more than the break buffer. One spike through is a wick, which is the entire
phenomenon being studied — defining it as a break would assume away the question.

**Path-dependent replay.** This is the part that matters for honesty. For each
visit: enter at the level, stop at `stop_dist` beyond it, then walk forward bar by
bar. The stop is checked **before** the target, and within a bar the stop is
assumed hit first — pessimistic, and the only defensible choice when M1 OHLC
doesn't reveal the intrabar path.

The alternative — measuring best-case and worst-case excursion independently — is
the standard way to make a mediocre level look like a goldmine. The first version
of this tool did exactly that and reported setups at "48R". Everything downstream
of that number would have been fiction.

**Stop distance is derived, not assumed.** `stop_dist` = the 90th percentile of
wick-through across visits that did not break — the empirical version of "just
beyond the deepest wick". Clamped below by the touch band (a stop inside your own
level gets hit by noise) and above by 6× it (past that it's a different trade).

**Conditioning.** Results are broken out by day bias (price vs that day's open at
the moment of the touch) and by session, because "on a bearish day" is a stated
part of the strategy and deserves to be measured rather than assumed.

## Layer 3 — Live resting liquidity (`dom_recorder.py`, `heatmap_render.py`)

`ProtoOASubscribeDepthQuotesReq` → `ProtoOADepthEvent` is an **incremental** feed:
apply `deletedQuotes` then `newQuotes` against a local `id → (side, price, size)`
map, and snapshot your own copy on a timer (default 250 ms) to JSONL. Aggregate
by price when snapshotting — multiple LPs quote the same level.

The renderer bins snapshots into a price × time grid, shades bids blue and offers
orange, draws the mid-price track over the top, and prints the number that
actually answers the question:

```
Average resting BID size (buyers) :  13.2
Average resting ASK size (sellers): 217.7
→ sellers outweigh buyers 16.45 : 1  (94% of size is on the offer)
```

Output is a single self-contained HTML file — no CDN, no build step.

**Gated on a probe.** Whether Pepperstone delivers usable depth on index CFDs is
an empirical question that could not be answered from this environment. Run
`dom_recorder.py --probe` first. Building Layer 3 analytics before knowing the
answer would be building on an assumption.

---

## Layer 4 — Gold context (`gold_context.py`)

Three independent sources, each priced in something other than XAUUSD spot. The
architecture is mostly about getting the translations right, because they are
larger and less stable than they look.

**Basis, measured not assumed.** GC-minus-spot is computed from overlapping hourly
bars every run. It decays to zero into contract expiry and steps ~58 points at the
roll, so a fixed constant is wrong twice over: wrong now, and wrong differently for
historical bars. A roll is flagged when the day-over-day step exceeds 15 points.

**Per-bar conversion.** The volume profile is built from futures bars each
converted at *that day's* basis, so a lookback spanning a roll still lands volume
at the right spot price. This is the single most important correctness decision in
the module — with a single current offset the POC was 33 points off.

**Ratio, measured not assumed.** spot/GLD is calibrated from overlapping hours
(10.9008 on 2026-08-01) rather than the conventional 10, which is now 335 points wrong.

**Greeks come from CBOE**, so there is no Black-Scholes and no scipy dependency —
the whole module is stdlib-only. GEX convention matches `GEX&OI/agent_skill`
(net = call GEX − put GEX) so the two projects agree.

**Expired series are filtered.** CBOE keeps just-expired contracts in the file;
including them would put dead open interest on the board as live positioning.

## Data honesty model

Carried over from `Order Flow System/Stage3_Architecture.md`, which established
the same tiering for the earlier project.

| Tier | Meaning | Here |
|---|---|---|
| 1 | True order flow — real aggressor-classified trade volume | **Not available** for these instruments at any free price |
| 1− | Real traded volume — where business happened, but *not* aggressor-classified | Layer 4 futures volume profile (gold only) |
| 1− | Real committed size — open interest by strike | Layer 4 options (gold, via GLD proxy) |
| 2 | Structural / statistical — price behaviour | Layer 1 + 2 |
| 2.5 | Real resting liquidity, broker-scoped | Layer 3 (if the probe passes) |
| 3 | Confluence — supporting context | Session, day bias, COT positioning |

Gold reaches Tier 1− on two independent axes, which no index CFD does. That is the
substantive reason the answer for XAUUSD is better than the answer for UK100 — it
is not that the method is different, it is that the data exists.

Every report states its tier. The tick-efficiency "absorption proxy" is
explicitly reported as a proxy, and — as measured — as one that **does not
separate holds from breaks** on either instrument tested. It's kept in the output
precisely so that stays visible rather than being quietly assumed to work.

---

## Extensions worth doing next

1. **Body/open-based levels.** Add a second detector using impulsive-candle opens
   and bodies, per the Gala method, and compare hold rates against wick pivots.
   This is a directly testable question: which kind of level holds better?
2. **Live alerting.** Watch spot, fire when price enters a level's band, and print
   that level's historical card. This is the operational form of the whole idea.
3. **Confluence scoring.** Reuse the 10-point framework in
   `Order Flow System/Stage3_Architecture.md`, with hold-rate and expectancy as
   inputs rather than the hand-assigned weights.
4. **Databento validation study.** Spend the $125 credit once on real CME depth
   around equivalent levels to test whether resting-size imbalance genuinely
   predicts rejection. If it doesn't there, Layer 3 won't help in a CFD book
   either — and that's worth knowing before investing in it.
5. **Walk-forward.** Split the sample; check that a level's hold rate in the first
   half predicts the second. Without this, per-level stats are description, not
   edge.

### Gold-specific

6. **Pull OG options instead of GLD.** Options on COMEX gold futures put strikes
   directly on the futures price, removing the ETF ratio entirely. CME publishes
   them free; every CME endpoint 403s from this environment but should work from
   your machine. This is the single biggest quality upgrade available to Layer 4.
7. **Condition `level_stats` on the gamma regime.** The obvious test: do XAUUSD
   pivots hold more often on positive-net-gamma days than negative ones? If the
   pinning story is real it will show up as a hold-rate difference, and that turns
   a plausible narrative into a filter worth trading. This is the highest-value
   next piece of work in the whole project — it joins two layers that currently
   only sit next to each other.
8. **Volume profile per session.** Rebuild the profile for the London and US
   windows separately; gold's character differs sharply between them, and a
   single 30-day profile blurs that.
9. **Track basis decay as a signal in its own right.** The basis falling toward
   zero dates the contract; a sharp move in it can front-run rate repricing.
