import type { ETFFlows } from '../../types/dashboard'
import styles from './Tile.module.css'

interface Props { flows: ETFFlows | null }

export function FlowsTile({ flows }: Props) {
  const wowCls = flows?.gldWoWChange != null
    ? (flows.gldWoWChange > 0 ? 'up' : flows.gldWoWChange < 0 ? 'down' : 'flat')
    : 'flat'

  const trendBadge = flows?.trend3W === 'INFLOW'
    ? <span className="badge badge-green">INFLOW (3W)</span>
    : flows?.trend3W === 'OUTFLOW'
    ? <span className="badge badge-red">OUTFLOW (3W)</span>
    : flows?.trend3W === 'FLAT'
    ? <span className="badge badge-muted">FLAT (3W)</span>
    : null

  return (
    <div className="tile">
      <div className="tile-eyebrow">ETF Flows · GLD</div>

      {flows ? (
        <div className={styles.rows}>
          <div>
            <div className="tile-label">GLD Holdings</div>
            <div className={styles.headline}>
              {flows.gldTonnes != null ? `${flows.gldTonnes.toFixed(1)}t` : '—'}
            </div>
          </div>
          <div className="tile-row">
            <span className="tile-label">WoW change</span>
            <span className={`tile-val mono ${wowCls}`}>
              {flows.gldWoWChange != null
                ? `${flows.gldWoWChange > 0 ? '+' : ''}${flows.gldWoWChange.toFixed(1)}t ${flows.gldWoWChange > 0 ? '▲' : flows.gldWoWChange < 0 ? '▼' : '→'}`
                : '—'}
            </span>
          </div>
          <div className="tile-row">
            <span className="tile-label">Trend</span>
            {trendBadge}
          </div>
          <div className="data-null" style={{ marginTop: 4 }}>
            {flows.trend3W === 'INFLOW'
              ? 'Institutional investors adding gold exposure'
              : flows.trend3W === 'OUTFLOW'
              ? 'Institutional investors reducing gold exposure'
              : 'ETF holdings stable'}
          </div>
        </div>
      ) : (
        <div className="data-null">Snapshot not yet generated</div>
      )}
    </div>
  )
}
