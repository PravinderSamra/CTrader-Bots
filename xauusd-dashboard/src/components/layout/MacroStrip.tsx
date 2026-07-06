import type { CTraderPrices, DailySnapshot } from '../../types/dashboard'
import styles from './MacroStrip.module.css'

function fmt(v: number, dp = 2): string {
  if (!v) return '—'
  return v.toLocaleString('en-US', { minimumFractionDigits: dp, maximumFractionDigits: dp })
}

function arrow(v: number): string {
  if (v > 0) return ' ▲'
  if (v < 0) return ' ▼'
  return ''
}

function dirClass(v: number): string {
  if (v > 0) return styles.up
  if (v < 0) return styles.down
  return ''
}

interface Props {
  prices: CTraderPrices
  snapshot: DailySnapshot | null
}

export function MacroStrip({ prices, snapshot }: Props) {
  const xau = prices.XAUUSD
  const dxy = prices.DXY
  const yields = snapshot?.yields ?? null
  const vix = snapshot?.marketVolatility?.VIX ?? null
  const gvz = snapshot?.marketVolatility?.GVZ ?? null
  const cot = snapshot?.positioning ?? null
  const riskTone = snapshot?.marketVolatility?.riskTone ?? null

  const riskCls = riskTone === 'RISK_ON' ? styles.riskOn
    : riskTone === 'RISK_OFF' ? styles.riskOff
    : styles.riskNeutral

  const cotLabel = cot?.crowding === 'CROWDED_LONG' ? 'CROWDED LONG'
    : cot?.crowding === 'CROWDED_SHORT' ? 'CROWDED SHORT'
    : cot?.cotNetLong != null ? (cot.cotNetLong > 0 ? 'NET LONG' : 'NET SHORT')
    : '—'

  const cotCls = cot?.cotNetLong != null && cot.cotNetLong > 0 ? styles.up : cot?.cotNetLong != null ? styles.down : ''

  const us10y = yields?.US10Y ?? null
  const us10yChg = yields?.dayOverDay?.US10Y ?? null

  return (
    <div className={styles.strip}>
      {/* Risk Tone */}
      <div className={styles.item}>
        <div className={styles.lbl}>Risk Tone</div>
        <div className={`${styles.val} ${riskCls}`}>
          {riskTone ? riskTone.replace('_', ' ') : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* DXY */}
      <div className={styles.item}>
        <div className={styles.lbl}>DXY</div>
        <div className={`${styles.val} ${dirClass(dxy.changeDay)}`}>
          {dxy.price ? `${fmt(dxy.price)}${arrow(dxy.changeDay)}` : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* XAUUSD */}
      <div className={styles.item}>
        <div className={styles.lbl}>XAUUSD</div>
        <div className={`${styles.val} ${dirClass(xau.changeDay)}`}>
          {xau.price ? `$${fmt(xau.price)}${arrow(xau.changeDay)}` : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* 10Y Yield */}
      <div className={styles.item}>
        <div className={styles.lbl}>10Y Yield</div>
        <div className={`${styles.val} ${dirClass(us10yChg ?? 0)}`}>
          {us10y != null ? `${us10y.toFixed(2)}%${arrow(us10yChg ?? 0)}` : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* VIX */}
      <div className={styles.item}>
        <div className={styles.lbl}>VIX</div>
        <div className={`${styles.val} ${vix != null && vix > 20 ? styles.down : ''}`}>
          {vix != null ? vix.toFixed(1) : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* GVZ */}
      <div className={styles.item}>
        <div className={styles.lbl}>GVZ</div>
        <div className={`${styles.val} ${gvz != null && gvz > 20 ? styles.down : ''}`}>
          {gvz != null ? gvz.toFixed(1) : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      {/* COT */}
      <div className={styles.item}>
        <div className={styles.lbl}>COT</div>
        <div className={`${styles.val} ${cotCls}`}>{cotLabel}</div>
      </div>
    </div>
  )
}
