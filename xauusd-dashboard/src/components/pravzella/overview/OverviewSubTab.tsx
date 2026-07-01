import type { TradeMetrics } from '../../../types/trades'
import { StatCard } from './StatCard'
import { DonutGauge } from './DonutGauge'
import { RatioBar } from './RatioBar'
import { ZellaScoreRadar } from './ZellaScoreRadar'
import { CumulativePnlChart } from './CumulativePnlChart'
import { DailyPnlBarChart } from './DailyPnlBarChart'
import styles from './OverviewSubTab.module.css'

function fmtMoney(n: number): string {
  const sign = n < 0 ? '-' : ''
  return `${sign}$${Math.abs(n).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`
}

interface Props {
  metrics: TradeMetrics
  loading: boolean
}

export function OverviewSubTab({ metrics, loading }: Props) {
  if (loading) {
    return <div className={styles.loading}>Loading trades…</div>
  }

  if (metrics.totalTrades === 0) {
    return (
      <div className={styles.empty}>
        <div className={styles.emptyTitle}>No trades synced yet</div>
        <div className={styles.emptySub}>
          Trades are pulled automatically from cTrader on a schedule. Once the sync workflow
          has run at least once, closed trades will appear here.
        </div>
      </div>
    )
  }

  const netColor = metrics.netPnl >= 0 ? 'var(--green)' : 'var(--red)'

  return (
    <div className={styles.tab}>
      <div className={styles.statsRow}>
        <StatCard label="Net P&L" value={fmtMoney(metrics.netPnl)} valueColor={netColor} badge={metrics.totalTrades} />

        <StatCard label="Trade Win %" value={`${metrics.winPct.toFixed(2)}%`}>
          <DonutGauge
            segments={[
              { value: metrics.wins, color: 'var(--green)' },
              { value: metrics.losses, color: 'var(--red)' },
            ]}
          />
        </StatCard>

        <StatCard label="Profit Factor" value={metrics.profitFactor.toFixed(2)}>
          <DonutGauge
            segments={[
              { value: Math.min(metrics.profitFactor, 3), color: 'var(--green)' },
              { value: Math.max(3 - metrics.profitFactor, 0), color: 'var(--border)' },
            ]}
          />
        </StatCard>

        <StatCard label="Day Win %" value={`${metrics.dayWinPct.toFixed(2)}%`}>
          <DonutGauge
            segments={[
              { value: metrics.daysPositive, color: 'var(--green)' },
              { value: metrics.daysWithTrades - metrics.daysPositive, color: 'var(--red)' },
            ]}
          />
        </StatCard>

        <StatCard label="Avg Win/Loss Trade" value={metrics.avgWinLossRatio.toFixed(2)} stackVisual>
          <RatioBar win={metrics.avgWin} loss={metrics.avgLoss} />
        </StatCard>
      </div>

      <div className={styles.chartsRow}>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Zella Score</div>
          <ZellaScoreRadar breakdown={metrics.zellaBreakdown} score={metrics.zellaScore} />
        </div>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Daily Net Cumulative P&L</div>
          <CumulativePnlChart series={metrics.cumulativeSeries} />
        </div>
        <div className={styles.chartCard}>
          <div className={styles.chartTitle}>Net Daily P&L</div>
          <DailyPnlBarChart series={metrics.dailySeries} />
        </div>
      </div>
    </div>
  )
}
