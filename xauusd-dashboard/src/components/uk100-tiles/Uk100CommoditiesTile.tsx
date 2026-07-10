import type { CommoditiesBlock, Uk100Prices } from '../../types/uk100'
import styles from '../tiles/Tile.module.css'

function fmt(v: number | null, dp = 2): string {
  if (v == null) return '—'
  return v.toFixed(dp)
}
function arrow(v: number | null): string {
  if (v == null) return ''
  if (v > 0.05) return ' ▲'
  if (v < -0.05) return ' ▼'
  return ' →'
}
function cls(v: number | null): string {
  if (v == null) return 'flat'
  if (v > 0.05) return 'up'
  if (v < -0.05) return 'down'
  return 'flat'
}

interface Props {
  commodities: CommoditiesBlock | null
  prices: Uk100Prices | null
}

export function Uk100CommoditiesTile({ commodities, prices }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">Commodities</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">Brent</span>
          <span className={`tile-val mono ${cls(commodities?.brentDayPct ?? null)}`}>
            {fmt(prices?.BRENT ?? null, 2)}
            {commodities?.brentDayPct != null && ` (${commodities.brentDayPct >= 0 ? '+' : ''}${fmt(commodities.brentDayPct)}%)`}
            {arrow(commodities?.brentDayPct ?? null)}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Brent 20d</span>
          <span className="tile-val mono">{commodities?.brent20dTrend ?? '—'}</span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Copper</span>
          <span className={`tile-val mono ${cls(commodities?.copperDayPct ?? null)}`}>
            {fmt(prices?.COPPER ?? null, 3)}
            {commodities?.copperDayPct != null && ` (${commodities.copperDayPct >= 0 ? '+' : ''}${fmt(commodities.copperDayPct)}%)`}
            {arrow(commodities?.copperDayPct ?? null)}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Gold</span>
          <span className={`tile-val mono ${cls(commodities?.goldDayPct ?? null)}`}>
            {fmt(prices?.XAUUSD ?? null, 2)}
            {commodities?.goldDayPct != null && ` (${commodities.goldDayPct >= 0 ? '+' : ''}${fmt(commodities.goldDayPct)}%)`}
            {arrow(commodities?.goldDayPct ?? null)}
          </span>
        </div>
      </div>

      <div className="tile-row" style={{ marginTop: 4 }}>
        <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>Brent → energy majors · Copper → miners/China proxy</span>
      </div>

      {!commodities && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}
    </div>
  )
}
