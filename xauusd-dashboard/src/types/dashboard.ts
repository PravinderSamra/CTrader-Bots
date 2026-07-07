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
  XAUUSD_spread: number | null   // ask − bid in display units; null when unavailable (snapshot fallback)
  XAGUSD: PricePoint
  goldSilverRatio: number
  DXY: PricePoint
  EURUSD: number
  USDJPY: number
  USDCHF: number
  USDCNH: number
  GBPUSD: number
  USDCAD: number
  USDSEK: number
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
  date: string            // YYYY-MM-DD
  daysFromToday: number   // 0 = today, 1 = tomorrow, etc.
  time: string
  event: string
  impact: ImpactLevel
  currency: string
  forecast: number | null
  previous: number | null
  actual: number | null
}

export interface NewsItem {
  headline: string
  source: string
  publishedAt: string   // ISO timestamp
  hoursAgo: number
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
  openInterest: number | null
  openInterestChange: number | null
}

export interface DollarLiquidity {
  stlfsi: number | null   // St. Louis Fed Financial Stress Index (0 = average; >0 = stress)
  nfci: number | null     // Chicago Fed National Financial Conditions Index (0 = average; >0 = tighter)
}

export interface GeopoliticalRisk {
  gpr: number | null      // Caldara-Iacoviello Geopolitical Risk Index (100 = 1985-2019 avg)
  gprDate: string | null  // month the latest reading covers
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
  GBPUSD: number | null
  USDCAD: number | null
  USDSEK: number | null
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
  dollarLiquidity?: DollarLiquidity
  geopoliticalRisk?: GeopoliticalRisk
  economicCalendar?: CalendarEvent[]
  newsItems?: NewsItem[]
  briefing?: BriefingResult | null
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

// ── Gold-Session AI history ────────────────────────────────────────────

export type PriceZone = 'DISCOUNT' | 'PREMIUM' | 'EQUILIBRIUM' | 'OTE'

export type KeyLevelKind =
  | 'BSL' | 'SSL' | 'PDH' | 'PDL' | 'PWH' | 'PWL'
  | 'ASIAN_HIGH' | 'ASIAN_LOW' | 'POC' | 'INVALIDATION' | 'DRAW' | 'OTHER'

export interface KeyLevel {
  price: number
  kind:  KeyLevelKind
  note?: string
}

export interface StructuredTradeIdea {
  direction:  'LONG' | 'SHORT'
  status:     'ACTIVE' | 'WAIT' | 'NO_TRADE'
  entryLow?:  number
  entryHigh?: number
  stop?:      number
  targets?:   number[]
  rr?:        number
  setupType?: string
}

// Optional structured fields shared by record + index (Phase 2). Absent on
// pre-Phase-2 records — consumers fall back to regex-parsing `analysis`.
export interface StructuredSessionFields {
  priceAtAnalysis?:     number
  drawOnLiquidity?:     number
  invalidation?:        number
  priceZone?:           PriceZone
  equilibrium?:         number
  keyLevels?:           KeyLevel[]
  tradeIdea?:           StructuredTradeIdea | null
  nextHighImpactEvent?: { event: string; timeIso: string } | null
  smtDivergence?:       'BULLISH' | 'BEARISH' | null
}

export interface GoldSessionRecord extends StructuredSessionFields {
  timestamp:   string   // ISO
  date:        string   // YYYY-MM-DD
  time:        string   // HH:MM (UK local, carries BST/GMT)
  session:     string   // LONDON | NEW_YORK | OVERLAP | ASIAN
  bias:        string   // BULLISH | BEARISH | NEUTRAL
  biasScore:   number   // -5 to +5
  probability: number   // 0-100 (primary scenario)
  confidence:  number   // 1-10
  analysis:    string   // full plain-text analysis output
}

export interface GoldSessionEntry {
  date:        string
  time:        string
  filename:    string   // YYYY-MM-DD/HH-MM.json  (relative to sessions/)
  session:     string
  bias:        string
  biasScore:   number
  probability: number
  confidence:  number
  timestamp:   string
  priceZone?:  PriceZone
  tradeIdea?:  { direction: 'LONG' | 'SHORT'; status: 'ACTIVE' | 'WAIT' | 'NO_TRADE' } | null
}

export interface GoldSessionIndex {
  updatedAt: string
  sessions:  GoldSessionEntry[]
}
