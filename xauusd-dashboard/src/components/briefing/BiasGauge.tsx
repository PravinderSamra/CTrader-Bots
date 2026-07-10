import styles from './BiasGauge.module.css'

interface Props {
  score: number       // -max to +max
  label: 'BEARISH' | 'NEUTRAL' | 'BULLISH'
  confidence: number  // 1–10
  max?: number        // gauge full-scale value (default 5 — gold's -5..+5 range;
                       // UK100's mechanical bias engine uses -10..+10, pass max={10})
}

const CX = 110
const CY = 108
const R_OUTER = 94
const R_INNER = 72

function donutPath(): string {
  return [
    `M ${CX - R_OUTER} ${CY}`,
    `A ${R_OUTER} ${R_OUTER} 0 1 1 ${CX + R_OUTER} ${CY}`,
    `L ${CX + R_INNER} ${CY}`,
    `A ${R_INNER} ${R_INNER} 0 1 0 ${CX - R_INNER} ${CY}`,
    `Z`,
  ].join(' ')
}

// Compute a point on the arc at a given SVG rotation angle (0° = right, CW)
function arcPoint(cx: number, cy: number, r: number, svgAngleDeg: number): [number, number] {
  const rad = (svgAngleDeg * Math.PI) / 180
  return [cx + r * Math.cos(rad), cy + r * Math.sin(rad)]
}

// Tick mark at score positions drawn as short arcs (outer→inner)
function tickLine(score: number, max: number): string {
  // SVG angle: score=-max → 180°, score=0 → 270°, score=+max → 0°/360°
  const svgAngle = 270 + (score / max) * 90
  const [x1, y1] = arcPoint(CX, CY, R_OUTER + 4, svgAngle)
  const [x2, y2] = arcPoint(CX, CY, R_INNER - 4, svgAngle)
  return `M ${x1} ${y1} L ${x2} ${y2}`
}

export function BiasGauge({ score, label, confidence, max = 5 }: Props) {
  // SVG rotation: 0° = up (neutral), -90° = bearish (left), +90° = bullish (right)
  const needleDeg = (score / max) * 90
  const labelCls = score < -max * 0.2 ? styles.bearish : score > max * 0.2 ? styles.bullish : styles.neutral
  const scoreSign = score > 0 ? '+' : ''

  return (
    <div className={styles.gauge}>
      <svg
        viewBox="0 0 220 186"
        className={styles.svg}
        aria-label={`Bias: ${label}, score ${score > 0 ? '+' : ''}${score}`}
      >
        <defs>
          <linearGradient id="gaugeGradFill" x1="0" y1="0" x2="1" y2="0">
            <stop offset="0%"   stopColor="#E05548" />
            <stop offset="35%"  stopColor="#D49038" stopOpacity="0.75" />
            <stop offset="50%"  stopColor="#4E5268" stopOpacity="0.5" />
            <stop offset="65%"  stopColor="#D49038" stopOpacity="0.75" />
            <stop offset="100%" stopColor="#2DC57E" />
          </linearGradient>
          <clipPath id="trackClip">
            <path d={donutPath()} />
          </clipPath>
        </defs>

        {/* Track base — dim surface */}
        <path d={donutPath()} className={styles.trackBase} />

        {/* Gradient color overlay clipped to track */}
        <rect
          x={CX - R_OUTER - 2} y={CY - R_OUTER - 2}
          width={(R_OUTER + 2) * 2} height={R_OUTER + 2}
          fill="url(#gaugeGradFill)"
          clipPath="url(#trackClip)"
        />

        {/* Score ticks at -max, -0.6max, 0, +0.6max, +max */}
        {[-max, -max * 0.6, 0, max * 0.6, max].map(s => (
          <path
            key={s}
            d={tickLine(s, max)}
            className={s === 0 ? styles.tickMajor : styles.tick}
          />
        ))}

        {/* Center cap */}
        <circle cx={CX} cy={CY} r={18} className={styles.centerCap} />

        {/* Needle group — rotated around pivot */}
        <g
          className={styles.needleGroup}
          style={{
            transform: `rotate(${needleDeg}deg)`,
            transformOrigin: `${CX}px ${CY}px`,
          }}
        >
          {/* Needle shadow */}
          <line
            x1={CX} y1={CY + 10}
            x2={CX} y2={CY - 84}
            className={styles.needleShadow}
          />
          {/* Needle body */}
          <line
            x1={CX} y1={CY + 10}
            x2={CX} y2={CY - 84}
            className={styles.needle}
          />
          {/* Needle pivot dot */}
          <circle cx={CX} cy={CY} r={6} className={styles.pivotDot} />
        </g>

        {/* BEARISH / BULLISH end labels */}
        <text x={CX - R_OUTER - 2} y={CY + 18} className={styles.endLabelBear}>◂ Bear</text>
        <text x={CX + R_OUTER + 2} y={CY + 18} className={styles.endLabelBull}>Bull ▸</text>

        {/* Center: label + score */}
        <text x={CX} y={CY + 36} className={`${styles.centerLabel} ${labelCls}`}>
          {label}
        </text>
        <text x={CX} y={CY + 52}>
          <tspan className={styles.centerScore}>{scoreSign}{score}</tspan>
          <tspan className={styles.centerScoreDenom}>/10</tspan>
        </text>
        <text x={CX} y={CY + 64} className={styles.centerConf}>
          confidence {confidence}/10
        </text>
      </svg>
    </div>
  )
}
