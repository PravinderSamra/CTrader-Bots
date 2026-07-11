import type { PositioningBlock } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainPositioning } from './explainers'
import styles from '../tiles/Tile.module.css'

function crowdingBadge(crowding: string | null): string {
  if (crowding === 'CROWDED_LONG') return 'badge-green'
  if (crowding === 'CROWDED_SHORT') return 'badge-red'
  return 'badge-muted'
}
function impactBadge(impact: string): string {
  if (impact === 'BULLISH') return 'badge-green'
  if (impact === 'BEARISH') return 'badge-red'
  return 'badge-muted'
}

interface Props { positioning: PositioningBlock | null }

export function Uk100PositioningTile({ positioning }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">GBP Positioning (COT)</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">Net Long</span>
          <span className="tile-val mono">
            {positioning?.gbpCotNetLong != null ? positioning.gbpCotNetLong.toLocaleString('en-US') : '—'}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">WoW Change</span>
          <span className={`tile-val mono ${positioning?.gbpCotWoWChange != null ? (positioning.gbpCotWoWChange > 0 ? 'up' : positioning.gbpCotWoWChange < 0 ? 'down' : 'flat') : 'flat'}`}>
            {positioning?.gbpCotWoWChange != null ? `${positioning.gbpCotWoWChange >= 0 ? '+' : ''}${positioning.gbpCotWoWChange.toLocaleString('en-US')}` : '—'}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Crowding</span>
          <span className={`badge ${crowdingBadge(positioning?.crowding ?? null)}`}>
            {positioning?.crowding ?? '—'}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">FTSE readthrough</span>
          <span className={`badge ${impactBadge(positioning?.ftseReadthrough ?? 'NEUTRAL')}`}>
            {positioning?.ftseReadthrough ?? '—'}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Report Date</span>
          <span className="tile-val mono">{positioning?.reportDate ? positioning.reportDate.slice(0, 10) : '—'}</span>
        </div>
      </div>

      {!positioning && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainPositioning(positioning)} />
    </div>
  )
}
