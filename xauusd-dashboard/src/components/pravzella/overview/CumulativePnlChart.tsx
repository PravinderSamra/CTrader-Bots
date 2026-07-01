import { useId } from 'react'
import styles from './CumulativePnlChart.module.css'

const WIDTH = 560
const HEIGHT = 190
const PAD = 8
const PAD_BOTTOM = 20

function fmtShort(n: number): string {
  const sign = n < 0 ? '-' : ''
  const abs = Math.abs(n)
  if (abs >= 1000) return `${sign}$${(abs / 1000).toFixed(1)}k`
  return `${sign}$${abs.toFixed(0)}`
}

interface Props {
  series: { date: string; cumulative: number }[]
}

export function CumulativePnlChart({ series }: Props) {
  const clipId = useId()

  if (series.length === 0) {
    return <div className={styles.empty}>No closed trades yet</div>
  }

  const values = series.map(s => s.cumulative)
  const min = Math.min(0, ...values)
  const max = Math.max(0, ...values)
  const range = max - min || 1
  const innerW = WIDTH - PAD * 2
  const innerH = HEIGHT - PAD - PAD_BOTTOM

  const xFor = (i: number) => PAD + (series.length === 1 ? innerW / 2 : (i / (series.length - 1)) * innerW)
  const yFor = (v: number) => PAD + innerH - ((v - min) / range) * innerH
  const zeroY = yFor(0)

  const linePoints = series.map((s, i) => `${xFor(i)},${yFor(s.cumulative)}`).join(' ')
  const areaPath =
    `M ${xFor(0)},${zeroY} ` +
    series.map((s, i) => `L ${xFor(i)},${yFor(s.cumulative)}`).join(' ') +
    ` L ${xFor(series.length - 1)},${zeroY} Z`

  const first = series[0].date.slice(5)
  const last = series[series.length - 1].date.slice(5)
  const mid = series[Math.floor(series.length / 2)].date.slice(5)

  return (
    <div className={styles.wrap}>
      <svg viewBox={`0 0 ${WIDTH} ${HEIGHT}`} className={styles.svg} preserveAspectRatio="none">
        <clipPath id={`${clipId}-top`}>
          <rect x={0} y={0} width={WIDTH} height={zeroY} />
        </clipPath>
        <clipPath id={`${clipId}-bottom`}>
          <rect x={0} y={zeroY} width={WIDTH} height={HEIGHT - zeroY} />
        </clipPath>
        <line x1={PAD} y1={zeroY} x2={WIDTH - PAD} y2={zeroY} className={styles.baseline} />
        <path d={areaPath} className={styles.areaGreen} clipPath={`url(#${clipId}-top)`} />
        <path d={areaPath} className={styles.areaRed} clipPath={`url(#${clipId}-bottom)`} />
        <polyline points={linePoints} className={styles.line} />
        <text x={WIDTH - PAD - 4} y={PAD + 10} textAnchor="end" className={styles.axisLabel}>{fmtShort(max)}</text>
        <text x={WIDTH - PAD - 4} y={HEIGHT - PAD_BOTTOM - 4} textAnchor="end" className={styles.axisLabel}>{fmtShort(min)}</text>
      </svg>
      <div className={styles.axisRow}>
        <span>{first}</span>
        <span>{mid}</span>
        <span>{last}</span>
      </div>
    </div>
  )
}
