# Agent Skill: Trend Continuation Agent

**Invoke with**: `/Trend-Continuation-Agent`

**Install**:
```bash
cp "Trend-Continuation-Agent/SKILL.md" ~/.claude/skills/trend-continuation-agent.md
```

---

## Description

Multi-market trend-continuation scanner for the Pepperstone UK Spread Betting
account (cTrader MCP HTTP). Runs **two pipelines every scan**:

- **Swing pipeline** — 4H gates, 1H entry timing, 4H-ATR-based SL. Up to 3
  cards, score X/100.
- **Day trade pipeline** — 1H gates (+ non-excluding 4H directional bias),
  15M entry timing, 1H-ATR-based SL. Up to 3 cards, score X/110.

All deterministic work — data retrieval, gates, scoring, ranking,
entry-zone/SL/TP maths, and order placement — is done by `orchestrator.py`
and the `agents/`/`utils/` modules. **This skill's job is rendering,
commentary, and the CONFIRM/CANCEL conversation** — do not re-derive any
numbers; read them from the JSON the orchestrator emits.

See `CLAUDE.md` in this directory for every place the implementation deviates
from or fills a gap in the spec (PDFs), e.g. position-sizing units, how
`relativeStopLoss`/`relativeTakeProfit` work, the TP2/TP3 ordering caveat, and
the day trade pipeline's interpretive decisions.

---

## Step 1 — Run the scan

From the `Trend-Continuation-Agent` directory:

```bash
python orchestrator.py [--symbols UK100,GER40,US500] [--full-universe] [--full-universe-all]
```

- No arguments → swing pipeline scans `CORE_INSTRUMENTS` (33 instruments,
  minus 2 known unavailable on this account); day trade pipeline scans
  `DAY_TRADE_UNIVERSE` (the subset of those that were fetched).
- `--symbols` → scan only the listed instruments (comma-separated, any case)
  for the swing pipeline; the day trade pipeline runs on whichever of those
  are also in `DAY_TRADE_UNIVERSE`.
- `--full-universe` → also scans `EXTENDED_UNIVERSE` (curated FX/metal
  crosses) for the swing pipeline.
- `--full-universe-all` → scans every enabled SB symbol (~1,600+ — slow, only
  use if explicitly asked for an overnight/batch scan).

The command prints the full result JSON to stdout (and writes it to
`data/last_scan.json` / `data/last_scan.log`). Parse that JSON for everything
below.

**Output is nested by pipeline**: `output["swing"]` and `output["day"]`, each
with `universe_count`, `gates_passed_count`, `scored_count`, `tier_counts`,
`ranked` (top-10 A/B, sorted), and `watchlist` (Tier C). Field names
referenced as `{ranked[i].field}` etc. below mean
`output["swing"]["ranked"][i]` or `output["day"]["ranked"][i]` as
appropriate. `output["scan_time_uk"]`, `output["session"]`,
`output["fetched_count"]`, and `output["log_summary"]` are top-level (shared
by both pipelines).

---

## Formatting conventions

- **Decimal precision**: render prices to the same number of decimals as
  `current_price`/`spot_bid` for that instrument in the JSON — don't add or
  drop precision.
- **"Points" vs raw price distance**: per `CLAUDE.md` item 2, "points" only
  equals the raw price difference for `point_size == 1.0` instruments
  (indices, XAU/XPD/XPT). For those, render `sl_distance`, `tp{1,2,3}_points`,
  `distance_points` with a `pts` suffix exactly as in the spec's UK100
  example (e.g. `55 pts`). For every other instrument (`point_size != 1.0`,
  e.g. FX, JPY pairs, oil), render the same fields as plain numbers at the
  instrument's natural precision with no `pts`/`pips` label (e.g.
  `0.00706 from entry`) — don't invent a pip/point conversion that isn't in
  the JSON.
- **Tier**: `ranked[i].tier` is `"A"` or `"B"` (Tier C goes to `watchlist`,
  scores below `TIER_C_MIN` never appear at all — see `CLAUDE.md` item 8).
- **Status**: `ranked[i].status` is `"AT_ENTRY"` or `"WATCH"` — selects which
  card template below to use.
- **Score denominator**: swing cards show `X/100`; day trade cards show
  `X/110` (100 base + the `bonus` field, which is `0` or `DAY_BONUS_4H`).

---

## Step 2 — Scan Header

Render first, using `output["scan_time_uk"]`, `output["session"]`,
`output["swing"]` and `output["day"]`:

```
═══════════════════════════════════════════════════════════
/TREND-CONTINUATION-AGENT | Dual Pipeline Scan Complete
Time     : {scan_time_uk}
Session  : {session.name} — {session.note}
Universe : {swing.universe_count} instruments (swing) | {day.universe_count} instruments (day trade)
Swing gates : {swing.gates_passed_count} passed | Tier A: {swing.tier_counts.A} B: {swing.tier_counts.B} C: {swing.tier_counts.C}
Day gates   : {day.gates_passed_count} passed | Tier A: {day.tier_counts.A} B: {day.tier_counts.B} C: {day.tier_counts.C}
═══════════════════════════════════════════════════════════
```

If both `output["swing"]["ranked"]` and `output["day"]["ranked"]` are empty,
state plainly: **"No Tier A/B setups found in either pipeline this scan."** —
then skip to the Watch List (Step 5) if it has entries, otherwise end here.

---

## Step 3 — Swing Trade Cards (`swing.ranked[0..2]`)

Render the divider, then up to 3 cards. If `swing.ranked` is empty, write
*"No swing setups this scan."* and move on. If it has 1-2 entries, render only
those and note *"Fewer than 3 actionable swing setups found this scan."*

```
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■■ SWING TRADES ■■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
```

For each card, `n` = 1-based position, `c` = `swing.ranked[n-1]`.

### AT_ENTRY card (`c.status == "AT_ENTRY"`)

```
───────────────────────────────────────────────────────────
SWING TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/100
Pipeline: Swing | Gate TF: 4H | Entry TF: 1H
───────────────────────────────────────────────────────────
Instrument     : {c.symbol} ({c.sb_symbol})
Direction      : {c.direction}
Current Price  : {c.current_price}
Status         : ✅ AT ENTRY ZONE

ENTRY      : {c.entry_low} – {c.entry_high}  (1H EMA21 zone)
STOP LOSS  : {c.sl}  ({c.sl_distance} [pts] / 1.5× 4H ATR)
TP1        : {c.tp1}  (+{c.tp1_points} [pts] | R:R 1.5:1)
TP2        : {c.tp2}  (+{c.tp2_points} [pts] | R:R 2.5:1)
TP3        : {c.tp3}  (+{c.tp3_points} [pts] | R:R 4.0:1)

CONFLUENCE MET
───────────────
✅ G1 ADX(14) = {c.adx_value:.1f} — Rising (trend confirmed)
✅ G2 EMA Stack: 21 {>|<} 50 {>|<} 200 on 4H  ({c.ema21_4h} {>|<} {c.ema50_4h} {>|<} {c.ema200_4h})
✅ G3 Price {above|below} 4H EMA21
✅ G4 No RSI divergence on 4H
{✅|❌} S1 ADX Strength: {c.adx_value:.1f} → {c.scores.S1}pts
{✅|❌} S2 1H EMA Proximity: price {c.ema21_distance_pct:.2f}% from EMA21 → {c.scores.S2}pts
{✅|❌} S3 RSI Zone: 1H RSI = {c.rsi_1h:.1f} ({in|outside} momentum zone) → {c.scores.S3}pts
{✅|❌} S4 ATR Guard: bar range {c.atr_ratio:.1f}× ATR → {c.scores.S4}pts
{✅|❌} S5 MTF Alignment: 1H stack also {bullish|bearish|not aligned} → {c.scores.S5}pts
{✅|❌} S6 Fib Zone: price at {c.fib_retracement_pct:.0f}% retracement → {c.scores.S6}pts

CLAUDE COMMENTARY
─────────────────
{2-4 sentences — see "Writing the commentary" below}
───────────────────────────────────────────────────────────
```

Fill the `{>|<}` / `{above|below}` / `{bullish|bearish}` placeholders from
`c.direction`: `LONG` → `>`, "above", "bullish"; `SHORT` → `<`, "below",
"bearish". `{in|outside}` for S3 is `"in"` if `c.scores.S3 > 0` else
`"outside"`. Every `{✅|❌}` is ✅ if that signal's score is `> 0`, else ❌
(G1-G4 are always ✅ — only gate-passed instruments reach a card).

### WATCH card (`c.status == "WATCH"`)

```
───────────────────────────────────────────────────────────
SWING TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/100
Pipeline: Swing | Gate TF: 4H | Entry TF: 1H
WATCH — ENTRY NOT YET REACHED
───────────────────────────────────────────────────────────
Instrument   : {c.symbol} ({c.sb_symbol})
Direction    : {c.direction}
Current Price: {c.current_price}
Entry Zone   : {c.entry_low} – {c.entry_high}  (1H EMA21)
Distance     : {c.distance_points} [pts] away ({c.distance_pct:.2f}% {c.entry_zone_position} entry)

[SL, TP1/2/3 calculated at entry zone midpoint]
STOP LOSS  : {c.sl}
TP1: {c.tp1}   TP2: {c.tp2}   TP3: {c.tp3}

RECOMMENDED RESCAN : {c.rescan_time_uk} (next 1H close)
NOTE: If price reaches {c.entry_low}–{c.entry_high} before rescan, entry
conditions are met — monitor manually.

CLAUDE COMMENTARY
─────────────────
{1-3 sentences — why it's not at entry yet, and what's needed}
───────────────────────────────────────────────────────────
```

`c.entry_zone_position` is `"above"` or `"below"` (or `"at"`, in the rare
case noted in `CLAUDE.md` item 7 where an `AT_ENTRY` card would have shown
nonzero distance — that case never reaches a WATCH card).

---

## Step 4 — Day Trade Cards (`day.ranked[0..2]`)

Render the divider, then up to 3 cards. If `day.ranked` is empty, write *"No
day trade setups this scan."* and move on. If it has 1-2 entries, render only
those and note *"Fewer than 3 actionable day trade setups found this scan."*

```
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
■■ DAY TRADES ■■
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
```

For each card, `n` = 1-based position, `c` = `day.ranked[n-1]`.

### AT_ENTRY card (`c.status == "AT_ENTRY"`)

```
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
DAY TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/110
Pipeline: Day Trade | Gate TF: 1H | Entry TF: 15M
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Instrument     : {c.symbol} ({c.sb_symbol})
Direction      : {c.direction}
Current Price  : {c.current_price}
Status         : ✅ AT ENTRY ZONE

ENTRY      : {c.entry_low} – {c.entry_high}  (15M EMA21 zone)
STOP LOSS  : {c.sl}  ({c.sl_distance} [pts] / 1.5× 1H ATR or 20-bar 1H structure)
TP1        : {c.tp1}  (+{c.tp1_points} [pts] | R:R 1.5:1)
TP2        : {c.tp2}  (+{c.tp2_points} [pts] | R:R 2.5:1)
TP3        : {c.tp3}  (+{c.tp3_points} [pts] | R:R 4.0:1)

CONFLUENCE MET
───────────────
✅ G1 ADX(14) on 1H = {c.adx_value:.1f} — Rising (trend confirmed, > 22)
✅ G2 EMA Stack: 21 {>|<} 50 {>|<} 200 on 1H  ({c.ema21_1h} {>|<} {c.ema50_1h} {>|<} {c.ema200_1h})
✅ G3 Price {above|below} 1H EMA21
✅ G4 No RSI divergence on 1H (30-bar lookback)
{✅|❌} S1 ADX Strength (1H): {c.adx_value:.1f} → {c.scores.S1}pts
{✅|❌} S2 15M EMA21 Proximity: price {c.ema21_distance_pct_15m:.2f}% from EMA21 → {c.scores.S2}pts
{✅|❌} S3 1H RSI Zone: RSI = {c.rsi_1h:.1f} ({in|outside} momentum zone) → {c.scores.S3}pts
{✅|❌} S4 1H ATR Guard: bar range {c.atr_ratio:.1f}× ATR → {c.scores.S4}pts
{✅|❌} S5 1H+4H Alignment: 1H stack {bullish|bearish}, 4H stack {also aligned|not aligned} → {c.scores.S5}pts
{✅|❌} S6 1H Fib Zone (30-bar): price at {c.fib_retracement_pct:.0f}% retracement → {c.scores.S6}pts
{✅|➖} BONUS 4H Bias Aligned: 4H EMA stack {confirms|does not confirm} 1H direction → +{c.bonus}pts

CLAUDE COMMENTARY
─────────────────
{2-4 sentences — see "Writing the commentary" below}
───────────────────────────────────────────────────────────
```

`{✅|➖}` for BONUS is ✅ if `c.bonus > 0` else ➖ (not a failure — just no
bonus). For S5, "1H stack" direction phrase comes from `c.direction` (always
aligned post-gate); "4H stack also aligned/not aligned" comes from
`c.bias_4h_aligned`.

### WATCH card (`c.status == "WATCH"`)

```
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
DAY TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/110
Pipeline: Day Trade | Gate TF: 1H | Entry TF: 15M
WATCH — ENTRY NOT YET REACHED
■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
Instrument   : {c.symbol} ({c.sb_symbol})
Direction    : {c.direction}
Current Price: {c.current_price}
Entry Zone   : {c.entry_low} – {c.entry_high}  (15M EMA21)
Distance     : {c.distance_points} [pts] away ({c.distance_pct:.2f}% {c.entry_zone_position} entry)

[SL, TP1/2/3 calculated at entry zone midpoint]
STOP LOSS  : {c.sl}
TP1: {c.tp1}   TP2: {c.tp2}   TP3: {c.tp3}

RECOMMENDED RESCAN : {c.rescan_time_uk} (next 15M close)
NOTE: If price reaches {c.entry_low}–{c.entry_high} before rescan, entry
conditions are met — monitor manually.

CLAUDE COMMENTARY
─────────────────
{1-3 sentences — why it's not at entry yet, and what's needed}
───────────────────────────────────────────────────────────
```

### Writing the commentary (both pipelines)

2-4 sentences (1-3 for WATCH cards), in Claude's own words, covering:
- The gate-timeframe trend picture (ADX level/direction, EMA stack) — why the
  continuation thesis holds. For day trade cards, also mention whether the 4H
  bias is aligned (the BONUS) or not.
- What the remaining signals collectively say about entry timing/quality —
  call out the *strongest* and *weakest* signals by name (don't just restate
  the ✅/❌ table).
- `session.note` (from the header) if it's relevant to execution quality
  right now (e.g. After Hours / Pre-London → flag wider spreads; NY
  Overlap/London Open → favourable). This is especially relevant for day
  trade cards.
- For WATCH cards: what would need to happen (price action vs EMA21) for
  status to flip to AT_ENTRY.

Do not fabricate numbers — every figure used in commentary must come from the
JSON.

---

## Step 5 — Watch List (Tier C, both pipelines)

Combine `output["swing"]["watchlist"]` and `output["day"]["watchlist"]`. If
both are empty, omit this section entirely. Otherwise:

```
WATCH LIST (Tier C — passed gates, below actionable threshold)
────────────────────────────────────────────────────────────
[SWING] {w.symbol} {w.direction} — Score {w.total_score}/100 (Tier C)
[DAY]   {w.symbol} {w.direction} — Score {w.total_score}/110 (Tier C)
... (one line per entry — `w.pipeline` selects the [SWING]/[DAY] tag)
```

---

## Step 6 — Rescan Guidance

Check `swing.ranked[0..2]` and `day.ranked[0..2]` (whichever were rendered)
for `status == "WATCH"`. Render only the lines that apply:

```
RESCAN GUIDANCE
───────────────
Swing : {rescan_time_uk from any WATCH swing card} (next 1H close)
Day   : {rescan_time_uk from any WATCH day card} (next 15M close)
```

Within a pipeline, all WATCH cards share the same `rescan_time_uk` (computed
from the same scan timestamp). Omit a line if no shown card from that
pipeline is `WATCH`; omit the whole section if neither pipeline has a WATCH
card.

---

## Step 7 — Entry Prompt

Always end with this single line (verbatim, per v1.1 §4.2):

```
To enter a trade, say: Enter [swing/day] trade [1/2/3] with £[amount] risk
```

---

## Execution Flow (spec §6 / v1.1 §5) — explicit invocation only

**Never run this flow unless Pravinder gives a direct instruction** like
*"Enter swing trade 1 with £450 risk"* or *"Enter day trade 2 — 300"*. A scan
alone never triggers execution.

### 6a — Build the order plan (dry run)

```bash
python orchestrator.py execute --pipeline {swing|day} --card N --risk <AMOUNT>
```

(`--pipeline` = `swing` or `day` depending on which list the user referred to,
default `swing` if genuinely ambiguous — but always confirm which pipeline if
the instruction doesn't say; `N` = the card number 1-3 from the *last* scan;
`<AMOUNT>` = risk in GBP, numeric only.) This returns
`{"order_plan": {...}, "issues": [...], "warnings": [...]}` and places **no
order**.

- If `issues` is non-empty: render each issue verbatim and **stop** — do not
  show a confirmation block. Each issue is a complete, user-facing sentence
  already (e.g. "Stake £0.00/pt is below the broker minimum...", "Price has
  moved through the SL level — trade no longer valid. Abort.", "Estimated
  margin requirement (£X) exceeds free margin (£Y) — aborting.").
- If `warnings` is non-empty, render each one above the confirmation block
  under a `⚠ WARNINGS` heading — these do NOT stop the flow, but the user
  should see them before typing CONFIRM (e.g. "Stake £X/pt exceeds £50/pt...",
  "Spread (...) is N% of the SL distance...").
- Otherwise (or after the warnings) render the confirmation block from
  `order_plan`:

```
== ORDER CONFIRMATION ({SWING|DAY} TRADE) ==
Instrument : {order_plan.symbol}
Direction  : {order_plan.trade_side}
Entry      : MARKET (current {ask|bid} ~{order_plan.entry_price})
Stop Loss  : {order_plan.sl}  ({order_plan.sl_distance_points:.2f} pts)
TP1 : {order_plan.tp1} | TP2: {order_plan.tp2} | TP3: {order_plan.tp3}
Risk       : £{order_plan.risk_amount}
Stake      : £{order_plan.sizing.broker_stake:.2f}/pt (rounded down from £{order_plan.sizing.raw_stake:.2f}; broker step = £1/pt)
Max loss   : £{order_plan.sizing.max_loss:.2f} (at SL)
Spread     : {order_plan.spread_points:.2f} pts
{If order_plan.split_tps: "Note: TP2/TP3 (£{order_plan.tp23_volume/100:.2f}/pt each) are placed as independent opposite-side LIMIT orders, not formally linked to this position — see CLAUDE.md item 5."}
{If NOT order_plan.split_tps: "Note: stake too small to split — TP2/TP3 not placed, full position runs to TP1."}

Type CONFIRM to place, or CANCEL to abort.
==
```

`{ask|bid}` = `"ask"` if `trade_side == "BUY"` else `"bid"`.
`order_plan.sizing.*` fields come from `calc_stake` (`raw_stake`,
`spec_stake`, `broker_stake`, `volume`, `max_loss`, `below_minimum`).

### 6b — On "CONFIRM"

```bash
python orchestrator.py execute --pipeline {swing|day} --card N --risk <AMOUNT> --confirm
```

Read `result`:
- `result.error` → report verbatim, do not retry automatically (spec §6
  Execution Error Handling).
- Otherwise `result.market_order` (and `result.tp2_order`/`result.tp3_order`
  if `split_tps` was true) — summarise: confirm the order was placed, surface
  any position/order ID and fill price present in the response, and list the
  TP2/TP3 limit orders placed (if any).

End with: *"Rescan available at any time with /Trend-Continuation-Agent —
open positions can be checked via the cTrader MCP `get_positions` tool."*
(Pravinder's discretion — this skill does not auto-monitor positions.)

### 6c — On "CANCEL"

Acknowledge and take no further action. Do not run `--confirm`.

---

## Behavioural Rules

1. **Never execute without the explicit CONFIRM/CANCEL step**, even if
   Pravinder's instruction sounds final ("enter trade 1 with £450, go
   ahead") — always show the confirmation block first and wait for the
   literal word `CONFIRM`.
2. **A scan never places an order.** Execution only runs from an explicit
   "Enter [swing/day] trade N with £X risk"-style instruction, against the
   *last* saved scan (`data/last_scan.json`). If no scan has been run yet, say
   so and run one first.
3. **If `issues` is non-empty, stop before the confirmation block** — report
   the issue(s) and ask whether to adjust risk or skip the trade.
4. **Render `warnings` (if any) before the confirmation block** but do not
   treat them as blocking — the user can still CONFIRM.
5. **Report MCP/order errors verbatim** — do not retry, reinterpret, or
   suppress them.
6. **Don't fabricate data.** Every number in a card or the commentary must
   trace back to a field in the orchestrator's JSON output.
7. **Flag After Hours / Pre-London sessions explicitly** in commentary per
   spec §10 — note wider spreads / "do not recommend entry" framing for
   After Hours. This applies doubly to day trade cards, where spread cost is
   a larger fraction of the (smaller) SL distance.
8. **Always disambiguate swing vs day trade** in execution — if Pravinder
   says "enter trade 1" without specifying which pipeline and both pipelines
   produced a card #1, ask which one before running `execute`.

---

## Invocation Modifiers

| Command | Behaviour |
|---|---|
| `/Trend-Continuation-Agent` | Default scan — swing on `CORE_INSTRUMENTS`, day trade on `DAY_TRADE_UNIVERSE` |
| `/Trend-Continuation-Agent --symbols UK100,GER40,US500` | Scan only the listed instruments (swing); day trade runs on the overlap with `DAY_TRADE_UNIVERSE` |
| `/Trend-Continuation-Agent --full-universe` | `CORE_INSTRUMENTS` + `EXTENDED_UNIVERSE` (swing only — day trade universe unchanged) |
| `/Trend-Continuation-Agent --full-universe-all` | All enabled SB symbols (slow — only if explicitly requested) |
| "Enter swing trade N with £X risk" | Run the Execution Flow (§6) with `--pipeline swing` for card N from the last scan |
| "Enter day trade N with £X risk" | Run the Execution Flow (§6) with `--pipeline day` for card N from the last scan |
