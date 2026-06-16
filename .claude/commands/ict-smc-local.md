Run the ICT/SMC pre-session market scanner using the cTrader Local MCP connection to the FTMO account.

**Before running**: cTrader desktop must be open and logged into your FTMO account — the Local MCP server at `127.0.0.1:9876/mcp/` only responds when the app is running. If it's closed, tell the user to open it first then re-run.

## Execute the scan

```bash
cd ICT-SMC-Local-Agent && python main.py
```

The scan fetches 1H + Daily candles for all 32 instruments and takes ~30–60 seconds. All 29 forex/indices/metals/commodities instruments should show `Feed: cTrader` (Tier 1, FTMO account). BTCUSDT/ETHUSDT/SOLUSDT use OKX — expected and correct. If any non-crypto instrument shows a fallback source (e.g. `Feed: cTrader → Twelve Data fallback`), flag it to the user — it means cTrader wasn't reachable for that symbol.

## Arguments

User specified: $ARGUMENTS

- **If `$ARGUMENTS` contains an instrument name** (e.g. GBPUSD, GOLD, SPX, US30): extract and display that instrument's full section from the report only — FVG detail, order blocks, liquidity, trade plan card, COT if available.
- **If `$ARGUMENTS` is empty**: present the condensed summary format below.

## Condensed summary format (when no instrument specified)

Present in this order. **Do not paste the raw report** — the user can ask "show me [SYMBOL] in full" for any instrument drill-down at any time.

---

**SCAN HEADER**
- Timestamp (UK/BST)
- Active session / kill zone
- Instruments on cTrader feed vs fallback (e.g. "29/32 cTrader · 3 OKX")
- Any `⚠ NEWS BLACKOUT` warnings

---

**A+ AND A GRADE SETUPS — full trade cards**
For each FVG graded A+ or A, paste the complete `── TRADE PLAN ──` block exactly as it appears in the report, including Direction, Current price, Entry zone, SL, TP1/TP2/TP3, Size, and Confluences bar.

---

**B GRADE SETUPS — one line each**
Format: `▲/▼ SYMBOL | Entry PRICE→PRICE | SL PRICE | TP★ PRICE [R:R X:1] | Conf X/9`

---

**NO ACTIONABLE SETUP — one line each**
Format: `SYMBOL — no setup (C/SKIP)` or `SYMBOL — no unmitigated FVGs`

---

**ECONOMIC CALENDAR — next 12h**
List upcoming HIGH-impact news events from the report's calendar section that could affect open setups.

---

This condensed format surfaces only what the user needs to make a trading decision while keeping token usage low.
