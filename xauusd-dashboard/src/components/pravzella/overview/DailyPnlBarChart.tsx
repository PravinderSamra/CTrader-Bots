import styles from './DailyPnlBarChart.module.css'

const WIDTH = 560
const HEIGHT = 190
const PAD = 8
const PAD_BOTTOM = 20

interface Props {
  series: { date: string; netPnl: number; tradeCount: number }[]
}

export function DailyPnlBarChart({ series }: Props) {
  if (series.length === 0) {
    return <div className={styles.empty}>No closed trades yet</div>
  }

  const values = series.map(s => s.netPnl)
  const min = Math.min(0, ...values)
  const max = Math.max(0, ...values)
  const range = max - min || 1
  const innerW = WIDTH - PAD * 2
  const innerH = HEIGHT - PAD - PAD_BOTTOM

  const yFor = (v: number) => PAD + innerH - ((v - min) / range) * innerH
  const zeroY = yFor(0)

  const slot = innerW / series.length
  const barGap = Math.min(4, slot * 0.2)
  const barW = Math.max(2, slot - barGap)

  const first = series[0].date.slice(5)
  const last = series[series.length - 1].date.slice(5)
  const mid = series[Math.floor(series.length / 2)].date.slice(5)

  return (
    <div className={styles.wrap}>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className={styles.svg} preserveAspectRatio="none">
        <line x1={PAD} y1={zeroY} x2={WIDTH - PAD} y2={zeroY} className={styles.baseline} />
        {series.map((s, i) => {
          const x = PAD + i * slot + barGap / 2
          const barY = s.netPnl >= 0 ? yFor(s.netPnl) : zeroY
          const h = Math.max(Math.abs(yFor(s.netPnl) - zeroY), 1)
          return (
            <rect
              key={s.date}
              x={x}
              y={barY}
              width={barW}
              height={h}
              rx={1}
              className={s.netPnl >= 0 ? styles.barPos : styles.barNeg}
            >
              <title>{`${s.date}: ${s.netPnl >= 0 ? '+' : ''}$${s.netPnl.toFixed(2)} (${s.tradeCount} trade${s.tradeCount === 1 ? '' : 's'})`}</title>
            </rect>
          )
        })}
      </svg>
      <div className={styles.axisRow}>
        <span>{first}</span>
        <span>{mid}</span>
        <span>{last}</span>
      </div>
    </div>
  )
}
