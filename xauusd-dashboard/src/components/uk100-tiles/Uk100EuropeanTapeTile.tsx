import type { EuropeanTapeBlock } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainEuropeanTape } from './explainers'
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
function agreementBadge(agreement: EuropeanTapeBlock['tapeAgreement']): string {
  if (agreement === 'DIVERGING') return 'badge-red'
  if (agreement === 'SPLIT') return 'badge-amber'
  return 'badge-muted'
}

interface Props {
  europeanTape: EuropeanTapeBlock | null
}

export function Uk100EuropeanTapeTile({ europeanTape }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">European Tape</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">Euro Stoxx 50</span>
          <span className={`tile-val mono ${cls(europeanTape?.eurostoxx50DayPct ?? null)}`}>
            {europeanTape?.eurostoxx50DayPct != null ? `${europeanTape.eurostoxx50DayPct >= 0 ? '+' : ''}${fmt(europeanTape.eurostoxx50DayPct)}%` : '—'}
            {arrow(europeanTape?.eurostoxx50DayPct ?? null)}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">DAX</span>
          <span className={`tile-val mono ${cls(europeanTape?.dax40DayPct ?? null)}`}>
            {europeanTape?.dax40DayPct != null ? `${europeanTape.dax40DayPct >= 0 ? '+' : ''}${fmt(europeanTape.dax40DayPct)}%` : '—'}
            {arrow(europeanTape?.dax40DayPct ?? null)}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">20d corr (SX5E)</span>
          <span className="tile-val mono">{fmt(europeanTape?.ftseSx5eCorr20d ?? null, 2)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">20d corr (DAX)</span>
          <span className="tile-val mono">{fmt(europeanTape?.ftseDaxCorr20d ?? null, 2)}</span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Tape agreement</span>
          <span className="tile-val mono">
            {europeanTape?.tapeAgreement && (
              <span className={`badge ${agreementBadge(europeanTape.tapeAgreement)} ${styles.badgeInline}`}>{europeanTape.tapeAgreement}</span>
            )}
          </span>
        </div>
        {europeanTape?.preOpenLead && europeanTape.preOpenLead !== 'NONE' && (
          <div className="tile-row">
            <span className="tile-label">Pre-open lead</span>
            <span className={`tile-val mono ${europeanTape.preOpenLead === 'UP' ? 'up' : 'down'}`}>
              {europeanTape.preOpenLead}
            </span>
          </div>
        )}
      </div>

      <div className="tile-row" style={{ marginTop: 4 }}>
        <span style={{ fontSize: 10, color: 'var(--text-dim)' }}>Euro Stoxx 50 is the primary read (tied-best measured correlate); DAX confirms or flags a split tape</span>
      </div>

      {!europeanTape && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainEuropeanTape(europeanTape)} />
    </div>
  )
}
