import { useState, useEffect } from 'react'

const HISTORY_URL = import.meta.env.BASE_URL + 'data/history.json'

export interface HistoryPoint {
  ts: string
  xau: number | null
  dxy: number | null
  us10y: number | null
  vix: number | null
  gvz: number | null
  realYield10Y: number | null
}

interface HistoryFile {
  updatedAt: string
  points: HistoryPoint[]
}

export type HistorySeries = keyof Omit<HistoryPoint, 'ts'>

// Shared across all tiles — one fetch, not one per sparkline.
let cache: Promise<HistoryPoint[]> | null = null
function loadHistory(): Promise<HistoryPoint[]> {
  if (!cache) {
    cache = fetch(HISTORY_URL)
      .then(r => r.ok ? r.json() : { points: [] })
      .then((data: HistoryFile) => data.points ?? [])
      .catch(() => [])
  }
  return cache
}

/**
 * Rolling 7-day intraday history for tile sparklines. Returns the raw points;
 * call `series(key)` to extract one metric's chronological values.
 */
export function useHistory(): { points: HistoryPoint[]; series: (key: HistorySeries) => (number | null)[] } {
  const [points, setPoints] = useState<HistoryPoint[]>([])

  useEffect(() => {
    let alive = true
    loadHistory().then(pts => { if (alive) setPoints(pts) })
    return () => { alive = false }
  }, [])

  return { points, series: (key: HistorySeries) => points.map(p => p[key]) }
}
