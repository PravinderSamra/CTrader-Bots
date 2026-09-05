import { useMemo, useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useGexLevels, describeFreshness, isUsCashOpen } from '../../hooks/useGexLevels'
import { LoginGate } from '../pravzella/LoginGate'
import type { GexSnapshot } from '../../types/gex'
import {
  buildLadderView, DEFAULT_WINDOW, PRIOR_LABELS, showsPriors,
  type GexReading, type PlottedRung,
} from './ladder'
import styles from './GexBotTab.module.css'

/** The NAS100 instrument. NQ_NDX is the futures-basis symbol, so its strikes
 *  already sit in futures space and line up with the CFD actually traded —
 *  cash NDX runs ~45 points low. */
const NAS100 = 'NQ_NDX'

function price(v: number): string {
  return v.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

/** Gamma spans several orders of magnitude across a ladder, so sizes are
 *  abbreviated — the comparison between bars is the point, not the digits. */
function size(v: number): string {
  const a = Math.abs(v)
  if (a >= 1_000_000) return `${(a / 1_000_000).toFixed(1)}M`
  if (a >= 1_000) return `${(a / 1_000).toFixed(1)}k`
  if (a >= 1) return a.toFixed(0)
  return a.toFixed(2)
}

function signed(v: number): string {
  const s = Math.round(v).toLocaleString('en-GB')
  return v > 0 ? `+${s}` : s
}

/** Position on the diverging axis, as a percentage. 50% is zero. */
function pct(value: number, scale: number): number {
  if (scale === 0) return 50
  return 50 + (value / scale) * 50
}

const TREND_MARK: Record<string, string> = {
  building: '▲', unwinding: '▼', flat: '',
}

function LadderRow({ rung, scale, showPriors }: {
  rung: PlottedRung
  scale: number
  showPriors: boolean
}) {
  const positive = rung.value > 0
  const raw = Math.abs(pct(rung.value, scale) - 50)
  // Only ranked walls get a minimum width. A ranked wall must always be
  // visible -- on the volume book positive gamma routinely dwarfs negative,
  // so P1 can be a sub-pixel sliver. Applying the same floor to unranked
  // strikes would inflate near-zero noise into apparent signal.
  const width = rung.value === 0 ? 0 : rung.rank ? Math.max(raw, 0.6) : raw
  const left = positive ? 50 : 50 - width

  const tip = [
    `${price(rung.strike)}`,
    `gamma ${signed(rung.value)}`,
    rung.rank ? `rank ${rung.rank}` : null,
    showPriors && rung.priors.length
      ? `was ${rung.priors.map((p, i) => `${PRIOR_LABELS[i]} ${size(p)}`).join(' · ')}`
      : null,
  ].filter(Boolean).join('\n')

  return (
    <div className={styles.row} title={tip}>
      <span className={`${styles.strike} mono`}>{price(rung.strike)}</span>

      <div className={styles.track}>
        <span className={styles.axis} aria-hidden="true" />
        <span
          className={`${styles.bar} ${positive ? styles.barPos : styles.barNeg}`}
          style={{ left: `${left}%`, width: `${width}%` }}
        />
        {/* Where this strike's gamma sat 1/5/10/15/30 minutes ago. A dot
            outside the bar's end means the wall is coming off; inside means
            it is being built. */}
        {showPriors && rung.priors.map((p, i) => (
          <span
            key={i}
            className={styles.prior}
            style={{ left: `${pct(p, scale)}%`, opacity: 0.85 - i * 0.13 }}
          />
        ))}
      </div>

      <span className={styles.meta}>
        {rung.rank && (
          <span className={rung.rank.startsWith('C') ? styles.rankC : styles.rankP}>
            {rung.rank}
          </span>
        )}
        {/* Only ranked walls get a number. A value beside every rung is noise. */}
        {rung.rank && <span className={`${styles.sizeLabel} mono`}>{size(rung.value)}</span>}
        {rung.rank && rung.trend !== 'flat' && (
          <span
            className={rung.trend === 'building' ? styles.building : styles.unwinding}
            title={rung.trend === 'building'
              ? 'Larger than 5 minutes ago — wall building'
              : 'Smaller than 5 minutes ago — wall coming off'}
          >
            {TREND_MARK[rung.trend]}
          </span>
        )}
      </span>
    </div>
  )
}

function SpotMarker({ spot, label }: { spot: number; label: string }) {
  return (
    <div className={styles.spotRow}>
      <span className={`${styles.strike} mono ${styles.spotPrice}`}>{price(spot)}</span>
      <div className={styles.spotLine}><span /></div>
      <span className={styles.spotTag}>{label}</span>
    </div>
  )
}

function Ladder({ snap, reading }: { snap: GexSnapshot; reading: GexReading }) {
  const { rows, scale } = useMemo(
    () => buildLadderView(snap, reading, DEFAULT_WINDOW),
    [snap, reading],
  )

  if (!rows.length) {
    return (
      <div className={styles.empty}>
        No ladder in this snapshot. The recorder began storing the full strike
        ladder recently — it appears after the next run.
      </div>
    )
  }

  // Spot sits between strikes; drop its marker into the right gap so distance
  // to each wall can be read straight off the column.
  const out: React.ReactNode[] = []
  rows.forEach((r, i) => {
    const next = rows[i + 1]
    out.push(
      <LadderRow
        key={r.strike}
        rung={r}
        scale={scale}
        showPriors={reading === 'vol' && showsPriors(r, scale)}
      />,
    )
    if (next && snap.spot <= r.strike && snap.spot > next.strike) {
      out.push(<SpotMarker key="spot" spot={snap.spot} label="spot" />)
    }
    if (snap.zero_gamma > 0 && next
        && snap.zero_gamma <= r.strike && snap.zero_gamma > next.strike) {
      out.push(
        <div key="zg" className={styles.zgRow}>
          <span className={`${styles.strike} mono ${styles.zgPrice}`}>{price(snap.zero_gamma)}</span>
          <div className={styles.zgLine}><span /></div>
          <span className={styles.zgTag}>zero gamma</span>
        </div>,
      )
    }
  })

  return <div className={styles.ladder}>{out}</div>
}

/** Presentation only, so it can be rendered from a fixture without auth or
 *  Firestore. GexBotContent supplies the snapshot. */
export function GexBotView({ snap, now = new Date() }: { snap: GexSnapshot; now?: Date }) {
  const [reading, setReading] = useState<GexReading>('vol')
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
              <div className={styles.toggle} role="group" aria-label="Gamma reading">
                <button
                  className={reading === 'vol' ? styles.toggleOn : styles.toggleOff}
                  onClick={() => setReading('vol')}
                >Volume</button>
                <button
                  className={reading === 'oi' ? styles.toggleOn : styles.toggleOff}
                  onClick={() => setReading('oi')}
                >Open interest</button>
              </div>
              <span className={fresh?.stale ? styles.stale : styles.fresh}>
                {snap.scope === 'zero' ? '0DTE' : snap.scope} · {fresh?.label}
              </span>
            </div>
          </div>

          {fresh?.stale && (
            <div className={styles.staleBanner}>
              <strong>Not live.</strong>{' '}
              {marketOpen
                ? 'The US session is open, so the recorder may have stopped — check the workflow before trading these.'
                : 'The US cash session is closed; GexBot repeats its last reading until it reopens.'}
            </div>
          )}

          <div className={styles.regimeRow}>
            <span className={styles.regimeItem}>
              <span className={styles.regimeKey}>Net GEX {reading === 'vol' ? 'vol' : 'OI'}</span>
              <span className={`${styles.regimeVal} mono ${
                (reading === 'vol' ? snap.sum_gex_vol : snap.sum_gex_oi) > 0 ? styles.pos : styles.neg
              }`}>
                {signed(reading === 'vol' ? snap.sum_gex_vol : snap.sum_gex_oi)}
              </span>
            </span>
            <span className={styles.regimeItem}>
              <span className={styles.regimeKey}>Zero gamma</span>
              <span className={`${styles.regimeVal} mono`}>
                {snap.zero_gamma > 0 ? price(snap.zero_gamma) : '—'}
              </span>
            </span>
            {reading === 'vol' && (
              <span className={styles.legend}>
                <span className={styles.legendDot} /> gamma 1 · 5 · 10 · 15 · 30 min ago
              </span>
            )}
          </div>

          <Ladder snap={snap} reading={reading} />

          <p className={styles.note}>
            Bars are gamma per strike — <strong>green right</strong> positive,{' '}
            <strong>red left</strong> negative — ranked <strong>C1…C5</strong> and{' '}
            <strong>P1…P5</strong> by size. On the volume reading, dots mark where each
            strike sat 1 to 30 minutes ago: dots outside the bar mean the wall is
            coming off, inside means it is building; the arrow compares against
            the 5-minute sample. Open interest carries no priors,
            so dots are hidden there rather than borrowed from the volume series.
          </p>
        </>
  )
}

function GexBotContent() {
  const { user } = useAuth()
  const { snapshots, loading, error } = useGexLevels(user)
  const snap = snapshots.find(s => s.ticker === NAS100) ?? null

  return (
    <div className={styles.wrap}>
      {error && <div className={styles.errorBanner}>Failed to load levels: {error}</div>}

      {loading && <div className={styles.empty}>Loading ladder…</div>}

      {!loading && !snap && !error && (
        <div className={styles.empty}>
          No {NAS100} levels recorded yet. They appear once the{' '}
          <code>Record GexBot snapshots</code> workflow has run.
        </div>
      )}

      {snap && <GexBotView snap={snap} />}
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
