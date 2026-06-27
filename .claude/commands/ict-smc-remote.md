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

Run `python main.py`, then present the output with this structure:

**SCAN HEADER** — Present the Python header verbatim (timestamp, kill zone, data sources, news).

**A+/A SETUPS** — For each A+ or A grade setup:
1. Present the trade card verbatim exactly as Python outputs it.
2. Immediately after the card, write an **ADVISOR NOTE** in plain English as an expert ICT/SMC trade advisor. This is the most important part — write it as if you are personally advising the trader on what to do and why. Cover:
   - **The narrative**: What has price done to set this up? (e.g. swept Asian high, ran into premium FVG, daily trend confirms direction). Connect the dots so the trade makes sense as a story.
   - **Why this specific FVG matters**: What structural level or liquidity pool is it sitting at? Why would institutions be interested at this zone?
   - **Exactly how to enter**: Which timeframe to drop to (5m or 15m), what confirmation to look for before pressing the button (e.g. "wait for a bearish engulfing or displacement candle on the 5m after price taps the top of the FVG at [price]"). Be specific — name the price level.
   - **Key risk**: One thing that would invalidate this setup (e.g. "if price closes a 1H candle above the SL level, the setup is dead — do not re-enter").
   - **Position management**: When to take the partial (TP1) and when to move SL to breakeven, in plain language.
   Format the advisor note clearly:

   > **Advisor Note — [SYMBOL] [LONG/SHORT]**
   > [3–6 sentences covering narrative, entry trigger, risk, and position management]

**B SETUPS** — Present the Python one-liner output verbatim for all B setups. No advisor note for B setups.

**NO SETUP** — Present the Python grouped output verbatim.

**RESCAN SCHEDULE** — After presenting all output, list all pending setups (A+/A and B) with their rescan times as a numbered watch-list:
  1. 12:00 BST — EURUSD SHORT (PENDING NEAR) → /ict-smc-remote EURUSD
  2. 14:45 BST — GOLD LONG (PENDING FAR, pre-Silver Bullet) → /ict-smc-remote GOLD

## Rescan (when $ARGUMENTS contains a symbol name)

Run `python main.py`, extract that instrument's section from the output, and:

1. Present the updated trade card verbatim.
2. Write an updated **Advisor Note** as above — but also state explicitly:
   - **Status change**: PROGRESSING (price moved closer to entry), STALLED (same distance), or DISQUALIFIED (price beyond SL, FVG filled in wrong direction, or aged out).
   - If PROGRESSING: update entry trigger with current price context.
   - If DISQUALIFIED: state clearly "Do not trade this setup — [reason]. Remove from watch list."
3. State the next rescan time in BST.
