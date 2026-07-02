# Pravzella — Trade Tracking & Journaling tab

> **For future AI sessions / contributors:** this file is the source of truth for the
> Pravzella tab — what it does, why it's built the way it is, and what's still
> outstanding. When you change anything under `src/components/pravzella/`,
> `scripts/sync-trades.ts`, `db/`, or the trade-sync workflow, **update this file in the
> same change** (especially the "Known limitations" and "Build log" sections at the
> bottom). Don't let this drift out of date — it's the only place the reasoning behind
> non-obvious decisions (auth model, why re-scan instead of a watermark, the Zella score
> approximation, why Firebase instead of Supabase) is written down.

## What it is

A third tab on the XAUUSD Intelligence Dashboard, styled and structured like
[TradeZella](https://tradezella.com): a trade journal built from the user's real
cTrader trade history. v1 scope is **read-only tracking** — an Overview stats
dashboard, a clickable day-by-day P&L calendar, and a full trade log. Journaling
(per-trade notes/tags, daily journal, playbooks) is an intentional follow-up once this
foundation is proven — see "Known limitations" below.

The tab is **login-gated** in its entirety (email/password via Firebase Auth) because
the dashboard is public on GitHub Pages and this tab shows real account P&L.

## Architecture

```
xauusd-dashboard/
├── db/firestore.rules                   One-time Firestore Security Rules (paste into Firebase Console)
├── scripts/sync-trades.ts               Server-side sync: cTrader deals -> Firestore trades
├── .github/workflows/xauusd-trade-sync.yml   Cron wrapper for the above
└── src/
    ├── types/trades.ts                  Trade / DailyPnl / TradeMetrics interfaces
    ├── services/
    │   ├── firebaseClient.ts            Browser Firebase client (Auth + Firestore)
    │   └── tradeMetrics.ts              Pure functions: win%, profit factor, Zella score, series
    ├── hooks/
    │   ├── useAuth.ts                   Firebase Auth session state + sign in/out
    │   └── useTrades.ts                 Live-subscribes to the logged-in user's trades
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
except here that "somewhere" is a Firestore database instead of a committed JSON file,
because the user wants durable, queryable history from go-live onward rather than a
static snapshot.

**Why Firebase and not Supabase:** Supabase was the original choice (bundled
Postgres + Auth + REST, free tier) and the tab was fully built against it first. The
user's Supabase sign-up got stuck behind an "email your administrator" prompt (Supabase
detected their email/GitHub account as belonging to an existing org and wanted an
invite rather than letting them create a fresh personal project) with no quick
workaround available at the time, so the whole backend was ported to Firebase
(Firestore + Firebase Auth) instead — same bundled DB+Auth+free-tier shape, but
sign-up is just a Google account with no org/admin gate. The UI, metrics, and chart
layer never touched Supabase-specific types directly (`Trade`, `TradeMetrics`, etc. are
plain data shapes), so only the plumbing layer (`firebaseClient.ts`, `useAuth.ts`,
`useTrades.ts`, `sync-trades.ts`'s write step, the schema/rules file) needed to change.

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
`--dry-run` output matched this exactly, and this worked example was re-verified after
the Firebase port (the reconstruction logic is storage-agnostic — only the final write
step changed).

**Why re-scan a rolling window instead of tracking a high-water mark:** the original
plan was to fetch deals from the latest stored `exit_time` forward on each run. This is
wrong — a position opened just before a previous sync's cutoff and closed after it
would have its *opening* fill permanently un-fetched on the next run, making it
unreconstructable (you'd see the closing leg with no matching entry). Instead, the
script always re-scans a rolling lookback window (`LOOKBACK_DAYS`, default 35 days —
comfortably longer than any position in this account has stayed open) and upserts
idempotently (Firestore doc id = `position_id`). This account trades tens of positions
a month, so re-scanning is cheap; correctness matters more than the minor extra API
calls.

## Database structure (Firestore)

No formal schema file (Firestore is schemaless) — structure by convention:

```
users/{uid}/trades/{positionId}
```

- One subcollection per user, one document per closed position, **doc id = the
  cTrader `positionId` as a string** — this is what makes `sync-trades.ts`'s writes
  idempotent (`.doc(String(position_id)).set(..., { merge: true })` instead of needing
  a separate `on_conflict` upsert clause like Supabase required).
- Fields per document: `symbol`, `direction`, `volume`, `entry_price`, `exit_price`,
  `entry_time`, `exit_time` (ISO strings, not Firestore Timestamps — keeps the client
  code identical to a plain `string` field, no conversion layer needed), `gross_pnl`,
  `commission`, `net_pnl`, `source`, `created_at`, `updated_at`.
- Access control: `db/firestore.rules` restricts all reads/writes on
  `users/{uid}/trades/**` to `request.auth.uid == uid` — see "Auth model" below.
- `journal_entries` (notes/tags per trade, daily journal) is **not created yet** — it's
  designed and added when the journaling UI is built in a follow-up pass, so we don't
  ship unused structure ahead of the feature that needs it. It would likely live at
  `users/{uid}/journalEntries/{id}` following the same per-user-subcollection pattern.

## Auth model

Firebase Auth, email/password, **no public sign-up UI** — the one user account is
created manually via the Firebase Console (Authentication → Add user), not through the
app. `LoginGate.tsx` only renders a sign-in form.

The Firebase **client config** (`VITE_FIREBASE_API_KEY`/`AUTH_DOMAIN`/`PROJECT_ID`/`APP_ID`)
is injected into the public build bundle — this is safe by Firebase's own design and is
a **different trust model** to the bearer tokens described in `README.md`'s "Security
note" section (which must never be client-side). This config only identifies *which*
Firebase project the app talks to; it grants nothing on its own. Every Firestore
request is still subject to Security Rules, which require `request.auth.uid == uid`,
which requires a real login. Someone with just the client config (trivially extractable
from any Firebase app's bundle, by design — Google documents this explicitly) cannot
read or write trades without your password. Do not "fix" this by removing the config
from the build — that would just break the tab, not add security.

The **service account key** (`FIREBASE_SERVICE_ACCOUNT_JSON`) is the opposite: the
Firebase Admin SDK authenticated with it bypasses Security Rules entirely and must only
ever be used server-side (`scripts/sync-trades.ts`, run in GitHub Actions). Because an
Admin SDK connection has no `request.auth.uid`, the sync script writes to the path
`users/{FIREBASE_USER_ID}/trades/...` explicitly, using the `FIREBASE_USER_ID` secret.

## One-time setup (manual — cannot be automated from here)

1. Create a free Firebase project at [console.firebase.google.com](https://console.firebase.google.com) (just needs a Google account — no org/admin approval for a personal project).
2. In the project: **Build → Authentication** → get started → enable the **Email/Password**
   sign-in provider.
3. Still in Authentication → **Users** tab → **Add user** — enter the email/password
   this tab will log in with (this is the only login it will ever accept). Copy the
   generated **User UID** from the users list.
4. **Build → Firestore Database** → Create database → start in production mode (any
   region). Once created, go to the **Rules** tab, paste the contents of
   `db/firestore.rules`, and click **Publish**.
5. **Project settings** (gear icon) → **General** tab → scroll to "Your apps" → click
   the **`</>`** (web) icon to register a web app (any nickname, Firebase Hosting not
   needed). It will show a `firebaseConfig` object — copy out `apiKey`, `authDomain`,
   `projectId`, `appId`.
6. **Project settings** → **Service accounts** tab → **Generate new private key** →
   confirm → a JSON file downloads. Open it in a text editor and copy its *entire
   contents* (you'll paste the whole JSON blob as one secret value).
7. Add these as GitHub repo secrets (repo → Settings → Secrets and variables →
   Actions → New repository secret):
   - `FIREBASE_API_KEY`
   - `FIREBASE_AUTH_DOMAIN`
   - `FIREBASE_PROJECT_ID`
   - `FIREBASE_APP_ID`
   - `FIREBASE_SERVICE_ACCOUNT_JSON` (the whole downloaded JSON file's contents)
   - `FIREBASE_USER_ID` (the UID from step 3)
8. Run the **Pravzella Trade Sync** workflow manually once (Actions tab →
   "Pravzella Trade Sync" → Run workflow) to backfill the last 35 days.
9. Run **Deploy Dashboards to GitHub Pages** manually once (or push any change under
   `xauusd-dashboard/src/**`) so the new `VITE_FIREBASE_*` values are baked into the
   deployed build.

For local development, copy the same four `VITE_FIREBASE_*` values into
`xauusd-dashboard/.env.local` per `.env.example` (the two server-only values aren't
needed locally unless you're testing `sync-trades.ts` against real Firestore).

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
- **No journaling yet** — no per-trade notes, tags, playbooks, or a daily journal. The
  Firestore structure for it is intentionally deferred until that UI is built (see
  "Database structure" above).
- **Trade Log has no pagination** — fine at this account's current trade volume;
  revisit if it grows into the thousands.
- **Firestore free tier limits**: 50K reads / 20K writes / 1GiB storage per day on the
  Spark (free) plan. `useTrades.ts` uses a live `onSnapshot` subscription rather than a
  one-shot fetch, which counts as a read per changed document, not per page view — at
  this account's trade volume this is nowhere close to the daily limit, but worth
  knowing if usage patterns change materially.

## Build log / reasoning

- **2026-07-01** — Initial build. Researched TradeZella's feature set from user-provided
  screenshots (Dashboard stat cards + Zella Score radar + cumulative/daily P&L charts;
  clickable day-by-day Calendar; Trade Log). Confirmed against the real cTrader account
  (`get_deals`) that trades must be reconstructed from raw fills — no P&L field exists
  upstream. User chose: scheduled auto-sync (not a manual button, since this is a
  static site), a real database over localStorage/committed-JSON for durability, and
  login-gating the whole tab since GitHub Pages is public. Shipped Overview + Calendar
  + Trade Log against Supabase; journaling/tags/playbooks deferred to a follow-up pass.
  Built and verified the reconstruction algorithm against real account history
  (`npx tsx scripts/sync-trades.ts --dry-run`) before wiring the database, and visually
  verified all three sub-tabs render correctly against that real data before removing
  the test harness. No changes made to the Macro Dashboard or Gold-Session AI tabs.
- **2026-07-02** — Ported the entire backend from Supabase to Firebase (Firestore +
  Firebase Auth) after the user's Supabase sign-up got stuck behind an org-admin
  approval gate — see "Why Firebase and not Supabase" above. Replaced
  `supabaseClient.ts` → `firebaseClient.ts`, rewrote `useAuth.ts`/`useTrades.ts` against
  the Firebase SDKs (`useTrades` now uses a live `onSnapshot` subscription instead of a
  one-shot fetch — a small UX upgrade that fell out naturally from the port), replaced
  `db/pravzella_schema.sql` (Postgres/RLS) with `db/firestore.rules`, and rewrote
  `sync-trades.ts`'s write step to use the Firebase Admin SDK with batched writes
  instead of a Supabase REST upsert. The trade-reconstruction algorithm itself
  (fill-matching, P&L math) is unchanged and was re-verified against the same real
  account data via `--dry-run`. Updated all three GitHub Actions workflows' secret
  names accordingly (`SUPABASE_*` → `FIREBASE_*`).
