import { useState, useEffect, useMemo } from 'react'
import type { Uk100SessionRecord, Uk100SessionIndex } from '../types/uk100'
import type { OutcomesIndex, OutcomeRow } from '../types/dashboard'

const BASE = import.meta.env.BASE_URL

export function useUk100SessionIndex(): { index: Uk100SessionIndex | null; loading: boolean } {
  const [index, setIndex] = useState<Uk100SessionIndex | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/uk100/sessions/index.json`)
      .then(r => r.ok ? r.json() : { updatedAt: '', sessions: [] })
      .then((data: Uk100SessionIndex) => { setIndex(data); setLoading(false) })
      .catch(() => { setIndex({ updatedAt: '', sessions: [] }); setLoading(false) })
  }, [])

  return { index, loading }
}

// C3 (UK100-V2-PLAN.md §5 Phase C3): mirrors gold's useSessionOutcomes exactly,
// reusing the shared OutcomesIndex/OutcomeRow types (not duplicated).
export function useUk100SessionOutcomes(): {
  outcomes: OutcomeRow[]
  byFilename: Map<string, OutcomeRow>
  loading: boolean
} {
  const [outcomes, setOutcomes] = useState<OutcomeRow[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetch(`${BASE}data/uk100/sessions/outcomes.json`)
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

export function useUk100Session(filename: string | null): { session: Uk100SessionRecord | null; loading: boolean } {
  const [session, setSession] = useState<Uk100SessionRecord | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!filename) { setSession(null); return }
    setLoading(true)
    setSession(null)
    fetch(`${BASE}data/uk100/sessions/${filename}`)
      .then(r => r.ok ? r.json() : null)
      .then((data: Uk100SessionRecord | null) => { setSession(data); setLoading(false) })
      .catch(() => { setSession(null); setLoading(false) })
  }, [filename])

  return { session, loading }
}
