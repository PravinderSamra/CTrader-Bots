import { useState } from 'react'
import { LoginGate } from '../pravzella/LoginGate'
import { useAuth } from '../../hooks/useAuth'
import { useGexLevels, describeFreshness, isUsCashOpen } from '../../hooks/useGexLevels'
import { useGexHistory } from '../../hooks/useGexHistory'
import type { GexSnapshot } from '../../types/gex'
import {
  type GexReading, buildLadderView, showsPriors, PRIOR_LABELS,
} from './ladder'
import styles from './GexBotTab.module.css'

const NAS100 = 'NQ_NDX'

// One chart, one price scale, two panels: price over time on the left, the
// strike ladder on the right. The vendor's own view overlays both on a single
// plot area with two x-axes; keeping them as adjacent panels sharing the y
// axis reads the same -- a bar still sits at its strike's height -- without
// two x-scales in one region inviting comparisons that are not meaningful.
const W = 1000, H = 560
const PAD_L = 62, PAD_T = 14, PAD_B = 26
const PRICE_X0 = PAD_L, PRICE_X1 = 600
const LAD_X0 = 620, LAD_X1 = 980
const ZERO_X = (LAD_X0 + LAD_X1) / 2
const LAD_HALF = ZERO_X - LAD_X0

function price(v: number): string {
  return v.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}
function size(v: number): string {
  const a = Math.abs(v)
  if (a >= 1e9) return `${(v / 1e9).toFixed(2)}Bn`
  if (a >= 1e6) return `${(v / 1e6).toFixed(2)}M`
  if (a >= 1e3) return `${(v / 1e3).toFixed(1)}k`
  return v.toFixed(2)
}
function clock(ts: number): string {
  return new Date(ts * 1000).toLocaleTimeString('en-GB',
    { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

/** A level to draw across the whole chart. */
interface Level {
  value: number
  label: string
  kind: 'anchor-pos' | 'anchor-neg' | 'intraday-pos' | 'intraday-neg' | 'zero'
}

/** Which levels to draw, and why each one is there.
 *
 *  The two 90-day open-interest walls are the structural anchors: recomputed
 *  once near the open and fixed for the session. The 0DTE volume walls and
 *  zero gamma move through the day. Both are shown at once deliberately --
 *  the vendor's UI toggles between scopes, but the whole point here is seeing
 *  where the fixed anchors and the live levels agree.
 */
export function levelsFor(zero: GexSnapshot | null, full: GexSnapshot | null): Level[] {
  const out: Level[] = []
  const push = (v: number | undefined, label: string, kind: Level['kind']) => {
    if (typeof v === 'number' && v > 0) out.push({ value: v, label, kind })
  }
  push(full?.major_pos_oi, '90d OI major +', 'anchor-pos')
  push(full?.major_neg_oi, '90d OI major −', 'anchor-neg')
  push(zero?.major_pos_vol, '0DTE vol major +', 'intraday-pos')
  push(zero?.major_neg_vol, '0DTE vol major −', 'intraday-neg')
  push(zero?.zero_gamma, 'zero gamma', 'zero')
  return out
}

function Chart({ snap, history, levels, reading }: {
  snap: GexSnapshot
  history: GexSnapshot[]
  levels: Level[]
  reading: GexReading
}) {
  const view = buildLadderView(snap, reading)
  const { rows, scale } = view

  const prices = [
    ...rows.map(r => r.strike),
    ...levels.map(l => l.value),
    ...history.map(h => h.spot),
    snap.spot,
  ].filter(v => v > 0)
  const lo = Math.min(...prices), hi = Math.max(...prices)
  const pad = (hi - lo) * 0.04 || 10
  const y = (p: number) =>
    PAD_T + (H - PAD_T - PAD_B) * (1 - (p - (lo - pad)) / ((hi + pad) - (lo - pad)))

  const t0 = history.length ? history[0].source_ts : 0
  const t1 = history.length ? history[history.length - 1].source_ts : 1
  const x = (ts: number) =>
    PRICE_X0 + (PRICE_X1 - PRICE_X0) * (t1 === t0 ? 1 : (ts - t0) / (t1 - t0))

  // Bar height must come from the PRICE scale, not the row count: NDX strikes
  // are 5, 10 and 25 apart, so evenly-sized rows would draw bars that do not
  // line up with where their strike actually sits on the axis.
  const gaps = rows.slice(1).map((r, i) => Math.abs(r.strike - rows[i].strike))
    .filter(g => g > 0).sort((a, b) => a - b)
  const step = gaps.length ? gaps[Math.floor(gaps.length / 2)] : 10
  const rowH = Math.max(2, Math.abs(y(lo) - y(lo + step)) - 2)
  const line = history.map(h => `${x(h.source_ts)},${y(h.spot)}`).join(' ')

  return (
    <svg className={styles.chart} viewBox={`0 0 ${W} ${H}`} role="img"
         aria-label={`${snap.ticker} gamma ladder against price`}>
      {/* ladder bars */}
      {rows.map(r => {
        const v = r.value   // already signed for the active reading
        const w = Math.abs(v) / scale * LAD_HALF
        const pos = v >= 0
        return (
          <g key={r.strike}>
            <rect
              x={pos ? ZERO_X : ZERO_X - w} y={y(r.strike) - rowH / 2}
              width={Math.max(w, 0.5)} height={rowH} rx={2}
              className={pos ? styles.barPos : styles.barNeg}
            >
              <title>{`${price(r.strike)} · ${size(v)}`}</title>
            </rect>
            {showsPriors(r, scale) && r.priors.map((p, i) => (
              <circle key={i} cx={ZERO_X + (p / scale) * LAD_HALF} cy={y(r.strike)}
                      r={2.5} className={styles.prior}>
                <title>{`${PRIOR_LABELS[i]} ago · ${size(p)}`}</title>
              </circle>
            ))}
          </g>
        )
      })}
      <line x1={ZERO_X} x2={ZERO_X} y1={PAD_T} y2={H - PAD_B} className={styles.axis} />

      {/* price series */}
      {history.length > 1 && (
        <polyline points={line} className={styles.priceLine} />
      )}

      {/* levels, drawn across both panels */}
      {levels.map(l => (
        <g key={`${l.kind}-${l.value}`}>
          <line x1={PAD_L} x2={LAD_X1} y1={y(l.value)} y2={y(l.value)}
                className={`${styles.level} ${styles[l.kind]}`} />
          <text x={PAD_L - 6} y={y(l.value) + 3} textAnchor="end"
                className={`${styles.pill} ${styles[l.kind]}`}>{price(l.value)}</text>
        </g>
      ))}

      {/* spot */}
      <line x1={PAD_L} x2={LAD_X1} y1={y(snap.spot)} y2={y(snap.spot)}
            className={styles.spotLine} />
      <text x={PAD_L - 6} y={y(snap.spot) + 3} textAnchor="end"
            className={styles.spotPill}>{price(snap.spot)}</text>

      {history.length > 1 && (
        <>
          <text x={PRICE_X0} y={H - 8} className={styles.tick}>{clock(t0)}</text>
          <text x={PRICE_X1} y={H - 8} textAnchor="end" className={styles.tick}>
            {clock(t1)}
          </text>
        </>
      )}
    </svg>
  )
}

function Block({ title, rows }: {
  title: string
  rows: { k: string; v: string; cls?: string }[]
}) {
  return (
    <div className={styles.block}>
      <div className={styles.blockTitle}>{title}</div>
      {rows.map(r => (
        <div key={r.k} className={styles.blockRow}>
          <span className={`${styles.blockKey} ${r.cls ?? ''}`}>{r.k}</span>
          <span className={`${styles.blockVal} mono`}>{r.v}</span>
        </div>
      ))}
    </div>
  )
}

export function GexBotView({ zero, full, history, now = new Date() }: {
  zero: GexSnapshot | null
  full: GexSnapshot | null
  history: GexSnapshot[]
  now?: Date
}) {
  const [scope, setScope] = useState<'zero' | 'full'>('zero')
  const [reading, setReading] = useState<GexReading>('vol')
  const snap = scope === 'zero' ? zero : full
  const levels = levelsFor(zero, full)

  if (!snap) return <div className={styles.empty}>No {scope} scope recorded yet.</div>

  const fresh = describeFreshness(snap.source_ts, now)
  const marketOpen = isUsCashOpen(now)

  return (
    <>
      <div className={styles.head}>
        <div>
          <div className="tile-eyebrow">NAS100 · {snap.ticker}</div>
          <div className={`${styles.spot} mono`}>{price(snap.spot)}</div>
        </div>
        <div className={styles.headRight}>
          <div className={styles.toggle} role="group" aria-label="Expiry scope">
            <button className={scope === 'zero' ? styles.toggleOn : styles.toggleOff}
                    onClick={() => setScope('zero')}>0DTE</button>
            <button className={scope === 'full' ? styles.toggleOn : styles.toggleOff}
                    onClick={() => setScope('full')}>90d agg</button>
          </div>
          <div className={styles.toggle} role="group" aria-label="Gamma reading">
            <button className={reading === 'vol' ? styles.toggleOn : styles.toggleOff}
                    onClick={() => setReading('vol')}>Volume</button>
            <button className={reading === 'oi' ? styles.toggleOn : styles.toggleOff}
                    onClick={() => setReading('oi')}>Open interest</button>
          </div>
          <span className={fresh.stale ? styles.stale : styles.fresh}>{fresh.label}</span>
        </div>
      </div>

      {fresh.stale && (
        <div className={styles.staleBanner}>
          <strong>Not live.</strong>{' '}
          {marketOpen
            ? 'The US session is open, so the recorder may have stopped — check the workflow before trading these.'
            : 'The US cash session is closed; GexBot repeats its last reading until it reopens.'}
        </div>
      )}

      <div className={styles.layout}>
        <Chart snap={snap} history={history} levels={levels} reading={reading} />

        <aside className={styles.panel}>
          <Block title="update" rows={[
            { k: 'time', v: clock(snap.source_ts) + ' UTC' },
            { k: 'spot', v: price(snap.spot) },
            { k: 'scope', v: scope === 'zero' ? '0DTE' : '90 day' },
          ]} />
          <Block title="volume" rows={[
            { k: 'zero gamma', v: snap.zero_gamma > 0 ? price(snap.zero_gamma) : '—', cls: styles.kZero },
            { k: 'major positive', v: price(snap.major_pos_vol), cls: styles.kPos },
            { k: 'major negative', v: price(snap.major_neg_vol), cls: styles.kNeg },
            { k: 'net gex', v: size(snap.sum_gex_vol) },
          ]} />
          <Block title="open interest" rows={[
            { k: 'major positive', v: price(snap.major_pos_oi), cls: styles.kPos },
            { k: 'major negative', v: price(snap.major_neg_oi), cls: styles.kNeg },
            { k: 'net gex', v: size(snap.sum_gex_oi) },
          ]} />
          {snap.max_priors && snap.max_priors.length > 0 && (
            <Block title="max change gex" rows={snap.max_priors.slice(0, 5).map((m, i) => ({
              k: PRIOR_LABELS[i] ?? `${i}`,
              v: `${price(m.strike)}  ${size(m.change)}`,
            }))} />
          )}
        </aside>
      </div>

      <p className={styles.note}>
        Two <strong>90-day open-interest</strong> levels are the structural
        anchors — recomputed once near the open and fixed all session. The{' '}
        <strong>0DTE volume</strong> levels and zero gamma move through the day.
        Bars are gamma per strike for the selected scope: positive right,
        negative left, so the sign is carried by direction as well as colour.
        Dots on the volume reading mark where a strike sat 1–30 minutes ago.
        A major negative sitting above a major positive is not an error — the
        vendor documents it as ITM put activity flipping the expected order.
        The price line is a 5-minute recording, not a tick chart.
      </p>
    </>
  )
}

function GexBotContent() {
  const { user } = useAuth()
  const { snapshots, loading, error } = useGexLevels(user)
  const { history } = useGexHistory(user, NAS100, 'zero')

  const zero = snapshots.find(s => s.ticker === NAS100 && s.scope === 'zero') ?? null
  const full = snapshots.find(s => s.ticker === NAS100 && s.scope === 'full') ?? null

  return (
    <div className={styles.wrap}>
      {error && <div className={styles.errorBanner}>Failed to load levels: {error}</div>}
      {loading && <div className={styles.empty}>Loading ladder…</div>}
      {!loading && !zero && !full && !error && (
        <div className={styles.empty}>
          No {NAS100} levels recorded yet. They appear once the{' '}
          <code>Record GexBot snapshots</code> workflow has run.
        </div>
      )}
      {(zero || full) && <GexBotView zero={zero} full={full} history={history} />}
    </div>
  )
}

export function GexBotTab() {
  return (
    <LoginGate>
      <GexBotContent />
    </LoginGate>
  )
}
