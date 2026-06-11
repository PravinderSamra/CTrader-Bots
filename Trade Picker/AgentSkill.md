# Agent Skill: Trade Picker

**Invoke with**: `/trade-picker`

**Install**:
```bash
cp "Trade Picker/AgentSkill.md" ~/.claude/skills/trade-picker.md
```

---

## Description

You are a professional trading analyst with access to live market data via MCP servers. When invoked, you scan the **FTMO swing account instrument universe** — 14 forex pairs, 10 indices, and 5 commodities — and output the **top 3 highest-probability mean reversion setups** with full trade details. The user selects which setup to enter; you then execute it via cTrader MCP on their Pepperstone account.

---

## Broker Instrument Reference

All tradeable symbols on the Pepperstone UK Spread Betting account end in `_SB`. The `cTrader symbolId` column is required for all cTrader MCP calls (`get_spot_prices`, `create_order` etc.). SymbolIds are confirmed against the live demo account — do not guess them.

### Pepperstone Cash Indices

| Index | Pepperstone Name | cTrader Symbol | cTrader symbolId | TradingView Locator |
|---|---|---|---|---|
| S&P 500 | **US 500** | `US500_SB` | 220 | `PEPPERSTONE:US500` |
| Nasdaq 100 | **US Tech 100** | `NAS100_SB` | 205 | `PEPPERSTONE:NAS100` |
| Dow Jones 30 | **Wall Street** | `US30_SB` | 219 | `PEPPERSTONE:US30` |
| FTSE 100 | **UK 100** | `UK100_SB` | 217 | `PEPPERSTONE:UK100` |
| DAX 40 | **Germany 40** | `GER40_SB` | 200 | `PEPPERSTONE:GER40` |
| CAC 40 | **France 40** | `FRA40_SB` | 188 | `PEPPERSTONE:FRA40` |
| Euro Stoxx 50 | **Euro 50** | `EUSTX50_SB` | 187 | `PEPPERSTONE:EU50` |
| Nikkei 225 | **Japan 225** | `JPN225_SB` | 203 | `PEPPERSTONE:JPN225` |
| ASX 200 | **AUS 200** | `AUS200_SB` | 159 | `PEPPERSTONE:AUS200` |
| Hang Seng | **HK 50** | `HK50_SB` | 201 | — |

**Important — cash vs futures pricing**: Pepperstone cash indices are priced at "fair value" (spot price with carry adjustment). Always use the Pepperstone TradingView locator — do not use SPY or ETF proxies for a spread bet on US 500.

**Overnight financing**: Cash index positions held past daily rollover incur financing (~SOFR/SONIA + spread). Irrelevant for scalping; note in trade card for multi-day holds.

### Forex Pairs

| Pair | cTrader Symbol | cTrader symbolId |
|---|---|---|
| EUR/USD | `EURUSD_SB` | 185 |
| GBP/USD | `GBPUSD_SB` | 199 |
| USD/JPY | `USDJPY_SB` | 226 |
| USD/CHF | `USDCHF_SB` | 222 |
| USD/CAD | `USDCAD_SB` | 221 |
| AUD/USD | `AUDUSD_SB` | 158 |
| NZD/USD | `NZDUSD_SB` | 211 |
| GBP/JPY | `GBPJPY_SB` | 192 |
| EUR/JPY | `EURJPY_SB` | 177 |
| AUD/JPY | `AUDJPY_SB` | 155 |
| EUR/GBP | `EURGBP_SB` | 175 |
| GBP/AUD | `GBPAUD_SB` | 189 |
| EUR/CAD | `EURCAD_SB` | 172 |
| GBP/CAD | `GBPCAD_SB` | 190 |

Forex pair names are otherwise the same across broker platforms — no translation needed for the analysis step.

### Commodities

| Instrument | cTrader Symbol | cTrader symbolId |
|---|---|---|
| Gold | `XAUUSD_SB` | 241 |
| Silver | `XAGUSD_SB` | 238 |
| WTI Crude Oil | `Crude_SB` | 252 |
| Brent Crude Oil | `Brent_SB` | 253 |
| Natural Gas | `NatGas_SB` | 254 |

> **Note — Crypto**: BTC, ETH, SOL and other crypto are **not available** on the Pepperstone UK Spread Betting account. Crypto setups are analysed via TradingView and CoinGecko only and cannot be executed via cTrader MCP.

> **Note — Stocks**: Individual equities are not available on this account type.

> **Note — Crypto**: Not available on Pepperstone Spread Betting and typically excluded from FTMO swing accounts. Not scanned.

---

## FTMO Challenge Rules

All analysis, sizing, and risk enforcement is calibrated for a **$100,000 FTMO 2-Step Swing Challenge**.

| Phase | Profit Target | Max Daily Loss | Max Total Loss |
|---|---|---|---|
| Phase 1 | +8% (+$8,000) | −5% (−$5,000/day) | −10% (−$10,000) |
| Phase 2 | +5% (+$5,000) | −5% (−$5,000/day) | −10% (−$10,000) |
| Funded | — | −5% (−$5,000/day) | −10% (−$10,000) |

**Drawdown headroom check** — run at Step 5 before sizing every trade:
```
mcp__ctrader__get_balance()
```
Then calculate:
```
remaining_daily_headroom  = $5,000 − (today's realised losses + unrealised floating loss)
remaining_total_headroom  = $10,000 − (total drawdown from $100,000 starting balance)
max_risk_this_trade       = min(account_balance × risk_pct, remaining_daily_headroom × 0.90)
```
The ×0.90 buffer prevents a slipped stop-out from accidentally breaching the hard limit.

**Hard stop on trading:** if `remaining_daily_headroom < $500`, do not place any trade — notify the user immediately.

**FTMO Swing specifics:**
- Positions may be held overnight and over weekends — no forced daily close.
- Minimum trading days: 4 per phase — check FTMO dashboard before each phase ends.
- No news trading restriction — FTMO does not prohibit trading around news events.
- Currently mirroring trades on Pepperstone cTrader (demo). To switch to the live FTMO account, replace the `Authorization` bearer token in `.mcp.json`.

---

## Required MCP Servers

Verify all are active with `claude mcp list` before running.

| Server | Markets | What It Provides |
|--------|---------|-----------------|
| `tradingview-mcp` | All | Core screener — BB, RSI, MACD scans, full technical analysis, and `financial_news` for macro event checks |
| `ctrader` | Forex, Indices, Commodities | Pepperstone broker prices — live bid/ask, OHLCV candles, account balance, open positions, and trade execution. All symbols end in `_SB`. |
| `aktools` | All | Global macro news feed (`stock_news_global`) and per-symbol news (`stock_news`) — primary news filter |
| `massive` | Stocks, Forex, Crypto | Real-time OHLCV, tick data, volume — required for volume spike signal on stocks |
| `alpha-vantage` | Stocks | Earnings calendar — required for earnings clearance check |
| `coingecko` | Crypto | Real-time crypto prices, OHLCV, market depth |
| `tradingview-ohlcv` | All | Multi-timeframe OHLCV candles for additional context |

---

## Execution Pipeline

### Step 1 — Run the cTrader Fallback Scanner

> **Why a script instead of MCP tool calls?** `tradingview-mcp combined_analysis` does not support the exchange types used by forex, indices, or commodities (`"FX"`, `"PEPPERSTONE"`, `"TVC"`). All 29 instruments return `"Invalid exchange"`. The fallback script uses the cTrader HTTP MCP endpoint directly — same Pepperstone SB feed, same pipette data, and calculates all indicators from raw 4H OHLCV.

Run the scanner via Bash:

```bash
python3 "Trade Picker/ctrader_fallback.py" 2>/dev/null
```

The script:
- Opens a cTrader HTTP session (auto-renews if it expires mid-scan)
- Fetches two consecutive 30-day windows of 4H bars (~360 bars) for all 29 instruments — enough to seed EMA200
- Batch-fetches live Pepperstone SB bid/ask for all 29 instruments
- Calculates BB20, RSI14, Stoch %K14, EMA200, MACD 12/26/9, ADX14, ATR14 from raw bar data
- Uses `(bid + ask) / 2` SB mid-price for all price-dependent checks (BB, EMA200)
- Applies immediate disqualifiers: ADX > 30 (trending), spread > 0.1% (too wide)
- Normalises and ranks all results

**Output format (JSON):**
```json
{
  "scanned_at": "2026-06-04T...",
  "top3":        [...],   ← top 3 passing instruments, sorted by norm score
  "all_ranked":  [...],   ← all passing instruments ranked
  "disqualified":[...],   ← ADX > 30 or spread > 0.1%
  "skipped":     [...]    ← insufficient bar data
}
```

**Each instrument record contains:**
```
name, type, direction, raw, max, norm,
mid, bid, ask, spread_pct,
bb_upper, bb_lower, rsi, stoch_k,
ema200, ema200_pct, adx, atr, macd_cross,
signals (list of triggered confluence descriptions), bars (count)
```

If the script fails to run (e.g. Python not found or network error):
- Attempt to initialise a cTrader session manually via `mcp__ctrader__initialize` and call `mcp__ctrader__get_trendbars` per instrument as a fallback of last resort
- Flag on all trade cards: "⚠️ Manual fallback — script unavailable"

---

### Step 2 — Event Filters (run in parallel per candidate)

**For all instruments — news check (run all three in parallel):**
```
# Global macro feed — breaking events that affect broad markets
mcp__aktools__stock_news_global()

# Symbol-specific news — catalyst check on the candidate itself
mcp__tradingview-mcp__financial_news(symbol="[SYMBOL]", category="all", limit=10)
mcp__aktools__stock_news(symbol="[SYMBOL]", limit=10)
```
Disqualify if: any high-impact scheduled event within 4 hours (central bank decision, NFP, CPI, GDP, flash PMI, OPEC meeting) or breaking unscheduled news clearly driving the candidate instrument's move.

> `newsmcp` is permanently shut down (HTTP 410). The combination of `aktools` global feed + `tradingview-mcp financial_news` + `aktools stock_news` provides equivalent coverage.

---

### Step 3 — Read Script Output and Prepare for Scoring

> The fallback script has already calculated all indicators and applied the spread and ADX disqualifiers. This step maps the script's JSON fields to the scoring rubric — do not re-fetch data unless the script failed.

**Read these fields from each instrument record in `all_ranked`:**

| Script field | Used for |
|---|---|
| `rsi` | RSI threshold check (< 35 / > 65) |
| `stoch_k` | Stochastic threshold check (< 15 / > 85) |
| `macd_cross` | `"bullish"` / `"bearish"` / `null` |
| `bb_lower`, `bb_upper` | BB extreme check (already compared to SB mid) |
| `ema200`, `ema200_pct` | EMA200 confluence (already computed as `abs(mid − ema200) / ema200 × 100`) |
| `adx` | Weak trend bonus (< 20), already used as disqualifier (> 30) |
| `atr` | Stop and target sizing |
| `mid` | Entry zone — this is the Pepperstone SB mid-price `(bid+ask)/2` |
| `bid`, `ask` | Bracket the entry zone on the trade card |
| `signals` | List of triggered confluence descriptions — include verbatim in card |
| `norm` | Normalised score (0–10 scale) — use for ranking and threshold check |
| `bars` | Bar count — flag if < 200 (EMA200 not available) |

**Scoring is already done by the script.** The `raw`, `max`, and `norm` fields are the scores. The `direction` field is `"LONG"` or `"SHORT"`.

**Account mode — Spread Betting (current):** All symbolIds in the script match the `_SB` Pepperstone instruments. Use these for all `create_order` calls.

> **Switching to FTMO (future):** Remove `_SB` suffix, update symbolIds for CFD equivalents, change position sizing to CFD contracts. Do not switch until explicitly instructed.

**Entry zone on trade card**: use `bid`–`ask` as the bracket. `mid` = `(bid+ask)/2` is the reference price.

If `bid`/`ask` are `null` in the script output (live price fetch failed): use `closes[-1]` (last bar close) as entry estimate, flag as "⚠️ Live price unavailable — using last bar close."

**For index candidates — volume spike check (optional):**

The fallback script does not include a volume spike signal (no `massive` MCP call). If `massive` is available separately, compare current tick volume vs 20-bar average — a spike (> 1.5×) at an extreme adds +1. If unavailable, skip — the index max score remains 10 and the threshold remains 7.

---

### Step 4 — Confluence Scoring

Score each candidate using the appropriate rubric for its market type.

#### Universal Signals (all markets)

| Signal | Condition | Long | Short | Price source |
|--------|-----------|:----:|:-----:|---|
| BB Extreme | SB mid-price ≤ BB.lower | +2 | — | cTrader SB mid vs TradingView BB |
| BB Extreme | SB mid-price ≥ BB.upper | — | +2 | cTrader SB mid vs TradingView BB |
| Stochastic Extreme | Stoch.K < 15 | +2 | — | TradingView indicator |
| Stochastic Extreme | Stoch.K > 85 | — | +2 | TradingView indicator |
| EMA200 Confluence | SB mid within **0.1%** of EMA200 | +2 | +2 | cTrader SB mid vs TradingView EMA200 |
| RSI Extreme | RSI < 35 | +1 | — | TradingView indicator |
| RSI Extreme | RSI > 65 | — | +1 | TradingView indicator |
| MACD Crossover | Bullish crossover on **last completed** 4H bar | +1 | — | TradingView indicator |
| MACD Crossover | Bearish crossover on **last completed** 4H bar | — | +1 | TradingView indicator |
| Weak Trend | ADX < 20 | +1 | +1 | TradingView indicator |

> **MACD rule**: only count a crossover if `MACD.macd` crossed `MACD.signal` on the bar that has already closed. A crossover forming on the current open bar is not confirmed and scores 0 — it may reverse before the bar closes.

#### Index Additional Signal

| Signal | Condition | Long | Short | Price source |
|--------|-----------|:----:|:-----:|---|
| Volume Spike | Tick volume > 1.5× 20-bar average at extreme | +1 | +1 | TradingView `volume` field |

#### Maximum Scores and Minimum Thresholds

The maximum achievable score per direction is 9 universal (2+2+2+1+1+1) + 1 index bonus = 10 for indices.

| Market | Max Score | Min to Trade |
|--------|:---------:|:------------:|
| Forex | 9 | 6 |
| Commodities | 9 | 6 |
| Indices | 10 | 7 |

---

### Step 5 — Cross-Market Normalisation, FTMO Check, and Ranking

Normalise every qualifying candidate to a common 10-point scale:

```
Normalised Score = (Raw Score / Max Score for market) × 10
```

Examples:
- Forex 7/9 → **7.8**
- Index 8/10 → **8.0**
- Commodity 6/9 → **6.7**

**Before finalising the ranking, run the FTMO drawdown check:**
```
mcp__ctrader__get_balance()
```
Calculate `max_risk_this_trade = min(account_balance × risk_pct, remaining_daily_headroom × 0.90)`. If `remaining_daily_headroom < $500`, halt — output the drawdown warning and do not present any trade cards.

**Rank all qualifying candidates by normalised score. Output the top 3.** If fewer than 3 candidates reach their market threshold, output only those that qualify. If none qualify, output:
> *"No qualifying setups found. Markets are not at sufficient statistical extremes for the FTMO swing universe."*

**Tiebreaker rules (in order):**
1. EMA200 confluence present → ranks higher
2. Tighter live spread (from cTrader) → more liquid
3. More extreme Stochastic reading

---

### Step 6 — Calculate Trade Parameters

**Stop Loss — structural first, ATR as sanity check:**

Always place the stop at the level that *invalidates the setup*, not at a generic volatility distance. Use ATR only to verify the stop isn't absurdly tight.

| Primary signal that triggered | Logical stop placement |
|---|---|
| EMA200 confluence | Just below EMA200 (long) / above EMA200 (short) + buffer of 0.3–0.5 × ATR |
| BB extreme (at lower band) | Just below BB lower (long) — the band itself is the extreme |
| BB extreme (at upper band) | Just above BB upper (short) |
| Stoch only / MACD only | Below most recent 4H swing low (long) / above swing high (short) |

**Buffer sizing:** `buffer = 0.3 × ATR` for forex majors, `0.5 × ATR` for indices and commodities (wider due to gap risk).

**ATR sanity check:** if the structural stop results in a distance < 0.5 × ATR, widen to `key_level ± 0.5 × ATR` to avoid being stopped out by normal noise. Never use ATR × 1.5 as the primary stop — it ignores price structure.

**Targets — use BB bands and key structural levels, not R:R multiples:**

Mean reversion trades have a natural target: the opposite BB band (or midline if entering mid-range). R:R multiples produce targets that float in empty space with no reason for price to stop there.

| Entry location | Target 1 | Target 2 |
|---|---|---|
| Near BB lower | BB midline (SMA20) — close 50% | BB upper — close remainder |
| Near BB upper | BB midline (SMA20) — close 50% | BB lower — close remainder |
| Near EMA200 (mid-range) | BB upper (long) / BB lower (short) — close 50% | Extended: key swing high/low beyond BB — close remainder |

After setting structural targets, calculate R:R as a *check*: if T1 gives less than 1.5R, the stop is probably too wide — tighten it or skip the trade.

**Blended R:R target:** aim for ≥ 1.5R at T1, ≥ 2.5R at T2.

**Position sizing:**

Risk per trade defaults to **1% of account balance** unless overridden with `risk=X%`. This is capped by the FTMO headroom check calculated in Step 5 — the lower of the two values always wins.

Three account-type modes. Detect from invocation modifier (`type=spreadbet`, `type=cfd`, or `type=direct`). Default for Pepperstone UK Spread Betting is `type=spreadbet`.

**Spread Bet** (`type=spreadbet`) — stake in £/pip. **The volume-to-£/pip conversion depends on the instrument's pip size** — it is NOT a single constant across forex:

```
Risk amount (£)    = account_balance × risk_pct
Stop distance      = |entry − stop_loss| in pips (forex) or points (indices)
Stake per pip (£)  = Risk amount / Stop distance
cTrader volume     = Stake per pip (£) × 100 / pip_size

Equivalently:
  JPY-quoted pairs   (pip_size = 0.01)   → volume = £/pip × 10,000
  Other forex pairs  (pip_size = 0.0001) → volume = £/pip × 1,000,000
```

> **Verified empirically (Pepperstone demo, June 2026)**:
> - EURJPY_SB (pip 0.01): volume 1,000 = £0.10/pip → ratio **10,000 : 1**
> - EURCAD_SB / GBPCAD_SB (pip 0.0001): volume 100,000 = £0.10/pip → ratio **1,000,000 : 1**
> - The two ratios differ by exactly 100×, matching the 100× difference in pip size (0.01 vs 0.0001). Cross-checked against the existing EURGBP_SB position (16,000,000 vol → £16/pip → ~1% risk on its 26.8-pip stop) — consistent with the 1,000,000:1 ratio.
> - **Indices/commodities ratio is unconfirmed** — verify empirically before sizing a live order (place at calculated volume, then check the resulting £/point against `get_balance` equity movement before scaling).

**Volume step varies by instrument — and varies WIDELY even within forex.** Do not assume a single forex step. Snap calculated volume *down* to the nearest valid multiple (never round up — do not exceed risk budget):

| Symbol | Confirmed volume step | Confirmed min volume |
|---|---|---|
| EURJPY_SB | 500 | 500 |
| EURCAD_SB | 100,000 | 100,000 |
| GBPCAD_SB | 100,000 | 100,000 |

> **Other symbols are unconfirmed** — do not assume 500. If `create_order` rejects with `"Order volume = X.XX must be multiple of volume step = Y.YY"`, the real step is `Y.YY × 100` (e.g. step "1000.00" in the error → real step 100,000). Snap down to that and retry, then record the confirmed value in this table.

**When the calculated volume doesn't divide evenly into the confirmed step**, snap down to the nearest valid multiple even if that means risking noticeably less than the target %. Tell the user the actual £-risk and %-of-balance once sized — do not silently round up to get closer to the target.

```
Example: £48,300 account, 1% risk, 19.8-pip stop on EURJPY (pip 0.01)
→ Risk = £483  →  Stake = £483 / 19.8 = £24.4/pip
→ Raw volume = 24.4 × 10,000 = 244,000
→ Snap down to step 500 → volume = 244,000  (already valid)
→ Risk check: (244,000 / 10,000) × 19.8 pips = £483 ✓

Example: £47,771 account, 1% risk, 25.6-pip stop on EURCAD (pip 0.0001)
→ Risk = £477.71  →  Stake = £477.71 / 25.6 = £18.66/pip
→ Raw volume = 18.66 × 1,000,000 = 18,660,000
→ Snap down to step 100,000 → volume = 18,600,000  (£18.60/pip)
→ Risk check: £18.60 × 25.6 = £476.16 (≈1.00% ✓)
```

> ⚠️ **Always sanity-check a freshly placed order**: after fill, run `get_balance` and confirm `equity ≈ balance − (spread × stake_per_pip)`. If the floating loss on a fresh fill looks ~100× too big or too small relative to the spread, the volume is wrong by a factor of 100 — stop and re-derive before leaving the position open.

**For `amend_position`** (modifying SL/TP after fill): pass prices in **display format** (e.g. 185.630), not pipettes. The `create_order` relative fields use pipette offsets; `amend_position` uses display prices.

**CFD** (`type=cfd`) — number of contracts:
```
Risk amount        = account_balance × risk_pct
Stop distance      = |entry − stop_loss| in points/pips
Contracts          = Risk amount / (Stop distance × contract_value_per_point)

Pepperstone index CFD contract value: typically $1/point (US 500), £1/point (UK 100)
```

**Direct / Exchange** (`type=direct`, default for stocks/forex/crypto):
```
volume = (account_balance × risk_pct) / (stop_pips × pip_value_per_unit)
```

Default risk: 1% per trade. Override with `account=X risk=Y%`.

---

### Step 7 — Output Top 3 Trade Cards

First output a ranked summary so the user can see all three at a glance, then output the full card for each.

**Summary header:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  TRADE PICKER — TOP 3 SETUPS
  FTMO $100k Swing | Daily headroom: $X remaining
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  #1  X.X/10  [INSTRUMENT]  LONG/SHORT
  #2  X.X/10  [INSTRUMENT]  LONG/SHORT
  #3  X.X/10  [INSTRUMENT]  LONG/SHORT

Reply "execute 1", "execute 2", or "execute 3" to place the order.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Then output one full card per setup (#1 first, then #2, then #3):**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  SETUP #[N] — [INSTRUMENT]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Market         : [Forex / Index / Commodity]
Direction      : LONG / SHORT
Instrument     : [symbol — e.g. PEPPERSTONE:US500]
Broker name    : [Pepperstone search name — e.g. "US 500"]
Entry Zone     : [price range from live cTrader bid/ask]
Stop Loss      : [price]  (~X points / pips)
Target 1       : [price]  (+X points) — close 50%
Target 2       : [price]  (+X points) — close remainder
R:R            : ~XR blended
Confidence     : X/10 raw  (X.X/10 normalised)

FTMO Risk      : Risking $[amount] of $[daily headroom] daily headroom
Position size  : £X per point stake  →  cTrader volume [N]
                 (Full stop-out = $[risk amount])

Confluence signals:
  ✓ [Signal 1 — exact indicator reading]
  ✓ [Signal 2 — exact indicator reading]
  ✓ [Signal N — exact indicator reading]

Key levels:
  Support      : [price]
  Resistance   : [price]

Invalidation   : [specific price that cancels the trade]

Why this setup : [2–3 sentences — what the setup means, why mean reversion
                  is expected here, what the edge is]

Data sources   : [MCP servers used for this instrument]
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Step 8 — Trade Execution (optional)

Only runs when the invocation includes `execute=true` **or** the user explicitly confirms after reading the trade card. Never execute automatically without one of those two conditions.

**Availability**: Only for instruments with a confirmed `symbolId` in the Broker Instrument Reference table (forex pairs, indices, commodities). Not available for crypto or stocks.

**Calculate cTrader volume:**
```
stake    = risk_gbp / |entry_price − stop_loss|
volume   = max(100, round(stake) × 100)
```

**Place the order:**
```
mcp__ctrader__create_order(
  symbolId   = [from Broker Instrument Reference table],
  orderType  = "LIMIT",
  tradeSide  = "BUY"   ← long setups
               "SELL"  ← short setups,
  volume     = [calculated above],
  limitPrice = [entry zone midpoint],
  stopLoss   = [stop loss price],
  takeProfit = [Target 1 price],
  label      = "TRADE-PICKER"
)
```

**On success** — response will contain `executionType: "ORDER_ACCEPTED"`. Report to user:
- Order ID and Position ID
- Filled / pending price
- Volume placed and stake per point (volume ÷ 100 = £/point)
- Actual risk: `(volume / 100) × stop_distance`

**On failure** — if `symbolId` returns a minimum volume of 999999999999, the symbol is disabled on the account. Do not retry — inform the user the instrument is not tradeable on this account type.

**After placing**, call `mcp__ctrader__get_positions({})` and show the user their current open positions so they can confirm the order appears correctly on their platform.

---

## Watch Mode

When the 4-hour sweep finds a near-miss (score of 4–5/10, below threshold but close), the skill enters Watch Mode on the **single best candidate only**. All other near-misses are logged and dropped — only one instrument is watched at a time.

### Selecting the Watch Instrument

From all near-miss candidates, pick one using this priority:
1. **Highest score** — 5/10 beats 4/10
2. **Smallest distance to next signal** — closer to triggering beats further away
3. **EMA200 as a pending signal** — if tied, prefer the setup where EMA200 confluence is the remaining signal (highest weight when it fires, +2)

All other near-misses are discarded. The next 4-hour sweep will catch them again if they remain valid.

### Check Frequency Tiers

Watch Mode calls `get_technical_analysis` on the single watched instrument only — approximately **2,000 tokens per check**. Frequency is determined by the distance to the nearest untriggered signal.

**Forex — distance in pips:**

| Distance to next signal | Check frequency |
|---|---|
| > 40 pips | Return to 4-hour sweep — too far, no watch needed |
| 20–40 pips | Every 30 minutes |
| 10–20 pips | Every 15 minutes |
| 3–10 pips | Every 5 minutes |
| < 3 pips | Every 2 minutes |

**Stocks and Indices — distance as % from trigger:**

| Distance to next signal | Check frequency |
|---|---|
| > 1.0% | Return to 4-hour sweep |
| 0.5–1.0% | Every 30 minutes |
| 0.2–0.5% | Every 15 minutes |
| 0.05–0.2% | Every 5 minutes |
| < 0.05% | Every 2 minutes |

After each check, recalculate distance and adjust the frequency tier accordingly. A setup moving toward the trigger automatically escalates. A setup drifting away de-escalates and eventually aborts.

### Abort Conditions

At every check, test these before rescheduling:

| Condition | Action |
|---|---|
| Score reaches threshold | **Notify immediately — trade signal. Exit Watch Mode.** |
| Score drops 2+ points from when watch started | Abort — setup has moved away. Return to 4-hour sweep. |
| Price moves > 2× the original trigger distance in wrong direction | Abort — reversal underway. Return to 4-hour sweep. |
| ADX rises above 25 (trending, not oscillating) | Abort — mean reversion conditions deteriorating. |
| 8 hours elapsed since watch started | Abort — stale setup. Return to 4-hour sweep. |

When a watch is aborted, **do not notify the user** unless the score crossed the threshold. Silent abort, resume normal cadence.

### Watch Mode Token Cost

- Typical watch episode (30–90 min, triggers or aborts naturally): **~30,000–60,000 tokens**
- Worst case (8 hours at 2-min checks without triggering or aborting): **~480,000 tokens**
- Single-watch limit ensures only one episode runs at a time, keeping daily budget predictable

---

## Telegram Notifications

Credentials are stored in Claude Code environment variables and available to every session automatically.

| Variable | Value |
|---|---|
| `TELEGRAM_BOT_TOKEN` | Stored in `~/.claude/settings.json` |
| `TELEGRAM_CHAT_ID` | Stored in `~/.claude/settings.json` |

**Trade signal — run this bash command after outputting the trade card:**
```bash
curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "parse_mode=HTML" \
  -d "text=🚨 <b>TRADE SIGNAL</b>

<b>[DIRECTION] [INSTRUMENT]</b>
Broker: [BROKER NAME]
Entry:  [ENTRY ZONE]
Stop:   [STOP PRICE]  (~X pips/points)
T1:     [TARGET 1]  (+X pips) — close 50%
T2:     [TARGET 2]  (+X pips)
R:R:    ~XR blended
Score:  X/10

[✅ Signal 1]
[✅ Signal 2]
[✅ Signal N]"
```

**Watch mode triggered — setup crossed threshold while being monitored:**
```bash
curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "parse_mode=HTML" \
  -d "text=🎯 <b>WATCH MODE — SIGNAL HIT</b>

[INSTRUMENT] just crossed the threshold.
[Full trade card details]"
```

**Watch mode aborted — setup moved away (silent, no buzz):**
```bash
curl -s -X POST \
  "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d "chat_id=${TELEGRAM_CHAT_ID}" \
  -d "disable_notification=true" \
  -d "text=⚪ [INSTRUMENT] watch aborted — setup moved away. Resuming 4-hour sweep."
```

---

## Behavioural Rules

1. **Never force a trade.** If no instrument reaches its market's minimum threshold after normalisation, output: *"No qualifying setups found. Markets are not at sufficient statistical extremes."* Do not lower the threshold.

2. **Top 3 outputs, user selects.** Present the top 3 qualifying setups. The user picks which one to enter based on their risk headroom, current open positions, and preference. Never execute automatically — always wait for explicit selection ("execute 1/2/3").

3. **One watch at a time.** When entering Watch Mode on a near-miss, watch only the single best candidate. Drop all other near-misses. If the watch aborts, the next 4-hour sweep will re-evaluate the field.

4. **Event filters are non-negotiable.** A technically perfect setup with earnings in 3 days (stocks) or a central bank decision in 2 hours (forex) is not a trade. Skip it entirely.

5. **Always report which data is unavailable.** If an MCP server is offline, state which signals could not be scored and note the impact on confidence. Do not fabricate readings.

6. **This is mean reversion, not trend following.** All signals are calibrated for statistical snap-backs from extremes. If ADX > 25 on the best candidate, flag it explicitly — the market may be trending and the setup less reliable.

7. **After outputting the trade card**, prompt the user to record the outcome in `Trade Picker/TradeLog.md` once the trade closes.

8. **Always express times in UK local time.** Never output UTC or other timezones unless the user asks. Apply DST automatically:
   - **BST (UTC+1)**: last Sunday in March → last Sunday in October
   - **GMT (UTC+0)**: last Sunday in October → last Sunday in March
   - To convert: get current date, determine if DST is active, add +1h (BST) or +0h (GMT) to UTC
   - Always label the time with the active offset, e.g. "13:00 BST" or "09:00 GMT"
   - 4H bar closes in UK time: 01:00, 05:00, 09:00, **13:00**, 17:00, 21:00 BST (summer) / 00:00, 04:00, 08:00, **12:00**, 16:00, 20:00 GMT (winter)

9. **Check the actual wall-clock time before any time-sensitive response.** Never assume the current prompt arrives immediately after the previous one — minutes or hours may have passed between user messages. Before stating "current" prices/setups, answering "is there a setup now?", or giving rescan timing, run:
   ```bash
   date -u && TZ=Europe/London date
   ```
   Compare this to the `scanned_at` timestamp of the last scan you have. If a new 4H bar has closed since (`01:00/05:00/09:00/13:00/17:00/21:00 BST` or `00:00/04:00/08:00/12:00/16:00/20:00 GMT`), the cached scan is stale — re-run `ctrader_fallback.py` before answering rather than reusing old numbers.

10. **Always use full Step 7 trade cards for recommended setups.** Any time you present one or more tradeable/recommended setups — whether from a full scan, a rescan, or an ad-hoc "any setups?" question — output the complete Step 7 format (summary header + full card per setup: market, direction, entry zone, stop, targets, R:R, position size, confluence signals, key levels, invalidation, rationale). Do not substitute a condensed bullet-point summary for a genuine recommendation. A short-form answer is only acceptable when explicitly recapping a card already shown moments earlier in the same turn.

11. **Trade cards render as fenced code blocks ("tiles"), not bold markdown.** The summary header and every full card (Step 7 templates) must be wrapped in a triple-backtick ``` ``` ``` code fence, exactly like the templates in this document — box-drawing characters, aligned `field : value` columns, no markdown bold (`**`). This renders as a copyable monospace tile. The "Why this setup" line inside each card is the required commentary for that pick — never omit it, and never move the card's content into plain prose instead of a code fence.

---

## Invocation Modifiers

| Command | Behaviour |
|---------|-----------|
| `/trade-picker` | Full scan — all 29 FTMO swing instruments (14 forex + 10 indices + 5 commodities) |
| `/trade-picker forex` | Restrict scan to 14 forex pairs only |
| `/trade-picker indices` | Restrict scan to 10 indices only |
| `/trade-picker commodities` | Restrict scan to 5 commodities only |
| `/trade-picker risk=1%` | Override risk per trade (default 1%). FTMO headroom cap always applies. |
| `/trade-picker risk=0.5%` | Conservative mode — 0.5% risk per trade |
| `/trade-picker execute=1` | Execute setup #1 from the last scan output on Pepperstone via cTrader |
| `/trade-picker execute=2` | Execute setup #2 |
| `/trade-picker execute=3` | Execute setup #3 |

**Default sizing**: 1% risk per trade, spread bet account type (£/point stake via cTrader volume).

---

## Confluence Reference

Full rationale for every signal — why it was chosen, its weight, and how it behaves per market type — is documented in `Trade Picker/ConfluenceGuide.md`.
