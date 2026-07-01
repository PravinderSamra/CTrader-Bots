import { useState, useEffect } from 'react'
import type { Session } from '@supabase/supabase-js'
import { supabase } from '../services/supabaseClient'
import type { Trade } from '../types/trades'

export function useTrades(session: Session | null): { trades: Trade[]; loading: boolean; error: string | null } {
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!session) { setTrades([]); setLoading(false); return }

    let cancelled = false
    setLoading(true)

    supabase
      .from('trades')
      .select('*')
      .order('exit_time', { ascending: true })
      .then(({ data, error: err }) => {
        if (cancelled) return
        if (err) { setError(err.message); setTrades([]) }
        else { setError(null); setTrades((data ?? []) as Trade[]) }
        setLoading(false)
      })

    return () => { cancelled = true }
  }, [session])

  return { trades, loading, error }
}
