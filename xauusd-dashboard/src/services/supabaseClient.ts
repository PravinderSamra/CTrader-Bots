import { createClient } from '@supabase/supabase-js'

// VITE_SUPABASE_URL/ANON_KEY are safe to ship in the client bundle by Supabase's own
// design — the anon key grants nothing on its own, protection comes entirely from
// Row Level Security policies (see db/pravzella_schema.sql) plus requiring a real
// login (see LoginGate.tsx, no public sign-up). This is a different trust model to
// the bearer tokens described in README.md's "Security note" section, which must
// never be injected client-side.
const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL ?? ''
const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY ?? ''

export const supabaseConfigured = Boolean(SUPABASE_URL && SUPABASE_ANON_KEY)

export const supabase = createClient(
  SUPABASE_URL || 'https://placeholder.supabase.co',
  SUPABASE_ANON_KEY || 'placeholder-anon-key',
)
