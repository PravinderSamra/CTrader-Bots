import type { OrbPlaybook } from '../../types/uk100'
import styles from './OrbPlaybookCard.module.css'

function pillClass(direction: OrbPlaybook['direction']): string {
  if (direction === 'LONG_ONLY') return styles.pillLong
  if (direction === 'SHORT_ONLY') return styles.pillShort
  if (direction === 'BOTH_OK') return styles.pillBoth
  return styles.pillStand
}

function pillLabel(direction: OrbPlaybook['direction']): string {
  if (direction === 'LONG_ONLY') return 'LONG ONLY'
  if (direction === 'SHORT_ONLY') return 'SHORT ONLY'
  if (direction === 'BOTH_OK') return 'BOTH OK'
  return 'STAND ASIDE'
}

interface Props { playbook: OrbPlaybook }

export function OrbPlaybookCard({ playbook }: Props) {
  return (
    <div className={styles.card}>
      <div className={styles.header}>
        <h3 className={styles.title}>ORB Playbook</h3>
        <span className={`${styles.pill} ${pillClass(playbook.direction)}`}>
          {pillLabel(playbook.direction)}
        </span>
        <span className={styles.dayType}>{playbook.dayType.replace('_', ' ')}</span>
      </div>

      <p className={styles.reasoning}>{playbook.reasoning}</p>

      {playbook.keyLevels.length > 0 && (
        <div className={styles.levelsTable}>
          {playbook.keyLevels.map((lvl, i) => (
            <div key={i} className={styles.levelRow}>
              <span className={styles.levelLabel}>{lvl.label}</span>
              <span className={styles.levelPrice}>
                {lvl.price.toLocaleString('en-US', { minimumFractionDigits: 1, maximumFractionDigits: 1 })}
              </span>
            </div>
          ))}
        </div>
      )}

      <div className={`${styles.metaLine} ${styles.invalidation}`}>
        <span className={styles.metaLabel}>Invalidation:</span>
        <span className={styles.metaValue}>{playbook.invalidation}</span>
      </div>

      {playbook.eventRisk && (
        <div className={`${styles.metaLine} ${styles.eventRisk}`}>
          <span className={styles.metaLabel}>Event risk:</span>
          <span className={styles.metaValue}>{playbook.eventRisk}</span>
        </div>
      )}
    </div>
  )
}
