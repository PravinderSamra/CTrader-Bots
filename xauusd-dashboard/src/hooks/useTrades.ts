import { useState, useEffect } from 'react'
import type { User } from 'firebase/auth'
import { collection, query, orderBy, onSnapshot } from 'firebase/firestore'
import { db } from '../services/firebaseClient'
import type { Trade } from '../types/trades'

export function useTrades(user: User | null): { trades: Trade[]; loading: boolean; error: string | null } {
  const [trades, setTrades] = useState<Trade[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!user) { setTrades([]); setLoading(false); return }

    setLoading(true)
    const tradesQuery = query(collection(db, 'users', user.uid, 'trades'), orderBy('exit_time', 'asc'))

    const unsubscribe = onSnapshot(
      tradesQuery,
      snapshot => {
        setError(null)
        setTrades(snapshot.docs.map(d => ({ id: d.id, ...d.data() } as Trade)))
        setLoading(false)
      },
      err => {
        setError(err.message)
        setTrades([])
        setLoading(false)
      },
    )

    return unsubscribe
  }, [user])

  return { trades, loading, error }
}
