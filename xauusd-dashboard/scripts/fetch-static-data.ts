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

interface CalendarEvent {
  date: string            // YYYY-MM-DD
  daysFromToday: number   // 0 = today, 1 = tomorrow, etc.
  time: string
  event: string
  impact: 'HIGH' | 'MEDIUM' | 'LOW'
  currency: string
  forecast: number | null
  previous: number | null
  actual: number | null
}

interface NewsItem {
  headline: string
  source: string
  publishedAt: string   // ISO timestamp
  hoursAgo: number
}

interface BriefingResult {
  biasScore: number
  biasLabel: 'BEARISH' | 'NEUTRAL' | 'BULLISH'
  confidence: number
  briefing: string
  generatedAt: string
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
  marketVolatility: { GVZ: number | null; VIX: number | null }
  positioning: {
    cotNetLong: number | null
    cotWoWChange: number | null
    crowding: 'CROWDED_LONG' | 'NEUTRAL' | 'CROWDED_SHORT' | null
    reportDate: string | null
    openInterest: number | null
    openInterestChange: number | null
  }
  etfFlows: {
    gldTonnes: number | null
    gldWoWChange: number | null
    trend3W: 'INFLOW' | 'OUTFLOW' | 'FLAT' | null
  }
  snapshotPrices: SnapshotPrices | null
  dollarLiquidity: { stlfsi: number | null; nfci: number | null }
  geopoliticalRisk: { gpr: number | null; gprDate: string | null }
  economicCalendar: CalendarEvent[]
  newsItems: NewsItem[]
  briefing: BriefingResult | null
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

async function fetchGLD(fallbackGoldPrice: number | null): Promise<Snapshot['etfFlows']> {
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

  // Method 1: Yahoo Finance (blocked from GitHub Actions — 429)
  try {
    // Yahoo Finance summaryDetail: totalAssets ($AUM) ÷ navPrice ($/share) = shares outstanding
    // shares × ~0.0904 troy oz/share ÷ 32,150.7 troy oz/tonne = tonnes of gold held
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
    console.log(`GLD YF: $${(totalAssets / 1e9).toFixed(1)}B AUM, NAV $${navPrice} → ${tonnes}t`)
    return toWoW(tonnes)
  } catch (err) {
    console.error('GLD YF fetch failed:', err)
  }

  // Method 2: Alpha Vantage ETF_PROFILE + FRED London gold fix
  // tonnes = net_assets (USD) / goldPrice (USD/oz) / 32150.7 (oz/tonne)
  // Requires ALPHA_VANTAGE_API_KEY secret — free key at alphavantage.co (25 calls/day)
  try {
    const avKey = process.env.ALPHA_VANTAGE_API_KEY
    if (!avKey) {
      console.log('GLD AV: ALPHA_VANTAGE_API_KEY not set — skipping (add secret to enable GLD data)')
    } else {
      const r = await fetch(`https://www.alphavantage.co/query?function=ETF_PROFILE&symbol=GLD&apikey=${avKey}`)
      console.log(`GLD AV HTTP ${r.status}`)
      if (r.ok) {
        const data = await r.json() as { net_assets?: string; Information?: string }
        if (data.Information) {
          console.log(`GLD AV rate limit: ${data.Information.slice(0, 120)}`)
        } else if (data.net_assets) {
          const netAssets = parseFloat(data.net_assets)
          if (netAssets > 1e9) {
            // GOLDAMGBD228NLBM (LBMA AM gold fix) is unreliable on FRED — fall back to
            // the already-confirmed-working CTrader XAUUSD spot price for goldPrice.
            const fredGold = await fredSeries('GOLDAMGBD228NLBM')
            const goldPrice = fredGold ?? fallbackGoldPrice
            console.log(`GLD AV: net_assets=$${(netAssets / 1e9).toFixed(1)}B, FRED gold=$${fredGold}/oz, fallback=$${fallbackGoldPrice}/oz, using=$${goldPrice}/oz`)
            if (goldPrice && goldPrice > 500) {
              const tonnes = Math.round(netAssets / goldPrice / 32150.7 * 10) / 10
              console.log(`GLD AV → ${tonnes}t`)
              return toWoW(tonnes)
            }
          }
        }
      }
    }
  } catch (err) {
    console.error('GLD AV fallback failed:', err)
  }

  console.log(`GLD: all sources failed, carrying forward prevTonnes=${prevTonnes}`)
  return { gldTonnes: prevTonnes, gldWoWChange: null, trend3W: null }
}

// ── CFTC COT data ─────────────────────────────────────────────────────────

async function fetchCOT(existingSnapshot: Partial<Snapshot>): Promise<Snapshot['positioning']> {
  console.log('Fetching CFTC COT data...')
  const prevData = existingSnapshot.positioning ?? {
    cotNetLong: null, cotWoWChange: null, crowding: null, reportDate: null,
    openInterest: null, openInterestChange: null,
  }

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
      '&$select=report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all,open_interest_all,change_in_open_interest_all'
    const raw = await httpGet(url, { Accept: 'application/json', 'User-Agent': 'xauusd-dashboard/1.0' })
    const rows = JSON.parse(raw) as Array<{
      report_date_as_yyyy_mm_dd?: string
      noncomm_positions_long_all?: string
      noncomm_positions_short_all?: string
      open_interest_all?: string
      change_in_open_interest_all?: string
    }>
    if (!rows.length) throw new Error('empty COT response')

    const latest   = rows[0]
    const longPos  = parseInt(latest.noncomm_positions_long_all  ?? '0')
    const shortPos = parseInt(latest.noncomm_positions_short_all ?? '0')
    const net      = longPos - shortPos
    const wow      = prevData.cotNetLong != null ? net - prevData.cotNetLong : null
    const crowding: Snapshot['positioning']['crowding'] = net > 200000 ? 'CROWDED_LONG' : net < 100000 ? 'CROWDED_SHORT' : 'NEUTRAL'
    const openInterest = latest.open_interest_all != null ? parseInt(latest.open_interest_all) : null
    const openInterestChange = latest.change_in_open_interest_all != null ? parseInt(latest.change_in_open_interest_all) : null
    console.log(`COT: long=${longPos.toLocaleString()} short=${shortPos.toLocaleString()} net=${net.toLocaleString()} OI=${openInterest?.toLocaleString()} OIchg=${openInterestChange}`)
    return {
      cotNetLong: net, cotWoWChange: wow, crowding, reportDate: latest.report_date_as_yyyy_mm_dd ?? null,
      openInterest, openInterestChange,
    }
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
  GBPUSD: 5, USDCAD: 5, USDSEK: 5,
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
  const SYMS = ['XAUUSD', 'XAGUSD', 'EURUSD', 'USDJPY', 'USDCHF', 'USDCNH', 'GBPUSD', 'USDCAD', 'USDSEK', 'US500', 'GER40', 'UK100']
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
      GBPUSD: mid('GBPUSD'), USDCAD: mid('USDCAD'), USDSEK: mid('USDSEK'),
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

// ── Finnhub economic calendar & news ───────────────────────────────────────

const FINNHUB_KEY = process.env.FINNHUB_API_KEY ?? ''
const HIGH_IMPACT_EVENTS = ['CPI', 'PCE', 'NFP', 'FOMC', 'ISM', 'GDP', 'PPI', 'Claims', 'JOLTS', 'Nonfarm', 'Federal Funds', 'Interest Rate']

type FinnhubEvent = {
  event: string
  time?: string
  impact?: string
  estimate?: number | null
  prev?: number | null
  actual?: number | null
  country?: string
  currency?: string
}

function normaliseImpact(raw: string | undefined, eventName: string): CalendarEvent['impact'] {
  if (!raw) {
    const name = eventName.toUpperCase()
    if (HIGH_IMPACT_EVENTS.some(k => name.includes(k.toUpperCase()))) return 'HIGH'
    return 'LOW'
  }
  const r = raw.toLowerCase()
  if (r === 'high' || r === '3') return 'HIGH'
  if (r === 'medium' || r === '2') return 'MEDIUM'
  return 'LOW'
}

// Today through Friday of the current week (UTC) — covers the rest of the trading
// week so the dashboard/briefing can flag "build-up caution" ahead of events that
// haven't happened yet, not just what's scheduled for today.
function weekAheadRange(): { from: string; to: string } {
  const now = new Date()
  const fmt = (d: Date) => d.toISOString().slice(0, 10)
  const day = now.getUTCDay() // 0=Sun, 1=Mon … 6=Sat
  // Sat(6)→6 days to next Fri, Sun(0)→5, Mon(1)→4 … Fri(5)→0
  const daysToFriday = day === 0 ? 5 : day === 6 ? 6 : 5 - day
  const friday = new Date(now)
  friday.setUTCDate(now.getUTCDate() + daysToFriday)
  return { from: fmt(now), to: fmt(friday) }
}

function daysBetween(dateStr: string, fromStr: string): number {
  const a = new Date(`${dateStr}T00:00:00Z`).getTime()
  const b = new Date(`${fromStr}T00:00:00Z`).getTime()
  return Math.round((a - b) / 86_400_000)
}

async function fetchEconomicCalendar(): Promise<CalendarEvent[]> {
  console.log('Fetching economic calendar (Finnhub)...')
  if (!FINNHUB_KEY) { console.log('Finnhub: FINNHUB_API_KEY env var not set — skipping calendar'); return [] }
  try {
    const { from, to } = weekAheadRange()
    const url = `https://finnhub.io/api/v1/calendar/economic?from=${from}&to=${to}&token=${FINNHUB_KEY}`
    const raw = await httpGet(url)
    const data = JSON.parse(raw) as { economicCalendar?: FinnhubEvent[] }
    if (!data.economicCalendar) return []
    return data.economicCalendar
      .filter(e => ['US', 'EU', 'GB', 'JP', 'EUR', 'USD', 'GBP', 'JPY'].some(c =>
        (e.country ?? e.currency ?? '').toUpperCase().includes(c)
      ))
      .map(e => {
        const date = e.time?.slice(0, 10) || from
        return {
          date,
          daysFromToday: daysBetween(date, from),
          time: e.time?.slice(11, 16) ?? '',
          event: e.event,
          impact: normaliseImpact(e.impact, e.event),
          currency: e.currency ?? e.country ?? 'US',
          forecast: e.estimate ?? null,
          previous: e.prev ?? null,
          actual: e.actual ?? null,
        } satisfies CalendarEvent
      })
      .sort((a, b) => (a.date + a.time).localeCompare(b.date + b.time))
  } catch (err) {
    console.error('Economic calendar fetch failed:', err)
    return []
  }
}

// Catches both scheduled-data-release catalysts (CPI, NFP) and unscheduled/rumor-driven
// catalysts (e.g. a "banks reduce dollar exposure" report moving DXY intraday) so the
// briefing can explain *why* price moved in the last few hours, not just what's on the
// calendar. Window is capped at 24h so stale headlines don't get reported as "recent."
const NEWS_KEYWORDS = [
  'gold', 'fed', 'inflation', 'yield', 'dollar', 'rate', 'powell', 'treasury',
  'central bank', 'reserve', 'diversif', 'tariff', 'sanction', 'geopolit',
  'safe haven', 'fx reserves', 'currency', 'recession', 'jobs report', 'payroll',
  'ecb', 'boj', 'pboc',
]
const NEWS_WINDOW_HOURS = 24

async function fetchNewsItems(): Promise<NewsItem[]> {
  console.log('Fetching news headlines (Finnhub)...')
  if (!FINNHUB_KEY) { console.log('Finnhub: FINNHUB_API_KEY env var not set — skipping headlines'); return [] }
  try {
    const raw = await httpGet(`https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}`)
    const data = JSON.parse(raw) as Array<{ headline: string; source?: string; datetime?: number }>
    const nowMs = Date.now()
    return data
      .filter(a => NEWS_KEYWORDS.some(k => a.headline.toLowerCase().includes(k)))
      .map(a => {
        const publishedMs = (a.datetime ?? 0) * 1000
        return {
          headline: a.headline,
          source: a.source ?? 'Finnhub',
          publishedAt: publishedMs ? new Date(publishedMs).toISOString() : '',
          hoursAgo: publishedMs ? Math.round((nowMs - publishedMs) / 3_600_000 * 10) / 10 : 999,
        } satisfies NewsItem
      })
      .filter(n => n.hoursAgo <= NEWS_WINDOW_HOURS)
      .sort((a, b) => a.hoursAgo - b.hoursAgo)
      .slice(0, 8)
  } catch (err) {
    console.error('News headlines fetch failed:', err)
    return []
  }
}

// ── Anthropic daily briefing ────────────────────────────────────────────────

const ANTHROPIC_KEY = process.env.ANTHROPIC_API_KEY ?? ''
const BRIEFING_MODEL = 'claude-sonnet-4-6'

const BRIEFING_SYSTEM_PROMPT = `You are a senior gold trading analyst and market intelligence advisor.
Your job is to write a daily intelligence briefing for a beginner day trader who uses ICT / Smart Money Concepts methodology to trade XAUUSD.

The trader only trades WITH the trend (buying into uptrends, selling into downtrends) using the 1H chart to determine trend direction, the 5M chart for signals, and the 1M chart for precise entry. They trade during the London and New York sessions.

You will receive a structured JSON snapshot of the current market data. The snapshot is refreshed roughly hourly during London/NY hours, so "recent" means since your last update, not necessarily since midnight.

The snapshot includes:
- `calendar`: this week's economic events, each tagged with `daysFromToday` (0 = today, 1+ = later this week). Events with `daysFromToday > 0` haven't happened yet — markets sometimes trade cautiously/range-bound in the days leading up to a major one (e.g. NFP, CPI, FOMC).
- `newsItems`: recent headlines (last 24h only), each tagged with `hoursAgo`. These include both scheduled-data headlines AND unscheduled/rumor-driven catalysts (central-bank rumors, reserve-diversification reports, tariffs, sanctions, geopolitical escalation) that can move the dollar and gold without being on any calendar.

Write a SINGLE flowing briefing paragraph (200–300 words) using PLAIN, BEGINNER-FRIENDLY language. Avoid jargon wherever possible. When you use a financial term, briefly explain what it means in brackets.

Your briefing MUST follow this structure within the single paragraph:
1. REGIME LINE: Which forces are most relevant right now and why.
2. RECENT CATALYSTS: Using `newsItems`, explicitly name any headline from the last few hours that plausibly explains a dollar or gold move (cite how many hours ago it broke). If nothing in `newsItems` looks market-moving, say so rather than inventing significance.
3. DIRECTIONAL BIAS with plain reasoning: Is price likely to favour gold going UP, DOWN, or being CHOPPY from here — and in simple terms, WHY.
4. CONFIDENCE SCORE: Express confidence in the bias as X/10. Explain what would change the view.
5. EVENT RISK: Any scheduled news today (when it hits GMT, what to expect), AND a build-up caution line if a HIGH-impact event is later this week (`daysFromToday` 1-4) — note that price may trade cautiously/range-bound into it.
6. KEY LEVELS: The most important price levels to watch from here. Use the ADR data to comment on how much move is likely remaining.
7. TRADE INTEGRATION: Explicit guidance on whether now is a good window for trend-following trades, what size/conviction is appropriate.

End with one sentence that a beginner can screenshot and remember.

CRITICAL RULES:
- Use plain English. Write as if explaining to a smart person who is new to financial markets.
- Never say "in conclusion" or "to summarise".
- Do NOT make up data. Only use what is in the JSON. If data is null or `newsItems`/`calendar` are empty, say so.
- Return your response as JSON:
  { "biasScore": number from -5 to +5 (negative = bearish, positive = bullish), "biasLabel": "BEARISH" | "NEUTRAL" | "BULLISH", "confidence": number 1-10, "briefing": "your paragraph here" }`

function computeDXY(eur: number, jpy: number, gbp: number, cad: number, sek: number, chf: number): number | null {
  if (eur <= 0 || jpy <= 0 || gbp <= 0 || cad <= 0 || sek <= 0 || chf <= 0) return null
  return parseFloat((50.14348
    * Math.pow(eur, -0.576)
    * Math.pow(jpy, 0.136)
    * Math.pow(gbp, -0.119)
    * Math.pow(cad, 0.091)
    * Math.pow(sek, 0.042)
    * Math.pow(chf, 0.036)).toFixed(2))
}

function getSessionLabel(utcH: number): string {
  if (utcH >= 13 && utcH < 16) return 'OVERLAP'
  if (utcH >= 8 && utcH < 16) return 'LONDON'
  if (utcH >= 16 && utcH < 21) return 'NEW_YORK'
  if (utcH >= 0 && utcH < 8) return 'ASIAN'
  return 'OFF'
}

async function generateDailyBriefing(snapshot: Omit<Snapshot, 'briefing'>): Promise<BriefingResult | null> {
  console.log('Generating daily briefing (Anthropic)...')
  if (!ANTHROPIC_KEY) { console.log('Anthropic: ANTHROPIC_API_KEY env var not set — skipping briefing'); return null }

  const sp = snapshot.snapshotPrices
  const payload = {
    timestamp: new Date().toISOString(),
    session: getSessionLabel(new Date().getUTCHours()),
    prices: {
      XAUUSD: sp?.XAUUSD ?? null,
      XAGUSD: sp?.XAGUSD ?? null,
      goldSilverRatio: sp?.goldSilverRatio ?? null,
      DXY: sp ? computeDXY(sp.EURUSD ?? 0, sp.USDJPY ?? 0, sp.GBPUSD ?? 0, sp.USDCAD ?? 0, sp.USDSEK ?? 0, sp.USDCHF ?? 0) : null,
      EURUSD: sp?.EURUSD ?? null,
      USDJPY: sp?.USDJPY ?? null,
      USDCHF: sp?.USDCHF ?? null,
      USDCNH: sp?.USDCNH ?? null,
      ADR_14day: sp?.ADR_14day ?? null,
      ADR_usedToday: sp?.ADR_usedToday ?? null,
    },
    yields: snapshot.yields,
    fedExpectations: snapshot.fedExpectations,
    marketVolatility: snapshot.marketVolatility,
    positioning: snapshot.positioning,
    etfFlows: snapshot.etfFlows,
    dollarLiquidity: snapshot.dollarLiquidity,
    geopoliticalRisk: snapshot.geopoliticalRisk,
    calendar: snapshot.economicCalendar,
    newsItems: snapshot.newsItems,
  }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: BRIEFING_MODEL,
        max_tokens: 1200,
        system: BRIEFING_SYSTEM_PROMPT,
        messages: [
          { role: 'user', content: `Here is today's market data snapshot:\n\n${JSON.stringify(payload, null, 2)}` },
        ],
      }),
    })

    if (!response.ok) {
      console.error(`Anthropic API error ${response.status}: ${(await response.text()).slice(0, 200)}`)
      return null
    }

    const body = await response.json() as { content: Array<{ type: string; text: string }> }
    const text = body.content.find(c => c.type === 'text')?.text ?? ''
    const cleaned = text.replace(/^```json?\s*/i, '').replace(/\s*```$/, '').trim()
    const parsed = JSON.parse(cleaned) as Omit<BriefingResult, 'generatedAt'>
    console.log(`Briefing generated: bias=${parsed.biasLabel} score=${parsed.biasScore} confidence=${parsed.confidence}`)
    return { ...parsed, generatedAt: new Date().toISOString() }
  } catch (err) {
    console.error('Briefing generation failed:', err)
    return null
  }
}

// ── Geopolitical Risk Index (Caldara-Iacoviello) ───────────────────────────

async function fetchGPR(): Promise<Snapshot['geopoliticalRisk']> {
  console.log('Fetching GPR (Geopolitical Risk Index)...')
  try {
    const res = await fetch('https://www.matteoiacoviello.com/gpr_files/data_gpr_export.xls')
    if (!res.ok) { console.log(`GPR HTTP ${res.status}`); return { gpr: null, gprDate: null } }
    const buf = Buffer.from(await res.arrayBuffer())
    const XLSX = await import('xlsx')
    const wb = XLSX.read(buf, { type: 'buffer' })
    const sheet = wb.Sheets[wb.SheetNames[0]]
    const rows = XLSX.utils.sheet_to_json<Record<string, unknown>>(sheet)
    if (!rows.length) throw new Error('empty GPR sheet')
    const last = rows[rows.length - 1]
    const gpr = typeof last.GPR === 'number' ? Math.round(last.GPR * 10) / 10 : null
    // "month" is an Excel date serial (days since 1899-12-30)
    const monthSerial = last.month
    const gprDate = typeof monthSerial === 'number'
      ? new Date(Date.UTC(1899, 11, 30) + monthSerial * 86400000).toISOString().slice(0, 7)
      : null
    console.log(`GPR: ${gpr} (${gprDate})`)
    return { gpr, gprDate }
  } catch (err) {
    console.error('GPR fetch failed:', err)
    return { gpr: null, gprDate: null }
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

  const [yields, fedExpectations, gvz, vix, stlfsi, nfci, positioning, snapshotPrices, geopoliticalRisk, economicCalendar, newsItems] = await Promise.all([
    fetchYields(),
    fetchFedWatch(),
    fetchGVZ(),
    fredSeries('VIXCLS'),
    fredSeries('STLFSI4'),
    fredSeries('NFCI'),
    fetchCOT(existing),
    fetchCTraderPrices(),
    fetchGPR(),
    fetchEconomicCalendar(),
    fetchNewsItems(),
  ])
  console.log(`VIX FRED VIXCLS: ${vix}, STLFSI4: ${stlfsi}, NFCI: ${nfci}`)

  // GLD needs the CTrader XAUUSD price as a fallback if FRED's gold series is null,
  // so it runs after the prices above rather than inside the initial Promise.all.
  const etfFlows = await fetchGLD(snapshotPrices?.XAUUSD ?? null)

  const snapshotWithoutBriefing: Omit<Snapshot, 'briefing'> = {
    generatedAt: new Date().toISOString(),
    yields,
    fedExpectations,
    marketVolatility: { GVZ: gvz, VIX: vix },
    positioning,
    etfFlows,
    snapshotPrices,
    dollarLiquidity: { stlfsi, nfci },
    geopoliticalRisk,
    economicCalendar,
    newsItems,
  }

  // Briefing runs last — it summarises everything fetched above.
  const briefing = await generateDailyBriefing(snapshotWithoutBriefing)
  const snapshot: Snapshot = { ...snapshotWithoutBriefing, briefing }

  fs.writeFileSync(outPath, JSON.stringify(snapshot, null, 2))
  console.log(`\nSnapshot written to ${outPath}`)
  console.log(`Generated at: ${snapshot.generatedAt}`)
  console.log(`10Y yield: ${yields.US10Y ?? 'null'}%`)
  console.log(`GVZ: ${gvz ?? 'null'}`)
  console.log(`GLD: ${etfFlows.gldTonnes ?? 'null'}t`)
  console.log(`COT net: ${positioning.cotNetLong ?? 'null'}`)
  console.log(`XAUUSD price: ${snapshotPrices?.XAUUSD ?? 'null'}`)
  console.log(`Calendar events (week): ${economicCalendar.length}, news items (24h): ${newsItems.length}`)
  console.log(`Briefing: ${briefing ? `${briefing.biasLabel} ${briefing.biasScore} (conf ${briefing.confidence})` : 'null'}`)
}

main().catch(err => {
  console.error('Fatal error in data fetch:', err)
  process.exit(1)
})
