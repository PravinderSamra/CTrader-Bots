import type { Uk100CalendarEvent, Uk100NewsItem } from '../../types/uk100'
import styles from '../tiles/Tile.module.css'

function dayLabel(daysFromToday: number): string {
  if (daysFromToday === 0) return 'TODAY'
  if (daysFromToday === 1) return 'TOMORROW'
  return `IN ${daysFromToday}D`
}

interface Props {
  events: Uk100CalendarEvent[]
  news: Uk100NewsItem[]
}

export function Uk100CalendarTile({ events, news }: Props) {
  const high = events.filter(e => e.impact === 'HIGH').length
  const med = events.filter(e => e.impact === 'MEDIUM').length
  const buildUp = events.filter(e => e.impact === 'HIGH' && e.daysFromToday > 0 && e.daysFromToday <= 4)

  return (
    <div className="tile">
      <div className="tile-eyebrow">UK/US/EZ Calendar &amp; News</div>

      <div className="tile-row" style={{ marginBottom: 4 }}>
        {high > 0 && <span className="badge badge-red">{high} HIGH</span>}
        {med > 0 && <span className="badge badge-amber">{med} MED</span>}
        {events.length === 0 && <span className="data-null">No events loaded</span>}
      </div>

      {buildUp.length > 0 && (
        <div className={styles.cautionBanner}>
          Build-up caution: {buildUp.length} HIGH-impact event{buildUp.length > 1 ? 's' : ''} later this week.
        </div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 3, maxHeight: 220, overflowY: 'auto' }}>
        {events.map((ev, i) => {
          const impactCls = ev.impact === 'HIGH' ? styles.calEventHigh : ev.impact === 'MEDIUM' ? styles.calEventMed : ''
          return (
            <div key={i} className={`${styles.calEvent} ${impactCls}`}>
              <div className={styles.calEventHeader}>
                <span className={styles.eventTime}>{ev.timeLondon} · {ev.region}</span>
                <span className={styles.calCountdown}>{dayLabel(ev.daysFromToday)}</span>
              </div>
              <div className={styles.eventName}>{ev.event}</div>
              {(ev.prior || ev.consensus) && (
                <div className={styles.eventMeta}>
                  {ev.consensus && <span>Cons: {ev.consensus}</span>}
                  {ev.prior && <span>Prior: {ev.prior}</span>}
                </div>
              )}
            </div>
          )
        })}
      </div>

      {news.length > 0 && (
        <>
          <hr className="tile-divider" />
          <div style={{ display: 'flex', flexDirection: 'column', gap: 4, maxHeight: 140, overflowY: 'auto' }}>
            {news.map((n, i) => (
              <div key={i} style={{ fontSize: 11 }}>
                <span style={{ color: 'var(--text)' }}>{n.headline}</span>
                <span style={{ color: 'var(--text-dim)', marginLeft: 6, fontSize: 10 }}>
                  {n.source} · {n.hoursAgo}h ago
                </span>
              </div>
            ))}
          </div>
        </>
      )}
    </div>
  )
}
