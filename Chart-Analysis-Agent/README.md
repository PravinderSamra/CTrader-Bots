# SMC/ICT Chart Analysis Agent

A standalone web-based chart analysis agent powered by Claude claude-sonnet-4-6, implementing the full ICT/SMC framework as specified in *SMC/ICT Master Reference v1.0* (Parts 16 & 17).

## How to Use

1. Open `index.html` directly in any modern browser — no install or build step required.
2. Enter your Anthropic API key (available at console.anthropic.com).
3. Upload a chart screenshot (TradingView, MT4/5, cTrader, or any broker platform).
4. Click **Analyse Chart** and wait 10–20 seconds.
5. Review the structured ICT/SMC analysis output.

## Features

### Core Analysis (Part 16 System Prompt)
- Full 6-step ICT analysis protocol (Structure → Liquidity → PD Arrays → Premium/Discount → Time Context → MTF)
- Probability scoring using the documented +/- rules (base 50%, capped at 92%)
- Structured output: Regime Assessment, Market Structure, Liquidity Map, PD Arrays, Trade Ideas, Market Narrative
- Color coding: **GREEN** bullish · **RED** bearish · **GOLD** key levels

### UI Features (Part 17 Spec)
- Dark theme: `#0D1117` background · `#F0B429` gold accent · `#E6EDF3` text
- Chart image upload with drag-and-drop support
- Visual probability progress bars
- Trade idea cards with Entry / Stop / Target clearly displayed
- Loading spinner during API call
- Reset button to clear and analyse a new chart
- Error handling with user-friendly messages

### Additional Features (Part 17.5)
- **Trade Journal** — save analyses with timestamps and chart thumbnails, view or delete entries
- **Session Clock** — live New York / London / Tokyo time with active kill zone indicator and macro window display
- **Level Calculator** — enter Account Size, Risk %, Entry, and Stop Loss to compute position size and R:R ratio
- **Probability Comparison** — primary vs alternative scenario displayed side-by-side with colour-coded bars

## Architecture

| Layer | Detail |
|---|---|
| Framework | React 18 (CDN UMD) + Babel Standalone (JSX in-browser) |
| Styling | Tailwind CSS Play CDN + inline styles |
| API | Anthropic `/v1/messages` — `claude-sonnet-4-6` |
| Image | Base64 via `FileReader` API, passed as vision content block |
| Storage | None — all state in React `useState`, no localStorage |
| Tokens | `max_tokens: 4000`, `temperature: 0` |

## API Key Security

The API key is held in React state only (browser memory). It is never written to disk, localStorage, or sent anywhere other than `api.anthropic.com`. Closing the browser tab clears it entirely.

## ICT Concepts Covered

Market Structure (BOS/CHoCH/MSS) · Liquidity (BSL/SSL/Sweeps/DOL) · PD Arrays (OB/FVG/BB/MB/BPR) · Premium/Discount/OTE · Kill Zones & Macros · AMD / Power of Three · Silver Bullet · Protected Highs/Lows & Regime Change · IPDA Look-back Periods · Multi-Timeframe Analysis
