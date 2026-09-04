# Gex-Bot

Trading Gamma Exposure (GEX) levels from the [GexBot](https://gexbot.com)
API — reading dealer gamma positioning and building a strategy that
trades between the major gamma levels.

- **Phase 1 — connectivity.** Complete. See below.
- **Phase 2 — strategy research.** Not started.

## Phase 1 status: connectivity confirmed

The `GEX_BOT_API_TOKEN` works and has full access to the API surface.
Verified live on 2026-09-04:

```
[PASS] GEX_BOT_API_TOKEN found (57 chars)
[PASS] API reachable -- /tickers lists 60 symbols
[PASS] Token authenticated -- fetched SPX classic/zero
[PASS] payload sane -- spot 7747.71 sits inside ladder 7480-8010
[PASS] spx      spot=7747.71      +G=7780         -G=7700
[PASS] ndx      spot=29483.37     +G=29570        -G=29600
[PASS] nq_ndx   spot=29528.56     +G=29615.19     -G=29645.19
[PASS] es_spx   spot=7756.31      +G=7788.6       -G=7708.6
[PASS] spy      spot=773.84       +G=775          -G=765
[PASS] qqq      spot=721.3        +G=722          -G=715
[PASS] vix      spot=14.12        +G=18           -G=14
RESULT: all checks passed -- GexBot connectivity confirmed
```

Access level: **Classic package** — `gex_zero`, `gex_one` and `gex_full`
across all 60 tickers. `state` (delta/gamma/vanna/charm by strike),
`orderflow`, historical downloads and WebSocket are **not** included; they
return `403 {"error":"Classic package does not have access."}`.

Classic is the same tier Freddy Siento uses for the strategy in the research
below, so it covers his primary model. His secondary *convexity* model reads
the volatility surface and would likely need **State** or **Research**.

### The one gotcha

**Auth is an `Authorization: Bearer` header, not a `?key=` query
parameter.** The `?key=` form that appears in various GexBot references
returns 401 against the live API, with an empty body and no error
message. This cost most of the Phase 1 debugging time — if you see a
bare 401, check how the token is being sent before assuming it expired.

Full detail in [`docs/api-reference.md`](docs/api-reference.md).

## Usage

```bash
export GEX_BOT_API_TOKEN=...          # already set in the Claude env

# Verify connectivity
python3 scripts/check_connection.py

# Check a specific symbol / expiry scope
python3 scripts/check_connection.py --ticker nq_ndx --scope full
```

```python
from gexbot_client import GexBotClient

client = GexBotClient()                 # reads GEX_BOT_API_TOKEN
snap = client.gex("nq_ndx", "zero")     # scopes: zero | one | full

snap.spot          # 29528.56
snap.call_wall     # 29615.19  major positive-gamma strike (resistance)
snap.put_wall      # 29645.19  major negative-gamma strike (support)
snap.zero_gamma    # gamma flip level
snap.strike_rows() # [{'strike':…, 'gex_vol':…, 'gex_oi':…, 'priors':[…]}, …]
```

No dependencies — stdlib only.

## What the API gives us

Base URL `https://api.gex.bot/v2`. On our tier: `GET /{ticker}/classic/
{zero|one|full}`, plus public `GET /tickers` and `GET /{package}/categories`.
Each response is a ~3 KB snapshot containing spot, the gamma flip level,
call/put walls computed both by open interest and by session volume, net
GEX, and a per-strike gamma ladder with five prior readings per strike.

Beyond our tier the API also offers `state` (per-strike delta, gamma, vanna,
charm), `orderflow`, historical downloads, WebSocket streaming, and a
separate *gexbot research* product on its own key. Full picture in
[`docs/gexbot-platform-guide.md`](docs/gexbot-platform-guide.md).

Two things matter for how we build on this:

- **Use `NQ_NDX`, not `NDX`, for NAS100.** It is the futures-basis
  symbol; its ladder is shifted onto the futures basis and lines up with
  the CFD actually traded. Cash `NDX` levels sit ~45 points low.
- **Pre-session, only the `_oi` fields are populated.** Volume-weighted
  fields and `zero_gamma` read 0 until the US cash session trades, and
  the feed's timestamp does not advance outside RTH. A stale timestamp
  pre-open is expected, not a connection fault.

## Relationship to the existing GEX work in this repo

`GEX&OI/` and the NAS100 daily brief build gamma levels from the **free
CBOE chain** — raw per-contract OI and greeks, ~15 min delayed, 7 MB
payloads reduced by a script.

GexBot is a different trade-off, not a replacement: it is a pre-computed
3 KB snapshot with walls and flip levels already derived, and it carries
**volume-weighted gamma**, which the CBOE OI chain cannot give at all.
Whether it replaces or supplements the CBOE path is a Phase 2 question —
the two should be cross-checked against each other before either is
trusted for live levels.

## Phase 2 — open questions

1. **Which scope is Siento's "90-day open interest"?** He reads 90-day OI at
   09:30 ET to see how the whole market is positioned for the day. That does
   not map cleanly onto `zero` / `one` / `full` — `full` is "all expiries",
   not a 90-day window. **This is the biggest blocker to implementing his
   model** and needs resolving against the platform UI or support.
2. **Refresh cadence during RTH.** Partly answered: the feed is static
   outside cash hours, and volume fields populate once the session trades
   (`sum_gex_vol` went 0 → 311,384 between our pre-open and mid-session
   checks). The actual tick interval is still unmeasured.
3. **Cross-validation against CBOE.** Do GexBot's walls agree with the
   levels the existing `GEX&OI` pipeline computes?
4. **What `zero_gamma` does once populated**, and how it behaves relative
   to the walls.
5. **`max_priors` semantics.** Six prior readings of the major levels — the
   interval between them is unknown. If it is a fixed cadence this is
   exactly the level-*migration* signal Siento describes (a put wall moving
   5550 → 5530 mid-session), so it is worth decoding.
6. **Backtest the actual claim.** Does price reverse at the largest OI gamma
   level, in the first two hours, often enough to matter? His 75% is
   self-reported on a sponsored podcast — it is a hypothesis, not a
   baseline.
7. **Encode the slope rule.** Fast approach → wait for reclaim; slow
   approach → take the level. This is the one discretionary element in his
   model and needs a quantitative definition.
8. **Rate limits.** No documented limit; none hit during probing.

## Layout

```
Gex-Bot/
├── README.md
├── docs/
│   ├── api-reference.md            # endpoint map, schema, auth, tier codes
│   └── gexbot-platform-guide.md    # what GexBot is, packages, concepts
├── youtube-research/
│   ├── README.md                   # video index + how to pull transcripts
│   ├── vtt_to_text.py              # VTT -> clean de-duplicated text
│   ├── transcripts/                # raw .vtt + cleaned .txt
│   └── analysis/                   # written analysis per video
└── scripts/
    ├── gexbot_client.py            # client library (stdlib only)
    └── check_connection.py         # Phase 1 verification script
```

## Research

- [`youtube-research/`](youtube-research/) — transcripts and analysis of
  practitioners explaining how they trade these levels. Currently: the
  Chart Fanatics episode with **Freddy Siento**, a ~20-year institutional
  market maker who trades NQ off SPX/NDX gamma levels
  ([analysis](youtube-research/analysis/chart-fanatics-freddy-siento.md)).
- [`docs/gexbot-platform-guide.md`](docs/gexbot-platform-guide.md) — what
  GexBot computes, its packages, and the core concepts.
