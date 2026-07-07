# XAUUSD Dashboard + Gold-Session Skill — Deep-Dive Audit & Improvement Plan

**Date:** 2026-07-07 · **Author:** Claude (deep-dive session)
**Purpose:** Executable work plan. Each item lists exact files, spec, and acceptance criteria so a
follow-up session can implement without re-deriving context. Work through phases in order;
each phase is independently shippable.

---

## PART 1 — AUDIT FINDINGS

### 1.1 What the system captures today (inventory)

| Domain | Points captured | Source | Cadence |
|---|---|---|---|
| Live prices | XAU, XAG, 6 DXY legs, USDCNH, US500/GER40/UK100, ADR 14d, Au/Ag ratio | cTrader MCP (snapshot fallback in prod) | hourly snapshot; 15s poll when token present |
| Rates | 10Y/2Y nominal, 10Y/5Y real, 2s10s, breakevens, 5y5y fwd, DoD deltas | FRED | hourly (session hours) |
| Fed | next meeting, cut/hold/hike probabilities | CME FedWatch scrape | hourly |
| Vol | VIX, GVZ, derived riskTone | FRED/Yahoo | hourly |
| Positioning | COT net long, WoW, crowding, COMEX OI + change | CFTC | weekly data, fetched hourly |
| Flows | GLD tonnes, WoW, 3-week trend | SPDR | hourly |
| Stress | STLFSI4, NFCI | FRED | weekly data |
| Geopolitics | GPR index | Caldara-Iacoviello xlsx | monthly data |
| Calendar | week-ahead, impact-graded, forecasts | Finnhub | hourly |
| News | 24h keyword-filtered headlines with hoursAgo | Finnhub | hourly |
| AI briefing | bias score −5..+5, confidence, prose | Anthropic API (server-side) | hourly |
| ICT structure | H1/M5/M1 trend, premium/discount+OTE, graded FVGs, scored OBs, BSL/SSL pools, volume profile (POC/VAH/VAL), Asian range+sweep, session/KZ, midnight-open bias | skill_adapter.py engine | on each /gold-session run |

### 1.2 Missing data points (ranked by expected impact on trade success)

**M-1. Prediction outcome tracking / calibration loop — the single highest-value gap.**
The system records predictions (bias, probability, invalidation) but never records what price
did afterwards. Without outcomes you cannot know if "72% probability" calls actually win 72%
of the time, which biases are systematically wrong, or whether confidence correlates with
accuracy. Everything else on this list refines the inputs; this one measures the output.

**M-2. Previous Day High/Low, Previous Week High/Low, Daily Open, NY Midnight Open.**
Core ICT reference liquidity levels — PDH/PDL are the most commonly targeted pools and the
engine doesn't compute them (only Asian range). Cheap: derivable from D_1/W_1 trendbars
already fetchable in the skill.

**M-3. SMT divergence (XAUUSD vs DXY).**
Gold making a lower low while DXY fails to make a higher high (or vice versa) is a first-class
ICT confluence signal. Skill already fetches XAU candles; adding one DXY-leg (EURUSD inverted
or synthetic DXY) M5/H1 series and a divergence check in skill_adapter.py is moderate effort,
genuinely additive signal.

**M-4. Explicit BOS/CHoCH detection with levels + displacement flag.**
Engine trend is an HH/HL heuristic; it doesn't emit "BOS at 4167.53 (07:00)" or flag
displacement (range-expansion candles) which is the trader's M1 entry confirmation. Add to
structure.py output: last BOS/CHoCH per timeframe {type, level, timestamp} and
`displacement_detected` bool on M5/M1 (body > 1.5× ATR(14) of bodies).

**M-5. Structured session record (removes the regex-parsing failure class).**
`save-gold-session.ts` meta only carries {session,bias,biasScore,probability,confidence}. The
dashboard regex-parses markdown for everything else — this already caused the "Price Zone: H"
bug. Extend meta JSON with structured fields (spec in Phase 2). Impact: reliability + unlocks
UI (liquidity map, R:R visual) that can't be built on regex.

**M-6. Intra-day key-value history for sparklines.**
Fetch workflow runs hourly but overwrites daily-snapshot.json — history is discarded. Append
{ts, XAU, DXY, US10Y, VIX, GVZ, realYield10Y} to a rolling 7-day `history.json` per run.
Enables sparklines/trend context on every tile (UI item U-4).

**M-7. Day-of-week / weekly-profile context label.**
ICT weekly profiles (Mon range set, Tue/Wed often form weekly high/low). Zero-cost contextual
line in the skill prompt + session record: "Tuesday — statistically likely day for weekly
extreme formation."

**M-8. Bid/ask spread surfacing.** Already in spot data, discarded. Show in GoldTile; wide
spread at KZ open is an execution-cost warning. Trivial.

**M-9 (deferred/hard).** Central-bank purchase aggregates (monthly WGC), gold lease rates,
options skew — valuable but no good free real-time source; revisit later. COMEX delivery
notices — niche. Citi surprise index — paid.

### 1.3 Architecture findings

**A-1. Three conflicting session-boundary definitions.** `App.tsx getSessionLabel` (UTC 8–16
London), `Header.tsx SESSIONS` (UTC 8–13 London + 13–16 overlap), `sessions.py` (ET-based,
DST-aware, the correct one). The dashboard's labels drift ±1h across DST. Fix: one shared
`src/utils/sessions.ts` mirroring sessions.py logic (ET-anchored), used by App, Header,
SessionTimeline.

**A-2. Timezone display inconsistency.** Header clock hardcodes "GMT" label year-round (it is
BST in July); GoldSessionTab shows "{time} UTC" while save script writes UK time (so it
displays "21:19 BST UTC"). Fix: shared `src/utils/ukTime.ts` (BST/GMT-aware, logic already
exists in Header.isBST); GoldSessionTab drops the hardcoded "UTC" suffix.

**A-3. Markdown-regex coupling between skill output and UI.** GoldSessionTab has ~6 regex
parsers over free text. Brittle by design. Phase 2 makes the skill emit structured JSON;
regexes stay only as fallback for pre-existing records.

**A-4. `aggregateData()` runs on every App render** (each second via Header clock state is
isolated, but every refresh/price update re-runs it). Wrap in `useMemo` keyed on
[prices, snapshot, vix]. Small but correct.

**A-5. `useCTraderPrices` serially awaits 12 `get_trendbars` calls per poll** (~12 round-trips
every 15s when live). Parallelise with `Promise.all`. (Dead path in prod today, but correct it
before it's ever re-enabled.)

**A-6. No React error boundary.** One thrown parse error blanks the whole app. Add a small
`<Boundary>` wrapper per tab.

**A-7. No tests for the parsers that have already regressed once.** Add vitest +
3 fixture-based tests (parsePriceInRange, parseSections/parseKVRows, ProbCard regexes) using
the real 2026-07-06 session file as fixture.

**A-8. Snapshot staleness invisible.** In offline/fallback mode the header shows OFFLINE but
not data age. Surface `snapshot.generatedAt` as "data as of HH:MM BST" chip.

**A-9. fetch-static-data.ts is a 1086-line monolith.** Works, but each new source raises risk
(the 6-day outage came from one template-literal typo breaking everything). Split into
`scripts/fetchers/*.ts` modules with per-fetcher try/catch already partially present.
Low urgency, do last.

### 1.4 UI/UX findings

**U-1. Gauge is unbounded — fills panel width** (visible in user screenshot: dial ~700px).
`.svg {width:100%}` with no max-width in either BriefingPanel `.gaugeWrap` or GoldSessionTab
`.gaugeWrap` (flex:1). Fix: `max-width: 300px; margin-inline: auto;` on the gauge, rebalance
gaugeRow so stats sit beside it, not dwarfed by it.

**U-2. No mobile layout at all** (`body {min-width:1200px}`) — yet the user reviews on a
phone. Highest-effort, highest-visibility UX item: responsive grid (tiles stack single-column
<768px), sidebar becomes horizontal chip-scroller, header collapses.

**U-3. Gold-Session tab shows numbers but no picture of the levels.** Build a vertical
"Liquidity Ruler": BSL pools above, SSL below, current price marker, draw-on-liquidity
highlighted, invalidation in red. Reads from structured `keyLevels` (Phase 2). This is the
flagship visual for the tab.

**U-4. No trend context anywhere** — every tile is a point-in-time number. Sparklines from
history.json (M-6): XAU, DXY, US10Y, VIX. 7-day, 24×7 points, tiny SVG polyline component.

**U-5. Trade-idea card lacks R:R visual.** When structured tradeIdea exists, render
entry/stop/T1-T3 as a proportional horizontal bar (red span = risk, green spans = targets).

**U-6. Yield curve number without shape.** 2s10s shown as number; tiny 2-point→multi-point
curve sketch (2Y,10Y + optionally 5Y real) in YieldsTile. Low priority.

**U-7. No countdown to next high-impact event** in Gold-Session tab (calendar data exists).
Add chip: "CPI in 3h 20m" — direct trade-timing relevance.

**U-8. Loading states are em-dashes.** Skeleton shimmer on tiles during first load. Cosmetic,
last.

---

## PART 2 — IMPLEMENTATION PLAN (5 phases, ordered)

> Rules for the implementing session: work on branch
> `claude/xauusd-intelligence-dashboard-t5jnzh`, merge to `main` to deploy (established
> pattern). Never commit secrets; snapshot fetch stays server-side. After each phase:
> `npx tsc --noEmit` (ignore pre-existing firebase errors only if firebase not installed —
> run `npm install` first), `npm run build`, commit, push.

### Phase 1 — Correctness & quick wins (small diffs, do first)

**1a. Gauge size fix.**
- `BiasGauge.module.css`: `.svg { max-width: 300px; display:block; margin-inline:auto; }`
- `GoldSessionTab.module.css .gaugeRow`: change to `align-items:center; gap:24px`; `.gaugeWrap { flex:0 1 320px }`; `.statPills { flex:1; justify-content:flex-end }`
- `BriefingPanel.module.css .gaugeWrap`: center content.
- Acceptance: dial ≤300px wide on desktop; text not clipped; stats visually co-equal.

**1b. Shared UK-time util + session-label unification.**
- New `src/utils/time.ts`: `isBST(d)`, `ukTimeString(d) → "HH:MM BST|GMT"`, `ukTzLabel(d)`.
- New `src/utils/sessions.ts`: single SESSIONS table (London 08:00, overlap 13:30–16:30,
  NY→21:00 UTC during BST; shift +1h when GMT — mirror `sessions.py` ET anchors: London KZ
  02:00–05:00 ET, NY KZ 08:30–11:00 ET, sessions ASIA 19:00–03:00 ET, LONDON 03:00–09:30 ET,
  OVERLAP 09:30–11:30 ET, NY 09:30–16:00 ET as per engine). Export `getSession(now)`,
  `getKillZone(now)`.
- Refactor `App.tsx`, `Header.tsx`, `SessionTimeline.tsx` to consume these; delete local copies.
- `Header.tsx` clock: use `ukTimeString` (fixes "GMT" label in July).
- `GoldSessionTab.tsx` line ~614: remove hardcoded `UTC` suffix (time already carries BST/GMT).
- Acceptance: header, timeline, and App session labels agree with each other and with UK DST.

**1c. useMemo aggregateData** in App.tsx; **Promise.all** the trendbars loop in
`useCTraderPrices.ts`; add **snapshot-age chip** in Header when `status==='offline'` and
snapshot present ("data as of {ukTimeString(generatedAt)}").

**1d. Error boundary.** New `src/components/layout/Boundary.tsx` (classic componentDidCatch,
renders compact error card); wrap each tab's content in App.tsx.

**1e. Spread display.** `useCTraderPrices`/`pricesFromSnapshot`: add `XAUUSD_spread` (ask−bid);
GoldTile row "Spread — $0.32". (Snapshot fallback: null → row hidden.)

### Phase 2 — Structured session records (unblocks Phases 3–4 UI)

**2a. Extend meta schema.** `save-gold-session.ts` `SessionMeta` gains optional:
```ts
priceAtAnalysis?: number
drawOnLiquidity?: number          // primary target level
invalidation?: number
priceZone?: 'DISCOUNT'|'PREMIUM'|'EQUILIBRIUM'|'OTE'
equilibrium?: number
keyLevels?: { price:number; kind:'BSL'|'SSL'|'PDH'|'PDL'|'PWH'|'PWL'|'ASIAN_HIGH'|'ASIAN_LOW'|'POC'|'INVALIDATION'|'DRAW'|'OTHER'; note?:string }[]
tradeIdea?: { direction:'LONG'|'SHORT'; status:'ACTIVE'|'WAIT'|'NO_TRADE'; entryLow?:number; entryHigh?:number; stop?:number; targets?:number[]; rr?:number; setupType?:string } | null
nextHighImpactEvent?: { event:string; timeIso:string } | null
```
All fields flow into the record + index entry (index gets only priceZone, tradeIdea.direction/
status for the sidebar). Types mirrored in `src/types/dashboard.ts`.

**2b. Update the gold-session skill** (`.claude/skills/gold-session/SKILL.md` — Step 8 /
save-to-dashboard section): instruct the agent to populate the new meta fields from the engine
output it already has (liquidity_pools → keyLevels, premium_discount → priceZone/equilibrium,
trade idea section → tradeIdea{}). Keep old fields for back-compat.

**2c. GoldSessionTab consumes structured fields when present**, regex fallback otherwise:
- Price Zone pill ← `meta.priceZone` (regex only if absent).
- Trade badge/variant ← `tradeIdea.status/direction`.
- Acceptance: 2026-07-06 record (no new fields) still renders; a new-format fixture renders
  without touching regex paths (assert via tests, 2d).

**2d. Vitest.** `npm i -D vitest`; `scripts/test` → `vitest run`. Tests:
`src/components/gold-session/__tests__/parsers.test.ts` — parsePriceInRange on "H1"-prefixed
line (regression), parseSections on real fixture, ProbCard regexes. Copy the real
`public/data/sessions/2026-07-06/20-19.json` into `src/test-fixtures/`.

### Phase 3 — Engine & skill data upgrades (M-2/3/4/7)

**3a. PDH/PDL/PWH/PWL/daily-open/midnight-open.** In `skill_adapter.py`: accept optional
`"d1": [...]` daily candles in input; compute prevDayHigh/Low, prevWeekHigh/Low, dailyOpen,
midnightOpenNY (already partially in Asian-range calc); emit under `"reference_levels"`.
Skill (Phase B) adds one D_1 fetch (20 days) to the trendbar calls and passes it through.
Skill instructs merging reference_levels into keyLevels meta.

**3b. BOS/CHoCH + displacement.** `analysis/structure.py`: add
`detect_structure_breaks(candles) → {last_bos:{...}|None, last_choch:{...}|None}` (swing-based:
close beyond last confirmed swing high/low = BOS with-trend, CHoCH counter-trend) and
`detect_displacement(candles, atr_period=14, mult=1.5) → bool` (any of last 3 bodies >
mult×avg body). ⚠ Per repo CLAUDE.md: apply identical change to the Remote Agent's
`analysis/structure.py` copy. Wire into `skill_adapter.py` per-timeframe output. Update skill
STEP 1 to cite engine BOS/CHoCH instead of manual-only.

**3c. SMT divergence.** `skill_adapter.py`: accept optional `"smt_symbol_m5": [...]` (EURUSD M5
candles — inverse-USD proxy). Compute: last two swing highs/lows on XAU vs proxy; flag
`smt_divergence: 'BULLISH'|'BEARISH'|null` (gold LL while proxy HL → bullish SMT, inverse for
bearish). Skill Phase B adds EURUSD M5 fetch (symbolId from get_symbols fallback map; EURUSD
known-stable on this broker — check fetch-static-data.ts SYMBOL_IDS map for the hardcoded id)
and passes it. Report in CROSS-CHECK section + `meta.smtDivergence`.

**3d. Weekly-profile note.** Skill STEP 6: add one line mapping UTC weekday → ICT weekly
profile note. No engine change.

### Phase 4 — Outcome tracking & calibration (M-1) 

**4a. Resolver script** `xauusd-dashboard/scripts/resolve-gold-sessions.ts`:
- Reads index.json + each session file lacking `outcome`.
- For records ≥4h old (and having priceAtAnalysis+invalidation or drawOnLiquidity): fetch
  XAUUSD H1 bars covering [timestamp, timestamp+8h] from cTrader MCP (reuse
  fetch-static-data.ts mcpFetch helpers — extract those into `scripts/lib/ctrader.ts`).
- Classify: hit draw before invalidation → `WIN`; invalidation first → `LOSS`; neither within
  8h → `EXPIRED_{FAVOURABLE|ADVERSE|FLAT}` by sign of (close−priceAtAnalysis) vs bias.
- Writes `outcome: {result, resolvedAt, maxFavourable, maxAdverse}` into the session file and
  appends summary row to `public/data/sessions/outcomes.json` (never pruned — this is the
  calibration archive).
- Wire into `.github/workflows/xauusd-daily-fetch.yml` as a step after the snapshot fetch
  (same secrets context; commits alongside).

**4b. Calibration UI.** Gold-Session tab sidebar footer card "Track Record": last 30 resolved
— win rate, avg probability vs realised rate (one line: "Called 68% · Hit 61%"), per-bias
breakdown. Sidebar entries get a small ✓/✗/○ glyph from outcome. Data: `outcomes.json` via new
`useSessionOutcomes` hook.

### Phase 5 — Visual layer (U-2/3/4/5/7)

**5a. History + sparklines.** fetch-static-data.ts main(): after building snapshot, load
`public/data/history.json`, append `{ts, xau, dxy, us10y, vix, gvz, realYield10Y}`, prune >7d,
write. New `src/components/common/SparkLine.tsx` (SVG polyline, 120×28, endpoint dot, ±color
by net change). Add to GoldTile (XAU), DollarTile (DXY), YieldsTile (10Y), EquitiesTile (VIX).

**5b. Liquidity Ruler** `src/components/gold-session/LiquidityRuler.tsx`: vertical axis
auto-scaled to keyLevels∪{priceAtAnalysis}; BSL/PDH etc. above in red-tinted rows, SSL/PDL
below in green-tinted, current price gold marker line, DRAW level pulsing outline,
INVALIDATION dashed red. Render beside AnalysisRenderer when `meta.keyLevels?.length`.

**5c. R:R bar** in TradeCard when structured tradeIdea present: horizontal scale from stop to
furthest target; red segment entry→stop, green segments entry→T1/T2/T3, printed R multiples.

**5d. Event countdown chip** in Gold-Session viewHeader + dashboard Header: nearest
`economicCalendar` HIGH event with future time → "CPI · 3h 20m". Reuse existing calendar data;
new `src/utils/nextEvent.ts`.

**5e. Responsive layout.** globals.css: drop `min-width:1200px`; add breakpoints —
`<1100px`: grid3→2col; `<768px`: all grids 1col, `.main` padding 12px, MacroStrip stays
h-scroll, Header stacks (price row + meta row), GoldSessionTab sidebar → horizontal
scroll chips above content (`flex-direction:column` on `.tab`), gaugeRow wraps.
Test at 390px width (iPhone). This is the largest single item in Phase 5 — do it last and
screenshot-verify with the /run skill or Playwright at 390/768/1200 widths.

**5f. Skeleton shimmer** for tiles pre-snapshot (pure CSS, `.skeleton` class on placeholder
rows). Optional/cosmetic.

---

## Suggested execution order for the implementing session

1. Phase 1 (one commit) — visible fixes, zero risk.
2. Phase 2 (one commit) — schema + tests; nothing breaks (all fields optional).
3. Phase 3 (two commits: 3a+3b engine, 3c+3d skill) — remember Remote Agent sync for structure.py.
4. Phase 5a+5d (quick visual wins), then 5b+5c (needs a new-format session record to exist —
   run /gold-session once after Phase 3 deploys), then 5e responsive, then 5f.
5. Phase 4 last (needs cTrader secrets in the workflow; verify `CTRADER_MCP_TOKEN` is available
   as an Actions secret — it is used by xauusd-daily-fetch.yml already).

## Explicit non-goals

- No live trading/execution features.
- No paid data sources (Citi surprise index, options flow).
- No client-side secrets ever (VITE_* token injection stays disabled).
- Don't remove `_is_session_gap()` in structure.py (per ICT-SMC-Local-Agent/CLAUDE.md).
- Don't re-architect to a server/database — static JSON on Pages remains the model.
