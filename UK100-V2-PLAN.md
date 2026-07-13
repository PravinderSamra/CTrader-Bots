# UK100 v2 — Fixes & Enhancements Spec (post-review build plan)

**Status:** ready for implementation · **Written:** 2026-07-12 by the review model (Fable) · **Builder:** Sonnet
**Prerequisite reading:** `UK100-BUILD-PLAN.md` (the v1 spec — architecture, symbols, series codes, gotchas §9 all still apply) and `xauusd-dashboard/README.md` § "UK100 tab".

This plan turns the findings of the 2026-07-11 architecture review into buildable phases. Everything in §1 was **observed live in production**, not hypothesised — do not re-litigate the diagnosis, but do re-verify each fix against the same evidence.

The v1 execution rules apply unchanged to every phase here:
- Each phase ends: `npx tsc --noEmit` + `npm run build` + `npx vitest run` green, workflow YAML parses, **gold pipeline regression-checked** (run `npx tsx scripts/fetch-static-data.ts` shape-check where the shared lib is touched) → commit with a descriptive message → push to the designated branch → rebase → fast-forward push to `main`.
- Never force-push `main`. Never hand-edit `index.json`/`outcomes.json`. Never touch `ICT-SMC-Local-Agent/analysis/` or `ICT-SMC-Remote-Agent/analysis/` (shared gold engine). `skill_adapter.py` and all gold paths must behave byte-identically after every phase.
- API keys are read with `.trim()`. Temp files are written with `cat` heredocs. The save script is only ever integration-tested against a **local scratch clone** (`git clone /home/user/CTrader-Bots /tmp/...`), never the real remote.

---

## 1. VERIFIED EVIDENCE (from the 2026-07-11 review — trust these observations)

### 1.1 cTrader MCP session loss in the TS pipeline (P0)
The production run of 2026-07-11 12:04 UTC (commit `ef2f898`, `public/data/uk100/daily-snapshot.json`) shows:
- Spot prices present (`UK100: 10523.3`) but **every trendbar-derived field null**: `overnightHigh/orbHigh/priorClose/gapPts/adr14` all null; `UK100_dayPct`, `gbpUsdDayPct`, `nas100DayPct`, `copperDayPct` all null.
- The failure **alternates** across the sequential `dayPctFor` calls: US500 ✓, NAS100 ✗, BRENT ✓, COPPER ✗, XAUUSD ✓, GBPUSD ✗.
- The matching error (reproduced locally at the same time): `CTrader MCP HTTP 404: {"jsonrpc":"2.0","error":{"code":-32000,"message":"Session not found; re-initialize"},"id":null}`.

Diagnosis: `scripts/lib/ctrader.ts` uses global `fetch()` per request with **no connection pinning**. The cTrader MCP sits behind a load balancer; the session created by `initialize` lives on one backend, and subsequent requests round-robin — every request landing on the *other* backend 404s. The Python fetcher (`ctrader_http_fetch.py`) already solved exactly this with a persistent keep-alive `http.client` connection (integration guide Lesson 1); the TS lib never got the fix. **This also degrades gold** (same lib powers `fetch-static-data.ts` ADR/prices and `resolve-gold-sessions.ts`).

### 1.2 Event-calendar blind spot (P0 — safety)
`economicCalendar` has been `[]` in **every** live UK100 snapshot observed. Consequences: `bias.eventSuppressed` is always false; `orbContext.eventWindows` always empty; **rows 1–2 of the ORB decision table (STAND_ASIDE on high-impact event mornings) can never fire** except on hardcoded MPC dates. A 07:00 UK CPI morning — the highest-risk setup for an 08:00 ORB trader — currently sails through to LONG_ONLY/SHORT_ONLY. Cause unconfirmed: could be the `regionFromCountry` mapping (`fetch-uk100-data.ts:514`) not matching Finnhub's actual `country`/`currency` values, or Finnhub's `/calendar/economic` being premium-gated on this key (in which case the same applies to gold's calendar). Diagnose first, then harden regardless of cause (§3 Phase A2).

**RESOLVED (Phase A2, 2026-07-11):** confirmed via a triggered `workflow_dispatch` production run (run `29166484720`, job `86580355938`) that Finnhub's `/calendar/economic` returns `{"error":"You don't have access to this resource."}` on this account's key — a **premium-gate**, not a `regionFromCountry` mapping bug. Gold's identical Finnhub calendar call is affected the same way (confirmed in the same job log; left unfixed here, out of scope per this section's own instruction). Fix: `scripts/lib/calendar.ts` adds a hand-verified `UK_STATIC_CALENDAR_2026` (CPI/Labour Market/GDP/Retail Sales next-occurrence dates from each series' ONS "latest" bulletin page, plus the existing MPC dates) and a pure `mergeCalendars(finnhub, staticEntries, today)` that dedupes by (date, keyword-class) with the static entry winning, trims to the 0–4 day lookahead window, and becomes the calendar's primary UK source. Only the *next* occurrence per series was verified — ONS release cadence is irregular (CPI alone ran 18 Feb → 25 Mar → 22 Apr → 20 May → 17 Jun → 22 Jul, 4–5 week gaps, no fixed day-of-month) — so later 2026 dates were deliberately not extrapolated and must be re-verified against the source bulletin as each date passes.

### 1.3 Bias-driver label noise (P1)
2026-07-11 snapshot: GBP/USD moved **−0.09%** (pure noise) and the weight-3 GBP driver displayed **BULLISH**. The label threshold in `computeBias` (`fetch-uk100-data.ts`, GBP block: `impact: comp > 0.3 ? 'BULLISH' ...`) fires at |comp| > 0.3, i.e. a cable move of just **0.075%**. The *score* contribution is correctly small — only the human-facing label misleads. Same over-sensitivity applies to US futures / Brent / Copper labels.

### 1.4 VIX regime naming split-brain (P1)
Same number, same dashboard, two labels: UK100's `vixRegime()` (`fetch-uk100-data.ts:623`) calls VIX 16.7 **ELEVATED** (bands <15 / 15–25 / >25 = CALM/ELEVATED/STRESS) while gold's `EquitiesTile.tsx:39` calls the same 16.7 **NORMAL** (>25 = "ELEVATED"). Observed live on 2026-07-11 with VIX 16.7 shown on both tabs.

### 1.5 Two definitions of "ORB broken" (P1)
- TS hourly snapshot (`computeOrbContext`, `fetch-uk100-data.ts` ~line 842): current price vs range — **non-sticky**, flips back to `NONE` if price re-enters the range.
- Python engine (`uk100_sessions.orb_window`): first M5 **close** outside the range, chronological — **sticky**. This is the correct definition for the strategy.
The two layers can disagree on the same day. The snapshot must adopt the engine's definition.

### 1.6 Snapshot timing misses the ORB window (P1)
Cron `0 6-20 * * 1-5` fires at 08:00 London (range not yet formed) and next at 09:00 — ORB numbers reach the macro tab ~45 min late for an ORB trader, in both BST and GMT seasons.

### 1.7 Structural/feedback gaps (P2–P4)
- No `resolve-uk100-sessions.ts` → no outcome archive, no Track Record card, no data for the planned ~4-week bias-weight recalibration.
- The GBP↔FTSE inverse correlation (the weight-3 assumption underpinning the whole section) is **regime-dependent** — it breaks in UK-domestic-crisis episodes (2022 gilt crisis: GBP↓, gilts↓, FTSE↓ together). Nothing currently measures whether the inverse link is live.
- No European-tape driver: at 08:00 London, US futures are thin Globex; the DAX opens *with* the FTSE (GER40 = symbolId 110, already in `KNOWN_SYMBOL_IDS`).
- No volume confirmation on the ORB break (M5 tick volume is already fetched by the Python side).
- Playbook has no numeric size guidance (`BOTH_OK → "half size"` exists only as prose).
- Every playbook heuristic (prefer second break, gap-fill >0.4%, morning-done-by-13:00) is an **unmeasured prior** — no ORB backtest exists.
- UI: UK100 tiles have no sparkline history (gold does); ORB tile has no pre-open countdown; `AiSubTab.tsx` duplicates ~400 lines of `GoldSessionTab.tsx`.

---

## 2. PHASE MAP (execute in order; A and B are independent of each other but do A first)

| Phase | Priority | Content | Est. |
|---|---|---|---|
| A | P0 | cTrader session fix · calendar diagnosis + static UK calendar | 2–3 h |
| B | P1 | Label thresholds · VIX unification · sticky ORB-broken · extra cron | 1–2 h |
| C | P2 | `resolve-uk100-sessions.ts` + outcomes + Track Record card | 2–3 h |
| D | P3 | GBP↔FTSE correlation · GER40 driver · volume confirmation · riskFraction | 3–4 h |
| E | P4 | ORB backtest (probe → harvest → stats → integrate) | 4–6 h |
| F | P5 | Sparklines · pre-open countdown · (optional) AiSubTab dedup | 2–3 h |

---

## 3. PHASE A — P0 fixes

### A1 — cTrader session resilience (`xauusd-dashboard/scripts/lib/ctrader.ts`)

Primary fix — **detect-and-reinit retry** (dependency-free, addresses the observed 404 directly):

1. `mcpFetch` currently discards the body on `!res.ok` (returns `{data: null}`), so callers can't see the JSON-RPC error. Change: on `!res.ok`, still attempt to parse the body (it IS the JSON-RPC error object, per §1.1 evidence) and return it as `data` alongside a new `httpStatus` field. Keep the existing `console.error` log line.
2. In `CTraderClient.callTool`, after each attempt, check for the session-loss signature: `parsed?.error?.message` containing `"Session not found"` (or `error.code === -32000`). On match: call `this.init()` again, then replay the call. **Bounded at 3 total attempts per call** (initial + 2 retries, each preceded by re-init), with a `console.error` noting each retry so failures remain visible in Actions logs.
3. `getTrendbars` needs no change (it goes through `callTool`).

Secondary fix — **connection pinning** (do this too; it prevents rather than repairs): add `undici` as a devDependency and construct one shared `new Agent({ keepAliveTimeout: 30_000, connections: 1 })`, passed to every `fetch` in `mcpFetch` via the `dispatcher` option. `connections: 1` serialises onto a single pinned TCP connection — the TS equivalent of the Python fetcher's Lesson-1 fix. If `undici`'s types fight the ambient `fetch` signature, cast narrowly at the call site rather than loosening the whole file.

**Acceptance:**
- Run `CTRADER_MCP_TOKEN="$CTRADER_MCP_SLUG" npx tsx scripts/fetch-uk100-data.ts` **three times** during market hours: zero unrecovered "Session not found" in output; all six `dayPct` values and all `orbContext` bar-derived fields non-null in all three runs. (If run outside market hours, bars still exist — dayPct/priorClose must be non-null regardless; only intra-day freshness differs.)
- Gold regression: `npx tsx scripts/fetch-static-data.ts` runs, snapshot shape unchanged (`git diff --stat` shows only value changes), then `git checkout -- public/data/` to discard both locally-generated snapshots (this sandbox lacks FRED/Finnhub/Anthropic keys — a local snapshot is strictly worse than the committed one; the hourly workflow regenerates).
- `resolve-gold-sessions.ts --dry` still runs clean (same lib).

### A2 — Event-calendar hardening

**Step 1 — diagnose (do not skip).** Add temporary logging to `fetchUk100Calendar`: HTTP status, raw body length, `economicCalendar.length` before filtering, and the first 3 raw events' `{country, currency, event, impact}`. Run once with the real key absent locally is useless — instead inspect the **next production run's Actions log** (or trigger `workflow_dispatch` and read the log via the GitHub MCP tools). Record the finding in the commit message: (a) mapping bug → fix `regionFromCountry` against the observed values and add a unit test with those literal values; (b) endpoint premium-gated/empty → note it, the static calendar below becomes the primary UK source (and flag that gold's calendar has the same issue, but do NOT change gold in this phase).

**Step 2 — static UK release calendar (build regardless of Step 1's outcome).**
- New const in `fetch-uk100-data.ts` (adjacent to `MPC_DATES_2026`): `UK_STATIC_CALENDAR_2026: { date: string; event: string; timeLondon: string; impact: 'HIGH' }[]` covering, for the remainder of 2026: **CPI** (monthly, 07:00), **Labour market / wages** (monthly, 07:00), **monthly GDP** (07:00), **Retail sales** (07:00), plus the existing MPC dates (12:00 decision — represent them here too so one array feeds the calendar).
- **Populate from the ONS release calendar via WebFetch at build time (https://www.ons.gov.uk/releasecalendar) — do not invent dates.** If the fetch fails, commit the structure with the entries you can verify from the BoE site plus a loud `// TODO: populate from ONS` and say so in the commit message. Wrong dates are worse than missing dates — only include what you verified.
- Merge into the calendar result: convert static entries to `Uk100CalendarEvent` (region `'UK'`, `timeIso` from date+time London→UTC using the existing `londonOffsetHours`), union with Finnhub's list, dedupe by `(date, keyword-class)` where keyword-class ∈ {cpi, gdp, labour/employment/wage, retail, mpc/bank rate} matched case-insensitively against the event name. Static entry wins on duplicate (its 07:00 timing is authoritative).
- `daysFromToday` for static entries computed the same way as Finnhub ones; entries with `daysFromToday < 0` or `> 4` are dropped at snapshot-build time (the array is the whole year; the snapshot only carries this week — same week-window the Finnhub path uses).

**Acceptance:** unit tests for the merge/dedupe (pure function — extract it as `mergeCalendars(finnhub, staticEntries, today)`); a `workflow_dispatch` run during a week containing a known UK release shows it in `economicCalendar` with `impact: 'HIGH'`; on such a day `bias.eventSuppressed === true` and `orbContext.eventWindows` non-empty. The `/uk100-session` decision-table rows 1–2 need no change — they read the snapshot.

---

## 4. PHASE B — P1 calibration & consistency

### B1 — Label thresholds in `computeBias`
For the four **continuous** drivers only (GBP, US futures, Brent, Copper): change the label rule from `|comp| > 0.3` to `|comp| ≥ 0.8`. Resulting label floors: GBP ±0.2% · US500 ±0.3% · Brent/Copper ±0.6%. **Do not change the score arithmetic** — `weightedSum` stays as-is; only the human-facing `impact` label. Discrete drivers (VIX, gilts, COT, risk tone) unchanged. Update/extend the bias unit tests: `-0.09%` GBP must now label NEUTRAL (regression pin against §1.3), `-0.6%` must label BULLISH.

### B2 — One VIX vocabulary across the dashboard
Canonical bands, both tabs: **CALM < 15 · NORMAL 15–25 · STRESS > 25.**
- `fetch-uk100-data.ts` `vixRegime()`: rename middle band `ELEVATED` → `NORMAL` (math identical; the bias driver's CALM +1 / middle 0 / STRESS −1 is unchanged).
- Types: `UsLinkageBlock.vixRegime` in both the script-local interface and `src/types/uk100.ts` → `'CALM' | 'NORMAL' | 'STRESS'`.
- UI: `Uk100UsLinkageTile` badge mapping (`NORMAL` → `badge-muted`, `STRESS` → `badge-red`); `explainers.ts` `explainUsLinkage` branches (keep the STRESS wording; middle branch says "normal"); gold's `EquitiesTile.tsx` `vixCtx`: `'ELEVATED'`(>25) → `'STRESS'` — one string, cosmetic only.
- Docs: README bias table row; `uk100-session.md` mentions of CALM/ELEVATED/STRESS.
- **Tolerance:** already-published snapshots still say `"ELEVATED"` until the next hourly run. Renderers print the string as-is (safe); `explainUsLinkage` must treat an unrecognised value as the middle band, not crash. Add a test for that.

### B3 — Sticky `orbBrokenDirection` in the hourly snapshot
Make the TS definition identical to the engine's: **first M5 close outside the ORB range after 08:15, chronological, sticky.**
- `fetchCtraderData`: add one more targeted fetch — M5 from `cashOpen + 15min` to `min(now, cashOpen + 8h15m)` (16:30 London). Bar-count check: 08:15→16:30 = 8h15m = **99 bars**, under the 100-bar cap (v1 gotcha §9). Skip the fetch when `now < cashOpen + 20min` (nothing to scan yet).
- `computeOrbContext`: replace the current-price comparison with a scan of those closes: first `close > orbHigh` → `'UP'`, first `close < orbLow` → `'DOWN'`, else `'NONE'`. Null-safe when the post-ORB series is absent (PRE_OPEN / fetch failure) — keep the existing `null` semantics for "unknown".
- Acceptance: unit-test the scan as a pure function (`firstCloseOutside(bars, orbHigh, orbLow)`) including the re-entry case: bars that break up then close back inside must still report `'UP'`.

### B4 — ORB-window cron
`.github/workflows/xauusd-daily-fetch.yml`: change the schedule to add `'20 7,8 * * 1-5'`. In BST, 07:20Z = 08:20 London (fresh ORB 5 min after formation); in GMT winter, 08:20Z = 08:20 London. The off-season sibling run is harmless (one extra refresh). YAML-parse check per the standard rules; note the two extra commits/day in the commit message.

---

## 5. PHASE C — Outcome resolver & track record (the feedback loop)

### C1 — `xauusd-dashboard/scripts/resolve-uk100-sessions.ts`
**Copy `resolve-gold-sessions.ts` as the template** (read it first — its header documents the WIN/LOSS/EXPIRED semantics) and change only:
- `DATA_DIR = public/data/uk100/sessions`, `OUTCOMES_FILE` alongside it; symbol `UK100` (id 113 via `KNOWN_SYMBOL_IDS`), H1 bars for scoring.
- Keep `MIN_AGE_MS = 4h`, `MAX_LOOKBACK_DAYS = 21`. **Change the scoring window:** gold uses a flat `WINDOW_MS = 8h`; UK100's ORB trade is strictly intraday, so the window is `min(analysisTime + 8h, same-day 16:30 London)` — bars after the cash close must not score an intraday call. Compute the 16:30 cutoff with the same `ukOffsetHours` helper used in `save-gold-session.ts` (copy it locally; do not import across scripts — matches existing convention).
- Outcome rows: same shape as gold's plus one field — `orbDirection` copied from the record's `orbPlaybook.direction` (nullable). This lets calibration later slice win-rates by playbook direction, including confirming that STAND_ASIDE days were genuinely worth skipping.
- Bot identity for the write-back commit: reuse the resolver's existing commit approach from gold verbatim (whatever it does — read, don't assume).

### C2 — Workflow wiring
New step in `xauusd-daily-fetch.yml` directly after "Resolve gold-session outcomes", `continue-on-error: true`, env = the two cTrader secrets only. The commit step already stages all of `public/data/` — verify `uk100/sessions/**` and the new outcomes file are inside its `git add` path (they are: it stages `xauusd-dashboard/public/data/`).

### C3 — Track Record UI on the AI sub-tab
- `useUk100Sessions.ts`: add `useUk100SessionOutcomes()` mirroring gold's `useSessionOutcomes` (path `data/uk100/sessions/outcomes.json`).
- `AiSubTab.tsx`: add `OutcomeGlyph` next to sidebar entries and the `TrackRecord` card below the list. Gold's versions live un-exported inside `GoldSessionTab.tsx` — **copy them** (≈80 lines incl. `computeTrackStats`) rather than exporting from gold's file; consolidation is Phase F3's job. Types (`OutcomeRow` etc.) already exist in `types/dashboard.ts` — reuse those imports; do not duplicate the types.
- Acceptance: with an empty/missing outcomes.json the tab renders exactly as today (card hidden); with a fabricated outcomes fixture in a vitest DOM test or a local preview, glyphs and card render. Dry-run the resolver against the sandbox record from Phase 2c testing if any exists, else against a synthetic record in a scratch clone.

---

## 6. PHASE D — Signal quality

### D1 — GBP↔FTSE rolling correlation (guards the weight-3 assumption)
- `fetchCtraderData`: extend the existing UK100 D_1 window from 22 → **30 days (not 32 — corrected during F8, UK100-SESSION-REVIEW-2026-07-13.md: `get_trendbars` D_1 has a hard cap live-verified at exactly 30 calendar days; 31 silently returns 0 bars)**, and add a GBPUSD D_1 fetch over the same window (one extra sequential call). Compute Pearson correlation of the paired **daily close-to-close returns** over the most recent 20 overlapping days → `fx.gbpFtseCorr20d: number | null` (round 2 dp). **`pearson()`, plus the date-keyed pairing helpers `dailyReturnsByDate()`/`pairByDate()`, already exist in `scripts/lib/stats.ts` (built for F8's European-tape correlation) — reuse them, do not re-extract.**
- Bias engine: new input `gbpFtseCorr20d`. In the GBP block, when `corr != null && corr > -0.2` (inverse link currently weak/absent/positive), **halve the GBP component** (multiplicative — stacks with the existing ERI-disagreement halving) and set the driver detail to note it, e.g. `"… (inverse GBP link weak: 20d corr ${corr} — component halved)"`.
- UI: one row on `Uk100FxTile` (`20d corr` + value, `down`-coloured when > −0.2); `explainFx` gains a branch: when the link is weak, append a sentence explaining that the usual weak-pound-helps rule is not currently reliable. Update the FX explainer tests.
- Types + README bias-table footnote.

### D2 — GER40 European-tape driver
- Add `GER40` to the UK100 price fetch (symbolId 110 — already in `KNOWN_SYMBOL_IDS`/`PIP_DIGITS`) + `dayPctFor('GER40')`.
- Types: `Uk100Prices.GER40`, `UsLinkageBlock.ger40DayPct` (script-local + `types/uk100.ts`).
- New bias driver **"European tape (GER40)", weight 2.0**: `comp = clamp(ger40DayPct / 0.75 × 2, ±2)`, label at |comp| ≥ 0.8 (B1 convention), 0 when null.
- **Divisor recalibration:** total weight rises 13 → 15, so `weightedSum / 1.35` → `weightedSum / 1.56` (= 1.35 × 15/13, keeping the score scale comparable). State in a comment that weights AND divisor remain v1.1 priors pending Phase E / resolver calibration.
- UI: GER40 row on the US-linkage tile (retitle its eyebrow to "US & Europe Linkage"); `explainUsLinkage` may mention Europe when GER40 is the larger mover — keep it to one optional clause. README weights table + `uk100-session.md` STEP 5 mention.
- Tests: bias unit test with GER40 ±; regression: all-null inputs still produce score 0.

### D3 — Volume confirmation on the ORB break (Python engine only)
The hourly TS side lacks the M5 history for a volume baseline; implement where it exists — `uk100_sessions.py` / `uk100_adapter.py`:
- `orb_window(...)`: when a break bar is found (existing first-close-outside scan), compute `break_volume_ratio = breakBar.volume / mean(volume of the 20 M5 bars preceding it)` (from the general `m5_candles` series). Add to the returned dict: `break_volume_ratio` (rounded 2 dp, `None` if no break or <20 prior bars or zero baseline) and `volume_confirmed` (`True` if ratio ≥ 1.2, `False` if < 1.2, `None` when ratio is `None`). Note in a comment: cTrader index-CFD volume is **tick volume** — valid relatively, not absolute contracts.
- Skill doc `uk100-session.md`: STEP 8 reasoning must cite it when present ("break came on {strong|weak} participation — weak-volume breaks fail more often; prefer the retest entry"); meta `orbPlaybook` gains optional `volumeConfirmed?: boolean | null`.
- Types: `OrbPlaybook.volumeConfirmed` in `types/uk100.ts` + save-script interface; `OrbPlaybookCard` renders one small line when non-null ("Break volume: confirmed ✓ / weak ✗").
- Tests: Python — extend the live-verification step (fabricated candle fixtures piped to `uk100_adapter.py` are acceptable if doctored timestamps keep the freshness gate happy — set them to `now`); TS — card renders both states.

### D4 — Playbook `riskFraction`
Deterministic mapping, computed in STEP 8 alongside the direction (skill doc + meta schema + types + card):

| Condition | riskFraction |
|---|---|
| STAND_ASIDE | 0 |
| BOTH_OK, non-event day | 0.5 |
| LONG_ONLY / SHORT_ONLY, non-event day | 1.0 |
| any tradeable direction on an EVENT_DRIVEN day | half the above (0.25 / 0.5) |

`OrbPlaybookCard` renders "Suggested size: {riskFraction × 100}% of normal risk" under the pill. Optional field — old records without it render unchanged.

---

## 7. PHASE E — ORB backtest (replace priors with base rates)

New script: `ICT-SMC-Local-Agent/uk100_orb_backtest.py`. Reuse the session-pinned client: `from ctrader_http_fetch import _Client, _token, _PIP, INSTRUMENTS` (module-level names — import, don't copy). Everything below runs against symbolId 113.

**E1 — Probe history depth first (result gates scope).** Request D_1 bars from 3 years back to now (one call — D_1 for 3y ≈ 780 bars will be capped at 100; instead walk backwards in 100-day windows until an empty window returns). Record `earliest_available_date`. If depth < 6 months, the backtest still runs — report `n` prominently and treat all stats as low-confidence. **Do not present small-n numbers without their n.**

**E2 — Harvest (cache aggressively).** For each trading day from `earliest` to yesterday:
- M5 window 1: 07:00→12:00 London (60 bars) · M5 window 2: 12:00→16:30 London (54 bars) — both under the 100-bar cap. One D_1 pass (chunked as in E1) supplies prior closes and ADR.
- Cache each day to `ICT-SMC-Local-Agent/backtest_cache/uk100/YYYY-MM-DD.json` (gitignore the cache dir); skip cached days on re-run; `time.sleep(0.15)` between requests. ~2 requests/day ≈ 1,000 requests for two years — one run of a few minutes.

**E3 — Per-day computation** (pure functions, unit-tested against 3 hand-built fixture days):
- ORB = high/low of the three 08:00–08:15 bars. Entry model: **entry at the close of the first bar closing outside the range; stop = opposite ORB boundary; R = |entry − stop|.**
- Record: break direction & time · outcome at 1R and 2R (which was touched first: +1R/+2R or the stop, scanning highs/lows bar-by-bar; a bar touching both counts as a loss — conservative) · MFE/MAE to 16:30 in R · whether price later closed out the opposite side (failed first break) · **second break**: the next close outside either boundary after a failed first break, scored the same way · gap vs prior close (pts and %, with/against first-break direction) · day-of-week · overnight-range-vs-ADR14 bucket.
- **Honest limitation, state it in the report:** historical *bias alignment* cannot be scored — no bias history exists. Bias-conditional stats come later from the Phase C resolver archive. Do not synthesise a retro-bias.

**E4 — Outputs.**
- `UK100-ORB-BACKTEST.md` (repo root): methodology (entry/stop/targets exactly as above), n, date range, then tables — first-break 1R/2R win rates overall · by direction · by day-of-week · by gap bucket (none / <0.4% with / <0.4% against / >0.4% with / >0.4% against) · first vs second break · median MFE/MAE · median time of day-high/day-low after an 08:15 break.
- `xauusd-dashboard/public/data/uk100/orb-stats.json`: the same numbers machine-readable `{generatedAt, n, dateRange, stats: {...}}` — committed, so the skill and UI can cite it.

**E5 — Integrate.** Update `uk100-session.md` STEP 8's narrative rules to cite the measured numbers, and — critically — **where the data contradicts a v1 heuristic (e.g. the second-break preference), change the rule to follow the data and say so in the doc**; do not keep a refuted rule for continuity. Add one line to the OrbPlaybookCard footer: "Base rates: first-break 1R hold {x}% (n={n})" read from `orb-stats.json` via a tiny hook (null-safe when the file is absent).

---

## 8. PHASE F — UI polish

- **F1 Sparklines:** mirror gold's `appendHistory` in `fetch-uk100-data.ts` → `public/data/uk100/history.json`, rolling 7 days, points `{ts, uk100, gbpusd, gilt10y, vix}`; add `useUk100History` hook; render `SparkLine` (existing component) under the UK100 price context on the FX and Rates tiles. Follow gold's pruning/append semantics exactly (read `appendHistory` first).
- **F2 Pre-open countdown:** in `Uk100OrbTile`, when `orb.mode === 'PRE_OPEN'`, render a chip "cash open in {H}h {M}m" computed client-side against the next 08:00 Europe/London (reuse the repo's UK-offset convention; a 60 s interval refresh like `CalendarTile`'s countdown).
- **F3 (optional, stretch):** extract the duplicated brief-renderer internals (`KVCard`, `ProbCard`, `LevelsCard`, `Collapsible`, `ProseBody`, `Inline`, `TradeCard`) from `GoldSessionTab.tsx`/`AiSubTab.tsx` into `src/components/session-shared/`, both tabs consuming them. Acceptance is a before/after screenshot pair of BOTH tabs showing no visual change. If this drags past ~1.5 h, stop and leave it — it's maintenance, not function.

---

## 9. GOTCHAS LEDGER (v2 additions — v1's §9 still applies in full)

1. **The 100-bar cap governs every new fetch window in this plan.** B3's post-ORB window (99 bars), E2's two M5 windows (60/54) were sized to fit — if you change any window, redo the bar arithmetic.
2. **Session-not-found retries must be bounded and logged.** An unbounded re-init loop against a dead backend would hang the hourly workflow. 3 attempts, loud logs.
3. **Old snapshots carry `"ELEVATED"`** after B2 — every consumer of `vixRegime` must tolerate unknown strings until the next hourly overwrite.
4. **Static calendar dates must be verified, never invented** (A2). An invented CPI date that suppresses the wrong morning — or misses the right one — is worse than the current blind spot, because it *looks* covered.
5. **Score vs label:** B1/D1/D2 must not change `weightedSum` semantics except where explicitly specified (D1 halving, D2 new driver + divisor). Pin with unit tests: identical inputs pre/post B1 give identical scores.
6. **Backtest conservatism:** a bar touching both stop and target counts as a loss; state every modelling choice in the report. No fill/slippage/spread modelling — say so.
7. **Resolver writes to `main`** exactly like gold's — test only in a scratch clone; never point a test run at the real remote.
8. **This sandbox has no FRED/Finnhub/Anthropic keys.** Local runs produce degraded snapshots — never commit one over the workflow's (checkout-restore after local verification, as in Phases 2a–2f).
9. **`orb-stats.json` and `outcomes.json` are append/regenerate artifacts** — the UI must render fully when either is missing (pre-first-run state).

## 10. BUILDER INSTRUCTIONS (token economy)

Work phase-by-phase in order; one commit+push cycle per phase (sub-splitting C or D into two commits is fine). Before each phase, read only the files that phase names — this doc plus v1's §9 carry the context so you do not need to re-derive the architecture. Where this doc says "read X first", that is load-bearing: the gold resolver, `appendHistory`, and the gold TrackRecord internals are the templates, and semantics must be cloned, not reinvented. When live verification is blocked (market closed, missing key), verify what is verifiable, say precisely what was and wasn't verified in the commit message, and do not fabricate a pass. If a finding in §1 turns out to differ from what you observe (e.g. the calendar starts returning events), update THIS file's §1 with the new evidence in the same commit.
