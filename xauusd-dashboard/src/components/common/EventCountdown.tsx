import { useState, useEffect } from 'react'
import { fmtCountdown, type ResolvedEvent } from '../../utils/nextEvent'
import styles from './EventCountdown.module.css'

interface Props {
  next: Omit<ResolvedEvent, 'msUntil'> | null   // {event, whenIso, currency?}
}

function shorten(name: string): string {
  return name.length > 22 ? name.slice(0, 21).trimEnd() + '…' : name
}

/**
 * Live countdown chip to the next HIGH-impact event. Ticks every 30s, turns
 * amber inside the final 2h, and disappears once the event has passed.
 */
export function EventCountdown({ next }: Props) {
  const [now, setNow] = useState(Date.now())
  useEffect(() => {
    const id = setInterval(() => setNow(Date.now()), 30_000)
    return () => clearInterval(id)
  }, [])

  if (!next) return null
  const msUntil = Date.parse(next.whenIso) - now
  if (!Number.isFinite(msUntil) || msUntil <= 0) return null

  const soon = msUntil < 2 * 3600 * 1000
  return (
    <span
      className={`${styles.chip} ${soon ? styles.soon : ''}`}
      title={`${next.currency ? next.currency + ' · ' : ''}${next.event} — high-impact`}
    >
      <span className={styles.icon} aria-hidden>◈</span>
      <span className={styles.name}>{shorten(next.event)}</span>
      <span className={styles.time}>{fmtCountdown(msUntil)}</span>
    </span>
  )
}
