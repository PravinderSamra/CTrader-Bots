import type { UsLinkageBlock, Uk100Prices } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainUsLinkage } from './explainers'
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
// B2: STRESS -> red, NORMAL -> muted (per V2 plan); CALM and any
// unrecognised legacy value (e.g. pre-B2 'ELEVATED') also fall to muted
// rather than crashing.
function vixBadge(regime: string): string {
  if (regime === 'STRESS') return 'badge-red'
  return 'badge-muted'
}

interface Props {
  usLinkage: UsLinkageBlock | null
  prices: Uk100Prices | null
}

export function Uk100UsLinkageTile({ usLinkage, prices }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">US Linkage</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">US500</span>
          <span className={`tile-val mono ${cls(usLinkage?.us500DayPct ?? null)}`}>
            {usLinkage?.us500DayPct != null ? `${usLinkage.us500DayPct >= 0 ? '+' : ''}${fmt(usLinkage.us500DayPct)}%` : '—'}
            {arrow(usLinkage?.us500DayPct ?? null)}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">NAS100</span>
          <span className={`tile-val mono ${cls(usLinkage?.nas100DayPct ?? null)}`}>
            {usLinkage?.nas100DayPct != null ? `${usLinkage.nas100DayPct >= 0 ? '+' : ''}${fmt(usLinkage.nas100DayPct)}%` : '—'}
            {arrow(usLinkage?.nas100DayPct ?? null)}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">VIX</span>
          <span className="tile-val mono">
            {fmt(usLinkage?.vix ?? null, 1)}
            {usLinkage?.vixRegime && <span className={`badge ${vixBadge(usLinkage.vixRegime)} ${styles.badgeInline}`}>{usLinkage.vixRegime}</span>}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">USDX</span>
          <span className="tile-val mono">{fmt(prices?.USDX ?? null, 2)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">US 10Y</span>
          <span className="tile-val mono">{fmt(usLinkage?.us10y ?? null, 2)}%</span>
        </div>
      </div>

      {!usLinkage && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainUsLinkage(usLinkage)} />
    </div>
  )
}
