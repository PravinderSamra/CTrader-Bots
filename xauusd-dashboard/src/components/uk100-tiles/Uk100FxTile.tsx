import type { FxBlock, Uk100Prices } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainFx } from './explainers'
import styles from '../tiles/Tile.module.css'

function fmt(v: number | null, dp = 2): string {
  if (v == null) return '—'
  return v.toFixed(dp)
}
function arrow(v: number | null): string {
  if (v == null) return ''
  if (v > 0) return ' ▲'
  if (v < 0) return ' ▼'
  return ' →'
}
function cls(v: number | null): string {
  if (v == null) return 'flat'
  if (v > 0) return 'up'
  if (v < 0) return 'down'
  return 'flat'
}
function impactBadge(impact: string): string {
  if (impact === 'BULLISH') return 'badge-green'
  if (impact === 'BEARISH') return 'badge-red'
  return 'badge-muted'
}

interface Props {
  fx: FxBlock | null
  prices: Uk100Prices | null
}

export function Uk100FxTile({ fx, prices }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">Sterling &amp; FX</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">GBPUSD</span>
          <span className={`tile-val mono ${cls(fx?.gbpUsdDayPct ?? null)}`}>
            {fmt(prices?.GBPUSD ?? null, 4)}{arrow(fx?.gbpUsdDayPct ?? null)}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Day %</span>
          <span className={`tile-val mono ${cls(fx?.gbpUsdDayPct ?? null)}`}>
            {fx?.gbpUsdDayPct != null ? `${fx.gbpUsdDayPct >= 0 ? '+' : ''}${fmt(fx.gbpUsdDayPct)}%` : '—'}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">GBPEUR</span>
          <span className="tile-val mono">{fmt(prices?.GBPEUR ?? null, 4)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Sterling ERI</span>
          <span className={`tile-val mono ${cls(fx?.sterlingEriDayChange ?? null)}`}>
            {fmt(fx?.sterlingEri ?? null, 2)}{arrow(fx?.sterlingEriDayChange ?? null)}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">FTSE readthrough</span>
          <span className={`badge ${impactBadge(fx?.ftseImpactFromGbp ?? 'NEUTRAL')}`}>
            {fx?.ftseImpactFromGbp ?? '—'}
          </span>
        </div>
      </div>

      {!fx && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainFx(fx)} />
    </div>
  )
}
