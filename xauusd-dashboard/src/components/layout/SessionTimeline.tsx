import { useState, useEffect } from 'react'
import {
  sessionSegmentsUtc, killZoneBandsUtc, getSession, getKillZone,
  type SessionKey,
} from '../../utils/sessions'
import { ukTimeString } from '../../utils/time'
import styles from './SessionTimeline.module.css'

const SEG_CLASS: Record<SessionKey, string> = {
  ASIAN:    styles.segAsian,
  LONDON:   styles.segLondon,
  OVERLAP:  styles.segOverlap,
  NEW_YORK: styles.segNY,
  OFF:      styles.segAsian,
}

const LBL_CLASS: Record<SessionKey, string> = {
  ASIAN:    styles.lblAsian,
  LONDON:   styles.lblLondon,
  OVERLAP:  styles.lblOverlap,
  NEW_YORK: styles.lblNY,
  OFF:      styles.lblAsian,
}

// Only the three major bands render on the bar (Silver Bullets / Asia KZ would clutter).
const KZ_CLASS: Record<string, string> = {
  'London KZ':    styles.kzLondon,
  'NY KZ':        styles.kzNY,
  'London Close': styles.kzClose,
}

function pct(mins: number) { return (mins / (24 * 60)) * 100 }

function fmtUtc(mins: number): string {
  const m = ((Math.round(mins) % 1440) + 1440) % 1440
  const h = Math.floor(m / 60)
  return `${String(h).padStart(2, '0')}:${String(m % 60).padStart(2, '0')}`
}

// A UTC-minute span that may wrap past midnight → one or two [start,width] rects in %.
function rects(startMin: number, endMin: number): { left: number; width: number }[] {
  if (startMin <= endMin) return [{ left: pct(startMin), width: pct(endMin - startMin) }]
  return [
    { left: pct(startMin), width: pct(1440 - startMin) },
    { left: 0, width: pct(endMin) },
  ]
}

function midpoint(startMin: number, endMin: number): number {
  const end = endMin >= startMin ? endMin : endMin + 1440
  return ((startMin + end) / 2) % 1440
}

export function SessionTimeline() {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  const utcMins = now.getUTCHours() * 60 + now.getUTCMinutes()
  const nowPct  = pct(utcMins)

  const segments = sessionSegmentsUtc(now)
  const bands    = killZoneBandsUtc(now).filter(b => KZ_CLASS[b.name])

  const session = getSession(now)
  const kz      = getKillZone(now)

  return (
    <div className={styles.shell}>
      <div className={styles.barWrap}>
        {/* Session segments */}
        {segments.map(s =>
          rects(s.startUtcMin, s.endUtcMin).map((r, i) => (
            <div
              key={`${s.key}-${i}`}
              className={`${styles.seg} ${SEG_CLASS[s.key]}`}
              style={{ left: `${r.left}%`, width: `${r.width}%` }}
              title={s.label}
            />
          ))
        )}

        {/* Kill zone overlays */}
        {bands.map(b =>
          rects(b.startUtcMin, b.endUtcMin).map((r, i) => (
            <div
              key={`${b.name}-${i}`}
              className={`${styles.kz} ${KZ_CLASS[b.name]}`}
              style={{ left: `${r.left}%`, width: `${r.width}%` }}
              title={b.name}
            />
          ))
        )}

        {/* Boundary ticks at each session start */}
        {segments.map(s => (
          <div key={`tick-${s.key}`} className={styles.tick} style={{ left: `${pct(s.startUtcMin)}%` }} />
        ))}

        {/* Now cursor */}
        <div className={styles.cursor} style={{ left: `${nowPct}%` }} title="Now" />
      </div>

      {/* Labels */}
      <div className={styles.labels}>
        {segments.map(s => (
          <span
            key={`lbl-${s.key}`}
            className={`${styles.lbl} ${LBL_CLASS[s.key]}`}
            style={{ left: `${pct(midpoint(s.startUtcMin, s.endUtcMin))}%` }}
          >
            {s.key === 'NEW_YORK' ? 'NEW YORK' : s.key === 'OVERLAP' ? 'OVR' : s.label.toUpperCase()}
          </span>
        ))}

        {/* Boundary times (UTC axis) */}
        {segments.map(s => (
          <span key={`t-${s.key}`} className={styles.timeLbl} style={{ left: `${pct(s.startUtcMin)}%` }}>
            {fmtUtc(s.startUtcMin)}
          </span>
        ))}
      </div>

      {/* Active indicator */}
      <div className={styles.nowLabel}>
        <span className={styles.nowDot} />
        <span className={styles.nowText}>
          {kz.active ? kz.name : session.label}
        </span>
        <span className={styles.nowUtc}>{ukTimeString(now)}</span>
      </div>
    </div>
  )
}
