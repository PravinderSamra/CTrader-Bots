import type { CalendarEvent } from '../../types/dashboard'
import styles from './Tile.module.css'

function impactDots(level: CalendarEvent['impact']): string {
  if (level === 'HIGH') return '●●●'
  if (level === 'MEDIUM') return '●●'
  return '●'
}

interface Props { events: CalendarEvent[] }

export function CalendarTile({ events }: Props) {
  const high = events.filter(e => e.impact === 'HIGH').length
  const med  = events.filter(e => e.impact === 'MEDIUM').length

  return (
    <div className="tile">
      <div className="tile-eyebrow">Economic Calendar</div>

      <div className="tile-row" style={{ marginBottom: 4 }}>
        {high > 0 && <span className="badge badge-gold">{high} HIGH</span>}
        {med  > 0 && <span className="badge badge-blue">{med} MED</span>}
        {events.length === 0 && <span className="data-null">No events loaded</span>}
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 220, overflowY: 'auto' }}>
        {events.map((ev, i) => (
          <div
            key={i}
            className={`${styles.calEvent} ${ev.impact === 'HIGH' ? styles.calEventHigh : ev.impact === 'MEDIUM' ? styles.calEventMed : ''}`}
          >
            <div className={styles.eventTime}>
              <span className={`${styles.impactDots} ${ev.impact === 'HIGH' ? 'down' : ev.impact === 'MEDIUM' ? '' : 'flat'}`}>
                {impactDots(ev.impact)}
              </span>
              {' '}{ev.time} GMT · {ev.currency}
              {ev.actual != null && <span className="badge badge-muted" style={{ marginLeft: 6 }}>RELEASED</span>}
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
        ))}
      </div>
    </div>
  )
}
