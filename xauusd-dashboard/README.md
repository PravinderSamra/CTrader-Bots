# XAUUSD Intelligence Dashboard

A static, public dashboard ([live site](https://pravindersamra.github.io/CTrader-Bots/xauusd-dashboard/)) that gives a beginner ICT/SMC gold day trader a single-glance macro picture before the London/New York sessions: yields, Fed expectations, COT positioning, ETF flows, dollar-liquidity stress, geopolitical risk, an economic calendar, and an AI-generated plain-English daily briefing with a directional bias gauge.

It is deliberately **not** a live order-execution tool — it's a pre-session intelligence briefing, consumed by both a human trader and (via `daily-snapshot.json`) the `/gold-session` agent skill described in `../ICT-SMC-Local-Agent/GOLD_SESSION_SKILL.md`.

## Architecture

```
xauusd-dashboard/
├── scripts/fetch-static-data.ts   Server-side fetcher — runs in CI only, never in the browser
├── public/data/daily-snapshot.json  Generated output (committed to the repo)
├── src/
│   ├── App.tsx                    Top-level composition, session-label logic
│   ├── hooks/
│   │   ├── useFredData.ts         Fetches the static daily-snapshot.json
│   │   └── useCTraderPrices.ts    Optional 15s live price polling (see Security below)
│   ├── services/
│   │   └── dataAggregator.ts      Combines live prices + snapshot into one view-model, computes risk tone
│   ├── components/tiles/*         One component per data tile (Yields, Dollar, Calendar, Gold, Equities, Fed, Positioning, Flows)
│   └── components/briefing/       BiasGauge + BriefingPanel (renders the pre-computed AI briefing)
└── types/dashboard.ts             Shared TypeScript interfaces
```

### Data flow

1. **`xauusd-daily-fetch.yml`** runs hourly, on the hour, 06:00–20:00 GMT Mon–Fri (and on manual dispatch) — covering London open through NY close so intraday catalysts aren't missed. It executes `scripts/fetch-static-data.ts` server-side (Node, via `tsx`), which:
   - Pulls yields, real yields, breakevens from FRED
   - Derives Fed rate-cut/hold/hike probabilities from CME Fed Funds futures (Yahoo) with a DGS1MO fallback
   - Pulls GVZ (gold volatility) from CBOE → Yahoo → Stooq → FRED, in that fallback order
   - Pulls CFTC COT positioning (net long, open interest, crowding label)
   - Pulls SPDR GLD holdings (ETF flow trend)
   - Pulls the Caldara-Iacoviello Geopolitical Risk Index (parsed from a published `.xls` file)
   - Pulls live spot prices, ADR, and gold/silver ratio from the **cTrader MCP server** (server-side call, using a non-`VITE_`-prefixed token — see Security)
   - Pulls the **week-ahead** economic calendar (today through Friday, each event tagged `daysFromToday`) and **recent** (last 24h, recency-tagged via `hoursAgo`) gold/Fed/yield/geopolitics-relevant news from **Finnhub** (server-side)
   - Calls the **Anthropic API** to generate the briefing paragraph + bias score, incorporating recent catalysts and any build-up caution ahead of later-in-week HIGH-impact events (server-side)
   - Writes everything to `public/data/daily-snapshot.json` and commits it to `main`
2. The same workflow then builds the dashboard (`npm run build`) and deploys the static bundle to GitHub Pages.
3. **`deploy-dashboard.yml`** runs on every push to `xauusd-dashboard/src/**` (or manual dispatch) and re-deploys the dashboard using whatever `daily-snapshot.json` is already committed — it does **not** re-run the fetch script.
4. In the browser, `useFredData.ts` fetches `data/daily-snapshot.json` (a same-origin static file, no API key required) and the UI renders entirely from it. `useCTraderPrices.ts` additionally attempts a 15-second live poll of the cTrader MCP server for fresher prices; if no token is configured (the current default — see below) it reports `status: 'offline'` and the UI transparently falls back to the snapshot prices via `pricesFromSnapshot()`.

### Week-ahead calendar & recent catalysts

- **`CalendarTile`** now shows the whole current week's events (not just today), grouped by day, and surfaces a build-up-caution banner whenever a HIGH-impact event is 1–4 days out — flagging that price action into the release is likely to be cautious/range-bound rather than committal.
- **`BriefingPanel`**'s "Recent Catalysts" list shows news items from the last 24h with an "Xh ago" / "Xm ago" recency badge and source, so a same-day move (e.g. a rumor about central banks reducing dollar exposure) can be cross-referenced against price action instead of going unexplained.
- The `/gold-session` agent skill (`.claude/commands/gold-session.md`) consumes the same `economicCalendar`/`newsItems` fields and is instructed to call out build-up caution and recent-catalyst explanations in its MACRO REGIME section.

### Briefing generation

The briefing (directional bias, confidence score, 200–300 word plain-English paragraph) is regenerated **hourly during London/NY hours**, server-side, by `generateDailyBriefing()` in `fetch-static-data.ts` — it reuses the same system prompt and JSON-output contract that used to live in `src/services/anthropicBriefing.ts` (since removed; see Security). The dashboard no longer has a "Generate Briefing" button — `BriefingPanel.tsx` simply renders `snapshot.briefing` and shows a "not yet available" placeholder before the first scheduled run of the day.

## Gold-Session AI tab

The dashboard's second tab ("Gold-Session AI") stores a rolling 3-day history of `/gold-session` analyses. Each entry is saved automatically at the end of every skill run — no manual action required from the trader.

### Data structure

```
xauusd-dashboard/
├── public/data/sessions/
│   ├── index.json                  Rolling 3-day index (max 3 days of entries)
│   └── YYYY-MM-DD/
│       └── HH-MM.json              One file per analysis (filename uses UTC for stability)
└── scripts/save-gold-session.ts    Save script — called by the skill at STEP 8
```

**`index.json`** shape:
```json
{
  "updatedAt": "2026-06-30T21:48:30.283Z",
  "sessions": [
    {
      "date": "2026-06-30",
      "time": "21:48 GMT",
      "filename": "2026-06-30/21-48.json",
      "session": "NEW_YORK",
      "bias": "BEARISH",
      "biasScore": -3,
      "probability": 65,
      "confidence": 5,
      "timestamp": "2026-06-30T21:48:30.283Z"
    }
  ]
}
```

**Session record** (`YYYY-MM-DD/HH-MM.json`) adds `analysis` (the full plain-text brief) to all index fields.

The index is maintained as a rolling window: entries older than 3 days are pruned on each write. The newest entry is always listed first.

### `save-gold-session.ts` — the save script

Called by the skill at the end of every run (STEP 8 in `gold-session.md`) with two temp files:

```bash
cd xauusd-dashboard
npx tsx scripts/save-gold-session.ts /tmp/gold-session-meta.json /tmp/gold-session-analysis.txt
```

- **`/tmp/gold-session-meta.json`** — 5 scalar fields: `session`, `bias`, `biasScore`, `probability`, `confidence`.
- **`/tmp/gold-session-analysis.txt`** — full analysis text (everything from the `# GOLD INTRADAY SESSION BRIEF` header to the end of `[DISCLAIMER]`). Kept as a separate file to avoid JSON-escaping a multi-kilobyte string.

The script computes UK time (BST = UTC+1 from last Sunday in March to last Sunday in October, else GMT), uses UTC time for the filename (so filenames are stable), and stores the UK-local time as the `time` display field (e.g. `"21:48 GMT"` or `"14:30 BST"`). It then commits the session file and updated index to `main` and pushes, triggering a GitHub Actions deploy (~1–2 min).

**ESM note:** the script uses `fileURLToPath(import.meta.url)` + `path.dirname()` instead of `__dirname` because the project's `tsconfig.json` targets ES modules — `__dirname` is not defined in ESM scope.

### How the tab renders

`GoldSessionTab.tsx` fetches `index.json` on load, displays entries grouped by day in a left sidebar (most recent first, labelled TODAY / YESTERDAY / day-name), and shows the full analysis for the selected entry in the main view alongside a `BiasGauge` component. The `time` field already includes the timezone label (`GMT` / `BST`) — the component does not append it again.

### MCP permissions required

The `/gold-session` skill needs the following tools pre-approved in `.claude/settings.json` (committed at repo root) so it can run without per-call prompts:

```json
"mcp__ctrader__get_version",
"mcp__ctrader__get_symbols",
"mcp__ctrader__get_spot_prices",
"mcp__ctrader__get_trendbars",
"mcp__ctrader__get_positions",
"mcp__ctrader__get_balance",
"mcp__tradingview-mcp__recognize_market_pattern",
"mcp__tradingview-mcp__get_trade_levels",
"mcp__tradingview-mcp__risk_based_position_size"
```

These are committed in `.claude/settings.json` at the repo root. **Do not use `.claude/settings.local.json`** for these — that file is globally gitignored by `/root/.config/git/ignore` and permissions added there are lost when the container is recycled.

---

## UK100 tab

The dashboard's third tab ("UK100") is a FTSE 100 index intelligence section built
around one specific trade: the **15-minute Opening Range Breakout (ORB) at London
cash open (08:00)**. It has two sub-tabs — **Macro** (a live snapshot of everything
that moves the index) and **AI Session** (a rolling 3-day history of `/uk100-session`
ICT/SMC briefs, each ending in a mechanical ORB playbook). Full design rationale
lives in `../UK100-BUILD-PLAN.md` at the repo root — this section is a condensed
operational reference.

### The GBP sign-flip (read this first)

UK100 and GBP are **inversely** correlated — weak GBP lifts the index's dollar/euro-
earning multinationals, strong GBP is a headwind. This is the opposite of gold's
DXY relationship and is the single most important rule in the whole section: every
tile, the bias engine, and the `/uk100-session` skill all sign-flip GBP moves before
using them. `fx.ftseImpactFromGbp` in the snapshot is already sign-flipped — never
re-derive the sign yourself.

### Data flow

`scripts/fetch-uk100-data.ts` runs as an extra step inside the existing
`xauusd-daily-fetch.yml` workflow (hourly, 06:00–20:00 GMT Mon–Fri), with
`continue-on-error: true` so a UK100 failure never blocks the gold snapshot/deploy.
It:
- Pulls UK100/GBPUSD/GBPEUR/US500/NAS100/BRENT/COPPER/VIX/USDX spot + bars from
  **cTrader** (server-side, `scripts/lib/ctrader.ts`), including two dedicated
  exact-timestamp fetches for the overnight range (22:00 prev day → 08:00) and the
  ORB itself (08:00–08:15) — a single wider request silently truncates at cTrader's
  100-bar cap, so these are always fetched separately.
- Pulls UK bank rate / SONIA / 5Y/10Y/20Y gilts / sterling ERI from the **Bank of
  England IADB** (keyless CSV, one request, six series codes).
- Pulls US 10Y and Brent trend context from **FRED**.
- Pulls **GBP futures COT positioning** (CFTC contract code `096742`) as the FTSE
  crowding proxy.
- Pulls the UK/US/EZ **economic calendar** and recent **news headlines** from
  **Finnhub**.
- Calls the **Anthropic API** twice: a risk-tone classifier over recent news
  (feeds the bias engine) and the daily briefing paragraph (runs last, over the
  fully-assembled snapshot) — same two-call, key-`.trim()`, `.catch`-returns-null
  pattern as gold's briefing.
- Computes the mechanical **bias engine** and **ORB context** (both below) and
  writes `public/data/uk100/daily-snapshot.json`.

### Symbols (cTrader, plain CFD — not `_SB` spread-bet variants)

| Symbol | symbolId | Role |
|---|---|---|
| UK100 | 113 | Main instrument |
| GBPUSD | 2 | SMT-divergence proxy (inverted read — see `/uk100-session`) |
| NAS100 | 116 | US linkage |
| BRENT | 249 | Energy-sector driver |
| COPPER | 109 | Miners/China proxy |
| VIX | 152 | Risk-regime damper |
| USDX | 101 | Context only |
| EURGBP | 9 | Context only |

Verified 2026-07-10 (`UK100-BUILD-PLAN.md` §1.1) — CFD and `_SB` prices are
identical to within spread noise; the user trades UK100 as a CFD.

### BoE IADB series codes

| Series | Code |
|---|---|
| Bank Rate | `IUDBEDR` |
| SONIA | `IUDSOIA` |
| Sterling ERI | `XUDLBK67` |
| 5Y gilt | `IUDSNZC` |
| 10Y gilt | `IUDMNZC` |
| 20Y gilt | `IUDLNZC` |

All six are fetched in one request (comma-separated) — a single bad code fails the
whole request, so these must stay exact.

### Mechanical bias engine

`computeBias()` in `fetch-uk100-data.ts` — a pure, unit-testable function. Each
component contributes a score in `[-2, +2]` (or `[-1, +1]` for the two 1.0-weight
drivers), weighted and summed, then divided by 1.35 and clamped to `[-10, +10]`:

| Component | Weight | Rule |
|---|---|---|
| GBP (sign-flipped) | 3.0 | `-gbpUsdDayPct / 0.5 × 2`, clamped ±2. Halved if sterling ERI disagrees in sign with cable. |
| US futures | 2.5 | `us500DayPct / 0.75 × 2`, clamped ±2, +0.5 bonus if NAS100 agrees in sign. |
| VIX regime | 1.5 | CALM → +1, ELEVATED → 0, STRESS → **−1 only** (a damper, never a full −2 direction call). |
| Brent | 1.5 | `brentDayPct / 1.5 × 2`, clamped ±2. |
| Copper (China proxy) | 1.5 | `copperDayPct / 1.5 × 2`, clamped ±2. |
| Gilts / rotation | 1.0 | 10Y ±≤3bp → 0; +4..8bp → +1 (banks rotation). **20Y ≥ +8bp forces −2 and sets `longEndStress`** (fiscal-stress override). |
| GBP COT (contrarian) | 1.0 | CROWDED_LONG → +1, CROWDED_SHORT → −1. |
| Risk tone (Anthropic) | 1.0 | classifier label → ±1. |

Label: score ≥ +3 BULLISH, ≤ −3 BEARISH, else NEUTRAL. Conviction: `|score| ≥ 6`
HIGH, `3–5` MEDIUM, else LOW — capped at MEDIUM whenever `eventSuppressed` is true
(a HIGH-impact event today). Every component writes a `drivers[]` entry with a
human-readable detail string, even when its input is null (e.g. "COT data
unavailable") — the bias score is never silently wrong, it's visibly incomplete.

**Sector panel** (`computeSectorPanel()`): ENERGY = sign(Brent, ±0.5%); MINERS =
sign(Copper, ±0.75%); BANKS = `longEndStress` → BEARISH, else sign(10Y gilt bp,
±4bp); PHARMA is always `IDIOSYNCRATIC` (AstraZeneca is often the single largest
index weight — low macro-sensitivity, high single-stock risk); STAPLES takes the
GBP sign-flip, softened one notch toward NEUTRAL (USD/EUR earners).

### ORB context & playbook

Definitions (Europe/London): cash open **08:00**; ORB = high/low of the three M5
candles **08:00–08:15**; overnight range = **22:00 (prev day) → 08:00**.

- **`orbContext`** (mechanical, in the hourly snapshot, always present): `mode`
  (`PRE_OPEN` <08:00 / `ORB_FORMING` 08:00–08:15 / `POST_ORB` 08:15–16:30 /
  `CLOSED` otherwise), overnight high/low, prior-day high/low/close, gap in points
  and percent, ORB high/low, `orbBrokenDirection`, today's HIGH-impact event
  windows, and 14-day ADR + percent used today.
- **`orbPlaybook`** (skill-generated, per `/uk100-session` record — see below): a
  6-row decision table applied mechanically by the skill, outputting one of
  `LONG_ONLY` / `SHORT_ONLY` / `BOTH_OK` / `STAND_ASIDE`, a day type
  (`EVENT_DRIVEN` / `TREND_EXPECTED` / `RANGE_EXPECTED`), reasoning, key levels,
  invalidation, and event risk. The full decision table is in
  `.claude/commands/uk100-session.md` STEP 8 and `UK100-BUILD-PLAN.md` §6.2 —
  it is not re-derived here to avoid two sources of truth drifting apart.

### `/uk100-session` — the AI skill

`.claude/commands/uk100-session.md` is `/gold-session`'s sibling: same core
ICT/SMC engine (`ICT-SMC-Local-Agent/analysis/`, shared, unmodified), same
HTTP-primary/MCP-fallback cTrader path, same freshness gates (refuses to publish
on stale data — see the gold README's incident notes on this), same conflict-proof
`commit-tree`-based push to `main`. The differences:

- `ctrader_http_fetch.py --instrument uk100` (vs the default `gold`) — fetches
  UK100/GBPUSD plus the dedicated overnight/ORB windows.
- `uk100_sessions.py` (new, not in `analysis/` — UK100-only) computes the London
  session map, ORB/overnight ranges, and ADR14.
- `uk100_adapter.py` (new, copies `skill_adapter.py`'s structure) drops the
  Asian-range block, adds `orb`/`session`/`reference_levels`, and checks SMT
  divergence against GBPUSD with an **inverted** read (UK100/GBP moving in the
  *same* direction is the divergence signal, not opposite directions like gold's
  EURUSD check).
- `save-gold-session.ts --instrument=uk100` routes to
  `public/data/uk100/sessions/`, a `uk100-session-bot` git identity, and a
  `uk100-session` commit prefix. Flag absent → byte-identical gold behaviour.
- The brief adds an `## ORB PLAYBOOK` section (STEP 8 in the skill doc) and an
  `orbPlaybook` object in the meta JSON — see "ORB context & playbook" above.

### UK100 AI Session tab data structure

```
xauusd-dashboard/
├── public/data/uk100/
│   ├── daily-snapshot.json         Hourly macro snapshot (Macro sub-tab)
│   └── sessions/
│       ├── index.json              Rolling 3-day index
│       └── YYYY-MM-DD/
│           └── HH-MM.json          One file per /uk100-session run
└── scripts/fetch-uk100-data.ts     Hourly fetcher (this section)
```

Same shape as the gold `sessions/` structure (see above), plus an optional
`orbPlaybook` field on both the record and — unlike every other structured
field — **with no text-parsing fallback**: `AiSubTab.tsx` renders it via a
dedicated `OrbPlaybookCard` sourced only from the meta JSON, so the skill must
always populate it when the brief's `## ORB PLAYBOOK` section is present.

### Recalibration note (v1 caveat)

The bias engine's weights (§ above) are **v1 priors**, not fitted coefficients —
they encode a reasonable starting judgement about which macro forces matter most
for UK100, not a backtested optimum. Log bias-vs-outcome daily once the skill is
in regular use and recalibrate the weights after ~4 weeks of data. An
`resolve-uk100-sessions.ts` outcome resolver (mirroring gold's
`resolve-gold-sessions.ts`) is a natural next step for this but is intentionally
**not** part of v1.

---

## Pravzella tab

The dashboard's third tab ("Pravzella") is a TradeZella-style trade journal — stats
overview, a clickable day-by-day P&L calendar, and a full trade log — built from real
cTrader trade history synced into a Firebase (Firestore) database on a schedule. It's
login-gated (the tab shows real account P&L on an otherwise-public site). Full
architecture, setup steps, the trade-reconstruction algorithm, and the auth/security
model are documented in **[`PRAVZELLA.md`](./PRAVZELLA.md)** — that file is the source
of truth for this tab and is expected to be kept current by whoever (human or AI)
touches it next.

---

## Environment variables / GitHub Secrets

Most API keys are consumed **only** by `xauusd-daily-fetch.yml`'s "Fetch daily data snapshot" step, which runs server-side in CI, and are never passed to `npm run build` or exposed to the browser bundle. The four `VITE_FIREBASE_*` secrets are the one deliberate exception — see `PRAVZELLA.md`'s "Auth model" for why that's safe.

| Secret | Used for |
|---|---|
| `FRED_API_KEY` | Yields, real yields, breakevens, STLFSI4, NFCI, VIX (VIXCLS series) |
| `ALPHA_VANTAGE_API_KEY` | Reserved (currently unused by the fetch script) |
| `VITE_CTRADER_MCP_URL` / `VITE_CTRADER_MCP_TOKEN` | cTrader MCP — read server-side as `CTRADER_MCP_URL`/`CTRADER_MCP_TOKEN` env vars for the macro snapshot fetch, and as the same names for the Pravzella trade sync (`sync-trades.ts`). (Secret names are legacy `VITE_`-prefixed from before the security fix below; the values are no longer forwarded to the client build.) |
| `FINNHUB_API_KEY` | Economic calendar + news headlines (gold and UK100 both) |
| `ANTHROPIC_API_KEY` | Daily briefing generation (gold and UK100 both — UK100 also uses it for the risk-tone classifier) |
| `FIREBASE_API_KEY` / `FIREBASE_AUTH_DOMAIN` / `FIREBASE_PROJECT_ID` / `FIREBASE_APP_ID` | Pravzella tab — injected into the client build as `VITE_FIREBASE_*` (safe to expose, see `PRAVZELLA.md`). |
| `FIREBASE_SERVICE_ACCOUNT_JSON` / `FIREBASE_USER_ID` | Pravzella trade sync only (`sync-trades.ts`, GitHub Actions) — bypasses Firestore Security Rules, never exposed to the browser. |

**UK100 needed zero new secrets** — `fetch-uk100-data.ts` reuses the same four keys
(`FRED_API_KEY`, `VITE_CTRADER_MCP_URL`/`VITE_CTRADER_MCP_TOKEN`, `FINNHUB_API_KEY`,
`ANTHROPIC_API_KEY`) already present for gold, plus the Bank of England IADB and
CFTC COT endpoints, both keyless.

No `.env` file or `VITE_*` build-time secret is required to run `npm run build` or `npm run dev` locally for the Macro Dashboard, Gold-Session AI, or UK100 tabs — they read everything from the static snapshot JSON at runtime. The Pravzella tab does need the four `VITE_FIREBASE_*` values in `.env.local` to authenticate locally (see `PRAVZELLA.md`); without them it renders a "not configured yet" message instead of breaking the build.

## Security note: client-side secret exposure (fixed)

This dashboard was originally built with the Anthropic, Finnhub, and cTrader API calls made **directly from the browser**, using Vite's `VITE_*`-prefixed env vars injected at CI build time. Vite statically inlines `VITE_*` values into the built JS bundle — they are plain text, visible to anyone via browser DevTools or `view-source`. Because this repository's GitHub Pages site is public, this meant a live, working Anthropic API key and cTrader MCP bearer token were extractable from the deployed bundle by anyone with the URL.

**Fix:** all three API calls were moved server-side into `scripts/fetch-static-data.ts` (which already ran in CI with non-public secrets for FRED data), and their results are written into the public-but-secret-free `daily-snapshot.json`. The `VITE_FINNHUB_KEY`, `VITE_ANTHROPIC_KEY`, `VITE_CTRADER_MCP_URL`, and `VITE_CTRADER_MCP_TOKEN` build-time env injections were removed entirely from both `deploy-dashboard.yml` and `xauusd-daily-fetch.yml`'s dashboard-build steps. `src/services/anthropicBriefing.ts` and `src/hooks/useEconomicCalendar.ts` (the client-side callers) were deleted.

**Trade-off:** live 15-second price polling (`useCTraderPrices.ts`) now always reports `offline` in production, since its token is no longer injected into the build. The dashboard shows prices from the hourly snapshot instead of true live ticks. The hook and its `pricesFromSnapshot()` fallback were left in place — if live polling is wanted again, it needs a small server-side proxy (e.g. a Cloudflare Worker holding the cTrader token and exposing a same-origin endpoint) rather than re-injecting the token into the client bundle.

**If you are reading this after the fact:** the leaked Anthropic key and cTrader MCP token from before this fix must be rotated/revoked in their respective dashboards — this code change does not invalidate keys that were already exposed.

## Known limitations

- Live price polling is currently disabled in production (see Security above) — prices update hourly (06:00–20:00 GMT Mon–Fri) from the snapshot instead of via true live ticks.
- The hourly cadence means ~14 commits/day land on `main` from the data-fetch bot, each touching only `public/data/daily-snapshot.json`.
- `ALPHA_VANTAGE_API_KEY` is configured as a secret but not currently used by `fetch-static-data.ts`.
- Session-label logic in `App.tsx` (`getSessionLabel`) uses fixed UTC-hour buckets and is not DST-aware, unlike the `analysis/sessions.py` convention used by the ICT/SMC agents — fine for a dashboard label, not used for trading decisions.
- Pravzella tab limitations (open positions not tracked yet, no R-multiple metrics, Zella Score is a custom approximation, no journaling yet) are documented separately in `PRAVZELLA.md`'s own "Known limitations" section.
- The UK100 bias engine's weights are v1 priors, not backtested coefficients — see "Recalibration note" in the UK100 tab section above. There is no `resolve-uk100-sessions.ts` outcome tracker yet, so the UK100 AI Session tab has no gold-style Track Record calibration card.
