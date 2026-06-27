Run the ICT/SMC pre-session market scanner using the cTrader Remote MCP connection (Pepperstone demo account via https://mcp.ctrader.com). This agent works from anywhere — no cTrader desktop app required.

## Execute the scan

Run this command: `cd ICT-SMC-Remote-Agent && python main.py`

The script outputs a condensed summary by default. For a full instrument-by-instrument report (high token cost), run `python main.py --full`. Use `python main.py --full` only when the user asks to see all setups in detail or when debugging.

The scan fetches 1H + Daily candles for all 32 instruments and takes ~30-60 seconds. Instruments with source set to ctrader will show Feed: cTrader when the Remote MCP succeeds. If the Remote MCP is unavailable, instruments transparently fall back to Twelve Data or Yahoo Finance (the Feed label will reflect the actual source used). BTCUSDT/ETHUSDT/SOLUSDT use OKX — expected and correct.

Note: this agent connects to the Pepperstone demo account by default. Prices will be close to but not identical to your FTMO account. Use /ict-smc-local for exact FTMO prices when cTrader desktop is open.

## Arguments

User specified: $ARGUMENTS

- If $ARGUMENTS contains an instrument name (e.g. GBPUSD, GOLD, SPX, US30): extract and display that instrument's full section from the report only — FVG detail, order blocks, liquidity, trade plan card, COT if available.
- If $ARGUMENTS is empty: present the condensed summary format below.

## Condensed summary format (when no instrument specified)

The Python script already outputs the condensed format directly — do NOT try to summarise it further. Present it to the user as-is, with this structure:

**SCAN HEADER** — Python outputs this directly (timestamp, kill zone, data sources)

**A+/A SETUPS** — Python outputs full trade cards for top-grade setups. Include these verbatim.

**B SETUPS** — Python outputs one-line summaries with BST rescan times and /ict-smc-remote SYMBOL commands. Include all of these verbatim.

**NO SETUP** — Python outputs these grouped. Include verbatim.

**RESCAN SCHEDULE** — After presenting the output, extract all pending B setups and list their rescan times as a numbered watch-list:
  1. 12:00 BST — EURUSD (PENDING NEAR) → /ict-smc-remote EURUSD
  2. 14:45 BST — GOLD (PENDING FAR, pre-Silver Bullet) → /ict-smc-remote GOLD

When $ARGUMENTS contains a symbol name (rescan): run `python main.py`, extract that instrument's result from the output, and compare it to what was shown in the previous scan in this chat. State whether the setup is PROGRESSING (closer to entry), STALLED (same distance), or DISQUALIFIED (beyond SL, FVG filled wrong direction, or aged out). Then state the next rescan time in BST.
