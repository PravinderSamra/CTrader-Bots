import { useEffect, useState } from 'react'
import { Uk100Snapshot } from '../types/uk100'

export function useUk100Snapshot() {
  const [snapshot, setSnapshot] = useState<Uk100Snapshot | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchSnapshot = async () => {
      try {
        setLoading(true)
        setError(null)
        const res = await fetch('/data/uk100/daily-snapshot.json')
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}`)
        }
        const data = (await res.json()) as Uk100Snapshot
        setSnapshot(data)
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Unknown error')
        setSnapshot(null)
      } finally {
        setLoading(false)
      }
    }

    fetchSnapshot()
    const interval = setInterval(fetchSnapshot, 60000) // Refresh every minute
    return () => clearInterval(interval)
  }, [])

  return { snapshot, loading, error }
}
