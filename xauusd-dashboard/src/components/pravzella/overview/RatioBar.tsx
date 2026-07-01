import styles from './RatioBar.module.css'

interface Props {
  win: number
  loss: number
}

export function RatioBar({ win, loss }: Props) {
  const total = win + loss || 1
  const winPct = (win / total) * 100

  return (
    <div className={styles.wrap}>
      <div className={styles.track}>
        <div className={styles.win} style={{ width: `${winPct}%` }} />
        <div className={styles.loss} style={{ width: `${100 - winPct}%` }} />
      </div>
      <div className={styles.labels}>
        <span className={styles.winLabel}>${win.toFixed(0)}</span>
        <span className={styles.lossLabel}>-${loss.toFixed(0)}</span>
      </div>
    </div>
  )
}
