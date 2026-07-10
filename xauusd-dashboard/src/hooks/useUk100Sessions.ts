import { useState, useEffect } from 'react'
import type { Uk100SessionRecord, Uk100SessionIndex } from '../types/uk100'

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
