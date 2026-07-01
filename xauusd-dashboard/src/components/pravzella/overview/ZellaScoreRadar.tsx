import type { TradeMetrics } from '../../../types/trades'
import styles from './ZellaScoreRadar.module.css'

const SIZE = 260
const CENTER = SIZE / 2
const MAX_R = 78

const AXES: { key: keyof TradeMetrics['zellaBreakdown']; label: string }[] = [
  { key: 'winRate', label: 'Win %' },
  { key: 'profitFactor', label: 'Profit factor' },
  { key: 'avgWinLoss', label: 'Avg win/loss' },
  { key: 'consistency', label: 'Consistency' },
  { key: 'maxDrawdown', label: 'Max drawdown' },
]

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n))
}

function point(angleDeg: number, r: number): [number, number] {
  const rad = (angleDeg - 90) * (Math.PI / 180)
  return [CENTER + r * Math.cos(rad), CENTER + r * Math.sin(rad)]
}

interface Props {
  breakdown: TradeMetrics['zellaBreakdown']
  score: number
}

export function ZellaScoreRadar({ breakdown, score }: Props) {
  const n = AXES.length
  const step = 360 / n

  const rings = [0.25, 0.5, 0.75, 1].map(frac =>
    AXES.map((_, i) => point(i * step, MAX_R * frac).join(',')).join(' '),
  )

  const dataPoints = AXES
    .map((a, i) => point(i * step, (clamp(breakdown[a.key], 0, 100) / 100) * MAX_R).join(','))
    .join(' ')

  return (
    <div className={styles.wrap}>
      <svg width={SIZE} height={SIZE} viewBox={`0 0 ${SIZE} ${SIZE}`} style={{ overflow: 'visible' }}>
        {rings.map((pts, i) => (
          <polygon key={i} points={pts} className={styles.ring} />
        ))}
        {AXES.map((a, i) => {
          const [x, y] = point(i * step, MAX_R)
          return <line key={a.key} x1={CENTER} y1={CENTER} x2={x} y2={y} className={styles.spoke} />
        })}
        <polygon points={dataPoints} className={styles.data} />
        {AXES.map((a, i) => {
          const [x, y] = point(i * step, MAX_R + 26)
          return (
            <text key={a.key} x={x} y={y} className={styles.axisLabel} textAnchor="middle" dominantBaseline="middle">
              {a.label}
            </text>
          )
        })}
      </svg>
      <div className={styles.scoreWrap}>
        <span className={styles.scoreLabel}>Your Zella Score</span>
        <span className={styles.scoreValue}>{score.toFixed(2)}</span>
      </div>
    </div>
  )
}
