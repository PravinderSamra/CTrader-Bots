/**
 * UK100 snapshot types — frontend consumption of public/data/uk100/daily-snapshot.json
 * Mirrors the backend Uk100Snapshot structure from scripts/fetch-uk100-data.ts exactly.
 */

import type { KeyLevel, PriceZone, StructuredTradeIdea, SessionOutcome } from './dashboard'

export type FtseImpact = 'BULLISH' | 'BEARISH' | 'NEUTRAL'

export interface Uk100Prices {
  UK100: number | null; GBPUSD: number | null; GBPEUR: number | null
  US500: number | null; NAS100: number | null; BRENT: number | null; COPPER: number | null
  VIX: number | null; USDX: number | null; XAUUSD: number | null
  UK100_dayPct: number | null
}

export interface FxBlock {
  gbpUsdDayPct: number | null
  gbpUsd20dPercentile: number | null
  sterlingEri: number | null
  sterlingEriDayChange: number | null
  ftseImpactFromGbp: FtseImpact
}

export interface UkRatesBlock {
  bankRate: number | null
  sonia: number | null
  soniaMinusBankRate: number | null
  gilt5y: number | null; gilt10y: number | null; gilt20y: number | null
  gilt10yDayBp: number | null; gilt20yDayBp: number | null
  slope5s20s: number | null
  giltUst10ySpread: number | null
  longEndStress: boolean
  nextMpcDate: string | null
  daysToMpc: number | null
}

export interface UsLinkageBlock {
  us500DayPct: number | null; nas100DayPct: number | null
  vix: number | null
  // B2 (UK100-V2-PLAN.md §4): canonical vocabulary is CALM/NORMAL/STRESS.
  // Old snapshots (pre-B2) can still carry the retired 'ELEVATED' string
  // until the next hourly overwrite — consumers (explainUsLinkage,
  // Uk100UsLinkageTile) must tolerate any unrecognised value as the middle
  // band, not crash, so this type is not treated as exhaustive at runtime.
  vixRegime: 'CALM' | 'NORMAL' | 'STRESS'
  us10y: number | null
  usdx: number | null
}

export interface CommoditiesBlock {
  brentDayPct: number | null; copperDayPct: number | null; goldDayPct: number | null
  brent20dTrend: 'UP' | 'DOWN' | 'FLAT'
}

export interface EuropeanTapeBlock {
  eurostoxx50DayPct: number | null; dax40DayPct: number | null
  eurUsdDayPct: number | null
  ftseDaxCorr20d: number | null; ftseSx5eCorr20d: number | null
  tapeAgreement: 'ALIGNED' | 'SPLIT' | 'DIVERGING'
  preOpenLead: 'UP' | 'DOWN' | 'NONE'
}

export interface PositioningBlock {
  gbpCotNetLong: number | null; gbpCotWoWChange: number | null
  crowding: 'CROWDED_LONG' | 'CROWDED_SHORT' | 'BALANCED' | null
  reportDate: string | null
  ftseReadthrough: FtseImpact
}

export interface SectorRead {
  sector: 'ENERGY' | 'MINERS' | 'BANKS' | 'PHARMA' | 'STAPLES'
  weightNote: string
  driver: string
  read: FtseImpact | 'IDIOSYNCRATIC'
  detail: string
}

export interface Uk100CalendarEvent {
  event: string; region: 'UK' | 'US' | 'EZ'; impact: 'HIGH' | 'MEDIUM' | 'LOW'
  timeIso: string; timeLondon: string
  daysFromToday: number; prior?: string; consensus?: string
}

export interface Uk100NewsItem {
  headline: string; source: string; hoursAgo: number; url?: string
}

export interface BiasDriver {
  name: string; impact: FtseImpact; weight: number; detail: string
}

export interface BiasBlock {
  score: number
  label: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  conviction: 'LOW' | 'MEDIUM' | 'HIGH'
  drivers: BiasDriver[]
  eventSuppressed: boolean
}

export interface OrbEventWindow {
  event: string; timeLondon: string; impact: string
}

export interface OrbContext {
  computedAt: string
  mode: 'PRE_OPEN' | 'ORB_FORMING' | 'POST_ORB' | 'CLOSED'
  cashOpenLondon: string
  overnightHigh: number | null; overnightLow: number | null
  priorDayHigh: number | null; priorDayLow: number | null; priorClose: number | null
  prevWeekHigh: number | null; prevWeekLow: number | null
  gapPts: number | null; gapPct: number | null
  orbHigh: number | null; orbLow: number | null
  orbBrokenDirection: 'UP' | 'DOWN' | 'NONE' | null
  eventWindows: OrbEventWindow[]
  adr14: number | null; adrUsedPct: number | null
}

// ── ORB intelligence (G1, UK100-ORB-INTEL-TLDR-DESIGN.md §2) — mirror of the
//    script-local types in scripts/fetch-uk100-data.ts. ──
export type OrbIntelDirection = 'FAVOURS_LONG' | 'FAVOURS_SHORT' | 'BREAKOUT_SUSPECT' | 'NEUTRAL'
export type OrbIntelSeverity  = 'INFO' | 'CAUTION' | 'STRONG'
export type OrbIntelSource    =
  'STRUCTURE' | 'RANGE' | 'GAP' | 'TAPE' | 'FX' | 'RATES' | 'POSITIONING' | 'EVENT' | 'AI'

export interface OrbIntelSignal {
  direction: OrbIntelDirection
  severity:  OrbIntelSeverity
  source:    OrbIntelSource
  text:      string
}

export type OrbIntelStance =
  'LONG_FAVOURED' | 'SHORT_FAVOURED' | 'FADE_FAVOURED' | 'BREAKOUTS_SUSPECT' | 'MIXED'

export interface OrbIntel {
  stance:       OrbIntelStance
  stanceLine:   string
  signals:      OrbIntelSignal[]
  aiStanceLine: string | null
  aiBullets:    string[]
  baseRateNote: string | null
}

export interface Uk100RiskTone {
  score: number; label: FtseImpact; rationale: string
}

export interface Uk100Briefing {
  biasScore: number; biasLabel: string; confidence: number; briefing: string; generatedAt: string
}

export interface Uk100Snapshot {
  generatedAt: string
  prices: Uk100Prices
  fx: FxBlock
  ukRates: UkRatesBlock
  usLinkage: UsLinkageBlock
  commodities: CommoditiesBlock
  europeanTape: EuropeanTapeBlock
  positioning: PositioningBlock
  sectorPanel: SectorRead[]
  economicCalendar: Uk100CalendarEvent[]
  newsItems: Uk100NewsItem[]
  riskTone: Uk100RiskTone | null
  bias: BiasBlock
  orbContext: OrbContext
  orbIntel: OrbIntel
  briefing: Uk100Briefing | null
}

// ── UK100 AI Session history (Phase 2c/2d) ─────────────────────────────────
// Written by save-gold-session.ts --instrument=uk100; read by useUk100Sessions.

export interface OrbPlaybook {
  direction:    'LONG_ONLY' | 'SHORT_ONLY' | 'BOTH_OK' | 'STAND_ASIDE'
  dayType:      'EVENT_DRIVEN' | 'TREND_EXPECTED' | 'RANGE_EXPECTED'
  reasoning:    string
  keyLevels:    { label: string; price: number }[]
  invalidation: string
  eventRisk?:   string
}

// Same optional structured fields as GoldSessionRecord (StructuredSessionFields
// in dashboard.ts), plus orbPlaybook. Kept as a separate interface (not
// `extends`) to avoid importing dashboard.ts's whole gold-specific surface.
export interface Uk100SessionRecord {
  timestamp:   string   // ISO
  date:        string   // YYYY-MM-DD
  time:        string   // HH:MM (UK local, carries BST/GMT)
  session:     string   // LONDON | ASIAN (UK100 has no NEW_YORK/OVERLAP equivalent)
  bias:        string   // BULLISH | BEARISH | NEUTRAL
  biasScore:   number   // -10 to +10 (mechanical bias engine range)
  probability: number   // 0-100 (primary scenario)
  confidence:  number   // 1-10
  analysis:    string   // full plain-text analysis output

  priceAtAnalysis?:     number
  drawOnLiquidity?:     number
  invalidation?:        number
  priceZone?:           PriceZone
  equilibrium?:         number
  keyLevels?:           KeyLevel[]
  tradeIdea?:           StructuredTradeIdea | null
  nextHighImpactEvent?: { event: string; timeIso: string } | null
  smtDivergence?:       'BULLISH' | 'BEARISH' | null
  orbPlaybook?:         OrbPlaybook | null
  outcome?:             SessionOutcome   // written back by the resolver once scored (F7)
}

export interface Uk100SessionEntry {
  date:        string
  time:        string
  filename:    string   // YYYY-MM-DD/HH-MM.json (relative to uk100/sessions/)
  timestamp:   string
  session:     string
  bias:        string
  biasScore:   number
  probability: number
  confidence:  number
  priceZone?:  PriceZone
  tradeIdea?:  { direction: 'LONG' | 'SHORT'; status: 'ACTIVE' | 'WAIT' | 'NO_TRADE' } | null
}

export interface Uk100SessionIndex {
  updatedAt: string
  sessions:  Uk100SessionEntry[]
}
