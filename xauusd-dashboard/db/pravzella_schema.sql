-- Pravzella trade journal — Supabase schema (v1)
--
-- One-time setup: paste this whole file into the Supabase SQL Editor (your project ->
-- SQL Editor -> New query) and run it. See PRAVZELLA.md for the full setup checklist.
--
-- Single-user design: every row belongs to one auth.users row (the account owner).
-- Row Level Security restricts all access to auth.uid() = user_id, so even though the
-- anon key ships in the public client bundle, nobody can read or write rows without
-- being logged in as that one user (see PRAVZELLA.md "Auth model").

create table if not exists public.trades (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null default auth.uid() references auth.users(id),
  position_id   bigint not null,
  symbol        text not null,
  direction     text not null check (direction in ('LONG', 'SHORT')),
  volume        numeric not null,             -- GBP stake per point (ctrader volume / 100)
  entry_price   numeric not null,
  exit_price    numeric not null,
  entry_time    timestamptz not null,
  exit_time     timestamptz not null,
  gross_pnl     numeric not null,
  commission    numeric not null default 0,
  net_pnl       numeric not null,
  source        text not null default 'ctrader_sync',
  created_at    timestamptz not null default now(),
  updated_at    timestamptz not null default now(),
  unique (user_id, position_id)
);

create index if not exists trades_user_exit_time_idx on public.trades (user_id, exit_time);

alter table public.trades enable row level security;

drop policy if exists "select own trades" on public.trades;
create policy "select own trades" on public.trades
  for select using (auth.uid() = user_id);

drop policy if exists "insert own trades" on public.trades;
create policy "insert own trades" on public.trades
  for insert with check (auth.uid() = user_id);

drop policy if exists "update own trades" on public.trades;
create policy "update own trades" on public.trades
  for update using (auth.uid() = user_id);

-- The sync script (scripts/sync-trades.ts) writes with the service_role key, which
-- bypasses RLS entirely, so it explicitly sets user_id = SUPABASE_USER_ID on every
-- upsert rather than relying on auth.uid() (which has no meaning for a service-role
-- connection). See PRAVZELLA.md for how SUPABASE_USER_ID is obtained.
