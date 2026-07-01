import type { Trade, DailyPnl, TradeMetrics } from '../types/trades'

function clamp(n: number, lo: number, hi: number): number {
  return Math.max(lo, Math.min(hi, n))
}

function exitDate(trade: Trade): string {
  return trade.exit_time.slice(0, 10)
}

export function groupByDay(trades: Trade[]): DailyPnl[] {
  const map = new Map<string, Trade[]>()
  for (const t of trades) {
    const d = exitDate(t)
    if (!map.has(d)) map.set(d, [])
    map.get(d)!.push(t)
  }
  return [...map.entries()]
    .map(([date, dayTrades]) => {
      const sorted = [...dayTrades].sort((a, b) => a.exit_time.localeCompare(b.exit_time))
      const netPnl = sorted.reduce((sum, t) => sum + t.net_pnl, 0)
      return {
        date,
        netPnl,
        trades: sorted,
        wins: sorted.filter(t => t.net_pnl > 0).length,
        losses: sorted.filter(t => t.net_pnl <= 0).length,
      }
    })
    .sort((a, b) => a.date.localeCompare(b.date))
}

/**
 * Our own 0-100 composite score inspired by TradeZella's "Zella Score" — TradeZella's
 * real formula is proprietary and undisclosed, so this is an approximation built from
 * five equally-weighted sub-scores, each independently clamped to 0-100.
 */
function computeZellaScore(
  winPct: number,
  profitFactor: number,
  avgWinLossRatio: number,
  dailyNetPnls: number[],
  maxDrawdownPct: number,
): TradeMetrics['zellaBreakdown'] & { score: number } {
  const winRate = clamp(winPct * (100 / 60), 0, 100) // 60% win rate -> 100
  const pf = clamp(profitFactor * 40, 0, 100) // PF 2.5 -> 100
  const avgWinLoss = clamp(avgWinLossRatio * 40, 0, 100) // ratio 2.5 -> 100

  let consistency = 50
  if (dailyNetPnls.length > 1) {
    const mean = dailyNetPnls.reduce((a, b) => a + b, 0) / dailyNetPnls.length
    const variance = dailyNetPnls.reduce((a, b) => a + (b - mean) ** 2, 0) / dailyNetPnls.length
    const stdev = Math.sqrt(variance)
    const meanAbs = Math.abs(mean) || 1
    const cv = stdev / meanAbs
    consistency = clamp(100 - cv * 25, 0, 100)
  }

  const maxDrawdown = clamp(100 - maxDrawdownPct, 0, 100)

  const score = (winRate + pf + avgWinLoss + consistency + maxDrawdown) / 5

  return { winRate, profitFactor: pf, avgWinLoss, consistency, maxDrawdown, score }
}

export function computeMetrics(trades: Trade[]): TradeMetrics {
  const empty: TradeMetrics = {
    netPnl: 0, totalTrades: 0, wins: 0, losses: 0, winPct: 0, profitFactor: 0,
    dayWinPct: 0, daysWithTrades: 0, daysPositive: 0, avgWin: 0, avgLoss: 0,
    avgWinLossRatio: 0, zellaScore: 0,
    zellaBreakdown: { winRate: 0, profitFactor: 0, avgWinLoss: 0, consistency: 0, maxDrawdown: 0 },
    cumulativeSeries: [], dailySeries: [], maxDrawdown: 0,
  }
  if (trades.length === 0) return empty

  const sorted = [...trades].sort((a, b) => a.exit_time.localeCompare(b.exit_time))
  const netPnl = sorted.reduce((sum, t) => sum + t.net_pnl, 0)
  const winners = sorted.filter(t => t.net_pnl > 0)
  const losers = sorted.filter(t => t.net_pnl <= 0)

  const winPct = (winners.length / sorted.length) * 100
  const grossWin = winners.reduce((s, t) => s + t.net_pnl, 0)
  const grossLoss = Math.abs(losers.reduce((s, t) => s + t.net_pnl, 0))
  const profitFactor = grossLoss > 0 ? grossWin / grossLoss : grossWin > 0 ? Infinity : 0

  const avgWin = winners.length > 0 ? grossWin / winners.length : 0
  const avgLoss = losers.length > 0 ? grossLoss / losers.length : 0
  const avgWinLossRatio = avgLoss > 0 ? avgWin / avgLoss : avgWin > 0 ? Infinity : 0

  const days = groupByDay(sorted)
  const daysPositive = days.filter(d => d.netPnl > 0).length
  const dayWinPct = days.length > 0 ? (daysPositive / days.length) * 100 : 0

  let running = 0
  let peak = 0
  let maxDrawdown = 0
  const cumulativeSeries = days.map(d => {
    running += d.netPnl
    peak = Math.max(peak, running)
    const dd = peak > 0 ? ((peak - running) / peak) * 100 : 0
    maxDrawdown = Math.max(maxDrawdown, dd)
    return { date: d.date, cumulative: running }
  })

  const dailySeries = days.map(d => ({ date: d.date, netPnl: d.netPnl, tradeCount: d.trades.length }))

  const { score, ...zellaBreakdown } = computeZellaScore(
    winPct,
    Number.isFinite(profitFactor) ? profitFactor : 5,
    Number.isFinite(avgWinLossRatio) ? avgWinLossRatio : 5,
    days.map(d => d.netPnl),
    maxDrawdown,
  )

  return {
    netPnl,
    totalTrades: sorted.length,
    wins: winners.length,
    losses: losers.length,
    winPct,
    profitFactor: Number.isFinite(profitFactor) ? profitFactor : 0,
    dayWinPct,
    daysWithTrades: days.length,
    daysPositive,
    avgWin,
    avgLoss,
    avgWinLossRatio: Number.isFinite(avgWinLossRatio) ? avgWinLossRatio : 0,
    zellaScore: score,
    zellaBreakdown,
    cumulativeSeries,
    dailySeries,
    maxDrawdown,
  }
}
