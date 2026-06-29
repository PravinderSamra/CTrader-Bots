/* ═══════════════════════════════════════════
   XAUUSD Dashboard — TypeScript Interfaces
   ═══════════════════════════════════════════ */

export interface PricePoint {
  price: number
  changeDay: number
  changePct: number
}

export interface CTraderPrices {
  XAUUSD: PricePoint
  XAGUSD: PricePoint
  goldSilverRatio: number
  DXY: PricePoint
  EURUSD: number
  USDJPY: number
  USDCHF: number
  USDCNH: number
  US500: PricePoint
  GER40: PricePoint
  UK100: PricePoint
  ADR_14day: number | null
  ADR_usedToday: number | null
  lastUpdated: string
  status: 'live' | 'offline' | 'loading'
}

export interface YieldsData {
  US10Y: number | null
  US2Y: number | null
  realYield10Y: number | null
  realYield5Y: number | null
  curve2s10s: number | null
  breakeven10Y: number | null
  breakeven5Y: number | null
  forward5y5y: number | null
  dayOverDay: {
    US10Y: number | null
    US2Y: number | null
    realYield10Y: number | null
  }
}

export type ImpactLevel = 'HIGH' | 'MEDIUM' | 'LOW'

export interface CalendarEvent {
  time: string
  event: string
  impact: ImpactLevel
  currency: string
  forecast: number | null
  previous: number | null
  actual: number | null
}

export interface FedExpectations {
  nextMeeting: string
  probCut: number | null
  probHold: number | null
  probHike: number | null
}

export interface MarketVolatility {
  VIX: number | null
  GVZ: number | null
  riskTone: 'RISK_ON' | 'RISK_OFF' | 'NEUTRAL' | null
}

export interface COTPositioning {
  cotNetLong: number | null
  cotWoWChange: number | null
  crowding: 'CROWDED_LONG' | 'NEUTRAL' | 'CROWDED_SHORT' | null
  reportDate: string | null
}

export interface ETFFlows {
  gldTonnes: number | null
  gldWoWChange: number | null
  trend3W: 'INFLOW' | 'OUTFLOW' | 'FLAT' | null
}

export interface SnapshotPrices {
  XAUUSD: number | null
  XAGUSD: number | null
  EURUSD: number | null
  USDJPY: number | null
  USDCHF: number | null
  USDCNH: number | null
  US500: number | null
  GER40: number | null
  UK100: number | null
  ADR_14day: number | null
  ADR_usedToday: number | null
  goldSilverRatio: number | null
}

export interface DailySnapshot {
  generatedAt: string
  yields: YieldsData
  fedExpectations: FedExpectations
  marketVolatility: Partial<MarketVolatility>
  positioning: COTPositioning
  etfFlows: ETFFlows
  snapshotPrices?: SnapshotPrices
}

export interface BriefingResult {
  biasScore: number        // -5 to +5
  biasLabel: 'BEARISH' | 'NEUTRAL' | 'BULLISH'
  confidence: number       // 1–10
  briefing: string
  generatedAt: string
}

export type SessionName = 'ASIAN' | 'LONDON' | 'OVERLAP' | 'NEW_YORK' | 'OFF'

export interface SessionInfo {
  current: SessionName
  label: string
  nextSessionName: string
  nextSessionTime: string
  minutesToNext: number
  isPrime: boolean
}
