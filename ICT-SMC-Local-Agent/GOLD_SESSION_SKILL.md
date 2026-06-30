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

When `/gold-session` runs, Claude is instructed to:

1. Call the **cTrader Local/Remote MCP server** (`mcp__ctrader__*` tools) for the current XAUUSD symbol info, spot price, and trendbars on **H1, M5, and M1**, plus open positions and account balance.
2. Fetch `xauusd-dashboard/public/data/daily-snapshot.json` (or the deployed `daily-snapshot.json` on GitHub Pages) for the macro picture — yields/real yields, Fed cut/hold/hike odds, GVZ, COT positioning, ETF flows, dollar-liquidity stress, geopolitical risk, and the AI-generated daily briefing/bias score. This is the same file the dashboard renders; the skill reuses it instead of re-deriving macro context itself.
3. Pipe the three candle sets (`h1`, `m5`, `m1`) plus `symbol`/`current_price` as JSON on stdin to `python skill_adapter.py`, which runs the shared `analysis/` engine (see below) and returns structured FVG/OB/liquidity/trend/premium-discount output per timeframe, plus the current session and kill-zone status.
4. Optionally cross-checks the read with the `recognize_market_pattern` tool (an independent pattern-recognition pass) as a sanity check against the rule-based engine's output.
5. Optionally pulls the Finnhub economic calendar for any high-impact events in the next few hours.

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

### Probability scoring rules

- Base probability starts at **50%**.
- Modifiers are added/subtracted for confluence: kill-zone timing, structure alignment across timeframes, FVG/OB grade, premium/discount position, macro-bias agreement, liquidity sweep confirmation, etc. (full modifier list lives in `gold-session.md`).
- Hard **cap at 92%**, hard **floor at 30%** — the skill is instructed never to claim near-certainty or near-impossibility.
- If a secondary/alternate trade idea is offered, its probability must differ from the primary idea's by **at least 15 percentage points** — this stops the report from hedging into two equally-weighted, equally-useless ideas.

### What the skill must never do

`gold-session.md` lists 9 hard constraints (e.g. never fabricate price levels not present in the candle data, never recommend a trade against the dominant H1 structure without explicitly flagging it as counter-trend, never omit the kill-zone/session context, never silently drop the cross-check step, never execute a trade). These are guardrails against the most likely failure modes of an LLM doing chart reasoning from structured data — fabrication and overconfidence — rather than general style guidance.

## Relationship to the standalone Local/Remote scanner agents

`ICT-SMC-Local-Agent/main.py` (and its Remote counterpart) run a non-interactive, multi-instrument scan across the full FTMO instrument list using the same `analysis/` engine, producing a `reports/pre_session_report.py`-formatted scan. `/gold-session` is narrower and interactive: XAUUSD only, driven by live cTrader MCP data plus the dashboard's macro snapshot, and produces a single conversational report rather than a batch scan. Both share the structure/session detection logic, so a fix to phantom-FVG filtering, trend detection, or kill-zone timing in `analysis/` benefits both paths immediately.

## Extending or modifying

- To change what counts as a high-quality FVG/OB, edit `analysis/structure.py` — changes apply to both the scanner agents and `/gold-session`.
- To change the report's structure, sections, or wording, edit `.claude/commands/gold-session.md` directly — it is the skill's entire prompt.
- To add a new data source to STEP 0 (e.g. DOM/Level-2 once Phase 3 of the Local Agent ships — see `CLAUDE.md`), add the fetch call to `gold-session.md`'s STEP 0 and, if it needs structural processing rather than raw display, add a corresponding function to `skill_adapter.py`.
- To change probability scoring, edit the modifier list and caps in `gold-session.md` — there is no separate scoring code; it's prompt-driven, not computed.
