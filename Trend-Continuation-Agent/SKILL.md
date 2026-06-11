# Agent Skill: Trend Continuation Agent

**Invoke with**: `/Trend-Continuation-Agent`

**Install**:
```bash
cp "Trend-Continuation-Agent/SKILL.md" ~/.claude/skills/trend-continuation-agent.md
```

---

## Description

Multi-market trend-continuation scanner for the Pepperstone UK Spread Betting
account (cTrader MCP HTTP). All deterministic work — data retrieval, the four
gates, the six-signal score, ranking, entry-zone/SL/TP maths, and order
placement — is done by `orchestrator.py` and the `agents/`/`utils/` modules.
**This skill's job is rendering, commentary, and the CONFIRM/CANCEL
conversation** — do not re-derive any numbers; read them from the JSON the
orchestrator emits.

See `CLAUDE.md` in this directory for every place the implementation deviates
from or fills a gap in the spec (PDF), e.g. position-sizing units, how
`relativeStopLoss`/`relativeTakeProfit` work, the TP2/TP3 ordering caveat.

---

## Step 1 — Run the scan

From the `Trend-Continuation-Agent` directory:

```bash
python orchestrator.py [--symbols UK100,GER40,US500] [--full-universe] [--full-universe-all]
```

- No arguments → scans `CORE_INSTRUMENTS` (the spec's 33, minus 2 known
  unavailable on this account).
- `--symbols` → scan only the listed instruments (comma-separated, any case).
- `--full-universe` → also scans `EXTENDED_UNIVERSE` (curated FX/metal
  crosses).
- `--full-universe-all` → scans every enabled SB symbol (~1,600+ — slow, only
  use if explicitly asked for an overnight/batch scan).

The command prints the full result JSON to stdout (and writes it to
`data/last_scan.json` / `data/last_scan.log`). Parse that JSON for everything
below. Field names referenced as `{ranked[i].field}` etc. are exactly the
JSON keys in `output["ranked"]` / `output["watchlist"]`.

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
  scores < 30 never appear at all — see `CLAUDE.md` item 8).
- **Status**: `ranked[i].status` is `"AT_ENTRY"` or `"WATCH"` — selects which
  card template below to use.

---

## Step 2 — Scan Header

Render first, using `output["scan_time_uk"]`, `output["session"]`,
`output["universe_count"]`, `output["gates_passed_count"]`,
`output["scored_count"]`, `output["tier_counts"]`:

```
═══════════════════════════════════════════════════════════
/TREND-CONTINUATION-AGENT | Scan complete
Time     : {scan_time_uk}
Session  : {session.name} — {session.note}
Universe : {universe_count} instruments scanned
Gates    : {gates_passed_count} passed all 4 gates
Scored   : {scored_count} | Tier A: {tier_counts.A} | Tier B: {tier_counts.B} | Tier C: {tier_counts.C}
Output   : Top 3 trade cards below
═══════════════════════════════════════════════════════════
```

If `output["ranked"]` is empty, state plainly: **"No Tier A/B setups found
this scan."** — then skip to the Watch List (Step 5) if it has entries,
otherwise end here. If `ranked` has 1-2 entries, render only those cards and
note *"Fewer than 3 actionable setups found this scan."* after the header.

---

## Step 3 — Trade Cards (`ranked[0]`, `ranked[1]`, `ranked[2]`)

For each card, `n` = 1-based position, `c` = `ranked[n-1]`.

### AT_ENTRY card (`c.status == "AT_ENTRY"`)

```
───────────────────────────────────────────────────────────
TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/100
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
TRADE CARD #{n} | TIER {c.tier} | SCORE: {c.total_score}/100
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

### Writing the commentary

2-4 sentences (1-3 for WATCH cards), in Claude's own words, covering:
- The 4H trend picture (ADX level/direction, EMA stack) — why the
  continuation thesis holds.
- What S2-S6 collectively say about entry timing/quality — call out the
  *strongest* and *weakest* signals by name (don't just restate the
  ✅/❌ table).
- `c.session.note` (from the header) if it's relevant to execution quality
  right now (e.g. After Hours / Pre-London → flag wider spreads; NY
  Overlap/London Open → favourable).
- For WATCH cards: what would need to happen (price action vs EMA21) for
  status to flip to AT_ENTRY.

Do not fabricate numbers — every figure used in commentary must come from the
JSON.

---

## Step 4 — Watch List (Tier C)

If `output["watchlist"]` is non-empty, render one line per entry:

```
WATCH LIST (Tier C — passed gates, below actionable threshold)
────────────────────────────────────────────────────────────
{w.symbol} {w.direction} — Score {w.total_score}/100 (Tier C)
... (one line per entry in output["watchlist"])
```

Omit this section entirely if `watchlist` is empty.

---

## Step 5 — Rescan Guidance

If any of `ranked[0..2]` has `status == "WATCH"`, render:

```
RESCAN GUIDANCE
───────────────
Next recommended scan: {rescan_time_uk} (next 1H close)
```

Use the `rescan_time_uk` from any WATCH card shown — they're all computed
from the same scan timestamp via the same §10 rule and will be identical.
Omit this section if no shown card is `WATCH`.

---

## Step 6 — Entry Prompt

Always end with this single line (verbatim, per spec §9):

```
To enter a trade, say: Enter trade [1/2/3] with £[amount] risk
```

---

## Execution Flow (spec §6) — explicit invocation only

**Never run this flow unless Pravinder gives a direct instruction** like
*"Enter trade 1 with £450 risk"* or *"Enter trade 2 — 300"*. A scan alone
never triggers execution.

### 6a — Build the order plan (dry run)

```bash
python orchestrator.py execute --card N --risk <AMOUNT>
```

(`N` = the card number 1-3 from the *last* scan; `<AMOUNT>` = risk in GBP,
numeric only.) This returns `{"order_plan": {...}, "issues": [...]}` and
places **no order**.

- If `issues` is non-empty: render each issue verbatim and **stop** — do not
  show a confirmation block. Each issue is a complete, user-facing sentence
  already (e.g. "Stake £0.00/pt is below the broker minimum...", "Price has
  moved through the SL level — trade no longer valid. Abort.").
- Otherwise render the confirmation block from `order_plan`:

```
== ORDER CONFIRMATION ==
Instrument : {order_plan.symbol}
Direction  : {order_plan.trade_side}
Entry      : MARKET (current {ask|bid} ~{order_plan.entry_price})
Stop Loss  : {order_plan.sl}  ({order_plan.sl_distance_points:.2f} pts)
TP1 : {order_plan.tp1} | TP2: {order_plan.tp2} | TP3: {order_plan.tp3}
Risk       : £{order_plan.risk_amount}
Stake      : £{order_plan.sizing.broker_stake:.2f}/pt (rounded down from £{order_plan.sizing.raw_stake:.2f}; broker step = £1/pt)
Max loss   : £{order_plan.sizing.max_loss:.2f} (at SL)
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
python orchestrator.py execute --card N --risk <AMOUNT> --confirm
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
   "Enter trade N with £X risk"-style instruction, against the *last* saved
   scan (`data/last_scan.json`). If no scan has been run yet, say so and run
   one first.
3. **If `issues` is non-empty, stop before the confirmation block** — report
   the issue(s) and ask whether to adjust risk or skip the trade.
4. **Report MCP/order errors verbatim** — do not retry, reinterpret, or
   suppress them.
5. **Don't fabricate data.** Every number in a card or the commentary must
   trace back to a field in the orchestrator's JSON output.
6. **Flag After Hours / Pre-London sessions explicitly** in commentary per
   spec §10 — note wider spreads / "do not recommend entry" framing for
   After Hours.

---

## Invocation Modifiers

| Command | Behaviour |
|---|---|
| `/Trend-Continuation-Agent` | Default scan — `CORE_INSTRUMENTS` |
| `/Trend-Continuation-Agent --symbols UK100,GER40,US500` | Scan only the listed instruments |
| `/Trend-Continuation-Agent --full-universe` | `CORE_INSTRUMENTS` + `EXTENDED_UNIVERSE` |
| `/Trend-Continuation-Agent --full-universe-all` | All enabled SB symbols (slow — only if explicitly requested) |
| "Enter trade N with £X risk" | Run the Execution Flow (§6) for card N from the last scan |
