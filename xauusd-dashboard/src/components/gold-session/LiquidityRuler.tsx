import type { KeyLevel } from '../../types/dashboard'
import styles from './LiquidityRuler.module.css'

interface Props {
  levels: KeyLevel[]
  current: number
}

const W = 520
const H = 340
const PAD = 22
const SPINE_X = 96          // vertical axis position
const TICK_END = SPINE_X + 14
const LABEL_X = TICK_END + 10

interface Placed {
  price: number
  kind: KeyLevel['kind']
  note?: string
  y: number       // true y for the tick
  labelY: number  // de-collided y for the text
  color: string
  dashed: boolean
  draw: boolean
  isCurrent: boolean
}

function kindColor(price: number, kind: KeyLevel['kind'], current: number): string {
  if (kind === 'DRAW') return 'var(--gold)'
  if (kind === 'INVALIDATION') return 'var(--red)'
  // Standing liquidity: above current = sell-side (red), below = buy-side (green).
  return price >= current ? 'var(--red)' : 'var(--green)'
}

export function LiquidityRuler({ levels, current }: Props) {
  // Build the value set (levels + current price) and scale it.
  const prices = [...levels.map(l => l.price), current].filter(p => Number.isFinite(p))
  if (prices.length < 2) return null

  let min = Math.min(...prices)
  let max = Math.max(...prices)
  const span0 = max - min || Math.abs(current) * 0.001 || 1
  min -= span0 * 0.08
  max += span0 * 0.08
  const span = max - min

  const y = (p: number) => PAD + ((max - p) / span) * (H - 2 * PAD)
  const curY = y(current)

  // Combined label set (levels + the current-price row) sorted high→low, then
  // de-collided together so the "PRICE NOW" gutter price never overlaps a level
  // label when price sits right on a level.
  const items: Placed[] = [
    ...levels.map(l => ({
      price: l.price, kind: l.kind, note: l.note,
      y: y(l.price), labelY: y(l.price),
      color: kindColor(l.price, l.kind, current),
      dashed: l.kind === 'INVALIDATION',
      draw: l.kind === 'DRAW',
      isCurrent: false,
    })),
    { price: current, kind: 'OTHER' as KeyLevel['kind'], y: curY, labelY: curY, color: 'var(--gold)', dashed: false, draw: false, isCurrent: true },
  ].sort((a, b) => a.y - b.y)

  const MIN_GAP = 18
  for (let i = 1; i < items.length; i++) {
    if (items[i].labelY - items[i - 1].labelY < MIN_GAP) {
      items[i].labelY = items[i - 1].labelY + MIN_GAP
    }
  }
  const placed = items.filter(it => !it.isCurrent)
  const curLabelY = items.find(it => it.isCurrent)!.labelY

  const fmtPrice = (p: number) => p.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })

  return (
    <div className={styles.card}>
      <h3 className={styles.title}>Liquidity Map</h3>
      <svg viewBox={`0 0 ${W} ${H}`} className={styles.svg} role="img" aria-label="Liquidity level map">
        {/* Spine */}
        <line x1={SPINE_X} y1={PAD} x2={SPINE_X} y2={H - PAD} className={styles.spine} />

        {/* Current price band + line (full width, gold) */}
        <line x1={SPINE_X - 8} y1={curY} x2={W - 8} y2={curY} className={styles.currentLine} />
        <circle cx={SPINE_X} cy={curY} r={4} className={styles.currentDot} />
        {Math.abs(curLabelY - curY) > 1 && (
          <line x1={SPINE_X - 4} y1={curY} x2={SPINE_X - 10} y2={curLabelY} stroke="var(--gold)" strokeWidth={1} opacity={0.5} />
        )}
        <text x={SPINE_X - 12} y={curLabelY + 3} className={styles.currentPrice}>{fmtPrice(current)}</text>
        <text x={W - 8} y={curY - 6} className={styles.currentTag}>PRICE NOW</text>

        {/* Levels */}
        {placed.map((p, i) => {
          const leader = Math.abs(p.labelY - p.y) > 1
          return (
            <g key={i} style={{ color: p.color }}>
              {/* tick */}
              <line
                x1={SPINE_X} y1={p.y} x2={TICK_END} y2={p.y}
                stroke="currentColor" strokeWidth={2}
                strokeDasharray={p.dashed ? '3 3' : undefined}
              />
              {p.draw && <circle cx={SPINE_X} cy={p.y} r={4} fill="none" stroke="currentColor" strokeWidth={2} className={styles.drawPulse} />}
              {/* leader from tick to nudged label */}
              {leader && (
                <line x1={TICK_END} y1={p.y} x2={LABEL_X - 4} y2={p.labelY} stroke="currentColor" strokeWidth={1} opacity={0.4} />
              )}
              {/* price on the gutter */}
              <text x={SPINE_X - 12} y={p.labelY + 3} className={styles.gutterPrice} style={{ fill: p.color }}>
                {fmtPrice(p.price)}
              </text>
              {/* kind + note */}
              <text x={LABEL_X} y={p.labelY + 3} className={styles.levelLabel}>
                <tspan className={styles.kind} style={{ fill: p.color }}>{p.kind.replace(/_/g, ' ')}</tspan>
                {p.note && <tspan className={styles.note} dx={8}>{p.note}</tspan>}
              </text>
            </g>
          )
        })}
      </svg>
    </div>
  )
}
