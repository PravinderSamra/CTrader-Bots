import type { CTraderPrices, MarketVolatility } from '../../types/dashboard'
import styles from './Tile.module.css'

function fmt(v: number, dp = 2): string {
  if (!v && v !== 0) return '—'
  return v.toFixed(dp)
}
function arrow(v: number): string {
  if (v > 0.05) return ' ▲'
  if (v < -0.05) return ' ▼'
  return ' →'
}
function cls(v: number): string {
  if (v > 0.05) return 'up'
  if (v < -0.05) return 'down'
  return 'flat'
}

interface Props {
  prices: CTraderPrices
  vix: number | null
  riskTone: MarketVolatility['riskTone']
}

export function EquitiesTile({ prices, vix, riskTone }: Props) {
  const isLive = prices.status === 'live'

  const tone = riskTone ?? 'NEUTRAL'
  const toneBadge = tone === 'RISK_OFF'
    ? 'badge-red'
    : tone === 'RISK_ON'
    ? 'badge-green'
    : 'badge-muted'
  const toneLabel = tone === 'RISK_OFF' ? 'RISK-OFF' : tone === 'RISK_ON' ? 'RISK-ON' : 'NEUTRAL'

  const vixCtx = vix == null ? null : vix > 25 ? 'ELEVATED' : vix > 15 ? 'NORMAL' : 'CALM'
  const vixCls = vix == null ? 'flat' : vix > 25 ? 'down' : vix > 15 ? 'flat' : 'up'

  return (
    <div className="tile">
      <div className="tile-eyebrow">Risk Tone</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">US500</span>
          <span className={`tile-val mono ${isLive ? cls(prices.US500.changePct) : 'flat'}`}>
            {isLive
              ? `${prices.US500.changePct >= 0 ? '+' : ''}${fmt(prices.US500.changePct)}%${arrow(prices.US500.changePct)}`
              : prices.US500.price ? prices.US500.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '—'}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">GER40</span>
          <span className={`tile-val mono ${isLive ? cls(prices.GER40.changePct) : 'flat'}`}>
            {isLive
              ? `${prices.GER40.changePct >= 0 ? '+' : ''}${fmt(prices.GER40.changePct)}%${arrow(prices.GER40.changePct)}`
              : prices.GER40.price ? prices.GER40.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '—'}
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">UK100</span>
          <span className={`tile-val mono ${isLive ? cls(prices.UK100.changePct) : 'flat'}`}>
            {isLive
              ? `${prices.UK100.changePct >= 0 ? '+' : ''}${fmt(prices.UK100.changePct)}%${arrow(prices.UK100.changePct)}`
              : prices.UK100.price ? prices.UK100.price.toLocaleString('en-US', { maximumFractionDigits: 0 }) : '—'}
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">VIX</span>
          <span className={`tile-val mono ${vixCls}`}>
            {vix != null ? `${fmt(vix, 1)}` : '—'}
            {vixCtx && <span className={`badge badge-muted ${styles.badgeInline}`}>{vixCtx}</span>}
          </span>
        </div>
      </div>

      <hr className="tile-divider" />
      <div className="tile-row">
        <span className="tile-label">Tone</span>
        <span className={`badge ${toneBadge}`}>{toneLabel}</span>
      </div>

      {prices.status === 'offline' && (
        <div className="data-null badge badge-muted" style={{ marginTop: 4 }}>CTrader offline</div>
      )}
    </div>
  )
}
