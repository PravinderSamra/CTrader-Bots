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

// ── CBOE GVZ ──────────────────────────────────────────────────────────────

async function fetchGVZ(): Promise<number | null> {
  console.log('Fetching CBOE GVZ...')
  try {
    // CBOE delayed quotes JSON (GVZ = Gold Volatility Index)
    const raw = await httpGet('https://cdn.cboe.com/api/global/delayed_quotes/charts/historical/_VIX.json')
    // Try GVZ endpoint
    const gvzRaw = await httpGet('https://cdn.cboe.com/api/global/delayed_quotes/charts/historical/GVZ.json')
    const data = JSON.parse(gvzRaw) as {
      data?: Array<{ datetime?: string; close?: number; price?: number }>
      currentPrice?: number
    }
    if (data.currentPrice) return data.currentPrice
    const rows = data.data ?? []
    if (rows.length > 0) {
      const last = rows[rows.length - 1]
      return last.close ?? last.price ?? null
    }
    void raw // suppress unused warning
    return null
  } catch {
    try {
      // Fallback: scrape CBOE page
      const html = await httpGet('https://www.cboe.com/us/indices/dashboard/gvz/', { Accept: 'text/html' })
      const match = html.match(/GVZ[^>]*>[\s\S]{0,200}?(\d+\.\d+)/i)
      return match ? parseFloat(match[1]) : null
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
  let prevTonnesWeek: number | null = null

  // Read previous value for WoW calculation
  try {
    const prev = JSON.parse(fs.readFileSync(outPath, 'utf8')) as { etfFlows?: { gldTonnes?: number; gldTonnesWeek?: number } }
    prevTonnes = prev.etfFlows?.gldTonnes ?? null
    prevTonnesWeek = (prev as { etfFlows?: { gldTonnesWeek?: number } }).etfFlows?.gldTonnesWeek ?? null
  } catch { /* first run */ }

  try {
    const html = await httpGet('https://www.spdrgoldshares.com/usa/gold/en/', {
      Accept: 'text/html',
      Referer: 'https://www.spdrgoldshares.com',
    })
    // Find "Tonnes" figure in the holdings table
    const match = html.match(/(\d[\d,]+\.\d+)\s*(?:tonnes|Tonnes|TONNES)/i)
      ?? html.match(/(?:Gold Holdings|Ounces)\D{0,40}(\d[\d,]+\.\d+)/i)
    const tonnes = match ? parseFloat(match[1].replace(/,/g, '')) : null
    const wow = tonnes != null && prevTonnes != null
      ? parseFloat((tonnes - prevTonnes).toFixed(2))
      : null

    // 3-week trend requires 3 data points — approximate from WoW direction
    let trend: Snapshot['etfFlows']['trend3W'] = null
    if (wow != null) trend = wow > 0.5 ? 'INFLOW' : wow < -0.5 ? 'OUTFLOW' : 'FLAT'
    void prevTonnesWeek

    return { gldTonnes: tonnes, gldWoWChange: wow, trend3W: trend }
  } catch {
    return { gldTonnes: prevTonnes, gldWoWChange: null, trend3W: null }
  }
}

// ── CFTC COT data ─────────────────────────────────────────────────────────

async function fetchCOT(existingSnapshot: Partial<Snapshot>): Promise<Snapshot['positioning']> {
  console.log('Fetching CFTC COT data...')
  const today = new Date()
  const dayOfWeek = today.getUTCDay() // 0=Sun, 5=Fri

  // COT releases Fridays; if we have recent data and it's not Friday, skip re-fetch
  const reportDate = existingSnapshot.positioning?.reportDate
  if (reportDate) {
    const reportAge = (today.getTime() - new Date(reportDate).getTime()) / (1000 * 60 * 60 * 24)
    if (reportAge < 7 && dayOfWeek !== 5) {
      console.log('COT data fresh, skipping re-fetch')
      return existingSnapshot.positioning!
    }
  }

  try {
    // CFTC legacy futures CSV for financial instruments
    const url = 'https://www.cftc.gov/dea/futures/deacmesf.htm'
    const html = await httpGet(url)
    // Extract gold row — COMEX gold futures
    const goldMatch = html.match(/GOLD[^\n]{0,2000}?(\d[\d,]+)\s*(\d[\d,]+)\s*(\d[\d,]+)/i)
    if (!goldMatch) return existingSnapshot.positioning ?? { cotNetLong: null, cotWoWChange: null, crowding: null, reportDate: null }

    const longPos  = parseInt(goldMatch[1].replace(/,/g, ''))
    const shortPos = parseInt(goldMatch[2].replace(/,/g, ''))
    const net      = longPos - shortPos
    const prevNet  = existingSnapshot.positioning?.cotNetLong ?? null
    const wow      = prevNet != null ? net - prevNet : null

    // Crowding threshold: top/bottom 20% of historical range (approximate)
    const crowding: Snapshot['positioning']['crowding'] = net > 200000 ? 'CROWDED_LONG' : net < 100000 ? 'CROWDED_SHORT' : 'NEUTRAL'

    return {
      cotNetLong: net,
      cotWoWChange: wow,
      crowding,
      reportDate: today.toISOString().slice(0, 10),
    }
  } catch {
    return existingSnapshot.positioning ?? { cotNetLong: null, cotWoWChange: null, crowding: null, reportDate: null }
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

  const [yields, fedExpectations, gvz, etfFlows, positioning] = await Promise.all([
    fetchYields(),
    fetchFedWatch(),
    fetchGVZ(),
    fetchGLD(),
    fetchCOT(existing),
  ])

  const snapshot: Snapshot = {
    generatedAt: new Date().toISOString(),
    yields,
    fedExpectations,
    marketVolatility: { GVZ: gvz },
    positioning,
    etfFlows,
  }

  fs.writeFileSync(outPath, JSON.stringify(snapshot, null, 2))
  console.log(`\nSnapshot written to ${outPath}`)
  console.log(`Generated at: ${snapshot.generatedAt}`)
  console.log(`10Y yield: ${yields.US10Y ?? 'null'}%`)
  console.log(`GVZ: ${gvz ?? 'null'}`)
  console.log(`GLD: ${etfFlows.gldTonnes ?? 'null'}t`)
  console.log(`COT net: ${positioning.cotNetLong ?? 'null'}`)
}

main().catch(err => {
  console.error('Fatal error in data fetch:', err)
  process.exit(1)
})
