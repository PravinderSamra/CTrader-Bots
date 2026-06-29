import { useState, useEffect } from 'react'
import type { CTraderPrices, SessionInfo } from '../../types/dashboard'
import styles from './Header.module.css'

// ── Session detection ─────────────────────────────────────────────────────

const SESSIONS = [
  { name: 'ASIAN',     start:  0, end:  8,   label: 'Asian',    next: 'London',   nextH: 8 },
  { name: 'LONDON',    start:  8, end: 13,   label: 'London',   next: 'Overlap',  nextH: 13 },
  { name: 'OVERLAP',   start: 13, end: 16,   label: 'Overlap',  next: 'New York', nextH: 16 },
  { name: 'NEW_YORK',  start: 16, end: 21,   label: 'New York', next: 'Close',    nextH: 21 },
] as const

function getSession(utcHour: number, utcMin: number): SessionInfo {
  const dec = utcHour + utcMin / 60
  for (const s of SESSIONS) {
    if (dec >= s.start && dec < s.end) {
      const nextH = s.nextH
      const minsToNext = Math.round((nextH - dec) * 60)
      const h = Math.floor(minsToNext / 60)
      const m = minsToNext % 60
      return {
        current: s.name,
        label: s.label,
        nextSessionName: s.next,
        nextSessionTime: `${String(nextH).padStart(2,'0')}:00 GMT`,
        minutesToNext: minsToNext,
        isPrime: s.name === 'OVERLAP',
        ...(h > 0 ? { nextLabel: `${h}h ${m}m` } : { nextLabel: `${m}m` }),
      } as SessionInfo & { nextLabel: string }
    }
  }
  const minsToAsia = Math.round((24 - dec) * 60)
  const h = Math.floor(minsToAsia / 60)
  const m = minsToAsia % 60
  return {
    current: 'OFF',
    label: 'After Hours',
    nextSessionName: 'Asian',
    nextSessionTime: '00:00 GMT',
    minutesToNext: minsToAsia,
    isPrime: false,
    nextLabel: `${h}h ${m}m`,
  } as SessionInfo & { nextLabel: string }
}

function fmt(n: number, dp = 2): string {
  if (!n) return '—'
  return n.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

function arrow(v: number): string {
  if (v > 0) return '▲'
  if (v < 0) return '▼'
  return '→'
}

function arrowClass(v: number): string {
  if (v > 0) return 'up'
  if (v < 0) return 'down'
  return 'flat'
}

interface Props {
  prices: CTraderPrices
  onRefresh: () => void
  lastRefresh: string
}

export function Header({ prices, onRefresh, lastRefresh }: Props) {
  const [now, setNow] = useState(new Date())

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  const utcH = now.getUTCHours()
  const utcM = now.getUTCMinutes()
  const utcS = now.getUTCSeconds()
  const session = getSession(utcH, utcM) as SessionInfo & { nextLabel: string }

  const timeStr = `${String(utcH).padStart(2,'0')}:${String(utcM).padStart(2,'0')}:${String(utcS).padStart(2,'0')} GMT`

  const xau = prices.XAUUSD
  const isLive = prices.status === 'live'
  const change = xau.changeDay
  const pct = xau.changePct

  return (
    <header className={styles.header}>
      <div className={styles.left}>
        <div className={styles.eyebrow}>XAUUSD Intelligence Dashboard</div>
        <div className={styles.priceRow}>
          <span className={styles.price}>
            {isLive ? `$${fmt(xau.price, 2)}` : '—'}
          </span>
          {isLive && (
            <span className={`${styles.change} ${arrowClass(change)}`}>
              {arrow(change)} {change >= 0 ? '+' : ''}{fmt(change, 2)} ({pct >= 0 ? '+' : ''}{fmt(pct, 2)}%)
            </span>
          )}
          <span className={`${styles.statusBadge} ${isLive ? styles.live : styles.offline}`}>
            {isLive ? 'LIVE' : prices.status === 'loading' ? 'CONNECTING...' : 'OFFLINE'}
          </span>
        </div>
      </div>

      <div className={styles.right}>
        <div className={styles.metaRow}>
          <span className={`${styles.sessionBadge} ${session.isPrime ? styles.prime : ''}`}>
            {session.label.toUpperCase()}
            {session.isPrime && ' · PRIME SESSION'}
          </span>
          <span className={styles.meta}>{session.nextSessionName} in {(session as unknown as { nextLabel: string }).nextLabel}</span>
        </div>
        <div className={styles.metaRow}>
          <span className={styles.clock}>{timeStr}</span>
          <span className={styles.meta}>
            Last refresh: {lastRefresh || '—'}
          </span>
          <button className={styles.refreshBtn} onClick={onRefresh} title="Refresh all data">
            ↺ Refresh
          </button>
        </div>
      </div>
    </header>
  )
}
