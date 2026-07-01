import { useState, useMemo } from 'react'
import type { Trade } from '../../../types/trades'
import { groupByDay } from '../../../services/tradeMetrics'
import { DayDetailPanel } from './DayDetailPanel'
import styles from './CalendarSubTab.module.css'

const WEEKDAYS = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

function startOfMonth(d: Date): Date {
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), 1))
}

function daysInMonth(d: Date): number {
  return new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth() + 1, 0)).getUTCDate()
}

interface Props {
  trades: Trade[]
}

export function CalendarSubTab({ trades }: Props) {
  const [cursor, setCursor] = useState(() => startOfMonth(new Date()))
  const [selectedDate, setSelectedDate] = useState<string | null>(null)

  const byDay = useMemo(() => {
    const map = new Map<string, ReturnType<typeof groupByDay>[number]>()
    for (const d of groupByDay(trades)) map.set(d.date, d)
    return map
  }, [trades])

  const year = cursor.getUTCFullYear()
  const month = cursor.getUTCMonth()
  const monthLabel = cursor.toLocaleDateString('en-GB', { month: 'long', year: 'numeric', timeZone: 'UTC' })
  const firstWeekday = startOfMonth(cursor).getUTCDay()
  const numDays = daysInMonth(cursor)

  const cells: (number | null)[] = []
  for (let i = 0; i < firstWeekday; i++) cells.push(null)
  for (let d = 1; d <= numDays; d++) cells.push(d)
  while (cells.length % 7 !== 0) cells.push(null)

  function dateKey(day: number): string {
    return `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`
  }

  function shiftMonth(delta: number) {
    setCursor(c => new Date(Date.UTC(c.getUTCFullYear(), c.getUTCMonth() + delta, 1)))
    setSelectedDate(null)
  }

  const selected = selectedDate ? byDay.get(selectedDate) ?? null : null
  const monthTotal = cells.reduce<number>((sum, day) => {
    if (day == null) return sum
    return sum + (byDay.get(dateKey(day))?.netPnl ?? 0)
  }, 0)

  return (
    <div className={styles.tab}>
      <div className={styles.calendarPane}>
        <div className={styles.nav}>
          <button className={styles.navBtn} onClick={() => shiftMonth(-1)}>‹</button>
          <span className={styles.monthLabel}>{monthLabel}</span>
          <button className={styles.navBtn} onClick={() => shiftMonth(1)}>›</button>
          <span className={monthTotal >= 0 ? styles.monthTotalPos : styles.monthTotalNeg}>
            {monthTotal >= 0 ? '+' : ''}${monthTotal.toFixed(2)}
          </span>
        </div>

        <div className={styles.weekHeader}>
          {WEEKDAYS.map(d => <div key={d} className={styles.weekHeaderCell}>{d}</div>)}
        </div>

        <div className={styles.grid}>
          {cells.map((day, i) => {
            if (day == null) return <div key={i} className={styles.cellEmpty} />
            const key = dateKey(day)
            const data = byDay.get(key)
            const hasTrades = !!data
            const positive = (data?.netPnl ?? 0) >= 0
            const cls = [
              styles.cell,
              hasTrades ? (positive ? styles.cellPos : styles.cellNeg) : '',
              selectedDate === key ? styles.cellActive : '',
            ].filter(Boolean).join(' ')
            return (
              <button key={i} className={cls} onClick={() => hasTrades && setSelectedDate(key)} disabled={!hasTrades}>
                <span className={styles.cellDate}>{day}</span>
                {data && (
                  <>
                    <span className={styles.cellPnl}>{data.netPnl >= 0 ? '+' : ''}${data.netPnl.toFixed(0)}</span>
                    <span className={styles.cellCount}>{data.trades.length} trade{data.trades.length === 1 ? '' : 's'}</span>
                  </>
                )}
              </button>
            )
          })}
        </div>
      </div>

      <DayDetailPanel day={selected} />
    </div>
  )
}
