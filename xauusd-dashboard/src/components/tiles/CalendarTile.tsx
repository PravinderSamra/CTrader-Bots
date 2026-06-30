import type { CalendarEvent } from '../../types/dashboard'
import styles from './Tile.module.css'

function impactDots(level: CalendarEvent['impact']): string {
  if (level === 'HIGH') return '●●●'
  if (level === 'MEDIUM') return '●●'
  return '●'
}

function dayLabel(ev: CalendarEvent): string {
  if (ev.daysFromToday === 0) return 'TODAY'
  if (ev.daysFromToday === 1) return 'TOMORROW'
  try {
    return new Date(`${ev.date}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'long', timeZone: 'UTC' }).toUpperCase()
  } catch {
    return ev.date
  }
}

interface Props { events: CalendarEvent[] }

export function CalendarTile({ events }: Props) {
  const high = events.filter(e => e.impact === 'HIGH').length
  const med  = events.filter(e => e.impact === 'MEDIUM').length

  const buildUp = events.filter(e => e.impact === 'HIGH' && e.daysFromToday > 0 && e.daysFromToday <= 4)

  let lastDate = ''

  return (
    <div className="tile">
      <div className="tile-eyebrow">Economic Calendar — Week Ahead</div>

      <div className="tile-row" style={{ marginBottom: 4 }}>
        {high > 0 && <span className="badge badge-gold">{high} HIGH</span>}
        {med  > 0 && <span className="badge badge-blue">{med} MED</span>}
        {events.length === 0 && <span className="data-null">No events loaded</span>}
      </div>

      {buildUp.length > 0 && (
        <div className={styles.cautionBanner}>
          ⚠ Build-up caution: {buildUp.length} HIGH-impact event{buildUp.length > 1 ? 's' : ''} later this week
          ({buildUp.map(e => `${dayLabel(e)} ${e.event}`).join(', ')}) — expect cautious positioning into the release.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 260, overflowY: 'auto' }}>
        {events.map((ev, i) => {
          const showDayHeader = ev.date !== lastDate
          lastDate = ev.date
          return (
            <div key={i}>
              {showDayHeader && (
                <div className={styles.dayHeader}>{dayLabel(ev)}</div>
              )}
              <div
                className={`${styles.calEvent} ${ev.impact === 'HIGH' ? styles.calEventHigh : ev.impact === 'MEDIUM' ? styles.calEventMed : ''}`}
              >
                <div className={styles.eventTime}>
                  <span className={`${styles.impactDots} ${ev.impact === 'HIGH' ? 'down' : ev.impact === 'MEDIUM' ? '' : 'flat'}`}>
                    {impactDots(ev.impact)}
                  </span>
                  {' '}{ev.time} GMT · {ev.currency}
                  {ev.actual != null && <span className="badge badge-muted" style={{ marginLeft: 6 }}>RELEASED</span>}
                  {ev.actual == null && ev.impact === 'HIGH' && ev.daysFromToday > 0 && (
                    <span className="badge badge-gold" style={{ marginLeft: 6 }}>UPCOMING</span>
                  )}
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
