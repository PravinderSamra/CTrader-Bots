# `/gold-session` Agent Skill

A Claude Code slash command (`.claude/commands/gold-session.md`) that turns Claude into a pre-session ICT/SMC gold (XAUUSD) analyst. It pulls live cTrader market data, the macro snapshot produced by the [XAUUSD Intelligence Dashboard](../xauusd-dashboard/README.md), and the repo's own structure-detection engine, then writes a single structured trade-readiness report to a fixed markdown template.

It is a **read-only analysis tool** — it never places, amends, or closes a trade itself. Execution remains a manual decision by the trader reading the report.

## How it fits together

```
.claude/commands/gold-session.md        The skill prompt: protocol, axioms, output format, scoring rules
ICT-SMC-Local-Agent/
├── skill_adapter.py                    Bridges live cTrader candles into the analysis engine
└── analysis/
    ├── structure.py                    FVG / order block / liquidity-pool / premium-discount detection
    └── sessions.py                     Kill-zone / session-bias detection
xauusd-dashboard/public/data/daily-snapshot.json   Macro context (yields, Fed odds, COT, GVZ, briefing) — see ../xauusd-dashboard/README.md
```

### STEP 0 — data gathering (defined in `gold-session.md`)

STEP 0 is divided into three **parallel phases** based on dependency. Within each phase, all tool calls fire simultaneously in a single response — never serialised within a phase.

#### Phase A (no dependencies — all fire at once)
- `mcp__ctrader__get_symbols` → resolve symbolId for XAUUSD and note `pipDigits`.
- `mcp__ctrader__get_positions` → existing exposure on the symbol.
- `mcp__ctrader__get_balance` → account balance/equity/free margin.
- HTTP fetch of `xauusd-dashboard/public/data/daily-snapshot.json` from GitHub Pages → macro snapshot (yields, COT, ETF flows, Fed odds, GVZ, VIX, GPR, news, calendar). Treat as stale and warn if `generatedAt` is >4h old during London/NY hours.
- `ToolSearch` with `query: "select:mcp__tradingview-mcp__recognize_market_pattern"` → pre-loads the TradingView tool schema so it is callable in Phase C. **This must be in Phase A** — TradingView tools are deferred (schema not loaded until explicitly fetched); calling them without a prior ToolSearch produces `InputValidationError`.

#### Phase B (requires symbolId from Phase A — all fire at once)
- `mcp__ctrader__get_spot_prices` → current bid/ask.
- `mcp__ctrader__get_trendbars` for H1 (100 candles), M5 (100 candles), M1 (60 candles).

  **⚠️ API quirk — always use explicit timestamps:** the `count`-only form of `get_trendbars` fails with `INVALID_REQUEST: fromTimestamp must not be null`. Derive timestamps from the spot price timestamp (`spotTimestamp` = the `timestamp` field returned by `get_spot_prices`, in milliseconds):

  | Timeframe | `fromTimestamp` | `toTimestamp` |
  |---|---|---|
  | H1 | `spotTimestamp - 360_000_000` (100 h back) | `spotTimestamp` |
  | M5 | `spotTimestamp - 30_000_000` (100 × 5 min back) | `spotTimestamp` |
  | M1 | `spotTimestamp - 3_600_000` (60 min back) | `spotTimestamp` |

#### Phase C (requires trendbar data from Phase B — both fire at once)
- **Structure engine:** divide every H1/M5/M1 `open/high/low/close` by `10^pipDigits` to get display prices, then write:
  ```bash
  python3 /home/user/CTrader-Bots/ICT-SMC-Local-Agent/skill_adapter.py < /tmp/gold_session_input.json
  ```
  Returns per-timeframe: trend, premium/discount + OTE zone, graded FVGs (A+/A/B/C/SKIP), quality-scored OBs (1–5), BSL/SSL liquidity pools, Asian range, session/kill-zone/bias notes. This is ground truth for structure levels.
- **Cross-check:** `mcp__tradingview-mcp__recognize_market_pattern` — an independent non-ICT pattern-recognition pass used only to confirm or challenge the structural bias.

### `skill_adapter.py` — the engine bridge

This script is the only thing standing between live cTrader JSON and the repo's existing ICT/SMC engine (`analysis/structure.py`, `analysis/sessions.py` — the same modules used by both the Local and Remote scanner agents, per `ICT-SMC-Local-Agent/CLAUDE.md`). It does not implement any trading logic itself; it only adapts data shapes:

- `_parse_candles()` — converts raw MCP JSON candles into the engine's `Candle` model.
- `_analyse_timeframe()` — for each of H1/M5/M1, runs:
  - `structure.detect_trend()`
  - `structure.calculate_premium_discount()`
  - `structure.detect_fvgs()` (top 10, includes the `_is_session_gap()` phantom-FVG filter — **never remove this**, per `CLAUDE.md`)
  - `structure.detect_order_blocks()` (top 10)
  - `structure.find_liquidity_pools()`
  - on H1 only: `structure.approximate_volume_profile()`, `structure.find_asian_range()` / `structure.asian_range_note()`
- `main()` reads `{symbol, current_price, h1, m5, m1}` from stdin, requires all three timeframes to be present (exits 1 with an error otherwise — the skill cannot run a partial analysis), adds `sessions.current_session()`, `sessions.active_kill_zone()`, `sessions.minutes_until_kill_zone_closes()`, and `sessions.session_bias_note()`, and prints the combined JSON to stdout.

Because this reuses the exact same `analysis/` modules as the standalone Local/Remote scanner agents, any bug fix made to `structure.py` or `sessions.py` for the scanner automatically applies to `/gold-session` too, and vice versa — they must be kept in sync (see `CLAUDE.md`'s "Local Agent ↔ Remote Agent" note).

### Core axioms (from `gold-session.md`)

The skill's system prompt encodes 7 ICT/SMC ground rules Claude must follow when reasoning over the engine output (e.g. price seeks liquidity before reversing, structure breaks confirm direction, FVGs/OBs are entries not signals on their own, premium/discount governs where longs vs. shorts are favoured, kill zones are where the highest-probability moves occur). These are framework knowledge embedded in the prompt, not code — they govern how Claude interprets `skill_adapter.py`'s output, not what the engine computes.

### Analysis protocol

`gold-session.md` requires Claude to work through 7 ordered steps before producing the report:

1. Structural reading (trend per timeframe, most recent break of structure)
2. Liquidity mapping (BSL/SSL pools, where stops are likely resting)
3. PD array identification (highest-quality FVGs/OBs per timeframe)
4. Premium/discount analysis (is current price favourable for longs or shorts)
5. Macro regime read (from the daily-snapshot.json briefing/yields/Fed odds/COT/GVZ)
6. Session/time context (current session, active kill zone, minutes remaining)
7. Cross-check (reconcile the rule-based engine read against the optional `recognize_market_pattern` pass and the macro briefing's bias — flag disagreement rather than silently picking one)

### Output format

A fixed markdown template, always in this order: **Account Context → Regime Assessment → Structure → Liquidity Map → Key PD Arrays → Macro Regime → Session Context → Cross-Check → Probability Assessment → Trade Idea (Primary) → Key Levels → Market Narrative.** Keeping this order fixed is intentional — it lets a trader scan the same section every time regardless of what the market is doing that day.

The report header always shows both UK time and UTC:
```
# GOLD INTRADAY SESSION BRIEF — YYYY-MM-DD — HH:MM BST|GMT / HH:MM UTC
```

**UK time rule (DST-aware):** BST (UTC+1) from the last Sunday in March to the last Sunday in October; GMT (UTC+0) otherwise. Approximate boundary: day ≥ 25 in March or October. Express all session times as `HH:MM BST` or `HH:MM GMT` — never UTC-only. The SESSION CONTEXT section includes a dedicated `**UK Time:**` line.

**OFF-HOURS mapping for STEP 8:** the `session` field in the meta JSON only accepts `LONDON`, `NEW_YORK`, `OVERLAP`, or `ASIAN`. If `skill_adapter.py` returns `OFF-HOURS`, write `ASIAN` to the meta file.

### Probability scoring rules

- Base probability starts at **50%**.
- Modifiers are added/subtracted for confluence: kill-zone timing, structure alignment across timeframes, FVG/OB grade, premium/discount position, macro-bias agreement, liquidity sweep confirmation, etc. (full modifier list lives in `gold-session.md`).
- Hard **cap at 92%**, hard **floor at 30%** — the skill is instructed never to claim near-certainty or near-impossibility.
- If a secondary/alternate trade idea is offered, its probability must differ from the primary idea's by **at least 15 percentage points** — this stops the report from hedging into two equally-weighted, equally-useless ideas.

### What the skill must never do

`gold-session.md` lists 9 hard constraints (e.g. never fabricate price levels not present in the candle data, never recommend a trade against the dominant H1 structure without explicitly flagging it as counter-trend, never omit the kill-zone/session context, never silently drop the cross-check step, never execute a trade). These are guardrails against the most likely failure modes of an LLM doing chart reasoning from structured data — fabrication and overconfidence — rather than general style guidance.

## STEP 8 — saving to the dashboard

After producing the report, the skill saves it to the **Gold-Session AI** tab in the dashboard using a two-file approach (no escaping of a long analysis string in JSON):

1. Write `/tmp/gold-session-meta.json` (5 scalar fields) and `/tmp/gold-session-analysis.txt` (full analysis text) **simultaneously** (parallel Write calls in one response).
2. Run:
   ```bash
   cd /home/user/CTrader-Bots/xauusd-dashboard && npx tsx scripts/save-gold-session.ts /tmp/gold-session-meta.json /tmp/gold-session-analysis.txt
   ```
   This writes `public/data/sessions/YYYY-MM-DD/HH-MM.json` and updates `public/data/sessions/index.json`, then commits and pushes to `main`. The dashboard tab is live after GitHub Actions deploys (~1–2 min).

**ESM note on `save-gold-session.ts`:** the script uses `fileURLToPath(import.meta.url)` + `path.dirname()` to compute `__dirname` — standard `__dirname` is not defined in ES module scope and will throw `ReferenceError` if used.

## Known issues & workarounds

| Issue | Root cause | Fix |
|---|---|---|
| `get_trendbars` fails with `INVALID_REQUEST: fromTimestamp must not be null` | The API requires explicit timestamps even when a count is given | Always provide both `fromTimestamp` and `toTimestamp` derived from `spotTimestamp` (see Phase B above) |
| `recognize_market_pattern` produces `InputValidationError` or "UNAVAILABLE" | TradingView tools are **deferred** — schema not loaded until `ToolSearch` is called; also, `uvx tradingview-mcp` stdio process has a slow cold-start | Add `ToolSearch` call with `query: "select:mcp__tradingview-mcp__recognize_market_pattern"` in Phase A, before Phase B; if still unavailable in Phase C, retry once and note degradation if it fails again |
| TradingView permission prompts appear each session | `settings.local.json` is globally gitignored (`**/.claude/settings.local.json` in `/root/.config/git/ignore`) — permissions added there are lost when the container is recycled | Permissions live in committed `.claude/settings.json` at repo root; do NOT use `settings.local.json` for persistent permissions |
| `get_symbols` response is very large (all broker instruments) | Pepperstone has hundreds of symbols; parsing the full list in Claude's context is expensive | Use Python: `python3 -c "import json,sys; data=json.load(sys.stdin); s=[x for x in data['symbols'] if 'XAU' in x.get('name','')]; print(json.dumps(s))"` piped from the MCP response, or filter by name/symbolId before returning |
| `save-gold-session.ts` fails with `ReferenceError: __dirname is not defined` | ESM module scope — `__dirname` is a CommonJS global | Script uses `fileURLToPath(import.meta.url)` + `path.dirname()` (already fixed) |
| `git pull --rebase` fails during save script with "unstaged changes" | Save script had already committed but unstaged local edits existed | Stage and commit any pending changes before running the save script; or ensure the working tree is clean before the skill run |

## Relationship to the standalone Local/Remote scanner agents

`ICT-SMC-Local-Agent/main.py` (and its Remote counterpart) run a non-interactive, multi-instrument scan across the full FTMO instrument list using the same `analysis/` engine, producing a `reports/pre_session_report.py`-formatted scan. `/gold-session` is narrower and interactive: XAUUSD only, driven by live cTrader MCP data plus the dashboard's macro snapshot, and produces a single conversational report rather than a batch scan. Both share the structure/session detection logic, so a fix to phantom-FVG filtering, trend detection, or kill-zone timing in `analysis/` benefits both paths immediately.

## Extending or modifying

- To change what counts as a high-quality FVG/OB, edit `analysis/structure.py` — changes apply to both the scanner agents and `/gold-session`.
- To change the report's structure, sections, or wording, edit `.claude/commands/gold-session.md` directly — it is the skill's entire prompt.
- To add a new data source to STEP 0 (e.g. DOM/Level-2 once Phase 3 of the Local Agent ships — see `CLAUDE.md`), add the fetch call to `gold-session.md`'s STEP 0 and, if it needs structural processing rather than raw display, add a corresponding function to `skill_adapter.py`.
- To change probability scoring, edit the modifier list and caps in `gold-session.md` — there is no separate scoring code; it's prompt-driven, not computed.
