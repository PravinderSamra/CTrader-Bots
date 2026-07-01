import { useState, useMemo } from 'react'
import type { Trade } from '../../../types/trades'
import styles from './TradeLogSubTab.module.css'

type SortKey = 'exit_time' | 'symbol' | 'net_pnl'
type FilterKey = 'ALL' | 'WINS' | 'LOSSES'

function fmtDateTime(iso: string): string {
  return new Date(iso).toLocaleString('en-GB', {
    day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit', timeZone: 'UTC',
  })
}

function fmtDuration(entry: string, exit: string): string {
  const ms = new Date(exit).getTime() - new Date(entry).getTime()
  const mins = Math.round(ms / 60000)
  if (mins < 60) return `${mins}m`
  const h = Math.floor(mins / 60)
  const m = mins % 60
  return `${h}h ${m}m`
}

interface Props {
  trades: Trade[]
}

export function TradeLogSubTab({ trades }: Props) {
  const [sortKey, setSortKey] = useState<SortKey>('exit_time')
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc')
  const [filter, setFilter] = useState<FilterKey>('ALL')
  const [symbolFilter, setSymbolFilter] = useState('ALL')

  const symbols = useMemo(() => ['ALL', ...new Set(trades.map(t => t.symbol))], [trades])

  const rows = useMemo(() => {
    let filtered = trades
    if (filter === 'WINS') filtered = filtered.filter(t => t.net_pnl > 0)
    if (filter === 'LOSSES') filtered = filtered.filter(t => t.net_pnl <= 0)
    if (symbolFilter !== 'ALL') filtered = filtered.filter(t => t.symbol === symbolFilter)

    const sorted = [...filtered].sort((a, b) => {
      let cmp = 0
      if (sortKey === 'exit_time') cmp = a.exit_time.localeCompare(b.exit_time)
      else if (sortKey === 'symbol') cmp = a.symbol.localeCompare(b.symbol)
      else cmp = a.net_pnl - b.net_pnl
      return sortDir === 'asc' ? cmp : -cmp
    })
    return sorted
  }, [trades, filter, symbolFilter, sortKey, sortDir])

  function toggleSort(key: SortKey) {
    if (sortKey === key) setSortDir(d => (d === 'asc' ? 'desc' : 'asc'))
    else { setSortKey(key); setSortDir('desc') }
  }

  if (trades.length === 0) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyTitle}>No trades synced yet</div>
        <div className={styles.emptySub}>Closed trades from cTrader will appear here once the sync workflow has run.</div>
      </div>
    )
  }

  return (
    <div className={styles.tab}>
      <div className={styles.toolbar}>
        <div className={styles.filterGroup}>
          {(['ALL', 'WINS', 'LOSSES'] as const).map(f => (
            <button key={f} className={`${styles.filterBtn} ${filter === f ? styles.filterBtnActive : ''}`} onClick={() => setFilter(f)}>
              {f}
            </button>
          ))}
        </div>
        <select className={styles.symbolSelect} value={symbolFilter} onChange={e => setSymbolFilter(e.target.value)}>
          {symbols.map(s => <option key={s} value={s}>{s === 'ALL' ? 'All symbols' : s}</option>)}
        </select>
        <span className={styles.count}>{rows.length} trade{rows.length === 1 ? '' : 's'}</span>
      </div>

      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th onClick={() => toggleSort('exit_time')} className={styles.sortable}>Date{sortKey === 'exit_time' ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}</th>
              <th onClick={() => toggleSort('symbol')} className={styles.sortable}>Symbol{sortKey === 'symbol' ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}</th>
              <th>Side</th>
              <th>Entry</th>
              <th>Exit</th>
              <th>Stake (£/pt)</th>
              <th>Duration</th>
              <th onClick={() => toggleSort('net_pnl')} className={styles.sortable}>Net P&L{sortKey === 'net_pnl' ? (sortDir === 'asc' ? ' ▲' : ' ▼') : ''}</th>
            </tr>
          </thead>
          <tbody>
            {rows.map(t => (
              <tr key={t.id}>
                <td className={styles.mono}>{fmtDateTime(t.exit_time)}</td>
                <td className={styles.symbolCell}>{t.symbol}</td>
                <td>
                  <span className={t.direction === 'LONG' ? styles.dirLong : styles.dirShort}>{t.direction}</span>
                </td>
                <td className={styles.mono}>{t.entry_price}</td>
                <td className={styles.mono}>{t.exit_price}</td>
                <td className={styles.mono}>{t.volume.toFixed(2)}</td>
                <td className={styles.mono}>{fmtDuration(t.entry_time, t.exit_time)}</td>
                <td className={`${styles.mono} ${t.net_pnl >= 0 ? styles.pnlPos : styles.pnlNeg}`}>
                  {t.net_pnl >= 0 ? '+' : ''}${t.net_pnl.toFixed(2)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
