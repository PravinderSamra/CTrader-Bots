import { useId } from 'react'

interface Props {
  data: (number | null)[]   // chronological; nulls are skipped
  width?: number
  height?: number
  /** Colour by net change of the series (up = green). Set false for a neutral gold line. */
  signed?: boolean
  ariaLabel?: string
}

/**
 * Tiny single-series sparkline — 2px line, faint area fill, emphasised endpoint
 * dot. Colour reflects the series' own net change over the window (domain
 * convention: up = green, down = red). Uses the dashboard's design tokens.
 */
export function SparkLine({ data, width = 120, height = 28, signed = true, ariaLabel }: Props) {
  const gradId = useId()
  const pts = data
    .map((v, i) => ({ v, i }))
    .filter((p): p is { v: number; i: number } => p.v != null && Number.isFinite(p.v))

  if (pts.length < 2) {
    return <svg width={width} height={height} role="img" aria-label={ariaLabel} />
  }

  const values = pts.map(p => p.v)
  const min = Math.min(...values)
  const max = Math.max(...values)
  const span = max - min || 1
  const pad = 3
  const n = data.length - 1

  const x = (i: number) => (n === 0 ? 0 : (i / n) * (width - 2) + 1)
  const y = (v: number) => height - pad - ((v - min) / span) * (height - pad * 2)

  const first = values[0]
  const last  = values[values.length - 1]
  const color = !signed
    ? 'var(--gold)'
    : last > first ? 'var(--green)'
    : last < first ? 'var(--red)'
    : 'var(--text-dim)'

  const line = pts.map((p, k) => `${k === 0 ? 'M' : 'L'} ${x(p.i).toFixed(1)} ${y(p.v).toFixed(1)}`).join(' ')
  const lastPt = pts[pts.length - 1]
  const area = `${line} L ${x(lastPt.i).toFixed(1)} ${height} L ${x(pts[0].i).toFixed(1)} ${height} Z`

  return (
    <svg width={width} height={height} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={ariaLabel} style={{ display: 'block', overflow: 'visible', color }}>
      <defs>
        <linearGradient id={gradId} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0%" stopColor="currentColor" stopOpacity="0.18" />
          <stop offset="100%" stopColor="currentColor" stopOpacity="0" />
        </linearGradient>
      </defs>
      <path d={area} fill={`url(#${gradId})`} stroke="none" />
      <path d={line} fill="none" stroke="currentColor" strokeWidth={1.5} strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={x(lastPt.i)} cy={y(lastPt.v)} r={2.5} fill="currentColor" />
    </svg>
  )
}
