#!/usr/bin/env tsx
/**
 * UK100 Data Fetcher — Phases 2a/2e of UK100-BUILD-PLAN.md.
 * Runs as an additional step inside the existing xauusd-daily-fetch.yml workflow
 * (hourly, 06:00-20:00 GMT Mon-Fri), with continue-on-error so a UK100 failure
 * never blocks the gold snapshot.
 *
 * Fetches: cTrader UK100/GBP/US-linkage/commodity prices + bars, BoE IADB gilt
 * strip, FRED context series, GBP COT (FTSE proxy), Finnhub calendar/news.
 * Computes the mechanical bias engine (§5 of the plan) and ORB context (§6.1).
 * Anthropic risk-tone classifier (news → score/label/rationale) feeds the bias
 * engine's "Risk tone" driver, and the Anthropic daily briefing runs last over
 * the fully-assembled snapshot — same two-call pattern as fetch-static-data.ts's
 * gold briefing. Both are null when ANTHROPIC_API_KEY is absent (the bias
 * engine treats a null risk-tone component as 0, same as before Phase 2e).
 *
 * Each fetch is wrapped in try/catch — partial failures write null, never crash.
 * Writes xauusd-dashboard/public/data/uk100/daily-snapshot.json
 */

import * as fs from 'fs'
import * as path from 'path'
import * as https from 'https'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, PIP_DIGITS, type Trendbar } from './lib/ctrader'
import { mergeCalendars, nextMpcDate, UK_STATIC_CALENDAR_2026, US_STATIC_CALENDAR_2026, type Uk100CalendarEvent } from './lib/calendar'
import { pearson, dailyReturnsByDate, pairByDate } from './lib/stats'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

// ── Types (local to this script — src/types/uk100.ts is the canonical UI copy,
//    wired in Phase 2b; scripts intentionally keep their own type copies, same
//    convention as fetch-static-data.ts's local Snapshot interface) ──────────

type FtseImpact = 'BULLISH' | 'BEARISH' | 'NEUTRAL'

interface Uk100Prices {
  UK100: number | null; GBPUSD: number | null; GBPEUR: number | null
  US500: number | null; NAS100: number | null; BRENT: number | null; COPPER: number | null
  VIX: number | null; USDX: number | null; XAUUSD: number | null
  UK100_dayPct: number | null
}

interface FxBlock {
  gbpUsdDayPct: number | null
  gbpUsd20dPercentile: number | null
  sterlingEri: number | null
  sterlingEriDayChange: number | null
  ftseImpactFromGbp: FtseImpact
}

interface UkRatesBlock {
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

interface UsLinkageBlock {
  us500DayPct: number | null; nas100DayPct: number | null
  vix: number | null
  vixRegime: 'CALM' | 'NORMAL' | 'STRESS'
  us10y: number | null
  usdx: number | null
}

interface CommoditiesBlock {
  brentDayPct: number | null; copperDayPct: number | null; goldDayPct: number | null
  brent20dTrend: 'UP' | 'DOWN' | 'FLAT'
}

// European-tape driver (UK100-SESSION-REVIEW-2026-07-13.md §4A/F8) — Euro
// Stoxx 50 as the primary European-tape read (measured r=0.68-0.75 vs UK100,
// tied-best correlate and the pan-Eurozone benchmark), GER40 as the second
// tape for the agreement/divergence signal.
interface EuropeanTapeBlock {
  eurostoxx50DayPct: number | null; dax40DayPct: number | null
  eurUsdDayPct: number | null
  ftseDaxCorr20d: number | null; ftseSx5eCorr20d: number | null
  tapeAgreement: 'ALIGNED' | 'SPLIT' | 'DIVERGING'
  preOpenLead: 'UP' | 'DOWN' | 'NONE'
}

interface PositioningBlock {
  gbpCotNetLong: number | null; gbpCotWoWChange: number | null
  crowding: 'CROWDED_LONG' | 'CROWDED_SHORT' | 'BALANCED' | null
  reportDate: string | null
  ftseReadthrough: FtseImpact
}

interface SectorRead {
  sector: 'ENERGY' | 'MINERS' | 'BANKS' | 'PHARMA' | 'STAPLES'
  weightNote: string
  driver: string
  read: FtseImpact | 'IDIOSYNCRATIC'
  detail: string
}

interface Uk100NewsItem { headline: string; source: string; hoursAgo: number; url?: string }

interface BiasDriver { name: string; impact: FtseImpact; weight: number; detail: string }

interface BiasBlock {
  score: number
  label: 'BULLISH' | 'BEARISH' | 'NEUTRAL'
  conviction: 'LOW' | 'MEDIUM' | 'HIGH'
  drivers: BiasDriver[]
  eventSuppressed: boolean
}

interface OrbContext {
  computedAt: string
  mode: 'PRE_OPEN' | 'ORB_FORMING' | 'POST_ORB' | 'CLOSED'
  cashOpenLondon: string
  overnightHigh: number | null; overnightLow: number | null
  priorDayHigh: number | null; priorDayLow: number | null; priorClose: number | null
  prevWeekHigh: number | null; prevWeekLow: number | null
  gapPts: number | null; gapPct: number | null
  orbHigh: number | null; orbLow: number | null
  orbBrokenDirection: 'UP' | 'DOWN' | 'NONE' | null
  eventWindows: { event: string; timeLondon: string; impact: string }[]
  adr14: number | null; adrUsedPct: number | null
}

// ── ORB intelligence (G1, UK100-ORB-INTEL-TLDR-DESIGN.md §2) — a synthesis
//    layer over the fields the snapshot already carries. Layer 1 (mechanical
//    computeOrbIntel) always renders; Layer 2 (aiStanceLine/aiBullets) comes
//    from the existing briefing call in G2 and is null/[] without an API key.
type OrbIntelDirection = 'FAVOURS_LONG' | 'FAVOURS_SHORT' | 'BREAKOUT_SUSPECT' | 'NEUTRAL'
type OrbIntelSeverity  = 'INFO' | 'CAUTION' | 'STRONG'
type OrbIntelSource    =
  'STRUCTURE' | 'RANGE' | 'GAP' | 'TAPE' | 'FX' | 'RATES' | 'POSITIONING' | 'EVENT' | 'AI'

interface OrbIntelSignal {
  direction: OrbIntelDirection
  severity:  OrbIntelSeverity
  source:    OrbIntelSource
  text:      string
}

type OrbIntelStance =
  'LONG_FAVOURED' | 'SHORT_FAVOURED' | 'FADE_FAVOURED' | 'BREAKOUTS_SUSPECT' | 'MIXED'

interface OrbIntel {
  stance:       OrbIntelStance
  stanceLine:   string
  signals:      OrbIntelSignal[]
  aiStanceLine: string | null
  aiBullets:    string[]
  baseRateNote: string | null
}

interface Uk100Snapshot {
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
  riskTone: { score: number; label: FtseImpact; rationale: string } | null
  bias: BiasBlock
  orbContext: OrbContext
  orbIntel: OrbIntel
  briefing: { biasScore: number; biasLabel: string; confidence: number; briefing: string; generatedAt: string } | null
}

// ── HTTP helper (same pattern as fetch-static-data.ts) ─────────────────────

function httpGet(url: string, headers: Record<string, string> = {}): Promise<string> {
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

// ── London wall-clock (DST) helper — same rule as save-gold-session.ts's
//    ukOffsetHours; duplicated locally per this repo's convention that scripts
//    stay self-contained rather than cross-importing from each other. ────────

function londonOffsetHours(d: Date): number {
  const m = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  if (m > 3 && m < 10) return 1
  if (m === 3 && day >= 25) return 1
  if (m === 10 && day < 25) return 1
  return 0
}

function londonNow(): Date {
  const now = new Date()
  return new Date(now.getTime() + londonOffsetHours(now) * 3_600_000)
}

// ISO-week key (e.g. "2026-W28") for a London-local Date (UTC fields hold the
// London wall clock). Used by fetchCtraderData to bucket D_1 bars into weeks
// for the previous-week high/low (F-E of UK100-ORB-INTEL-TLDR-DESIGN.md).
export function isoWeekKey(d: Date): string {
  const date = new Date(Date.UTC(d.getUTCFullYear(), d.getUTCMonth(), d.getUTCDate()))
  const dayNum = (date.getUTCDay() + 6) % 7            // Mon=0 … Sun=6
  date.setUTCDate(date.getUTCDate() - dayNum + 3)      // move to the week's Thursday
  const firstThursday = new Date(Date.UTC(date.getUTCFullYear(), 0, 4))
  const firstDayNum = (firstThursday.getUTCDay() + 6) % 7
  firstThursday.setUTCDate(firstThursday.getUTCDate() - firstDayNum + 3)
  const week = 1 + Math.round((date.getTime() - firstThursday.getTime()) / (7 * 86_400_000))
  return `${date.getUTCFullYear()}-W${String(week).padStart(2, '0')}`
}

// ISO-week key for a D_1 bar's TRADING day. cTrader stamps UK100 D_1 bars at
// the session open — 21:00 UTC of the PRIOR calendar day (22:00 London BST;
// verified 2026-07-15 against live bars: Monday 06 Jul's bar is stamped
// Sun 05 Jul 21:00Z). Bucketing the raw stamp therefore throws every Monday
// bar into the previous ISO week (Sunday is that week's last day). Shifting
// +12h maps a 21:00/22:00-prior-day stamp onto its actual trading day (and is
// a no-op for a 00:00-same-day convention), so the week bucket is right under
// either stamping scheme.
export function tradingDayIsoWeekKey(tsMs: number): string {
  return isoWeekKey(new Date(tsMs + 12 * 3_600_000))
}

function londonTimeLabel(iso: string): string {
  const d = new Date(iso)
  const offsetH = londonOffsetHours(d)
  const ld = new Date(d.getTime() + offsetH * 3_600_000)
  const hh = String(ld.getUTCHours()).padStart(2, '0')
  const mm = String(ld.getUTCMinutes()).padStart(2, '0')
  return `${hh}:${mm} ${offsetH === 1 ? 'BST' : 'GMT'}`
}

// ── D10: the GBP sign-flip — single tested function, every tile/component
//    that needs the FTSE read from a GBP move calls this, never inline logic.
export function ftseImpact(gbpMovePct: number | null): FtseImpact {
  if (gbpMovePct == null) return 'NEUTRAL'
  if (gbpMovePct <= -0.5) return 'BULLISH'   // weak GBP lifts FTSE
  if (gbpMovePct >= 0.5) return 'BEARISH'    // strong GBP weighs on FTSE
  return 'NEUTRAL'
}

// ── FRED (same pattern as fetch-static-data.ts) ─────────────────────────────

const FRED_KEY = process.env.FRED_API_KEY ?? ''

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

async function fredTrend(id: string, limit = 20, thresholdPct = 1): Promise<'UP' | 'DOWN' | 'FLAT'> {
  if (!FRED_KEY) return 'FLAT'
  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${id}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=${limit}`
    const raw = await httpGet(url)
    const data = JSON.parse(raw) as { observations?: Array<{ value: string }> }
    const obs = (data.observations?.filter(o => o.value !== '.') ?? []).map(o => parseFloat(o.value))
    if (obs.length < 2) return 'FLAT'
    const newest = obs[0]; const oldest = obs[obs.length - 1]
    if (!oldest) return 'FLAT'
    const pct = (newest - oldest) / oldest * 100
    if (pct >= thresholdPct) return 'UP'
    if (pct <= -thresholdPct) return 'DOWN'
    return 'FLAT'
  } catch {
    return 'FLAT'
  }
}

async function fredPercentile20d(id: string, current: number | null): Promise<number | null> {
  if (!FRED_KEY || current == null) return null
  try {
    const url = `https://api.stlouisfed.org/fred/series/observations?series_id=${id}&api_key=${FRED_KEY}&file_type=json&sort_order=desc&limit=20`
    const raw = await httpGet(url)
    const data = JSON.parse(raw) as { observations?: Array<{ value: string }> }
    const obs = (data.observations?.filter(o => o.value !== '.') ?? []).map(o => parseFloat(o.value))
    if (obs.length < 5) return null
    const below = obs.filter(v => v <= current).length
    return Math.round(below / obs.length * 100)
  } catch {
    return null
  }
}

// ── BoE IADB — keyless daily CSV, six verified series codes (§1.2). One bad
//    code fails the WHOLE request, so only ever request exactly these six. ──

const BOE_CODES = {
  bankRate: 'IUDBEDR', sonia: 'IUDSOIA', sterlingEri: 'XUDLBK67',
  gilt5y: 'IUDSNZC', gilt10y: 'IUDMNZC', gilt20y: 'IUDLNZC',
} as const

interface BoeRow { date: string; values: Record<string, number> }

async function fetchBoeIadb(): Promise<BoeRow[]> {
  console.log('Fetching BoE IADB gilt/rates strip...')
  try {
    const now = new Date()
    const from = new Date(now.getTime() - 30 * 24 * 3600 * 1000)
    const fmtBoe = (d: Date) => {
      const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
      return `${String(d.getUTCDate()).padStart(2, '0')}/${months[d.getUTCMonth()]}/${d.getUTCFullYear()}`
    }
    const codes = Object.values(BOE_CODES)
    const url = `https://www.bankofengland.co.uk/boeapps/database/_iadb-fromshowcolumns.asp?csv.x=yes&UsingCodes=Y&CSVF=TN&Datefrom=${fmtBoe(from)}&Dateto=${fmtBoe(now)}&SeriesCodes=${codes.join(',')}`
    const raw = await httpGet(url)
    const lines = raw.trim().split(/\r?\n/)
    if (lines.length < 2) throw new Error('empty BoE IADB response')
    const header = lines[0].split(',').map(h => h.trim())
    const rows: BoeRow[] = []
    for (const line of lines.slice(1)) {
      const cells = line.split(',')
      if (cells.length < 2) continue
      const values: Record<string, number> = {}
      for (let i = 1; i < header.length; i++) {
        const v = parseFloat(cells[i])
        if (!isNaN(v)) values[header[i]] = v
      }
      rows.push({ date: cells[0].trim(), values })
    }
    console.log(`BoE IADB: ${rows.length} rows`)
    return rows
  } catch (err) {
    console.error('BoE IADB fetch failed:', err)
    return []
  }
}

function boeLatestTwo(rows: BoeRow[], code: string): [number | null, number | null] {
  const withValue = rows.filter(r => r.values[code] != null)
  if (withValue.length === 0) return [null, null]
  const cur = withValue[withValue.length - 1].values[code]
  const prev = withValue.length >= 2 ? withValue[withValue.length - 2].values[code] : null
  return [cur, prev]
}

// ── cTrader — prices + bars for UK100 and the driver symbols (§1.1) ────────

const UK100_SYMS = ['UK100', 'GBPUSD', 'EURGBP', 'US500', 'NAS100', 'BRENT', 'COPPER', 'VIX', 'USDX', 'XAUUSD', 'GER40', 'EUSTX50', 'EURUSD']

interface CtraderResult {
  prices: Uk100Prices
  priorDayHigh: number | null; priorDayLow: number | null; priorClose: number | null
  prevWeekHigh: number | null; prevWeekLow: number | null
  overnightHigh: number | null; overnightLow: number | null
  orbHigh: number | null; orbLow: number | null
  postOrbCloses: number[]
  adr14: number | null; adrUsedPct: number | null
  us500DayPct: number | null; nas100DayPct: number | null
  brentDayPct: number | null; copperDayPct: number | null; goldDayPct: number | null
  gbpUsdDayPct: number | null
  ger40DayPct: number | null; eustx50DayPct: number | null; eurUsdDayPct: number | null
  ftseDaxCorr20d: number | null; ftseSx5eCorr20d: number | null
  tapeAgreement: EuropeanTapeBlock['tapeAgreement']
  preOpenLead: EuropeanTapeBlock['preOpenLead']
}

async function fetchCtraderData(): Promise<CtraderResult | null> {
  console.log('Fetching cTrader UK100 prices + bars...')
  const client = new CTraderClient()
  if (!client.hasToken()) { console.log('CTrader: no token — skipping'); return null }
  const ok = await client.init()
  if (!ok) { console.error('CTrader: init failed'); return null }

  try {
    const idFor = (s: string) => KNOWN_SYMBOL_IDS[s]
    const ids = UK100_SYMS.map(idFor).filter((id): id is number => id != null)
    const spotRaw = await client.callTool('get_spot_prices', { symbolId: ids })
    const spots = (spotRaw as { prices?: Array<{ symbolId: number; bid?: number; ask?: number }> })?.prices ?? []
    const spotMap = new Map(spots.map(s => [s.symbolId, s]))

    const pip = (sym: string) => PIP_DIGITS[sym] ?? 5
    const mid = (sym: string): number | null => {
      const id = idFor(sym); if (!id) return null
      const sp = spotMap.get(id); if (!sp) return null
      const bid = sp.bid ?? 0; const ask = sp.ask ?? bid
      if (!bid && !ask) return null
      return parseFloat(((bid + ask) / 2 / 10 ** pip(sym)).toFixed(pip(sym)))
    }

    const uk100Mid = mid('UK100')
    const gbpUsd = mid('GBPUSD')
    const eurGbp = mid('EURGBP')

    const uk100Id = idFor('UK100')
    let priorDayHigh: number | null = null, priorDayLow: number | null = null, priorClose: number | null = null
    let prevWeekHigh: number | null = null, prevWeekLow: number | null = null
    let overnightHigh: number | null = null, overnightLow: number | null = null
    let orbHigh: number | null = null, orbLow: number | null = null
    let adr14: number | null = null, adrUsedPct: number | null = null
    let uk100D1Bars: Trendbar[] = []
    let postOrbCloses: number[] = []

    if (uk100Id) {
      const now = Date.now()
      // D_1 bars — prior-day levels + ADR14. Widened from 20->30 calendar
      // days (F8, UK100-SESSION-REVIEW-2026-07-13.md) so the European-tape
      // correlation below has enough overlapping trading days after UK/DE/EU
      // holiday mismatches — the prior-day/ADR14 logic just below is
      // end-relative (.slice(-15,-1), [len-2]) so the wider window is a no-op
      // for it. 30 IS THE MAX: live-verified 2026-07-13 that get_trendbars
      // D_1 silently rejects (returns 0 bars, logs a "Time range" parse
      // failure) any window over 30 calendar days — 30 gives 21 bars, 31
      // gives 0. UK100-V2-PLAN.md's D1 spec (not yet built) proposed 32 days
      // for the same reason; that number needs correcting to 30 when D1 is
      // implemented.
      const d1Bars = await client.getTrendbars(uk100Id, 'D_1', now - 30 * 24 * 3600 * 1000, now)
      uk100D1Bars = d1Bars
      if (d1Bars.length >= 2) {
        const prior = d1Bars[d1Bars.length - 2]
        priorDayHigh = prior.high / 1e5
        priorDayLow  = prior.low / 1e5
        priorClose   = prior.close / 1e5
        const recent = d1Bars.slice(-15, -1) // last 14 completed days
        if (recent.length > 0) {
          const ranges = recent.map(b => (b.high - b.low) / 1e5)
          adr14 = Math.round(ranges.reduce((a, b) => a + b, 0) / ranges.length * 10) / 10
        }
        const today = d1Bars[d1Bars.length - 1]
        if (today && adr14) {
          adrUsedPct = Math.round((today.high - today.low) / 1e5 / adr14 * 100)
        }

        // Previous-ISO-week high/low (F-E) — bucket the D_1 bars by their
        // TRADING day's ISO week (tradingDayIsoWeekKey compensates for the
        // 21:00Z-prior-day session-open stamp, which otherwise threw every
        // Monday bar into the previous week — caught in the G1 review), take
        // the week before the current one. Null when fewer than 3 bars land
        // in it (holiday-shortened week / thin data).
        const prevWeekKey = isoWeekKey(new Date(londonNow().getTime() - 7 * 86_400_000))
        const prevWeekBars = d1Bars.filter(b => tradingDayIsoWeekKey(b.timestamp) === prevWeekKey)
        if (prevWeekBars.length >= 3) {
          prevWeekHigh = Math.max(...prevWeekBars.map(b => b.high)) / 1e5
          prevWeekLow  = Math.min(...prevWeekBars.map(b => b.low)) / 1e5
        }
      }

      // Overnight range (22:00 prev London → 08:00 today London) + ORB
      // (08:00-08:15 today). The MCP caps get_trendbars at 100 bars PER CALL
      // regardless of the requested window (verified 2026-07-10: a 36h M5
      // request and a 10h M5 request both silently truncated to the newest 100
      // bars) — a single bulk M5 fetch + bar-count slicing under-covers the
      // 10h overnight window. Fixed by requesting each window with its own
      // EXACT from/to timestamps: H_1 for the overnight range (10 bars, only
      // need high/low, well under the cap) and a precisely-bounded M5 call for
      // the 15-minute ORB itself (3 bars).
      const ld = londonNow()
      const offsetH = londonOffsetHours(new Date())
      const londonMidnightUtc = Date.UTC(ld.getUTCFullYear(), ld.getUTCMonth(), ld.getUTCDate()) - offsetH * 3_600_000
      const cashOpenMs = londonMidnightUtc + 8 * 3_600_000
      const orbEndMs   = londonMidnightUtc + 8.25 * 3_600_000
      const overnightStartMs = cashOpenMs - 10 * 3_600_000 // 22:00 prev day London

      if (now >= overnightStartMs) {
        const onTo = Math.min(now, cashOpenMs)
        const onBars = await client.getTrendbars(uk100Id, 'H_1', overnightStartMs, onTo)
        if (onBars.length > 0) {
          overnightHigh = Math.max(...onBars.map(b => b.high)) / 1e5
          overnightLow  = Math.min(...onBars.map(b => b.low)) / 1e5
        }
      }
      if (now >= orbEndMs) {
        const orbBars = await client.getTrendbars(uk100Id, 'M_5', cashOpenMs, orbEndMs)
        if (orbBars.length > 0) {
          orbHigh = Math.max(...orbBars.map(b => b.high)) / 1e5
          orbLow  = Math.min(...orbBars.map(b => b.low)) / 1e5
        }
      }

      // B3 (UK100-V2-PLAN.md §4): post-ORB M5 closes, 08:15 -> 16:30 London
      // (99 bars, under the 100-bar cap), so orbBrokenDirection below can be
      // the engine's own "first M5 close outside the range, sticky" rule
      // instead of a current-price snapshot that flips back to NONE on any
      // later reclaim (UK100-SESSION-REVIEW-2026-07-13.md §3.10 — live proof
      // 2026-07-13: the hourly snapshot would have flipped DOWN -> NONE on
      // an intrabar reclaim while the engine correctly held DOWN).
      const postOrbCapMs = londonMidnightUtc + 16.5 * 3_600_000
      if (now >= cashOpenMs + 20 * 60 * 1000) {
        const postOrbBars = await client.getTrendbars(uk100Id, 'M_5', orbEndMs, Math.min(now, postOrbCapMs))
        postOrbCloses = postOrbBars.map(b => b.close / 1e5)
      }
    }

    const dayPct = (cur: number | null, prior: number | null) =>
      cur != null && prior ? Math.round((cur - prior) / prior * 10000) / 100 : null

    // European-tape driver (F8): Euro Stoxx 50 primary, GER40 secondary. One
    // wide D_1 fetch per symbol serves both day% (last two bars) and the
    // 20-day rolling correlation against UK100's own D_1 series above — no
    // second, narrower fetch needed.
    const ger40Id = idFor('GER40')
    const eustx50Id = idFor('EUSTX50')
    const ger40D1Bars = ger40Id ? await client.getTrendbars(ger40Id, 'D_1', Date.now() - 30 * 24 * 3600 * 1000, Date.now()) : []
    const eustx50D1Bars = eustx50Id ? await client.getTrendbars(eustx50Id, 'D_1', Date.now() - 30 * 24 * 3600 * 1000, Date.now()) : []

    const ger40DayPct = ger40D1Bars.length >= 2
      ? dayPct(mid('GER40'), ger40D1Bars[ger40D1Bars.length - 2].close / 1e5) : null
    const eustx50DayPct = eustx50D1Bars.length >= 2
      ? dayPct(mid('EUSTX50'), eustx50D1Bars[eustx50D1Bars.length - 2].close / 1e5) : null

    const toDated = (bars: Trendbar[]) => bars.map(b => ({ timestamp: b.timestamp, close: b.close / 1e5 }))
    const uk100Returns = dailyReturnsByDate(toDated(uk100D1Bars))
    const ftseDaxCorr20d = ger40D1Bars.length
      ? (() => { const { xs, ys } = pairByDate(uk100Returns, dailyReturnsByDate(toDated(ger40D1Bars)), 20); return pearson(xs, ys) })()
      : null
    const ftseSx5eCorr20d = eustx50D1Bars.length
      ? (() => { const { xs, ys } = pairByDate(uk100Returns, dailyReturnsByDate(toDated(eustx50D1Bars)), 20); return pearson(xs, ys) })()
      : null

    // Pre-open lead (§4A(a)): only meaningful before the FTSE's own ORB has
    // formed — DAX/SX5E futures trade the pre-market and can show direction
    // while the FTSE ORB is still building. Reuses the same London-time
    // boundaries UK100's own overnight-range fetch above computes.
    let preOpenLead: EuropeanTapeBlock['preOpenLead'] = 'NONE'
    {
      const now = Date.now()
      const ld = londonNow()
      const offsetH = londonOffsetHours(new Date())
      const londonMidnightUtc = Date.UTC(ld.getUTCFullYear(), ld.getUTCMonth(), ld.getUTCDate()) - offsetH * 3_600_000
      const cashOpenMs = londonMidnightUtc + 8 * 3_600_000
      const orbEndMsLocal = londonMidnightUtc + 8.25 * 3_600_000
      const overnightStartMsLocal = cashOpenMs - 10 * 3_600_000
      if (now >= overnightStartMsLocal && now < orbEndMsLocal) {
        const breakDir = async (id: number | undefined, sym: string): Promise<'UP' | 'DOWN' | 'NONE'> => {
          if (!id) return 'NONE'
          const bars = await client.getTrendbars(id, 'H_1', overnightStartMsLocal, Math.min(now, cashOpenMs))
          if (!bars.length) return 'NONE'
          const hi = Math.max(...bars.map(b => b.high)) / 1e5
          const lo = Math.min(...bars.map(b => b.low)) / 1e5
          const cur = mid(sym)
          if (cur == null) return 'NONE'
          if (cur > hi) return 'UP'
          if (cur < lo) return 'DOWN'
          return 'NONE'
        }
        const ger40Lead = await breakDir(ger40Id, 'GER40')
        const eustx50Lead = await breakDir(eustx50Id, 'EUSTX50')
        if (ger40Lead !== 'NONE' && ger40Lead === eustx50Lead) preOpenLead = ger40Lead
        else if (ger40Lead !== 'NONE' && eustx50Lead === 'NONE') preOpenLead = ger40Lead
        else if (eustx50Lead !== 'NONE' && ger40Lead === 'NONE') preOpenLead = eustx50Lead
        // else both NONE, or conflicting (one UP one DOWN) — stays NONE
      }
    }

    // US500/NAS100/Brent/Copper/Gold day% and GBP day% — use D_1 bars per symbol.
    // Sequential, not Promise.all: the MCP session is stateful and concurrent
    // tool calls on one sessionId raced and threw "Session not found" (observed
    // 2026-07-10) — same reason ctrader_http_fetch.py and resolve-gold-sessions.ts
    // call the MCP one round-trip at a time rather than in parallel.
    const dayPctFor = async (sym: string): Promise<number | null> => {
      const id = idFor(sym); if (!id) return null
      const bars = await client.getTrendbars(id, 'D_1', Date.now() - 5 * 24 * 3600 * 1000, Date.now())
      if (bars.length < 2) return null
      const prior = bars[bars.length - 2].close / 1e5
      const cur = mid(sym)
      return dayPct(cur, prior)
    }

    const us500DayPct  = await dayPctFor('US500')
    const nas100DayPct = await dayPctFor('NAS100')
    const brentDayPct  = await dayPctFor('BRENT')
    const copperDayPct = await dayPctFor('COPPER')
    const goldDayPct   = await dayPctFor('XAUUSD')
    const gbpUsdDayPct = await dayPctFor('GBPUSD')
    // EUR/USD day% (F9, UK100-SESSION-REVIEW-2026-07-13.md §4A/§5): the EUR
    // sign-flip analog — a strong EUR is a headwind for DAX/SX5E exporters,
    // so it modulates how bullish a European-tape rally really is.
    const eurUsdDayPct = await dayPctFor('EURUSD')

    const uk100DayPct = dayPct(uk100Mid, priorClose)

    // Tape agreement (§4A): SPLIT when GER40/EUSTX50 disagree with EACH
    // OTHER (the European tape is itself internally conflicted, a weak
    // signal either way); DIVERGING when they agree with each other but
    // UK100 moves the opposite way (FTSE trading its own idiosyncratic
    // story, e.g. a commodity-driven day — §4A(b)'s decoupling case);
    // ALIGNED otherwise (the default/normal beta-tracking case).
    const classifySign = (pct: number | null): -1 | 0 | 1 => pct == null ? 0 : pct > 0.15 ? 1 : pct < -0.15 ? -1 : 0
    const tapeAgreement: EuropeanTapeBlock['tapeAgreement'] = (() => {
      const g = classifySign(ger40DayPct)
      const e = classifySign(eustx50DayPct)
      const f = classifySign(uk100DayPct)
      if (g !== 0 && e !== 0 && g !== e) return 'SPLIT'
      const euroSign = g !== 0 ? g : e
      if (euroSign !== 0 && f !== 0 && euroSign !== f) return 'DIVERGING'
      return 'ALIGNED'
    })()

    const prices: Uk100Prices = {
      UK100: uk100Mid, GBPUSD: gbpUsd, GBPEUR: eurGbp ? Math.round(1 / eurGbp * 100000) / 100000 : null,
      US500: mid('US500'), NAS100: mid('NAS100'), BRENT: mid('BRENT'), COPPER: mid('COPPER'),
      VIX: mid('VIX'), USDX: mid('USDX'), XAUUSD: mid('XAUUSD'),
      UK100_dayPct: uk100DayPct,
    }

    console.log(`CTrader UK100: ${prices.UK100}, GBPUSD: ${prices.GBPUSD}, dayPct: ${uk100DayPct}`)
    console.log(`European tape: GER40 ${ger40DayPct}%, EUSTX50 ${eustx50DayPct}%, EURUSD ${eurUsdDayPct}%, corr(DAX)=${ftseDaxCorr20d}, corr(SX5E)=${ftseSx5eCorr20d}, agreement=${tapeAgreement}, preOpenLead=${preOpenLead}`)

    return {
      prices, priorDayHigh, priorDayLow, priorClose, prevWeekHigh, prevWeekLow, overnightHigh, overnightLow,
      orbHigh, orbLow, postOrbCloses, adr14, adrUsedPct,
      us500DayPct, nas100DayPct, brentDayPct, copperDayPct, goldDayPct, gbpUsdDayPct,
      ger40DayPct, eustx50DayPct, eurUsdDayPct, ftseDaxCorr20d, ftseSx5eCorr20d, tapeAgreement, preOpenLead,
    }
  } catch (err) {
    console.error('CTrader UK100 fetch failed:', err)
    return null
  }
}

// ── GBP COT (CFTC) — FTSE positioning proxy (§1.4) ──────────────────────────

interface CotResult {
  cotNetLong: number | null; cotWoWChange: number | null
  crowding: 'CROWDED_LONG' | 'CROWDED_SHORT' | 'BALANCED' | null
  reportDate: string | null
}

async function fetchGbpCot(prevData: CotResult): Promise<CotResult> {
  console.log('Fetching GBP COT (FTSE proxy)...')
  const today = new Date()
  if (prevData.reportDate) {
    const ageMs = today.getTime() - new Date(prevData.reportDate).getTime()
    if (ageMs < 5 * 24 * 3600 * 1000 && today.getUTCDay() !== 5) {
      console.log('GBP COT data fresh, skipping re-fetch')
      return prevData
    }
  }
  try {
    const url =
      'https://publicreporting.cftc.gov/resource/jun7-fc8e.json' +
      "?$where=cftc_contract_market_code='096742'" +
      '&$order=report_date_as_yyyy_mm_dd%20DESC' +
      '&$limit=2' +
      '&$select=report_date_as_yyyy_mm_dd,noncomm_positions_long_all,noncomm_positions_short_all'
    const raw = await httpGet(url, { Accept: 'application/json', 'User-Agent': 'xauusd-dashboard/1.0' })
    const rows = JSON.parse(raw) as Array<{
      report_date_as_yyyy_mm_dd?: string
      noncomm_positions_long_all?: string
      noncomm_positions_short_all?: string
    }>
    if (!rows.length) throw new Error('empty GBP COT response')
    // The API is already asked for the 2 most recent reports (see $limit=2
    // above), so week-over-week is computed report-over-report from THIS
    // response, not against prevData.cotNetLong from a previous run of the
    // script. The old run-over-run comparison read the same report against
    // itself on every hourly run once the report was >5 days old (the
    // freshness-skip window lapses well before CFTC publishes the next one),
    // making gbpCotWoWChange silently read 0 (UK100-SESSION-REVIEW-2026-07-13.md
    // §3.9 — the live 2026-07-13 snapshot showed exactly this: report
    // 2026-07-07, WoW 0). Require both rows; a malformed/short response falls
    // through to the catch below like any other fetch failure.
    if (rows.length < 2) throw new Error(`GBP COT response had only ${rows.length} row(s), need 2 for week-over-week`)
    const [latest, prior] = rows
    const longPos = parseInt(latest.noncomm_positions_long_all ?? '0')
    const shortPos = parseInt(latest.noncomm_positions_short_all ?? '0')
    const net = longPos - shortPos
    const priorLongPos = parseInt(prior.noncomm_positions_long_all ?? '0')
    const priorShortPos = parseInt(prior.noncomm_positions_short_all ?? '0')
    const wow = net - (priorLongPos - priorShortPos)
    const crowding: CotResult['crowding'] = net > 60000 ? 'CROWDED_LONG' : net < -20000 ? 'CROWDED_SHORT' : 'BALANCED'
    console.log(`GBP COT: long=${longPos.toLocaleString()} short=${shortPos.toLocaleString()} net=${net.toLocaleString()} wow=${wow.toLocaleString()} (vs report ${prior.report_date_as_yyyy_mm_dd})`)
    return { cotNetLong: net, cotWoWChange: wow, crowding, reportDate: latest.report_date_as_yyyy_mm_dd ?? null }
  } catch (err) {
    console.error('GBP COT fetch failed:', err)
    return prevData
  }
}

// ── Economic calendar (Finnhub) — UK + US + EZ, week-ahead ──────────────────

const FINNHUB_KEY = process.env.FINNHUB_API_KEY ?? ''
const HIGH_IMPACT_EVENTS = ['CPI', 'PCE', 'NFP', 'FOMC', 'ISM', 'GDP', 'PPI', 'Claims', 'JOLTS', 'Nonfarm', 'Federal Funds', 'Interest Rate', 'MPC', 'Bank Rate']

type FinnhubEvent = {
  event: string; time?: string; impact?: string
  estimate?: number | null; prev?: number | null; country?: string; currency?: string
}

function normaliseImpact(raw: string | undefined, eventName: string): 'HIGH' | 'MEDIUM' | 'LOW' {
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

function regionFromCountry(country: string | undefined, currency: string | undefined): 'UK' | 'US' | 'EZ' | null {
  const c = (country ?? currency ?? '').toUpperCase()
  if (c.includes('GB') || c.includes('GBP') || c.includes('UK')) return 'UK'
  if (c.includes('US') || c.includes('USD')) return 'US'
  if (c.includes('EU') || c.includes('EUR') || c.includes('DE') || c.includes('FR')) return 'EZ'
  return null
}

function weekAheadRange(): { from: string; to: string } {
  const now = new Date()
  const fmt = (d: Date) => d.toISOString().slice(0, 10)
  const day = now.getUTCDay()
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

async function fetchUk100Calendar(): Promise<Uk100CalendarEvent[]> {
  console.log('Fetching UK100 economic calendar (Finnhub + static UK/US fallback)...')
  const { from, to } = weekAheadRange()
  let finnhubEvents: Uk100CalendarEvent[] = []
  if (!FINNHUB_KEY) {
    console.log('Finnhub: FINNHUB_API_KEY not set — using static UK+US calendar only')
  } else {
    try {
      const url = `https://finnhub.io/api/v1/calendar/economic?from=${from}&to=${to}&token=${FINNHUB_KEY}`
      const raw = await httpGet(url)
      const data = JSON.parse(raw) as { economicCalendar?: FinnhubEvent[]; error?: string }
      if (data.error) {
        // Confirmed premium-gated on this account's key (see the
        // UK_STATIC_CALENDAR_2026 comment in scripts/lib/calendar.ts) —
        // not a mapping bug.
        console.log(`Finnhub calendar: premium-gated ("${data.error}") — using static UK+US calendar only`)
      } else if (data.economicCalendar) {
        finnhubEvents = data.economicCalendar
          .map(e => ({ e, region: regionFromCountry(e.country, e.currency) }))
          .filter((x): x is { e: FinnhubEvent; region: 'UK' | 'US' | 'EZ' } => x.region != null)
          .map(({ e, region }) => {
            const date = e.time?.slice(0, 10) || from
            const timeIso = e.time ?? `${date}T00:00:00Z`
            return {
              event: e.event, region, impact: normaliseImpact(e.impact, e.event),
              timeIso, timeLondon: londonTimeLabel(timeIso),
              daysFromToday: daysBetween(date, from),
              prior: e.prev != null ? String(e.prev) : undefined,
              consensus: e.estimate != null ? String(e.estimate) : undefined,
            } satisfies Uk100CalendarEvent
          })
      } else {
        console.log('Finnhub calendar: response had neither economicCalendar nor error — using static UK+US calendar only')
      }
    } catch (err) {
      console.error('Finnhub calendar fetch failed:', err)
    }
  }
  return mergeCalendars(finnhubEvents, [...UK_STATIC_CALENDAR_2026, ...US_STATIC_CALENDAR_2026], from)
}

// ── News (Finnhub) — FTSE-relevant keyword filter ───────────────────────────

const UK100_NEWS_KEYWORDS = [
  'ftse', 'bank of england', 'boe', 'gilt', 'sterling', 'gbp', 'uk economy',
  'shell', 'bp', 'astrazeneca', 'hsbc', 'rate', 'inflation', 'budget', 'obr',
  'tariff', 'china stimulus',
]
const NEWS_WINDOW_HOURS = 24

async function fetchUk100News(): Promise<Uk100NewsItem[]> {
  console.log('Fetching UK100 news headlines (Finnhub)...')
  if (!FINNHUB_KEY) { console.log('Finnhub: FINNHUB_API_KEY not set — skipping headlines'); return [] }
  try {
    const raw = await httpGet(`https://finnhub.io/api/v1/news?category=general&token=${FINNHUB_KEY}`)
    const data = JSON.parse(raw) as Array<{ headline: string; source?: string; datetime?: number; url?: string }>
    const nowMs = Date.now()
    return data
      .filter(a => UK100_NEWS_KEYWORDS.some(k => a.headline.toLowerCase().includes(k)))
      .map(a => {
        const publishedMs = (a.datetime ?? 0) * 1000
        return {
          headline: a.headline, source: a.source ?? 'Finnhub', url: a.url,
          hoursAgo: publishedMs ? Math.round((nowMs - publishedMs) / 3_600_000 * 10) / 10 : 999,
        } satisfies Uk100NewsItem
      })
      .filter(n => n.hoursAgo <= NEWS_WINDOW_HOURS)
      .sort((a, b) => a.hoursAgo - b.hoursAgo)
      .slice(0, 8)
  } catch (err) {
    console.error('UK100 news fetch failed:', err)
    return []
  }
}

// ── §5 Mechanical bias engine ────────────────────────────────────────────────

function clampScore(x: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, x))
}

// B2 (UK100-V2-PLAN.md §4): one VIX vocabulary across the dashboard —
// CALM < 15, NORMAL 15-25, STRESS > 25. Math unchanged, only the middle
// band's name (was 'ELEVATED').
function vixRegime(vix: number | null): 'CALM' | 'NORMAL' | 'STRESS' {
  if (vix == null) return 'CALM'
  if (vix < 15) return 'CALM'
  if (vix <= 25) return 'NORMAL'
  return 'STRESS'
}

/**
 * European-tape driver weight, time-of-day ramped: 2.5 pre-14:30 London (the
 * European cash session out-correlates the US tape intraday — measured
 * r=0.68-0.75 vs UK100, UK100-SESSION-REVIEW-2026-07-13.md §4A), linearly
 * decaying to 1.0 across 14:30-15:30 as the US tape (US futures driver,
 * weight 2.5) takes over, held at 1.0 after 15:30. Pure function of the
 * London hour so it's independently testable and doesn't hide a `new Date()`
 * call inside computeBias.
 *
 * PROVISIONAL (user-set 2026-07-13): recalibrate from F7 resolver outcomes
 * once enough UK100 session data exists — this is a starting prior, not a
 * measured optimum.
 */
export function europeanTapeWeight(londonHour: number): number {
  if (londonHour < 14.5) return 2.5
  if (londonHour >= 15.5) return 1.0
  return 2.5 - (londonHour - 14.5) * 1.5
}

export function computeBias(input: {
  gbpUsdDayPct: number | null; sterlingEriDayChange: number | null
  us500DayPct: number | null; nas100DayPct: number | null
  vix: number | null
  brentDayPct: number | null; copperDayPct: number | null
  gilt10yDayBp: number | null; gilt20yDayBp: number | null
  cotCrowding: 'CROWDED_LONG' | 'CROWDED_SHORT' | 'BALANCED' | null
  riskToneLabel: FtseImpact | null
  eventSuppressed: boolean
  ger40DayPct: number | null; eustx50DayPct: number | null
  nowLondonHour: number
}): BiasBlock {
  const drivers: BiasDriver[] = []
  let weightedSum = 0

  // GBP (sign-flipped), weight 3.0
  {
    const w = 3.0
    let comp = 0
    if (input.gbpUsdDayPct != null) {
      comp = clampScore(-input.gbpUsdDayPct / 0.5 * 2, -2, 2)
      if (input.sterlingEriDayChange != null) {
        const eriSign = Math.sign(input.sterlingEriDayChange)
        const cableSign = Math.sign(input.gbpUsdDayPct)
        if (eriSign !== 0 && cableSign !== 0 && eriSign !== cableSign) comp /= 2
      }
    }
    weightedSum += comp * w
    drivers.push({
      name: 'GBP', weight: w,
      // B1 (UK100-V2-PLAN.md §4): |comp| >= 0.8 label floor, not >0.3 —
      // score arithmetic (weightedSum) is unchanged, only the human-facing
      // label. Floor works out to +-0.2% GBP/USD day%.
      impact: comp >= 0.8 ? 'BULLISH' : comp <= -0.8 ? 'BEARISH' : 'NEUTRAL',
      detail: input.gbpUsdDayPct != null
        ? `GBP/USD ${input.gbpUsdDayPct >= 0 ? '+' : ''}${input.gbpUsdDayPct}% → FTSE ${comp >= 0 ? 'tailwind' : 'headwind'} (sign-flipped)`
        : 'GBP/USD unavailable',
    })
  }

  // US futures, weight 2.5
  {
    const w = 2.5
    let comp = 0
    if (input.us500DayPct != null) {
      comp = clampScore(input.us500DayPct / 0.75 * 2, -2, 2)
      if (input.nas100DayPct != null) {
        const bonus = clampScore(Math.sign(input.nas100DayPct) * 0.5, -0.5, 0.5)
        if (Math.sign(input.nas100DayPct) === Math.sign(input.us500DayPct)) comp = clampScore(comp + bonus, -2, 2)
      }
    }
    weightedSum += comp * w
    drivers.push({
      name: 'US futures', weight: w,
      // B1: |comp| >= 0.8 label floor. Floor works out to +-0.3% US500 day%.
      impact: comp >= 0.8 ? 'BULLISH' : comp <= -0.8 ? 'BEARISH' : 'NEUTRAL',
      detail: input.us500DayPct != null ? `US500 ${input.us500DayPct >= 0 ? '+' : ''}${input.us500DayPct}% today` : 'US500 unavailable',
    })
  }

  // VIX regime, weight 1.5, capped at -1 (damper not a direction)
  {
    const w = 1.5
    const regime = vixRegime(input.vix)
    const comp = regime === 'CALM' ? 1 : regime === 'NORMAL' ? 0 : -1
    weightedSum += comp * w
    drivers.push({
      name: 'VIX regime', weight: w,
      impact: comp > 0 ? 'BULLISH' : comp < 0 ? 'BEARISH' : 'NEUTRAL',
      detail: `VIX ${input.vix ?? '—'} — ${regime} regime`,
    })
  }

  // Brent, weight 1.5
  {
    const w = 1.5
    const comp = input.brentDayPct != null ? clampScore(input.brentDayPct / 1.5 * 2, -2, 2) : 0
    weightedSum += comp * w
    drivers.push({
      name: 'Brent', weight: w,
      // B1: |comp| >= 0.8 label floor. Floor works out to +-0.6% Brent day%.
      impact: comp >= 0.8 ? 'BULLISH' : comp <= -0.8 ? 'BEARISH' : 'NEUTRAL',
      detail: input.brentDayPct != null ? `Brent ${input.brentDayPct >= 0 ? '+' : ''}${input.brentDayPct}% (energy majors)` : 'Brent unavailable',
    })
  }

  // Copper (China proxy), weight 1.5
  {
    const w = 1.5
    const comp = input.copperDayPct != null ? clampScore(input.copperDayPct / 1.5 * 2, -2, 2) : 0
    weightedSum += comp * w
    drivers.push({
      name: 'Copper (China proxy)', weight: w,
      // B1: |comp| >= 0.8 label floor. Floor works out to +-0.6% Copper day%.
      impact: comp >= 0.8 ? 'BULLISH' : comp <= -0.8 ? 'BEARISH' : 'NEUTRAL',
      detail: input.copperDayPct != null ? `Copper ${input.copperDayPct >= 0 ? '+' : ''}${input.copperDayPct}% (miners/China)` : 'Copper unavailable',
    })
  }

  // Gilts / rotation, weight 1.0 — long-end blowout overrides
  let longEndStress = false
  {
    const w = 1.0
    let comp = 0
    if (input.gilt20yDayBp != null && input.gilt20yDayBp >= 8) {
      comp = -2; longEndStress = true
    } else if (input.gilt10yDayBp != null) {
      const abs10y = Math.abs(input.gilt10yDayBp)
      comp = abs10y <= 3 ? 0 : (input.gilt10yDayBp >= 4 && input.gilt10yDayBp <= 8 ? 1 : 0)
    }
    weightedSum += comp * w
    drivers.push({
      name: 'Gilts / rotation', weight: w,
      impact: comp > 0.3 ? 'BULLISH' : comp < -0.3 ? 'BEARISH' : 'NEUTRAL',
      detail: longEndStress
        ? `20Y gilt +${input.gilt20yDayBp}bp — fiscal-stress override`
        : input.gilt10yDayBp != null ? `10Y gilt ${input.gilt10yDayBp >= 0 ? '+' : ''}${input.gilt10yDayBp}bp` : 'Gilt data unavailable',
    })
  }

  // GBP COT (contrarian), weight 1.0
  {
    const w = 1.0
    const comp = input.cotCrowding === 'CROWDED_LONG' ? 1 : input.cotCrowding === 'CROWDED_SHORT' ? -1 : 0
    weightedSum += comp * w
    drivers.push({
      name: 'GBP COT (proxy, contrarian)', weight: w,
      impact: comp > 0 ? 'BULLISH' : comp < 0 ? 'BEARISH' : 'NEUTRAL',
      detail: input.cotCrowding ? `GBP positioning: ${input.cotCrowding}` : 'COT data unavailable',
    })
  }

  // Risk tone (Anthropic classifier over recent news — null when
  // ANTHROPIC_API_KEY is absent or there's no news to classify)
  {
    const w = 1.0
    const comp = input.riskToneLabel === 'BULLISH' ? 1 : input.riskToneLabel === 'BEARISH' ? -1 : 0
    weightedSum += comp * w
    drivers.push({
      name: 'Risk tone', weight: w,
      impact: input.riskToneLabel ?? 'NEUTRAL',
      detail: input.riskToneLabel ? `Risk-tone classifier: ${input.riskToneLabel}` : 'Risk-tone classifier unavailable (no API key or no news)',
    })
  }

  // European tape (SX5E/DAX), time-of-day weighted 2.5→1.0 — see
  // europeanTapeWeight()'s docstring. Euro Stoxx 50 is primary (tied-best
  // measured correlate); averaged with GER40 when both are available for a
  // steadier read, falls back to whichever one is present. Uses the same
  // |comp| ≥ 0.8 label floor B1 later applies to the other continuous
  // drivers — built in after the label-noise finding, not before it.
  const europeanWeight = europeanTapeWeight(input.nowLondonHour)
  {
    const w = europeanWeight
    const g = input.ger40DayPct, e = input.eustx50DayPct
    let comp = 0
    if (e != null && g != null) comp = clampScore((e + g) / 2 / 0.75 * 2, -2, 2)
    else if (e != null) comp = clampScore(e / 0.75 * 2, -2, 2)
    else if (g != null) comp = clampScore(g / 0.75 * 2, -2, 2)
    weightedSum += comp * w
    drivers.push({
      name: 'European tape (SX5E/DAX)', weight: Math.round(w * 100) / 100,
      impact: comp >= 0.8 ? 'BULLISH' : comp <= -0.8 ? 'BEARISH' : 'NEUTRAL',
      detail: e != null || g != null
        ? `SX5E ${e != null ? `${e >= 0 ? '+' : ''}${e}%` : '—'} / DAX ${g != null ? `${g >= 0 ? '+' : ''}${g}%` : '—'}`
        : 'European tape unavailable',
    })
  }

  // Total driver weight scales with the European tape's time-varying weight
  // (13.0 fixed-weight drivers + europeanWeight, vs the flat 13.0 before this
  // driver existed), so the divisor is recomputed the same way V2 Phase D2's
  // GER40 spec already anticipated for a flat addition (divisor scaled
  // proportionally to total weight, 1.35 × totalWeight/13) — just evaluated
  // per-call since totalWeight now varies through the day.
  const totalWeight = 13.0 + europeanWeight
  const divisor = 1.35 * (totalWeight / 13.0)
  const score = clampScore(Math.round(weightedSum / divisor), -10, 10)
  const label: BiasBlock['label'] = score >= 3 ? 'BULLISH' : score <= -3 ? 'BEARISH' : 'NEUTRAL'
  let conviction: BiasBlock['conviction'] = Math.abs(score) >= 6 ? 'HIGH' : Math.abs(score) >= 3 ? 'MEDIUM' : 'LOW'
  if (input.eventSuppressed && conviction === 'HIGH') conviction = 'MEDIUM'

  return { score, label, conviction, drivers, eventSuppressed: input.eventSuppressed }
}

// Sector panel (§5) — derived, no new fetches.
function computeSectorPanel(input: {
  brentDayPct: number | null; copperDayPct: number | null
  gilt10yDayBp: number | null; longEndStress: boolean
  ftseImpactFromGbp: FtseImpact
}): SectorRead[] {
  const sign = (v: number | null, threshold: number): FtseImpact =>
    v == null ? 'NEUTRAL' : v >= threshold ? 'BULLISH' : v <= -threshold ? 'BEARISH' : 'NEUTRAL'

  const banksRead: FtseImpact = input.longEndStress ? 'BEARISH'
    : input.gilt10yDayBp != null && input.gilt10yDayBp >= 4 ? 'BULLISH'
    : input.gilt10yDayBp != null && input.gilt10yDayBp <= -4 ? 'BEARISH'
    : 'NEUTRAL'

  const staplesRead: FtseImpact = input.ftseImpactFromGbp === 'BULLISH' ? 'NEUTRAL'
    : input.ftseImpactFromGbp === 'BEARISH' ? 'NEUTRAL' : 'NEUTRAL'
  // Softened one notch toward neutral per §5 — staples never take the full
  // sign-flip swing that GBP itself gets.

  return [
    {
      sector: 'ENERGY', weightNote: 'Shell, BP — top-5 index weights',
      driver: input.brentDayPct != null ? `Brent ${input.brentDayPct >= 0 ? '+' : ''}${input.brentDayPct}%` : 'Brent unavailable',
      read: sign(input.brentDayPct, 0.5),
      detail: 'Higher oil lifts the energy majors directly.',
    },
    {
      sector: 'MINERS', weightNote: 'Rio, Glencore, Anglo, Antofagasta',
      driver: input.copperDayPct != null ? `Copper ${input.copperDayPct >= 0 ? '+' : ''}${input.copperDayPct}%` : 'Copper unavailable',
      read: sign(input.copperDayPct, 0.75),
      detail: 'Copper is the fast proxy for China demand + global growth.',
    },
    {
      sector: 'BANKS', weightNote: 'HSBC, Barclays, NatWest, StanChart',
      driver: input.longEndStress ? '20Y gilt blowout' : input.gilt10yDayBp != null ? `10Y gilt ${input.gilt10yDayBp >= 0 ? '+' : ''}${input.gilt10yDayBp}bp` : 'Gilt data unavailable',
      read: banksRead,
      detail: input.longEndStress ? 'Fiscal-stress long-end sell-off overrides the normal rotation lift.' : 'Yields up helps bank net interest margins.',
    },
    {
      sector: 'PHARMA', weightNote: 'AstraZeneca (often largest single weight), GSK',
      driver: 'Idiosyncratic / single-stock',
      read: 'IDIOSYNCRATIC',
      detail: 'AZN alone can swing the index on stock-specific news — low macro-sensitivity, high single-stock risk.',
    },
    {
      sector: 'STAPLES', weightNote: 'Unilever, Diageo, BAT, Reckitt',
      driver: `GBP impact: ${input.ftseImpactFromGbp}`,
      read: staplesRead,
      detail: 'USD/EUR earners — takes the GBP sign-flip, softened toward neutral vs the index-level read.',
    },
  ]
}

// ── §6.1 ORB context — mechanical, always present ───────────────────────────

// B3 (UK100-V2-PLAN.md §4): sticky orbBrokenDirection, matching the Python
// engine's own definition exactly — first M5 close outside the ORB range
// after 08:15, chronological, sticky. A current-price snapshot flips back
// to NONE on any later reclaim (evidence-backed: UK100-SESSION-REVIEW-
// 2026-07-13.md §3.10, a live 2026-07-13 DOWN->NONE flip the engine itself
// did not make). Bars that break up then close back inside the range must
// still report 'UP' — the scan stops at the FIRST match, not the latest.
export function firstCloseOutside(closes: number[], orbHigh: number, orbLow: number): 'UP' | 'DOWN' | 'NONE' {
  for (const close of closes) {
    if (close > orbHigh) return 'UP'
    if (close < orbLow) return 'DOWN'
  }
  return 'NONE'
}

function computeOrbContext(input: {
  ctrader: CtraderResult | null
  uk100Price: number | null
  calendar: Uk100CalendarEvent[]
}): OrbContext {
  const now = new Date()
  const ld = londonNow()
  const hh = ld.getUTCHours() + ld.getUTCMinutes() / 60
  const mode: OrbContext['mode'] =
    hh < 8 ? 'PRE_OPEN' : hh < 8.25 ? 'ORB_FORMING' : hh < 16.5 ? 'POST_ORB' : 'CLOSED'

  const c = input.ctrader
  const priorClose = c?.priorClose ?? null
  const gapPts = input.uk100Price != null && priorClose != null ? Math.round((input.uk100Price - priorClose) * 10) / 10 : null
  const gapPct = input.uk100Price != null && priorClose ? Math.round((input.uk100Price - priorClose) / priorClose * 10000) / 100 : null

  // Null-safe when the post-ORB series is absent (PRE_OPEN, or the fetch
  // failed) — keep the existing null semantics for "unknown" rather than
  // falling back to a current-price comparison.
  let orbBrokenDirection: OrbContext['orbBrokenDirection'] = null
  if (c && c.orbHigh != null && c.orbLow != null && c.postOrbCloses.length > 0) {
    orbBrokenDirection = firstCloseOutside(c.postOrbCloses, c.orbHigh, c.orbLow)
  }

  const eventWindows = input.calendar
    .filter(e => e.impact === 'HIGH' && e.daysFromToday === 0)
    .map(e => ({ event: e.event, timeLondon: e.timeLondon, impact: e.impact }))

  return {
    computedAt: now.toISOString(),
    mode,
    cashOpenLondon: `08:00 ${londonOffsetHours(now) === 1 ? 'BST' : 'GMT'}`,
    overnightHigh: c?.overnightHigh ?? null, overnightLow: c?.overnightLow ?? null,
    priorDayHigh: c?.priorDayHigh ?? null, priorDayLow: c?.priorDayLow ?? null, priorClose,
    prevWeekHigh: c?.prevWeekHigh ?? null, prevWeekLow: c?.prevWeekLow ?? null,
    gapPts, gapPct,
    orbHigh: c?.orbHigh ?? null, orbLow: c?.orbLow ?? null,
    orbBrokenDirection,
    eventWindows,
    adr14: c?.adr14 ?? null, adrUsedPct: c?.adrUsedPct ?? null,
  }
}

// ── §2 ORB intelligence — the mechanical rules engine (G1) ──────────────────
// A pure, unit-testable synthesis layer over fields the snapshot already
// carries (UK100-ORB-INTEL-TLDR-DESIGN.md §2.3). Every rule either pushes one
// signal or nothing; thresholds are deliberate — do not re-tune here.

// The same-day /uk100-session record echo (rule R12). Read from disk in main()
// so computeOrbIntel stays pure; null when there is no same-day session.
export interface TodaySessionEcho {
  time:         string
  direction:    'LONG' | 'SHORT' | null   // tradeIdea.direction (null on NO_TRADE)
  status:       string | null             // tradeIdea.status
  probability:  number | null
  orbDirection: string | null             // orbPlaybook.direction
  draw:         number | null             // drawOnLiquidity (primary target)
}

export interface OrbIntelInput {
  orbContext:   OrbContext
  bias:         BiasBlock
  europeanTape: EuropeanTapeBlock
  usLinkage:    UsLinkageBlock
  fx:           FxBlock
  ukRates:      UkRatesBlock
  positioning:  PositioningBlock
  calendar:     Uk100CalendarEvent[]
  uk100Price:   number | null
  nowLondonHour: number
  todaySession: TodaySessionEcho | null
}

const SOURCE_PRIORITY: Record<OrbIntelSource, number> = {
  STRUCTURE: 0, RANGE: 1, GAP: 2, TAPE: 3, RATES: 4, FX: 5, EVENT: 6, POSITIONING: 7, AI: 8,
}
const SEVERITY_RANK: Record<OrbIntelSeverity, number> = { STRONG: 3, CAUTION: 2, INFO: 1 }

function rankSignals(signals: OrbIntelSignal[]): OrbIntelSignal[] {
  return [...signals].sort((a, b) =>
    SEVERITY_RANK[b.severity] - SEVERITY_RANK[a.severity] ||
    SOURCE_PRIORITY[a.source] - SOURCE_PRIORITY[b.source])
}

export function computeOrbIntel(input: OrbIntelInput): OrbIntel {
  const { orbContext: o, bias, europeanTape: et, usLinkage: us, fx, ukRates, positioning, calendar, uk100Price, nowLondonHour, todaySession } = input
  const signals: OrbIntelSignal[] = []
  const score = bias.score
  const price = uk100Price
  const budget = o.adr14 != null && o.adrUsedPct != null ? o.adr14 * (1 - o.adrUsedPct / 100) : null

  // R1 — Fakeout / reclaim: the break was swept and fully reclaimed.
  let r1Signal: OrbIntelSignal | null = null
  const postOrb = o.mode === 'POST_ORB' || o.mode === 'CLOSED'
  if (postOrb && price != null && o.orbHigh != null && o.orbLow != null) {
    if (o.orbBrokenDirection === 'DOWN' && price > o.orbHigh) {
      r1Signal = { direction: 'FAVOURS_LONG', severity: 'STRONG', source: 'STRUCTURE',
        text: `ORB broke DOWN but price has fully reclaimed the range (back above ${o.orbHigh}) — the break was a liquidity sweep; the reclaim direction is in control, don't trade the original break.` }
    } else if (o.orbBrokenDirection === 'UP' && price < o.orbLow) {
      r1Signal = { direction: 'FAVOURS_SHORT', severity: 'STRONG', source: 'STRUCTURE',
        text: `ORB broke UP but price has fully reclaimed the range (back below ${o.orbLow}) — the break was a liquidity sweep; the reclaim direction is in control, don't trade the original break.` }
    }
  }
  if (r1Signal) signals.push(r1Signal)

  // R2 / R3 — counter-bias vs with-bias break (only when R1 did not fire).
  if (!r1Signal && o.mode === 'POST_ORB' && (o.orbBrokenDirection === 'UP' || o.orbBrokenDirection === 'DOWN') && Math.abs(score) >= 3) {
    const brokeUp = o.orbBrokenDirection === 'UP'
    const biasUp = score >= 3
    const label = biasUp ? 'BULLISH' : 'BEARISH'
    if (brokeUp !== biasUp) {
      // R2 — against the bias
      signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'CAUTION', source: 'STRUCTURE',
        text: `ORB broke ${o.orbBrokenDirection} against a ${label} macro bias (${score >= 0 ? '+' : ''}${score}) — counter-bias breaks fail more often; treat continuation as suspect.` })
    } else {
      // R3 — with the bias
      signals.push({ direction: biasUp ? 'FAVOURS_LONG' : 'FAVOURS_SHORT', severity: 'INFO', source: 'STRUCTURE',
        text: `ORB break ${o.orbBrokenDirection} is aligned with the ${label} macro bias (${score >= 0 ? '+' : ''}${score}) — continuation has the backdrop behind it.` })
    }
  }

  // R4 — range budget spent.
  if (o.adrUsedPct != null && o.adrUsedPct >= 70) {
    const strong = o.adrUsedPct >= 90
    signals.push({ direction: 'BREAKOUT_SUSPECT', severity: strong ? 'STRONG' : 'CAUTION', source: 'RANGE',
      text: `${o.adrUsedPct}% of a typical day's range is already spent — fresh breakouts have little fuel; favour fades back into the range over chasing.` })
  }

  // R5 / R6 — gap dynamics, only in the pre-/opening window (London hour < 9).
  if (nowLondonHour < 9 && o.gapPct != null && Math.abs(score) >= 3) {
    const gapUp = o.gapPct > 0
    const biasUp = score >= 3
    if (Math.abs(o.gapPct) >= 0.4 && gapUp !== biasUp) {
      signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'CAUTION', source: 'GAP',
        text: `Gapped ${gapUp ? 'UP' : 'DOWN'} ${o.gapPct >= 0 ? '+' : ''}${o.gapPct}% against a ${biasUp ? 'bullish' : 'bearish'} bias${o.priorClose != null ? ` — a gap-fill toward prior close (${o.priorClose}) is the favoured first move` : ''}, not continuation.` })
    } else if (Math.abs(o.gapPct) >= 0.25 && gapUp === biasUp && o.overnightHigh != null && o.overnightLow != null && o.adr14 != null && (o.overnightHigh - o.overnightLow) < 0.5 * o.adr14) {
      signals.push({ direction: biasUp ? 'FAVOURS_LONG' : 'FAVOURS_SHORT', severity: 'INFO', source: 'GAP',
        text: `Gap ${gapUp ? 'up' : 'down'} in the bias direction with a tight overnight range — trend-day conditions; the first ORB break ${biasUp ? 'long' : 'short'} carries the setup.` })
    }
  }

  // R7 — the obvious draw sits beyond what's left of a typical day's range.
  if (budget != null && price != null) {
    if (score >= 0 && o.priorDayHigh != null && price < o.priorDayHigh && (o.priorDayHigh - price) > budget) {
      signals.push({ direction: 'NEUTRAL', severity: 'CAUTION', source: 'RANGE',
        text: `The obvious draw (PDH ${o.priorDayHigh}) sits beyond what's left of a typical day's range — targets past it are stretch-only today.` })
    } else if (score < 0 && o.priorDayLow != null && price > o.priorDayLow && (price - o.priorDayLow) > budget) {
      signals.push({ direction: 'NEUTRAL', severity: 'CAUTION', source: 'RANGE',
        text: `The obvious draw (PDL ${o.priorDayLow}) sits beyond what's left of a typical day's range — targets past it are stretch-only today.` })
    }
  }

  // R8 — European tape.
  if (et.tapeAgreement === 'DIVERGING') {
    signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'CAUTION', source: 'TAPE',
      text: `FTSE is diverging from a united European tape — it's trading its own story today; tape-based confirmation is unreliable.` })
  } else if (et.tapeAgreement === 'SPLIT') {
    signals.push({ direction: 'NEUTRAL', severity: 'INFO', source: 'TAPE',
      text: `The European tape is split (Euro Stoxx and DAX disagree) — no clean cross-market lead; weight the tape less than usual.` })
  } else if (et.tapeAgreement === 'ALIGNED' && et.eurostoxx50DayPct != null && Math.abs(et.eurostoxx50DayPct) > 0.15) {
    const up = et.eurostoxx50DayPct > 0
    signals.push({ direction: up ? 'FAVOURS_LONG' : 'FAVOURS_SHORT', severity: 'INFO', source: 'TAPE',
      text: `FTSE is tracking a ${up ? 'firmer' : 'softer'} European tape (Euro Stoxx ${et.eurostoxx50DayPct >= 0 ? '+' : ''}${et.eurostoxx50DayPct}%) — the cross-market lean is ${up ? 'up' : 'down'}.` })
  }
  if ((o.mode === 'PRE_OPEN' || o.mode === 'ORB_FORMING') && (et.preOpenLead === 'UP' || et.preOpenLead === 'DOWN')) {
    signals.push({ direction: et.preOpenLead === 'UP' ? 'FAVOURS_LONG' : 'FAVOURS_SHORT', severity: 'INFO', source: 'TAPE',
      text: `European futures already broke ${et.preOpenLead} through their overnight range pre-open — an early lean for a ${et.preOpenLead === 'UP' ? 'upside' : 'downside'} resolution.` })
  }

  // R9 — US tape / VIX.
  if (us.vixRegime === 'STRESS') {
    signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'STRONG', source: 'TAPE',
      text: `VIX in STRESS — violent reversals both ways; cut size and distrust breakouts in either direction.` })
  } else if (nowLondonHour >= 13.5 && us.us500DayPct != null && Math.abs(us.us500DayPct) >= 0.3) {
    const up = us.us500DayPct > 0
    signals.push({ direction: up ? 'FAVOURS_LONG' : 'FAVOURS_SHORT', severity: 'INFO', source: 'TAPE',
      text: `Past 13:30 with US futures ${us.us500DayPct >= 0 ? '+' : ''}${us.us500DayPct}% — the 14:30 US handoff argues ${up ? 'for' : 'against'} holding longs into the US open.` })
  }

  // R10 — sterling at a 20-day extreme.
  if (fx.gbpUsd20dPercentile != null && fx.gbpUsdDayPct != null) {
    if (fx.gbpUsd20dPercentile >= 85 && fx.gbpUsdDayPct > 0) {
      signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'CAUTION', source: 'FX',
        text: `Sterling is at the ${fx.gbpUsd20dPercentile}th percentile of its 20-day range and still rising — a persistent FX headwind capping upside breaks (weak GBP is what lifts FTSE).` })
    } else if (fx.gbpUsd20dPercentile <= 15 && fx.gbpUsdDayPct < 0) {
      signals.push({ direction: 'FAVOURS_LONG', severity: 'INFO', source: 'FX',
        text: `Sterling is at the ${fx.gbpUsd20dPercentile}th percentile of its 20-day range and falling — a weak-GBP tailwind for the index's dollar earners.` })
    }
  }

  // R11 — fiscal stress / COT.
  if (ukRates.longEndStress) {
    signals.push({ direction: 'FAVOURS_SHORT', severity: 'STRONG', source: 'RATES',
      text: `20Y gilt +${ukRates.gilt20yDayBp}bp — a fiscal-stress selloff; this historically drags the whole index regardless of the banks rotation.` })
  }
  if (positioning.crowding === 'CROWDED_SHORT') {
    signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'INFO', source: 'POSITIONING',
      text: `GBP is a crowded short — a short-squeeze higher in sterling is a latent slap for upside breaks (strong GBP weighs on FTSE).` })
  }

  // R12 — same-day AI session echo.
  let r12Signal: OrbIntelSignal | null = null
  if (todaySession) {
    const ts = todaySession
    const dir: OrbIntelDirection = ts.direction === 'LONG' ? 'FAVOURS_LONG' : ts.direction === 'SHORT' ? 'FAVOURS_SHORT' : 'NEUTRAL'
    const drawClause = ts.direction && ts.draw != null ? ` toward ${ts.draw}` : ''
    const call = ts.direction ? `${ts.direction}${drawClause}` : 'NO TRADE'
    const meta = [ts.status, ts.probability != null ? `${ts.probability}%` : null].filter(Boolean).join(', ')
    const playbook = ts.orbDirection ? ` — playbook ${ts.orbDirection}` : ''
    r12Signal = { direction: dir, severity: 'INFO', source: 'AI',
      text: `Today's ${ts.time} AI session read: ${call}${meta ? ` (${meta})` : ''}${playbook}.` }
    signals.push(r12Signal)
  }

  // R13 — event windows.
  if (o.eventWindows.length > 0) {
    signals.push({ direction: 'BREAKOUT_SUSPECT', severity: 'CAUTION', source: 'EVENT',
      text: `${o.eventWindows.map(e => `${e.event} @ ${e.timeLondon}`).join(', ')} today — pre-release breaks are positioning, not conviction.` })
  } else {
    const tomorrowHigh = calendar.find(e => e.impact === 'HIGH' && e.daysFromToday === 1)
    if (tomorrowHigh && nowLondonHour >= 14) {
      signals.push({ direction: 'NEUTRAL', severity: 'INFO', source: 'EVENT',
        text: `${tomorrowHigh.event} prints tomorrow ${tomorrowHigh.timeLondon} — late-session moves today are as likely pre-event de-risking as conviction.` })
    }
  }

  // ── Stance aggregation (§2.4) — computed from the FULL signal set. ──
  const strongOpposes = (favourLong: boolean) => signals.some(s =>
    s.severity === 'STRONG' && (s.direction === (favourLong ? 'FAVOURS_SHORT' : 'FAVOURS_LONG') || s.direction === 'BREAKOUT_SUSPECT'))
  const suspectCount = signals.filter(s => s.direction === 'BREAKOUT_SUSPECT' && SEVERITY_RANK[s.severity] >= SEVERITY_RANK.CAUTION).length

  let stance: OrbIntelStance
  if (r1Signal) {
    stance = 'FADE_FAVOURED'
  } else if (score >= 3 && !strongOpposes(true)) {
    stance = 'LONG_FAVOURED'
  } else if (score <= -3 && !strongOpposes(false)) {
    stance = 'SHORT_FAVOURED'
  } else if (suspectCount >= 2) {
    stance = 'BREAKOUTS_SUSPECT'
  } else {
    stance = 'MIXED'
  }

  const STANCE_PHRASE: Record<OrbIntelStance, string> = {
    LONG_FAVOURED: 'Backdrop favours upside breaks',
    SHORT_FAVOURED: 'Backdrop favours downside breaks',
    FADE_FAVOURED: 'Fade day — the ORB break was a trap',
    BREAKOUTS_SUSPECT: 'Breakouts suspect in both directions today',
    MIXED: 'No clean edge — mixed signals',
  }

  // ── Rank & cap at 6, always keeping R1 and R12 (§2.5). ──
  const ranked = rankSignals(signals)
  let capped = ranked
  if (ranked.length > 6) {
    const forced = [r1Signal, r12Signal].filter((s): s is OrbIntelSignal => s != null)
    const others = ranked.filter(s => !forced.includes(s))
    capped = rankSignals([...forced, ...others.slice(0, 6 - forced.length)])
  }

  const stanceLine = capped.length > 0
    ? `${STANCE_PHRASE[stance]} — ${capped[0].text}`
    : STANCE_PHRASE[stance]

  return { stance, stanceLine, signals: capped, aiStanceLine: null, aiBullets: [], baseRateNote: null }
}

// Read today's latest /uk100-session record for rule R12. Best-effort — any
// failure (no index, no same-day entry, unreadable file) returns null and the
// rule simply doesn't fire. Runs in main(), keeping computeOrbIntel pure.
function readTodaySessionEcho(): TodaySessionEcho | null {
  try {
    const sessionsDir = path.join(__dirname, '../public/data/uk100/sessions')
    const indexPath = path.join(sessionsDir, 'index.json')
    const index = JSON.parse(fs.readFileSync(indexPath, 'utf8')) as { sessions?: Array<{ date: string; time: string; filename: string; timestamp: string }> }
    const todayLondon = londonNow().toISOString().slice(0, 10)
    const todays = (index.sessions ?? []).filter(s => s.date === todayLondon)
    if (todays.length === 0) return null
    todays.sort((a, b) => b.timestamp.localeCompare(a.timestamp))
    const latest = todays[0]
    const rec = JSON.parse(fs.readFileSync(path.join(sessionsDir, latest.filename), 'utf8')) as {
      tradeIdea?: { direction?: 'LONG' | 'SHORT'; status?: string } | null
      probability?: number
      orbPlaybook?: { direction?: string } | null
      drawOnLiquidity?: number
    }
    const noTrade = rec.tradeIdea?.status === 'NO_TRADE' || !rec.tradeIdea
    return {
      time: latest.time,
      direction: noTrade ? null : (rec.tradeIdea?.direction ?? null),
      status: rec.tradeIdea?.status ?? null,
      probability: rec.probability ?? null,
      orbDirection: rec.orbPlaybook?.direction ?? null,
      draw: rec.drawOnLiquidity ?? null,
    }
  } catch {
    return null
  }
}

// ── Anthropic risk-tone classifier + daily briefing (Phase 2e) ─────────────
// Same key-sourcing pattern as fetch-static-data.ts: .trim() defends against
// a trailing newline in the GitHub secret, which makes Headers.append throw
// "invalid header value" and silently nulls the result (observed 2026-07-07
// on the gold briefing — same failure mode applies here).
const ANTHROPIC_KEY = (process.env.ANTHROPIC_API_KEY ?? '').trim()
const ANTHROPIC_MODEL = 'claude-sonnet-4-6'

const RISK_TONE_SYSTEM_PROMPT = `You are a risk-sentiment classifier for a UK100 (FTSE 100) index trading desk.
Given a list of recent news headlines (last 24h, tagged with hoursAgo), classify the overall market risk tone.
UK100 is a risk-asset equity index: RISK-ON conditions (calm markets, easing tension, dovish central banks, strong growth data) are typically BULLISH for it; RISK-OFF conditions (geopolitical escalation, financial stress, hawkish surprises, recession fear) are typically BEARISH.
If the headlines contain nothing clearly risk-relevant, return NEUTRAL with a low score and say so in the rationale — do not invent significance.
Return ONLY this JSON, no other text: { "score": number from -5 (strong risk-off) to +5 (strong risk-on), "label": "BULLISH" | "BEARISH" | "NEUTRAL", "rationale": "one sentence, under 200 characters" }`

async function fetchUk100RiskTone(newsItems: Uk100NewsItem[]): Promise<Uk100Snapshot['riskTone']> {
  console.log('Classifying risk tone (Anthropic)...')
  if (!ANTHROPIC_KEY) { console.log('Anthropic: ANTHROPIC_API_KEY env var not set — skipping risk-tone'); return null }
  if (newsItems.length === 0) { console.log('Risk-tone: no newsItems — skipping'); return null }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: ANTHROPIC_MODEL,
        max_tokens: 300,
        system: RISK_TONE_SYSTEM_PROMPT,
        messages: [
          { role: 'user', content: `Recent headlines:\n\n${JSON.stringify(newsItems, null, 2)}` },
        ],
      }),
    })

    if (!response.ok) {
      console.error(`Anthropic risk-tone API error ${response.status}: ${(await response.text()).slice(0, 200)}`)
      return null
    }

    const body = await response.json() as { content: Array<{ type: string; text: string }> }
    const text = body.content.find(c => c.type === 'text')?.text ?? ''
    const cleaned = text.replace(/^```json?\s*/i, '').replace(/\s*```$/, '').trim()
    const parsed = JSON.parse(cleaned) as { score: number; label: FtseImpact; rationale: string }
    console.log(`Risk tone: ${parsed.label} (${parsed.score})`)
    return parsed
  } catch (err) {
    console.error('Risk-tone classification failed:', err)
    return null
  }
}

const BRIEFING_SYSTEM_PROMPT = `You are a senior UK100 (FTSE 100) index trading analyst and market intelligence advisor.
Your job is to write a daily intelligence briefing for a trader who trades the 15-minute Opening Range Breakout (ORB) at London cash open (08:00), long or short per a mechanical ORB playbook, using the 1H chart for trend and the 5M chart for the ORB and signals.

You will receive a structured JSON snapshot of the current UK100 market data. The snapshot is refreshed roughly hourly during London/NY hours, so "recent" means since your last update, not necessarily since midnight.

CRITICAL — GBP sign-flip: UK100 and GBP are INVERSELY correlated. Weak GBP (GBPUSD falling) is BULLISH for UK100 (lifts the index's dollar/euro-earning multinationals); strong GBP is BEARISH. Always state the GBP move and its FTSE implication using this inverted relationship — never reason about it the way you would DXY vs gold.

The snapshot includes:
- \`sectorPanel\`: five sectors (ENERGY, MINERS, BANKS, PHARMA, STAPLES) each with a read and explanation — cite these directly rather than re-deriving them. PHARMA is flagged IDIOSYNCRATIC (AstraZeneca is often the single largest index weight and can swing the index on stock-specific news alone).
- \`usLinkage.vixRegime\`: CALM / ELEVATED / STRESS — treat STRESS as a defensive damper on conviction, not a directional signal.
- \`ukRates.longEndStress\`: true when the 20-year gilt has sold off sharply — this is a fiscal-stress signal that overrides the normal "higher yields help bank stocks" rotation logic and is bearish for the index overall.
- \`orbContext\`: today's opening-range mechanics — cash open time, overnight range, ORB high/low, gap, and how much of the 14-day average daily range has already been used today.
- \`orbIntel.signals\`: a MECHANICAL read of the opening-range setup already computed for you — a list of \`{ direction, severity, source, text }\` plus a \`stance\`. These are deterministic rules (fakeout/reclaim, range budget, gap dynamics, tape, GBP extreme, etc.). Do NOT repeat them — your job is to ADD cross-field synthesis they do not already state (e.g. how two or three of these forces combine into one read).
- \`calendar\`: this week's UK/US/EZ economic events, each tagged with \`daysFromToday\`. \`newsItems\`: recent headlines tagged with \`hoursAgo\`.

Write a SINGLE flowing briefing paragraph (200–300 words) using PLAIN, BEGINNER-FRIENDLY language. Avoid jargon wherever possible. When you use a financial term, briefly explain what it means in brackets.

Your briefing MUST follow this structure within the single paragraph:
1. GBP SIGN-FLIP FIRST: state the GBPUSD move and what it means for UK100 (inverted).
2. REGIME LINE: which forces (sectors, gilts, US linkage, risk tone) are most relevant right now and why.
3. RECENT CATALYSTS: name any headline from the last few hours that plausibly explains a sterling, gilt, or index move (cite hoursAgo). If nothing looks market-moving, say so.
4. DIRECTIONAL BIAS with plain reasoning: is UK100 likely to favour UP, DOWN, or CHOPPY from here, and why.
5. CONFIDENCE SCORE: express confidence as X/10. Explain what would change the view.
6. ORB RELEVANCE: one sentence on what today's macro picture means specifically for the 08:00 opening-range trade — does the setup favour a clean trend day, a fakeout/sweep-then-reverse day, or a stand-aside day.
7. EVENT RISK: any scheduled news today (time in UK local), and a build-up caution line if a HIGH-impact event is later this week.
8. KEY LEVELS: the most important price levels to watch, referencing \`orbContext\` (overnight high/low, ORB high/low) and \`adr14\`/how much range is already used today.

End with one sentence a trader can screenshot and remember.

You must ALSO produce an \`orbIntel\` object — a short synthesis of the opening-range read that ADDS to (never repeats) the mechanical \`orbIntel.signals\` already in the snapshot:
- \`stanceLine\`: ONE sentence in the form "Due to X, Y and Z, <the read>" (e.g. "Due to a crowded-short pound, a split European tape and 78% of the daily range already spent, upside breaks look poorly supported today.").
- \`bullets\`: 2–4 bullets, each ≤ 30 words, each citing at least one concrete number from the snapshot, each covering CROSS-FIELD synthesis the mechanical signals do not already say. No invented data.

CRITICAL RULES:
- Use plain English. Do NOT make up data — only use what is in the JSON. If a field is null or an array is empty, say so.
- Never say "in conclusion" or "to summarise".
- Return your response as JSON:
  { "biasScore": number from -10 to +10 (negative = bearish, positive = bullish — match the snapshot's own bias.score scale), "biasLabel": "BEARISH" | "NEUTRAL" | "BULLISH", "confidence": number 1-10, "briefing": "your paragraph here", "orbIntel": { "stanceLine": "your one-sentence synthesis", "bullets": ["...", "..."] } }`

// The briefing call also carries the ORB-intel AI overlay (G2) — no extra API
// call. Both are best-effort: null/[] on any failure so the tile falls back to
// the mechanical layer.
interface BriefingResult {
  briefing: Uk100Snapshot['briefing']
  orbIntelOverlay: { stanceLine: string | null; bullets: string[] }
}
const EMPTY_OVERLAY: BriefingResult['orbIntelOverlay'] = { stanceLine: null, bullets: [] }

async function generateUk100Briefing(snapshot: Omit<Uk100Snapshot, 'briefing'>): Promise<BriefingResult> {
  console.log('Generating UK100 daily briefing (Anthropic)...')
  if (!ANTHROPIC_KEY) { console.log('Anthropic: ANTHROPIC_API_KEY env var not set — skipping briefing'); return { briefing: null, orbIntelOverlay: EMPTY_OVERLAY } }

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'x-api-key': ANTHROPIC_KEY,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: JSON.stringify({
        model: ANTHROPIC_MODEL,
        max_tokens: 1500,
        system: BRIEFING_SYSTEM_PROMPT,
        messages: [
          { role: 'user', content: `Here is today's UK100 market data snapshot:\n\n${JSON.stringify(snapshot, null, 2)}` },
        ],
      }),
    })

    if (!response.ok) {
      console.error(`Anthropic briefing API error ${response.status}: ${(await response.text()).slice(0, 200)}`)
      return { briefing: null, orbIntelOverlay: EMPTY_OVERLAY }
    }

    const body = await response.json() as { content: Array<{ type: string; text: string }> }
    const text = body.content.find(c => c.type === 'text')?.text ?? ''
    const cleaned = text.replace(/^```json?\s*/i, '').replace(/\s*```$/, '').trim()
    const parsed = JSON.parse(cleaned) as Omit<NonNullable<Uk100Snapshot['briefing']>, 'generatedAt'> & {
      orbIntel?: { stanceLine?: string; bullets?: string[] }
    }
    console.log(`UK100 briefing generated: bias=${parsed.biasLabel} score=${parsed.biasScore} confidence=${parsed.confidence}`)
    // Tolerate the orbIntel field being absent or malformed (older cached
    // prompt, model noncompliance) — never fail the snapshot on it.
    const overlay = {
      stanceLine: typeof parsed.orbIntel?.stanceLine === 'string' ? parsed.orbIntel.stanceLine : null,
      bullets: Array.isArray(parsed.orbIntel?.bullets) ? parsed.orbIntel!.bullets.filter((b): b is string => typeof b === 'string') : [],
    }
    return {
      briefing: { biasScore: parsed.biasScore, biasLabel: parsed.biasLabel, confidence: parsed.confidence, briefing: parsed.briefing, generatedAt: new Date().toISOString() },
      orbIntelOverlay: overlay,
    }
  } catch (err) {
    console.error('UK100 briefing generation failed:', err)
    return { briefing: null, orbIntelOverlay: EMPTY_OVERLAY }
  }
}

// ── Main ─────────────────────────────────────────────────────────────────

async function main() {
  const outDir  = path.join(__dirname, '../public/data/uk100')
  const outPath = path.join(outDir, 'daily-snapshot.json')
  fs.mkdirSync(outDir, { recursive: true })

  let existing: Partial<Uk100Snapshot> = {}
  try { existing = JSON.parse(fs.readFileSync(outPath, 'utf8')) } catch { /* first run */ }

  console.log('=== UK100 Data Fetch ===')

  const prevCot: CotResult = existing.positioning
    ? {
        cotNetLong: existing.positioning.gbpCotNetLong ?? null,
        cotWoWChange: existing.positioning.gbpCotWoWChange ?? null,
        crowding: existing.positioning.crowding ?? null,
        reportDate: existing.positioning.reportDate ?? null,
      }
    : { cotNetLong: null, cotWoWChange: null, crowding: null, reportDate: null }

  const [ctrader, boeRows, usdgbpFredPair, gbpCot, calendar, newsItems, us10yPair, brent20dTrend] = await Promise.all([
    fetchCtraderData(),
    fetchBoeIadb(),
    fredSeriesPair('DEXUSUK'),
    fetchGbpCot(prevCot),
    fetchUk100Calendar(),
    fetchUk100News(),
    fredSeriesPair('DGS10'),
    fredTrend('DCOILBRENTEU'),
  ])

  const [bankRate] = boeLatestTwo(boeRows, BOE_CODES.bankRate)
  const [sonia] = boeLatestTwo(boeRows, BOE_CODES.sonia)
  const [sterlingEri, sterlingEriPrev] = boeLatestTwo(boeRows, BOE_CODES.sterlingEri)
  const [gilt5y] = boeLatestTwo(boeRows, BOE_CODES.gilt5y)
  const [gilt10y, gilt10yPrev] = boeLatestTwo(boeRows, BOE_CODES.gilt10y)
  const [gilt20y, gilt20yPrev] = boeLatestTwo(boeRows, BOE_CODES.gilt20y)

  const gilt10yDayBp = gilt10y != null && gilt10yPrev != null ? Math.round((gilt10y - gilt10yPrev) * 100) : null
  const gilt20yDayBp = gilt20y != null && gilt20yPrev != null ? Math.round((gilt20y - gilt20yPrev) * 100) : null
  const sterlingEriDayChange = sterlingEri != null && sterlingEriPrev != null ? Math.round((sterlingEri - sterlingEriPrev) * 100) / 100 : null
  const [us10y] = us10yPair

  const gbpUsdDayPct = ctrader?.gbpUsdDayPct ?? null
  const gbpUsd20dPercentile = await fredPercentile20d('DEXUSUK', usdgbpFredPair[0])
  const ftseImpactFromGbp = ftseImpact(gbpUsdDayPct)

  const { date: nextMpc, daysToMpc } = nextMpcDate()
  const longEndStress = gilt20yDayBp != null && gilt20yDayBp >= 8

  const ukRates: UkRatesBlock = {
    bankRate, sonia,
    soniaMinusBankRate: sonia != null && bankRate != null ? Math.round((sonia - bankRate) * 100) / 100 : null,
    gilt5y, gilt10y, gilt20y, gilt10yDayBp, gilt20yDayBp,
    slope5s20s: gilt5y != null && gilt20y != null ? Math.round((gilt20y - gilt5y) * 100) / 100 : null,
    giltUst10ySpread: gilt10y != null && us10y != null ? Math.round((gilt10y - us10y) * 100) / 100 : null,
    longEndStress, nextMpcDate: nextMpc, daysToMpc,
  }

  const fx: FxBlock = {
    gbpUsdDayPct, gbpUsd20dPercentile, sterlingEri, sterlingEriDayChange, ftseImpactFromGbp,
  }

  const usLinkage: UsLinkageBlock = {
    us500DayPct: ctrader?.us500DayPct ?? null, nas100DayPct: ctrader?.nas100DayPct ?? null,
    vix: ctrader?.prices.VIX ?? null, vixRegime: vixRegime(ctrader?.prices.VIX ?? null),
    us10y, usdx: ctrader?.prices.USDX ?? null,
  }

  const commodities: CommoditiesBlock = {
    brentDayPct: ctrader?.brentDayPct ?? null, copperDayPct: ctrader?.copperDayPct ?? null,
    goldDayPct: ctrader?.goldDayPct ?? null, brent20dTrend,
  }

  const europeanTape: EuropeanTapeBlock = {
    eurostoxx50DayPct: ctrader?.eustx50DayPct ?? null, dax40DayPct: ctrader?.ger40DayPct ?? null,
    eurUsdDayPct: ctrader?.eurUsdDayPct ?? null,
    ftseDaxCorr20d: ctrader?.ftseDaxCorr20d ?? null, ftseSx5eCorr20d: ctrader?.ftseSx5eCorr20d ?? null,
    tapeAgreement: ctrader?.tapeAgreement ?? 'ALIGNED', preOpenLead: ctrader?.preOpenLead ?? 'NONE',
  }

  const positioning: PositioningBlock = {
    gbpCotNetLong: gbpCot.cotNetLong, gbpCotWoWChange: gbpCot.cotWoWChange,
    crowding: gbpCot.crowding, reportDate: gbpCot.reportDate,
    ftseReadthrough: gbpCot.crowding === 'CROWDED_LONG' ? 'BULLISH' : gbpCot.crowding === 'CROWDED_SHORT' ? 'BEARISH' : 'NEUTRAL',
  }

  const eventSuppressed = calendar.some(e => e.impact === 'HIGH' && e.daysFromToday === 0)

  // Risk tone feeds the bias engine's "Risk tone" driver, so it must resolve
  // before computeBias runs (same reason gold's briefing runs last: everything
  // else needs to already be settled).
  const riskTone = await fetchUk100RiskTone(newsItems)

  const nowLondon = londonNow()
  const nowLondonHour = nowLondon.getUTCHours() + nowLondon.getUTCMinutes() / 60

  const bias = computeBias({
    gbpUsdDayPct, sterlingEriDayChange,
    us500DayPct: usLinkage.us500DayPct, nas100DayPct: usLinkage.nas100DayPct,
    vix: usLinkage.vix,
    brentDayPct: commodities.brentDayPct, copperDayPct: commodities.copperDayPct,
    gilt10yDayBp, gilt20yDayBp,
    cotCrowding: positioning.crowding,
    riskToneLabel: riskTone?.label ?? null,
    eventSuppressed,
    ger40DayPct: europeanTape.dax40DayPct, eustx50DayPct: europeanTape.eurostoxx50DayPct,
    nowLondonHour,
  })

  const sectorPanel = computeSectorPanel({
    brentDayPct: commodities.brentDayPct, copperDayPct: commodities.copperDayPct,
    gilt10yDayBp, longEndStress, ftseImpactFromGbp,
  })

  const orbContext = computeOrbContext({ ctrader, uk100Price: ctrader?.prices.UK100 ?? null, calendar })

  // ORB intelligence (G1) — synthesised from the assembled blocks above plus
  // today's AI session echo (R12). Runs before the briefing call so the
  // briefing prompt (G2) can see the mechanical signals and add synthesis.
  const orbIntel = computeOrbIntel({
    orbContext, bias, europeanTape, usLinkage, fx, ukRates, positioning,
    calendar, uk100Price: ctrader?.prices.UK100 ?? null, nowLondonHour,
    todaySession: readTodaySessionEcho(),
  })
  console.log(`ORB intel: ${orbIntel.stance} (${orbIntel.signals.length} signals)`)

  const snapshotWithoutBriefing: Omit<Uk100Snapshot, 'briefing'> = {
    generatedAt: new Date().toISOString(),
    prices: ctrader?.prices ?? {
      UK100: null, GBPUSD: null, GBPEUR: null, US500: null, NAS100: null, BRENT: null,
      COPPER: null, VIX: null, USDX: null, XAUUSD: null, UK100_dayPct: null,
    },
    fx, ukRates, usLinkage, commodities, europeanTape, positioning, sectorPanel,
    economicCalendar: calendar, newsItems,
    riskTone,
    bias, orbContext, orbIntel,
  }

  const { briefing, orbIntelOverlay } = await generateUk100Briefing(snapshotWithoutBriefing)
  // Merge the AI overlay (G2) into the mechanical orbIntel; the tile prefers
  // aiStanceLine when present and falls back to the mechanical stanceLine.
  const orbIntelFinal: OrbIntel = { ...orbIntel, aiStanceLine: orbIntelOverlay.stanceLine, aiBullets: orbIntelOverlay.bullets }
  const snapshot: Uk100Snapshot = { ...snapshotWithoutBriefing, orbIntel: orbIntelFinal, briefing }

  fs.writeFileSync(outPath, JSON.stringify(snapshot, null, 2))
  console.log(`UK100 snapshot written: ${path.relative(path.join(__dirname, '../..'), outPath)}`)
  console.log(`Bias: ${bias.label} (score=${bias.score}, conviction=${bias.conviction})`)
  console.log(`ORB intel: ${orbIntelFinal.stance}, aiBullets=${orbIntelFinal.aiBullets.length}`)
  console.log(`Risk tone: ${riskTone ? `${riskTone.label} (${riskTone.score})` : 'null'}`)
  console.log(`Briefing: ${briefing ? `${briefing.biasLabel} ${briefing.biasScore} (conf ${briefing.confidence})` : 'null'}`)
}

// Only run when invoked directly (not when imported for unit tests) —
// same guard as resolve-gold-sessions.ts, needed so B1/B3's pure functions
// (computeBias, firstCloseOutside) can be unit-tested without triggering a
// live fetch on import.
if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(err => {
    console.error('UK100 fetch failed:', err)
    process.exit(1)
  })
}
