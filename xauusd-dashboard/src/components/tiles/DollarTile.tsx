import type { CTraderPrices } from '../../types/dashboard'
import styles from './Tile.module.css'

function fmt(v: number, dp = 3): string {
  if (!v) return '—'
  return v.toFixed(dp)
}
function arrow(v: number): string {
  if (v > 0) return ' ▲'
  if (v < 0) return ' ▼'
  return ' →'
}
function cls(v: number): string {
  if (v > 0) return 'up'
  if (v < 0) return 'down'
  return 'flat'
}

interface Props { prices: CTraderPrices }

export function DollarTile({ prices }: Props) {
  const dxy = prices.DXY
  const isLive = prices.status === 'live'

  return (
    <div className="tile">
      <div className="tile-eyebrow">Dollar &amp; FX</div>

      <div>
        <div className="tile-label" style={{ marginBottom: 4 }}>DXY</div>
        <div className={`${styles.headline} ${cls(dxy.changePct)}`}>
          {dxy.price ? fmt(dxy.price, 2) : '—'}
        </div>
        <div className={`${styles.change} ${cls(dxy.changePct)}`}>
          {isLive && dxy.changePct !== 0 ? `${arrow(dxy.changePct)} ${dxy.changePct >= 0 ? '+' : ''}${fmt(dxy.changePct, 2)}%` : ''}
        </div>
      </div>

      <hr className="tile-divider" />

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">EUR/USD</span>
          <span className="tile-val mono">{fmt(prices.EURUSD, 4)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">USD/JPY</span>
          <span className="tile-val mono">{fmt(prices.USDJPY, 2)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">USD/CHF</span>
          <span className="tile-val mono">{fmt(prices.USDCHF, 4)}</span>
        </div>
        <div className="tile-row">
          <span className="tile-label" title="China proxy">USD/CNH</span>
          <span className="tile-val mono">{fmt(prices.USDCNH, 4)}</span>
        </div>
      </div>

      {prices.status === 'offline' && (
        <div className="data-null badge badge-muted">CTrader offline</div>
      )}
    </div>
  )
}
