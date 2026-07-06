import { useState, useEffect, useCallback } from 'react'
import type { CTraderPrices, SessionInfo } from '../../types/dashboard'
import type { OpenPosition } from '../../hooks/useOpenPosition'
import styles from './Header.module.css'

// ── BST / Kill zone detection ─────────────────────────────────────────────

function isBST(d: Date): boolean {
  const y = d.getUTCFullYear()
  // Last Sunday of March at 01:00 UTC → BST starts
  const marchSun = new Date(Date.UTC(y, 2, 31, 1))
  marchSun.setUTCDate(31 - marchSun.getUTCDay())
  // Last Sunday of October at 01:00 UTC → GMT returns
  const octSun = new Date(Date.UTC(y, 9, 31, 1))
  octSun.setUTCDate(31 - octSun.getUTCDay())
  return d >= marchSun && d < octSun
}

interface KZDef { name: string; localStart: number; localEnd: number }
const KILL_ZONES: KZDef[] = [
  { name: 'London KZ',     localStart: 7*60,       localEnd: 10*60      },
  { name: 'Silver Bullet', localStart: 9*60,        localEnd: 10*60      },
  { name: 'NY KZ',         localStart: 13*60+30,    localEnd: 16*60      },
  { name: 'London Close',  localStart: 15*60,        localEnd: 16*60      },
]

interface KZInfo {
  active: boolean
  name: string
  minutes: number    // remaining if active, until if not
}

function getKZInfo(now: Date): KZInfo {
  const bst = isBST(now)
  const utcMin = now.getUTCHours() * 60 + now.getUTCMinutes()
  const londonMin = bst ? utcMin + 60 : utcMin

  for (const kz of KILL_ZONES) {
    if (londonMin >= kz.localStart && londonMin < kz.localEnd) {
      return { active: true, name: kz.name, minutes: kz.localEnd - londonMin }
    }
  }

  const todayRemaining = KILL_ZONES.filter(kz => kz.localStart > londonMin)
    .sort((a, b) => a.localStart - b.localStart)

  if (todayRemaining.length > 0) {
    return { active: false, name: todayRemaining[0].name, minutes: todayRemaining[0].localStart - londonMin }
  }

  const nextKZ = [...KILL_ZONES].sort((a, b) => a.localStart - b.localStart)[0]
  return { active: false, name: nextKZ.name, minutes: (24*60 - londonMin) + nextKZ.localStart }
}

function fmtKZTime(mins: number): string {
  const h = Math.floor(mins / 60)
  const m = mins % 60
  if (h > 0) return `${h}h ${String(m).padStart(2,'0')}m`
  return `${m}m`
}

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
  openPosition?: OpenPosition | null
}

export function Header({ prices, onRefresh, lastRefresh, openPosition }: Props) {
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

  const utcH = now.getUTCHours()
  const utcM = now.getUTCMinutes()
  const utcS = now.getUTCSeconds()
  const session = getSession(utcH, utcM) as SessionInfo & { nextLabel: string }
  const kz = getKZInfo(now)

  const timeStr = `${String(utcH).padStart(2,'0')}:${String(utcM).padStart(2,'0')}:${String(utcS).padStart(2,'0')} GMT`

  const xau = prices.XAUUSD
  const isLive = prices.status === 'live'
  const change = xau.changeDay
  const pct = xau.changePct

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
                {kz.active ? `closes in ${fmtKZTime(kz.minutes)}` : `opens in ${fmtKZTime(kz.minutes)}`}
              </span>
            </div>
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
