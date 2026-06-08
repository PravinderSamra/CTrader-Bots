# RSI-ADX Rejection Scanner

A scalping agent for the Pepperstone (cTrader) demo spread-betting account. It scans
the same ~32-instrument watchlist used by the other agents in this repo for
**momentum-exhaustion reversals**: RSI at an extreme, ADX rolling over from a recent
peak (the trend that drove price to the extreme is running out of steam), and a
rejection candle (long wick) printing at a meaningful level.

| Setup | Conditions |
|---|---|
| **LONG**  | RSI oversold (≤30) + ADX declining from a recent peak (still >18, i.e. a real trend faded, not chop) + bullish rejection wick (long lower wick) at/near a swing low / support |
| **SHORT** | RSI overbought (≥70) + ADX declining from a recent peak + bearish rejection wick (long upper wick) at/near a swing high / resistance |

This is a **fade-the-exhaustion** model, not a breakout/trend-following one — it looks
for the moment a move runs out of conviction at a level, not the start of a new trend.

---

## Install

```bash
cp "RSI-ADX/AgentSkill.md" ~/.claude/skills/rsi-adx.md
```

Invoke with `/rsi-adx` (see `AgentSkill.md` for modifiers — restrict to an asset
class, request execution, set account size, etc).

---

## How it works (short version)

1. **Scan** — pull M15 candles for every instrument via `mcp__ctrader__get_trendbars`,
   run them through `analysis/indicators.py` (computes RSI(14), ADX(14)/+DI/-DI,
   ADX-peak-decline state, and reads the latest closed candle for a rejection wick).
2. **Shortlist** — keep instruments where RSI is at an extreme AND ADX is declining
   from a recent peak (the two-indicator "exhaustion" gate).
3. **Deep dive** — for shortlisted candidates: confirm on H1, check the rejection
   wick sits at a real swing high/low (not mid-range), check spread, check session
   timing, check volume on the rejection candle, check upcoming news.
4. **Score & rank** — confluence rubric in `ConfluenceGuide.md`; normalise and pick
   the single best setup.
5. **Trade card** — entry, stop, targets, R:R, position size (spread-bet stake/point),
   confidence score, and the specific reasoning.
6. **Execute (optional)** — on your go-ahead, places the order via
   `mcp__ctrader__create_order` with relative SL/TP, and logs it to `TradeLog.md`.

See `AgentSkill.md` for the full pipeline, scoring rubric, instrument table (with
cTrader symbol IDs), and trade-card format. See `ConfluenceGuide.md` for the
reasoning behind each signal and its weight.

---

## Files

| File | Purpose |
|---|---|
| `AgentSkill.md` | The skill definition — install this to `~/.claude/skills/` |
| `ConfluenceGuide.md` | Rationale for every signal and its weight |
| `analysis/indicators.py` | Stdlib-only Python: RSI/ADX/rejection-candle calculator from raw cTrader trendbar JSON |
| `TradeLog.md` | Outcome log — record every trade taken from this agent here |

---

## Connection notes (read before running)

- The `mcp__ctrader__*` tools occasionally return `"session expired"` on the first
  call of a session — just retry once, it reconnects automatically.
- All tradeable symbols on this account end in `_SB` (e.g. `EURUSD_SB`). Use the
  bare name (`EURUSD`) for `--symbol` when running `indicators.py` — it strips the
  suffix internally.
- Prices from `get_trendbars` / `get_spot_prices` are in **pipettes** — `indicators.py`
  auto-detects the divisor from a built-in price-range table (same one used in
  `ctrader-mcp-integration-guide.md`). Prices in `get_positions` / order parameters
  are already display prices — do not convert those.
- Spread-betting position sizing is **stake-per-point**, not lots:
  `volume = round(risk_gbp / stop_distance_points) * 100`, minimum 100, step 100.
  See Lesson 5 of `ctrader-mcp-integration-guide.md` for the full table.
