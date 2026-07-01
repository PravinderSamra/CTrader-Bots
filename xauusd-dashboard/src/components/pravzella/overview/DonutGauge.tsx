import styles from './DonutGauge.module.css'

interface Segment {
  value: number
  color: string
}

interface Props {
  segments: Segment[]
  sizePx?: number
  thickness?: number
}

export function DonutGauge({ segments, sizePx = 60, thickness = 8 }: Props) {
  const total = segments.reduce((s, seg) => s + seg.value, 0)
  let cursor = 0
  const stops = total > 0
    ? segments.map(seg => {
        const start = (cursor / total) * 360
        cursor += seg.value
        const end = (cursor / total) * 360
        return `${seg.color} ${start}deg ${end}deg`
      })
    : ['var(--border) 0deg 360deg']

  return (
    <div
      className={styles.donut}
      style={{ width: sizePx, height: sizePx, background: `conic-gradient(${stops.join(', ')})` }}
    >
      <div className={styles.hole} style={{ inset: thickness }} />
    </div>
  )
}
