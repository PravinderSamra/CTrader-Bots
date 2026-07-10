# UK100 Intelligence Section — Verified Spec & End-to-End Build Plan v1.0

**Status:** Phase 1 (analysis/research) COMPLETE — this document is its output.
**Written by:** the Fable-model planning pass, 2026-07-10, after live verification of every external unknown.
**Audience:** a lower-capability builder model. Every decision is already made; every symbol ID, series code, file path, interface, and acceptance test is specified. **Do not re-research, re-decide, or refactor beyond what is written here.** Where this plan says "copy file X as template", copy it — do not redesign.

**Companion input:** `UK100_Macro_Dashboard_Spec_v1.md` (user's research doc) — this plan supersedes it where they differ, because everything here was verified against the live account/APIs on 2026-07-10.

---

## 0. What is being built (one paragraph)

A **UK100** top-level tab on the existing XAUUSD dashboard with two sub-tabs: **UK100 Macro** (tile grid: GBP sign-flipped FX, UK rates/gilts, US linkage, commodities, sector-driver panel, positioning, calendar, risk tone, mechanical bias gauge) and **UK100-AI** (session-brief archive, same UX as Gold-Session AI, plus a dedicated **ORB Playbook card**). Behind it: an hourly `fetch-uk100-data.ts` snapshot pipeline (step added to the existing hourly workflow), a `/uk100-session` agent skill mirroring `/gold-session` (cTrader HTTP fetch → `uk100_adapter.py` structure engine → brief → conflict-proof save to `main`), and a mechanical + narrative daily bias with explicit guidance for how to trade the **15-minute Opening Range Breakout (08:00–08:15 London)** that day.

---

## 1. VERIFIED FACTS (live-checked 2026-07-10 — trust these, do not re-verify)

### 1.1 cTrader symbols (Pepperstone account; all prices = raw ÷ 10^5)

**CFD symbol IDs are the primary set** — the user trades UK100 as a CFD and wants CFD pricing. Verified 2026-07-10: the CFD IDs return live quotes on the existing token, and side-by-side comparison with the `_SB` (spread-bet) variants shows **identical prices to within spread noise** (UK100 CFD 10487.6 = UK100_SB 10487.6; both wrappers price off the same underlying feed). The `_SB` IDs are documented as fallbacks only.

| Purpose | Symbol | symbolId | Verified live price | Fallback (`_SB`) |
|---|---|---|---|---|
| The instrument | `UK100` | **113** | 10487.6 | 217 |
| GBP driver | `GBPUSD` | **2** | 1.3409 (already in gold pipeline) | — |
| GBP/EUR (derive GBPEUR = 1/EURGBP) | `EURGBP` | **9** | 0.852 | 175 |
| US futures proxy | `US500` | **115** | 7550.7 (already in gold pipeline) | 220 |
| US tech proxy | `NAS100` | **116** | 29691.1 | 205 |
| Energy sector driver | `SpotBrent` | **249** | 76.045 | 253 (`Brent_SB`) |
| Miners driver / China proxy | `Copper` | **109** | 6.2812 ($/lb — reconciles with FRED $13,483/t) | 2359 |
| Risk regime | `VIX` | **152** | 16.81 (matches FRED VIXCLS prior close) | 408 |
| Dollar index (bonus — live DXY exists) | `USDX` | **101** | 100.821 | 235 |

Notes: `get_symbols` returns 6,426 rows (~1.5MB) — **never call it in the pipeline**; use the IDs above (self-heal fallback in `scripts/lib/ctrader.ts` covers drift; if a CFD ID ever stops pricing, the listed `_SB` ID is the drop-in replacement at an identical price). The CFD symbols are flagged `enabled: false` for *trading* on this (spread-bet) account but stream quotes fine — this pipeline only reads prices, never trades. `scripts/lib/ctrader.ts` already maps `UK100: 113` and `US500: 115` — **no change needed for those**; Phase 2a only ADDS `NAS100: 116, BRENT: 249, COPPER: 109, VIX: 152, USDX: 101, EURGBP: 9`.

> If exact chart-matching against a *different broker's* CFD account (e.g. FTMO) is ever wanted, that account's cTrader API token can be added as a separate GitHub secret and the fetch pointed at it — symbol IDs are broker-specific and would need one re-resolution pass. Not needed for v1: Pepperstone CFD pricing is what the plan uses.

### 1.2 Bank of England IADB (keyless daily CSV — all verified returning current data)

Endpoint template (GET):
```
https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&UsingCodes=Y&CSVF=TN&Datefrom=DD/Mon/YYYY&Dateto=DD/Mon/YYYY&SeriesCodes=CODE1,CODE2
```
Returns CSV: `DATE,CODE1,CODE2…` with rows like `09 Jun 2026,3.75,3.7271`.

| Series | Code | Verified value (Jul 2026) |
|---|---|---|
| BoE Bank Rate | `IUDBEDR` | 3.75 |
| SONIA overnight | `IUDSOIA` | 3.7271 |
| Sterling ERI (trade-weighted GBP, daily) | `XUDLBK67` | 84.97 |
| Gilt 5Y nominal zero-coupon | `IUDSNZC` | 4.42 |
| Gilt 10Y nominal zero-coupon | `IUDMNZC` | 4.96 |
| Gilt 20Y nominal zero-coupon | `IUDLNZC` | 5.64 |

**Constraints found:** there is **no 2Y** in the IADB zero-coupon set (candidate codes error out, and one bad code fails the whole request — only ever request the six codes above). The long-end fiscal-stress gauge is the **20Y**, not 30Y. The front-end/BoE-path read = **5Y gilt + (SONIA − Bank Rate) spread**. Slope metric = **5s20s** (`IUDLNZC − IUDSNZC`).

### 1.3 FRED (existing `FRED_API_KEY` secret works; series verified via keyless fredgraph)

| Series | Code | Note |
|---|---|---|
| US 10Y | `DGS10` | already fetched by gold pipeline |
| US 2Y | `DGS2` | already fetched |
| GBP/USD daily official | `DEXUSUK` | ~4–7 day lag observed — **context/percentile only** |
| VIX close | `VIXCLS` | 1-day lag — context only (live = VIX_SB) |
| Brent spot FOB | `DCOILBRENTEU` | verified BUT ~$7 basis gap vs the CFD (69.56 vs 76.24) + 4-day lag → use for **trend direction only, never display next to the live price as comparable** |
| Copper $/tonne monthly | `PCOPPUSDM` | monthly; context only |
| UK 10Y monthly | `IRLTLT01GBM156N` | cross-validates IADB (4.94 vs 4.95 ✔) — not needed in build, IADB is better |
| UK CPI | — | **FRED UK CPI series are stale (2025-03) — do NOT wire them.** CPI prints come from the calendar scrape. |

### 1.4 CFTC COT — GBP futures proxy

Same Socrata endpoint the gold scraper already uses (`https://publicreporting.cftc.gov/resource/jun7-fc8e.json`). Filter: `cftc_contract_market_code='096742'` (BRITISH POUND — CME). Copy the gold COT fetch function, change the filter code, keep the same net-long/WoW/crowding computation. Label the tile "GBP positioning (FTSE proxy)" — there is no free FTSE futures COT (ICE Europe, not CFTC).

### 1.5 Secrets & infra already in place (no new secrets needed)

`FRED_API_KEY`, `FINNHUB_API_KEY`, `ANTHROPIC_API_KEY`, `ALPHA_VANTAGE_API_KEY`, `VITE_CTRADER_MCP_URL`, `VITE_CTRADER_MCP_TOKEN` — all live GitHub secrets used by `xauusd-daily-fetch.yml`. The Claude Code session env has `CTRADER_MCP_SLUG` for the skill's HTTP fetch.

### 1.6 Hard-won architecture rules (violating these re-introduces fixed incidents)

1. **Single Pages deploy owner.** Only `deploy-dashboard.yml` (push-to-main, `paths` filtered) and the deploy step inside `xauusd-daily-fetch.yml` may deploy. **Never add a Pages deploy to any new/other workflow** (2026-07-10 incident: a second deployer wiped the dashboard).
2. **Session saves push to `main` via the conflict-proof `commit-tree` loop** in `save-gold-session.ts` (fetch origin/main → rebuild index from origin/main's copy → temp `GIT_INDEX_FILE` → `commit-tree` → plain push, retry ×5). **Never rebase, never force-push, never hand-edit an index.json** (2026-07-09 Haiku incident).
3. **Freshness gates are mechanical, not instructional.** Engine refuses stale candles (m1>45min / m5>90 / h1>180); save script refuses engine input >60min old (2026-07-09 fabricated-brief incident). The UK100 engine and save path MUST have the same gates.
4. **`ICT-SMC-Local-Agent/analysis/` must stay byte-identical with `ICT-SMC-Remote-Agent/analysis/`.** New UK100 session logic therefore lives OUTSIDE `analysis/` (in a new root-level module). Adapters (`skill_adapter.py`, and the new `uk100_adapter.py`) are exempt from the sync rule.
5. **Skill/script changes only propagate to fresh sessions once on `main`** — every phase ends with a push to `main`.
6. **cTrader MCP tools are flaky in remote sessions; direct HTTPS is the primary path** (persistent keep-alive connection, SSE multi-`data:`-line rejoin, ISO-8601 trendbar timestamps, `HTTP 401` = credential problem → report & stop).
7. **DST:** UK100 session times are Europe/London wall-clock. Compute offsets like `save-gold-session.ts`'s `ukOffsetHours()` — never hardcode UTC.

---

## 2. ARCHITECTURE DECISIONS (locked)

| # | Decision | Rationale |
|---|---|---|
| D1 | UK100 data lives under `xauusd-dashboard/public/data/uk100/` (`daily-snapshot.json`, `sessions/<date>/<hhmm>.json`, `sessions/index.json`) | Isolates from gold files; already inside deploy triggers and the workflow's `git add public/data/` |
| D2 | New script `scripts/fetch-uk100-data.ts`; run as an **additional step in the existing `xauusd-daily-fetch.yml`**, before the single commit step | One workflow = one push to main per hour = no new race. Commit step already stages the whole data dir — zero change needed there |
| D3 | `save-gold-session.ts` gains an optional `--instrument=uk100` flag (default `gold`, gold behaviour byte-identical) switching: data dir, engine-input path, commit message, bot identity | Reuses the battle-tested commit-tree push; one file to maintain; tiny diff |
| D4 | `ctrader_http_fetch.py` gains `--instrument uk100` (default `gold` unchanged) switching the symbol/timeframe table and temp-file names | Same reliability path, no duplicate transport code |
| D5 | New engine adapter `ICT-SMC-Local-Agent/uk100_adapter.py` + session module `ICT-SMC-Local-Agent/uk100_sessions.py`; imports `analysis/structure.py` + `analysis/patterns.py` **unmodified** | Rule 1.6-4. FTSE session map ≠ gold session map (no Asia range logic; London-cash-open anchored) |
| D6 | UI: 4th top-level tab `UK100` → `src/components/uk100/Uk100Tab.tsx` with internal sub-tabs `macro` / `ai` following the exact `PravzellaTab.tsx` sub-tab pattern | Existing in-repo precedent for sub-tabs |
| D7 | Mechanical bias score computed **in the fetch script** (deterministic, testable) and stored in the snapshot; the Anthropic briefing narrates on top of it, never replaces it | Same shape as gold (`briefing.biasScore`); keeps the UI dumb |
| D8 | ORB Playbook is produced by BOTH layers: a mechanical `orbContext` block in the hourly snapshot (works even if no skill run happened) and a richer structured `orbPlaybook` in each `/uk100-session` record | The user trades this daily; it must never be missing just because no one ran the skill |
| D9 | New types in `src/types/uk100.ts`; new hooks `src/hooks/useUk100Snapshot.ts`, `src/hooks/useUk100Sessions.ts` (copy `useFredData.ts` / `useGoldSessions.ts` patterns, change paths) | Keeps gold types untouched |
| D10 | GBP sign-flip is implemented **in one function** `ftseImpact(gbpMovePct): 'BULLISH'\|'BEARISH'\|'NEUTRAL'` in the fetch script + exported UI helper — every tile calls it; no inline inversions | The #1 predicted bug class; single point of correctness |

**Explicit non-goals for the build model:** no refactor of gold code paths beyond the flag additions in D3/D4 and the `KNOWN_SYMBOL_IDS` UK100 fix; no new workflows; no `get_symbols` calls; no new npm/pip dependencies; G2 (ETF flows) from the research doc is **dropped from v1** (patchy free data — revisit later); BoE implied-path scraping (short sterling futures) is **out of v1** — SONIA−BankRate spread + static MPC dates instead.

---

## 3. DATA CONTRACTS (exact — copy into `src/types/uk100.ts`)

```ts
// ── Snapshot (public/data/uk100/daily-snapshot.json) ──────────────────────
export type FtseImpact = 'BULLISH' | 'BEARISH' | 'NEUTRAL'

export interface Uk100Snapshot {
  generatedAt: string                       // ISO
  prices: {                                 // live cTrader mid prices
    UK100: number; GBPUSD: number; GBPEUR: number;   // GBPEUR = 1/EURGBP
    US500: number; NAS100: number; BRENT: number; COPPER: number;
    VIX: number; USDX: number; XAUUSD: number;
    UK100_dayPct: number | null             // vs prior D1 close (from D_1 bars)
  }
  fx: {
    gbpUsdDayPct: number | null             // live vs FRED prior close
    gbpUsd20dPercentile: number | null      // 0-100, from FRED DEXUSUK last 20 obs
    sterlingEri: number | null              // XUDLBK67 latest
    sterlingEriDayChange: number | null
    ftseImpactFromGbp: FtseImpact           // the sign-flipped badge (D10)
  }
  ukRates: {
    bankRate: number | null                 // IUDBEDR
    sonia: number | null                    // IUDSOIA
    soniaMinusBankRate: number | null       // path pressure: negative = easing priced
    gilt5y: number | null; gilt10y: number | null; gilt20y: number | null
    gilt10yDayBp: number | null; gilt20yDayBp: number | null
    slope5s20s: number | null
    giltUst10ySpread: number | null         // IUDMNZC - DGS10
    longEndStress: boolean                  // gilt20yDayBp >= +8bp → fiscal-stress flag
    nextMpcDate: string | null              // from static MPC_DATES table
    daysToMpc: number | null
  }
  usLinkage: {
    us500DayPct: number | null; nas100DayPct: number | null
    vix: number | null
    vixRegime: 'CALM' | 'ELEVATED' | 'STRESS'   // <15 / 15-25 / >25
    us10y: number | null                    // DGS10
    usdx: number | null
  }
  commodities: {
    brentDayPct: number | null; copperDayPct: number | null; goldDayPct: number | null
    brent20dTrend: 'UP' | 'DOWN' | 'FLAT'   // FRED DCOILBRENTEU direction only (basis gap — see 1.3)
  }
  positioning: {                            // GBP COT proxy — label as proxy in UI
    gbpCotNetLong: number | null; gbpCotWoWChange: number | null
    crowding: 'CROWDED_LONG' | 'CROWDED_SHORT' | 'BALANCED' | null
    reportDate: string | null
    ftseReadthrough: FtseImpact             // crowded-long GBP → latent FTSE tailwind, etc.
  }
  sectorPanel: SectorRead[]                 // Group F — derived, no new fetches
  economicCalendar: Uk100CalendarEvent[]    // UK + US + EZ, week-ahead
  newsItems: Uk100NewsItem[]                // FTSE-keyword-filtered, 24h
  riskTone: { score: number; label: FtseImpact; rationale: string } | null  // Anthropic classifier
  bias: {                                   // mechanical roll-up (§5) — computed in fetch script
    score: number                           // -10 … +10
    label: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
    conviction: 'LOW' | 'MEDIUM' | 'HIGH'
    drivers: { name: string; impact: FtseImpact; weight: number; detail: string }[]
    eventSuppressed: boolean                // true when high-impact event in <4h
  }
  orbContext: OrbContext                    // §6 — mechanical, always present
  briefing: { biasScore: number; biasLabel: string; confidence: number;
              briefing: string; generatedAt: string } | null   // Anthropic narrative
}

export interface SectorRead {
  sector: 'ENERGY' | 'MINERS' | 'BANKS' | 'PHARMA' | 'STAPLES'
  weightNote: string          // e.g. "Shell, BP — top-5 index weights"
  driver: string              // e.g. "Brent +1.2% today"
  read: FtseImpact | 'IDIOSYNCRATIC'
  detail: string
}

export interface Uk100CalendarEvent {
  event: string; region: 'UK' | 'US' | 'EZ'; impact: 'HIGH' | 'MEDIUM' | 'LOW'
  timeIso: string; timeLondon: string       // "07:00 BST"
  daysFromToday: number; prior?: string; consensus?: string
}

export interface Uk100NewsItem { headline: string; source: string; hoursAgo: number; url?: string }

// ── ORB (Group: the 15-min Opening Range Breakout layer) ─────────────────
export interface OrbContext {               // mechanical block in the snapshot
  computedAt: string
  mode: 'PRE_OPEN' | 'ORB_FORMING' | 'POST_ORB' | 'CLOSED'   // vs 08:00-08:15 London
  cashOpenLondon: string                    // "08:00 BST"
  overnightHigh: number | null; overnightLow: number | null   // 22:00→08:00 London from H1/M5
  priorDayHigh: number | null; priorDayLow: number | null; priorClose: number | null
  gapPts: number | null; gapPct: number | null               // live/open vs priorClose
  orbHigh: number | null; orbLow: number | null              // null until 08:15
  orbBrokenDirection: 'UP' | 'DOWN' | 'NONE' | null          // post-ORB only
  eventWindows: { event: string; timeLondon: string; impact: string }[]  // today's HIGH within 07:00-16:30
  adr14: number | null; adrUsedPct: number | null
}

// ── Session records (public/data/uk100/sessions/…) ───────────────────────
// SAME shape as gold's SessionMeta/SessionRecord/IndexEntry (reuse the interfaces
// in save-gold-session.ts unchanged) PLUS one optional field:
export interface OrbPlaybook {              // written by /uk100-session into meta
  direction: 'LONG_ONLY' | 'SHORT_ONLY' | 'BOTH_OK' | 'STAND_ASIDE'
  dayType: 'TREND_EXPECTED' | 'RANGE_EXPECTED' | 'EVENT_DRIVEN'
  confidence: number                        // 1-10
  reasoning: string                         // 2-4 sentences, plain English
  keyLevels: { label: string; price: number }[]   // ONH/ONL/PDH/PDL/ORB levels
  invalidation: string                      // what kills the plan
  eventRisk: string | null                  // e.g. "US CPI 13:30 — flat by 13:15"
}
```

---

## 4. FILE MAP (every file the builder creates ● or modifies ◐)

### Data pipeline
- ● `xauusd-dashboard/scripts/fetch-uk100-data.ts` (~500 lines) — structure mirrors `fetch-static-data.ts`: tolerant per-source fetchers (each failure → `null` field + console.error, never a crash), assembled snapshot, mechanical bias (§5), `orbContext` (§6), Anthropic briefing call (reuse the exact request pattern incl. `.trim()` on the key and the retry), write `public/data/uk100/daily-snapshot.json`. Reuses `scripts/lib/ctrader.ts` (`fetchCTraderPrices` extended or called with the §1.1 map). cTrader D_1+M5 bars for UK100 (for day%, overnight range, prior-day levels, ADR14): copy the trendbar call from `resolve-gold-sessions.ts`.
- ◐ `xauusd-dashboard/scripts/lib/ctrader.ts` — `UK100: 113` and `US500: 115` already correct; ADD `{ NAS100: 116, BRENT: 249, COPPER: 109, VIX: 152, USDX: 101, EURGBP: 9 }` (CFD IDs, §1.1) to `KNOWN_SYMBOL_IDS`/`PIP_DIGITS`.
- ◐ `.github/workflows/xauusd-daily-fetch.yml` — one new step after "Fetch daily data snapshot", same env block: `run: cd xauusd-dashboard && npx tsx scripts/fetch-uk100-data.ts`, with `continue-on-error: true` (UK100 failure must not block the gold snapshot). No changes to commit/build/deploy steps.

### Engine & skill
- ◐ `ICT-SMC-Local-Agent/ctrader_http_fetch.py` — add `INSTRUMENTS` dict + `--instrument` argv parse:
  ```python
  INSTRUMENTS = {
    "gold":  {"main": 241, "proxy": 1,  "pfx": "gs",  "input": "/tmp/gold_session_input.json"},
    "uk100": {"main": 113, "proxy": 2,  "pfx": "uk",  "input": "/tmp/uk100_session_input.json"},  # UK100 CFD (fallback 217 _SB, identical price)
  }  # proxy for uk100 = GBPUSD (inverse SMT: GBP up should confirm UK100 down)
  ```
  Temp files become `/tmp/{pfx}_h1.json` etc. Gold default = current behaviour byte-identical.
- ● `ICT-SMC-Local-Agent/uk100_sessions.py` (~150 lines) — Europe/London session map (NOT in `analysis/`):
  `current_session()` → PRE_OPEN (06:00-08:00) / OPENING_HOUR (08:00-09:00) / MORNING (09:00-13:00) / PRE_US (13:00-14:30) / US_OVERLAP (14:30-16:30) / POST_CLOSE; `orb_window(m5_candles)` → dict with overnight range (22:00→08:00), cash-open, ORB high/low from the 08:00-08:15 M5 bars (3 bars), broken direction; `prior_day_levels(d1)`; `session_bias_note(...)`. DST via `zoneinfo.ZoneInfo("Europe/London")`.
- ● `ICT-SMC-Local-Agent/uk100_adapter.py` (~250 lines) — **copy `skill_adapter.py` as the template** and change: imports add `uk100_sessions`; the freshness gate stays IDENTICAL (m1 45/m5 90/h1 180 + `data_age_minutes`); Asian-range block REMOVED; adds `orb` (from `uk100_sessions.orb_window`), `session` (London map), `reference_levels` (prior day/week from D1 — reuse `_reference_levels` as-is), SMT vs GBPUSD proxy with INVERTED interpretation (gold's `_smt_divergence` compares positively-correlated pairs; UK100↔GBP is inverse — new 20-line `_smt_divergence_inverse`: UK100 lower low + GBPUSD lower low (= GBP also weak, which should LIFT FTSE) → BULLISH divergence; UK100 higher high + GBPUSD higher high → BEARISH). Structure per timeframe via the same `_analyse_timeframe` calls into `analysis/structure.py`/`patterns.py` (unmodified).
- ● `.claude/commands/uk100-session.md` — **copy `gold-session.md` as the template**, then apply the §7 skill-diff table below. Keep verbatim: the HTTP-primary/MCP-fallback logic, freshness-gate language, "NEVER reconstruct from saved records", the save-step "do NOT perform manual git recovery" block.
- ◐ `xauusd-dashboard/scripts/save-gold-session.ts` — parse `--instrument=uk100` from argv (filter it out of positional args). When uk100: `DATA_DIR=public/data/uk100/sessions`, `ENGINE_INPUT=/tmp/uk100_session_input.json` default, commit msg `chore: uk100-session …`, bot `uk100-session-bot`, REL paths under `uk100/`. Everything else (freshness gate, commit-tree loop) untouched.

### UI
- ● `src/types/uk100.ts` — §3 verbatim.
- ● `src/hooks/useUk100Snapshot.ts` — copy `useFredData.ts`'s `useDailySnapshot`, path `data/uk100/daily-snapshot.json`, 5-min refresh.
- ● `src/hooks/useUk100Sessions.ts` — copy `useGoldSessions.ts`, paths under `data/uk100/sessions/`.
- ● `src/components/uk100/Uk100Tab.tsx` + `.module.css` — sub-tab shell copied from `PravzellaTab.tsx` (`type SubTab = 'macro' | 'ai'`), labels **UK100 Macro** / **UK100-AI**.
- ● `src/components/uk100/MacroSubTab.tsx` — tile grid (§ layout below) + `BiasGauge` reuse + sector panel + ORB context strip.
- ● `src/components/uk100/tiles/` — `GbpTile.tsx` (A1+A2+A3 incl. sign-flip badge), `UkRatesTile.tsx` (B1-B4), `UsLinkageTile.tsx` (C1-C3, VIX regime chip), `CommoditiesTile.tsx` (D1-D3), `SectorPanel.tsx` (F1 — 5 rows, read chip each), `GbpCotTile.tsx` (G1, "proxy" label), `Uk100CalendarTile.tsx` (H, region-tagged), `OrbContextCard.tsx` (the §6 block: mode, ranges, gap, event windows). Copy `src/components/tiles/Tile.module.css` conventions; reuse `TileSpark`/`SparkLine` for 20-day context lines.
- ● `src/components/uk100/AiSubTab.tsx` — copy `GoldSessionTab.tsx` structure (session list from index, record viewer). Where gold parses its analysis text, reuse `gold-session/parsers.ts` (bias/levels regexes are format-compatible because the skill output template §7 keeps the same section markers) + render `meta.orbPlaybook` in a dedicated `OrbPlaybookCard.tsx` (direction pill LONG_ONLY=green/SHORT_ONLY=red/BOTH_OK=blue/STAND_ASIDE=grey, day-type, key-levels mini-table, invalidation line, event-risk line).
- ◐ `src/App.tsx` — `type DashTab = 'dashboard' | 'gold-session' | 'uk100' | 'pravzella'`; 4th nav button `UK100`; lazy-load `Uk100Tab` like `PravzellaTab` (it's behind a tab; keep initial bundle lean); wrap in `<Boundary label="UK100">`.

### UI layout (MacroSubTab, desktop → 1 col mobile)
```
[ Bias gauge + conviction + drivers list        ] [ OrbContextCard        ]
[ GbpTile ] [ UkRatesTile ]  [ UsLinkageTile    ]
[ CommoditiesTile ]  [ GbpCotTile ] [ CalendarTile ]
[ SectorPanel (full width) ]
[ Risk tone + news items (full width)           ]
[ Briefing narrative panel (reuse BriefingPanel pattern, full width) ]
```

---

## 5. MECHANICAL BIAS ENGINE (implemented in `fetch-uk100-data.ts` — pure function, unit-testable)

`computeBias(snapshot parts) → Uk100Snapshot['bias']`. Score = Σ weighted component scores, each component ∈ {-2,-1,0,+1,+2} before weighting:

| Component | Weight | +2 / -2 rule (linear in between; 0 when data null) |
|---|---|---|
| GBP (sign-flipped) | 3.0 | GBP/USD day% ≤ -0.5% → +2 (weak GBP lifts FTSE); ≥ +0.5% → -2. ERI confirms: if ERI and cable disagree in sign, halve the component |
| US futures | 2.5 | US500 day% ≥ +0.75% → +2; ≤ -0.75% → -2; NAS100 same sign adds ±0.5 (capped ±2) |
| VIX regime | 1.5 | CALM → +1; ELEVATED → 0; STRESS → -1 **only** (defensive cushion — never -2; this is a regime damper, not a direction) |
| Brent | 1.5 | day% ≥ +1.5% → +2; ≤ -1.5% → -2 |
| Copper (China fast proxy) | 1.5 | day% ≥ +1.5% → +2; ≤ -1.5% → -2 |
| Gilts / rotation | 1.0 | 10Y ±≤3bp → 0; +4..8bp → +1 (banks rotation); **gilt20yDayBp ≥ +8 → force -2 and set `longEndStress`** (fiscal stress overrides rotation) |
| GBP COT (contrarian) | 1.0 | CROWDED_LONG GBP → +1 (latent FTSE tailwind); CROWDED_SHORT → -1 |
| Risk tone (Anthropic) | 1.0 | classifier label → ±1 |

`score = round(Σ / 1.35)` clamped to [-10,+10] (divisor calibrated so all-max ≈ ±10). Label: ≥ +3 BULLISH, ≤ -3 BEARISH, else NEUTRAL. Conviction: |score| ≥ 6 HIGH, 3–5 MEDIUM, else LOW. **Event suppression:** if any HIGH-impact UK/US event is within the next 4h, set `eventSuppressed=true` and cap conviction at MEDIUM (never change the score — display both). Every component pushes a `drivers[]` entry with its detail string (e.g. `"GBP/USD -0.6% → FTSE tailwind (sign-flipped)"`).

**Sector panel derivation (F1):** ENERGY read = sign(brentDayPct, ±0.5% threshold); MINERS = sign(copperDayPct, ±0.75%); BANKS = gilt10yDayBp ≥ +4 → BULLISH, ≤ -4 → BEARISH, longEndStress → BEARISH; PHARMA = always `IDIOSYNCRATIC` with detail "AZN single-stock risk — low macro sensitivity"; STAPLES = ftseImpactFromGbp (USD earners) softened one notch toward NEUTRAL.

---

## 6. ORB CONTEXT & PLAYBOOK (the 15-min Opening Range Breakout layer)

Definitions (Europe/London): cash open **08:00**; ORB = high/low of **08:00–08:15** (three M5 candles); overnight range = **22:00 (prev) → 08:00**; prior-day levels from D_1.

### 6.1 Mechanical `orbContext` (fetch script, hourly)
Compute `mode` from current London time (PRE_OPEN <08:00, ORB_FORMING 08:00-08:15, POST_ORB 08:15-16:30, CLOSED otherwise). Ranges from the UK100 M5/H1/D1 bars fetched in Phase 2a. Gap = (current pre-open price or 08:00 open) − priorClose. `eventWindows` = today's HIGH-impact calendar entries between 07:00-16:30 London. ADR14 from D_1 (mean of last 14 true ranges); `adrUsedPct` = today's range/ADR14.

### 6.2 Skill-generated `OrbPlaybook` (richer, per session record) — decision table the skill MUST follow

Direction (first matching row wins):
| # | Condition | direction |
|---|---|---|
| 1 | HIGH-impact UK print 07:00 today not yet released, or MPC day before 12:00 | `STAND_ASIDE` (until print digested) |
| 2 | `eventSuppressed` and event is within 08:00-09:30 window | `STAND_ASIDE` |
| 3 | bias label BULLISH **and** H1 structure trend ≠ BEARISH | `LONG_ONLY` |
| 4 | bias label BEARISH **and** H1 structure trend ≠ BULLISH | `SHORT_ONLY` |
| 5 | bias NEUTRAL, both macro and structure mixed | `BOTH_OK` (take the break, half size) |
| 6 | bias and H1 structure in outright conflict | `STAND_ASIDE` |

Day type: `EVENT_DRIVEN` if any HIGH event 07:00-16:30; else `TREND_EXPECTED` if |bias score| ≥ 5 AND gap in bias direction AND overnight range < 0.8×ADR14-per-night-norm; else `RANGE_EXPECTED`. Additional narrative rules the skill encodes in `reasoning`: gap >0.4% against bias → warn of gap-fill first ("let the fill complete before the ORB trade"); price opening inside prior-day range with both PDH/PDL unswept → expect a liquidity run at one extreme before trend (classic sweep-then-break — prefer the SECOND break of ORB, not the first); 13:30 US data → "morning move often complete by 13:00, don't chase the pre-US chop"; US open 14:30 can reverse the day — book partials before it. Invalidation: always a concrete price (e.g. "ORB long invalid on M5 close back inside range / below ONL").

---

## 7. `/uk100-session` SKILL — diff table vs `gold-session.md` (copy the file, apply these)

| Section | Change |
|---|---|
| Persona/target | XAUUSD desk analyst → UK100 (FTSE 100) index desk analyst; trader profile: trades the 15-min ORB at London cash open, long/short per playbook |
| Phase A HTTP script | `python3 …/ctrader_http_fetch.py --instrument uk100`; env/401/fallback language identical |
| Phase A macro snapshot | fetch `…/xauusd-dashboard/data/uk100/daily-snapshot.json` (plus keep the gold snapshot fetch as OPTIONAL cross-asset context) |
| Phase B (MCP fallback path) | symbolIds: 113 main (UK100 CFD) / 2 proxy (GBPUSD M5); same explicit from/to timestamp rule |
| Phase C engine | `python3 …/uk100_adapter.py < /tmp/uk100_session_input.json` |
| Kill zones / session table | replace gold's map with §6 London map + the intraday table from the research doc §3 (07:00 UK data → 08:00 open → 09:30 EZ → 13:30 US data → 14:30 US open → 16:30 close), all times Europe/London with BST/GMT rule |
| Liquidity mapping step | replace "Asia high/low swept" with: overnight H/L, prior-day H/L, cash-open range, pre-US consolidation range — from `orb` + `reference_levels` engine blocks |
| Macro step | GBP sign-flip first; sector-panel citation; VIX-regime nuance; gilt long-end stress check; China-via-copper |
| NEW step "ORB PLAYBOOK" | apply §6.2 decision table mechanically; output a dedicated `## ORB PLAYBOOK` section in the brief AND the `orbPlaybook` object in meta |
| Save step | `npx tsx scripts/save-gold-session.ts /tmp/uk100-session-meta.json /tmp/uk100-session-analysis.txt --instrument=uk100`; same "no manual git recovery" block verbatim |
| Meta schema table | same fields + `orbPlaybook` (§3); keep the same section-marker headings so `parsers.ts` regexes keep working |

---

## 8. PHASED BUILD PLAN (execute in order; each phase ends: typecheck+build+test green → commit → push to designated branch → rebase → fast-forward push to `main`)

### Phase 2a — Data plumbing (v0 usable) — est. 2-3h
1. `scripts/lib/ctrader.ts`: §4 symbol additions.
2. `scripts/fetch-uk100-data.ts`: prices + D_1/M5 UK100 bars + BoE CSV fetch (one request, six codes, last 30 business days) + FRED (DGS10/DGS2/DEXUSUK/VIXCLS/DCOILBRENTEU via existing key pattern) + GBP COT (code 096742) + calendar/news (copy gold's Finnhub fetchers; news keyword list: `FTSE,Bank of England,BoE,gilt,sterling,GBP,UK economy,Shell,BP,AstraZeneca,HSBC,rate,inflation,budget,OBR,tariff,China stimulus`) + §5 bias + §6.1 orbContext + Anthropic briefing (prompt in Phase 2e — stub `briefing: null` until then). Static `MPC_DATES_2026` array — **populate from https://www.bankofengland.co.uk/monetary-policy (WebFetch at build time; do not invent dates)**.
3. Workflow step (§4). Run locally once with env vars to generate a real snapshot; commit the generated `public/data/uk100/daily-snapshot.json`.
   **Accept:** local run exits 0 with ≥80% fields non-null during market hours; snapshot validates against `Uk100Snapshot`; gold snapshot untouched; workflow YAML parses (`python3 -c "import yaml,sys; yaml.safe_load(open('.github/workflows/xauusd-daily-fetch.yml'))"`).

### Phase 2b — Macro sub-tab UI — est. 3-4h
Types, hooks, `Uk100Tab` shell, all §4 tiles, App.tsx 4th tab. Every tile handles `null` fields ("—" + dim) — the snapshot WILL have gaps.
   **Accept:** `npm run build` + `npx vitest run` green; tab renders from the committed snapshot; GBP tile shows the sign-flip badge with the correct inversion (unit-test `ftseImpact()`: `-0.5 → 'BULLISH'`); mobile ≤390px no horizontal scroll (screenshot).

### Phase 2c — Engine + skill — est. 3-4h
`ctrader_http_fetch.py --instrument` param; `uk100_sessions.py`; `uk100_adapter.py`; `save-gold-session.ts --instrument` flag; `.claude/commands/uk100-session.md` per §7.
   **Accept:** `python3 ctrader_http_fetch.py --instrument uk100` live → sane summary (UK100 ≈ 10,000-11,000 range sanity check) and `/tmp/uk100_session_input.json`; `python3 uk100_adapter.py < /tmp/uk100_session_input.json` → JSON with `orb`, `session`, `reference_levels`, `data_age_minutes`, h1/m5/m1 blocks; stale-input test (doctor timestamps −2h) exits 1; gold path regression: `--instrument` absent behaves byte-identically (run gold fetch, diff summaries); save script sandbox test: uk100 record lands under `public/data/uk100/sessions/` and gold dir untouched; `analysis/` dirs still identical (`diff -r ICT-SMC-Local-Agent/analysis ICT-SMC-Remote-Agent/analysis` → empty).

### Phase 2d — AI sub-tab UI — est. 2h
`AiSubTab` + `OrbPlaybookCard` + hooks wiring. Seed one real record by running `/uk100-session` end-to-end in-session.
   **Accept:** build/tests green; record renders with ORB card; empty-state ("No sessions yet") renders when index missing.

### Phase 2e — Briefing + risk tone — est. 1-2h
Anthropic calls in fetch script: (1) risk-tone classifier over `newsItems` (≤300 tokens out, JSON response: `{score,label,rationale}`), (2) briefing prompt = gold's briefing skeleton with FTSE framing: sign-flip stated, sector panel injected, VIX-regime nuance, AZN idiosyncratic caveat, ORB-relevance sentence ("what today's macro means for the open"). Reuse gold's response-parsing + `.trim()` + error-tolerance exactly.
   **Accept:** live run produces `riskTone` + `briefing` populated; total added Anthropic cost per run ≤ ~2k output tokens; fetch still exits 0 when `ANTHROPIC_API_KEY` absent (fields null).

### Phase 2f — Verification & docs — est. 1h
Full hourly-workflow dry run via `workflow_dispatch`; confirm Pages deploy carries `/xauusd-dashboard/data/uk100/daily-snapshot.json` (curl 200) and the tab live; update `xauusd-dashboard/README.md` (UK100 section: symbols table, series codes, bias weights, ORB rules — condensed from this doc); note §5 weights are v1 priors — log bias-vs-outcome daily and recalibrate after ~4 weeks (an `resolve-uk100-sessions.ts` outcome resolver is a **later** phase, not v1).

**Estimated total: 12-16 focused hours for a competent lower model.** Phases are independent enough that a session can end after any phase with everything on `main` and nothing half-wired (2a ships data invisible to UI; 2b renders it; 2c is skill-only; 2d renders skill output).

---

## 9. GOTCHAS LEDGER FOR THE BUILDER (read before every phase)

1. **The sign flip.** Strong GBP = BEARISH FTSE. One function (D10), unit-tested. If any tile shows GBP up as bullish-FTSE, the build has failed its primary purpose.
2. **BoE CSV:** one bad series code fails the entire request — request exactly the six verified codes; dates in `DD/Mon/YYYY`; response uses `dd Mon yyyy` rows, business days only (gaps at weekends — "day change" = vs previous ROW, not previous calendar day).
3. **Brent basis:** never render FRED Brent value next to the live CFD price (–$7 basis + lag). Trend arrow only.
4. **VIX is a regime flag** — the bias table caps its bearish contribution at -1 by design. Don't "fix" that.
5. **pipDigits:** all §1.1 symbols divide by 10^5 (verified). UK100 raw bid is ~1.05e9.
6. **No `get_symbols`** anywhere in the pipeline (1.5MB response, historical parser breakages).
7. **07:00 UK prints land BEFORE the 08:00 open** — that's why ORB rule #1 exists; don't reorder the decision table.
8. **`Europe/London` via zoneinfo / the `ukOffsetHours` pattern** — never a fixed UTC offset.
9. **Weekend/closed:** UK100 CFD halts (22:00 Fri → 22:00 Sun London area). Freshness gates will trip by design — a closed-market skill run must report and NOT save, same as gold.
10. **Don't touch `analysis/`** (sync rule). Don't touch gold's session files, parsers' section markers, or the commit-tree push logic.
11. **Anthropic key:** `.trim()` it (newline incident 2026-07-06); missing key → degrade gracefully to null briefing, exit 0.
12. **All tiles null-tolerant** — FRED lags Fridays/holidays; BoE publishes ~9:30am London; first hourly run of the day will have yesterday's BoE values (that's correct, they're daily series — show the series date).

## 10. Token-economy instructions for the builder model

- Copy the named template file first, then edit — do not compose large files from scratch.
- Do not read `fetch-static-data.ts` in full (1,092 lines); read only the functions named in §4 when copying a pattern (FRED fetcher ~L168-200, COT ~L510-560, Finnhub ~L760-830, Anthropic ~L836-960).
- Do not re-run symbol/series verification (§1 is verified); exception: `MPC_DATES_2026` (one WebFetch).
- Run the acceptance commands exactly as written; if one fails, fix and re-run that phase's commands only.
- Commit per phase with message prefix `feat(uk100): …`; push to the designated feature branch, then fast-forward `main` per the established rebase flow.
