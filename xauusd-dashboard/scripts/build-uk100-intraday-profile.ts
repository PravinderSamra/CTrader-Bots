#!/usr/bin/env tsx
/**
 * Build the UK100 intraday completion profile — the per-hour "how much of a
 * typical day's RANGE and VOLUME is done by hour H" baseline that powers the
 * `expansionState` read in fetch-uk100-data.ts (is today an expansion day, and
 * is most of the move / volume already done → likely to range?).
 *
 * Why this exists: `orbContext.adrUsedPct` alone is time-BLIND — 67% of a
 * UK100 day's range is typically set by 11:00 BST but only ~47% of its volume
 * has traded (range front-loads on the open, volume back-loads on the US
 * overlap). So "range looks done" mid-morning is unreliable until the heavier
 * afternoon volume has passed. This baseline makes that judgement possible.
 *
 * Output: public/data/uk100/intraday-profile.json — a small (~1KB) cached
 * curve, refreshed occasionally (e.g. weekly from the daily workflow). It is
 * the SHAPE (percentages) that matters; absolute ADR stays sourced from D_1 in
 * the fetch. cTrader `volume` is TICK volume (LP-aggregated price updates), not
 * true exchange contract volume — fine for the intraday shape, not for absolute
 * figures.
 *
 * Usage (from xauusd-dashboard/):
 *   npx tsx scripts/build-uk100-intraday-profile.ts           # fetch + write
 *   npx tsx scripts/build-uk100-intraday-profile.ts --days 60 # wider sample
 *   npx tsx scripts/build-uk100-intraday-profile.ts --dry     # compute + log, no write
 *
 * Requires CTRADER_MCP_URL / CTRADER_MCP_TOKEN (the daily workflow provides
 * them). Without a token it exits cleanly as a no-op.
 */

import * as fs from 'fs'
import * as path from 'path'
import { fileURLToPath } from 'url'
import { CTraderClient, KNOWN_SYMBOL_IDS, type Trendbar } from './lib/ctrader'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

const OUT_FILE = path.join(__dirname, '../public/data/uk100/intraday-profile.json')
const UK100_ID = KNOWN_SYMBOL_IDS.UK100

const DRY = process.argv.includes('--dry')
const daysArgIdx = process.argv.indexOf('--days')
const TARGET_DAYS = daysArgIdx >= 0 ? Math.max(10, Math.min(90, Number(process.argv[daysArgIdx + 1]) || 45)) : 45

// The London cash session hours we bucket into (08:00 open → 16:30 close).
export const SESSION_HOURS = [8, 9, 10, 11, 12, 13, 14, 15, 16]

// BST (UTC+1) ~ last Sun Mar → last Sun Oct, month-boundary approximation
// (same convention as the other scripts' date helpers).
function londonHour(ms: number): number {
  const d = new Date(ms)
  const m = d.getUTCMonth() + 1
  const day = d.getUTCDate()
  const bst = (m > 3 && m < 10) || (m === 3 && day >= 25) || (m === 10 && day < 25)
  return new Date(ms + (bst ? 3_600_000 : 0)).getUTCHours()
}

export interface HourPoint { cumRangePct: number; cumVolPct: number }
export interface IntradayProfile {
  generatedAt: string
  instrument: 'UK100'
  daysSampled: number
  avgSessionRangePts: number | null
  byHourLondon: Record<string, HourPoint>
}

/**
 * Pure: average the per-hour cumulative range% and volume% across the sampled
 * days. Each day's cumulatives are normalised to that day's OWN full range /
 * volume, so range% and volume% are scale-invariant (pipettes are fine) and a
 * big day doesn't dominate the average. Hours with no bar carry the last seen
 * value forward (a gap doesn't reset the cumulative).
 */
export function computeProfile(
  days: { date: string; bars: { timestamp: number; high: number; low: number; volume: number }[] }[],
): IntradayProfile {
  const rangeAcc: Record<number, number[]> = {}
  const volAcc: Record<number, number[]> = {}
  const sessionRanges: number[] = []
  for (const h of SESSION_HOURS) { rangeAcc[h] = []; volAcc[h] = [] }

  for (const { bars } of days) {
    if (bars.length === 0) continue
    const dayHi = Math.max(...bars.map(b => b.high))
    const dayLo = Math.min(...bars.map(b => b.low))
    const dayRange = dayHi - dayLo
    const dayVol = bars.reduce((a, b) => a + b.volume, 0)
    if (dayRange <= 0 || dayVol <= 0) continue
    sessionRanges.push(dayRange)

    // Cumulative state walked chronologically; snapshot at each hour's last bar.
    let cumHi = -Infinity, cumLo = Infinity, cumVol = 0
    const byHour: Record<number, HourPoint> = {}
    for (const b of [...bars].sort((a, z) => a.timestamp - z.timestamp)) {
      cumHi = Math.max(cumHi, b.high)
      cumLo = Math.min(cumLo, b.low)
      cumVol += b.volume
      byHour[londonHour(b.timestamp)] = {
        cumRangePct: (cumHi - cumLo) / dayRange * 100,
        cumVolPct: cumVol / dayVol * 100,
      }
    }
    // Forward-fill: carry the last seen cumulative across empty hours.
    let running: HourPoint | null = null
    for (const h of SESSION_HOURS) {
      if (byHour[h]) running = byHour[h]
      if (running) { rangeAcc[h].push(running.cumRangePct); volAcc[h].push(running.cumVolPct) }
    }
  }

  const avg = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : 0)
  const byHourLondon: Record<string, HourPoint> = {}
  for (const h of SESSION_HOURS) {
    if (rangeAcc[h].length === 0) continue
    byHourLondon[String(h)] = {
      cumRangePct: Math.round(avg(rangeAcc[h])),
      cumVolPct: Math.round(avg(volAcc[h])),
    }
  }

  return {
    generatedAt: new Date().toISOString(),
    instrument: 'UK100',
    daysSampled: sessionRanges.length,
    avgSessionRangePts: sessionRanges.length ? Math.round(avg(sessionRanges) / 1e5 * 10) / 10 : null,
    byHourLondon,
  }
}

// ── Live read: expansion vs range, computed each run against the baseline ──

export type ExpansionLabel = 'EXPANSION' | 'NORMAL' | 'COMPRESSED' | 'UNKNOWN'
export interface ExpansionState {
  label: ExpansionLabel
  rangeSoFarPct: number | null        // today's realised range as % of ADR14 (= adrUsedPct)
  expectedRangePctByNow: number | null
  rangeVsTypical: number | null       // rangeSoFarPct / expectedRangePctByNow (>1 = ahead of pace)
  expectedVolPctByNow: number | null  // % of a typical day's volume usually done by now (time budget)
  moveMostlyDone: boolean             // little range/volume expected to remain → likely to range
  note: string
}

/**
 * Pure: classify today's pace against the baseline. `adrUsedPct` is today's
 * realised range as a % of ADR14 (from orbContext) — comparable to the
 * profile's `cumRangePct` because a day's own range ≈ ADR on average.
 * `hourLondon` is the current London hour; it's clamped to the session
 * (pre-open → UNKNOWN, post-close → treated as 16:00 / fully done).
 */
export function computeExpansionState(
  profile: IntradayProfile | null,
  hourLondon: number,
  adrUsedPct: number | null,
): ExpansionState {
  const unknown = (note: string): ExpansionState => ({
    label: 'UNKNOWN', rangeSoFarPct: adrUsedPct, expectedRangePctByNow: null,
    rangeVsTypical: null, expectedVolPctByNow: null, moveMostlyDone: false, note,
  })
  if (!profile || Object.keys(profile.byHourLondon).length === 0) return unknown('No intraday profile available.')
  if (adrUsedPct == null) return unknown('Range-used% unavailable.')
  if (hourLondon < 8) return unknown('Pre-open — session range has not started.')

  const h = Math.min(16, hourLondon)
  const point = profile.byHourLondon[String(h)] ?? profile.byHourLondon['16']
  const expRange = point.cumRangePct
  const expVol = point.cumVolPct
  const ratio = expRange > 0 ? Math.round(adrUsedPct / expRange * 100) / 100 : null

  let label: ExpansionLabel = 'NORMAL'
  if (ratio != null && ratio >= 1.35) label = 'EXPANSION'
  else if (ratio != null && ratio <= 0.65) label = 'COMPRESSED'

  // Most of the day is done when either most of the day's VOLUME has typically
  // traded (little session left), or the range is essentially used up past
  // midday — both argue for a rangebound remainder / tighter targets.
  const moveMostlyDone = hourLondon > 16 || expVol >= 80 || (adrUsedPct >= 95 && expVol >= 55)

  const pace = label === 'EXPANSION' ? 'ahead of the typical pace (expansion)'
    : label === 'COMPRESSED' ? 'below the typical pace (compressed/range)'
    : 'about the typical pace'
  const remain = moveMostlyDone
    ? ` ~${expVol}% of a typical day's volume already done — expect a rangebound remainder, tighten targets.`
    : ` only ~${expVol}% of volume typically done by now — an afternoon expansion is still possible.`
  const note = `Range ${adrUsedPct}% of ADR vs ~${expRange}% typical by ${String(h).padStart(2, '0')}:00 BST (${pace}).${remain}`

  return { label, rangeSoFarPct: adrUsedPct, expectedRangePctByNow: expRange, rangeVsTypical: ratio, expectedVolPctByNow: expVol, moveMostlyDone, note }
}

async function main() {
  // Self-managing freshness: the baseline changes slowly, so skip the ~45
  // fetches when the existing profile is < 7 days old (unless --force). Lets
  // the daily workflow call this every run cheaply — it no-ops when fresh.
  if (!process.argv.includes('--force') && !DRY) {
    try {
      const existing = JSON.parse(fs.readFileSync(OUT_FILE, 'utf8')) as IntradayProfile
      const ageDays = (Date.now() - Date.parse(existing.generatedAt)) / 86_400_000
      if (ageDays < 7) { console.log(`Intraday profile is ${ageDays.toFixed(1)}d old (< 7d) — skipping rebuild.`); return }
    } catch { /* no profile yet — build it */ }
  }

  const client = new CTraderClient()
  if (!UK100_ID) { console.error('UK100 symbolId unknown — aborting.'); process.exit(1) }
  if (!(await client.init())) {
    console.log('CTrader MCP unavailable (no token or init failed) — skipping profile build (no-op).')
    return
  }

  // Walk back over calendar days, fetching each weekday's cash session (07:00–
  // 15:30 UTC = 08:00–16:30 BST) as one M15 request (~34 bars, under the
  // 100-bar cap) until we have TARGET_DAYS worth of data.
  const days: { date: string; bars: Trendbar[] }[] = []
  const cursor = new Date()
  cursor.setUTCHours(0, 0, 0, 0)
  let guard = 0
  while (days.length < TARGET_DAYS && guard < TARGET_DAYS * 2 + 30) {
    guard++
    const dow = cursor.getUTCDay()
    if (dow !== 0 && dow !== 6) {
      const dayStr = cursor.toISOString().slice(0, 10)
      const from = Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth(), cursor.getUTCDate(), 7, 0)
      const to = Date.UTC(cursor.getUTCFullYear(), cursor.getUTCMonth(), cursor.getUTCDate(), 15, 30)
      if (to < Date.now()) {
        try {
          const bars = await client.getTrendbars(UK100_ID, 'M_15', from, to)
          if (bars.length >= 10) days.push({ date: dayStr, bars })
        } catch { /* skip a bad day, keep walking */ }
      }
    }
    cursor.setUTCDate(cursor.getUTCDate() - 1)
  }

  if (days.length < 10) { console.error(`Only ${days.length} usable days fetched — need ≥10; aborting.`); process.exit(1) }

  const profile = computeProfile(days)
  console.log(`Profile from ${profile.daysSampled} days (avg session range ${profile.avgSessionRangePts}pts):`)
  for (const h of SESSION_HOURS) {
    const p = profile.byHourLondon[String(h)]
    if (p) console.log(`  ${String(h).padStart(2, '0')}:00 BST  range ${String(p.cumRangePct).padStart(3)}%  vol ${String(p.cumVolPct).padStart(3)}%`)
  }

  if (!DRY) {
    fs.writeFileSync(OUT_FILE, JSON.stringify(profile, null, 2) + '\n')
    console.log(`Wrote ${path.relative(path.join(__dirname, '..'), OUT_FILE)}`)
  } else {
    console.log('(dry run — no write)')
  }
}

if (process.argv[1] && fileURLToPath(import.meta.url) === path.resolve(process.argv[1])) {
  main().catch(err => { console.error('build-uk100-intraday-profile failed:', err); process.exit(1) })
}
