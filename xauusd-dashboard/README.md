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

## Environment variables / GitHub Secrets

All API keys are consumed **only** by `xauusd-daily-fetch.yml`'s "Fetch daily data snapshot" step, which runs server-side in CI. None of these are ever passed to `npm run build` and none reach the browser bundle.

| Secret | Used for |
|---|---|
| `FRED_API_KEY` | Yields, real yields, breakevens, STLFSI4, NFCI, VIX (VIXCLS series) |
| `ALPHA_VANTAGE_API_KEY` | Reserved (currently unused by the fetch script) |
| `VITE_CTRADER_MCP_URL` / `VITE_CTRADER_MCP_TOKEN` | cTrader MCP — read server-side as `CTRADER_MCP_URL`/`CTRADER_MCP_TOKEN` env vars. (Secret names are legacy `VITE_`-prefixed from before the security fix below; the values are no longer forwarded to the client build.) |
| `FINNHUB_API_KEY` | Economic calendar + news headlines |
| `ANTHROPIC_API_KEY` | Daily briefing generation |

No `.env` file or `VITE_*` build-time secret is required to run `npm run build` or `npm run dev` locally — the dashboard reads everything from the static snapshot JSON at runtime. Local development without secrets simply shows whatever `daily-snapshot.json` is currently committed.

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
