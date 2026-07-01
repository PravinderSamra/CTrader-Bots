import type { DailyPnl } from '../../../types/trades'
import styles from './DayDetailPanel.module.css'

function fmtMoney(n: number): string {
  const sign = n < 0 ? '-' : '+'
  return `${sign}$${Math.abs(n).toFixed(2)}`
}

function fmtTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('en-GB', { hour: '2-digit', minute: '2-digit', timeZone: 'UTC' })
}

interface Props {
  day: DailyPnl | null
}

export function DayDetailPanel({ day }: Props) {
  if (!day) {
    return (
      <aside className={styles.panel}>
        <div className={styles.empty}>Select a day with trades to see the breakdown</div>
      </aside>
    )
  }

  return (
    <aside className={styles.panel}>
      <div className={styles.header}>
        <span className={styles.date}>
          {new Date(`${day.date}T00:00:00Z`).toLocaleDateString('en-GB', { weekday: 'long', day: 'numeric', month: 'long', timeZone: 'UTC' })}
        </span>
        <span className={day.netPnl >= 0 ? styles.pnlPos : styles.pnlNeg}>{fmtMoney(day.netPnl)}</span>
      </div>
      <div className={styles.summary}>
        <span className={styles.winCount}>{day.wins} win{day.wins === 1 ? '' : 's'}</span>
        <span className={styles.lossCount}>{day.losses} loss{day.losses === 1 ? '' : 'es'}</span>
        <span className={styles.tradeCount}>{day.trades.length} trade{day.trades.length === 1 ? '' : 's'}</span>
      </div>
      <div className={styles.list}>
        {day.trades.map(t => (
          <div key={t.id} className={styles.tradeRow}>
            <div className={styles.tradeMain}>
              <span className={styles.symbol}>{t.symbol}</span>
              <span className={t.direction === 'LONG' ? styles.dirLong : styles.dirShort}>{t.direction}</span>
            </div>
            <div className={styles.tradeMeta}>
              <span>{fmtTime(t.entry_time)}–{fmtTime(t.exit_time)}</span>
              <span>{t.entry_price} → {t.exit_price}</span>
            </div>
            <span className={t.net_pnl >= 0 ? styles.pnlPos : styles.pnlNeg}>{fmtMoney(t.net_pnl)}</span>
          </div>
        ))}
      </div>
    </aside>
  )
}
