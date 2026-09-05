import { useMemo, useState } from 'react'
import { useAuth } from '../../hooks/useAuth'
import { useGexLevels, describeFreshness, isUsCashOpen } from '../../hooks/useGexLevels'
import { LoginGate } from '../pravzella/LoginGate'
import type { GexSnapshot } from '../../types/gex'
import { buildLadder } from './ladder'
import styles from './GexBotTab.module.css'

/** Levels are read off this screen and drawn on a chart, so they are shown at
 *  the precision GexBot sends rather than rounded to look tidy. */
function price(v: number): string {
  return v.toLocaleString('en-GB', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function signed(v: number): string {
  const s = Math.round(v).toLocaleString('en-GB')
  return v > 0 ? `+${s}` : s
}

/** Has the session traded enough for the volume reading to mean anything?
 *
 *  Every volume-derived field reads 0 until the US cash session trades. That
 *  is absence, not a flat regime, and the two are worth distinguishing: the
 *  recorder's `regimes_agree` compares signs, so a missing volume reading
 *  (sign 0) against any OI reading looks like disagreement. Flagging that as
 *  a conflict would cry wolf on every pre-open card and devalue the badge on
 *  the cards where the readings genuinely do conflict. */
function hasVolumeReading(snap: GexSnapshot): boolean {
  return snap.sum_gex_vol !== 0 || snap.major_pos_vol > 0 || snap.major_neg_vol > 0
}

function RegimeBadge({ snap }: { snap: GexSnapshot }) {
  const volLive = hasVolumeReading(snap)
  const word = (n: number) => (n > 0 ? 'positive' : n < 0 ? 'negative' : 'flat')
  const tone = (n: number) => (n > 0 ? styles.pos : n < 0 ? styles.neg : styles.flat)

  // Only a genuine conflict counts: both readings present, opposite signs.
  const conflict = volLive && !snap.regimes_agree

  return (
    <div className={styles.regimeRow}>
      <span className={styles.regimeItem}>
        <span className={styles.regimeKey}>Net GEX vol</span>
        {volLive ? (
          <span className={`${styles.regimeVal} mono ${tone(snap.regime_vol)}`}>
            {signed(snap.sum_gex_vol)} <em>{word(snap.regime_vol)}</em>
          </span>
        ) : (
          <span className={`${styles.regimeVal} ${styles.awaiting}`}>
            awaiting session
          </span>
        )}
      </span>
      <span className={styles.regimeItem}>
        <span className={styles.regimeKey}>Net GEX OI</span>
        <span className={`${styles.regimeVal} mono ${tone(snap.regime_oi)}`}>
          {signed(snap.sum_gex_oi)} <em>{word(snap.regime_oi)}</em>
        </span>
      </span>
      {conflict && (
        <span className={styles.disagree} title="The two readings imply opposite regimes. Which one price respects is not yet established.">
          readings disagree
        </span>
      )}
    </div>
  )
}

function SymbolCard({ snap }: { snap: GexSnapshot }) {
  const ladder = useMemo(() => buildLadder(snap), [snap])
  const fresh = describeFreshness(snap.source_ts)

  return (
    <div className="tile">
      <div className={styles.cardHead}>
        <div>
          <div className="tile-eyebrow">{snap.ticker}</div>
          <div className={`${styles.spot} mono`}>{price(snap.spot)}</div>
        </div>
        <div className={styles.cardMeta}>
          <span className={styles.scope}>{snap.scope === 'zero' ? '0DTE' : snap.scope}</span>
          <span className={fresh.stale ? styles.stale : styles.fresh}>{fresh.label}</span>
        </div>
      </div>

      <RegimeBadge snap={snap} />

      <div className={styles.ladder}>
        {ladder.map((l, i) => {
          const distance = l.price - snap.spot
          return (
            <div
              key={`${l.label}-${l.reading ?? 'x'}-${i}`}
              className={`${styles.rung} ${styles[l.kind]}`}
            >
              <span className={`${styles.rungPrice} mono`}>{price(l.price)}</span>
              <span className={styles.rungLabel}>
                {l.label}
                {l.reading && <em className={styles.reading}>{l.reading === 'vol' ? 'vol' : 'OI'}</em>}
              </span>
              <span className={`${styles.rungDist} mono`}>
                {l.kind === 'spot' ? '' : signed(distance)}
              </span>
            </div>
          )
        })}
      </div>
    </div>
  )
}

function GexBotContent() {
  const { user } = useAuth()
  const { snapshots, loading, error } = useGexLevels(user)
  const [now] = useState(() => new Date())

  const marketOpen = isUsCashOpen(now)
  const oldest = snapshots.length
    ? Math.min(...snapshots.map(s => s.source_ts))
    : null
  const feedStale = oldest != null && describeFreshness(oldest, now).stale

  return (
    <div className={styles.wrap}>
      {error && (
        <div className={styles.errorBanner}>
          Failed to load levels: {error}
        </div>
      )}

      {feedStale && (
        <div className={styles.staleBanner}>
          <strong>Levels are not live.</strong>{' '}
          {marketOpen
            ? 'The US session is open, so the recorder may have stopped — check the Record GexBot snapshots workflow before trading these.'
            : 'The US cash session is closed; GexBot repeats its last reading until it reopens. These are the previous session’s levels.'}
        </div>
      )}

      {loading && <div className={styles.empty}>Loading levels…</div>}

      {!loading && snapshots.length === 0 && !error && (
        <div className={styles.empty}>
          No levels recorded yet. They appear once the{' '}
          <code>Record GexBot snapshots</code> workflow has run.
        </div>
      )}

      <div className={styles.grid}>
        {snapshots.map(s => (
          <SymbolCard key={`${s.ticker}-${s.scope}`} snap={s} />
        ))}
      </div>

      {snapshots.length > 0 && (
        <p className={styles.note}>
          Every level is shown twice — once from session <strong>volume</strong> and
          once from <strong>open interest</strong>. Which one price respects is not
          yet established, so neither is treated as authoritative here. The
          recorder is building the history needed to settle it.
        </p>
      )}
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
