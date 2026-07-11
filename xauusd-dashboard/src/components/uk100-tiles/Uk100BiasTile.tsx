import type { BiasBlock } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainBias } from './explainers'
import styles from '../tiles/Tile.module.css'

function labelBadge(label: string): string {
  if (label === 'BULLISH') return 'badge-green'
  if (label === 'BEARISH') return 'badge-red'
  return 'badge-muted'
}
function convictionBadge(conviction: string): string {
  if (conviction === 'HIGH') return 'badge-gold'
  if (conviction === 'MEDIUM') return 'badge-amber'
  return 'badge-muted'
}
function driverImpactCls(impact: string): string {
  if (impact === 'BULLISH') return 'up'
  if (impact === 'BEARISH') return 'down'
  return 'flat'
}

interface Props { bias: BiasBlock | null }

export function Uk100BiasTile({ bias }: Props) {
  const score = bias?.score ?? 0
  const maxAbs = 10
  const pct = Math.min(100, (Math.abs(score) / maxAbs) * 100)

  return (
    <div className="tile">
      <div className="tile-eyebrow">UK100 Regime &amp; Bias</div>

      <div className="tile-row" style={{ alignItems: 'baseline', gap: 10 }}>
        <span className="tile-headline">{score >= 0 ? '+' : ''}{score.toFixed(1)}</span>
        {bias?.label && <span className={`badge ${labelBadge(bias.label)}`}>{bias.label}</span>}
        {bias?.conviction && <span className={`badge ${convictionBadge(bias.conviction)}`}>{bias.conviction}</span>}
      </div>

      <div className={styles.barOuter} style={{ marginTop: 6, marginBottom: 8 }}>
        <div
          className={styles.barInner}
          style={{
            width: `${pct}%`,
            background: score > 0 ? 'var(--green)' : score < 0 ? 'var(--red)' : 'var(--text-dim)',
            marginLeft: score < 0 ? `${100 - pct}%` : 0,
          }}
        />
      </div>

      {bias?.eventSuppressed && (
        <div className={styles.cautionBanner}>Event-suppressed — a HIGH-impact release nearby is muting conviction.</div>
      )}

      <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginTop: 4 }}>
        {(bias?.drivers ?? []).map((d, i) => (
          <div key={i} className="tile-row">
            <span className="tile-label" style={{ flex: 1 }}>{d.name}</span>
            <span className={`tile-val mono ${driverImpactCls(d.impact)}`} style={{ fontSize: 10 }}>
              w{d.weight} · {d.impact}
            </span>
          </div>
        ))}
      </div>

      {!bias && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainBias(bias)} />
    </div>
  )
}
