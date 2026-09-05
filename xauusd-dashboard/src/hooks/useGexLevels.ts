import { useState, useEffect } from 'react'
import type { User } from 'firebase/auth'
import { collection, onSnapshot } from 'firebase/firestore'
import { db } from '../services/firebaseClient'
import type { GexSnapshot } from '../types/gex'

/**
 * Live subscription to the GexBot levels the recorder keeps current.
 *
 * gex_latest holds one document per ticker+scope, overwritten on every poll,
 * so this is a small collection that onSnapshot can watch cheaply. The
 * append-only history lives in gex_snapshots and is not read here.
 *
 * Firestore rules require sign-in for both collections (paid vendor data on a
 * public site), so this returns nothing until there is a user.
 */
export function useGexLevels(user: User | null): {
  snapshots: GexSnapshot[]
  loading: boolean
  error: string | null
} {
  const [snapshots, setSnapshots] = useState<GexSnapshot[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) { setSnapshots([]); setLoading(false); return }

    setLoading(true)
    // No orderBy: the collection is a handful of docs and sorting by ticker
    // client-side avoids needing a composite index for a trivial result set.
    const unsubscribe = onSnapshot(
      collection(db, 'gex_latest'),
      snapshot => {
        setError(null)
        setSnapshots(
          snapshot.docs
            .map(d => d.data() as GexSnapshot)
            .sort((a, b) => a.ticker.localeCompare(b.ticker)),
        )
        setLoading(false)
      },
      err => {
        setError(err.message)
        setSnapshots([])
        setLoading(false)
      },
    )

    return unsubscribe
  }, [user])

  return { snapshots, loading, error }
}

/**
 * How stale a snapshot is, and whether that is expected.
 *
 * The feed genuinely freezes outside US cash hours — it repeats its last
 * timestamp rather than going away — so age alone is not a fault. Saying
 * which of the two it is matters: these levels get traded off, and a frozen
 * Friday-close reading shown as if it were live would be actively misleading.
 */
export function describeFreshness(sourceTs: number, now: Date = new Date()): {
  ageSeconds: number
  label: string
  stale: boolean
} {
  const ageSeconds = Math.max(0, Math.floor(now.getTime() / 1000 - sourceTs))

  const mins = Math.floor(ageSeconds / 60)
  const label =
    mins < 1 ? 'just now'
      : mins < 60 ? `${mins}m ago`
        : mins < 60 * 24 ? `${Math.floor(mins / 60)}h ${mins % 60}m ago`
          : `${Math.floor(mins / (60 * 24))}d ago`

  // The recorder polls every 5 minutes, so anything past ~15 minutes means
  // either the market is shut or the workflow has stopped running.
  return { ageSeconds, label, stale: ageSeconds > 15 * 60 }
}

/** Is the US cash session open right now? Used to explain staleness. */
export function isUsCashOpen(now: Date = new Date()): boolean {
  const day = now.getUTCDay()
  if (day === 0 || day === 6) return false
  // 13:30-20:00 UTC on EDT, 14:30-21:00 on EST. The wider window avoids
  // asserting a precision we do not have about which side of DST we are on.
  const minutes = now.getUTCHours() * 60 + now.getUTCMinutes()
  return minutes >= 13 * 60 + 30 && minutes <= 21 * 60
}
