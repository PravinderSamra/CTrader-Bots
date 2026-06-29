import type { COTPositioning } from '../../types/dashboard'
import styles from './Tile.module.css'

function fmtNet(v: number | null): string {
  if (v == null) return '—'
  return (v >= 0 ? '+' : '') + v.toLocaleString('en-US')
}

function fmtDate(iso: string | null): string {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short' })
  } catch { return iso }
}

interface Props { cot: COTPositioning | null }

export function PositioningTile({ cot }: Props) {
  const crowding = cot?.crowding ?? null
  const wowCls = cot?.cotWoWChange != null
    ? (cot.cotWoWChange > 0 ? 'up' : cot.cotWoWChange < 0 ? 'down' : 'flat')
    : 'flat'

  const crowdBadge = crowding === 'CROWDED_LONG'
    ? <span className="badge badge-amber">CROWDED LONG</span>
    : crowding === 'CROWDED_SHORT'
    ? <span className="badge badge-blue">CROWDED SHORT</span>
    : crowding === 'NEUTRAL'
    ? <span className="badge badge-muted">NEUTRAL</span>
    : null

  return (
    <div className="tile">
      <div className="tile-eyebrow">Positioning · COT</div>

      {cot ? (
        <div className={styles.rows}>
          <div>
            <div className="tile-label">Net Speculative</div>
            <div className={`${styles.headline} ${cot.cotNetLong != null && cot.cotNetLong > 0 ? 'up' : 'down'}`}>
              {fmtNet(cot.cotNetLong)}
            </div>
          </div>
          <div className="tile-row">
            <span className="tile-label">WoW change</span>
            <span className={`tile-val mono ${wowCls}`}>
              {fmtNet(cot.cotWoWChange)}
              {cot.cotWoWChange != null && (cot.cotWoWChange > 0 ? ' ▲' : cot.cotWoWChange < 0 ? ' ▼' : ' →')}
            </span>
          </div>
          <div className="tile-row">
            <span className="tile-label">Crowd</span>
            {crowdBadge}
          </div>
          <div className="tile-row">
            <span className="tile-label">Report date</span>
            <span className="tile-val mono">{fmtDate(cot.reportDate)}</span>
          </div>
          {cot.reportDate && (
            <div className="data-null">COT updates Fridays only</div>
          )}
        </div>
      ) : (
        <div className="data-null">Snapshot not yet generated</div>
      )}
    </div>
  )
}
