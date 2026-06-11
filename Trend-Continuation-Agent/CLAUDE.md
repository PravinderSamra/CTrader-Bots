# /Trend-Continuation-Agent — Implementation Notes

This document records every place the implementation deviates from, fills a
gap in, or makes an interpretive decision about
`spec/TrendContinuation_Agent_Spec_v1.pdf` ("the spec"). Built against the
live cTrader MCP HTTP endpoint (`mcp.ctrader.com/trading/mcp`) on the
Pepperstone UK Spread Betting demo account.

Run `python orchestrator.py` from this directory for a scan, or
`python orchestrator.py execute --card N --risk 450 [--confirm]` to size and
place a trade from the last scan. See `SKILL.md` for the rendering /
commentary / confirmation layer.

---

## 1. `get_trendbars` requires `fromTimestamp`/`toTimestamp`, capped at 720h

**Spec says**: `getBars(symbol, period, count)` — fetch N bars by count.

**Reality** (confirmed via live HTTP 400s): the deployed `get_trendbars` tool
rejects `count` alone with `"fromTimestamp: must not be null"`, despite its
own description claiming `(count)` is a valid combination. It requires
`fromTimestamp` + `toTimestamp`, and the upstream range is hard-capped at
**720h (30 days)** — a larger range returns
`"Time range exceeds upstream cap of 720h... Split into 720h-or-smaller
windows and call this tool multiple times"`.

210 × 4H bars need ~840 calendar hours, which exceeds the 720h cap in one
call (and even 720h of 24/5 trading only yields ~126 4H bars, well short of
the 200 needed).

**Fix** (`utils/mcp_client.py` `get_trendbars`): walk backwards from "now" in
≤720h windows (`_MAX_RANGE_HOURS = 720.0`, up to `_MAX_WINDOWS = 4`), merging
and de-duplicating bars by timestamp until `count` bars are collected or a
window returns nothing. For 1H (210 bars ≈ 210h of trading time) this
resolves in a single window/call; for 4H it takes two. This is the same
windowing approach used by `ICT-SMC-Remote-Agent`'s `ctrader_fetcher.py`.

---

## 2. Position sizing must convert SL distance into the symbol's `point_size`

**Spec §6 says**: `Stake (£/pt) = Risk Amount (£) ÷ SL distance (points)`,
where `SL distance (points) = |entry − SL|` (a raw price difference). The
worked example (UK100, SL = 55 *points*, point_size = 1.0) makes "points"
and "raw price units" the same number, so the formula reads as a direct
division.

**Reality**: for spread-betting, "£/pt" is denominated in the symbol's
broker-defined point size from `get_symbols`'
`"...bet in 1 GBP per (X)"` description (`InstrumentData.point_size`):
`1.0` for indices/XAU/XPD/XPT, `0.0001` for most FX majors/crosses,
`0.01` for JPY pairs/XAG/CORN/oil, `0.001` for NATGAS, etc. Applying the
spec's formula literally to a raw price-distance SL on, say, AUDUSD
(`sl_distance ≈ 0.00706`) gives `stake = 450 / 0.00706 ≈ £63,762/pt` and a
6,376,200-unit order — roughly 10,000× oversized (confirmed by a live
calculation before this fix; not placed).

**Fix** (`agents/execution.py` `build_order_plan`):
```python
sl_distance_points = plan["sl_distance"] / (data.point_size or 1.0)
sizing = calc_stake(risk_amount, sl_distance_points)
```
For index-style instruments (`point_size == 1.0`) this is a no-op and
matches the spec's worked example exactly. For AUDUSD it now gives
`≈ £6.38/pt raw → £6/pt broker stake → volume 600`, which is sane for a
£450 risk on a ~70-pip stop.

Note this is a *different* "points" unit from `to_raw_points()` /
`relativeStopLoss` / `relativeTakeProfit` (item 4 below), which are in
cTrader's pipette units derived from `pip_digits`, not `point_size`. Two
different broker unit systems collide on the word "points" — `point_size`
is the **spread-betting stake unit**; pipettes are the **cTrader API order
unit**.

---

## 3. Symbol alias map: USOIL → Crude, UKOIL → Brent (plus EU50 → EUSTX50)

**Spec §11 says**: "33 pre-configured instruments... fuzzy match on base
name". `EU50 → EUSTX50` was an expected case.

**Reality**: this broker lists oil as `Crude_SB` ("WTI Cash (or Spot)
Contract") and `Brent_SB` ("Brent Crude vs US dollar") — neither
`USOIL`/`UKOIL` nor any name containing those substrings exists, so the
fuzzy `startswith`/`contains` fallback in `resolve_symbol` never matches and
both instruments would silently disappear from every scan (2 of the 33 core
instruments).

**Fix** (`utils/mcp_client.py` `resolve_symbol`): added explicit aliases
`{"USOIL": "CRUDE", "UKOIL": "BRENT"}` alongside the existing `EU50 →
EUSTX50` alias. `PRICE_RANGES` already had `CRUDE`/`BRENT` entries
(point_size = 0.01 for both), so pip-digit detection works unchanged.

---

## 4. `relativeStopLoss`/`relativeTakeProfit` are raw pipette *points*, not display-price distances

**Spec §6 pseudocode says**: `createMarketOrder(symbol, direction, volume,
stopLoss, takeProfit=TP1)` — implies absolute prices.

**Reality** (from the live `create_order` tool schema): `MARKET` orders take
`relativeStopLoss` / `relativeTakeProfit` as **positive integer pipette
counts** from the fill price (direction is implied by `tradeSide`), not
absolute prices. Absolute prices (`stopLoss`/`takeProfit`/`limitPrice`) are
only accepted on `LIMIT`/`STOP` orders.

**Fix**: `mcp_client.to_raw_points(symbol, display_distance)` /
`get_pip_digits(symbol)` convert a display-price distance to pipettes using
the same auto-detected `pip_digits` as `get_trendbars`/`get_spot_prices`.
`execution.execute_order` converts `sl_distance` and `tp1_points` this way
before calling `create_market_order`; TP2/TP3 limit orders use absolute
prices (`order_plan["tp2"]`/`["tp3"]`) directly, which is correct for
`LIMIT` orders.

---

## 5. TP2/TP3 are independent opposite-side LIMIT orders (no `linkedPositionId`)

**Spec §6 step 3-4 pseudocode says**: `createLimitOrder(symbol,
CLOSE_direction, volume/3, TP2, linkedPositionId)` — implying a "reduce this
specific position" linked closing order.

**Reality**: the live `create_order` schema has no `linkedPositionId` field
at all. `execution.execute_order` places TP2/TP3 as plain opposite-side
`LIMIT` orders (`close_side`, `tp23_volume`, `tp2`/`tp3` price). On a
netted spread-betting account these will net down/close the position when
filled, which achieves the same economic effect, but they are **not**
formally linked to the market order's position the way the spec's
pseudocode implies. If Pepperstone ever rejects an opposite-side LIMIT order
while a position is open (hedging-mode-only accounts behave differently),
this step will need revisiting.

**Volume split** (`agents/execution.py` `build_order_plan`): `tp23_volume =
(volume // 3 // BROKER_VOLUME_STEP) * BROKER_VOLUME_STEP` (each of TP2/TP3
gets ⌊volume/3⌋ rounded down to the nearest £1/pt step); `tp1_volume =
volume - 2 × tp23_volume` keeps the remainder (≥ 1/3) on the position with
TP1. If a third of the stake rounds to 0 broker units (small stakes),
`split_tps = False` and the full position runs with TP1 only — TP2/TP3 are
not placed.

**Caveat — TP ordering** (flagged for Pravinder, not changed): because
`TP1_R (1.5) < TP2_R (2.5) < TP3_R (4.0)`, in a clean continuation move TP1
(closest, attached to the market order) fills first and reduces the
position to the TP2/TP3 remainder — consistent with "bank profit, reduce
risk, let the runner work". This is almost certainly the intended behaviour.
However the two TP2/TP3 LIMIT orders are placed independently of TP1's
fate: if price reverses sharply *before* TP1 fills and tags TP2/TP3's price
levels first (e.g. a SHORT that spikes back up through TP2/TP3 territory
without ever reaching the much-closer TP1), those LIMIT orders could fill
against an unintended/larger remaining position. This is an edge case the
spec doesn't address; flagging rather than silently "fixing" since any fix
(e.g. OCO-style cancellation) would need product-level decisions beyond
"implement exactly as specified".

---

## 6. `BARS_1H` bumped from 110/100 to 210/200

**Spec §12 config says**: `BARS_1H = 110 # fetch 110, use last 100`.

**Reality**: §8 Signal S5 requires `EMA(close_1H, 200)`. A 200-period EMA
needs ≥200 bars of history — with only 100 1H bars, `ema(..., 200)` is
`None` for the entire series and S5 would score 0 for *every* instrument,
every time. Bumped `BARS_1H`/`BARS_1H_USED` to 210/200 (identical to the 4H
depth) so `EMA200_1H` is computable. `BARS_4H`/`BARS_4H_USED` (210/200) are
unchanged from the spec.

---

## 7. Entry-zone half-width derived as 1/10th of S2's proximity threshold

**Spec** doesn't give an explicit formula for the "ENTRY: 8,340 – 8,345 (1H
EMA21 zone)" band — only the worked example (EMA21 ≈ 8,342.5 → zone
8,340–8,345, i.e. a half-width of ~2.5, ≈ 0.03% of price).

**Decision** (`config.ENTRY_ZONE_HALFWIDTH_PCT = 0.0003`): derived as 1/10th
of S2's "tight" 0.3% proximity threshold (spec §8 S2). This reproduces the
worked example almost exactly (8,342.5 × 0.0003 ≈ 2.503).

**Resulting nuance**: a card's `AT_ENTRY` vs `WATCH` status is driven by S2
(`scores.S2 > 0`, i.e. price within **0.3%** of EMA21_1H — spec's explicit
rule), but the *displayed* entry zone (`entry_low`/`entry_high`) is the much
tighter **0.03%** band. So an `AT_ENTRY` card can legitimately have
`distance_points`/`distance_pct` > 0 (price is within S2's 0.3% but outside
the literal ±0.03% band). Per the spec's own card layouts this is invisible
to the user — `distance_points`/`distance_pct` are only rendered on `WATCH`
cards — but it's worth knowing if those fields are inspected directly on an
`AT_ENTRY` card.

---

## 8. Scores below `TIER_C_MIN` (30) are dropped entirely

**Spec §8 says**: `tier = 'A' if total_score >= 75 else 'B' if total_score
>= 50 else 'C'` — no lower bound on `'C'`, so a score of e.g. 5 would
technically be tier `'C'`.

**Decision** (`agents/scoring_ranking.py`): treated `TIER_C_MIN = 30` (from
`config.py`, already present pre-session) as a real floor — instruments
scoring `< 30` get `tier = None` and are dropped from both `ranked` and
`watchlist` entirely (gates passed but conviction is too low to even watch).
This matches §4's "Tier C (30-49)" framing and avoids a "watchlist" full of
near-zero-conviction noise on quiet days.

---

## 9. S6 Fibonacci zone test is direction-symmetric (no inversion needed)

**Spec §8 S6 says**: `if fib_382 <= current_price <= fib_618: s6 = 15 ...
# Note: invert logic for SHORT (price below fib levels)`.

**Decision** (`agents/scoring_ranking.py`): no inversion implemented. The
38.2%–61.8% *price band* is a fixed absolute-price interval — checking
whether `current_price` falls inside it is identical regardless of whether
the setup is LONG or SHORT. There is no separate "SHORT fib level set" to
invert *to*; the spec's note appears to be a leftover caution that doesn't
apply to an absolute price-band test. `fib_retracement_pct` (added for the
trade card / commentary, item 11) gives the same answer either way: `0%` =
at `swing_high_ref`, `100%` = at `swing_low_ref`.

**Bug fix (post-initial-build)**: `utils.indicators.fibonacci_levels` returns
levels in **descending** order — `fib["0.0"]` = `swing_high_ref` down to
`fib["1.0"]` = `swing_low_ref`, so `fib["0.382"] > fib["0.618"]` and
`fib["0.236"] > fib["0.382"]` etc. The original comparisons
(`fib["0.382"] <= current_price <= fib["0.618"]`, and similarly for the
8pt zones) were therefore **always false** — `lower_bound <= x <= upper_bound`
where `lower_bound > upper_bound` is never satisfiable — so **S6 scored 0 for
every instrument, every scan**, regardless of price. Caught when a live scan
showed EURGBP at `fib_retracement_pct = 74.2%` (squarely in the 61.8–76.4%
band) still scoring `S6 = 0`. Fixed by swapping the comparison bounds to
match the descending order:
```python
if fib["0.618"] <= current_price <= fib["0.382"]:      # 38.2-61.8% zone -> 15
    s6 = 15
elif (fib["0.764"] <= current_price <= fib["0.618"]) or (fib["0.382"] <= current_price <= fib["0.236"]):
    s6 = 8                                              # 23.6-38.2% or 61.8-76.4% -> 8
else:
    s6 = 0
```
This changed EURGBP's live score from 70 (Tier B) to 78 (Tier A) on the
2026-06-11 10:46 BST scan.

---

## 10. `DATA_FAIL` vs `INSUFFICIENT_DATA` vs `SYMBOL_NOT_FOUND`

**Spec §2** lists these as error conditions without precisely separating
"couldn't fetch" from "fetched but too little history". `agents/
data_retrieval.py` distinguishes:
- `SYMBOL_NOT_FOUND` — `resolve_symbol` returned nothing (not in the
  enabled SB symbol map). Skipped silently per spec §11.
- `DATA_FAIL` — `get_trendbars`/`get_spot_price` returned `None` after
  `mcp_client`'s internal retry (session re-init + one retry).
- `INSUFFICIENT_DATA` — bars were returned but `< MIN_BARS` (150) remain
  after dropping the still-forming trailing bar (spec §2: "Partial data
  (< 150 bars) → Skip — ADX/EMA calculations are unreliable").

All three are logged to `data/last_scan.log` and summarised by prefix in
`log_summary` in `last_scan.json`; the instrument is skipped from the rest
of the pipeline in all three cases.

---

## 11. Trade-card commentary helper fields (`agents/scoring_ranking.py`)

To keep "Python does the deterministic maths, the skill renders + comments"
(per `orchestrator.py`'s docstring), three extra fields were added to
`score_instrument`'s output, mirroring values shown in the spec §9 worked
example but not otherwise exposed:
- `ema21_distance_pct` — the S2 input (`|price − EMA21_1H| / EMA21_1H ×
  100`), e.g. "price 0.18% from EMA21".
- `atr_ratio` — the S4 input (`current_1H_bar_range / ATR_1H`), e.g. "bar
  range 0.8× ATR".
- `fib_retracement_pct` — derived from the S6 fib levels (`(swing_high_ref −
  price) / (swing_high_ref − swing_low_ref) × 100`), e.g. "price at 71%
  retracement".

---

## 12. Full-universe scan scope (`config.py`, pre-session deviation, restated)

Spec §1 instrument scope is "33 configured instruments + full available SB
symbol list scan". The live enabled SB symbol list has **1,618** instruments
(`mcp_client.list_base_names()`), and Sub-Agent 1 fetches 4H+1H bars
sequentially per instrument (now up to 3 `get_trendbars` calls each, per
item 1) — scanning all 1,618 is an overnight batch job, not an interactive
"scan". Default behaviour scans `CORE_INSTRUMENTS` (33, minus
`KNOWN_UNAVAILABLE = {BTCUSD, ETHUSD}` → 31 fetched in practice);
`--full-universe` adds `EXTENDED_UNIVERSE` (18 curated FX/metal crosses);
`--full-universe-all` scans all 1,618 (not recommended interactively).

---

## 13. `call_tool` was swallowing real broker errors as a generic "no response"

**Live test (2026-06-11)**: First-ever `--confirm` execution — Card #2
(EURGBP SHORT, £450 risk, £16/pt, `split_tps: true`) — returned:
```
{"error": "MCP create_order (MARKET) returned no response — check get_positions before retrying."}
```
Verified via `get_positions` (empty) and `get_order_history` (empty for the
day) that **no order was placed** — not a margin issue either (`get_balance`
showed £48,233.50 free margin). `tools/list` confirmed `create_order` is
present and the session/auth handshake succeeds, so the failure was specific
to the `tools/call` for `create_order`.

**Root cause** (`utils/mcp_client.py` `call_tool`): the old code only handled
the success path (`data["result"]["content"][0]["type"] == "text"`, parsed as
JSON) and a session-expiry `error`. Any *other* response shape — a top-level
JSON-RPC `error` (broker rejection), an MCP tool-execution error
(`result.isError: true` with a plain-text message), or successful-but-non-JSON
text — fell through to `return None`. `execute_order` then reported the
generic "no response" message, hiding the broker's actual rejection reason
and violating spec §6 / SKILL.md's "report MCP/order errors verbatim" rule.

**Fix**: `call_tool` now returns `{"error": <message>}` for all three of
those cases (and only returns `None` on a true transport/session failure).
`execute_order` (`agents/execution.py`) unwraps `market_resp["error"]`
directly so the confirmation-flow caller sees the real broker message.
`--card 2 --risk 450` dry-run re-verified working after the fix
(`issues: []`, same sizing). **The EURGBP trade itself was not retried** —
per spec §6 Execution Error Handling ("do not retry automatically — ask
Pravinder to review"), a fresh CONFIRM is required.

---

## 14. `volume` is "cents of base asset" — NOT a flat £/pt unit for non-index instruments

With item 13's fix in place, retrying `--confirm` for the same EURGBP SHORT
(Card #2, £450 risk, £16/pt) returned a **second**, now-real broker error:
```
HTTP 400: {"error":{"code":"400 BAD_REQUEST","message":"Order volume = 16.00 is smaller than minimum allowed volume = 1000.00.","httpStatus":400}}
```
Confirmed again via `get_positions`/`get_order_history`: still nothing
placed.

**Root cause**: `ctrader-mcp-integration-guide.md` Lesson 5 ("volume = £/pt
stake × 100, min/step 100") was derived from an **index** (US30) example. For
indices/XAU/XPD/XPT (`point_size == 1.0`), this happens to coincide with
cTrader's real convention — `volume` = "cents of base asset"
(`volume = lots × lotSize × 100`) — because 1 unit of the underlying = £1
P&L per 1-point move. For an FX pair the relationship between "1 unit of
base-currency notional" and "£/pt P&L" is scaled by `point_size`
(EURGBP: a 1 EUR notional position moves by `0.0001` GBP per `0.0001` price
change, i.e. per "point" — so £1/pt needs `1/point_size = 10,000` EUR
notional, not 1). Our submitted `volume=1600` (the old `broker_stake*100`
formula, i.e. £16/pt taken literally as "cents of base") was interpreted by
the broker as **16 EUR notional** — far below its **1,000 EUR (0.01 lot)
minimum** — hence "16.00 ... minimum ... 1000.00".

**Fix** (`utils/position_sizing.py` `calc_stake`, now takes `point_size`):
```python
volume = int(round(broker_stake * 100 / point_size))
min_volume = int(round(BROKER_MIN_VOLUME / point_size))
```
For `point_size == 1.0` this is unchanged (`volume = broker_stake * 100`,
verified against the original XAUUSD/AUDUSD-style dry runs). For EURGBP
(£16/pt, `point_size = 0.0001`): `volume = 16,000,000` — comfortably above
the ~100,000 (0.01 lot) minimum observed above.

The TP2/TP3 split in `agents/execution.py` `build_order_plan` used a fixed
`BROKER_VOLUME_STEP = 100` to snap `tp23_volume` — also only valid for
`point_size == 1.0`. Now scaled the same way:
`volume_step = round(BROKER_VOLUME_STEP / point_size)`. For EURGBP this gives
`tp1_volume = 6,000,000` (£6/pt) / `tp23_volume = 5,000,000` (£5/pt each) —
same £/pt split (6/5/5) as before, just correctly scaled.

**Not yet retried** — per spec §6, a fresh CONFIRM against the corrected
`order_plan` (10,000× larger `volume` numbers for EURGBP — same £16/pt risk,
just a different unit) is required before the third attempt.

---

## 15. LIVE TRADE PLACED — TP2/TP3 limit-price precision bug

**The third attempt (2026-06-11, fresh CONFIRM) succeeded for the MARKET
leg**: EURGBP SHORT, £16/pt (`volume: 16,000,000`), `positionId: 50650145`,
`orderId: 65620412`, `entryPrice: 0.86296`, `stopLoss: 0.86564`,
`takeProfit: 0.85894` (TP1) — `executionType: ORDER_ACCEPTED`. Confirmed live
via `get_positions`. **This is a real open position on the Pepperstone demo
SB account**, fully protected by SL + TP1.

The TP2/TP3 LIMIT legs both failed:
```
tp2_order: HTTP 400: {"error":{"code":"400 BAD_REQUEST","message":"Order price = 0.8561696562357894 has more digits than symbol allows. Allowed 5 digits","httpStatus":400}}
tp3_order: HTTP 400: {"error":{"code":"400 BAD_REQUEST","message":"Order price = 0.8521449243755937 has more digits than symbol allows. Allowed 5 digits","httpStatus":400}}
```

**Root cause**: `tp2`/`tp3` are computed via floating-point arithmetic
(`entry_mid + sign * TPn_R * sl_distance` in `agents/trade_card.py`) and
retain ~16 significant digits. `create_limit_order`'s `limitPrice` was passed
this raw float — EURGBP only allows 5 decimal places.

**Fix**: added `mcp_client.round_price(base_name, price)` (rounds to
`get_pip_digits`, the same precision used for `to_raw_points`/
`get_trendbars`/`get_spot_prices`). `execute_order` now rounds `tp2`/`tp3`
through this before calling `create_limit_order`. Also extracted the TP2/TP3
placement loop into `execution.place_tp_legs(order_plan)`, reused by
`execute_order` AND exposed via a new `--retry-tps` flag on
`orchestrator.py execute` — so the two missing legs for the open position
above can be (re)placed without re-submitting the MARKET order (which would
double the position). Dry-run with `--retry-tps` re-verified: `tp2=0.85617`,
`tp3=0.85214` (both within 5 digits), `tp23_volume=5,000,000` (£5/pt) each,
`close_side=BUY` (closes the SHORT).

**Not yet retried** — placing TP2/TP3 is itself a new order action and
requires fresh CONFIRM per spec §6.

---

## 16. `BARS_15M = 65` / `BARS_15M_USED = 60` — extra fetch buffer beyond v1.1's literal `60`

**v1.1 §2.4 says**: `BARS_15M = 60 # 15M bars, ~15 hours of 15M data`.

**Decision** (`config.py`): matched the existing `BARS_4H`/`BARS_1H` "fetch a
few more than you use" pattern (item 6) — `BARS_15M = 65` (fetch) /
`BARS_15M_USED = 60` (use). The extra 5 bars give `_drop_incomplete_bar` and
`MIN_BARS_15M` (21) headroom against any short window from `get_trendbars`
(item 1). The *used* count (60) matches the spec exactly, so all downstream
indicator math (EMA21_15M etc.) sees exactly the spec's window.

---

## 17. Day trade SL uses simple last-20-1H-bar `min`/`max`, not `find_swings`

**v1.1 §3.3 says**: SL = wider of `1.5 × ATR_1H` from entry and
`min(low of last 20 1H bars) − 0.5 × ATR_1H` (LONG), symmetric `max(high)`
for SHORT — with no mention of `find_swings`'s confirmed-swing-point logic
(used by the swing pipeline's SL, spec §5).

**Decision** (`agents/trade_card.py` `build_day_trade_plan`): implemented
literally — `data.bars_1h[-20:]`, plain `min(b.low ...)` / `max(b.high ...)`,
no swing-confirmation filter. This is a deliberate spec difference, not an
oversight: the day trade pipeline trades faster-moving 15M-entry structure,
where the raw 20-bar extreme (even if not a "confirmed" swing point) is the
relevant invalidation level — vs the swing pipeline's slower 4H structure,
where only confirmed swing points are meaningful support/resistance.

---

## 18. `compute_rescan_time_15m` — interpretive day-trade rescan cadence

**v1.1 §3.4** says WATCH cards get a "recommended rescan time" but gives no
formula for the day trade pipeline (the swing pipeline's
`compute_rescan_time` is keyed to the 1H grid).

**Decision** (`utils/time_utils.py`): added `compute_rescan_time_15m`,
mirroring `compute_rescan_time`'s shape but on the 15M grid — recommended
rescan = next 15M candle close + 15 minutes (i.e. 2 candles forward), with
the same "if the next close is within 2 minutes, push out one extra candle
first" guard against an immediate re-scan. Same interpretive-derivation
pattern as item 7 (no explicit spec formula; derived from the existing
analogous swing-pipeline mechanism).

---

## 19. `ASSUMED_MARGIN_RATE` (1/30) + notional-value formula for the v1.1 §5.2 margin check

**v1.1 §5.2 says**: "Check free margin covers the estimated requirement for
this position; if not, abort with a clear message" — no formula is given,
and no per-symbol margin/leverage rate is exposed by `get_symbols`.

**Decision** (`config.py` / `agents/execution.py` `check_margin`):

```python
notional_value_gbp = (order_plan["sizing"]["volume"] / 100) * entry_price
estimated_margin = notional_value_gbp * ASSUMED_MARGIN_RATE   # 1/30
```

`ASSUMED_MARGIN_RATE = 1/30` (~3.33%) is the ESMA retail FX/CFD leverage cap
(30:1) — a conservative *floor* on real leverage for indices/majors (which
often allow higher), so this errs toward **over-estimating** the margin
requirement and blocking a marginal trade, not under-estimating and allowing
an over-leveraged one.

`notional_value_gbp = (volume / 100) * entry_price` follows from the cTrader
MCP server's documented convention `volume = lots × lotSize × 100`
(`volume / 100` = base-asset units; × `entry_price` = notional in the
instrument's quote currency, treated as GBP for this approximation — same
simplification as item 2). Verified against two cases:
- **UK100** (`point_size = 1.0`, £16/pt → `volume = 1600`):
  `notional = 16 × entry_price` — sane for a £16/pt index CFD.
- **EURGBP** (`point_size = 0.0001`, £16/pt → `volume = 16,000,000`, item
  14): `notional = 160,000 × 0.86 ≈ £137,600` (i.e. 160,000 EUR notional ×
  spot ≈ £137,600); `estimated_margin ≈ £4,587` at 30:1 — a believable
  margin requirement for a position that size.

---

## 20. Day trade S4 (1H ATR Range Guard) "≥2x: 0pts" treated as consistent with "else: 0"

**v1.1 §3.2 S4 says**: `<1.0x ATR: 15pts | 1.0–1.5x: 8pts | ≥2x: 0pts` —
leaving the `[1.5x, 2.0x)` band unstated.

**Decision** (`agents/scoring_ranking.py` `score_day_trade`): implemented
`<1.0 → 15, <1.5 → 8, else → 0`, identical in shape to the (unambiguous)
swing pipeline S4. The `[1.5, 2.0)` gap falls into `else → 0` — "≥2x: 0pts"
is treated as a redundant special case of the general "else: 0": any bar
range ≥1.5×ATR scores 0, whether it's 1.6× or 6×.

---

## 21. Day trade S5 (1H + 4H Alignment) "Neither: 0pts" branch is unreachable post-gate

**v1.1 §3.2 S5 says**: "1H EMA stack aligned AND 4H EMA stack same direction:
15pts | 1H only: 8pts | Neither: 0pts".

**Decision** (`agents/scoring_ranking.py` `score_day_trade`): implemented
all three branches via `aligned_1h` (1H EMA stack matches `direction`) and
`gate_result["bias_4h_aligned"]` (4H stack matches `direction`, computed in
`day_trade_gates`). However, the day trade gate cascade's G2 (mirroring the
swing pipeline's hard EMA-alignment gate) already requires `aligned_1h ==
True` for any instrument that reaches scoring, so "Neither: 0pts"
(`not aligned_1h`) can never execute in practice. Kept for spec fidelity /
defensive completeness rather than removed — same approach as item 9's
provably-unreachable branch.

**Overlap with `DAY_BONUS_4H`** (not double-counting): `S5` and the +10
bonus both reward 4H/1H alignment, so a fully-aligned setup gets `S5 = 15`
**and** `bonus = 10`. This is intentional per v1.1 §2.1/§3.2 — the bonus
answers a separate question ("is this day trade *also* a swing-aligned
trend continuation?") layered on top of the day-trade-only S1-S6 score, not
a re-statement of S5.

---

## 22. Day trade universe = `DAY_TRADE_UNIVERSE ∩ data_by_symbol` (bounded by `--symbols`/`--full-universe` scope)

**v1.1 §2.5/§6.2 step 4 says**: the day trade pipeline runs on a fixed
27-instrument `DAY_TRADE_UNIVERSE` (config.py), "using existing 4H+1H data"
already fetched for the swing pipeline — explicitly no second fetch loop.

**Decision** (`orchestrator.py` `_day_trade_symbols`): when `--symbols` (or
the default `CORE_INSTRUMENTS`) is a *subset* of `DAY_TRADE_UNIVERSE`, the
day trade pipeline only scans `DAY_TRADE_UNIVERSE ∩ data_by_symbol.keys()` —
never an instrument that wasn't fetched for the swing pipeline this run.
This is the only interpretation consistent with "no second fetch": a
`DAY_TRADE_UNIVERSE` member with no 4H/1H data in `data_by_symbol` is
silently absent from the day trade universe (not logged as a failure — it
was never requested this scan). `--full-universe`/`--full-universe-all`
naturally cover all of `DAY_TRADE_UNIVERSE`, since it's a subset of
`EXTENDED_UNIVERSE ∪ CORE_INSTRUMENTS`.

---

## 23. Crypto (`BTCUSD`/`ETHUSD`) >0.15%-of-price spread exclusion in `_day_trade_symbols`

**v1.1 §2.5 says**: crypto symbols (BTCUSD, ETHUSD) should be flagged/excluded
if the live spread exceeds 0.15% of price.

**Decision** (`orchestrator.py` `_day_trade_symbols`): implemented as an
exclusion-with-log (`WIDE_SPREAD_DAY: {symbol} (spread=X.XXX% of price)`)
rather than a soft "flag but include" — a >0.15% spread is large enough to
materially distort the tight day-trade SL/TP math (spread eats directly into
the SL distance), so exclusion is the safer reading of "flag/exclude". In
practice `BTCUSD`/`ETHUSD` are already in `config.KNOWN_UNAVAILABLE` (item
12) and never reach `data_by_symbol`, so this check is currently a no-op —
implemented for correctness/future-proofing if either is ever re-enabled.

---

## 24. Day trade AT_ENTRY/WATCH status via `scores["S2"] > 0` matches v1.1's 0.1%/0.5% description

**v1.1 §3.4 says**: entry zone = `ema21_15m ± 0.1%`; a setup is AT_ENTRY if
price is "within" this zone and WATCH otherwise. Separately, §3.2 S2 scores
`<=0.2% → 20pts, <=0.5% → 10pts, else → 0pts`.

**Decision** (`agents/trade_card.py` `build_day_trade_plan`): reused the
swing pipeline's pattern (item 7), `status = "AT_ENTRY" if scores["S2"] > 0
else "WATCH"`. For day trade this maps onto S2's **0.5%** threshold — i.e.
AT_ENTRY means "price within 0.5% of EMA21_15M" — which is a tighter fit to
spec intent than the swing pipeline's analogous mapping (item 7 noted a
0.3%-vs-0.03% mismatch there, since swing's S2 thresholds are 0.3%/0.75%).
The *displayed* entry zone (`entry_low`/`entry_high`, ±0.1%) remains
narrower than the AT_ENTRY threshold (±0.5%), so item 7's "an AT_ENTRY card
can have `distance_points` > 0" nuance applies here too.

---

## 25. cTrader `get_trendbars` requires `M_15`, not `M15`, for the 15M period

**Live test (2026-06-11, first end-to-end day-trade-pipeline run)**: a
31-instrument `CORE_INSTRUMENTS` scan found exactly one day-trade-gate-passed
instrument (NZDUSD), but its 15M fetch failed:
`DATA_FAIL: NZDUSD (15M bars)` — `day.scored_count = 0`, `day.ranked = []`,
despite `day.gates_passed_count = 1`.

**Root cause**: `get_trendbars`'s `period_map` (item added this session,
v1.1 §2.4) mapped `"15M"`/`"M15"` → `"M15"`. A direct `call_tool` with
`period: "M15"` returned a JSON-RPC validation error — the tool's `period`
enum is `["M_1","M_5","M_15","M_30","H_1","H_4","D_1","W_1","MN_1"]`
(underscore-separated, matching the existing `"H_4"`/`"H_1"` mappings for 4H/1H —
`"M15"` was the only one missing the underscore).

**Fix** (`utils/mcp_client.py` `get_trendbars`): `period_map` now maps
`"15M"`/`"M15"`/`"M_15"` → `"M_15"`. Re-ran the same scan: NZDUSD's 15M fetch
now returns 65 bars, `day.scored_count = 1`, and produces a Tier A (75/110)
SHORT day trade card (`bonus = 10`, `bias_4h_aligned = true`) with no
`DATA_FAIL`/`INSUFFICIENT_DATA` entries anywhere in `last_scan.log`.

---

## Testing performed

- `python orchestrator.py --symbols UK100,GER40,EURUSD` and a 10-instrument
  multi-asset-class subset, then a full default `CORE_INSTRUMENTS` run (31
  fetched, 0 `DATA_FAIL`/`INSUFFICIENT_DATA`) — all against the **live**
  cTrader MCP HTTP endpoint.
- `python orchestrator.py execute --card 1 --risk 450` (dry-run, no
  `--confirm`) against a real ranked AUDUSD SHORT setup — produced a sane
  `order_plan` (£6/pt, 600-unit volume, max loss £423.45 against a £450
  risk budget, `split_tps: true`, `issues: []`).
- No order was placed (`--confirm` not used) — execution placement itself
  has not been live-tested.

### Day Trade Pipeline Upgrade (v1.1)

- `python orchestrator.py --symbols UK100,GER40,EURUSD,GBPUSD,EURGBP,XAUUSD`
  (6-instrument smoke test) — both pipelines ran end-to-end, output JSON has
  the new top-level `swing`/`day` structure, `day.gates_passed_count = 0`
  for this small subset (`DAY_GATE_FAIL` for all 6 — expected, see item 22).
- Full default `python orchestrator.py` (`CORE_INSTRUMENTS`, 31 fetched) —
  first run surfaced item 25's `M_15` period-code bug
  (`day.gates_passed_count = 1`, `day.scored_count = 0`,
  `DATA_FAIL: NZDUSD (15M bars)`). After the fix, re-ran the identical scan:
  - **Swing**: 4/31 gates passed, all 4 scored → 3× Tier A (EURGBP 93,
    AUDUSD 85, XAUUSD 75, all SHORT/AT_ENTRY) + 1× Tier B (NZDUSD 65,
    SHORT/AT_ENTRY). Watchlist empty.
  - **Day**: 25-instrument `DAY_TRADE_UNIVERSE ∩ data_by_symbol`, 1/25
    1H-gates passed (NZDUSD), 15M fetch succeeded (65 bars), scored Tier A
    (75/110, `bonus = 10`, `bias_4h_aligned = true`, SHORT/AT_ENTRY).
    Watchlist empty.
  - `last_scan.log`: 27 `GATE_FAIL` + 24 `DAY_GATE_FAIL`, 0
    `DATA_FAIL`/`INSUFFICIENT_DATA`/`WIDE_SPREAD_DAY`/`BELOW_WATCH_DAY`.
  - No anomalies in score breakdowns — every S1-S6/bonus component checked
    against its inputs (ADX, RSI, ATR ratio, EMA stacks, fib retracement,
    15M EMA21 distance) and matches the configured thresholds.
  - Only 4 actionable setups total (3 swing + 1 swing/day overlap on
    NZDUSD) reflects current market conditions (most instruments failed
    `G1_adx`/`G2_ema_stack` — a quiet/ranging session per the "London Mid"
    session note), not a pipeline defect.
