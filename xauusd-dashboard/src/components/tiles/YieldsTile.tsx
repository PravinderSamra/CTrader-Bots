import type { YieldsData } from '../../types/dashboard'
import { TileSpark } from '../common/TileSpark'
import styles from './Tile.module.css'

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

interface Props { yields: YieldsData | null }

export function YieldsTile({ yields }: Props) {
  const dod = yields?.dayOverDay ?? null
  const curve = yields?.curve2s10s ?? null
  const dodUS10Y = dod?.US10Y ?? null
  const dodUS2Y = dod?.US2Y ?? null
  const dodReal10Y = dod?.realYield10Y ?? null

  return (
    <div className="tile">
      <div className="tile-eyebrow">Yields &amp; Rates</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">10Y</span>
          <span className={`tile-val mono ${cls(dodUS10Y)}`}>
            {fmt(yields?.US10Y ?? null)}%{arrow(dodUS10Y)}
          </span>
        </div>
        <TileSpark metric="us10y" label="US 10Y 7-day trend" />
        <div className="tile-row">
          <span className="tile-label">2Y</span>
          <span className={`tile-val mono ${cls(dodUS2Y)}`}>
            {fmt(yields?.US2Y ?? null)}%{arrow(dodUS2Y)}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Real 10Y</span>
          <span className={`tile-val mono ${yields?.realYield10Y != null && yields.realYield10Y > 0 ? styles.bearish : ''}`}>
            {fmt(yields?.realYield10Y ?? null)}%{arrow(dodReal10Y)}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">2s10s</span>
          <span className={`tile-val mono ${curve != null && curve < 0 ? styles.warning : ''}`}>
            {curve != null ? `${curve > 0 ? '+' : ''}${curve}bp` : '—'}
            {curve != null && curve < 0 && (
              <span className={`badge badge-amber ${styles.badgeInline}`}>INVERTED</span>
            )}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">BE 10Y</span>
          <span className="tile-val mono">{fmt(yields?.breakeven10Y ?? null)}%</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">BE 5Y</span>
          <span className="tile-val mono">{fmt(yields?.breakeven5Y ?? null)}%</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">5y5y</span>
          <span className="tile-val mono">{fmt(yields?.forward5y5y ?? null)}%</span>
        </div>
      </div>

      {!yields && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}
    </div>
  )
}
