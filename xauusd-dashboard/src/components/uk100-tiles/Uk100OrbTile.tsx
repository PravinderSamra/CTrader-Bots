import type { OrbContext } from '../../types/uk100'
import styles from '../tiles/Tile.module.css'

function fmt(v: number | null, dp = 1): string {
  if (v == null) return '—'
  return v.toFixed(dp)
}
function modeBadge(mode: string): string {
  if (mode === 'ORB_FORMING') return 'badge-gold'
  if (mode === 'POST_ORB') return 'badge-green'
  if (mode === 'PRE_OPEN') return 'badge-muted'
  return 'badge-muted'
}
function brokenBadge(dir: string | null): string {
  if (dir === 'UP') return 'badge-green'
  if (dir === 'DOWN') return 'badge-red'
  return 'badge-muted'
}

interface Props { orb: OrbContext | null }

export function Uk100OrbTile({ orb }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">15M Opening Range (ORB)</div>

      <div className="tile-row" style={{ marginBottom: 6 }}>
        {orb?.mode && <span className={`badge ${modeBadge(orb.mode)}`}>{orb.mode.replace('_', ' ')}</span>}
        <span className="tile-label" style={{ marginLeft: 8 }}>Cash open {orb?.cashOpenLondon ?? '—'}</span>
      </div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">ORB High / Low</span>
          <span className="tile-val mono">{fmt(orb?.orbHigh ?? null)} / {fmt(orb?.orbLow ?? null)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Broken</span>
          <span className={`badge ${brokenBadge(orb?.orbBrokenDirection ?? null)}`}>
            {orb?.orbBrokenDirection ?? '—'}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Overnight H/L</span>
          <span className="tile-val mono">{fmt(orb?.overnightHigh ?? null)} / {fmt(orb?.overnightLow ?? null)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Prior Day H/L</span>
          <span className="tile-val mono">{fmt(orb?.priorDayHigh ?? null)} / {fmt(orb?.priorDayLow ?? null)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Prior Close</span>
          <span className="tile-val mono">{fmt(orb?.priorClose ?? null)}</span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">Gap</span>
          <span className={`tile-val mono ${orb?.gapPts != null ? (orb.gapPts > 0 ? 'up' : orb.gapPts < 0 ? 'down' : 'flat') : 'flat'}`}>
            {orb?.gapPts != null ? `${orb.gapPts >= 0 ? '+' : ''}${fmt(orb.gapPts)}pts` : '—'}
            {orb?.gapPct != null && ` (${orb.gapPct >= 0 ? '+' : ''}${fmt(orb.gapPct, 2)}%)`}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">ADR14 / Used</span>
          <span className="tile-val mono">
            {fmt(orb?.adr14 ?? null)}pts
            {orb?.adrUsedPct != null && ` · ${orb.adrUsedPct}% used`}
          </span>
        </div>
      </div>

      {(orb?.eventWindows.length ?? 0) > 0 && (
        <div className={styles.cautionBanner}>
          {orb!.eventWindows.map(e => `${e.event} @ ${e.timeLondon}`).join(' · ')}
        </div>
      )}

      {!orb && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}
    </div>
  )
}
