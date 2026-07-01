import type { ReactNode } from 'react'
import styles from './StatCard.module.css'

interface Props {
  label: string
  value: string
  valueColor?: string
  badge?: string | number
  stackVisual?: boolean
  children?: ReactNode
}

export function StatCard({ label, value, valueColor, badge, stackVisual, children }: Props) {
  return (
    <div className={styles.card}>
      <div className={styles.headerRow}>
        <span className={styles.label}>{label}</span>
        {badge != null && <span className={styles.badge}>{badge}</span>}
      </div>
      {stackVisual ? (
        <div className={styles.stack}>
          <span className={styles.value} style={valueColor ? { color: valueColor } : undefined}>{value}</span>
          {children && <div className={styles.visualFull}>{children}</div>}
        </div>
      ) : (
        <div className={styles.bottomRow}>
          <span className={styles.value} style={valueColor ? { color: valueColor } : undefined}>{value}</span>
          {children && <div className={styles.visual}>{children}</div>}
        </div>
      )}
    </div>
  )
}
