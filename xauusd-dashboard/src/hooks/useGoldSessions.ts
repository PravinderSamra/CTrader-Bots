import { useState, useEffect, useMemo } from 'react'
import type { GoldSessionRecord, GoldSessionIndex, OutcomesIndex, OutcomeRow } from '../types/dashboard'

const BASE = import.meta.env.BASE_URL

export function useGoldSessionIndex(): { index: GoldSessionIndex | null; loading: boolean } {
  const [index, setIndex] = useState<GoldSessionIndex | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/sessions/index.json`)
      .then(r => r.ok ? r.json() : { updatedAt: '', sessions: [] })
      .then((data: GoldSessionIndex) => { setIndex(data); setLoading(false) })
      .catch(() => { setIndex({ updatedAt: '', sessions: [] }); setLoading(false) })
  }, [])

  return { index, loading }
}

export function useSessionOutcomes(): {
  outcomes: OutcomeRow[]
  byFilename: Map<string, OutcomeRow>
  loading: boolean
} {
  const [outcomes, setOutcomes] = useState<OutcomeRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/sessions/outcomes.json`)
      .then(r => r.ok ? r.json() : { updatedAt: '', outcomes: [] })
      .then((data: OutcomesIndex) => { setOutcomes(data.outcomes ?? []); setLoading(false) })
      .catch(() => { setOutcomes([]); setLoading(false) })
  }, [])

  const byFilename = useMemo(
    () => new Map(outcomes.map(o => [o.filename, o])),
    [outcomes],
  )

  return { outcomes, byFilename, loading }
}

export function useGoldSession(filename: string | null): { session: GoldSessionRecord | null; loading: boolean } {
  const [session, setSession] = useState<GoldSessionRecord | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!filename) { setSession(null); return }
    setLoading(true)
    setSession(null)
    fetch(`${BASE}data/sessions/${filename}`)
      .then(r => r.ok ? r.json() : null)
      .then((data: GoldSessionRecord | null) => { setSession(data); setLoading(false) })
      .catch(() => { setSession(null); setLoading(false) })
  }, [filename])

  return { session, loading }
}
