/**
 * UK100 snapshot types — frontend consumption of daily-snapshot.json
 * Mirrors the backend Uk100Snapshot structure from fetch-uk100-data.ts
 */

export interface Uk100FxBlock {
  gbpusd: number | null
  gbpusdDayPct: number | null
  eurusd: number | null
  eurusdDayPct: number | null
  gbpusdOpen: number | null
  gbpusdTrend: 'UP' | 'DOWN' | 'FLAT' | null
}

export interface Uk100RatesBlock {
  gilt20y: number | null
  gilt20yDayBp: number | null
  gilt20yTrend: 'UP' | 'DOWN' | 'FLAT' | null
  realYield5y: number | null
  realYield10y: number | null
  bankRateEst: number | null
  longEndStress: boolean
  giltSelloffRisk: string | null
}

export interface Uk100UsLinkageBlock {
  sp500: number | null
  sp500DayPct: number | null
  nas100: number | null
  nas100DayPct: number | null
  us500: number | null
  us500DayPct: number | null
  usTrend: 'UP' | 'DOWN' | 'FLAT' | null
}

export interface Uk100CommoditiesBlock {
  brent: number | null
  brentDayPct: number | null
  copper: number | null
  copperDayPct: number | null
  brentTrend: 'UP' | 'DOWN' | 'FLAT' | null
  copperTrend: 'UP' | 'DOWN' | 'FLAT' | null
}

export interface Uk100PositioningBlock {
  gbpCotNetLong: number | null
  gbpCotWeekChange: number | null
  gbpCrowding: string | null
  gbpCotUpdated: string | null
}

export interface Uk100SectorRead {
  sector: 'ENERGY' | 'MINERS' | 'BANKS' | 'PHARMA' | 'STAPLES'
  signal: 'STRONG_BUY' | 'BUY' | 'NEUTRAL' | 'SELL' | 'STRONG_SELL'
  confidence: number
  drivers: string[]
}

export interface Uk100CalendarEvent {
  time: string
  country: string
  event: string
  impact: 'HIGH' | 'MEDIUM' | 'LOW'
  daysFromToday: number
  hoursFromNow?: number
}

export interface Uk100NewsItem {
  headline: string
  hoursAgo: number
  source: string
  sentiment?: 'POSITIVE' | 'NEGATIVE' | 'NEUTRAL'
}

export interface BiasDriver {
  component: string
  weight: number
  value: number
  signal: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
}

export interface BiasBlock {
  score: number
  label: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  conviction: 'LOW' | 'MEDIUM' | 'HIGH'
  drivers: BiasDriver[]
}

export interface OrbContext {
  mode: 'PRE_OPEN' | 'ORB_FORMING' | 'POST_ORB' | 'CLOSED'
  computedAt: string
  cashOpenLondon: string
  overnightHigh: number | null
  overnightLow: number | null
  priorDayHigh: number | null
  priorDayLow: number | null
  priorClose: number | null
  gapPts: number | null
  gapPct: number | null
  orbHigh: number | null
  orbLow: number | null
  orbBrokenDirection: 'UP' | 'DOWN' | null
  eventWindows: { event: string; hoursFromNow: number }[]
  adr14: number | null
  adrUsedPct: number | null
}

export interface Uk100Snapshot {
  timestamp: string
  generatedAt: string
  uk100: number | null
  fx: Uk100FxBlock
  rates: Uk100RatesBlock
  usLinkage: Uk100UsLinkageBlock
  commodities: Uk100CommoditiesBlock
  positioning: Uk100PositioningBlock
  sectors: Uk100SectorRead[]
  economicCalendar: Uk100CalendarEvent[]
  newsItems: Uk100NewsItem[]
  bias: BiasBlock
  orbContext: OrbContext
  briefing: string | null
  riskTone: string | null
}
