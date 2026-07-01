# Pravzella — Trade Tracking & Journaling tab

> **For future AI sessions / contributors:** this file is the source of truth for the
> Pravzella tab — what it does, why it's built the way it is, and what's still
> outstanding. When you change anything under `src/components/pravzella/`,
> `scripts/sync-trades.ts`, `db/`, or the trade-sync workflow, **update this file in the
> same change** (especially the "Known limitations" and "Build log" sections at the
> bottom). Don't let this drift out of date — it's the only place the reasoning behind
> non-obvious decisions (auth model, why re-scan instead of a watermark, the Zella score
> approximation) is written down.

## What it is

A third tab on the XAUUSD Intelligence Dashboard, styled and structured like
[TradeZella](https://tradezella.com): a trade journal built from the user's real
cTrader trade history. v1 scope is **read-only tracking** — an Overview stats
dashboard, a clickable day-by-day P&L calendar, and a full trade log. Journaling
(per-trade notes/tags, daily journal, playbooks) is an intentional follow-up once this
foundation is proven — see "Known limitations" below.

The tab is **login-gated** in its entirety (email/password via Supabase Auth) because
the dashboard is public on GitHub Pages and this tab shows real account P&L.

## Architecture

```
xauusd-dashboard/
├── db/pravzella_schema.sql              One-time Supabase SQL migration (paste into SQL Editor)
├── scripts/sync-trades.ts               Server-side sync: cTrader deals -> Supabase trades
├── .github/workflows/xauusd-trade-sync.yml   Cron wrapper for the above
└── src/
    ├── types/trades.ts                  Trade / DailyPnl / TradeMetrics interfaces
    ├── services/
    │   ├── supabaseClient.ts            Browser Supabase client (anon key)
    │   └── tradeMetrics.ts              Pure functions: win%, profit factor, Zella score, series
    ├── hooks/
    │   ├── useAuth.ts                   Supabase Auth session state + sign in/out
    │   └── useTrades.ts                 Fetches the logged-in user's trades
    └── components/pravzella/
        ├── PravzellaTab.tsx             Sub-tab nav (Overview/Calendar/Trade Log), wraps LoginGate
        ├── LoginGate.tsx                Email/password form — no sign-up UI, see "Auth model"
        ├── overview/                    Stat cards, Zella score radar, cumulative + daily P&L charts
        ├── calendar/                    Month grid + day detail breakdown panel
        └── trade-log/                   Sortable/filterable trade table
```

This follows the same pattern as the Macro Dashboard and Gold-Session AI tabs: a
GitHub Actions workflow runs a server-side script that talks to external services
(here, the cTrader MCP server) and writes results somewhere the browser can read —
except here that "somewhere" is Supabase instead of a committed JSON file, because the
user wants durable, queryable history from go-live onward rather than a static
snapshot.

## Data pipeline: how a cTrader fill becomes a "trade"

cTrader's `get_deals` MCP tool returns raw fills — `positionId`, `tradeSide`,
`volume`, `executionPrice`, `executionTimestamp`, `commission` — with **no P&L
field**. `scripts/sync-trades.ts` reconstructs each closed trade:

1. Group fills by `positionId`, sort chronologically.
2. The **direction** is the side of the first fill (`BUY` = LONG, `SELL` = SHORT).
3. Fills on the *opening* side accumulate into a volume-weighted average **entry
   price**; fills on the *opposite* side accumulate into a volume-weighted average
   **exit price**. This correctly handles partial closes and scale-ins/outs sharing one
   `positionId` (e.g. two BUY fills opening a position, one SELL fill closing it — a
   real case in this account's history).
4. Once the running signed size returns to exactly 0, the position is fully closed and
   becomes one trade:
   ```
   stake (£/pt) = entryVolume / 100
   net_pnl = (direction == LONG ? avgExit - avgEntry : avgEntry - avgExit) * stake - commission
   ```
5. Positions that haven't returned to 0 within the fetch window are skipped (still
   open) — picked up automatically once they close in a later sync run.

**Worked example** (verified against this account's real history during the build):
positionId `50932300`, US500, opened SHORT 2000@7522.2, closed BUY 2000@7511.9 →
`stake = 2000/100 = £20/pt`, `net_pnl = (7522.2 - 7511.9) * 20 = +£206.00`. The script's
`--dry-run` output matched this exactly.

**Why re-scan a rolling window instead of tracking a high-water mark:** the original
plan was to fetch deals from `max(exit_time)` in Supabase forward on each run. This is
wrong — a position opened just before a previous sync's cutoff and closed after it
would have its *opening* fill permanently un-fetched on the next run, making it
unreconstructable (you'd see the closing leg with no matching entry). Instead, the
script always re-scans a rolling lookback window (`LOOKBACK_DAYS`, default 35 days —
comfortably longer than any position in this account has stayed open) and upserts
idempotently on `(user_id, position_id)`. This account trades tens of positions a
month, so re-scanning is cheap; correctness matters more than the minor extra API
calls.

## Database schema (Supabase Postgres)

See `db/pravzella_schema.sql` for the full migration. Single table, single user:

- `trades` — one row per closed position, unique on `(user_id, position_id)` so syncs
  are idempotent upserts. Row Level Security restricts all access to
  `auth.uid() = user_id`.
- `journal_entries` (notes/tags per trade, daily journal) is **not created yet** — it's
  designed and added when the journaling UI is built in a follow-up pass, so we don't
  ship unused schema ahead of the feature that needs it.

## Auth model

Supabase Auth, email/password, **no public sign-up UI** — the one user account is
created manually via the Supabase dashboard (Authentication → Add user), not through
the app. `LoginGate.tsx` only renders a sign-in form.

The Supabase **anon key** (`VITE_SUPABASE_ANON_KEY`) is injected into the public build
bundle — this is safe by Supabase's own design and is a **different trust model** to
the bearer tokens described in `README.md`'s "Security note" section (which must never
be client-side). The anon key grants nothing by itself; every request it makes is
still subject to Row Level Security, and RLS requires `auth.uid() = user_id`, which
requires a real login. Someone with just the anon key (trivially extractable from any
Supabase app's bundle, by design) cannot read or write trades without your password.
Do not "fix" this by removing the anon key from the build — that would just break the
tab, not add security.

The **service role key** (`SUPABASE_SERVICE_ROLE_KEY`) is the opposite: it bypasses
RLS entirely and must only ever be used server-side (`scripts/sync-trades.ts`, run in
GitHub Actions). Because the service role connection has no `auth.uid()`, the sync
script sets `user_id` explicitly from the `SUPABASE_USER_ID` secret.

## One-time setup (manual — cannot be automated from here)

1. Create a free Supabase project at [supabase.com](https://supabase.com).
2. Project → SQL Editor → paste and run `db/pravzella_schema.sql`.
3. Project → Authentication → Add user (email + password) — this is the only login
   the tab will ever accept. Copy the generated **User UID**.
4. Project → Settings → API — copy the **Project URL**, **anon public key**, and
   **service_role key**.
5. Add these as GitHub repo secrets (Settings → Secrets and variables → Actions):
   - `SUPABASE_URL`
   - `SUPABASE_ANON_KEY`
   - `SUPABASE_SERVICE_ROLE_KEY`
   - `SUPABASE_USER_ID` (the UID from step 3)
6. Run the **Pravzella Trade Sync** workflow manually once (Actions tab →
   "Pravzella Trade Sync" → Run workflow) to backfill the last 35 days.
7. Push any change under `xauusd-dashboard/src/**` (or manually run **Deploy
   Dashboards to GitHub Pages**) so the new `VITE_SUPABASE_URL`/`VITE_SUPABASE_ANON_KEY`
   are baked into the deployed build.

For local development, copy the same four values (plus the two `VITE_`-prefixed ones)
into `xauusd-dashboard/.env.local` per `.env.example`.

## Metrics (`src/services/tradeMetrics.ts`)

- **Net P&L** — sum of `net_pnl` across all closed trades.
- **Trade Win %** — winning trades / total trades.
- **Profit Factor** — gross winning P&L / |gross losing P&L|.
- **Day Win %** — trading days with positive net P&L / all trading days.
- **Avg Win/Loss** — mean winning trade vs mean losing trade, shown as a ratio bar.
- **Zella Score** (0–100) — our own composite, **not** TradeZella's real formula
  (which is proprietary/undisclosed). Average of five sub-scores, each independently
  scaled to 0–100: win rate, profit factor, avg win/loss ratio, consistency (inverse
  coefficient of variation of daily P&L), and max drawdown (from the cumulative P&L
  curve). Treat this as directionally useful, not as a benchmark against real
  TradeZella numbers.

## Known limitations

- **Open positions aren't shown anywhere in the tab yet.** Only fully-closed
  positions become trades. A currently-open position won't appear in Overview,
  Calendar, or Trade Log until it closes.
- **No R-multiple / stop-loss-based metrics.** cTrader's `get_deals`/`get_order_history`
  don't expose the SL/TP that was attached to a position in a way that survived to the
  closed deal, so risk-adjusted metrics (R-multiple, risk:reward) aren't computed. Would
  need `get_order_history` cross-referenced with the opening order's SL/TP, which
  returned empty for this account in testing — worth revisiting if that changes.
- **Zella Score is an approximation** (see above) — don't quote it as equivalent to
  TradeZella's own score.
- **No journaling yet** — no per-trade notes, tags, playbooks, or a daily journal.
  `journal_entries` schema is intentionally deferred until that UI is built (see
  "Database schema" above).
- **Trade Log has no pagination** — fine at this account's current trade volume;
  revisit if it grows into the thousands.

## Build log / reasoning

- **2026-07-01** — Initial build. Researched TradeZella's feature set from user-provided
  screenshots (Dashboard stat cards + Zella Score radar + cumulative/daily P&L charts;
  clickable day-by-day Calendar; Trade Log). Confirmed against the real cTrader account
  (`get_deals`) that trades must be reconstructed from raw fills — no P&L field exists
  upstream. User chose: scheduled auto-sync (not a manual button, since this is a
  static site), a real database (Supabase) over localStorage/committed-JSON for
  durability, and login-gating the whole tab since GitHub Pages is public. Shipped
  Overview + Calendar + Trade Log; journaling/tags/playbooks deferred to a follow-up
  pass. Built and verified the reconstruction algorithm against real account history
  (`npx tsx scripts/sync-trades.ts --dry-run`) before wiring Supabase, and visually
  verified all three sub-tabs render correctly against that real data before removing
  the test harness. No changes made to the Macro Dashboard or Gold-Session AI tabs.
