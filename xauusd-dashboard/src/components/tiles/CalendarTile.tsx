import { useState, useEffect } from 'react'
import type { CalendarEvent } from '../../types/dashboard'
import styles from './Tile.module.css'

function dayLabel(ev: CalendarEvent): string {
  if (ev.daysFromToday === 0) return 'TODAY'
  if (ev.daysFromToday === 1) return 'TOMORROW'
  try {
    return new Date(`${ev.date}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'long', timeZone: 'UTC' }).toUpperCase()
  } catch { return ev.date }
}

function eventCountdown(ev: CalendarEvent, now: Date): string | null {
  if (ev.actual != null) return null
  if (ev.daysFromToday < 0) return null
  const [h, m] = (ev.time ?? '00:00').split(':').map(Number)
  const evUtc = new Date(`${ev.date}T${String(h).padStart(2,'0')}:${String(m || 0).padStart(2,'0')}:00Z`)
  const diffMs = evUtc.getTime() - now.getTime()
  if (diffMs < 0) return null
  const totalMin = Math.floor(diffMs / 60000)
  if (totalMin > 48 * 60) return null  // only show countdown within 48h
  const hrs = Math.floor(totalMin / 60)
  const mins = totalMin % 60
  return hrs > 0 ? `in ${hrs}h ${mins}m` : `in ${mins}m`
}

interface Props { events: CalendarEvent[] }

export function CalendarTile({ events }: Props) {
  const [now, setNow] = useState(new Date())
  useEffect(() => {
    const id = setInterval(() => setNow(new Date()), 60_000)
    return () => clearInterval(id)
  }, [])

  const high = events.filter(e => e.impact === 'HIGH').length
  const med  = events.filter(e => e.impact === 'MEDIUM').length
  const buildUp = events.filter(e => e.impact === 'HIGH' && e.daysFromToday > 0 && e.daysFromToday <= 4)

  let lastDate = ''

  return (
    <div className="tile">
      <div className="tile-eyebrow">Economic Calendar — Week Ahead</div>

      <div className="tile-row" style={{ marginBottom: 4 }}>
        {high > 0 && <span className="badge badge-red">{high} HIGH</span>}
        {med  > 0 && <span className="badge badge-amber">{med} MED</span>}
        {events.length === 0 && <span className="data-null">No events loaded</span>}
      </div>

      {buildUp.length > 0 && (
        <div className={styles.cautionBanner}>
          Build-up caution: {buildUp.length} HIGH-impact event{buildUp.length > 1 ? 's' : ''} later this week
          — cautious positioning expected.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3, maxHeight: 280, overflowY: 'auto' }}>
        {events.map((ev, i) => {
          const showDayHeader = ev.date !== lastDate
          lastDate = ev.date
          const countdown = eventCountdown(ev, now)
          const impactCls = ev.impact === 'HIGH' ? styles.calEventHigh : ev.impact === 'MEDIUM' ? styles.calEventMed : ''
          return (
            <div key={i}>
              {showDayHeader && (
                <div className={styles.dayHeader}>{dayLabel(ev)}</div>
              )}
              <div className={`${styles.calEvent} ${impactCls}`}>
                <div className={styles.calEventHeader}>
                  <span className={styles.eventTime}>{ev.time} GMT · {ev.currency}</span>
                  {countdown && (
                    <span className={`${styles.calCountdown} ${ev.impact === 'HIGH' ? styles.calCountdownHigh : ''}`}>
                      {countdown}
                    </span>
                  )}
                  {ev.actual != null && <span className="badge badge-muted">RELEASED</span>}
                </div>
                <div className={styles.eventName}>{ev.event}</div>
                <div className={styles.eventMeta}>
                  {ev.forecast != null && <span>Fcst: {ev.forecast}</span>}
                  {ev.previous != null && <span>Prev: {ev.previous}</span>}
                  {ev.actual != null && (
                    <span className={ev.actual > (ev.forecast ?? ev.actual) ? 'up' : ev.actual < (ev.forecast ?? ev.actual) ? 'down' : 'flat'}>
                      Act: {ev.actual}
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
