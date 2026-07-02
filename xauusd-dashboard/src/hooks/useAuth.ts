import { useState, useEffect, useCallback } from 'react'
import { onAuthStateChanged, signInWithEmailAndPassword, signOut as firebaseSignOut, type User } from 'firebase/auth'
import { auth, firebaseConfigured } from '../services/firebaseClient'

interface AuthState {
  user: User | null
  loading: boolean
  configured: boolean
  signIn: (email: string, password: string) => Promise<string | null>
  signOut: () => Promise<void>
}

function friendlyAuthError(code: string): string {
  if (code.includes('invalid-credential') || code.includes('wrong-password') || code.includes('user-not-found')) {
    return 'Incorrect email or password'
  }
  if (code.includes('too-many-requests')) return 'Too many attempts — try again shortly'
  return 'Sign-in failed — check your connection and try again'
}

export function useAuth(): AuthState {
  const [user, setUser] = useState<User | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!firebaseConfigured) { setLoading(false); return }

    const unsubscribe = onAuthStateChanged(auth, u => {
      setUser(u)
      setLoading(false)
    })
    return unsubscribe
  }, [])

  const signIn = useCallback(async (email: string, password: string): Promise<string | null> => {
    try {
      await signInWithEmailAndPassword(auth, email, password)
      return null
    } catch (err) {
      const code = (err as { code?: string }).code ?? ''
      return friendlyAuthError(code)
    }
  }, [])

  const signOut = useCallback(async () => {
    await firebaseSignOut(auth)
  }, [])

  return { user, loading, configured: firebaseConfigured, signIn, signOut }
}
