import type {
  CTraderPrices, DailySnapshot, CalendarEvent,
  MarketVolatility, DollarLiquidity, GeopoliticalRisk,
} from '../types/dashboard'

export interface AggregatedData {
  timestamp: string
  session: string
  prices: {
    XAUUSD: { price: number; changeDay: number; changePct: number }
    XAGUSD: { price: number; changeDay: number; changePct: number }
    goldSilverRatio: number
    DXY: { price: number; changePct: number }
    EURUSD: number
    USDJPY: number
    USDCHF: number
    USDCNH: number
    US500: { changePct: number }
    GER40: { changePct: number }
    UK100: { changePct: number }
    ADR_14day: number | null
    ADR_usedToday: number | null
  }
  yields: DailySnapshot['yields'] | null
  fedExpectations: DailySnapshot['fedExpectations'] | null
  marketVolatility: MarketVolatility
  positioning: DailySnapshot['positioning'] | null
  etfFlows: DailySnapshot['etfFlows'] | null
  dollarLiquidity: DollarLiquidity | null
  geopoliticalRisk: GeopoliticalRisk | null
  calendar: CalendarEvent[]
  headlines: string[]
}

export function aggregateData(
  prices: CTraderPrices,
  snapshot: DailySnapshot | null,
  calendar: CalendarEvent[],
  headlines: string[],
  vix: number | null,
  session: string,
): AggregatedData {
  const gvz = snapshot?.marketVolatility?.GVZ ?? null
  const riskTone = computeRiskTone(prices, vix)

  return {
    timestamp: new Date().toISOString(),
    session,
    prices: {
      XAUUSD: prices.XAUUSD,
      XAGUSD: prices.XAGUSD,
      goldSilverRatio: prices.goldSilverRatio,
      DXY: { price: prices.DXY.price, changePct: prices.DXY.changePct },
      EURUSD: prices.EURUSD,
      USDJPY: prices.USDJPY,
      USDCHF: prices.USDCHF,
      USDCNH: prices.USDCNH,
      US500: { changePct: prices.US500.changePct },
      GER40:  { changePct: prices.GER40.changePct },
      UK100:  { changePct: prices.UK100.changePct },
      ADR_14day: prices.ADR_14day,
      ADR_usedToday: prices.ADR_usedToday,
    },
    yields: snapshot?.yields ?? null,
    fedExpectations: snapshot?.fedExpectations ?? null,
    marketVolatility: { VIX: vix, GVZ: gvz, riskTone },
    positioning: snapshot?.positioning ?? null,
    etfFlows: snapshot?.etfFlows ?? null,
    dollarLiquidity: snapshot?.dollarLiquidity ?? null,
    geopoliticalRisk: snapshot?.geopoliticalRisk ?? null,
    calendar,
    headlines,
  }
}

function computeRiskTone(prices: CTraderPrices, vix: number | null): MarketVolatility['riskTone'] {
  const indicesNeg = prices.US500.changePct < -0.1 && prices.UK100.changePct < -0.1
  const indicesPos = prices.US500.changePct > 0.1 && prices.GER40.changePct > 0.1
  if (vix && vix > 20 && indicesNeg) return 'RISK_OFF'
  if (vix && vix < 16 && indicesPos) return 'RISK_ON'
  if (indicesNeg) return 'RISK_OFF'
  if (indicesPos) return 'RISK_ON'
  return 'NEUTRAL'
}
