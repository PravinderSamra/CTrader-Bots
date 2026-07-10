import type { SectorRead } from '../../types/uk100'
import styles from '../tiles/Tile.module.css'

function readBadge(read: string): string {
  if (read === 'BULLISH') return 'badge-green'
  if (read === 'BEARISH') return 'badge-red'
  if (read === 'IDIOSYNCRATIC') return 'badge-gold'
  return 'badge-muted'
}

interface Props { sectors: SectorRead[] }

export function Uk100SectorTile({ sectors }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">Sector Panel</div>

      {sectors.length === 0 && <div className="data-null">Snapshot not yet generated — run GitHub Action</div>}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
        {sectors.map(s => (
          <div key={s.sector} className={styles.calEvent}>
            <div className={styles.calEventHeader}>
              <span className={styles.eventName} style={{ margin: 0 }}>{s.sector}</span>
              <span className={`badge ${readBadge(s.read)}`} style={{ marginLeft: 'auto' }}>{s.read}</span>
            </div>
            <div className={styles.eventMeta} style={{ marginTop: 2 }}>{s.weightNote}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 2 }}>{s.driver}</div>
            <div style={{ fontSize: 10, color: 'var(--text-dim)', marginTop: 2 }}>{s.detail}</div>
          </div>
        ))}
      </div>
    </div>
  )
}
