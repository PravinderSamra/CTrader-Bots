import type { OrbContext, OrbIntel, OrbIntelSignal, OrbIntelStance } from '../../types/uk100'
import { TileExplainer } from './TileExplainer'
import { explainOrb } from './explainers'
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
function stanceBadge(stance: OrbIntelStance): string {
  if (stance === 'LONG_FAVOURED') return 'badge-green'
  if (stance === 'SHORT_FAVOURED') return 'badge-red'
  if (stance === 'FADE_FAVOURED' || stance === 'BREAKOUTS_SUSPECT') return 'badge-amber'
  return 'badge-muted'
}
function stanceLabel(stance: OrbIntelStance): string {
  return stance.replace(/_/g, ' ')
}
// Colour the signal text by direction — reuses the global up/down/flat classes.
function signalTextClass(dir: OrbIntelSignal['direction']): string {
  if (dir === 'FAVOURS_LONG') return 'up'
  if (dir === 'FAVOURS_SHORT') return 'down'
  return 'flat'
}

interface Props { orb: OrbContext | null; intel?: OrbIntel | null }

export function Uk100OrbTile({ orb, intel }: Props) {
  const stanceLine = intel ? (intel.aiStanceLine ?? intel.stanceLine) : null

  return (
    <div className="tile">
      <div className="tile-eyebrow">15M Opening Range (ORB)</div>

      <div className="tile-row" style={{ marginBottom: 6 }}>
        {orb?.mode && <span className={`badge ${modeBadge(orb.mode)}`}>{orb.mode.replace('_', ' ')}</span>}
        <span className="tile-label" style={{ marginLeft: 8 }}>Cash open {orb?.cashOpenLondon ?? '—'}</span>
      </div>

      {/* ── Intel layer (G1) ── */}
      {intel && (
        <>
          <div className={styles.stanceBanner}>
            <span className={`badge ${stanceBadge(intel.stance)}`}>{stanceLabel(intel.stance)}</span>
            {stanceLine && <span className={styles.stanceLine}>{stanceLine}</span>}
          </div>

          {(intel.signals.length > 0 || intel.aiBullets.length > 0) && (
            <div className={styles.signalList}>
              {intel.signals.map((s, i) => (
                <div key={`s${i}`} className={styles.signalRow}>
                  <span className={`${styles.sourceChip} ${s.severity === 'STRONG' ? styles.sourceChipStrong : ''}`}>{s.source}</span>
                  <span className={`${styles.signalText} ${signalTextClass(s.direction)}`}>{s.text}</span>
                </div>
              ))}
              {intel.aiBullets.map((b, i) => (
                <div key={`ai${i}`} className={styles.signalRow}>
                  <span className={`${styles.sourceChip} ${styles.sourceChipAi}`}>AI</span>
                  <span className={styles.signalText}>{b}</span>
                </div>
              ))}
            </div>
          )}

          {intel.baseRateNote && (
            <div className="tile-row">
              <span className="tile-label" style={{ fontSize: 10 }}>{intel.baseRateNote}</span>
            </div>
          )}
        </>
      )}

      {/* ── Range numbers demoted into a collapsible (intel is primary) ── */}
      <details className={styles.rangeDetails}>
        <summary>Range numbers</summary>
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
            <span className="tile-label">Prior Week H/L</span>
            <span className="tile-val mono">{fmt(orb?.prevWeekHigh ?? null)} / {fmt(orb?.prevWeekLow ?? null)}</span>
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
      </details>

      {(orb?.eventWindows.length ?? 0) > 0 && (
        <div className={styles.cautionBanner} style={{ marginTop: 6 }}>
          {orb!.eventWindows.map(e => `${e.event} @ ${e.timeLondon}`).join(' · ')}
        </div>
      )}

      {!orb && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}

      <TileExplainer text={explainOrb(orb)} />
    </div>
  )
}
