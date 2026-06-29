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

// ── Yahoo Finance cookie+crumb auth ───────────────────────────────────────
// fc.yahoo.com sets the A3 session cookie (returns 404 but still sets it);
// that cookie is required to fetch a crumb for authenticated endpoints.

let _yfAuth: { cookie: string; crumb: string } | null = null

async function getYFAuth(): Promise<{ cookie: string; crumb: string } | null> {
  if (_yfAuth) return _yfAuth
  const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
  try {
    const r1 = await fetch('https://fc.yahoo.com/', {
      headers: { 'User-Agent': UA, 'Accept-Encoding': 'identity' },
    })
    type HeadersWithSetCookie = Headers & { getSetCookie?: () => string[] }
    const h1 = r1.headers as HeadersWithSetCookie
    const rawCookies: string[] = typeof h1.getSetCookie === 'function'
      ? h1.getSetCookie()
      : [h1.get('set-cookie') ?? ''].filter(Boolean)
    const cookie = rawCookies.map(c => c.split(';')[0]).join('; ')
    if (!cookie) return null

    const r2 = await fetch('https://query1.finance.yahoo.com/v1/test/getcrumb', {
      headers: { 'User-Agent': UA, Cookie: cookie, 'Accept-Encoding': 'identity' },
    })
    if (!r2.ok) { console.log(`YF crumb HTTP ${r2.status} — auth skipped`); return null }
    const crumb = (await r2.text()).trim()
    // Reject if it looks like an error page/message rather than a real crumb
    if (!crumb || crumb.length < 3 || crumb.includes(' ') || crumb.startsWith('<') || crumb.startsWith('{')) return null

    _yfAuth = { cookie, crumb }
    console.log(`YF auth OK: crumb=${crumb.slice(0, 4)}…`)
    return _yfAuth
  } catch {
    return null
  }
}

// ── FRED API ───────────────────────────────────────────────────────────────

const FRED_KEY = process.env.FRED_API_KEY ?? ''

async function fredSeries(id: string): Promise<number | null> {
  if (!FRED_KEY) return null
  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${id}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=10`
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
  console.log('Fetching Fed expectations...')

  // FOMC decision dates (second day of each two-day meeting) — updated annually
  const FOMC_DATES = [
    '2026-01-28', '2026-03-18', '2026-04-29', '2026-06-10',
    '2026-07-29', '2026-09-16', '2026-10-28', '2026-12-09',
    '2027-01-27', '2027-03-17', '2027-04-28', '2027-06-09',
    '2027-07-28', '2027-09-15', '2027-10-27', '2027-12-08',
  ]

  const now = new Date()
  // Include same-day meetings (decision announced after market open)
  const nextMeeting = FOMC_DATES.find(d => new Date(d + 'T23:59:59Z') > now) ?? null

  if (!nextMeeting) return { nextMeeting: null, probCut: null, probHold: null, probHike: null }

  // Current Fed Funds upper target rate from FRED
  const currentRate = await fredSeries('DFEDTARU')
  console.log(`Fed DFEDTARU: ${currentRate}`)
  if (!currentRate) return { nextMeeting, probCut: null, probHold: null, probHike: null }

  // 30-Day Fed Funds futures for the month AFTER the meeting
  // (that month's entire period reflects the post-meeting rate)
  const MONTH_CODES = ['F','G','H','J','K','M','N','Q','U','V','X','Z']
  const meetDate = new Date(nextMeeting)
  const futMon = new Date(meetDate.getFullYear(), meetDate.getMonth() + 1, 1)
  const ticker = `ZQ${MONTH_CODES[futMon.getMonth()]}${String(futMon.getFullYear()).slice(-2)}.CBT`
  console.log(`Fed futures ticker: ${ticker}`)

  try {
    const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    const r = await fetch(`https://query2.finance.yahoo.com/v8/finance/chart/${ticker}?interval=1d&range=5d`, {
      headers: { 'User-Agent': UA, Accept: 'application/json', 'Accept-Encoding': 'identity' },
    })
    console.log(`Fed futures HTTP ${r.status}`)
    if (!r.ok) {
      const txt = await r.text()
      console.log(`Fed futures body: ${txt.slice(0, 150)}`)
      // fall through to DGS1MO fallback below
    } else {
      const parsed = await r.json() as {
        chart?: { result?: Array<{ meta?: { regularMarketPrice?: number; chartPreviousClose?: number } }>; error?: unknown }
      }
      if (parsed.chart?.error) console.log(`Fed futures error: ${JSON.stringify(parsed.chart.error)}`)
      const meta = parsed.chart?.result?.[0]?.meta
      const futuresPrice = meta?.regularMarketPrice ?? meta?.chartPreviousClose
      console.log(`Fed futures price: ${futuresPrice}`)
      if (futuresPrice) {
        const impliedRate = 100 - futuresPrice
        const expectedChange = currentRate - impliedRate
        const pct = Math.round(expectedChange / 0.25 * 100)
        const probCut  = Math.max(0, Math.min(100, pct))
        const probHike = Math.max(0, Math.min(100, -pct))
        const probHold = Math.max(0, 100 - probCut - probHike)
        console.log(`Fed: R0=${currentRate}% implied=${impliedRate.toFixed(3)}% (${ticker}) → cut=${probCut}% hold=${probHold}% hike=${probHike}%`)
        return { nextMeeting, probCut, probHold, probHike }
      }
    }
  } catch (err) {
    console.error('FedWatch futures error:', err)
  }

  // Fallback: approximate via 1-month T-bill yield from FRED
  // DGS1MO reflects the market's expected average fed funds rate over the next month
  try {
    const oneMoYield = await fredSeries('DGS1MO')
    console.log(`Fed DGS1MO fallback: ${oneMoYield}`)
    if (oneMoYield !== null) {
      const expectedChange = currentRate - oneMoYield
      const pct = Math.round(expectedChange / 0.25 * 100)
      const probCut  = Math.max(0, Math.min(100, pct))
      const probHike = Math.max(0, Math.min(100, -pct))
      const probHold = Math.max(0, 100 - probCut - probHike)
      console.log(`Fed DGS1MO: R0=${currentRate}% 1mo=${oneMoYield}% → cut=${probCut}% hold=${probHold}% hike=${probHike}%`)
      return { nextMeeting, probCut, probHold, probHike }
    }
  } catch (err) {
    console.error('FedWatch DGS1MO fallback error:', err)
  }

  return { nextMeeting, probCut: null, probHold: null, probHike: null }
}

// ── GVZ via Yahoo Finance ──────────────────────────────────────────────────

async function fetchGVZ(): Promise<number | null> {
  console.log('Fetching GVZ (Gold Volatility Index)...')
  const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'

  // Method 0: CBOE CDN — delayed quotes static endpoint, rarely rate-limits
  try {
    const r = await fetch('https://cdn.cboe.com/api/global/delayed_quotes/quotes/%5EGVZ.json', {
      headers: { 'User-Agent': UA, Accept: 'application/json' },
    })
    console.log(`GVZ CBOE CDN HTTP ${r.status}`)
    if (r.ok) {
      const parsed = await r.json() as { data?: { last?: number; close?: number } }
      const price = parsed.data?.last ?? parsed.data?.close ?? null
      console.log(`GVZ CBOE CDN price: ${price}`)
      if (price != null && price > 2) return price
    }
  } catch (err) {
    console.error('GVZ CBOE CDN failed:', err)
  }

  // Method 1: Yahoo Finance query2 chart API (no auth required)
  try {
    const r = await fetch('https://query2.finance.yahoo.com/v8/finance/chart/%5EGVZ?interval=1d&range=5d', {
      headers: { 'User-Agent': UA, Accept: 'application/json', 'Accept-Encoding': 'identity' },
    })
    console.log(`GVZ query2 HTTP ${r.status}`)
    if (r.ok) {
      const parsed = await r.json() as {
        chart?: { result?: Array<{ meta?: { regularMarketPrice?: number; chartPreviousClose?: number } }>; error?: unknown }
      }
      if (parsed.chart?.error) console.log(`GVZ query2 error: ${JSON.stringify(parsed.chart.error)}`)
      const meta = parsed.chart?.result?.[0]?.meta
      const price = meta?.regularMarketPrice ?? meta?.chartPreviousClose ?? null
      console.log(`GVZ query2 price: ${price}`)
      if (price != null && price > 2) return price
    } else {
      const txt = await r.text()
      console.log(`GVZ query2 body: ${txt.slice(0, 150)}`)
    }
  } catch (err) {
    console.error('GVZ query2 failed:', err)
  }

  // Method 2: Yahoo Finance query1 with cookie+crumb auth
  try {
    const auth = await getYFAuth()
    if (auth) {
      const r = await fetch(
        `https://query1.finance.yahoo.com/v8/finance/chart/%5EGVZ?interval=1d&range=5d&crumb=${encodeURIComponent(auth.crumb)}`,
        { headers: { 'User-Agent': UA, Cookie: auth.cookie, Accept: 'application/json', 'Accept-Encoding': 'identity' } },
      )
      console.log(`GVZ query1-auth HTTP ${r.status}`)
      if (r.ok) {
        const parsed = await r.json() as {
          chart?: { result?: Array<{ meta?: { regularMarketPrice?: number; chartPreviousClose?: number } }> }
        }
        const meta = parsed.chart?.result?.[0]?.meta
        const price = meta?.regularMarketPrice ?? meta?.chartPreviousClose ?? null
        console.log(`GVZ query1-auth price: ${price}`)
        if (price != null && price > 2) return price
      }
    }
  } catch (err) {
    console.error('GVZ query1-auth failed:', err)
  }

  // Method 3: Stooq CSV (Date,Open,High,Low,Close,Volume — close is column index 4)
  try {
    const csv = await httpGet('https://stooq.com/q/d/l/?s=%5Egvz&i=d')
    const lines = csv.trim().split('\n').filter(l => l.trim())
    console.log(`GVZ Stooq: ${lines.length} lines, last: ${lines[lines.length - 1] ?? 'none'}`)
    if (lines.length >= 2) {
      const last = lines[lines.length - 1].split(',')
      const price = last[4] ? parseFloat(last[4]) : null
      if (price != null && price > 2) return price
    }
  } catch (err) {
    console.error('GVZ Stooq failed:', err)
  }

  // Method 4: FRED GVZCLS (CBOE Gold ETF Volatility Index — updated daily by CBOE)
  try {
    const gvzFred = await fredSeries('GVZCLS')
    console.log(`GVZ FRED GVZCLS: ${gvzFred}`)
    if (gvzFred != null && gvzFred > 2) return gvzFred
  } catch (err) {
    console.error('GVZ FRED failed:', err)
  }

  return null
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

  try {
    // Yahoo Finance summaryDetail: totalAssets ($AUM) ÷ navPrice ($/share) = shares outstanding
    // shares × ~0.0904 troy oz/share ÷ 32,150.7 troy oz/tonne = tonnes of gold held
    // quoteSummary requires YF cookie+crumb auth (crumb prevents unauthenticated scraping)
    const UA = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36'
    const auth = await getYFAuth()
    if (!auth) throw new Error('no YF auth')
    const r = await fetch(
      `https://query1.finance.yahoo.com/v10/finance/quoteSummary/GLD?modules=summaryDetail&crumb=${encodeURIComponent(auth.crumb)}`,
      { headers: { 'User-Agent': UA, Cookie: auth.cookie, Accept: 'application/json', 'Accept-Encoding': 'identity' } },
    )
    const parsed = await r.json() as {
      quoteSummary?: { result?: Array<{ summaryDetail?: { totalAssets?: { raw?: number }; navPrice?: { raw?: number } } }> }
    }
    const sd = parsed.quoteSummary?.result?.[0]?.summaryDetail
    const totalAssets = sd?.totalAssets?.raw
    const navPrice = sd?.navPrice?.raw
    if (!totalAssets || !navPrice) throw new Error('missing GLD data')
    const shares = totalAssets / navPrice
    const tonnes = Math.round(shares * 0.0904 / 32150.7 * 10) / 10
    console.log(`GLD: $${(totalAssets / 1e9).toFixed(1)}B AUM, NAV $${navPrice} → ${tonnes}t`)
    return toWoW(tonnes)
  } catch (err) {
    console.error('GLD fetch failed:', err)
    return { gldTonnes: prevTonnes, gldWoWChange: null, trend3W: null }
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

// All CTrader _SB spread-bet instruments use 10^5 pipettes (verified empirically)
const PIP_DIGITS: Record<string, number> = {
  XAUUSD: 5, XAGUSD: 5,
  EURUSD: 5, USDJPY: 5, USDCHF: 5, USDCNH: 5,
  US500: 5, GER40: 5, UK100: 5,
}

async function mcpFetch(body: object, sessionId?: string): Promise<{ data: unknown; sessionId: string | null }> {
  const headers: Record<string, string> = {
    Authorization: `Bearer ${CTRADER_TOKEN}`,
    'Content-Type': 'application/json',
    Accept: 'application/json, text/event-stream',
  }
  if (sessionId) headers['Mcp-Session-Id'] = sessionId

  const ctrl = new AbortController()
  const timer = setTimeout(() => ctrl.abort(), 20000)
  try {
    const res = await fetch(CTRADER_URL, { method: 'POST', headers, body: JSON.stringify(body), signal: ctrl.signal })
    const newSid = res.headers.get('Mcp-Session-Id') ?? res.headers.get('mcp-session-id') ?? sessionId ?? null
    const text = await res.text()

    if (!res.ok) {
      console.error(`CTrader MCP HTTP ${res.status}: ${text.slice(0, 200)}`)
      return { data: null, sessionId: newSid }
    }

    for (const line of text.split('\n')) {
      if (line.startsWith('data: ')) {
        try { return { data: JSON.parse(line.slice(6)), sessionId: newSid } } catch { /* next line */ }
      }
    }
    try { return { data: JSON.parse(text), sessionId: newSid } } catch { /* ignore */ }
    return { data: null, sessionId: newSid }
  } finally {
    clearTimeout(timer)
  }
}

interface McpBar { high?: number; low?: number; open?: number }

async function fetchCTraderPrices(): Promise<SnapshotPrices | null> {
  const SYMS = ['XAUUSD', 'XAGUSD', 'EURUSD', 'USDJPY', 'USDCHF', 'USDCNH', 'US500', 'GER40', 'UK100']
  console.log(`Fetching CTrader prices via MCP (url=${CTRADER_URL.slice(0, 50)}…)`)

  if (!CTRADER_TOKEN) {
    console.log('CTrader MCP: CTRADER_MCP_TOKEN env var not set — skipping')
    return null
  }

  try {
    // Initialize session
    const { data: initData, sessionId } = await mcpFetch({
      jsonrpc: '2.0', id: 0, method: 'initialize',
      params: { protocolVersion: '2024-11-05', capabilities: {}, clientInfo: { name: 'xauusd-fetch', version: '1.0' } },
    })
    console.log(`CTrader MCP: init result=${JSON.stringify(initData)?.slice(0, 150)} sid=${sessionId}`)
    if (!(initData as Record<string,unknown>)?.result) {
      console.log('CTrader MCP: init failed — no result in response')
      return null
    }
    // sessionId is optional (stateless REST proxy servers may not return Mcp-Session-Id)
    await mcpFetch({ jsonrpc: '2.0', method: 'notifications/initialized', params: {} }, sessionId ?? undefined)

    async function callTool(name: string, args: object): Promise<unknown> {
      const { data } = await mcpFetch({ jsonrpc: '2.0', id: 1, method: 'tools/call', params: { name, arguments: args } }, sessionId ?? undefined)
      const result = (data as Record<string,unknown>)?.result as Record<string,unknown> | undefined
      const content = result?.content as Array<{ type: string; text: string }> | undefined
      if (content?.[0]?.type === 'text') {
        try { return JSON.parse(content[0].text) } catch { return null }
      }
      return null
    }

    // Symbol map — field is symbolName (not name); prefer enabled=true variants
    const symRaw = await callTool('get_symbols', {})
    console.log(`CTrader get_symbols raw: ${JSON.stringify(symRaw)?.slice(0, 300)}`)
    const symbols = (symRaw as { symbols?: Array<{ symbolName: string; symbolId: number; enabled?: boolean }> })?.symbols ?? []
    console.log(`CTrader symbols count: ${symbols.length}`)
    const symMap: Record<string, number> = {}
    const symEnabledMap: Record<string, boolean> = {}
    const suffixRe = /(_SBE|_SB|-F_SBE|-F_SB|-PERP_SBE|-PERP_SB|-PERP|-F)$/
    for (const s of symbols) {
      if (!s.symbolName || !s.symbolId) continue
      const base = s.symbolName.replace(suffixRe, '').toUpperCase()
      const upperName = s.symbolName.toUpperCase()
      symMap[upperName] = s.symbolId
      // For base name, prefer enabled symbol over disabled
      if (symEnabledMap[base] === undefined || s.enabled) {
        symMap[base] = s.symbolId
        symEnabledMap[base] = !!s.enabled
      }
    }
    console.log(`CTrader symMap XAUUSD=${symMap['XAUUSD']} EURUSD=${symMap['EURUSD']}`)

    const ids = SYMS.map(s => symMap[s]).filter((id): id is number => id != null)
    console.log(`CTrader requesting spot prices for ids: ${JSON.stringify(ids)}`)

    // Spot prices
    const spotRaw = await callTool('get_spot_prices', { symbolId: ids })
    console.log(`CTrader get_spot_prices raw: ${JSON.stringify(spotRaw)?.slice(0, 300)}`)
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
          .map(b => (b.high ?? 0) / 10 ** 5 - (b.low ?? 0) / 10 ** 5)
        if (ranges.length > 0) adr14 = Math.round(ranges.reduce((a, b) => a + b, 0) / ranges.length * 10) / 10
        const last = recent[recent.length - 1]
        adrUsed = Math.round(((last.high ?? 0) - (last.low ?? 0)) / 10 ** 5 * 10) / 10
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
