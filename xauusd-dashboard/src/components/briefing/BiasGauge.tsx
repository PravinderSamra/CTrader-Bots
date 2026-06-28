import styles from './BiasGauge.module.css'

interface Props {
  score: number       // -5 to +5
  label: 'BEARISH' | 'NEUTRAL' | 'BULLISH'
  confidence: number  // 1–10
}

export function BiasGauge({ score, label, confidence }: Props) {
  // Map -5…+5 to 0…100%
  const pct = ((score + 5) / 10) * 100

  const scoreColour = score < -1
    ? 'var(--red)'
    : score > 1
    ? 'var(--green)'
    : 'var(--text-muted)'

  const labelCls = score < -1 ? styles.bearish : score > 1 ? styles.bullish : styles.neutral

  return (
    <div className={styles.gauge}>
      <div className={styles.track}>
        {/* Colour gradient: red → grey → green */}
        <div className={styles.gradient} />
        {/* Gold indicator dot */}
        <div
          className={styles.dot}
          style={{ left: `clamp(6px, calc(${pct}% - 6px), calc(100% - 6px))` }}
          title={`Bias score: ${score > 0 ? '+' : ''}${score}`}
        />
      </div>
      <div className={styles.labels}>
        <span className={styles.end} style={{ color: 'var(--red)' }}>BEARISH</span>
        <div className={styles.center}>
          <span className={`${styles.label} ${labelCls}`}>{label}</span>
          <span className={styles.score} style={{ color: scoreColour }}>
            {score > 0 ? '+' : ''}{score}/10
          </span>
          <span className={styles.conf}>confidence {confidence}/10</span>
        </div>
        <span className={styles.end} style={{ color: 'var(--green)' }}>BULLISH</span>
      </div>
    </div>
  )
}
