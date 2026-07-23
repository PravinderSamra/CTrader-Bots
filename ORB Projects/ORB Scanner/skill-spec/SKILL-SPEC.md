# ORB Scanner — Agent Skill Build Specification (for Opus)

**Author:** Fable 5 (Phase 1). **Builder:** Opus (Phase 3). **Reviewer:** Fable 5 (Phase 4).
**Strategy authority:** `../research/STRATEGY-ANALYSIS.md` — if this spec and that document ever conflict, the strategy analysis wins and the conflict must be raised, not silently resolved.
**Connection authority:** `/ctrader-mcp-integration-guide.md` (repo root) — the persistent-HTTP `_call_tool()` pattern is mandatory; do not call `mcp__ctrader__*` tools from scripts.

---

## 0. Prerequisites (do not start the build without these)

1. `CTRADER_MCP_SLUG` (or `CTRADER_MCP_TOKEN`) available as an environment secret. The user provides this via GitHub secrets. Never hardcode it; never commit it.
2. **Phase 2 universe audit completed** and `research/UNIVERSE-AUDIT.md` written (see §8). The audit decides which universe mode (§4.1) the scanner runs in. Building the scan logic can proceed in parallel, but the skill must not be declared done with the universe mode unresolved.

## 1. Deliverable layout

```
.claude/skills/orb-scanner/
├── SKILL.md                  # skill definition (frontmatter: name, description, triggers)
└── scripts/
    ├── ctrader_client.py     # persistent-HTTP MCP client (port of integration-guide Lessons 1,2,4,7)
    ├── orb_scan.py           # the scanner engine (CLI, deterministic, all math lives here)
    └── universe.json         # cached instrument universe from the Phase-2 audit (symbolId, name, class, enabled)

ORB Projects/ORB Scanner/
├── runs/                     # scan outputs, one JSON + one MD per run, named YYYY-MM-DD-HHMM-ET.{json,md}
└── ... (existing research/spec files)
```

Division of labour — **hard rule:** every number (filters, ATR, RVOL, ranking, sizing) is computed in `orb_scan.py`, deterministically and unit-tested. The agent (skill layer) orchestrates, fetches catalyst context, applies the §6 veto checklist, and writes the report. The agent never recomputes or overrides the maths.

## 2. SKILL.md behaviour contract

Trigger: `/orb-scanner` or any user request to scan for ORB / opening-range / stocks-in-play picks.

Modes (skill must auto-select by current ET clock, overridable by argument):

| Mode | When | Behaviour |
|---|---|---|
| `preopen` | before 09:30 ET | Build/refresh watchlist: run `orb_scan.py --phase preopen`. Output watchlist table + cached history stats. |
| `scan` | 09:35–16:00 ET | Full scan: `orb_scan.py --phase scan`. Then agent layer: catalyst lookup, veto checklist, top-3 report. |
| `replay` | any time, `--date YYYY-MM-DD` | Same as scan but for a past session (for validation/journaling). Must state clearly it is a replay. |
| outside market days / 09:30–09:35 | — | Say so and stop (or offer preopen/replay). Never scan an incomplete opening range (wait until 09:35:00 ET). |

The skill must print, at the top of every report: mode, ET timestamp of data, universe mode in effect (§4.1), and any degraded-data warnings surfaced by the engine.

## 3. `ctrader_client.py` requirements

Port from the integration guide **unchanged in behaviour**: persistent `http.client.HTTPSConnection`, `initialize` + `notifications/initialized` handshake, `Mcp-Session-Id` tracking, single retry on session expiry, SSE `data:` line parsing. Token from env (`CTRADER_MCP_SLUG` preferred, `CTRADER_MCP_TOKEN` fallback). Additions:

- `get_trendbars(symbol_id, period, from_iso, to_iso)` with the exact param names `symbolId`, `period` (`"M_5"`, `"D_1"`), `fromTimestamp`/`toTimestamp` as ISO strings; respect the 720-hour max window (split requests if needed).
- `get_spot_prices(symbol_ids: list)` — note the key is singular `symbolId` with an array value.
- `get_symbols()` with enabled-only filtering.
- Price normalisation: pipette divisor per symbol. For equities do **not** trust the FX heuristic table — divisor must come from the audit data in `universe.json` (field `pipDivisor`), falling back to sanity-checking against a daily close.
- Politeness: ≤ ~5 requests/sec, exponential backoff on failures, hard timeout so a hung symbol can't stall the 09:35 pass.

## 4. `orb_scan.py` — the engine

### 4.1 Universe modes (decided by Phase-2 audit)

- **Mode A — `ctrader-native`:** the account exposes enough US share instruments (target ≥100). Universe = enabled share-class symbols from `universe.json`.
- **Mode B — `hybrid`:** few/no shares on the account. Shortlist high-RVOL candidates externally (TradingView screener MCP premarket/volume scan run by the *agent layer*, passed in via `--candidates`), engine validates and computes everything from cTrader data for symbols that exist there; symbols without cTrader coverage are reported in a clearly-separated "external data — advisory only" section computed from the external source.
- The active mode lives in `universe.json` metadata and is printed on every report.

### 4.2 Pre-open phase (`--phase preopen`, run any time 07:00–09:29 ET; results cached to `runs/cache-YYYY-MM-DD.json`)

For each universe symbol:
1. Fetch `D_1` bars, last 30 calendar days → last ≥15 trading days.
2. Compute `ATR14` = simple mean of the last 14 daily True Ranges (TR uses previous close; data up to and including yesterday). Insufficient history → exclude, reason-coded.
3. Compute `avgDailyVol14` (tick-volume proxy — see analysis §7).
4. Fetch `M_5` bars covering the last 15 trading days (one request, ~500h < 720h cap). Extract the bar starting exactly 09:30 ET for each prior day → `ORV` history (need 14 values; fewer → exclude).
5. Apply static filters: prior close > $5 (opening price is checked live at 09:35), `ATR14 > 0.50`, liquidity floor per audit calibration.
6. Emit watchlist sorted by `avgDailyVol14`, capped at `--max-watchlist` (default 60) so the 09:35 pass finishes fast. Cache per-symbol: `ATR14`, `orVolHistory[14]`, `pipDivisor`, `prevClose`.

### 4.3 Scan phase (`--phase scan`, valid 09:35:00–16:00 ET)

1. Load today's cache (if missing: run preopen first automatically, warn about timing).
2. For each watchlist symbol fetch today's `M_5` bars from 09:30 ET to now (one request per symbol; parallelism not required, keep sequential+keep-alive).
3. Identify the 09:30 ET bar → `ORH, ORL, ORV, open, close`. Missing/zero-volume bar → reason-coded exclusion (`no-or-bar`).
4. `direction`: close>open → long; close<open → short; equal → excluded (`doji`).
5. Live check: today's opening price > $5 else exclude.
6. `relVol = ORV / mean(orVolHistory)`. Exclude if `< 1.0` (`low-rvol`).
7. Corporate-action guard (analysis §6.5): if |today's open / prevClose − 1| > 0.40 **and** relVol > 10 → flag `rvol-suspect` (still ranked, but flagged).
8. Rank survivors by `relVol` descending. Top 3 = picks; ranks 4–10 = watch table.
9. For each pick compute the trade plan:
   - `entry = ORH` (long) / `ORL` (short); `stopDistance = 0.1 × ATR14`; `SL = entry ∓ stopDistance`.
   - `R` per share = `stopDistance`. Sizing for equity `E` (`--equity`, default 25000): `shares = floor(0.01×E / stopDistance)` capped by `floor(4×E / entry)`; report both the uncapped and capped figures and which bound binds.
   - Exit: EoD 16:00 ET, no target.
   - **Status field** from latest price: `pending` (entry not yet touched since 09:35), `triggered` (crossed entry; report current price, unrealised R, and % beyond entry), `stopped-would-be` (crossed entry then hit SL — replay/late scans), `late` (price > 1R beyond entry — chasing costs expectancy; advisory: do not chase).
10. Write `runs/<stamp>.json` (schema §5) and print a compact human table to stdout.

### 4.4 Determinism & tests

Pure functions for ATR, TR, RVOL, direction, sizing, ET-time mapping. Unit tests (pytest, no network): ATR vs hand-computed fixture; DST boundary (a March and a November date — 09:30 ET bar correctly found at 13:30Z summer / 14:30Z winter); doji exclusion; leverage-cap binding case; RVOL with exactly-14 history; the BLDR worked example from the paper (entry 174.44 short, ATR 5 → SL 174.94, exit 167.63 → +13.62R).

## 5. Output JSON schema (stable interface for the future execution phase)

```json
{
  "run": {"mode": "scan", "etTimestamp": "...", "universeMode": "ctrader-native", "warnings": []},
  "picks": [
    {
      "rank": 1, "symbol": "NVDA", "symbolId": 123, "direction": "long",
      "relVol": 8.4, "atr14": 2.31, "orHigh": 0.0, "orLow": 0.0, "orVolume": 0,
      "entry": 0.0, "stopLoss": 0.0, "stopDistance": 0.0,
      "sizing": {"equity": 25000, "riskPct": 1.0, "shares": 0, "leverageCapBinds": false},
      "exit": "EOD-16:00-ET", "status": "pending", "flags": [],
      "catalyst": null
    }
  ],
  "watch": [], "excluded": [{"symbol": "X", "reason": "doji"}]
}
```

`catalyst` is filled by the **agent layer**, not the engine.

## 6. Agent layer (in SKILL.md instructions)

After the engine returns:
1. For each pick, one news lookup (newsmcp/tavily/web search — best available) → one-line catalyst note or "no catalyst found (RVOL unexplained — caution)".
2. **Veto checklist** (report as flags, never silently drop a pick — the human decides):
   - pending/announced cash merger or acquisition target (price pinned → no trend) — the one known RVOL failure mode;
   - trading halt in effect or LULD-halt-prone (multiple halts already today);
   - `rvol-suspect` flag from the engine (split/corporate action);
   - `late` status (breakout already extended > 1R).
3. Compose the report (template §7). Save as `runs/<stamp>.md`. Both files committed if the user asks to track runs.
4. Never invent numbers. Every figure in the report must come from the engine JSON. If the engine failed for a symbol, say so.

## 7. Report template

```
# ORB Stocks-in-Play Scan — {date} {time} ET  [mode | universe mode]
Market: {open/closed}; data as of {ts}. Warnings: {...}

## Top 3 Picks
### 1. {SYM} — {LONG/SHORT} — RVOL {x.x}×
Catalyst: {one line}
Entry (stop order): {price} | SL: {price} ({0.1×ATR} = {d}) | Exit: EoD 16:00 ET
Size @1% risk on £/${E}: {n} shares {(leverage-capped)} | Status: {pending/triggered(+x.xR)/late}
Flags: {none | ...}

## Watch (ranks 4–10)      → compact table
## Excluded notables       → count by reason
## Discipline reminders    → no profit target; one entry per symbol; direction lock; no chase >1R
```

## 8. Phase-2 universe audit (blocking task, own doc: `research/UNIVERSE-AUDIT.md`)

With the live token: (1) `get_symbols` full dump → classify asset classes, count enabled share instruments, note naming (`_SB` suffix etc.); (2) for ~10 sample equities (mega-cap + mid-cap): pull `D_1` and `M_5` bars, verify: pipette divisor, presence and semantics of volume field on M_5 equity bars (**if tick volume is absent/always zero on equities, RVOL is impossible on cTrader data and Mode B is forced — this is the single biggest project risk**), session coverage (pre-market bars present? 09:30 ET bar identifiable?), data latency near the open; (3) write findings + recommended universe mode + liquidity-floor calibration into the audit doc and `universe.json`.

## 9. Acceptance criteria (Fable 5 review gate)

1. Every rule R1–R7 from the strategy analysis implemented exactly; deviations listed in SKILL.md under "Known deviations" with rationale.
2. All §4.4 tests pass; test run output included in the PR/commit description.
3. `replay` mode reproduces a plausible historical session end-to-end with the demo token.
4. No secrets in the repo; engine fails with a clear message when the token env var is missing.
5. Report renders correctly with zero qualifying stocks (quiet day) — must say "no Stocks in Play today", not error.
6. 09:35 scan pass completes in < 3 minutes for a 60-symbol watchlist.
7. Skill refuses to scan 09:30–09:35 ET and explains why.
```
