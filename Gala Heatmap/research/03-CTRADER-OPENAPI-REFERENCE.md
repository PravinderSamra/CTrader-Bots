# cTrader Open API — Depth & Tick Reference

Working notes for the two capabilities that the cTrader **MCP** server does not
expose but the **Open API** does. Complements `ctrader-mcp-integration-guide.md`
in the repo root, which covers the MCP path.

---

## 1. Which endpoint gives what

| Capability | MCP (`mcp.ctrader.com/trading/mcp`) | Open API (`*.ctraderapi.com:5035`) |
|---|---|---|
| Symbols, spot prices | ✅ | ✅ |
| Trendbars (OHLCV) | ✅ (100-bar cap) | ✅ |
| Orders / positions / deals | ✅ | ✅ |
| **Level 2 depth quotes** | ❌ **not exposed** | ✅ `ProtoOASubscribeDepthQuotesReq` |
| **Historical tick data** | ❌ not exposed | ✅ `ProtoOAGetTickDataReq` |
| Live trendbar subscription | ❌ | ✅ `ProtoOASubscribeLiveTrendbarReq` |

Tool surface confirmed by enumerating the live MCP schemas on 2026-08-01:
`get_symbols`, `get_spot_prices`, `get_trendbars`, `get_assets`, `get_balance`,
`get_positions`, `get_position_details`, `get_pending_orders`, `get_order_history`,
`get_deals`, `get_version`, plus the mutating trade tools. No depth tool exists.

---

## 2. Authentication — the two are separate

The MCP endpoint takes a single `Authorization: Bearer <slug>` header, where the
slug is base64url of `{"plant":…,"environment":…,"token":…}`. **That token does not
authenticate the Open API protobuf endpoint.**

The Open API needs its own handshake:

1. Register an app at <https://openapi.ctrader.com/> → **Client ID + Client Secret**.
2. Complete the OAuth flow for your trading account → **Access Token** (scope: `trading`).
3. Connect TLS to `demo.ctraderapi.com:5035` or `live.ctraderapi.com:5035`.
4. `ProtoOAApplicationAuthReq{clientId, clientSecret}`
5. `ProtoOAGetAccountListByAccessTokenReq{accessToken}` → discover `ctidTraderAccountId`
6. `ProtoOAAccountAuthReq{ctidTraderAccountId, accessToken}`
7. Now you may subscribe.

Registration is free. `src/dom_recorder.py` implements steps 3–7.

---

## 3. Depth of market

### Subscribe

```
ProtoOASubscribeDepthQuotesReq {
  ctidTraderAccountId : int64
  symbolId            : repeated int64
}
```

Unsubscribe with `ProtoOAUnsubscribeDepthQuotesReq`.

### The event

```
ProtoOADepthEvent {
  ctidTraderAccountId : int64
  symbolId            : int64
  newQuotes           : repeated ProtoOADepthQuote
  deletedQuotes       : repeated uint64          // quote ids to remove
}

ProtoOADepthQuote {
  id   : uint64
  size : uint64        // in cents of base  → divide by 100 for units
  bid  : uint64 (opt)  // in pipettes       → divide by 100000 for display price
  ask  : uint64 (opt)  // exactly one of bid/ask is set
}
```

**It is an incremental feed.** There is no full-book snapshot message. You must
hold `id -> (side, price, size)` yourself, apply `deletedQuotes` then `newQuotes`
on every event, and snapshot your own copy on a timer. Getting this wrong is the
usual reason a homemade heatmap looks like confetti.

Multiple LP quotes can rest at the same price — aggregate by price before
rendering, or the "size at this level" number will be wrong.

### Expect thin books on CFDs

Depth is Pepperstone's aggregated LP book, not exchange depth. FX generally has
several levels a side; index and commodity CFDs are often quoted by a handful of
LPs and may return very little. **Probe before you build:**

```bash
python3 src/dom_recorder.py --probe --probe-seconds 60
```

---

## 4. Historical tick data

```
ProtoOAGetTickDataReq {
  ctidTraderAccountId : int64
  symbolId            : int64
  type                : ProtoOAQuoteType    // BID = 1, ASK = 2
  fromTimestamp       : int64 (opt)         // ms
  toTimestamp         : int64 (opt)         // ms, max 2147483646000
}

ProtoOAGetTickDataRes {
  tickData : repeated ProtoOATickData        // chronological
  hasMore  : bool                            // page with a moved toTimestamp
}
```

`ProtoOATickData` is **delta-encoded**: the first entry carries an absolute Unix
ms timestamp, every subsequent entry carries the *difference* from the previous
one. Same for price. Decode cumulatively or your series will be nonsense.

**One request returns one side.** Ask twice — once `BID`, once `ASK` — and merge
if you want a spread series.

**There is no size and no aggressor flag.** This is a quote feed. It cannot
produce true delta or CVD; see `02-DATA-SOURCE-INVESTIGATION.md` §3.

---

## 5. MCP trendbar gotchas (verified 2026-08-01)

Recorded here because they cost real debugging time and aren't documented.

1. **100-bar silent cap.** Requesting 08:00→15:00 M1 (420 bars) returns exactly
   100 bars — the *most recent* 100 of the range, 13:20→15:00. No error, no flag.
2. **Timestamps must be strings.** `{"fromTimestamp": 1785510000000}` is rejected
   with `invalid_type, expected string`. Pass `"1785510000000"`.
3. **`count` alone doesn't work** despite the schema showing it as valid — the
   server replies `fromTimestamp: must not be null`. Always send an explicit range.
4. **Paging must handle gaps.** A window falling mostly in a market-closed period
   returns a single bar at `toTimestamp` (the endpoint is inclusive). Resuming
   from "oldest bar returned" then makes zero progress and the walk stalls
   silently at one day of data. Correct rule:

   ```python
   cursor = oldest if (len(bars) >= 100 and oldest < cursor) else frm
   ```

   i.e. a *full* response means you were truncated (resume at the oldest bar); a
   *short* response means you already have everything in that window (skip it).

   Implemented in `src/ctrader_http.py::trendbars`.
5. **`volume` is tick volume**, not contracts. See §4 of the investigation doc.

---

## 6. Symbol IDs on this account

From existing repo config plus this session's `get_symbols`. All are `_SB`
(spread betting) and `pipDigits = 5`, so divide raw prices by 100,000.

| Symbol | ID |
|---|---|
| EURUSD | 1 |
| GBPUSD | 2 |
| UK100 | 113 |
| US500 | 115 |
| NAS100 | 116 |
| VIX | 152 |
| XAUUSD | 241 |

Resolve others at runtime — `level_stats.py::resolve_symbol` matches on name with
the `_SB` suffix stripped.
