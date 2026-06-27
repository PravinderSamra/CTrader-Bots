Run the ICT/SMC pre-session market scanner using the cTrader Remote MCP connection (Pepperstone demo account via https://mcp.ctrader.com). This agent works from anywhere — no cTrader desktop app required.

## Execute the scan

Run this command: `cd ICT-SMC-Remote-Agent && python main.py`

The scan fetches 1H + Daily candles for all 32 instruments and takes ~30-60 seconds. Instruments with source set to ctrader will show Feed: cTrader when the Remote MCP succeeds. If the Remote MCP is unavailable, instruments transparently fall back to Twelve Data or Yahoo Finance (the Feed label will reflect the actual source used). BTCUSDT/ETHUSDT/SOLUSDT use OKX — expected and correct.

Note: this agent connects to the Pepperstone demo account by default. Prices will be close to but not identical to your FTMO account. Use /ict-smc-local for exact FTMO prices when cTrader desktop is open.

## Arguments

User specified: $ARGUMENTS

- If $ARGUMENTS contains an instrument name (e.g. GBPUSD, GOLD, SPX, US30): extract and display that instrument's full section from the report only — FVG detail, order blocks, liquidity, trade plan card, COT if available.
- If $ARGUMENTS is empty: present the condensed summary format below.

## Condensed summary format (when no instrument specified)

Do not paste the raw report. The user can ask "show me [SYMBOL] in full" at any time.

**SCAN HEADER** — timestamp (UK/BST), active kill zone, instruments on cTrader Remote feed vs fallback (e.g. 29/32 cTrader Remote, 3 OKX), any NEWS BLACKOUT warnings.

**A+ AND A GRADE SETUPS** — paste the complete TRADE PLAN block exactly as printed in the report for each A+ or A graded FVG. This includes: Status (ACTIVE/PENDING NEAR/PENDING FAR), Direction, Current price, Entry zone, SL, TP1/TP2/TP3 with PRIMARY marker, Size (mid + worst-case edge), Entry window (kill zone), and Confluences weighted score (e.g. 8.5/12.3 [████████░░░░] (69%)) with each ✓/✗ check listed.

**B GRADE SETUPS** — one line each: SYMBOL direction | Status | Entry zone | SL | TP primary | R:R | Confluences X.X/12.X (Y%)
If NO VIABLE TP flag is set on a B setup, append: ⚠ no viable TP — skip.

**NO ACTIONABLE SETUP** — one line each: SYMBOL — no setup (C/SKIP/filtered)

**ECONOMIC CALENDAR** — list upcoming HIGH-impact news events from the report that could affect open setups.

This condensed format surfaces only what is needed to make a trading decision while keeping token usage low.
