# GexBot — platform and data guide

Research compiled 2026-09-04 from the official OpenAPI repo listing, the
GexBot site, third-party integrations, and direct probing of the live API
with our own token.

**Caveat on sources:** `gexbot.com` and its `/pricing` and `/research` pages
are fully client-side rendered and return no readable content to a fetcher,
so pricing and marketing detail below comes from search-result summaries and
third-party pages, not from the vendor page itself. The **API surface and
tier boundaries below were verified directly against the live API** and are
reliable. Treat prices as indicative and confirm on the site.

---

## What GexBot is

An options-analytics vendor (operated by NFA LLC) that computes dealer
positioning metrics — gamma exposure, greeks, and order flow — from options
chains and serves them as pre-derived levels via a web platform and a REST
API. The value is not raw chain data; it is the modelling of what dealers
must hedge.

It matters that this is *modelled*, not summed. As Freddy Siento notes in
the Chart Fanatics episode, when a market maker receives offsetting client
orders at the same strike he matches them internally and hedges nothing. A
naive open-interest sum would overstate hedging pressure. That netting logic
is part of what the subscription buys.

---

## The two products

| Product | Purpose | Key |
|---|---|---|
| **gexbot** | GEX, greeks, orderflow for an enumerated ticker list | gexbot key |
| **gexbot research (gbR)** | Chart/analytical data across a broad metric set, flexible output formats and filtering | separate gbR key |

Keys are **not interchangeable** between the two products.

---

## Packages (tiers)

Verified live: requesting an out-of-tier endpoint returns
`403 {"error":"Classic package does not have access."}` — an explicit,
diagnosable tier boundary.

| Package | Categories exposed (from `/{package}/categories`) |
|---|---|
| **Classic** | `gex_full`, `gex_zero`, `gex_one` |
| **State** | the Classic three **plus** `delta_zero/one`, `gamma_zero/one`, `vanna_zero/one`, `charm_zero/one` |
| **Orderflow** | `orderflow` |
| **Quant** | full access — adds historical downloads and WebSocket feeds |
| **Research** | gbR chart/analytical data |

Positioning, per vendor/third-party description: Classic = GEX by OI and
volume for bias and concentration. State = live per-strike gamma, classified
levels for intraday pivots. Orderflow = classified flow signals and regime
detection. Quant = build your own system on their data.

Indicative pricing seen in third-party listings starts around $19/mo for
State, with a `TRIAL50` code for 50% off a first month. **Unconfirmed** —
verify on the site.

### Our token's tier

**Classic.** Confirmed by the 403 body above. We have `gex_zero`, `gex_one`
and `gex_full` across all 60 tickers, and nothing else.

This matters for the strategy work: Freddy Siento also uses **Classic**, so
the tier we hold is the one his primary (open-interest levels) model needs.
His secondary *convexity* model draws on the volatility surface and would
likely require **State** or **Research**.

---

## API surface

**Base URL: `https://api.gex.bot/v2`**

`https://api.gexbot.com` also resolves and serves the same `classic` data,
and `api.gex.bot` works without the `/v2` prefix too. Prefer the documented
`https://api.gex.bot/v2`.

### Authentication

`Authorization: Bearer <token>`.

Confirmed by the official spec description: all endpoints except `/tickers`
and `/{package}/categories` require a Bearer key. Our own probing agrees —
every query-parameter form (`?key=`, `?api_key=`, `?token=`, `?auth=`),
`X-API-Key`, and cookie auth all return **401 with an empty body**. Only the
Authorization header works. See `api-reference.md` for the full matrix.

### Endpoints

| Endpoint | Auth | Notes |
|---|---|---|
| `GET /tickers` | none | 60 symbols in `stocks` / `indexes` / `futures` |
| `GET /{package}/categories` | none | enumerates that package's categories |
| `GET /{ticker}/classic/{zero\|one\|full}` | Bearer | the GEX snapshot — **our tier** |
| `GET /{ticker}/state/{category}` | Bearer | greeks by strike — 403 for us |
| `GET /{ticker}/orderflow/...` | Bearer | 403 for us |
| historical download, WebSocket negotiate | Bearer | Quant tier |

The spec also describes `GET /research/{ticker}/{metric}` with `format`,
`view`, `theme` and filter parameters, on a gbR key.

### Expiry scopes

- `zero` — nearest expiry (0DTE when one exists)
- `one` — next expiry out
- `full` — all expiries combined

All three return an identical schema. See `api-reference.md` for fields.

**Open question for the strategy:** Siento says he reads *"90-day open
interest"* to see how the whole market is positioned for the day. That does
not map cleanly onto these three scopes — `full` is the closest but is "all
expiries", not a 90-day window. Whether the platform UI offers a DTE filter
that the Classic API does not expose is unresolved, and it's the single most
important gap to close before implementing his model.

---

## Core concepts

**Gamma exposure (GEX)** — the dollar value of the underlying that dealers
must buy or sell to stay delta-neutral per 1% move. Positive GEX = dealers
long gamma: they sell rallies and buy dips, damping volatility, producing
mean-reverting ranges. Negative GEX = dealers short gamma: they buy rallies
and sell dips, amplifying moves, producing trends and vol expansion.

**The levels:**

| Term | GexBot field | Meaning |
|---|---|---|
| Call wall / major positive gamma | `major_pos_oi`, `major_pos_vol` | Largest positive-gamma strike. Resistance, pinning. |
| Put wall / major negative gamma | `major_neg_oi`, `major_neg_vol` | Largest negative-gamma strike. Support, acceleration. |
| Zero gamma / gamma flip | `zero_gamma` | Where net gamma crosses zero — the day's structural pivot. Above: compression. Below: expansion. |
| Net GEX | `sum_gex_oi`, `sum_gex_vol` | Aggregate regime measure. |

A third-party Quantower integration reads `classic/zero` for zero-gamma and
OI levels and `state/gamma` for the greeks variant — corroborating the
package/category mapping above.

**OI-based vs volume-based.** Every level comes in both flavours. OI is the
standing position (available pre-open, the whole market's positioning);
volume is today's traded flow (accumulates through the session). Our probing
confirms **all `_vol` fields and `zero_gamma` read 0 outside US cash hours**,
so pre-session work is necessarily OI-based — which is exactly what Siento's
model uses.

**0DTE.** Since 2021, 0DTE has grown to roughly 60-70% of index option
volume. It compresses an entire hedging cycle into one session, which is why
intraday gamma levels have become tradeable at all.

---

## Coverage

60 tickers total.

- **Indexes (4):** NDX, RUT, SPX, VIX
- **Futures (2):** ES_SPX, NQ_NDX
- **Stocks/ETFs (54):** AAPL AMD AMZN APP AVGO BABA BOIL COIN CRWD CRWV DDOG
  DIA GLD GME GOOG GOOGL HOOD HYG IBIT INTC IONQ IWM META MSFT MSTR MU NFLX
  NVDA NVO ORCL PL PLTR QQQ RDDT ROKU SHOP SLV SMCI SNDK SNOW SOFI SPCX SPY
  TLT TQQQ TSLA TSM UBER UNG UNH USO UVXY VALE ZS

**`NQ_NDX` and `ES_SPX` are futures-basis symbols** — the strike ladder is
shifted onto the futures basis. Verified: `NQ_NDX` spot 29528.56 vs cash
`NDX` 29483.37 at the same instant. This is the platform feature Siento
relies on ("prices convert to NQ prices"), and it is why `NQ_NDX` is the
correct symbol for NAS100 CFD work — cash NDX levels sit ~45 points low.

---

## Ecosystem

- **Official OpenAPI spec:** `github.com/nfa-llc/gexbot-openapi` (OpenAPI
  3.0.1, spec in `latest/`, WebSocket docs in `docs/`). We could not read
  the file contents — GitHub is reachable only through this session's
  scoped proxy and the repo is outside our allow-list.
- Third-party integrations exist for Quantower and TradingView; competing
  GEX vendors include SpotGamma, MenthorQ, GEXBoard and FlashAlpha.

---

## Sources

- [nfa-llc/gexbot-openapi](https://github.com/nfa-llc/gexbot-openapi) — official spec
- [gexbot.com](https://www.gexbot.com/pricing) · [gexbot research](https://www.gexbot.com/research)
- [Quantower GexBot Gamma Point](https://github.com/The-R2D2-code/Quantower_GexBot_Gamma_Point)
- [Gexbot State listing](https://groupbuytrading.com/product/gexbot-state/)
- [SpotGamma — GEX](https://spotgamma.com/gamma-exposure-gex/) · [How to trade GEX](https://spotgamma.com/gex/)
- [FlashAlpha — GEX explained](https://flashalpha.com/articles/what-is-gamma-exposure-gex-explained)
- [InsiderFinance — Ultimate Guide to GEX](https://www.insiderfinance.io/resources/the-ultimate-guide-to-gamma-exposure-gex)
- Direct probing of the live API with our token, 2026-09-04
