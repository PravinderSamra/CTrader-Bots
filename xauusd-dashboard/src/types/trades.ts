/* ═══════════════════════════════════════════
   Pravzella — Trade journal TypeScript interfaces
   ═══════════════════════════════════════════ */

export type TradeDirection = 'LONG' | 'SHORT'

export interface Trade {
  id: string
  user_id: string
  position_id: number
  symbol: string
  direction: TradeDirection
  volume: number          // GBP stake per point (ctrader volume / 100)
  entry_price: number
  exit_price: number
  entry_time: string      // ISO timestamp
  exit_time: string       // ISO timestamp
  gross_pnl: number
  commission: number
  net_pnl: number
  source: string
  created_at: string
  updated_at: string
}

export interface DailyPnl {
  date: string             // YYYY-MM-DD (UTC)
  netPnl: number
  trades: Trade[]
  wins: number
  losses: number
}

export interface TradeMetrics {
  netPnl: number
  totalTrades: number
  wins: number
  losses: number
  winPct: number
  profitFactor: number
  dayWinPct: number
  daysWithTrades: number
  daysPositive: number
  avgWin: number
  avgLoss: number
  avgWinLossRatio: number
  zellaScore: number
  zellaBreakdown: {
    winRate: number
    profitFactor: number
    avgWinLoss: number
    consistency: number
    maxDrawdown: number
  }
  cumulativeSeries: { date: string; cumulative: number }[]
  dailySeries: { date: string; netPnl: number; tradeCount: number }[]
  maxDrawdown: number
}
