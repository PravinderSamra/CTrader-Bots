import { Uk100FxBlock } from '../../types/uk100'
import { formatPrice } from '../../utils/format'
import styles from '../tiles/Tile.module.css'

interface Props {
  fx: Uk100FxBlock | null
}

export function Uk100FxTile({ fx }: Props) {
  if (!fx) return <div className={styles.tile}>FX data unavailable</div>

  return (
    <div className={styles.tile}>
      <h3 className={styles.tileTitle}>Sterling & FX</h3>

      <div className={styles.tileRow}>
        <div className={styles.tileLabel}>GBPUSD</div>
        <div className={styles.tileValue}>
          {fx.gbpusd ? formatPrice(fx.gbpusd, 4) : '—'}
        </div>
        {fx.gbpusdDayPct !== null && (
          <div className={`${styles.tilePct} ${fx.gbpusdDayPct >= 0 ? styles.positive : styles.negative}`}>
            {fx.gbpusdDayPct >= 0 ? '+' : ''}{fx.gbpusdDayPct.toFixed(2)}%
          </div>
        )}
      </div>

      <div className={styles.tileRow}>
        <div className={styles.tileLabel}>Trend</div>
        <div className={styles.tileValue}>
          {fx.gbpusdTrend ? (
            <span className={fx.gbpusdTrend === 'UP' ? styles.positive : fx.gbpusdTrend === 'DOWN' ? styles.negative : ''}>
              {fx.gbpusdTrend}
            </span>
          ) : '—'}
        </div>
      </div>

      <div className={styles.divider} />

      <div className={styles.tileRow}>
        <div className={styles.tileLabel}>EURUSD</div>
        <div className={styles.tileValue}>
          {fx.eurusd ? formatPrice(fx.eurusd, 4) : '—'}
        </div>
        {fx.eurusdDayPct !== null && (
          <div className={`${styles.tilePct} ${fx.eurusdDayPct >= 0 ? styles.positive : styles.negative}`}>
            {fx.eurusdDayPct >= 0 ? '+' : ''}{fx.eurusdDayPct.toFixed(2)}%
          </div>
        )}
      </div>

      <div className={styles.tileNote}>
        Weak GBP bullish for UK100; strong GBP bearish
      </div>
    </div>
  )
}
