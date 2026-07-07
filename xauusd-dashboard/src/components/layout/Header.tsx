import { useState, useEffect, useCallback } from 'react'
import type { CTraderPrices, CalendarEvent } from '../../types/dashboard'
import type { OpenPosition } from '../../hooks/useOpenPosition'
import { getSession, getKillZone, fmtDuration } from '../../utils/sessions'
import { ukClockString, ukTimeString } from '../../utils/time'
import { nextHighImpactEvent } from '../../utils/nextEvent'
import { EventCountdown } from '../common/EventCountdown'
import styles from './Header.module.css'

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
  openPosition?: OpenPosition | null
  snapshotGeneratedAt?: string | null
  calendar?: CalendarEvent[]
}

export function Header({ prices, onRefresh, lastRefresh, openPosition, snapshotGeneratedAt, calendar }: Props) {
  const [now, setNow] = useState(new Date())
  const [theme, setTheme] = useState<'dark' | 'light'>(() => {
    const stored = localStorage.getItem('xau-theme')
    if (stored === 'light' || stored === 'dark') return stored
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 1000)
    return () => clearInterval(id)
  }, [])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
    localStorage.setItem('xau-theme', theme)
  }, [theme])

  const toggleTheme = useCallback(() => setTheme(t => t === 'dark' ? 'light' : 'dark'), [])

  const session = getSession(now)
  const kz = getKillZone(now)
  const timeStr = ukClockString(now)

  const xau = prices.XAUUSD
  const isLive = prices.status === 'live'
  const change = xau.changeDay
  const pct = xau.changePct

  const snapshotAge = !isLive && snapshotGeneratedAt
    ? ukTimeString(new Date(snapshotGeneratedAt))
    : null

  return (
    <>
      <header className={styles.header}>
        <div className={styles.left}>
          <div className={styles.eyebrow}>XAUUSD Intelligence Dashboard</div>
          <div className={styles.priceRow}>
            <span className={styles.price}>
              {xau.price ? `$${fmt(xau.price, 2)}` : '—'}
            </span>
            {isLive && change !== 0 && (
              <span className={`${styles.change} ${arrowClass(change)}`}>
                {arrow(change)} {change >= 0 ? '+' : ''}{fmt(change, 2)} ({pct >= 0 ? '+' : ''}{fmt(pct, 2)}%)
              </span>
            )}
            <span className={`${styles.statusBadge} ${isLive ? styles.live : styles.offline}`}>
              {isLive ? 'LIVE' : prices.status === 'loading' ? 'CONNECTING...' : 'OFFLINE'}
            </span>
            {snapshotAge && (
              <span className={styles.snapshotAge} title="Live feed unavailable — showing last server snapshot">
                data as of {snapshotAge}
              </span>
            )}
          </div>
        </div>

        <div className={styles.right}>
          <div className={styles.metaRow}>
            <span className={`${styles.sessionBadge} ${session.isPrime ? styles.prime : ''}`}>
              {session.label.toUpperCase()}
              {session.isPrime && ' · PRIME SESSION'}
            </span>
            <div className={`${styles.kzBadge} ${kz.active ? styles.kzActive : styles.kzWaiting}`}>
              {kz.active && <span className={styles.kzPulse} />}
              <span className={styles.kzName}>{kz.name}</span>
              <span className={styles.kzTime}>
                {kz.active ? `closes in ${fmtDuration(kz.minutes)}` : `opens in ${fmtDuration(kz.minutes)}`}
              </span>
            </div>
            {calendar && <EventCountdown next={nextHighImpactEvent(calendar, now.getTime())} />}
          </div>
          <div className={styles.metaRow}>
            <span className={styles.clock}>{timeStr}</span>
            <span className={styles.meta}>
              Last refresh: {lastRefresh || '—'}
            </span>
            <button className={styles.themeBtn} onClick={toggleTheme} title="Toggle theme">
              {theme === 'dark' ? '☀' : '◑'}
            </button>
            <button className={styles.refreshBtn} onClick={onRefresh} title="Refresh all data">
              ↺ Refresh
            </button>
          </div>
        </div>
      </header>

      {openPosition && (
        <div className={`${styles.posBanner} ${openPosition.pnl >= 0 ? styles.posProfit : styles.posLoss}`}>
          <span className={styles.posDir}>{openPosition.direction}</span>
          <span className={styles.posDetail}>
            {openPosition.lots.toFixed(2)} lot · Entry ${fmt(openPosition.entryPrice, 2)} · Now ${fmt(openPosition.currentPrice, 2)}
          </span>
          <span className={styles.posPnl}>
            {openPosition.pnl >= 0 ? '+' : ''}${openPosition.pnl.toFixed(2)}
            {' '}({openPosition.pnlPct >= 0 ? '+' : ''}{openPosition.pnlPct.toFixed(2)}%)
          </span>
        </div>
      )}
    </>
  )
}
