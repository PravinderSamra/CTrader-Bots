import { useState, useEffect, useRef, useCallback } from 'react'
import type { CTraderPrices, PricePoint, SnapshotPrices } from '../types/dashboard'

const MCP_URL = import.meta.env.VITE_CTRADER_MCP_URL ?? 'https://mcp.ctrader.com/trading/mcp'
const MCP_TOKEN = import.meta.env.VITE_CTRADER_MCP_TOKEN ?? ''
const POLL_MS = 15_000

// All _SB spread-bet instruments use 10^5 pipettes (verified server-side empirically)
const PIP_DIGITS: Record<string, number> = {
  XAUUSD: 5, XAGUSD: 5,
  EURUSD: 5, USDJPY: 5, USDCHF: 5, USDCNH: 5,
  US500: 5, GER40: 5, UK100: 5,
}

// ── MCP protocol helpers ────────────────────────────────────────────────────

async function mcpPost(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${MCP_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const res = await fetch(MCP_URL, { method: 'POST', headers, body: JSON.stringify(body) })
  const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
  const text = await res.text()

  // SSE format: lines starting with "data: "
  for (const line of text.split('\n')) {
    if (line.startsWith('data: ')) {
      return { data: JSON.parse(line.slice(6)), sessionId: newSid }
    }
  }
  // Plain JSON fallback
  try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
  return { data: null, sessionId: newSid }
}

async function initSession(): Promise<string | null> {
  const { data, sessionId } = await mcpPost({
    jsonrpc: '2.0', id: 0, method: 'initialize',
    params: {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'xauusd-dashboard', version: '1.0' },
    },
  })
  if (!data || !(data as Record<string,unknown>).result || !sessionId) return null
  // Complete handshake
  await mcpPost({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, sessionId)
  return sessionId
}

async function callTool(tool: string, args: object, sessionId: string): Promise<unknown> {
  const { data } = await mcpPost({
    jsonrpc: '2.0', id: 1, method: 'tools/call',
    params: { name: tool, arguments: args },
  }, sessionId)
  if (!data) return null
  const result = (data as Record<string, unknown>).result as Record<string, unknown> | undefined
  if (!result) return null
  const content = result.content as Array<{ type: string; text: string }> | undefined
  if (content?.[0]?.type === 'text') {
    try { return JSON.parse(content[0].text) } catch { return null }
  }
  return null
}

// ── Symbol resolution ───────────────────────────────────────────────────────

// CTrader API returns `symbolName` (not `name`) — keep in sync with fetch-static-data.ts
interface SymbolEntry { symbolName: string; symbolId: number; enabled?: boolean }
let symbolCache: Record<string, number> | null = null

async function loadSymbols(sessionId: string): Promise<Record<string, number>> {
  if (symbolCache) return symbolCache
  const raw = await callTool('get_symbols', {}, sessionId)
  const symbols = (raw as { symbols?: SymbolEntry[] })?.symbols ?? []
  const map: Record<string, number> = {}
  const enabledMap: Record<string, boolean> = {}
  const suffixRe = /(_SBE|_SB|-F_SBE|-F_SB|-PERP_SBE|-PERP_SB|-PERP|-F)$/
  for (const s of symbols) {
    if (!s.symbolName || s.symbolId == null) continue
    const upper = s.symbolName.toUpperCase()
    const base = upper.replace(suffixRe, '')
    map[upper] = s.symbolId
    if (enabledMap[base] === undefined || s.enabled) {
      map[base] = s.symbolId
      enabledMap[base] = !!s.enabled
    }
  }
  symbolCache = map
  return map
}

function getSymbolId(name: string, map: Record<string, number>): number | null {
  return map[name.toUpperCase()] ?? null
}

// ── Price conversion ────────────────────────────────────────────────────────

function rawToDisplay(raw: number, symbol: string): number {
  const d = PIP_DIGITS[symbol] ?? 5
  return raw / 10 ** d
}

// ── Build price point ───────────────────────────────────────────────────────

interface SpotEntry { bid?: number; ask?: number }

function makePrice(spot: SpotEntry, openRaw: number | undefined, symbol: string): PricePoint {
  const bid = rawToDisplay(spot.bid ?? 0, symbol)
  const ask = rawToDisplay(spot.ask ?? 0, symbol)
  const price = bid > 0 && ask > 0 ? (bid + ask) / 2 : bid || ask
  const open = openRaw != null ? rawToDisplay(openRaw, symbol) : price
  const changeDay = price - open
  const changePct = open > 0 ? (changeDay / open) * 100 : 0
  return { price, changeDay, changePct }
}

// ── Default / empty state ───────────────────────────────────────────────────

function emptyPrices(status: CTraderPrices['status']): CTraderPrices {
  const z: PricePoint = { price: 0, changeDay: 0, changePct: 0 }
  return {
    XAUUSD: z, XAGUSD: z, goldSilverRatio: 0,
    DXY: z, EURUSD: 0, USDJPY: 0, USDCHF: 0, USDCNH: 0,
    US500: z, GER40: z, UK100: z,
    ADR_14day: null, ADR_usedToday: null,
    lastUpdated: '', status,
  }
}

// ── ADR calculation from daily bars ─────────────────────────────────────────

interface Bar { high?: number; low?: number; open?: number; close?: number; utcTimestamp?: number; timestamp?: number }

function calcADR(bars: Bar[], symbol: string): { adr: number; used: number } {
  if (bars.length < 2) return { adr: 0, used: 0 }
  const recent = bars.slice(-15)
  const ranges = recent.slice(0, 14).map(b => {
    const h = rawToDisplay(b.high ?? 0, symbol)
    const l = rawToDisplay(b.low ?? 0, symbol)
    return h - l
  })
  const adr = ranges.reduce((a, b) => a + b, 0) / ranges.length
  const today = recent[recent.length - 1]
  const h = rawToDisplay(today.high ?? 0, symbol)
  const l = rawToDisplay(today.low ?? 0, symbol)
  const used = h - l
  return { adr: Math.round(adr * 10) / 10, used: Math.round(used * 10) / 10 }
}

// ── Snapshot fallback ───────────────────────────────────────────────────────

export function pricesFromSnapshot(sp: SnapshotPrices): CTraderPrices {
  const pt = (price: number | null): PricePoint => ({ price: price ?? 0, changeDay: 0, changePct: 0 })
  const eur = sp.EURUSD ?? 0
  const dxyPrice = eur > 0 ? parseFloat((50.14348 / eur * 0.576 + 13.4).toFixed(3)) : 0
  return {
    XAUUSD: pt(sp.XAUUSD),
    XAGUSD: pt(sp.XAGUSD),
    goldSilverRatio: sp.goldSilverRatio ?? 0,
    DXY: pt(dxyPrice),
    EURUSD: eur,
    USDJPY: sp.USDJPY ?? 0,
    USDCHF: sp.USDCHF ?? 0,
    USDCNH: sp.USDCNH ?? 0,
    US500: pt(sp.US500),
    GER40:  pt(sp.GER40),
    UK100:  pt(sp.UK100),
    ADR_14day: sp.ADR_14day,
    ADR_usedToday: sp.ADR_usedToday,
    lastUpdated: '',
    status: 'offline',
  }
}

// ── Hook ────────────────────────────────────────────────────────────────────

export function useCTraderPrices(): CTraderPrices {
  const [prices, setPrices] = useState<CTraderPrices>(() => emptyPrices('loading'))
  const sessionRef = useRef<string | null>(null)
  const symbolMapRef = useRef<Record<string, number> | null>(null)

  const fetchPrices = useCallback(async () => {
    if (!MCP_TOKEN) {
      setPrices(emptyPrices('offline'))
      return
    }

    try {
      // Establish session if needed
      if (!sessionRef.current) {
        sessionRef.current = await initSession()
        if (!sessionRef.current) { setPrices(emptyPrices('offline')); return }
      }

      const sid = sessionRef.current

      // Load symbol map once
      if (!symbolMapRef.current) {
        symbolMapRef.current = await loadSymbols(sid)
      }
      const smap = symbolMapRef.current

      const SYMBOLS = ['XAUUSD', 'XAGUSD', 'EURUSD', 'USDJPY', 'USDCHF', 'USDCNH', 'US500', 'GER40', 'UK100']
      const ids = SYMBOLS.map(s => getSymbolId(s, smap)).filter((id): id is number => id != null)

      const spotRaw = await callTool('get_spot_prices', { symbolId: ids }, sid)
      const spots = (spotRaw as { prices?: Array<{ symbolId: number; bid?: number; ask?: number }> })?.prices ?? []
      const spotMap: Record<number, { bid?: number; ask?: number }> = {}
      for (const s of spots) spotMap[s.symbolId] = s

      // Today's open — fetch D_1 bars for each
      const todayOpen: Record<string, number> = {}
      const now = new Date()
      const from = new Date(now.getTime() - 24 * 3600 * 1000)
      for (const sym of SYMBOLS) {
        const symId = getSymbolId(sym, smap)
        if (!symId) continue
        const barsRaw = await callTool('get_trendbars', {
          symbolId: symId, period: 'D_1',
          fromTimestamp: from.toISOString(),
          toTimestamp: now.toISOString(),
        }, sid)
        const bars = (barsRaw as { trendbars?: Bar[]; bars?: Bar[] })?.trendbars
          ?? (barsRaw as { trendbars?: Bar[]; bars?: Bar[] })?.bars ?? []
        if (bars.length > 0) todayOpen[sym] = bars[bars.length - 1].open ?? 0
      }

      // ADR from 15 daily bars for XAUUSD
      const xauId = getSymbolId('XAUUSD', smap)
      let adr = 0, adrUsed = 0
      if (xauId) {
        const adrFrom = new Date(now.getTime() - 16 * 24 * 3600 * 1000)
        const adrRaw = await callTool('get_trendbars', {
          symbolId: xauId, period: 'D_1',
          fromTimestamp: adrFrom.toISOString(),
          toTimestamp: now.toISOString(),
        }, sid)
        const adrBars = (adrRaw as { trendbars?: Bar[]; bars?: Bar[] })?.trendbars
          ?? (adrRaw as { trendbars?: Bar[]; bars?: Bar[] })?.bars ?? []
        const calc = calcADR(adrBars, 'XAUUSD')
        adr = calc.adr
        adrUsed = calc.used
      }

      const getSpot = (sym: string) => {
        const id = getSymbolId(sym, smap)
        return id != null ? spotMap[id] ?? {} : {}
      }

      const xau = makePrice(getSpot('XAUUSD'), todayOpen['XAUUSD'], 'XAUUSD')
      const xag = makePrice(getSpot('XAGUSD'), todayOpen['XAGUSD'], 'XAGUSD')

      const rawEUR = getSpot('EURUSD')
      const eur = rawEUR.bid != null ? rawToDisplay((rawEUR.bid + (rawEUR.ask ?? rawEUR.bid)) / 2, 'EURUSD') : 0
      const rawJPY = getSpot('USDJPY')
      const jpy = rawJPY.bid != null ? rawToDisplay((rawJPY.bid + (rawJPY.ask ?? rawJPY.bid)) / 2, 'USDJPY') : 0
      const rawCHF = getSpot('USDCHF')
      const chf = rawCHF.bid != null ? rawToDisplay((rawCHF.bid + (rawCHF.ask ?? rawCHF.bid)) / 2, 'USDCHF') : 0
      const rawCNH = getSpot('USDCNH')
      const cnh = rawCNH.bid != null ? rawToDisplay((rawCNH.bid + (rawCNH.ask ?? rawCNH.bid)) / 2, 'USDCNH') : 0

      // DXY approximation from EUR/USD (DXY ≈ 50.14348% EUR/USD inverse weighted)
      const dxyPrice = eur > 0 ? parseFloat((50.14348 / eur * 0.576 + 13.4).toFixed(3)) : 0
      const dxyOpen = todayOpen['EURUSD'] ? 50.14348 / rawToDisplay(todayOpen['EURUSD'], 'EURUSD') * 0.576 + 13.4 : dxyPrice
      const dxy: typeof xau = {
        price: dxyPrice,
        changeDay: dxyPrice - dxyOpen,
        changePct: dxyOpen > 0 ? ((dxyPrice - dxyOpen) / dxyOpen) * 100 : 0,
      }

      setPrices({
        XAUUSD: xau,
        XAGUSD: xag,
        goldSilverRatio: xag.price > 0 ? Math.round((xau.price / xag.price) * 10) / 10 : 0,
        DXY: dxy,
        EURUSD: eur,
        USDJPY: jpy,
        USDCHF: chf,
        USDCNH: cnh,
        US500: makePrice(getSpot('US500'), todayOpen['US500'], 'US500'),
        GER40:  makePrice(getSpot('GER40'),  todayOpen['GER40'],  'GER40'),
        UK100:  makePrice(getSpot('UK100'),  todayOpen['UK100'],  'UK100'),
        ADR_14day: adr || null,
        ADR_usedToday: adrUsed || null,
        lastUpdated: new Date().toISOString(),
        status: 'live',
      })
    } catch {
      // Session may have expired — reset and try next poll
      sessionRef.current = null
      symbolMapRef.current = null
      setPrices(prev => prev.status === 'loading' ? emptyPrices('offline') : { ...prev, status: 'offline' })
    }
  }, [])

  useEffect(() => {
    fetchPrices()
    const id = setInterval(fetchPrices, POLL_MS)
    return () => clearInterval(id)
  }, [fetchPrices])

  return prices
}
