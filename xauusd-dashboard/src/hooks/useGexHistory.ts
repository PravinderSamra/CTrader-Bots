import { useState, useEffect } from 'react'
import type { User } from 'firebase/auth'
import {
  collection, documentId, onSnapshot, orderBy, query, where,
} from 'firebase/firestore'
import { db } from '../services/firebaseClient'
import type { GexSnapshot } from '../types/gex'

/**
 * The session's recorded snapshots, for plotting price against the levels.
 *
 * Why a document-id range rather than a field query: the recorder keys each
 * document `{TICKER}_{scope}_{source_ts}`, so a prefix range on the id selects
 * one ticker and scope without a composite index — which would otherwise need
 * creating in the Firebase console before this hook returned anything. Unix
 * seconds stay ten digits until 2286, so lexicographic order over the id is
 * also chronological order, and `orderBy(documentId())` needs no index either.
 *
 * The series is coarse by construction: the recorder polls every five minutes,
 * so a full session is ~78 points against the vendor's near-continuous line.
 * Enough to see price approach a level and react; not tick-accurate, and it
 * should not be read as if it were.
 */
export function useGexHistory(user: User | null, ticker: string, scope: string): {
  history: GexSnapshot[]
  loading: boolean
  error: string | null
} {
  const [history, setHistory] = useState<GexSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) { setHistory([]); setLoading(false); return }
    setLoading(true)

    const prefix = `${ticker}_${scope}_`
    // '{' sorts above every digit and underscore, closing the prefix range.
    const q = query(
      collection(db, 'gex_snapshots'),
      where(documentId(), '>=', prefix),
      where(documentId(), '<', `${prefix}{`),
      orderBy(documentId()),
    )

    const unsubscribe = onSnapshot(
      q,
      snap => {
        setError(null)
        const rows = snap.docs.map(d => d.data() as GexSnapshot)
        // Keep only the most recent session: the feed freezes out of hours and
        // repeats a timestamp, so splitting on a gap is more reliable than a
        // calendar day, which would cut a session at midnight UTC mid-flow.
        let start = 0
        for (let i = rows.length - 1; i > 0; i--) {
          if (rows[i].source_ts - rows[i - 1].source_ts > 4 * 3600) { start = i; break }
        }
        setHistory(rows.slice(start))
        setLoading(false)
      },
      err => { setError(err.message); setHistory([]); setLoading(false) },
    )
    return unsubscribe
  }, [user, ticker, scope])

  return { history, loading, error }
}
