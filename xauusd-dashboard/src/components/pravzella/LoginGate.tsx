import { useState, type FormEvent, type ReactNode } from 'react'
import { useAuth } from '../../hooks/useAuth'
import styles from './LoginGate.module.css'

interface Props {
  children: ReactNode
}

export function LoginGate({ children }: Props) {
  const { user, loading, configured, signIn } = useAuth()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)

  if (loading) {
    return <div className={styles.status}>Loading…</div>
  }

  if (!configured) {
    return (
      <div className={styles.status}>
        <div className={styles.statusTitle}>Pravzella isn&rsquo;t configured yet</div>
        <div className={styles.statusSub}>
          VITE_FIREBASE_API_KEY / VITE_FIREBASE_AUTH_DOMAIN / VITE_FIREBASE_PROJECT_ID / VITE_FIREBASE_APP_ID
          aren&rsquo;t all set for this build. See <code>PRAVZELLA.md</code> for setup steps.
        </div>
      </div>
    )
  }

  if (user) {
    return <>{children}</>
  }

  async function handleSubmit(e: FormEvent) {
    e.preventDefault()
    setSubmitting(true)
    setError(null)
    const err = await signIn(email, password)
    setSubmitting(false)
    if (err) setError(err)
  }

  return (
    <div className={styles.wrap}>
      <form className={styles.card} onSubmit={handleSubmit}>
        <div className={styles.title}>Pravzella</div>
        <div className={styles.sub}>Sign in to view your trade journal</div>
        <input
          className={styles.input}
          type="email"
          placeholder="Email"
          value={email}
          onChange={e => setEmail(e.target.value)}
          autoComplete="username"
          required
        />
        <input
          className={styles.input}
          type="password"
          placeholder="Password"
          value={password}
          onChange={e => setPassword(e.target.value)}
          autoComplete="current-password"
          required
        />
        {error && <div className={styles.error}>{error}</div>}
        <button className={styles.button} type="submit" disabled={submitting}>
          {submitting ? 'Signing in…' : 'Sign in'}
        </button>
      </form>
    </div>
  )
}
