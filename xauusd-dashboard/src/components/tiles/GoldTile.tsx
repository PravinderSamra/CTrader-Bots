import type { CTraderPrices } from '../../types/dashboard'
import styles from './Tile.module.css'

function fmt(v: number, dp = 2): string {
  if (!v) return '—'
  return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

interface Props {
  prices: CTraderPrices
  gvz: number | null
}

export function GoldTile({ prices, gvz }: Props) {
  const isLive = prices.status === 'live'
  const xau = prices.XAUUSD
  const xag = prices.XAGUSD

  const adr = prices.ADR_14day
  const used = prices.ADR_usedToday
  const adrPct = adr && used ? Math.min(100, (used / adr) * 100) : 0

  const gvzCtx = gvz == null ? null : gvz > 25 ? 'ELEVATED' : gvz > 15 ? 'NORMAL' : 'CALM'
  const gvzCls = gvz == null ? 'flat' : gvz > 25 ? 'down' : 'flat'

  const chgCls = xau.changeDay > 0 ? 'up' : xau.changeDay < 0 ? 'down' : 'flat'

  return (
    <div className="tile">
      <div className="tile-eyebrow">Gold Panel</div>

      <div>
        <div className="tile-label" style={{ marginBottom: 4 }}>XAUUSD</div>
        <div className={`${styles.headline} ${chgCls}`}>
          {isLive ? `$${fmt(xau.price, 2)}` : '—'}
        </div>
        <div className={`${styles.change} ${chgCls}`}>
          {isLive ? `${xau.changeDay >= 0 ? '+' : ''}${fmt(xau.changeDay, 2)} (${xau.changePct >= 0 ? '+' : ''}${fmt(xau.changePct, 2)}%)` : ''}
        </div>
      </div>

      <hr className="tile-divider" />

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">XAGUSD</span>
          <span className="tile-val mono">{isLive ? `$${fmt(xag.price, 3)}` : '—'}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Au/Ag Ratio</span>
          <span className="tile-val mono">{isLive && prices.goldSilverRatio ? prices.goldSilverRatio.toFixed(1) : '—'}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">GVZ</span>
          <span className={`tile-val mono ${gvzCls}`}>
            {gvz != null ? gvz.toFixed(1) : '—'}
            {gvzCtx && <span className={`badge badge-muted ${styles.badgeInline}`}>{gvzCtx}</span>}
          </span>
        </div>
      </div>

      <hr className="tile-divider" />

      <div className="tile-row">
        <span className="tile-label">ADR (14d)</span>
        <span className="tile-val mono">{adr ? `$${adr.toFixed(0)}` : '—'}</span>
      </div>
      <div className="tile-row">
        <span className="tile-label">Used today</span>
        <span className="tile-val mono">{used ? `$${used.toFixed(0)}` : '—'}</span>
      </div>
      {adr != null && used != null && (
        <div>
          <div className={styles.barOuter}>
            <div className={styles.barInner} style={{ width: `${adrPct}%` }} />
          </div>
          <div className="tile-label" style={{ marginTop: 2 }}>
            {adrPct.toFixed(0)}% of daily range consumed
          </div>
        </div>
      )}

      {prices.status === 'offline' && (
        <div className="data-null badge badge-muted">CTrader offline</div>
      )}
    </div>
  )
}
