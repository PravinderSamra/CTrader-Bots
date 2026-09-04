# GexBot API Reference

Derived by probing the live API on 2026-09-04. There is no public OpenAPI
spec or `/docs` route (`/docs` returns 404), so everything below was
established empirically.

Base URL: `https://api.gexbot.com`

## Authentication

**Auth is an `Authorization: Bearer <token>` header.**

This is the single most important finding of Phase 1. Several GexBot
references describe a `?key=<token>` query parameter. That form is **not
accepted** by the live API — it returns `401` with an empty body. Every
variant tested returned 401 except the header:

| Method | Result |
|---|---|
| `?key=<token>` | 401 |
| `?api_key=` / `?apikey=` / `?token=` / `?auth=` | 401 |
| `X-API-Key: <token>` header | 401 |
| `Cookie: auth=<token>` | 401 |
| **`Authorization: Bearer <token>`** | **200** |
| `Authorization: <token>` (raw, no scheme) | 200 |

A 401 comes back with `content-length: 0` and expiring `auth` /
`__Secure-NFA` cookies, so there is no error message to diagnose from —
a 401 almost always means the token was sent the wrong way, not that the
token itself is bad.

The token lives in the `GEX_BOT_API_TOKEN` environment variable. Never
commit it.

## Endpoints

### `GET /tickers` — public, no token required

Returns supported symbols grouped by asset class:

```json
{ "stocks": [...54], "indexes": [...4], "futures": [...2] }
```

- **indexes** (4): `NDX`, `RUT`, `SPX`, `VIX`
- **futures** (2): `ES_SPX`, `NQ_NDX`
- **stocks** (54): `AAPL AMD AMZN APP AVGO BABA BOIL COIN CRWD CRWV DDOG
  DIA GLD GME GOOG GOOGL HOOD HYG IBIT INTC IONQ IWM META MSFT MSTR MU
  NFLX NVDA NVO ORCL PL PLTR QQQ RDDT ROKU SHOP SLV SMCI SNDK SNOW SOFI
  SPCX SPY TLT TQQQ TSLA TSM UBER UNG UNH USO UVXY VALE ZS`

Because it needs no token, `/tickers` is the right endpoint for a
"is the API up?" check, separate from "is my token good?".

### `GET /{ticker}/classic/{scope}` — requires token

The only data family that exists. Ticker is case-insensitive
(lowercase in the path works). `scope` is one of:

| Scope | Meaning |
|---|---|
| `zero` | Nearest expiry only (0DTE when one exists) |
| `one` | Next expiry out |
| `full` | All expiries combined |

All three return an **identical schema**; only the aggregation scope
differs. Verified 200 across all tested tickers × all three scopes.

**404 on everything else.** These were probed and do not exist:
`/{t}/gex/*`, `/{t}/oi/*`, `/{t}/volume/*`, `/{t}/greeks/*`,
`/{t}/state`, `/{t}/maxchange`, and scopes `two`, `three`, `all`,
`week`, `month`.

## Response schema

```jsonc
{
  "timestamp": 1788523185,      // unix seconds, UTC
  "ticker": "SPX",
  "min_dte": 0,                 // DTE of the nearest expiry in this payload
  "sec_min_dte": 4,             // DTE of the second expiry
  "spot": 7747.71,
  "zero_gamma": 0,              // gamma flip level (0 = not computed yet)
  "major_pos_vol": 0,           // call wall by session VOLUME
  "major_pos_oi": 7780,         // call wall by OPEN INTEREST
  "major_neg_vol": 0,           // put wall by session VOLUME
  "major_neg_oi": 7700,         // put wall by OPEN INTEREST
  "sum_gex_vol": 0,             // net gamma, volume-weighted
  "sum_gex_oi": 15188.713,      // net gamma, OI-weighted
  "delta_risk_reversal": 0,
  "strikes": [ [7480, 0, -6.45, [0,0,0,0,0]], ... ],
  "max_priors": [ [0,0], ... ]  // 6 prior readings of the max levels
}
```

### `strikes` rows

Packed positional arrays, ascending by strike:

```
[ strike, gex_vol, gex_oi, [5 prior gex readings] ]
```

- `gex_oi` — gamma exposure at that strike from open interest. Positive
  = dealers long gamma (price suppression / pinning). Negative =
  dealers short gamma (price acceleration).
- `gex_vol` — same, from the current session's traded volume.

Ladder size varies by ticker: SPX 101 strikes, NQ_NDX 141.

## Operational notes

- **Volume fields are zero outside US cash hours.** Every `*_vol` field
  and `zero_gamma` read 0 during the pre-open probing. They populate as
  the session trades. **Pre-session analysis must use the `_oi` fields.**
- **The feed is static outside RTH.** The `timestamp` did not advance
  across repeated polls spanning ~15 minutes pre-open. Do not treat a
  stale timestamp as a broken connection — check it against US market
  hours first. Refresh cadence during RTH is still to be measured
  (Phase 2).
- **`NQ_NDX` / `ES_SPX` are the futures-basis symbols.** `NQ_NDX` spot
  read 29528.56 against cash `NDX` at 29483.37 — the strike ladder is
  shifted onto the futures basis. For NAS100 CFD trading, `NQ_NDX` is
  the correct symbol; its levels line up with the instrument actually
  being traded, whereas `NDX` levels sit ~45 points low.
- **Payloads are small** (~3 KB for SPX 0DTE), unlike the 7 MB raw CBOE
  chain used elsewhere in this repo. They can be fetched and parsed
  inline without a reduction step.
