import type { FedExpectations } from '../../types/dashboard'
import styles from './Tile.module.css'

interface Props { fed: FedExpectations | null }

export function FedTile({ fed }: Props) {
  const cut  = fed?.probCut  ?? null
  const hold = fed?.probHold ?? null
  const hike = fed?.probHike ?? null

  const fmtDate = (iso: string | undefined) => {
    if (!iso) return '—'
    try {
      return new Date(iso).toLocaleDateString('en-GB', { day: 'numeric', month: 'short', year: 'numeric' })
    } catch { return iso }
  }

  const dominantLabel = () => {
    if (cut == null || hold == null) return null
    if (cut > hold && cut > (hike ?? 0)) return <span className="badge badge-green">DOVISH</span>
    if (hike != null && hike > hold && hike > cut) return <span className="badge badge-red">HAWKISH</span>
    return <span className="badge badge-muted">NEUTRAL</span>
  }

  return (
    <div className="tile">
      <div className="tile-eyebrow">Fed Expectations</div>

      {fed ? (
        <>
          <div className="tile-row" style={{ marginBottom: 4 }}>
            <span className="tile-label">Next FOMC</span>
            <span className="tile-val mono">{fmtDate(fed.nextMeeting)}</span>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8, marginTop: 8 }}>
            <div className={styles.probBar}>
              <span className={`${styles.probLabel} up`}>Cut</span>
              <div className={styles.probTrack}>
                <div className={styles.probFill} style={{ width: `${cut ?? 0}%`, background: 'var(--green)' }} />
              </div>
              <span className={styles.probNum}>{cut != null ? `${cut}%` : '—'}</span>
            </div>
            <div className={styles.probBar}>
              <span className={`${styles.probLabel} flat`}>Hold</span>
              <div className={styles.probTrack}>
                <div className={styles.probFill} style={{ width: `${hold ?? 0}%`, background: 'var(--text-dim)' }} />
              </div>
              <span className={styles.probNum}>{hold != null ? `${hold}%` : '—'}</span>
            </div>
            <div className={styles.probBar}>
              <span className={`${styles.probLabel} down`}>Hike</span>
              <div className={styles.probTrack}>
                <div className={styles.probFill} style={{ width: `${hike ?? 0}%`, background: 'var(--red)' }} />
              </div>
              <span className={styles.probNum}>{hike != null ? `${hike}%` : '—'}</span>
            </div>
          </div>

          <div className="tile-row" style={{ marginTop: 4 }}>
            <span className="tile-label">Market pricing</span>
            {dominantLabel()}
          </div>
        </>
      ) : (
        <div className="data-null">Snapshot not yet generated</div>
      )}
    </div>
  )
}
