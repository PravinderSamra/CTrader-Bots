import { useState, useEffect } from 'react'
import type { Uk100Snapshot } from '../types/uk100'

const SNAPSHOT_URL = import.meta.env.BASE_URL + 'data/uk100/daily-snapshot.json'

export function useUk100Snapshot(): Uk100Snapshot | null {
  const [snapshot, setSnapshot] = useState<Uk100Snapshot | null>(null)

  useEffect(() => {
    fetch(SNAPSHOT_URL)
      .then(r => r.ok ? r.json() : null)
      .then((data: Uk100Snapshot | null) => { if (data) setSnapshot(data) })
      .catch(() => {/* snapshot not yet generated */})
  }, [])

  return snapshot
}
