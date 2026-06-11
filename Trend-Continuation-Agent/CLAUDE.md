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
