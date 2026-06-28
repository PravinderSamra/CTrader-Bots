import { useState, useEffect } from 'react'
import type { DailySnapshot } from '../types/dashboard'

const SNAPSHOT_URL = import.meta.env.BASE_URL + 'data/daily-snapshot.json'

export function useDailySnapshot(): DailySnapshot | null {
  const [snapshot, setSnapshot] = useState<DailySnapshot | null>(null)

  useEffect(() => {
    fetch(SNAPSHOT_URL)
      .then(r => r.ok ? r.json() : null)
      .then((data: DailySnapshot | null) => { if (data) setSnapshot(data) })
      .catch(() => {/* snapshot not yet generated */})
  }, [])

  return snapshot
}
