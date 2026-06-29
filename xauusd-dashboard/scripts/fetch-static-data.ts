#!/usr/bin/env tsx
/**
 * XAUUSD Daily Data Fetcher
 * Runs via GitHub Action at 06:45 GMT Mon–Fri.
 * Fetches FRED, CME FedWatch, CBOE GVZ, SPDR GLD, CFTC COT.
 * Writes to xauusd-dashboard/public/data/daily-snapshot.json
 *
 * Each fetch is wrapped in try/catch — partial failures write null, never crash.
 */

import * as fs from 'fs'
import * as path from 'path'
import * as https from 'https'
import { fileURLToPath } from 'url'

// ESM shim — tsx runs as ESM on GitHub Actions runners
const __dirname = path.dirname(fileURLToPath(import.meta.url))

// ── Types ──────────────────────────────────────────────────────────────────

interface YieldsData {
  US10Y: number | null
  US2Y: number | null
  realYield10Y: number | null
  realYield5Y: number | null
  curve2s10s: number | null
  breakeven10Y: number | null
  breakeven5Y: number | null
  forward5y5y: number | null
  dayOverDay: { US10Y: number | null; US2Y: number | null; realYield10Y: number | null }
}

interface SnapshotPrices {
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

interface Snapshot {
  generatedAt: string
  yields: YieldsData
  fedExpectations: {
    nextMeeting: string | null
    probCut: number | null
    probHold: number | null
    probHike: number | null
  }
  marketVolatility: { GVZ: number | null }
  positioning: {
    cotNetLong: number | null
    cotWoWChange: number | null
    crowding: 'CROWDED_LONG' | 'NEUTRAL' | 'CROWDED_SHORT' | null
    reportDate: string | null
  }
  etfFlows: {
    gldTonnes: number | null
    gldWoWChange: number | null
    trend3W: 'INFLOW' | 'OUTFLOW' | 'FLAT' | null
  }
  snapshotPrices: SnapshotPrices | null
}

// ── HTTP helper ────────────────────────────────────────────────────────────

function httpGet(url: string, headers: Record<string,string> = {}): Promise<string> {
  return new Promise((resolve, reject) => {
    const opts = new URL(url)
    const req = https.get({
      hostname: opts.hostname,
      path: opts.pathname + opts.search,
      headers: { 'User-Agent': 'xauusd-dashboard/1.0', ...headers },
    }, res => {
      let data = ''
      res.on('data', c => { data += c })
      res.on('end', () => resolve(data))
    })
    req.on('error', reject)
    req.setTimeout(15000, () => { req.destroy(); reject(new Error('Timeout')) })
  })
}

// ── FRED API ───────────────────────────────────────────────────────────────

const FRED_KEY = process.env.FRED_API_KEY ?? ''

async function fredSeries(id: string): Promise<number | null> {
  if (!FRED_KEY) return null
  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${id}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=2`
    const raw = await httpGet(url)
    const data = JSON.parse(raw) as { observations?: Array<{ value: string; date: string }> }
    const obs = data.observations?.filter(o => o.value !== '.') ?? []
    if (obs.length === 0) return null
    return parseFloat(obs[0].value)
  } catch {
    return null
  }
}

async function fredSeriesPair(id: string): Promise<[number | null, number | null]> {
  if (!FRED_KEY) return [null, null]
  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${id}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=3`
    const raw = await httpGet(url)
    const data = JSON.parse(raw) as { observations?: Array<{ value: string }> }
    const obs = data.observations?.filter(o => o.value !== '.') ?? []
    const cur  = obs[0] ? parseFloat(obs[0].value) : null
    const prev = obs[1] ? parseFloat(obs[1].value) : null
    return [cur, prev]
  } catch {
    return [null, null]
  }
}

async function fetchYields(): Promise<YieldsData> {
  console.log('Fetching FRED yields...')
  const [[us10y, us10yPrev], [us2y, us2yPrev], [real10y, real10yPrev], real5y, be10y, be5y, fwd5y5y] =
    await Promise.all([
      fredSeriesPair('DGS10'),
      fredSeriesPair('DGS2'),
      fredSeriesPair('DFII10'),
      fredSeries('DFII5'),
      fredSeries('T10YIE'),
      fredSeries('T5YIE'),
      fredSeries('T5YIFR'),
    ])

  const curve = us10y != null && us2y != null
    ? Math.round((us10y - us2y) * 100)   // convert to bp
    : null

  return {
    US10Y: us10y,
    US2Y: us2y,
    realYield10Y: real10y,
    realYield5Y: real5y,
    curve2s10s: curve,
    breakeven10Y: be10y,
    breakeven5Y: be5y,
    forward5y5y: fwd5y5y,
    dayOverDay: {
      US10Y:       us10y != null && us10yPrev != null   ? parseFloat((us10y - us10yPrev).toFixed(3))     : null,
      US2Y:        us2y  != null && us2yPrev  != null   ? parseFloat((us2y  - us2yPrev).toFixed(3))      : null,
      realYield10Y: real10y != null && real10yPrev != null ? parseFloat((real10y - real10yPrev).toFixed(3)) : null,
    },
  }
}

// ── CME FedWatch scrape ────────────────────────────────────────────────────

async function fetchFedWatch(): Promise<Snapshot['fedExpectations']> {
  console.log('Fetching CME FedWatch...')
  try {
    // CME FedWatch probabilities — public JSON endpoint
    const raw = await httpGet('https://www.cmegroup.com/CmeWS/mvc/ProductCalendar/V2/fomc')
    const data = JSON.parse(raw) as {
      meetingList?: Array<{
        meetingDate?: string
        cutProb?: number | string
        holdProb?: number | string
        hikeProb?: number | string
        raiseProb?: number | string
        lowerProb?: number | string
        unchangedProb?: number | string
      }>
    }
    const meetings = data.meetingList ?? []
    const now = new Date()
    const next = meetings.find(m => m.meetingDate && new Date(m.meetingDate) > now)
    if (!next) return { nextMeeting: null, probCut: null, probHold: null, probHike: null }

    const toNum = (v: unknown) => v != null ? Math.round(parseFloat(String(v))) : null
    return {
      nextMeeting: next.meetingDate ?? null,
      probCut:  toNum(next.lowerProb ?? next.cutProb),
      probHold: toNum(next.unchangedProb ?? next.holdProb),
      probHike: toNum(next.raiseProb ?? next.hikeProb),
    }
  } catch {
    // Fallback: scrape HTML
    try {
      const html = await httpGet('https://www.cmegroup.com/markets/interest-rates/cme-fedwatch-tool.html', {
        Accept: 'text/html',
      })
      const meetingMatch = html.match(/(\d{4}-\d{2}-\d{2})[^"]*FOMC/i)
      const cutMatch   = html.match(/lower[^>]*>[\s\S]*?(\d+\.\d+)%/i)
      const holdMatch  = html.match(/unchanged[^>]*>[\s\S]*?(\d+\.\d+)%/i)
      const hikeMatch  = html.match(/raise[^>]*>[\s\S]*?(\d+\.\d+)%/i)
      return {
        nextMeeting: meetingMatch?.[1] ?? null,
        probCut:  cutMatch  ? Math.round(parseFloat(cutMatch[1]))  : null,
        probHold: holdMatch ? Math.round(parseFloat(holdMatch[1])) : null,
        probHike: hikeMatch ? Math.round(parseFloat(hikeMatch[1])) : null,
      }
    } catch {
      return { nextMeeting: null, probCut: null, probHold: null, probHike: null }
    }
  }
}

// ── GVZ via Yahoo Finance ──────────────────────────────────────────────────

async function fetchGVZ(): Promise<number | null> {
  console.log('Fetching GVZ (Gold Volatility Index)...')
  const YF_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    Accept: 'application/json',
  }
  try {
    const raw = await httpGet(
      'https://query1.finance.yahoo.com/v8/finance/chart/%5EGVZ?interval=1d&range=3d',
      YF_HEADERS,
    )
    const parsed = JSON.parse(raw) as {
      chart?: { result?: Array<{ meta?: { regularMarketPrice?: number } }> }
    }
    return parsed.chart?.result?.[0]?.meta?.regularMarketPrice ?? null
  } catch {
    // Fallback: Stooq free CSV
    try {
      const csv = await httpGet('https://stooq.com/q/d/l/?s=%5Egvz&i=d')
      const lines = csv.trim().split('\n').filter(l => l.trim())
      if (lines.length < 2) return null
      const last = lines[lines.length - 1].split(',')
      return last[4] ? parseFloat(last[4]) : null   // close price is column 5
    } catch {
      return null
    }
  }
}

// ── SPDR GLD holdings ─────────────────────────────────────────────────────

async function fetchGLD(): Promise<Snapshot['etfFlows']> {
  console.log('Fetching SPDR GLD holdings...')
  const outPath = path.join(__dirname, '../public/data/daily-snapshot.json')
  let prevTonnes: number | null = null

  try {
    const prev = JSON.parse(fs.readFileSync(outPath, 'utf8')) as { etfFlows?: { gldTonnes?: number } }
    prevTonnes = prev.etfFlows?.gldTonnes ?? null
  } catch { /* first run */ }

  const toWoW = (tonnes: number | null) => {
    const wow = tonnes != null && prevTonnes != null ? parseFloat((tonnes - prevTonnes).toFixed(2)) : null
    const trend: Snapshot['etfFlows']['trend3W'] = wow != null ? (wow > 0.5 ? 'INFLOW' : wow < -0.5 ? 'OUTFLOW' : 'FLAT') : null
    return { gldTonnes: tonnes, gldWoWChange: wow, trend3W: trend }
  }

  const YF_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
    Accept: 'application/json',
  }

  try {
    // Yahoo Finance: GLD shares outstanding × gold per share → tonnes
    // GLD holds ~0.0904 troy oz per share (started at 0.1, decays 0.4%/yr for expenses)
    // 1 metric tonne = 32,150.7 troy oz
    const raw = await httpGet(
      'https://query1.finance.yahoo.com/v10/finance/quoteSummary/GLD?modules=defaultKeyStatistics',
      YF_HEADERS,
    )
    const parsed = JSON.parse(raw) as {
      quoteSummary?: { result?: Array<{ defaultKeyStatistics?: { sharesOutstanding?: { raw?: number } } }> }
    }
    const shares = parsed.quoteSummary?.result?.[0]?.defaultKeyStatistics?.sharesOutstanding?.raw
    if (!shares) throw new Error('no shares data')
    const tonnes = Math.round(shares * 0.0904 / 32150.7 * 10) / 10
    console.log(`GLD: ${shares.toLocaleString()} shares → ${tonnes}t`)
    return toWoW(tonnes)
  } catch {
    // Fallback: SSGA CSV holdings export
    try {
      const csv = await httpGet(
        'https://www.ssga.com/us/en/intermediary/etfs/funds/spdr-gold-shares-gld',
        { 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36' }
      )
      const match = csv.match(/(\d[\d,]+\.\d+)\s*(?:tonnes|oz)/i)
      const tonnes = match ? parseFloat(match[1].replace(/,/g, '')) : null
      return toWoW(tonnes)
    } catch {
      return { gldTonnes: prevTonnes, gldWoWChange: null, trend3W: null }
    }
  }
}

// ── CFTC COT data ─────────────────────────────────────────────────────────

async function fetchCOT(existingSnapshot: Partial<Snapshot>): Promise<Snapshot['positioning']> {
  console.log('Fetching CFTC COT data...')
  const prevData = existingSnapshot.positioning ?? { cotNetLong: null, cotWoWChange: null, crowding: null, reportDate: null }

  // COT releases Fridays; skip mid-week if data is fresh
  const today = new Date()
  if (prevData.reportDate) {
    const ageMs = today.getTime() - new Date(prevData.reportDate).getTime()
    if (ageMs < 5 * 24 * 3600 * 1000 && today.getUTCDay() !== 5) {
      console.log('COT data fresh, skipping re-fetch')
      return prevData
    }
  }

  try {
    // CFTC public Socrata API — Legacy Futures-Only COT (non-commercial positions, COMEX Gold)
    const url =
      'https://publicreporting.cftc.gov/resource/jun7-fc8e.json' +
      '?$where=market_and_exchange_names%20like%20%27%25GOLD%25%27' +
      '&$order=report_date_as_yyyy_mm_dd%20DESC' +
      '&$limit=2' +
      '&$select=report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all'
    const raw = await httpGet(url, { Accept: 'application/json', 'User-Agent': 'xauusd-dashboard/1.0' })
    const rows = JSON.parse(raw) as Array<{
      report_date_as_yyyy_mm_dd?: string
      noncomm_positions_long_all?: string
      noncomm_positions_short_all?: string
    }>
    if (!rows.length) throw new Error('empty COT response')

    const latest   = rows[0]
    const longPos  = parseInt(latest.noncomm_positions_long_all  ?? '0')
    const shortPos = parseInt(latest.noncomm_positions_short_all ?? '0')
    const net      = longPos - shortPos
    const wow      = prevData.cotNetLong != null ? net - prevData.cotNetLong : null
    const crowding: Snapshot['positioning']['crowding'] = net > 200000 ? 'CROWDED_LONG' : net < 100000 ? 'CROWDED_SHORT' : 'NEUTRAL'
    console.log(`COT: long=${longPos.toLocaleString()} short=${shortPos.toLocaleString()} net=${net.toLocaleString()}`)
    return { cotNetLong: net, cotWoWChange: wow, crowding, reportDate: latest.report_date_as_yyyy_mm_dd ?? null }
  } catch (err) {
    console.error('COT fetch failed:', err)
    return prevData
  }
}

// ── CTrader MCP prices ─────────────────────────────────────────────────────

const CTRADER_URL   = process.env.CTRADER_MCP_URL   || 'https://mcp.ctrader.com/trading/mcp'
const CTRADER_TOKEN = process.env.CTRADER_MCP_TOKEN || ''

const PIP_DIGITS: Record<string, number> = {
  XAUUSD: 3, XAGUSD: 3,
  EURUSD: 5, USDJPY: 3, USDCHF: 5, USDCNH: 5,
  US500: 3, GER40: 3, UK100: 3,
}

async function mcpFetch(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${CTRADER_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const res = await fetch(CTRADER_URL, { method: 'POST', headers, body: JSON.stringify(body) })
  const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
  const text = await res.text()

  for (const line of text.split('\n')) {
    if (line.startsWith('data: ')) {
      try { return { data: JSON.parse(line.slice(6)), sessionId: newSid } } catch { /* next line */ }
    }
  }
  try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
  return { data: null, sessionId: newSid }
}

interface McpBar { high?: number; low?: number; open?: number }

async function fetchCTraderPrices(): Promise<SnapshotPrices | null> {
  const SYMS = ['XAUUSD', 'XAGUSD', 'EURUSD', 'USDJPY', 'USDCHF', 'USDCNH', 'US500', 'GER40', 'UK100']
  console.log('Fetching CTrader prices via MCP...')

  if (!CTRADER_TOKEN) {
    console.log('CTrader MCP: no token, skipping')
    return null
  }

  try {
    // Initialize session
    const { data: initData, sessionId } = await mcpFetch({
      jsonrpc: '2.0', id: 0, method: 'initialize',
      params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'xauusd-fetch', version: '1.0' } },
    })
    if (!(initData as Record<string,unknown>)?.result || !sessionId) {
      console.log('CTrader MCP: init failed')
      return null
    }
    await mcpFetch({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, sessionId)

    async function callTool(name: string, args: object): Promise<unknown> {
      const { data } = await mcpFetch({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } }, sessionId!)
      const result = (data as Record<string,unknown>)?.result as Record<string,unknown> | undefined
      const content = result?.content as Array<{ type: string; text: string }> | undefined
      if (content?.[0]?.type === 'text') {
        try { return JSON.parse(content[0].text) } catch { return null }
      }
      return null
    }

    // Symbol map
    const symRaw = await callTool('get_symbols', {})
    const symbols = (symRaw as { symbols?: Array<{ name: string; symbolId: number }> })?.symbols ?? []
    const symMap: Record<string, number> = {}
    for (const s of symbols) {
      const base = s.name.replace(/(_SBE|_SB|-F_SB|-F)$/, '')
      symMap[s.name.toUpperCase()] = s.symbolId
      symMap[base.toUpperCase()] = s.symbolId
    }

    const ids = SYMS.map(s => symMap[s]).filter((id): id is number => id != null)

    // Spot prices
    const spotRaw = await callTool('get_spot_prices', { symbolId: ids })
    const spots = (spotRaw as { prices?: Array<{ symbolId: number; bid?: number; ask?: number }> })?.prices ?? []
    const spotMap: Record<number, { bid?: number; ask?: number }> = {}
    for (const s of spots) spotMap[s.symbolId] = s

    const pip = (sym: string) => PIP_DIGITS[sym] ?? 5
    const mid = (sym: string): number | null => {
      const id = symMap[sym]; if (!id) return null
      const sp = spotMap[id]; if (!sp) return null
      const bid = sp.bid ?? 0; const ask = sp.ask ?? bid
      if (!bid && !ask) return null
      return parseFloat(((bid + ask) / 2 / 10 ** pip(sym)).toFixed(pip(sym)))
    }

    // ADR for XAUUSD
    let adr14: number | null = null
    let adrUsed: number | null = null
    const xauId = symMap['XAUUSD']
    if (xauId) {
      const now = new Date()
      const from = new Date(now.getTime() - 16 * 24 * 3600 * 1000)
      const adrRaw = await callTool('get_trendbars', {
        symbolId: xauId, period: 'D_1',
        fromTimestamp: from.toISOString(), toTimestamp: now.toISOString(),
      })
      const bars: McpBar[] = (adrRaw as { trendbars?: McpBar[] })?.trendbars ?? []
      if (bars.length >= 2) {
        const recent = bars.slice(-15)
        const ranges = recent.slice(0, Math.min(14, recent.length - 1))
          .map(b => (b.high ?? 0) / 10 ** 3 - (b.low ?? 0) / 10 ** 3)
        if (ranges.length > 0) adr14 = Math.round(ranges.reduce((a, b) => a + b, 0) / ranges.length * 10) / 10
        const last = recent[recent.length - 1]
        adrUsed = Math.round(((last.high ?? 0) - (last.low ?? 0)) / 10 ** 3 * 10) / 10
      }
    }

    const xau = mid('XAUUSD')
    const xag = mid('XAGUSD')
    const result: SnapshotPrices = {
      XAUUSD: xau, XAGUSD: xag,
      EURUSD: mid('EURUSD'), USDJPY: mid('USDJPY'), USDCHF: mid('USDCHF'), USDCNH: mid('USDCNH'),
      US500: mid('US500'), GER40: mid('GER40'), UK100: mid('UK100'),
      ADR_14day: adr14, ADR_usedToday: adrUsed,
      goldSilverRatio: xau && xag ? Math.round(xau / xag * 10) / 10 : null,
    }
    console.log(`CTrader: XAUUSD=${result.XAUUSD}, EURUSD=${result.EURUSD}, ADR=${result.ADR_14day}`)
    return result
  } catch (err) {
    console.error('CTrader MCP fetch failed:', err)
    return null
  }
}

// ── Main ───────────────────────────────────────────────────────────────────

async function main() {
  const outDir  = path.join(__dirname, '../public/data')
  const outPath = path.join(outDir, 'daily-snapshot.json')

  fs.mkdirSync(outDir, { recursive: true })

  // Load existing for incremental updates (COT, WoW deltas)
  let existing: Partial<Snapshot> = {}
  try { existing = JSON.parse(fs.readFileSync(outPath, 'utf8')) } catch { /* first run */ }

  console.log('=== XAUUSD Daily Data Fetch ===')

  const [yields, fedExpectations, gvz, etfFlows, positioning, snapshotPrices] = await Promise.all([
    fetchYields(),
    fetchFedWatch(),
    fetchGVZ(),
    fetchGLD(),
    fetchCOT(existing),
    fetchCTraderPrices(),
  ])

  const snapshot: Snapshot = {
    generatedAt: new Date().toISOString(),
    yields,
    fedExpectations,
    marketVolatility: { GVZ: gvz },
    positioning,
    etfFlows,
    snapshotPrices,
  }

  fs.writeFileSync(outPath, JSON.stringify(snapshot, null, 2))
  console.log(`\nSnapshot written to ${outPath}`)
  console.log(`Generated at: ${snapshot.generatedAt}`)
  console.log(`10Y yield: ${yields.US10Y ?? 'null'}%`)
  console.log(`GVZ: ${gvz ?? 'null'}`)
  console.log(`GLD: ${etfFlows.gldTonnes ?? 'null'}t`)
  console.log(`COT net: ${positioning.cotNetLong ?? 'null'}`)
  console.log(`XAUUSD price: ${snapshotPrices?.XAUUSD ?? 'null'}`)
}

main().catch(err => {
  console.error('Fatal error in data fetch:', err)
  process.exit(1)
})
