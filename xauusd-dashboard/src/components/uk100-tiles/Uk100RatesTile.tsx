import type { UkRatesBlock } from '../../types/uk100'
import styles from '../tiles/Tile.module.css'

function fmt(v: number | null, dp = 2): string {
  if (v == null) return '—'
  return v.toFixed(dp)
}
function bpFmt(v: number | null): string {
  if (v == null) return '—'
  return `${v >= 0 ? '+' : ''}${v}bp`
}
function bpCls(v: number | null): string {
  if (v == null) return 'flat'
  return v > 0 ? 'down' : v < 0 ? 'up' : 'flat'  // rising yields = headwind for FTSE
}

interface Props { rates: UkRatesBlock | null }

export function Uk100RatesTile({ rates }: Props) {
  return (
    <div className="tile">
      <div className="tile-eyebrow">UK Rates &amp; Gilts</div>

      <div className={styles.rows}>
        <div className="tile-row">
          <span className="tile-label">Bank Rate</span>
          <span className="tile-val mono">{fmt(rates?.bankRate ?? null, 2)}%</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">SONIA</span>
          <span className="tile-val mono">{fmt(rates?.sonia ?? null, 2)}%</span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">5Y Gilt</span>
          <span className="tile-val mono">{fmt(rates?.gilt5y ?? null, 2)}%</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">10Y Gilt</span>
          <span className={`tile-val mono ${bpCls(rates?.gilt10yDayBp ?? null)}`}>
            {fmt(rates?.gilt10y ?? null, 2)}% ({bpFmt(rates?.gilt10yDayBp ?? null)})
          </span>
        </div>
        <div className="tile-row">
          <span className="tile-label">20Y Gilt</span>
          <span className={`tile-val mono ${bpCls(rates?.gilt20yDayBp ?? null)}`}>
            {fmt(rates?.gilt20y ?? null, 2)}% ({bpFmt(rates?.gilt20yDayBp ?? null)})
          </span>
        </div>
        <hr className="tile-divider" />
        <div className="tile-row">
          <span className="tile-label">5s20s Slope</span>
          <span className="tile-val mono">{fmt(rates?.slope5s20s ?? null, 2)}%</span>
        </div>
        <div className="tile-row">
          <span className="tile-label">Next MPC</span>
          <span className="tile-val mono">
            {rates?.nextMpcDate ?? '—'}
            {rates?.daysToMpc != null && ` (${rates.daysToMpc}d)`}
          </span>
        </div>
      </div>

      {rates?.longEndStress && (
        <div className={styles.cautionBanner}>
          Long-end gilt stress — fiscal-risk sell-off overriding normal rate/rotation logic.
        </div>
      )}

      {!rates && (
        <div className="data-null">Snapshot not yet generated — run GitHub Action</div>
      )}
    </div>
  )
}
